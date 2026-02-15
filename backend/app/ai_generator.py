"""AI task generation utilities with pluggable model adapters and personalization.

Personalization rules implemented:
- If 7-day completion rate > 80%: increase next-task difficulty.
- If 7-day completion rate < 40%: reduce duration and complexity.
- If a pillar is consistently low: give that pillar extra weight.
- If joy score < 3 for 5 straight days: reduce task load slightly.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import os
from typing import Protocol

from openai import OpenAI

# Canonical developmental pillars.
PILLARS = ["Cognitive", "Physical", "Language", "Character", "Creativity"]
DIFFICULTY_ORDER = ["easy", "medium", "hard"]

# Stoic-inspired character lesson prompts to include in each generated plan.
STOIC_CHARACTER_TEMPLATES = [
    {
        "kind": "stoic_reflection",
        "title": "Stoic Reflection",
        "prompt": "What can you control today?",
    },
    {
        "kind": "gratitude",
        "title": "Gratitude Practice",
        "prompt": "Name three good things that happened.",
    },
    {
        "kind": "responsibility",
        "title": "Responsibility Assignment",
        "prompt": "Complete one small responsibility before free time.",
    },
    {
        "kind": "story_excerpt",
        "title": "Story Excerpt Reflection",
        "prompt": "Read or listen to a short story excerpt and note one moral lesson.",
    },
]


@dataclass(slots=True)
class PersonalizationSignal:
    """Behavioral signals computed from historical task/check-in data."""

    completion_rate_7d: float = 0.0
    low_pillar: str | None = None
    joy_below_three_streak_5d: bool = False


@dataclass(slots=True)
class GenerationStrategy:
    """Concrete generation instructions derived from personalization signals."""

    target_pillars: list[str]
    difficulty_bias: int = 0  # -1 easier, 0 neutral, +1 harder
    duration_scale: float = 1.0
    low_pillar: str | None = None


class TaskGenerationAdapter(Protocol):
    """Adapter protocol to support different model providers/backends."""

    def generate(
        self,
        *,
        age: int,
        parent_priority: str,
        strategy: GenerationStrategy,
    ) -> list[dict]:
        """Return structured tasks for the requested strategy and pillars."""


class OpenAIResponsesAdapter:
    """Default adapter backed by OpenAI Responses API."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(
        self,
        *,
        age: int,
        parent_priority: str,
        strategy: GenerationStrategy,
    ) -> list[dict]:
        task_count = len(strategy.target_pillars)
        prompt = (
            "You generate developmental daily tasks for ages 0-21. "
            f"Child age: {age}. Parent priority: {parent_priority}. "
            f"Generate {task_count} tasks for pillars in this exact order: {strategy.target_pillars}. "
            f"Difficulty bias: {strategy.difficulty_bias} (1=harder, -1=easier). "
            f"Duration scale: {strategy.duration_scale}. "
            f"Low pillar to emphasize: {strategy.low_pillar}. "
            "Return STRICT JSON array with objects that include keys: "
            "pillar, title, description, duration_minutes, difficulty_level. "
            "difficulty_level must be one of easy|medium|hard."
        )

        response = self.client.responses.create(model=self.model, input=prompt)
        raw = response.output_text.strip()
        parsed = json.loads(raw)
        if not isinstance(parsed, list) or len(parsed) != task_count:
            raise ValueError(f"Model response must be a list of {task_count} tasks")
        return parsed


class StaticFallbackAdapter:
    """Deterministic fallback if no external model is configured/available."""

    def generate(
        self,
        *,
        age: int,
        parent_priority: str,
        strategy: GenerationStrategy,
    ) -> list[dict]:
        seed = {
            "Cognitive": (
                "Focus Sprint Puzzle",
                f"Solve one age-{age} logic puzzle aligned with {parent_priority}.",
                20,
                "medium",
            ),
            "Physical": (
                "Movement Circuit",
                "Complete a short movement routine with stretching and balance.",
                25,
                "easy",
            ),
            "Language": (
                "Story Retell",
                "Read/listen to a short story and retell key points aloud.",
                15,
                "easy",
            ),
            "Character": (
                "Kindness Action",
                "Plan and complete one helpful action for family or friends.",
                10,
                "easy",
            ),
            "Creativity": (
                "Create and Share",
                "Create a drawing, beat, or short craft and explain your choices.",
                30,
                "medium",
            ),
        }

        tasks: list[dict] = []
        for pillar in strategy.target_pillars:
            title, description, duration, difficulty = seed[pillar]
            tasks.append(
                {
                    "pillar": pillar,
                    "title": title,
                    "description": description,
                    "duration_minutes": duration,
                    "difficulty_level": difficulty,
                }
            )
        return tasks


def _select_adapter(model_hint: str | None = None) -> TaskGenerationAdapter:
    """Resolve adapter by model hint while keeping a safe fallback."""
    if model_hint == "fallback":
        return StaticFallbackAdapter()
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIResponsesAdapter(model=model_hint or "gpt-4o-mini")
    return StaticFallbackAdapter()


def _derive_strategy(signals: PersonalizationSignal, parent_priority: str) -> GenerationStrategy:
    """Convert behavioral signals into scheduling + generation strategy."""
    # Baseline: one task per pillar.
    target_pillars = list(PILLARS)
    difficulty_bias = 0
    duration_scale = 1.0

    # Rule 1: high completion => harder next tasks.
    if signals.completion_rate_7d > 80:
        difficulty_bias = 1

    # Rule 2: low completion => easier + shorter tasks.
    if signals.completion_rate_7d < 40:
        difficulty_bias = -1
        duration_scale = 0.85

    # Rule 4: low joy streak => reduce load slightly (5 -> 4 tasks).
    if signals.joy_below_three_streak_5d:
        target_pillars = _prioritize_pillars_for_reduced_load(
            low_pillar=signals.low_pillar,
            parent_priority=parent_priority,
            max_tasks=4,
        )

    return GenerationStrategy(
        target_pillars=target_pillars,
        difficulty_bias=difficulty_bias,
        duration_scale=duration_scale,
        low_pillar=signals.low_pillar,
    )


def _prioritize_pillars_for_reduced_load(
    low_pillar: str | None,
    parent_priority: str,
    max_tasks: int,
) -> list[str]:
    """Select which pillars remain when reducing load, preserving personalization."""
    ordered: list[str] = []

    # Keep low-performing pillar in rotation first when applicable.
    if low_pillar in PILLARS:
        ordered.append(low_pillar)

    # Map parent priority text to a likely pillar and keep it near front.
    priority_map = {
        "study": "Cognitive",
        "fitness": "Physical",
        "exercise": "Physical",
        "language": "Language",
        "communication": "Language",
        "behavior": "Character",
        "discipline": "Character",
        "creative": "Creativity",
        "art": "Creativity",
    }
    normalized_priority = parent_priority.lower()
    matched = next((v for k, v in priority_map.items() if k in normalized_priority), None)
    if matched and matched not in ordered:
        ordered.append(matched)

    for pillar in PILLARS:
        if pillar not in ordered:
            ordered.append(pillar)

    return ordered[:max_tasks]


def _shift_difficulty(level: str, bias: int) -> str:
    """Shift difficulty one step up/down based on strategy bias."""
    try:
        index = DIFFICULTY_ORDER.index(level)
    except ValueError:
        index = 1
    index = max(0, min(len(DIFFICULTY_ORDER) - 1, index + bias))
    return DIFFICULTY_ORDER[index]


def _age_scaled_character_config(age: int) -> dict[str, str | int]:
    """Return age-specific settings for character lesson complexity and duration."""
    if age <= 3:
        return {
            "difficulty_level": "easy",
            "duration_minutes": 6,
            "tone": "Use simple language and parent-guided reflection.",
        }
    if age <= 7:
        return {
            "difficulty_level": "easy",
            "duration_minutes": 8,
            "tone": "Use short sentences and concrete examples.",
        }
    if age <= 12:
        return {
            "difficulty_level": "medium",
            "duration_minutes": 10,
            "tone": "Use practical examples and one written sentence.",
        }
    if age <= 16:
        return {
            "difficulty_level": "medium",
            "duration_minutes": 12,
            "tone": "Use reflective journaling with personal responsibility.",
        }
    return {
        "difficulty_level": "hard",
        "duration_minutes": 14,
        "tone": "Use deeper self-audit and independent decision framing.",
    }


def _build_stoic_character_tasks(age: int) -> list[dict]:
    """Build required Stoic character tasks and scale them to age."""
    cfg = _age_scaled_character_config(age)
    tasks: list[dict] = []

    for template in STOIC_CHARACTER_TEMPLATES:
        tasks.append(
            {
                "pillar": "Character",
                "title": template["title"],
                "description": f"{template['prompt']} {cfg['tone']}",
                "duration_minutes": cfg["duration_minutes"],
                "difficulty_level": cfg["difficulty_level"],
            }
        )
    return tasks


def _post_process_tasks(tasks: list[dict], strategy: GenerationStrategy) -> list[dict]:
    """Apply deterministic personalization adjustments after model generation."""
    adjusted: list[dict] = []
    for task in tasks:
        pillar = task.get("pillar")
        duration = int(task.get("duration_minutes", 20))
        difficulty = str(task.get("difficulty_level", "medium"))

        # Rule 2: decrease duration when completion is weak.
        duration = max(8, int(round(duration * strategy.duration_scale)))

        # Rule 1/2: adjust complexity.
        difficulty = _shift_difficulty(difficulty, strategy.difficulty_bias)

        # Rule 3: if a pillar is consistently low, boost exposure slightly.
        if strategy.low_pillar and pillar == strategy.low_pillar:
            duration = int(round(duration * 1.15))
            task["description"] = (
                f"(Priority pillar focus) {task.get('description', '')}".strip()
            )

        task["duration_minutes"] = duration
        task["difficulty_level"] = difficulty
        adjusted.append(task)

    return adjusted


async def generateDailyTasks(
    age: int,
    parent_priority: str,
    model_hint: str | None = None,
    signals: PersonalizationSignal | None = None,
) -> list[dict]:
    """Generate personalized next tasks and schedule based on behavior signals."""
    strategy = _derive_strategy(signals or PersonalizationSignal(), parent_priority)
    adapter = _select_adapter(model_hint)
    tasks = await asyncio.to_thread(
        adapter.generate,
        age=age,
        parent_priority=parent_priority,
        strategy=strategy,
    )

    # Normalize by requested pillar order and enforce required count.
    by_pillar: dict[str, dict] = {task["pillar"]: task for task in tasks if "pillar" in task}
    ordered = [by_pillar[p] for p in strategy.target_pillars if p in by_pillar]
    if len(ordered) != len(strategy.target_pillars):
        raise ValueError("Generated tasks did not include all required pillars in strategy")

    adjusted = _post_process_tasks(ordered, strategy)

    # Weekly-plan policy: include Stoic character lesson tasks on every plan generation.
    # These cover reflection, gratitude, responsibility, and story-moral exploration.
    adjusted.extend(_build_stoic_character_tasks(age))
    return adjusted

"""Async CRUD logic for child profiles, daily plans, milestones, and progress metrics."""

from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import ai_generator, models, schemas

# Milestone catalog for all developmental phases (0-21).
MILESTONE_LIBRARY: list[dict[str, str]] = [
    # Phase 1: 0–3
    {"age_phase": "Phase 1 (0-3)", "focus": "sensory", "title": "Responds to familiar sounds and voices"},
    {"age_phase": "Phase 1 (0-3)", "focus": "language", "title": "Uses first meaningful words"},
    # Phase 2: 4–7
    {"age_phase": "Phase 2 (4-7)", "focus": "curiosity", "title": "Asks exploratory why/how questions"},
    {"age_phase": "Phase 2 (4-7)", "focus": "basic skills", "title": "Reads simple instructions independently"},
    # Phase 3: 8–12
    {"age_phase": "Phase 3 (8-12)", "focus": "competence", "title": "Completes multi-step projects consistently"},
    {"age_phase": "Phase 3 (8-12)", "focus": "logic", "title": "Applies logic to solve age-level problems"},
    # Phase 4: 13–16
    {"age_phase": "Phase 4 (13-16)", "focus": "identity", "title": "Expresses personal values and goals"},
    {"age_phase": "Phase 4 (13-16)", "focus": "responsibility", "title": "Manages responsibilities with minimal reminders"},
    # Phase 5: 17–21
    {"age_phase": "Phase 5 (17-21)", "focus": "mastery", "title": "Builds mastery in a chosen domain"},
    {"age_phase": "Phase 5 (17-21)", "focus": "independence", "title": "Plans and executes independent life routines"},
]


async def create_profile(db: AsyncSession, payload: schemas.ChildProfileCreate) -> models.ChildProfile:
    """Create and persist a new child profile."""
    profile = models.ChildProfile(**payload.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_profile(db: AsyncSession, child_id: int) -> models.ChildProfile | None:
    """Fetch one child profile by ID."""
    result = await db.execute(
        select(models.ChildProfile).where(models.ChildProfile.id == child_id)
    )
    return result.scalar_one_or_none()


async def get_milestones_for_child(db: AsyncSession, child_id: int) -> list[schemas.MilestoneStatusOut]:
    """Return milestone examples across all phases with achieved status for a child."""
    result = await db.execute(
        select(models.Milestone).where(models.Milestone.child_id == child_id)
    )
    rows = result.scalars().all()
    achieved_map = {(row.age_phase, row.title): row.achieved for row in rows}

    milestones: list[schemas.MilestoneStatusOut] = []
    for item in MILESTONE_LIBRARY:
        key = (item["age_phase"], item["title"])
        milestones.append(
            schemas.MilestoneStatusOut(
                age_phase=item["age_phase"],
                focus=item["focus"],
                title=item["title"],
                achieved=achieved_map.get(key, False),
            )
        )
    return milestones


async def _compute_completion_rate_7d(db: AsyncSession, child_id: int) -> float:
    """Compute 7-day completion percentage for personalization decisions."""
    start_date = date.today() - timedelta(days=6)

    total_result = await db.execute(
        select(func.count(models.DailyTask.id)).where(
            models.DailyTask.child_id == child_id,
            models.DailyTask.date_assigned >= start_date,
        )
    )
    completed_result = await db.execute(
        select(func.count(models.DailyTask.id)).where(
            models.DailyTask.child_id == child_id,
            models.DailyTask.date_assigned >= start_date,
            models.DailyTask.completed.is_(True),
        )
    )

    total = total_result.scalar_one() or 0
    completed = completed_result.scalar_one() or 0
    return (completed / total * 100.0) if total else 0.0


async def _detect_low_pillar_7d(db: AsyncSession, child_id: int) -> str | None:
    """Identify consistently weak pillar from last 7 days of task outcomes.

    Rule: choose pillar with the lowest completion rate if it is meaningfully lower
    than the global average (>= 15 percentage points lower).
    """
    start_date = date.today() - timedelta(days=6)

    result = await db.execute(
        select(models.DailyTask).where(
            models.DailyTask.child_id == child_id,
            models.DailyTask.date_assigned >= start_date,
        )
    )
    rows = result.scalars().all()
    if not rows:
        return None

    totals: dict[str, int] = defaultdict(int)
    completed: dict[str, int] = defaultdict(int)
    for row in rows:
        totals[row.pillar] += 1
        if row.completed:
            completed[row.pillar] += 1

    rates: dict[str, float] = {
        pillar: (completed[pillar] / totals[pillar] * 100.0) for pillar in totals
    }
    global_rate = sum(completed.values()) / sum(totals.values()) * 100.0

    low_pillar = min(rates, key=rates.get)
    if rates[low_pillar] <= global_rate - 15:
        return low_pillar
    return None


async def _joy_low_streak_5d(db: AsyncSession, child_id: int) -> bool:
    """Check if joy_score stayed below 3 for the last 5 check-ins."""
    result = await db.execute(
        select(models.DailyCheckin.joy_score)
        .where(models.DailyCheckin.child_id == child_id)
        .order_by(models.DailyCheckin.checkin_date.desc())
        .limit(5)
    )
    scores = list(result.scalars().all())
    if len(scores) < 5:
        return False
    return all(score < 3 for score in scores)


async def _build_personalization_signal(
    db: AsyncSession,
    child_id: int,
) -> ai_generator.PersonalizationSignal:
    """Aggregate behavioral signals used by AI task personalization rules."""
    completion_rate_7d = await _compute_completion_rate_7d(db, child_id)
    low_pillar = await _detect_low_pillar_7d(db, child_id)
    joy_below_three_streak_5d = await _joy_low_streak_5d(db, child_id)

    return ai_generator.PersonalizationSignal(
        completion_rate_7d=completion_rate_7d,
        low_pillar=low_pillar,
        joy_below_three_streak_5d=joy_below_three_streak_5d,
    )


async def generate_daily_plan(db: AsyncSession, child_id: int) -> list[models.DailyTask]:
    """Generate next tasks using personalized AI strategy and save today's plan."""
    profile = await get_profile(db, child_id)
    if profile is None:
        return []

    age_years = max(0, (date.today() - profile.date_of_birth).days // 365)

    # Personalization: use recent completion, low-pillar trends, and joy streaks.
    signals = await _build_personalization_signal(db, child_id)
    generated = await ai_generator.generateDailyTasks(
        age=age_years,
        parent_priority=profile.parent_priority,
        signals=signals,
    )

    created_tasks: list[models.DailyTask] = []
    for task in generated:
        row = models.DailyTask(
            child_id=child_id,
            pillar=task["pillar"],
            title=task["title"],
            description=task["description"],
            duration_minutes=task["duration_minutes"],
            difficulty_level=task["difficulty_level"],
            date_assigned=date.today(),
        )
        db.add(row)
        created_tasks.append(row)

    await db.commit()
    for task in created_tasks:
        await db.refresh(task)
    return created_tasks


async def update_task_status(
    db: AsyncSession, task_id: int, completed: bool
) -> models.DailyTask | None:
    """Mark a task complete/incomplete and set completion timestamp accordingly."""
    result = await db.execute(select(models.DailyTask).where(models.DailyTask.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        return None

    task.completed = completed
    task.completion_timestamp = datetime.utcnow() if completed else None
    await db.commit()
    await db.refresh(task)
    return task


async def create_daily_checkin(
    db: AsyncSession,
    child_id: int,
    payload: schemas.DailyCheckinCreate,
) -> models.DailyCheckin | None:
    """Persist a daily check-in (joy score + notes) for a child profile."""
    profile = await get_profile(db, child_id)
    if profile is None:
        return None

    checkin = models.DailyCheckin(
        child_id=child_id,
        joy_score=payload.joy_score,
        parent_notes=payload.parent_notes or None,
        checkin_date=date.today(),
    )
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return checkin


async def fetch_weekly_progress(db: AsyncSession, child_id: int) -> schemas.WeeklyProgress:
    """Compute weekly completion ratio for dashboard charting."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    total_result = await db.execute(
        select(func.count(models.DailyTask.id)).where(
            models.DailyTask.child_id == child_id,
            models.DailyTask.date_assigned >= week_start,
        )
    )
    completed_result = await db.execute(
        select(func.count(models.DailyTask.id)).where(
            models.DailyTask.child_id == child_id,
            models.DailyTask.date_assigned >= week_start,
            models.DailyTask.completed.is_(True),
        )
    )

    total_tasks = total_result.scalar_one() or 0
    completed_tasks = completed_result.scalar_one() or 0
    rate = (completed_tasks / total_tasks) if total_tasks else 0.0

    return schemas.WeeklyProgress(
        child_id=child_id,
        week_start=week_start,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=round(rate, 3),
    )

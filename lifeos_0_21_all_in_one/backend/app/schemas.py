"""Pydantic request/response schemas for LifeOS 0-21 API."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---------- Child profile schemas ----------
class ChildProfileBase(BaseModel):
    """Shared profile fields used for create/read operations."""

    name: str
    date_of_birth: date
    interests: list[str] = Field(default_factory=list)
    parent_priority: str


class ChildProfileCreate(ChildProfileBase):
    """Payload for creating a child profile."""


class ChildProfileOut(ChildProfileBase):
    """Response model for child profile reads."""

    id: int

    model_config = {"from_attributes": True}


# ---------- Daily task schemas ----------
class DailyTaskBase(BaseModel):
    """Shared fields for daily task data."""

    pillar: Literal["Cognitive", "Physical", "Language", "Character", "Creativity"]
    title: str
    description: str
    duration_minutes: int = Field(20, ge=5, le=180)
    difficulty_level: Literal["easy", "medium", "hard"] = "medium"


class DailyTaskCreate(DailyTaskBase):
    """Payload for inserting an assigned daily task."""

    child_id: int
    date_assigned: date = Field(default_factory=date.today)


class DailyTaskOut(DailyTaskBase):
    """Response model for daily tasks."""

    id: int
    child_id: int
    completed: bool
    completion_timestamp: datetime | None
    date_assigned: date

    model_config = {"from_attributes": True}


class CompleteTaskRequest(BaseModel):
    """Payload for marking one task complete/incomplete."""

    task_id: int
    completed: bool = True


# ---------- Milestone schemas ----------
class MilestoneBase(BaseModel):
    """Shared milestone fields."""

    age_phase: str
    title: str
    achieved: bool = False


class MilestoneCreate(MilestoneBase):
    """Payload for creating a milestone."""

    child_id: int


class MilestoneOut(MilestoneBase):
    """Response model for milestones."""

    id: int
    child_id: int

    model_config = {"from_attributes": True}


class MilestoneStatusOut(BaseModel):
    """Milestone response with developmental phase examples and achieved status."""

    age_phase: str
    focus: str
    title: str
    achieved: bool


class WeeklyProgress(BaseModel):
    """Aggregated weekly completion stats for a child."""

    child_id: int
    week_start: date
    total_tasks: int
    completed_tasks: int
    completion_rate: float


# ---------- Daily check-in schemas ----------
class DailyCheckinCreate(BaseModel):
    """Payload for logging a joy score and optional parent notes."""

    joy_score: int = Field(..., ge=1, le=5)
    parent_notes: str = ""


class DailyCheckinOut(BaseModel):
    """Response model for persisted daily check-ins."""

    id: int
    child_id: int
    joy_score: int
    parent_notes: str | None
    checkin_date: date

    model_config = {"from_attributes": True}

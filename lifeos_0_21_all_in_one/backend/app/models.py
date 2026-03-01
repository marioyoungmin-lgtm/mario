"""SQLAlchemy ORM models for LifeOS 0-21 backend domain."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ChildProfile(Base):
    """Represents a child profile managed by parent/guardian preferences."""

    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    interests: Mapped[list[str]] = mapped_column(JSONB, default=list)
    parent_priority: Mapped[str] = mapped_column(String(120), nullable=False)

    # Child has many daily tasks, milestones, and optional daily check-ins.
    tasks: Mapped[list["DailyTask"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    checkins: Mapped[list["DailyCheckin"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )


class DailyTask(Base):
    """Represents one assigned daily task under a development pillar."""

    __tablename__ = "daily_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child_profiles.id"), nullable=False)
    pillar: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=20)
    difficulty_level: Mapped[str] = mapped_column(String(20), default="medium")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    date_assigned: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    child: Mapped[ChildProfile] = relationship(back_populates="tasks")


class Milestone(Base):
    """Tracks phase-based growth milestones for a child profile."""

    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child_profiles.id"), nullable=False)
    age_phase: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    achieved: Mapped[bool] = mapped_column(Boolean, default=False)

    child: Mapped[ChildProfile] = relationship(back_populates="milestones")


class DailyCheckin(Base):
    """Stores joy score and notes used for personalization of future tasks."""

    __tablename__ = "daily_checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child_profiles.id"), nullable=False)
    joy_score: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    checkin_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    child: Mapped[ChildProfile] = relationship(back_populates="checkins")

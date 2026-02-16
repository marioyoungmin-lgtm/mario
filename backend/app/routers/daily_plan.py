"""Daily planning routes for AI-generated child tasks."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/daily-plan", tags=["daily_plan"])


@router.get("/{child_id}", response_model=list[schemas.DailyTaskOut])
async def get_daily_plan(child_id: int, db: AsyncSession = Depends(get_db)):
    """Generate and return today's 5-task plan for a child profile."""
    tasks = await crud.generate_daily_plan(db, child_id)
    if not tasks:
        raise HTTPException(status_code=404, detail="Child profile not found")
    return tasks


@router.get("/{child_id}/weekly-progress", response_model=schemas.WeeklyProgress)
async def get_weekly_progress(child_id: int, db: AsyncSession = Depends(get_db)):
    """Return completion metrics for the current week."""
    return await crud.fetch_weekly_progress(db, child_id)


@router.post("/{child_id}/checkin", response_model=schemas.DailyCheckinOut)
async def create_daily_checkin(
    child_id: int,
    payload: schemas.DailyCheckinCreate,
    db: AsyncSession = Depends(get_db),
):
    """Store daily joy score + notes for personalization signals."""
    checkin = await crud.create_daily_checkin(db, child_id, payload)
    if checkin is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    return checkin


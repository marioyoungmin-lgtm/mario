"""Task update routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/complete_task", response_model=schemas.DailyTaskOut)
async def complete_task(
    payload: schemas.CompleteTaskRequest,
    db: AsyncSession = Depends(get_db),
):
    """Toggle task completion status."""
    updated = await crud.update_task_status(db, payload.task_id, payload.completed)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

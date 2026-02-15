"""Milestone routes for developmental phase tracking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/milestones", tags=["milestones"])


@router.get("/{child_id}", response_model=list[schemas.MilestoneStatusOut])
async def list_milestones(child_id: int, db: AsyncSession = Depends(get_db)):
    """Return milestone examples per phase with achieved status for a child."""
    profile = await crud.get_profile(db, child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")

    return await crud.get_milestones_for_child(db, child_id)

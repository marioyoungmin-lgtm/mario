"""Child profile routes for LifeOS 0-21."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=schemas.ChildProfileOut, status_code=status.HTTP_201_CREATED)
async def create_child_profile(
    payload: schemas.ChildProfileCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new child profile."""
    return await crud.create_profile(db, payload)


@router.get("/{child_id}", response_model=schemas.ChildProfileOut)
async def get_child_profile(child_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch one child profile by ID."""
    profile = await crud.get_profile(db, child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    return profile

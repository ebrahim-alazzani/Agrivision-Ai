"""Pest database and management endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.domain.models import Pest, User
from backend.domain.schemas import PestResponse
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/pests", tags=["Pests"])


@router.get("", response_model=List[PestResponse])
async def list_pests(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List known agricultural pests."""
    stmt = select(Pest).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{pest_id}", response_model=PestResponse)
async def get_pest(
    pest_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get pest details, lifecycle, and control methods."""
    pest = await db.get(Pest, pest_id)
    if not pest:
        raise HTTPException(status_code=404, detail="Pest not found")
    return pest

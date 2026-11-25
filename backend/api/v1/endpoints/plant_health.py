"""Plant health and disease endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_current_user
from backend.domain.models import Crop, Disease, User
from backend.domain.schemas import DiseaseResponse
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/plant-health", tags=["Plant Health"])


@router.get("/diseases", response_model=List[DiseaseResponse])
async def list_diseases(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List known crop diseases."""
    stmt = select(Disease).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/diseases/{disease_id}", response_model=DiseaseResponse)
async def get_disease(
    disease_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get detailed information, symptoms, and treatment for a specific disease."""
    disease = await db.get(Disease, disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease


@router.get("/crops/{crop_id}/diseases", response_model=List[DiseaseResponse])
async def get_diseases_for_crop(
    crop_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List all diseases known to afflict a specific crop."""
    stmt = (
        select(Crop)
        .where(Crop.id == crop_id)
        .options(selectinload(Crop.diseases))
    )
    result = await db.execute(stmt)
    crop = result.scalars().first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop.diseases

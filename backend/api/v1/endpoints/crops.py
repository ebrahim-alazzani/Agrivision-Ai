"""Crop endpoints (CRUD, list supported crops for AI inference)."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_current_active_admin, get_current_user
from backend.domain.models import Crop, User
from backend.domain.schemas import CropCreate, CropResponse, CropUpdate
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.get("", response_model=List[CropResponse])
async def list_crops(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List all registered crops."""
    stmt = (
        select(Crop)
        .options(selectinload(Crop.varieties), selectinload(Crop.growth_stages))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/supported", response_model=List[CropResponse])
async def list_supported_crops(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List crops currently supported by AI vision and diagnostics engines."""
    stmt = (
        select(Crop)
        .where(Crop.is_supported == True)
        .options(selectinload(Crop.varieties), selectinload(Crop.growth_stages))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get crop by ID."""
    stmt = (
        select(Crop)
        .where(Crop.id == crop_id)
        .options(selectinload(Crop.varieties), selectinload(Crop.growth_stages))
    )
    result = await db.execute(stmt)
    crop = result.scalars().first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop


@router.post("", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_in: CropCreate,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new crop (Admin only)."""
    crop = Crop(
        name=crop_in.name,
        name_ar=crop_in.name_ar,
        scientific_name=crop_in.scientific_name,
        description=crop_in.description,
        description_ar=crop_in.description_ar,
        is_supported=crop_in.is_supported,
        icon_url=crop_in.icon_url,
    )
    db.add(crop)
    await db.commit()
    await db.refresh(crop)
    return crop


@router.put("/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: uuid.UUID,
    crop_in: CropUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Update crop details (Admin only)."""
    crop = await db.get(Crop, crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    for field, value in crop_in.model_dump(exclude_unset=True).items():
        setattr(crop, field, value)

    await db.commit()
    await db.refresh(crop)
    return crop

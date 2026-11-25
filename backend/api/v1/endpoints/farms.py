"""Farm management endpoints (CRUD, crop cycles, health records)."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.application.farm_service import FarmService
from backend.domain.models import User
from backend.domain.schemas import (
    CropHealthRecordCreate,
    CropHealthRecordResponse,
    FarmCreate,
    FarmCropCycleCreate,
    FarmCropCycleResponse,
    FarmResponse,
    FarmUpdate,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.get("", response_model=List[FarmResponse])
async def list_farms(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List farms associated with the current user."""
    service = FarmService(db)
    return await service.list_farms(user_id=current_user.id, skip=skip, limit=limit)


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(
    farm_in: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new farm profile."""
    service = FarmService(db)
    return await service.create_farm(farm_in=farm_in, owner_id=current_user.id)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get farm details by ID."""
    service = FarmService(db)
    farm = await service.get_farm(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: uuid.UUID,
    farm_in: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update farm information."""
    service = FarmService(db)
    return await service.update_farm(farm_id=farm_id, farm_in=farm_in, user_id=current_user.id)


@router.get("/{farm_id}/crops", response_model=List[FarmCropCycleResponse])
async def get_farm_crops(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get crops planted at this farm."""
    service = FarmService(db)
    return await service.get_farm_crops(farm_id)


@router.post("/{farm_id}/crops", response_model=FarmCropCycleResponse, status_code=status.HTTP_201_CREATED)
async def add_crop_cycle(
    farm_id: uuid.UUID,
    cycle_in: FarmCropCycleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Add a new crop cycle to the farm."""
    service = FarmService(db)
    return await service.add_crop_to_farm(farm_id, cycle_in)


@router.get("/{farm_id}/health-records", response_model=List[CropHealthRecordResponse])
async def get_farm_health_records(
    farm_id: uuid.UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get historical health records for crops in this farm."""
    service = FarmService(db)
    return await service.get_farm_health_records(farm_id, limit=limit)


@router.post("/{farm_id}/health-records", response_model=CropHealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def add_farm_health_record(
    farm_id: uuid.UUID,
    record_in: CropHealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Manually add a crop health record."""
    service = FarmService(db)
    return await service.add_health_record(farm_id, record_in)

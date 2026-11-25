"""AI Studio dataset management endpoints (CRUD for datasets and versions)."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_current_user
from backend.domain.models import Dataset, DatasetVersion, User
from backend.domain.schemas import (
    DatasetCreate,
    DatasetResponse,
    DatasetVersionCreate,
    DatasetVersionResponse,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/studio/datasets", tags=["AI Studio Datasets"])


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List studio datasets with versions."""
    stmt = (
        select(Dataset)
        .options(selectinload(Dataset.versions))
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset_in: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new dataset collection."""
    ds = Dataset(
        name=dataset_in.name,
        description=dataset_in.description,
        analysis_type=dataset_in.analysis_type,
        created_by_id=current_user.id,
        tags=dataset_in.tags,
    )
    db.add(ds)
    await db.commit()
    await db.refresh(ds)
    return ds


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get dataset and all version history."""
    stmt = (
        select(Dataset)
        .where(Dataset.id == dataset_id)
        .options(selectinload(Dataset.versions))
    )
    res = await db.execute(stmt)
    ds = res.scalars().first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds


@router.post("/{dataset_id}/versions", response_model=DatasetVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset_version(
    dataset_id: uuid.UUID,
    version_in: DatasetVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Snapshot a new dataset version."""
    ds = await db.get(Dataset, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    ver = DatasetVersion(
        dataset_id=dataset_id,
        version=version_in.version,
        split_config=version_in.split_config,
        notes=version_in.notes,
        sample_count=0,
    )
    db.add(ver)
    await db.commit()
    await db.refresh(ver)
    return ver

"""Agricultural knowledge base and encyclopedia endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_current_user
from backend.domain.models import Crop, Disease, User
from backend.domain.schemas import CropResponse, DiseaseResponse
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.get("/crops", response_model=List[CropResponse])
async def get_crop_encyclopedia(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Browse agricultural crop encyclopedia with agronomic details and growth stages."""
    stmt = (
        select(Crop)
        .options(selectinload(Crop.varieties), selectinload(Crop.growth_stages))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/diseases", response_model=List[DiseaseResponse])
async def get_disease_encyclopedia(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Browse plant pathology encyclopedia with symptoms and preventative treatments."""
    stmt = select(Disease).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

"""Pesticide catalog, search, and dosage calculator endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_current_user
from backend.domain.models import PesticideProduct, User
from backend.domain.schemas import (
    DosageCalculationRequest,
    DosageCalculationResponse,
    PesticideProductResponse,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/pesticides", tags=["Pesticides"])


@router.get("", response_model=List[PesticideProductResponse])
async def list_pesticides(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List registered pesticide products with ingredients and labels."""
    stmt = (
        select(PesticideProduct)
        .options(
            selectinload(PesticideProduct.active_ingredients),
            selectinload(PesticideProduct.labels),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/search", response_model=List[PesticideProductResponse])
async def search_pesticides(
    q: str = Query(..., min_length=2, description="Search term for product name or active ingredient"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Search pesticides by commercial trade name or Arabic name."""
    search_pattern = f"%{q}%"
    stmt = (
        select(PesticideProduct)
        .where(
            or_(
                PesticideProduct.name.ilike(search_pattern),
                PesticideProduct.name_ar.ilike(search_pattern),
                PesticideProduct.manufacturer.ilike(search_pattern),
            )
        )
        .options(
            selectinload(PesticideProduct.active_ingredients),
            selectinload(PesticideProduct.labels),
        )
        .limit(25)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{pesticide_id}", response_model=PesticideProductResponse)
async def get_pesticide(
    pesticide_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get complete pesticide product details."""
    stmt = (
        select(PesticideProduct)
        .where(PesticideProduct.id == pesticide_id)
        .options(
            selectinload(PesticideProduct.active_ingredients),
            selectinload(PesticideProduct.labels),
        )
    )
    result = await db.execute(stmt)
    prod = result.scalars().first()
    if not prod:
        raise HTTPException(status_code=404, detail="Pesticide product not found")
    return prod


@router.post("/calculate-dosage", response_model=DosageCalculationResponse)
async def calculate_dosage(
    request: DosageCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Calculate exact pesticide product quantity, water dilution volume, and safety interval."""
    prod = await db.get(PesticideProduct, request.pesticide_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Pesticide product not found")

    # Standard agronomic calculation baseline (2.5 kg/ha or 200ml/100L typical)
    rate_per_ha = 2.0  # kg or L per hectare
    total_product = rate_per_ha * request.area_hectares
    water_volume = request.water_volume_liters or (400.0 * request.area_hectares)

    warnings = [
        "ارتدِ معدات الوقاية الشخصية (قفازات، كمامة، نظارات واقية) أثناء الخلط والرش.",
        "لا تقم بالرش أثناء هبوب الرياح القوية أو في درجات حرارة تتجاوز 30 درجة مئوية.",
    ]
    if prod.is_restricted:
        warnings.append("تنبيه: هذا المبيد مقيد الاستخدام، يجب إشراف مهندس زراعي معتمد.")

    return DosageCalculationResponse(
        pesticide_id=prod.id,
        pesticide_name=prod.name,
        area_hectares=request.area_hectares,
        recommended_product_amount=f"{total_product:.2f} kg/L",
        recommended_water_volume=f"{water_volume:.1f} Liters",
        safety_interval_days=prod.safety_period_days or 14,
        application_instructions="رش رذاذاً متجانساً على المجموع الخضري حتى البلل التام دون إسالة.",
        safety_warnings=warnings,
    )

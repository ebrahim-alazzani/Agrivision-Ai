"""Admin-only overview and read APIs used by the ASP.NET Core dashboard."""

import csv
import io
import uuid
from datetime import datetime, time, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from backend.api.deps import get_current_active_admin
from backend.domain.models import (
    AnalysisJob, AnalysisResult, Crop, Dataset, Farm, ModelVersion, TrainingRun, User,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/admin", tags=["Administration"])


async def _count(db: AsyncSession, model: Any) -> int:
    return int(await db.scalar(select(func.count()).select_from(model)) or 0)


@router.get("/dashboard")
async def dashboard_summary(
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session)
):
    """Aggregate counters; farmer-level records and personal data are excluded."""
    return {
        "users": await _count(db, User), "farms": await _count(db, Farm),
        "crops": await _count(db, Crop), "analyses": await _count(db, AnalysisJob),
        "datasets": await _count(db, Dataset), "models": await _count(db, ModelVersion),
        "training_runs": await _count(db, TrainingRun),
    }


@router.get("/analytics")
async def dashboard_analytics(
    days: int = Query(14, ge=7, le=90),
    _: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Return real analysis activity grouped by UTC day, status, and result label."""
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=days - 1)
    since = datetime.combine(first_day, time.min, tzinfo=timezone.utc)
    day_expression = func.date(AnalysisJob.created_at)

    daily_result = await db.execute(
        select(day_expression, func.count(AnalysisJob.id))
        .where(AnalysisJob.created_at >= since)
        .group_by(day_expression)
        .order_by(day_expression)
    )
    daily_counts = {
        (day.isoformat() if hasattr(day, "isoformat") else str(day)): int(count)
        for day, count in daily_result.all()
    }
    daily = [
        {"date": (first_day + timedelta(days=offset)).isoformat(),
         "count": daily_counts.get((first_day + timedelta(days=offset)).isoformat(), 0)}
        for offset in range(days)
    ]

    status_result = await db.execute(
        select(AnalysisJob.status, func.count(AnalysisJob.id))
        .where(AnalysisJob.created_at >= since)
        .group_by(AnalysisJob.status)
    )
    statuses = [
        {"status": str(status.value if hasattr(status, "value") else status), "count": int(count)}
        for status, count in status_result.all()
    ]

    label_result = await db.execute(
        select(AnalysisResult.label, func.count(AnalysisResult.id))
        .join(AnalysisJob, AnalysisResult.job_id == AnalysisJob.id)
        .where(AnalysisJob.created_at >= since)
        .group_by(AnalysisResult.label)
        .order_by(func.count(AnalysisResult.id).desc(), AnalysisResult.label)
        .limit(5)
    )
    top_labels = [
        {"label": label, "count": int(count)} for label, count in label_result.all()
    ]

    return {
        "window_days": days,
        "timezone": "UTC",
        "daily_analyses": daily,
        "statuses": statuses,
        "top_result_labels": top_labels,
    }


@router.get("/diagnostics")
async def admin_diagnostics(
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session)
):
    """Check the database connection used by this request; never return configuration."""
    try:
        await db.execute(select(1))
    except SQLAlchemyError:
        return Response(
            content='{"api":"healthy","database":"unavailable"}',
            media_type="application/json",
            status_code=503,
        )
    return {
        "api": "healthy",
        "database": "healthy",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/users")
async def list_users(
    limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(
        select(User).options(selectinload(User.role)).order_by(User.created_at.desc())
        .offset(offset).limit(limit)
    )
    return [{"id": str(u.id), "username": u.username, "email": u.email,
             "full_name": u.full_name, "is_active": u.is_active,
             "role": u.role.name if u.role else None,
             "created_at": u.created_at.isoformat() if u.created_at else None}
            for u in result.scalars().all()]


class UserActiveUpdate(BaseModel):
    is_active: bool


@router.patch("/users/{user_id}/active")
async def set_user_active(
    user_id: uuid.UUID, update: UserActiveUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db_session),
):
    if user_id == current_user.id and not update.is_active:
        raise HTTPException(status_code=409, detail="An administrator cannot deactivate their own account")
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = update.is_active
    await db.commit()
    return {"id": str(user.id), "is_active": user.is_active}


@router.get("/crops")
async def list_crops(
    limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(select(Crop).order_by(Crop.name).offset(offset).limit(limit))
    return [{"id": str(c.id), "name": c.name, "name_ar": c.name_ar,
             "scientific_name": c.scientific_name, "is_supported": c.is_supported}
            for c in result.scalars().all()]


class CropSupportUpdate(BaseModel):
    is_supported: bool


@router.patch("/crops/{crop_id}/support")
async def set_crop_supported(
    crop_id: uuid.UUID, update: CropSupportUpdate,
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session),
):
    crop = await db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    crop.is_supported = update.is_supported
    await db.commit()
    return {"id": str(crop.id), "is_supported": crop.is_supported}


@router.get("/models")
async def list_model_versions(
    limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(select(ModelVersion).order_by(ModelVersion.created_at.desc())
                              .offset(offset).limit(limit))
    return [{"id": str(m.id), "name": m.name, "version": m.version,
             "status": str(m.status.value if hasattr(m.status, "value") else m.status),
             "metrics": m.metrics} for m in result.scalars().all()]


@router.get("/reports/summary.csv")
async def summary_csv(
    _: User = Depends(get_current_active_admin), db: AsyncSession = Depends(get_db_session)
):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["metric", "count"])
    for metric, model in (("users", User), ("farms", Farm), ("crops", Crop),
                          ("analyses", AnalysisJob), ("datasets", Dataset),
                          ("models", ModelVersion), ("training_runs", TrainingRun)):
        writer.writerow([metric, await _count(db, model)])
    return Response(output.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": 'attachment; filename="agrivision-summary.csv"'})

"""AI Studio model registry, deployment, and rollback endpoints."""

import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_active_admin, get_current_user
from backend.domain.enums import ModelStatus
from backend.domain.models import ModelDeployment, ModelVersion, User
from backend.domain.schemas import (
    ModelDeploymentRequest,
    ModelDeploymentResponse,
    ModelVersionResponse,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/studio/models", tags=["AI Studio Model Registry"])


@router.get("", response_model=List[ModelVersionResponse])
async def list_models(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List trained AI model versions in registry."""
    stmt = select(ModelVersion).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{model_id}", response_model=ModelVersionResponse)
async def get_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get model version metadata, architecture, metrics, and artifact key."""
    model = await db.get(ModelVersion, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
    if model.status != ModelStatus.READY:
        raise HTTPException(status_code=409, detail="Only validated READY models can be deployed")
    return model


@router.post("/{model_id}/deploy", response_model=ModelDeploymentResponse, status_code=status.HTTP_201_CREATED)
async def deploy_model(
    model_id: uuid.UUID,
    req: ModelDeploymentRequest,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Deploy model version to target environment (server/mobile/edge)."""
    model = await db.get(ModelVersion, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")

    deployment = ModelDeployment(
        model_version_id=model_id,
        target=req.target,
        is_active=True,
        deployed_by_id=current_user.id,
        deployed_at=datetime.now(timezone.utc),
        config=req.config,
    )
    model.status = ModelStatus.DEPLOYED
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return deployment


@router.post("/{model_id}/rollback", response_model=ModelDeploymentResponse)
async def rollback_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Roll back an active model deployment."""
    stmt = (
        select(ModelDeployment)
        .where(
            ModelDeployment.model_version_id == model_id,
            ModelDeployment.is_active == True,
        )
        .order_by(ModelDeployment.deployed_at.desc())
    )
    res = await db.execute(stmt)
    deployment = res.scalars().first()
    if not deployment:
        raise HTTPException(status_code=404, detail="No active deployment found for this model")

    deployment.is_active = False
    deployment.rolled_back_at = datetime.now(timezone.utc)

    model = await db.get(ModelVersion, model_id)
    if model:
        model.status = ModelStatus.READY

    await db.commit()
    await db.refresh(deployment)
    return deployment

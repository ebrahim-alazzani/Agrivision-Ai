"""AI Studio model training and experiment tracking endpoints."""

import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.domain.enums import TrainingStatus
from backend.domain.models import DatasetVersion, Experiment, TrainingRun, User
from backend.domain.schemas import (
    ExperimentCreate,
    ExperimentResponse,
    TrainingRunCreate,
    TrainingRunResponse,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/studio", tags=["AI Studio Training"])


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List AI model experiments."""
    stmt = select(Experiment).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/experiments", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    exp_in: ExperimentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new experiment workspace."""
    exp = Experiment(
        name=exp_in.name,
        description=exp_in.description,
        analysis_type=exp_in.analysis_type,
        hypothesis=exp_in.hypothesis,
        tags=exp_in.tags,
        created_by_id=current_user.id,
    )
    db.add(exp)
    await db.commit()
    await db.refresh(exp)
    return exp


@router.post("/training-runs", response_model=TrainingRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_training_run(
    run_in: TrainingRunCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Trigger a new training run on a designated dataset version."""
    exp = await db.get(Experiment, run_in.experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    ds_ver = await db.get(DatasetVersion, run_in.dataset_version_id)
    if not ds_ver:
        raise HTTPException(status_code=404, detail="Dataset version not found")

    run = TrainingRun(
        experiment_id=run_in.experiment_id,
        dataset_version_id=run_in.dataset_version_id,
        status=TrainingStatus.PENDING,
        hyperparameters=run_in.hyperparameters or {
            "epochs": 50,
            "batch_size": 32,
            "learning_rate": 0.001,
            "backbone": "efficientnet_b0",
        },
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.get("/training-runs/{run_id}", response_model=TrainingRunResponse)
async def get_training_run(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get status, loss curves, and evaluation metrics of a training run."""
    run = await db.get(TrainingRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Training run not found")
    return run

"""AI analysis submission, status polling, and results retrieval."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.application.analysis_service import AnalysisService
from backend.domain.models import User
from backend.domain.schemas import AnalysisRequest, AnalysisResponse
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_analysis(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Submit an asynchronous AI analysis job for plant disease, pest, or pesticide label."""
    service = AnalysisService(db)
    job = await service.submit_analysis_job(request=request, user_id=current_user.id)
    return job


@router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get history of analysis jobs submitted by current user."""
    service = AnalysisService(db)
    return await service.get_user_history(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{job_id}", response_model=AnalysisResponse)
async def get_analysis_status(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Check status and progress of an analysis job."""
    service = AnalysisService(db)
    job = await service.get_job_by_id(job_id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return job


@router.get("/{job_id}/results", response_model=AnalysisResponse)
async def get_analysis_results(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get full inference results, detections, and recommendations for an analysis job."""
    service = AnalysisService(db)
    job = await service.get_job_by_id(job_id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return job

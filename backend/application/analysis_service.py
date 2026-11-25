"""Analysis service for orchestrating AI analysis pipeline and async job submission."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from backend.domain.enums import AnalysisStatus, AnalysisType, SeverityLevel
from backend.domain.models import AnalysisJob, AnalysisResult, MediaAsset
from backend.domain.schemas import AnalysisRequest


class AnalysisService:
    """Service orchestrating AI analysis job creation, queue dispatch, and result fetching."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_analysis_job(
        self, request: AnalysisRequest, user_id: uuid.UUID
    ) -> AnalysisJob:
        """Create an analysis job and enqueue for async worker processing."""
        # Verify media exists
        media = await self.db.get(MediaAsset, request.media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found"
            )

        job = AnalysisJob(
            user_id=user_id,
            media_id=request.media_id,
            analysis_type=request.analysis_type,
            status=AnalysisStatus.PENDING,
            priority=request.priority,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # Trigger Celery worker task asynchronously
        try:
            from backend.workers.analysis_worker import process_analysis_job
            process_analysis_job.delay(str(job.id))
        except Exception:
            # If celery is not running in local test environment, we still keep job in pending/queued
            job.status = AnalysisStatus.QUEUED
            await self.db.commit()

        return job

    async def get_job_by_id(
        self, job_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> Optional[AnalysisJob]:
        """Fetch analysis job by ID with results."""
        stmt = (
            select(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .options(selectinload(AnalysisJob.results))
        )
        if user_id:
            stmt = stmt.where(AnalysisJob.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_history(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> List[AnalysisJob]:
        """Fetch history of analysis jobs for a user."""
        stmt = (
            select(AnalysisJob)
            .where(AnalysisJob.user_id == user_id)
            .options(selectinload(AnalysisJob.results))
            .order_by(AnalysisJob.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def complete_job_with_results(
        self,
        job_id: uuid.UUID,
        results_data: List[dict],
        processing_time_ms: int,
        error_message: Optional[str] = None,
    ) -> AnalysisJob:
        """Called by worker to record analysis completion."""
        job = await self.db.get(AnalysisJob, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job.completed_at = datetime.now(timezone.utc)
        job.processing_time_ms = processing_time_ms

        if error_message:
            job.status = AnalysisStatus.FAILED
            job.error_message = error_message
        else:
            job.status = AnalysisStatus.COMPLETED
            for item in results_data:
                res = AnalysisResult(
                    job_id=job.id,
                    label=item.get("label", "Unknown"),
                    confidence=float(item.get("confidence", 0.0)),
                    severity=item.get("severity", SeverityLevel.LOW),
                    bounding_box=item.get("bounding_box"),
                    segmentation_mask_key=item.get("segmentation_mask_key"),
                    details=item.get("details"),
                    recommendations=item.get("recommendations"),
                )
                self.db.add(res)

        await self.db.commit()
        await self.db.refresh(job)
        return job

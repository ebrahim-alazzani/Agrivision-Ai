"""User feedback and diagnostic correction endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.domain.models import AnalysisJob, FeedbackRecord, User
from backend.domain.schemas import FeedbackCreate, FeedbackResponse
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Submit user confirmation or agronomist correction for an AI diagnosis."""
    job = await db.get(AnalysisJob, feedback_in.analysis_job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    rec = FeedbackRecord(
        user_id=current_user.id,
        analysis_job_id=feedback_in.analysis_job_id,
        feedback_type=feedback_in.feedback_type,
        correct_label=feedback_in.correct_label,
        comment=feedback_in.comment,
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec

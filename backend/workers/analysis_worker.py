"""Celery worker task for processing asynchronous AI inference jobs."""

import time
import uuid
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.domain.enums import AnalysisStatus, AnalysisType, SeverityLevel
from backend.domain.models import AnalysisJob, AnalysisResult
from backend.infrastructure.config import get_settings

settings = get_settings()

celery_app = Celery(
    "agrivision_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Sync engine for Celery tasks
sync_engine = create_engine(settings.database_url_sync, pool_pre_ping=True)


@celery_app.task(name="tasks.process_analysis_job", bind=True, max_retries=3)
def process_analysis_job(self, job_id_str: str) -> dict:
    """Execute AI inference pipeline for an uploaded media asset."""
    start_time = time.time()
    job_uuid = uuid.UUID(job_id_str)

    with Session(sync_engine) as session:
        job = session.get(AnalysisJob, job_uuid)
        if not job:
            return {"error": "Job not found"}

        job.status = AnalysisStatus.PROCESSING
        session.commit()

        try:
            # Simulated inference logic based on analysis_type
            # In production, this loads ONNX/TensorRT or calls torch engine
            results = []
            if job.analysis_type == AnalysisType.DISEASE_DETECTION:
                results.append(
                    AnalysisResult(
                        job_id=job.id,
                        label="Tomato Early Blight (Alternaria solani)",
                        confidence=0.942,
                        severity=SeverityLevel.MODERATE,
                        bounding_box={"x_min": 0.12, "y_min": 0.24, "x_max": 0.58, "y_max": 0.72},
                        details={
                            "affected_leaf_area_pct": 28.5,
                            "pathogen_type": "Fungal",
                            "scientific_name": "Alternaria solani",
                        },
                        recommendations={
                            "ar": "قم بإزالة الأوراق المصابة فوراً ورش مركب نحاسي وقائي. تجنب الري بالرشاشات على الأوراق.",
                            "en": "Remove infected leaves immediately and apply a copper-based fungicide. Avoid overhead watering.",
                            "pesticide_suggestions": ["Copper Oxychloride 50% WP", "Mancozeb 75% WP"],
                        },
                    )
                )
            elif job.analysis_type == AnalysisType.PEST_DETECTION:
                results.append(
                    AnalysisResult(
                        job_id=job.id,
                        label="Whitefly (Bemisia tabaci)",
                        confidence=0.887,
                        severity=SeverityLevel.HIGH,
                        bounding_box={"x_min": 0.35, "y_min": 0.40, "x_max": 0.65, "y_max": 0.80},
                        details={"pest_count": 14, "nymph_presence": True},
                        recommendations={
                            "ar": "استخدم المصائد الصفراء اللاصقة ورش زيت النيم أو مبيد حشري مناسب لتجنب نقل فيروس تجعد أوراق الطماطم.",
                            "en": "Deploy yellow sticky traps and apply Neem oil or an approved insecticide to prevent TYLCV spread.",
                        },
                    )
                )
            elif job.analysis_type == AnalysisType.PESTICIDE_LABEL:
                results.append(
                    AnalysisResult(
                        job_id=job.id,
                        label="Label OCR Analysis",
                        confidence=0.975,
                        severity=SeverityLevel.NONE,
                        details={
                            "product_name": "Ridomil Gold MZ",
                            "active_ingredients": ["Mefenoxam 4%", "Mancozeb 64%"],
                            "target_crops": ["Potato", "Tomato", "Grape"],
                            "safety_period_days": 14,
                        },
                        recommendations={
                            "recommended_dosage": "2.5 kg/ha in 400-600 L of water",
                            "safety_notes": "Wear protective gloves and mask. Do not apply near water bodies.",
                        },
                    )
                )
            else:
                results.append(
                    AnalysisResult(
                        job_id=job.id,
                        label="Crop Health Normal",
                        confidence=0.915,
                        severity=SeverityLevel.NONE,
                        details={"canopy_cover_pct": 78.0, "vigor_index": 0.82},
                        recommendations={
                            "ar": "المحصول في حالة صحية جيدة، استمر بالري المنتظم وبرنامج التسميد المعتاد.",
                            "en": "Crop is in healthy state, continue regular irrigation and nutrient schedule.",
                        },
                    )
                )

            for r in results:
                session.add(r)

            elapsed_ms = int((time.time() - start_time) * 1000)
            job.status = AnalysisStatus.COMPLETED
            job.processing_time_ms = elapsed_ms
            session.commit()
            return {"status": "success", "job_id": job_id_str, "duration_ms": elapsed_ms}

        except Exception as exc:
            session.rollback()
            job.status = AnalysisStatus.FAILED
            job.error_message = str(exc)
            session.commit()
            raise self.retry(exc=exc, countdown=5)

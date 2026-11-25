"""
Inference Server Runtime.

Central production runtime hosting all AI vision and detection engines:
- Pre-warms neural models on the primary compute device
- Dispatches analysis tasks across engines
- Provides unified execution pipeline with end-to-end timing and telemetry.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image

from ai.config import DEVICE
from ai.engines.decision_support.context_analyzer import ContextAnalyzer, FarmContext
from ai.engines.decision_support.report_generator import (
    AnalysisReportGenerator,
    ComprehensiveFieldReport,
    TreatmentRecommendation,
)
from ai.engines.pest_detection.detector import PestDetector
from ai.engines.pesticide_knowledge.product_database import PesticideDatabase
from ai.engines.plant_vision.classifier import PlantDiseaseClassifier
from ai.engines.plant_vision.config import PlantVisionConfig
from ai.engines.plant_vision.crop_identifier import CropIdentifier
from ai.engines.plant_vision.severity_estimator import SeverityEstimator
from ai.shared.preprocessing.image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class InferenceServer:
    """
    Unified high-throughput inference engine manager.
    """

    def __init__(
        self,
        device: Optional[str] = None,
        lazy_load: bool = False,
    ) -> None:
        self.device = device or DEVICE
        self.preprocessor = ImagePreprocessor()
        self.pesticide_db = PesticideDatabase()
        self.context_analyzer = ContextAnalyzer()
        self.report_generator = AnalysisReportGenerator()

        # Engine placeholders
        self.disease_classifier: Optional[PlantDiseaseClassifier] = None
        self.crop_identifier: Optional[CropIdentifier] = None
        self.severity_estimator: Optional[SeverityEstimator] = None
        self.pest_detector: Optional[PestDetector] = None

        if not lazy_load:
            self.warmup()

    def warmup(self) -> None:
        """Pre-initializes and warms up models."""
        logger.info("Initializing and warming up AI engines on device %s...", self.device)
        self.disease_classifier = PlantDiseaseClassifier(device=self.device)
        self.crop_identifier = CropIdentifier(device=self.device)
        self.severity_estimator = SeverityEstimator(device=self.device)
        self.pest_detector = PestDetector(device=self.device)
        logger.info("All AI engines successfully initialized and warm.")

    def run_full_diagnosis(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        farm_context: Optional[FarmContext] = None,
        job_id: str = "job_default",
    ) -> ComprehensiveFieldReport:
        """
        Executes end-to-end multi-engine agricultural diagnosis.
        """
        if self.disease_classifier is None:
            self.warmup()

        # 1. Image Quality Verification
        quality = self.preprocessor.assess_quality(image_input)
        if not quality.is_acceptable:
            logger.warning("Image quality warnings detected: %s", quality.issues)

        # 2. Disease classification
        disease_pred = self.disease_classifier.predict(image_input)

        # 3. Crop identification
        crop_pred = self.crop_identifier.predict(image_input)

        # 4. Severity estimation
        severity_pred = self.severity_estimator.predict(image_input)

        # 5. Pest detection
        pest_pred = self.pest_detector.predict(image_input)

        # 6. Contextual epidemiological assessment
        context_assessment = None
        if farm_context:
            context_assessment = self.context_analyzer.analyze(
                predicted_disease=disease_pred.primary_label,
                base_confidence=disease_pred.confidence,
                context=farm_context,
            )

        # 7. Prescribe remedies if disease or pest detected
        treatments: List[TreatmentRecommendation] = []
        if disease_pred.primary_label != "healthy":
            solutions = self.pesticide_db.find_solutions(
                crop=crop_pred.primary_label,
                target_pest_or_disease=disease_pred.primary_label,
            )
            for prod, usage in solutions:
                unit = "g" if prod.formulation_type in ("WP", "WG") else "ml"
                treatments.append(
                    TreatmentRecommendation(
                        category=prod.category,
                        title_ar=f"{prod.trade_name_ar} ({prod.active_ingredient})",
                        title_en=f"{prod.trade_name_en} ({prod.active_ingredient})",
                        description_ar=f"رش بمعدل {usage.rate_ml_or_g_per_100l} {unit} لكل 100 لتر ماء. فترة الأمان قبل الحصاد {usage.phi_days} أيام.",
                        description_en=f"Apply at rate of {usage.rate_ml_or_g_per_100l} {unit} per 100L water. PHI: {usage.phi_days} days.",
                        safety_period_days=usage.phi_days,
                    )
                )

        # 8. Synthesize final dossier report
        report = self.report_generator.generate_report(
            report_id=job_id,
            plant_prediction=disease_pred,
            severity_prediction=severity_pred,
            crop_prediction=crop_pred,
            pest_prediction=pest_pred,
            context_assessment=context_assessment,
            treatments=treatments,
        )

        return report

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "device": str(self.device),
            "engines": {
                "disease_classifier": self.disease_classifier.health_check() if self.disease_classifier else "unloaded",
                "crop_identifier": self.crop_identifier.health_check() if self.crop_identifier else "unloaded",
                "severity_estimator": self.severity_estimator.health_check() if self.severity_estimator else "unloaded",
                "pest_detector": self.pest_detector.health_check() if self.pest_detector else "unloaded",
            },
        }

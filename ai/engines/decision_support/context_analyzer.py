"""
Context Analyzer and Agronomic Fusion Engine.

Merges visual image diagnosis with micro-climate variables, crop growth stage,
historical field infections, and regional epidemiologic patterns.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FarmContext:
    """Environmental and management background for a farm plot."""
    farm_id: str
    governorate: str
    crop: str
    growth_stage: str  # 'seedling', 'vegetative', 'flowering', 'fruiting', 'harvest'
    recent_humidity_pct: Optional[float] = None
    recent_temp_c: Optional[float] = None
    recent_rainfall_mm: Optional[float] = None
    irrigation_method: Optional[str] = "drip"  # 'drip', 'flood', 'sprinkler'
    previous_diseases: List[str] = field(default_factory=list)


@dataclass
class ContextAssessment:
    plausibility_score: float  # 0.0 to 1.0
    is_favorable_environment: bool
    environmental_risks: List[str]
    context_adjusted_confidence: float
    notes: List[str]


class ContextAnalyzer:
    """
    Evaluates epidemiological and contextual fit of model predictions.
    """

    def analyze(
        self,
        predicted_disease: str,
        base_confidence: float,
        context: FarmContext,
    ) -> ContextAssessment:
        """
        Adjusts prediction confidence and identifies environmental disease risk drivers.
        """
        notes: List[str] = []
        env_risks: List[str] = []
        favorable_environment = False
        multiplier = 1.0

        p_lower = predicted_disease.lower()

        # Check fungal blight patterns: thrives in cool-to-moderate temps and high moisture
        if "blight" in p_lower or "mildew" in p_lower or "rot" in p_lower:
            if context.recent_humidity_pct and context.recent_humidity_pct >= 75.0:
                env_risks.append("High relative humidity creates ideal sporulation conditions for fungal pathogens.")
                favorable_environment = True
                multiplier *= 1.10
            if context.irrigation_method == "sprinkler":
                env_risks.append("Overhead sprinkler irrigation prolongs leaf wetness, accelerating pathogen infection.")
                multiplier *= 1.05

        # Check powdery mildew: thrives in dry warm foliage with humid ambient air
        if "powdery_mildew" in p_lower:
            if context.recent_temp_c and 20.0 <= context.recent_temp_c <= 30.0:
                favorable_environment = True
                multiplier *= 1.08

        # Viral vectors (whitefly, aphids) thrive in warm dry weather
        if "virus" in p_lower or "curl" in p_lower:
            if context.recent_temp_c and context.recent_temp_c >= 28.0:
                env_risks.append("Warm temperatures accelerate insect vector reproduction (whiteflies/aphids).")
                favorable_environment = True
                multiplier *= 1.05

        # Check crop history recurrence
        if predicted_disease in context.previous_diseases:
            notes.append(f"Historical presence noted: {predicted_disease} was previously recorded in this plot.")
            multiplier *= 1.08

        adjusted_conf = min(0.99, max(0.10, base_confidence * multiplier))
        plausibility = min(1.0, 0.70 + (0.30 if favorable_environment else 0.10))

        return ContextAssessment(
            plausibility_score=round(plausibility, 2),
            is_favorable_environment=favorable_environment,
            environmental_risks=env_risks,
            context_adjusted_confidence=round(adjusted_conf, 4),
            notes=notes,
        )

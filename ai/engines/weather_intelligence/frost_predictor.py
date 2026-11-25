"""
Frost Risk Predictor.

Analyzes hourly forecast micro-meteorological variables (minimum temperatures,
dew point depression, cloud cover radiative cooling, and wind stillness)
to forecast radiation frost and advection freeze risks, providing actionable farmer alerts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ai.engines.weather_intelligence.config import FrostRiskLevel, WeatherConfig
from ai.engines.weather_intelligence.weather_client import WeatherDataPoint

logger = logging.getLogger(__name__)


@dataclass
class FrostAlert:
    risk_level: FrostRiskLevel
    start_time: str
    end_time: str
    minimum_expected_temp_c: float
    probability: float
    recommendation_ar: str
    recommendation_en: str
    contributing_factors: List[str] = field(default_factory=list)


class FrostRiskPredictor:
    """
    Evaluates micro-climate freeze and frost probability.
    """

    def __init__(self, config: Optional[WeatherConfig] = None) -> None:
        self.config = config or WeatherConfig()

    def evaluate_risk(
        self,
        forecast_points: List[WeatherDataPoint],
        crop_sensitive_stage: bool = True,
    ) -> List[FrostAlert]:
        """
        Scans a sequence of hourly forecast data points and generates frost warnings.
        """
        alerts: List[FrostAlert] = []
        frost_streak: List[WeatherDataPoint] = []

        for pt in forecast_points:
            t = pt.temperature_c
            # Check if within low risk threshold
            if t <= self.config.frost_low_temp_c:
                frost_streak.append(pt)
            else:
                if frost_streak:
                    alert = self._build_alert(frost_streak, crop_sensitive_stage)
                    if alert.risk_level != FrostRiskLevel.NONE:
                        alerts.append(alert)
                    frost_streak = []

        if frost_streak:
            alert = self._build_alert(frost_streak, crop_sensitive_stage)
            if alert.risk_level != FrostRiskLevel.NONE:
                alerts.append(alert)

        return alerts

    def _build_alert(
        self,
        streak: List[WeatherDataPoint],
        crop_sensitive: bool,
    ) -> FrostAlert:
        min_temp = min(pt.temperature_c for pt in streak)
        start_ts = streak[0].timestamp
        end_ts = streak[-1].timestamp

        factors = []
        # Radiative cooling factor: clear skies (< 20% cloud) + low wind (< 5 km/h)
        avg_cloud = sum(pt.cloud_cover_pct for pt in streak) / len(streak)
        avg_wind = sum(pt.wind_speed_kmh for pt in streak) / len(streak)

        if avg_cloud < 25:
            factors.append("سماء صافية تزيد الفقد الإشعاعي (Clear sky accelerating radiative cooling)")
        if avg_wind < 6:
            factors.append("سكون الرياح يمنع تقليب الهواء (Calm wind enabling thermal inversion)")

        # Determine risk level
        if min_temp <= self.config.frost_critical_temp_c:
            level = FrostRiskLevel.CRITICAL
            prob = 0.95
            rec_ar = "خطر صقيع مميت! ابدأ بالري الرذاذي فوراً، وغطِ الشتلات الحساسة، وشغل مصدات الدخان قبل الفجر."
            rec_en = "Critical frost hazard! Start sprinkler irrigation immediately, cover sensitive seedlings, and prepare smudge pots."
        elif min_temp <= self.config.frost_high_temp_c:
            level = FrostRiskLevel.HIGH
            prob = 0.85
            rec_ar = "خطر صقيع شديد. يُنصح بري الحقل مساءً لرفع السعة الحرارية للتربة وتغطية المشاتل."
            rec_en = "High frost risk. Irrigate evening fields to increase soil thermal mass and cover high-value nurseries."
        elif min_temp <= self.config.frost_moderate_temp_c:
            level = FrostRiskLevel.MODERATE
            prob = 0.65
            rec_ar = "احتمال تشكل صقيع خفيف في المنخفضات والوديان. راقب درجات الحرارة السطحية."
            rec_en = "Moderate frost probability in low terrain valleys. Monitor ground temperature."
        else:
            level = FrostRiskLevel.LOW
            prob = 0.40
            rec_ar = "انخفاض ملحوظ في درجات الحرارة ليلاً. لا يتوقع ضرر كبير إلا للأشجار الاستوائية الحساسة."
            rec_en = "Low frost risk. Temperature drops significantly at night; protect delicate tropical canopies."

        if crop_sensitive and level in (FrostRiskLevel.MODERATE, FrostRiskLevel.LOW):
            prob += 0.1

        return FrostAlert(
            risk_level=level,
            start_time=start_ts,
            end_time=end_ts,
            minimum_expected_temp_c=round(min_temp, 1),
            probability=round(min(1.0, prob), 2),
            recommendation_ar=rec_ar,
            recommendation_en=rec_en,
            contributing_factors=factors,
        )

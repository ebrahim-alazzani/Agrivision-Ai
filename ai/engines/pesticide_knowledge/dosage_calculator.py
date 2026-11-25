"""
Agricultural Dosage and Spray Tank Volume Calculator.

Performs deterministic, safety-checked calculations for pesticide application:
- Computes exact formulation volume/mass required per tank size or field area
- Tracks safety constraints (Pre-Harvest Interval - PHI, Re-Entry Interval - REI)
- Provides bilingual step-by-step arithmetic explanations and safety warnings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ai.engines.pesticide_knowledge.product_database import ApprovedUsage, PesticideProduct

logger = logging.getLogger(__name__)


@dataclass
class DosageCalculationResult:
    product_id: str
    product_name_en: str
    product_name_ar: str
    water_volume_liters: float
    required_quantity: float
    unit: str  # 'ml' or 'g'
    phi_days: int
    rei_hours: int
    calculation_steps_ar: List[str]
    calculation_steps_en: List[str]
    safety_precautions_ar: List[str]
    safety_precautions_en: List[str]


class DosageCalculator:
    """
    Calculates precise spray tank pesticide dilution rates.
    """

    @staticmethod
    def calculate_for_tank(
        product: PesticideProduct,
        usage: ApprovedUsage,
        tank_capacity_liters: float,
    ) -> DosageCalculationResult:
        """
        Calculates quantity of pesticide needed for a specific sprayer tank (e.g., 20L knapsack, 200L barrel, 600L tractor).
        """
        if tank_capacity_liters <= 0:
            raise ValueError("Tank capacity must be greater than zero.")

        # Rate is per 100 Liters of water
        rate_per_100l = usage.rate_ml_or_g_per_100l
        factor = tank_capacity_liters / 100.0
        required_qty = round(rate_per_100l * factor, 2)
        unit = "g" if product.formulation_type in ("WP", "WG", "SP") else "ml"

        steps_en = [
            f"1. Approved application rate: {rate_per_100l} {unit} per 100 Liters of water.",
            f"2. Your sprayer tank capacity: {tank_capacity_liters} Liters.",
            f"3. Dilution multiplier: {tank_capacity_liters} / 100 = {factor:.2f}",
            f"4. Required product: {rate_per_100l} * {factor:.2f} = {required_qty} {unit}.",
        ]

        steps_ar = [
            f"1. الجرعة المعتمدة على الملصق: {rate_per_100l} {unit} لكل 100 لتر ماء.",
            f"2. سعة خزان الرش لديك: {tank_capacity_liters} لتر.",
            f"3. معامل التخفيف: {tank_capacity_liters} ÷ 100 = {factor:.2f}",
            f"4. كمية المبيد المطلوبة: {rate_per_100l} × {factor:.2f} = {required_qty} {unit}.",
        ]

        precautions_en = [
            f"Pre-Harvest Interval (PHI): Do not harvest crops for at least {usage.phi_days} days after spraying.",
            f"Re-Entry Interval (REI): Do not enter treated field without protective gear for {usage.rei_hours} hours.",
            "Always wear chemical-resistant gloves, goggles, and mask during mixing and spraying.",
            "Do not spray during strong winds or hottest hours of the day (11 AM - 3 PM).",
        ]

        precautions_ar = [
            f"فترة الأمان قبل الحصاد (PHI): يُحظر حصاد المحصول لمدة {usage.phi_days} يوماً على الأقل بعد الرش.",
            f"فترة إعادة دخول الحقل (REI): يُحظر دخول الحقل دون معدات وقاية لمدة {usage.rei_hours} ساعة.",
            "ارتدِ قفازات وكمامة ونظارة واقية عند خلط ورش المبيد.",
            "تجنب الرش أثناء هبوب الرياح القوية أو وقت الظهيرة والحر الشديد (11 ص - 3 م).",
        ]

        return DosageCalculationResult(
            product_id=product.product_id,
            product_name_en=product.trade_name_en,
            product_name_ar=product.trade_name_ar,
            water_volume_liters=tank_capacity_liters,
            required_quantity=required_qty,
            unit=unit,
            phi_days=usage.phi_days,
            rei_hours=usage.rei_hours,
            calculation_steps_ar=steps_ar,
            calculation_steps_en=steps_en,
            safety_precautions_ar=precautions_ar,
            safety_precautions_en=precautions_en,
        )

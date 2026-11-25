"""
Pesticide Knowledge Database.

Provides authoritative database lookups for registered agricultural plant protection products,
active ingredients, approved target crops, verified dosage rates, and pre-harvest safety intervals.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ApprovedUsage:
    """Official registered label recommendation for a crop-pathogen pair."""
    crop: str
    target: str  # disease or pest name
    rate_ml_or_g_per_100l: float
    rate_per_hectare: Optional[float] = None
    phi_days: int = 7  # Pre-Harvest Interval in days
    rei_hours: int = 24  # Re-Entry Interval in hours
    max_applications: int = 3


@dataclass
class PesticideProduct:
    """Registered commercial agricultural chemical or biological formulation."""
    product_id: str
    trade_name_en: str
    trade_name_ar: str
    active_ingredient: str
    concentration: str
    formulation_type: str  # WP, EC, SC, WG
    category: str          # Fungicide, Insecticide, Acaricide, Bactericide
    who_toxicity_class: str  # Class II (Moderately hazardous), Class III, Class U
    approved_usages: List[ApprovedUsage] = field(default_factory=list)


# Seed reference registry for Yemeni and regional agriculture
_DEFAULT_REGISTRY: List[PesticideProduct] = [
    PesticideProduct(
        product_id="prod_mancozeb_80wp",
        trade_name_en="Dithane M-45",
        trade_name_ar="دايثين م-45",
        active_ingredient="Mancozeb",
        concentration="80% WP",
        formulation_type="WP",
        category="Fungicide",
        who_toxicity_class="Class U (Unlikely to present acute hazard)",
        approved_usages=[
            ApprovedUsage(crop="tomato", target="tomato_early_blight", rate_ml_or_g_per_100l=250.0, phi_days=7),
            ApprovedUsage(crop="tomato", target="tomato_late_blight", rate_ml_or_g_per_100l=250.0, phi_days=7),
            ApprovedUsage(crop="potato", target="potato_late_blight", rate_ml_or_g_per_100l=250.0, phi_days=7),
            ApprovedUsage(crop="grape", target="grape_downy_mildew", rate_ml_or_g_per_100l=200.0, phi_days=21),
        ],
    ),
    PesticideProduct(
        product_id="prod_copper_hydroxide",
        trade_name_en="Kocide 2000",
        trade_name_ar="كوسايد 2000",
        active_ingredient="Copper Hydroxide",
        concentration="53.8% WG",
        formulation_type="WG",
        category="Fungicide/Bactericide",
        who_toxicity_class="Class III (Slightly hazardous)",
        approved_usages=[
            ApprovedUsage(crop="tomato", target="tomato_bacterial_spot", rate_ml_or_g_per_100l=150.0, phi_days=3),
            ApprovedUsage(crop="coffee", target="coffee_leaf_rust", rate_ml_or_g_per_100l=200.0, phi_days=14),
            ApprovedUsage(crop="grape", target="grape_downy_mildew", rate_ml_or_g_per_100l=175.0, phi_days=14),
        ],
    ),
    PesticideProduct(
        product_id="prod_imidacloprid",
        trade_name_en="Confidor 200 SL",
        trade_name_ar="كونفيدور 200",
        active_ingredient="Imidacloprid",
        concentration="200 g/L SL",
        formulation_type="SL",
        category="Insecticide",
        who_toxicity_class="Class II (Moderately hazardous)",
        approved_usages=[
            ApprovedUsage(crop="tomato", target="whitefly", rate_ml_or_g_per_100l=50.0, phi_days=3),
            ApprovedUsage(crop="cucumber", target="aphid", rate_ml_or_g_per_100l=40.0, phi_days=3),
            ApprovedUsage(crop="wheat", target="aphid", rate_ml_or_g_per_100l=100.0, phi_days=14),
        ],
    ),
    PesticideProduct(
        product_id="prod_abamectin",
        trade_name_en="Vertimec 1.8% EC",
        trade_name_ar="فيرتيميك 1.8%",
        active_ingredient="Abamectin",
        concentration="18 g/L EC",
        formulation_type="EC",
        category="Acaricide/Insecticide",
        who_toxicity_class="Class II (Moderately hazardous)",
        approved_usages=[
            ApprovedUsage(crop="tomato", target="tomato_leafminer_tuta_absoluta", rate_ml_or_g_per_100l=50.0, phi_days=7),
            ApprovedUsage(crop="cucumber", target="spider_mite", rate_ml_or_g_per_100l=40.0, phi_days=7),
        ],
    ),
    PesticideProduct(
        product_id="prod_azoxystrobin",
        trade_name_en="Amistar 250 SC",
        trade_name_ar="اميستار 250",
        active_ingredient="Azoxystrobin",
        concentration="250 g/L SC",
        formulation_type="SC",
        category="Fungicide",
        who_toxicity_class="Class U (Unlikely to present acute hazard)",
        approved_usages=[
            ApprovedUsage(crop="tomato", target="tomato_early_blight", rate_ml_or_g_per_100l=80.0, phi_days=3),
            ApprovedUsage(crop="grape", target="grape_powdery_mildew", rate_ml_or_g_per_100l=75.0, phi_days=14),
            ApprovedUsage(crop="wheat", target="wheat_stripe_rust", rate_ml_or_g_per_100l=100.0, phi_days=28),
        ],
    ),
]


class PesticideDatabase:
    """
    Searchable catalog of registered plant protection remedies.
    """

    def __init__(self, products: Optional[List[PesticideProduct]] = None) -> None:
        self.products = products or list(_DEFAULT_REGISTRY)

    def search_by_name(self, query: str) -> List[PesticideProduct]:
        """Case-insensitive search across trade name and active ingredient in English and Arabic."""
        q = query.lower().strip()
        results = []
        for p in self.products:
            if (
                q in p.trade_name_en.lower()
                or q in p.trade_name_ar.lower()
                or q in p.active_ingredient.lower()
            ):
                results.append(p)
        return results

    def find_solutions(
        self,
        crop: str,
        target_pest_or_disease: str,
    ) -> List[Tuple[PesticideProduct, ApprovedUsage]]:
        """
        Finds all verified registered formulations approved for a specific crop and pathogen.
        """
        c = crop.lower().strip()
        t = target_pest_or_disease.lower().strip()
        matches = []

        for p in self.products:
            for u in p.approved_usages:
                if u.crop.lower() == c and (u.target.lower() == t or t in u.target.lower()):
                    matches.append((p, u))
        return matches

    def get_by_id(self, product_id: str) -> Optional[PesticideProduct]:
        for p in self.products:
            if p.product_id == product_id:
                return p
        return None

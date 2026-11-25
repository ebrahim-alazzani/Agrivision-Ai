"""
Temporal Crop Analyzer.

Tracks changes in crop vigor, foliage canopy, and disease spread over time
using sequential image pairs, RGB vegetation indices (VARI, GLI, ExG), and histogram comparison.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class VegetationIndex(str, Enum):
    VARI = "vari"  # Visible Atmospherically Resistant Index: (G - R) / (G + R - B)
    GLI = "gli"    # Green Leaf Index: (2*G - R - B) / (2*G + R + B)
    EXG = "exg"    # Excess Green Index: 2*G - R - B


@dataclass
class TemporalComparisonResult:
    """Quantitative comparison between two chronological crop observations."""
    histogram_similarity: float
    vegetation_index_change: float
    percent_canopy_change: float
    change_status: str  # 'improved', 'stable', 'degraded'
    details: Dict[str, float]


class TemporalAnalyzer:
    """
    Analyzes temporal variation across observation photos of the same crop plot or leaf.
    """

    def __init__(self, target_size: Tuple[int, int] = (512, 512)) -> None:
        self.target_size = target_size

    def compute_vegetation_index(
        self,
        image_rgb: np.ndarray,
        index_type: VegetationIndex = VegetationIndex.VARI,
    ) -> np.ndarray:
        """
        Computes pixel-wise RGB visual vegetation index.
        """
        img = image_rgb.astype(np.float32) / 255.0
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        eps = 1e-6

        if index_type == VegetationIndex.VARI:
            # (Green - Red) / (Green + Red - Blue + eps)
            denom = g + r - b
            denom = np.where(np.abs(denom) < eps, eps, denom)
            vi = (g - r) / denom
            return np.clip(vi, -1.0, 1.0)

        elif index_type == VegetationIndex.GLI:
            # (2*G - R - B) / (2*G + R + B + eps)
            denom = 2 * g + r + b
            denom = np.where(np.abs(denom) < eps, eps, denom)
            vi = (2 * g - r - b) / denom
            return np.clip(vi, -1.0, 1.0)

        elif index_type == VegetationIndex.EXG:
            # 2*G - R - B
            return (2 * g - r - b)

        raise ValueError(f"Unknown index type: {index_type}")

    def compute_histogram_similarity(
        self,
        img_a_bgr: np.ndarray,
        img_b_bgr: np.ndarray,
    ) -> float:
        """
        Computes 3-channel color histogram correlation (range [-1, 1], 1 is identical).
        """
        hist_a = cv2.calcHist([img_a_bgr], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist_b = cv2.calcHist([img_b_bgr], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

        cv2.normalize(hist_a, hist_a, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist_b, hist_b, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        correlation = float(cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL))
        return max(0.0, correlation)

    def compare_observations(
        self,
        image_before: Union[str, Path, np.ndarray],
        image_after: Union[str, Path, np.ndarray],
    ) -> TemporalComparisonResult:
        """
        Compares an earlier photo with a later photo of the same field or plant.
        """
        # Load & resize
        def _load_and_prep(data):
            if isinstance(data, (str, Path)):
                img = cv2.imread(str(data))
                if img is None:
                    raise IOError(f"Could not read image {data}")
            else:
                img = data
            img = cv2.resize(img, self.target_size)
            return img

        bgr1 = _load_and_prep(image_before)
        bgr2 = _load_and_prep(image_after)

        rgb1 = cv2.cvtColor(bgr1, cv2.COLOR_BGR2RGB)
        rgb2 = cv2.cvtColor(bgr2, cv2.COLOR_BGR2RGB)

        # Histogram similarity
        hist_sim = self.compute_histogram_similarity(bgr1, bgr2)

        # Vegetation index
        vi1 = self.compute_vegetation_index(rgb1, VegetationIndex.VARI)
        vi2 = self.compute_vegetation_index(rgb2, VegetationIndex.VARI)

        mean_vi1 = float(np.mean(vi1))
        mean_vi2 = float(np.mean(vi2))
        vi_change = mean_vi2 - mean_vi1

        # Canopy cover (% pixels with VARI > 0.1)
        canopy1 = float(np.mean(vi1 > 0.1) * 100.0)
        canopy2 = float(np.mean(vi2 > 0.1) * 100.0)
        canopy_change = canopy2 - canopy1

        # Classify change status
        if vi_change > 0.08 or canopy_change > 5.0:
            status = "improved"
        elif vi_change < -0.08 or canopy_change < -5.0:
            status = "degraded"
        else:
            status = "stable"

        return TemporalComparisonResult(
            histogram_similarity=round(hist_sim, 4),
            vegetation_index_change=round(vi_change, 4),
            percent_canopy_change=round(canopy_change, 2),
            change_status=status,
            details={
                "initial_vari": round(mean_vi1, 4),
                "subsequent_vari": round(mean_vi2, 4),
                "initial_canopy_coverage_pct": round(canopy1, 2),
                "subsequent_canopy_coverage_pct": round(canopy2, 2),
            },
        )

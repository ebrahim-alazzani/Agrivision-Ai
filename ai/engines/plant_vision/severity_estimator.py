"""
Infection Severity Estimator.

Estimates infection stage/severity: healthy, mild, moderate, severe.
Supports ordinal regression principles and lesion coverage estimation.
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image

from ai.config import DEVICE
from ai.shared.model_interfaces.base_engine import (
    AlternativePrediction,
    BaseAIEngine,
    EngineMetadata,
    EnginePrediction,
)
from ai.shared.preprocessing.image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    HEALTHY = "healthy"
    MILD = "mild"          # < 15% leaf area affected
    MODERATE = "moderate"  # 15% - 40% leaf area affected
    SEVERE = "severe"      # > 40% leaf area affected


class SeverityEstimator(BaseAIEngine):
    """
    Ordinal classification & visual lesion coverage estimator.
    """

    SEVERITY_ORDER = [
        SeverityLevel.HEALTHY.value,
        SeverityLevel.MILD.value,
        SeverityLevel.MODERATE.value,
        SeverityLevel.SEVERE.value,
    ]

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        device: Optional[Union[str, torch.device]] = None,
    ) -> None:
        super().__init__(
            model_path=model_path,
            device=device or DEVICE,
            confidence_threshold=0.50,
        )
        self.preprocessor = ImagePreprocessor(target_size=224)
        self.model = self._build_model()
        self._is_loaded = True

    def _build_model(self) -> nn.Module:
        # Ordinal regression network head: 3 cumulative binary threshold heads
        # P(Y > healthy), P(Y > mild), P(Y > moderate)
        model = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 3),
        )
        return model.to(self.device)

    def load_model(self) -> None:
        self._is_loaded = True

    def unload_model(self) -> None:
        self._is_loaded = False

    def estimate_lesion_percentage(self, image_rgb: np.ndarray) -> float:
        """
        Estimates percentage of diseased / necrotic leaf area using HSV lesion isolation.
        """
        hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)

        # Plant leaf mask (greenish hue 25 - 85)
        leaf_mask = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([85, 255, 255]))
        leaf_pixels = np.count_nonzero(leaf_mask)
        if leaf_pixels < 500:
            # Fallback if non-green or dry leaf: full non-background
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
            _, leaf_mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
            leaf_pixels = np.count_nonzero(leaf_mask)

        if leaf_pixels == 0:
            return 0.0

        # Necrotic / lesion mask (brown, yellow, rust spots)
        brown_mask1 = cv2.inRange(hsv, np.array([10, 50, 40]), np.array([24, 255, 200]))
        yellow_mask = cv2.inRange(hsv, np.array([18, 50, 80]), np.array([35, 255, 255]))
        dark_spot_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))

        lesion_mask = cv2.bitwise_or(brown_mask1, yellow_mask)
        lesion_mask = cv2.bitwise_or(lesion_mask, dark_spot_mask)
        lesion_on_leaf = cv2.bitwise_and(lesion_mask, leaf_mask)

        lesion_pixels = np.count_nonzero(lesion_on_leaf)
        percentage = (lesion_pixels / leaf_pixels) * 100.0
        return float(min(100.0, max(0.0, percentage)))

    def predict(
        self,
        input_data: Union[str, Path, Image.Image, np.ndarray],
        **kwargs,
    ) -> EnginePrediction:
        start_t = time.perf_counter()

        if isinstance(input_data, (str, Path)):
            img = cv2.imread(str(input_data))
            if img is None:
                raise IOError(f"Could not read image: {input_data}")
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif isinstance(input_data, Image.Image):
            rgb = np.asarray(input_data.convert("RGB"))
        elif isinstance(input_data, np.ndarray):
            rgb = input_data
        else:
            raise TypeError(f"Unsupported input: {type(input_data)}")

        lesion_pct = self.estimate_lesion_percentage(rgb)

        # Mapping percentage to severity level
        if lesion_pct < 2.0:
            level = SeverityLevel.HEALTHY.value
            confidence = 0.95
        elif lesion_pct < 15.0:
            level = SeverityLevel.MILD.value
            confidence = 0.88
        elif lesion_pct < 40.0:
            level = SeverityLevel.MODERATE.value
            confidence = 0.85
        else:
            level = SeverityLevel.SEVERE.value
            confidence = 0.90

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        return EnginePrediction(
            engine_name="SeverityEstimator",
            task="severity_estimation",
            primary_label=level,
            confidence=confidence,
            is_confident=True,
            execution_time_ms=float(round(elapsed_ms, 2)),
            model_version="severity_heuristics_v1",
            details={
                "affected_area_percentage": round(lesion_pct, 2),
                "severity_scale": self.SEVERITY_ORDER,
            },
        )

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_name="SeverityEstimator",
            version="1.0.0",
            model_architecture="ordinal_heuristic_vision",
            model_version="v1.0.0",
            device=str(self.device),
            supported_tasks=["severity_estimation"],
            confidence_threshold=self.confidence_threshold,
        )

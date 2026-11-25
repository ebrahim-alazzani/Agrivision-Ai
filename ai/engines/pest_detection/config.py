"""
Configuration and Class Definitions for Pest Detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

DEFAULT_PEST_CLASSES: List[str] = [
    "desert_locust",
    "fall_armyworm",
    "whitefly",
    "aphid",
    "tomato_leafminer_tuta_absoluta",
    "thrips",
    "spider_mite",
    "stem_borer",
    "fruit_fly",
    "caterpillar",
]


@dataclass
class PestDetectionConfig:
    """YOLO / Object Detection Configuration."""
    model_name: str = "yolov8m.pt"
    confidence_threshold: float = 0.40
    iou_threshold: float = 0.45
    image_size: int = 640
    classes: List[str] = field(default_factory=lambda: list(DEFAULT_PEST_CLASSES))
    device: str = "cpu"
    max_detections: int = 300

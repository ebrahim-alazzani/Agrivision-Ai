"""
Configuration and Class Catalogs for Plant Vision Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# Default major agricultural diseases in Yemen & Middle East / East Africa
DEFAULT_DISEASE_CLASSES: List[str] = [
    "healthy",
    "tomato_early_blight",
    "tomato_late_blight",
    "tomato_yellow_leaf_curl_virus",
    "tomato_bacterial_spot",
    "tomato_septoria_leaf_spot",
    "potato_early_blight",
    "potato_late_blight",
    "grape_black_rot",
    "grape_downy_mildew",
    "grape_powdery_mildew",
    "wheat_stripe_rust",
    "wheat_leaf_rust",
    "coffee_leaf_rust",
    "coffee_berry_disease",
    "mango_anthracnose",
    "cucumber_powdery_mildew",
    "onion_purple_blotch",
]

DEFAULT_CROP_CLASSES: List[str] = [
    "tomato",
    "potato",
    "grape",
    "wheat",
    "coffee",
    "mango",
    "cucumber",
    "onion",
    "corn",
    "citrus",
]


@dataclass
class PlantVisionConfig:
    """Configuration for plant disease and crop vision models."""
    architecture: str = "resnet50"  # 'resnet50' | 'efficientnet_b0' | 'mobilenetv3_large_100'
    pretrained: bool = True
    num_classes: int = len(DEFAULT_DISEASE_CLASSES)
    image_size: int = 224
    confidence_threshold: float = 0.65
    top_k: int = 3
    disease_classes: List[str] = field(default_factory=lambda: list(DEFAULT_DISEASE_CLASSES))
    crop_classes: List[str] = field(default_factory=lambda: list(DEFAULT_CROP_CLASSES))
    dropout_rate: float = 0.3

    # Severity levels
    severity_classes: List[str] = field(
        default_factory=lambda: ["healthy", "mild", "moderate", "severe"]
    )

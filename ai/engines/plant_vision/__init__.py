"""
Plant Vision Engine.

Sub-modules for:
- Crop disease classification (ResNet50, EfficientNet-B0, MobileNetV3)
- Crop type identification
- Infection severity estimation (Healthy, Mild, Moderate, Severe)
"""

from ai.engines.plant_vision.config import PlantVisionConfig
from ai.engines.plant_vision.classifier import PlantDiseaseClassifier
from ai.engines.plant_vision.crop_identifier import CropIdentifier
from ai.engines.plant_vision.severity_estimator import SeverityEstimator, SeverityLevel

__all__ = [
    "PlantVisionConfig",
    "PlantDiseaseClassifier",
    "CropIdentifier",
    "SeverityEstimator",
    "SeverityLevel",
]

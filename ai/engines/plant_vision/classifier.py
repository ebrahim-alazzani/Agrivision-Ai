"""
Plant Disease Classifier.

Supports ResNet50, EfficientNet-B0, and MobileNetV3 backbones with customizable
classification heads, multi-class Softmax probabilities, and Top-K alternatives.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import torchvision.models as models

from ai.config import DEVICE
from ai.engines.plant_vision.config import DEFAULT_DISEASE_CLASSES, PlantVisionConfig
from ai.shared.model_interfaces.base_engine import (
    AlternativePrediction,
    BaseAIEngine,
    EngineMetadata,
    EnginePrediction,
)
from ai.shared.preprocessing.image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class DiseaseClassificationHead(nn.Module):
    """Custom multi-layer classification head with dropout and batchnorm."""

    def __init__(self, in_features: int, num_classes: int, dropout_rate: float = 0.3):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


class PlantDiseaseClassifier(BaseAIEngine):
    """
    Production-grade Plant Disease Classification Engine.
    """

    def __init__(
        self,
        config: Optional[PlantVisionConfig] = None,
        model_path: Optional[Union[str, Path]] = None,
        device: Optional[Union[str, torch.device]] = None,
    ) -> None:
        self.config = config or PlantVisionConfig()
        super().__init__(
            model_path=model_path,
            device=device or DEVICE,
            confidence_threshold=self.config.confidence_threshold,
        )
        self.classes = self.config.disease_classes
        self.preprocessor = ImagePreprocessor(target_size=self.config.image_size)
        self.model = self._build_architecture()
        if self.model_path and Path(self.model_path).exists():
            self.load_model()

    def _build_architecture(self) -> nn.Module:
        """Instantiates backbone with custom classification head."""
        arch = self.config.architecture.lower()
        num_classes = len(self.classes)

        if "resnet50" in arch:
            weights = models.ResNet50_Weights.DEFAULT if self.config.pretrained else None
            backbone = models.resnet50(weights=weights)
            in_features = backbone.fc.in_features
            backbone.fc = DiseaseClassificationHead(in_features, num_classes, self.config.dropout_rate)
        elif "efficientnet" in arch:
            weights = models.EfficientNet_B0_Weights.DEFAULT if self.config.pretrained else None
            backbone = models.efficientnet_b0(weights=weights)
            in_features = backbone.classifier[1].in_features
            backbone.classifier = DiseaseClassificationHead(in_features, num_classes, self.config.dropout_rate)
        elif "mobilenet" in arch:
            weights = models.MobileNet_V3_Large_Weights.DEFAULT if self.config.pretrained else None
            backbone = models.mobilenet_v3_large(weights=weights)
            in_features = backbone.classifier[0].in_features
            backbone.classifier = DiseaseClassificationHead(in_features, num_classes, self.config.dropout_rate)
        else:
            raise ValueError(f"Unsupported architecture: {arch}")

        return backbone.to(self.device)

    def freeze_backbone(self) -> None:
        """Freezes all layers except the classification head for transfer learning."""
        for name, param in self.model.named_parameters():
            if "fc" not in name and "classifier" not in name:
                param.requires_grad = False
        logger.info("Backbone frozen for transfer learning.")

    def unfreeze_backbone(self) -> None:
        """Unfreezes all parameters for full fine-tuning."""
        for param in self.model.parameters():
            param.requires_grad = True
        logger.info("Backbone unfrozen for fine-tuning.")

    def load_model(self) -> None:
        """Loads state dictionary checkpoint from file."""
        if not self.model_path or not self.model_path.exists():
            logger.warning("No checkpoint file found at %s. Model remains in initialized state.", self.model_path)
            self._is_loaded = True
            return

        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            state_dict = checkpoint.get("state_dict", checkpoint)
            self.model.load_state_dict(state_dict, strict=False)
            self.model.eval()
            self._is_loaded = True
            logger.info("Loaded weights from %s", self.model_path)
        except Exception as e:
            logger.error("Failed to load model from %s: %s", self.model_path, e)
            raise

    def unload_model(self) -> None:
        """Releases model from compute memory."""
        self.model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self._is_loaded = False
        logger.info("PlantDiseaseClassifier unloaded.")

    def predict(
        self,
        input_data: Union[str, Path, Image.Image, np.ndarray, torch.Tensor],
        top_k: Optional[int] = None,
        **kwargs,
    ) -> EnginePrediction:
        """
        Infers disease presence on input image.
        """
        k = top_k or self.config.top_k
        start_t = time.perf_counter()

        # Image preprocessing
        if isinstance(input_data, (str, Path)):
            arr = self.preprocessor.preprocess(input_data)
            tensor = torch.from_numpy(arr.transpose((2, 0, 1))).unsqueeze(0).to(self.device)
        elif isinstance(input_data, Image.Image):
            resized = self.preprocessor.resize(input_data)
            arr = self.preprocessor.normalize(self.preprocessor.to_numpy(resized))
            tensor = torch.from_numpy(arr.transpose((2, 0, 1))).unsqueeze(0).to(self.device)
        elif isinstance(input_data, np.ndarray):
            if input_data.ndim == 3 and input_data.shape[2] == 3:
                tensor = torch.from_numpy(input_data.transpose((2, 0, 1))).unsqueeze(0).float().to(self.device)
            else:
                tensor = torch.from_numpy(input_data).float().to(self.device)
        elif isinstance(input_data, torch.Tensor):
            tensor = input_data.to(self.device)
            if tensor.ndim == 3:
                tensor = tensor.unsqueeze(0)
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}")

        self.model.eval()
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0)

        # Extract top-K
        top_probs, top_indices = torch.topk(probs, min(k, len(self.classes)))
        top_probs = top_probs.cpu().numpy()
        top_indices = top_indices.cpu().numpy()

        primary_idx = int(top_indices[0])
        primary_conf = float(top_probs[0])
        primary_label = self.classes[primary_idx] if primary_idx < len(self.classes) else f"class_{primary_idx}"

        alternatives: List[AlternativePrediction] = []
        for i in range(1, len(top_indices)):
            c_idx = int(top_indices[i])
            c_label = self.classes[c_idx] if c_idx < len(self.classes) else f"class_{c_idx}"
            alternatives.append(
                AlternativePrediction(
                    label=c_label,
                    confidence=float(round(top_probs[i], 4)),
                )
            )

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        is_confident = primary_conf >= self.confidence_threshold
        requires_expert = not is_confident or (primary_label != "healthy" and primary_conf < 0.75)

        return EnginePrediction(
            engine_name="PlantVisionClassifier",
            task="disease_classification",
            primary_label=primary_label,
            confidence=float(round(primary_conf, 4)),
            alternatives=alternatives,
            is_confident=is_confident,
            requires_expert_review=requires_expert,
            execution_time_ms=float(round(elapsed_ms, 2)),
            model_version=f"{self.config.architecture}_v1",
            details={
                "all_probabilities": {
                    self.classes[i]: float(round(p, 4))
                    for i, p in enumerate(probs.cpu().numpy())
                    if i < len(self.classes)
                }
            },
        )

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_name="PlantVisionClassifier",
            version="1.0.0",
            model_architecture=self.config.architecture,
            model_version=f"{self.config.architecture}_v1",
            device=str(self.device),
            supported_tasks=["disease_classification"],
            confidence_threshold=self.config.confidence_threshold,
            extra={"num_classes": len(self.classes)},
        )

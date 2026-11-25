"""
Crop Type Identifier.

Identifies the agricultural crop species from foliage, canopy, or fruit imagery.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import torchvision.models as models

from ai.config import DEVICE
from ai.engines.plant_vision.config import DEFAULT_CROP_CLASSES, PlantVisionConfig
from ai.shared.model_interfaces.base_engine import (
    AlternativePrediction,
    BaseAIEngine,
    EngineMetadata,
    EnginePrediction,
)
from ai.shared.preprocessing.image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class CropIdentifier(BaseAIEngine):
    """
    Identifies crop type (Tomato, Potato, Coffee, Wheat, Grape, etc.) from an image.
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
            confidence_threshold=0.60,
        )
        self.crops = self.config.crop_classes
        self.preprocessor = ImagePreprocessor(target_size=self.config.image_size)
        self.model = self._build_model()
        if self.model_path and Path(self.model_path).exists():
            self.load_model()

    def _build_model(self) -> nn.Module:
        backbone = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT if self.config.pretrained else None)
        in_feat = backbone.classifier[0].in_features
        backbone.classifier = nn.Sequential(
            nn.Linear(in_feat, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, len(self.crops)),
        )
        return backbone.to(self.device)

    def load_model(self) -> None:
        if self.model_path and self.model_path.exists():
            checkpoint = torch.load(self.model_path, map_location=self.device)
            state_dict = checkpoint.get("state_dict", checkpoint)
            self.model.load_state_dict(state_dict, strict=False)
            self.model.eval()
            self._is_loaded = True
        else:
            self._is_loaded = True

    def unload_model(self) -> None:
        self.model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self._is_loaded = False

    def predict(
        self,
        input_data: Union[str, Path, Image.Image, np.ndarray, torch.Tensor],
        **kwargs,
    ) -> EnginePrediction:
        start_t = time.perf_counter()

        # Preprocess
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

        top_probs, top_indices = torch.topk(probs, min(3, len(self.crops)))
        top_probs = top_probs.cpu().numpy()
        top_indices = top_indices.cpu().numpy()

        primary_idx = int(top_indices[0])
        primary_conf = float(top_probs[0])
        primary_crop = self.crops[primary_idx] if primary_idx < len(self.crops) else f"crop_{primary_idx}"

        alternatives = [
            AlternativePrediction(
                label=self.crops[int(top_indices[i])],
                confidence=float(round(top_probs[i], 4)),
            )
            for i in range(1, len(top_indices))
        ]

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        return EnginePrediction(
            engine_name="CropIdentifier",
            task="crop_identification",
            primary_label=primary_crop,
            confidence=float(round(primary_conf, 4)),
            alternatives=alternatives,
            is_confident=primary_conf >= self.confidence_threshold,
            execution_time_ms=float(round(elapsed_ms, 2)),
            model_version="crop_id_v1",
        )

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_name="CropIdentifier",
            version="1.0.0",
            model_architecture="mobilenetv3_crop",
            model_version="v1.0.0",
            device=str(self.device),
            supported_tasks=["crop_identification"],
            confidence_threshold=self.confidence_threshold,
            extra={"supported_crops": self.crops},
        )

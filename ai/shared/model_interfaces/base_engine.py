"""
Base AI Engine Interface.

Defines the core contract that every domain engine in AgriVision AI must implement:
- Lifecycle: load_model(), unload_model()
- Standard prediction method: predict()
- Version and metadata inspection
- Health and readiness status
- Standardized EnginePrediction response container
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
from pydantic import BaseModel, Field

from ai.config import DEFAULT_CONFIDENCE_THRESHOLD, DEVICE


@dataclass
class EngineMetadata:
    """Metadata describing the AI engine instance and active model."""
    engine_name: str
    version: str
    model_architecture: str
    model_version: str
    device: str
    loaded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    supported_tasks: List[str] = field(default_factory=list)
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    extra: Dict[str, Any] = field(default_factory=dict)


class AlternativePrediction(BaseModel):
    """An alternative diagnosis or candidate class."""
    label: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EnginePrediction(BaseModel):
    """Standardized result returned by any AgriVision AI engine."""
    engine_name: str
    task: str
    primary_label: str
    confidence: float
    alternatives: List[AlternativePrediction] = Field(default_factory=list)
    is_confident: bool = True
    requires_expert_review: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    model_version: str = "v1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseAIEngine(abc.ABC):
    """
    Abstract base class for all AgriVision AI domain engines.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        device: Optional[Union[str, torch.device]] = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        self.model_path = Path(model_path) if model_path else None
        self.device = torch.device(device) if device else DEVICE
        self.confidence_threshold = confidence_threshold
        self.model: Optional[Any] = None
        self._is_loaded: bool = False

    @property
    def is_loaded(self) -> bool:
        """Whether the underlying neural model is loaded into memory."""
        return self._is_loaded

    @abc.abstractmethod
    def load_model(self) -> None:
        """Load weights into memory on the target compute device."""
        pass

    @abc.abstractmethod
    def unload_model(self) -> None:
        """Unload weights and clear device cache."""
        pass

    @abc.abstractmethod
    def predict(self, input_data: Any, **kwargs) -> EnginePrediction:
        """
        Execute inference on given input (image, audio, sensor dict, or video path).
        """
        pass

    @abc.abstractmethod
    def get_metadata(self) -> EngineMetadata:
        """Return runtime metadata and model description."""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Returns readiness and operational health status."""
        return {
            "engine": self.__class__.__name__,
            "is_loaded": self.is_loaded,
            "device": str(self.device),
            "model_path": str(self.model_path) if self.model_path else None,
            "status": "ready" if self.is_loaded else "not_loaded",
        }

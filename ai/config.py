"""
AgriVision AI — Global Configuration

Central configuration for all AI modules: paths, device selection,
model defaults, and runtime constants.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import torch

logger = logging.getLogger(__name__)

# ────────────────────────────── path constants ──────────────────────────────

AI_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = AI_ROOT.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MANIFESTS_DIR = DATA_DIR / "manifests"

MODELS_DIR = PROJECT_ROOT / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
EXPORTS_DIR = MODELS_DIR / "exports"
REGISTRY_DIR = MODELS_DIR / "registry"

LOGS_DIR = PROJECT_ROOT / "logs"
RESULTS_DIR = PROJECT_ROOT / "results"

# Ensure critical directories exist
for _d in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MANIFESTS_DIR,
           MODELS_DIR, CHECKPOINTS_DIR, EXPORTS_DIR, REGISTRY_DIR,
           LOGS_DIR, RESULTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ────────────────────────────── device detection ────────────────────────────


def detect_device() -> torch.device:
    """Select the best available compute device."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info("CUDA device detected: %s", torch.cuda.get_device_name(0))
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        logger.info("Apple MPS device detected")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU device")
    return device


DEVICE = detect_device()

# ────────────────────────────── global defaults ─────────────────────────────

# Image defaults
DEFAULT_IMAGE_SIZE: int = 224
MAX_IMAGE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
SUPPORTED_IMAGE_FORMATS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]

# Model defaults
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
DEFAULT_TOP_K: int = 5
DEFAULT_BATCH_SIZE: int = 32
DEFAULT_NUM_WORKERS: int = min(4, os.cpu_count() or 1)

# Training defaults
DEFAULT_LEARNING_RATE: float = 1e-4
DEFAULT_EPOCHS: int = 50
DEFAULT_EARLY_STOPPING_PATIENCE: int = 7


@dataclass
class AIConfig:
    """Runtime-adjustable AI configuration."""

    # Paths
    data_dir: Path = DATA_DIR
    models_dir: Path = MODELS_DIR
    logs_dir: Path = LOGS_DIR
    results_dir: Path = RESULTS_DIR

    # Device
    device: torch.device = field(default_factory=detect_device)

    # Image
    image_size: int = DEFAULT_IMAGE_SIZE
    max_image_bytes: int = MAX_IMAGE_SIZE_BYTES
    supported_formats: List[str] = field(
        default_factory=lambda: list(SUPPORTED_IMAGE_FORMATS)
    )

    # Inference
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    top_k: int = DEFAULT_TOP_K
    batch_size: int = DEFAULT_BATCH_SIZE
    num_workers: int = DEFAULT_NUM_WORKERS

    # Training
    learning_rate: float = DEFAULT_LEARNING_RATE
    epochs: int = DEFAULT_EPOCHS
    early_stopping_patience: int = DEFAULT_EARLY_STOPPING_PATIENCE

    # MLflow
    mlflow_tracking_uri: Optional[str] = None
    mlflow_experiment_name: str = "agrivision"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")
        if self.batch_size < 1:
            raise ValueError("batch_size must be >= 1")


# Singleton default config
default_config = AIConfig()

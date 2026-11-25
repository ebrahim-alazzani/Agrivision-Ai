"""
Training Configuration.

Hyperparameters, optimizer settings, scheduler policies, and checkpointing controls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ai.config import CHECKPOINTS_DIR, RESULTS_DIR


@dataclass
class TrainingConfig:
    # Model
    architecture: str = "resnet50"
    num_classes: int = 18
    pretrained: bool = True
    freeze_epochs: int = 3  # Initial epochs with frozen backbone

    # Optimization
    learning_rate: float = 1e-4
    backbone_lr_multiplier: float = 0.1  # Differential learning rates for fine-tuning
    weight_decay: float = 1e-4
    optimizer_name: str = "adamw"  # 'adamw', 'sgd', 'adam'
    scheduler_name: str = "cosine"  # 'cosine', 'step', 'plateau'
    min_lr: float = 1e-6

    # Training execution
    epochs: int = 30
    batch_size: int = 32
    num_workers: int = 2
    mixed_precision: bool = True

    # Regularization & early stopping
    early_stopping_patience: int = 7
    label_smoothing: float = 0.1

    # Paths & Logging
    checkpoint_dir: Path = CHECKPOINTS_DIR
    results_dir: Path = RESULTS_DIR
    experiment_name: str = "plant_disease_baseline"
    run_name: Optional[str] = None
    use_mlflow: bool = False
    mlflow_uri: Optional[str] = None

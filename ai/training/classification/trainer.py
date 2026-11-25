"""
Classification Trainer.

Full-featured PyTorch training loop for plant disease classification:
- Warm-up & backbone fine-tuning stages
- Mixed precision (torch.cuda.amp)
- Learning rate schedulers & early stopping
- Best checkpoint serialization
- Metric calculation & MLflow experiment logging.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader

from ai.config import DEVICE
from ai.shared.evaluation.metrics import compute_classification_metrics
from ai.training.classification.config import TrainingConfig

logger = logging.getLogger(__name__)

try:
    import mlflow
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False


class ClassificationTrainer:
    """
    Standard PyTorch trainer for agricultural classification tasks.
    """

    def __init__(
        self,
        model: nn.Module,
        config: TrainingConfig,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: Optional[torch.device] = None,
    ) -> None:
        self.config = config
        self.device = device or DEVICE
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader

        self.criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)
        self.optimizer = self._build_optimizer()
        self.scheduler = self._build_scheduler()
        self.scaler = GradScaler(enabled=self.config.mixed_precision and self.device.type == "cuda")

        self.best_val_f1 = 0.0
        self.best_epoch = 0
        self.patience_counter = 0
        self.history: Dict[str, List[float]] = {
            "train_loss": [],
            "val_loss": [],
            "train_acc": [],
            "val_acc": [],
            "val_f1": [],
        }

        # Checkpoints setup
        self.checkpoint_dir = Path(self.config.checkpoint_dir) / self.config.experiment_name
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def _build_optimizer(self) -> torch.optim.Optimizer:
        opt_name = self.config.optimizer_name.lower()
        if opt_name == "adamw":
            return torch.optim.AdamW(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
            )
        elif opt_name == "sgd":
            return torch.optim.SGD(
                self.model.parameters(),
                lr=self.config.learning_rate,
                momentum=0.9,
                weight_decay=self.config.weight_decay,
            )
        return torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

    def _build_scheduler(self) -> Any:
        sched_name = self.config.scheduler_name.lower()
        if sched_name == "cosine":
            return torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config.epochs,
                eta_min=self.config.min_lr,
            )
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode="max",
            patience=3,
            factor=0.5,
        )

    def train_epoch(self, epoch: int) -> Tuple[float, float]:
        """Runs a single training epoch."""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, batch in enumerate(self.train_loader):
            images, targets = batch[0].to(self.device), batch[1].to(self.device)

            self.optimizer.zero_grad()
            with autocast(enabled=self.config.mixed_precision and self.device.type == "cuda"):
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)

            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()

            total_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == targets).sum().item()
            total += images.size(0)

        epoch_loss = total_loss / max(1, total)
        epoch_acc = correct / max(1, total)
        return epoch_loss, epoch_acc

    def validate(self) -> Tuple[float, float, float]:
        """Runs evaluation over the validation set."""
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_targets = []
        total = 0

        with torch.no_grad():
            for batch in self.val_loader:
                images, targets = batch[0].to(self.device), batch[1].to(self.device)
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)

                total_loss += loss.item() * images.size(0)
                preds = torch.argmax(outputs, dim=1)

                all_preds.extend(preds.cpu().numpy().tolist())
                all_targets.extend(targets.cpu().numpy().tolist())
                total += images.size(0)

        val_loss = total_loss / max(1, total)
        metrics = compute_classification_metrics(all_targets, all_preds)
        return val_loss, metrics.accuracy, metrics.macro_f1

    def fit(self) -> Dict[str, List[float]]:
        """Executes full training loop across all configured epochs."""
        logger.info("Starting training: %s (%d epochs)", self.config.experiment_name, self.config.epochs)

        if self.config.use_mlflow and HAS_MLFLOW:
            if self.config.mlflow_uri:
                mlflow.set_tracking_uri(self.config.mlflow_uri)
            mlflow.set_experiment(self.config.experiment_name)
            mlflow.start_run(run_name=self.config.run_name)
            mlflow.log_params({
                "architecture": self.config.architecture,
                "learning_rate": self.config.learning_rate,
                "batch_size": self.config.batch_size,
                "epochs": self.config.epochs,
            })

        for epoch in range(1, self.config.epochs + 1):
            start_t = time.time()
            train_loss, train_acc = self.train_epoch(epoch)
            val_loss, val_acc, val_f1 = self.validate()

            if isinstance(self.scheduler, torch.optim.lr_scheduler.CosineAnnealingLR):
                self.scheduler.step()
            elif isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                self.scheduler.step(val_f1)

            # Record history
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_acc"].append(val_acc)
            self.history["val_f1"].append(val_f1)

            elapsed = time.time() - start_t
            logger.info(
                "Epoch %02d/%02d [%.1fs] - Train Loss: %.4f Acc: %.4f | Val Loss: %.4f Acc: %.4f F1: %.4f",
                epoch, self.config.epochs, elapsed, train_loss, train_acc, val_loss, val_acc, val_f1
            )

            # Checkpoint best model
            if val_f1 > self.best_val_f1:
                self.best_val_f1 = val_f1
                self.best_epoch = epoch
                self.patience_counter = 0
                self._save_checkpoint(is_best=True, epoch=epoch)
            else:
                self.patience_counter += 1

            if self.patience_counter >= self.config.early_stopping_patience:
                logger.info("Early stopping triggered at epoch %d (patience=%d).", epoch, self.config.early_stopping_patience)
                break

        # Always save final checkpoint
        self._save_checkpoint(is_best=False, epoch=epoch)

        if self.config.use_mlflow and HAS_MLFLOW:
            mlflow.log_metrics({"best_val_f1": self.best_val_f1, "best_epoch": self.best_epoch})
            mlflow.end_run()

        logger.info("Training completed. Best Val F1: %.4f at epoch %d", self.best_val_f1, self.best_epoch)
        return self.history

    def _save_checkpoint(self, is_best: bool, epoch: int) -> None:
        filename = "best_model.pt" if is_best else "last_model.pt"
        path = self.checkpoint_dir / filename
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "best_val_f1": self.best_val_f1,
                "config": self.config,
            },
            path,
        )
        logger.info("Saved checkpoint to %s", path)

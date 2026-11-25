"""
Experiment Runner.

Automates end-to-end model development lifecycle:
- Dataset validation & train/val/test splitting
- Model instantiation & fine-tuning
- Full metric evaluation on unseen test partition
- Exporting confusion matrix & loss curves
- Baseline benchmark comparison.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ai.config import RESULTS_DIR
from ai.engines.plant_vision.classifier import PlantDiseaseClassifier
from ai.engines.plant_vision.config import PlantVisionConfig
from ai.shared.datasets.base_dataset import AgriculturalDataset, split_dataset
from ai.shared.datasets.data_validator import DatasetValidator
from ai.shared.evaluation.metrics import (
    ClassificationMetrics,
    compute_classification_metrics,
    generate_evaluation_report,
)
from ai.shared.evaluation.visualization import plot_confusion_matrix, plot_training_curves
from ai.shared.preprocessing.augmentation import get_training_transforms, get_validation_transforms
from ai.training.classification.config import TrainingConfig
from ai.training.classification.trainer import ClassificationTrainer

logger = logging.getLogger(__name__)


class Experiment:
    """
    Coordinates repeatable experiments and baseline comparisons.
    """

    def __init__(
        self,
        experiment_name: str,
        training_config: Optional[TrainingConfig] = None,
        plant_config: Optional[PlantVisionConfig] = None,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.experiment_name = experiment_name
        self.training_config = training_config or TrainingConfig(experiment_name=experiment_name)
        self.plant_config = plant_config or PlantVisionConfig()
        self.output_dir = Path(output_dir or RESULTS_DIR) / experiment_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        manifest_path: Union[str, Path],
        holdout_regions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end training, validation, and evaluation pipeline.
        """
        logger.info(">>> Launching Experiment: %s <<<", self.experiment_name)

        # 1. Dataset loading and split
        df = pd.read_csv(manifest_path) if str(manifest_path).endswith(".csv") else pd.read_json(manifest_path)
        train_df, val_df, test_df = split_dataset(
            manifest_df=df,
            val_ratio=0.15,
            test_ratio=0.15,
            holdout_regions=holdout_regions,
        )

        train_manifest = self.output_dir / "train_manifest.csv"
        val_manifest = self.output_dir / "val_manifest.csv"
        test_manifest = self.output_dir / "test_manifest.csv"

        train_df.to_csv(train_manifest, index=False)
        val_df.to_csv(val_manifest, index=False)
        test_df.to_csv(test_manifest, index=False)

        # 2. Datasets & Loaders
        train_tf = get_training_transforms(image_size=self.plant_config.image_size)
        val_tf = get_validation_transforms(image_size=self.plant_config.image_size)

        train_ds = AgriculturalDataset(manifest_path=train_manifest, transform=train_tf)
        val_ds = AgriculturalDataset(manifest_path=val_manifest, transform=val_tf, class_to_idx=train_ds.class_to_idx)
        test_ds = AgriculturalDataset(manifest_path=test_manifest, transform=val_tf, class_to_idx=train_ds.class_to_idx)

        train_loader = DataLoader(
            train_ds,
            batch_size=self.training_config.batch_size,
            shuffle=True,
            num_workers=self.training_config.num_workers,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=self.training_config.batch_size,
            shuffle=False,
            num_workers=self.training_config.num_workers,
        )
        test_loader = DataLoader(
            test_ds,
            batch_size=self.training_config.batch_size,
            shuffle=False,
            num_workers=self.training_config.num_workers,
        )

        # 3. Model setup
        self.plant_config.num_classes = len(train_ds.class_to_idx)
        self.plant_config.disease_classes = [train_ds.idx_to_class[i] for i in range(len(train_ds.idx_to_class))]
        classifier = PlantDiseaseClassifier(config=self.plant_config)

        # 4. Training
        trainer = ClassificationTrainer(
            model=classifier.model,
            config=self.training_config,
            train_loader=train_loader,
            val_loader=val_loader,
        )
        history = trainer.fit()

        # 5. Evaluate on Holdout Test Set
        classifier.model.eval()
        test_preds, test_targets, test_probs = [], [], []
        with torch.no_grad():
            for batch in test_loader:
                imgs, targets = batch[0].to(trainer.device), batch[1].to(trainer.device)
                logits = classifier.model(imgs)
                probs = torch.softmax(logits, dim=1)
                preds = torch.argmax(probs, dim=1)

                test_preds.extend(preds.cpu().numpy().tolist())
                test_targets.extend(targets.cpu().numpy().tolist())
                test_probs.append(probs.cpu().numpy())

        all_test_probs = np.vstack(test_probs) if test_probs else None
        test_metrics = compute_classification_metrics(
            y_true=test_targets,
            y_pred=test_preds,
            y_prob=all_test_probs,
            class_names=self.plant_config.disease_classes,
        )

        # 6. Save Reports and Plots
        json_rep, md_rep = generate_evaluation_report(
            metrics=test_metrics,
            output_dir=self.output_dir,
            experiment_name=self.experiment_name,
        )
        plot_training_curves(
            history=history,
            output_path=self.output_dir / "training_curves.png",
        )
        plot_confusion_matrix(
            cm=test_metrics.confusion_matrix,
            class_names=self.plant_config.disease_classes,
            output_path=self.output_dir / "confusion_matrix.png",
        )

        summary = {
            "experiment_name": self.experiment_name,
            "best_val_f1": trainer.best_val_f1,
            "test_accuracy": test_metrics.accuracy,
            "test_macro_f1": test_metrics.macro_f1,
            "artifacts_dir": str(self.output_dir),
            "report_markdown": str(md_rep),
        }

        with open(self.output_dir / "experiment_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info("Experiment %s concluded successfully. Test F1: %.4f", self.experiment_name, test_metrics.macro_f1)
        return summary

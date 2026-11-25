"""
Model Registry and Model Card Management.

Tracks lifecycle of trained models, deployment status, evaluation benchmarks,
and auto-generates transparent Model Cards.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ai.config import REGISTRY_DIR

logger = logging.getLogger(__name__)


class DeploymentStage(str, Enum):
    CANDIDATE = "candidate"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelCard:
    """Standardized transparent model card."""
    model_name: str
    model_version: str
    architecture: str
    description: str
    training_dataset: str
    intended_use: str
    factors_and_limitations: List[str]
    metrics: Dict[str, float]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    authors: List[str] = field(default_factory=lambda: ["AgriVision AI Team"])


@dataclass
class RegisteredModel:
    model_id: str
    model_name: str
    version: str
    checkpoint_path: str
    stage: DeploymentStage
    model_card: ModelCard
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ModelRegistry:
    """
    Catalog of validated neural network checkpoints.
    """

    def __init__(self, registry_dir: Optional[Union[str, Path]] = None) -> None:
        self.registry_dir = Path(registry_dir or REGISTRY_DIR)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.registry_dir / "models_index.json"
        self._models: Dict[str, RegisteredModel] = self._load_index()

    def _load_index(self) -> Dict[str, RegisteredModel]:
        if not self.index_file.exists():
            return {}
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            result = {}
            for k, v in data.items():
                card = ModelCard(**v["model_card"])
                result[k] = RegisteredModel(
                    model_id=v["model_id"],
                    model_name=v["model_name"],
                    version=v["version"],
                    checkpoint_path=v["checkpoint_path"],
                    stage=DeploymentStage(v["stage"]),
                    model_card=card,
                    registered_at=v["registered_at"],
                )
            return result
        except Exception as e:
            logger.warning("Failed to parse registry index: %s. Starting fresh.", e)
            return {}

    def _save_index(self) -> None:
        serialized = {}
        for k, v in self._models.items():
            entry = asdict(v)
            entry["stage"] = v.stage.value
            serialized[k] = entry
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)

    def register(
        self,
        model_name: str,
        version: str,
        checkpoint_path: Union[str, Path],
        model_card: ModelCard,
        initial_stage: DeploymentStage = DeploymentStage.CANDIDATE,
    ) -> RegisteredModel:
        """
        Registers a new model version.
        """
        model_id = f"{model_name}:{version}"
        reg = RegisteredModel(
            model_id=model_id,
            model_name=model_name,
            version=version,
            checkpoint_path=str(Path(checkpoint_path).resolve()),
            stage=initial_stage,
            model_card=model_card,
        )
        self._models[model_id] = reg
        self._save_index()
        logger.info("Successfully registered model: %s (stage=%s)", model_id, initial_stage.value)
        return reg

    def transition_stage(self, model_id: str, new_stage: DeploymentStage) -> None:
        """Promotes or transitions a model version between stages."""
        if model_id not in self._models:
            raise KeyError(f"Model ID '{model_id}' not found in registry.")

        target_model = self._models[model_id]

        # If promoting to production, archive existing production models of the same name
        if new_stage == DeploymentStage.PRODUCTION:
            for m in self._models.values():
                if m.model_name == target_model.model_name and m.stage == DeploymentStage.PRODUCTION:
                    m.stage = DeploymentStage.ARCHIVED
                    logger.info("Archiving previous production model: %s", m.model_id)

        target_model.stage = new_stage
        self._save_index()
        logger.info("Transitioned model %s to %s", model_id, new_stage.value)

    def get_production_model(self, model_name: str) -> Optional[RegisteredModel]:
        """Returns currently active production model for given model family."""
        for m in self._models.values():
            if m.model_name == model_name and m.stage == DeploymentStage.PRODUCTION:
                return m
        return None

    def export_model_card_markdown(self, model_id: str, output_path: Union[str, Path]) -> Path:
        """Exports a standard GitHub/HuggingFace style Model Card markdown file."""
        if model_id not in self._models:
            raise KeyError(f"Model ID '{model_id}' not found.")

        m = self._models[model_id]
        card = m.model_card

        lines = [
            f"# Model Card: {card.model_name} ({card.model_version})",
            "",
            f"**Architecture:** `{card.architecture}`  ",
            f"**Deployment Stage:** `{m.stage.value.upper()}`  ",
            f"**Created At:** {card.created_at}  ",
            f"**Authors:** {', '.join(card.authors)}  ",
            "",
            "## Description",
            card.description,
            "",
            "## Intended Use",
            card.intended_use,
            "",
            "## Training Dataset",
            card.training_dataset,
            "",
            "## Evaluation Metrics",
            "| Metric | Value |",
            "|---|---|",
        ]
        for k, v in card.metrics.items():
            lines.append(f"| {k} | {v:.4f} |")

        lines.extend([
            "",
            "## Factors and Limitations",
        ])
        for f in card.factors_and_limitations:
            lines.append(f"- {f}")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return out

"""
Tests for PlantDiseaseClassifier.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest
import torch

from ai.engines.plant_vision.classifier import PlantDiseaseClassifier
from ai.engines.plant_vision.config import PlantVisionConfig


def test_classifier_initialization():
    config = PlantVisionConfig(
        architecture="mobilenetv3_large_100",
        pretrained=False,
        disease_classes=["healthy", "blight", "rust"],
    )
    clf = PlantDiseaseClassifier(config=config, device="cpu")
    assert clf.is_loaded
    assert len(clf.classes) == 3


def test_classifier_prediction(sample_image_path: Path):
    config = PlantVisionConfig(
        architecture="mobilenetv3_large_100",
        pretrained=False,
        disease_classes=["healthy", "blight", "rust"],
        top_k=2,
    )
    clf = PlantDiseaseClassifier(config=config, device="cpu")
    pred = clf.predict(sample_image_path)

    assert pred.engine_name == "PlantVisionClassifier"
    assert pred.primary_label in ["healthy", "blight", "rust"]
    assert 0.0 <= pred.confidence <= 1.0
    assert len(pred.alternatives) == 1
    assert "all_probabilities" in pred.details


def test_freeze_unfreeze():
    config = PlantVisionConfig(architecture="resnet50", pretrained=False)
    clf = PlantDiseaseClassifier(config=config, device="cpu")

    clf.freeze_backbone()
    # Check that backbone params are frozen
    for name, p in clf.model.named_parameters():
        if "fc" not in name:
            assert not p.requires_grad

    clf.unfreeze_backbone()
    for p in clf.model.parameters():
        assert p.requires_grad

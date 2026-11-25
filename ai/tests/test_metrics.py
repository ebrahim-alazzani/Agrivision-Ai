"""
Tests for Evaluation Metrics and Report Generation.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np

from ai.shared.evaluation.metrics import (
    compute_calibration_metrics,
    compute_classification_metrics,
    compute_iou,
    generate_evaluation_report,
)


def test_classification_metrics():
    y_true = [0, 1, 0, 1, 2]
    y_pred = [0, 1, 0, 0, 2]
    class_names = ["healthy", "blight", "rust"]

    metrics = compute_classification_metrics(y_true, y_pred, class_names=class_names)
    assert metrics.accuracy == 0.8
    assert len(metrics.per_class) == 3
    assert metrics.per_class[0].class_name == "healthy"


def test_calibration_metrics():
    # 3 samples, 2 classes
    probs = np.array([
        [0.9, 0.1],
        [0.2, 0.8],
        [0.7, 0.3],
    ])
    labels = np.array([0, 1, 1])  # 2 correct, 1 wrong

    calib = compute_calibration_metrics(probs, labels, n_bins=5)
    assert 0.0 <= calib.expected_calibration_error <= 1.0
    assert 0.0 <= calib.brier_score <= 1.0


def test_compute_iou():
    box1 = [10.0, 10.0, 20.0, 20.0]
    box2 = [10.0, 10.0, 20.0, 20.0]
    assert compute_iou(box1, box2) == 1.0

    box3 = [30.0, 30.0, 40.0, 40.0]
    assert compute_iou(box1, box3) == 0.0


def test_generate_evaluation_report(temp_workspace: Path):
    y_true = [0, 1, 1]
    y_pred = [0, 1, 1]
    metrics = compute_classification_metrics(y_true, y_pred)

    json_p, md_p = generate_evaluation_report(
        metrics=metrics,
        output_dir=temp_workspace,
        experiment_name="unit_test",
    )
    assert json_p.exists()
    assert md_p.exists()
    assert "Overall Metrics" in md_p.read_text(encoding="utf-8")

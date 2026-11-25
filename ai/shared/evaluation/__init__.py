"""Evaluation metrics and visualization tools."""

from ai.shared.evaluation.metrics import (
    ClassificationMetrics,
    DetectionMetrics,
    compute_classification_metrics,
    compute_calibration_metrics,
    compute_iou,
    compute_detection_map,
    generate_evaluation_report,
)
from ai.shared.evaluation.visualization import (
    plot_confusion_matrix,
    plot_training_curves,
    plot_class_distribution,
    visualize_predictions,
)

__all__ = [
    "ClassificationMetrics",
    "DetectionMetrics",
    "compute_classification_metrics",
    "compute_calibration_metrics",
    "compute_iou",
    "compute_detection_map",
    "generate_evaluation_report",
    "plot_confusion_matrix",
    "plot_training_curves",
    "plot_class_distribution",
    "visualize_predictions",
]

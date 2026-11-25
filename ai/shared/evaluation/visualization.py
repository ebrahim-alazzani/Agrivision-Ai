"""
Evaluation Visualizations.

Generates plots for:
- Confusion matrices
- Loss & metric training curves
- Dataset class distribution histograms
- Model predictions overlaid on sample images
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

logger = logging.getLogger(__name__)


def plot_confusion_matrix(
    cm: Union[List[List[int]], np.ndarray],
    class_names: List[str],
    output_path: Optional[Union[str, Path]] = None,
    normalize: bool = True,
    title: str = "Confusion Matrix",
) -> plt.Figure:
    """Plots and optionally saves a heatmap confusion matrix."""
    matrix = np.array(cm, dtype=float)
    if normalize:
        row_sums = matrix.sum(axis=1, keepdims=True)
        matrix = np.divide(matrix, row_sums, out=np.zeros_like(matrix), where=row_sums != 0)

    fig, ax = plt.subplots(figsize=(max(8, len(class_names) * 0.8), max(6, len(class_names) * 0.6)))
    fmt = ".2f" if normalize else ".0f"
    sns.heatmap(
        matrix,
        annot=True,
        fmt=fmt,
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
    )
    ax.set_ylabel("True Label")
    ax.set_xlabel("Predicted Label")
    ax.set_title(title)
    plt.tight_layout()

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=300)
        logger.info("Saved confusion matrix plot to %s", out)

    return fig


def plot_training_curves(
    history: Dict[str, List[float]],
    output_path: Optional[Union[str, Path]] = None,
    title: str = "Training & Validation Curves",
) -> plt.Figure:
    """Plots train vs validation loss and accuracy curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    epochs = range(1, len(history.get("train_loss", [])) + 1)

    # Loss
    if "train_loss" in history:
        ax1.plot(epochs, history["train_loss"], label="Train Loss", color="#1f77b4", lw=2)
    if "val_loss" in history:
        ax1.plot(epochs, history["val_loss"], label="Val Loss", color="#ff7f0e", lw=2)
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Loss over Epochs")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy / F1
    if "train_acc" in history:
        ax2.plot(epochs, history["train_acc"], label="Train Acc", color="#1f77b4", lw=2)
    if "val_acc" in history:
        ax2.plot(epochs, history["val_acc"], label="Val Acc", color="#ff7f0e", lw=2)
    if "val_f1" in history:
        ax2.plot(epochs, history["val_f1"], label="Val F1", color="#2ca02c", linestyle="--", lw=2)
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Score")
    ax2.set_title("Performance Metrics")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.suptitle(title)
    plt.tight_layout()

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=300)
        logger.info("Saved training curves to %s", out)

    return fig


def plot_class_distribution(
    distribution: Dict[str, int],
    output_path: Optional[Union[str, Path]] = None,
    title: str = "Class Sample Distribution",
) -> plt.Figure:
    """Plots a horizontal bar chart of dataset class frequencies."""
    sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in sorted_items]
    counts = [v for _, v in sorted_items]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.4)))
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, counts, align="center", color="#2b5c8f")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Sample Count")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=300)
        logger.info("Saved class distribution plot to %s", out)

    return fig


def visualize_predictions(
    images: List[np.ndarray],
    true_labels: List[str],
    pred_labels: List[str],
    confidences: List[float],
    output_path: Optional[Union[str, Path]] = None,
    max_images: int = 8,
) -> plt.Figure:
    """Plots grid of sample images with true vs predicted labels and confidence."""
    n = min(len(images), max_images)
    cols = min(4, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.5, rows * 3.5))
    if n == 1:
        axes = np.array([axes])
    axes = np.ravel(axes)

    for i in range(len(axes)):
        if i < n:
            img = images[i]
            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)
            axes[i].imshow(img)
            is_correct = true_labels[i] == pred_labels[i]
            col = "green" if is_correct else "red"
            title_text = f"True: {true_labels[i]}\nPred: {pred_labels[i]} ({confidences[i]:.2f})"
            axes[i].set_title(title_text, color=col, fontsize=10)
        axes[i].axis("off")

    plt.tight_layout()

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=300)
        logger.info("Saved predictions visualization to %s", out)

    return fig

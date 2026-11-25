"""
Tests for Agricultural Dataset and Validator.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest
import torch

from ai.shared.datasets.base_dataset import AgriculturalDataset, split_dataset
from ai.shared.datasets.data_validator import DatasetValidator


def test_agricultural_dataset_loading(sample_manifest: Path):
    ds = AgriculturalDataset(manifest_path=sample_manifest, target_column="disease")
    assert len(ds) == 6
    assert "tomato_early_blight" in ds.class_to_idx

    img_tensor, label_idx, meta = ds[0]
    assert isinstance(img_tensor, torch.Tensor)
    assert isinstance(label_idx, int)
    assert meta["crop"] in ("tomato", "potato")


def test_geographic_holdout_split(sample_manifest: Path):
    df = pd.read_csv(sample_manifest)
    train_df, val_df, test_df = split_dataset(
        manifest_df=df,
        val_ratio=0.2,
        test_ratio=0.2,
        geographic_holdout_column="region",
        holdout_regions=["Dhamar"],
    )

    # Verify that Dhamar samples are exclusively in test_df
    assert "Dhamar" in test_df["region"].unique()
    assert "Dhamar" not in train_df["region"].unique()
    assert "Dhamar" not in val_df["region"].unique()


def test_dataset_validator(sample_manifest: Path):
    df = pd.read_csv(sample_manifest)
    validator = DatasetValidator()
    summary = validator.validate_manifest(manifest_df=df)

    assert summary.total_samples == 6
    assert summary.valid_samples == 6
    assert len(summary.corrupted_images) == 0
    assert len(summary.missing_files) == 0
    assert "tomato_early_blight" in summary.class_distribution

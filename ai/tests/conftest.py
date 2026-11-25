"""
Shared Pytest Fixtures.

Generates reproducible synthetic images, manifests, and dummy dataset files for AI test runs.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import cv2
import numpy as np
import pandas as pd
import pytest
from PIL import Image


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Temporary test directory cleaned up after test run."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_image_path(temp_workspace: Path) -> Path:
    """Creates a sample 256x256 test image."""
    img_path = temp_workspace / "sample_leaf.jpg"
    arr = np.zeros((256, 256, 3), dtype=np.uint8)
    # Green leaf background with a brownish spot
    arr[50:200, 50:200] = [34, 139, 34]  # Forest green
    arr[100:130, 100:130] = [139, 69, 19]  # Brown blight spot
    cv2.imwrite(str(img_path), arr)
    return img_path


@pytest.fixture
def blurry_image_path(temp_workspace: Path) -> Path:
    """Creates a uniformly smooth / blurry test image."""
    img_path = temp_workspace / "blurry_leaf.jpg"
    arr = np.full((256, 256, 3), 120, dtype=np.uint8)
    cv2.imwrite(str(img_path), arr)
    return img_path


@pytest.fixture
def sample_manifest(temp_workspace: Path, sample_image_path: Path) -> Path:
    """Creates a small CSV manifest with sample records."""
    manifest_path = temp_workspace / "manifest.csv"
    data = [
        {
            "sample_id": f"s_{i}",
            "image_path": str(sample_image_path),
            "crop": "tomato" if i % 2 == 0 else "potato",
            "disease": "tomato_early_blight" if i % 2 == 0 else "potato_late_blight",
            "region": "Sanaa" if i < 3 else "Dhamar",
            "severity": "moderate",
        }
        for i in range(6)
    ]
    df = pd.DataFrame(data)
    df.to_csv(manifest_path, index=False)
    return manifest_path

"""
Tests for ImagePreprocessor.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest
from PIL import Image

from ai.shared.preprocessing.image_preprocessor import (
    ImagePreprocessor,
    QualityIssue,
)


def test_load_and_validate_success(sample_image_path: Path):
    pre = ImagePreprocessor(target_size=224)
    img = pre.load_and_validate(sample_image_path)
    assert isinstance(img, Image.Image)
    assert img.mode == "RGB"


def test_load_missing_file_raises(temp_workspace: Path):
    pre = ImagePreprocessor()
    with pytest.raises(FileNotFoundError):
        pre.load_and_validate(temp_workspace / "non_existent.jpg")


def test_unsupported_format_raises(temp_workspace: Path):
    txt_file = temp_workspace / "bad.txt"
    txt_file.write_text("not an image")
    pre = ImagePreprocessor()
    with pytest.raises(ValueError, match="Unsupported format"):
        pre.load_and_validate(txt_file)


def test_resize_and_preprocess(sample_image_path: Path):
    pre = ImagePreprocessor(target_size=224)
    arr = pre.preprocess(sample_image_path)
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (224, 224, 3)
    assert arr.dtype == np.float32


def test_quality_assessment_blurry(blurry_image_path: Path):
    pre = ImagePreprocessor()
    report = pre.assess_quality(Image.open(blurry_image_path))
    assert QualityIssue.BLURRY in report.issues
    assert not report.is_acceptable

"""
Image Preprocessor — loading, validation, orientation, resizing, normalisation
and quality assessment for agricultural images.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image, ExifTags

from ai.config import (
    DEFAULT_IMAGE_SIZE,
    MAX_IMAGE_SIZE_BYTES,
    SUPPORTED_IMAGE_FORMATS,
)

logger = logging.getLogger(__name__)

# ────────────────────── Quality thresholds ───────────────────────

_LAPLACIAN_BLUR_THRESHOLD = 100.0  # variance below this ⟹ blurry
_MIN_CONTRAST = 30.0               # std-dev of grayscale below this ⟹ low contrast
_MIN_BRIGHTNESS = 40.0             # mean brightness below this ⟹ too dark
_MAX_BRIGHTNESS = 220.0            # mean brightness above this ⟹ too bright

# ImageNet normalisation constants
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class QualityIssue(str, Enum):
    """Possible quality problems detected in an image."""
    BLURRY = "blurry"
    LOW_CONTRAST = "low_contrast"
    TOO_DARK = "too_dark"
    TOO_BRIGHT = "too_bright"


@dataclass
class QualityReport:
    """Result of an image-quality assessment."""
    laplacian_variance: float
    contrast_std: float
    mean_brightness: float
    issues: List[QualityIssue]

    @property
    def is_acceptable(self) -> bool:
        return len(self.issues) == 0


class ImagePreprocessor:
    """Load, validate, correct, resize and normalise agricultural images.

    Parameters
    ----------
    target_size : int
        Side length of the square output image (default 224).
    max_bytes : int
        Maximum raw file size in bytes.
    supported_formats : list[str] | None
        Allowed lowercase extensions including the dot.
    """

    def __init__(
        self,
        target_size: int = DEFAULT_IMAGE_SIZE,
        max_bytes: int = MAX_IMAGE_SIZE_BYTES,
        supported_formats: Optional[List[str]] = None,
    ) -> None:
        self.target_size = target_size
        self.max_bytes = max_bytes
        self.supported_formats = supported_formats or list(SUPPORTED_IMAGE_FORMATS)

    # ────────────────────── public API ──────────────────────

    def load_and_validate(self, path: Union[str, Path]) -> Image.Image:
        """Load an image, validate format/size, and apply EXIF orientation.

        Returns an RGB PIL Image.

        Raises
        ------
        FileNotFoundError
            If *path* does not exist.
        ValueError
            If the file is too large or has an unsupported format.
        IOError
            If the file is not a readable image.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        # Format check
        suffix = path.suffix.lower()
        if suffix not in self.supported_formats:
            raise ValueError(
                f"Unsupported format '{suffix}'. "
                f"Allowed: {self.supported_formats}"
            )

        # Size check
        file_size = path.stat().st_size
        if file_size > self.max_bytes:
            raise ValueError(
                f"File size {file_size / 1024 / 1024:.1f} MB exceeds "
                f"limit of {self.max_bytes / 1024 / 1024:.0f} MB"
            )

        try:
            img = Image.open(path)
            img.verify()  # verify integrity without loading pixels
            img = Image.open(path)  # re-open after verify
        except Exception as exc:
            raise IOError(f"Cannot read image {path}: {exc}") from exc

        img = self._fix_exif_orientation(img)
        img = img.convert("RGB")
        logger.debug("Loaded %s  size=%s", path.name, img.size)
        return img

    def resize(
        self,
        img: Image.Image,
        size: Optional[int] = None,
        resample: Image.Resampling = Image.Resampling.BILINEAR,
    ) -> Image.Image:
        """Resize *img* to a square of ``size × size`` pixels."""
        size = size or self.target_size
        return img.resize((size, size), resample=resample)

    def to_numpy(self, img: Image.Image) -> np.ndarray:
        """Convert a PIL image to a float32 HWC numpy array in [0, 1]."""
        arr = np.asarray(img, dtype=np.float32) / 255.0
        return arr

    def normalize(
        self,
        arr: np.ndarray,
        mean: Tuple[float, ...] = IMAGENET_MEAN,
        std: Tuple[float, ...] = IMAGENET_STD,
    ) -> np.ndarray:
        """Apply channel-wise normalisation (ImageNet defaults)."""
        mean_arr = np.array(mean, dtype=np.float32).reshape(1, 1, 3)
        std_arr = np.array(std, dtype=np.float32).reshape(1, 1, 3)
        return (arr - mean_arr) / std_arr

    def preprocess(
        self,
        path: Union[str, Path],
        size: Optional[int] = None,
    ) -> np.ndarray:
        """End-to-end: load → validate → resize → normalise → HWC float32."""
        img = self.load_and_validate(path)
        img = self.resize(img, size)
        arr = self.to_numpy(img)
        arr = self.normalize(arr)
        return arr

    # ────────────────────── quality assessment ──────────────────────

    def assess_quality(
        self, img: Union[Image.Image, np.ndarray]
    ) -> QualityReport:
        """Run blur, contrast, and brightness checks on *img*.

        Parameters
        ----------
        img : PIL Image or uint8 HWC numpy array (BGR or RGB).
        """
        if isinstance(img, Image.Image):
            arr = np.asarray(img.convert("RGB"))
        else:
            arr = img

        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        contrast_std = float(gray.std())
        mean_bright = float(gray.mean())

        issues: List[QualityIssue] = []
        if laplacian_var < _LAPLACIAN_BLUR_THRESHOLD:
            issues.append(QualityIssue.BLURRY)
        if contrast_std < _MIN_CONTRAST:
            issues.append(QualityIssue.LOW_CONTRAST)
        if mean_bright < _MIN_BRIGHTNESS:
            issues.append(QualityIssue.TOO_DARK)
        if mean_bright > _MAX_BRIGHTNESS:
            issues.append(QualityIssue.TOO_BRIGHT)

        return QualityReport(
            laplacian_variance=laplacian_var,
            contrast_std=contrast_std,
            mean_brightness=mean_bright,
            issues=issues,
        )

    # ────────────────────── internals ──────────────────────

    @staticmethod
    def _fix_exif_orientation(img: Image.Image) -> Image.Image:
        """Rotate / flip the image according to its EXIF orientation tag."""
        try:
            exif = img.getexif()
            orientation_key = next(
                (k for k, v in ExifTags.TAGS.items() if v == "Orientation"),
                None,
            )
            if orientation_key is None or orientation_key not in exif:
                return img

            orientation = exif[orientation_key]
            transforms = {
                2: Image.Transpose.FLIP_LEFT_RIGHT,
                3: Image.Transpose.ROTATE_180,
                4: Image.Transpose.FLIP_TOP_BOTTOM,
                5: Image.Transpose.TRANSPOSE,
                6: Image.Transpose.ROTATE_270,
                7: Image.Transpose.TRANSVERSE,
                8: Image.Transpose.ROTATE_90,
            }
            if orientation in transforms:
                img = img.transpose(transforms[orientation])
        except Exception:
            # Corrupted EXIF is non-fatal
            logger.debug("Could not read EXIF orientation; skipping correction")
        return img

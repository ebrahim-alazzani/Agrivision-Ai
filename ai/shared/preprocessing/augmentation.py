"""
Data Augmentation Pipelines for Agricultural Imagery.

Provides Albumentations transforms for training, validation, and field-condition simulation
(direct sun, shadow, dust, atmospheric haze, varying angles).
"""

from __future__ import annotations

import albumentations as A
from albumentations.pytorch import ToTensorV2
from typing import Optional, Tuple

from ai.config import DEFAULT_IMAGE_SIZE
from ai.shared.preprocessing.image_preprocessor import IMAGENET_MEAN, IMAGENET_STD


def get_training_transforms(
    image_size: int = DEFAULT_IMAGE_SIZE,
    mean: Tuple[float, ...] = IMAGENET_MEAN,
    std: Tuple[float, ...] = IMAGENET_STD,
) -> A.Compose:
    """Standard training pipeline with geometry and light augmentations."""
    return A.Compose(
        [
            A.RandomResizedCrop(
                height=image_size,
                width=image_size,
                scale=(0.8, 1.0),
                ratio=(0.9, 1.1),
                p=1.0,
            ),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.3),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.0625,
                scale_limit=0.1,
                rotate_limit=45,
                p=0.5,
                border_mode=0,
            ),
            A.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1,
                p=0.5,
            ),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def get_validation_transforms(
    image_size: int = DEFAULT_IMAGE_SIZE,
    mean: Tuple[float, ...] = IMAGENET_MEAN,
    std: Tuple[float, ...] = IMAGENET_STD,
) -> A.Compose:
    """Deterministic validation pipeline: resize and normalize."""
    return A.Compose(
        [
            A.Resize(height=image_size, width=image_size),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def get_agricultural_transforms(
    image_size: int = DEFAULT_IMAGE_SIZE,
    mean: Tuple[float, ...] = IMAGENET_MEAN,
    std: Tuple[float, ...] = IMAGENET_STD,
) -> A.Compose:
    """
    Robust agricultural field augmentation pipeline.
    Simulates high solar exposure, uneven shadowing, soil dust, slight lens blur,
    and perspective shifts common when farmers shoot handheld in fields.
    """
    return A.Compose(
        [
            A.RandomResizedCrop(
                height=image_size,
                width=image_size,
                scale=(0.7, 1.0),
                ratio=(0.85, 1.15),
                p=1.0,
            ),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.25),
            A.RandomRotate90(p=0.5),
            A.Perspective(scale=(0.05, 0.1), p=0.4),
            # Lighting & weather variations in field conditions
            A.OneOf(
                [
                    A.RandomSunFlare(
                        flare_roi=(0, 0, 1, 0.5),
                        angle_range=(0, 1),
                        num_flare_circles_lower=1,
                        num_flare_circles_upper=3,
                        src_radius=100,
                        p=1.0,
                    ),
                    A.RandomShadow(
                        shadow_roi=(0, 0, 1, 1),
                        num_shadows_lower=1,
                        num_shadows_upper=2,
                        shadow_dimension=5,
                        p=1.0,
                    ),
                    A.RandomBrightnessContrast(
                        brightness_limit=0.25,
                        contrast_limit=0.25,
                        p=1.0,
                    ),
                ],
                p=0.6,
            ),
            # Sensor / optics noise
            A.OneOf(
                [
                    A.MotionBlur(blur_limit=5, p=1.0),
                    A.GaussianBlur(blur_limit=(3, 5), p=1.0),
                    A.GaussNoise(var_limit=(10.0, 50.0), p=1.0),
                    A.ImageCompression(quality_range=(60, 95), p=1.0),
                ],
                p=0.4,
            ),
            A.CoarseDropout(
                num_holes_range=(1, 4),
                hole_height_range=(8, 32),
                hole_width_range=(8, 32),
                fill=0,
                p=0.3,
            ),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )

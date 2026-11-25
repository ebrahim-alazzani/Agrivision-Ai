"""
Video Processor for Crop & Field Monitoring.

Performs smart keyframe extraction from field walk-through videos:
- Filters out blurry frames (via Laplacian variance)
- Detects scene changes and moves past redundant frames
- Extracts optimal candidate frames for downstream disease and pest diagnosis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class KeyframeMetadata:
    frame_index: int
    timestamp_sec: float
    sharpness_score: float
    saved_path: Optional[str] = None


class VideoProcessor:
    """
    Extracts high-clarity keyframes from agricultural smartphone video footage.
    """

    def __init__(
        self,
        min_sharpness: float = 80.0,
        similarity_threshold: float = 0.85,
        target_fps: float = 1.0,
    ) -> None:
        """
        Args:
            min_sharpness: Minimum Laplacian variance required to consider a frame non-blurry.
            similarity_threshold: Maximum histogram correlation before a frame is considered redundant.
            target_fps: Sample at most this many frames per second of video.
        """
        self.min_sharpness = min_sharpness
        self.similarity_threshold = similarity_threshold
        self.target_fps = target_fps

    def extract_keyframes(
        self,
        video_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        max_frames: int = 30,
    ) -> List[KeyframeMetadata]:
        """
        Processes video stream, selecting distinct, high-sharpness frames.
        """
        v_path = Path(video_path)
        if not v_path.exists():
            raise FileNotFoundError(f"Video file does not exist: {v_path}")

        cap = cv2.VideoCapture(str(v_path))
        if not cap.isOpened():
            raise IOError(f"Could not open video file: {v_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, int(fps / self.target_fps))

        keyframes: List[KeyframeMetadata] = []
        last_hist: Optional[np.ndarray] = None
        frame_idx = 0

        out_path = Path(output_dir) if output_dir else None
        if out_path:
            out_path.mkdir(parents=True, exist_ok=True)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

                if sharpness >= self.min_sharpness:
                    # Check redundancy with previous selected frame
                    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

                    is_redundant = False
                    if last_hist is not None:
                        sim = cv2.compareHist(last_hist, hist, cv2.HISTCMP_CORREL)
                        if sim > self.similarity_threshold:
                            is_redundant = True

                    if not is_redundant:
                        ts = frame_idx / fps
                        save_dest = None
                        if out_path:
                            save_dest = str(out_path / f"keyframe_{frame_idx:06d}.jpg")
                            cv2.imwrite(save_dest, frame)

                        keyframes.append(
                            KeyframeMetadata(
                                frame_index=frame_idx,
                                timestamp_sec=round(ts, 2),
                                sharpness_score=round(sharpness, 1),
                                saved_path=save_dest,
                            )
                        )
                        last_hist = hist

                        if len(keyframes) >= max_frames:
                            break

            frame_idx += 1

        cap.release()
        logger.info("Extracted %d keyframes from %s", len(keyframes), v_path.name)
        return keyframes

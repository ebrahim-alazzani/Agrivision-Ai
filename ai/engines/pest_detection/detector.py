"""
Pest Detector.

Object detection engine specialized in identifying, localizing, and counting
agricultural insect pests in field images using YOLO architectures with NMS filtering.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from ai.config import DEVICE
from ai.engines.pest_detection.config import DEFAULT_PEST_CLASSES, PestDetectionConfig
from ai.shared.model_interfaces.base_engine import (
    AlternativePrediction,
    BaseAIEngine,
    EngineMetadata,
    EnginePrediction,
)

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    HAS_ULTRALYTICS = True
except ImportError:
    HAS_ULTRALYTICS = False


@dataclass
class DetectedPest:
    """Individual detected pest bounding box and classification."""
    box: List[float]  # [x1, y1, x2, y2] in pixel coords
    class_name: str
    confidence: float
    area: float


class PestDetector(BaseAIEngine):
    """
    Pest detection and counting engine.
    """

    def __init__(
        self,
        config: Optional[PestDetectionConfig] = None,
        model_path: Optional[Union[str, Path]] = None,
        device: Optional[Union[str, Any]] = None,
    ) -> None:
        self.config = config or PestDetectionConfig()
        super().__init__(
            model_path=model_path,
            device=device or DEVICE,
            confidence_threshold=self.config.confidence_threshold,
        )
        self.classes = self.config.classes
        self._yolo = None
        self.load_model()

    def load_model(self) -> None:
        if HAS_ULTRALYTICS and self.model_path and Path(self.model_path).exists():
            try:
                self._yolo = YOLO(str(self.model_path))
                logger.info("Loaded YOLO model from %s", self.model_path)
            except Exception as e:
                logger.warning("Failed to initialize YOLO from %s: %s", self.model_path, e)
                self._yolo = None
        self._is_loaded = True

    def unload_model(self) -> None:
        self._yolo = None
        self._is_loaded = False

    def non_max_suppression_fast(
        self,
        boxes: np.ndarray,
        scores: np.ndarray,
        overlap_thresh: float,
    ) -> List[int]:
        """Applies Non-Maximum Suppression to filter duplicate overlapping detections."""
        if len(boxes) == 0:
            return []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= overlap_thresh)[0]
            order = order[inds + 1]

        return keep

    def predict(
        self,
        input_data: Union[str, Path, Image.Image, np.ndarray],
        conf_thresh: Optional[float] = None,
        iou_thresh: Optional[float] = None,
        **kwargs,
    ) -> EnginePrediction:
        """
        Detects pests and returns bounding boxes, counts, and classification summary.
        """
        start_t = time.perf_counter()
        c_thresh = conf_thresh or self.config.confidence_threshold
        i_thresh = iou_thresh or self.config.iou_threshold

        # Load image array
        if isinstance(input_data, (str, Path)):
            img = cv2.imread(str(input_data))
            if img is None:
                raise IOError(f"Could not load image: {input_data}")
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif isinstance(input_data, Image.Image):
            rgb = np.asarray(input_data.convert("RGB"))
        elif isinstance(input_data, np.ndarray):
            rgb = input_data
        else:
            raise TypeError(f"Unsupported input: {type(input_data)}")

        detected_pests: List[DetectedPest] = []
        per_class_counts: Dict[str, int] = {c: 0 for c in self.classes}

        if self._yolo is not None:
            results = self._yolo.predict(
                source=rgb,
                conf=c_thresh,
                iou=i_thresh,
                imgsz=self.config.image_size,
                verbose=False,
            )
            for res in results:
                for box in res.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    cls_name = self.classes[cls_id] if cls_id < len(self.classes) else f"pest_{cls_id}"
                    area = float((xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1]))

                    pest = DetectedPest(
                        box=[round(c, 1) for c in xyxy],
                        class_name=cls_name,
                        confidence=round(conf, 4),
                        area=round(area, 1),
                    )
                    detected_pests.append(pest)
                    per_class_counts[cls_name] = per_class_counts.get(cls_name, 0) + 1

        total_count = len(detected_pests)
        dominant_pest = "none_detected"
        dominant_conf = 0.0

        if total_count > 0:
            # Sort by frequency
            freq = sorted(per_class_counts.items(), key=lambda x: x[1], reverse=True)
            dominant_pest = freq[0][0]
            confs = [p.confidence for p in detected_pests if p.class_name == dominant_pest]
            dominant_conf = float(np.mean(confs)) if confs else 0.0

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        return EnginePrediction(
            engine_name="PestDetector",
            task="pest_detection",
            primary_label=dominant_pest,
            confidence=round(dominant_conf, 4),
            is_confident=dominant_conf >= c_thresh if total_count > 0 else True,
            requires_expert_review=total_count > 20 or (total_count > 0 and dominant_conf < 0.6),
            execution_time_ms=round(elapsed_ms, 2),
            model_version="yolo_pest_v1",
            details={
                "total_pest_count": total_count,
                "counts_by_pest": {k: v for k, v in per_class_counts.items() if v > 0},
                "detections": [asdict(p) for p in detected_pests],
            },
        )

    def draw_detections(self, image: np.ndarray, detections: List[DetectedPest]) -> np.ndarray:
        """Draws bounding boxes and labels on an image array."""
        out = image.copy()
        for p in detections:
            x1, y1, x2, y2 = [int(v) for v in p.box]
            cv2.rectangle(out, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label = f"{p.class_name} {p.confidence:.2f}"
            cv2.putText(out, label, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        return out

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_name="PestDetector",
            version="1.0.0",
            model_architecture="yolov8",
            model_version="v1.0.0",
            device=str(self.device),
            supported_tasks=["pest_detection", "pest_counting"],
            confidence_threshold=self.confidence_threshold,
            extra={"pest_classes": self.classes},
        )

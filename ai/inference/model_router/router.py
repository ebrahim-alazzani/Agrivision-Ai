"""
Hybrid Model Router.

Intelligently orchestrates edge (mobile phone on-device) vs. cloud server inference:
- Decides execution target based on task complexity, connectivity status, and device capability
- Dispatches to lightweight quantized MobileNet models on device vs heavy ResNet/YOLO in the cloud
- Ensures seamless offline operation with queued cloud sync.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExecutionTarget(str, Enum):
    EDGE_DEVICE = "edge_device"
    CLOUD_SERVER = "cloud_server"


class NetworkState(str, Enum):
    OFFLINE = "offline"
    POOR_2G_3G = "poor_cellular"
    GOOD_WIFI_4G = "good_connection"


@dataclass
class RoutingDecision:
    target: ExecutionTarget
    selected_engine: str
    model_name: str
    reason: str
    allow_offline_queue: bool = False


class ModelRouter:
    """
    Directs diagnostic inference workloads to edge or cloud runtime.
    """

    def __init__(self) -> None:
        # Registry of edge-capable vs cloud-only tasks
        self.edge_capable_tasks = {
            "disease_screening": "mobilenetv3_small_quantized",
            "crop_identification": "mobilenetv3_crop",
            "image_quality_check": "laplacian_heuristics",
        }
        self.cloud_exclusive_tasks = {
            "disease_deep_classification": "resnet50_full_precision",
            "pest_detection": "yolov8m_pest",
            "temporal_change_analysis": "temporal_analyzer",
            "video_processing": "video_keyframe_processor",
            "full_dossier_fusion": "decision_support_engine",
        }

    def route_request(
        self,
        task: str,
        network_state: NetworkState = NetworkState.GOOD_WIFI_4G,
        device_memory_mb: int = 4096,
        user_tier: str = "standard",
    ) -> RoutingDecision:
        """
        Determines whether to compute locally on phone or stream to cloud server.
        """
        # Case 1: Device is completely offline
        if network_state == NetworkState.OFFLINE:
            if task in self.edge_capable_tasks:
                return RoutingDecision(
                    target=ExecutionTarget.EDGE_DEVICE,
                    selected_engine="edge_plant_vision",
                    model_name=self.edge_capable_tasks[task],
                    reason="Device offline. Executing rapid on-device quantized model.",
                    allow_offline_queue=True,
                )
            else:
                return RoutingDecision(
                    target=ExecutionTarget.EDGE_DEVICE,
                    selected_engine="offline_queue_manager",
                    model_name="none",
                    reason=f"Task '{task}' requires high-parameter server models. Job queued locally until internet reconnects.",
                    allow_offline_queue=True,
                )

        # Case 2: Poor connectivity (high packet loss or slow 2G/3G in rural valleys)
        if network_state == NetworkState.POOR_2G_3G:
            if task in self.edge_capable_tasks:
                return RoutingDecision(
                    target=ExecutionTarget.EDGE_DEVICE,
                    selected_engine="edge_plant_vision",
                    model_name=self.edge_capable_tasks[task],
                    reason="Low bandwidth detected. Performing edge inference to save data and provide instant feedback.",
                    allow_offline_queue=True,
                )

        # Case 3: Good connection or cloud-exclusive tasks
        if task in self.cloud_exclusive_tasks:
            return RoutingDecision(
                target=ExecutionTarget.CLOUD_SERVER,
                selected_engine=task,
                model_name=self.cloud_exclusive_tasks[task],
                reason=f"Task '{task}' requires server-class GPU acceleration and full precision weights.",
                allow_offline_queue=False,
            )

        # Default fallback to server for highest diagnostic fidelity
        return RoutingDecision(
            target=ExecutionTarget.CLOUD_SERVER,
            selected_engine="cloud_plant_vision",
            model_name="resnet50_full_precision",
            reason="Good network connectivity. Utilizing cloud high-precision model for maximum accuracy.",
            allow_offline_queue=False,
        )

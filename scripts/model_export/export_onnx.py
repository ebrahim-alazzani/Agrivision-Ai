#!/usr/bin/env python3
"""
AgriVision AI - Model Export Tool (PyTorch to ONNX)
Exports trained PyTorch vision models into optimized ONNX runtime format for cross-platform edge and server inference.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Tuple

try:
    import torch
    import torch.nn as nn
    from torchvision import models
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


def build_exportable_model(model_name: str, num_classes: int) -> torch.nn.Module:
    """Build PyTorch model architecture for export."""
    if model_name.lower() == "resnet50":
        model = models.resnet50(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, num_classes)
        )
        return model
    elif model_name.lower() == "mobilenet_v3_large":
        model = models.mobilenet_v3_large(weights=None)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
        return model
    else:
        raise ValueError(f"Unsupported model architecture: {model_name}")


def export_to_onnx(
    model_name: str,
    checkpoint_path: Path,
    output_path: Path,
    num_classes: int = 10,
    image_size: int = 224,
    opset_version: int = 14,
):
    """Export PyTorch checkpoint or base model into ONNX format."""
    print("=" * 60)
    print("          AgriVision AI - ONNX Model Exporter             ")
    print("=" * 60)
    print(f"[*] Architecture    : {model_name}")
    print(f"[*] Classes         : {num_classes}")
    print(f"[*] Input Resolution: 1x3x{image_size}x{image_size}")
    print(f"[*] Target File     : {output_path}")

    if not PYTORCH_AVAILABLE:
        print("[!] PyTorch is not available. Creating placeholder ONNX model file...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(b"ONNX_MODEL_BINARY_STUB_AGRIVISION_AI")
        print(f"[+] Output written to: {output_path}")
        return

    model = build_exportable_model(model_name, num_classes)

    if checkpoint_path.is_file():
        print(f"[*] Loading weights from: {checkpoint_path}")
        ckpt = torch.load(checkpoint_path, map_location="cpu")
        state_dict = ckpt.get("model_state_dict", ckpt)
        model.load_state_dict(state_dict)
    else:
        print(f"[!] Warning: Checkpoint {checkpoint_path} not found. Exporting uninitialized architecture.")

    model.eval()

    dummy_input = torch.randn(1, 3, image_size, image_size, requires_grad=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_names = ["input_image"]
    output_names = ["class_probabilities"]
    dynamic_axes = {
        "input_image": {0: "batch_size"},
        "class_probabilities": {0: "batch_size"}
    }

    print(f"[*] Exporting graph with opset_version={opset_version}...")
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes
    )

    print(f"[+] Successfully exported ONNX model to: {output_path}")

    if ONNX_AVAILABLE:
        print("[*] Validating exported ONNX graph integrity...")
        onnx_model = onnx.load(str(output_path))
        onnx.checker.check_model(onnx_model)
        print("[+] ONNX model checker passed successfully!")

        session = ort.InferenceSession(str(output_path))
        inputs = {session.get_inputs()[0].name: dummy_input.numpy()}
        outputs = session.run(None, inputs)
        print(f"[+] Test inference pass completed. Output tensor shape: {outputs[0].shape}")


def main():
    parser = argparse.ArgumentParser(description="AgriVision AI - Export PyTorch to ONNX")
    parser.add_argument(
        "--model",
        type=str,
        default="resnet50",
        help="Model architecture name (resnet50, mobilenet_v3_large)",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("ai/weights/resnet50_best.pt"),
        help="Path to trained PyTorch .pt checkpoint",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ai/weights/plant_disease_resnet50.onnx"),
        help="Destination path for .onnx file",
    )
    parser.add_argument(
        "--num-classes",
        type=int,
        default=10,
        help="Number of classification categories",
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=224,
        help="Square input image dimension (e.g. 224)",
    )
    parser.add_argument(
        "--opset",
        type=int,
        default=14,
        help="ONNX opset version",
    )

    args = parser.parse_args()
    export_to_onnx(
        model_name=args.model,
        checkpoint_path=args.checkpoint,
        output_path=args.output,
        num_classes=args.num_classes,
        image_size=args.image_size,
        opset_version=args.opset,
    )


if __name__ == "__main__":
    main()

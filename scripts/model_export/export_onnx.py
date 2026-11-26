"""Export a reviewed checkpoint to ONNX and verify PyTorch/ORT parity.

This script deliberately refuses placeholder models and missing checkpoints.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torchvision import models


def build_model(name: str, count: int) -> nn.Module:
    if count < 2:
        raise ValueError("num_classes must be at least 2")
    if name.lower() == "resnet50":
        model = models.resnet50(weights=None)
        model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(model.fc.in_features, count))
    elif name.lower() == "mobilenet_v3_large":
        model = models.mobilenet_v3_large(weights=None)
        in_features = model.classifier[0].in_features
        model.classifier = nn.Sequential(
            nn.Linear(in_features, 512), nn.BatchNorm1d(512), nn.Hardswish(inplace=True),
            nn.Dropout(p=0.3), nn.Linear(512, count),
        )
    else:
        raise ValueError(f"Unsupported architecture: {name}")
    return model


def export(model_name: str, checkpoint: Path, destination: Path, count: int,
           image_size: int, opset: int, max_abs_error: float) -> None:
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Refusing to export without a trained checkpoint: {checkpoint}")
    try:
        import onnx
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError("Install both onnx and onnxruntime to validate the export") from exc

    payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    state = payload.get("model_state_dict", payload) if isinstance(payload, dict) else payload
    if not isinstance(state, dict) or not state:
        raise ValueError("Checkpoint does not contain a model state dictionary")
    declared = payload.get("num_classes") if isinstance(payload, dict) else None
    if declared is not None and int(declared) != count:
        raise ValueError(f"Checkpoint has {declared} classes but --num-classes is {count}")
    class_map = payload.get("class_to_idx") if isinstance(payload, dict) else None
    if not isinstance(class_map, dict) or len(class_map) != count:
        raise ValueError("Checkpoint must include a class_to_idx map matching --num-classes")
    class_map = {str(label): int(index) for label, index in class_map.items()}
    if sorted(class_map.values()) != list(range(count)):
        raise ValueError("Checkpoint class_to_idx must map labels bijectively to 0..num_classes-1")

    model = build_model(model_name, count)
    try:
        model.load_state_dict(state, strict=True)
    except RuntimeError as exc:
        raise ValueError("Checkpoint architecture/head does not match the selected exporter") from exc
    model.eval()

    destination.parent.mkdir(parents=True, exist_ok=True)
    sample = torch.randn(1, 3, image_size, image_size, dtype=torch.float32)
    with torch.inference_mode():
        expected = model(sample).cpu().numpy()
    torch.onnx.export(
        model, sample, str(destination), export_params=True, opset_version=opset,
        do_constant_folding=True, input_names=["input"], output_names=["logits"],
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
    )
    graph = onnx.load(str(destination))
    onnx.checker.check_model(graph)
    session = ort.InferenceSession(str(destination), providers=["CPUExecutionProvider"])
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    if len(inputs) != 1 or inputs[0].name != "input" or inputs[0].type != "tensor(float)":
        raise ValueError("Unexpected ONNX input contract")
    if len(outputs) != 1 or outputs[0].name != "logits":
        raise ValueError("Unexpected ONNX output contract")
    actual = session.run(["logits"], {"input": sample.numpy()})[0]
    if actual.shape != (1, count) or not np.isfinite(actual).all():
        raise ValueError(f"Invalid ONNX output shape or non-finite values: {actual.shape}")
    error = float(np.max(np.abs(expected - actual)))
    if error > max_abs_error:
        raise ValueError(f"PyTorch/ONNX parity failed: max abs error={error:.8g} > {max_abs_error}")
    label_map = {
        "num_classes": count,
        "class_to_idx": class_map,
        "idx_to_class": {str(index): label for label, index in class_map.items()},
        "arabic_labels": payload.get("arabic_labels", {}),
    }
    destination.with_name("class_indices.json").write_text(
        json.dumps(label_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Export verified: {destination} | classes={count} | max_abs_error={error:.8g}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["resnet50", "mobilenet_v3_large"], default="mobilenet_v3_large")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--num-classes", type=int, required=True)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--opset", type=int, default=17)
    parser.add_argument("--max-abs-error", type=float, default=1e-4)
    args = parser.parse_args()
    export(args.model, args.checkpoint, args.output, args.num_classes,
           args.image_size, args.opset, args.max_abs_error)


if __name__ == "__main__":
    main()

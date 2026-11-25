#!/usr/bin/env python3
"""
AgriVision AI - PlantVillage Dataset Importer
Transforms directory-structured PlantVillage crop pathology datasets into AgriVision AI standardized sample manifests.
"""

import argparse
import json
import os
import sys
import uuid
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Tuple

# Mapping of PlantVillage class folder names to AgriVision IDs
PLANTVILLAGE_MAPPING = {
    "Tomato___Early_blight": {
        "crop_id": "crop-tomato",
        "disease_id": "dis-early-blight",
        "severity_label": "medium",
    },
    "Tomato___Late_blight": {
        "crop_id": "crop-tomato",
        "disease_id": "dis-late-blight",
        "severity_label": "high",
    },
    "Tomato___healthy": {
        "crop_id": "crop-tomato",
        "disease_id": None,
        "severity_label": "healthy",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop_id": "crop-tomato",
        "disease_id": "dis-tylcv",
        "severity_label": "high",
    },
    "Potato___Early_blight": {
        "crop_id": "crop-potato",
        "disease_id": "dis-early-blight",
        "severity_label": "medium",
    },
    "Potato___Late_blight": {
        "crop_id": "crop-potato",
        "disease_id": "dis-late-blight",
        "severity_label": "high",
    },
    "Potato___healthy": {
        "crop_id": "crop-potato",
        "disease_id": None,
        "severity_label": "healthy",
    },
    "Grape___Black_rot": {
        "crop_id": "crop-grape",
        "disease_id": "dis-black-rot",
        "severity_label": "medium",
    },
    "Grape___healthy": {
        "crop_id": "crop-grape",
        "disease_id": None,
        "severity_label": "healthy",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop_id": "crop-grape",
        "disease_id": "dis-leaf-blight",
        "severity_label": "medium",
    },
}


def parse_plantvillage_folder(folder_name: str) -> Tuple[Optional[str], Optional[str], str]:
    """Parse raw class name or retrieve from mapping."""
    if folder_name in PLANTVILLAGE_MAPPING:
        m = PLANTVILLAGE_MAPPING[folder_name]
        return m["crop_id"], m["disease_id"], m["severity_label"]

    # Fallback heuristic parser: Plant___Disease
    if "___" in folder_name:
        plant, cond = folder_name.split("___", 1)
        crop_id = f"crop-{plant.lower()}"
        if "healthy" in cond.lower():
            return crop_id, None, "healthy"
        dis_id = f"dis-{cond.lower().replace('_', '-')}"
        return crop_id, dis_id, "medium"

    return "crop-unknown", None, "unspecified"


def import_plantvillage(source_dir: Path, output_manifest: Path, dataset_version: str = "v1.0.0"):
    """Scan PlantVillage hierarchy and generate AgriVision sample metadata manifest."""
    print(f"[*] Scanning PlantVillage directory: {source_dir}")
    samples = []
    supported_extensions = {".jpg", ".jpeg", ".png"}

    for class_dir in sorted(source_dir.iterdir()):
        if not class_dir.is_dir():
            continue

        folder_name = class_dir.name
        crop_id, disease_id, default_severity = parse_plantvillage_folder(folder_name)

        images = [p for p in class_dir.glob("*") if p.suffix.lower() in supported_extensions]
        print(f"  -> Found {len(images)} images in class: {folder_name} (Crop: {crop_id}, Disease: {disease_id})")

        for idx, img_path in enumerate(images):
            sample_record = {
                "sample_id": f"PV-{crop_id.replace('crop-', '')[:3].upper()}-{idx:06d}-{uuid.uuid4().hex[:6]}",
                "crop_id": crop_id,
                "disease_id": disease_id,
                "pest_id": None,
                "image_path": str(img_path.resolve()),
                "capture_date": str(date.today()),
                "governorate_id": None,
                "district_id": None,
                "farm_id": None,
                "growth_stage": "vegetative",
                "severity_label": default_severity,
                "annotation_status": "expert_validated",
                "annotator_id": None,
                "reviewer_id": None,
                "source": "plantvillage_open_dataset",
                "license": "CC-BY-SA-4.0",
                "dataset_version": dataset_version,
            }
            samples.append(sample_record)

    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest_payload = {
        "dataset_name": "PlantVillage-AgriVision-Normalized",
        "version": dataset_version,
        "total_samples": len(samples),
        "license": "CC-BY-SA-4.0",
        "samples": samples,
    }

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Successfully imported {len(samples)} samples.")
    print(f"[+] AgriVision metadata manifest saved to: {output_manifest}")


def main():
    parser = argparse.ArgumentParser(description="AgriVision AI - PlantVillage Importer")
    parser.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Path to unzipped PlantVillage directory containing class subfolders",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        default=Path("data/manifests/plantvillage_manifest.json"),
        help="Output manifest destination path",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1.0.0",
        help="Dataset version tag to assign to records",
    )

    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"Error: Source directory {args.source_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    import_plantvillage(args.source_dir, args.output_manifest, args.version)


if __name__ == "__main__":
    main()

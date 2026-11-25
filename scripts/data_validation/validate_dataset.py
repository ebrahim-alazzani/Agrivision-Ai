#!/usr/bin/env python3
"""
AgriVision AI - Dataset Validation & Integrity Tool
Validates image files, metadata adherence, class distribution, and detects duplicates.
"""

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file for duplicate detection."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def verify_image(filepath: Path) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]]]:
    """Verify image file integrity, readability, and dimensions."""
    if Image is None:
        return True, None, None  # PIL not available; skip deep check
    try:
        with Image.open(filepath) as img:
            img.verify()
        # Re-open for dimension inspection after verify() closes the file
        with Image.open(filepath) as img:
            dims = img.size
            if dims[0] < 32 or dims[1] < 32:
                return False, f"Image dimensions too small: {dims}", dims
            return True, None, dims
    except Exception as e:
        return False, str(e), None


def validate_metadata_entry(entry: dict, required_fields: List[str]) -> List[str]:
    """Check required fields and basic constraints in metadata record."""
    missing = [f for f in required_fields if f not in entry or entry[f] is None]
    return missing


def run_validation(data_dir: Path, manifest_path: Optional[Path]) -> dict:
    """Execute complete validation suite on directory or manifest."""
    print(f"[*] Starting dataset validation in: {data_dir}")
    required_fields = [
        "sample_id",
        "crop_id",
        "image_path",
        "capture_date",
        "growth_stage",
        "annotation_status",
    ]

    results = {
        "total_images_scanned": 0,
        "valid_images": 0,
        "corrupt_images": [],
        "duplicate_groups": {},
        "metadata_entries": 0,
        "metadata_errors": [],
        "crop_distribution": {},
        "disease_distribution": {},
        "severity_distribution": {},
        "summary": "PASSED",
    }

    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
    image_files = [
        p for p in data_dir.rglob("*") if p.is_file() and p.suffix.lower() in image_extensions
    ]
    results["total_images_scanned"] = len(image_files)

    hashes: Dict[str, List[str]] = {}
    print(f"[*] Found {len(image_files)} image files. Inspecting integrity and hashes...")

    for img_path in image_files:
        is_valid, err, dims = verify_image(img_path)
        if not is_valid:
            results["corrupt_images"].append({"file": str(img_path), "error": err})
        else:
            results["valid_images"] += 1
            h = compute_sha256(img_path)
            hashes.setdefault(h, []).append(str(img_path.relative_to(data_dir)))

    # Identify duplicates
    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    results["duplicate_groups"] = duplicates
    if duplicates:
        print(f"[!] Warning: Found {len(duplicates)} duplicate image clusters.")

    # Validate metadata if manifest or metadata JSONs exist
    records = []
    if manifest_path and manifest_path.is_file():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data if isinstance(data, list) else data.get("samples", [])
        except Exception as e:
            results["metadata_errors"].append(f"Failed to parse manifest: {e}")

    crop_counter = Counter()
    disease_counter = Counter()
    severity_counter = Counter()

    results["metadata_entries"] = len(records)
    for rec in records:
        missing = validate_metadata_entry(rec, required_fields)
        if missing:
            results["metadata_errors"].append(
                {"sample_id": rec.get("sample_id", "unknown"), "missing_fields": missing}
            )
        crop_counter[rec.get("crop_id", "unknown")] += 1
        disease_counter[rec.get("disease_id", "healthy_or_unspecified")] += 1
        severity_counter[rec.get("severity_label", "unspecified")] += 1

    results["crop_distribution"] = dict(crop_counter)
    results["disease_distribution"] = dict(disease_counter)
    results["severity_distribution"] = dict(severity_counter)

    if results["corrupt_images"] or results["metadata_errors"]:
        results["summary"] = "FAILED"
    elif results["duplicate_groups"]:
        results["summary"] = "WARNINGS"

    return results


def main():
    parser = argparse.ArgumentParser(
        description="AgriVision AI - Agricultural Dataset Integrity Validator"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Path to folder containing dataset images and metadata",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional path to dataset manifest JSON or JSONL file",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        default=None,
        help="Optional output path to save JSON validation report",
    )

    args = parser.parse_args()

    if not args.data_dir.exists():
        print(f"Error: Data directory does not exist: {args.data_dir}", file=sys.stderr)
        sys.exit(1)

    report = run_validation(args.data_dir, args.manifest)

    print("\n" + "=" * 60)
    print("             AgriVision AI Validation Summary              ")
    print("=" * 60)
    print(f"Status               : {report['summary']}")
    print(f"Images Scanned       : {report['total_images_scanned']}")
    print(f"Valid Images         : {report['valid_images']}")
    print(f"Corrupted Images     : {len(report['corrupt_images'])}")
    print(f"Duplicate Image Sets : {len(report['duplicate_groups'])}")
    print(f"Metadata Records     : {report['metadata_entries']}")
    print(f"Metadata Errors      : {len(report['metadata_errors'])}")

    if report["crop_distribution"]:
        print("\n--- Crop Distribution ---")
        for crop, count in report["crop_distribution"].items():
            print(f"  {crop}: {count}")

    if report["disease_distribution"]:
        print("\n--- Disease Distribution ---")
        for dis, count in report["disease_distribution"].items():
            print(f"  {dis}: {count}")

    if args.output_report:
        with open(args.output_report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Full report saved to: {args.output_report}")

    sys.exit(0 if report["summary"] in ("PASSED", "WARNINGS") else 1)


if __name__ == "__main__":
    main()

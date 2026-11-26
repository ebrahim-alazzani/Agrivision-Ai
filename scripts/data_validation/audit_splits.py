"""Fail-closed audit for immutable train/validation/test image manifests.

Manifest CSV columns: split,path,label,group_id. Paths are resolved relative to
--data-root unless absolute. A SHA-256 pass catches exact duplicates even when
paths differ. Group IDs should identify a plant/scene/capture, not be guessed
from filenames. This tool never modifies the dataset.
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = {"split", "path", "label", "group_id"}
EXPECTED = {"train", "validation", "test"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(manifest: Path, data_root: Path) -> dict:
    rows = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or [])
        if not REQUIRED.issubset(fields):
            raise ValueError(f"Manifest needs columns: {', '.join(sorted(REQUIRED))}")
        for line, row in enumerate(reader, start=2):
            split = row["split"].strip().lower()
            if split not in EXPECTED:
                raise ValueError(f"Line {line}: split must be one of {sorted(EXPECTED)}")
            if not row["label"].strip() or not row["group_id"].strip():
                raise ValueError(f"Line {line}: label and group_id must be non-empty")
            p = Path(row["path"].strip())
            if not p.is_absolute():
                p = data_root / p
            if not p.is_file():
                raise ValueError(f"Line {line}: image file not found: {p}")
            rows.append({"split": split, "label": row["label"].strip(),
                         "group_id": row["group_id"].strip(), "path": p,
                         "sha256": sha256(p)})
    if not rows:
        raise ValueError("Manifest has no samples")
    present = {row["split"] for row in rows}
    missing = EXPECTED - present
    if missing:
        raise ValueError(f"Missing required held-out split(s): {sorted(missing)}")
    groups = defaultdict(set)
    hashes = defaultdict(set)
    class_counts = {split: Counter() for split in EXPECTED}
    for row in rows:
        groups[row["group_id"]].add(row["split"])
        hashes[row["sha256"]].add(row["split"])
        class_counts[row["split"]][row["label"]] += 1
    group_leaks = sorted(k for k, v in groups.items() if len(v) > 1)
    duplicate_leaks = sorted(k for k, v in hashes.items() if len(v) > 1)
    labels = set().union(*(set(counts) for counts in class_counts.values()))
    missing_classes = {split: sorted(labels - set(class_counts[split])) for split in EXPECTED}
    return {
        "status": "FAILED" if group_leaks or duplicate_leaks or any(missing_classes.values()) else "PASSED",
        "samples": len(rows), "counts_by_split": {k: sum(v.values()) for k, v in class_counts.items()},
        "classes": sorted(labels), "class_counts_by_split": {k: dict(v) for k, v in class_counts.items()},
        "missing_classes_by_split": missing_classes,
        "group_leak_count": len(group_leaks), "duplicate_hash_leak_count": len(duplicate_leaks),
        "group_leaks_sample": group_leaks[:20], "duplicate_hashes_sample": duplicate_leaks[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.manifest, args.data_root)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

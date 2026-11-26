import csv

from scripts.data_validation.audit_splits import audit


def write_manifest(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["split", "path", "label", "group_id"])
        writer.writeheader()
        writer.writerows(rows)


def test_requires_independent_test_split(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"a")
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [
        {"split": "train", "path": "a.jpg", "label": "healthy", "group_id": "plant-a"},
        {"split": "validation", "path": "a.jpg", "label": "healthy", "group_id": "plant-a"},
    ])
    try:
        audit(manifest, tmp_path)
        assert False, "missing test data must fail"
    except ValueError as error:
        assert "test" in str(error)


def test_detects_cross_split_group_and_duplicate_leaks(tmp_path):
    for name in ("a.jpg", "b.jpg", "c.jpg"):
        (tmp_path / name).write_bytes(name.encode())
    (tmp_path / "d.jpg").write_bytes(b"a.jpg")
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [
        {"split": "train", "path": "a.jpg", "label": "healthy", "group_id": "plant-1"},
        {"split": "validation", "path": "b.jpg", "label": "healthy", "group_id": "plant-2"},
        {"split": "test", "path": "c.jpg", "label": "healthy", "group_id": "plant-3"},
        {"split": "test", "path": "d.jpg", "label": "healthy", "group_id": "plant-1"},
    ])
    result = audit(manifest, tmp_path)
    assert result["status"] == "FAILED"
    assert result["group_leak_count"] == 1
    assert result["duplicate_hash_leak_count"] == 1

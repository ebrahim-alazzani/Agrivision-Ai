# AgriVision Test Sample Fixtures (بيانات العينات التجريبية)

This directory is reserved for small, curated test fixtures, mock metadata records, and sample images used strictly for continuous integration (CI), unit tests, and pipeline verification.

---

## 1. Directory Structure

```text
data/samples/
├── README.md                  # This guide
├── metadata/                  # JSON metadata records matching sample_metadata.json
│   ├── sample_tomato_lb.json
│   └── sample_coffee_rust.json
└── images/                    # Lightweight test images (<500 KB each)
    ├── tomato_early_blight_01.jpg
    ├── tomato_late_blight_01.jpg
    └── coffee_rust_01.jpg
```

---

## 2. Guidelines for Adding Test Samples

1. **Size Limit**:
   - Each sample image must be strictly under **500 KB**.
   - Standard resolution for fixtures: 512x512 or 224x224 JPEG/PNG.
   - Do NOT commit full-resolution raw field datasets here.

2. **Naming Convention**:
   - Format: `<crop>_<disease_or_pest_or_healthy>_<index>.<ext>`
   - Examples:
     - `tomato_late_blight_001.jpg`
     - `coffee_leaf_rust_002.jpg`
     - `potato_healthy_001.jpg`

3. **Metadata Matching**:
   - For every image fixture added under `images/`, provide a corresponding descriptor entry or JSON record matching [`data/schemas/sample_metadata.json`](../schemas/sample_metadata.json).

4. **Consent & Verification**:
   - All sample images must have verified open licenses (e.g. CC0, CC-BY) or signed non-confidential research consent from the capturing agronomist.

# AgriVision Data Layer (طبقة البيانات ومستودعات المعرفة)

This directory serves as the centralized metadata registry, schema validation layer, and manifest store for all agricultural datasets and agronomy domain knowledge used across AgriVision AI.

---

## 1. What Belongs Here

✅ **Permitted in Version Control**:
- **Schemas (`data/schemas/`)**: JSON Schemas defining sample metadata, diagnostic analysis results, and model cards.
- **Manifests (`data/manifests/`)**: Standardized catalogs of Yemeni governorates, supported crops, plant diseases, pests, and agro-climatic boundaries.
- **Sample Metadata & Fixtures (`data/samples/`)**: Lightweight test fixtures and small sets of validated sample image descriptors for unit and integration testing.

❌ **NOT Permitted in Version Control**:
- Raw high-resolution training/validation images.
- Uncompressed video files or drone survey rasters.
- Large archive files (`.zip`, `.tar.gz`, `.h5`, `.parquet`).
- Direct training datasets (e.g. 50GB of PlantVillage or field survey folders).
- Model weights or binary checkpoints (`.pt`, `.onnx`).

---

## 2. Directory Structure

```text
data/
├── README.md                           # This guide
├── manifests/                          # Canonical domain catalogs
│   ├── yemen_governorates.json         # 22 Yemeni governorates + coords
│   ├── supported_crops.json            # Agricultural crop definitions
│   ├── diseases_catalog.json           # Plant pathology knowledge base
│   └── pests_catalog.json              # Entomological pest catalog
├── schemas/                            # Strict JSON Schemas
│   ├── sample_metadata.json            # Dataset image sample metadata
│   ├── analysis_result.json            # Diagnostic inference output format
│   └── model_card.json                 # Model governance and benchmark schema
└── samples/                            # Curated testing samples
    └── README.md                       # Instructions for adding test fixtures
```

---

## 3. How to Add and Ingest Datasets

To import or prepare a new dataset for model training:
1. Store raw files in the designated MinIO / S3 object storage bucket under `s3://agrivision-datasets/<dataset_name>/v<version>/`.
2. Generate or extract metadata complying with [`data/schemas/sample_metadata.json`](schemas/sample_metadata.json).
3. Validate dataset integrity using the validation CLI:
   ```bash
   python scripts/data_validation/validate_dataset.py --data-dir /path/to/extracted/dataset --schema data/schemas/sample_metadata.json
   ```
4. For PlantVillage or public archives, use dedicated importer scripts:
   ```bash
   python scripts/dataset_import/import_plantvillage.py --source-dir /raw/plantvillage --output-manifest data/manifests/plantvillage_manifest.json
   ```

---

## 4. License and Data Governance Requirements

Every ingested sample and dataset must declare an explicit, legally compliant license attribute (`CC-BY-4.0`, `CC-BY-SA-4.0`, `Open-Access-Academic`, or `Proprietary-Consented-AgriVision`). Field images collected directly from Yemeni farmers require documented informed consent regarding non-commercial agronomic research and AI training.

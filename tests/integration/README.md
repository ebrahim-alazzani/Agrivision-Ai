# Integration Testing Guidelines (إرشادات اختبارات التكامل)

Integration tests in AgriVision AI verify the interaction between multiple decoupled services: FastAPI backend, PostgreSQL/PostGIS database, Redis cache/broker, MinIO S3 storage, and PyTorch AI inference services.

---

## 1. Scope & Objectives
- **Spatial Queries**: Ensure PostGIS queries correctly calculate farm boundaries, intersection of regional disease outbreak zones, and nearest weather stations.
- **Object Storage Flow**: Test image uploads through backend presigned URLs to MinIO buckets and ensure clean cleanup on failed uploads.
- **Inference Pipeline**: Verify end-to-end routing from image submission -> background worker -> AI inference -> schema-validated result storage.

---

## 2. Directory Structure

```text
tests/integration/
├── README.md                  # This guide
├── conftest.py                # Pytest fixtures (DB sessions, MinIO client, Redis client)
├── test_database_spatial.py   # PostGIS queries & geospatial integrity
├── test_storage_s3.py         # MinIO image upload & retrieval
├── test_inference_pipeline.py # Backend to AI service workflow
└── test_weather_integration.py# Weather API synchronization
```

---

## 3. Running Integration Tests

Ensure backing services are running before launching tests:
```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres redis minio
```

Run tests with `pytest`:
```bash
pytest tests/integration/ -v --durations=10
```

---

## 4. Best Practices
- Use test containers or isolated test databases (`agrivision_test`) with automatic rollbacks.
- Never write tests that mutate shared production or persistent seed tables without cleaning up.
- Mock external third-party internet APIs (such as global commercial weather APIs) unless explicitly running live integration smoke tests.

# API Contract Testing Guidelines (إرشادات اختبارات عقود الواجهات البرمجية)

Contract tests guarantee that the FastAPI backend API adheres strictly to OpenAPI 3.1 specifications and defined JSON schemas, preventing breaking changes for client applications (such as the Flutter Farmer Mobile App and AI Studio).

---

## 1. Scope & Strategy
- **OpenAPI Schema Validation**: Ensure every response from `/api/v1/*` conforms to the generated Pydantic models.
- **Diagnostic Result Contract**: Ensure output from `/api/v1/analyze/disease` strictly conforms to [`data/schemas/analysis_result.json`](../../data/schemas/analysis_result.json).
- **Client Backward Compatibility**: Verify that newly introduced fields are optional so older mobile versions do not crash.

---

## 2. Directory Structure

```text
tests/contract/
├── README.md                      # This guide
├── test_openapi_schema.py         # OpenAPI schema compliance test
├── test_analysis_result_schema.py # Diagnostic result JSON Schema validator
└── test_mobile_contract.py        # Mobile app endpoint payload contracts
```

---

## 3. Running Contract Tests

Contract tests do not require a running database; they can run against FastAPI `TestClient`:
```bash
pytest tests/contract/ -v
```

---

## 4. Contract Rules
1. **Never rename or remove existing field keys** in active `/api/v1/` routes without deprecation warnings across two release cycles.
2. Coordinate with the mobile team (`apps/farmer_mobile`) whenever a field type or enum set is expanded.
3. Every new route must have an explicit response model defined with Pydantic.

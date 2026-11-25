# Contributing to AgriVision AI (إرشادات المساهمة في أجريفيجن)

Thank you for your interest in contributing to AgriVision AI! This project aims to bring state-of-the-art agricultural computer vision and decision support to Yemeni farmers, agronomists, and researchers.

---

## 1. Code of Conduct and Ethics
AgriVision AI adheres to ethical agricultural and data safety standards:
- Always consider the local Yemeni agricultural context, crop safety, and water preservation.
- Recommendations regarding pesticides must follow verified integrated pest management (IPM) guidelines.
- Never hardcode sensitive agricultural field coordinates or private user identifying information.

---

## 2. Git Workflow

We use a feature-branch workflow:
1. **Fork or Clone**: Ensure your local copy is up to date with `main`.
2. **Branch Naming**:
   - `feature/short-description` (e.g., `feature/pesticide-ocr-trocr`)
   - `fix/issue-description` (e.g., `fix/yemen-governorate-coordinates`)
   - `docs/doc-topic` (e.g., `docs/crop-monitoring-spec`)
3. **Commits**:
   - Write clear, imperative commit messages (e.g., `Add PostGIS spatial index for farm boundary queries`).
4. **Pull Requests**:
   - Provide a concise description of what was changed, testing steps, and relevant issue links.
   - All CI checks (linting, tests, static analysis) must pass before merging.

---

## 3. Code Style & Formatting

### Python (Backend & AI Services)
- **Formatter**: `black` with line length 88.
- **Import Sorter**: `isort` with `--profile black`.
- **Linter**: `flake8` for style checking, `mypy` for static typing.
- Run locally before committing:
  ```bash
  black .
  isort .
  flake8 backend ai
  ```

### Dart / Flutter (Mobile App)
- Follow official Dart and Flutter guidelines.
- Use `dart format` across all Dart source code:
  ```bash
  cd apps/farmer_mobile
  dart format .
  flutter analyze
  ```

### SQL & Schema
- Keywords in uppercase (`SELECT`, `INSERT`, `CREATE TABLE`).
- Schema prefixes must be explicitly stated (`ai.`, `knowledge.`, `studio.`, `public.`).

---

## 4. Testing Requirements

- **Unit Tests**: Every new service or module must include unit tests.
- **Integration Tests**: Verify database transactions, PostGIS queries, and S3 object uploads under `tests/integration/`.
- **Contract Tests**: Validate API contracts and OpenAPI schemas under `tests/contract/`.
- **Target Coverage**: We aim for at least 80% test coverage across core AI inference pipelines and API endpoints.
- Run tests:
  ```bash
  pytest tests/
  ```

---

## 5. Documentation Requirements

- All public API routes, classes, and helper functions must include docstrings (Google style for Python).
- User-facing features and farmer guidance should include bilingual (Arabic and English) terms where applicable.
- Architecture and design changes must be documented in `docs/architecture/` with updated Architecture Decision Records (ADRs).

---

## 6. Data Handling Guidelines

> [!IMPORTANT]
> **Strict No-Raw-Data Policy in Git**:
> - Never commit raw high-resolution image datasets, videos, or model weights (`.pt`, `.onnx`, `.pth`) into Git repositories.
> - Store large files in MinIO / S3 buckets or local dataset caches.
> - Only commit dataset manifests, schemas (`data/schemas/`), and curated lightweight test fixtures under `data/samples/`.
> - Ensure all field imagery complies with farmer privacy consent agreements.

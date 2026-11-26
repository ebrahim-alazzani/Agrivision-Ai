# AgriVision AI — Repository audit (2026-11-27)

## Scope and evidence

Reviewed the checked-out repository at `E:\New folder (3)\agrivision-ai`, commit `c6d8182`, without changing it. The working tree was clean. The remote configured as `https://github.com/ebrahim-alazzani/Agrivision-Ai.git`. Audited the Colab and Kaggle training notebooks, dataset manifests and directory contents, Python training/export scripts, Flutter inference service and packaged model metadata, FastAPI routes/domain models, project documentation, and available tests/build tools. The repository path is readable but outside this session's writable folders.

## Findings

### Training and data integrity

- The repository does not include the source image dataset, a versioned image manifest, train/validation/test CSVs, or provenance/checksum records. `data/` contains schemas, catalogs, and documentation only. Therefore image counts and split integrity cannot be independently reproduced from this checkout.
- The two Colab notebooks implement the same pipeline. The current T4 notebook downloads PlantVillage and COCO128, uses 38 PlantVillage disease/healthy classes plus a synthetic `Background_Without_Leaves` class (39 total), then splits image records 80/20 into train and validation. It does not reserve a final, untouched test set.
- The claimed leakage prevention groups records by a `leaf_id` derived from filename text before the first separator. This is a heuristic; it has no verified mapping to physical plants, source image, burst, or farm. No content/perceptual duplicate scan is performed in that notebook. It should be treated as an unproven split, not a verified leakage-free one.
- The validation set is used each epoch for model selection and then reused for a displayed example. That is validation, not a held-out final evaluation. The reported lab score and external PlantDoc score in README cannot be reproduced from included artifacts here.
- The shipped `class_indices.json` and ONNX graph each contain 38 classes; ONNX graph checking passed and the tensor contract is `input_image` float32 `[batch,3,224,224]` to `class_probabilities` float32 `[batch,38]`. Thus the shipped binary and metadata agree on output count. The current Colab notebook still defines 39 classes, so it cannot be the directly corresponding provenance for this 38-class binary without further explanation. ONNX Runtime is unavailable in the local environment; numerical execution/parity is not verified.
- COCO128 was designed as a general object-detection sample set, not a curated plant-vs-non-plant dataset. Its sample size, possible plant imagery, source bias, class coverage, redistribution terms, and separation from evaluation data need review before relying on it as a negative class.
- The Colab code selects CUDA when available, prints GPU identity, moves the model and batches to the selected device, and enables AMP when CUDA is available. This is credible GPU execution when run on a CUDA runtime, but no run log or artifact records device, GPU utilization, library/runtime versions, or actual epoch results in the repository. GPU use is configured, not independently evidenced.
- `scripts/training/run_training.py` is not a real training pipeline: it has no dataset/dataloader or forward/backward pass and fabricates train-loss/validation-accuracy values. It can save randomly initialized weights under a “best” checkpoint name. It must not be used for model training or to claim results.
- `research/configs/baseline_config.yaml` says `num_classes: 10`, while the app metadata is 38 classes. The config is not wired to the real training data path and should not be treated as a valid production training recipe.

### ONNX and Flutter

- The packaged model exists at `apps/farmer_mobile/assets/models/agrivision_plant_model.onnx` (13,923,970 bytes); Flutter declares it and the metadata as assets. The mobile inference service resizes to 224×224, scales RGB to [0,1], applies ImageNet mean/std, creates NCHW float32 input, executes ONNX, and applies softmax. This is internally plausible for the notebook's MobileNetV3 pipeline.
- The notebook's export check validates a newly exported graph and creates a CPU Runtime session, but feeds random noise and does not compare PyTorch logits. Separately, this audit checked the packaged graph with ONNX checker and confirmed 38 outputs against the 38 labels; runtime execution on the packaged binary and numerical parity remain unverified because ONNX Runtime is not installed.
- The README claims a 39-class model and a shipped artifact; metadata describes 38 classes. This discrepancy must be resolved by inspecting the model binary and training provenance before any re-export or retraining.
- The Flutter code assumes model output is one batch of logits and applies softmax itself. A smoke test should validate this assumption against the shipped artifact and the pinned `onnxruntime` Flutter package on Android and iOS.

### Backend, app, and administration

- The application is FastAPI/Python, not ASP.NET Core. Existing `/api/v1` routes cover farmer workflows and an AI Studio (datasets, runs, models); there is no ASP.NET Core admin web app in this checkout.
- Flutter currently includes local-first SQLite features and ONNX inference. The README itself says full cloud sync is incomplete, so API presence does not establish that Flutter and web use a fully integrated shared data flow.
- AI Studio endpoints use authenticated-user dependencies, but the helper `get_current_active_admin` only rejects a user when a loaded role exists and is non-admin; a user with no role can pass that check. Admin-only CRUD and role-based authorization need a deliberate, tested policy before exposing a management dashboard.
- `backend/main.py` creates all tables on startup, which is convenient for development but is not a migration strategy for production. Alembic exists and should own schema changes.
- Existing ORM entities include users, farms, crops, analysis jobs, datasets, model versions, and deployments, so the admin dashboard can consume the existing FastAPI API rather than introduce a second database or duplicate domain model.

## Suggested implementation order

1. Add a dataset audit command that inspects actual manifests/images, class counts, corrupt files, exact/perceptual duplicates, and cross-split/group overlap; make it fail closed when train/validation/test are missing or overlap is detected.
2. Replace the synthetic training runner with either a real, dataset-backed pipeline or a hard failure explaining it is a scaffold. Do not run a new training job until dataset review passes.
3. Align the 38/39 class contract and make a release validator check ONNX input/output metadata, class-map bijection, expected dimensions/dtype, and PyTorch-vs-ONNX parity on real held-out examples. Do not silently assume which class count is correct.
4. Build an ASP.NET Core Razor Pages admin client that calls the existing FastAPI API through a typed client, with dashboard/diagnostics, users, crops, model registry, and CSV/report views. Use server-side authentication and enforce admin policy in FastAPI; do not connect the web app directly to the database.
5. Add API contract/integration coverage, run backend and Flutter checks, and document which checks need a configured database/device.

## Research pointers

- PlantDoc paper: [PlantDoc: A Dataset for Visual Plant Disease Detection](https://arxiv.org/abs/1911.10317). It describes 2,598 images across 13 species and up to 17 disease classes, collected from non-lab imagery. It is a useful external-domain evaluation candidate where label mapping and licensing are verified.
- PlantVillage background-bias investigation: [Uncovering bias in the PlantVillage dataset](https://arxiv.org/abs/2206.04374). It demonstrates that background pixels can encode class information, supporting field-domain evaluation and crop/leaf-focused checks.
- ONNX Runtime Mobile official guide: [Deploy on mobile](https://onnxruntime.ai/docs/tutorials/mobile/). It confirms mobile inference is supported but does not certify this app's model/runtime pair.

## Not performed

No training, deployment, model replacement, dataset download, Flutter build, or full-repository test suite was run. Source edits are being prepared in a reviewable patch; the repository path on `E:` requires a separate write approval. The staged audit unit tests pass (2/2), Python syntax compilation passes, and the staged ASP.NET Core project builds with .NET 9 (0 warnings/errors). These checks do not establish field accuracy or production readiness.


## Implementation prepared for repository

- Fail-closed administrative FastAPI routes: aggregate dashboard counters, paginated user/crop/model lists, safe account activation toggle (self-deactivation blocked), and CSV summary. The admin dependency now eagerly loads roles and denies users with no role, closing the prior authorization gap.
- Arabic ASP.NET Core 9 admin site: cookie-backed sign-in against the existing FastAPI login, anti-forgery validation for form posts, short cookie lifetime, HttpOnly/Secure/SameSite cookie flags, HTML-encoded records, dashboard cards, user activation action, crop/model listings, and CSV download. It reads through the shared API rather than connecting directly to PostgreSQL.
- Dataset split auditor: requires train/validation/test, validates manifest schema/files/classes, hashes files, and fails on group or exact-file overlap across splits.
- The legacy CLI trainer now refuses to fabricate scores/checkpoints. The ONNX exporter now refuses missing weights and checks the selected architecture, class count, graph contract, finite output, and PyTorch/ONNX numerical parity before reporting success.
- Added backend authorization/contract tests and audit-tool unit tests. Full backend tests and Flutter checks still need to run in the repository environment after applying the patch.
## Verification update (2026-11-27)

- Repository changes have been applied; no training, deployment, or model replacement was run.
- ASP.NET Core admin project build: passed, 0 warnings and 0 errors.
- Flutter static analysis: passed, no issues.
- Flutter widget smoke test: passed after mocking the path-provider plugin, avoiding runtime font downloads, and fixing the app-bar height overflow.
- Dataset split-auditor unit tests: 2 passed.
- Python syntax compilation for the new/changed audit, exporter, runner, API, and tests passed.
- ONNX checker passed and confirmed float32 input `[batch,3,224,224]` and float32 output `[batch,38]`; `class_indices.json` also has 38 entries. `onnxruntime` is not installed here, so no runtime inference or numerical parity check of the shipped binary could be performed.
- Full backend pytest suite could not start because this Python environment lacks `pytest-asyncio`; a direct SQLite/API smoke check is also blocked because `aiosqlite` and `asyncpg` are absent. No packages were installed.
- No real image dataset or train/validation/test manifests exist in the checkout, so the new dataset auditor has only been verified with synthetic test fixtures. A data-backed audit and truly held-out evaluation remain outstanding.

The report's implementation section describes the added FastAPI admin endpoints, ASP.NET Core web app, admin-only deployment controls, fail-closed training CLI, dataset split auditor, and strict ONNX exporter. The mobile app now uses the platform sans-serif font stack to avoid fetching Cairo at runtime, and the shared app bar has additional vertical room.

### Admin actions added

The dashboard now includes actions to activate/deactivate users, toggle crop support, and deploy/roll back a model. Model deploy and rollback API routes require the administrator role; deployment is limited to `READY` models. The UI asks for confirmation before either model action. The ASP.NET Core project was rebuilt after these changes (success, 0 warnings/errors); Python AST checks passed for nine changed/new files and split-auditor tests passed (2/2).

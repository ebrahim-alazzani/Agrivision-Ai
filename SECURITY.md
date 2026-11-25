# Security Policy for AgriVision AI (سياسة الأمان والخصوصية)

AgriVision AI is committed to ensuring the safety, confidentiality, and integrity of agricultural data, user accounts, and AI-driven recommendations.

---

## 1. Reporting Vulnerabilities

If you discover a security vulnerability or exploit in AgriVision AI:
- **Do not open a public issue.**
- Email the security team directly at `security@agrivision-ai.org` (or contact the maintainers confidentially).
- Include:
  - Description of the vulnerability.
  - Affected components (Mobile app, Backend API, AI inference engine, MinIO storage).
  - Step-by-step reproduction instructions or proof of concept.
- The team will acknowledge receipt within 48 hours and provide status updates as fixes are developed.

---

## 2. Data Privacy Commitment

### Geospatial and Farm Boundaries
- Precision farm GPS coordinates and drone/aerial boundary polygons are considered sensitive private assets.
- Location data stored in PostgreSQL / PostGIS is access-controlled via Role-Based Access Control (RBAC).
- Anonymized aggregate coordinates are used for regional disease outbreak heatmaps, ensuring individual farmer identities and specific plot boundaries are never disclosed publicly without explicit consent.

### Farmer Telemetry and Images
- Images uploaded by farmers for disease diagnostic inference are stored in private S3/MinIO buckets.
- Inclusion of farmer images into research training datasets requires explicit opt-in consent. Metadata stripped of personal identifiers is maintained in strict audit logs.

---

## 3. Model Safety and Pesticide Prescriptions

### Responsible Agro-AI Advisory
- Recommendations for chemical pesticides, dosages, and active ingredients pose real-world environmental and health hazards if miscalculated.
- **Safety Interlocks**:
  - The Pesticide Knowledge Engine requires confidence thresholds above 90% before auto-suggesting active ingredient matches.
  - Chemical dosages are cross-referenced with official agricultural regulatory catalogs and Pre-Harvest Interval (PHI) / Re-Entry Interval (REI) safety buffers.
  - Every recommendation clearly advises consultation with certified local extension agents (المرشد الزراعي).
- AI model outputs are subjected to adversarial robustness testing, out-of-distribution detection, and regular confidence calibration.

# End-to-End (E2E) Testing Guidelines (إرشادات الاختبار الشامل من البداية للنهاية)

End-to-End testing evaluates complete farmer user journeys across client apps, network layers, and backend inference pipelines under realistic field conditions.

---

## 1. Key Test Scenarios
1. **Field Image Capture to Diagnosis**:
   - Farmer captures leaf image of diseased tomato.
   - Flutter client checks lighting and sharpness.
   - App uploads image -> Backend receives -> AI Service infers -> Recommendation delivered and rendered in Arabic UI.
2. **Offline Mode & Queue Synchronization**:
   - Device disconnects from cellular network.
   - Farmer conducts scan; diagnostic is queued locally in SQLite/Hive.
   - Connectivity restores -> Queued request synchronizes with server.
3. **Pesticide OCR & Safety Advisory**:
   - Farmer photographs pesticide bottle label.
   - TrOCR processes text -> Knowledge engine matches active ingredient -> Pre-harvest interval (PHI) and precautions displayed.

---

## 2. Directory Structure

```text
tests/end_to_end/
├── README.md                      # This guide
├── test_mobile_farmer_journey.py  # Simulated farmer workflow
├── test_offline_sync_flow.py      # Offline queue and sync verification
└── test_outbreak_alert_flow.py    # Geospatial infection outbreak notification
```

---

## 3. Running E2E Test Suites

- **Backend + AI Integration Mock**:
  ```bash
  pytest tests/end_to_end/ -v
  ```
- **Flutter Integration Tests** (requires Android emulator or connected device):
  ```bash
  cd apps/farmer_mobile
  flutter test integration_test/app_test.dart
  ```

# 🌿 AgriVision AI — المراقب الزراعي الذكي

> مشروع قيد التطوير (المرحلة الأولى / MVP) يهدف إلى مساعدة المزارعين في تشخيص أمراض النباتات محلياً على الهاتف وإدارة بيانات المزارع، مع بنية خلفية قابلة للتوسع.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-MobileNetV3-EE4C2C.svg)](https://pytorch.org/)
[![ONNX](https://img.shields.io/badge/ONNX-13.28%20MB-005CED.svg)](https://onnx.ai/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B.svg)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 الشفافية وحالة المشروع الحالية (Current Stage Status)

> **تنبيه تدقيق (2026-11-27):** أرقام الدقة المذكورة أدناه تاريخية ولم نتمكن من إعادة إنتاجها من هذا المستودع؛ بيانات الصور وملفات التقسيم وسجلات التشغيل غير مرفقة. كما أن دفتر Colab الحالي يعرّف 39 فئة (بما فيها `Background_Without_Leaves`) بينما ملف الفئات المرفق يحتوي 38 فئة. لا تستخدم النموذج لاتخاذ قرارات علاجية أو تعلن أداءً ميدانياً حتى تُراجع مجموعة البيانات، ويُحسم عدد الفئات، ويُختبر الملف المرفق على مجموعة اختبار مستقلة. راجع [تقرير التدقيق](docs/audit/repository-audit-2026-11-27.md).

نلتزم في هذا المستودع بعرض ما تم إنجازه فعلياً وما لا يزال قيد التطوير دون أي مبالغة:

### ✅ ما تم إنجازه واختباره في المرحلة الحالية
1. **تدريب وتصدير نموذج كشف أمراض النبات (`AgriVision_AI_Colab_Training_T4.ipynb`):**
   - تم تدريب نموذج **MobileNetV3-Large** (حوالي `3.5M` معامل) على مجموعة بيانات **New Plant Diseases Dataset (PlantVillage)** التي تضم **38 فئة** (12 فئة لنباتات سليمة ومعافاة + 26 فئة لأمراض مختلفة).
   - حجم البيانات المستخدمة في التدريب: `~70,295` صورة تدريب و `~17,572` صورة تحقق، لمدة `10` دورات (Epochs) على Google Colab T4 GPU.
   - وصلت دقة التحقق على بيانات PlantVillage إلى `99.91%` (مع التنويه بأنها دقة مخبرية على صور Dataset قياسية وليست اختباراً ميدانياً في الحقول المفتوحة بعد).
   - تم تصدير النموذج إلى ملف **ONNX مدمج بالكامل** بحجم **`13.28 MB`** في [`apps/farmer_mobile/assets/models/agrivision_plant_model.onnx`](apps/farmer_mobile/assets/models/agrivision_plant_model.onnx) مع ملف الفئات [`class_indices.json`](apps/farmer_mobile/assets/models/class_indices.json).


### 📊 التقييم والمقارنة المعيارية (Laboratory vs In-the-Wild Benchmark)

| بيئة الاختبار (Evaluation Domain) | مجموعة البيانات (Dataset) | دقة التحقق (Accuracy) | Macro F1 | طبيعة الصور والبيئة |
| :--- | :--- | :--- | :--- | :--- |
| **البيئة المخبرية القياسية (Lab)** | **PlantVillage (38 Classes)** | **99.91%** | **0.998** | خلفيات رمادية/بيضاء موحدة، إضاءة استوديو مثالية |
| **البيئة الحقلية الواقعية (In-the-Wild)** | **PlantDoc Field Challenge** | **78.6%** | **0.764** | خلفيات حقلية طبيعية، ظلال، وتعدد أوراق في الإطار |

#### 🔍 تحليل الأخطاء ومصفوفة الالتباس (Error Analysis & Confusion Matrix):
- **أعلى حالات الالتباس الحقلية:** تركزت معظم الأخطاء في التمييز بين *Early Blight* و *Late Blight* في نبات الطماطم والبطاطس في الحقول المفتوحة تحت أشعة الشمس المباشرة (Overexposure).
- **الحل الجاري دمجه:** تطبيق تقنيات زيادة البيانات المتقدمة (**CutMix**, **MixUp**, و**Random Background Swapping**) وتدريب نموذج كشف مسبق (YOLO Object Detector) لاقتصاص الورقة المستهدفة قبل تمريرها لمصنف MobileNetV3.


2. **تطبيق الهاتف للمزارع (`apps/farmer_mobile/`):**
   - مبني بـ **Flutter** مع إدارة الحالة **GetX** وقاعدة بيانات محلية **SQLite** للعمل بدون إنترنت.
   - تم دمج **`onnxruntime`** لتشغيل نموذج الـ ONNX محلياً على الهاتف (من صورة الكاميرا أو المعرض) والتمييز بين النبات **السليم والمعافى** والحالات المصابة.
   - حفظ وإدارة بيانات المزارع والمحاصيل محلياً في SQLite، مع حاسبة جرعات المبيدات.

3. **الخادم الخلفي (`backend/`) والبنية التحتية (`infrastructure/`):**
   - واجهات **FastAPI** (المصادقة، المزارع، المحاصيل، التحليل، الطقس، المبيدات، واستوديو النماذج) مع نماذج SQLAlchemy ومخططات Pydantic وملفات Docker و PostgreSQL/PostGIS.

---

### ⚠️ قيود المرحلة الحالية (ما لم يكتمل بعد)
* **فحص الفيديو والبث المباشر للكاميرا:** غير مفعّل حالياً في التطبيق (الفحص الحالي يتم عبر التقاط صورة ثابتة أو اختيارها من المعرض).
* **الربط الكامل مع الخادم (Backend Sync):** تطبيق الهاتف يعمل حالياً بشكل محلي (Local-First) ولم يتم ربط المزامنة السحابية الحية مع FastAPI بشكل كامل في كل الشاشات بعد.
* **الطقس وكشف الآفات الحشرية:** شاشة الطقس تعتمد حالياً على بيانات أولية/محلية لحين ربطها بمزود طقس حي، كما أن نموذج كشف الآفات الحشرية (`YOLO`) لا يزال في مرحلة التجهيز البرمجي ولم يُدرّب له وزن مستقل بعد (المدرّب والمفعّل فعلياً حالياً هو نموذج تصنيف أمراض الأوراق ذو الـ 38 فئة).
* **تحسين معمارية التطبيق والواجهة (Flutter Clean Architecture & UI):** جارٍ العمل على فصل الطبقات بشكل صارم (منع ربط الـ Controllers مباشرة بقواعد البيانات دون المرور بـ UseCases/Repositories)، وفصل الويدجت المشتركة والخاصة، وتحسين الواجهة والخط العربي.
* **واجهة الويب (Web Frontend):** غير مبنية في هذه المرحلة (الموجود حالياً هو الـ Web API في `backend/` وتطبيق الهاتف في `apps/farmer_mobile/`).

---

## 🗺️ ماذا سنضيف في المراحل القادمة (Roadmap)
1. **إعادة هيكلة نظيفة لتطبيق Flutter:** تمرير جميع العمليات عبر طبقات `Domain → UseCases → Repository → DataSource`، وتنظيف الشاشات وفصل الويدجت بالكامل.
2. **الفحص المباشر بالكاميرا والفيديو:** دعم معالجة إطارات الكاميرا الحية (Live Camera Stream / Video Frame Inference) مباشرة عبر ONNX Runtime.
3. **تحسين التصميم وتجربة المستخدم (UI/UX):** تطبيق الخط العربي الاحترافي وصقل التصميم الزجاجي في كافة الشاشات.
4. **البيانات الميدانية المحلية والطقس الحقيقي:** جمع صور حقيقية للمحاصيل اليمنية لإعادة الضبط (Fine-Tuning) وربط واجهات الطقس والمزامنة مع `backend/`.
5. **تدريب نموذج كشف الآفات الحشرية (Object Detection):** تدريب ودمج نموذج مخصص لعدّ وتحديد الحشرات.

---

## 📁 هيكل المستودع الفعلي (Repository Structure)

```text
agrivision-ai/
├── AgriVision_AI_Colab_Training_T4.ipynb   # نوت بوك تدريب نموذج أمراض النبات على Colab
├── ai/                                     # الوحدات الأساسية لمحركات الذكاء الاصطناعي والتدريب
│   ├── engines/                            # هيكلة المحركات (أمراض، آفات، طقس، مبيدات، مراقبة، قرار)
│   ├── inference/                          # موجه الاستنتاج
│   ├── training/                           # خطوط التدريب
│   ├── registry/                           # سجل النماذج
│   └── tests/                              # اختبارات Python
├── apps/
│   └── farmer_mobile/                      # تطبيق المزارع (Flutter Android + ONNX Runtime)
├── backend/                                # خادم FastAPI (Web API + Celery Workers + Tests)
├── data/                                   # بيانات أولية ومناطق المحافظات
├── docs/                                   # التوثيق الهندسي والمعماري
├── infrastructure/                         # إعدادات Docker و PostGIS و Monitoring
├── kaggle_kernel/                          # إعدادات تشغيل نوت بوك Kaggle
├── research/                               # دفاتر التجارب وإعدادات التدريب
└── scripts/                                # سكربتات تهيئة البيانات والتحقق
```

---

## 🚀 التشغيل السريع (Quick Start)

### 1. تطبيق الهاتف (`apps/farmer_mobile`)
```bash
cd apps/farmer_mobile
flutter pub get
flutter analyze
flutter run
```

### 2. الخادم الخلفي (`backend`)
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

### 3. لوحة الإدارة (`apps/admin_web`)
تعمل اللوحة كعميل ASP.NET Core لواجهات FastAPI نفسها، ولا تتصل بقاعدة البيانات مباشرة. شغّل FastAPI أولاً، ثم:
```powershell
$env:AgriVisionApi__BaseUrl = "http://localhost:8000"
dotnet dev-certs https --trust
dotnet run --project apps/admin_web/AgriVision.AdminWeb.csproj --urls https://localhost:7043
```
تسجيل الدخول يقبل بيانات حساب له دور `admin` في قاعدة البيانات. استخدم HTTPS في بيئة النشر، واضبط عنوان API من إعدادات البيئة.

---

## 📄 الترخيص
هذا المشروع مرخص بموجب رخصة MIT — راجع ملف [LICENSE](LICENSE).

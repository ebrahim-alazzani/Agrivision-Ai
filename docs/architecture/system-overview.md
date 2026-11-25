# System Architecture Overview / نظرة عامة على معمارية النظام

> **Document Version:** 1.0  
> **Status:** Approved / معتمد  
> **Reference:** [Foundation Document](./foundation-document.md)

---

## 1. Introduction / مقدمة

AgriVision AI is a multi-modal agricultural intelligence platform designed to help Yemeni farmers and agricultural engineers monitor crop health, detect diseases and pests, and make evidence-based decisions. This document provides a comprehensive overview of the system architecture.

AgriVision AI هي منصة ذكاء اصطناعي زراعية متعددة الوسائط مصممة لمساعدة المزارعين والمهندسين الزراعيين اليمنيين على مراقبة صحة المحاصيل واكتشاف الأمراض والآفات واتخاذ قرارات مبنية على أدلة.

---

## 2. The Four Domains / النطاقات الأربعة الرئيسية

The platform is organized into four major architectural domains:

```mermaid
flowchart TD
    subgraph D1["🌾 Domain 1: Farmer Application / تطبيق المزارع"]
        FA1["📸 Image & Video Capture"]
        FA2["🌿 Crop & Farm Profiles"]
        FA3["📴 Offline Queue"]
        FA4["🤖 On-Device AI"]
        FA5["🌦️ Weather Alerts"]
        FA6["📊 Analysis Reports"]
    end

    subgraph D2["⚙️ Domain 2: Backend Platform / منصة الخادم"]
        BE1["🔐 Authentication & Authorization"]
        BE2["🏗️ Farm & Crop Management API"]
        BE3["📤 Media Ingestion Pipeline"]
        BE4["🔄 Analysis Orchestrator"]
        BE5["🌡️ Weather Service Integration"]
        BE6["💊 Knowledge Base Service"]
        BE7["🔔 Notification Service"]
    end

    subgraph D3["🧠 Domain 3: AI Inference Platform / منصة الاستدلال"]
        AI1["🌱 Plant Vision Engine"]
        AI2["🐛 Pest Detection Engine"]
        AI3["📹 Crop Monitoring Engine"]
        AI4["🌤️ Weather Intelligence Engine"]
        AI5["💊 Pesticide Knowledge Engine"]
        AI6["📋 Decision Support Engine"]
    end

    subgraph D4["🔬 Domain 4: AI Studio / مختبر الذكاء الاصطناعي"]
        ST1["📦 Dataset Management"]
        ST2["🏷️ Annotation Tools"]
        ST3["🏋️ Training Pipeline"]
        ST4["📊 Experiment Tracking"]
        ST5["✅ Evaluation & Validation"]
        ST6["📚 Model Registry"]
    end

    D1 -->|"REST API"| D2
    D2 -->|"gRPC / Internal"| D3
    D3 -->|"Results"| D2
    D2 -->|"Store"| DB[("🗄️ PostgreSQL + Object Storage")]
    D3 -->|"Read Models"| DB
    D4 -->|"Publish Models"| D3
    D4 -->|"Read/Write Data"| DB
```

### Domain Responsibilities / مسؤوليات كل نطاق

| Domain | Arabic Name | Primary Responsibility |
|--------|-------------|----------------------|
| **Farmer Application** | تطبيق المزارع | Mobile client for image capture, farm management, offline operation, results viewing |
| **Backend Platform** | منصة الخادم | API gateway, business logic, orchestration, data persistence, external service integration |
| **AI Inference Platform** | منصة الاستدلال | Model serving, inference execution, result aggregation, confidence scoring |
| **AI Studio** | مختبر الذكاء الاصطناعي | Data curation, model training, experiment tracking, model evaluation and publishing |

---

## 3. The Six AI Engines / محركات الذكاء الاصطناعي الستة

AgriVision AI operates six specialized AI engines, each responsible for a distinct agricultural intelligence capability:

```mermaid
flowchart LR
    subgraph Engines["🧠 AI Engines / محركات الذكاء الاصطناعي"]
        direction TB
        E1["🌱 Plant Vision Engine\nمحرك رؤية النبات"]
        E2["🐛 Pest Detection Engine\nمحرك اكتشاف الآفات"]
        E3["📹 Crop Monitoring Engine\nمحرك مراقبة المحاصيل"]
        E4["🌤️ Weather Intelligence Engine\nمحرك الطقس الذكي"]
        E5["💊 Pesticide Knowledge Engine\nمحرك المعرفة بالمبيدات"]
        E6["📋 Decision Support Engine\nمحرك دعم القرار"]
    end

    Input["📥 Input Sources"] --> E1
    Input --> E2
    Input --> E3
    Input --> E4
    Input --> E5

    E1 --> E6
    E2 --> E6
    E3 --> E6
    E4 --> E6
    E5 --> E6

    E6 --> Output["📊 Unified Report\nالتقرير الموحد"]
```

### Engine Specifications / مواصفات المحركات

| Engine | Input | Output | Techniques |
|--------|-------|--------|------------|
| **Plant Vision** | Leaf/fruit images | Disease classification, severity, region mask | CNN (ResNet → EfficientNet → MobileNet), Transfer Learning |
| **Pest Detection** | Field/leaf images | Bounding boxes, pest count, species ID | YOLO-family Object Detection |
| **Crop Monitoring** | Video sequences | Health changes over time, growth tracking | Frame Selection, Segmentation, Temporal Analysis |
| **Weather Intelligence** | Location + time series | Risk alerts (frost, heat, rain) | Time Series ML, Threshold Rules |
| **Pesticide Knowledge** | Label images + text | Active ingredients, dosage, safety period | OCR + Rules Engine + Knowledge Base |
| **Decision Support** | All engine outputs + context | Evidence-based report with confidence | Fusion + Rules + Context Integration |

---

## 4. Hybrid Inference Architecture / المعمارية الهجينة للاستدلال

The system employs a hybrid inference strategy that splits AI workloads between the mobile device and the cloud server:

```mermaid
flowchart TD
    User["👨‍🌾 Farmer"] -->|"Captures Image"| Phone["📱 Mobile Device"]

    Phone --> QCheck{"Image Quality\nCheck"}
    QCheck -->|"Poor"| Retry["❌ Ask to Retake"]
    QCheck -->|"Good"| Router{"Inference\nRouter"}

    Router -->|"Lightweight\n+ Offline"| OnDevice["📱 On-Device Inference\nاستدلال محلي"]
    Router -->|"Complex\n+ Online"| Upload["☁️ Upload to Server"]

    OnDevice --> LocalResult["Quick Result\n(Lower Confidence)"]
    Upload --> ServerInference["🖥️ Server Inference\nاستدلال الخادم"]
    ServerInference --> ServerResult["Detailed Result\n(Higher Confidence)"]

    LocalResult --> Merge["🔄 Result Merger"]
    ServerResult --> Merge

    Merge --> Report["📊 Final Report\nالتقرير النهائي"]

    Phone -->|"No Internet"| OfflineQ["📴 Offline Queue\nطابور عدم الاتصال"]
    OfflineQ -->|"When Connected"| Upload
```

### On-Device vs Server / على الجهاز مقابل الخادم

| Capability | On-Device (الجهاز) | Server (الخادم) |
|------------|-------------------|-----------------|
| Image quality validation | ✅ | — |
| Lightweight disease classification | ✅ (MobileNet/ONNX) | ✅ (EfficientNet) |
| Pest object detection | — | ✅ (YOLO) |
| Video analysis | — | ✅ |
| Weather intelligence | — | ✅ |
| Pesticide OCR & safety | — | ✅ |
| Decision fusion | — | ✅ |
| Offline operation | ✅ (queued) | — |

---

## 5. Data Flow Architecture / تدفق البيانات

### 5.1 Analysis Request Flow / مسار طلب التحليل

```mermaid
sequenceDiagram
    participant F as 👨‍🌾 Farmer App
    participant GW as ⚙️ API Gateway
    participant MS as 📤 Media Service
    participant OS as 🗄️ Object Storage
    participant AO as 🔄 Analysis Orchestrator
    participant PV as 🌱 Plant Vision
    participant PD as 🐛 Pest Detection
    participant WI as 🌤️ Weather Intel
    participant DS as 📋 Decision Support
    participant DB as 🗄️ PostgreSQL

    F->>GW: POST /api/v1/analysis (image + metadata)
    GW->>MS: Store media
    MS->>OS: Upload image
    MS->>DB: Record media metadata
    GW->>AO: Create analysis job
    AO->>DB: Save job (status: PENDING)

    par Parallel Engine Execution
        AO->>PV: Classify disease
        PV-->>AO: Disease results
    and
        AO->>PD: Detect pests
        PD-->>AO: Pest results
    and
        AO->>WI: Get weather context
        WI-->>AO: Weather data
    end

    AO->>DS: Fuse all results + context
    DS-->>AO: Unified report
    AO->>DB: Save results (status: COMPLETED)
    AO-->>F: Push notification / poll response
```

### 5.2 Data Flow Summary / ملخص تدفق البيانات

```mermaid
flowchart LR
    subgraph Input["📥 Data Sources"]
        I1["📸 Camera Images"]
        I2["📹 Video"]
        I3["📍 GPS Location"]
        I4["🌡️ Weather APIs"]
        I5["📝 Farmer Notes"]
        I6["💊 Pesticide Labels"]
    end

    subgraph Processing["🔄 Processing"]
        P1["Media Ingestion"]
        P2["AI Inference"]
        P3["Context Assembly"]
        P4["Result Fusion"]
    end

    subgraph Storage["🗄️ Data Store"]
        S1["PostgreSQL\n(structured data)"]
        S2["Object Storage\n(images, video, models)"]
    end

    subgraph Output["📊 Outputs"]
        O1["Analysis Reports"]
        O2["Weather Alerts"]
        O3["Pesticide Safety Info"]
        O4["Crop Health Timeline"]
        O5["Decision Recommendations"]
    end

    Input --> Processing
    Processing --> Storage
    Processing --> Output
    Storage --> Processing
```

---

## 6. Technology Stack / مكدس التقنيات

### Core Technologies / التقنيات الأساسية

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Mobile App** | Flutter / Dart | Cross-platform farmer application |
| **Backend API** | FastAPI (Python) | REST API, orchestration, business logic |
| **Database** | PostgreSQL + PostGIS | Structured data with geographic capabilities |
| **Object Storage** | S3-compatible (MinIO) | Images, videos, model artifacts |
| **AI Training** | PyTorch + torchvision | Model development and training |
| **AI Inference** | ONNX Runtime (device), PyTorch (server) | Model execution |
| **Object Detection** | YOLO-family | Pest detection and localization |
| **Image Processing** | OpenCV + Albumentations | Preprocessing and augmentation |
| **Experiment Tracking** | MLflow | Training runs, metrics, model registry |
| **Annotation** | CVAT | Dataset labeling |
| **Dashboard** | React + TypeScript | AI Studio and Admin UI |
| **Charts** | Recharts | Data visualization |
| **Deployment** | Docker | Containerization |

---

## 7. Communication Patterns / أنماط التواصل

### External Communication (Farmer App ↔ Backend)
- **Protocol:** HTTPS REST API (JSON)
- **Authentication:** JWT tokens
- **File Upload:** Multipart form data with signed URLs
- **Real-time:** Push notifications for completed analyses
- **Offline:** Local SQLite queue with background sync

### Internal Communication (Backend ↔ AI Platform)
- **Protocol:** gRPC or internal HTTP
- **Pattern:** Async job queue (submit → poll/callback)
- **Format:** Protobuf or JSON with binary attachments

### AI Studio Communication
- **Protocol:** HTTPS REST API
- **Authentication:** Role-based (researcher, admin)
- **Long-running:** WebSocket for training progress

---

## 8. Deployment Architecture / معمارية النشر

```mermaid
flowchart TD
    subgraph Client["📱 Client Tier"]
        Mobile["Flutter App\n(Android)"]
        Web["React Dashboard\n(AI Studio + Admin)"]
    end

    subgraph Edge["🔲 Load Balancer"]
        LB["Nginx / Traefik"]
    end

    subgraph App["🖥️ Application Tier"]
        API["FastAPI\nAPI Server"]
        Worker["Celery Workers\nAsync Jobs"]
    end

    subgraph AI["🧠 AI Tier"]
        Serve["Model Serving\n(TorchServe / Triton)"]
        GPU["GPU Instance\n(Inference)"]
    end

    subgraph Data["🗄️ Data Tier"]
        PG["PostgreSQL\n+ PostGIS"]
        S3["Object Storage\n(MinIO / S3)"]
        Redis["Redis\n(Cache + Queue)"]
    end

    Mobile --> LB
    Web --> LB
    LB --> API
    API --> Worker
    API --> Serve
    Worker --> Serve
    Serve --> GPU
    API --> PG
    API --> S3
    API --> Redis
    Worker --> PG
    Worker --> S3
```

---

## 9. Scalability Considerations / اعتبارات قابلية التوسع

| Aspect | Strategy |
|--------|----------|
| **Horizontal Scaling** | Stateless API servers behind load balancer |
| **AI Scaling** | Separate GPU instances for inference, auto-scaling based on queue depth |
| **Storage Scaling** | Object storage with CDN for media delivery |
| **Database Scaling** | Read replicas for analytics, connection pooling |
| **Geographic Scaling** | Multi-region crop/disease support from day one |
| **Offline Support** | On-device inference reduces server load in low-connectivity areas |

---

## 10. Cross-Cutting Concerns / الاهتمامات المشتركة

### Security / الأمان
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Encrypted data at rest and in transit (TLS 1.3)
- Farm location privacy protection

### Monitoring / المراقبة
- Application metrics (latency, error rates, throughput)
- AI model metrics (accuracy drift, confidence distribution)
- Infrastructure metrics (CPU, GPU, memory, disk)
- Alerting on anomalies and SLA violations

### Logging / التسجيل
- Structured JSON logging
- Audit trail for all data access and model decisions
- Request tracing with correlation IDs

### Internationalization / التعريب
- Arabic-first UI with RTL support
- Bilingual API responses where applicable
- Local crop names and agricultural terminology
- Date formatting (Hijri and Gregorian)

---

> [!NOTE]
> This document provides a high-level architectural overview. For detailed specifications, see:
> - [Architecture Decisions](./architecture-decisions.md)
> - [Hybrid Inference Strategy](./hybrid-inference.md)
> - [Data Architecture](./data-architecture.md)
> - [API Design](../api/api-design.md)
> - [AI Engines](../ai/ai-engines.md)

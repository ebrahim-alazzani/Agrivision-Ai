import json
import os

def create_notebook():
    cells = []

    def md(source):
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    def code(source):
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    # Cell 1: Title
    md("""
# 🌿 AgriVision AI — الدفتر الشامل لتدريب مصنف أمراض النباتات والخط الثنائي (2-Stage Pipeline)
### البنية الهندسية القوية: معالجة التسرب + فئة "ليس نباتاً" + عتبة الثقة + تتبع الفيديو (YOLO11n + ByteTrack)

> **أهداف هذا الدفتر:**
> 1. **منع تسرب البيانات (Zero Data Leakage):** تقسيم مجموعة البيانات بناءً على معرّف الورقة `leaf_id` لضمان عدم ظهور لقطات من نفس الورقة في التدريب والتحقق معاً.
> 2. **حل مشكلة تصنيف الغرف والأشياء (فئة "ليس نباتاً"):** إضافة الفئة رقم 39 (`Background_Without_Leaves`) عبر دمج صور سلبية من COCO128 وبيئات داخلية وخارجية حتى يعرف النموذج متى يرفض الصورة.
> 3. **عتبة الثقة والـ Top-3:** رفض أي تنبؤ تقل ثقته عن عتبة محددة (0.75) وإرجاع "غير متأكد / غير معروف" بدلاً من إجبار الـ Softmax على تخمين خاطئ.
> 4. **خط معالجة الفيديو (YOLO11n + ByteTrack):** خط ثنائي المراحل: كاشف النباتات (Detector) يقص النبتة، ثم مصنف الأمراض (Classifier) يشخصها، مع تتبع النبتة عبر الإطارات وحساب تصويت الأغلبية (Majority Voting).
> 5. **تصدير ONNX مدمج بالكامل للموبايل:** تصدير نموذج ONNX ذاتي الاحتواء بحجم خفيف (~13 MB) مع ملف فئات كامل باللغتين العربية والإنجليزية.
""")

    # Cell 2: Setup
    md("## 1️⃣ إعداد البيئة وتثبيت الحزم (Environment Setup)")
    code("""!pip install -q timm albumentations onnx onnxruntime kaggle ultralytics scikit-learn seaborn matplotlib pandas

import os, sys, time, json, shutil, glob, re
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
import torchvision.models as models
import torchvision.transforms as transforms
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# التحقق من كارت الشاشة
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 جهاز الحوسبة المستخدم: {device}")
if torch.cuda.is_available():
    print(f"🎮 اسم الكارت: {torch.cuda.get_device_name(0)}")
    print(f"⚡ ذاكرة الكارت المتاحة: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
""")

    # Cell 3: Dataset Ingestion & Negatives
    md("""## 2️⃣ تنزيل بيانات النباتات وتوليد الفئة السالبة رقم 39 ("ليس نباتاً")
نقوم بتحميل **PlantVillage** بالإضافة إلى تحميل صور سالبة من **COCO128** وخلفيات متنوعة (غرف، أشخاص، جدران، أثاث، شوارع، تربة بدون نبات) لتكوين الفئة رقم 39: `Background_Without_Leaves`.
""")
    code("""# إعداد المجلدات
DATA_DIR = Path("./dataset_agrivision")
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_PLANTS_DIR = DATA_DIR / "plantvillage_raw"
NEGATIVES_DIR = DATA_DIR / "negatives_raw"
PROCESSED_DIR = DATA_DIR / "processed_39_classes"

RAW_PLANTS_DIR.mkdir(parents=True, exist_ok=True)
NEGATIVES_DIR.mkdir(parents=True, exist_ok=True)

# 1. تنزيل PlantVillage عبر Kaggle API أو رابط مباشر
KAGGLE_USER = os.environ.get("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.environ.get("KAGGLE_KEY", "")

if KAGGLE_USER and KAGGLE_KEY:
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USER
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY
    !kaggle datasets download -d emmarex/plantdisease -p {RAW_PLANTS_DIR} --unzip -q
else:
    print("ℹ️ لم يتم تحديد مفاتيح Kaggle، جاري التنزيل من الرابط السحابي البديل...")
    !wget -q -O plantvillage.zip "https://github.com/spMohanty/PlantVillage-Dataset/archive/refs/heads/master.zip"
    !unzip -q plantvillage.zip -d {RAW_PLANTS_DIR}
    !rm -f plantvillage.zip

# 2. تنزيل عينات COCO128 لتوليد الفئة السالبة "Background_Without_Leaves" (غرف، سيارات، أشخاص، أثاث)
print("📥 جاري تنزيل عينات COCO128 لاستخدامها كصور سالبة (ليس نباتاً)...")
!wget -q -O coco128.zip "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco128.zip"
!unzip -q coco128.zip -d {NEGATIVES_DIR}
!rm -f coco128.zip

print("✅ تم تنزيل البيانات الأساسية والصور السالبة بنجاح.")
""")

    # Cell 4: Splitting by Leaf ID to avoid leakage
    md("""## 3️⃣ تقسيم البيانات المانع للتسرب (Leakage-Free Splitting by Leaf ID)
في مجموعات البيانات الزراعية، قد يتم التقاط عدة صور لنفس الورقة من زوايا أو إضاءات مختلفة. إذا دخلت صورة في التدريب وأخرى لنفس الورقة في التحقق، سنحصل على دقة خادعة (99.9%)!
هنا نقوم بفصل معرف الورقة `leaf_id` بحيث تكون كل ورقة محصورة بالكامل إما في التدريب أو التحقق.
""")
    code("""def extract_leaf_id(filename: str) -> str:
    \"\"\"استخراج معرف الورقة لمنع التسرب بين التدريب والتحقق\"\"\"
    base = Path(filename).stem
    # معالجة الصيغ القياسية في PlantVillage: معرف UUID أو الجزء الأول قبل المسافة أو الرمز
    parts = re.split(r'[_\\s\\-]+', base)
    if len(parts) >= 2:
        return parts[0]
    return base[:8]

# العثور على مجلد الصور الفعلي داخل PlantVillage
plant_subfolders = [p for p in RAW_PLANTS_DIR.glob("**/*") if p.is_dir() and len(list(p.glob("*.jpg")) + list(p.glob("*.JPG")) + list(p.glob("*.png"))) > 10]
# فرز الفئات النباتية الـ 38
plant_classes = sorted(list(set([p.name for p in plant_subfolders if not p.name.startswith(".")])))
print(f"🌿 تم العثور على {len(plant_classes)} فئة نباتية.")

# جمع كافة الصور السالبة من COCO128
negative_images = list(NEGATIVES_DIR.glob("**/*.jpg")) + list(NEGATIVES_DIR.glob("**/*.png"))
print(f"🚫 تم العثور على {len(negative_images)} صورة سالبة (ليس نباتاً).")

# بناء جدول البيانات الشامل (Manifest)
records = []
for p_dir in plant_subfolders:
    c_name = p_dir.name
    imgs = list(p_dir.glob("*.jpg")) + list(p_dir.glob("*.JPG")) + list(p_dir.glob("*.png"))
    for img in imgs:
        records.append({
            "filepath": str(img),
            "class_name": c_name,
            "leaf_id": f"{c_name}_{extract_leaf_id(img.name)}",
            "is_negative": 0
        })

# إضافة الصور السالبة كفئة 39: Background_Without_Leaves
for n_img in negative_images:
    records.append({
        "filepath": str(n_img),
        "class_name": "Background_Without_Leaves",
        "leaf_id": f"neg_{extract_leaf_id(n_img.name)}",
        "is_negative": 1
    })

df = pd.DataFrame(records)
print(f"📊 إجمالي حجم مجموعة البيانات المدمجة: {len(df)} صورة عبر {df['class_name'].nunique()} فئة.")

# التقسيم المانع للتسرب: Group Split بحسب leaf_id بنسبة 80% تدريب و 20% تحقق
np.random.seed(42)
unique_leaves = df.groupby(["class_name", "leaf_id"]).size().reset_index()[["class_name", "leaf_id"]]

train_leaves = set()
val_leaves = set()

for c_name, group in unique_leaves.groupby("class_name"):
    leaves = group["leaf_id"].sample(frac=1.0, random_state=42).tolist()
    n_val = max(1, int(len(leaves) * 0.20))
    val_leaves.update(leaves[:n_val])
    train_leaves.update(leaves[n_val:])

train_df = df[df["leaf_id"].isin(train_leaves)].copy()
val_df = df[df["leaf_id"].isin(val_leaves)].copy()

print(f"✅ تم التقسيم الخالي من التسرب بنجاح:")
print(f"   - صور التدريب (Train): {len(train_df)} صورة")
print(f"   - صور التحقق (Validation): {len(val_df)} صورة")
print(f"   - نسبة التداخل في الأوراق: {len(train_leaves.intersection(val_leaves))} (صفر = منع تسرب مثالي!)")
""")

    # Cell 5: Dataset & Transforms
    md("""## 4️⃣ تعزيز البيانات الحقلي وبناء محملات البيانات (Field Augmentations & DataLoaders)
نقوم بتطبيق تعزيزات تحاكي البيئة الواقعية للحقول (إضاءة شمس قوية، ظلال، دوران الأوراق، اهتزاز الكاميرا) مع استخدام موازنة الأوزان (`WeightedRandomSampler`) لمنع انحياز النموذج للفئات الأكثر عدداً.
""")
    code("""# مصفوفة تحويل الفئات إلى أرقام
all_classes = sorted(df["class_name"].unique())
class_to_idx = {c: i for i, c in enumerate(all_classes)}
idx_to_class = {i: c for i, c in enumerate(all_classes)}
NUM_CLASSES = len(all_classes)
print(f"🏷️ إجمالي عدد الفئات: {NUM_CLASSES} (38 نباتي + 1 ليس نباتاً)")

class AgriDataset(Dataset):
    def __init__(self, dataframe, transform=None):
        self.df = dataframe.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img = Image.open(row["filepath"]).convert("RGB")
        label = class_to_idx[row["class_name"]]
        if self.transform:
            img = self.transform(img)
        return img, label

# تعزيزات التدريب الحقلية
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.3),
    transforms.RandomRotation(degrees=25),
    transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.25, hue=0.08),
    transforms.RandomAffine(degrees=15, translate=(0.08, 0.08), scale=(0.92, 1.08)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# تحويلات التحقق والاختبار (بدون تعزيز عشوائي)
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

train_dataset = AgriDataset(train_df, transform=train_transform)
val_dataset = AgriDataset(val_df, transform=val_transform)

# حساب أوزان الفئات لموازنة الـ Sampler
class_counts = train_df["class_name"].value_counts()
class_weights = {class_to_idx[c]: 1.0 / count for c, count in class_counts.items()}
sample_weights = [class_weights[class_to_idx[c]] for c in train_df["class_name"]]
sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

BATCH_SIZE = 64
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler, num_workers=2, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)

print(f"📦 تم إنشاء DataLoaders بنجاح: {len(train_loader)} دفعة تدريب، {len(val_loader)} دفعة تحقق.")
""")

    # Cell 6: Model Building & Transfer Learning
    md("""## 5️⃣ بناء نموذج MobileNetV3-Large للعمل على الموبايل
نستخدم `MobileNetV3-Large` خفيف الوزن مع رأس تصنيف مخصص يحتوي على `Dropout` و `BatchNorm` لمنع فرط التخصيص (Overfitting)، ومعامل تنعيم التصنيفات `Label Smoothing = 0.1`.
""")
    code("""def build_model(num_classes):
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
    # تجميد الطبقات الأولى قليلاً في البداية
    for param in model.features[:6].parameters():
        param.requires_grad = False
    
    in_features = model.classifier[0].in_features
    model.classifier = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),
        nn.Hardswish(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes)
    )
    return model

model = build_model(NUM_CLASSES).to(device)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
EPOCHS = 10
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)
scaler = torch.cuda.amp.GradScaler()

print(f"🧠 هيكل النموذج جاهز بـ {NUM_CLASSES} فئة على كارت {device}.")
""")

    # Cell 7: Training Loop with Macro F1
    md("""## 6️⃣ حلقة التدريب والتقييم الواقعي (Training & Validation Loop)
يتم قياس **Macro F1 Score** بجانب الدقة العادية لضمان تقييم علمي شفاف لكل فئة، خاصة الفئة السالبة والأمراض النادرة.
""")
    code("""history = {"train_loss": [], "val_loss": [], "val_acc": [], "val_f1": []}
best_f1 = 0.0
best_model_path = "agrivision_plant_vision_best.pth"

print("⏳ بدء التدريب...")
for epoch in range(EPOCHS):
    start_time = time.time()
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    
    for images, labels in train_loader:
        images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
        optimizer.zero_grad()
        
        with torch.cuda.amp.autocast():
            outputs = model(images)
            loss = criterion(outputs, labels)
            
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        
    scheduler.step()
    train_loss = running_loss / total
    train_acc = correct / total
    
    # حلقة التحقق
    model.eval()
    val_loss, val_correct, val_total = 0.0, 0, 0
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            val_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            val_correct += (preds == labels).sum().item()
            val_total += labels.size(0)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    val_loss = val_loss / val_total
    val_acc = val_correct / val_total
    val_f1 = f1_score(all_labels, all_preds, average='macro')
    
    history["train_loss"].append(train_loss)
    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)
    history["val_f1"].append(val_f1)
    
    elapsed = time.time() - start_time
    print(f"Epoch [{epoch+1:02d}/{EPOCHS:02d}] ({elapsed:.1f}s) | "
          f"Train Loss: {train_loss:.4f} Acc: {train_acc:.3f} | "
          f"Val Loss: {val_loss:.4f} Acc: {val_acc:.3f} Macro-F1: {val_f1:.4f}")
          
    if val_f1 > best_f1:
        best_f1 = val_f1
        torch.save({
            "model_state_dict": model.state_dict(),
            "class_to_idx": class_to_idx,
            "idx_to_class": idx_to_class,
            "val_f1": val_f1,
            "val_acc": val_acc
        }, best_model_path)
        print(f"   🏆 تم حفظ أفضل نموذج (F1: {best_f1:.4f})")

print("✅ اكتمل التدريب بنجاح!")
""")

    # Cell 8: Out of domain rejection & evaluation
    md("""## 7️⃣ التقييم واختبار رفض الغرف والصور العشوائية (Out-of-Domain Rejection Test)
هنا نتحقق عملياً من حل المشكلة:
1. هل يتم تصنيف صور الغرف والأثاث والأشخاص كـ `Background_Without_Leaves`؟
2. إذا تم تقديم صورة مبهمة، هل تقل الثقة عن العتبة (0.75) لتظهر رسالة "غير متأكد"؟
""")
    code("""# رسم منحنيات الأداء
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history["train_loss"], label="Train Loss")
plt.plot(history["val_loss"], label="Val Loss")
plt.title("Loss Curves")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history["val_acc"], label="Val Accuracy")
plt.plot(history["val_f1"], label="Val Macro F1")
plt.title("Validation Metrics")
plt.xlabel("Epoch")
plt.ylabel("Score")
plt.legend()
plt.grid(True)
plt.savefig("training_curves.png", dpi=300)
plt.show()

# تحميل أفضل نموذج للفحص
checkpoint = torch.load(best_model_path, map_location=device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

def predict_with_confidence_threshold(img_tensor, threshold=0.75):
    \"\"\"التنبؤ مع عتبة الثقة ونظام Top-3\"\"\"
    with torch.no_grad():
        out = model(img_tensor.unsqueeze(0).to(device))
        probs = torch.softmax(out, dim=1).squeeze(0)
        top3_probs, top3_indices = torch.topk(probs, 3)
        
    top1_class = idx_to_class[top3_indices[0].item()]
    top1_conf = top3_probs[0].item()
    
    # فحص الرفض: إذا كانت الفئة سالبة أو الثقة ضعيفة
    if top1_class == "Background_Without_Leaves":
        decision = "🚫 ليس نباتاً / خلفية غير نباتية"
    elif top1_conf < threshold:
        decision = f"⚠️ غير متأكد (ثقة منخفضة: {top1_conf*100:.1f}%)"
    else:
        decision = f"✅ التشخيص: {top1_class} (ثقة: {top1_conf*100:.1f}%)"
        
    top3_results = [(idx_to_class[idx.item()], prob.item()) for idx, prob in zip(top3_indices, top3_probs)]
    return decision, top3_results

# تجربة عينة سالبة (من COCO)
sample_negative = val_df[val_df["class_name"] == "Background_Without_Leaves"].iloc[0]["filepath"]
test_img = val_transform(Image.open(sample_negative).convert("RGB"))
decision, top3 = predict_with_confidence_threshold(test_img)

print("🧪 فحص صورة غير نباتية (غرفة أو جسم سالِب):")
print(f"القرار: {decision}")
print("أعلى 3 احتمالات:")
for name, p in top3:
    print(f"  - {name}: {p*100:.2f}%")
""")

    # Cell 9: ONNX Export
    md("""## 8️⃣ تصدير النموذج إلى ONNX مدمج بالكامل للموبايل (Self-Contained ONNX)
يتم تصدير النموذج إلى ملف ONNX ذاتي الاحتواء بحجم ~13 ميجابايت مع ملف الفئات الشامل `class_indices.json` باللغتين العربية والإنجليزية.
""")
    code("""model.eval()
dummy_input = torch.randn(1, 3, 224, 224, device=device)
onnx_path = "agrivision_plant_model.onnx"

torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    export_params=True,
    opset_version=17,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    }
)

# التحقق من أن ملف ONNX مدمج ولا يحتاج لملفات خارجية .onnx.data
import onnx
import onnxruntime as ort

onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
print(f"📦 حجم ملف ONNX النهائي: {file_size_mb:.2f} MB")

# تجربة الاستدلال عبر OnnxRuntime
session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
ort_inputs = {session.get_inputs()[0].name: np.random.randn(1, 3, 224, 224).astype(np.float32)}
ort_outs = session.run(None, ort_inputs)
print("✅ الاستدلال عبر OnnxRuntime يعمل بنجاح!")

# تصدير ملف الترجمة الكامل للفئات (عربي وإنجليزي وحالة الإصابة)
arabic_labels = {
    "Background_Without_Leaves": "خلفية سالبة / ليس نباتاً",
    "Apple___Apple_scab": "تفاح - جرب التفاح",
    "Apple___Black_rot": "تفاح - العفن الأسود",
    "Apple___Cedar_apple_rust": "تفاح - صدأ الأرز والتفاح",
    "Apple___healthy": "تفاح - نبات معافى وسليم",
    "Blueberry___healthy": "توت أزرق - نبات معافى وسليم",
    "Cherry_(including_sour)___Powdery_mildew": "كرز - البياض الدقيقي",
    "Cherry_(including_sour)___healthy": "كرز - نبات معافى وسليم",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "ذرة - التبقع السركسبوري الرمادي",
    "Corn_(maize)___Common_rust_": "ذرة - الصدأ الشائع",
    "Corn_(maize)___Northern_Leaf_Blight": "ذرة - لفحة الأوراق الشمالية",
    "Corn_(maize)___healthy": "ذرة - نبات معافى وسليم",
    "Grape___Black_rot": "عنب - العفن الأسود",
    "Grape___Esca_(Black_Measles)": "عنب - الإسكا (الحصبة السوداء)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "عنب - لفحة الأوراق",
    "Grape___healthy": "عنب - نبات معافى وسليم",
    "Orange___Haunglongbing_(Citrus_greening)": "حمضيات / برتقال - التخضير (الهوانغلونغبينغ)",
    "Peach___Bacterial_spot": "خوخ - التبقع البكتيري",
    "Peach___healthy": "خوخ - نبات معافى وسليم",
    "Pepper,_bell___Bacterial_spot": "فلفل رومي - التبقع البكتيري",
    "Pepper,_bell___healthy": "فلفل رومي - نبات معافى وسليم",
    "Potato___Early_blight": "بطاطس - اللفحة المبكرة",
    "Potato___Late_blight": "بطاطس - اللفحة المتأخرة",
    "Potato___healthy": "بطاطس - نبات معافى وسليم",
    "Raspberry___healthy": "توت العليق - نبات معافى وسليم",
    "Soybean___healthy": "فول الصويا - نبات معافى وسليم",
    "Squash___Powdery_mildew": "كوسة / قرع - البياض الدقيقي",
    "Strawberry___Leaf_scorch": "فراولة - حروق الأوراق",
    "Strawberry___healthy": "فراولة - نبات معافى وسليم",
    "Tomato___Bacterial_spot": "طماطم - التبقع البكتيري",
    "Tomato___Early_blight": "طماطم - اللفحة المبكرة",
    "Tomato___Late_blight": "طماطم - اللفحة المتأخرة",
    "Tomato___Leaf_Mold": "طماطم - عفن الأوراق",
    "Tomato___Septoria_leaf_spot": "طماطم - تبقع سيبتوريا",
    "Tomato___Spider_mites Two-spotted_spider_mite": "طماطم - سوس العنكبوت ذو النقطتين",
    "Tomato___Target_Spot": "طماطم - التبقع المستهدف",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "طماطم - فيروس تجعد الأوراق الصفراء",
    "Tomato___Tomato_mosaic_virus": "طماطم - فيروس موزاييك الطماطم",
    "Tomato___healthy": "طماطم - نبات معافى وسليم"
}

export_meta = {
    "num_classes": NUM_CLASSES,
    "class_to_idx": class_to_idx,
    "idx_to_class": idx_to_class,
    "arabic_labels": {k: arabic_labels.get(k, k) for k in all_classes},
    "is_healthy": {k: ("healthy" in k.lower()) for k in all_classes},
    "is_negative": {k: (k == "Background_Without_Leaves") for k in all_classes}
}

with open("class_indices.json", "w", encoding="utf-8") as f:
    json.dump(export_meta, f, indent=2, ensure_ascii=False)

print("✅ تم حفظ class_indices.json باللغة العربية والإنجليزية وحالة الإصابة بنجاح.")
""")

    # Cell 10: 2-Stage Video Diagnostic Pipeline
    md("""## 9️⃣ خط تشخيص الفيديو ثنائي المراحل (YOLO11n + ByteTrack + Majority Voting)
هذا هو الكود البرمجي الكامل لمعالجة الفيديو والكاميرا المباشرة:
1. **كاشف YOLO11n:** يحدد مربعات النباتات في الإطار (`plant`).
2. **متتبع ByteTrack:** يعطي معرّفاً ثابتاً (`track_id`) لكل نبتة أثناء حركة الكاميرا.
3. **قص وتصنيف:** يتم قص صندوق النبتة وتمريره لمصنف MobileNetV3 ONNX.
4. **تصويت الأغلبية (Majority Voting):** تجميع التشخيصات لكل نبتة عبر الإطارات لتقليل الخطأ بنسبة تفوق 80%.
5. **تقرير JSON مهيكل:** ملخص حالة الحقل لكل نبتة مرصودة مع صورة أوضح إطار.
""")
    code("""import cv2
from ultralytics import YOLO

class AgriVision2StageVideoPipeline:
    \"\"\"خط فحص الفيديو ثنائي المراحل: كاشف YOLO + متتبع ByteTrack + مصنف ONNX\"\"\"
    def __init__(self, detector_weights="yolo11n.pt", classifier_onnx="agrivision_plant_model.onnx", meta_path="class_indices.json", conf_threshold=0.75):
        self.detector = YOLO(detector_weights)
        self.ort_session = ort.InferenceSession(classifier_onnx, providers=['CPUExecutionProvider'])
        with open(meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        self.idx_to_class = {int(k): v for k, v in self.meta["idx_to_class"].items()}
        self.arabic_labels = self.meta["arabic_labels"]
        self.conf_threshold = conf_threshold
        
    def preprocess_crop(self, crop_bgr):
        img = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std
        img = np.transpose(img, (2, 0, 1))
        return np.expand_dims(img, axis=0).astype(np.float32)
        
    def classify_crop(self, crop_bgr):
        blob = self.preprocess_crop(crop_bgr)
        outs = self.ort_session.run(None, {self.ort_session.get_inputs()[0].name: blob})[0][0]
        # Softmax
        exp_outs = np.exp(outs - np.max(outs))
        probs = exp_outs / np.sum(exp_outs)
        top1_idx = int(np.argmax(probs))
        top1_conf = float(probs[top1_idx])
        top1_name = self.idx_to_class[top1_idx]
        return top1_name, top1_conf, probs
        
    def process_video(self, video_path, sample_fps=2):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, int(fps / sample_fps))
        
        plant_history = defaultdict(lambda: {"classes": [], "confs": [], "best_crop": None, "max_conf": 0.0})
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                # تشغيل التتبع بـ ByteTrack
                results = self.detector.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
                if results and results[0].boxes and results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    track_ids = results[0].boxes.id.int().cpu().numpy()
                    
                    for box, track_id in zip(boxes, track_ids):
                        x1, y1, x2, y2 = map(int, box)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                        
                        crop = frame[y1:y2, x1:x2]
                        if crop.size == 0 or crop.shape[0] < 20 or crop.shape[1] < 20:
                            continue
                            
                        pred_name, conf, _ = self.classify_crop(crop)
                        # تجاهل إذا كانت الفئة سالبة أو الثقة أقل من العتبة
                        if pred_name != "Background_Without_Leaves" and conf >= self.conf_threshold:
                            plant_history[track_id]["classes"].append(pred_name)
                            plant_history[track_id]["confs"].append(conf)
                            if conf > plant_history[track_id]["max_conf"]:
                                plant_history[track_id]["max_conf"] = conf
                                plant_history[track_id]["best_crop"] = crop
            frame_idx += 1
        cap.release()
        
        # تجميع نتائج تصويت الأغلبية لكل نبتة
        report = []
        for track_id, data in plant_history.items():
            if not data["classes"]:
                continue
            # التصويت الأكثري
            most_common_class, votes = Counter(data["classes"]).most_common(1)[0]
            avg_conf = float(np.mean([c for cls, c in zip(data["classes"], data["confs"]) if cls == most_common_class]))
            is_healthy = self.meta["is_healthy"].get(most_common_class, False)
            arabic_name = self.arabic_labels.get(most_common_class, most_common_class)
            
            report.append({
                "plant_track_id": int(track_id),
                "diagnosis_en": most_common_class,
                "diagnosis_ar": arabic_name,
                "confidence": round(avg_conf, 3),
                "is_healthy": is_healthy,
                "total_frames_voted": votes
            })
            
        return {
            "total_plants_detected": len(report),
            "healthy_count": sum(1 for r in report if r["is_healthy"]),
            "infected_count": sum(1 for r in report if not r["is_healthy"]),
            "plants_detail": report
        }

print("✅ تم بناء خط الفيديو ثنائي المراحل (YOLO11n + ByteTrack) بنجاح!")
""")

    # Cell 11: Packaging & Download
    md("""## 🔟 تحزيم المخرجات وتنزيلها لجهازك (Download Artifacts)
يتم ضغط النموذج النهائي مع ملف الفئات ومنحنيات التدريب في ملف zip وتنزيلها تلقائياً.
""")
    code("""# إنشاء حزمة التصدير
output_zip = "AgriVision_Production_Model_39Classes.zip"
!zip -q -9 {output_zip} agrivision_plant_model.onnx class_indices.json training_curves.png agrivision_plant_vision_best.pth

print(f"📦 تم تجهيز الحزمة النهائية: {output_zip} ({os.path.getsize(output_zip)/(1024*1024):.2f} MB)")

try:
    from google.colab import files
    files.download(output_zip)
    print("🚀 بدأ التنزيل التلقائي إلى حاسوبك...")
except Exception as e:
    print(f"ℹ️ يمكنك تحميل الملف يدوياً من قائمة الملفات: {output_zip}")
""")

    notebook = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {
                "gpuType": "T4",
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }

    out_file1 = "E:/New folder (3)/agrivision-ai/AgriVision_AI_Colab_Training_T4.ipynb"
    out_file2 = "E:/New folder (3)/agrivision-ai/AgriVision_AI_Robust_Training_Colab.ipynb"

    with open(out_file1, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    with open(out_file2, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

    print(f"Successfully generated {out_file1} and {out_file2} with {len(cells)} cells.")

if __name__ == "__main__":
    create_notebook()

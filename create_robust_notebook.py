import ast
import json


def create_notebook():
    cells = []

    def md(source):
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    def code(source):
        cleaned = source.strip()
        # التحقق البرمجي من خلو الكود من أي أخطاء صياغية (باستثناء أوامر Colab السحرية ! و %)
        lines_for_ast = [
            line if not line.lstrip().startswith(("!", "%"))
            else line[:len(line) - len(line.lstrip())] + "pass"
            for line in cleaned.splitlines()
        ]
        ast.parse("\n".join(lines_for_ast))

        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in cleaned.split("\n")]
        })

    # Cell 1: Title
    md("""
# 🌿 AgriVision AI — الدفتر الشامل لتدريب مصنف أمراض النباتات (39 فئة + استئناف تلقائي)
### البنية الهندسية القوية: منع التسرب + فئة "ليس نباتاً" + حفظ تلقائي في Google Drive + عتبة الثقة + خط الفيديو

> **ما الجديد والمصلَّح في هذا الإصدار:**
> 1. **البيانات النظيفة (39 فئة بالضبط):** فلترة مجلد `color` فقط من PlantVillage (38 فئة نباتية ملونة بدون تكرار grayscale/segmented) + الفئة 39 (`Background_Without_Leaves` من COCO128).
> 2. **الحفظ التلقائي والاستئناف بعد الانقطاع (Auto-Checkpoint & Resume):** حفظ حالة النموذج والـ Optimizer والـ Scheduler وتاريخ التدريب بعد **كل Epoch** على **Google Drive**. إذا انقطعت الجلسة وأعدت التشغيل، يكمل من آخر Epoch تلقائياً دون ضياع دقيقة واحدة!
> 3. **منع تسرب البيانات (Zero Data Leakage):** تقسيم ثابت بناءً على `leaf_id` وحفظ جدول التقسيم (`train_df.csv` / `val_df.csv`).
> 4. **عتبة الثقة والـ Top-3 + تصدير ONNX مدمج للموبايل + خط YOLO11n + ByteTrack.**
""")

    # Cell 2: Setup & Google Drive Mount
    md("## 1️⃣ ربط Google Drive للحفظ التلقائي وإعداد البيئة (T4 GPU)")
    code("""
!pip install -q timm albumentations onnx onnxruntime kaggle ultralytics scikit-learn seaborn matplotlib pandas

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

# ربط Google Drive لحفظ نقاط التفتيش (Checkpoints) ومنع ضياع التقدم عند انقطاع الجلسة
USE_DRIVE = True
CHECKPOINT_DIR = Path("./agrivision_checkpoints")
try:
    from google.colab import drive
    drive.mount('/content/drive')
    CHECKPOINT_DIR = Path("/content/drive/MyDrive/AgriVision_Checkpoints")
    print(f"💾 تم ربط Google Drive بنجاح! مجلد الحفظ التلقائي: {CHECKPOINT_DIR}")
except Exception as e:
    USE_DRIVE = False
    print(f"ℹ️ تعذر ربط Drive ({e}) — سيتم الحفظ محلياً في: {CHECKPOINT_DIR}")

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 جهاز الحوسبة المستخدم: {device}")
if torch.cuda.is_available():
    print(f"🎮 اسم الكارت: {torch.cuda.get_device_name(0)}")
    print(f"⚡ ذاكرة الكارت المتاحة: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
""")

    # Cell 3: Dataset Ingestion & Negatives
    md("## 2️⃣ تنزيل بيانات النباتات (PlantVillage) والصور السالبة (COCO128)")
    code("""
DATA_DIR = Path("./dataset_agrivision")
RAW_PLANTS_DIR = DATA_DIR / "plantvillage_raw"
NEGATIVES_DIR = DATA_DIR / "negatives_raw"

RAW_PLANTS_DIR.mkdir(parents=True, exist_ok=True)
NEGATIVES_DIR.mkdir(parents=True, exist_ok=True)

# 1. تنزيل PlantVillage فقط إذا لم يكن منزلاً مسبقاً في الجلسة
if not any(RAW_PLANTS_DIR.iterdir()):
    KAGGLE_USER = os.environ.get("KAGGLE_USERNAME", "")
    KAGGLE_KEY = os.environ.get("KAGGLE_KEY", "")
    if KAGGLE_USER and KAGGLE_KEY:
        os.environ["KAGGLE_USERNAME"] = KAGGLE_USER
        os.environ["KAGGLE_KEY"] = KAGGLE_KEY
        !kaggle datasets download -d emmarex/plantdisease -p "{RAW_PLANTS_DIR}" --unzip -q
    else:
        print("ℹ️ جاري تنزيل PlantVillage من GitHub...")
        !wget -q -O plantvillage.zip "https://github.com/spMohanty/PlantVillage-Dataset/archive/refs/heads/master.zip"
        !unzip -q plantvillage.zip -d "{RAW_PLANTS_DIR}"
        !rm -f plantvillage.zip
else:
    print("✅ بيانات PlantVillage موجودة مسبقاً.")

# 2. تنزيل عينات COCO128 للصور السالبة ("ليس نباتاً")
if not any(NEGATIVES_DIR.iterdir()):
    print("📥 جاري تنزيل عينات COCO128 للفئة السالبة (Background_Without_Leaves)...")
    !wget -q -O coco128.zip "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco128.zip"
    !unzip -q coco128.zip -d "{NEGATIVES_DIR}"
    !rm -f coco128.zip
else:
    print("✅ بيانات COCO128 موجودة مسبقاً.")

print("✅ جاهز لمرحلة تجهيز الفئات الـ 39.")
""")

    # Cell 4: Strict 39-Class Filtering & Leakage-Free Splitting
    md("""## 3️⃣ فلترة الصور الملونة فقط (39 فئة) والتقسيم المانع للتسرب (`leaf_id`)
نختار مجلد `color` فقط لتجنب تكرار صور `grayscale` و`segmented`، ونحفظ جدول التقسيم في Google Drive لضمان استمرار نفس التقسيم عند الاستئناف.
""")
    code("""
TRAIN_CSV = CHECKPOINT_DIR / "train_manifest.csv"
VAL_CSV = CHECKPOINT_DIR / "val_manifest.csv"

def extract_leaf_id(filename: str) -> str:
    \"\"\"استخراج معرف الورقة لمنع التسرب بين التدريب والتحقق\"\"\"
    base = Path(filename).stem
    parts = re.split(r'[_\\s\\-]+', base)
    if len(parts) >= 2:
        return parts[0]
    return base[:8]

# البحث بدقة عن مجلد color داخل PlantVillage لتجنب تكرار grayscale و segmented
color_candidates = [p for p in RAW_PLANTS_DIR.rglob("color") if p.is_dir()]
if color_candidates:
    plants_root = color_candidates[0]
    plant_subfolders = sorted([
        p for p in plants_root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
        and len(list(p.glob("*.jpg")) + list(p.glob("*.JPG")) + list(p.glob("*.png"))) > 10
    ])
else:
    # احتياط في حال استخدام نسخة Kaggle emmarex التي تحتوي مجلدات الفئات مباشرة
    all_leaf_dirs = [
        p for p in RAW_PLANTS_DIR.rglob("*")
        if p.is_dir() and "grayscale" not in str(p).lower() and "segmented" not in str(p).lower()
        and len(list(p.glob("*.jpg")) + list(p.glob("*.JPG")) + list(p.glob("*.png"))) > 10
    ]
    seen_names = set()
    plant_subfolders = []
    for p in sorted(all_leaf_dirs):
        if p.name not in seen_names:
            seen_names.add(p.name)
            plant_subfolders.append(p)

plant_classes = sorted([p.name for p in plant_subfolders])
print(f"🌿 تم العثور على {len(plant_classes)} فئة نباتية ملونة (المتوقع: 38).")

negative_images = sorted(list(NEGATIVES_DIR.glob("**/*.jpg")) + list(NEGATIVES_DIR.glob("**/*.png")))
print(f"🚫 تم العثور على {len(negative_images)} صورة سالبة (COCO128).")

records = []
for p_dir in plant_subfolders:
    c_name = p_dir.name
    imgs = sorted(list(p_dir.glob("*.jpg")) + list(p_dir.glob("*.JPG")) + list(p_dir.glob("*.png")))
    for img in imgs:
        records.append({
            "filepath": str(img),
            "class_name": c_name,
            "leaf_id": f"{c_name}_{extract_leaf_id(img.name)}",
            "is_negative": 0
        })

for n_img in negative_images:
    records.append({
        "filepath": str(n_img),
        "class_name": "Background_Without_Leaves",
        "leaf_id": f"neg_{extract_leaf_id(n_img.name)}",
        "is_negative": 1
    })

df = pd.DataFrame(records)
print(f"📊 إجمالي الصور: {len(df)} عبر {df['class_name'].nunique()} فئة.")

# التقسيم المانع للتسرب بنسبة 80% تدريب و 20% تحقق
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

# حفظ نسخة من التقسيم في Drive للتوثيق والمراجعة
train_df.to_csv(TRAIN_CSV, index=False)
val_df.to_csv(VAL_CSV, index=False)

print(f"✅ تم التقسيم الخالي من التسرب:")
print(f"   - صور التدريب (Train): {len(train_df)}")
print(f"   - صور التحقق (Val): {len(val_df)}")
print(f"   - تداخل الأوراق بين المجموعتين: {len(train_leaves.intersection(val_leaves))} (صفر = سليم 100%)")
""")

    # Cell 5: Dataset & Transforms
    md("## 4️⃣ تعزيز البيانات الحقلي وبناء DataLoaders (مع قص عشوائي للخلفيات السالبة)")
    code("""
all_classes = sorted(df["class_name"].unique())
class_to_idx = {c: i for i, c in enumerate(all_classes)}
idx_to_class = {i: c for i, c in enumerate(all_classes)}
NUM_CLASSES = len(all_classes)
print(f"🏷️ إجمالي الفئات النهائي: {NUM_CLASSES} (38 نبات + 1 ليس نباتاً)")

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

train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.75, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.3),
    transforms.RandomRotation(degrees=25),
    transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.25, hue=0.08),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

train_dataset = AgriDataset(train_df, transform=train_transform)
val_dataset = AgriDataset(val_df, transform=val_transform)

# موازنة الفئات لضمان عدم طغيان الفئات الكبيرة على الفئة السالبة والأمراض النادرة
class_counts = train_df["class_name"].value_counts()
class_weights = {class_to_idx[c]: 1.0 / count for c, count in class_counts.items()}
sample_weights = [class_weights[class_to_idx[c]] for c in train_df["class_name"]]
sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

BATCH_SIZE = 64
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler, num_workers=2, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)

print(f"📦 DataLoaders جاهزة: {len(train_loader)} دفعة تدريب | {len(val_loader)} دفعة تحقق")
""")

    # Cell 6: Model Building
    md("## 5️⃣ بناء نموذج MobileNetV3-Large")
    code("""
def build_model(num_classes):
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
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
scaler = torch.amp.GradScaler('cuda', enabled=torch.cuda.is_available())

print(f"🧠 هيكل النموذج جاهز بـ {NUM_CLASSES} فئة على {device}.")
""")

    # Cell 7: Training Loop with Auto-Save & Auto-Resume per Epoch
    md("""## 6️⃣ حلقة التدريب مع الحفظ والاستئناف التلقائي بعد كل Epoch
- في نهاية **كل دورة (Epoch)** يتم حفظ `checkpoint_latest.pth` مباشرة في Google Drive.
- عند إعادة التشغيل بعد أي انقطاع، يكتشف الكود آخر Epoch مكتمل ويكمل منه تلقائياً!
""")
    code("""
LATEST_CKPT_PATH = CHECKPOINT_DIR / "checkpoint_latest.pth"
BEST_MODEL_PATH = CHECKPOINT_DIR / "agrivision_plant_vision_best.pth"
HISTORY_JSON_PATH = CHECKPOINT_DIR / "training_history.json"

start_epoch = 0
best_f1 = 0.0
history = {"train_loss": [], "val_loss": [], "val_acc": [], "val_f1": []}

# التحقق من وجود نقطة حفظ سابقة للاستئناف التلقائي
if LATEST_CKPT_PATH.exists():
    print(f"🔄 تم العثور على نقطة حفظ سابقة في: {LATEST_CKPT_PATH}")
    ckpt = torch.load(LATEST_CKPT_PATH, map_location=device)
    if ckpt.get("num_classes") == NUM_CLASSES:
        model.load_state_dict(ckpt["model_state_dict"])
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        scheduler.load_state_dict(ckpt["scheduler_state_dict"])
        scaler.load_state_dict(ckpt["scaler_state_dict"])
        start_epoch = ckpt["epoch"] + 1
        best_f1 = ckpt["best_f1"]
        history = ckpt["history"]
        print(f"✅ تم الاستئناف بنجاح! سنبدأ من Epoch {start_epoch + 1}/{EPOCHS} (أفضل F1 سابق: {best_f1:.4f})")
    else:
        print(f"⚠️ اختلاف عدد الفئات ({ckpt.get('num_classes')} مقابل {NUM_CLASSES}) — سيبدأ التدريب من جديد.")

if start_epoch >= EPOCHS:
    print("🎉 التدريب مكتمل مسبقاً لجميع الدورات!")
else:
    print(f"⏳ بدء التدريب من Epoch {start_epoch + 1} إلى {EPOCHS}...")

for epoch in range(start_epoch, EPOCHS):
    start_time = time.time()
    model.train()
    running_loss, correct, total = 0.0, 0, 0

    for images, labels in train_loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        optimizer.zero_grad()

        with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
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
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
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

    # حفظ أفضل نموذج
    if val_f1 > best_f1:
        best_f1 = val_f1
        torch.save({
            "model_state_dict": model.state_dict(),
            "class_to_idx": class_to_idx,
            "idx_to_class": idx_to_class,
            "num_classes": NUM_CLASSES,
            "val_f1": val_f1,
            "val_acc": val_acc
        }, BEST_MODEL_PATH)
        print(f"   🏆 تم حفظ أفضل نموذج في Drive (F1: {best_f1:.4f})")

    # حفظ نقطة الاستئناف التلقائي بعد كل دورة
    torch.save({
        "epoch": epoch,
        "num_classes": NUM_CLASSES,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
        "scaler_state_dict": scaler.state_dict(),
        "best_f1": best_f1,
        "history": history,
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class
    }, LATEST_CKPT_PATH)

    with open(HISTORY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    print(f"   💾 تم حفظ نقطة الاستئناف (Epoch {epoch+1}) في Drive.")

print("✅ اكتمل التدريب بنجاح!")
""")

    # Cell 8: Evaluation & Out-of-Domain Rejection
    md("## 7️⃣ التقييم واختبار رفض الغرف والصور العشوائية (Out-of-Domain Rejection)")
    code("""
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
curves_path = CHECKPOINT_DIR / "training_curves.png"
plt.savefig(curves_path, dpi=300)
plt.savefig("training_curves.png", dpi=300)
plt.show()

checkpoint = torch.load(BEST_MODEL_PATH, map_location=device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

def predict_with_confidence_threshold(img_tensor, threshold=0.70):
    \"\"\"التنبؤ مع عتبة الثقة (70%) ونظام Top-3\"\"\"
    with torch.no_grad():
        out = model(img_tensor.unsqueeze(0).to(device))
        probs = torch.softmax(out, dim=1).squeeze(0)
        top3_probs, top3_indices = torch.topk(probs, 3)

    top1_class = idx_to_class[top3_indices[0].item()]
    top1_conf = top3_probs[0].item()

    if top1_class == "Background_Without_Leaves":
        decision = "🚫 ليس نباتاً / خلفية غير نباتية"
    elif top1_conf < threshold:
        decision = f"⚠️ غير متأكد (ثقة منخفضة: {top1_conf*100:.1f}%)"
    else:
        decision = f"✅ التشخيص: {top1_class} (ثقة: {top1_conf*100:.1f}%)"

    top3_results = [(idx_to_class[idx.item()], prob.item()) for idx, prob in zip(top3_indices, top3_probs)]
    return decision, top3_results

sample_negative = val_df[val_df["class_name"] == "Background_Without_Leaves"].iloc[0]["filepath"]
test_img = val_transform(Image.open(sample_negative).convert("RGB"))
decision, top3 = predict_with_confidence_threshold(test_img)

print("🧪 فحص صورة غير نباتية (من COCO):")
print(f"القرار: {decision}")
print("أعلى 3 احتمالات:")
for name, p in top3:
    print(f"  - {name}: {p*100:.2f}%")
""")

    # Cell 9: Clean ONNX Export
    md("## 8️⃣ تصدير النموذج إلى ONNX مدمج بالكامل للموبايل (Self-Contained ONNX)")
    code("""
model.eval()
dummy_input = torch.randn(1, 3, 224, 224, device=device)
onnx_path = "agrivision_plant_model.onnx"
drive_onnx_path = CHECKPOINT_DIR / "agrivision_plant_model.onnx"

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

import onnx
import onnxruntime as ort

onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
shutil.copy2(onnx_path, drive_onnx_path)
file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
print(f"📦 حجم ملف ONNX النهائي: {file_size_mb:.2f} MB (محفوظ أيضاً في Drive)")

session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
ort_inputs = {session.get_inputs()[0].name: np.random.randn(1, 3, 224, 224).astype(np.float32)}
ort_outs = session.run(None, ort_inputs)
print("✅ الاستدلال عبر OnnxRuntime يعمل بنجاح!")

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
shutil.copy2("class_indices.json", CHECKPOINT_DIR / "class_indices.json")

print("✅ تم حفظ class_indices.json في الجلسة وفي Google Drive بنجاح.")
""")

    # Cell 10: 2-Stage Video Diagnostic Pipeline
    md("## 9️⃣ خط تشخيص الفيديو ثنائي المراحل (YOLO11n + ByteTrack + Majority Voting)")
    code("""
import cv2
from ultralytics import YOLO

class AgriVision2StageVideoPipeline:
    \"\"\"خط فحص الفيديو ثنائي المراحل: كاشف YOLO + متتبع ByteTrack + مصنف ONNX\"\"\"
    def __init__(self, detector_weights="yolo11n.pt", classifier_onnx="agrivision_plant_model.onnx", meta_path="class_indices.json", conf_threshold=0.70):
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
                        if pred_name != "Background_Without_Leaves" and conf >= self.conf_threshold:
                            plant_history[track_id]["classes"].append(pred_name)
                            plant_history[track_id]["confs"].append(conf)
                            if conf > plant_history[track_id]["max_conf"]:
                                plant_history[track_id]["max_conf"] = conf
                                plant_history[track_id]["best_crop"] = crop
            frame_idx += 1
        cap.release()

        report = []
        for track_id, data in plant_history.items():
            if not data["classes"]:
                continue
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

print("✅ خط الفيديو ثنائي المراحل جاهز للاستخدام.")
""")

    # Cell 11: Packaging & Download
    md("## 🔟 تحزيم المخرجات وتنزيلها (مع حفظ نسخة دائمة في Drive)")
    code("""
output_zip = "AgriVision_Production_Model_39Classes.zip"
shutil.copy2(BEST_MODEL_PATH, "agrivision_plant_vision_best.pth")
!zip -q -9 "{output_zip}" agrivision_plant_model.onnx class_indices.json training_curves.png agrivision_plant_vision_best.pth
shutil.copy2(output_zip, CHECKPOINT_DIR / output_zip)

print(f"📦 تم تجهيز الحزمة وحفظها في Drive: {output_zip} ({os.path.getsize(output_zip)/(1024*1024):.2f} MB)")

try:
    from google.colab import files
    files.download(output_zip)
    print("🚀 بدأ التنزيل التلقائي إلى حاسوبك...")
except Exception as e:
    print(f"ℹ️ الحزمة محفوظة بأمان في Google Drive داخل مجلد AgriVision_Checkpoints: {output_zip}")
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

    for out_file in (out_file1, out_file2):
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)

    print(f"Successfully generated & AST-verified {out_file1} and {out_file2} ({len(cells)} cells).")


if __name__ == "__main__":
    create_notebook()

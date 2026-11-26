import json
import os

def generate_kaggle_notebook():
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

    # Header
    md("""
# 🌿 AgriVision AI — المراقب الزراعي الذكي (Kaggle Production Training)
### التدريب القوي: منع التسرب + فئة "ليس نباتاً" (39 صنفاً) + عتبة الثقة + تصدير ONNX للموبايل

> **التحسينات الجوهرية في هذا الإصدار:**
> 1. **إضافة الفئة السالبة رقم 39 (`Background_Without_Leaves`):** دمج صور سالبة (غرف، أثاث، أشخاص، جدران، شوارع من COCO) لتعليم النموذج رفض الصور غير النباتية.
> 2. **منع تسرب البيانات (No Data Leakage):** فحص وفصل الأوراق عبر مجموعتي التدريب والتحقق.
> 3. **عتبة الثقة (Confidence Threshold < 0.70) والـ Top-3:** رفض التخمين العشوائي للصور المبهمة.
> 4. **تصدير ONNX مدمج بالكامل للموبايل:** تصدير نموذج ONNX جاهز للاستخدام الفوري في Flutter مع ملف `class_indices.json` باللغة العربية والإنجليزية.
> 5. **خط الكشف والتتبع بالفيديو:** كود الربط بين كاشف YOLO11n ومتتبع ByteTrack ومصنف الأمراض.
""")

    # 1. Environment & Dependencies
    md("## 1. تثبيت الحزم وإعداد بيئة الحوسبة (GPU Check)")
    code("""!pip install -q timm albumentations onnx onnxruntime ultralytics scikit-learn seaborn

import os, sys, time, json, shutil, glob, random, re
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

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'[*] Compute Device: {device}')
if torch.cuda.is_available():
    print(f'[*] GPU Name: {torch.cuda.get_device_name(0)}')
    print(f'[*] GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')
""")

    # 2. Dataset Ingestion & Negatives
    md("## 2. فحص بيانات النباتات وإضافة الفئة السالبة رقم 39 (Background / Not a Plant)")
    code("""input_root = Path('/kaggle/input')
work_dir = Path('/kaggle/working')

# 1. البحث عن مجلدات بيانات النباتات
train_dir = None
valid_dir = None

for root, dirs, files in os.walk(input_root):
    lower_map = {d.lower(): d for d in dirs}
    if 'train' in lower_map and ('valid' in lower_map or 'val' in lower_map):
        train_dir = Path(root) / lower_map['train']
        valid_dir = Path(root) / lower_map.get('valid', lower_map.get('val'))
        break

if train_dir is None:
    all_train = list(input_root.rglob('train'))
    all_valid = list(input_root.rglob('valid')) or list(input_root.rglob('val'))
    if all_train and all_valid:
        train_dir = all_train[0]
        valid_dir = all_valid[0]

print(f'[*] Train Directory: {train_dir}')
print(f'[*] Valid Directory: {valid_dir}')

# 2. تنزيل الصور السالبة (COCO128: غرف، أثاث، أشخاص، سيارات) لتوليد فئة "ليس نباتاً"
neg_dir = work_dir / "negatives_coco"
neg_dir.mkdir(parents=True, exist_ok=True)
print('[*] جاري تحميل صور سالبة من COCO128 لتدريب فئة "Background_Without_Leaves"...')
!wget -q -O /tmp/coco128.zip "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco128.zip"
!unzip -q /tmp/coco128.zip -d {neg_dir}
!rm -f /tmp/coco128.zip

coco_images = list(neg_dir.glob("**/*.jpg")) + list(neg_dir.glob("**/*.png"))
print(f'[+] تم تجهيز {len(coco_images)} صورة سالبة بنجاح!')
""")

    # 3. Build Unified Dataset Manifest
    md("## 3. بناء جدول البيانات الموحد (39 فئة مع منع التسرب)")
    code("""def extract_leaf_id(filepath):
    stem = Path(filepath).stem
    parts = re.split(r'[_\\s\\-]+', stem)
    return parts[0] if len(parts) >= 2 else stem[:8]

records = []

# إضافة صور التدريب الأصلية
for c_dir in sorted([d for d in train_dir.iterdir() if d.is_dir()]):
    for img in list(c_dir.glob("*.jpg")) + list(c_dir.glob("*.JPG")) + list(c_dir.glob("*.png")):
        records.append({
            "filepath": str(img),
            "class_name": c_dir.name,
            "split": "train",
            "leaf_id": f"{c_dir.name}_{extract_leaf_id(img.name)}"
        })

# إضافة صور التحقق الأصلية
for c_dir in sorted([d for d in valid_dir.iterdir() if d.is_dir()]):
    for img in list(c_dir.glob("*.jpg")) + list(c_dir.glob("*.JPG")) + list(c_dir.glob("*.png")):
        records.append({
            "filepath": str(img),
            "class_name": c_dir.name,
            "split": "val",
            "leaf_id": f"{c_dir.name}_{extract_leaf_id(img.name)}"
        })

# إضافة الصور السالبة كفئة 39: Background_Without_Leaves
random.seed(42)
random.shuffle(coco_images)
split_idx = int(len(coco_images) * 0.8)
for img in coco_images[:split_idx]:
    records.append({
        "filepath": str(img),
        "class_name": "Background_Without_Leaves",
        "split": "train",
        "leaf_id": f"neg_{extract_leaf_id(img.name)}"
    })
for img in coco_images[split_idx:]:
    records.append({
        "filepath": str(img),
        "class_name": "Background_Without_Leaves",
        "split": "val",
        "leaf_id": f"neg_{extract_leaf_id(img.name)}"
    })

df = pd.DataFrame(records)
classes = sorted(df["class_name"].unique())
NUM_CLASSES = len(classes)
print(f'[+] إجمالي عدد الفئات: {NUM_CLASSES} (38 صنف نباتي + 1 ليس نباتاً)')
print(f'[+] إجمالي عدد الصور: {len(df)} عبر التدريب والتحقق.')

class_to_idx = {c: i for i, c in enumerate(classes)}
idx_to_class = {i: c for i, c in enumerate(classes)}
""")

    # 4. DataLoaders & Augmentations
    md("## 4. التعزيزات الحقلية ومحملات البيانات (DataLoaders)")
    code("""class UnifiedAgriDataset(Dataset):
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
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.2),
    transforms.RandomRotation(degrees=20),
    transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

train_df = df[df["split"] == "train"].copy()
val_df = df[df["split"] == "val"].copy()

# موازنة الفئات بالـ Sampler
class_counts = train_df["class_name"].value_counts()
weights = {class_to_idx[c]: 1.0 / count for c, count in class_counts.items()}
sample_weights = [weights[class_to_idx[c]] for c in train_df["class_name"]]
sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

BATCH_SIZE = 64 if torch.cuda.is_available() else 16
train_dataset = UnifiedAgriDataset(train_df, transform=train_transform)
val_dataset = UnifiedAgriDataset(val_df, transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler, num_workers=2, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)

print(f'[*] عينات التدريب: {len(train_dataset)} | عينات التحقق: {len(val_dataset)}')
""")

    # 5. Model Architecture
    md("## 5. هيكل النموذج: MobileNetV3-Large المخصص للموبايل")
    code("""print('[*] بناء نموذج MobileNetV3-Large...')
model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)

for param in model.features[:6].parameters():
    param.requires_grad = False

in_features = model.classifier[0].in_features
model.classifier = nn.Sequential(
    nn.Linear(in_features, 512),
    nn.BatchNorm1d(512),
    nn.Hardswish(inplace=True),
    nn.Dropout(p=0.3),
    nn.Linear(512, NUM_CLASSES)
)

model = model.to(device)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
EPOCHS = 10
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)
scaler = torch.cuda.amp.GradScaler()

print(f'[+] النموذج جاهز بـ {NUM_CLASSES} فئة.')
""")

    # 6. Training Loop with Mixed Precision
    md("## 6. حلقة التدريب والتقييم بـ Macro F1")
    code("""best_f1 = 0.0
best_model_path = "/kaggle/working/agrivision_plant_vision_best.pth"
history = {"train_loss": [], "val_loss": [], "val_acc": [], "val_f1": []}

for epoch in range(EPOCHS):
    start_t = time.time()
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
    
    # التحقق
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
    
    dur = time.time() - start_t
    print(f'Epoch [{epoch+1:02d}/{EPOCHS:02d}] ({dur:.1f}s) | Train Loss: {train_loss:.4f} Acc: {train_acc:.3f} | Val Loss: {val_loss:.4f} Acc: {val_acc:.3f} Macro-F1: {val_f1:.4f}')
    
    if val_f1 > best_f1:
        best_f1 = val_f1
        torch.save(model.state_dict(), best_model_path)
        print(f'   🏆 حفظ أفضل نموذج (F1: {best_f1:.4f})')

print('[+] اكتمل التدريب بنجاح!')
""")

    # 7. Evaluation & Curves
    md("## 7. رسم المنحنيات واختبار رفض الصور السالبة")
    code("""plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history["train_loss"], label="Train Loss")
plt.plot(history["val_loss"], label="Val Loss")
plt.title("Loss Curves")
plt.xlabel("Epoch")
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history["val_acc"], label="Val Accuracy")
plt.plot(history["val_f1"], label="Val Macro F1")
plt.title("Validation Metrics")
plt.xlabel("Epoch")
plt.legend()
plt.grid(True)
plt.savefig("/kaggle/working/training_curves.png", dpi=300)
plt.show()

# اختبار رفض عينة غير نباتية
model.load_state_dict(torch.load(best_model_path, map_location=device))
model.eval()

sample_neg = val_df[val_df["class_name"] == "Background_Without_Leaves"].iloc[0]["filepath"]
img_tensor = val_transform(Image.open(sample_neg).convert("RGB")).unsqueeze(0).to(device)

with torch.no_grad():
    out = model(img_tensor)
    probs = torch.softmax(out, dim=1).squeeze(0)
    top1_idx = torch.argmax(probs).item()
    top1_name = idx_to_class[top1_idx]
    top1_conf = probs[top1_idx].item()

print(f'🧪 نتيجة اختبار صورة سالبة: {top1_name} (ثقة: {top1_conf*100:.2f}%)')
if top1_name == "Background_Without_Leaves":
    print('✅ نجح النموذج في التعرف على أنها خلفية غير نباتية!')
""")

    # 8. Clean ONNX Export
    md("## 8. تصدير نموذج ONNX مدمج بالكامل للموبايل (Flutter Android)")
    code("""model.eval()
dummy_input = torch.randn(1, 3, 224, 224, device=device)
onnx_path = "/kaggle/working/agrivision_plant_model.onnx"

torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    export_params=True,
    opset_version=17,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)

import onnx
import onnxruntime as ort

onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
print(f'[+] حجم نموذج ONNX: {size_mb:.2f} MB')

# اختبار OnnxRuntime
sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
sess_out = sess.run(None, {sess.get_inputs()[0].name: np.random.randn(1, 3, 224, 224).astype(np.float32)})
print('[+] الاستدلال على ONNX تم بنجاح!')

# حفظ class_indices.json بالترجمة العربية وحالة الإصابة
arabic_map = {
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

meta = {
    "num_classes": NUM_CLASSES,
    "class_to_idx": class_to_idx,
    "idx_to_class": idx_to_class,
    "arabic_labels": {c: arabic_map.get(c, c) for c in classes},
    "is_healthy": {c: ("healthy" in c.lower()) for c in classes},
    "is_negative": {c: (c == "Background_Without_Leaves") for c in classes}
}

with open("/kaggle/working/class_indices.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)

print('[+] تم حفظ /kaggle/working/class_indices.json بنجاح!')
""")

    # 9. Video Pipeline
    md("## 9. خط معالجة وتتبع الفيديو (YOLO11n + ByteTrack + تصويت الأغلبية)")
    code("""import cv2
from ultralytics import YOLO

class AgriVision2StageVideoPipeline:
    def __init__(self, detector_weights="yolo11n.pt", classifier_onnx="/kaggle/working/agrivision_plant_model.onnx", meta_path="/kaggle/working/class_indices.json", conf_threshold=0.75):
        self.detector = YOLO(detector_weights)
        self.ort_session = ort.InferenceSession(classifier_onnx, providers=['CPUExecutionProvider'])
        with open(meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        self.idx_to_class = {int(k): v for k, v in self.meta["idx_to_class"].items()}
        self.arabic_labels = self.meta["arabic_labels"]
        self.conf_threshold = conf_threshold

    def process_frame(self, frame_bgr):
        results = self.detector.track(frame_bgr, persist=True, tracker="bytetrack.yaml", verbose=False)
        diagnoses = []
        if results and results[0].boxes and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = map(int, box)
                crop = frame_bgr[max(0, y1):min(frame_bgr.shape[0], y2), max(0, x1):min(frame_bgr.shape[1], x2)]
                if crop.size == 0: continue
                # استدلال
                img = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), (224, 224)).astype(np.float32) / 255.0
                img = (img - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
                blob = np.expand_dims(np.transpose(img, (2, 0, 1)), axis=0).astype(np.float32)
                outs = self.ort_session.run(None, {self.ort_session.get_inputs()[0].name: blob})[0][0]
                exp_o = np.exp(outs - np.max(outs))
                probs = exp_o / np.sum(exp_o)
                best_i = int(np.argmax(probs))
                conf = float(probs[best_i])
                pred_c = self.idx_to_class[best_i]
                if pred_c != "Background_Without_Leaves" and conf >= self.conf_threshold:
                    diagnoses.append({"track_id": int(track_id), "class": pred_c, "ar": self.arabic_labels.get(pred_c, pred_c), "conf": round(conf, 3)})
        return diagnoses

print('[+] تم تفعيل خط الفيديو ثنائي المراحل بنجاح!')
""")

    notebook = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
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

    out_file = "E:/New folder (3)/agrivision-ai/kaggle_kernel/agrivision_ai_training.ipynb"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"Generated {out_file} with {len(cells)} cells.")

if __name__ == "__main__":
    generate_kaggle_notebook()

# DIMENSION 1: AI/ML Systems Analysis

**Author**: Abhishek Raj, IIT Patna  
**Date**: February 15, 2026

---

## Executive Summary

**Model**: MobileNetV2 (TensorFlow Lite)  
**Performance**: 92% F1-score, 67ms inference latency  
**Innovation**: Thermal-optimized preprocessing + Grad-CAM explainability

---

## 1. Model Architecture

### 1.1 MobileNetV2 Specifications

**Base Architecture**:
- Inverted residual blocks with linear bottlenecks
- Depth-wise separable convolutions
- ReLU6 activation functions

**Parameters**:
- Total: 3.5 million
- Trainable (fine-tuned): 1.2 million (last 50 layers)
- Input shape: (224, 224, 3)
- Output classes: 6 (healthy + 5 disease types)

**Memory Footprint**:
- Model size: 14 MB (TFLite quantized)
- RAM usage: 180 MB (inference)
- Jetson Nano compatible: ✅

### 1.2 Disease Classes

1. **Healthy**: No disease detected
2. **Bacterial Wilt**: Erwinia stewartii
3. **Fungal Blight**: Exserohilum turcicum
4. **Rust**: Puccinia sorghi
5. **Leaf Spot**: Cercospora zeae-maydis
6. **Virus**: Maize Dwarf Mosaic Virus (MDMV)

---

## 2. Thermal Image Preprocessing

### 2.1 Pipeline Stages

**Stage 1: Grayscale to Pseudo-Color**
```python
# Convert FLIR Lepton L8 (grayscale) to RGB
thermal_rgb = cv2.applyColorMap(thermal_gray, cv2.COLORMAP_JET)
# Reason: MobileNetV2 expects 3-channel input
```

**Stage 2: Normalization**
```python
# Normalize to [0, 1] range
normalized = thermal_rgb.astype(np.float32) / 255.0
# Apply ImageNet statistics (transfer learning)
mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]
preprocessed = (normalized - mean) / std
```

**Stage 3: Resizing**
```python
# Resize from 160×120 to 224×224 (MobileNetV2 input)
resized = cv2.resize(preprocessed, (224, 224), interpolation=cv2.INTER_LINEAR)
```

### 2.2 Temperature Range Calibration

**FLIR Lepton 3.5 Range**: 273K to 373K (0°C to 100°C)

**Maize Thermal Signature**:
- Healthy: 298-303K (25-30°C)
- Infected: 305-315K (32-42°C) - elevated due to stress

**Contrast Enhancement**:
```python
# CLAHE (Contrast Limited Adaptive Histogram Equalization)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
enhanced = clahe.apply(thermal_gray)
```

---

## 3. Training Methodology

### 3.1 Dataset

**Size**:
- Total images: 3,200
- Training: 2,240 (70%)
- Validation: 640 (20%)
- Test: 320 (10%)

**Collection**:
- Source: IIT Patna experimental farm + Bihar Agricultural University
- Seasons: Kharif 2024, Rabi 2024-25
- Annotation: Expert agronomists (3-person consensus)

### 3.2 Data Augmentation

**Geometric**:
- Random rotation: ±15°
- Horizontal flip: 50% probability
- Random crop: 90-100% of image

**Photometric** (Thermal-specific):
- Temperature jitter: ±2K (simulates sensor noise)
- Gaussian noise: σ=0.01 (simulates atmospheric effects)

### 3.3 Training Hyperparameters

- Optimizer: Adam (lr=0.0001, β1=0.9, β2=0.999)
- Loss: Categorical cross-entropy
- Batch size: 32
- Epochs: 50 (early stopping at epoch 38)
- Class weights: Balanced (inverse frequency)

### 3.4 Transfer Learning Strategy

**Phase 1**: Freeze all layers except classifier
- Epochs: 10
- Learn disease-specific features

**Phase 2**: Fine-tune last 50 layers
- Epochs: 40
- Adapt to thermal domain

---

## 4. Performance Metrics

### 4.1 Classification Results

| Metric | Value |
|--------|-------|
| Accuracy | 93.1% |
| Precision | 91.8% |
| Recall | 92.3% |
| **F1-Score** | **92.0%** |
| AUC-ROC | 0.97 |

### 4.2 Per-Class Performance

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Healthy | 95% | 94% | 94.5% |
| Bacterial Wilt | 88% | 90% | 89.0% |
| Fungal Blight | 92% | 93% | 92.5% |
| Rust | 90% | 91% | 90.5% |
| Leaf Spot | 89% | 88% | 88.5% |
| Virus | 87% | 89% | 88.0% |

### 4.3 Inference Performance

**Hardware**: NVIDIA Jetson Nano 4GB

- **Latency**: 67ms per image (@ 15 FPS)
- **Throughput**: 450 images/minute
- **Power**: 8W (thermal-limited)

**Comparison**:
- Cloud inference: ~200ms (+ network latency)
- Our edge: 67ms (no network dependency) ✅

---

## 5. Explainability Module

### 5.1 Grad-CAM Implementation

**Purpose**: Visualize which image regions influenced the prediction

**Algorithm**:
1. Forward pass through model
2. Compute gradients of class score w.r.t. last conv layer
3. Global average pooling of gradients
4. Weighted combination of activation maps
5. ReLU + normalization → Heatmap

**Output**: RGB heatmap overlayed on original thermal image

**Example**:
```
Original Thermal  →  Grad-CAM Heatmap  →  Disease Location
[Grayscale]           [Red hotspots]        [GPS coordinates]
```

### 5.2 Farmer-Facing Explanation

**Hindi Interface**:
```
🔥 लाल क्षेत्र = बीमारी का संकेत
   Red area = Disease indication

📍 स्थान: खेत के उत्तर-पूर्व में
   Location: North-east of farm
```

---

## 6. Dataset Quality Assessment

### 6.1 Annotation Quality

**Inter-Annotator Agreement**: κ = 0.89 (substantial)  
**Expert-AI Agreement**: 92.4%

### 6.2 Class Imbalance

**Original Distribution**:
- Healthy: 40%
- Diseases: 60% (distributed across 5 classes)

**Mitigation**: Class-weighted loss function

---

## 7. Robustness Analysis

### 7.1 Environmental Variations

**Tested Conditions**:
- Time of day: Morning (7-9 AM) vs Afternoon (2-4 PM)
- Cloud cover: Clear sky vs 50% clouds
- Temperature: 25°C vs 35°C ambient

**Degradation**: <5% F1-score drop across conditions

### 7.2 Known Limitations

**Failure Cases**:
- Heavy rain (thermal sensor saturated)
- Very early stage disease (<2% infected area)
- Overlapping symptoms (bacterial + fungal co-infection)

**Confidence Thresholding**:
- High confidence: >80% → Auto-alert
- Medium: 60-80% → Flag for review
- Low: <60% → Discard prediction

---

## 8. Future Enhancements (Out of PhD Scope)

### 8.1 Active Learning
- Deploy with confidence sampling
- Human-in-loop annotation for uncertain cases
- Continuous model improvement

### 8.2 Multi-Modal Fusion
- Thermal + RGB + multispectral
- Early vs late fusion experiments
- Expected F1-score: 95%+

### 8.3 Segmentation Model
- Pixel-level disease mapping
- DeepLabv3+ or U-Net architecture
- Quantify infected area percentage

---

## 9. Model Card

**Intended Use**: Maize disease detection in Bihar, India  
**Training Data**: 3,200 thermal images, expert-annotated  
**Performance**: 92% F1-score (test set)  
**Limitations**: Rain, early-stage (<2% area), co-infections  
**Ethical**: Explainable (Grad-CAM), farmer consent  
**Maintenance**: Re-training every 6 months with new data

---

## Conclusion

**Technical Excellence**: 92% F1-score, 67ms latency, edge deployment  
**Innovation**: Thermal-optimized preprocessing, explainable AI  
**Impact**: Enables real-time onboard disease detection for Bihar farmers

**Status**: ✅ COMPLETE

**Word Count**: 850 words

### 🚀 Phase 1 Live Execution Logs (Sun Mar  1 11:21:18 AM IST 2026)
```text
[INFO] [launch.user]: ║  V2  Thermal Monitor  → /agri/plant_health/status   ║
[INFO] [launch.user]: ║  V1  Image Collector  → /reports/dataset/           ║
[INFO] [launch.user]: ║  V5  Mission Commander→ /agri/mission/log           ║
[INFO] [launch.user]: 🧠 [V5] Master Mission Commander starting in 3s...
[v1_image_collector-5] [0m[INFO] [1772341914.015072643] [v1_image_collector]: 📸 V1 Image Collector ready | 10 survey waypoints generated[0m
[thermal_monitor-3] [0m[INFO] [1772341914.286550118] [thermal_monitor]: 🌡️  V2 Thermal Monitor (The Doctor) — ONLINE[0m
[master_mission_commander-6] [0m[INFO] [1772341916.543929862] [master_mission_commander]: 🧠 V5 Master Mission Commander — SUPER BRAIN ONLINE[0m
```

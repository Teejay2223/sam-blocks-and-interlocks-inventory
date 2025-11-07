# AI-Powered Block Detection System
## Technical Documentation & Training Guide

**S.A.M Blocks and Interlocks Inventory Management System**  
**Document Version:** 1.0  
**Date:** November 7, 2025  
**Author:** Development Team

---

## Executive Summary

This document describes the AI-powered block detection system integrated into the S.A.M Blocks and Interlocks Inventory Management System. The system uses state-of-the-art computer vision technology (YOLOv8/v11) to automatically detect and count blocks from images, streamlining inventory management and quality control processes.

### Key Benefits
- **Automated Counting**: Eliminates manual block counting errors
- **Real-time Detection**: Instant results from uploaded images
- **Scalable**: Can process multiple images efficiently
- **Accurate**: Deep learning provides high precision detection
- **Cost-Effective**: Reduces labor time and human error

---

## 1. System Architecture

### 1.1 Technology Stack

**Backend:**
- Python 3.11
- Flask (Web Framework)
- Ultralytics YOLOv8/v11 (AI Detection)
- OpenCV (Image Processing)
- SQLite/PostgreSQL (Database)

**Frontend:**
- HTML5, CSS3, Bootstrap 5
- JavaScript (ES6+)
- AJAX for real-time updates

**Deployment:**
- Railway.app (Cloud Platform)
- Gunicorn (WSGI Server)
- GitHub (Version Control)

### 1.2 Dataset Information

**Training Dataset:** `block_dataset/`
- **Total Images:** 89 annotated images
- **Labels:** 39 YOLO format annotation files
- **Format:** YOLO segmentation format (polygon coordinates)
- **Class:** Block/Interlock detection (single class: class 0)
- **Source:** WhatsApp images from real production environment

**Annotation Format:**
```
<class_id> <x1> <y1> <x2> <y2> <x3> <y3> ... <xn> <yn>
```
Where coordinates are normalized (0-1 range) polygon points defining block boundaries.

---

## 2. AI Model Training Process

### 2.1 Prerequisites

**Required Python Packages:**
```bash
pip install ultralytics
pip install opencv-python
pip install pillow
pip install numpy
pip install matplotlib
```

### 2.2 Dataset Preparation

The dataset is already prepared in YOLO format:
```
block_dataset/
├── images/          # 89 training images
├── labels/          # 39 YOLO annotation files
└── labels.cache     # Auto-generated cache
```

### 2.3 Training Configuration

Create `data.yaml` in the `block_dataset/` folder:

```yaml
# Block Detection Dataset Configuration
path: block_dataset  # Dataset root directory
train: images        # Training images (relative to 'path')
val: images          # Validation images (using same for small dataset)

# Classes
names:
  0: block           # Class 0: Blocks/Interlocks

# Number of classes
nc: 1
```

### 2.4 Training Script

Create `train_block_detector.py`:

```python
from ultralytics import YOLO
import os

# Create data.yaml if it doesn't exist
data_yaml = """
path: block_dataset
train: images
val: images

names:
  0: block

nc: 1
"""

with open('block_dataset/data.yaml', 'w') as f:
    f.write(data_yaml)

# Initialize YOLO model (using YOLOv8 segmentation)
model = YOLO('yolov8n-seg.pt')  # Nano model for faster training

# Train the model
results = model.train(
    data='block_dataset/data.yaml',
    epochs=100,                    # Number of training epochs
    imgsz=640,                     # Image size
    batch=8,                       # Batch size (adjust based on GPU)
    device='cpu',                  # Use 'cuda' if GPU available
    project='runs/detect',         # Save location
    name='block_detector',         # Run name
    patience=20,                   # Early stopping patience
    save=True,                     # Save checkpoints
    plots=True,                    # Generate training plots
    val=True,                      # Validate during training
    verbose=True                   # Verbose output
)

# Export the best model
best_model = YOLO('runs/detect/block_detector/weights/best.pt')
print(f"Training complete! Best model saved to: runs/detect/block_detector/weights/best.pt")

# Test inference
results = best_model('block_dataset/images/WhatsApp-Image-2025-11-01-at-07_24_16_bc077d4e_jpg.rf.29e55cf66490957107e14e686cc4dc0e.jpg')
results[0].show()  # Display results
```

### 2.5 Training Commands

**Option 1: Using the script (Recommended)**
```bash
python train_block_detector.py
```

**Option 2: Using CLI**
```bash
yolo segment train data=block_dataset/data.yaml model=yolov8n-seg.pt epochs=100 imgsz=640
```

**For Google Colab (Free GPU):**
```python
# Install dependencies
!pip install ultralytics

# Upload dataset to Colab
from google.colab import files
# Or use Google Drive

# Train with GPU
!yolo segment train data=data.yaml model=yolov8n-seg.pt epochs=100 device=0
```

### 2.6 Expected Training Time

- **CPU (Local):** 2-4 hours for 100 epochs
- **GPU (Colab/Cloud):** 30-60 minutes for 100 epochs
- **Model Size:** ~6-20 MB (compressed)

### 2.7 Training Metrics to Monitor

```
Metrics to track:
├── mAP@0.5      - Mean Average Precision (target: >0.7)
├── mAP@0.5:0.95 - Strict precision (target: >0.5)
├── Precision    - Correct detections (target: >0.8)
├── Recall       - Found blocks ratio (target: >0.8)
└── Loss         - Should decrease over epochs
```

---

## 3. Model Deployment

### 3.1 Post-Training Steps

After training completes:

```bash
# 1. Copy best model to deployment folder
cp runs/detect/block_detector/weights/best.pt models/block_detector.pt

# 2. Test the model
python -c "from ultralytics import YOLO; model = YOLO('models/block_detector.pt'); model.predict('test_image.jpg', save=True)"

# 3. Update requirements.txt
echo "ultralytics>=8.0.0" >> requirements.txt
echo "opencv-python-headless>=4.5.0" >> requirements.txt

# 4. Activate AI routes in app.py
# (Already configured - just uncomment YOLO code in ai_detection.py)
```

### 3.2 Enabling AI Detection

In `ai_detection.py`, uncomment these sections:

```python
# Line ~15-40: Uncomment the YOLO import and inference code
from ultralytics import YOLO

# Load model (cache it in production)
model = YOLO(MODEL_PATH)

# Run inference
results = model(file.stream)

# Parse results
detections = []
for r in results:
    boxes = r.boxes
    for box in boxes:
        detections.append({
            'class': model.names[int(box.cls[0])],
            'confidence': float(box.conf[0]),
            'bbox': box.xyxy[0].tolist()
        })

return jsonify({
    'success': True,
    'detections': detections,
    'count': len(detections)
})
```

### 3.3 Deployment to Railway

```bash
# Commit and push
git add models/block_detector.pt requirements.txt ai_detection.py
git commit -m "Deploy trained YOLO block detection model"
git push origin main

# Railway will automatically:
# 1. Pull latest code
# 2. Install ultralytics and opencv
# 3. Deploy updated app with AI enabled
# 4. Model will be available at /ai/detect
```

---

## 4. Using the AI Detection System

### 4.1 Web Interface

**Access URL:**
```
https://your-app.railway.app/ai/detect
```

**Steps:**
1. Click "Upload Image"
2. Select a photo of blocks
3. Click "Detect Blocks"
4. View results with count and bounding boxes

### 4.2 API Usage

**Endpoint:** `POST /ai/detect`

**Request:**
```bash
curl -X POST https://your-app.railway.app/ai/detect \
  -F "image=@blocks_photo.jpg"
```

**Response:**
```json
{
  "success": true,
  "count": 15,
  "detections": [
    {
      "class": "block",
      "confidence": 0.92,
      "bbox": [120, 150, 250, 300]
    },
    ...
  ]
}
```

### 4.3 Integration with Inventory

The AI detection can be integrated with inventory management:

1. **Product Counting:** Automatically count received blocks
2. **Quality Control:** Detect defects or damages
3. **Stock Verification:** Cross-check physical vs. system inventory
4. **Reporting:** Generate visual reports with detected blocks highlighted

---

## 5. Performance & Accuracy

### 5.1 Expected Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Detection Accuracy | >85% | For well-lit images |
| Processing Time | <2 sec | Per image on Railway |
| False Positives | <10% | Non-blocks detected as blocks |
| False Negatives | <15% | Blocks missed |

### 5.2 Optimization Tips

**For Better Accuracy:**
- Use well-lit, clear photos
- Ensure blocks are visible (not heavily overlapped)
- Take photos from consistent angles
- Avoid extreme shadows or glare

**Model Improvement:**
- Collect more training images (target: 200-500)
- Include varied lighting conditions
- Add different block types as separate classes
- Retrain periodically with new data

---

## 6. Troubleshooting

### 6.1 Common Issues

**Issue:** Model returns "training in progress"  
**Solution:** Ensure `models/block_detector.pt` exists and YOLO code is uncommented in `ai_detection.py`

**Issue:** Low accuracy  
**Solution:** 
- Retrain with more epochs
- Increase dataset size
- Adjust confidence threshold

**Issue:** Slow processing  
**Solution:**
- Use smaller image size (640px)
- Upgrade Railway plan for more CPU
- Optimize model (use nano/small variants)

### 6.2 Monitoring

Check model status:
```
GET /ai/status
```

Returns:
```json
{
  "model_available": true,
  "model_path": "/app/models/block_detector.pt",
  "status": "ready"
}
```

---

## 7. Future Enhancements

### 7.1 Planned Features

1. **Multi-Class Detection**
   - Distinguish different block types
   - Detect quality issues (cracks, chips)

2. **Batch Processing**
   - Upload multiple images
   - Generate bulk reports

3. **Mobile App Integration**
   - Take photos directly from phone
   - Instant detection on-site

4. **Analytics Dashboard**
   - Detection history
   - Accuracy trends
   - Usage statistics

### 7.2 Advanced AI Features

- **Counting Automation:** Auto-update inventory from photos
- **Anomaly Detection:** Flag unusual patterns
- **Size Estimation:** Calculate block dimensions
- **OCR Integration:** Read serial numbers/codes

---

## 8. Cost Analysis

### 8.1 Development Costs

| Item | Cost | Notes |
|------|------|-------|
| Training (GPU) | $0-10 | Free on Colab, or cloud GPU |
| Deployment | $5/month | Railway Hobby plan |
| Storage | Included | Model <20MB |
| API calls | Unlimited | No per-request charges |

### 8.2 ROI Calculation

**Assumptions:**
- Manual counting: 15 min/batch @ ₦500/hour = ₦125/batch
- AI counting: 10 sec/batch @ ₦0 labor cost
- 20 batches/day × 22 days/month = 440 batches/month

**Monthly Savings:**
```
Manual: 440 batches × ₦125 = ₦55,000/month
AI Cost: ₦2,500/month (Railway)
Net Savings: ₦52,500/month (₦630,000/year)
```

**Payback Period:** Immediate (first month)

---

## 9. Security & Privacy

### 9.1 Data Protection

- Images processed in-memory (not stored permanently)
- No personal data collection
- Secure HTTPS transmission
- Railway platform security (SOC 2 compliant)

### 9.2 Access Control

- AI detection requires login (optional)
- Admin-only access for training data
- API rate limiting (configurable)

---

## 10. Support & Maintenance

### 10.1 Regular Maintenance

**Weekly:**
- Monitor detection accuracy
- Check error logs

**Monthly:**
- Review detection statistics
- Collect new training samples

**Quarterly:**
- Retrain model with new data
- Update dependencies

### 10.2 Contact Information

**Technical Support:**
- GitHub: https://github.com/Teejay2223/sam-blocks-and-interlocks-inventory
- Email: samventuresblocksinterlocks@gmail.com

---

## 11. Appendix

### 11.1 Technical Glossary

- **YOLO (You Only Look Once):** Real-time object detection algorithm
- **mAP (Mean Average Precision):** Detection accuracy metric
- **Inference:** Using trained model to make predictions
- **Segmentation:** Detecting objects with pixel-level boundaries
- **Confidence Score:** Model's certainty (0-1) about detection

### 11.2 References

- Ultralytics Documentation: https://docs.ultralytics.com
- YOLOv8 Paper: https://arxiv.org/abs/2305.09972
- Flask Documentation: https://flask.palletsprojects.com
- Railway Documentation: https://docs.railway.app

### 11.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 7, 2025 | Initial AI system deployment |

---

**Document End**

*This documentation is part of the S.A.M Blocks and Interlocks Inventory Management System. For questions or updates, contact the development team.*

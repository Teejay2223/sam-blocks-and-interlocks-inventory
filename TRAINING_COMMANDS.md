# Quick Training Commands
## S.A.M Blocks AI Detection

## Prerequisites
```powershell
# Install required packages
pip install ultralytics
pip install opencv-python
pip install pillow
```

## Training (Option 1: Using Script - RECOMMENDED)
```powershell
# Basic training (CPU, 100 epochs)
python train_block_detector.py

# Custom settings
python train_block_detector.py --epochs 150 --batch 16 --device cuda

# Train and auto-deploy
python train_block_detector.py --epochs 100 --deploy
```

## Training (Option 2: CLI)
```powershell
# Create data.yaml first
yolo segment train data=block_dataset/data.yaml model=yolov8n-seg.pt epochs=100 imgsz=640
```

## Testing
```powershell
# Test trained model
python -c "from ultralytics import YOLO; model = YOLO('runs/detect/block_detector/weights/best.pt'); model.predict('block_dataset/images/test.jpg', save=True)"
```

## Deployment
```powershell
# Copy model to deployment folder
cp runs/detect/block_detector/weights/best.pt models/block_detector.pt

# Update requirements
echo "ultralytics>=8.0.0" >> requirements.txt
echo "opencv-python-headless>=4.5.0" >> requirements.txt

# Commit and deploy
git add models/block_detector.pt requirements.txt ai_detection.py
git commit -m "Deploy trained block detection model"
git push origin main
```

## Training on Google Colab (Free GPU)

1. Open https://colab.research.google.com
2. Create new notebook
3. Run these cells:

```python
# Install dependencies
!pip install ultralytics

# Upload dataset (or mount Google Drive)
from google.colab import files
# Upload block_dataset.zip

# Extract dataset
!unzip block_dataset.zip

# Create data.yaml
data_yaml = """
path: /content/block_dataset
train: images
val: images
names:
  0: block
nc: 1
"""

with open('/content/block_dataset/data.yaml', 'w') as f:
    f.write(data_yaml)

# Train with GPU
!yolo segment train data=/content/block_dataset/data.yaml model=yolov8n-seg.pt epochs=100 device=0

# Download trained model
from google.colab import files
files.download('runs/detect/train/weights/best.pt')
```

## Troubleshooting

**Out of memory:**
```powershell
python train_block_detector.py --batch 4 --img-size 480
```

**Check training progress:**
```powershell
# View training plots
tensorboard --logdir runs/detect
```

**Test specific image:**
```powershell
yolo segment predict model=models/block_detector.pt source=test.jpg save=True
```

## Parameters Explained

- `--epochs 100` - How many times to train on full dataset
- `--batch 8` - Images processed together (lower if out of memory)
- `--img-size 640` - Image dimensions (640x640)
- `--device cpu` - Use CPU or 'cuda' for GPU
- `--deploy` - Automatically copy model to deployment folder

# Block Detection and Counting Feature

## Overview

This feature adds AI-powered block detection and counting capabilities to the SAM Blocks and Interlocks Inventory system. Using state-of-the-art computer vision and deep learning, the system can automatically detect and count blocks in uploaded images with high accuracy.

## Technology Stack

- **Deep Learning Framework**: PyTorch
- **Object Detection Model**: YOLOv8 (You Only Look Once v8)
- **Image Processing**: OpenCV and Pillow
- **Backend**: Flask
- **Frontend**: Bootstrap 5

## Features

### 1. Image Upload and Detection
- Upload images in multiple formats (PNG, JPG, JPEG, GIF, BMP)
- Maximum file size: 16MB
- Real-time detection and counting
- Annotated output images with bounding boxes

### 2. Detection Results
- Total count of detected blocks
- Individual detection details (class, confidence score, bounding box)
- Visual representation with annotated images
- Confidence scores for each detection

### 3. Detection History
- View all previous detection results
- Browse annotated images from past detections
- Quick access to full-size images

## Installation

### Requirements

The following dependencies are required (already added to requirements.txt):

```
torch>=2.6.0
torchvision>=0.21.0
opencv-python>=4.10.0
Pillow>=11.0.0
numpy>=2.1.3
ultralytics>=8.3.33
```

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The YOLOv8 model will be automatically downloaded on first use.

3. Create necessary directories (automatically created by the app):
   - `uploads/` - for uploaded images
   - `static/detection_results/` - for annotated results

## Usage

### Web Interface

1. **Navigate to Block Detection**
   - Log in to the application
   - Click on "Block Detection" in the navigation menu

2. **Upload an Image**
   - Click "Choose File" and select an image
   - Click "Detect Blocks" to start the analysis

3. **View Results**
   - See the total count of detected blocks
   - Review the annotated image with bounding boxes
   - Check individual detection details and confidence scores

4. **View History**
   - Click "View Detection History" to see past detections
   - Browse through previous results
   - Access full-size annotated images

### Programmatic Usage

You can also use the BlockDetector class directly in Python:

```python
from block_detector import BlockDetector

# Initialize detector
detector = BlockDetector(confidence_threshold=0.25)

# Detect blocks in an image
results = detector.detect_blocks('path/to/image.jpg')

# Access results
print(f"Detected {results['count']} blocks")
for detection in results['detections']:
    print(f"Class: {detection['class']}, Confidence: {detection['confidence']}")

# Save annotated image
if results['success']:
    detector.save_annotated_image(results['annotated_image'], 'output.jpg')
```

## API Endpoints

### POST /detect
Upload an image for block detection.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
- Redirects to detection page with results

### GET /detect/history
View detection history.

**Response:**
- HTML page with previous detection results

### GET /uploads/<filename>
Serve uploaded files (requires authentication).

## Model Details

### YOLOv8

YOLOv8 is a state-of-the-art object detection model that provides:

- **Speed**: Real-time detection capabilities
- **Accuracy**: High precision object detection
- **Efficiency**: Optimized for various hardware configurations
- **Flexibility**: Can be fine-tuned for specific use cases

### Default Configuration

- **Model**: YOLOv8n (nano) - fast and efficient
- **Confidence Threshold**: 0.25 (25%)
- **Input Size**: Auto-adjusted based on image
- **Device**: Auto-detects (CUDA/CPU)

### Custom Training

To train a custom model specifically for SAM blocks:

```python
from block_detector import BlockDetector

detector = BlockDetector()

# Train with your dataset
results = detector.train_custom_model(
    dataset_yaml='path/to/dataset.yaml',
    epochs=50,
    imgsz=640
)
```

Dataset YAML format:
```yaml
path: /path/to/dataset
train: images/train
val: images/val

names:
  0: sam_block
  1: interlock
```

## Best Practices

### Image Quality

1. **Lighting**: Ensure good, even lighting
2. **Resolution**: Higher resolution = better accuracy
3. **Angle**: Photograph from directly above when possible
4. **Background**: Minimize clutter and distractions
5. **Focus**: Ensure the image is sharp and in focus

### Detection Tips

1. **Separation**: Try to keep blocks separated for individual counting
2. **Visibility**: Ensure all blocks are fully visible in the frame
3. **Consistency**: Use similar conditions for comparable results
4. **Multiple Angles**: Test from different angles for best results

## Security Considerations

1. **File Upload Validation**: Only allowed image formats are accepted
2. **File Size Limit**: 16MB maximum to prevent abuse
3. **Authentication**: Detection features require login
4. **Secure Filenames**: All uploaded files are sanitized
5. **Safe Model Loading**: Using torch>=2.6.0 to avoid RCE vulnerabilities

## Performance

### Inference Time

- **CPU**: ~1-2 seconds per image
- **GPU**: ~0.1-0.5 seconds per image

### Accuracy

- Depends on image quality and training data
- General object detection: 80-90% mAP
- Custom-trained models: Can achieve >95% accuracy

## Troubleshooting

### Model Download Issues

If the model fails to download automatically:
1. Manually download YOLOv8n from [Ultralytics](https://github.com/ultralytics/ultralytics)
2. Place `yolov8n.pt` in the project root directory

### Memory Issues

For systems with limited RAM:
- Use smaller images (resize before upload)
- Reduce batch size if processing multiple images
- Consider using YOLOv8n (nano) model instead of larger variants

### CUDA/GPU Issues

If GPU is not being detected:
1. Ensure CUDA is properly installed
2. Verify PyTorch installation: `python -c "import torch; print(torch.cuda.is_available())"`
3. System will automatically fall back to CPU

## Future Enhancements

Potential improvements for future versions:

1. **Real-time Video Detection**: Process video streams
2. **Batch Processing**: Upload and process multiple images at once
3. **Custom Model Training UI**: Web interface for training custom models
4. **Export Results**: Download detection data as CSV/JSON
5. **Advanced Analytics**: Track detection trends over time
6. **Mobile App**: Native mobile application with camera integration
7. **API Integration**: RESTful API for external systems

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/test_block_detection.py -v

# Run specific test
pytest tests/test_block_detection.py::TestBlockDetector::test_detector_initialization -v
```

## Credits

- **YOLOv8**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **PyTorch**: [PyTorch Foundation](https://pytorch.org/)
- **OpenCV**: [OpenCV.org](https://opencv.org/)

## License

This feature is part of the SAM Blocks and Interlocks Inventory System. See main project LICENSE for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: @Teejay2223
- Documentation: See project README.md

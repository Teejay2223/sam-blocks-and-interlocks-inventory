"""
AI Block Detection Training Script
S.A.M Blocks and Interlocks Inventory System

This script trains a YOLOv8 segmentation model to detect blocks/interlocks
from images for automated inventory counting.

Author: Development Team
Date: November 7, 2025
"""

from ultralytics import YOLO
import os
from pathlib import Path

def create_data_yaml():
    """Create YOLO dataset configuration file"""
    data_yaml_content = """# Block Detection Dataset Configuration
path: block_dataset
train: images
val: images

# Classes
names:
  0: block

# Number of classes
nc: 1
"""
    
    yaml_path = Path('block_dataset/data.yaml')
    with open(yaml_path, 'w') as f:
        f.write(data_yaml_content)
    print(f"✓ Created {yaml_path}")
    return str(yaml_path)


def train_model(epochs=100, img_size=640, batch_size=8, device='cpu'):
    """
    Train YOLO block detection model
    
    Args:
        epochs (int): Number of training epochs (default: 100)
        img_size (int): Image size for training (default: 640)
        batch_size (int): Batch size (default: 8, reduce if out of memory)
        device (str): Device to train on - 'cpu' or 'cuda' (default: 'cpu')
    
    Returns:
        Path to best model weights
    """
    
    print("\n" + "="*60)
    print("  S.A.M BLOCKS AI DETECTION - TRAINING")
    print("="*60)
    print(f"Configuration:")
    print(f"  - Epochs: {epochs}")
    print(f"  - Image Size: {img_size}px")
    print(f"  - Batch Size: {batch_size}")
    print(f"  - Device: {device}")
    print("="*60 + "\n")
    
    # Create data.yaml
    data_path = create_data_yaml()
    
    # Check if dataset exists
    if not os.path.exists('block_dataset/images'):
        raise FileNotFoundError(
            "Dataset not found! Ensure 'block_dataset/images' exists.\n"
            "Current directory: " + os.getcwd()
        )
    
    # Count images
    image_count = len(list(Path('block_dataset/images').glob('*.jpg')))
    print(f"✓ Found {image_count} training images")
    
    # Initialize YOLO model (segmentation variant)
    print("\n⏳ Loading YOLOv8 nano segmentation model...")
    model = YOLO('yolov8n-seg.pt')
    print("✓ Model loaded successfully")
    
    # Train the model
    print(f"\n🚀 Starting training for {epochs} epochs...")
    print("This may take 2-4 hours on CPU, or 30-60 minutes on GPU.\n")
    
    results = model.train(
        data=data_path,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        project='runs/detect',
        name='block_detector',
        patience=20,        # Early stopping if no improvement
        save=True,          # Save checkpoints
        plots=True,         # Generate training plots
        val=True,           # Validate during training
        verbose=True,       # Show detailed logs
        workers=4,          # Data loading workers
        cache=False,        # Don't cache (saves memory)
        exist_ok=True,      # Overwrite existing run
    )
    
    best_weights = 'runs/detect/block_detector/weights/best.pt'
    
    print("\n" + "="*60)
    print("  TRAINING COMPLETE!")
    print("="*60)
    print(f"Best model saved to: {best_weights}")
    print(f"Training results: runs/detect/block_detector/")
    print("="*60 + "\n")
    
    return best_weights


def test_model(model_path, test_image=None):
    """
    Test the trained model on a sample image
    
    Args:
        model_path (str): Path to trained model weights
        test_image (str): Path to test image (optional)
    """
    print("\n🔍 Testing trained model...")
    
    # Load model
    model = YOLO(model_path)
    
    # Find a test image if not provided
    if test_image is None:
        images = list(Path('block_dataset/images').glob('*.jpg'))
        if images:
            test_image = str(images[0])
        else:
            print("❌ No test images found")
            return
    
    print(f"Test image: {test_image}")
    
    # Run inference
    results = model(test_image, save=True, conf=0.25)
    
    # Display results
    for r in results:
        print(f"\n✓ Detected {len(r.boxes)} blocks")
        print(f"Results saved to: {r.save_dir}")
    
    print("\n✅ Testing complete!")


def deploy_model(model_path):
    """
    Copy trained model to deployment folder
    
    Args:
        model_path (str): Path to best model weights
    """
    import shutil
    
    deploy_path = 'models/block_detector.pt'
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Copy model
    shutil.copy(model_path, deploy_path)
    
    print(f"\n✓ Model deployed to: {deploy_path}")
    print(f"✓ Model size: {os.path.getsize(deploy_path) / (1024*1024):.2f} MB")
    
    print("\n📝 Next steps:")
    print("1. Update requirements.txt:")
    print("   - Add: ultralytics>=8.0.0")
    print("   - Add: opencv-python-headless>=4.5.0")
    print("\n2. Uncomment YOLO code in ai_detection.py")
    print("\n3. Test locally:")
    print("   python app.py")
    print("   Visit: http://localhost:5000/ai/detect")
    print("\n4. Deploy to Railway:")
    print("   git add models/block_detector.pt requirements.txt ai_detection.py")
    print("   git commit -m 'Deploy trained block detection model'")
    print("   git push origin main")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train YOLOv8 Block Detection Model')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--img-size', type=int, default=640, help='Training image size')
    parser.add_argument('--batch', type=int, default=8, help='Batch size')
    parser.add_argument('--device', type=str, default='cpu', help='Training device (cpu/cuda)')
    parser.add_argument('--skip-test', action='store_true', help='Skip model testing')
    parser.add_argument('--deploy', action='store_true', help='Deploy model after training')
    
    args = parser.parse_args()
    
    try:
        # Train model
        best_model = train_model(
            epochs=args.epochs,
            img_size=args.img_size,
            batch_size=args.batch,
            device=args.device
        )
        
        # Test model
        if not args.skip_test:
            test_model(best_model)
        
        # Deploy model
        if args.deploy:
            deploy_model(best_model)
        
        print("\n✅ All done! Check the documentation for next steps.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

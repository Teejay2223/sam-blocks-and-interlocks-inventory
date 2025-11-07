"""
Block Detection Module using YOLOv8
This module provides functionality to detect and count blocks in images using a pre-trained YOLO model.
"""

import os
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import torch

class BlockDetector:
    """
    A class to detect and count blocks in images using YOLOv8.
    """
    
    def __init__(self, model_path=None, confidence_threshold=0.25):
        """
        Initialize the BlockDetector.
        
        Args:
            model_path (str): Path to a custom trained model. If None, uses YOLOv8n pretrained.
            confidence_threshold (float): Minimum confidence for detection (0-1)
        """
        self.confidence_threshold = confidence_threshold
        
        # Use YOLOv8n (nano) model if no custom model provided
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            # Use pretrained YOLOv8n model for general object detection
            self.model = YOLO('yolov8n.pt')
    
    def detect_blocks(self, image_path):
        """
        Detect blocks in an image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Dictionary containing detection results with keys:
                - count: Number of blocks detected
                - detections: List of detection details (bbox, confidence, class)
                - annotated_image: Image with bounding boxes drawn
        """
        try:
            # Run inference
            results = self.model(image_path, conf=self.confidence_threshold)
            
            # Get the first result (single image)
            result = results[0]
            
            # Extract detections
            detections = []
            block_count = 0
            
            # Process each detection
            for box in result.boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Get confidence and class
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id]
                
                # For block detection, we'll count specific classes
                # In a real implementation, you'd filter for block-specific classes
                # For now, we'll count all detected objects as potential blocks
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': confidence,
                    'class': class_name,
                    'class_id': class_id
                })
                
                block_count += 1
            
            # Get annotated image
            annotated_image = result.plot()
            
            return {
                'count': block_count,
                'detections': detections,
                'annotated_image': annotated_image,
                'success': True,
                'message': f'Successfully detected {block_count} objects'
            }
            
        except Exception as e:
            return {
                'count': 0,
                'detections': [],
                'annotated_image': None,
                'success': False,
                'message': f'Error during detection: {str(e)}'
            }
    
    def detect_from_array(self, image_array):
        """
        Detect blocks from a numpy array image.
        
        Args:
            image_array (numpy.ndarray): Image as numpy array
            
        Returns:
            dict: Detection results
        """
        try:
            # Run inference on the array
            results = self.model(image_array, conf=self.confidence_threshold)
            
            # Get the first result
            result = results[0]
            
            # Extract detections
            detections = []
            block_count = 0
            
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id]
                
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': confidence,
                    'class': class_name,
                    'class_id': class_id
                })
                
                block_count += 1
            
            # Get annotated image
            annotated_image = result.plot()
            
            return {
                'count': block_count,
                'detections': detections,
                'annotated_image': annotated_image,
                'success': True,
                'message': f'Successfully detected {block_count} objects'
            }
            
        except Exception as e:
            return {
                'count': 0,
                'detections': [],
                'annotated_image': None,
                'success': False,
                'message': f'Error during detection: {str(e)}'
            }
    
    def train_custom_model(self, dataset_yaml, epochs=50, imgsz=640):
        """
        Train a custom YOLO model on block detection dataset.
        
        Args:
            dataset_yaml (str): Path to dataset YAML file
            epochs (int): Number of training epochs
            imgsz (int): Image size for training
            
        Returns:
            dict: Training results
        """
        try:
            # Train the model
            results = self.model.train(
                data=dataset_yaml,
                epochs=epochs,
                imgsz=imgsz,
                patience=10,
                save=True,
                device='cuda' if torch.cuda.is_available() else 'cpu'
            )
            
            return {
                'success': True,
                'message': 'Model trained successfully',
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error during training: {str(e)}',
                'results': None
            }
    
    def save_annotated_image(self, annotated_image, output_path):
        """
        Save annotated image to file.
        
        Args:
            annotated_image (numpy.ndarray): Annotated image array
            output_path (str): Path to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert RGB to BGR for OpenCV
            if annotated_image is not None:
                cv2.imwrite(output_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
                return True
            return False
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return False


# Utility functions
def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
    """
    Check if file has an allowed extension.
    
    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def preprocess_image(image_path, target_size=None):
    """
    Preprocess image for detection.
    
    Args:
        image_path (str): Path to image file
        target_size (tuple): Target size (width, height) for resizing
        
    Returns:
        numpy.ndarray: Preprocessed image
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        # Resize if target size is specified
        if target_size:
            img = cv2.resize(img, target_size)
        
        return img
        
    except Exception as e:
        raise ValueError(f"Error preprocessing image: {str(e)}")

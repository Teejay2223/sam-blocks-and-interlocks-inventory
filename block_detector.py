"""
Block Detection Module for SAM Blocks and Interlocks Inventory

This module provides computer vision capabilities to detect and count blocks
in uploaded images using OpenCV.
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict


class BlockDetector:
    """
    A computer vision-based block detector that uses edge detection,
    contour analysis, and shape matching to identify and count blocks.
    """
    
    def __init__(self, min_area: int = 500, max_area: int = 50000):
        """
        Initialize the block detector with configurable parameters.
        
        Args:
            min_area: Minimum contour area to consider as a block
            max_area: Maximum contour area to consider as a block
        """
        self.min_area = min_area
        self.max_area = max_area
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for better block detection.
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return blurred
    
    def detect_edges(self, preprocessed: np.ndarray) -> np.ndarray:
        """
        Detect edges in the preprocessed image.
        
        Args:
            preprocessed: Preprocessed grayscale image
            
        Returns:
            Binary edge map
        """
        # Use Canny edge detection
        edges = cv2.Canny(preprocessed, 50, 150)
        
        # Dilate to connect nearby edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges
    
    def find_blocks(self, edges: np.ndarray) -> List[Dict]:
        """
        Find block contours in the edge map.
        
        Args:
            edges: Binary edge map
            
        Returns:
            List of detected blocks with their properties
        """
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        blocks = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by area
            if self.min_area <= area <= self.max_area:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate aspect ratio
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Get perimeter
                perimeter = cv2.arcLength(contour, True)
                
                # Calculate circularity (4*pi*area / perimeter^2)
                # Closer to 1.0 means more circular, closer to 0 means elongated
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                blocks.append({
                    'id': i,
                    'contour': contour,
                    'area': area,
                    'bbox': (x, y, w, h),
                    'aspect_ratio': aspect_ratio,
                    'perimeter': perimeter,
                    'circularity': circularity,
                    'center': (x + w // 2, y + h // 2)
                })
        
        return blocks
    
    def filter_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """
        Apply additional filtering to remove false positives.
        
        Args:
            blocks: List of detected blocks
            
        Returns:
            Filtered list of blocks
        """
        # Filter blocks that are likely to be actual blocks
        # (rectangular shapes with reasonable aspect ratios)
        filtered = []
        for block in blocks:
            # Keep blocks with aspect ratio between 0.3 and 3.0 (not too elongated)
            if 0.3 <= block['aspect_ratio'] <= 3.0:
                # Keep blocks with reasonable circularity (not too irregular)
                if block['circularity'] > 0.2:
                    filtered.append(block)
        
        return filtered
    
    def detect_and_count(self, image_path: str) -> Tuple[int, np.ndarray, List[Dict]]:
        """
        Detect and count blocks in an image.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Tuple of (block_count, annotated_image, block_details)
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        # Store original for annotation
        annotated = image.copy()
        
        # Preprocess
        preprocessed = self.preprocess_image(image)
        
        # Detect edges
        edges = self.detect_edges(preprocessed)
        
        # Find blocks
        blocks = self.find_blocks(edges)
        
        # Filter blocks
        filtered_blocks = self.filter_blocks(blocks)
        
        # Annotate image with detected blocks
        for block in filtered_blocks:
            x, y, w, h = block['bbox']
            # Draw bounding box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Draw center point
            center = block['center']
            cv2.circle(annotated, center, 5, (0, 0, 255), -1)
            # Add label
            label = f"Block {block['id']}"
            cv2.putText(annotated, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add count to image
        count_text = f"Total Blocks: {len(filtered_blocks)}"
        cv2.putText(annotated, count_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return len(filtered_blocks), annotated, filtered_blocks
    
    def detect_from_bytes(self, image_bytes: bytes) -> Tuple[int, np.ndarray, List[Dict]]:
        """
        Detect and count blocks from image bytes (for web uploads).
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Tuple of (block_count, annotated_image, block_details)
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Could not decode image from bytes")
        
        # Store original for annotation
        annotated = image.copy()
        
        # Preprocess
        preprocessed = self.preprocess_image(image)
        
        # Detect edges
        edges = self.detect_edges(preprocessed)
        
        # Find blocks
        blocks = self.find_blocks(edges)
        
        # Filter blocks
        filtered_blocks = self.filter_blocks(blocks)
        
        # Annotate image with detected blocks
        for block in filtered_blocks:
            x, y, w, h = block['bbox']
            # Draw bounding box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Draw center point
            center = block['center']
            cv2.circle(annotated, center, 5, (0, 0, 255), -1)
            # Add label
            label = f"Block {block['id']}"
            cv2.putText(annotated, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add count to image
        count_text = f"Total Blocks: {len(filtered_blocks)}"
        cv2.putText(annotated, count_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return len(filtered_blocks), annotated, filtered_blocks


def create_detector() -> BlockDetector:
    """
    Factory function to create a BlockDetector with default settings.
    
    Returns:
        Configured BlockDetector instance
    """
    return BlockDetector(min_area=500, max_area=50000)

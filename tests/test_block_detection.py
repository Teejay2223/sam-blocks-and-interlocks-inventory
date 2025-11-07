"""
Tests for block detection functionality
"""

import pytest
import os
import sys
import tempfile
import numpy as np
from PIL import Image

# Add parent directory to path to import block_detector
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from block_detector import BlockDetector, allowed_file, preprocess_image


class TestBlockDetector:
    """Test cases for BlockDetector class"""
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        detector = BlockDetector(confidence_threshold=0.3)
        assert detector is not None
        assert detector.confidence_threshold == 0.3
        assert detector.model is not None
    
    def test_detector_with_custom_threshold(self):
        """Test detector with different confidence thresholds"""
        detector = BlockDetector(confidence_threshold=0.5)
        assert detector.confidence_threshold == 0.5
    
    def test_detect_blocks_with_invalid_image(self):
        """Test detection with invalid image path"""
        detector = BlockDetector()
        result = detector.detect_blocks("nonexistent_image.jpg")
        assert result['success'] is False
        assert result['count'] == 0
        assert 'Error' in result['message'] or 'error' in result['message'].lower()
    
    def test_detect_blocks_returns_correct_structure(self):
        """Test that detection returns the expected structure"""
        detector = BlockDetector()
        
        # Create a temporary test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Create a simple test image
            img = Image.new('RGB', (640, 480), color='white')
            img.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            result = detector.detect_blocks(tmp_path)
            
            # Check result structure
            assert 'count' in result
            assert 'detections' in result
            assert 'annotated_image' in result
            assert 'success' in result
            assert 'message' in result
            
            # Check types
            assert isinstance(result['count'], int)
            assert isinstance(result['detections'], list)
            assert isinstance(result['success'], bool)
            assert isinstance(result['message'], str)
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_detect_from_array(self):
        """Test detection from numpy array"""
        detector = BlockDetector()
        
        # Create a test image array
        img_array = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = detector.detect_from_array(img_array)
        
        # Check result structure
        assert 'count' in result
        assert 'detections' in result
        assert 'success' in result
        assert isinstance(result['count'], int)
        assert isinstance(result['detections'], list)
    
    def test_save_annotated_image(self):
        """Test saving annotated image"""
        detector = BlockDetector()
        
        # Create a simple test image array
        img_array = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Save the image
            success = detector.save_annotated_image(img_array, tmp_path)
            assert success is True
            assert os.path.exists(tmp_path)
            
            # Verify the image can be read
            saved_img = Image.open(tmp_path)
            assert saved_img is not None
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_save_annotated_image_with_none(self):
        """Test saving None image returns False"""
        detector = BlockDetector()
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            success = detector.save_annotated_image(None, tmp_path)
            assert success is False
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_allowed_file_with_valid_extensions(self):
        """Test allowed_file with valid extensions"""
        assert allowed_file('test.jpg') is True
        assert allowed_file('test.jpeg') is True
        assert allowed_file('test.png') is True
        assert allowed_file('test.gif') is True
        assert allowed_file('test.bmp') is True
        assert allowed_file('TEST.JPG') is True  # Test case insensitivity
    
    def test_allowed_file_with_invalid_extensions(self):
        """Test allowed_file with invalid extensions"""
        assert allowed_file('test.txt') is False
        assert allowed_file('test.pdf') is False
        assert allowed_file('test.py') is False
        assert allowed_file('test') is False
        assert allowed_file('test.') is False
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        # Create a temporary test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            img = Image.new('RGB', (640, 480), color='red')
            img.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Test preprocessing without resizing
            processed = preprocess_image(tmp_path)
            assert processed is not None
            assert processed.shape[0] == 480
            assert processed.shape[1] == 640
            assert processed.shape[2] == 3
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_preprocess_image_with_resize(self):
        """Test image preprocessing with resizing"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            img = Image.new('RGB', (640, 480), color='blue')
            img.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Test preprocessing with resizing
            processed = preprocess_image(tmp_path, target_size=(320, 240))
            assert processed is not None
            assert processed.shape[0] == 240
            assert processed.shape[1] == 320
            assert processed.shape[2] == 3
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_preprocess_image_invalid_path(self):
        """Test preprocessing with invalid image path"""
        with pytest.raises(ValueError):
            preprocess_image("nonexistent_image.jpg")


class TestDetectionEndToEnd:
    """End-to-end tests for detection pipeline"""
    
    def test_full_detection_pipeline(self):
        """Test the complete detection pipeline"""
        detector = BlockDetector(confidence_threshold=0.25)
        
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Create an image with some content
            img = Image.new('RGB', (640, 480), color='white')
            img.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Run detection
            result = detector.detect_blocks(tmp_path)
            
            # Validate results
            assert result['success'] is True
            assert isinstance(result['count'], int)
            assert result['count'] >= 0
            
            # Check detections
            for detection in result['detections']:
                assert 'bbox' in detection
                assert 'confidence' in detection
                assert 'class' in detection
                assert len(detection['bbox']) == 4
                assert 0 <= detection['confidence'] <= 1
            
            # Save annotated image
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as out_file:
                out_path = out_file.name
            
            if result['annotated_image'] is not None:
                saved = detector.save_annotated_image(result['annotated_image'], out_path)
                assert saved is True
                assert os.path.exists(out_path)
                os.unlink(out_path)
                
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

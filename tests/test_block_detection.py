"""
Test suite for block detection functionality
"""
import os
import io
import tempfile
import pytest
import cv2
import numpy as np
from block_detector import BlockDetector, create_detector
from app import app, init_db


def create_test_image_with_blocks(num_blocks=5):
    """Create a synthetic test image with rectangular blocks."""
    width, height = 800, 600
    img = np.ones((height, width, 3), dtype=np.uint8) * 240
    
    blocks = []
    for i in range(num_blocks):
        x = 50 + (i % 3) * 250
        y = 50 + (i // 3) * 250
        w = 100 + i * 10
        h = 80 + i * 8
        
        # Draw block
        color = (60 + i*20, 80, 100)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, -1)
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), 2)
        blocks.append((x, y, w, h))
    
    return img, blocks


class TestBlockDetector:
    """Test the BlockDetector class."""
    
    def test_detector_creation(self):
        """Test that detector can be created with default parameters."""
        detector = create_detector()
        assert detector is not None
        assert detector.min_area == 500
        assert detector.max_area == 50000
    
    def test_detector_custom_params(self):
        """Test detector creation with custom parameters."""
        detector = BlockDetector(min_area=1000, max_area=30000)
        assert detector.min_area == 1000
        assert detector.max_area == 30000
    
    def test_preprocess_image(self):
        """Test image preprocessing."""
        detector = create_detector()
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        preprocessed = detector.preprocess_image(img)
        
        # Should return grayscale image
        assert len(preprocessed.shape) == 2
        assert preprocessed.shape == (100, 100)
    
    def test_detect_edges(self):
        """Test edge detection."""
        detector = create_detector()
        gray = np.ones((100, 100), dtype=np.uint8) * 128
        # Add a rectangle
        cv2.rectangle(gray, (20, 20), (80, 80), 255, -1)
        
        edges = detector.detect_edges(gray)
        assert edges is not None
        assert edges.shape == gray.shape
    
    def test_detect_blocks_in_image(self):
        """Test block detection on synthetic image."""
        detector = create_detector()
        
        # Create test image
        img, expected_blocks = create_test_image_with_blocks(5)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = f.name
            cv2.imwrite(temp_path, img)
        
        try:
            # Detect blocks
            count, annotated, blocks = detector.detect_and_count(temp_path)
            
            # Should detect approximately the number of blocks we drew
            assert count > 0
            assert count <= len(expected_blocks) + 2  # Allow some tolerance
            assert annotated is not None
            assert len(blocks) == count
        finally:
            os.unlink(temp_path)
    
    def test_detect_from_bytes(self):
        """Test block detection from image bytes."""
        detector = create_detector()
        
        # Create test image
        img, _ = create_test_image_with_blocks(3)
        
        # Encode to bytes
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()
        
        # Detect blocks
        count, annotated, blocks = detector.detect_from_bytes(image_bytes)
        
        assert count > 0
        assert annotated is not None
        assert len(blocks) == count
    
    def test_filter_blocks(self):
        """Test block filtering logic."""
        detector = create_detector()
        
        # Create mock blocks with different properties
        blocks = [
            {'aspect_ratio': 0.5, 'circularity': 0.3, 'id': 0},  # Valid
            {'aspect_ratio': 5.0, 'circularity': 0.4, 'id': 1},  # Invalid aspect ratio
            {'aspect_ratio': 1.0, 'circularity': 0.1, 'id': 2},  # Invalid circularity
            {'aspect_ratio': 1.5, 'circularity': 0.5, 'id': 3},  # Valid
        ]
        
        filtered = detector.filter_blocks(blocks)
        
        # Should keep blocks 0 and 3
        assert len(filtered) == 2
        assert filtered[0]['id'] == 0
        assert filtered[1]['id'] == 3


@pytest.fixture
def client(tmp_path):
    """Create test client with temporary database."""
    db_fd, db_path = tempfile.mkstemp(dir=tmp_path)
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = str(tmp_path / 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        init_db()
    
    client = app.test_client()
    
    yield client
    
    os.close(db_fd)
    try:
        os.remove(db_path)
    except OSError:
        pass


class TestBlockDetectionRoutes:
    """Test Flask routes for block detection."""
    
    def test_detect_blocks_page_requires_login(self, client):
        """Test that detect_blocks page requires authentication."""
        rv = client.get('/detect_blocks')
        # Should redirect to login
        assert rv.status_code == 302
        assert '/login' in rv.location
    
    def test_detect_blocks_page_authenticated(self, client):
        """Test accessing detect_blocks page when logged in."""
        # Register and login
        client.post('/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        client.post('/login', data={
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Access page
        rv = client.get('/detect_blocks')
        assert rv.status_code == 200
        assert b'Block Detection' in rv.data
    
    def test_api_detect_blocks_requires_login(self, client):
        """Test that API endpoint requires authentication."""
        rv = client.post('/api/detect_blocks')
        # Should redirect to login or return 401
        assert rv.status_code in [302, 401]
    
    def test_upload_file_route(self, client):
        """Test file upload for block detection."""
        # Login first
        client.post('/register', data={
            'name': 'Test',
            'email': 'test@example.com',
            'password': 'pass'
        })
        client.post('/login', data={
            'username': 'test@example.com',
            'password': 'pass'
        })
        
        # Create test image
        img, _ = create_test_image_with_blocks(4)
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()
        
        # Upload image
        rv = client.post('/detect_blocks', data={
            'image': (io.BytesIO(image_bytes), 'test.jpg')
        }, content_type='multipart/form-data')
        
        # Should succeed or redirect
        assert rv.status_code in [200, 302]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

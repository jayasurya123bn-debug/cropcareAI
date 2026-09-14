"""
=================================================================
Prediction & Recommendation Unit Tests
=================================================================
"""
import io
import os
import tempfile
import pytest
import numpy as np
from PIL import Image


class TestImageProcessor:
    def test_validate_valid_jpeg(self, sample_image_bytes):
        from prediction.image_processor import validate_upload
        from werkzeug.datastructures import FileStorage
        fs = FileStorage(
            stream=io.BytesIO(sample_image_bytes),
            filename='leaf.jpg',
            content_type='image/jpeg',
        )
        result = validate_upload(fs)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_reject_invalid_extension(self):
        from prediction.image_processor import validate_upload, ImageValidationError
        from werkzeug.datastructures import FileStorage
        fs = FileStorage(
            stream=io.BytesIO(b'fake'),
            filename='malware.exe',
            content_type='application/octet-stream',
        )
        with pytest.raises(ImageValidationError):
            validate_upload(fs)

    def test_reject_empty_file(self):
        from prediction.image_processor import validate_upload, ImageValidationError
        from werkzeug.datastructures import FileStorage
        fs = FileStorage(stream=io.BytesIO(b''), filename='leaf.jpg')
        with pytest.raises(ImageValidationError):
            validate_upload(fs)

    def test_reject_oversized_file(self, sample_image_bytes):
        from prediction.image_processor import validate_upload, ImageValidationError
        from werkzeug.datastructures import FileStorage
        large = sample_image_bytes * 600  # well over 5 MB
        fs = FileStorage(stream=io.BytesIO(large), filename='big.jpg')
        with pytest.raises(ImageValidationError):
            validate_upload(fs, max_size=100)

    def test_preprocess_returns_correct_shape(self, sample_image_bytes):
        from prediction.image_processor import preprocess_from_bytes
        arr = preprocess_from_bytes(sample_image_bytes)
        assert arr.shape == (1, 224, 224, 3)
        assert arr.dtype == np.float32
        assert arr.min() >= 0.0
        assert arr.max() <= 1.0

    def test_save_upload(self, sample_image_bytes):
        from prediction.image_processor import save_upload
        with tempfile.TemporaryDirectory() as tmpdir:
            fname = save_upload(sample_image_bytes, 'leaf.jpg', tmpdir)
            assert fname.endswith('.jpg')
            assert os.path.exists(os.path.join(tmpdir, fname))


class TestPredictor:
    def test_demo_result_structure(self):
        """When no model is loaded, demo result should have expected keys."""
        from prediction.predictor import _demo_result
        result = _demo_result('en')
        required_keys = [
            'crop', 'disease', 'class_key', 'class_index',
            'confidence', 'confidence_pct', 'confidence_level',
            'is_healthy', 'status', 'demo_mode',
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_demo_result_tamil(self):
        from prediction.predictor import _demo_result
        result = _demo_result('ta')
        assert result['demo_mode'] is True

    def test_classify_confidence_high(self):
        from prediction.predictor import classify_confidence
        assert classify_confidence(0.95) == 'high'
        assert classify_confidence(0.80) == 'high'

    def test_classify_confidence_medium(self):
        from prediction.predictor import classify_confidence
        assert classify_confidence(0.65) == 'medium'
        assert classify_confidence(0.50) == 'medium'

    def test_classify_confidence_low(self):
        from prediction.predictor import classify_confidence
        assert classify_confidence(0.49) == 'low'
        assert classify_confidence(0.10) == 'low'

    def test_parse_class_name_disease(self):
        from prediction.predictor import parse_class_name
        result = parse_class_name('Tomato___Early_blight')
        assert result['crop'] == 'Tomato'
        assert result['disease'] == 'Early blight'
        assert result['is_healthy'] is False

    def test_parse_class_name_healthy(self):
        from prediction.predictor import parse_class_name
        result = parse_class_name('Apple___healthy')
        assert result['is_healthy'] is True

    def test_predict_without_model(self):
        """predict() should return demo result when model not loaded."""
        from prediction.predictor import predict
        dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
        result = predict(dummy, lang='en')
        assert 'crop' in result
        assert 'confidence' in result
        assert isinstance(result['confidence'], float)

    def test_confidence_message_en(self):
        from prediction.predictor import confidence_message
        msg = confidence_message('high', 'en')
        assert 'high confidence' in msg.lower()

    def test_confidence_message_ta(self):
        from prediction.predictor import confidence_message
        msg = confidence_message('high', 'ta')
        assert len(msg) > 0


class TestRecommendationEngine:
    def test_load_returns_data(self):
        from recommendations.recommendation_engine import get_all_class_keys
        keys = get_all_class_keys()
        assert len(keys) > 0

    def test_get_recommendations_tomato_blight_en(self):
        from recommendations.recommendation_engine import get_recommendations
        rec = get_recommendations('Tomato___Early_blight', lang='en')
        assert rec is not None
        assert rec['crop'] == 'Tomato'
        assert len(rec['symptoms']) > 0
        assert len(rec['prevention']) > 0
        assert len(rec['management']) > 0

    def test_get_recommendations_tamil(self):
        from recommendations.recommendation_engine import get_recommendations
        rec = get_recommendations('Tomato___Early_blight', lang='ta')
        assert rec is not None
        # Tamil content should be different from English
        assert len(rec['symptoms']) > 0

    def test_get_recommendations_healthy(self):
        from recommendations.recommendation_engine import get_recommendations
        rec = get_recommendations('Apple___healthy', lang='en')
        assert rec is not None
        assert rec['is_healthy'] is True

    def test_get_recommendations_unknown_class(self):
        from recommendations.recommendation_engine import get_recommendations
        rec = get_recommendations('Unknown___Unknown_disease', lang='en')
        assert rec is None

    def test_list_all_diseases(self):
        from recommendations.recommendation_engine import list_all_diseases
        diseases = list_all_diseases('en')
        assert len(diseases) >= 10
        for d in diseases:
            assert 'class_key' in d
            assert 'disease_name' in d

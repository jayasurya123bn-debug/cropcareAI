"""
=================================================================
API Endpoint Tests
=================================================================
"""
import io
import json
import pytest


class TestAPIStatus:
    def test_status_returns_200(self, client):
        r = client.get('/api/status')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['success'] is True
        assert 'model_loaded' in data

    def test_status_has_version(self, client):
        r = client.get('/api/status')
        data = json.loads(r.data)
        assert 'version' in data


class TestAPIPredict:
    def test_predict_no_file(self, client):
        r = client.post('/api/predict')
        assert r.status_code == 400
        data = json.loads(r.data)
        assert data['success'] is False

    def test_predict_valid_image(self, client, sample_image_bytes):
        data = {'leaf_image': (io.BytesIO(sample_image_bytes), 'leaf.jpg', 'image/jpeg')}
        r = client.post('/api/predict', data=data, content_type='multipart/form-data')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result['success'] is True
        assert 'crop' in result
        assert 'disease' in result
        assert 'confidence' in result
        assert 'recommendations' in result

    def test_predict_returns_recommendations(self, client, sample_image_bytes):
        data = {'leaf_image': (io.BytesIO(sample_image_bytes), 'leaf.jpg', 'image/jpeg')}
        r = client.post('/api/predict', data=data, content_type='multipart/form-data')
        result = json.loads(r.data)
        assert 'recommendations' in result
        rec = result['recommendations']
        assert 'symptoms' in rec
        assert 'prevention' in rec
        assert 'management' in rec

    def test_predict_invalid_extension(self, client):
        data = {'leaf_image': (io.BytesIO(b'fake'), 'malware.exe', 'application/octet-stream')}
        r = client.post('/api/predict', data=data, content_type='multipart/form-data')
        assert r.status_code == 422
        result = json.loads(r.data)
        assert result['success'] is False

    def test_predict_with_lang_ta(self, client, sample_image_bytes):
        data = {
            'leaf_image': (io.BytesIO(sample_image_bytes), 'leaf.jpg', 'image/jpeg'),
            'lang': 'ta',
        }
        r = client.post('/api/predict', data=data, content_type='multipart/form-data')
        assert r.status_code == 200


class TestAPIDisease:
    def test_get_known_disease(self, client):
        r = client.get('/api/disease/Tomato___Early_blight')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['success'] is True
        assert 'disease' in data

    def test_get_unknown_disease(self, client):
        r = client.get('/api/disease/Unknown___Unknown_disease')
        assert r.status_code == 404

    def test_get_disease_tamil(self, client):
        r = client.get('/api/disease/Tomato___Early_blight?lang=ta')
        assert r.status_code == 200


class TestAPIAuth:
    def test_register_json(self, client):
        r = client.post('/api/register',
                        json={'name': 'API User', 'email': 'apiuser@test.com', 'password': 'pass12345'})
        assert r.status_code == 201
        data = json.loads(r.data)
        assert data['success'] is True

    def test_register_duplicate(self, client, test_user):
        r = client.post('/api/register',
                        json={'name': 'Dup', 'email': test_user.email, 'password': 'pass12345'})
        assert r.status_code == 409

    def test_register_short_password(self, client):
        r = client.post('/api/register',
                        json={'name': 'X', 'email': 'x@x.com', 'password': 'abc'})
        assert r.status_code == 400

    def test_login_valid(self, client, test_user):
        r = client.post('/api/login',
                        json={'email': test_user.email, 'password': 'testpass123'})
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['success'] is True

    def test_login_invalid(self, client, test_user):
        r = client.post('/api/login',
                        json={'email': test_user.email, 'password': 'wrongpass'})
        assert r.status_code == 401


class TestAPIHistory:
    def test_history_requires_auth(self, client):
        r = client.get('/api/history')
        assert r.status_code == 401

    def test_history_accessible_when_logged_in(self, logged_in_client):
        r = logged_in_client.get('/api/history')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['success'] is True
        assert 'predictions' in data


class TestAPIDashboard:
    def test_dashboard_requires_auth(self, client):
        r = client.get('/api/dashboard')
        assert r.status_code == 401

    def test_dashboard_returns_stats(self, logged_in_client):
        r = logged_in_client.get('/api/dashboard')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['success'] is True
        assert 'total_scans' in data
        assert 'avg_confidence' in data

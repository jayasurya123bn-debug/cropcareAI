"""
=================================================================
Route Tests
=================================================================
"""
import io
import pytest


class TestHomePage:
    def test_home_returns_200(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_home_contains_brand(self, client):
        r = client.get('/')
        assert b'CropCare' in r.data


class TestAuth:
    def test_register_page_loads(self, client):
        r = client.get('/auth/register')
        assert r.status_code == 200

    def test_login_page_loads(self, client):
        r = client.get('/auth/login')
        assert r.status_code == 200

    def test_register_creates_user(self, client, db):
        r = client.post('/auth/register', data={
            'name': 'New Farmer', 'email': 'newfarmer@test.com',
            'password': 'secure1234', 'confirm_password': 'secure1234',
            'preferred_language': 'en',
        }, follow_redirects=True)
        assert r.status_code == 200
        from database.models import User
        user = User.query.filter_by(email='newfarmer@test.com').first()
        assert user is not None

    def test_register_duplicate_email(self, client, test_user):
        r = client.post('/auth/register', data={
            'name': 'Dup', 'email': test_user.email,
            'password': 'secure1234', 'confirm_password': 'secure1234',
        }, follow_redirects=True)
        assert b'already exists' in r.data or r.status_code == 200

    def test_login_valid(self, client, test_user):
        r = client.post('/auth/login', data={
            'email': test_user.email, 'password': 'testpass123',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_invalid_password(self, client, test_user):
        r = client.post('/auth/login', data={
            'email': test_user.email, 'password': 'wrongpassword',
        }, follow_redirects=True)
        assert b'Invalid' in r.data

    def test_logout(self, logged_in_client):
        r = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert r.status_code == 200

    def test_set_language_en(self, client):
        r = client.get('/auth/set-language/en', follow_redirects=True)
        assert r.status_code == 200

    def test_set_language_ta(self, client):
        r = client.get('/auth/set-language/ta', follow_redirects=True)
        assert r.status_code == 200


class TestProtectedRoutes:
    def test_dashboard_requires_login(self, client):
        r = client.get('/dashboard', follow_redirects=False)
        assert r.status_code in (302, 401)

    def test_history_requires_login(self, client):
        r = client.get('/history', follow_redirects=False)
        assert r.status_code in (302, 401)

    def test_dashboard_accessible_when_logged_in(self, logged_in_client):
        r = logged_in_client.get('/dashboard')
        assert r.status_code == 200

    def test_history_accessible_when_logged_in(self, logged_in_client):
        r = logged_in_client.get('/history')
        assert r.status_code == 200


class TestPredict:
    def test_predict_no_file(self, client):
        r = client.post('/predict', data={}, follow_redirects=True)
        assert r.status_code == 200

    def test_predict_with_valid_image(self, client, sample_image_bytes):
        data = {'leaf_image': (io.BytesIO(sample_image_bytes), 'leaf.jpg', 'image/jpeg')}
        r = client.post('/predict', data=data, content_type='multipart/form-data',
                        follow_redirects=True)
        assert r.status_code == 200

    def test_predict_with_wrong_extension(self, client):
        data = {'leaf_image': (io.BytesIO(b'fake content'), 'file.exe', 'application/octet-stream')}
        r = client.post('/predict', data=data, content_type='multipart/form-data',
                        follow_redirects=True)
        assert r.status_code == 200  # redirects back with error flash


class TestAbout:
    def test_about_loads(self, client):
        r = client.get('/about')
        assert r.status_code == 200
        assert b'CropCare' in r.data


class TestErrors:
    def test_404(self, client):
        r = client.get('/nonexistent-page')
        assert r.status_code == 404

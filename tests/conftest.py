"""
=================================================================
Test Fixtures — Pytest conftest.py
=================================================================
"""
import io
import os
import pytest
from PIL import Image

os.environ['DATABASE_URL']   = 'sqlite:///:memory:'
os.environ['SECRET_KEY']     = 'test-secret-key'
os.environ['UPLOAD_FOLDER']  = 'static/uploads'
os.environ['MODEL_PATH']     = 'models/crop_disease_model.keras'
os.environ['CLASS_NAMES_PATH'] = 'models/class_names.json'

from app import create_app
from database.database import db as _db


@pytest.fixture(scope='session')
def app():
    """Create a test Flask application."""
    _app = create_app()
    _app.config.update({
        'TESTING'             : True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED'    : False,
        'SECRET_KEY'          : 'test-secret-key',
    })
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def db(app):
    """Database session."""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    from database.models import User
    from werkzeug.security import generate_password_hash
    user = User(
        name='Test Farmer', email='test@cropcare.ai',
        password_hash=generate_password_hash('testpass123'),
        preferred_language='en', role='user',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_admin(db):
    """Create a test admin user."""
    from database.models import User
    from werkzeug.security import generate_password_hash
    admin = User(
        name='Admin User', email='admin2@cropcare.ai',
        password_hash=generate_password_hash('adminpass123'),
        preferred_language='en', role='admin',
    )
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def sample_image_bytes():
    """Generate a valid 224x224 RGB JPEG image as bytes."""
    img = Image.new('RGB', (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf.read()


@pytest.fixture
def logged_in_client(client, test_user):
    """Client with a logged-in session."""
    client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'testpass123',
    }, follow_redirects=True)
    return client

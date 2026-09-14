"""
=================================================================
Database Setup — SQLAlchemy + Flask-SQLAlchemy
=================================================================
Supports:
  SQLite (default, zero-config)
  MySQL (via DATABASE_URL env var)
=================================================================
"""

import os
import logging
from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger(__name__)

# Shared db instance — imported by models and routes
db = SQLAlchemy()


def init_db(app):
    """
    Create all tables and seed the admin user on first run.
    Called from app.py inside app_context.
    """
    db.create_all()
    _seed_admin(app)
    log.info("Database initialised.")


def _seed_admin(app):
    """Create a default admin account if none exists."""
    from database.models import User
    from werkzeug.security import generate_password_hash

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@cropcare.ai')
    admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123')

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return

    admin = User(
        name             = 'Admin',
        email            = admin_email,
        password_hash    = generate_password_hash(admin_password),
        preferred_language = 'en',
        role             = 'admin',
    )
    db.session.add(admin)
    db.session.commit()
    log.info(f"Default admin account created: {admin_email}")

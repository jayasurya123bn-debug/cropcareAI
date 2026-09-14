"""
=================================================================
Database Models — SQLAlchemy ORM
=================================================================
Models:
  User        — authentication, roles, language preference
  Prediction  — stores each scan result
=================================================================
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db


class User(UserMixin, db.Model):
    """Application user (farmer or admin)."""
    __tablename__ = 'users'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String(120), nullable=False)
    email               = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash       = db.Column(db.String(256), nullable=False)
    preferred_language  = db.Column(db.String(4), nullable=False, default='en')
    role                = db.Column(db.String(16), nullable=False, default='user')   # 'user' | 'admin'
    created_at          = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to predictions
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def to_dict(self) -> dict:
        return {
            'id'                : self.id,
            'name'              : self.name,
            'email'             : self.email,
            'preferred_language': self.preferred_language,
            'role'              : self.role,
            'created_at'        : self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'


class Prediction(db.Model):
    """Stores each crop disease prediction scan."""
    __tablename__ = 'predictions'

    id                 = db.Column(db.Integer, primary_key=True)
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    image_filename     = db.Column(db.String(256), nullable=False)
    original_filename  = db.Column(db.String(256), nullable=True)
    gradcam_filename   = db.Column(db.String(256), nullable=True)
    crop               = db.Column(db.String(80), nullable=False)
    disease            = db.Column(db.String(120), nullable=False)
    class_key          = db.Column(db.String(150), nullable=True)
    confidence         = db.Column(db.Float, nullable=False)
    confidence_level   = db.Column(db.String(16), nullable=True)   # high | medium | low
    is_healthy         = db.Column(db.Boolean, default=False)
    status             = db.Column(db.String(32), nullable=True)    # disease_detected | healthy | low_confidence
    language           = db.Column(db.String(4), default='en')
    demo_mode          = db.Column(db.Boolean, default=False)
    created_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def confidence_pct(self) -> float:
        return round(self.confidence * 100, 2)

    def to_dict(self) -> dict:
        return {
            'id'                : self.id,
            'user_id'           : self.user_id,
            'image_filename'    : self.image_filename,
            'original_filename' : self.original_filename,
            'gradcam_filename'  : self.gradcam_filename,
            'crop'              : self.crop,
            'disease'           : self.disease,
            'class_key'         : self.class_key,
            'confidence'        : self.confidence,
            'confidence_pct'    : self.confidence_pct(),
            'confidence_level'  : self.confidence_level,
            'is_healthy'        : self.is_healthy,
            'status'            : self.status,
            'language'          : self.language,
            'demo_mode'         : self.demo_mode,
            'created_at'        : self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Prediction {self.id}: {self.crop}/{self.disease} {self.confidence:.2f}>'

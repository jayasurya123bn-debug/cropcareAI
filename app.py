"""
=================================================================
CropCare AI — Main Flask Application
AI-Based Crop Disease Detection & Smart Recommendation System
=================================================================
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ── Core Config ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')

    is_vercel = bool(os.getenv('VERCEL'))
    if is_vercel:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/cropcare.db'
        app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    else:
        db_url = os.getenv('DATABASE_URL', 'sqlite:///cropcare.db')
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join('static', 'uploads'))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5 MB
    app.config['MODEL_PATH'] = os.getenv('MODEL_PATH', os.path.join('models', 'crop_disease_model.keras'))
    app.config['CLASS_NAMES_PATH'] = os.getenv('CLASS_NAMES_PATH', os.path.join('models', 'class_names.json'))
    app.config['CONFIDENCE_HIGH'] = float(os.getenv('CONFIDENCE_HIGH', 0.80))
    app.config['CONFIDENCE_MEDIUM'] = float(os.getenv('CONFIDENCE_MEDIUM', 0.50))
    app.config['DEFAULT_LANGUAGE'] = os.getenv('DEFAULT_LANGUAGE', 'en')

    # ── Ensure required directories exist ─────────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if not is_vercel:
        os.makedirs('models', exist_ok=True)
        os.makedirs('results', exist_ok=True)

    # ── Database ───────────────────────────────────────────────────────────
    from database.database import db, init_db
    db.init_app(app)

    # ── Flask-Login ────────────────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from database.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Register Blueprints ────────────────────────────────────────────────
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ── Error Handlers ─────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('errors/413.html'), 413

    # ── Context Processors ─────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        lang = session.get('lang', app.config['DEFAULT_LANGUAGE'])
        return dict(current_lang=lang)

    # ── Initialise DB & Seed Admin ─────────────────────────────────────────
    with app.app_context():
        init_db(app)

    # ── Logging ────────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    return app


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)

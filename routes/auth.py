"""
=================================================================
Authentication Routes — Register / Login / Logout
=================================================================
"""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from database.database import db
from database.models import User

auth_bp = Blueprint('auth', __name__)


# ── Register ───────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    lang = session.get('lang', current_app.config['DEFAULT_LANGUAGE'])

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        pref_lang = request.form.get('preferred_language', 'en')

        # ── Validation ────────────────────────────────────────────────────
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', lang=lang)

        # ── Create user ───────────────────────────────────────────────────
        user = User(
            name               = name,
            email              = email,
            password_hash      = generate_password_hash(password),
            preferred_language = pref_lang,
            role               = 'user',
        )
        db.session.add(user)
        db.session.commit()

        session['lang'] = pref_lang
        login_user(user)
        flash('Account created successfully! Welcome to CropCare AI.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html', lang=lang)


# ── Login ──────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    lang = session.get('lang', current_app.config['DEFAULT_LANGUAGE'])

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember_me') == 'on'

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', lang=lang)

        login_user(user, remember=remember)
        session['lang'] = user.preferred_language

        next_page = request.args.get('next')
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(next_page or url_for('main.index'))

    return render_template('login.html', lang=lang)


# ── Logout ─────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ── Language Switcher ──────────────────────────────────────────────────────

@auth_bp.route('/set-language/<lang>')
def set_language(lang: str):
    """Store language preference in session (and user profile if logged in)."""
    if lang in ('en', 'ta'):
        session['lang'] = lang
        if current_user.is_authenticated:
            current_user.preferred_language = lang
            db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

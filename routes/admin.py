"""
=================================================================
Admin Routes — Admin Panel
=================================================================
Requires: logged-in user with role == 'admin'
=================================================================
"""

import logging
from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort)
from flask_login import current_user, login_required

from database.database import db
from database.models import User, Prediction

log = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)


# ---------------------------------------------------------------------------
# Admin Guard
# ---------------------------------------------------------------------------

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_users   = User.query.count()
    total_preds   = Prediction.query.count()
    total_disease = Prediction.query.filter_by(is_healthy=False).count()
    total_healthy = Prediction.query.filter_by(is_healthy=True).count()

    recent_preds = Prediction.query.order_by(Prediction.created_at.desc()).limit(20).all()

    from collections import Counter
    all_preds = Prediction.query.all()
    top_diseases = Counter(p.disease for p in all_preds if not p.is_healthy).most_common(10)

    return render_template(
        'admin/index.html',
        total_users   = total_users,
        total_preds   = total_preds,
        total_disease = total_disease,
        total_healthy = total_healthy,
        recent_preds  = recent_preds,
        top_diseases  = top_diseases,
    )


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id: int):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete admin accounts.", 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.email} deleted.", 'success')
    return redirect(url_for('admin.users'))


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

@admin_bp.route('/predictions')
@login_required
@admin_required
def predictions():
    page  = request.args.get('page', 1, type=int)
    preds = Prediction.query.order_by(Prediction.created_at.desc())\
                             .paginate(page=page, per_page=25, error_out=False)
    return render_template('admin/predictions.html', preds=preds)


# ---------------------------------------------------------------------------
# Disease Editor (stub — reads from disease_data.json)
# ---------------------------------------------------------------------------

@admin_bp.route('/diseases')
@login_required
@admin_required
def disease_editor():
    import json
    from pathlib import Path
    data_path = Path('recommendations/disease_data.json')
    diseases = []
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            diseases = json.load(f)
    return render_template('admin/disease_editor.html', diseases=diseases)

"""
=================================================================
Main Routes — Home, Predict, Result, Dashboard, History, About
=================================================================
"""

import os
import logging
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session, current_app, abort)
from flask_login import current_user, login_required

from database.database import db
from database.models import Prediction, User
from prediction.image_processor import process_upload, ImageValidationError
from prediction.predictor import predict, generate_gradcam, is_model_loaded
from recommendations.recommendation_engine import get_recommendations

log = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_lang():
    return session.get('lang', current_app.config['DEFAULT_LANGUAGE'])


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@main_bp.route('/')
def index():
    return render_template('index.html', lang=get_lang(),
                           model_ready=is_model_loaded())


# ---------------------------------------------------------------------------
# Predict (POST — form upload)
# ---------------------------------------------------------------------------

@main_bp.route('/predict', methods=['POST'])
def predict_route():
    lang   = get_lang()
    upload_folder = current_app.config['UPLOAD_FOLDER']

    # ── Validate & save upload ────────────────────────────────────────────
    file = request.files.get('leaf_image')
    try:
        filename, img_array = process_upload(
            file, upload_folder,
            max_size=current_app.config['MAX_CONTENT_LENGTH']
        )
    except ImageValidationError as e:
        flash(str(e), 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        log.error(f"Upload error: {e}")
        flash('An unexpected error occurred while processing your image.', 'danger')
        return redirect(url_for('main.index'))

    # ── Run prediction ────────────────────────────────────────────────────
    result = predict(img_array, lang=lang)

    # ── Grad-CAM ──────────────────────────────────────────────────────────
    gradcam_filename = None
    image_path = os.path.join(upload_folder, filename)
    gradcam_path = os.path.join(upload_folder, f"gradcam_{filename}")

    gc = generate_gradcam(image_path, result['class_index'], gradcam_path)
    if gc:
        gradcam_filename = f"gradcam_{filename}"

    # ── Recommendations ───────────────────────────────────────────────────
    recommendations = get_recommendations(
        result['class_key'],
        crop=result['crop'],
        disease=result['disease'],
        is_healthy=result['is_healthy'],
        lang=lang
    )

    # ── Save to database ──────────────────────────────────────────────────
    pred = Prediction(
        user_id          = current_user.id if current_user.is_authenticated else None,
        image_filename   = filename,
        gradcam_filename = gradcam_filename,
        crop             = result['crop'],
        disease          = result['disease'],
        class_key        = result['class_key'],
        confidence       = result['confidence'],
        confidence_level = result['confidence_level'],
        is_healthy       = result['is_healthy'],
        status           = result['status'],
        language         = lang,
        demo_mode        = result.get('demo_mode', False),
    )
    db.session.add(pred)
    db.session.commit()

    # POST/Redirect/GET: redirect to the GET result page so that
    # language toggles, refreshes, and back-navigation all work correctly.
    return redirect(url_for('main.result', pred_id=pred.id))


# ---------------------------------------------------------------------------
# Result (GET by ID — view saved prediction)
# ---------------------------------------------------------------------------

@main_bp.route('/result/<int:pred_id>')
def result(pred_id: int):
    pred = Prediction.query.get_or_404(pred_id)
    lang = get_lang()

    from prediction.predictor import confidence_message

    conf_level = pred.confidence_level or 'high'
    result = {
        'crop'              : pred.crop,
        'disease'           : pred.disease,
        'class_key'         : pred.class_key,
        'confidence'        : pred.confidence,
        'confidence_pct'    : pred.confidence_pct(),
        'confidence_level'  : conf_level,
        'is_healthy'        : pred.is_healthy,
        'status'            : pred.status,
        'demo_mode'         : pred.demo_mode,
        'confidence_message': confidence_message(conf_level, lang=lang),
    }

    recommendations = get_recommendations(
        pred.class_key or '',
        crop=pred.crop,
        disease=pred.disease,
        is_healthy=pred.is_healthy,
        lang=lang
    )

    return render_template(
        'result.html',
        lang            = lang,
        result          = result,
        recommendations = recommendations,
        prediction_id   = pred.id,
        image_filename  = pred.image_filename,
        gradcam_filename= pred.gradcam_filename,
    )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@main_bp.route('/dashboard')
@login_required
def dashboard():
    lang = get_lang()
    user_preds = Prediction.query.filter_by(user_id=current_user.id)\
                                  .order_by(Prediction.created_at.desc())\
                                  .all()

    total_scans    = len(user_preds)
    healthy_count  = sum(1 for p in user_preds if p.is_healthy)
    disease_count  = total_scans - healthy_count
    avg_confidence = (sum(p.confidence for p in user_preds) / total_scans * 100
                      if total_scans > 0 else 0)

    recent = user_preds[:10]

    # Chart data (last 30 predictions, chronological)
    chart_data = [{'date': p.created_at.strftime('%d %b') if p.created_at else '',
                   'confidence': round(p.confidence * 100, 1)}
                  for p in reversed(user_preds[:30])]

    # Disease frequency
    from collections import Counter
    disease_freq = Counter(p.disease for p in user_preds if not p.is_healthy)
    top_diseases = disease_freq.most_common(5)

    return render_template(
        'dashboard.html',
        lang           = lang,
        total_scans    = total_scans,
        healthy_count  = healthy_count,
        disease_count  = disease_count,
        avg_confidence = round(avg_confidence, 1),
        recent         = recent,
        chart_data     = chart_data,
        top_diseases   = top_diseases,
    )


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

@main_bp.route('/history')
@login_required
def history():
    lang = get_lang()
    page = request.args.get('page', 1, type=int)
    per_page = 15

    preds = Prediction.query.filter_by(user_id=current_user.id)\
                             .order_by(Prediction.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('history.html', lang=lang, preds=preds)


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

@main_bp.route('/about')
def about():
    return render_template('about.html', lang=get_lang())

"""
=================================================================
REST API Routes
=================================================================
POST  /api/predict
GET   /api/history
GET   /api/disease/<class_key>
POST  /api/register
POST  /api/login
GET   /api/dashboard
=================================================================
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app, session
from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash

from database.database import db
from database.models import User, Prediction
from prediction.image_processor import process_upload, ImageValidationError
from prediction.predictor import predict, generate_gradcam, is_model_loaded
from recommendations.recommendation_engine import get_recommendations

log = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)


def success(data: dict, code: int = 200):
    return jsonify({'success': True, **data}), code


def error(message: str, code: int = 400):
    return jsonify({'success': False, 'error': message}), code


# ---------------------------------------------------------------------------
# POST /api/predict
# ---------------------------------------------------------------------------

@api_bp.route('/predict', methods=['POST'])
def api_predict():
    lang          = request.form.get('lang', 'en')
    upload_folder = current_app.config['UPLOAD_FOLDER']

    file = request.files.get('leaf_image')
    original_filename = file.filename if file else None
    if not file:
        return error('No image file uploaded. Use field name: leaf_image', 400)

    try:
        filename, img_array = process_upload(
            file, upload_folder,
            max_size=current_app.config['MAX_CONTENT_LENGTH']
        )
    except ImageValidationError as e:
        return error(str(e), 422)
    except Exception as e:
        log.error(f"API predict error: {e}")
        return error('Image processing failed.', 500)

    result = predict(img_array, lang=lang)

    # Grad-CAM
    image_path = os.path.join(upload_folder, filename)
    gradcam_path = os.path.join(upload_folder, f"gradcam_{filename}")
    gc = generate_gradcam(image_path, result['class_index'], gradcam_path)
    gradcam_filename = f"gradcam_{filename}" if gc else None

    # Recommendations
    recommendations = get_recommendations(result['class_key'], lang=lang) or {}

    # Save prediction
    pred = Prediction(
        user_id            = current_user.id if current_user.is_authenticated else None,
        image_filename     = filename,
        original_filename  = original_filename,
        gradcam_filename   = gradcam_filename,
        crop               = result['crop'],
        disease            = result['disease'],
        class_key          = result['class_key'],
        confidence         = result['confidence'],
        confidence_level   = result['confidence_level'],
        is_healthy         = result['is_healthy'],
        status             = result['status'],
        language           = lang,
        demo_mode          = result.get('demo_mode', False),
    )
    db.session.add(pred)
    db.session.commit()

    return success({
        'prediction_id'   : pred.id,
        'crop'            : result['crop'],
        'disease'         : result['disease'],
        'class_key'       : result['class_key'],
        'confidence'      : result['confidence_pct'],
        'confidence_raw'  : result['confidence'],
        'confidence_level': result['confidence_level'],
        'is_healthy'      : result['is_healthy'],
        'status'          : result['status'],
        'demo_mode'       : result.get('demo_mode', False),
        'recommendations' : {
            'crop'                  : recommendations.get('crop'),
            'botanical_name'        : recommendations.get('botanical_name'),
            'disease_name'          : recommendations.get('disease_name'),
            'is_healthy'            : recommendations.get('is_healthy'),
            'pathogen_type'         : recommendations.get('pathogen_type'),
            'causal_agent'          : recommendations.get('causal_agent'),
            'severity'              : recommendations.get('severity'),
            'spread_risk'           : recommendations.get('spread_risk'),
            'symptoms'              : recommendations.get('symptoms', []),
            'prevention'            : recommendations.get('prevention', []),
            'management'            : recommendations.get('management', []),
            'monitoring'            : recommendations.get('monitoring', []),
            'environmental_triggers': recommendations.get('environmental_triggers'),
            'immediate_action'      : recommendations.get('immediate_action'),
            'steps'                 : recommendations.get('steps', []),
        },
        'image_url'       : f'/static/uploads/{filename}',
        'original_filename': original_filename,
        'gradcam_url'     : f'/static/uploads/{gradcam_filename}' if gradcam_filename else None,
    })


# ---------------------------------------------------------------------------
# GET /api/history
# ---------------------------------------------------------------------------

@api_bp.route('/history', methods=['GET'])
def api_history():
    if not current_user.is_authenticated:
        return error('Authentication required.', 401)

    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    preds = Prediction.query.filter_by(user_id=current_user.id)\
                             .order_by(Prediction.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)

    return success({
        'predictions' : [p.to_dict() for p in preds.items],
        'total'       : preds.total,
        'pages'       : preds.pages,
        'current_page': preds.page,
    })


# ---------------------------------------------------------------------------
# GET /api/disease/<class_key>
# ---------------------------------------------------------------------------

@api_bp.route('/disease/<path:class_key>', methods=['GET'])
def api_disease(class_key: str):
    lang = request.args.get('lang', 'en')
    rec  = get_recommendations(class_key, lang=lang)
    if not rec:
        return error(f"Disease '{class_key}' not found in database.", 404)
    return success({'disease': rec})


# ---------------------------------------------------------------------------
# POST /api/register
# ---------------------------------------------------------------------------

@api_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or request.form

    name      = str(data.get('name', '')).strip()
    email     = str(data.get('email', '')).strip().lower()
    password  = str(data.get('password', ''))
    pref_lang = str(data.get('preferred_language', 'en'))

    if not name or not email or not password:
        return error('name, email, and password are required.', 400)
    if '@' not in email:
        return error('Invalid email address.', 400)
    if len(password) < 8:
        return error('Password must be at least 8 characters.', 400)
    if User.query.filter_by(email=email).first():
        return error('Email already registered.', 409)

    user = User(
        name               = name,
        email              = email,
        password_hash      = generate_password_hash(password),
        preferred_language = pref_lang,
        role               = 'user',
    )
    db.session.add(user)
    db.session.commit()

    return success({'message': 'Account created.', 'user_id': user.id}, 201)


# ---------------------------------------------------------------------------
# POST /api/login
# ---------------------------------------------------------------------------

@api_bp.route('/login', methods=['POST'])
def api_login():
    data     = request.get_json(silent=True) or request.form
    email    = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error('Invalid email or password.', 401)

    login_user(user)
    return success({'message': 'Login successful.', 'user': user.to_dict()})


# ---------------------------------------------------------------------------
# GET /api/dashboard
# ---------------------------------------------------------------------------

@api_bp.route('/dashboard', methods=['GET'])
def api_dashboard():
    if not current_user.is_authenticated:
        return error('Authentication required.', 401)

    preds = Prediction.query.filter_by(user_id=current_user.id).all()
    total      = len(preds)
    healthy    = sum(1 for p in preds if p.is_healthy)
    diseases   = total - healthy
    avg_conf   = (sum(p.confidence for p in preds) / total * 100) if total else 0

    from collections import Counter
    top = Counter(p.disease for p in preds if not p.is_healthy).most_common(5)

    return success({
        'total_scans'     : total,
        'healthy_count'   : healthy,
        'disease_count'   : diseases,
        'avg_confidence'  : round(avg_conf, 2),
        'top_diseases'    : [{'disease': d, 'count': c} for d, c in top],
    })


# ---------------------------------------------------------------------------
# GET /api/status
# ---------------------------------------------------------------------------

@api_bp.route('/status', methods=['GET'])
def api_status():
    return success({
        'model_loaded': is_model_loaded(),
        'version'     : '1.0.0',
        'app'         : 'CropCare AI',
    })

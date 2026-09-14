"""
=================================================================
Predictor — Disease Detection via Gemini API
=================================================================
Uses Google Gemini API for real-time plant disease detection,
bypassing the need for a local 2.3 GB dataset and CNN training.
=================================================================
"""

import os
import io
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image
from google import genai
from google.genai import types

log = logging.getLogger(__name__)

# Configure Gemini client
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
_client: Optional[genai.Client] = None

if GEMINI_API_KEY:
    _client = genai.Client(api_key=GEMINI_API_KEY)

_class_names: dict = {}

CONFIDENCE_HIGH   = float(os.getenv('CONFIDENCE_HIGH',   0.80))
CONFIDENCE_MEDIUM = float(os.getenv('CONFIDENCE_MEDIUM', 0.50))

# Use the latest available model
GEMINI_MODEL = 'gemini-3.6-flash'


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def load_model(model_path: str, class_names_path: str):
    """Load class names. (Gemini replaces the local model)."""
    global _class_names

    if Path(class_names_path).exists():
        with open(class_names_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        _class_names = {int(k): v for k, v in raw.items()}
        log.info(f"Loaded {len(_class_names)} class names.")
    else:
        # Fallback to using our recommendation DB to get known classes
        fallback_path = Path(__file__).parent.parent / 'recommendations' / 'disease_data.json'
        if fallback_path.exists():
            with open(fallback_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _class_names = {i: d['class_key'] for i, d in enumerate(data.get('en', []))}
            log.info(f"Loaded {len(_class_names)} class names from fallback JSON.")
        else:
            log.warning("Could not load class names.")
            _class_names = {}


def is_model_loaded() -> bool:
    # We consider the "model" loaded if the Gemini API key is configured
    return _client is not None


# ---------------------------------------------------------------------------
# Confidence Classification
# ---------------------------------------------------------------------------

def classify_confidence(confidence: float) -> str:
    if confidence >= CONFIDENCE_HIGH:
        return 'high'
    elif confidence >= CONFIDENCE_MEDIUM:
        return 'medium'
    else:
        return 'low'


def confidence_message(level: str, lang: str = 'en') -> str:
    messages = {
        'high': {
            'en': 'Disease detected with high confidence.',
            'ta': 'அதிக நம்பகத்தன்மையுடன் நோய் கண்டறியப்பட்டது.',
        },
        'medium': {
            'en': 'Possible disease. Please upload a clearer image or consult an agricultural expert.',
            'ta': 'சாத்தியமான நோய். தெளிவான படம் பதிவேற்றவும் அல்லது வேளாண் நிபுணரை அணுகவும்.',
        },
        'low': {
            'en': 'Unable to identify the disease reliably. Please upload a clear, close-up image of the leaf.',
            'ta': 'நோயை நம்பகத்தன்மையுடன் அடையாளம் காண முடியவில்லை. தெளிவான இலை படம் பதிவேற்றவும்.',
        },
    }
    return messages.get(level, {}).get(lang, messages[level]['en'])


# ---------------------------------------------------------------------------
# Class Name Parsing
# ---------------------------------------------------------------------------

def parse_class_name(class_key: str) -> dict:
    parts = class_key.split('___')
    crop    = parts[0].replace('_', ' ') if parts else 'Unknown'
    disease = parts[1].replace('_', ' ') if len(parts) > 1 else 'Unknown'
    is_healthy = 'healthy' in disease.lower()
    return {'crop': crop, 'disease': disease, 'is_healthy': is_healthy}


# ---------------------------------------------------------------------------
# Prediction via Gemini API
# ---------------------------------------------------------------------------

def _pil_to_part(img: Image.Image) -> types.Part:
    """Convert a PIL Image to a Gemini types.Part (JPEG bytes)."""
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    return types.Part.from_bytes(data=buf.read(), mime_type='image/jpeg')


def predict(image_array: np.ndarray, lang: str = 'en') -> dict:
    """
    Run prediction using Gemini on the image array.
    Falls back to demo mode if API is unavailable.
    """
    if not is_model_loaded():
        log.warning("No Gemini API Key found. Returning Demo Result.")
        return _demo_result(image_array, lang)

    # Convert preprocessed array (1, 224, 224, 3) float [0,1] → PIL Image
    arr = (image_array[0] * 255.0).astype('uint8')
    img = Image.fromarray(arr)

    prompt = """
You are an expert plant pathologist and agronomist.
Analyze this leaf image and identify the specific crop species and any disease present.
If the leaf is healthy, state disease as "healthy".

Respond STRICTLY with ONLY a raw JSON object — no markdown, no backticks, no explanation.
Example:
{"crop": "Tomato", "disease": "Early Blight", "is_healthy": false, "confidence": 0.92}
    """.strip()

    try:
        img_part = _pil_to_part(img)
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Content(parts=[
                    types.Part.from_text(text=prompt),
                    img_part,
                ])
            ],
        )
        text = response.text.strip()

        # Strip any accidental markdown fences
        for fence in ('```json', '```'):
            if text.startswith(fence):
                text = text[len(fence):]
        if text.endswith('```'):
            text = text[:-3]

        data = json.loads(text.strip())

        crop      = str(data.get('crop', 'Unknown'))
        disease   = str(data.get('disease', 'Unknown'))
        is_healthy = bool(data.get('is_healthy', 'healthy' in disease.lower()))
        conf      = float(data.get('confidence', 0.85))

        # Match to closest PlantVillage class_key for recommendations
        best_match_key = f"{crop.replace(' ', '_')}___{disease.replace(' ', '_')}"
        best_match_idx = 0

        for idx, key in _class_names.items():
            k_lower = key.lower()
            if crop.lower() in k_lower and (
                disease.lower() in k_lower or
                ('healthy' in k_lower and is_healthy)
            ):
                best_match_key = key
                best_match_idx = idx
                break

        conf_level = classify_confidence(conf)
        status = 'healthy' if is_healthy else 'disease_detected'
        if conf_level == 'low':
            status = 'low_confidence'

        return {
            'crop'               : crop,
            'disease'            : disease,
            'class_key'          : best_match_key,
            'class_index'        : best_match_idx,
            'confidence'         : conf,
            'confidence_pct'     : round(conf * 100, 2),
            'confidence_level'   : conf_level,
            'confidence_message' : confidence_message(conf_level, lang),
            'is_healthy'         : is_healthy,
            'status'             : status,
            'demo_mode'          : False,
        }

    except Exception as e:
        log.error(f"Gemini API Error: {e}")
        return _demo_result(image_array, lang)


def _demo_result(image_array: np.ndarray = None, lang: str = 'en') -> dict:
    """Return a deterministic demo prediction when API is disabled/fails."""
    val = int(np.sum(image_array) * 1000) if image_array is not None else 42

    demo_classes = [
        ('Tomato',     'Early Blight',    'Tomato___Early_blight',            False),
        ('Apple',      'Apple Scab',      'Apple___Apple_scab',                False),
        ('Corn',       'Common Rust',     'Corn_(maize)___Common_rust_',       False),
        ('Potato',     'Late Blight',     'Potato___Late_blight',              False),
        ('Strawberry', 'Healthy',         'Strawberry___healthy',              True),
        ('Pepper',     'Bacterial Spot',  'Pepper,_bell___Bacterial_spot',     False),
    ]

    idx = val % len(demo_classes)
    crop, disease, class_key, is_healthy = demo_classes[idx]

    conf = 0.70 + (val % 300) / 1000.0
    status = 'healthy' if is_healthy else 'disease_detected'

    return {
        'crop'               : crop,
        'disease'            : disease,
        'class_key'          : class_key,
        'class_index'        : idx,
        'confidence'         : conf,
        'confidence_pct'     : round(conf * 100, 2),
        'confidence_level'   : 'high',
        'confidence_message' : confidence_message('high', lang),
        'is_healthy'         : is_healthy,
        'status'             : status,
        'demo_mode'          : True,
    }


# ---------------------------------------------------------------------------
# Grad-CAM Explainability (Disabled for LLM)
# ---------------------------------------------------------------------------

def generate_gradcam(image_path: str, class_index: int,
                     save_path: str,
                     last_conv_layer_name: str = 'Conv_1') -> Optional[str]:
    """
    Grad-CAM requires a local CNN. Since we use the Gemini API backend,
    we cannot generate local feature activation maps. Returns None.
    """
    log.info("Grad-CAM bypassed (using Gemini API backend).")
    return None

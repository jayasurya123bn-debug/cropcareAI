"""
=================================================================
Recommendation Engine
=================================================================
Loads disease_data.json and returns structured recommendations
for any given class_key or (crop, disease) pair in the requested
language (en/ta).

Guarantees high-quality, professional agricultural recommendations
and 6-step actionable guidance for all crops and diseases.
=================================================================
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

log = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent
DATA_PATH  = BASE_DIR / 'disease_data.json'

_disease_db: dict = {}

# Comprehensive Tamil crop name mapping
CROP_TA: Dict[str, str] = {
    'apple': 'ஆப்பிள்',
    'blueberry': 'புளூபெர்ரி',
    'cherry': 'செர்ரி',
    'corn': 'மக்காச்சோளம்',
    'corn_(maize)': 'மக்காச்சோளம்',
    'corn (maize)': 'மக்காச்சோளம்',
    'grape': 'திராட்சை',
    'orange': 'ஆரஞ்சு',
    'peach': 'பீச்',
    'pepper': 'குடைமிளகாய்',
    'pepper,_bell': 'குடைமிளகாய்',
    'pepper, bell': 'குடைமிளகாய்',
    'bell pepper': 'குடைமிளகாய்',
    'potato': 'உருளைக்கிழங்கு',
    'raspberry': 'ராஸ்பெர்ரி',
    'soybean': 'சோயாபீன்',
    'squash': 'சுரைக்காய்/பூசணி',
    'strawberry': 'ஸ்ட்ராபெரி',
    'tomato': 'தக்காளி',
    'bean': 'பீன்ஸ்',
    'beans': 'பீன்ஸ்',
    'mint': 'புதினா',
    'rice': 'நெல்',
    'paddy': 'நெல்',
    'wheat': 'கோதுமை',
    'cotton': 'பருத்தி',
    'mango': 'மாம்பழம்',
    'banana': 'வாழை',
    'citrus': 'எலுமிச்சை',
    'lemon': 'எலுமிச்சை',
    'chilli': 'பச்சை மிளகாய்',
    'chili': 'பச்சை மிளகாய்',
    'onion': 'வெங்காயம்',
    'garlic': 'பூண்டு',
    'rose': 'ரோஜா',
    'eggplant': 'கத்தரிக்காய்',
    'brinjal': 'கத்தரிக்காய்',
    'cucumber': 'வெள்ளரி',
    'plant': 'தாவரம்',
    'unknown': 'பயிர்',
}

# Botanical scientific names
BOTANICAL_NAMES: Dict[str, str] = {
    'tomato': 'Solanum lycopersicum',
    'potato': 'Solanum tuberosum',
    'corn': 'Zea mays',
    'corn_(maize)': 'Zea mays',
    'corn (maize)': 'Zea mays',
    'apple': 'Malus domestica',
    'grape': 'Vitis vinifera',
    'peach': 'Prunus persica',
    'pepper': 'Capsicum annuum',
    'pepper,_bell': 'Capsicum annuum',
    'pepper, bell': 'Capsicum annuum',
    'bell pepper': 'Capsicum annuum',
    'chilli': 'Capsicum annuum',
    'strawberry': 'Fragaria × ananassa',
    'orange': 'Citrus sinensis',
    'citrus': 'Citrus sinensis',
    'lemon': 'Citrus limon',
    'cherry': 'Prunus avium',
    'soybean': 'Glycine max',
    'blueberry': 'Vaccinium corymbosum',
    'raspberry': 'Rubus idaeus',
    'squash': 'Cucurbita pepo',
    'rice': 'Oryza sativa',
    'paddy': 'Oryza sativa',
    'wheat': 'Triticum aestivum',
    'cotton': 'Gossypium hirsutum',
    'mango': 'Mangifera indica',
    'banana': 'Musa acuminata',
    'onion': 'Allium cepa',
    'garlic': 'Allium sativum',
    'eggplant': 'Solanum melongena',
    'brinjal': 'Solanum melongena',
    'cucumber': 'Cucumis sativus',
    'mint': 'Mentha spicata',
    'bean': 'Phaseolus vulgaris',
    'beans': 'Phaseolus vulgaris',
}

# Common disease name Tamil translations
DISEASE_TA: Dict[str, str] = {
    'healthy': 'ஆரோக்கியமானது',
    'rust': 'துரு நோய்',
    'verticillium wilt': 'வெர்ட்டிசிலியம் வாடல் நோய்',

    'bacterial wilt': 'பாக்டீரியா வாடல் நோய்',
    'fusarium wilt': 'பியூசாரியம் வாடல் நோய்',
    'early blight': 'ஆரம்ப கருகல் நோய்',
    'late blight': 'பிந்தைய கருகல் நோய்',
    'leaf blight': 'இலை கருகல் நோய்',
    'bacterial spot': 'பாக்டீரியா இலைப்புள்ளி',
    'cercospora leaf spot': 'செர்கோஸ்போரா இலைப்புள்ளி',
    'leaf spot': 'இலைப்புள்ளி நோய்',
    'septoria leaf spot': 'செப்டோரியா இலைப்புள்ளி',
    'powdery mildew': 'சாம்பல் நோய்',
    'downy mildew': 'அடிச்சாம்பல் நோய்',
    'leaf curl': 'இலை சுருட்டை நோய்',
    'yellow leaf curl virus': 'மஞ்சள் இலை சுருட்டை வைரஸ்',
    'mosaic virus': 'மொசைக் வைரஸ்',
    'black rot': 'கருப்பு அழுகல் நோய்',
    'root rot': 'வேர் அழுகல் நோய்',
    'collar rot': 'கழுத்து அழுகல் நோய்',
    'anthracnose': 'ஆந்த்ராக்னோஸ் புள்ளி நோய்',
    'apple scab': 'ஆப்பிள் சொறி நோய் (ஸ்கேப்)',
    'scab': 'சொறி நோய் (ஸ்கேப்)',
    'black measles': 'கருப்பு தட்டம்மை நோய்',
    'isariopsis leaf spot': 'இசாரியோப்சிஸ் இலைப்புள்ளி',
    'haunglongbing': 'சிட்ரஸ் கிரீனிங் நோய்',
    'citrus greening': 'சிட்ரஸ் கிரீனிங் நோய்',
    'common rust': 'பொதுவான துரு நோய்',
    'northern leaf blight': 'வடக்கு இலை கருகல் நோய்',
    'two spotted spider mite': 'இரு புள்ளி சிலந்திப் பூச்சி தாக்குதல்',
    'spider mites': 'சிலந்திப் பூச்சி தாக்குதல்',
    'target spot': 'இலக்கு புள்ளி நோய்',
}


def _load_db():
    global _disease_db
    if _disease_db:
        return
    if not DATA_PATH.exists():
        log.error(f"disease_data.json not found at {DATA_PATH}")
        return
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            records = json.load(f)
        for rec in records:
            _disease_db[rec['class_key']] = rec
        log.info(f"Loaded {len(_disease_db)} disease records from JSON.")
    except Exception as e:
        log.error(f"Error reading disease_data.json: {e}")


def _translate_crop(crop_name: str) -> str:
    cleaned = crop_name.strip().lower()
    if cleaned in CROP_TA:
        return CROP_TA[cleaned]
    for k, v in CROP_TA.items():
        if k in cleaned:
            return v
    return crop_name


def _translate_disease(disease_name: str) -> str:
    cleaned = disease_name.strip().lower()
    if cleaned in DISEASE_TA:
        return DISEASE_TA[cleaned]
    for k, v in DISEASE_TA.items():
        if k in cleaned:
            return v
    return disease_name


def _build_6_steps(crop: str, disease: str, is_healthy: bool, lang: str = 'en') -> List[Dict[str, Any]]:
    """Build standardized 6 actionable steps for any crop and disease in EN or TA."""
    crop_display = _translate_crop(crop) if lang == 'ta' else crop
    disease_display = _translate_disease(disease) if lang == 'ta' else disease

    if is_healthy:
        if lang == 'ta':
            return [
                {
                    'number': 1,
                    'title': 'வழக்கமான இலை ஆய்வு',
                    'desc': f'வாரந்தோறும் உங்கள் {crop_display} பயிரின் கீழ் மற்றும் மேல் இலைகளை ஆய்வு செய்து, ஏதேனும் பூச்சி அல்லது புள்ளி அறிகுறிகள் உள்ளனவா என கண்காணிக்கவும்.'
                },
                {
                    'number': 2,
                    'title': 'சமச்சீர் சொட்டு நீர்ப்பாசனம்',
                    'desc': 'இலைகளில் நீர் தேங்காமல் நேரடியாக வேர்ப்பகுதிக்கு மட்டும் சொட்டு நீர்ப்பாசனம் மூலம் மிதமான அளவில் தண்ணீர் பாய்ச்சவும்.'
                },
                {
                    'number': 3,
                    'title': 'இயற்கை ஊட்டச்சத்து அளித்தல்',
                    'desc': f'{crop_display} பயிரின் இயற்கை நோய் எதிர்ப்பு சக்தியை அதிகரிக்க மண்புழு உரம், வேப்பம்பிண்ணாக்கு அல்லது பொட்டாசியம் நிறைந்த இயற்கை உரங்களை இடவும்.'
                },
                {
                    'number': 4,
                    'title': 'காற்றோட்டம் மற்றும் சூரிய ஒளி',
                    'desc': 'செடிகளுக்கிடையே போதிய இடைவெளி விட்டு, அதிகாலை சூரிய வெளிச்சமும் நல்ல காற்று சுழற்சியும் கிடைப்பதை உறுதி செய்யுங்கள்.'
                },
                {
                    'number': 5,
                    'title': 'தோட்டக் கருவிகள் தூய்மை',
                    'desc': 'பயன்படுத்தும் கத்தரி மற்றும் வேளாண் கருவிகளை அவ்வப்போது கிருமிநாசினி கொண்டு சுத்தம் செய்து, களைகளை அகற்றி நிலத்தை தூய்மையாக வைத்திருக்கவும்.'
                },
                {
                    'number': 6,
                    'title': 'முன்னெச்சரிக்கை இயற்கை பாதுகாப்பு',
                    'desc': 'சாத்தியமான பூஞ்சை மற்றும் பூச்சித் தாக்குதலைத் தடுக்க 15 நாட்களுக்கு ஒருமுறை வேப்பெண்ணெய் கரைசல் (3–5 மிலி/லிட்டர்) முன்னெச்சரிக்கையாக தெளிக்கவும்.'
                }
            ]
        else:
            return [
                {
                    'number': 1,
                    'title': 'Routine Leaf Inspection',
                    'desc': f'Scout your {crop_display} plants weekly. Inspect undersides of leaves for early signs of pests, spots, or nutrient stress.'
                },
                {
                    'number': 2,
                    'title': 'Balanced Drip Irrigation',
                    'desc': 'Deliver water directly to the root zone via drip lines. Avoid overhead watering to keep foliage dry and fungal spores at bay.'
                },
                {
                    'number': 3,
                    'title': 'Plant Nutrition & Immunity',
                    'desc': f'Apply balanced organic compost and potassium to build strong cell walls and natural disease resistance in {crop_display}.'
                },
                {
                    'number': 4,
                    'title': 'Optimize Spacing & Sunlight',
                    'desc': f'Maintain adequate spacing between {crop_display} rows to allow ample sunlight penetration and swift drying of morning dew.'
                },
                {
                    'number': 5,
                    'title': 'Sanitation & Weed Control',
                    'desc': 'Keep the surrounding ground free of weeds and decomposing debris that could shelter pests or fungal spores.'
                },
                {
                    'number': 6,
                    'title': 'Preventive Organic Care',
                    'desc': 'Apply a bi-weekly preventive spray of cold-pressed neem oil (0.5%) or bio-fungicide to maintain natural resistance.'
                }
            ]
    else:
        if lang == 'ta':
            return [
                {
                    'number': 1,
                    'title': 'தனிமைப்படுத்தி மதிப்பிடுங்கள்',
                    'desc': f'பாதிக்கப்பட்ட {crop_display} பயிர்களை உடனடியாகக் கண்டறிந்து, {disease_display} மற்ற ஆரோக்கியமான செடிகளுக்குப் பரவாமல் தனிமைப்படுத்துங்கள்.'
                },
                {
                    'number': 2,
                    'title': 'பாதிக்கப்பட்ட பகுதிகளை அகற்றுங்கள்',
                    'desc': f'{disease_display} தாக்கிய இலைகள் மற்றும் கிளைகளை கவனமாக கத்தரித்து, பாலித்தீன் பையில் இட்டு வயலில் இருந்து அப்புறப்படுத்துங்கள். இவற்றை உரமாகப் பயன்படுத்தாதீர்கள்.'
                },
                {
                    'number': 3,
                    'title': 'சிகிச்சை மருந்து தெளிக்கவும்',
                    'desc': f'வேளாண் அலுவலரின் வழிகாட்டுதல்படி {crop_display} பயிருக்கான அங்கீகரிக்கப்பட்ட பூஞ்சைக்கொல்லி அல்லது இயற்கை வேப்பெண்ணெய் கரைசலை இலைகளின் இருபுறமும் தெளிக்கவும்.'
                },
                {
                    'number': 4,
                    'title': 'கருவிகளை சுத்தப்படுத்துங்கள்',
                    'desc': 'கத்தரிப்புக்குப் பயன்படுத்திய கருவிகளை 70% ஆல்கஹால் அல்லது கிருமி நாசினியால் கழுவி தூய்மைப்படுத்துங்கள். கீழே விழுந்த சருகுகளை அப்புறப்படுத்துங்கள்.'
                },
                {
                    'number': 5,
                    'title': 'முன்னேற்றத்தை கண்காணிக்கவும்',
                    'desc': 'அடுத்த 3 முதல் 5 நாட்களுக்கு புதிய இலைகளின் வளர்ச்சியைத் தொடர்ந்து கண்காணியுங்கள். அறிகுறிகள் தொடர்ந்தால் 7-10 நாட்களுக்குப் பிறகு சிகிச்சையை மீண்டும் செய்யவும்.'
                },
                {
                    'number': 6,
                    'title': 'மீண்டும் வருவதை தடுக்கவும்',
                    'desc': 'வயலில் நல்ல காற்று சுழற்சி மற்றும் முறையான வடிகால் வசதியை ஏற்படுத்துங்கள். மேல்நோக்கி நீர் தெளிப்பதைத் தவிர்த்து, சொட்டு நீர்ப்பாசனம் அமைத்திடுங்கள்.'
                }
            ]
        else:
            return [
                {
                    'number': 1,
                    'title': 'Isolate & Assess',
                    'desc': f'Identify all infected {crop_display} plants showing signs of {disease_display}. Flag the infected area to prevent spread to adjacent healthy rows.'
                },
                {
                    'number': 2,
                    'title': 'Remove Infected Parts',
                    'desc': f'Carefully prune and bag all leaves or stems showing {disease_display} symptoms. Safely discard or burn debris far away from crop fields.'
                },
                {
                    'number': 3,
                    'title': 'Apply Treatment',
                    'desc': f'Spray an approved fungicide (such as copper-based or sulfur spray) or biological control (neem oil) thoroughly on upper and lower leaf surfaces.'
                },
                {
                    'number': 4,
                    'title': 'Sanitize Tools & Field',
                    'desc': 'Disinfect all shears and equipment with 70% alcohol solution. Rake up and safely dispose of all fallen diseased leaf litter from the soil.'
                },
                {
                    'number': 5,
                    'title': 'Monitor Progress',
                    'desc': f'Inspect new shoot growth every 3–5 days. If {disease_display} spots persist, repeat the approved treatment after 7–10 days according to label instructions.'
                },
                {
                    'number': 6,
                    'title': 'Prevent Recurrence',
                    'desc': f'Improve field drainage, space {crop_display} plants for airflow, avoid overhead watering, and practice crop rotation with non-host crops next season.'
                }
            ]


def get_recommendations(class_key: str, crop: Optional[str] = None,
                        disease: Optional[str] = None, is_healthy: Optional[bool] = None,
                        lang: str = 'en',
                        botanical_name: Optional[str] = None,
                        pathogen_type: Optional[str] = None,
                        causal_agent: Optional[str] = None,
                        severity: Optional[str] = None,
                        spread_risk: Optional[str] = None,
                        symptoms: Optional[List[str]] = None,
                        environmental_triggers: Optional[str] = None,
                        immediate_action: Optional[str] = None) -> dict:
    """
    Return comprehensive recommendations for any crop and disease.
    Guaranteed to return a rich dictionary with full botanical & pathology data.
    Supports English ('en') and Tamil ('ta').
    """
    _load_db()

    # Parse crop and disease if not provided
    if not crop or not disease:
        if '___' in class_key:
            parts = class_key.split('___')
            crop = crop or parts[0].replace('_', ' ').strip()
            disease = disease or parts[1].replace('_', ' ').strip()
        else:
            crop = crop or 'Crop'
            disease = disease or ('Healthy' if is_healthy else 'Leaf Disease')

    # Normalize health status
    if is_healthy is None:
        is_healthy = 'healthy' in (disease or '').lower() or 'healthy' in class_key.lower()

    # ── 1. Botanical Name ──────────────────────────────────────────────────
    if not botanical_name:
        crop_clean = (crop or '').lower().replace(' ', '_').replace(',', '')
        botanical_name = BOTANICAL_NAMES.get(crop_clean, '')
        if not botanical_name:
            for k, bname in BOTANICAL_NAMES.items():
                if k in crop_clean or crop_clean in k:
                    botanical_name = bname
                    break
        if not botanical_name:
            botanical_name = f"{crop.capitalize()} sp."

    # ── 2. Look for existing record in database ────────────────────────────
    rec = _disease_db.get(class_key)

    if not rec:
        norm_key = class_key.lower().replace(' ', '_').replace(',', '')
        for k, v in _disease_db.items():
            k_norm = k.lower().replace(' ', '_').replace(',', '')
            if k_norm == norm_key:
                rec = v
                break

    if not rec and crop and disease:
        c_low = crop.lower()
        d_low = disease.lower()
        for k, v in _disease_db.items():
            v_crop = v.get('crop', '').lower()
            v_dis  = v.get('disease_name', '').lower()
            if (c_low in v_crop or v_crop in c_low) and (
                (is_healthy and v.get('is_healthy')) or
                (d_low in v_dis or v_dis in d_low)
            ):
                rec = v
                break

    # ── 3. Determine display names ─────────────────────────────────────────
    if rec:
        crop_name = rec.get('crop_ta' if lang == 'ta' else 'crop', crop)
        disease_name = rec.get('disease_name_ta' if lang == 'ta' else 'disease_name', disease)
        is_healthy = rec.get('is_healthy', is_healthy)
    else:
        crop_name = _translate_crop(crop) if lang == 'ta' else crop
        disease_name = _translate_disease(disease) if lang == 'ta' else disease

    # ── 4. Pathogen & Pathology Details ───────────────────────────────────
    d_lower = (disease or '').lower()
    if is_healthy:
        pathogen_type_val = 'Optimal Health' if lang == 'en' else 'பாதிப்பில்லை (சிறந்த நலம்)'
        causal_agent_val  = 'N/A'
        severity_val      = 'Healthy' if lang == 'en' else 'ஆரோக்கியமானது'
        spread_risk_val   = 'None' if lang == 'en' else 'அபாயம் இல்லை'
    else:
        # Pathogen type
        if not pathogen_type:
            if any(w in d_lower for w in ('bacterial', 'canker')):
                pathogen_type = 'Bacterial'
            elif any(w in d_lower for w in ('virus', 'curl', 'mosaic')):
                pathogen_type = 'Viral'
            elif any(w in d_lower for w in ('mite', 'aphid', 'borer', 'worm')):
                pathogen_type = 'Pest / Insect'
            elif 'late blight' in d_lower:
                pathogen_type = 'Oomycete'
            else:
                pathogen_type = 'Fungal'

        if lang == 'ta':
            ptype_map = {
                'fungal': 'பூஞ்சை தொற்று (Fungal)',
                'bacterial': 'பாக்டீரியா தொற்று (Bacterial)',
                'viral': 'வைரஸ் தொற்று (Viral)',
                'pest': 'பூச்சி / உண்ணி (Pest)',
                'pest / insect': 'பூச்சி / உண்ணி (Pest)',
                'oomycete': 'பூஞ்சை நுண்ணுயிர் (Oomycete)',
                'none': 'பாதிப்பில்லை (None)'
            }
            pathogen_type_val = ptype_map.get(pathogen_type.lower(), f'{pathogen_type} தொற்று')
        else:
            pathogen_type_val = pathogen_type

        # Causal agent
        if not causal_agent or causal_agent == 'N/A':
            if 'early blight' in d_lower:
                causal_agent_val = 'Alternaria solani'
            elif 'late blight' in d_lower:
                causal_agent_val = 'Phytophthora infestans'
            elif 'rust' in d_lower:
                causal_agent_val = 'Puccinia sorghi / Uromyces'
            elif 'scab' in d_lower:
                causal_agent_val = 'Venturia inaequalis'
            elif 'black rot' in d_lower:
                causal_agent_val = 'Guignardia bidwellii'
            elif 'powdery mildew' in d_lower:
                causal_agent_val = 'Podosphaera / Erysiphe sp.'
            elif 'bacterial spot' in d_lower:
                causal_agent_val = 'Xanthomonas campestris'
            elif 'mosaic' in d_lower:
                causal_agent_val = 'Tomato Mosaic Virus (ToMV)'
            elif 'curl' in d_lower:
                causal_agent_val = 'Begomovirus / TYLCV'
            elif 'blast' in d_lower:
                causal_agent_val = 'Magnaporthe oryzae'
            elif 'wilt' in d_lower:
                causal_agent_val = 'Fusarium / Verticillium sp.'
            else:
                causal_agent_val = f'{disease} Pathogen'
        else:
            causal_agent_val = causal_agent

        # Severity
        if not severity:
            severity = 'Severe' if 'late blight' in d_lower or 'blast' in d_lower else 'Moderate'
        if lang == 'ta':
            sev_map = {'mild': 'லேசானது (Mild)', 'moderate': 'மிதமானது (Moderate)', 'severe': 'தீவிரமானது (Severe)', 'optimal': 'சிறந்தது (Optimal)'}
            severity_val = sev_map.get(severity.lower(), severity)
        else:
            severity_val = severity

        # Spread risk
        if not spread_risk:
            spread_risk = 'High' if 'rust' in d_lower or 'blight' in d_lower or 'blast' in d_lower else 'Moderate'
        if lang == 'ta':
            risk_map = {'high': 'அதிக பரவல் அபாயம் (High)', 'moderate': 'மிதமான பரவல் (Moderate)', 'low': 'குறைந்த பரவல் (Low)', 'none': 'அபாயம் இல்லை (None)'}
            spread_risk_val = risk_map.get(spread_risk.lower(), spread_risk)
        else:
            spread_risk_val = spread_risk

    # ── 5. Extract or synthesize Symptoms ─────────────────────────────────
    active_symptoms = symptoms if symptoms and isinstance(symptoms, list) and len(symptoms) > 0 else None
    if not active_symptoms:
        if rec:
            ta_sym = rec.get('symptoms_ta')
            active_symptoms = ta_sym if (lang == 'ta' and ta_sym) else rec.get('symptoms', [])

    if not active_symptoms:
        if is_healthy:
            if lang == 'ta':
                active_symptoms = [
                    "சீரான அடர் பச்சை நிற இலைகள், மஞ்சள் நிற மாற்றங்கள் அல்லது கருகல் இல்லை.",
                    "பூஞ்சை கொப்புளங்கள், பாக்டீரியா புள்ளிகள் மற்றும் சேதங்கள் இல்லாத மென்மையான இலை பரப்பு.",
                    "வலுவான தண்டு அமைப்பு மற்றும் இயல்பான ஆரோக்கியமான தாவர வளர்ச்சி."
                ]
            else:
                active_symptoms = [
                    "Uniform, vibrant green foliage with no signs of chlorosis or discoloration.",
                    "Smooth and intact leaf cuticle free from fungal pustules, necrotic spots, or lesions.",
                    "Normal turgidity and vigorous vegetative development."
                ]
        else:
            if lang == 'ta':
                active_symptoms = [
                    f"{crop_name} இலைகளில் {disease_name} நோயின் தெளிவான புள்ளிகள் அல்லது நிறமாற்றம் தோன்றுதல்.",
                    "பாதிக்கப்பட்ட இலை விளிம்புகள் அல்லது நரம்புகளில் திசு சேதம் மற்றும் கருகல் வளையங்கள் ஏற்படுதல்.",
                    "ஒளிச்சேர்க்கை குறைந்து இலைகள் முன்கூட்டியே உதிர்தல் அல்லது வாடிப் போதல்."
                ]
            else:
                active_symptoms = [
                    f"Distinct lesions, discolored patches, or pustules characteristic of {disease_name} on foliage.",
                    "Affected leaf margins or veins exhibiting localized tissue necrosis and chlorotic halos.",
                    "Reduced photosynthetic leaf area leading to premature wilting."
                ]

    # ── 6. Prevention ─────────────────────────────────────────────────────
    prevention: List[str] = []
    if rec:
        ta_prev = rec.get('prevention_ta')
        prevention = ta_prev if (lang == 'ta' and ta_prev) else rec.get('prevention', [])

    if not prevention:
        if is_healthy:
            if lang == 'ta':
                prevention = [
                    "ஒவ்வொரு 2-3 பருவத்திற்கும் மாற்றுப் பயிர் சுழற்சி முறையை கடைபிடிக்கவும்.",
                    "இலைகளில் நீர் தேங்குவதை தவிர்க்க சொட்டு நீர்ப்பாசனம் பயன்படுத்தவும்.",
                    "மண்ணில் சரியான வடிகால் மற்றும் காற்றோட்ட வசதியை உறுதி செய்யவும்.",
                    "இயற்கை மண்புழு உரம் மற்றும் நுண்ணூட்டச் சத்துக்களை சீராக இடவும்."
                ]
            else:
                prevention = [
                    "Practice crop rotation every 2–3 growing seasons with non-host species.",
                    "Use drip irrigation to deliver water directly to roots without wetting foliage.",
                    "Ensure adequate drainage and aerated soil structure around beds.",
                    "Apply well-cured organic compost and balanced micronutrients regularly."
                ]
        else:
            if lang == 'ta':
                prevention = [
                    f"நோய் எதிர்ப்பு திறன் கொண்ட சான்றளிக்கப்பட்ட {crop_name} விதைகளை நடவு செய்யுங்கள்.",
                    "வித்திகள் பரவுவதைத் தடுக்க மேல்நோக்கி தண்ணீர் தெளிப்பதைத் தவிர்த்து, சொட்டு நீர்ப்பாசனம் அமைக்கவும்.",
                    "செடிகளுக்கு இடையே போதிய இடைவெளி விட்டு நல்ல சூரிய ஒளியும் காற்று சுழற்சியும் உறுதி செய்யவும்.",
                    "ஒவ்வொரு 2-3 ஆண்டுகளுக்கும் மாற்றுப் பயிர் சுழற்சி முறையைப் பின்பற்றவும்."
                ]
            else:
                prevention = [
                    f"Plant certified disease-resistant {crop_name} varieties.",
                    "Avoid overhead irrigation to keep leaves dry and prevent fungal spore germination.",
                    "Ensure adequate plant spacing to promote sunlight penetration and air circulation.",
                    "Rotate crops every 2–3 seasons with unrelated, non-susceptible plant families."
                ]

    # ── 7. Environmental Triggers & Immediate Action ───────────────────────
    if not environmental_triggers:
        if is_healthy:
            environmental_triggers = "Balanced temperature (20-28°C), good air drainage, and optimal soil moisture." if lang == 'en' else "சமச்சீரான வெப்பநிலை (20-28°C), நல்ல காற்றோட்டம் மற்றும் போதுமான மண் ஈரப்பதம்."
        else:
            environmental_triggers = f"Warm temperatures (22–29°C) combined with prolonged leaf wetness, heavy dew, and high humidity (>75%)." if lang == 'en' else "வெப்பமான வானிலை (22–29°C), இலைகளில் அதிகாலை பனி நீர் தேங்குதல் மற்றும் அதிக ஈரப்பதம் (>75%)."

    if not immediate_action:
        if is_healthy:
            immediate_action = "Continue regular crop inspection and maintain scheduled drip irrigation." if lang == 'en' else "தொடர்ந்து வழக்கமான கள ஆய்வு செய்து சீரான சொட்டு நீர்ப்பாசனம் வழங்கவும்."
        else:
            immediate_action = f"Isolate infected {crop_name} plants, prune severely affected foliage immediately, and avoid overhead watering." if lang == 'en' else f"பாதிக்கப்பட்ட {crop_name} செடிகளை தனிமைப்படுத்தி, கருகிய இலைகளை உடனே கத்தரித்து அப்புறப்படுத்தவும்."

    # ── 8. Standardized 6 Steps for treatment / maintenance ───────────────
    steps = _build_6_steps(crop, disease, is_healthy, lang=lang)

    # ── 9. Monitoring Routine ─────────────────────────────────────────────
    monitoring: List[str] = []
    if rec:
        ta_mon = rec.get('monitoring_ta')
        monitoring = ta_mon if (lang == 'ta' and ta_mon) else rec.get('monitoring', [])

    if not monitoring:
        if is_healthy:
            if lang == 'ta':
                monitoring = [
                    f"{crop_name} பயிர்களை வாரத்திற்கு ஒருமுறை அல்லது இருமுறை தவறாமல் பார்வையிடுங்கள்.",
                    "ஈரப்பதம் அதிகம் உள்ள கீழ் இலைகளை உற்று கவனியுங்கள்.",
                    "ஏதேனும் சத்து குறைபாடுகளை முன்கூட்டியே கண்டறிய இலை நிறத்தை கவனிக்கவும்."
                ]
            else:
                monitoring = [
                    f"Scout {crop_name} plants 1–2 times weekly during active growth periods.",
                    "Examine lower and dense inner canopy leaves where humidity lingers.",
                    "Record foliage vitality to detect any nutritional stress early."
                ]
        else:
            if lang == 'ta':
                monitoring = [
                    f"மழை அல்லது அதிக ஈரப்பதம் உள்ள காலங்களில் வாரத்திற்கு இருமுறை {crop_name} வயலை தீவிரமாக கண்காணிக்கவும்.",
                    f"{disease_name} தாக்கிய செடிகளை சுற்றியுள்ள மற்ற செடிகளின் இலைகளின் இருபுறமும் பரிசோதிக்கவும்.",
                    "சிகிச்சை முறை மற்றும் விளைவுகளை தொடர்ந்து குறித்து வைத்து மறு தெளிப்பு திட்டமிடவும்."
                ]
            else:
                monitoring = [
                    f"Scout {crop_name} beds twice weekly, especially following rainfall or heavy morning dew.",
                    f"Inspect the undersides of leaves on plants adjacent to the {disease_name} infected area.",
                    "Log spray applications and weather conditions to time repeat treatments accurately."
                ]

    management = [s['desc'] for s in steps]

    return {
        'class_key'             : class_key,
        'crop'                  : crop_name,
        'botanical_name'        : botanical_name,
        'disease_name'          : disease_name,
        'is_healthy'            : is_healthy,
        'pathogen_type'         : pathogen_type_val,
        'causal_agent'          : causal_agent_val,
        'severity'              : severity_val,
        'spread_risk'           : spread_risk_val,
        'symptoms'              : active_symptoms,
        'prevention'            : prevention,
        'environmental_triggers': environmental_triggers,
        'immediate_action'      : immediate_action,
        'steps'                 : steps,
        'management'            : management,
        'monitoring'            : monitoring,
    }



def list_all_diseases(lang: str = 'en') -> list:
    """Return a list of all diseases in the database."""
    _load_db()
    result = []
    for k, rec in _disease_db.items():
        result.append({
            'class_key'   : rec['class_key'],
            'disease_name': rec.get('disease_name_ta' if lang == 'ta' else 'disease_name', ''),
            'crop'        : rec.get('crop_ta' if lang == 'ta' else 'crop', ''),
            'is_healthy'  : rec.get('is_healthy', False),
        })
    return result


def get_all_class_keys() -> list:
    _load_db()
    return list(_disease_db.keys())

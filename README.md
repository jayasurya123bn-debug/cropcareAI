# CropCare AI 🌿

## AI-Based Crop Disease Detection and Smart Recommendation System Using Deep Learning

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.18-orange)](https://tensorflow.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## Problem Statement

Smallholder farmers face significant crop losses due to plant diseases, often lacking access to timely agricultural expertise. Manual disease identification is slow, error-prone, and geographically constrained. This project addresses that gap using deep learning to provide instant, accessible, and bilingual crop disease detection.

---

## Objectives

1. Build a deep-learning model to classify 38 crop disease/healthy classes
2. Provide a web application for image-based disease detection
3. Generate smart, evidence-based recommendations (symptoms, prevention, management)
4. Support English and Tamil languages
5. Store prediction history for farmers
6. Provide Grad-CAM explainability

---

## Features

| Feature | Status |
|---------|--------|
| Image upload (drag-drop, camera) | ✅ |
| Image validation (extension, magic bytes, size) | ✅ |
| MobileNetV2 transfer learning | ✅ |
| Confidence scoring (High / Medium / Low) | ✅ |
| Grad-CAM heatmap | ✅ |
| Disease recommendations (symptoms/prevention/management) | ✅ |
| English & Tamil bilingual UI | ✅ |
| User authentication | ✅ |
| Prediction history | ✅ |
| Dashboard with charts | ✅ |
| Admin panel | ✅ |
| REST API | ✅ |
| Responsive mobile UI | ✅ |

---

## System Architecture

```
User Browser
     │
     ▼
Flask Web Application (app.py)
     │
     ├── routes/auth.py    → Register, Login, Language
     ├── routes/main.py    → Home, Predict, Result, Dashboard, History
     ├── routes/api.py     → REST API endpoints
     └── routes/admin.py   → Admin panel
          │
          ├── prediction/image_processor.py  → Validate & preprocess upload
          ├── prediction/predictor.py        → MobileNetV2 inference + Grad-CAM
          ├── recommendations/               → Disease knowledge base
          └── database/                      → SQLAlchemy ORM (SQLite/MySQL)
```

---

## Technology Stack

### AI / ML
- Python 3.13
- TensorFlow 2.18 / Keras
- MobileNetV2 (Transfer Learning)
- OpenCV (Grad-CAM)
- NumPy, scikit-learn, Matplotlib

### Backend
- Flask 3.1
- Flask-Login, Flask-SQLAlchemy
- SQLite (default) / MySQL

### Frontend
- HTML5, CSS3 (Vanilla)
- JavaScript (ES6+)
- Bootstrap Icons
- Chart.js

---

## Dataset

- **Source**: [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset)
- **Size**: 54,306 images
- **Classes**: 38 (26 diseases + 12 healthy)
- **Crops**: 14 species
- **Split**: Leaf-aware 70/15/15 train/val/test

---

## Installation

### Prerequisites
- Python 3.10+
- Git + Git LFS (for dataset download)
- pip

### Steps

```bash
# 1. Clone this project
git clone <your-project-repo-url>
cd crop-disease-ai

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env and set your SECRET_KEY

# 5. Download the PlantVillage dataset
python scripts/download_dataset.py

# 6. Train the model
python training/train.py

# 7. Evaluate the model
python training/evaluate.py

# 8. Run the application
python app.py
```

Then open: **http://localhost:5000**

---

## Training Instructions

```bash
# Download dataset
python scripts/download_dataset.py

# Train model (Phase 1 + Phase 2 fine-tuning)
python training/train.py

# Outputs:
#   models/crop_disease_model.keras
#   models/class_names.json
#   models/training_history.json
```

> ⚠ **Note**: Training on CPU takes 6–24 hours. Use a GPU or Google Colab for faster training.  
> On Google Colab, mount your Drive and copy the project files there.

---

## Running the Application

```bash
# Start Flask development server
python app.py

# Visit: http://localhost:5000
```

**Demo Mode**: The app runs in Demo Mode if no trained model is found. Upload and UI features work, but predictions are placeholder values.

---

## Model Evaluation

```bash
python training/evaluate.py
```

Results saved to `results/`:
- `evaluation_results.json` — accuracy, precision, recall, F1
- `training_history.png` — accuracy/loss curves
- `confusion_matrix.png` — normalised confusion matrix
- `per_class_f1.png` — per-class F1 bar chart

> ⚠ Actual accuracy depends on your training run. Do not assume any specific value.

---

## API Documentation

### POST /api/predict
Upload a leaf image for disease detection.

```bash
curl -X POST http://localhost:5000/api/predict \
  -F "leaf_image=@leaf.jpg" \
  -F "lang=en"
```

**Response:**
```json
{
  "success": true,
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 94.7,
  "confidence_level": "high",
  "is_healthy": false,
  "recommendations": {
    "symptoms": ["..."],
    "prevention": ["..."],
    "management": ["..."]
  }
}
```

### GET /api/disease/<class_key>
```bash
curl http://localhost:5000/api/disease/Tomato___Early_blight?lang=en
```

### GET /api/history *(auth required)*
### GET /api/dashboard *(auth required)*
### POST /api/register
### POST /api/login
### GET /api/status

---

## Testing

```bash
pytest tests/ -v
```

Test coverage:
- Route tests (home, auth, predict, history, dashboard)
- Image processor tests (validation, preprocessing)
- Predictor tests (confidence, class parsing)
- Recommendation engine tests (EN/TA, healthy/disease)
- API endpoint tests (all endpoints)

---

## Future Enhancements

1. Weather-based disease risk indicator (OpenWeatherMap API)
2. Push notifications for high-risk weather conditions
3. Offline mobile app (TensorFlow Lite)
4. Multi-language support (Hindi, Telugu)
5. Expert consultation booking
6. Pest detection (not just disease)
7. Yield prediction module
8. Migration to MySQL/PostgreSQL for production
9. Docker deployment
10. Model retraining pipeline with user-submitted images

---

## Dataset Citation

> Hughes, D. P., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics.* arXiv preprint arXiv:1511.08060.

Source: https://github.com/spMohanty/PlantVillage-Dataset

---

## Disclaimer

> ⚠ **CropCare AI is an educational and informational tool.** AI predictions carry uncertainty.  
> **Always consult a qualified agricultural extension officer before applying any pesticide or chemical treatment.**  
> **Follow locally approved pesticide labels for all dosage and application instructions.**  
> Do not make crop management decisions based solely on this application's output.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

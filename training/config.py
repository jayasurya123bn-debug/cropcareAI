"""
=================================================================
Training Configuration
=================================================================
Central place for all training hyperparameters and paths.
Edit here — no need to touch train.py for common changes.
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR     = os.path.join(BASE_DIR, 'dataset', 'plantvillage', 'raw', 'color')
MODEL_DIR       = os.path.join(BASE_DIR, 'models')
RESULTS_DIR     = os.path.join(BASE_DIR, 'results')
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, 'crop_disease_model.keras')
CLASS_NAMES_PATH = os.path.join(MODEL_DIR, 'class_names.json')
HISTORY_PATH    = os.path.join(MODEL_DIR, 'training_history.json')

# ── Image Settings ─────────────────────────────────────────────────────────
IMAGE_SIZE   = (224, 224)    # MobileNetV2 / EfficientNetB0 input
IMAGE_CHANNELS = 3
INPUT_SHAPE  = (224, 224, 3)

# ── Data Split ─────────────────────────────────────────────────────────────
TRAIN_SPLIT = 0.70
VAL_SPLIT   = 0.15
TEST_SPLIT  = 0.15
RANDOM_SEED = 42

# ── Training Hyperparameters ───────────────────────────────────────────────
BATCH_SIZE          = 32
INITIAL_EPOCHS      = 20    # Head-only training
FINE_TUNE_EPOCHS    = 10    # Fine-tuning last N layers
LEARNING_RATE       = 1e-3
FINE_TUNE_LR        = 1e-5
FINE_TUNE_AT        = 100   # Unfreeze layers from this index (MobileNetV2 has 154)
DROPOUT_RATE        = 0.3

# ── Augmentation ──────────────────────────────────────────────────────────
AUGMENTATION = {
    'rotation_range'      : 15,
    'width_shift_range'   : 0.1,
    'height_shift_range'  : 0.1,
    'shear_range'         : 0.05,
    'zoom_range'          : 0.1,
    'horizontal_flip'     : True,
    'brightness_range'    : [0.8, 1.2],
    'fill_mode'           : 'nearest',
}

# ── Model Architecture ─────────────────────────────────────────────────────
BACKBONE        = 'MobileNetV2'   # or 'EfficientNetB0'
POOLING         = 'avg'           # Global Average Pooling
DENSE_UNITS     = 256
ACTIVATION      = 'relu'
OUTPUT_ACTIVATION = 'softmax'

# ── Callbacks ─────────────────────────────────────────────────────────────
EARLY_STOPPING_PATIENCE    = 5
REDUCE_LR_PATIENCE         = 3
REDUCE_LR_FACTOR           = 0.5
REDUCE_LR_MIN              = 1e-7

# ── Confidence Thresholds ─────────────────────────────────────────────────
CONFIDENCE_HIGH   = 0.80
CONFIDENCE_MEDIUM = 0.50

# Create output directories
for d in [MODEL_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

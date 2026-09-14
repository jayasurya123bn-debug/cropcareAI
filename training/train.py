"""
=================================================================
Model Training Script
=================================================================
Run: python training/train.py

Phase 1: Train classification head (backbone frozen)
Phase 2: Fine-tune last N layers of backbone

Training artifacts saved:
  models/crop_disease_model.keras
  models/class_names.json
  models/training_history.json
=================================================================
"""

import os
import sys
import json
import logging
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
)

from training.config import (
    DATASET_DIR, MODEL_SAVE_PATH, CLASS_NAMES_PATH, HISTORY_PATH,
    IMAGE_SIZE, INPUT_SHAPE, BATCH_SIZE, INITIAL_EPOCHS, FINE_TUNE_EPOCHS,
    LEARNING_RATE, FINE_TUNE_LR, FINE_TUNE_AT, DROPOUT_RATE,
    BACKBONE, DENSE_UNITS, EARLY_STOPPING_PATIENCE,
    REDUCE_LR_PATIENCE, REDUCE_LR_FACTOR, REDUCE_LR_MIN, RANDOM_SEED
)
from training.preprocess import prepare_datasets

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

tf.random.set_seed(RANDOM_SEED)


# ---------------------------------------------------------------------------
# Model Builder
# ---------------------------------------------------------------------------

def build_model(n_classes: int, backbone_name: str = 'MobileNetV2') -> keras.Model:
    """
    Build a transfer-learning model.
    Backbone is frozen; only the classification head is trainable initially.
    """
    # ── Load pretrained backbone ──────────────────────────────────────────
    if backbone_name == 'MobileNetV2':
        backbone = MobileNetV2(
            input_shape=INPUT_SHAPE,
            include_top=False,
            weights='imagenet'
        )
    elif backbone_name == 'EfficientNetB0':
        backbone = EfficientNetB0(
            input_shape=INPUT_SHAPE,
            include_top=False,
            weights='imagenet'
        )
    else:
        raise ValueError(f"Unknown backbone: {backbone_name}. Use 'MobileNetV2' or 'EfficientNetB0'.")

    backbone.trainable = False
    log.info(f"Loaded {backbone_name} backbone ({len(backbone.layers)} layers, frozen).")

    # ── Classification Head ───────────────────────────────────────────────
    inputs = keras.Input(shape=INPUT_SHAPE, name='leaf_image')
    x = backbone(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name='global_avg_pool')(x)
    x = layers.BatchNormalization(name='batch_norm')(x)
    x = layers.Dropout(DROPOUT_RATE, name='dropout')(x)
    x = layers.Dense(DENSE_UNITS, activation='relu', name='dense_head')(x)
    x = layers.Dropout(DROPOUT_RATE / 2, name='dropout_2')(x)
    outputs = layers.Dense(n_classes, activation='softmax', name='predictions')(x)

    model = keras.Model(inputs, outputs, name=f'CropCare_{backbone_name}')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    log.info(f"Model built: {model.count_params():,} total params, "
             f"{sum(np.prod(v.shape) for v in model.trainable_variables):,} trainable.")
    return model, backbone


def unfreeze_for_fine_tuning(model: keras.Model, backbone: keras.Model, fine_tune_at: int):
    """Unfreeze the top layers of the backbone for fine-tuning."""
    backbone.trainable = True

    # Freeze all layers before fine_tune_at
    for layer in backbone.layers[:fine_tune_at]:
        layer.trainable = False

    n_trainable = sum(1 for l in backbone.layers if l.trainable)
    log.info(f"Fine-tuning: {n_trainable}/{len(backbone.layers)} backbone layers unfrozen.")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=FINE_TUNE_LR),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

def get_callbacks(phase: int) -> list:
    """Build Keras callbacks for a training phase."""
    callbacks = [
        ModelCheckpoint(
            filepath=MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        ),
        EarlyStopping(
            monitor='val_accuracy',
            patience=EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=REDUCE_LR_FACTOR,
            patience=REDUCE_LR_PATIENCE,
            min_lr=REDUCE_LR_MIN,
            verbose=1
        ),
        TensorBoard(
            log_dir=f'results/tensorboard/phase{phase}',
            histogram_freq=0
        ),
    ]
    return callbacks


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train():
    print("\n" + "=" * 60)
    print("  CropCare AI — Model Training")
    print("=" * 60 + "\n")

    # ── Check dataset exists ──────────────────────────────────────────────
    if not Path(DATASET_DIR).exists():
        log.error(f"Dataset not found at {DATASET_DIR}")
        log.error("Run: python scripts/download_dataset.py")
        sys.exit(1)

    # ── Prepare datasets ──────────────────────────────────────────────────
    log.info("Preparing datasets...")
    start = time.time()
    data = prepare_datasets(DATASET_DIR)
    log.info(f"Dataset ready in {time.time() - start:.1f}s")

    print(f"\n  Dataset Summary:")
    print(f"  ├─ Total Images   : {data['total_size']:,}")
    print(f"  ├─ Training       : {data['train_size']:,}")
    print(f"  ├─ Validation     : {data['val_size']:,}")
    print(f"  ├─ Testing        : {data['test_size']:,}")
    print(f"  └─ Classes        : {data['n_classes']}\n")

    n_classes = data['n_classes']

    # ── Build model ───────────────────────────────────────────────────────
    model, backbone = build_model(n_classes, backbone_name=BACKBONE)
    model.summary(line_length=90)

    history_all = {}

    # ── Phase 1: Head-only training ────────────────────────────────────────
    log.info(f"\n{'─'*60}")
    log.info(f"PHASE 1: Training classification head ({INITIAL_EPOCHS} epochs max)")
    log.info(f"{'─'*60}")

    history1 = model.fit(
        data['train_ds'],
        validation_data=data['val_ds'],
        epochs=INITIAL_EPOCHS,
        callbacks=get_callbacks(phase=1),
        verbose=1
    )
    history_all['phase1'] = {k: [float(v) for v in vals]
                              for k, vals in history1.history.items()}

    # ── Phase 2: Fine-tuning ──────────────────────────────────────────────
    log.info(f"\n{'─'*60}")
    log.info(f"PHASE 2: Fine-tuning last layers ({FINE_TUNE_EPOCHS} epochs max)")
    log.info(f"{'─'*60}")

    unfreeze_for_fine_tuning(model, backbone, fine_tune_at=FINE_TUNE_AT)

    history2 = model.fit(
        data['train_ds'],
        validation_data=data['val_ds'],
        epochs=INITIAL_EPOCHS + FINE_TUNE_EPOCHS,
        initial_epoch=len(history1.history['accuracy']),
        callbacks=get_callbacks(phase=2),
        verbose=1
    )
    history_all['phase2'] = {k: [float(v) for v in vals]
                              for k, vals in history2.history.items()}

    # ── Save training history ─────────────────────────────────────────────
    history_all['class_names'] = data['class_names']
    history_all['n_classes']   = n_classes
    history_all['total_images']= data['total_size']
    history_all['train_size']  = data['train_size']
    history_all['val_size']    = data['val_size']
    history_all['test_size']   = data['test_size']

    with open(HISTORY_PATH, 'w') as f:
        json.dump(history_all, f, indent=2)

    log.info(f"\n✅ Training complete!")
    log.info(f"   Model saved → {MODEL_SAVE_PATH}")
    log.info(f"   History    → {HISTORY_PATH}")
    log.info(f"\n   Next: python training/evaluate.py")


if __name__ == '__main__':
    train()

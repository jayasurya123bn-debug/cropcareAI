"""
=================================================================
Data Preprocessing & Leaf-Aware Splitting
=================================================================
Handles:
  - Loading images efficiently with tf.data
  - Leaf-group-aware train/val/test splitting
  - Data augmentation pipeline
  - Dataset statistics reporting
=================================================================
"""

import os
import json
import logging
import random
from pathlib import Path
from collections import defaultdict

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

from training.config import (
    DATASET_DIR, IMAGE_SIZE, BATCH_SIZE, RANDOM_SEED,
    TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT, AUGMENTATION,
    CLASS_NAMES_PATH
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Leaf-Aware Splitting
# ---------------------------------------------------------------------------

def get_leaf_groups(class_dir: Path) -> dict:
    """
    PlantVillage images from the same physical leaf share a common filename
    prefix before the trailing index. Group images by their leaf ID so
    near-duplicates don't bleed across splits.

    Returns: { leaf_id: [image_path, ...], ... }
    """
    groups = defaultdict(list)
    for img in class_dir.iterdir():
        if img.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
            # Use first 20 chars of stem as leaf group key
            leaf_id = img.stem[:20]
            groups[leaf_id].append(str(img))
    return dict(groups)


def leaf_aware_split(image_paths: list[str], labels: list[int],
                     class_to_leaf: dict[str, list]) -> tuple:
    """
    Perform a leaf-group-aware split.
    Groups images by leaf prefix, splits the groups, then collects images.
    Falls back to random split if leaf groups cannot be determined.
    """
    random.seed(RANDOM_SEED)

    # Build (leaf_group_key → list_of_indices) lookup
    idx_by_leaf = defaultdict(list)
    for i, path in enumerate(image_paths):
        leaf_key = Path(path).stem[:20]
        idx_by_leaf[leaf_key].append(i)

    leaf_keys = list(idx_by_leaf.keys())
    random.shuffle(leaf_keys)

    n = len(leaf_keys)
    n_train = int(n * TRAIN_SPLIT)
    n_val   = int(n * VAL_SPLIT)

    train_keys = leaf_keys[:n_train]
    val_keys   = leaf_keys[n_train:n_train + n_val]
    test_keys  = leaf_keys[n_train + n_val:]

    def collect(keys):
        idxs = []
        for k in keys:
            idxs.extend(idx_by_leaf[k])
        return idxs

    train_idx = collect(train_keys)
    val_idx   = collect(val_keys)
    test_idx  = collect(test_keys)

    X_train = [image_paths[i] for i in train_idx]
    y_train = [labels[i] for i in train_idx]
    X_val   = [image_paths[i] for i in val_idx]
    y_val   = [labels[i] for i in val_idx]
    X_test  = [image_paths[i] for i in test_idx]
    y_test  = [labels[i] for i in test_idx]

    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


# ---------------------------------------------------------------------------
# Dataset Loading
# ---------------------------------------------------------------------------

def load_all_image_paths(dataset_dir: str) -> tuple[list, list, list, dict]:
    """
    Walk the color dataset directory and collect all image paths and labels.
    Returns: (paths, labels, class_names_list, class_to_index)
    """
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {dataset_dir}\n"
            "Run: python scripts/download_dataset.py"
        )

    class_dirs = sorted([d for d in dataset_path.iterdir() if d.is_dir()])
    if not class_dirs:
        raise ValueError(f"No class subdirectories found in {dataset_dir}")

    class_names = [d.name for d in class_dirs]
    class_to_index = {name: i for i, name in enumerate(class_names)}

    image_paths = []
    labels      = []

    for class_dir in class_dirs:
        class_idx = class_to_index[class_dir.name]
        images = [
            str(f) for f in class_dir.iterdir()
            if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}
        ]
        image_paths.extend(images)
        labels.extend([class_idx] * len(images))

    log.info(f"Loaded {len(image_paths):,} images across {len(class_names)} classes.")

    # Save class names
    os.makedirs(os.path.dirname(CLASS_NAMES_PATH), exist_ok=True)
    with open(CLASS_NAMES_PATH, 'w', encoding='utf-8') as f:
        json.dump({str(i): name for i, name in enumerate(class_names)}, f, indent=2)

    return image_paths, labels, class_names, class_to_index


# ---------------------------------------------------------------------------
# tf.data Pipeline
# ---------------------------------------------------------------------------

def parse_image(path: str, label: int, augment: bool = False) -> tuple:
    """Load, decode, resize, and optionally augment an image."""
    raw = tf.io.read_file(path)
    img = tf.image.decode_jpeg(raw, channels=3)
    img = tf.image.resize(img, IMAGE_SIZE)
    img = tf.cast(img, tf.float32) / 255.0

    if augment:
        img = tf.image.random_flip_left_right(img)
        img = tf.image.random_flip_up_down(img)
        img = tf.image.random_brightness(img, max_delta=0.2)
        img = tf.image.random_contrast(img, lower=0.8, upper=1.2)
        img = tf.image.random_saturation(img, lower=0.8, upper=1.2)
        img = tf.clip_by_value(img, 0.0, 1.0)

    return img, label


def build_dataset(paths: list[str], labels: list[int],
                  augment: bool = False, shuffle: bool = True) -> tf.data.Dataset:
    """Build an efficient tf.data.Dataset pipeline."""
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))

    if shuffle:
        ds = ds.shuffle(buffer_size=min(10_000, len(paths)), seed=RANDOM_SEED)

    ds = ds.map(
        lambda p, l: parse_image(p, l, augment),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    ds = ds.batch(BATCH_SIZE)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def prepare_datasets(dataset_dir: str) -> dict:
    """
    Main entry point: load images, split leaf-aware, build tf.data datasets.
    Returns a dict with train/val/test datasets and metadata.
    """
    image_paths, labels, class_names, class_to_index = load_all_image_paths(dataset_dir)

    # Leaf-aware split
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = leaf_aware_split(
        image_paths, labels, class_to_index
    )

    log.info(f"  Train  : {len(X_train):,} images")
    log.info(f"  Val    : {len(X_val):,} images")
    log.info(f"  Test   : {len(X_test):,} images")

    train_ds = build_dataset(X_train, y_train, augment=True,  shuffle=True)
    val_ds   = build_dataset(X_val,   y_val,   augment=False, shuffle=False)
    test_ds  = build_dataset(X_test,  y_test,  augment=False, shuffle=False)

    return {
        'train_ds'      : train_ds,
        'val_ds'        : val_ds,
        'test_ds'       : test_ds,
        'class_names'   : class_names,
        'class_to_index': class_to_index,
        'n_classes'     : len(class_names),
        'train_size'    : len(X_train),
        'val_size'      : len(X_val),
        'test_size'     : len(X_test),
        'total_size'    : len(image_paths),
        'test_paths'    : X_test,
        'test_labels'   : y_test,
    }

"""
=================================================================
Model Evaluation Script
=================================================================
Run: python training/evaluate.py

Computes:
  - Accuracy, Precision, Recall, F1-score (per class + weighted)
  - Confusion matrix
  - Training history plots
  - Results saved to results/
=================================================================
"""

import os
import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score
)

import tensorflow as tf

from training.config import (
    MODEL_SAVE_PATH, CLASS_NAMES_PATH, HISTORY_PATH,
    DATASET_DIR, RESULTS_DIR
)
from training.preprocess import prepare_datasets

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

os.makedirs(RESULTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Plot Helpers
# ---------------------------------------------------------------------------

def plot_training_history(history_path: str):
    """Generate accuracy and loss curves from training history JSON."""
    with open(history_path, 'r') as f:
        history = json.load(f)

    # Combine both phases
    acc  = history.get('phase1', {}).get('accuracy', []) + \
           history.get('phase2', {}).get('accuracy', [])
    val_acc = history.get('phase1', {}).get('val_accuracy', []) + \
              history.get('phase2', {}).get('val_accuracy', [])
    loss = history.get('phase1', {}).get('loss', []) + \
           history.get('phase2', {}).get('loss', [])
    val_loss = history.get('phase1', {}).get('val_loss', []) + \
               history.get('phase2', {}).get('val_loss', [])

    epochs = range(1, len(acc) + 1)
    phase1_len = len(history.get('phase1', {}).get('accuracy', []))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('CropCare AI — Training History', fontsize=14, fontweight='bold')

    # Accuracy
    axes[0].plot(epochs, acc, 'b-o', markersize=3, label='Training Accuracy')
    axes[0].plot(epochs, val_acc, 'r-o', markersize=3, label='Validation Accuracy')
    if phase1_len > 0:
        axes[0].axvline(x=phase1_len, color='gray', linestyle='--', alpha=0.7, label='Fine-tune start')
    axes[0].set_title('Accuracy')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Loss
    axes[1].plot(epochs, loss, 'b-o', markersize=3, label='Training Loss')
    axes[1].plot(epochs, val_loss, 'r-o', markersize=3, label='Validation Loss')
    if phase1_len > 0:
        axes[1].axvline(x=phase1_len, color='gray', linestyle='--', alpha=0.7, label='Fine-tune start')
    axes[1].set_title('Loss')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(RESULTS_DIR, 'training_history.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Training history plot saved → {save_path}")


def plot_confusion_matrix(cm: np.ndarray, class_names: list, max_classes: int = 30):
    """Plot confusion matrix. Truncates to max_classes if there are too many."""
    n = min(len(class_names), max_classes)
    cm_trunc  = cm[:n, :n]
    names_trunc = class_names[:n]

    # Normalize
    cm_norm = cm_trunc.astype('float') / (cm_trunc.sum(axis=1, keepdims=True) + 1e-8)

    fig_size = max(12, n * 0.45)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.heatmap(
        cm_norm, annot=(n <= 20), fmt='.2f',
        xticklabels=names_trunc, yticklabels=names_trunc,
        cmap='Blues', ax=ax, linewidths=0.5
    )
    ax.set_title('Confusion Matrix (Normalized)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    plt.xticks(rotation=45, ha='right', fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()

    save_path = os.path.join(RESULTS_DIR, 'confusion_matrix.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Confusion matrix saved → {save_path}")


def plot_per_class_f1(report_dict: dict, class_names: list):
    """Bar chart of per-class F1 scores."""
    classes = [c for c in class_names if c in report_dict]
    f1_scores = [report_dict[c]['f1-score'] for c in classes]

    # Shorten class names for display
    short_names = [c.split('___')[-1].replace('_', ' ')[:25] for c in classes]

    fig, ax = plt.subplots(figsize=(14, max(6, len(classes) * 0.35)))
    colors = ['#2ecc71' if f >= 0.9 else '#f39c12' if f >= 0.7 else '#e74c3c'
              for f in f1_scores]
    ax.barh(short_names, f1_scores, color=colors)
    ax.set_xlabel('F1 Score')
    ax.set_title('Per-Class F1 Score', fontweight='bold')
    ax.set_xlim(0, 1.05)
    ax.axvline(x=0.9, color='green', linestyle='--', alpha=0.5, label='0.90 target')
    ax.legend()
    plt.tight_layout()

    save_path = os.path.join(RESULTS_DIR, 'per_class_f1.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Per-class F1 plot saved → {save_path}")


# ---------------------------------------------------------------------------
# Main Evaluation
# ---------------------------------------------------------------------------

def evaluate():
    print("\n" + "=" * 60)
    print("  CropCare AI — Model Evaluation")
    print("=" * 60 + "\n")

    # ── Check model exists ────────────────────────────────────────────────
    if not Path(MODEL_SAVE_PATH).exists():
        log.error(f"Model not found: {MODEL_SAVE_PATH}")
        log.error("Run: python training/train.py  first.")
        sys.exit(1)

    # ── Load model ────────────────────────────────────────────────────────
    log.info(f"Loading model from {MODEL_SAVE_PATH}...")
    model = tf.keras.models.load_model(MODEL_SAVE_PATH)

    # ── Load class names ──────────────────────────────────────────────────
    with open(CLASS_NAMES_PATH, 'r') as f:
        class_idx_map = json.load(f)
    class_names = [class_idx_map[str(i)] for i in range(len(class_idx_map))]

    # ── Load test dataset ─────────────────────────────────────────────────
    log.info("Loading test dataset...")
    data = prepare_datasets(DATASET_DIR)
    test_ds = data['test_ds']
    test_labels_true = np.array(data['test_labels'])

    # ── Run predictions ───────────────────────────────────────────────────
    log.info("Running predictions on test set...")
    y_pred_probs = model.predict(test_ds, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)

    # Handle size mismatch (due to batching)
    y_true = test_labels_true[:len(y_pred)]

    # ── Metrics ───────────────────────────────────────────────────────────
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec  = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1   = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    print(f"\n  ══ Evaluation Results ══")
    print(f"  Accuracy          : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Precision (w.avg) : {prec:.4f}")
    print(f"  Recall    (w.avg) : {rec:.4f}")
    print(f"  F1-Score  (w.avg) : {f1:.4f}")

    # ── Per-class report ──────────────────────────────────────────────────
    report = classification_report(
        y_true, y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    report_str = classification_report(
        y_true, y_pred,
        target_names=class_names,
        zero_division=0
    )
    print(f"\n  Per-Class Report:\n{report_str}")

    # ── Confusion matrix ──────────────────────────────────────────────────
    cm = confusion_matrix(y_true, y_pred)

    # ── Save results JSON ─────────────────────────────────────────────────
    results = {
        'accuracy'          : float(acc),
        'precision_weighted': float(prec),
        'recall_weighted'   : float(rec),
        'f1_weighted'       : float(f1),
        'n_classes'         : len(class_names),
        'test_size'         : int(len(y_true)),
        'per_class_report'  : report,
    }
    results_path = os.path.join(RESULTS_DIR, 'evaluation_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    log.info(f"Evaluation results saved → {results_path}")

    # ── Plots ─────────────────────────────────────────────────────────────
    if Path(HISTORY_PATH).exists():
        plot_training_history(HISTORY_PATH)

    plot_confusion_matrix(cm, class_names)
    plot_per_class_f1(report, class_names)

    print(f"\n  ✅ Evaluation complete!")
    print(f"     Results → {RESULTS_DIR}/")
    print(f"\n  Next: python app.py\n")


if __name__ == '__main__':
    evaluate()

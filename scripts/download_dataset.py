"""
=================================================================
Dataset Download & Setup Script
=================================================================
Run: python scripts/download_dataset.py

This script:
  1. Clones the PlantVillage dataset repository (git-lfs required)
  2. Locates the RGB/color images
  3. Identifies all disease classes
  4. Generates models/class_names.json
  5. Checks for corrupted images
  6. Counts images per class
  7. Produces dataset/dataset_report.json
=================================================================
"""

import os
import sys
import json
import shutil
import subprocess
import hashlib
import logging
from pathlib import Path
from collections import Counter

# ── Try to import PIL for image validation ────────────────────────────────
try:
    from PIL import Image, UnidentifiedImageError
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARNING] Pillow not installed. Skipping image integrity checks.")
    print("         Run: pip install Pillow")

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR     = Path(__file__).resolve().parent.parent
DATASET_DIR  = BASE_DIR / 'dataset'
CLONE_DIR    = DATASET_DIR / 'plantvillage'
COLOR_DIR    = CLONE_DIR / 'raw' / 'color'
MODELS_DIR   = BASE_DIR / 'models'
REPORT_PATH  = DATASET_DIR / 'dataset_report.json'
CLASS_NAMES_PATH = MODELS_DIR / 'class_names.json'

REPO_URL = 'https://github.com/spMohanty/PlantVillage-Dataset.git'

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_cmd(cmd: list[str], cwd: Path = None) -> int:
    """Run a shell command and stream its output."""
    log.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    return result.returncode


def check_git():
    """Ensure git is available."""
    rc = run_cmd(['git', '--version'])
    if rc != 0:
        log.error("git is not installed. Install it from https://git-scm.com/")
        sys.exit(1)


def check_git_lfs():
    """Check if git-lfs is installed; warn if not."""
    rc = subprocess.run(['git', 'lfs', 'version'], capture_output=True).returncode
    if rc != 0:
        log.warning("git-lfs is NOT installed. Large image files may not download.")
        log.warning("Install git-lfs: https://git-lfs.github.com/")
        return False
    return True


def clone_or_update_repo():
    """Clone the PlantVillage repo, or pull if it already exists."""
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    if CLONE_DIR.exists() and (CLONE_DIR / '.git').exists():
        log.info("Repository already cloned — pulling latest changes...")
        run_cmd(['git', 'pull'], cwd=CLONE_DIR)
        run_cmd(['git', 'lfs', 'pull'], cwd=CLONE_DIR)
    else:
        log.info(f"Cloning PlantVillage Dataset from {REPO_URL} ...")
        run_cmd(['git', 'clone', REPO_URL, str(CLONE_DIR)])
        if (CLONE_DIR / '.git').exists():
            run_cmd(['git', 'lfs', 'pull'], cwd=CLONE_DIR)


def find_color_directory() -> Path:
    """Find the RGB/color image directory in the repo."""
    candidates = [
        CLONE_DIR / 'raw' / 'color',
        CLONE_DIR / 'Dataset' / 'PlantVillage' / 'raw' / 'color',
        CLONE_DIR / 'color',
    ]
    for c in candidates:
        if c.exists():
            log.info(f"Found color image directory: {c}")
            return c

    # Search recursively for any 'color' folder containing subdirectories
    for p in CLONE_DIR.rglob('color'):
        if p.is_dir():
            log.info(f"Found color directory via search: {p}")
            return p

    log.error("Could not find color image directory in the repository.")
    log.error(f"Expected at: {CLONE_DIR / 'raw' / 'color'}")
    log.error("The repository may not have downloaded correctly (git-lfs required).")
    return None


def gather_class_info(color_dir: Path) -> dict:
    """Walk the color directory and collect class/image information."""
    class_info = {}
    corrupted = []

    class_dirs = sorted([d for d in color_dir.iterdir() if d.is_dir()])

    if not class_dirs:
        log.error("No class subdirectories found. Dataset may not have downloaded.")
        return {}, []

    log.info(f"Found {len(class_dirs)} class directories.")

    for idx, class_dir in enumerate(class_dirs):
        class_name = class_dir.name
        images = [
            f for f in class_dir.iterdir()
            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png'}
        ]

        valid_images = []
        class_corrupted = 0

        for img_path in images:
            if PIL_AVAILABLE:
                try:
                    with Image.open(img_path) as im:
                        im.verify()
                    valid_images.append(str(img_path))
                except (UnidentifiedImageError, Exception):
                    corrupted.append(str(img_path))
                    class_corrupted += 1
            else:
                valid_images.append(str(img_path))

        # Parse crop and disease from directory name (e.g., "Tomato___Early_blight")
        parts = class_name.split('___')
        crop    = parts[0].replace('_', ' ') if len(parts) > 0 else 'Unknown'
        disease = parts[1].replace('_', ' ') if len(parts) > 1 else 'Unknown'
        is_healthy = 'healthy' in disease.lower()

        class_info[class_name] = {
            'index'       : idx,
            'class_key'   : class_name,
            'crop'        : crop,
            'disease'     : disease,
            'is_healthy'  : is_healthy,
            'total_images': len(images),
            'valid_images': len(valid_images),
            'corrupted'   : class_corrupted,
        }

        log.info(f"  [{idx:02d}] {class_name}: {len(valid_images)} valid images")

    return class_info, corrupted


def save_class_names(class_info: dict):
    """Save class name index → class key mapping as JSON."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    class_names = {v['index']: k for k, v in class_info.items()}
    with open(CLASS_NAMES_PATH, 'w', encoding='utf-8') as f:
        json.dump(class_names, f, indent=2, ensure_ascii=False)
    log.info(f"Saved class names to {CLASS_NAMES_PATH}")


def save_report(class_info: dict, corrupted: list, color_dir: Path):
    """Generate and save dataset_report.json."""
    total_images = sum(v['valid_images'] for v in class_info.values())
    n_healthy    = sum(1 for v in class_info.values() if v['is_healthy'])
    n_disease    = len(class_info) - n_healthy

    report = {
        'repository_url'     : REPO_URL,
        'color_directory'    : str(color_dir),
        'total_classes'      : len(class_info),
        'healthy_classes'    : n_healthy,
        'disease_classes'    : n_disease,
        'total_images'       : total_images,
        'corrupted_images'   : len(corrupted),
        'corrupted_files'    : corrupted[:50],  # first 50 for brevity
        'per_class'          : class_info,
    }

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log.info(f"Saved dataset report to {REPORT_PATH}")
    return report


def print_summary(report: dict):
    """Print a formatted summary."""
    print("\n" + "=" * 60)
    print("  PLANTVILLAGE DATASET REPORT")
    print("=" * 60)
    print(f"  Total Classes   : {report['total_classes']}")
    print(f"  Healthy Classes : {report['healthy_classes']}")
    print(f"  Disease Classes : {report['disease_classes']}")
    print(f"  Total Images    : {report['total_images']:,}")
    print(f"  Corrupted       : {report['corrupted_images']}")
    print("=" * 60)
    print(f"\n  Class Names saved → {CLASS_NAMES_PATH}")
    print(f"  Full Report     → {REPORT_PATH}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("  CropCare AI — Dataset Setup")
    print("=" * 60 + "\n")

    check_git()
    has_lfs = check_git_lfs()

    clone_or_update_repo()

    color_dir = find_color_directory()
    if color_dir is None:
        print("\n[ERROR] Dataset directory not found.")
        print("        Make sure git-lfs is installed and try again.")
        sys.exit(1)

    log.info("Gathering class information and checking images...")
    class_info, corrupted = gather_class_info(color_dir)

    if not class_info:
        print("\n[ERROR] No classes found. The dataset may not have downloaded properly.")
        sys.exit(1)

    save_class_names(class_info)
    report = save_report(class_info, corrupted, color_dir)
    print_summary(report)

    print("  ✅ Dataset setup complete!")
    print("  Next step: python training/train.py\n")


if __name__ == '__main__':
    main()

"""
=================================================================
Image Processor — Upload Validation & Preprocessing
=================================================================
Handles:
  - File extension validation
  - File size validation
  - Magic bytes verification (prevents fake extensions)
  - Secure filename generation
  - Image resizing and normalization
=================================================================
"""

import os
import io
import uuid
import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
IMAGE_SIZE = (224, 224)

# Magic bytes for image format verification
MAGIC_BYTES = {
    b'\xff\xd8\xff'       : 'jpeg',   # JPEG
    b'\x89PNG\r\n\x1a\n'  : 'png',    # PNG
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ImageValidationError(Exception):
    """Raised when an uploaded image fails validation."""
    pass


def allowed_extension(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def verify_magic_bytes(file_bytes: bytes) -> bool:
    """Verify the actual file format using magic bytes, not just extension."""
    for magic, fmt in MAGIC_BYTES.items():
        if file_bytes[:len(magic)] == magic:
            return True
    return False


def validate_upload(file: FileStorage, max_size: int = MAX_FILE_SIZE_BYTES) -> bytes:
    """
    Validate an uploaded FileStorage object.
    Returns raw file bytes if valid.
    Raises ImageValidationError on failure.
    """
    if file is None or file.filename == '':
        raise ImageValidationError("No file was uploaded.")

    filename = file.filename.strip()

    # Extension check
    if not allowed_extension(filename):
        raise ImageValidationError(
            f"Invalid file type. Only JPG, JPEG, and PNG files are allowed."
        )

    # Read bytes
    file.seek(0)
    file_bytes = file.read()

    # Size check
    if len(file_bytes) > max_size:
        raise ImageValidationError(
            f"File too large. Maximum allowed size is {max_size // (1024*1024)} MB."
        )

    if len(file_bytes) == 0:
        raise ImageValidationError("Uploaded file is empty.")

    # Magic bytes check (prevents executable files with image extensions)
    if not verify_magic_bytes(file_bytes):
        raise ImageValidationError(
            "File content does not match a valid image format. "
            "Please upload a real JPG or PNG image."
        )

    # Try to open with PIL to confirm it's a decodable image
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()  # Check for corruption
    except (UnidentifiedImageError, Exception) as e:
        raise ImageValidationError(f"Image appears to be corrupted or invalid: {e}")

    return file_bytes


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def save_upload(file_bytes: bytes, original_filename: str,
                upload_folder: str) -> str:
    """
    Save validated image bytes to the upload folder with a secure unique name.
    Returns the saved filename (not full path).
    """
    ext = original_filename.rsplit('.', 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(upload_folder, unique_name)

    os.makedirs(upload_folder, exist_ok=True)

    with open(save_path, 'wb') as f:
        f.write(file_bytes)

    log.info(f"Saved upload: {save_path}")
    return unique_name


# ---------------------------------------------------------------------------
# Preprocessing for Model
# ---------------------------------------------------------------------------

def preprocess_for_model(image_path: str) -> np.ndarray:
    """
    Load an image from disk, resize to 224×224, convert to RGB,
    normalize to [0, 1], and add batch dimension.

    Returns: np.ndarray of shape (1, 224, 224, 3)
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMAGE_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)  # (1, 224, 224, 3)


def preprocess_from_bytes(file_bytes: bytes) -> np.ndarray:
    """
    Load image from raw bytes, resize, normalize, and add batch dimension.
    Returns: np.ndarray of shape (1, 224, 224, 3)
    """
    img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    img = img.resize(IMAGE_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------

def process_upload(file: FileStorage, upload_folder: str,
                   max_size: int = MAX_FILE_SIZE_BYTES) -> Tuple[str, np.ndarray]:
    """
    Full upload pipeline:
      validate → save → preprocess

    Returns:
      (saved_filename: str, preprocessed_array: np.ndarray)
    Raises:
      ImageValidationError on any failure.
    """
    file_bytes = validate_upload(file, max_size)
    filename   = save_upload(file_bytes, file.filename, upload_folder)
    image_path = os.path.join(upload_folder, filename)
    arr        = preprocess_for_model(image_path)
    return filename, arr

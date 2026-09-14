/**
 * CropCare AI — Main JavaScript
 * Handles: upload, drag-drop, camera, image preview,
 *          language switching, navbar, user menu, flash auto-dismiss
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Language ──────────────────────────────────────────────────────────
  const lang = document.body.dataset.lang || 'en';
  if (window.applyTranslations) applyTranslations(lang);

  // ── Navbar Scroll ─────────────────────────────────────────────────────
  const navbar = document.getElementById('main-navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // ── Mobile Nav Toggle ─────────────────────────────────────────────────
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.getElementById('navLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  // ── User Dropdown ─────────────────────────────────────────────────────
  const userMenuBtn   = document.getElementById('userMenuBtn');
  const userDropdown  = document.getElementById('userDropdown');
  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('open');
    });
    document.addEventListener('click', () => userDropdown.classList.remove('open'));
  }

  // ── Flash Auto-Dismiss ────────────────────────────────────────────────
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.opacity = '0';
      f.style.transition = 'opacity 0.4s';
      setTimeout(() => f.remove(), 400);
    }, 5000);
  });

  // ── Upload / Drag-Drop / Preview ──────────────────────────────────────
  const dropZone    = document.getElementById('dropZone');
  const leafInput   = document.getElementById('leafInput');
  const imagePreview= document.getElementById('imagePreview');
  const dropIcon    = document.getElementById('dropIcon');
  const dropText    = document.getElementById('dropText');
  const detectBtn   = document.getElementById('detectBtn');
  const detectSpinner = document.getElementById('detectSpinner');
  const uploadForm  = document.getElementById('uploadForm');

  if (dropZone && leafInput) {
    // Click on zone → trigger file picker
    dropZone.addEventListener('click', (e) => {
      if (e.target !== leafInput) leafInput.click();
    });
    dropZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') leafInput.click();
    });

    // Drag events
    ['dragenter', 'dragover'].forEach(evt => {
      dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
      });
    });
    ['dragleave', 'drop'].forEach(evt => {
      dropZone.addEventListener(evt, () => dropZone.classList.remove('dragover'));
    });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        // Create a DataTransfer to set the file input value
        const dt = new DataTransfer();
        dt.items.add(files[0]);
        leafInput.files = dt.files;
        handleFileSelected(files[0]);
      }
    });

    // File input change
    leafInput.addEventListener('change', () => {
      if (leafInput.files.length > 0) {
        handleFileSelected(leafInput.files[0]);
      }
    });
  }

  function handleFileSelected(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      showAlert('Only JPG and PNG images are allowed.', 'danger');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      showAlert('File size must not exceed 5 MB.', 'danger');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (imagePreview) {
        imagePreview.src = e.target.result;
        imagePreview.classList.remove('hidden');
      }
      if (dropIcon) dropIcon.classList.add('hidden');
      if (dropText) dropText.querySelector('.drop-main').textContent = file.name;
      if (dropText) dropText.querySelector('.drop-sub').textContent =
        `${(file.size / 1024).toFixed(0)} KB — Click to change`;
    };
    reader.readAsDataURL(file);

    if (detectBtn) detectBtn.disabled = false;
  }

  // ── Form Submit with Loading State ────────────────────────────────────
  if (uploadForm) {
    uploadForm.addEventListener('submit', (e) => {
      if (!leafInput || leafInput.files.length === 0) {
        e.preventDefault();
        showAlert('Please select or capture an image first.', 'danger');
        return;
      }
      if (detectBtn) {
        detectBtn.disabled = true;
        if (detectSpinner) detectSpinner.classList.remove('hidden');
        detectBtn.querySelector('span[data-i18n]').textContent = 'Analyzing...';
      }
    });
  }

  // ── Camera Capture ────────────────────────────────────────────────────
  const cameraBtn       = document.getElementById('cameraBtn');
  const cameraContainer = document.getElementById('cameraContainer');
  const cameraVideo     = document.getElementById('cameraVideo');
  const captureBtn      = document.getElementById('captureBtn');
  const cancelCameraBtn = document.getElementById('cancelCameraBtn');
  const captureCanvas   = document.getElementById('captureCanvas');

  let cameraStream = null;

  if (cameraBtn && cameraContainer) {
    cameraBtn.addEventListener('click', async () => {
      try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });
        cameraVideo.srcObject = cameraStream;
        cameraContainer.classList.remove('hidden');
        cameraBtn.classList.add('hidden');
      } catch (err) {
        showAlert('Camera not available: ' + err.message, 'warning');
      }
    });

    if (cancelCameraBtn) {
      cancelCameraBtn.addEventListener('click', () => {
        stopCamera();
      });
    }

    if (captureBtn) {
      captureBtn.addEventListener('click', () => {
        if (!cameraVideo || !captureCanvas) return;
        captureCanvas.width  = cameraVideo.videoWidth;
        captureCanvas.height = cameraVideo.videoHeight;
        captureCanvas.getContext('2d').drawImage(cameraVideo, 0, 0);

        captureCanvas.toBlob((blob) => {
          const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
          const dt = new DataTransfer();
          dt.items.add(file);
          leafInput.files = dt.files;
          handleFileSelected(file);
          stopCamera();
        }, 'image/jpeg', 0.92);
      });
    }
  }

  function stopCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(t => t.stop());
      cameraStream = null;
    }
    if (cameraContainer) cameraContainer.classList.add('hidden');
    if (cameraBtn) cameraBtn.classList.remove('hidden');
  }

  // ── Alert Helper ──────────────────────────────────────────────────────
  function showAlert(message, type = 'info') {
    const container = document.getElementById('flashContainer') ||
      (() => {
        const c = document.createElement('div');
        c.className = 'flash-container'; c.id = 'flashContainer';
        document.body.appendChild(c); return c;
      })();

    const icons = { success: 'bi-check-circle-fill', danger: 'bi-exclamation-triangle-fill',
                    warning: 'bi-exclamation-circle-fill', info: 'bi-info-circle-fill' };
    const div = document.createElement('div');
    div.className = `flash flash--${type}`;
    div.innerHTML = `<i class="bi ${icons[type] || icons.info}"></i><span>${message}</span>
      <button class="flash-close" onclick="this.parentElement.remove()"><i class="bi bi-x"></i></button>`;
    container.appendChild(div);
    setTimeout(() => { div.style.opacity='0'; div.style.transition='opacity 0.4s'; setTimeout(()=>div.remove(),400); }, 5000);
  }

  // ── Confidence Bar Animation (result page) ────────────────────────────
  const confBar = document.getElementById('confBar');
  if (confBar) {
    const target = confBar.style.width;
    confBar.style.width = '0%';
    confBar.style.transition = 'width 1s cubic-bezier(0.4,0,0.2,1)';
    setTimeout(() => { confBar.style.width = target; }, 200);
  }

}); // DOMContentLoaded

// ── Image preview ────────────────────────────────────────────────────────────

function previewImage(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const preview = document.getElementById('imgPreview');
    const prompt  = document.getElementById('uploadPrompt');
    preview.src = e.target.result;
    preview.style.display = 'block';
    prompt.style.display  = 'none';
  };
  reader.readAsDataURL(file);
}

// Drag & drop support
document.addEventListener('DOMContentLoaded', function() {
  const area = document.getElementById('uploadArea');
  if (!area) return;

  area.addEventListener('dragover', function(e) {
    e.preventDefault();
    area.style.background = '#dceefb';
    area.style.borderColor = '#1a6db5';
  });

  area.addEventListener('dragleave', function() {
    area.style.background = '';
    area.style.borderColor = '';
  });

  area.addEventListener('drop', function(e) {
    e.preventDefault();
    area.style.background = '';
    area.style.borderColor = '';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const input = document.getElementById('image');
      input.files = files;
      previewImage({ target: input });
    }
  });
});


// ── Form submission ───────────────────────────────────────────────────────────

async function submitForm(event) {
  event.preventDefault();

  const btn     = document.getElementById('calcBtn');
  const errorBox = document.getElementById('errorBox');
  errorBox.style.display = 'none';
  errorBox.innerHTML = '';

  btn.disabled   = true;
  btn.textContent = '⏳ Calculating…';

  const form = document.getElementById('calcForm');
  const data = new FormData(form);

  try {
    const response = await fetch('/calculate', { method: 'POST', body: data });
    const result   = await response.json();

    if (!result.success) {
      errorBox.innerHTML = result.errors.map(e => `<p>⚠ ${e}</p>`).join('');
      errorBox.style.display = 'block';
      return;
    }

    displayResult(result);

  } catch (err) {
    errorBox.innerHTML = `<p>⚠ Network error: ${err.message}</p>`;
    errorBox.style.display = 'block';
  } finally {
    btn.disabled    = false;
    btn.textContent = '⚗ Calculate Real Size';
  }
}


// ── Display result ────────────────────────────────────────────────────────────

function displayResult(r) {
  const card    = document.getElementById('resultCard');
  const content = document.getElementById('resultContent');

  const rows = [
    ['Performed by',   r.username],
    ['Microscope Type', r.mic_name],
    ['Magnification',  `×${r.magnification.toLocaleString()}`],
    ['Measured Size',  `${r.measured_mm} mm`],
    ['Formula',        'Real Size = Measured Size ÷ Magnification'],
    ['Calculation',    `${r.measured_mm} ÷ ${r.magnification.toLocaleString()} = ${r.real_size_mm.toExponential(4)} mm`],
  ];

  let html = rows.map(([label, val]) =>
    `<div class="result-row">
       <span class="result-label">${label}:</span>
       <span>${val}</span>
     </div>`
  ).join('');

  html += `
    <div class="result-row" style="border-top:1px solid #334; margin-top:8px; padding-top:8px;">
      <span class="result-label result-final">✓ REAL SIZE:</span>
      <span class="result-final">${r.real_size_disp.toFixed(6)} ${r.unit_name}</span>
    </div>`;

  if (r.image_url) {
    html += `<div class="result-img"><img src="${r.image_url}" alt="Specimen"/></div>`;
  }

  content.innerHTML = html;
  card.style.display = 'block';
  card.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

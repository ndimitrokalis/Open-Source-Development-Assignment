/* =============================================================================
   create_article.js — handles the new-article form submission.
   Sends POST /articles (JSON) and redirects to the articles list on success.
   ============================================================================= */

const form      = document.getElementById('create-article-form');
const alertBox  = document.getElementById('alert-box');
const submitBtn = document.getElementById('submit-btn');
const btnText   = document.getElementById('btn-text');
const spinner   = document.getElementById('spinner');

/* ── Helpers ─────────────────────────────────────────────────────────────────── */

function showAlert(msg, type) {
  alertBox.textContent = msg;
  alertBox.className   = 'alert alert-' + type;
  alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function setLoading(on) {
  submitBtn.disabled = on;
  btnText.classList.toggle('d-none', on);
  spinner.classList.toggle('d-none', !on);
}

/* ── Title character counter ─────────────────────────────────────────────────── */

const titleInput = document.getElementById('title');
const titleCount = document.getElementById('title-count');

titleInput.addEventListener('input', () => {
  const len = titleInput.value.length;
  titleCount.textContent = len;
  titleCount.classList.toggle('near-limit', len >= 160 && len < 200);
  titleCount.classList.toggle('at-limit',   len >= 200);
});

/* ── File preview ────────────────────────────────────────────────────────────── */

const fileInput   = document.getElementById('attachments');
const filePreview = document.getElementById('file-preview');

fileInput.addEventListener('change', () => {
  filePreview.innerHTML = '';
  Array.from(fileInput.files).forEach(f => {
    const chip = document.createElement('span');
    chip.className = 'file-chip';
    chip.innerHTML = `<i class="bi bi-paperclip"></i>${f.name}`;
    filePreview.appendChild(chip);
  });
});

/* ── Form submit ─────────────────────────────────────────────────────────────── */

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const title       = titleInput.value.trim();
  const type        = document.getElementById('type').value;
  const content     = document.getElementById('content').value.trim();
  const attachments = Array.from(fileInput.files).map(f => f.name);

  /* Client-side validation */
  if (!title) {
    showAlert('Title is required.', 'danger');
    titleInput.focus();
    return;
  }
  if (title.length > 200) {
    showAlert('Title must be 200 characters or fewer.', 'danger');
    titleInput.focus();
    return;
  }
  if (!type) {
    showAlert('Please select an article type.', 'danger');
    document.getElementById('type').focus();
    return;
  }
  if (!content) {
    showAlert('Content is required.', 'danger');
    document.getElementById('content').focus();
    return;
  }

  setLoading(true);
  try {
    const res  = await fetch('/articles', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ title, type, content, attachments })
    });
    const data = await res.json();

    if (res.ok) {
      showAlert('Article published! Redirecting…', 'success');
      setTimeout(() => { window.location.href = '/dashboard'; }, 700);
    } else {
      showAlert(data.error || 'Failed to create article.', 'danger');
      setLoading(false);
    }
  } catch {
    showAlert('Network error. Please try again.', 'danger');
    setLoading(false);
  }
});

/* =============================================================================
   create_ticket.js — handles the new-ticket form submission.
   Sends POST /tickets (JSON) and redirects to the created ticket's detail page.
   ============================================================================= */

const form      = document.getElementById('create-form');
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
    chip.className   = 'file-chip';
    chip.innerHTML   = `<i class="bi bi-paperclip"></i>${f.name}`;
    filePreview.appendChild(chip);
  });
});

/* ── Form submit ─────────────────────────────────────────────────────────────── */

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  /* Collect values */
  const title       = titleInput.value.trim();
  const type        = document.getElementById('type').value;
  const priority    = document.getElementById('priority').checked;
  const description = document.getElementById('description').value.trim() || null;
  const company     = document.getElementById('company').value.trim() || null;
  const done_by     = document.getElementById('done_by').value || null;
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

  setLoading(true);
  try {
    const res  = await fetch('/tickets', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ title, type, priority, description, company, done_by, attachments })
    });
    const data = await res.json();

    if (res.ok) {
      showAlert('Ticket created! Redirecting…', 'success');
      /* Redirect to the new ticket's detail page */
      setTimeout(() => { window.location.href = '/tickets/' + data.ticket.id; }, 700);
    } else {
      showAlert(data.error || 'Failed to create ticket.', 'danger');
      setLoading(false);
    }
  } catch {
    showAlert('Network error. Please try again.', 'danger');
    setLoading(false);
  }
});

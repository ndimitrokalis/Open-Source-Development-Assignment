/* =============================================================================
   update_ticket.js — ticket detail page interactions.
   "Update" means posting a comment only — no editing of ticket fields.

   Actions handled:
     • Post a comment      POST /tickets/<id>/comments
     • Delete a comment    DELETE /tickets/<id>/comments/<commentId>
     • Assign technician   POST /tickets/<id>/assign        (manager / admin)
     • Close ticket        POST /tickets/<id>/close         (staff only)
   ============================================================================= */

const TICKET_ID = parseInt(
  document.getElementById('ticket-container').dataset.ticketId,
  10
);

const alertBox = document.getElementById('alert-box');

/* ── Helpers ─────────────────────────────────────────────────────────────────── */

function showAlert(msg, type) {
  alertBox.textContent = msg;
  alertBox.className   = 'alert alert-' + type;
  alertBox.classList.remove('d-none');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ── Character counter ───────────────────────────────────────────────────────── */

const commentBody = document.getElementById('comment-body');
const charCount   = document.getElementById('char-count');

if (commentBody && charCount) {
  commentBody.addEventListener('input', () => {
    charCount.textContent = commentBody.value.length;
  });
}

/* ── Post comment ────────────────────────────────────────────────────────────── */

const commentForm    = document.getElementById('comment-form');
const commentBtn     = document.getElementById('comment-btn');
const commentBtnText = document.getElementById('comment-btn-text');
const commentSpinner = document.getElementById('comment-spinner');

if (commentForm) {
  commentForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const body = commentBody.value.trim();
    if (!body) {
      showAlert('Comment cannot be empty.', 'warning');
      commentBody.focus();
      return;
    }
    if (body.length > 5000) {
      showAlert('Comment must be 5000 characters or fewer.', 'warning');
      return;
    }

    /* Loading state */
    commentBtn.disabled = true;
    commentBtnText.classList.add('d-none');
    commentSpinner.classList.remove('d-none');

    try {
      const res  = await fetch(`/tickets/${TICKET_ID}/comments`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ body })
      });
      const data = await res.json();

      if (res.ok) {
        /* Reload to show the new comment in the thread */
        window.location.reload();
      } else {
        showAlert(data.error || 'Failed to post comment.', 'danger');
        commentBtn.disabled = false;
        commentBtnText.classList.remove('d-none');
        commentSpinner.classList.add('d-none');
      }
    } catch {
      showAlert('Network error. Please try again.', 'danger');
      commentBtn.disabled = false;
      commentBtnText.classList.remove('d-none');
      commentSpinner.classList.add('d-none');
    }
  });
}

/* ── Delete comment ──────────────────────────────────────────────────────────── */

/* Called by the inline onclick on each comment's delete button */
async function deleteComment(commentId) {
  if (!confirm('Delete this comment?')) return;

  try {
    const res  = await fetch(`/tickets/${TICKET_ID}/comments/${commentId}`, {
      method: 'DELETE'
    });
    const data = await res.json();

    if (res.ok) {
      window.location.reload();
    } else {
      showAlert(data.error || 'Failed to delete comment.', 'danger');
    }
  } catch {
    showAlert('Network error. Please try again.', 'danger');
  }
}

/* ── Close ticket ────────────────────────────────────────────────────────────── */

const closeBtn = document.getElementById('close-btn');

if (closeBtn) {
  closeBtn.addEventListener('click', async () => {
    if (!confirm('Mark this ticket as Done? This cannot be undone here.')) return;

    closeBtn.disabled = true;

    try {
      const res  = await fetch(`/tickets/${TICKET_ID}/close`, { method: 'POST' });
      const data = await res.json();

      if (res.ok) {
        window.location.reload();
      } else {
        showAlert(data.error || 'Failed to close ticket.', 'danger');
        closeBtn.disabled = false;
      }
    } catch {
      showAlert('Network error. Please try again.', 'danger');
      closeBtn.disabled = false;
    }
  });
}

/* ── Assign technician ───────────────────────────────────────────────────────── */

const assignForm = document.getElementById('assign-form');

if (assignForm) {
  assignForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const raw         = document.getElementById('assignee-select').value;
    const assignee_id = raw === '' ? null : parseInt(raw, 10);

    try {
      const res  = await fetch(`/tickets/${TICKET_ID}/assign`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ assignee_id })
      });
      const data = await res.json();

      if (res.ok) {
        window.location.reload();
      } else {
        showAlert(data.error || 'Failed to assign ticket.', 'danger');
      }
    } catch {
      showAlert('Network error. Please try again.', 'danger');
    }
  });
}

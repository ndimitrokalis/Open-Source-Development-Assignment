function togglePw(id) {
  const el = document.getElementById(id);
  el.type = el.type === 'password' ? 'text' : 'password';
}

document.getElementById('rem-label').addEventListener('click', function(e) {
  e.preventDefault();
  const cb  = document.getElementById('remember');
  const box = document.getElementById('rem-box');
  cb.checked = !cb.checked;
  box.textContent   = cb.checked ? '✓' : '';
  box.style.background  = cb.checked ? '#6366f1' : 'rgba(255,255,255,.03)';
  box.style.borderColor = cb.checked ? '#6366f1' : 'rgba(255,255,255,.12)';
});

const form      = document.getElementById('login-form');
const alertBox  = document.getElementById('alert-box');
const submitBtn = document.getElementById('submit-btn');
const btnText   = document.getElementById('btn-text');
const spinner   = document.getElementById('spinner');

function showAlert(msg, type) {
  alertBox.textContent = msg;
  alertBox.className   = 'alert ' + type;
}
function setLoading(on) {
  submitBtn.disabled    = on;
  btnText.style.display = on ? 'none'  : 'inline';
  spinner.style.display = on ? 'block' : 'none';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  alertBox.className = 'alert';

  const identifier = document.getElementById('identifier').value.trim();
  const password   = document.getElementById('password').value;
  const remember   = document.getElementById('remember').checked;

  if (!identifier || !password) {
    showAlert('Please fill in all fields.', 'error');
    return;
  }

  setLoading(true);
  try {
    const res  = await fetch('/login', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ username: identifier, password, remember })
    });
    const data = await res.json();
    if (res.ok) {
      showAlert('Login successful! Redirecting…', 'success');
      setTimeout(() => { window.location.href = '/dashboard'; }, 800);
    } else {
      showAlert(data.error || 'Login failed.', 'error');
    }
  } catch {
    showAlert('Network error. Please try again.', 'error');
  } finally {
    setLoading(false);
  }
});
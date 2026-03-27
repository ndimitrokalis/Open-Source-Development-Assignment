function togglePw(id) {
  const el = document.getElementById(id);
  el.type = el.type === 'password' ? 'text' : 'password';
}

const strColors = ['#ef4444','#f59e0b','#22c55e','#10b981'];
const strLabels = ['Weak','Fair','Good','Strong'];
function strengthCheck(inp) {
  const pw = inp.value;
  let score = 0;
  if (pw.length >= 6)  score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  for (let i = 0; i < 4; i++) {
    document.getElementById('s'+(i+1)).style.background =
      i < score ? strColors[score-1] : 'rgba(255,255,255,.07)';
  }
  const lbl = document.getElementById('strength-label');
  lbl.textContent = pw ? (strLabels[score-1] || '') : '';
  lbl.style.color = pw && score ? strColors[score-1] : '#3d4270';
}

const form      = document.getElementById('register-form');
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

  const username = document.getElementById('username').value.trim();
  const email    = document.getElementById('email').value.trim();
  const company  = document.getElementById('company').value.trim();
  const password = document.getElementById('password').value;
  const confirm  = document.getElementById('confirm').value;

  if (username.length < 3) { showAlert('Username must be at least 3 characters.', 'error'); return; }
  if (!email.includes('@')) { showAlert('Please enter a valid email address.', 'error'); return; }
  if (!password)            { showAlert('Please choose a password.', 'error'); return; }
  if (password !== confirm) { showAlert('Passwords do not match.', 'error'); return; }

  setLoading(true);
  try {
    const res  = await fetch('/register', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ username, email, company, password, role: 'customer' })
    });
    const data = await res.json();
    if (res.ok) {
      showAlert('Account created! Redirecting to login…', 'success');
      setTimeout(() => { window.location.href = '/login'; }, 1000);
    } else {
      showAlert(data.error || 'Registration failed.', 'error');
    }
  } catch {
    showAlert('Network error. Please try again.', 'error');
  } finally {
    setLoading(false);
  }
});
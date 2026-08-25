// ── CSRF Token ───────────────────────────────────────────
function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (let c of cookies) {
    const [k, v] = c.trim().split('=');
    if (k === name) return decodeURIComponent(v);
  }
  return null;
}

const CSRF = getCookie('csrftoken');

// ── Delete Notification بدون reload ─────────────────────
document.querySelectorAll('.delete-notif-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    const pk   = btn.dataset.pk;
    const item = document.getElementById(`notif-${pk}`);

    const res = await fetch(`/notifications/${pk}/delete/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF,
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    if (res.ok) {
      item.style.transition = 'all .3s ease';
      item.style.opacity    = '0';
      setTimeout(() => item.remove(), 300);
    }
  });
});

// ── بروزرسانی عدد زنگوله ─────────────────────────────────
function updateBellCount(delta) {
  const badge = document.querySelector('.notif-badge');
  if (!badge) return;
  let count = parseInt(badge.textContent) + delta;
  if (count <= 0) badge.remove();
  else badge.textContent = count;
}
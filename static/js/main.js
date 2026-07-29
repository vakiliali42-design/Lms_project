// ── Page Loader ──────────────────────────────────────────
window.addEventListener('load', () => {
  const loader = document.getElementById('page-loader');
  if (loader) {
    loader.style.opacity = '0';
    setTimeout(() => loader.remove(), 400);
  }
});

// ── Scroll to Top ────────────────────────────────────────
const scrollBtn = document.getElementById('scrollTop');

window.addEventListener('scroll', () => {
  if (scrollBtn) {
    scrollBtn.classList.toggle('show', window.scrollY > 300);
  }
});

if (scrollBtn) {
  scrollBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ── Auto-dismiss Alerts ──────────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.transition = 'opacity .5s ease';
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 500);
  }, 4000);
});

// ── Fade-in Cards on Scroll ──────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card').forEach(card => {
  card.style.opacity = '0';
  card.style.transform = 'translateY(20px)';
  card.style.transition = 'opacity .4s ease, transform .4s ease';
  observer.observe(card);
});

// ── Tooltip Bootstrap ────────────────────────────────────
document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
  new bootstrap.Tooltip(el);
});

// ── Filter Auto-submit ───────────────────────────────────
document.querySelectorAll('#filterForm select').forEach(el => {
  el.addEventListener('change', () => {
    document.getElementById('filterForm')?.submit();
  });
});
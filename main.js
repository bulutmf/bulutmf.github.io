// The single place for the patent count. After changing it, run tools/build_site.py: it writes the number into
// index.html (the bio and the description tags), so search engines and link previews see it without JavaScript.
var PATENT_COUNT = 48;

// The publication lists are written into index.html and publications.html by tools/build_site.py from list.csv.

// Animated counter for stats
function animateCounter(element, target, suffix) {
  if (!suffix) suffix = '';
  var duration = 1500;
  var startTime = performance.now();

  function update(currentTime) {
    var elapsed = currentTime - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var easeOut = 1 - Math.pow(1 - progress, 3);
    var current = Math.floor(target * easeOut);
    element.textContent = current + suffix;

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  requestAnimationFrame(update);
}

// Scroll fade-in animations
function initAnimations() {
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-in').forEach(function (el) { observer.observe(el); });

  setTimeout(function () {
    var patentEl = document.getElementById('patent-count');
    if (patentEl) animateCounter(patentEl, PATENT_COUNT, '+');
    var stats = document.querySelectorAll('.stat-value');
    if (stats[2]) animateCounter(stats[2], 15, '+');
  }, 300);
}

// Back to top button
function initBackToTop() {
  var btn = document.getElementById('back-to-top');

  window.addEventListener('scroll', function () {
    if (window.scrollY > 500) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  });

  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function () {
  // Keep the bio's count current even before tools/build_site.py is run again
  var patentText = document.getElementById('patent-text');
  if (patentText) patentText.textContent = PATENT_COUNT + '+';

  initAnimations();
  initBackToTop();
});

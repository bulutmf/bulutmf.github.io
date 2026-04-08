// Load and parse publications from CSV
async function loadPublications() {
  try {
    var response = await fetch('list.csv');
    var text = await response.text();
    var lines = text.trim().split('\n').filter(function (line) { return line.trim(); });

    var publications = lines.map(function (line, index) {
      var parts = line.split(';');
      return {
        type: parts[0] || '',
        year: parts[1] || '',
        authors: parts[2] || '',
        title: parts[3] || '',
        venue: parts[4] || '',
        award: parts[5] || '',
        number: lines.length - index
      };
    }).filter(function (pub) { return pub.title; });

    renderCompactPublications(publications.slice(0, 5));

    var pubCountEl = document.getElementById('pub-count');
    animateCounter(pubCountEl, publications.length, '+');
  } catch (error) {
    console.error('Error loading publications:', error);
  }
}

function renderPublications(publications, filter) {
  if (!filter) filter = 'all';
  var grid = document.getElementById('pub-grid');
  var filtered = filter === 'all'
    ? publications
    : publications.filter(function (p) { return p.type.toLowerCase() === filter.toLowerCase(); });

  grid.innerHTML = filtered.map(function (pub) {
    var badgeClass = pub.type.toLowerCase().replace(' ', '');
    var linksHtml = pub.venue || '';
    var awardHtml = pub.award ? '<div class="pub-award">\uD83C\uDFC6 ' + pub.award + '</div>' : '';

    return '<article class="pub-card" data-type="' + pub.type + '">' +
      '<div class="pub-header">' +
      '<span class="pub-number">#' + pub.number + '</span>' +
      '<span class="pub-badge ' + badgeClass + '">' + pub.type + '</span>' +
      '<span class="pub-year">' + pub.year + '</span>' +
      '</div>' +
      '<h3 class="pub-title">' + pub.title + '</h3>' +
      '<p class="pub-authors">' + pub.authors + '</p>' +
      '<div class="pub-venue">' + linksHtml + '</div>' +
      awardHtml +
      '</article>';
  }).join('');
}

function setupFilters(publications) {
  var buttons = document.querySelectorAll('.filter-btn');
  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      buttons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      renderPublications(publications, btn.dataset.filter);
    });
  });
}

function renderCompactPublications(publications) {
  var grid = document.getElementById('pub-grid-compact');
  if (!grid) return;

  grid.innerHTML = publications.map(function (pub, i) {
    var badgeClass = pub.type.toLowerCase().replace(' ', '');
    var venueHtml = pub.venue ? '<span class="pub-recent-venue">' + pub.venue + '</span>' : '';

    return '<div class="pub-recent">' +
      '<span class="pub-recent-num">' + (i + 1) + '</span>' +
      '<div class="pub-recent-body">' +
      '<div class="pub-recent-title">' + pub.title + '</div>' +
      '<div class="pub-recent-meta">' +
      '<span class="pub-badge ' + badgeClass + '">' + pub.type + '</span>' +
      '<span class="pub-recent-year">' + pub.year + '</span>' +
      venueHtml +
      '</div>' +
      '</div>' +
      '</div>';
  }).join('');
}

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
    var stats = document.querySelectorAll('.stat-value');
    if (stats[0]) animateCounter(stats[0], 40, '+');
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

// News toggle
function initNewsToggle() {
  var VISIBLE_COUNT = 3;
  var toggle = document.getElementById('news-toggle');
  var allItems = document.querySelectorAll('#news-list .news-item');
  var totalCount = allItems.length;
  var hiddenCount = totalCount - VISIBLE_COUNT;
  var expanded = false;

  allItems.forEach(function (item, i) {
    if (i >= VISIBLE_COUNT) item.classList.add('news-hidden');
  });

  if (hiddenCount <= 0) { toggle.style.display = 'none'; return; }

  toggle.textContent = 'View all ' + totalCount + ' news \u2192';

  toggle.addEventListener('click', function () {
    expanded = !expanded;
    allItems.forEach(function (item, i) {
      if (i < VISIBLE_COUNT) return;
      if (expanded) {
        setTimeout(function () { item.classList.add('show'); }, (i - VISIBLE_COUNT) * 80);
      } else {
        item.classList.remove('show');
      }
    });
    toggle.textContent = expanded ? '\u2190 Show less' : 'View all ' + totalCount + ' news \u2192';
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function () {
  loadPublications();
  initAnimations();
  initBackToTop();
  initNewsToggle();
});

document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    var expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!expanded));
    links.classList.toggle('active');
  });

  links.addEventListener('click', function (e) {
    if (e.target.closest('a')) {
      toggle.setAttribute('aria-expanded', 'false');
      links.classList.remove('active');
    }
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-container')) {
      toggle.setAttribute('aria-expanded', 'false');
      links.classList.remove('active');
    }
  });
});

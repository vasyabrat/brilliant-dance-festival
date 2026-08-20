// Brilliant Dance Festival — shared site behavior

document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      var expanded = nav.classList.contains('open');
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    });
  }

  // Mark the current page's nav link as active
  var here = window.location.pathname.replace(/index\.html$/, '') || '/';
  document.querySelectorAll('nav.main-nav a[href]').forEach(function (link) {
    var href = link.getAttribute('href');
    if (!href || href.startsWith('http')) return;
    var normalized = href.replace(/index\.html$/, '') || '/';
    if (normalized === here) link.classList.add('active');
  });

  // Contact form: client-side only placeholder.
  // Wire this up to your own form backend (e.g. Formspree, Netlify Forms,
  // a serverless function, or an email API) — see README "Contact form" section.
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = document.getElementById('form-status');
      if (status) {
        status.textContent = 'Thanks! This form is not yet connected to an email service — see the README for how to wire it up.';
        status.style.color = '#15224b';
      }
      form.reset();
    });
  }
});

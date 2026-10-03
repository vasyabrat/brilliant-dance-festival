// Brilliant Dance Festival — shared site behavior (progressive enhancement)
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.addEventListener('DOMContentLoaded', function () {
    root.classList.add('js-ready');

    // ---- Mobile menu ----
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.getElementById('site-nav');
    function setMenu(open) {
      if (!toggle || !nav) return;
      nav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    if (toggle && nav) {
      toggle.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
    }

    // ---- Dropdown menus ----
    var menus = Array.prototype.slice.call(document.querySelectorAll('.has-menu'));
    function closeMenus(except) {
      menus.forEach(function (m) {
        if (m === except) return;
        m.classList.remove('open');
        m.querySelector('.menu-btn').setAttribute('aria-expanded', 'false');
      });
    }
    menus.forEach(function (m) {
      var btn = m.querySelector('.menu-btn');
      btn.addEventListener('click', function () {
        var open = !m.classList.contains('open');
        closeMenus(m);
        m.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      m.addEventListener('focusout', function (e) {
        if (!m.contains(e.relatedTarget) && window.innerWidth > 960) {
          m.classList.remove('open');
          btn.setAttribute('aria-expanded', 'false');
        }
      });
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.has-menu')) closeMenus();
      if (nav && toggle && nav.classList.contains('open') && !e.target.closest('.site-header')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var openMenu = document.querySelector('.has-menu.open');
      if (openMenu) { openMenu.querySelector('.menu-btn').focus(); closeMenus(); }
      if (nav && nav.classList.contains('open')) { setMenu(false); if (toggle) toggle.focus(); }
    });
    window.addEventListener('resize', function () { if (window.innerWidth > 960) setMenu(false); });

    // ---- Gentle reveal on scroll ----
    var items = document.querySelectorAll('.reveal');
    if (reduce || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      items.forEach(function (el) { io.observe(el); });
    }

    // ---- Contact form ----
    // No backend is connected. Submitting opens the visitor's email app with the
    // message pre-filled and addressed to the organizer; nothing is sent automatically.
    var form = document.getElementById('contact-form');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var v = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
        var body = v('message') + '\n\n— ' + v('name') + '\n' + v('email') + (v('phone') ? '\n' + v('phone') : '');
        var subject = v('subject') || 'Brilliant Dance Festival inquiry';
        var status = document.getElementById('form-status');
        if (status) status.textContent = 'Your email app should open with your message ready to send.';
        window.location.href = 'mailto:' + form.getAttribute('data-mailto') +
          '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      });
    }
  });
})();

(function () {
  'use strict';

  var raf = requestAnimationFrame;
  var mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  var scrollY = 0, tScrollY = 0;

  /* ── Cache elements ── */
  var orb1       = document.querySelector('.orb-1');
  var orb2       = document.querySelector('.orb-2');
  var orb3       = document.querySelector('.orb-3');
  var heroInner  = document.querySelector('.hero-inner');
  var heroVideo  = document.querySelector('.hero-video');
  var cards      = document.querySelectorAll('.fc');

  /* ── 1. MOUSE PARALLAX ── */
  document.addEventListener('mousemove', function (e) {
    mouse.tx = (e.clientX / window.innerWidth  - 0.5) * 2;
    mouse.ty = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });

  /* ── 2. SCROLL CAPTURE ── */
  window.addEventListener('scroll', function () {
    tScrollY = window.scrollY;
  }, { passive: true });

  /* ── 3. RAF LOOP — smooth lerp everything ── */
  var LERP = 0.072;
  function tick() {
    mouse.x += (mouse.tx - mouse.x) * LERP;
    mouse.y += (mouse.ty - mouse.y) * LERP;
    scrollY  += (tScrollY - scrollY)  * 0.12;

    var mx = mouse.x, my = mouse.y;

    /* Orbs — different parallax depths */
    if (orb1) orb1.style.transform =
      'translateX(calc(-50% + ' + (mx * 28) + 'px)) translateY(' + (my * 18 - 280) + 'px)';
    if (orb2) orb2.style.transform =
      'translate(' + (mx * -18) + 'px,' + (my * 14) + 'px)';
    if (orb3) orb3.style.transform =
      'translate(' + (mx * 22) + 'px,' + (my * -16) + 'px)';

    /* Hero text — subtle float with scroll */
    if (heroInner) heroInner.style.transform =
      'translate(' + (mx * 6) + 'px,' + (my * 4 + scrollY * 0.18) + 'px)';

    /* Video — slower scroll = depth illusion, slight mouse parallax */
    if (heroVideo) heroVideo.style.transform =
      'translate(' + (mx * -12) + 'px,' + (scrollY * 0.38) + 'px) scale(1.12)';

    raf(tick);
  }
  raf(tick);

  /* ── 4. CARD 3D TILT ── */
  cards.forEach(function (card) {
    card.style.transition = 'transform 0.15s ease, box-shadow 0.15s ease';
    card.style.willChange = 'transform';

    card.addEventListener('mousemove', function (e) {
      var r   = card.getBoundingClientRect();
      var cx  = (e.clientX - r.left)  / r.width  - 0.5;
      var cy  = (e.clientY - r.top)   / r.height - 0.5;
      card.style.transition = 'transform 0.08s ease, box-shadow 0.08s ease';
      card.style.transform  =
        'perspective(700px) rotateX(' + (-cy * 16) + 'deg) rotateY(' + (cx * 16) + 'deg) translateZ(14px) scale(1.03)';
      card.style.boxShadow  =
        (cx * 14) + 'px ' + (cy * 14) + 'px 30px rgba(99,102,241,0.25)';
    });

    card.addEventListener('mouseleave', function () {
      card.style.transition = 'transform 0.55s cubic-bezier(.34,1.56,.64,1), box-shadow 0.55s ease';
      card.style.transform  = 'perspective(700px) rotateX(0) rotateY(0) translateZ(0) scale(1)';
      card.style.boxShadow  = '';
    });
  });

  /* ── 5. SCROLL-DRIVEN SECTION DEPTH ── */
  if (typeof IntersectionObserver !== 'undefined') {
    var depthObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.style.transform = 'translateY(0) scale(1)';
          e.target.style.opacity   = '1';
        }
      });
    }, { threshold: 0.08 });

    document.querySelectorAll('.fc').forEach(function (el, i) {
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(40px) scale(0.96)';
      el.style.transition = 'transform 0.65s cubic-bezier(.34,1.56,.64,1) ' + (i * 0.09) + 's, opacity 0.5s ease ' + (i * 0.09) + 's';
      depthObs.observe(el);
    });
  }

})();

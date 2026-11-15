// Meta pixel for enchantratarot.com (M, 16 Nov 2026). Brief: "Meta tracking setup brief", Job 3.
//
// What it does: tells Meta a page was visited (PageView). Nothing else.
//   - No advanced matching: init gets the pixel ID alone, never an email, name or form field.
//   - autoConfig off: stops Meta collecting button clicks and page metadata by itself.
//   - Not loaded on /confirmed (ENCH-294: that address can carry sign-in tokens).
//   - The short links (/insta, /fb, /linkedin, /tiktok, /substack, /app) carry their own
//     copy of the ID and fire app_store_click instead. Change the ID in all seven places.
var ENCHANTRA_META_PIXEL_ID = '1457599145748355';

(function (id) {
  if (!/^\d+$/.test(id) || window.fbq) return;
  var f = window.fbq = function () {
    f.callMethod ? f.callMethod.apply(f, arguments) : f.queue.push(arguments);
  };
  window._fbq = f; f.push = f; f.loaded = true; f.version = '2.0'; f.queue = [];
  f('set', 'autoConfig', false, id);
  f('init', id);
  f('track', 'PageView');
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://connect.facebook.net/en_US/fbevents.js';
  (document.head || document.documentElement).appendChild(s);
})(ENCHANTRA_META_PIXEL_ID);

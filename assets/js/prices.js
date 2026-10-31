/* Enchantra prices by country, and where the app is on sale.
   Source: Notion, "Enchantra payments setup for launch", Stage 2 (App Store Connect, 25 Oct 2026),
   and ENCH-317 (Australia and New Zealand first, M 30 Oct 2026).

   The visitor's country is worked out in the browser from the device time zone
   (then browser language), so nothing is sent to any other service. No IP address.
   Test any country by adding ?country=GB (AU, NZ, GB, IE, US, CA, or any other code such as JP)
   to the address. Add &live=1 to preview release day while the switch below is still off. */

/* ════════════════════ RELEASE SWITCH ════════════════════
   Release day: paste the App Store link, then change false to true. That's all.
   While it is false, everyone sees "coming soon" and the waitlist, as before. */
var ENCHANTRA_RELEASE = {
  APP_STORE_LIVE: false,
  APP_STORE_URL: 'PASTE_APP_STORE_LINK_HERE', // for example https://apps.apple.com/app/id0000000000
  OPEN_IN: ['AU', 'NZ']                         // countries where the App Store sells Enchantra
};
/* ════════════════════════════════════════════════════════ */

(function () {
  var PRICES = {
    AU: { monthly: 'A$6.49',  annual: 'A$63.99',  m: 6.49, a: 63.99, sym: 'A$' },
    NZ: { monthly: 'NZ$6.99', annual: 'NZ$69',    m: 6.99, a: 69,    sym: 'NZ$' },
    GB: { monthly: '£4.49',   annual: '£44.49',   m: 4.49, a: 44.49, sym: '£' },
    IE: { monthly: '€4.49',   annual: '€44.49',   m: 4.49, a: 44.49, sym: '€' },
    US: { monthly: 'US$5.99', annual: 'US$58.99', m: 5.99, a: 58.99, sym: 'US$' },
    CA: { monthly: 'C$5.99',  annual: 'C$58.99',  m: 5.99, a: 58.99, sym: 'C$' }
  };

  /* Words on the page. WAITING FOR M'S YES (ENCH-317): the line under the price,
     the App Store button label and the footer line. */
  var WORDS = {
    // Line under the price for countries that open later; {country} is filled in below.
    noteLater: 'Enchantra opens in {country} soon. Join the waitlist and she’ll write to you on the day.',
    // Line under the price for everyone else (they see Australian prices).
    noteElsewhere: 'Enchantra isn’t in your country yet. Prices shown are for Australia.',
    countryName: { GB: 'the UK', IE: 'Ireland', US: 'the US', CA: 'Canada' },
    storeButton: 'Download on the App Store',
    storeFooter: 'iPhone · on the App Store',
    // Release day, Australia and New Zealand: the line under the App Store button (M, 31 Oct)
    androidSoon: 'Android · coming soon'
  };

  var CA_ZONES = ['Toronto','Vancouver','Edmonton','Winnipeg','Halifax','St_Johns','Regina','Moncton',
    'Glace_Bay','Goose_Bay','Whitehorse','Dawson','Dawson_Creek','Fort_Nelson','Creston','Iqaluit',
    'Rankin_Inlet','Resolute','Cambridge_Bay','Inuvik','Swift_Current','Atikokan','Blanc-Sablon',
    'Nipigon','Thunder_Bay','Rainy_River','Yellowknife','Pangnirtung','Montreal'];
  var US_ZONES = ['New_York','Chicago','Denver','Phoenix','Los_Angeles','Anchorage','Adak','Boise',
    'Detroit','Juneau','Sitka','Metlakatla','Yakutat','Nome','Menominee'];

  function fromZone(tz) {
    if (!tz) return null;
    if (tz.indexOf('Australia/') === 0) return 'AU';
    if (tz === 'Pacific/Auckland' || tz === 'Pacific/Chatham' || tz.indexOf('NZ') === 0) return 'NZ';
    if (tz === 'Europe/London' || tz === 'Europe/Belfast' || tz === 'GB') return 'GB';
    if (tz === 'Europe/Dublin' || tz === 'Eire') return 'IE';
    if (tz.indexOf('Canada/') === 0) return 'CA';
    if (tz.indexOf('US/') === 0 || tz === 'Pacific/Honolulu') return 'US';
    if (tz.indexOf('America/') === 0) {
      var city = tz.slice(8);
      if (CA_ZONES.indexOf(city) > -1) return 'CA';
      if (US_ZONES.indexOf(city) > -1 || /^(Indiana|Kentucky|North_Dakota)\//.test(city)) return 'US';
    }
    return null;
  }

  function fromLanguage() {
    var langs = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || ''];
    for (var i = 0; i < langs.length; i++) {
      var m = /-([A-Za-z]{2})\b/.exec(langs[i] || '');
      if (m && PRICES[m[1].toUpperCase()]) return m[1].toUpperCase();
    }
    return null;
  }

  function param(name) {
    try { var q = new RegExp('[?&]' + name + '=([^&#]*)').exec(location.search); return q ? q[1] : null; } catch (e) { return null; }
  }

  /* One of the six countries, 'XX' for anywhere else, or null when nothing can be told. */
  function country() {
    var q = param('country');
    if (q && /^[A-Za-z]{2}$/.test(q)) return PRICES[q.toUpperCase()] ? q.toUpperCase() : 'XX';
    var tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    var c = fromZone(tz);
    if (c) return c;
    // A real time zone outside the six countries: anywhere else.
    if (tz && tz.indexOf('Etc/') !== 0 && tz !== 'UTC') return 'XX';
    return fromLanguage();
  }

  function each(sel, fn) { var els = document.querySelectorAll(sel); for (var i = 0; i < els.length; i++) fn(els[i]); }

  function applyPrices(c) {
    var p = PRICES[c];
    if (!p) return; // anywhere else keeps the page's own A$ prices
    var perMonth = p.sym + (Math.round(p.a / 12 * 100) / 100).toFixed(2);
    each('[data-price]', function (el) {
      var k = el.getAttribute('data-price');
      if (k === 'monthly') el.textContent = p.monthly;
      else if (k === 'annual') el.textContent = p.annual;
      else if (k === 'annual-month') el.textContent = perMonth;
    });
  }

  function applyNote(c, open) {
    if (!c || open) return; // AU, NZ, and unknown: no line
    var text = WORDS.countryName[c] ? WORDS.noteLater.replace('{country}', WORDS.countryName[c]) : WORDS.noteElsewhere;
    each('[data-launch-note]', function (el) { el.textContent = text; el.hidden = false; });
  }

  function applyStore(open, live) {
    var url = ENCHANTRA_RELEASE.APP_STORE_URL;
    if (!/^https:\/\/apps\.apple\.com\//.test(url)) {
      if (param('live') !== '1') return; // no real link yet: stay on the waitlist
      url = '#app-store-link';           // preview only
    }
    if (!live || !open) return;
    // Every gold waitlist button becomes the App Store button.
    each('a.btn-gold[href*="substack.com/subscribe"], a[data-store-cta]', function (a) {
      a.href = url;
      a.removeAttribute('target');
      for (var n = a.firstChild; n; n = n.nextSibling) {
        if (n.nodeType === 3 && /\S/.test(n.nodeValue)) { n.nodeValue = ' ' + WORDS.storeButton + ' '; break; }
      }
    });
    // "Coming soon" becomes "Android · coming soon" (M, 31 Oct). The dot stays.
    each('[data-store-soon]', function (el) {
      for (var n = el.lastChild; n; n = n.previousSibling) {
        if (n.nodeType === 3 && /\S/.test(n.nodeValue)) { n.nodeValue = WORDS.androidSoon; break; }
      }
    });
    each('[data-store-footer]', function (el) {
      var a = document.createElement('a');
      a.href = url; a.textContent = WORDS.storeFooter;
      a.setAttribute('style', 'font-size: 14px; color: #e8c98a; text-decoration: none;');
      el.parentNode.replaceChild(a, el);
    });
    // Structured data: Australia and New Zealand offers become in stock.
    each('script[type="application/ld+json"]', function (s) {
      if (s.textContent.indexOf('schema.org/PreOrder') > -1) s.textContent = s.textContent.replace(/schema\.org\/PreOrder/g, 'schema.org/InStock');
    });
  }

  function apply() {
    var c = country();
    var open = !!c && ENCHANTRA_RELEASE.OPEN_IN.indexOf(c) > -1;
    var live = ENCHANTRA_RELEASE.APP_STORE_LIVE || param('live') === '1';
    applyPrices(c);
    applyNote(c, open);
    applyStore(open, live);
    if (c) document.documentElement.setAttribute('data-price-country', c);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
})();

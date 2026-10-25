/* Enchantra prices by country.
   Source: Notion, "Enchantra payments setup for launch", Stage 2 (App Store Connect, 25 Oct 2026).
   Sold in six countries only. The page's own text (A$) is the fallback when no match is found.

   The visitor's country is worked out in the browser from the device time zone
   (then browser language), so nothing is sent to any other service.
   Test any country by adding ?country=GB (AU, NZ, GB, IE, US, CA) to the address. */
(function () {
  var PRICES = {
    AU: { monthly: 'A$6.49',  annual: 'A$63.99',  m: 6.49, a: 63.99, sym: 'A$' },
    NZ: { monthly: 'NZ$6.99', annual: 'NZ$69',    m: 6.99, a: 69,    sym: 'NZ$' },
    GB: { monthly: '£4.49',   annual: '£44.49',   m: 4.49, a: 44.49, sym: '£' },
    IE: { monthly: '€4.49',   annual: '€44.49',   m: 4.49, a: 44.49, sym: '€' },
    US: { monthly: 'US$5.99', annual: 'US$58.99', m: 5.99, a: 58.99, sym: 'US$' },
    CA: { monthly: 'C$5.99',  annual: 'C$58.99',  m: 5.99, a: 58.99, sym: 'C$' }
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

  function country() {
    try {
      var q = /[?&]country=([A-Za-z]{2})/.exec(location.search);
      if (q && PRICES[q[1].toUpperCase()]) return q[1].toUpperCase();
    } catch (e) {}
    var tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    var c = fromZone(tz);
    if (c) return c;
    // A real time zone outside the six countries: keep the page's default prices.
    if (tz && tz.indexOf('Etc/') !== 0 && tz !== 'UTC') return null;
    return fromLanguage();
  }

  function apply() {
    var c = country();
    if (!c) return;
    var p = PRICES[c];
    var perMonth = p.sym + (Math.round(p.a / 12 * 100) / 100).toFixed(2);
    var els = document.querySelectorAll('[data-price]');
    for (var i = 0; i < els.length; i++) {
      var k = els[i].getAttribute('data-price');
      if (k === 'monthly') els[i].textContent = p.monthly;
      else if (k === 'annual') els[i].textContent = p.annual;
      else if (k === 'annual-month') els[i].textContent = perMonth;
    }
    document.documentElement.setAttribute('data-price-country', c);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
})();

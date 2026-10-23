#!/usr/bin/env python3
"""Build Where Decks Find You (/tarot-card-shops/) from data/shops.json.

Adding a shop: add one entry to data/shops.json, then run from the repo root:

    python3 scripts/build_shops.py

It rewrites only the generated parts of tarot-card-shops/index.html (between the
shops:*:start / shops:*:end markers): the region jump list, the shop cards
and the JSON-LD ItemList. Everything is written into the HTML itself, so
search and AI answer engines read every shop without JavaScript.
No dependencies beyond Python 3.
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "shops.json"
PAGE = ROOT / "tarot-card-shops" / "index.html"
FIELDS = ("name", "region", "town", "address", "days", "description", "website")
COUNT_WORDS = {1: "One shop", 2: "Two shops", 3: "Three shops", 4: "Four shops", 5: "Five shops", 6: "Six shops", 7: "Seven shops", 8: "Eight shops", 9: "Nine shops"}
OPTIONAL = {"instagram": "", "facebook": "", "tiktok": "", "shop_online": False, "logo": "", "logo_bg": ""}
SHOPFRONT = ('<svg viewBox="0 0 24 24" width="34" height="34" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5 5.5 4h13L20 9.5"/><path d="M4 9.5c0 1.4 1.1 2.5 2.7 2.5s2.6-1.1 2.6-2.5c0 1.4 1.1 2.5 2.7 2.5s2.7-1.1 2.7-2.5c0 1.4 1 2.5 2.6 2.5S20 10.9 20 9.5"/><path d="M5.5 12v8h13v-8"/><path d="M10 20v-4.5h4V20"/></svg>')

PIN = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
       'stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11Z"/>'
       '<circle cx="12" cy="10" r="2.4"/></svg>')
CLOCK = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>')
GLOBE = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.3 2.4 3.4 5.2 3.4 8.5s-1.1 6.1-3.4 8.5c-2.3-2.4-3.4-5.2-3.4-8.5S9.7 5.9 12 3.5Z"/></svg>')
BAG = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
       'stroke-linecap="round" stroke-linejoin="round"><path d="M5.5 8h13l-1 12h-11l-1-12Z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/></svg>')
MAP = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
       'stroke-linecap="round" stroke-linejoin="round"><path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6 9 4Z"/><path d="M9 4v14M15 6v14"/></svg>')


def icon(paths):
    return ('<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round">' + paths + '</svg>')


# Plain line icons in the site's own style (generic shapes, not the platforms' trademarked logos)
I_GLOBE = icon('<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.3 2.4 3.4 5.2 3.4 8.5s-1.1 6.1-3.4 8.5c-2.3-2.4-3.4-5.2-3.4-8.5S9.7 5.9 12 3.5Z"/>')
I_BAG = icon('<path d="M5.5 8h13l-1 12h-11l-1-12Z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>')
I_MAP = icon('<path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6 9 4Z"/><path d="M9 4v14M15 6v14"/>')
I_CAMERA = icon('<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="3.8"/><circle cx="17" cy="7" r="0.6" fill="currentColor"/>')
I_PEOPLE = icon('<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19c0-3 2.5-5.2 5.5-5.2s5.5 2.2 5.5 5.2"/><circle cx="16.5" cy="9.5" r="2.4"/><path d="M15.5 14.1c2.7.2 5 2.2 5 4.9"/>')
# Official marks, used as published by Meta (Instagram glyph, Facebook logo), shown in one colour
I_INSTAGRAM = '<span class="brand-ico ico-instagram" aria-hidden="true"></span>'
I_FACEBOOK = '<span class="brand-ico ico-facebook" aria-hidden="true"></span>'
I_TIKTOK = '<span class="brand-ico ico-tiktok" aria-hidden="true"></span>'
I_NOTE = icon('<path d="M9 18V5.5l10-2V16"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>')


def e(text):
    return html.escape(text, quote=True)


def site_url(website):
    w = website.strip()
    if not w:
        return ""
    return w if w.startswith(("http://", "https://")) else "https://" + w


def maps_url(address, country):
    # Plain maps search: the address only, no tracking parameters.
    return "https://www.google.com/maps/search/?api=1&query=" + quote(f"{address}, {country}", safe="")


def card(shop, country):
    for k, v in OPTIONAL.items():
        shop.setdefault(k, v)
    name = e(shop["name"])
    actions = []
    def btn(href, label, ico, main=False):
        cls = "act act-main" if main else "act"
        return f'<a class="{cls}" href="{e(href)}" rel="noopener" aria-label="{label}" title="{label}">{ico}</a>'
    if shop["website"]:
        if shop["shop_online"]:
            actions.append(btn(site_url(shop["website"]), f"Shop online at {shop['name']}", I_BAG, True))
        else:
            actions.append(btn(site_url(shop["website"]), f"{shop['name']} website", I_GLOBE, True))
    actions.append(btn(maps_url(shop["address"], country), f"Open {shop['name']} in Maps", I_MAP))
    for key, label, ico in (("instagram", "Instagram", I_INSTAGRAM), ("facebook", "Facebook", I_FACEBOOK), ("tiktok", "TikTok", I_TIKTOK)):
        if shop[key]:
            actions.append(btn(shop[key], f"{shop['name']} on {label}", ico))
    # Logo band: the shop's own logo on the background it was made for (logo_bg: light, dark or black).
    # Shops without a logo get Enchantra's own shopfront icon.
    if shop["logo"]:
        base = "/" + shop["logo"].lstrip("/")
        w, h = shop.get("logo_w", 240), shop.get("logo_h", 120)
        logo = (f'          <div class="shop-logo logo-{e(shop.get("logo_bg") or "light")}">'
                f'<picture><source srcset="{e(base)}.webp" type="image/webp">'
                f'<img src="{e(base)}.png" alt="{name} logo" width="{w}" height="{h}" loading="lazy" decoding="async"></picture></div>\n')
    else:
        logo = f'          <div class="shop-logo logo-none" aria-hidden="true">{SHOPFRONT}</div>\n'
    return (
        '        <article class="shop">\n'
        '          <div class="shop-head">\n'
        + logo.replace("          <div", "            <div", 1) +
        f'            <div class="shop-title">\n              <h3 class="en-serif">{name}</h3>\n              <p class="shop-town">{e(shop["town"])}</p>\n            </div>\n'
        '          </div>\n'
        f'          <p class="shop-desc">{e(shop["description"])}</p>\n'
        '          <ul class="shop-facts">\n'
        f'            <li><span class="sr-only">Address: </span>{PIN}<span>{e(shop["address"])}</span></li>\n'
        f'            <li><span class="sr-only">Open: </span>{CLOCK}<span>{e(shop["days"])}</span></li>\n'
        '          </ul>\n'
        f'          <div class="shop-actions">{"".join(actions)}</div>\n'
        '        </article>\n'
    )


def region_block(r, shops, tag="section"):
    note = f'\n          <p class="region-note">{e(r["note"])}</p>' if r.get("note") else ""
    eyebrow = "Aotearoa New Zealand" if r["country"] == "New Zealand" else r["country"]
    count = COUNT_WORDS.get(len(shops), f"{len(shops)} shops")
    return (
        f'    <{tag} class="region" id="{r["id"]}" aria-labelledby="{r["id"]}-h">\n'
        '      <div class="region-head">\n'
        f'        <div>\n          <p class="region-eyebrow">{e(eyebrow)}</p>\n          <h2 class="en-serif" id="{r["id"]}-h">{e(r["name"])}</h2>{note}\n        </div>\n'
        f'        <p class="region-count">{count}</p>\n'
        '      </div>\n'
        '      <div class="shop-grid">\n'
        + "".join(card(s, r["country"]) for s in shops)
        + f'      </div>\n    </{tag}>\n'
    )


def build():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    regions = data["regions"]
    names = {r["name"] for r in regions}
    for s in data["shops"]:
        missing = [f for f in FIELDS if f not in s]
        if missing:
            raise SystemExit(f'{s.get("name", "?")}: missing {", ".join(missing)}')
        if s["region"] not in names:
            raise SystemExit(f'{s["name"]}: unknown region "{s["region"]}"')

    jump = ['    <ul>']
    sections = []
    groups = []
    for r in regions:
        shops = sorted((s for s in data["shops"] if s["region"] == r["name"]), key=lambda s: s["town"].lower())
        if not shops:
            continue
        jump.append(f'      <li><a href="#{r["id"]}">{e(r["short"])}<span class="jump-count">{len(shops)}</span></a></li>')
        groups.append([(r, shops)])
    for i, g in enumerate(groups):
        band = "band-a" if i % 2 == 0 else "band-b"
        sections.append(f'  <div class="band {band}">\n  <div class="band-inner">\n' + region_block(*g[0]) + '  </div>\n  </div>\n')
    jump.append('    </ul>')

    items = []
    position = 0
    for r in regions:
        for s in sorted((s for s in data["shops"] if s["region"] == r["name"]), key=lambda s: s["town"].lower()):
            position += 1
            item = {"@type": "Store", "name": s["name"]}
            if s["website"]:
                item["url"] = site_url(s["website"])
            same = [s[k] for k in ("instagram", "facebook", "tiktok") if s.get(k)]
            if same:
                item["sameAs"] = same
            items.append({"@type": "ListItem", "position": position, "item": item})
    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Where Decks Find You: tarot shops in Australia and New Zealand",
        "url": "https://enchantratarot.com/tarot-card-shops/",
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    jsonld = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + '\n</script>'

    page = PAGE.read_text(encoding="utf-8")
    for key, body in (("jsonld", jsonld), ("jump", "\n".join(jump)), ("regions", "".join(sections).rstrip("\n"))):
        pattern = re.compile(rf"(<!-- shops:{key}:start -->)(.*?)(<!-- shops:{key}:end -->)", re.S)
        if not pattern.search(page):
            raise SystemExit(f"marker shops:{key} not found in {PAGE}")
        page = pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", page)
    PAGE.write_text(page, encoding="utf-8")
    print(f"Built {PAGE.relative_to(ROOT)}: {position} shops in {sum(len(g) for g in groups)} regions.")


if __name__ == "__main__":
    build()

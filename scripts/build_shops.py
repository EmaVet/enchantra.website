#!/usr/bin/env python3
"""Build Where Decks Find You (/shops/) from data/shops.json.

Adding a shop: add one entry to data/shops.json, then run from the repo root:

    python3 scripts/build_shops.py

It rewrites only the generated parts of shops/index.html (between the
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
PAGE = ROOT / "shops" / "index.html"
FIELDS = ("name", "region", "town", "address", "days", "description", "website")

PIN = ('<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none" stroke="#9a8fc0" stroke-width="1.6" '
       'stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11Z"/>'
       '<circle cx="12" cy="10" r="2.4"/></svg>')
CLOCK = ('<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none" stroke="#9a8fc0" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>')
GLOBE = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="#9a8fc0" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.3 2.4 3.4 5.2 3.4 8.5s-1.1 6.1-3.4 8.5c-2.3-2.4-3.4-5.2-3.4-8.5S9.7 5.9 12 3.5Z"/></svg>')
MAP = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="#9a8fc0" stroke-width="1.6" '
       'stroke-linecap="round" stroke-linejoin="round"><path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6 9 4Z"/><path d="M9 4v14M15 6v14"/></svg>')


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
    links = []
    if shop["website"]:
        links.append(f'<a href="{e(site_url(shop["website"]))}" rel="noopener">{GLOBE}{e(shop["website"])}</a>')
    links.append(f'<a href="{e(maps_url(shop["address"], country))}" rel="noopener" '
                 f'aria-label="Open {e(shop["name"])} in Maps">{MAP}Open in Maps</a>')
    return (
        '        <article class="shop">\n'
        f'          <h3 class="en-serif">{e(shop["name"])}</h3>\n'
        f'          <p class="shop-town">{e(shop["town"])}</p>\n'
        '          <ul class="shop-facts">\n'
        f'            <li><span class="sr-only">Address: </span>{PIN}<span>{e(shop["address"])}</span></li>\n'
        f'            <li><span class="sr-only">Open: </span>{CLOCK}<span>{e(shop["days"])}</span></li>\n'
        '          </ul>\n'
        f'          <p class="shop-desc">{e(shop["description"])}</p>\n'
        f'          <div class="shop-links">{"".join(links)}</div>\n'
        '        </article>\n'
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
    for r in regions:
        shops = sorted((s for s in data["shops"] if s["region"] == r["name"]), key=lambda s: s["town"].lower())
        if not shops:
            continue
        jump.append(f'      <li><a href="#{r["id"]}">{e(r["short"])}</a></li>')
        note = f'\n        <p class="region-note">{e(r["note"])}</p>' if r.get("note") else ""
        sections.append(
            f'  <section class="region" id="{r["id"]}" aria-labelledby="{r["id"]}-h">\n'
            '    <div class="region-inner">\n'
            f'      <div class="region-head">\n        <h2 class="en-serif" id="{r["id"]}-h">{e(r["name"])}</h2>{note}\n      </div>\n'
            '      <div class="shop-grid">\n'
            + "".join(card(s, r["country"]) for s in shops)
            + '      </div>\n    </div>\n  </section>\n'
        )
    jump.append('    </ul>')

    items = []
    position = 0
    for r in regions:
        for s in sorted((s for s in data["shops"] if s["region"] == r["name"]), key=lambda s: s["town"].lower()):
            position += 1
            item = {"@type": "Store", "name": s["name"]}
            if s["website"]:
                item["url"] = site_url(s["website"])
            items.append({"@type": "ListItem", "position": position, "item": item})
    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Where Decks Find You: tarot shops in Australia and New Zealand",
        "url": "https://enchantratarot.com/shops/",
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
    print(f"Built {PAGE.relative_to(ROOT)}: {position} shops in {len(sections)} regions.")


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
"""Keep the article cards and the questions on /confirmed/ up to date.

The page always shows the newest Almanac article first, then these two, which
stay for good (M, 2 Nov 2026): Reading tarot with the lunar cycle, and How to
read tarot for reflection.

Runs on every push (.github/workflows/sitemap.yml), or by hand from the repo root:

    python3 scripts/build_confirmed_articles.py

The questions are copied from the homepage on every run, less HIDDEN_QUESTION.

It rewrites only what sits between the confirmed: markers in
confirmed/index.html. "Newest" is the <time datetime> in each article's byline.
Title, category, read time and blurb come from that article's card on the
Almanac front page, so an article appears here once it has a card there.
The article picture is code-drawn, chosen by category, so no image files are needed.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "confirmed" / "index.html"
HOME = ROOT / "index.html"
FRONT = ROOT / "almanac" / "index.html"
PINNED = ["reading-tarot-with-the-lunar-cycle", "how-to-read-tarot-for-reflection"]
ART = {
    "lunar": '<span class="m-s m-l"></span><span class="m-b"></span><span class="m-s m-r"></span>',
    "journaling": '<span class="thread"></span>',
    "reflection": '<span class="m-b"></span>',
}
START, END = "<!-- confirmed:articles:start -->", "<!-- confirmed:articles:end -->"
HIDDEN_QUESTION = "When will Enchantra be available?"
FAQ_START, FAQ_END = "<!-- confirmed:faq:start -->", "<!-- confirmed:faq:end -->"


def text(fragment):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def front_cards():
    """Slug to details, from the Almanac front page's 'All articles' cards."""
    source = FRONT.read_text(encoding="utf-8")
    cards = {}
    for m in re.finditer(r'<a [^>]*href="/almanac/([a-z0-9-]+)/?"[^>]*>(.*?)</a>', source, re.S):
        slug, body = m.groups()
        meta = re.search(r"([\w ]+?)\s*·\s*(\d+ min read)", text(body))
        pieces = re.findall(r'<div[^>]*class="en-serif"[^>]*>(.*?)</div>\s*<div[^>]*>(.*?)</div>', body, re.S)
        if meta and pieces:
            cards[slug] = {"cat": meta.group(1).strip(), "read": meta.group(2),
                           "title": text(pieces[0][0]), "line": text(pieces[0][1])}
    return cards


def article_date(slug):
    found = re.search(r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})', (ROOT / "almanac" / slug / "index.html").read_text(encoding="utf-8"))
    return found.group(1) if found else ""


def art(category):
    """Drawn picture for a card. Any new category gets the moon."""
    inner = ART.get(category.lower(), ART["reflection"])
    return f'<span class="post-img post-draw" aria-hidden="true">{inner}</span>'


def card(slug, c):
    return f'''        <a class="post" href="/almanac/{slug}/">
          {art(c["cat"])}
          <span class="post-body"><span class="post-meta"><span class="post-cat">{c["cat"]}</span><span class="post-dot">·</span>{c["read"]}</span><span class="en-serif post-title">{c["title"]}</span><span class="post-line">{c["line"]}</span></span>
        </a>'''


def faq_section():
    """The homepage's questions, word for word, so they never drift apart.
    This page has no scroll reveal, and a section with overflow hidden stops the sticky heading."""
    home = HOME.read_text(encoding="utf-8")
    start = home.index('<section id="faq"')
    section = home[start:home.index("</section>", start) + len("</section>")]
    section = section.replace("opacity: 0; transform: translateY(24px); transition: opacity 900ms ease, transform 900ms ease; ", "")
    # Hidden here (M, 4 Nov 2026): the answer talks about the waitlist, and this reader has just signed up.
    section = re.sub(r'\s*<details class="faq"(?:(?!</details>).)*?' + re.escape(HIDDEN_QUESTION) + r".*?</details>", "", section, flags=re.S)
    return section.replace('position: relative; overflow: hidden;', 'position: relative; overflow: clip;', 1)


def main():
    cards = front_cards()
    missing = [s for s in PINNED if s not in cards]
    if missing:
        raise SystemExit(f"No Almanac card for: {missing}")
    others = [s for s in cards if s not in PINNED and (ROOT / "almanac" / s / "index.html").exists()]
    newest = sorted(others, key=article_date)[-1:]
    slugs = newest + PINNED
    block = "\n".join(card(s, cards[s]) for s in slugs)
    page = PAGE.read_text(encoding="utf-8")
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: f"{START}\n{block}\n        {END}", page, flags=re.S)
    if START not in page:
        raise SystemExit("Markers not found in confirmed/index.html")
    new = re.sub(re.escape(FAQ_START) + r".*?" + re.escape(FAQ_END), lambda _: f"{FAQ_START}\n  {faq_section()}\n  {FAQ_END}", new, flags=re.S)
    PAGE.write_text(new, encoding="utf-8")
    print("Confirmed page articles:", ", ".join(slugs))


if __name__ == "__main__":
    main()

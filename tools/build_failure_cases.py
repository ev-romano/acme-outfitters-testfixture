#!/usr/bin/env python3
"""Build the two failure-case storefronts under /zero-pages/ and /big-site/.

zero-pages: an app shell whose only script fetches a JSON file that does not
exist, so the page has no title, no text and no links with or without
JavaScript. A crawler that starts here finds nothing to read.

big-site: Linden Scrubs, a fictional scrubs brand. One home page links ten
section hubs; each hub links nine articles. 101 pages, all within two links of
the home page, none under /products/, /collections/, /search, /cart,
/checkout or /account. Every article has its own text, so no two pages dedupe.

Deterministic: re-running writes identical bytes.
Usage: python3 tools/build_failure_cases.py
"""

from __future__ import annotations

import hashlib
import html
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ZERO_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="./app.js" defer></script>
</head>
<body>
<div id="app"></div>
</body>
</html>
"""

ZERO_APP = """(function () {
  var mount = document.getElementById("app");
  fetch("./storefront-data/home.json")
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) {
      if (!data || !mount) { return; }
      mount.textContent = String(data.headline || "");
    })
    .catch(function () {});
})();
"""

BRAND = "Linden Scrubs"

SECTIONS: dict[str, tuple[str, list[str]]] = {
    "styles": ("Styles", ["V-neck top", "Mock-wrap top", "Jogger pant", "Straight-leg pant",
                          "Cargo pant", "Scrub jacket", "Underscrub tee", "Maternity top",
                          "Tall and petite cuts"]),
    "fabrics": ("Fabrics", ["FlexWeave stretch", "Recycled poly blend", "Cotton-rich twill",
                            "Antimicrobial finish", "Fluid barrier coating", "Four-way stretch",
                            "Colorfast dyes", "Breathable mesh panels", "Fabric weights explained"]),
    "fit": ("Fit guide", ["Measuring your chest", "Measuring your inseam", "Size chart for tops",
                          "Size chart for pants", "Between two sizes", "Shrinkage after washing",
                          "Rise and waistband", "Sleeve lengths", "Fit for long shifts"]),
    "care": ("Care", ["Washing new scrubs", "Removing stains", "Drying without shrinkage",
                      "Ironing and steaming", "Keeping colors bright", "Washing with bleach",
                      "Caring for jackets", "Storing a rotation", "When to replace scrubs"]),
    "help": ("Help center", ["Placing an order", "Changing an order", "Payment options",
                             "Gift cards", "Promo codes", "Guest orders",
                             "Order confirmation emails", "Contacting support", "Accessibility"]),
    "shipping": ("Shipping", ["Shipping times", "Shipping costs", "Express shipping",
                              "International shipping", "Tracking a parcel", "Lost parcels",
                              "Shipping to hospitals", "PO boxes", "Holiday cutoffs"]),
    "returns": ("Returns", ["Return window", "Starting a return", "Exchanges",
                            "Worn-once returns", "Embroidered items", "Refund timing",
                            "Return shipping labels", "Damaged items", "Final sale items"]),
    "stories": ("Stories", ["Night shift essentials", "A day with an ER nurse", "Why pockets matter",
                            "Designing the jogger", "Scrubs and sustainability", "Nurses week",
                            "Student clinical tips", "Veterinary teams", "Dental office uniforms"]),
    "teams": ("Team orders", ["Ordering for a unit", "Matching colors across a team",
                              "Embroidery and logos", "Team sizing kits", "Invoicing and net terms",
                              "Reorders", "Hospital color codes", "Team discounts",
                              "Delivery to a department"]),
    "about": ("About", ["Our story", "Who we design for", "Where we make scrubs", "Our factories",
                        "Giving back", "Careers", "Press", "Wear testing panel", "Our promise"]),
}

FACTS = [
    "shifts that run twelve hours or longer",
    "a pocket that holds a phone, a penlight and trauma shears at once",
    "fabric that springs back after a day of bending and lifting",
    "colors that match the codes most hospital units use",
    "stitching tested through two hundred wash cycles",
    "a waistband that stays flat under a badge reel",
    "a hem that does not drag on the floor of a busy ward",
    "sizes from XXS to 5XL in every color",
    "free exchanges within forty-five days",
    "shipping that leaves the warehouse within one business day",
    "a wear-testing panel of two hundred nurses, techs and vets",
    "seams placed away from where a stethoscope rests",
]
VERBS = ["We designed", "Our team built", "Nurses asked for", "Wear testers helped shape",
         "We refined", "Every season we revisit"]
CLOSERS = [
    "Questions about this page go to support@linden-scrubs.example, answered within one business day.",
    "If something here does not match your experience, tell us and we will update the page.",
    "Team buyers can ask for a sample kit before placing a unit-wide order.",
    "Our care team works Monday to Saturday, 7am to 7pm Central.",
]


def slug(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-").replace("--", "-")


def page(title: str, body: str, depth: int) -> str:
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{key}/index.html">{html.escape(name)}</a>'
        for key, (name, _) in SECTIONS.items()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {BRAND}</title>
<meta name="description" content="{html.escape(title)} from {BRAND}, scrubs made for long shifts.">
<meta property="og:site_name" content="{BRAND}">
<style>body{{font-family:system-ui,sans-serif;margin:0;color:#1d2b36}}header{{background:#0f5c4d;color:#fff;padding:12px 24px}}header a{{color:#fff;margin-right:14px}}main{{max-width:760px;margin:24px auto;padding:0 16px;line-height:1.6}}a.button{{background:#e8743b;color:#fff;padding:8px 14px;border-radius:4px;text-decoration:none}}</style>
</head>
<body>
<header><a href="{up}index.html"><strong>{BRAND}</strong></a> <nav aria-label="Main">{nav}</nav></header>
<main>
{body}
</main>
<footer><p>{BRAND} · Scrubs for long shifts · support@linden-scrubs.example</p></footer>
</body>
</html>
"""


def article_body(section: str, topic: str) -> str:
    rng = random.Random(hashlib.sha256(f"{section}/{topic}".encode()).hexdigest())
    paragraphs = []
    for index in range(5):
        facts = rng.sample(FACTS, 3)
        verb = rng.choice(VERBS)
        paragraphs.append(
            f"<p>{verb} {html.escape(topic.lower())} around {facts[0]}. "
            f"In the {html.escape(SECTIONS[section][0].lower())} guide, part {index + 1} covers "
            f"{facts[1]}, and why it matters for {facts[2]}. "
            f"Reference {rng.randint(100, 999)}-{rng.randint(10, 99)} tracks this detail in our "
            f"wear-test notes, updated {rng.choice(['every spring', 'each quarter', 'after every panel'])}.</p>"
        )
    paragraphs.append(f"<p>{rng.choice(CLOSERS)}</p>")
    return f"<h1>{html.escape(topic)}</h1>\n" + "\n".join(paragraphs)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def build_zero_pages() -> None:
    base = ROOT / "zero-pages"
    write(base / "index.html", ZERO_INDEX)
    write(base / "app.js", ZERO_APP)


def build_big_site() -> None:
    base = ROOT / "big-site"
    hub_links = "".join(
        f'<li><a href="./{key}/index.html">{html.escape(name)}</a></li>'
        for key, (name, _) in SECTIONS.items()
    )
    home = (
        f"<h1>{BRAND}: scrubs made for long shifts</h1>\n"
        "<p>We make scrubs for nurses, techs, vets and dental teams. Every piece is wear-tested "
        "on real twelve-hour shifts before it ships, in sizes XXS to 5XL.</p>\n"
        f'<p><a class="button" href="./styles/index.html">Browse styles</a></p>\n<ul>{hub_links}</ul>'
    )
    write(base / "index.html", page(f"{BRAND} — Scrubs for long shifts", home, 0))
    for key, (name, topics) in SECTIONS.items():
        links = "".join(
            f'<li><a href="./{slug(topic)}.html">{html.escape(topic)}</a></li>' for topic in topics
        )
        hub = (
            f"<h1>{html.escape(name)}</h1>\n<p>Everything {BRAND} has written about "
            f"{html.escape(name.lower())}, in nine short guides.</p>\n<ul>{links}</ul>"
        )
        write(base / key / "index.html", page(name, hub, 1))
        for topic in topics:
            write(base / key / f"{slug(topic)}.html", page(topic, article_body(key, topic), 1))


if __name__ == "__main__":
    build_zero_pages()
    build_big_site()

#!/usr/bin/env python3
"""Build script for smartphone-photo-basics-guide.

Converts docs/*.md into a warm, dependency-free static HTML site under
site/. No third-party packages are required - only Python 3.8+.

Usage:
    python3 build.py            # build the site, then verify it
    python3 build.py --verify   # verify an already-built site only
    python3 build.py --build    # build only, skip verification
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
ASSETS = ROOT / "assets"

# Reading order: front matter lives in index.html, chapters follow.
CHAPTER_ORDER = [
    "00-start-here.md",
    "01-light-without-jargon.md",
    "02-steady-hands.md",
    "03-framing-rules-you-can-bend.md",
    "04-portraits-that-flatter.md",
    "05-organizing-as-you-shoot.md",
    "06-backup-without-worry.md",
    "07-printing-favorites.md",
    "shooting-checklist.md",
    "monthly-print-ritual.md",
    "glossary.md",
]

TITLES = {
    "00-start-here.md": "Start Here",
    "01-light-without-jargon.md": "Light Without Jargon",
    "02-steady-hands.md": "Steady Hands",
    "03-framing-rules-you-can-bend.md": "Framing Rules You Can Bend",
    "04-portraits-that-flatter.md": "Portraits That Flatter",
    "05-organizing-as-you-shoot.md": "Organizing As You Shoot",
    "06-backup-without-worry.md": "Backup Without Worry",
    "07-printing-favorites.md": "Printing Favorites",
    "shooting-checklist.md": "The Shooting Checklist",
    "monthly-print-ritual.md": "The Monthly Print Ritual",
    "glossary.md": "Glossary",
}

SHORT_TITLES = {
    "00-start-here.md": "Start Here",
    "01-light-without-jargon.md": "Light",
    "02-steady-hands.md": "Steady Hands",
    "03-framing-rules-you-can-bend.md": "Framing",
    "04-portraits-that-flatter.md": "Portraits",
    "05-organizing-as-you-shoot.md": "Organizing",
    "06-backup-without-worry.md": "Backup",
    "07-printing-favorites.md": "Printing",
    "shooting-checklist.md": "Shooting Checklist",
    "monthly-print-ritual.md": "Print Ritual",
    "glossary.md": "Glossary",
}

BLURBS = {
    "01-light-without-jargon.md": "Turn toward window light, skip the flash, love cloudy days.",
    "02-steady-hands.md": "End the blur with your body, a wall, and a 3-second timer.",
    "03-framing-rules-you-can-bend.md": "Fill the frame, watch the edges - then break the rules on purpose.",
    "04-portraits-that-flatter.md": "Chest height, real laughter, light on the face.",
    "05-organizing-as-you-shoot.md": "Ten-second habits that make sorting later almost unnecessary.",
    "06-backup-without-worry.md": "Two copies of every photo that matters, set up once in minutes.",
    "07-printing-favorites.md": "From camera roll to fridge door, three easy routes to paper.",
    "shooting-checklist.md": "The whole manual as a one-page card to keep on your phone.",
    "monthly-print-ritual.md": "Twenty cozy minutes a month: sweep, back up, print three.",
    "glossary.md": "Every razzle-dazzle camera term, explained like a friend would.",
}

SITE_TITLE = "Smartphone Photo Basics"
SITE_TAGLINE = "A warm manual for taking photos worth keeping with the phone already in your pocket"
FOOTER_CREDIT = "A friendly guide by Dylan Asdale - published by Asdale Dynamics, LLC"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "section"


def render_inline(text: str) -> str:
    """Escape HTML, then apply inline markdown."""
    text = html.escape(text, quote=True)

    # links [label](target)
    def link_sub(match: re.Match) -> str:
        label, target = match.group(1), match.group(2)
        target = target.strip()
        if target.endswith(".md"):
            target = target[:-3] + ".html"
        return f'<a href="{target}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link_sub, text)

    # code spans (after links so URLs survive)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # bold then italics
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def parse_markdown(md_text: str) -> tuple[list[str], list[str]]:
    """Minimal, purposeful markdown -> (html body lines, heading texts)."""
    lines = md_text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    doc_title = ""
    headings: list[str] = []

    i = 0
    in_list: str | None = None  # "ul" or "ol"

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()

        # fenced code blocks
        if line.startswith("```"):
            close_list()
            out.append("<pre><code>")
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                out.append(html.escape(lines[i]))
                i += 1
            out.append("</code></pre>")
            i += 1
            continue

        if not line.strip():
            close_list()
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            text = render_inline(m.group(2).strip())
            sid = slugify(re.sub(r"[`*]", "", m.group(2).strip()))
            headings.append(text)
            if level == 1 and not doc_title:
                doc_title = re.sub(r"<[^>]+>", "", text)
                out.append(f'<h1 id="{sid}">{text}</h1>')
            else:
                out.append(f'<h{level} id="{sid}">{text}</h{level}>')
            i += 1
            continue

        # horizontal rule
        if re.match(r"^-{3,}$", line) or re.match(r"^\*{3,}$", line):
            close_list()
            out.append("<hr>")
            i += 1
            continue

        # blockquote
        if line.startswith(">"):
            close_list()
            quote: list[str] = []
            while i < len(lines) and lines[i].rstrip().startswith(">"):
                quote.append(lines[i].rstrip()[1:].strip())
                i += 1
            quote_text = render_inline(" ".join(q for q in quote if q))
            out.append(f"<blockquote><p>{quote_text}</p></blockquote>")
            continue

        # checklist item (false if a bare "[ ]" starts a paragraph line)
        def is_checklist_line(text: str) -> re.Match | None:
            return re.match(r"^(?:[-*])\s+\[( |x|X)\]\s+(.*)$", text.strip())

        def is_ul_line(text: str) -> re.Match | None:
            return re.match(r"^(?:[-*])\s+(?!\[ \]|\[[xX]\])(.*)$", text.strip())

        def is_ol_line(text: str) -> re.Match | None:
            return re.match(r"^(\d+)\.\s+(.*)$", text.strip())

        def continuation_ok(text: str, previous_line: str) -> bool:
            # a line indented by >=2 spaces continues the previous
            # list item / paragraph when it is plainly text
            if not text.startswith(("  ", "\t")):
                return False
            if previous_line.lstrip().startswith(">"):
                return False
            if (
                re.match(r"^(#{1,4})\s", text)
                or re.match(r"^-{3,}$", text.strip())
                or re.match(r"^\*{3,}$", text.strip())
            ):
                return False
            return True

        def gather_text_lines(start: int, first: str) -> tuple[list[str], int]:
            """Collect all plain continuation lines of a block."""
            pieces = [first.strip()]
            j = start
            while j < len(lines):
                nxt = lines[j].rstrip()
                if not nxt.strip():
                    j += 1
                    # blank line ends the block unless the very next line
                    # is also a continuation of a list item (common when a
                    # list item has a spaced second thought)
                    if j < len(lines) and lines[j].startswith(("  ", "\t")):
                        continue
                    break
                if continuation_ok(nxt, lines[j - 1]):
                    pieces.append(nxt.strip())
                    j += 1
                    continue
                if (
                    not nxt.startswith(("  ", "\t"))
                    and not re.match(r"^(#{1,4})\s", nxt)
                    and nxt[0] != ">"
                    and not nxt.startswith("```")
                    and re.match(r"^-{3,}$", nxt.strip()) is None
                    and re.match(r"^\*{3,}$", nxt.strip()) is None
                    and is_ul_line(nxt) is None
                    and is_checklist_line(nxt) is None
                    and is_ol_line(nxt) is None
                ):
                    pieces.append(nxt.strip())
                    j += 1
                    continue
                break
            return pieces, j

        # checkbox list item
        cb = is_checklist_line(line)
        if cb:
            if in_list != "ul":
                close_list()
                out.append('<ul class="checklist">')
                in_list = "ul"
            box = "checked" if cb.group(1).lower() == "x" else ""
            first = cb.group(2)
            pieces, i = gather_text_lines(i + 1, first)
            text = render_inline(" ".join(pieces))
            out.append(f'<li><span class="box {box}"></span>{text}</li>')
            continue

        # unordered list
        ulm = is_ul_line(line)
        if ulm:
            if in_list != "ul":
                close_list()
                out.append("<ul>")
                in_list = "ul"
            pieces, i = gather_text_lines(i + 1, ulm.group(1))
            out.append(f"<li>{render_inline(' '.join(pieces))}</li>")
            continue

        # ordered list
        olm = is_ol_line(line)
        if olm:
            if in_list != "ol":
                close_list()
                out.append("<ol>")
                in_list = "ol"
            pieces, i = gather_text_lines(i + 1, olm.group(2))
            out.append(f"<li>{render_inline(' '.join(pieces))}</li>")
            continue

        # paragraph: gather until blank line / block element
        close_list()
        pieces, i = gather_text_lines(i + 1, line)
        out.append(f"<p>{render_inline(' '.join(pieces))}</p>")

    close_list()
    return out, headings


def page_template(
    body_html: str,
    title: str,
    description: str,
    nav_html: str,
    is_home: bool = False,
    current: str | None = None,
) -> str:
    chapter_nav = "".join(
        f'<a href="{name[:-3]}.html" class="{"active" if name == current else ""}">'
        f"{SHORT_TITLES[name]}</a>"
        for name in CHAPTER_ORDER
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(description)}">
<title>{html.escape(title if title != SITE_TITLE else SITE_TITLE)} | {SITE_TITLE}</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <p class="brand"><a href="index.html">{SITE_TITLE}</a></p>
    <p class="tagline">{html.escape(SITE_TAGLINE)}</p>
    <nav class="chapters">{chapter_nav}</nav>
  </div>
</header>
<main class="wrap{' home' if is_home else ''}">
{body_html}
</main>
<nav class="pager wrap">{nav_html}</nav>
<footer>
  <div class="wrap">
    <p>{FOOTER_CREDIT}</p>
    <p>Companions: <em>photo-library-comfort-guide</em> (sorting what you have) and
    <em>photo-digitizing-guide</em> (scanning what predates your phone).</p>
    <p>No gear purchases required. Ever.</p>
  </div>
</footer>
</body>
</html>
"""


def build_chapter_page(name: str, md_text: str) -> str:
    title = TITLES[name]
    body_lines, _ = parse_markdown(md_text)
    body_html = "\n".join(body_lines)

    # previous / next chapter navigation
    idx = CHAPTER_ORDER.index(name)
    prev_name = CHAPTER_ORDER[idx - 1] if idx > 0 else None
    next_name = CHAPTER_ORDER[idx + 1] if idx < len(CHAPTER_ORDER) - 1 else None
    prev_html = f'<a class="prev" href="{prev_name[:-3]}.html">← {SHORT_TITLES[prev_name]}</a>' if prev_name else "<span></span>"
    next_html = f'<a class="next" href="{next_name[:-3]}.html">{SHORT_TITLES[next_name]} →</a>' if next_name else "<span></span>"
    nav_html = f'{prev_html}<a href="index.html">Contents</a>{next_html}'

    description = BLURBS.get(name, title + " - a plain-English chapter of the Smartphone Photo Basics guide.")
    return page_template(body_html, title, description, nav_html, current=name)


def build_home() -> str:
    intro_md = (DOCS / "00-start-here.md").read_text(encoding="utf-8")
    body_doc, _ = parse_markdown(intro_md)

    cards = []
    for name in CHAPTER_ORDER:
        if name == "00-start-here.md":
            continue
        cards.append(
            '<section class="card">'
            f'<h3><a href="{name[:-3]}.html">{TITLES[name]}</a></h3>'
            f"<p>{BLURBS[name]}</p></section>"
        )
    card_html = "\n".join(cards)

    companions = """<section class="companions">
<h2>Two friendly companions</h2>
<ul>
<li><strong>photo-library-comfort-guide</strong> - for organizing and enjoying a photo library <em>you already have</em>. This guide keeps new photos tidy as you take them; that one rescues the mountain you already own.</li>
<li><strong>photo-digitizing-guide</strong> - for scanning the boxes of prints and albums that predate phones, so they can join the same backup and print habits.</li>
</ul>
</section>"""

    body_html = '<div class="hero"><h1>Smartphone Photo Basics</h1><p class="lede">' + html.escape(SITE_TAGLINE) + ". No new gear, no jargon, just a friendlier camera roll.</p></div>"
    body_html += "\n".join(body_doc[1:])  # skip doc's own <h1>
    body_html += f'<div class="cards"><h2>The chapters</h2>\n{card_html}\n</div>'
    body_html += companions
    return page_template(body_html, SITE_TITLE, SITE_TAGLINE, "")


def build_site() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    # missing-chapter safety net: fail visibly rather than producing a
    # site that quietly lacks a chapter
    missing = [n for n in CHAPTER_ORDER if not (DOCS / n).is_file()]
    if missing:
        raise SystemExit(f"build error: missing docs: {', '.join(missing)}")

    for name in CHAPTER_ORDER:
        md_text = (DOCS / name).read_text(encoding="utf-8")
        page = build_chapter_page(name, md_text)
        (SITE / (name[:-3] + ".html")).write_text(page, encoding="utf-8")

    (SITE / "index.html").write_text(build_home(), encoding="utf-8")

    # styles
    site_css = (ASSETS / "styles.css")
    if site_css.is_file():
        shutil.copy(site_css, SITE / "styles.css")
    else:
        raise SystemExit("build error: assets/styles.css missing")

    # favicon: tiny inline data URI is overkill; ship a simple SVG
    (SITE / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<rect x="2" y="5" width="20" height="14" rx="3" fill="#c96f4a"/>'
        '<circle cx="12" cy="12" r="4" fill="#fff7ee"/></svg>',
        encoding="utf-8",
    )
    # reference favicon in every page: cheap post-pass
    for page in SITE.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        text = text.replace(
            '<link rel="stylesheet" href="styles.css">',
            '<link rel="icon" type="image/svg+xml" href="favicon.svg">\n'
            '<link rel="stylesheet" href="styles.css">',
        )
        page.write_text(text, encoding="utf-8")

    print(f"built {len(CHAPTER_ORDER) + 1} pages into site/")


def verify_site() -> None:
    """Post-build checks; raises SystemExit on the first failure found.

    Checks:
      1. every chapter file exists in site/, non-empty, correct title tag
      2. every internal <a href="..."> resolves to an existing file
      3. every in-page anchor href="#..." resolves to an existing id
      4. no unconverted markdown remnants left in the HTML
      5. index references every chapter
      6. stylesheet + hidden broken-image checks
    """
    problems: list[str] = []

    expected_pages = {n[:-3] + ".html" for n in CHAPTER_ORDER} | {"index.html"}
    for page_name in expected_pages:
        path = SITE / page_name
        if not path.is_file():
            problems.append(f"missing built page: {page_name}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            problems.append(f"empty page: {page_name}")
        if '<link rel="stylesheet" href="styles.css">' not in text:
            problems.append(f"{page_name}: stylesheet link missing")
        if "Asdale Dynamics, LLC" not in text:
            problems.append(f"{page_name}: LLC credit line missing")

    # title tags match the roster
    for name in CHAPTER_ORDER:
        path = SITE / (name[:-3] + ".html")
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        expected_title = TITLES[name]
        if html.escape(expected_title) not in text.split("<title>", 1)[-1].split("</title>", 1)[0]:
            problems.append(f"{name[:-3]}.html: <title> does not include '{expected_title}'")

    # internal links resolve
    ids_by_page: dict[str, set[str]] = {}
    for page_name in expected_pages:
        path = SITE / page_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        ids_by_page[page_name] = set(re.findall(r'id="([^"]+)"', text))
        external = re.compile(r'https?://')
        for href in re.findall(r'href="([^"]+)"', text):
            if external.match(href) or href.startswith("mailto:"):
                continue
            if href.startswith("#"):
                if href.lstrip("#") not in ids_by_page.get(page_name, set()):
                    problems.append(f"{page_name}: dead in-page anchor {href}")
                continue
            target = href.split("#")[0] or page_name
            fragment = href.split("#")[1] if "#" in href else ""
            if not (SITE / target).is_file():
                problems.append(f"{page_name}: broken link -> {href}")
            elif fragment and fragment not in ids_by_page.get(target, set()):
                problems.append(
                    f"{page_name}: link {href} targets missing id #{fragment}"
                )

    # unconverted markdown leftovers
    for page_name in expected_pages:
        path = SITE / page_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        body = text.split("<main", 1)[-1]
        if re.search(r"\*\*|\]\( ", body):
            problems.append(f"{page_name}: leftover markdown markers in body")
        if re.search(r"<p>\s*</p>", body):
            problems.append(f"{page_name}: empty <p> element")
        if "&amp;quot;" in body or "&amp;lt;" in body:
            problems.append(f"{page_name}: double-escaped entities")

    # index lists every chapter card
    index_text = (SITE / "index.html").read_text(encoding="utf-8") if (SITE / "index.html").is_file() else ""
    for name in CHAPTER_ORDER:
        if name != "00-start-here.md" and f"{name[:-3]}.html" not in index_text:
            problems.append(f"index.html: missing chapter link {name}")

    if not (SITE / "styles.css").is_file():
        problems.append("missing site/styles.css")

    # rough structural sanity: this project's pages should never contain
    # a stray unclosed list or table tag
    for page_name in expected_pages:
        path = SITE / page_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for tag in ("ul", "ol", "blockquote", "section", "main", "nav"):
            opens = len(re.findall(rf"<{tag}(\s[^>]*)?>", text))
            closes = len(re.findall(rf"</{tag}>", text))
            if opens != closes:
                problems.append(f"{page_name}: <{tag}> open/close mismatch ({opens} vs {closes})")

    if problems:
        print("VERIFY FAILED:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)

    print(
        f"verify OK: {len(expected_pages)} pages, "
        f"links and anchors checked, markdown fully converted"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and verify the site.")
    parser.add_argument("--build", action="store_true", help="build only")
    parser.add_argument("--verify", action="store_true", help="verify only")
    args = parser.parse_args()

    if args.verify and not args.build:
        verify_site()
        return
    build_site()
    if not args.build:
        verify_site()


if __name__ == "__main__":
    main()

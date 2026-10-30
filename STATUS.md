# STATUS.md — smartphone-photo-basics-guide

Last updated: 2026-10-30

## What was built

A complete, warm, plain-English manual for taking phone photos worth
keeping, delivered as both markdown documentation and a small static
HTML website built by a dependency-free Python script.

Original goal vs. what shipped — every element of the goal is present:

- **Light without jargon** — `docs/01-light-without-jargon.md`
- **Steady hands** — `docs/02-steady-hands.md`
- **Framing rules you can bend** — `docs/03-framing-rules-you-can-bend.md`
- **Portraits that flatter** — `docs/04-portraits-that-flatter.md`
- **Organizing shots as you take them** — `docs/05-organizing-as-you-shoot.md`
- **Safe backup** — `docs/06-backup-without-worry.md`
- **Printing favorites** — `docs/07-printing-favorites.md`
- **Shooting checklist** — `docs/shooting-checklist.md` (rendered as HTML checkboxes)
- **Monthly print ritual** — `docs/monthly-print-ritual.md`
- **Glossary** — `docs/glossary.md`
- **No gear purchases required** — stated throughout; every technique uses the phone and everyday objects
- **Markdown docs/ + static HTML site via build script** — `build.py` (stdlib only, no third-party packages)
- **Complements photo-library-comfort-guide and photo-digitizing-guide** — linked and described in README and in the site footer/Companions section
- **MIT LICENSE** — exact line: `Copyright (c) 2026 Asdale Dynamics, LLC`
- **README credit** — README "License" section and build footer credit Asdale Dynamics, LLC

## How to run it

```bash
python3 build.py             # build site/ from docs/, then self-verify
python3 build.py --build     # build only
python3 build.py --verify    # verify an existing build only

python3 -m http.server -d site 8000   # read the site at http://localhost:8000
```

Requirements: Python 3.8+ (standard library only). The markdown
sources in `docs/` are readable on their own without building.

## Verification results

Run on 2026-10-30, fresh build after deleting `site/`:

```
built 12 pages into site/
verify OK: 12 pages, links and anchors checked, markdown fully converted
python3 build.py --verify  → exit 0
```

`build.py --verify` checks per page: title correctness, stylesheet and
LLC credit presence, resolution of every internal link and `#anchor`,
absence of leftover markdown markers/empty paragraphs, and balanced
`<ul>/<ol>/<blockquote>/<section>/<main>/<nav>` tags. It also confirms
`index.html` links every chapter.

Negative tests (on temp copies, not the real tree):

- broken internal link injected → verify FAILED, exit 1
- `docs/glossary.md` removed → build error listing the missing doc, exit 1
- leftover `**` injected into a built page → verify FAILED, exit 1
- `python3 -m http.server -d site` served `index.html` and `styles.css` with HTTP 200

Manual inspection of rendered HTML (portrait chapter, checklist
checkboxes, glossary terms, index cards) confirmed clean output.

## Fixes made during this session

- Starter repo was empty; the entire project (docs, builder, styles,
  README, LICENSE) was authored here.
- Build script bug: `parse_markdown` return values unpacked in the wrong
  order, which char-split the body; fixed and re-run.
- Inline renderer treated each line separately, so bold spanning wrapped
  lines leaked `**` into output; reworked to gather paragraphs/list items/
  blockquotes first, then render markdown inline once per block.
- The verifier caught both of the above as failures before they shipped.

## Known gaps

- The site is tested as static files (presence, structure, links, tag
  balance); no headless-browser rendering test exists yet.
- No screenshot/visual review across browsers or dark mode.
- Markdown converter is intentionally minimal: supports headings,
  paragraphs, ordered/unordered/checklists, blockquotes, hr, code
  fences and spans, bold/italic/links. It does not support tables,
  images, or nested lists (none are used in this content).
- Companion guides (photo-library-comfort-guide, photo-digitizing-guide)
  are referenced by name only, since they live in separate projects.
- No CI workflow file; run `python3 build.py` as the test command.

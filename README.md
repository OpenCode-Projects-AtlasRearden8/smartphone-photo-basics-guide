# Smartphone Photo Basics

A warm, plain-English manual for taking photos worth keeping — with the
phone already in your pocket. No gear purchases required, no jargon,
no lectures. Light, steady hands, framing rules you can bend, portraits
that flatter, tidy-while-you-shoot habits, bulletproof backup habits,
and a monthly ritual that turns favorites into prints you can hold.

The site is built from `docs/` markdown into a small static HTML site
by a dependency-free Python build script — nothing to install, nothing
to sign up for.

## Why this exists

Most camera advice is written for people gearing up. This manual is
written for the person who already owns a camera 100% of the time and
just wants better photos of the people and days they love. Every
chapter ends with something small to try *today*, and the whole thing
compresses into three habits: **move toward light, tap the face,
favorite the keeper.**

## The chapters

| Chapter | What it covers |
| --- | --- |
| [Start Here](docs/00-start-here.md) | The one big idea, and how to read the manual |
| [Light Without Jargon](docs/01-light-without-jargon.md) | Window light, cloudy days, why the flash stays off |
| [Steady Hands](docs/02-steady-hands.md) | Ending blur with your body, a wall, and a timer |
| [Framing Rules You Can Bend](docs/03-framing-rules-you-can-bend.md) | Fill the frame, mind the edges, then break rules on purpose |
| [Portraits That Flatter](docs/04-portraits-that-flatter.md) | Chest height, real laughter, light on the face |
| [Organizing As You Shoot](docs/05-organizing-as-you-shoot.md) | Ten-second habits so sorting later takes minutes |
| [Backup Without Worry](docs/06-backup-without-worry.md) | Two copies of everything, set up once in minutes |
| [Printing Favorites](docs/07-printing-favorites.md) | Three easy routes from camera roll to paper |
| [Shooting Checklist](docs/shooting-checklist.md) | The whole manual as a one-page card |
| [Monthly Print Ritual](docs/monthly-print-ritual.md) | Twenty cozy minutes a month |
| [Glossary](docs/glossary.md) | Every camera term, explained like a friend would |

## Companion guides

- **photo-library-comfort-guide** — for organizing and enjoying a photo
  library you *already have*. This guide keeps new photos tidy as you
  take them; that one rescues the mountain that already exists.
- **photo-digitizing-guide** — for scanning the boxes of prints and
  albums that predate phones, so they can join the same backup and
  print habits.

## Building the site

Requirements: Python 3.8+ (standard library only; nothing to install).

```bash
python3 build.py             # build site/ and verify it
python3 build.py --build     # build only
python3 build.py --verify    # verify an existing build only
```

Then read the site as files in `site/`, or serve it locally:

```bash
python3 -m http.server -d site 8000
# open http://localhost:8000
```

### Verification checks

`build.py --verify` confirms, for every generated page:

- every chapter built, non-empty, with the right `<title>`;
- every internal link and `#anchor` resolves to a real target;
- no leftover markdown markers (`**`, `](`) or empty paragraphs;
- matched open/close tags for `<ul>`, `<ol>`, `<blockquote>`, `<section>`, `<main>`, `<nav>`;
- the stylesheet, LLC credit line, and chapter roster are present everywhere.

## Project layout

```
build.py               # md -> HTML build + verify (stdlib only)
docs/                  # all content, plain markdown
  00-start-here.md ... glossary.md
assets/styles.css      # warm, calm, print-friendly styling
site/                  # generated static site (do not edit by hand)
LICENSE                # MIT
STATUS.md              # current state, verification results, known gaps
```

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.

Published by **Asdale Dynamics, LLC**: beginner-friendly, plain-English,
local-first guides — clear, warm, polished, and tested.

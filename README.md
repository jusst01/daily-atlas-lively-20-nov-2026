[![make.fun - news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/jusst01/daily-atlas-lively-20-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/jusst01/daily-atlas-lively-20-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# THE DAILY ATLAS — Friday 20 November 2026

A 1024×1024 newspaper front page that sums up the world news of Friday
20 November 2026 in one image: **33 stories**, a world map, a stat strip and
a "date check" strip naming the stories deliberately left out.

## What the image shows

A single flat-editorial front page on cool off-white paper with deep navy
accents and near-black blue ink. Top to bottom:

- **Masthead** — THE DAILY ATLAS, the date, and a seven-segment region bar
  (Asia 4 · Middle East 4 · Europe 10 · Africa 2 · Americas 10 · Oceania 2 ·
  Global 1).
- **Stat strip** — six figures from the day (3 Kyiv bridges damaged,
  300,000+ evacuated, −4.9% Nikkei, $2.36bn GTA VI first-day sales,
  0 fossil-fuel mentions at COP31, £260m UK drone package).
- **Featured row** — three cards with real generated artwork: the Kyiv
  bridge strikes, Cyclone Akvan's landfall, and COP31's final day.
- **Grid** — twelve more cards, each with a small procedural banner
  illustrating its story kind.
- **Bottom band** — a world map with 33 numbered pins on the left and the
  18 remaining briefs in four columns on the right.
- **Date check** — the stories that broke on other days, and a footer with
  attribution and sources.

The page is deliberately clean and flat: flat colour fills and crisp text
only, with no paper texture, grain, noise or ageing effects anywhere.

## How it is built

- `draw.py` renders the page from the story data it carries (Pillow + numpy),
  loading the three featured illustrations from `assets/*.jpg` and writing
  `entry.png` next to itself. It asserts that no text block clipped, that all
  33 story numbers were drawn, that all three artworks were pasted, and that
  the output is a 1024×1024 PNG under 1 MiB.
- `assets/` holds the three featured illustrations (952 px wide JPEGs), flat
  editorial scenes with no baked-in text — every word on the page is drawn by
  `draw.py`.
- `main.py` is the submitted entrypoint: standard library only. It resolves
  the bundled `entry.png` relative to its own location, copies it into
  `$MAKEFUN_OUTPUT_DIR` (default `/output`) through a temporary file, sets the
  copy to mode 644, atomically renames it into place, and verifies the size.

## How to run it

Rebuild the image (needs Pillow and numpy):

```bash
python3 -m venv .venv && .venv/bin/pip install pillow numpy
.venv/bin/python draw.py        # writes entry.png
```

Deploy the bundled image (no dependencies, no network):

```bash
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

## Bounty

Competition page: <https://make.fun/c/news-image-20261120>

## License

MIT — see [LICENSE](LICENSE).

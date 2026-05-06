# HTML Artifact Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static HTML artifact at `site/` that renders the Phase 0 evidence memo in editorial-longform style, with a sticky TOC, reading-progress bar, 12 inline static charts, and 2 interactive charts (precinct map and multi-baseline view), suitable for publishing at `zarrenkuzma.com/nyc-strategy/`.

**Architecture:** Pure static HTML/CSS/JS. No build step, no framework, no npm. Memo body lives directly in `site/index.html`. Two interactive charts use Observable Plot loaded from a CDN; both have static PNG fallbacks. A small Python script (`scripts/build_site_data.py`) generates the JSON data files and copies chart assets from the existing project. Newsreader (body) + Inter (UI) loaded from Google Fonts CDN. Single stylesheet.

**Tech Stack:** HTML5, CSS3 (custom properties, grid, sticky positioning, Intersection Observer), vanilla ES2020 JavaScript, Observable Plot via CDN, Google Fonts CDN, Python 3.11 (pandas + geopandas) for the one-time build script.

**Spec:** `docs/superpowers/specs/2026-05-06-html-artifact-design.md`. Read before starting.

---

## File Structure

```
nyc-strategy-artifact/
  scripts/
    build_site_data.py            # Python; copies chart PNGs + builds JSON data
    test_build_site_data.py       # pytest tests for the build script
  site/
    index.html                    # the memo, single page
    styles.css                    # one stylesheet
    favicon.svg                   # simple monogram
    js/
      progress-bar.js             # reading-progress + sticky TOC active state
      precinct-map.js             # interactive chart 06
      multi-baseline.js           # interactive chart 14
    data/
      precincts.geojson           # NYC police-precinct boundaries (copied from data/geo/)
      precinct-stats.json         # 2017/2024 counts + percent change per precinct
      baseline-data.json          # NYC vs national comparison numbers (hand-curated)
    assets/
      og-image.png                # Open Graph + Twitter Card share image
      charts/
        01-hero.png
        02-majors.png
        03-dv-split.png
        04-stacked.png
        05-trajectories.png
        06-precinct-growth.png
        07-beds.png
        08-distal.png
        09-bheard-breakdown.png
        10-bheard-coverage.png
        11-timeline.png
        12-dv-rank.png
        13-quadrant.png
        14-baselines.png
```

---

## Task 1: Build script + tests for site data

**Files:**
- Create: `scripts/build_site_data.py`
- Create: `scripts/test_build_site_data.py`

The build script does four things: copies the 14 chart PNGs from `figures/sketches/` to `site/assets/charts/` with renamed paths; copies `data/geo/precincts.geojson` to `site/data/precincts.geojson`; converts `data/processed/aggregates/felony_precinct_yearly.parquet` to `site/data/precinct-stats.json`; writes `site/data/baseline-data.json` with hand-curated numbers from the memo. Wrap each step in a function and test independently.

- [ ] **Step 1.1: Write failing tests for the build script**

Create `scripts/test_build_site_data.py`:

```python
"""Tests for scripts/build_site_data.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_chart_renames_complete():
    """All 14 charts must be present in site/assets/charts/ with renamed paths."""
    from scripts.build_site_data import RENAME_MAP, copy_charts
    site_dir = ROOT / "site"
    copy_charts(ROOT / "figures" / "sketches", site_dir / "assets" / "charts")
    expected = {
        "01-hero.png", "02-majors.png", "03-dv-split.png",
        "04-stacked.png", "05-trajectories.png", "06-precinct-growth.png",
        "07-beds.png", "08-distal.png", "09-bheard-breakdown.png",
        "10-bheard-coverage.png", "11-timeline.png", "12-dv-rank.png",
        "13-quadrant.png", "14-baselines.png",
    }
    actual = {p.name for p in (site_dir / "assets" / "charts").glob("*.png")}
    assert expected.issubset(actual), f"Missing: {expected - actual}"
    assert len(RENAME_MAP) == 14


def test_precinct_stats_shape():
    """precinct-stats.json must include count_2017, count_2024, pct_change per precinct."""
    from scripts.build_site_data import build_precinct_stats
    out_path = ROOT / "site" / "data" / "precinct-stats.json"
    build_precinct_stats(
        ROOT / "data" / "processed" / "aggregates" / "felony_precinct_yearly.parquet",
        out_path,
    )
    data = json.loads(out_path.read_text())
    assert isinstance(data, list)
    assert len(data) >= 76, "Expected at least 76 precincts with both 2017 and 2024 data"
    sample = data[0]
    assert set(sample.keys()) == {"precinct", "count_2017", "count_2024", "pct_change"}
    assert isinstance(sample["precinct"], int)
    assert isinstance(sample["pct_change"], (int, float))


def test_baseline_data_shape():
    """baseline-data.json must include four panels with the values from the memo."""
    from scripts.build_site_data import write_baseline_data
    out_path = ROOT / "site" / "data" / "baseline-data.json"
    write_baseline_data(out_path)
    data = json.loads(out_path.read_text())
    assert set(data.keys()) == {"one_year", "five_year", "decade", "national"}
    assert data["decade"]["adjusted"] == 47
    assert data["national"]["nyc_adjusted"] == 47


def test_geojson_copied():
    """precincts.geojson must be copied to site/data/."""
    from scripts.build_site_data import copy_geojson
    src = ROOT / "data" / "geo" / "precincts.geojson"
    dst = ROOT / "site" / "data" / "precincts.geojson"
    copy_geojson(src, dst)
    assert dst.exists()
    assert dst.stat().st_size > 1000
```

- [ ] **Step 1.2: Run tests; expect them to fail**

Run:

```bash
cd /home/zkuzma8/claude_code/nyc-strategy-artifact
.venv/bin/python -m pytest scripts/test_build_site_data.py -v
```

Expected: ImportError (module `scripts.build_site_data` does not exist) or 4 failures.

- [ ] **Step 1.3: Implement the build script**

Create `scripts/build_site_data.py`:

```python
"""Build the site/ data assets from the project sources.

Run once (or whenever underlying data changes):
    .venv/bin/python scripts/build_site_data.py

This copies the 14 chart PNGs from figures/sketches/ to site/assets/charts/,
copies the precinct geojson, generates per-precinct stats JSON, and writes
hand-curated baseline data for the multi-baseline interactive chart.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Map source filename in figures/sketches/ to dest filename in site/assets/charts/
RENAME_MAP = {
    "01_hero_bignumber.png": "01-hero.png",
    "02_situation_majors.png": "02-majors.png",
    "03_dv_split.png": "03-dv-split.png",
    "04_complication_stacked.png": "04-stacked.png",
    "05_trajectories.png": "05-trajectories.png",
    "06_precinct_growth.png": "06-precinct-growth.png",
    "07_beds.png": "07-beds.png",
    "08_distal.png": "08-distal.png",
    "09_bheard_breakdown.png": "09-bheard-breakdown.png",
    "10_bheard_coverage.png": "10-bheard-coverage.png",
    "11_timeline.png": "11-timeline.png",
    "12_dv_rank.png": "12-dv-rank.png",
    "13_quadrant.png": "13-quadrant.png",
    "14_baselines.png": "14-baselines.png",
}


def copy_charts(src_dir: Path, dst_dir: Path) -> None:
    """Copy the 14 sketches to dst_dir with renamed filenames."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in RENAME_MAP.items():
        src = src_dir / src_name
        if not src.exists():
            raise FileNotFoundError(f"Missing source chart: {src}")
        shutil.copy2(src, dst_dir / dst_name)


def copy_geojson(src: Path, dst: Path) -> None:
    """Copy the precinct geojson to the site data dir."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_precinct_stats(parquet_path: Path, out_path: Path) -> None:
    """Convert per-precinct felony-assault counts to a JSON the precinct-map JS reads."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(parquet_path)
    fa = df[df.ofns_desc == "FELONY ASSAULT"].copy()
    fa.addr_pct_cd = pd.to_numeric(fa.addr_pct_cd, errors="coerce")
    pivot = fa.pivot_table(
        index="addr_pct_cd", columns="year", values="n", aggfunc="sum"
    ).fillna(0)
    rows = []
    for pct in pivot.index:
        if pd.isna(pct):
            continue
        c2017 = float(pivot.loc[pct].get(2017, 0))
        c2024 = float(pivot.loc[pct].get(2024, 0))
        if c2017 == 0:
            continue
        rows.append({
            "precinct": int(pct),
            "count_2017": int(c2017),
            "count_2024": int(c2024),
            "pct_change": round((c2024 / c2017 - 1) * 100, 1),
        })
    rows.sort(key=lambda r: r["precinct"])
    out_path.write_text(json.dumps(rows, indent=2))


def write_baseline_data(out_path: Path) -> None:
    """Hand-curated values from the memo for the multi-baseline interactive chart."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "one_year": {
            "label": "1-year (2023 to 2024)",
            "value": 5.8,
            "note": "NYPD year-end 2024 reporting.",
        },
        "five_year": {
            "label": "5-year (2019 to 2024)",
            "value": 41.4,
            "note": "Indexed off 2019 (pre-COVID baseline).",
        },
        "decade": {
            "headline": 72,
            "adjusted": 47,
            "label": "Decade (2010 to 2024)",
            "note": "Adjusted figure subtracts Strangulation 1st reclassification from both endpoints.",
        },
        "national": {
            "label": "National context",
            "nyc_adjusted": 47,
            "us_national": 2,
            "ccj_24_city": 4,
            "la_yoy": -10,
            "note": "NYC's reclassification-adjusted decade rise vs FBI national rate, "
                    "Council on Criminal Justice 24-city sample, and LAPD 2024 year-over-year.",
        },
    }
    out_path.write_text(json.dumps(data, indent=2))


def main() -> None:
    site_dir = ROOT / "site"
    copy_charts(ROOT / "figures" / "sketches", site_dir / "assets" / "charts")
    copy_geojson(ROOT / "data" / "geo" / "precincts.geojson", site_dir / "data" / "precincts.geojson")
    build_precinct_stats(
        ROOT / "data" / "processed" / "aggregates" / "felony_precinct_yearly.parquet",
        site_dir / "data" / "precinct-stats.json",
    )
    write_baseline_data(site_dir / "data" / "baseline-data.json")
    print(f"Wrote site assets to {site_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 1.4: Run tests; expect them to pass**

Run:

```bash
.venv/bin/python -m pytest scripts/test_build_site_data.py -v
```

Expected: 4 passed.

- [ ] **Step 1.5: Run the build script end-to-end**

Run:

```bash
.venv/bin/python scripts/build_site_data.py
ls site/assets/charts/ | wc -l   # expect 14
ls site/data/                    # expect: baseline-data.json, precinct-stats.json, precincts.geojson
```

- [ ] **Step 1.6: Commit**

```bash
git add scripts/build_site_data.py scripts/test_build_site_data.py site/
git commit -m "Add build script and tests for site data"
```

---

## Task 2: Site skeleton (HTML + CSS scaffolding)

**Files:**
- Create: `site/index.html`
- Create: `site/styles.css`

This task creates the skeleton: page metadata, hero block, two-column body grid (TOC + main), and footer. Sections inside `main` are stubs to be filled in later tasks. Goal: open `site/index.html` in a browser and see a styled (but mostly empty) page with the right typography, color, and layout grid.

- [ ] **Step 2.1: Create the HTML skeleton**

Create `site/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NYC has a sustained, domestic-violence-driven assault crisis | Zarren Kuzma</title>
  <meta name="description" content="A NYC strategy memo on the sustained, DV-driven felony-assault rise. Built as a public artifact by Zarren Kuzma.">
  <link rel="stylesheet" href="styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
</head>
<body>

  <div class="progress-bar" role="progressbar" aria-label="Reading progress" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>

  <header class="topbar">
    <div class="site-mark">zarrenkuzma.com</div>
    <div class="reading-time">22 min read</div>
  </header>

  <article>

    <section class="hero" id="hero">
      <!-- Hero content fills in Task 3 -->
    </section>

    <div class="body-grid">

      <nav class="toc" role="navigation" aria-label="Table of contents">
        <div class="toc-label">Contents</div>
        <ul>
          <li><a href="#in-brief">In brief</a></li>
          <li><a href="#numbers">What the numbers show</a></li>
          <li><a href="#response">Why the city has not responded</a></li>
          <li><a href="#what-to-do">What to do</a></li>
          <li><a href="#sources">Sources</a></li>
          <li><a href="#methodology">Methodology</a></li>
          <li><a href="#appendix">Appendix</a></li>
        </ul>
      </nav>

      <main class="body">
        <section id="in-brief"><h2>In brief</h2><!-- Task 5 --></section>
        <section id="numbers"><h2>What the numbers show</h2><!-- Task 6 --></section>
        <section id="response"><h2>Why the city has not responded</h2><!-- Task 7 --></section>
        <section id="what-to-do"><h2>What to do</h2><!-- Task 8 --></section>
        <section id="sources"><h2>Sources</h2><!-- Task 9 --></section>
        <section id="methodology"><h2>Methodology</h2><!-- Task 10 --></section>
        <section id="appendix"><h2>Appendix</h2><!-- Task 11 --></section>
      </main>

    </div>

  </article>

  <footer class="site-footer">
    <!-- Footer fills in Task 12 -->
  </footer>

  <script src="js/progress-bar.js" defer></script>
  <script src="js/precinct-map.js" defer></script>
  <script src="js/multi-baseline.js" defer></script>

</body>
</html>
```

- [ ] **Step 2.2: Create the stylesheet**

Create `site/styles.css`:

```css
/* ---------- variables + reset ---------- */
:root {
  --orange: #FF6319;
  --magenta: #D8127B;
  --navy: #003C71;
  --ink: #1a1a1a;
  --paper: #fafaf7;
  --mute: #888888;
  --light: #e8e8e8;

  --font-body: 'Newsreader', Georgia, 'Times New Roman', serif;
  --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  --content-max: 720px;
  --toc-width: 200px;
  --content-gap: 60px;

  --space-1: 6px;
  --space-2: 12px;
  --space-3: 18px;
  --space-4: 24px;
  --space-5: 36px;
  --space-6: 48px;
  --space-7: 72px;
}

*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: var(--font-body);
  font-size: 18px;
  line-height: 1.65;
  color: var(--ink);
  background: #fff;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ---------- progress bar ---------- */
.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 0;
  background: var(--orange);
  z-index: 100;
  transition: width 60ms linear;
}

/* ---------- top bar ---------- */
.topbar {
  font-family: var(--font-ui);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--light);
  font-size: 13px;
  color: var(--mute);
}
.topbar .site-mark {
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0.2px;
}

/* ---------- hero (Task 3 fills in) ---------- */
.hero {
  padding: var(--space-7) var(--space-5) var(--space-6);
  max-width: 900px;
  margin: 0 auto;
}

/* ---------- body grid ---------- */
.body-grid {
  display: grid;
  grid-template-columns: var(--toc-width) 1fr;
  gap: var(--content-gap);
  padding: 0 var(--space-5) var(--space-7);
  max-width: 1100px;
  margin: 0 auto;
}

@media (max-width: 880px) {
  .body-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
}

/* ---------- TOC ---------- */
.toc {
  font-family: var(--font-ui);
  position: sticky;
  top: var(--space-4);
  align-self: start;
  font-size: 14px;
  line-height: 1.7;
}
.toc .toc-label {
  text-transform: uppercase;
  letter-spacing: 1.4px;
  font-size: 10px;
  color: var(--mute);
  font-weight: 600;
  margin-bottom: var(--space-2);
}
.toc ul {
  list-style: none;
  padding: 0;
  margin: 0;
  border-left: 2px solid var(--light);
}
.toc li { margin: 0; }
.toc a {
  display: block;
  padding: 4px 0 4px 14px;
  color: var(--mute);
  text-decoration: none;
  transition: color 100ms ease;
}
.toc a:hover { color: var(--ink); }
.toc li.active a {
  color: var(--ink);
  font-weight: 600;
  border-left: 2px solid var(--orange);
  margin-left: -2px;
  padding-left: 14px;
}

@media (max-width: 880px) {
  .toc {
    position: static;
    border-bottom: 1px solid var(--light);
    padding-bottom: var(--space-3);
    margin-bottom: var(--space-3);
  }
}

/* ---------- main body ---------- */
.body {
  max-width: var(--content-max);
}
.body h2 {
  font-family: var(--font-body);
  font-size: 30px;
  line-height: 1.20;
  font-weight: 700;
  margin: var(--space-6) 0 var(--space-3);
  color: var(--ink);
  letter-spacing: -0.3px;
  scroll-margin-top: var(--space-4);
}
.body h3 {
  font-family: var(--font-body);
  font-size: 22px;
  line-height: 1.30;
  font-weight: 700;
  margin: var(--space-5) 0 var(--space-2);
  color: var(--ink);
  letter-spacing: -0.2px;
}
.body p {
  margin: 0 0 var(--space-3);
}
.body p strong { font-weight: 700; color: var(--ink); }
.body p em { font-style: italic; }
.body a {
  color: var(--navy);
  text-decoration: underline;
  text-decoration-color: var(--light);
  text-underline-offset: 2px;
  transition: text-decoration-color 120ms ease;
}
.body a:hover { text-decoration-color: var(--orange); }

.body ul, .body ol {
  padding-left: var(--space-4);
  margin: 0 0 var(--space-3);
}
.body ul li, .body ol li {
  margin: 0 0 var(--space-2);
}

/* ---------- figures / charts ---------- */
.body figure {
  margin: var(--space-5) 0;
  padding: var(--space-3);
  background: var(--paper);
  border-radius: 4px;
}
.body figure img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 3px;
}
.body figcaption {
  font-family: var(--font-ui);
  font-size: 13px;
  font-style: italic;
  color: var(--mute);
  line-height: 1.5;
  margin-top: var(--space-2);
}

/* ---------- tables ---------- */
.body table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-ui);
  font-size: 14px;
  margin: var(--space-4) 0;
}
.body table th,
.body table td {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--light);
  text-align: left;
  vertical-align: top;
  line-height: 1.5;
}
.body table th {
  font-weight: 600;
  color: var(--ink);
  border-bottom: 2px solid var(--ink);
}

/* ---------- footer ---------- */
.site-footer {
  font-family: var(--font-ui);
  background: var(--paper);
  padding: var(--space-6) var(--space-5);
  border-top: 1px solid var(--light);
  font-size: 13px;
  color: var(--mute);
  text-align: center;
}
.site-footer a { color: var(--navy); text-decoration: none; }
.site-footer a:hover { text-decoration: underline; }
```

- [ ] **Step 2.3: Verify the page renders**

Run:

```bash
cd /home/zkuzma8/claude_code/nyc-strategy-artifact/site
python3 -m http.server 8000
```

Then open `http://localhost:8000` in a browser. Expected: a page with the topbar, an empty hero area, a sticky-positioned TOC on the left, empty section stubs in the main column, and an empty footer at the bottom. Newsreader and Inter fonts are loading. No console errors.

Stop the server with Ctrl+C.

- [ ] **Step 2.4: Commit**

```bash
git add site/index.html site/styles.css
git commit -m "Add site skeleton with base typography and layout"
```

---

## Task 3: Hero section + chart 01

**Files:**
- Modify: `site/index.html` (replace `<section class="hero">` content)
- Modify: `site/styles.css` (add hero-specific rules)

The hero is the first thing a reader sees. Kicker (orange uppercase, Inter) → serif title → italic dek → byline → big-number hero chart.

- [ ] **Step 3.1: Add the hero content to index.html**

Replace the hero section in `site/index.html`:

```html
<section class="hero" id="hero">
  <div class="kicker">Strategy &middot; Public Safety &middot; New York City</div>
  <h1>NYC has a sustained, domestic-violence-driven assault crisis. The city's response is not scaling to meet it.</h1>
  <p class="dek">Felony assault is rising at multiples of the national rate. The story sits inside a single sub-category that the city's reporting framework hides. Here's what the data show, why the city has not responded, and what to do.</p>
  <div class="byline">By Zarren Kuzma &middot; May 2026 &middot; <a href="#methodology">Phase 0 Evidence Memo</a></div>
  <figure class="hero-figure">
    <img src="assets/charts/01-hero.png" alt="Headline chart: the +72% felony-assault headline overstates the rise. After stripping out the 2010 strangulation reclassification, the real behavioral rise is +47% from 2010 to 2024.">
    <figcaption>The +72% headline NYC's reporting would produce overstates the rise. Strip out the 2010 first-degree-strangulation reclassification and the real behavioral rise is about 47%.</figcaption>
  </figure>
</section>
```

- [ ] **Step 3.2: Add hero CSS rules**

Append to `site/styles.css`:

```css
/* ---------- hero content ---------- */
.hero .kicker {
  font-family: var(--font-ui);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.6px;
  color: var(--orange);
  font-weight: 600;
  margin-bottom: var(--space-3);
}
.hero h1 {
  font-family: var(--font-body);
  font-size: 44px;
  line-height: 1.15;
  font-weight: 700;
  margin: 0 0 var(--space-3);
  color: var(--ink);
  letter-spacing: -0.6px;
}
.hero .dek {
  font-family: var(--font-body);
  font-size: 22px;
  line-height: 1.5;
  font-style: italic;
  color: #444;
  margin: 0 0 var(--space-5);
}
.hero .byline {
  font-family: var(--font-ui);
  font-size: 13px;
  color: var(--mute);
  padding-top: var(--space-3);
  border-top: 1px solid var(--light);
  margin-bottom: var(--space-6);
}
.hero .byline a {
  color: var(--mute);
  text-decoration: underline;
  text-decoration-color: var(--light);
  text-underline-offset: 2px;
}
.hero-figure {
  margin: 0;
}
.hero-figure img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--light);
  border-radius: 4px;
}
.hero-figure figcaption {
  font-family: var(--font-ui);
  font-size: 13px;
  font-style: italic;
  color: var(--mute);
  line-height: 1.5;
  margin-top: var(--space-2);
}

@media (max-width: 880px) {
  .hero h1 { font-size: 32px; letter-spacing: -0.4px; }
  .hero .dek { font-size: 18px; }
}
```

- [ ] **Step 3.3: Verify**

Run a local server and open the page. Expected: hero shows kicker → title → dek → byline → chart 01 image. Image renders without 404 (the file `site/assets/charts/01-hero.png` was copied by the Task 1 build script).

```bash
cd /home/zkuzma8/claude_code/nyc-strategy-artifact/site && python3 -m http.server 8000
# open localhost:8000, verify, Ctrl+C
```

- [ ] **Step 3.4: Commit**

```bash
git add site/index.html site/styles.css
git commit -m "Add hero section with chart 01"
```

---

## Task 4: Reading-progress bar + sticky TOC active tracking (JS)

**Files:**
- Create: `site/js/progress-bar.js`

This is two related behaviors handled by one script: a reading-progress bar that fills as the user scrolls, and a TOC that highlights the active section using `IntersectionObserver`. Vanilla JS, no dependencies.

- [ ] **Step 4.1: Write the script**

Create `site/js/progress-bar.js`:

```javascript
/**
 * Reading-progress bar + sticky-TOC active-section tracking.
 *
 * - Reading progress: width of .progress-bar tracks scroll position vs document height.
 * - Active TOC: IntersectionObserver watches each <section> in main; the most-visible
 *   section's TOC <li> gets .active.
 *
 * Pure vanilla JS, no dependencies. Runs after DOMContentLoaded (defer attribute on <script>).
 */
(function () {
  "use strict";

  // --- reading progress ---
  const progressBar = document.querySelector('.progress-bar');

  function updateProgress() {
    if (!progressBar) return;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
    progressBar.style.width = pct + '%';
    progressBar.setAttribute('aria-valuenow', Math.round(pct));
  }

  // throttle scroll handler with requestAnimationFrame
  let scrollScheduled = false;
  window.addEventListener('scroll', function () {
    if (scrollScheduled) return;
    scrollScheduled = true;
    requestAnimationFrame(function () {
      updateProgress();
      scrollScheduled = false;
    });
  }, { passive: true });

  updateProgress(); // initial

  // --- active TOC section ---
  const tocItems = document.querySelectorAll('.toc li');
  const tocSections = Array.from(document.querySelectorAll('.body section[id]'));

  function tocItemForId(id) {
    return Array.from(tocItems).find(function (li) {
      const a = li.querySelector('a');
      return a && a.getAttribute('href') === '#' + id;
    });
  }

  if (tocSections.length && 'IntersectionObserver' in window) {
    const visibilityMap = new Map();

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visibilityMap.set(entry.target.id, entry.intersectionRatio);
      });
      // pick the section with the highest intersection ratio (or first if all 0)
      let bestId = null;
      let bestRatio = -1;
      visibilityMap.forEach(function (ratio, id) {
        if (ratio > bestRatio) {
          bestRatio = ratio;
          bestId = id;
        }
      });
      tocItems.forEach(function (li) { li.classList.remove('active'); });
      if (bestId && bestRatio > 0) {
        const item = tocItemForId(bestId);
        if (item) item.classList.add('active');
      }
    }, {
      rootMargin: '-80px 0px -40% 0px',
      threshold: [0, 0.1, 0.25, 0.5, 0.75, 1.0],
    });

    tocSections.forEach(function (s) { observer.observe(s); });
  }

  // --- smooth scroll on TOC click ---
  document.querySelectorAll('.toc a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
```

- [ ] **Step 4.2: Verify in the browser**

Start the local server:

```bash
cd /home/zkuzma8/claude_code/nyc-strategy-artifact/site && python3 -m http.server 8000
```

Open `http://localhost:8000`, scroll the page, and verify:
- The orange progress bar at the top fills as you scroll.
- The TOC item highlights as you scroll into different sections (after Task 6, when there is content; at this stage with empty stubs, the active item updates as the section IDs come into view).
- Clicking a TOC item scrolls smoothly to that section.

Open DevTools Console: no errors.

Ctrl+C.

- [ ] **Step 4.3: Commit**

```bash
git add site/js/progress-bar.js
git commit -m "Add reading progress bar and active TOC tracking"
```

---

## Task 5: "In brief" section content

**Files:**
- Modify: `site/index.html` (replace the `#in-brief` section content)

Render the In brief content from `memos/phase0_evidence.md`. The In brief covers the synthesis paragraph, the three-part recommendation as a numbered list, the cost / funding paragraph, and the savings caveat paragraph.

- [ ] **Step 5.1: Replace the in-brief section in index.html**

Replace `<section id="in-brief">` with the following:

```html
<section id="in-brief">
  <h2>In brief</h2>

  <p>New York City (NYC) has a sustained, domestic-violence-driven assault crisis. The city's response is not scaling to meet it.</p>

  <p>Felony assault is NYC's largest violent-felony category. Domestic violence (DV) is the dominant driver of its rise. Between 2017 and 2024, DV-related felony assault grew about 73%, nearly twice the pace of other felony assault. Roughly 39% of all NYC felony assault involves people in the same household, which works out to about 11,500 of the 29,501 cases reported in 2024. The pattern is not part of a national trend. NYC's 47% behavioral rise from 2010 to 2024 sits well above the Federal Bureau of Investigation (FBI) national rate, which has been essentially flat over the same period, and well above the Council on Criminal Justice (CCJ) 24-city average of about 4% since 2019.</p>

  <p>Two things stop the city from acting on this. First, the city's standard reporting framework hides the structural rise. The headline number NYC's reporting would produce, comparing 2024 to 2010, is +72% in felony-assault counts. About 35 percentage points of that growth come from a 2010 statutory change rather than from new behavior: New York State created a new felony class called first-degree strangulation (codified at New York Penal Law section 121.13). Acts that had previously been charged as a misdemeanor or as Assault 2nd were now charged as Strangulation 1st, generating new felony counts without a behavioral change. Strip the reclassification out and the underlying behavioral rise is about 47%. NYC's standard reporting cadence, monthly and annual against the prior year, also hides the multi-year trend. October 2024 felony assault was down 1.9% versus October 2023. The same year ended up 5.8% versus 2023. Both numbers come from NYPD; both are accurate. The divergence is what choosing one window over another can do to the story.</p>

  <p>The second thing keeping the city from acting: real spending on DV prevention has not moved. The Human Resources Administration's "Domestic Violence Services" program area grew about 28% nominally from fiscal year (FY) 2017 to FY24, almost exactly tracking inflation. In real terms, spending is flat. Over the same period, DV-related felony assault rose about 73%. Combining those two figures, real spending per DV-related case fell about 42%. NYC City Council requested expansions for DV microgrants, legal services, and the HOME+ permanent-supportive-housing program in three consecutive budget cycles; each request was zeroed out in the Mayor's Executive Budget for FY24, FY25, and FY26.</p>

  <p>The recommendation is a three-part package, ordered by political cost and evidence strength.</p>

  <ol class="recommendation-list">
    <li><strong>Operationalize at scale the $650M Bridge to Home and supportive-housing pipeline that Mayor Adams announced in January 2025</strong> as part of the Care, Community, Action plan. Today's capacity, about 100 Bridge to Home beds plus 900 Safe Haven beds, covers roughly 5% of the announced 2,000-person target. Of all the levers in this memo, supportive housing has the strongest evidence for reducing the population-level conditions that produce DV-driven assault: stable housing keeps survivors from being trapped with abusers and gives clinical stability to the people most likely to escalate.</li>

    <li><strong>Expand the Behavioral Health Emergency Assistance Response Division (B-HEARD)</strong>, NYC's program for sending non-police EMS-led teams to mental-health 911 calls, to 24-hour operations. Implement the cause-tracking that the Comptroller's audit recommended. B-HEARD operates in 31 of NYC's 78 precincts and runs roughly 8 a.m. to 1 a.m. The 2024 Comptroller audit found that 35% of eligible in-hours calls did not get a B-HEARD team and explicitly did not track why. About 14,200 separate overnight calls fall outside the program's operating hours by design.</li>

    <li><strong>Run a pilot in four to six precincts of two domestic-violence-specific interventions:</strong> a Lethality Assessment Program (LAP), a structured 11-question screen that police administer to survivors at the scene of a DV incident, and an Offender-Focused Domestic Violence Initiative (OFDVI), modeled on the High Point, North Carolina program. Build in survivor-protection safeguards (interpreter access, an immigration-enforcement firewall, accessibility for Deaf and disabled survivors), reserve at least 30% of the implementation budget for culturally-specific DV organizations like Sakhi, Womankind, the Violence Intervention Program, and the Anti-Violence Project, and tie this third recommendation to a sunset clause that ends the pilot automatically if it does not hit a pre-set target after 24 to 36 months. The sunset is specific to recommendation three; it does not apply to recommendations one and two.</li>
  </ol>

  <p>Pilot annual cost is roughly $6 to $15M, about 0.3% of NYC's $4.22B FY26 projected budget gap. Plausible funding sources include reallocation from the NYPD operating budget (politically contentious), Mayor's Office of Criminal Justice (MOCJ) discretionary funds, federal Department of Justice (DOJ) Office on Violence Against Women grants, or a philanthropic match.</p>

  <p>Estimating the long-run savings is difficult. The pilot would reduce demand on city-funded services such as emergency-department visits, jail bed-days, homeless-shelter use, and Administration for Children's Services investigations. A reasonable directional estimate places those city-borne savings somewhere between about $5M and $35M per year. The wide range comes from real methodology issues: city services have both fixed and variable costs, so reducing demand by, say, ten percent does not reduce city spending by ten percent; the city still pays for staff, facilities, and infrastructure even if fewer people use the service. And not all the savings flow to NYC. Some accrue to state Medicaid, federal Medicare, or private insurers. The pilot is plausibly cost-neutral to modestly cost-saving on NYC's books in the central case, but the range should be treated as illustrative, not as a budgetable forecast. The primary deliverable of the evaluation cycle is rigorous evidence about what works in NYC.</p>
</section>
```

- [ ] **Step 5.2: Add styling for the recommendation list**

Append to `site/styles.css`:

```css
/* ---------- recommendation list (In brief) ---------- */
.body ol.recommendation-list {
  counter-reset: rec;
  list-style: none;
  padding-left: 0;
  margin: var(--space-4) 0;
}
.body ol.recommendation-list > li {
  counter-increment: rec;
  position: relative;
  padding-left: var(--space-6);
  margin-bottom: var(--space-4);
}
.body ol.recommendation-list > li::before {
  content: counter(rec);
  position: absolute;
  left: 0;
  top: 2px;
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: 700;
  color: var(--orange);
  background: var(--paper);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid var(--orange);
}
```

- [ ] **Step 5.3: Verify**

Open the page in a browser. The In brief section should render with the synthesis paragraph, four full prose paragraphs, the three numbered recommendations (each with an orange-circled number), and the cost-and-savings paragraphs. No console errors.

- [ ] **Step 5.4: Commit**

```bash
git add site/index.html site/styles.css
git commit -m "Add In brief section content"
```

---

## Task 6: "What the numbers show" section + static charts 02, 03, 05; placeholders for interactive 06 and 14

**Files:**
- Modify: `site/index.html` (replace the `#numbers` section content)

This section is the longest in the body. It has five bolded sub-claims, each followed by prose. Charts 02 (violent-felony category sizes), 03 (DV split), 05 (trajectories), 14 (multi-baseline view), and 06 (precinct map) are inline. Charts 06 and 14 are placed as PNGs first; the interactive versions (Tasks 13 and 14) replace them via DOM manipulation.

- [ ] **Step 6.1: Replace the numbers section in index.html**

Replace `<section id="numbers">` with the following:

```html
<section id="numbers">
  <h2>What the numbers show</h2>

  <p>NYC's public-safety conversation runs on aggregate metrics: NYPD's Index Crime, the seven-category Major Felony framework, the Mayor's monthly and annual announcements, and the NYPD CompStat 2.0 dashboard. The framing is almost always year-over-year, at the city level. Inside that conversation, four facts about felony assault stand out.</p>

  <p><strong>Felony assault is NYC's largest violent-felony category.</strong> In 2024 there were 29,501 felony-assault reports. That is roughly twice the next-largest violent felony (robbery at 16,567) and an order of magnitude more than rape (1,534) or murder (363). Grand Larceny at 47,808 is larger overall, but it is a property crime. Among the felonies that capture interpersonal harm, felony assault is by far the biggest. It is the highest felony-assault count NYC has recorded in the modern era.</p>

  <figure>
    <img src="assets/charts/02-majors.png" alt="Bar chart: felony assault dwarfs other violent-felony categories. 29,501 felony-assault reports in 2024, vs 16,567 robberies, 1,534 rapes, and 363 murders.">
    <figcaption>Felony assault dwarfs other violent-felony categories in 2024. Source: NYPD Complaint Data Historic.</figcaption>
  </figure>

  <p><strong>Domestic violence is the dominant driver of the rise.</strong> Vital City's analysis of NYPD data, citing the New York State Division of Criminal Justice Services (DCJS) DV feed, finds that domestic and elder assault rose about 73% from 2017 to 2024. Other felony assault grew about 40% over the same period. About 39% of NYC felony assault involves members of the same household, which works out to roughly 11,500 of the 29,501 cases in 2024. NYPD's public dataset does not contain a victim-relationship field, so the household-share figure is sourced from the DCJS feed.</p>

  <figure>
    <img src="assets/charts/03-dv-split.png" alt="Two-panel chart. Left: bar chart showing DV-related assault grew 73% from 2017 to 2024 vs 40% for other felony assault. Right: pie chart showing 11,505 DV-related cases (39%) and 17,996 other (61%) of 29,501 total.">
    <figcaption>DV-related felony assault grew nearly twice as fast as other felony assault since 2017. Source: Vital City analysis of NYPD data, citing the DCJS DV feed.</figcaption>
  </figure>

  <p><strong>Felony assault is the only violent-felony category showing a sustained rise.</strong> Indexed to 2017 equal to 1.0, felony assault has risen every year through 2024, ending at 1.46. Murder spiked during the pandemic and has since declined. Robbery and rape have stayed roughly flat. This is not a generalized public-safety deterioration. It is a specific, sustained pattern in felony assault, driven by DV inside the catch-all "Assault 2/1/Unclassified" sub-category.</p>

  <figure>
    <img src="assets/charts/05-trajectories.png" alt="Line chart: felony assault, indexed to 2017, rises every year through 2024 to 1.46. Murder spikes around 2020 and declines. Robbery and rape stay near 1.0.">
    <figcaption>Felony assault has risen every year since 2017. Murder spiked in the pandemic; robbery and rape are roughly flat. Source: NYPD Complaint Data Historic.</figcaption>
  </figure>

  <p><strong>The rise is not a national trend.</strong> The national aggravated-assault rate was roughly flat from 2010 to 2024 (FBI Uniform Crime Reporting: about 252 per 100,000 in 2010, about 256 per 100,000 in 2024 after the year's decline). The CCJ 24-city sample shows about 4% growth since 2019. The same sample posted a 4% year-over-year decline in 2024 while NYC ended the year up 5.8%. Peer cities are flattening or falling at exactly the moment NYC is still rising. Among individual peer cities, Los Angeles posted a roughly 10% year-over-year decline in 2024. Chicago was at multi-year highs through 2024 then down 16% in early 2025. Philadelphia's gun-related aggravated-assault counts fell sharply in 2024. Houston's 9% one-year rise is the high-end peer outlier. National Incident-Based Reporting System (NIBRS) data show the DV share of violent crime drifting from 25.6% in 2020 to 27.5% in 2024, a modest movement compared with NYC's 73% DV-related growth. Definitional differences (NY "felony assault" versus FBI "aggravated assault"), the FBI's transition from older Uniform Crime Reporting to NIBRS in 2021, and NYC's strangulation reclassification narrow the gap but do not close it.</p>

  <figure id="chart-14-container" data-chart="multi-baseline">
    <img src="assets/charts/14-baselines.png" alt="Four-panel comparison. Left to right: NYC 1-year +5.8%, NYC 5-year +41.4%, NYC decade headline +72% / adjusted +47%, and a national-context panel showing NYC adjusted +47%, US national +2%, 24-city avg +4%, and LA 2024 year-over-year minus 10%.">
    <figcaption>Four windows on the same metric. The decade scale puts NYC well above any peer benchmark. Source: NYPD; FBI; Council on Criminal Justice; LAPD 2024 year-end.</figcaption>
  </figure>

  <p><strong>The rise is broadly distributed, not concentrated.</strong> Of NYC's 78 precincts, 76 saw growth in felony-assault counts between 2017 and 2024. The largest single precinct accounted for only about 6% of the citywide increase. The top 10 together accounted for roughly 36%. The lever is categorical, not geographic. A citywide intervention is more appropriate than a hot-spots strategy.</p>

  <figure id="chart-06-container" data-chart="precinct-map">
    <img src="assets/charts/06-precinct-growth.png" alt="NYC choropleth map of felony-assault percent change per precinct, 2017 to 2024. 76 of 78 precincts saw growth; the largest contributor is about 6% of citywide growth, the top 10 about 36%.">
    <figcaption>76 of 78 precincts grew between 2017 and 2024. The rise is broadly distributed, not concentrated in a few hot spots. Source: NYPD Complaint Data Historic.</figcaption>
  </figure>
</section>
```

- [ ] **Step 6.2: Verify**

Open the page in a browser. The Numbers section should render with five bolded sub-claims and five inline figures (charts 02, 03, 05, 14, 06). All images load.

- [ ] **Step 6.3: Commit**

```bash
git add site/index.html
git commit -m "Add What the numbers show section with charts 02, 03, 05, and placeholders for 06 and 14"
```

---

## Task 7: "Why the city has not responded" section + chart 04

**Files:**
- Modify: `site/index.html` (replace the `#response` section content)

Two-point Complication. Chart 04 (stacked sub-categories) sits inside point 1.

- [ ] **Step 7.1: Replace the response section in index.html**

Replace `<section id="response">` with:

```html
<section id="response">
  <h2>Why the city has not responded</h2>

  <p>Two things stop the city from acting at scale.</p>

  <p><strong>The reporting framework hides the structural rise.</strong> NYC's standard reporting compares the current month or year against the prior month or year. By that frame, the multi-year picture never appears. The longer-window picture is also distorted by a 2010 statutory change. The headline NYC's reporting would produce, comparing 2024 to 2010, is +72% in felony-assault counts. About 4,400 of those 12,364 added cases come from a brand-new felony class created in November 2010: first-degree strangulation, codified at New York Penal Law section 121.13. Strangulation acts existed before 2010 but were charged under Assault 2nd or as a misdemeanor. After 2010, the same conduct generates a Strangulation 1st felony count. About 35 percentage points of the +72% headline are this reclassification, not new behavior. The underlying behavioral rise, after stripping it out, is about 47%. The reclassification adjustment has been quantified by Vital City and the Brennan Center. No NYC government publication has named it. The same window problem appears in NYPD's reporting cadence. The October 2024 monthly press release reported felony assault at minus 1.9% versus October 2023. The full year ended at plus 5.8% versus 2023. Both numbers come from NYPD; both are accurate. They tell different stories because they cover different time windows.</p>

  <figure>
    <img src="assets/charts/04-stacked.png" alt="Stacked bar chart, 2010 to 2024. Bars show DV-driven cases inside the catch-all (magenta) doubling from about 6,800 to 11,800; the rest of the catch-all (orange) growing more modestly; assault on police steady; Strangulation 1st (navy) appearing in 2010 and contributing about 35% of the headline rise; small new sub-categories accounting for the rest.">
    <figcaption>Felony-assault sub-categories, 2010 to 2024. The DV-driven share of the catch-all (magenta) accounts for most of the actual behavioral rise; Strangulation 1st (navy) is a 2010 statutory creation that explains roughly 35% of the headline figure. Source: NYPD Complaint Data Historic, drilled to pd_cd.</figcaption>
  </figure>

  <p><strong>Investment in DV prevention has not kept pace with the rise.</strong> The Human Resources Administration's (HRA) "Domestic Violence Services" program area, which consolidates the Mayor's Office to End Gender-Based Violence (ENDGBV) operations, the Family Justice Centers, the Teen Relationship Abuse Prevention Program (Teen RAPP), microgrants, and DV shelter contracts, grew about 28% nominally from FY17 ($131.5M adopted) to FY24 ($168.5M adopted). Inflation, measured by the Consumer Price Index for Urban Consumers, was approximately 28% over the same window. In real terms, spending on DV services is flat. Over the same period, DV-related felony assault rose about 73%. Real spending per DV-related case therefore fell roughly 42%. The NYC City Council requested expansions in three consecutive budget cycles: $4.8M in DV Housing Stability Microgrants in the FY24 budget response, and $8.3M across DV legal services, the HOME+ permanent-supportive-housing program (NYC's program for placing DV survivors and other priority populations into permanent supportive units), and microgrants in FY26. Each was zeroed out in the Mayor's Executive Budget. Mayor Adams' January 2024 Women's Agenda announced $43M across all gender-equity programs, multi-year and multi-agency; the DV-specific share included survivor-security alarms at $186K. The transfer of the Office of Crime Victim Services to ENDGBV (about $23.6M baselined FY26 forward) is the largest real expansion of ENDGBV's portfolio in the period, but it is a function transfer from MOCJ, not new dedicated DV funding.</p>

  <p>The combined effect is this. NYC's largest violent-crime category is rising sharply. The rise is driven by the most under-served population. The city's reporting choices and budget choices have not surfaced or responded to it.</p>
</section>
```

- [ ] **Step 7.2: Verify**

Open the page; the Response section renders with two bolded points and chart 04. No console errors.

- [ ] **Step 7.3: Commit**

```bash
git add site/index.html
git commit -m "Add Why the city has not responded section with chart 04"
```

---

## Task 8: "What to do" section + charts 07-13

**Files:**
- Modify: `site/index.html` (replace the `#what-to-do` section content)

Four sub-sections: The problem to solve, The space of possible action, The chosen levers, How to run the pilot. Charts inline at the right places.

- [ ] **Step 8.1: Replace the what-to-do section in index.html**

Replace `<section id="what-to-do">` with the following. (This is a large block; copy it in full.)

```html
<section id="what-to-do">
  <h2>What to do</h2>

  <h3>The problem to solve</h3>
  <p>NYC has a sustained, DV-driven felony-assault rise that the city's reporting hides and that its budget has not responded to. The action question runs in two steps. First, which interventions actually target this driver in the criminology literature, and of those, which fit NYC well enough to deploy or pilot? Second, how should the city actually execute on the chosen levers, with what funding, and with what guardrails?</p>

  <h3>The space of possible action</h3>
  <p>Five categories of intervention plausibly address NYC's DV-driven assault rise. Each has a different evidence quality and a different fit with NYC.</p>

  <p><strong>Structural drivers (housing and mental-health capacity).</strong> Permanent supportive housing places people experiencing homelessness or housing instability into long-term subsidized units paired with on-site services like case management and behavioral-health care. The evidence base is the longest-running and highest-quality of any intervention in this memo: the Tsemberis Pathways-to-Housing randomized controlled trials and their replications, plus the Culhane cost-offset studies. The connection to DV is direct. Survivors who can leave abusers need somewhere stable to go, and people in mental-health crisis are less likely to escalate to violence when they have a stable home and clinical care. New York State lost more than 700 state-operated inpatient psychiatric beds between 2014 and 2021, according to a Manhattan Institute report. That figure is corroborated by the NY State Comptroller's March 2024 report, which used Office of Mental Health data to find that broader statewide inpatient psychiatric capacity fell by 990 beds, a 10.5% decline, between April 2014 and December 2023. The political cost of supportive-housing investment is among the lowest of any lever here, because supportive housing has cross-coalition support. Dollars are partially authorized through the announced $650M Bridge to Home plan.</p>

  <p><strong>Mobile crisis response (B-HEARD-style mental-health teams).</strong> When a 911 call involves someone in mental-health crisis, sending an EMS-led non-police team can de-escalate situations that would otherwise lead to use of force or unnecessary hospitalization. A 2024 working paper from the National Bureau of Economic Research, an academic research nonprofit (Shem-Tov 2024), found that mobile crisis teams divert about 5 to 8% of police calls. A 2025 study in the peer-reviewed psychiatric journal <em>Psychiatric Services</em> found that NYC's B-HEARD program specifically reduced unnecessary emergency-department transports. This is not a DV-specific intervention, but DV calls often involve mental-health crises, and a non-police response reduces the chance the call escalates to violence. The model has mid-quality evidence and is already established in NYC.</p>

  <p><strong>DV-specific policing and advocacy interventions.</strong> Three programs in this category have published evaluations.</p>

  <p>The Lethality Assessment Program (LAP) is a structured 11-question screen that police administer to survivors at the scene of a DV incident. Questions cover the abuser's history of violence, access to weapons, threats to kill, and similar risk factors. Survivors whose answers indicate high homicide risk get connected by phone to a trained advocate before police leave. The advocate offers immediate safety planning and shelter referral. Maryland adopted LAP statewide between 2007 and 2013 in a staggered rollout, which let researchers compare jurisdictions that adopted earlier with those that adopted later. Koppa (2024, <em>Journal of Economic Behavior &amp; Organization</em>) found a 35 to 45% reduction in female intimate-partner-homicide rate at the jurisdiction level. CrimeSolutions, the federal evidence-rating clearinghouse, classifies LAP as "Promising." The study is peer-reviewed but has not yet been independently replicated, and it is a single-state finding.</p>

  <p>The Offender-Focused Domestic Violence Initiative (OFDVI) is modeled on the High Point, North Carolina program. Police, prosecutors, and community members hold structured call-in meetings with high-risk DV offenders. The offenders are warned about the consequences of repeat offending and offered services. Sechrist and Weil 2018 reported about a 20% reduction in intimate-partner DV calls in High Point, in a single-site before-after analysis with no contemporaneous comparator (meaning the study did not compare High Point to similar cities that did not adopt the program).</p>

  <p>Mandatory arrest is a policy in which police arrest the primary aggressor at a DV scene rather than separating the parties. The original 1981-1982 Sherman and Berk Minneapolis Domestic Violence Experiment (a randomized controlled trial) showed 13% repeat-assault under arrest versus 26% under separation. Five-city replications produced mixed results. New York State already has a mandatory-arrest policy for felony DV, so this is not a new lever NYC could choose to add.</p>

  <p><strong>Community Violence Intervention (CVI) and credible-messenger work.</strong> This category includes NYC's Crisis Management System (CMS), which deploys credible-messenger outreach workers (often people with backgrounds in the communities they serve) to interrupt cycles of retaliatory violence. Comptroller Lander's 2024 report found a 21% reduction in shootings associated with CMS. The evidence is strong for shooting reduction. There is no published evaluation of CVI or credible-messenger programs targeting DV outcomes. Cure Violence Global's 50-plus international sites all target community or gun violence. Porting the model to DV would be a research bet, not a deployment bet.</p>

  <p><strong>Batterer-intervention programs.</strong> These are court-mandated group counseling programs for people convicted of DV offenses. The Duluth Model and cognitive-behavioral programs are the two main approaches; both require offenders to attend weekly sessions for 26 to 52 weeks as a condition of probation. Cheng and colleagues' 2021 meta-analysis found non-significant overall effects on re-offending. Not recommended.</p>

  <p>A note on what to expect from any of these programs in NYC. None of these effect sizes will translate one-for-one. The criminology literature shows that interventions which worked in smaller jurisdictions tend to produce smaller effects when scaled to large cities. There are several reasons. Study quality matters; when researchers use rigorous matched comparisons, the apparent effect typically shrinks to about a quarter of what less-rigorous studies report (Braga and Weisburd 2019, Campbell systematic review). Demographics differ; the Maryland LAP study and the High Point OFDVI study were both conducted in jurisdictions whose population sizes, racial compositions, and policing structures differ substantially from NYC's. And implementation quality is hard to replicate. Plan for any NYC pilot to produce roughly a 10 to 15% rate change in pilot precincts, not the headline figures from source studies.</p>

  <h3>The chosen levers</h3>
  <p>Three programs, ordered by political cost and evidence strength.</p>

  <p><strong>Lever 1: Operationalize the $650M Bridge to Home pipeline at scale.</strong> This is the strongest evidence base in the memo, the lowest political cost, and the dollars are already authorized. Today's capacity (about 100 Bridge to Home beds and 900 Safe Haven beds) covers about 5% of the announced 2,000-person target. The action: double the Bridge to Home bed count over 18 months; set up 72-hour discharge-to-bed protocols from Bellevue and NYC Health and Hospitals psychiatric emergency departments; pair the housing investment with tenant legal services so eviction does not push survivors and people in crisis back into shelter; and prioritize survivor-flagged clients in intake.</p>

  <figure>
    <img src="assets/charts/07-beds.png" alt="Stacked horizontal bar chart. Today: 100 Bridge to Home beds plus 900 Safe Haven beds, total 1,000, against a 2,000-person target. Recommended: 200 Bridge to Home beds plus 1,800 Safe Haven beds, total 2,000.">
    <figcaption>NYC has fewer than 100 supportive-housing beds against a 2,000-person target. Source: NYC Mayor's January 2025 Care, Community, Action announcement.</figcaption>
  </figure>

  <figure>
    <img src="assets/charts/08-distal.png" alt="Two indexed lines, both at 100 in 2014. NY State inpatient psychiatric beds drop to 75 by 2021 (a 25% decline). NYC felony assault rises to 146 by 2024 (a 46% increase).">
    <figcaption>As New York State inpatient psychiatric capacity contracted, NYC felony assault rose. Sources: Manhattan Institute and NY State Comptroller (psych beds); NYPD Complaint Data Historic (felony assault).</figcaption>
  </figure>

  <p><strong>Lever 2: Expand B-HEARD to 24-hour operations and implement audit-recommended cause-tracking.</strong> B-HEARD operates in 31 of 78 precincts. The 2024 Comptroller audit found that 35% of in-hours eligible calls did not get a B-HEARD team and explicitly did not track why. About 14,200 overnight calls fall outside the program's scope. There are two distinct fixes. Extend operating hours to overnight, which adds about 14,000 reachable calls per year (a structural fix). Implement the audit-recommended cause-tracking, which is what would let the city size a fix to the in-hours gap (an operational fix). The combined cost is roughly $30 to $50M annually beyond the current B-HEARD budget, plus or minus 50%.</p>

  <figure>
    <img src="assets/charts/09-bheard-breakdown.png" alt="Three-segment horizontal bar of B-HEARD eligibility outcomes per year. Got B-HEARD: 24,071 (47%). In-hours unserved with untracked cause: 13,042 (25%). Overnight unserved (program does not operate): 14,200 (28%).">
    <figcaption>How B-HEARD eligible calls split each year. The 35% in-hours unserved gap has untracked causes. The 14,200 overnight calls fall outside the program's hours by design. Source: NYC Comptroller 2024 audit.</figcaption>
  </figure>

  <figure>
    <img src="assets/charts/10-bheard-coverage.png" alt="Map of NYC police precincts. The 31 covered by B-HEARD are highlighted, concentrated in northern Manhattan, the Bronx, central Brooklyn, and parts of Queens. Staten Island and most of southern Brooklyn and Queens are uncovered.">
    <figcaption>B-HEARD currently operates in 31 of NYC's 78 precincts. Source: NYC Comptroller 2024 audit, Appendix II; reaffirmed by the Mayor's Office November 2025 release on the H+H operational transition.</figcaption>
  </figure>

  <p><strong>Lever 3: Pilot LAP and a NYC OFDVI program in four to six precincts.</strong> Among the DV-specific policing and advocacy interventions, LAP and OFDVI are the strongest-evidence options. They also carry implementation risks that the source studies did not measure. The pilot is meant to gather rigorous evidence about what works in NYC, not to deploy a known formula citywide.</p>

  <figure>
    <img src="assets/charts/12-dv-rank.png" alt="Horizontal bar chart ranking DV intervention effects. LAP (Maryland, Koppa JEBO 2024): 35-45% reduction in female intimate-partner-homicide rate. Mandatory arrest (MDVE): 5-21%. OFDVI (High Point): 12-28%. Batterer programs: -5 to +5% (null). CVI for DV: untested.">
    <figcaption>DV-intervention effect sizes, ranked. Sources: Koppa 2024 (Maryland LAP); Sherman and Berk MDVE; Sechrist and Weil 2018 (High Point OFDVI); Cheng et al. 2021 meta-analysis; Cure Violence Global.</figcaption>
  </figure>

  <figure>
    <img src="assets/charts/13-quadrant.png" alt="Two-by-two scatterplot. X axis: evidence quality. Y axis: DV relevance. LAP and OFDVI are in the top-right quadrant (DV-evaluated, strong evidence). CMS is bottom-right (strong evidence, not for DV). CMS-for-DV is top-left (DV-relevant but untested).">
    <figcaption>LAP and OFDVI are the only programs with both strong evidence and direct DV relevance. The other DV-relevant options are untested; the other strong-evidence options target gun or street violence, not DV. Source: derived from this memo's "What NYC has tried" review.</figcaption>
  </figure>

  <p>Three intervention categories are not in the recommendation. Community Violence Intervention adapted to DV is excluded because there is no published DV evaluation; the city would be running a research bet, not a deployment. Batterer-intervention programs are excluded because rigorous studies show null effects on re-offending. Hot-spots policing is excluded because it relies on a "place as driver" assumption (the idea that crime concentrates at specific street blocks) that does not fit DV; DV is driven by household relationships, not by place, and 76 of NYC's 78 precincts are showing growth, not a few hot blocks. A fuller note on hot-spots policing is in the appendix. Mandatory arrest is already in place in New York State, so it is not a lever NYC could choose to add.</p>

  <h3>How to run the pilot</h3>
  <p>Lever 3 carries the most risk and needs the most explicit design. The recommendations in this section apply specifically to Lever 3.</p>

  <p>There are four implementation risks the source studies did not measure. The LAP score could become a <em>gate</em> for advocate referral rather than an <em>enhancer</em>; that is, advocates might end up only serving survivors who score "high danger," even though moderate-risk and low-risk survivors today have access to the same hotline and shelter pathways. OFDVI call-in lists are pre-conviction rosters administered by police, which carries the same civil-liberties profile as gang-database programs. Pilot precincts selected purely for high DV incidence overlap with neighborhoods that are already over-policed in NYC. And $5 to $15M of new annual spending against a $4.22B FY26 budget gap has to come from somewhere; without a specified source, it displaces other spending.</p>

  <p>The pilot has to satisfy specific design conditions for the recommendation to hold up. These are binding conditions in the procurement contracts, not aspirational goals; if the city implements the pilot without them, the recommendation does not stand.</p>

  <p>For LAP, the lethality score must be <em>additive</em> to existing self-identified survivor pathways, never a replacement for them. Moderate-risk and low-risk survivors must keep access to the same hotline, advocate, and shelter pathways they had before LAP arrived. Trained interpreters must be available. Language must be gender-inclusive. There must be an immigration-enforcement firewall, meaning LAP responses do not generate Immigration and Customs Enforcement referrals. The program must be accessible to Deaf and disabled survivors (TTY, on-scene American Sign Language interpreters, or equivalent post-call protocols).</p>

  <p>For OFDVI, call-in inclusion must be limited to post-conviction history or judicially-confirmed restraining-order data, not arrest history alone. The roster must be publicly transparent, and inclusion must sunset; people roll off the list after a defined period rather than staying on indefinitely. An independent civil-liberties impact assessment must be commissioned in Phase 1, contracted to an entity outside NYPD and outside the National Network for Safe Communities (NNSC), the program developer; the Vera Institute or the New York University Center on Race, Inequality, and the Law are credible candidates.</p>

  <p>On geography, the city should pick pilot precincts that include both high-DV-incidence neighborhoods and mixed-incidence neighborhoods. Picking only the highest-incidence precincts would maximize the pilot's chance of detecting an effect, but it would concentrate the program in already-over-policed areas. Mixing precincts costs some statistical power and builds political legitimacy.</p>

  <p>On procurement, the implementation contracts must include a binding set-aside of at least 30% of the implementation budget for culturally-specific DV-survivor organizations such as Sakhi, Womankind, the Violence Intervention Program, the Anti-Violence Project, and Barrier Free Living, with the final list developed through ENDGBV consultation. The set-aside must be substantively binding by contract, not nominal.</p>

  <p>The sunset clause is the most important design feature, and it deserves an explanation. NYC's track record on terminating pilots that do not work is poor. B-HEARD, the Crisis Management System, and the Subway Safety Surge all continued or expanded despite null or mixed evaluations. If the sunset for this pilot is just a promise, it will not bind. The pilot should be funded for one Phase-1 evaluation cycle of 24 to 36 months. The primary endpoint, change in DV-felony rate in matched comparison precincts, must be pre-registered before the pilot starts. Funding ends automatically if the endpoint is not met under transparent identification (Callaway-Sant'Anna staggered difference-in-differences with formal pretrend tests). The sunset language is binding through the procurement-contract structure itself, not through a policy aspiration.</p>

  <figure>
    <img src="assets/charts/11-timeline.png" alt="Gantt-style timeline. Months 0-6: pilot design and staffing. Months 6-12: implementation in 4-6 precincts. Months 12-30: data collection. Months 24-30: evaluation. Month 30 marks the binding sunset gate.">
    <figcaption>Pilot timeline. The sunset gate at month 30 is binding through procurement-contract structure: funding ends automatically if the pre-registered endpoint is not met.</figcaption>
  </figure>

  <p>Pilot annual cost is roughly $3 to $8M for LAP, $2 to $5M for OFDVI, and $1 to $2M for evaluation, for a combined total of $6 to $15M per year, about 0.3% of NYC's $4.22B FY26 projected budget gap. Small in absolute terms, but it has to displace something. Plausible funding sources include reallocation from the NYPD operating budget (politically contentious), MOCJ discretionary funds, federal grant pass-throughs from the DOJ Office on Violence Against Women, and a philanthropic match (the NYC Fund for Public Health, the Robin Hood Foundation, or a similar partner).</p>

  <p>Estimating the long-run savings is difficult. The pilot would reduce demand on city-funded services such as emergency-department visits, jail bed-days, homeless-shelter use, and Administration for Children's Services investigations. A reasonable directional estimate places those city-borne savings somewhere between about $5M and $35M per year. Two methodology issues make precision impossible. First, city services have both fixed and variable costs. Reducing demand by ten percent does not reduce city spending by ten percent, because the city still pays for staff, facilities, and infrastructure even if fewer people use the service. Second, not all the savings flow to NYC; federal Medicaid, state Medicaid, federal Medicare, and private insurers cover much of the medical and shelter costs. The pilot is plausibly cost-neutral to modestly cost-saving on NYC's books at the central case. The range should be treated as illustrative, not as a budgetable forecast.</p>

  <p>Source-study effects (Koppa 35 to 45%, Sechrist and Weil 20%) almost certainly will not translate at face value. Plan for a 10 to 15% rate reduction in pilot precincts, with wide confidence intervals. Scale only what shows a statistically significant effect under transparent identification. The sunset clause is what makes that promise enforceable.</p>
</section>
```

- [ ] **Step 8.2: Verify**

Open the page; the What to do section renders with four sub-headings, prose, and seven inline figures (charts 07, 08, 09, 10, 11, 12, 13). All images load.

- [ ] **Step 8.3: Commit**

```bash
git add site/index.html
git commit -m "Add What to do section with charts 07 through 13"
```

---

## Task 9: Sources section

**Files:**
- Modify: `site/index.html` (replace the `#sources` section content)

Render the Sources lists from the memo. Group headings; bulleted link lists.

- [ ] **Step 9.1: Replace the sources section in index.html**

Replace `<section id="sources">` with:

```html
<section id="sources">
  <h2>Sources</h2>

  <h3>DV-specific evidence base</h3>
  <ul>
    <li><a href="https://www.sciencedirect.com/science/article/abs/pii/S0167268123004018">Koppa, V. (2024). "Can information save lives? Effect of a victim-focused police intervention on intimate partner homicides." <em>Journal of Economic Behavior &amp; Organization</em> 217, 756 to 782.</a></li>
    <li><a href="https://nij.ojp.gov/topics/articles/how-effective-are-lethality-assessment-programs-addressing-intimate-partner">National Institute of Justice: <em>How Effective Are Lethality Assessment Programs for Addressing Intimate Partner Violence?</em></a></li>
    <li><a href="https://crimesolutions.ojp.gov/ratedprograms/345">CrimeSolutions: Lethality Assessment Program Oklahoma (Promising tier)</a></li>
    <li><a href="https://www.campbellcollaboration.org/better-evidence/focused-deterrence-strategies-effects-on-crime.html">Braga and Weisburd 2019: Campbell review on focused-deterrence transportability</a></li>
    <li><a href="https://onlinelibrary.wiley.com/doi/10.3102/0162373713493517">Tipton 2014: generalizability index framework</a></li>
    <li><a href="https://pubmed.ncbi.nlm.nih.gov/29332533/">Sechrist and Weil: High Point Offender-Focused Domestic Violence Initiative evaluation (PubMed)</a></li>
    <li><a href="https://nnscommunities.org/strategies/intimate-partner-violence-intervention/">National Network for Safe Communities: Intimate Partner Violence Intervention</a></li>
    <li><a href="https://pubmed.ncbi.nlm.nih.gov/31359840/">Cheng et al. 2021: meta-analysis of batterer-intervention programs (PubMed)</a></li>
    <li><a href="https://www.jstor.org/stable/2095575">Sherman, L.W. and Berk, R.A. (1984). "The Specific Deterrent Effects of Arrest for Domestic Assault." <em>American Sociological Review</em> 49(2): 261 to 272.</a></li>
    <li><a href="https://cvg.org/what-we-do/">Cure Violence Global: international site list (no DV deployment)</a></li>
    <li><a href="https://www.brennancenter.org/our-work/research-reports/2025-trends-crime-and-safety-new-york-city">Brennan Center: <em>2025 Trends in Crime and Safety in New York City</em></a></li>
    <li><a href="https://www.criminaljustice.ny.gov/crimnet/ojsa/domestic-violence-data.html">DCJS: <em>Domestic Violence Data</em></a></li>
    <li><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6161830/">Peterson, Liu, Kresnow, Florence et al. 2018: Lifetime Economic Burden of IPV in the US (PMC)</a></li>
  </ul>

  <h3>NYC programs and evaluations</h3>
  <ul>
    <li><a href="https://comptroller.nyc.gov/reports/the-cure-for-crisis/">NYC Comptroller: <em>The Cure for Crisis</em> (CMS evaluation, 21% shooting reduction)</a></li>
    <li><a href="https://comptroller.nyc.gov/reports/audit-of-the-behavioral-health-emergency-assistance-response-divisions-effectiveness-in-responding-to-individuals-with-mental-health-crises-and-meeting-its-goals/">NYC Comptroller: B-HEARD audit (35% of eligible calls unserved; 31 of 78 precincts)</a></li>
    <li><a href="https://comptroller.nyc.gov/wp-content/uploads/2025/05/MG24-060A.pdf">NYC Comptroller: B-HEARD audit PDF (MG24-060A)</a></li>
    <li><a href="https://www.nyc.gov/mayors-office/news/2025/11/mayor-adams-announces-new-model-to-have-new-york-city-s-911-ment">Mayor's Office: November 2025 release on B-HEARD H+H operational transition</a></li>
    <li><a href="https://www.thecity.nyc/2022/7/18/23267193/mental-health-911-b-heard-teams">THE CITY: B-HEARD operational reporting (team availability gap)</a></li>
    <li><a href="https://www.nyc.gov/site/ocdv/press-resources/annual-reports-and-fact-sheets.page">NYC ENDGBV: Annual Reports and Fact Sheets</a></li>
    <li><a href="https://johnjayrec.nyc/2017/10/02/cvinsobronxeastny/">John Jay REC: Cure Violence evaluation in S. Bronx and East NY</a></li>
    <li><a href="https://vitalcitynyc.org/articles/crime-in-new-york-city-trends-statistics">Vital City: <em>The State of Crime in NYC: 2025 and Beyond</em></a></li>
    <li><a href="https://gothamist.com/news/domestic-and-elder-abuse-fuel-rise-in-nyc-felony-assaults-data-shows">Gothamist: <em>Domestic and elder abuse fuel rise in NYC felony assaults</em></a></li>
    <li><a href="https://manhattan.institute/article/systems-under-strain-deinstitutionalization-in-new-york-state-and-city-2025-update">Manhattan Institute: <em>Systems Under Strain: Deinstitutionalization in NY</em></a></li>
    <li><a href="https://www.osc.ny.gov/files/reports/pdf/mental-health-inpatient-service-capacity.pdf">NY State Comptroller (Mar 2024): <em>Mental Health: Inpatient Service Capacity</em> (PDF)</a></li>
    <li><a href="https://www.osc.ny.gov/press/releases/2024/03/dinapoli-percentage-new-yorkers-mental-illness-rose-available-psychiatric-beds-declined">NY State Comptroller (Mar 2024): DiNapoli press release on declining psychiatric beds</a></li>
    <li><a href="https://www.nyc.gov/mayors-office/news/2025/01/mayor-adams-takes-unprecedented-action-curb-street-homelessness-support-people-severe">NYC Mayor's Office: <em>Bridge to Home</em> / $650M mental-health plan</a></li>
    <li><a href="https://www.nyc.gov/mayors-office/news/2025/01/transcript-mayor-adams-nypd-commissioner-tisch-crime-down-2024">Mayor Adams and Commissioner Tisch announce 2024 crime statistics (January 2025)</a></li>
    <li><a href="https://www.nyc.gov/assets/nypd/downloads/pdf/analysis_and_planning/year-end-2024-enforcement-report.pdf">NYPD year-end 2024 enforcement report</a></li>
    <li><a href="https://compstat.nypdonline.org/">NYPD CompStat 2.0</a></li>
  </ul>

  <h3>NYC DV spending sources</h3>
  <ul>
    <li><a href="https://council.nyc.gov/budget/wp-content/uploads/sites/54/2024/05/HRA-.pdf">NYC Council FY25 Executive Plan HRA report (FY22 to FY25 data)</a></li>
    <li><a href="https://council.nyc.gov/budget/wp-content/uploads/sites/54/2023/05/HRA.pdf">NYC Council FY24 Executive Plan HRA report (FY21 to FY24 data)</a></li>
    <li><a href="http://council.nyc.gov/budget/wp-content/uploads/sites/54/2017/03/069-HRA.pdf">NYC Council FY18 Preliminary HRA report (FY15 to FY18 data)</a></li>
    <li><a href="https://council.nyc.gov/press/2025/05/16/2872/">NYC Council press release on FY26 Executive Budget DV funding gaps (May 16, 2025)</a></li>
    <li><a href="https://www.nyc.gov/office-of-the-mayor/news/069-24/mayor-adams-43-million-plan-lead-gender-equity-lays-ambitious-goal-make-nyc-most">Mayor Adams $43M Gender Equity Plan (Jan 2024)</a></li>
    <li><a href="https://data.cityofnewyork.us/Public-Safety/Mayor-s-Office-to-End-Domestic-and-Gender-Based-Vi/augs-s4dd">ENDGBV Annual Fact Sheet on NYC OpenData</a></li>
  </ul>

  <h3>National crime data</h3>
  <ul>
    <li><a href="https://www.fbi.gov/news/press-releases/fbi-releases-2024-reported-crimes-in-the-nation-statistics">FBI 2024 Reported Crimes in the Nation</a></li>
    <li><a href="https://cde.ucr.cjis.gov/">FBI Crime Data Explorer</a></li>
    <li><a href="https://ucr.fbi.gov/crime-in-the-u.s/2010/crime-in-the-u.s.-2010/violent-crime/aggravatedassaultmain">FBI UCR 2010: Aggravated Assault</a></li>
    <li><a href="https://counciloncj.org/crime-trends-in-u-s-cities-year-end-2024-update/">Council on Criminal Justice: Crime Trends in U.S. Cities, Year-End 2024</a></li>
    <li><a href="https://mayor.lacity.gov/news/lapd-releases-2024-end-year-crime-statistics-city-los-angeles">LAPD 2024 EOY Crime Stats (Mayor Bass)</a></li>
    <li><a href="https://crimelab.uchicago.edu/resources/2024-end-of-year-analysis-chicago-crime-trends/">UChicago Crime Lab 2024 Chicago analysis</a></li>
    <li><a href="https://bjs.ojp.gov/library/publications/criminal-victimization-2024">BJS Criminal Victimization 2024</a></li>
    <li><a href="https://cde.ucr.cjis.gov/LATEST/resources/reports/Domestic%20Relationships%20and%20Violent%20Crimes%202020-2024.pdf">FBI Domestic Relationships and Violent Crimes 2020 to 2024</a></li>
  </ul>

  <h3>Underlying data</h3>
  <ul>
    <li><a href="https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Historic/qgea-i56i">NYPD Complaint Data Historic: qgea-i56i (NYC OpenData)</a></li>
    <li><a href="https://data.cityofnewyork.us/Public-Safety/Police-Precincts/78dh-3ptz">NYC Police Precincts (NYC OpenData)</a></li>
  </ul>

  <h3>Broader violence-reduction evidence base</h3>
  <ul>
    <li><a href="https://onlinelibrary.wiley.com/doi/full/10.4073/csr.2012.8">Braga et al.: Campbell Collaboration meta-analysis on hot-spots policing</a></li>
    <li><a href="https://academic.oup.com/policing/article/doi/10.1093/police/paae056/7739691">Oxford 2024: domestic-abuse hot spots place-based study</a></li>
    <li><a href="https://crimelab.uchicago.edu/projects/becoming-a-man-bam/">Heller et al.: Becoming a Man RCT (45% violent-crime arrest reduction)</a></li>
    <li><a href="https://www.brennancenter.org/our-work/research-reports/facts-bail-reform-and-crime-rates-new-york-state">Brennan Center: Bail reform's negligible causal effect</a></li>
    <li><a href="https://help.neighborhoodscout.com/support/solutions/articles/25000001997-what-is-the-crime-index-">NeighborhoodScout: <em>What is the Crime Index?</em></a></li>
  </ul>
</section>
```

- [ ] **Step 9.2: Verify**

Open the page. The Sources section shows six grouped lists with all source links rendered. Click a few; they open the right URLs.

- [ ] **Step 9.3: Commit**

```bash
git add site/index.html
git commit -m "Add Sources section"
```

---

## Task 10: Methodology section

**Files:**
- Modify: `site/index.html` (replace the `#methodology` section content)

The methodology section is the AI-tool provenance disclosure. Target: ~600-800 words. Honest tradecraft notes for a curious reader.

- [ ] **Step 10.1: Replace the methodology section in index.html**

Replace `<section id="methodology">` with:

```html
<section id="methodology">
  <h2>Methodology</h2>

  <p>This memo started as Phase 0 evidence discovery and ended up as a published artifact. What follows is an honest walk through how it was built, aimed at a reader who's curious whether they should trust the analysis.</p>

  <h3>Data sources</h3>
  <p>The primary data is NYPD's Complaint Data Historic dataset (qgea-i56i, on NYC OpenData), which covers every NYPD-recorded complaint from 2006 through the most recent year. Domestic-violence-specific figures come from the New York State Division of Criminal Justice Services DV feed, accessed via Vital City's published analysis (NYPD's public dataset does not contain a victim-relationship field, so we rely on the DCJS feed where Vital City does the underlying joins). B-HEARD operational data comes from NYC Comptroller Lander's 2024 audit. Mental-health system context comes from the Manhattan Institute's <em>Systems Under Strain</em> deinstitutionalization paper and the NY State Comptroller's March 2024 inpatient-capacity report (which uses Office of Mental Health data). NYC DV-spending data comes from NYC City Council Finance Committee HRA reports. National benchmarks come from FBI Uniform Crime Reporting and the Council on Criminal Justice's 24-city year-end 2024 update. Source studies for the recommended programs come from peer-reviewed criminology literature: Koppa 2024 (<em>Journal of Economic Behavior &amp; Organization</em>), Sechrist and Weil 2018 (NIJ), Sherman and Berk 1984 (<em>American Sociological Review</em>), Braga and Weisburd 2019 (Campbell systematic review), and Cheng et al. 2021 (meta-analysis).</p>

  <h3>The analytical pipeline</h3>
  <p>Python 3.11 with pandas, geopandas, and DuckDB. Raw data is hive-partitioned parquet under <code>data/raw/</code>; small aggregate parquets and CSVs (per-precinct counts, sub-category drill, indexed time series) are committed to the repo for reproducibility. Charts are rendered by <code>scripts/render_sketches.py</code> (matplotlib for static, Observable Plot at runtime for the two interactive charts).</p>

  <h3>Three rounds of adversarial review</h3>
  <p>The Phase 0 memo went through three rounds of adversarial critique before publication. Each round, a fresh reviewer attacked the memo with no continuity from prior rounds. Round 1: skeptical hiring manager (would they put this down on a first read?). Round 2: methodological peer reviewer (where is the methodology weak, where are the citations sloppy?). Round 3: hostile policy critic (what's the most damaging fair attack?). Critiques the memo could rebut became sharpenings; critiques that survived rebuttal became research questions for a separate, neutrally framed research agent. The recommendation visibly changed across the three rounds: from "deploy a domestic-violence Crisis Management System port" through "deploy LAP and OFDVI" to the current "lead with housing and B-HEARD; pilot LAP and OFDVI third with safeguards and a sunset." Each reframe traded confidence for defensibility.</p>

  <h3>Independent research and verification on load-bearing claims</h3>
  <p>Four high-stakes claims got research-then-verify agent pairs (a research agent finds the evidence; an independent verification agent re-reads the cited sources and reports confirm / dispute / inconclusive). The B-HEARD precinct count was corrected from "28" to the verified 31, sourced to the Comptroller audit's Appendix II. The "NYC vs national outlier" framing was independently confirmed against FBI UCR, the Council on Criminal Justice 24-city sample, and per-city year-end data from Los Angeles, Chicago, and Philadelphia. The DV-spending trajectory was reconstructed from NYC Council Finance Committee HRA reports across FY15 through FY26 with explicit Consumer Price Index adjustment. The long-run cost-offset estimate was disputed in verification (several unit costs were sensitive to marginal-versus-average accounting, and federal payer share isn't NYC-borne), so the memo flags those numbers as illustrative rather than estimable.</p>

  <h3>Source audit</h3>
  <p>Every cited URL was classified by reputability category (government, peer-reviewed academic, university research center, reputable news, reputable nonprofit, partisan think tank, Wikipedia, other). Load-bearing claims were independently fact-checked against their cited sources. Where a source was partisan-tilted (Manhattan Institute on deinstitutionalization), a primary government cite was paired alongside it (NY State Comptroller using OMH data). Where a citation was structurally one source reported three times (the DV split appearing in Vital City, Brennan Center, and Gothamist, all citing DCJS), the memo says so.</p>

  <h3>AI-tool transparency</h3>
  <p>This memo and the analysis behind it were built with the assistance of <a href="https://claude.com/claude-code">Claude Code</a>, an Anthropic-built agentic coding tool. Claude Code drafted prose, ran statistical analyses through the project's Python stack, dispatched independent research and verification agents, and surfaced findings the author would not have caught alone. The author directs intent, makes every decision, edits every paragraph, and is solely responsible for the recommendation. The use of AI tools is named here, not hidden, because the methodology is part of the work.</p>

  <h3>Limits of the analysis</h3>
  <p>See the appendix's <a href="#appendix">Limits of the data</a> note. Briefly: NYPD does not publish a victim-relationship field, so the DV split is not directly reproducible from the NYPD dataset alone; the HRA "Domestic Violence Services" budget line conflates ENDGBV operations with DV shelter contracts; the long-run cost-offset estimate is illustrative, not estimable; and FBI Uniform Crime Reporting and NIBRS are not the same as NY State Penal Law definitions, so cross-jurisdiction comparisons require a methodological asterisk.</p>

  <h3>Reproducibility</h3>
  <p>The full source repository is on GitHub (link in footer). All aggregate parquet files and CSVs that drive the charts are committed. Raw NYPD data is regenerable from NYC OpenData with a free SODA application token. The memo, the chart-rendering scripts, the build script for this site, and the round-by-round adversarial critique transcripts are all in the repo.</p>
</section>
```

- [ ] **Step 10.2: Verify**

Open the page. Methodology section renders with seven sub-headings and ~700 words of prose. The link to claude.com/claude-code resolves.

- [ ] **Step 10.3: Commit**

```bash
git add site/index.html
git commit -m "Add Methodology section"
```

---

## Task 11: Appendix section

**Files:**
- Modify: `site/index.html` (replace the `#appendix` section content)

Five sub-sections: What NYC has tried (table), Strength of supporting evidence (table), Findings worth flagging, Limits of the data, Why hot-spots policing isn't in the recommendation.

- [ ] **Step 11.1: Replace the appendix section in index.html**

Replace `<section id="appendix">` with the following block. (This is large; keep it in one edit.)

```html
<section id="appendix">
  <h2>Appendix</h2>

  <h3>What New York City has already tried</h3>
  <table>
    <thead>
      <tr><th>Program</th><th>Scope</th><th>Evidence</th><th>Verdict</th></tr>
    </thead>
    <tbody>
      <tr><td>Crisis Management System / Cure Violence</td><td>$86M, 29 precincts (shootings)</td><td>21% reduction in shootings (Comptroller Lander 2024); 37 to 50% gun-injury reductions in S. Bronx and East NY (John Jay 2017).</td><td>Proven model for <em>gun violence</em>. CVI-for-DV has no published evaluation; do not port.</td></tr>
      <tr><td>B-HEARD</td><td>31 of 78 precincts; FY24: 14,900 calls</td><td>35% of in-hours eligible calls unserved with <strong>untracked causes</strong> (Comptroller 2024 audit). Roughly 14,200 separate overnight eligible calls outside operating hours. 2025 <em>Psychiatric Services</em> study shows ED diversion.</td><td><strong>Expand 24-hour operations and implement audit-recommended cause-tracking.</strong></td></tr>
      <tr><td>Subway Safety Surge / NYPD CRT</td><td>Plus 1,000 officers per day; CRT 18 officers</td><td>No published causal evaluation. NYPD Inspector General (2024) flagged operational issues.</td><td>Tactical, not evaluated.</td></tr>
      <tr><td>NYC Ceasefire (Group Violence Intervention)</td><td>Brooklyn, Bronx, Staten Island, NNSC partnership</td><td>Boston Ceasefire achieved 63 to 68% reduction in youth gun violence; NYC-specific evaluation thin.</td><td>Strong elsewhere. NYC scope is too small to evaluate, but <strong>NNSC's NYC infrastructure is the natural launchpad for an OFDVI.</strong></td></tr>
      <tr><td>Bridge to Home / supportive housing</td><td>100 beds plus 900 Safe Haven; $650M plan announced January 2025</td><td>Too new for outcome data.</td><td><strong>Scale up, fast.</strong></td></tr>
      <tr><td>ENDGBV / family justice centers / DV hotlines</td><td>Citywide service network; spending flat in real terms FY17 to FY24</td><td>Fragmented; no precinct-targeted outcome evaluation; no LAP or focused-deterrence program.</td><td><strong>The DV gap. The recommended LAP plus OFDVI fills it.</strong></td></tr>
      <tr><td>Lethality Assessment Program (LAP)</td><td>Not deployed at NYC scale</td><td>Koppa 2024 staggered-DiD on the Maryland LAP rollout: <strong>35 to 45% reduction in female intimate-partner-homicide rate, jurisdiction-level.</strong> CrimeSolutions rates LAP-Oklahoma "Promising." Quasi-experimental, not randomized.</td><td><strong>Pilot in four to six high-incidence precincts with DiD evaluation built in.</strong></td></tr>
      <tr><td>High Point OFDVI / focused-deterrence for IPV</td><td>Not deployed in NYC</td><td>Sechrist and Weil 2018: single-jurisdiction before-after, about 20% IPDV-call/arrest reduction, no contemporaneous comparator.</td><td><strong>Pilot via NNSC partnership with rigorous matched-comparison evaluation. Do not assume citywide deployment grade.</strong></td></tr>
    </tbody>
  </table>

  <h3>Strength of supporting evidence</h3>
  <table>
    <thead>
      <tr><th>Claim</th><th>Supported by</th><th>Strength</th></tr>
    </thead>
    <tbody>
      <tr><td>Felony assault has a real behavioral rise of about 40 to 47% from 2010 to 2024, after adjusting for reclassification.</td><td>Direct count from NYPD Complaint Data Historic; sub-category drill-down; research on additional reclassification streams.</td><td>Strong</td></tr>
      <tr><td>Felony assault is the only violent-felony category showing a sustained rise (2017 to 2024).</td><td>Indexing of violent felonies to 2017 equal to 1.0 across 2017 to 2024.</td><td>Strong</td></tr>
      <tr><td>76 of 78 precincts saw felony-assault growth 2017 to 2024; top-1 precinct equals about 6% of citywide growth, top-10 about 36%.</td><td>Per-precinct decomposition.</td><td>Strong</td></tr>
      <tr><td>The Mayor's "felony assault minus 1.9%" figure was the October 2024 monthly stat, not the year-end number.</td><td>Reconciled directly against NYPD's October 2024 press release.</td><td>Strong</td></tr>
      <tr><td>Roughly 35% of the +72% headline is statutory creation (Strangulation 1st, NYPL section 121.13).</td><td>Sub-category drill-down across 2010 to 2024.</td><td>Strong</td></tr>
      <tr><td>Domestic violence is the dominant felony-assault driver (about 73% DV growth versus about 40% other; about 39% of all NYC felony assault is household-related).</td><td>Vital City, Gothamist, and the Brennan Center each cite the same DCJS feed; corroboration is structurally one source reported three times.</td><td>Strong (single-source claim, three independent secondary citations)</td></tr>
      <tr><td>The "35 to 45% LAP" figure comes from Koppa (<em>JEBO</em> 2024) staggered-DiD on Maryland (jurisdiction-level female-IPH rate), not from Messing's Oklahoma study.</td><td>Citation accuracy correction.</td><td>Strong (corrects a prior misattribution)</td></tr>
      <tr><td>LAP, OFDVI, and CMS effect sizes come from quasi-experimental observational studies, not from RCTs.</td><td>Koppa 2024 staggered-DiD; Sechrist and Weil 2018 single-jurisdiction before-after; Comptroller 2024 Callaway-Sant'Anna DiD with visual-only parallel-trends.</td><td>Strong</td></tr>
      <tr><td>Focused-deterrence transportability: matched-design effects are about 28% of non-matched-design effects.</td><td>Braga-Weisburd 2019 Campbell review.</td><td>Strong</td></tr>
      <tr><td>The cited effect sizes use heterogeneous denominators, so citywide projection is arithmetically undefined without scope adjustment.</td><td>Per-effect denominator analysis.</td><td>Strong</td></tr>
      <tr><td>CVI / credible-messenger work has no published evaluation against DV.</td><td>Cure Violence Global's 50 plus sites all target community / gun violence.</td><td>Strong</td></tr>
      <tr><td><strong>NYC felony-assault rise is an outlier, not part of a national trend.</strong> National rate roughly flat 2010 to 2024; CCJ 24-city average plus 4% since 2019; LA, Chicago, Philadelphia all moving in the opposite direction.</td><td>FBI UCR; CCJ Year-End 2024; LAPD 2024 EOY; UChicago Crime Lab 2024.</td><td>Strong (verified independently)</td></tr>
      <tr><td><strong>B-HEARD operates in 31 of NYC's 78 precincts, not 28.</strong></td><td>Comptroller 2024 audit Appendix II; reaffirmed by Mayor's Office Nov 2025 release; corroborated by NYC IBO Jan 2026 brief.</td><td>Strong (verified)</td></tr>
      <tr><td><strong>NYC DV-services real spending is flat FY17 to FY24 while DV felony assault rose about 73%.</strong> Per-incident real spending fell about 42%.</td><td>NYC Council Finance Committee HRA reports; CPI-U inflation adjustment.</td><td>Strong (medium confidence on aggregation, given the HRA "DV Services" line conflates ENDGBV and DV shelters)</td></tr>
      <tr><td>LAP and OFDVI piloted in NYC will produce about a 10 to 15% effect (post-attenuation).</td><td>Inference from source-study effects plus the Braga-Weisburd 2019 attenuation factor.</td><td>External-evidence projection; substantial uncertainty</td></tr>
      <tr><td>Cost figures: $3 to $8M LAP pilot, $2 to $5M OFDVI pilot, $30 to $50M B-HEARD scaling, $650M housing already authorized.</td><td>Order-of-magnitude pilot estimates.</td><td>Rough estimates; plus or minus 50% uncertainty</td></tr>
      <tr><td>NYC FY26 has a $4.22B projected budget gap.</td><td>Comptroller projection.</td><td>Strong</td></tr>
      <tr><td>NYC's pilot-termination track record: located cases (B-HEARD, CMS, Patternizr, SCOUT) all continued or expanded despite mixed or null evaluations.</td><td>Open-records research.</td><td>Strong (informs sunset-clause design)</td></tr>
      <tr><td>Plausible long-run NYC-borne cost offsets from LAP plus OFDVI pilots are in the $5 to $35M range.</td><td>Mechanism-by-mechanism build (avoided ED, incarceration, shelter, ACS).</td><td>Directional only. Verification disputed several unit-cost figures. Treat as illustrative, not estimable.</td></tr>
    </tbody>
  </table>

  <h3>Findings worth flagging</h3>
  <p>Findings discovered in research that materially changed the memo's recommendation or methodology.</p>
  <ol>
    <li><strong>Community Violence Intervention has no published DV evaluation.</strong> Cure Violence Global's 50-plus international sites all target community or gun violence. An earlier draft of this memo proposed porting NYC's CMS architecture to DV; the research base does not support it. This finding caused the central recommendation to switch from "deploy DV-CMS" to "pilot LAP and OFDVI."</li>
    <li><strong>NYC DV investment is flat in real terms while DV cases rose about 73%.</strong> Per-incident real spending fell about 42% from FY17 to FY24, and Council-requested DV expansions were zeroed in three consecutive Mayoral Executive Budgets. This is the second pillar of the Complication.</li>
    <li><strong>NYC's pilot-termination track record is poor.</strong> Located cases (B-HEARD, CMS, Patternizr, SCOUT) all continued or expanded despite mixed, null, or absent evaluations. Load-bearing for the sunset clause: the kill-switch must be encoded in procurement-contract language with automatic de-funding triggers, or it will be politically unenforceable.</li>
    <li><strong>The Maryland LAP figure is widely misattributed.</strong> The 35 to 45% female-IPH rate reduction comes from Koppa, <em>Journal of Economic Behavior &amp; Organization</em> (2024), a peer-reviewed staggered-rollout DiD on Maryland's adoption, not from Messing's Oklahoma study (which has no homicide endpoint). The misattribution is common in policy summaries; the memo cites Koppa directly.</li>
    <li><strong>Strangulation 1st reclassification accounts for about 35% of the +72% headline.</strong> The November 2010 New York Penal Law section 121.13 created a brand-new felony class that contributed about 4,400 of the 12,364 added cases between 2010 and 2024. The reclassification adjustment is what produces the +47% behavioral figure.</li>
    <li><strong>NYC versus national outlier.</strong> NYC's reclass-adjusted +47% felony-assault rise sits well above any peer benchmark. National aggravated assault is roughly flat, the 24-city average is plus 4% since 2019, and LA, Chicago, Philadelphia all moved in the opposite direction in 2024. This strengthens the structural-driver framing: the rise is NYC-specific, not part of a national trend.</li>
    <li><strong>B-HEARD count corrected to 31 of 78 precincts.</strong> The "28" figure that appears in some press summaries is not supported by any primary source. Comptroller audit Appendix II lists all 31 explicitly. The memo references the verified figure throughout.</li>
  </ol>

  <h3>Limits of the data</h3>
  <ul>
    <li><strong>Sub-category attribution within the catch-all <code>pd_cd 109</code> (Assault 2/1/Unclassified).</strong> We cannot distinguish intimate-partner from street from transit assault at the level NYPD publishes. The 73% / 40% DV-versus-non-DV split comes from Vital City's deeper analysis of NYPD data; we cite it but did not re-derive it.</li>
    <li><strong>DV split corroboration is structurally one source.</strong> The Brennan Center's 2025 Trends report and Gothamist's reporting both cite the same DCJS feed Vital City uses. Three publications carry the figure; one underlying source produces it. If the DCJS feed has a methodology issue, three citations would all share it.</li>
    <li><strong>DV-spending aggregation.</strong> The HRA "Domestic Violence Services" program area conflates ENDGBV operations with DV shelter operations. ENDGBV's standalone budget is not published as a clean line; the FY26 Adopted Schedule C requires ENDGBV to begin reporting its budget by program area precisely because the line is opaque. The "real spending is flat" finding therefore rests on a medium-confidence aggregation rather than a precise per-agency figure.</li>
    <li><strong>Long-run cost-offset estimate is illustrative, not estimable.</strong> Verification flagged several unit-cost issues (incarceration $480K versus Comptroller $556K; ED $1,800 versus AHRQ $530 average; LAP 7% ED-reduction not from Messing). Use the directional read, not the dollar figures.</li>
    <li><strong>National comparison.</strong> "Felony assault" (NY Penal Law) is not identical to FBI UCR "aggravated assault." The FBI's UCR-to-NIBRS transition (2021) introduces measurement breaks; many large cities did not report to NIBRS in 2022.</li>
  </ul>

  <h3>Why hot-spots policing is not in the recommendation</h3>
  <p>A note on the exclusion. Hot-spots policing concentrates police presence on specific street blocks, intersections, or small geographic areas where crime is observed to cluster. The strategy works for offenses driven by physical place (open-air drug markets, street robberies, gun-violence corners). The "place as driver" assumption does not fit DV. A 2024 Oxford study on domestic-abuse hot spots found that DV concentrates around households, not blocks; the spatial signature does not match what hot-spots strategies were designed to address. NYC's data confirms the same pattern at the precinct level. Of NYC's 78 precincts, 76 saw growth in felony-assault counts between 2017 and 2024. The largest single precinct accounts for only about 6% of the citywide increase, and the top 10 precincts together account for only about 36%. There is no concentrated set of places to target. A categorical lever is the appropriate fit; a geographic concentration strategy is not.</p>
</section>
```

- [ ] **Step 11.2: Verify**

Open the page. The Appendix section renders with two tables (What NYC has tried; Strength of supporting evidence), an ordered list (Findings worth flagging), an unordered list (Limits of the data), and a closing paragraph (hot-spots policing rationale). Tables look readable.

- [ ] **Step 11.3: Commit**

```bash
git add site/index.html
git commit -m "Add Appendix section"
```

---

## Task 12: Footer

**Files:**
- Modify: `site/index.html` (replace the `<footer class="site-footer">` content)

- [ ] **Step 12.1: Replace the footer in index.html**

Replace the existing `<footer class="site-footer">` block with:

```html
<footer class="site-footer">
  <div class="footer-grid">
    <div class="footer-bio">
      <strong>Zarren Kuzma</strong> is a product manager focused on civic-tech, strategy, and public-safety analytics. This is a public artifact for the New York City strategy and chief-of-staff conversation. He's available at
      <a href="mailto:zkuzma8@gmail.com">zkuzma8@gmail.com</a>
      and on
      <a href="https://www.linkedin.com/in/zarrenkuzma/">LinkedIn</a>.
    </div>
    <div class="footer-meta">
      <div>Built with <a href="https://claude.com/claude-code">Claude Code</a>. Methodology: <a href="#methodology">how this was made</a>.</div>
      <div>Source repository: <a href="https://github.com/zkuzma8/nyc-strategy-artifact">github.com/zkuzma8/nyc-strategy-artifact</a></div>
      <div class="footer-copyright">&copy; 2026 Zarren Kuzma. Memo released under CC BY 4.0.</div>
    </div>
  </div>
</footer>
```

- [ ] **Step 12.2: Add footer styles**

Append to `site/styles.css`:

```css
.site-footer { text-align: left; }
.site-footer .footer-grid {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
  align-items: start;
}
.site-footer .footer-bio { font-size: 14px; line-height: 1.6; color: var(--ink); }
.site-footer .footer-bio strong { color: var(--ink); font-weight: 600; }
.site-footer .footer-meta { font-size: 12px; line-height: 1.7; color: var(--mute); }
.site-footer .footer-copyright { margin-top: var(--space-2); font-size: 11px; color: #aaa; }

@media (max-width: 720px) {
  .site-footer .footer-grid { grid-template-columns: 1fr; gap: var(--space-3); }
}
```

- [ ] **Step 12.3: Verify**

Open the page. The footer renders at the bottom with bio on the left and methodology / repo / copyright on the right. Email and LinkedIn links work.

- [ ] **Step 12.4: Commit**

```bash
git add site/index.html site/styles.css
git commit -m "Add footer"
```

---

## Task 13: Interactive chart 06 (precinct map)

**Files:**
- Create: `site/js/precinct-map.js`

The static PNG fallback (`assets/charts/06-precinct-growth.png`) is already in the page from Task 6. This script replaces it with an interactive Observable Plot choropleth on script load. If the CDN fails or the script errors, the PNG stays.

- [ ] **Step 13.1: Write the precinct-map script**

Create `site/js/precinct-map.js`:

```javascript
/**
 * Interactive precinct map (chart 06).
 *
 * - Loads Observable Plot from CDN.
 * - Reads data/precincts.geojson and data/precinct-stats.json.
 * - Renders an orange-ramp choropleth of percent change in felony assault, 2017 to 2024.
 * - On hover: tooltip with precinct number, 2024 count, and percent change.
 * - On click: pin / unpin the tooltip.
 * - If anything fails, the static PNG fallback already in the DOM stays.
 */
(function () {
  "use strict";

  const CONTAINER_ID = "chart-06-container";
  const PLOT_CDN = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/dist/plot.umd.min.js";

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  async function loadData() {
    const [geoResp, statsResp] = await Promise.all([
      fetch("data/precincts.geojson"),
      fetch("data/precinct-stats.json"),
    ]);
    if (!geoResp.ok || !statsResp.ok) {
      throw new Error("Failed to fetch precinct data");
    }
    const geojson = await geoResp.json();
    const stats = await statsResp.json();
    const statsByPrecinct = new Map(stats.map(function (r) { return [r.precinct, r]; }));
    geojson.features.forEach(function (f) {
      const pct = parseInt(f.properties.precinct, 10);
      const stat = statsByPrecinct.get(pct);
      if (stat) {
        f.properties.count_2017 = stat.count_2017;
        f.properties.count_2024 = stat.count_2024;
        f.properties.pct_change = stat.pct_change;
      }
    });
    return geojson;
  }

  function renderPlot(container, geojson) {
    const Plot = window.Plot;
    const plot = Plot.plot({
      width: container.clientWidth,
      height: 600,
      projection: {
        type: "mercator",
        domain: geojson,
      },
      color: {
        type: "linear",
        scheme: "Oranges",
        domain: [-50, 0, 100, 200],
        legend: true,
        label: "Percent change in felony assault, 2017 to 2024",
      },
      marks: [
        Plot.geo(geojson, {
          fill: function (d) { return d.properties.pct_change; },
          stroke: "#fff",
          strokeWidth: 0.5,
          title: function (d) {
            const p = d.properties;
            return "Precinct " + p.precinct +
                   "\n2017: " + (p.count_2017 || "?") +
                   "\n2024: " + (p.count_2024 || "?") +
                   "\nChange: " + (p.pct_change != null ? p.pct_change + "%" : "?");
          },
        }),
      ],
    });
    container.innerHTML = "";
    container.appendChild(plot);
    attachPinHandlers(container, geojson);
  }

  // Click-to-pin: clicking a precinct pins a sticky tooltip with its info;
  // clicking the same precinct again unpins; clicking another swaps.
  function attachPinHandlers(container, geojson) {
    const features = geojson.features;
    const paths = container.querySelectorAll("svg path");
    if (!paths.length) return;

    let pinnedIdx = null;

    // Tooltip element (created once per render).
    const tip = document.createElement("div");
    tip.className = "precinct-pin-tip";
    tip.style.display = "none";
    container.appendChild(tip);

    function showPinned(idx, x, y) {
      const f = features[idx];
      if (!f) return;
      const p = f.properties;
      tip.innerHTML =
        "<strong>Precinct " + p.precinct + "</strong>" +
        "<div>2017: " + (p.count_2017 != null ? p.count_2017.toLocaleString() : "—") + "</div>" +
        "<div>2024: " + (p.count_2024 != null ? p.count_2024.toLocaleString() : "—") + "</div>" +
        "<div class='pct'>" + (p.pct_change != null ? (p.pct_change > 0 ? "+" : "") + p.pct_change + "%" : "—") + "</div>" +
        "<button class='unpin-btn' aria-label='Unpin precinct'>&times;</button>";
      tip.style.left = x + "px";
      tip.style.top = y + "px";
      tip.style.display = "block";
      const btn = tip.querySelector(".unpin-btn");
      if (btn) btn.addEventListener("click", function (e) {
        e.stopPropagation();
        unpin();
      });
    }

    function unpin() {
      pinnedIdx = null;
      tip.style.display = "none";
      paths.forEach(function (p) { p.classList.remove("pinned"); });
    }

    paths.forEach(function (path, idx) {
      path.style.cursor = "pointer";
      path.addEventListener("click", function (e) {
        e.stopPropagation();
        if (pinnedIdx === idx) {
          unpin();
          return;
        }
        paths.forEach(function (p) { p.classList.remove("pinned"); });
        path.classList.add("pinned");
        pinnedIdx = idx;
        const rect = container.getBoundingClientRect();
        showPinned(idx, e.clientX - rect.left + 10, e.clientY - rect.top + 10);
      });
    });

    // Click outside the map → unpin.
    container.addEventListener("click", function (e) {
      if (e.target === container) unpin();
    });
  }

  async function init() {
    const figure = document.getElementById(CONTAINER_ID);
    if (!figure) return;
    const figcaption = figure.querySelector("figcaption");
    const captionText = figcaption ? figcaption.outerHTML : "";

    try {
      await loadScript(PLOT_CDN);
      const geojson = await loadData();
      const renderTarget = document.createElement("div");
      renderTarget.className = "chart-06-render";
      figure.innerHTML = "";
      figure.appendChild(renderTarget);
      if (captionText) figure.insertAdjacentHTML("beforeend", captionText);
      renderPlot(renderTarget, geojson);
      // Re-render on resize.
      let resizeTimer;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          renderPlot(renderTarget, geojson);
        }, 200);
      });
    } catch (err) {
      console.warn("Chart 06 interactive render failed; static PNG fallback in use.", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
```

- [ ] **Step 13.2: Add styles for pin tooltip and pinned precinct**

Append to `site/styles.css`:

```css
/* ---------- precinct-map pinned tooltip ---------- */
.chart-06-render { position: relative; }
.precinct-pin-tip {
  position: absolute;
  background: var(--ink);
  color: #fff;
  font-family: var(--font-ui);
  font-size: 12px;
  line-height: 1.4;
  padding: 10px 14px;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  z-index: 10;
  min-width: 140px;
  pointer-events: auto;
}
.precinct-pin-tip strong { color: #fff; font-size: 13px; }
.precinct-pin-tip .pct { color: var(--orange); font-weight: 700; margin-top: 4px; }
.precinct-pin-tip .unpin-btn {
  position: absolute;
  top: 4px;
  right: 6px;
  background: transparent;
  border: 0;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  padding: 2px 6px;
  line-height: 1;
}
.precinct-pin-tip .unpin-btn:hover { color: var(--orange); }
.chart-06-render svg path.pinned {
  stroke: var(--ink);
  stroke-width: 2;
}
```

- [ ] **Step 13.3: Verify in browser**

Run a local server and open the page. Scroll to the precinct map figure. Expected: the static PNG appears briefly, then is replaced by an Observable Plot choropleth that you can hover over to see precinct numbers, 2017 and 2024 counts, and percent change.

Then click any precinct: a sticky tooltip appears with the precinct's stats and a close button. Click the same precinct again or hit the close button to unpin. Click another precinct to swap pins.

If Observable Plot fails to load (test by disabling JS), the page shows the static PNG instead.

- [ ] **Step 13.4: Commit**

```bash
git add site/js/precinct-map.js site/styles.css
git commit -m "Add interactive precinct map with hover and click-to-pin (chart 06)"
```

---

## Task 14: Interactive chart 14 (multi-baseline view)

**Files:**
- Create: `site/js/multi-baseline.js`

Same pattern as Task 13. Static PNG fallback already in the DOM. Script replaces it with a four-tab toggle UI showing the four panels (1-year, 5-year, decade, national context).

- [ ] **Step 14.1: Write the multi-baseline script**

Create `site/js/multi-baseline.js`:

```javascript
/**
 * Interactive multi-baseline view (chart 14).
 *
 * - Loads Observable Plot from CDN.
 * - Reads data/baseline-data.json.
 * - Renders a four-tab UI (1-year, 5-year, decade, national).
 * - Each tab swaps the rendered bar chart.
 * - If anything fails, the static PNG fallback already in the DOM stays.
 */
(function () {
  "use strict";

  const CONTAINER_ID = "chart-14-container";
  const PLOT_CDN = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/dist/plot.umd.min.js";

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.Plot) { resolve(); return; }
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function panelData(key, all) {
    if (key === "one_year") return [{ label: "NYC", value: all.one_year.value, fill: "#FF6319" }];
    if (key === "five_year") return [{ label: "NYC", value: all.five_year.value, fill: "#FF6319" }];
    if (key === "decade") return [
      { label: "Headline", value: all.decade.headline, fill: "#888" },
      { label: "Adjusted", value: all.decade.adjusted, fill: "#FF6319" },
    ];
    if (key === "national") return [
      { label: "NYC (adjusted)", value: all.national.nyc_adjusted, fill: "#D8127B" },
      { label: "US national", value: all.national.us_national, fill: "#888" },
      { label: "24-city avg", value: all.national.ccj_24_city, fill: "#888" },
      { label: "LA (2024 YoY)", value: all.national.la_yoy, fill: "#888" },
    ];
    return [];
  }

  function panelTitle(key, all) {
    return all[key].label;
  }

  function panelNote(key, all) { return all[key].note; }

  function renderPanel(container, data) {
    const Plot = window.Plot;
    const plot = Plot.plot({
      width: container.clientWidth,
      height: 280,
      x: { label: null },
      y: { label: "Percent change", grid: true, domain: data.length > 1 ? null : [0, Math.max(10, data[0].value * 1.2)] },
      marks: [
        Plot.barY(data, {
          x: "label",
          y: "value",
          fill: "fill",
          title: function (d) { return d.label + ": " + d.value + "%"; },
        }),
        Plot.ruleY([0]),
        Plot.text(data, {
          x: "label",
          y: "value",
          text: function (d) { return (d.value > 0 ? "+" : "") + d.value + "%"; },
          dy: function (d) { return d.value >= 0 ? -8 : 16; },
          fill: "#1a1a1a",
          fontWeight: 700,
        }),
      ],
    });
    container.innerHTML = "";
    container.appendChild(plot);
  }

  async function init() {
    const figure = document.getElementById(CONTAINER_ID);
    if (!figure) return;
    const figcaption = figure.querySelector("figcaption");
    const captionText = figcaption ? figcaption.outerHTML : "";

    try {
      await loadScript(PLOT_CDN);
      const resp = await fetch("data/baseline-data.json");
      if (!resp.ok) throw new Error("Failed to fetch baseline data");
      const data = await resp.json();

      figure.innerHTML = "";
      // Tab strip
      const tabs = document.createElement("div");
      tabs.className = "baseline-tabs";
      const panels = [
        { key: "one_year", label: "1-year" },
        { key: "five_year", label: "5-year" },
        { key: "decade", label: "Decade" },
        { key: "national", label: "National context" },
      ];
      const buttons = panels.map(function (p) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "baseline-tab";
        b.textContent = p.label;
        b.dataset.key = p.key;
        return b;
      });
      buttons.forEach(function (b) { tabs.appendChild(b); });
      figure.appendChild(tabs);

      const titleEl = document.createElement("div");
      titleEl.className = "baseline-title";
      figure.appendChild(titleEl);

      const renderTarget = document.createElement("div");
      renderTarget.className = "baseline-plot";
      figure.appendChild(renderTarget);

      const noteEl = document.createElement("div");
      noteEl.className = "baseline-note";
      figure.appendChild(noteEl);

      if (captionText) figure.insertAdjacentHTML("beforeend", captionText);

      function activate(key) {
        buttons.forEach(function (b) {
          b.classList.toggle("active", b.dataset.key === key);
        });
        titleEl.textContent = panelTitle(key, data);
        renderPanel(renderTarget, panelData(key, data));
        noteEl.textContent = panelNote(key, data);
      }

      buttons.forEach(function (b) {
        b.addEventListener("click", function () { activate(b.dataset.key); });
      });
      activate("decade"); // default

      let resizeTimer;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          const active = buttons.find(function (b) { return b.classList.contains("active"); });
          if (active) activate(active.dataset.key);
        }, 200);
      });
    } catch (err) {
      console.warn("Chart 14 interactive render failed; static PNG fallback in use.", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
```

- [ ] **Step 14.2: Add styles for the multi-baseline chart**

Append to `site/styles.css`:

```css
/* ---------- multi-baseline interactive chart ---------- */
.baseline-tabs {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-3);
}
.baseline-tab {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
  background: #fff;
  border: 1px solid var(--light);
  color: var(--mute);
  border-radius: 999px;
  cursor: pointer;
  transition: all 100ms ease;
}
.baseline-tab:hover { color: var(--ink); border-color: var(--mute); }
.baseline-tab.active {
  background: var(--ink);
  color: #fff;
  border-color: var(--ink);
}
.baseline-title {
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: var(--space-2);
}
.baseline-plot { background: #fff; border-radius: 3px; }
.baseline-note {
  font-family: var(--font-ui);
  font-size: 12px;
  font-style: italic;
  color: var(--mute);
  line-height: 1.5;
  margin-top: var(--space-2);
}
```

- [ ] **Step 14.3: Verify in browser**

Open the page; scroll to the multi-baseline figure. Expected: PNG flashes briefly, then is replaced by a tab strip (1-year / 5-year / Decade / National context). "Decade" is active by default and shows two bars (Headline +72%, Adjusted +47%). Click each tab; the bar chart swaps. Hovering bars shows tooltips.

- [ ] **Step 14.4: Commit**

```bash
git add site/js/multi-baseline.js site/styles.css
git commit -m "Add interactive multi-baseline view (chart 14)"
```

---

## Task 15: SEO + Open Graph metadata + favicon + og-image

**Files:**
- Modify: `site/index.html` (extend `<head>` with metadata tags)
- Create: `site/favicon.svg`
- Create: `site/assets/og-image.png` (or use chart 01 hero crop)

- [ ] **Step 15.1: Add metadata tags to the <head>**

Within `site/index.html`'s `<head>`, immediately after the existing `<meta name="description">` tag, insert:

```html
<meta property="og:type" content="article">
<meta property="og:title" content="NYC has a sustained, domestic-violence-driven assault crisis. The city's response is not scaling to meet it.">
<meta property="og:description" content="A NYC strategy memo on the sustained, DV-driven felony-assault rise. Built as a public artifact by Zarren Kuzma.">
<meta property="og:url" content="https://zarrenkuzma.com/nyc-strategy/">
<meta property="og:image" content="https://zarrenkuzma.com/nyc-strategy/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="zarrenkuzma.com">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="NYC has a sustained, domestic-violence-driven assault crisis.">
<meta name="twitter:description" content="A NYC strategy memo on the DV-driven felony-assault rise. By Zarren Kuzma.">
<meta name="twitter:image" content="https://zarrenkuzma.com/nyc-strategy/assets/og-image.png">

<meta name="author" content="Zarren Kuzma">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://zarrenkuzma.com/nyc-strategy/">
```

- [ ] **Step 15.2: Create the favicon**

Create `site/favicon.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="12" fill="#1a1a1a"/>
  <text x="32" y="44" text-anchor="middle" font-family="-apple-system, Inter, sans-serif" font-size="36" font-weight="700" fill="#FF6319">Z</text>
</svg>
```

- [ ] **Step 15.3: Create the og-image**

Use chart 01 (the hero) as the share image. From the project root:

```bash
cd /home/zkuzma8/claude_code/nyc-strategy-artifact
.venv/bin/python -c "
from PIL import Image
img = Image.open('site/assets/charts/01-hero.png')
target = Image.new('RGB', (1200, 630), '#fafaf7')
# Fit chart 01 (preserving aspect ratio) into 1200x630 canvas
ratio = min(1200 / img.width, 630 / img.height)
new_w, new_h = int(img.width * ratio), int(img.height * ratio)
img_resized = img.resize((new_w, new_h), Image.LANCZOS)
target.paste(img_resized.convert('RGB'), ((1200 - new_w) // 2, (630 - new_h) // 2))
target.save('site/assets/og-image.png', 'PNG', optimize=True)
print('Wrote site/assets/og-image.png')
"
```

Expected output: `Wrote site/assets/og-image.png`. Verify the file exists and is approximately 1200x630.

- [ ] **Step 15.4: Verify**

Open the page; nothing visible should change. View page source; the new meta tags are present. The favicon shows in the browser tab.

Optionally test sharing via [opengraph.xyz](https://www.opengraph.xyz) (paste the eventual deployed URL); the OG image should preview correctly.

- [ ] **Step 15.5: Commit**

```bash
git add site/index.html site/favicon.svg site/assets/og-image.png
git commit -m "Add SEO, Open Graph metadata, favicon, and og-image"
```

---

## Task 16: Accessibility pass

**Files:**
- Modify: `site/index.html` (add ARIA where missing)
- Modify: `site/styles.css` (focus styles)

- [ ] **Step 16.1: Add ARIA attributes**

Several places in `site/index.html` need ARIA hints. Make these edits:

In the hero figure, on the `<img>` tag, ensure the `alt` text is descriptive (it was added in Task 3; verify it exists).

For the interactive chart figures, add an `aria-label` describing each:

```html
<!-- In the multi-baseline figure (chart 14): -->
<figure id="chart-14-container" data-chart="multi-baseline" aria-label="Multi-baseline view: how NYC's felony-assault rise looks at different time scales versus national peers.">

<!-- In the precinct map figure (chart 06): -->
<figure id="chart-06-container" data-chart="precinct-map" aria-label="NYC precinct map: percent change in felony assault from 2017 to 2024, broken down by police precinct.">
```

For the precinct-map and multi-baseline interactive elements (added by JS in Tasks 13 and 14), add an extra step in those scripts to give the rendered SVGs an `aria-label`. Already covered by Plot's `title` channel for hover tooltips; the figure-level `aria-label` is the main improvement here.

- [ ] **Step 16.2: Add visible focus styles**

Append to `site/styles.css`:

```css
/* ---------- focus styles ---------- */
a:focus-visible, button:focus-visible {
  outline: 2px solid var(--orange);
  outline-offset: 2px;
  border-radius: 2px;
}
.toc a:focus-visible {
  outline-offset: 1px;
}
```

- [ ] **Step 16.3: Verify keyboard navigation**

Open the page. Press Tab repeatedly. Expected:
- Focus moves through topbar links, hero byline link, TOC items (in order), body links and inline links, multi-baseline tabs, source links, methodology links, footer links.
- Each focused element gets a visible orange outline.
- Pressing Enter on a TOC item scrolls to that section.
- Pressing Enter on a multi-baseline tab activates it.

- [ ] **Step 16.4: Run an accessibility audit (manual)**

Open Chrome DevTools → Lighthouse → Accessibility audit. Run it. Expected: score ≥ 95. Note any flagged issues and fix the two or three most impactful ones inline (color contrast, missing labels, button-without-name, etc.) before commit.

- [ ] **Step 16.5: Commit**

```bash
git add site/index.html site/styles.css site/js/precinct-map.js site/js/multi-baseline.js
git commit -m "Accessibility pass: ARIA labels, focus styles, keyboard navigation"
```

---

## Task 17: Performance pass + final verification

**Files:**
- Verify (no edits unless issues found)

- [ ] **Step 17.1: Run Lighthouse on the production-style build**

Start a local server and run Lighthouse in Chrome DevTools (desktop preset, "Performance" + "Accessibility" + "Best Practices" + "SEO"):

```bash
cd /home/zkuzma8/claude_code/nyc-strategy-artifact/site && python3 -m http.server 8000
# In Chrome DevTools, run Lighthouse on http://localhost:8000
```

Expected: each category ≥ 95. Note specific failures.

- [ ] **Step 17.2: Verify the 14 acceptance criteria from the spec**

Open `docs/superpowers/specs/2026-05-06-html-artifact-design.md`, scroll to the Verification section, and walk through each numbered item with the live page. Mark which pass and which need follow-up. Specifically:

1. `site/index.html` renders the full memo content in the structured order. ✓ if all 7 sections + appendix + footer are present.
2. All 14 charts appear at their assigned section locations. ✓ if charts 01-14 are visible in the right sections.
3. Chart 06 shows hover tooltips and click-to-pin. ✓ if hovering precincts gives info; falls back if scripting blocked.
4. Chart 14 supports the four-tab toggle. ✓ if tabs swap content; falls back if scripting blocked.
5. Reading-progress bar fills as scrolling. ✓ if orange bar grows with scroll.
6. Sticky TOC tracks the active section. ✓ if highlighting shifts as you scroll.
7. FCP < 1.5s on a typical broadband connection. ✓ if Lighthouse's First Contentful Paint metric is under 1500ms.
8. axe DevTools (or Lighthouse Accessibility) shows no critical/serious issues.
9. Lighthouse desktop ≥ 95 across Performance, Accessibility, Best Practices, SEO.
10. The site directory contains only relative paths. ✓ if grep for absolute paths or `https://localhost` returns nothing.
11. Open Graph and Twitter Card metadata renders correctly when shared.
12. Methodology section is filled out as 600-800 words. ✓ if word count is in range.
13. Footer links to author contact and to a methodology anchor. ✓ if both work.
14. The artifact reads as a finished essay top to bottom. ✓ subjective; verify no draft markers, TODOs, or process artifacts remain.

- [ ] **Step 17.3: Final commit**

If any small fixes were made during verification:

```bash
git add -A
git commit -m "Final verification: address Lighthouse and accessibility findings"
```

If nothing changed, skip this step.

- [ ] **Step 17.4: Tag a release candidate**

```bash
git tag -a phase-2-ship-rc -m "HTML artifact ready for deployment to zarrenkuzma.com/nyc-strategy/"
git log --oneline -20
```

---

## Verification

The build is complete when each task's checkboxes are checked, the Verification subsection of the spec passes (Task 17 step 17.2), and the page reads as a polished editorial essay top to bottom in a browser.

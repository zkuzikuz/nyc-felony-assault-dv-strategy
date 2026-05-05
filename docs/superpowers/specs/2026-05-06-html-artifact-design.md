# HTML Artifact Design Spec

**Date:** 2026-05-06
**Status:** Approved (post-brainstorm)
**Implementation:** to follow via writing-plans skill

---

## Context

Phase 0 produced a hardened evidence memo (`memos/phase0_evidence.md`, ~6,700 words) and 14 chart sketches (`figures/sketches/01-14_*.png`) on NYC's domestic-violence-driven felony-assault rise. The memo argues for a three-part policy package (operationalizing the announced $650M Bridge to Home pipeline, expanding B-HEARD to 24-hour operations, piloting LAP and OFDVI in 4-6 precincts) and was hardened through three rounds of adversarial review with independent research-and-verification agents on load-bearing claims.

Phase 2 turns that memo into a published HTML artifact for Zarren Kuzma's NYC job applications. The artifact must:

1. Read as a polished public essay aimed at a generic intelligent reader (hiring managers across civic-tech, strategy, chief-of-staff, and ads roles).
2. Preserve the memo's analytical rigor while presenting it in editorial-longform form.
3. Embed the 14 charts at the right narrative moments.
4. Be transparent about the AI-assisted workflow that produced it.

The artifact lives at `zarrenkuzma.com/nyc-strategy/` as a public, search-indexed page.

---

## Decisions (locked during brainstorm)

| # | Decision | Choice |
|---|---|---|
| 1 | Scope | Public portfolio piece; not targeted variants |
| 2 | Closing CTA | Strict-analytical (no "hire me" pitch in memo body) |
| 3 | Visual personality | Editorial longform (NYT Upshot / Atlantic feel) |
| 4 | Layout | Single long-scroll page, sticky TOC on left, charts inline, thin reading-progress bar at top |
| 5 | Hero | Kicker (orange uppercase), serif title, italic dek, byline divider |
| 6 | Chart treatment | Hybrid: 12 static (PNG with caption), 2 interactive (precinct map and multi-baseline view) |
| 7 | Tech stack | Pure static HTML/CSS/JS; no framework, no npm, no build step |
| 8 | Typography | Newsreader (body) + Inter (UI), Google Fonts CDN |
| 9 | AI-tool provenance | Dedicated methodology section near the end of the memo, also linked from the byline |

---

## Color palette

Carries forward from the chart sketches so the page and the charts feel like one artifact.

| Name | Hex | Use |
|---|---|---|
| NYC Orange | `#FF6319` | Focal accent, kicker, progress bar, link hover, chart focal category (felony assault) |
| DV Magenta | `#D8127B` | DV-specific cuts in charts only |
| Navy | `#003C71` | Structural drivers in charts; link color in body |
| Ink | `#1a1a1a` | Body text and headings |
| Paper | `#fafaf7` | Chart blocks, code surfaces, footer |
| Mute | `#888888` | Captions, source lines, meta text |
| Light gray | `#e8e8e8` | Borders, hairlines |

---

## Typography

Fonts loaded from Google Fonts CDN (single `<link>` tag).

```html
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

| Element | Font | Size | Line height | Weight |
|---|---|---|---|---|
| Body paragraph | Newsreader | 18px | 1.65 | 400 |
| Body emphasis (`<strong>`) | Newsreader | 18px | 1.65 | 700 |
| Body italic (`<em>`) | Newsreader italic | 18px | 1.65 | 400 |
| H1 (page title) | Newsreader | 44px | 1.15 | 700 |
| H2 (section) | Newsreader | 30px | 1.20 | 700 |
| H3 (sub-section) | Newsreader | 22px | 1.30 | 700 |
| Dek (lede italic) | Newsreader italic | 22px | 1.50 | 400 |
| Kicker | Inter | 12px | 1.4 | 600 (uppercase, letter-spacing 1.6px) |
| Byline | Inter | 13px | 1.5 | 500 |
| TOC | Inter | 14px | 1.7 | 500 |
| Chart caption | Inter italic | 13px | 1.5 | 400 |
| Source line | Inter italic | 12px | 1.45 | 400 |
| Footer | Inter | 12px | 1.5 | 400 |
| Code (inline) | system monospace | 0.92em | inherit | 400 |

Body column max-width: 720px (centered). TOC column: 200px wide. Total content width on wide screens: ~1100px.

---

## Page structure (top to bottom)

| # | Section | Content | Charts inline |
|---|---|---|---|
| 1 | Top bar | Site mark, reading time | — |
| 2 | Reading-progress bar | Thin (3px), orange fill on scroll | — |
| 3 | Hero | Kicker, title, dek, byline divider | 01 hero (big-number panel + sparkline) |
| 4 | In brief | Synthesis paragraph, three-part recommendation as numbered list, cost / funding paragraph, savings caveat paragraph | — |
| 5 | What the numbers show | Four facts: largest violent felony, DV is the driver, sustained rise, not a national trend, broadly distributed | 02 majors, 03 DV split, 05 trajectories, 14 multi-baseline (interactive), 06 precinct map (interactive) |
| 6 | Why the city has not responded | Reporting framework + flat investment | 04 stacked layers |
| 7 | What to do | Problem to solve, opportunity space (5 categories), chosen levers (3), execution detail for Lever 3 | 07 beds, 08 distal, 09 B-HEARD breakdown, 10 B-HEARD coverage, 11 timeline, 12 DV rank, 13 quadrant |
| 8 | Sources | Grouped link list | — |
| 9 | Methodology | How the analysis was done; AI-assisted workflow; agent-driven research and verification | — |
| 10 | Appendix | What NYC has tried (table), Strength of supporting evidence, Findings worth flagging, Limits of the data, Why hot-spots policing isn't in the recommendation | — |
| 11 | Footer | Author byline, contact / LinkedIn, copyright, "built with Claude Code" methodology link | — |

The TOC mirrors sections 4-10 (skips Hero, top bar, footer). TOC items are clickable anchor links; the active section highlights as the reader scrolls.

---

## Interactive chart specs

### Chart 06: precinct map (interactive)

- **Library:** Observable Plot loaded from CDN (`https://cdn.jsdelivr.net/npm/@observablehq/plot`).
- **Behavior:**
  - Default render: NYC 5-borough choropleth, 78 precincts colored on an orange ramp by 2017→2024 felony-assault percent change.
  - On hover: tooltip shows precinct number, borough, 2024 count, percent change.
  - On click: tooltip pins (re-click to unpin).
  - Concentration callout box stays as static text overlay (top-1 share, top-10 share, "76 of 78 precincts grew").
- **Data files:**
  - `data/precincts.geojson` (already in repo at `data/geo/precincts.geojson`).
  - `data/precinct-stats.json` — per-precinct 2017 count, 2024 count, percent change. Generated from `data/processed/aggregates/felony_precinct_yearly.parquet` via a small Python script run once.
- **Static fallback:** the existing `figures/sketches/06_precinct_growth.png`. Loaded as an `<img>`; replaced by the interactive chart on DOM ready if Plot loads. If the CDN is unreachable, the PNG stays.

### Chart 14: multi-baseline view (interactive)

- **Library:** Observable Plot, same CDN.
- **Behavior:**
  - Tab-style toggle at top of chart: "1-year" / "5-year" / "Decade" / "National context."
  - Click a tab → swap the rendered panel. Each panel shows a single bar chart with the relevant comparison.
  - Default tab: "Decade" (the strongest version of the story).
  - On hover within a panel: tooltip shows the exact percentage and source.
- **Data file:** `data/baseline-data.json` — small, hand-curated JSON with the percentages from the memo.
- **Static fallback:** the existing `figures/sketches/14_baselines.png` (which shows all four panels at once). Same progressive-enhancement pattern.

---

## Methodology section — content outline

Target: ~600-800 words, written as honest tradecraft notes for a curious reader. Outline:

1. **What this is.** A NYC strategy memo built as a public artifact. Phase 0 evidence work, Phase 1 (chart selection) complete, Phase 2 (this HTML build) shipped.
2. **Data sources.** NYPD Complaint Data Historic (qgea-i56i, NYC OpenData), NYC Comptroller's B-HEARD audit, NY DCJS DV feed (via Vital City), Manhattan Institute deinstitutionalization paper, NY State Comptroller's 2024 mental-health report, NYC Council Finance Committee HRA reports, FBI UCR/NIBRS, Council on Criminal Justice city panels, Koppa 2024 (JEBO), Sechrist & Weil 2018 (NIJ), Braga & Weisburd 2019 (Campbell systematic review).
3. **The analytical pipeline.** Python (pandas, geopandas, sodapy), DuckDB for local cache, hive-partitioned parquet under `data/raw/`. Small aggregate parquets and CSVs committed to the repo for chart reproducibility.
4. **Three rounds of adversarial review.** Round 1: skeptical hiring manager. Round 2: methodological peer reviewer. Round 3: hostile policy critic. Each round, a fresh independent agent attacked the memo's claims; gaps that survived rebuttal became research questions for a separate unbiased research agent. The recommendation visibly changed across the three rounds: "deploy DV-CMS port" → "deploy LAP and OFDVI" → "pilot LAP and OFDVI with rigorous evaluation" → "lead with housing and B-HEARD; pilot LAP and OFDVI third with safeguards and a sunset."
5. **Independent research and verification on load-bearing claims.** Four high-stakes claims got research-then-verify agent pairs: B-HEARD precinct count (verified at 31 of 78, correcting an earlier "28"), NYC vs national outlier framing (verified across FBI UCR, CCJ 24-city, and per-city comparators), NYC DV-spending trajectory (verified via NYC Council Finance reports plus CPI-U adjustment), and long-run cost offsets of the recommended pilots (disputed several unit-cost figures, leading the memo to label the savings range "illustrative, not estimable").
6. **Source audit.** Every cited URL classified A-H by reputability (government, peer-reviewed, university research center, reputable news, reputable nonprofit, partisan think tank, Wikipedia, other). Load-bearing claims independently fact-checked.
7. **AI-tool transparency.** Built using Claude Code as drafting and analysis support. Human directs intent, edits, and decision-making throughout. Full conversation logs available on request.
8. **Limits of the analysis.** Pointer to the appendix's "Limits of the data" section.
9. **Reproducibility.** Repo public on GitHub; link in the footer. All aggregates and chart-rendering scripts in the repo. Raw data regenerable from NYC OpenData with a free SODA token.

---

## File structure

```
nyc-strategy-artifact/
  site/
    index.html              # the memo, single page
    styles.css              # one stylesheet
    js/
      precinct-map.js       # interactive chart 06
      multi-baseline.js     # interactive chart 14
      progress-bar.js       # reading-progress + sticky TOC active state
    data/
      precincts.geojson     # for chart 06 (copy from data/geo/)
      precinct-stats.json   # 2017/2024 counts + percent change per precinct
      baseline-data.json    # for chart 14
    assets/
      charts/
        01-hero.png         # PNG fallbacks for all 14 charts
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
      og-image.png          # social-share image (Open Graph + Twitter Card)
    favicon.svg
```

All paths relative; the site can drop into `zarrenkuzma.com/nyc-strategy/` with no rewriting. The PNGs in `assets/charts/` are direct copies (renamed from the sketches/) for path simplicity.

---

## Deployment

Static. The `site/` directory is the artifact. Deploy by uploading to wherever zarrenkuzma.com is hosted (S3, Netlify, Vercel, Cloudflare Pages, GitHub Pages, or a traditional web server) under the `/nyc-strategy/` path. No build step. No runtime dependencies.

A small Python script (`scripts/build_site_data.py`) runs once to:
1. Convert `data/processed/aggregates/felony_precinct_yearly.parquet` to `site/data/precinct-stats.json`.
2. Copy `data/geo/precincts.geojson` to `site/data/precincts.geojson`.
3. Copy `figures/sketches/0*.png` to `site/assets/charts/` with the renamed paths above.
4. Hand-curate `site/data/baseline-data.json` (small, ~10 lines, values copied directly from the memo).

The script runs once and only re-runs if the underlying parquet/sketches change.

---

## Performance budget

- First Contentful Paint: under 1.5s on a typical broadband connection.
- Total page weight: under 3MB (mostly chart PNGs).
- CSS: single stylesheet, < 100KB unminified, < 30KB minified.
- JS: < 80KB total (Observable Plot from CDN counts toward weight; ~70KB gzipped).
- Fonts: Google Fonts CDN with `display=swap` so text appears immediately in fallback then swaps.
- All chart PNGs already optimized at 1200-1650px wide; no further compression needed at first.

---

## Accessibility

- Semantic HTML (`<article>`, `<section>`, `<nav>`, `<aside>`, `<figure>`, `<figcaption>`).
- All chart `<img>` tags get descriptive `alt` text mirroring the chart's title and message.
- Interactive charts have `aria-label` and keyboard navigation (tab through precincts; Enter to pin tooltip).
- Color contrast meets WCAG AA at body text size (NYC orange #FF6319 on white = 3.36:1, fails for body but passes for large text and accents — that's its only role here).
- Reading-progress bar has `role="progressbar"` and `aria-valuenow`.
- TOC has `role="navigation"` and `aria-label="Table of contents"`.

---

## Out of scope

- Targeted variants of the memo (e.g., "for [your company]" closes). Decided as Scope = public portfolio piece.
- A multi-page chaptered version. Decided as Layout = single long-scroll.
- All-interactive charts. Decided as Chart treatment = hybrid.
- A framework-based build (Astro, Next, etc.). Decided as Tech stack = pure static HTML/CSS/JS.
- Server-side rendering, runtime data fetching, or any backend. The artifact is fully static.
- A CMS or dynamic content. The memo content lives in `index.html` directly.
- Any analytics or tracking. (Author may add later separately if desired; not in scope for this build.)
- Comments, social engagement, or interactivity beyond the two interactive charts.
- Print stylesheet beyond the natural cascade. (PDF export is a Phase 3 nice-to-have, not in scope here.)

---

## Verification

The build is complete when:

1. `site/index.html` renders the full memo content from `memos/phase0_evidence.md` in the structure described above.
2. All 14 charts appear at their assigned section locations.
3. Chart 06 (precinct map) shows hover tooltips and click-to-pin behavior; falls back to PNG if Observable Plot fails to load.
4. Chart 14 (multi-baseline view) supports the four-tab toggle; falls back to PNG if Observable Plot fails to load.
5. Reading-progress bar fills as the user scrolls.
6. Sticky TOC tracks the active section; clicking an entry scrolls smoothly to it.
7. Page loads in under 1.5s First Contentful Paint on a typical broadband connection (test with browser devtools throttle).
8. Accessibility: passes axe DevTools with no critical or serious issues; tab-through-only navigation reaches every interactive element.
9. Lighthouse desktop score: ≥ 95 across Performance, Accessibility, Best Practices, SEO.
10. The site directory contains only relative paths; copy-pasting `site/` to a different host root preserves all links.
11. Open Graph + Twitter Card metadata renders correctly when the URL is shared (test via Facebook Sharing Debugger or Twitter's Card Validator).
12. The methodology section's outline is filled out as ~600-800 words of finished prose.
13. The footer links to author contact and to a methodology anchor.
14. The artifact reads as a finished essay top to bottom, with no draft markers, TODO comments, or process artifacts.

---

## Implementation handoff

Next step: invoke the writing-plans skill to produce a step-by-step implementation plan, sequencing the build into reviewable checkpoints (skeleton + styles → memo content → static charts → interactive chart 06 → interactive chart 14 → progress bar + TOC → methodology section prose → polish + verification).

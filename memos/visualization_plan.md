# Visualization Plan v2 for Phase 0 Memo

**Status.** 14 sketch PNGs are rendered to `figures/sketches/01_*` through `figures/sketches/14_*`. The script that produces them is `scripts/render_sketches.py`. This document is the planning artifact that ties each chart to a memo claim and a data source.

**Layout convention for every chart:**
1. Bold title at the top — the message.
2. Italic grey subtitle below the title — a complete sentence at 9th-grade reading level that says what the chart means.
3. Chart body.
4. Italic grey source line at the bottom, well clear of axis labels.

**Color palette.** Orange (#FF6319) for the focal category (felony assault). Magenta (#D8127B) for DV-specific cuts. Navy (#003C71) for structural / non-focal violent. Grey (#6B6B6B / #CCCCCC) for neutrals and non-focal categories.

---

## Final chart sequence (14 charts)

| # | File | Section in memo | Message |
|---|---|---|---|
| 01 | `01_hero_bignumber.png` | TL;DR | The +72% headline overstates how much NYC felony assault actually grew; the real behavioral rise is +47%. |
| 02 | `02_situation_majors.png` | Situation | Felony assault is the largest violent-felony category in NYC. |
| 03 | `03_dv_split.png` | TL;DR / Complication | DV is the dominant driver — both as a growth rate (+73% vs +40%) and as a 2024 absolute share (~11,800 of 29,501 cases). |
| 04 | `04_complication_stacked.png` | Complication | The +72% headline includes a new felony class (Strangulation 1st) and a DV surge inside the catch-all sub-category. |
| 05 | `05_trajectories.png` | Complication | Felony assault is rising faster than any other violent-crime peer in NYC. |
| 06 | `06_precinct_growth.png` | Complication | No single precinct drove the citywide rise — 76 of 78 precincts grew, top-1 contributed ~6% and top-10 ~36%. |
| 07 | `07_beds.png` | Support 1 — Housing | NYC has fewer than 100 supportive-housing beds against the announced 2,000-person target. |
| 08 | `08_distal.png` | Support 1 — Housing | As NY State inpatient psychiatric capacity contracted, NYC felony assault rose. Aligned dual-axis scales make the visual comparison honest. |
| 09 | `09_bheard_breakdown.png` | Support 2 — B-HEARD | Eligible mental-health 911 calls split into three distinct buckets (got B-HEARD; in-hours unmet; overnight unmet) with two distinct fix levers. |
| 10 | `10_bheard_coverage.png` | Support 2 — B-HEARD | B-HEARD covers 31 of 78 precincts — and they are higher-incidence on average. |
| 11 | `11_timeline.png` | Support 3 — DV Pilot | The pilot has a binding fund-or-de-fund decision at month 30. |
| 12 | `12_dv_rank.png` | Evidence base | LAP and OFDVI are the recommended programs because they have the strongest DV-specific evidence. |
| 13 | `13_quadrant.png` | Evidence base / What NYC tried | LAP and OFDVI are the only programs with both strong evidence and DV relevance. |
| 14 | `14_baselines.png` | Secondary observation / National context | The window choice IS the framing. NYC is well above any national or peer-city benchmark. |

---

## Chart specifications

### 01 — Hero (`01_hero_bignumber.png`)
- **Type.** Big-number panel + paired sparkline.
- **Data.** `data/processed/aggregates/felony_assault_subcategory_yearly.parquet` (in-repo). Naive total minus Strangulation 1st.
- **Annotations.** Heavy black strikethrough on top of the +72% (renders above text via zorder); +47% in orange below; sparkline shows naive total in grey vs adjusted in orange with dots only at actual data years (2010, 2014, 2019, 2024).
- **Message.** "The +72% headline overstates how much NYC felony assault has actually grown."

### 02 — Situation (`02_situation_majors.png`)
- **Type.** Horizontal bar of 4 violent-felony categories in 2024.
- **Data.** `data/processed/aggregates/felony_yearly.parquet` (in-repo). Filter to Murder, Rape, Robbery, Felony Assault.
- **Annotations.** Felony Assault highlighted in orange; numeric labels at bar ends.
- **Message.** "Felony assault is the largest violent-felony category in NYC (2024)."
- **Note.** Property crime (Grand Larceny) is larger overall but excluded from this comparison.

### 03 — DV split (`03_dv_split.png`)
- **Type.** Two-panel: horizontal bars (growth rates) + pie (2024 absolute share).
- **Data.** External (Vital City citing DCJS DV feed) for the +73% / +40% growth rates and ~40% household share.
- **Annotations.** +73% vs +40% growth rate labels; pie shows 11,800 vs 17,701 cases (=29,501 total).
- **Message.** "Domestic violence is the dominant driver of NYC's felony-assault rise."
- **Caveat.** NYPD's public dataset does not contain a victim-relationship field; the DV share is sourced from the DCJS feed Vital City reports against.

### 04 — Stacked sub-categories with DV breakout (`04_complication_stacked.png`)
- **Type.** Stacked column at four data years (2010, 2014, 2019, 2024).
- **Data.** `data/processed/aggregates/felony_assault_subcategory_yearly.parquet` (in-repo). DV portion of catch-all estimated via Vital City's ~40% household-share figure applied to total felony-assault count, capped at the catch-all sub-category size.
- **Annotations.** 2010 baseline reference line; arrow callout explaining the strangulation reclassification.
- **Message.** "The +72% headline includes a new felony class and a DV surge inside the catch-all."
- **Layers.** DV-driven catch-all (magenta), other catch-all (orange), Assault on Police/Peace Officer (grey), Strangulation 1st (navy), other new sub-categories (light grey).

### 05 — Trajectories (`05_trajectories.png`)
- **Type.** Single-chart line plot of all 16 top felony categories, 2017-2024, indexed to 2017 = 1.0.
- **Data.** `data/processed/aggregates/felony_yearly.parquet` (in-repo).
- **Color groups.** Orange for Felony Assault (focal); navy for the other three violent felonies (Murder, Rape, Robbery); grey for property and non-violent felonies.
- **Annotations.** Endpoint labels for the violent set + a few comparators; COVID reference line at 2020.
- **Message.** "Felony assault is rising faster than any other violent-crime category in NYC."

### 06 — Precinct growth (`06_precinct_growth.png`)
- **Type.** Single NYC choropleth (no left/right split).
- **Data.** `data/processed/aggregates/felony_precinct_yearly.parquet` + `data/geo/precincts.geojson` (in-repo).
- **Annotations.** Color encodes 2017-to-2024 % change per precinct; concentration callout box reports top-1 share, top-10 share, and number of precincts with growth.
- **Message.** "No single precinct drove the citywide felony-assault rise — 76 of 78 precincts saw growth, top-1 contributed about 6% and top-10 about 36%."

### 07 — Bed-capacity gap (`07_beds.png`)
- **Type.** Stacked horizontal bars: today vs recommended.
- **Data.** External (Mayor's January 2025 announcement; memo Sources).
- **Annotations.** Numeric labels for BTH and Safe Haven counts; reference line at 2,000-person target.
- **Message.** "NYC has fewer than 100 supportive-housing beds against a 2,000-person target."
- **Note.** Could be substituted for a small text table in HTML; kept as chart for visual consistency.

### 08 — Distal driver (`08_distal.png`)
- **Type.** Dual-axis line chart with aligned scales.
- **Data.** External (Manhattan Institute deinstitutionalization paper for 2014 and 2021 psych-bed endpoints; memo Sources). NYPD `felony_assault_subcategory_yearly.parquet` (in-repo) for assault.
- **Aligned-scales construction.** Left axis 2200-3200; right axis 16000-32000; both axes have the same number of evenly spaced ticks at matching vertical positions.
- **Annotations.** Dots at documented data years only (no inferred values between); callout for "−700+ beds, documented endpoints."
- **Message.** "As NY State inpatient psychiatric capacity contracted, NYC felony assault rose."
- **Caveat.** Trend lines connect documented endpoints; intermediate values are not pulled.

### 09 — B-HEARD breakdown (`09_bheard_breakdown.png`)
- **Type.** Single horizontal stacked bar with three segments + lever callouts.
- **Data.** External (NYC Comptroller 2024 audit; memo Sources).
- **Annotations.** In-line segment labels (count + %); two lever callouts below the bar pointing to the in-hours and overnight gaps.
- **Message.** "NYC's eligible mental-health 911 calls split into three distinct buckets — and the two gaps have different fixes."

### 10 — B-HEARD coverage (`10_bheard_coverage.png`)
- **Type.** NYC choropleth with felony-assault density (orange shading) and B-HEARD precinct outlines (navy borders).
- **Data.** B-HEARD precinct list from NYC Comptroller 2024 audit Appendix II — verified independently against Mayor's Office November 2025 release and NYC IBO January 2026 brief. The 31-precinct list: Manhattan 25, 26, 28, 30, 32, 33, 34; Bronx 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52; Brooklyn 63, 67, 69, 71, 73, 75; Queens 104, 108, 110, 112, 114, 115. Felony-assault counts from `felony_precinct_yearly.parquet` (in-repo).
- **Annotations.** Comparison statistic box (mean count per precinct, covered vs uncovered, with ratio).
- **Message.** "B-HEARD covers 31 of 78 NYPD precincts — and they are higher-incidence on average."
- **Memo correction.** The earlier "28 of 77" framing was an interim count not supported by primary sources. The memo has been updated to 31 of 78.

### 11 — Pilot timeline (`11_timeline.png`)
- **Type.** Gantt-style horizontal with task labels on the left.
- **Data.** Derived from memo Section 3 design constraints.
- **Annotations.** Sunset gate at month 30 highlighted with vertical reference line and callout.
- **Message.** "The pilot has a binding fund-or-de-fund decision at month 30."

### 12 — Ranked DV interventions (`12_dv_rank.png`)
- **Type.** Horizontal effect-size bars with study-quality color, intervention description, and order-of-magnitude cost.
- **Data.** Memo literature review (Koppa 2024; Sherman & Berk; Sechrist & Weil; Cheng et al. 2021 meta-analysis; Cure Violence Global).
- **Annotations.** Bars colored orange for the two recommended programs (LAP, OFDVI); per-row description and cost.
- **Message.** "LAP and OFDVI are the recommended DV interventions — they have the strongest evidence."

### 13 — Program quadrant (`13_quadrant.png`)
- **Type.** 2×2 scatter — Evidence quality (x) × DV relevance (y).
- **Data.** Derived from memo "What NYC has tried" table.
- **Annotations.** Quadrant labels; orange dots for the two recommended programs (LAP, OFDVI); acronym key footer.
- **Message.** "LAP and OFDVI are the only programs with both strong evidence and DV relevance."

### 14 — Multi-baseline + national context (`14_baselines.png`)
- **Type.** Four-panel small-multiple bar chart.
- **Data.** NYC values from NYPD `qgea-i56i` + sub-category parquet (in-repo). National benchmarks from FBI UCR (~+1-2% 2010 to 2024), Council on Criminal Justice 24-city sample (~+4% since 2019), and LAPD 2024 EOY release (~−10% YoY).
- **Annotations.** Numeric labels at each bar; NYC adjusted figure highlighted in magenta in the national-context panel.
- **Message.** "The choice of time window decides whether NYC's felony-assault rise looks small, big, or like an outlier — NYC is well above any peer benchmark."

---

## Charts dropped during revision

- **Three-pillar comparator (Housing / B-HEARD / DV-pilot).** Did not earn its space. The same content lives more cleanly as a small text table in the memo's Framing-choice section.
- **Effect-size attenuation funnel.** Folded into memo Section 3 prose. The transportability discount is a paragraph, not a chart.
- **Cost stack vs FY26 budget gap.** Folded into memo Section 3 prose. The cost figures, plausible funding sources, and a directional read on long-run cost offsets are now a paragraph.
- **Window-selection illustration (October 2024 vs full-year).** Folded into the multi-baseline panel + memo Secondary-observation paragraph.

## Memo additions written during this revision

- **Section 3 paragraph on long-run cost offsets** — replaces the cost-stack chart. Cites $5-35M directional range with verification caveats; pilot is plausibly net-neutral to small-positive ROI on NYC's books.
- **Secondary-observation sub-section "National context"** — supports chart 14. Establishes that NYC is an outlier vs national + peer-city benchmarks, which strengthens the structural-driver framing.
- **B-HEARD precinct count correction** — memo now reads "31 of NYC's 78 precincts" everywhere it previously said "28 of 77."

---

## Cross-cutting design notes

- **Subtitle below title for every chart.** Subtitle reads at 9th-grade level in complete sentences; says what the chart means if extracted standalone.
- **Aligned dual-axis scales** (chart 08): tick positions on left and right axes line up at matching vertical positions.
- **No process artifacts** (no references to "earlier memo drafts," round numbers, Phase-2 implementation hedges, or HTML/SVG roadmap notes inside the charts themselves).
- **Even year ticks where applicable.** Multi-year time series use evenly spaced ticks (e.g., every 2 years from 2010 to 2024), with dots only at actual data years and lines connecting them.
- **Map projection.** Default geopandas projection (EPSG:2263 / NY State Plane equivalent works for NYC choropleths). Precinct boundaries from `data/geo/precincts.geojson`.
- **Static for sketch round.** Phase 2 may layer Plotly or Observable interactivity on the precinct map and the multi-baseline view.
- **Accessibility.** Color-blind-safe palette; minimum 4.5:1 contrast; alt-text per chart will be added in Phase 2 HTML.

## Data sources at a glance

**In-repo (ready to draw):**
- `data/processed/aggregates/felony_yearly.parquet`
- `data/processed/aggregates/felony_assault_subcategory_yearly.parquet`
- `data/processed/aggregates/felony_precinct_yearly.parquet`
- `data/processed/aggregates/cluster_assignments.csv`
- `data/processed/aggregates/precinct_dominant_cluster.csv`
- `data/geo/precincts.geojson`

**External (cited from memo Sources):**
- Vital City analysis of NYPD data citing DCJS DV feed (DV split for charts 03 and 04).
- Manhattan Institute deinstitutionalization paper (psych-bed endpoints for chart 08).
- NYC Mayor's January 2025 Care, Community, Action announcement (chart 07).
- NYC Comptroller 2024 B-HEARD audit Appendix II (chart 09 numbers; chart 10 precinct list).
- NYC.gov Mayor's Office November 2025 release (chart 10 corroboration).
- NYC IBO January 2026 brief (chart 10 corroboration).
- FBI UCR / Crime Data Explorer (chart 14 national benchmark).
- Council on Criminal Justice "Crime Trends in U.S. Cities" Year-End 2024 (chart 14, 24-city benchmark).
- LAPD 2024 EOY release (chart 14, peer-city benchmark).
- Koppa 2024 (Maryland LAP staggered DiD; chart 12).
- Sechrist & Weil 2018 (High Point OFDVI; chart 12).
- Sherman & Berk Minneapolis Domestic Violence Experiment (chart 12).
- Cheng et al. 2021 meta-analysis (chart 12).

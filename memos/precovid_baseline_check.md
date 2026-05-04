# Pre-COVID baseline check: structural vs COVID-driven rises

**Question.** For the seven NYC felony categories that were still rising in 2024, is the post-2020 increase a continuation of a pre-pandemic structural drift, or a COVID-era novelty (flat/declining 2010–2019, rising only after 2020)?

**Method.** Pulled 2010 and 2014 annual felony counts from NYPD `qgea-i56i` via the same SoQL aggregate pattern used in `scripts/pull_aggregates.py` (`$select=ofns_desc, COUNT(*)`, `$where=law_cat_cd='FELONY' AND <year-range>`, `$group=ofns_desc`). Indexed every category to its 2019 baseline and inspected the 2010 → 2014 → 2019 → 2024 trajectory.

## Results — indexed to 2019 = 1.00

| Category | 2010 | 2014 | 2017 | 2018 | 2019 | 2024 | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| FELONY ASSAULT | 0.82 | 0.97 | 0.97 | 0.98 | 1.00 | 1.41 | **STRUCTURAL** |
| CRIMINAL MISCHIEF & RELATED OF | 0.54 | 0.78 | 0.90 | 0.94 | 1.00 | 1.43 | **STRUCTURAL** |
| MISCELLANEOUS PENAL LAW | 0.77 | 0.95 | 0.92 | 0.92 | 1.00 | 1.34 | **STRUCTURAL** |
| DANGEROUS DRUGS | 1.11 | 0.82 | 0.85 | 0.75 | 1.00 | 1.57 | COVID-DRIVEN (rebound) |
| DANGEROUS WEAPONS | 1.29 | 1.09 | 1.15 | 1.10 | 1.00 | 1.33 | COVID-DRIVEN (rebound) |
| POSSESSION OF STOLEN PROPERTY | 1.20 | 1.48 | 1.42 | 1.28 | 1.00 | 2.27 | COVID-DRIVEN (rebound) |
| FORGERY | 1.00 | 1.01 | 1.12 | 1.08 | 1.00 | 1.48 | COVID-DRIVEN (flat baseline) |
| *contrast: GRAND LARCENY OF MOTOR VEHICLE* | 1.90 | 1.42 | 1.05 | 1.00 | 1.00 | 2.62 | COVID-DRIVEN (rebound) |
| *contrast: ROBBERY* | 1.46 | 1.23 | 1.04 | 0.97 | 1.00 | 1.23 | COVID-DRIVEN (rebound) |
| *contrast: GRAND LARCENY* | 0.88 | 1.03 | 1.00 | 1.01 | 1.00 | 1.11 | MIXED (near-flat 2010–2019) |

Classification rule: STRUCTURAL = 2010 indexed value ≥ 5% below 2019 with non-decreasing drift through 2014. COVID-DRIVEN (rebound) = 2010 ≥ 5% above 2019 (so 2010-2019 was declining; 2024 spike reverses that decline). COVID-DRIVEN (flat baseline) = 2010-2019 within ±10% with no drift. MIXED = anything else.

## Bottom-line verdict

**Of the 7 still-rising categories, 3 are structural and 4 are COVID-driven.**

- **Structural rises (already trending up before COVID):** FELONY ASSAULT, CRIMINAL MISCHIEF, MISCELLANEOUS PENAL LAW. All three were ≥18% below their 2019 level back in 2010, and the trend ran consistently upward through 2014 to 2019. The 2020-2024 acceleration extended a pre-existing drift.
- **COVID-driven rises (declining or flat pre-COVID, only rising after 2020):** DANGEROUS DRUGS, DANGEROUS WEAPONS, POSSESSION OF STOLEN PROPERTY, FORGERY. These four either declined sharply through the 2010s (POSSESSION OF STOLEN PROPERTY: 1.20 → 1.00; DANGEROUS WEAPONS: 1.29 → 1.00) or were essentially flat (FORGERY: 1.00 → 1.00). Their 2024 levels look like a regime break rather than the continuation of a pre-COVID trend.

The contrast group (GLA, ROBBERY, GRAND LARCENY) confirms the pattern — these are textbook 2010s success stories (GLA fell 47% from 2010 to 2019, robbery 32%) where 2024 is partly a rebound off historic lows. They are NOT structural rises, just incomplete reversions.

**Strategic implication for the memo.** A "structural rise" framing only honestly applies to FELONY ASSAULT, CRIMINAL MISCHIEF, and MISC PENAL LAW. The DANGEROUS DRUGS / DANGEROUS WEAPONS / FORGERY / STOLEN PROPERTY narrative needs different framing — it is a COVID-era regime break, not a long-running trend. Lumping them together would be a Minto-thesis liability.

## Data-quality notes

- **`qgea-i56i` does cover 2010 and 2014 cleanly.** 147,930 felonies in 2010 and 152,044 in 2014, distributed across 26 and 27 offense categories respectively. This confirms the registry note that the dataset is mis-named "Historic" but is the canonical full-history source.
- **Schema shifts to be aware of:** A few `ofns_desc` strings only appear in some years — `KIDNAPPING & RELATED OFFENSES` vs `KIDNAPPING AND RELATED OFFENSES` (different ampersand, used briefly in 2019), `CHILD ABANDONMENT/NON SUPPORT` vs `CHILD ABANDONMENT/NON SUPPORT 1` (renamed 2023+), `CANNABIS RELATED OFFENSES` (only post-legalization, 2022+), `FELONY SEX CRIMES` (2019-2023 only, distinct from `SEX CRIMES`). None of the 7 study categories suffered a rename — direct year-over-year comparison is valid for our seven targets.
- **One minor null:** a small number of complaints come back with `ofns_desc = (null)` and were filtered out via `ofns_desc IS NOT NULL`, matching `pull_aggregates.py`.
- 2010 and 2014 totals include all five boroughs and standard precinct coverage, so the comparison is apples-to-apples without borough/precinct adjustment.

## Files

- Pull script: `scripts/pull_precovid.py`
- New aggregate: `data/processed/aggregates/felony_yearly_precovid.parquet` (53 rows: 26 categories × 2010 + 27 × 2014)
- Existing 2017-2024 data: `data/processed/aggregates/felony_yearly.parquet` (untouched)

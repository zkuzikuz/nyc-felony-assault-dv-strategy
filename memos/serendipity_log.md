# Serendipity Log

Append-only record of anomalies, surprises, and side-observations encountered during
EDA that fall outside the three primary hypotheses (H1, H4, H5). Each entry follows:

```
## YYYY-MM-DD — short title
**What:** observation in one sentence.
**Where seen:** notebook / cut / dataset / query.
**Why surprising:** what makes this stand out.
**Worth pursuing?** Y / N / maybe — and why.
```

Top candidates surface into the Phase 0 evidence memo and may seed Phase 1 sub-stories.

---

## 2026-04-26 — 311 modern dataset (`erm2-nwe9`) has no `bbl` column
**What:** Modern 311 schema (2020-present) drops the `bbl` (Borough-Block-Lot) field that the historic dataset (`76ig-c548`) carries.
**Where seen:** schema sniff at acquisition time, before any cuts ran.
**Why surprising:** BBL is the canonical building identifier for NYC. Repeat-address analysis (C19) loses precision because we have to fall back to `incident_address` string matching, which has spelling/format variations.
**Worth pursuing?** Maybe — affects C19 and any future H5 building-level analysis. Could rejoin BBL via PLUTO if needed.

## 2026-04-30 — The "35-45% LAP" cite is misattributed; correct source is Koppa 2024 staggered-DiD on Maryland (37-44% female-IPH rate)
**What:** The frequently-cited "35-45% reduction in female homicide" figure for Lethality Assessment Programs is from Koppa 2024 — a staggered-rollout DiD analysis of Maryland's LAP rollout — not from the Messing Oklahoma evaluation, which has no homicide endpoint. Effect is 37-44%, jurisdiction-level female-IPH rate change, quasi-experimental identification.
**Where seen:** R2 research traced the citation chain; multiple policy summaries (NIJ included) attribute the figure imprecisely.
**Why surprising:** The misattribution shows up in policy memos that haven't dug into the underlying evaluations. Quoting the "35-45%" without naming Koppa 2024 leaves the source open to challenge. CrimeSolutions tiers are Effective / Promising / No Effects only — no "Supported" tier exists, despite this term appearing in some policy summaries.
**Worth pursuing?** **Yes — load-bearing for memo accuracy.** Memo updated to cite Koppa 2024 directly, with identification strategy made explicit.

## 2026-04-30 — Focused-deterrence transportability attenuation: matched-design effects ~28% of non-matched-design effects
**What:** Braga-Weisburd 2019 Campbell systematic review of focused-deterrence evaluations finds that matched-design comparisons produce effect sizes averaging ~28% of those reported by non-matched-design (simple pre/post or treated-only) studies. Cure Violence systematic review separately finds only 32.5% of evaluations report statistically significant findings.
**Where seen:** R2 research (transportability question).
**Why surprising:** Quantifies what "transportability discount" looks like for the focused-deterrence intervention class specifically. NYC effects from Maryland LAP (37-44%) or High Point OFDVI (20%) should plausibly be discounted to ~10-15% under matched-design identification — a substantial reframe of any "deploy this, it works" recommendation.
**Worth pursuing?** **Yes — load-bearing for recommendation framing.** Memo updated to acknowledge attenuation and reframe as pilot-with-evaluation rather than deployment-with-cited-effect-size.

## 2026-04-30 — B-HEARD audit denominator misframing corrected: the 14K overnight figure is in addition to, not the cause of, the 13K in-hours unserved gap
**What:** Comptroller Lander's B-HEARD audit found 13,042 unserved in-hours eligible calls (35% of in-hours eligible). Separately, ~14,200 calls during overnight hours were classified as eligible but B-HEARD doesn't operate then. R1 research initially framed the 14K overnight as "the largest single component" of the 13K gap — but R2 re-read of the audit finds the two are non-overlapping denominators. The audit does NOT track the cause of the in-hours unserved gap.
**Where seen:** R2 research; Comptroller audit appendix.
**Why surprising:** "Primarily a supply problem" was a misread. The supply lever (24-hour operations) addresses the separate ~14K overnight gap; the in-hours gap has untracked causes. The right action is implementing the audit's recommended cause-tracking before sizing an in-hours fix.
**Worth pursuing?** **Yes — corrects R1's framing.** Memo updated.

## 2026-04-30 — 3-cluster solution survives leave-one-offense-out (16/16 runs, k=3 best)
**What:** R2 ran a leave-one-offense-out clustering sensitivity test: drop each of the 16 felony offenses one at a time, re-run Ward-linkage clustering. k=3 was the silhouette-maximizing partition in 16 of 16 runs (silhouette 0.402-0.470). The FELONY ASSAULT / CRIMINAL MISCHIEF / MISC PENAL LAW trio co-clustered in 13 of 13 non-trio drops.
**Where seen:** R2 research using existing `data/processed/aggregates/felony_yearly.parquet`.
**Why surprising:** Adds a meaningful robustness check beyond R1's k-sweep + year-bootstrap. The structural-rise trio is statistically stable even when individual offenses are removed.
**Worth pursuing?** Methodologically reassuring; adds a strong row to the audit table.

## 2026-04-29 — Strangulation 1st (NYPL §121.11/12) was created in Nov 2010 — 35% of the +72% felony-assault headline is statutory, not behavioral
**What:** Of the 2010→2024 felony-assault increase (12,364 cases), ~4,400 came from a single sub-category — STRANGULATION 1ST (pd_cd 105) — which had only 146 cases in 2010 (capturing ~6 weeks after the law took effect) and 4,546 in 2024. The remainder of the rise distributes across the catch-all pd_cd 109 (Assault 2/1/Unclassified, +6,841) and smaller buckets. Excluding strangulation, the real behavioral rise is +47%, not +72%.
**Where seen:** Sub-category drill via SoQL `GROUP BY (pd_cd, pd_desc)`. Memo: `memos/assault_composition.md`.
**Why surprising:** Quoting the +72% number without this adjustment would not survive scrutiny. The statutory creation accounts for more than a third of what naive analysis treats as "behavioral rise." This is exactly the kind of definitional drift that any year-over-year crime comparison can hide.
**Worth pursuing?** **Yes — load-bearing.** Memo headline figures must use +47%, not +72%. Generalizes to a method note: any multi-decade trend claim on NYPD data must screen for statutory creation events.

## 2026-04-29 — DV is the dominant driver of NYC felony assault — and CMS, NYC's strongest violence-prevention model, doesn't address it
**What:** Vital City's analysis of NYPD data shows domestic + elder assault rose 73% from 2017-2024 vs 40% for other felony assault. ~40% of NYC felony assaults involve members of the same household. NYC's Crisis Management System (CMS / Cure Violence) — $86M, 41 precinct sites, with documented 21% shooting reductions per Comptroller Lander 2024 — is the city's strongest violence-prevention evidence base. It targets shootings. It does not target DV-driven assault.
**Where seen:** Memo: `memos/assault_interventions.md`. External sources: Comptroller Lander's *The Cure for Crisis* (CMS eval), Vital City crime trend analysis, Gothamist coverage of DV-driven assault rise.
**Why surprising:** The intervention gap is exactly where the empirical driver concentrates. NYC has a working architecture for the analogous problem and hasn't deployed it against the dominant assault driver. This is the substantive memo recommendation, not just a reporting fix.
**Worth pursuing?** **Yes — central thesis.** Phase 2 verification: reach out to John Jay REC for any work-in-progress on DV-CMS porting; check whether any other city has run an analogous program.

## 2026-04-28 — Mayor's "−1.9% felony assault" is a monthly Oct 2024 stat, not full-year 2024
**What:** The "felony assault down 1.9%" figure that initially looked like a contradiction with our +5.8% YoY number turned out to be the October 2024 *monthly* press release (2,359 vs 2,404 = −1.87% ≈ −1.9%). The January 2025 year-end announcement actually reports felony assault UP about 5% in 2024 — consistent with our analysis.
**Where seen:** Agent investigation comparing our SODA pull totals (29,501 in 2024 by `cmplnt_fr_dt`) against NYPD press-release wording. The monthly press release: nyc.gov/site/nypd/news/p0529/nypd-citywide-crime-statistics-october-2024.
**Why surprising:** Apples-to-oranges comparison hidden in plain sight. The monthly window happened to be favorable; the year-end window was not. Anyone citing the −1.9% as a year-end number would be misquoting NYPD's own data.
**Worth pursuing?** Yes — adds nuance to the audit. The framing problem isn't only baseline-selection (1yr vs 5yr); it's also **window-selection** (monthly stats that look better than year-end, used in press releases that are then re-cited). Worth surfacing in the strategy memo.

## 2026-04-28 — Pre-COVID baseline test splits the Surge cluster into structural vs COVID-rebound
**What:** Of the 7 felony categories still rising in 2024, only 3 are structurally trending upward since 2010 (FELONY ASSAULT, CRIMINAL MISCHIEF, MISC PENAL LAW — all were ≥18% below their 2019 level back in 2010 and rose monotonically through the 2010s). The other 4 (DRUGS, WEAPONS, POSSESSION OF STOLEN PROPERTY, FORGERY) declined or stayed flat 2010-2019 and only spiked after COVID — these are post-COVID regime breaks, not continuations of a structural drift.
**Where seen:** `memos/precovid_baseline_check.md` (agent-produced sub-investigation). Pulled 2010 and 2014 annual aggregates from `qgea-i56i` and indexed against 2019.
**Why surprising:** A "this is just COVID recovery" critique against the rotation thesis was partially correct — for 4 of the 7 categories, the COVID-rebound interpretation fits better than the structural-rise interpretation. But for 3 categories, the rise pre-dates COVID by a decade. **Felony assault has risen every year since 2010, including pre-COVID.** That's the cleanest, most defensible structural-rise example for the memo.
**Worth pursuing?** **Yes — load-bearing.** This refines the thesis to a stronger version: structural rises (3 categories) are hidden by the aggregate AND by 1-year YoY framing. The COVID-rebound categories deserve separate framing, not the same treatment.

## 2026-04-26 — NYPD "Historic" dataset is actually ALL years through 2025; "YTD" is current year only
**What:** Despite the names, `qgea-i56i` ("Historic") covers 2006-2025 with 9.49M rows including 565K rows for 2024. `5uac-w243` ("YTD") contains only 2025 + a few stragglers — 579K rows total, of which 568K are 2025 and 9K are 2024 (likely late-reported / re-classified).
**Where seen:** Pilot pulled Q4 2024 from YTD and got 5,786 rows — implausibly low (Q4 2019 historic had 113,914). Year-distribution query on YTD revealed almost the whole dataset is 2025.
**Why surprising:** Both the dataset names and the official NYC OpenData metadata text imply Historic ends in 2019 ("2006-2019"). It does not — it now extends through 2025. Anyone reading the dataset descriptions naively (as the original explore-agent research did) would partition pulls along the wrong boundary, dramatically under-counting post-2020 NYPD data.
**Worth pursuing?** **YES — load-bearing for H4 and H1.** Without this correction, every analysis from 2020 onward is missing 95%+ of NYPD records. **Action taken:** updated `DATASETS` dict so `qgea-i56i` is the canonical multi-year source; YTD is reserved for current-year only.


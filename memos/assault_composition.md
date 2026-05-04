# Felony Assault Composition: Where Is the 72% Rise Coming From?

**Question.** Is the multi-decade structural rise in NYC felony assault (`ofns_desc='FELONY ASSAULT'`, `ky_cd=106`) uniform across NYPD's internal sub-categorization (`pd_cd`/`pd_desc`), or concentrated in specific drivers?

**Source.** NYPD `qgea-i56i`, SoQL `GROUP BY (pd_cd, pd_desc)`, filtered to `law_cat_cd='FELONY' AND ofns_desc='FELONY ASSAULT'`, for years 2010 / 2014 / 2019 / 2024.

**Citywide totals (sanity check):** 2010 = 17,137 → 2014 = 20,254 → 2019 = 20,864 → 2024 = 29,501. Confirms the +72% headline (17,137 → 29,501) and the 1.41x post-2019 jump.

## Sub-category table

| pd_cd | pd_desc | 2010 | 2019 | 2024 | Share 2010 | Share 2019 | Share 2024 | Idx 2010=1 | Idx 2019=1 | Verdict |
|------:|---------|-----:|-----:|-----:|----:|----:|----:|----:|----:|---------|
| 109 | ASSAULT 2,1,UNCLASSIFIED | 15,140 | 15,596 | 21,981 | 88.4% | 74.7% | 74.5% | 1.45 | 1.41 | **Primary driver** of post-2019 surge (74% of 2019→2024 increase) |
| 105 | STRANGULATION 1ST | 146 | 3,411 | 4,546 | 0.9% | 16.4% | 15.4% | 31.14 | 1.33 | **New statutory category** — explains 36% of 2010→2024 increase but is *flat-share* post-2019 |
| 106 | ASSAULT POLICE/PEACE OFFICER | 1,851 | 1,526 | 2,502 | 10.8% | 7.3% | 8.5% | 1.35 | 1.64 | Stable long-run; meaningful post-2019 acceleration (+64%) |
| 108 | ASSAULT OTHER PUBLIC SERVICE EMPLOYEE | 0 | 268 | 418 | 0% | 1.3% | 1.4% | n/a | 1.56 | New category (post-2010); small absolute |
| 103 | ASSAULT TRAFFIC AGENT | 0 | 33 | 34 | 0% | 0.2% | 0.1% | n/a | 1.03 | New category; negligible |
| 102 | ASSAULT SCHOOL SAFETY AGENT | 0 | 30 | 20 | 0% | 0.1% | 0.1% | n/a | 0.67 | New category; declining |

## Bottom-line

**The rise is concentrated, not distributed — but the concentration story is different at different time horizons:**

- **2010 → 2024 (+12,364):** Two sub-categories explain 91% of the absolute increase: `ASSAULT 2,1,UNCLASSIFIED` (pd_cd 109, +6,841 / 55%) and `STRANGULATION 1ST` (pd_cd 105, +4,400 / 36%).
- **2019 → 2024 (+8,637):** The post-COVID surge is dominated by pd_cd 109 (74%), with strangulation contributing only 13% and assault-on-police 11%. Strangulation has plateaued; the recent acceleration is in the generic "Assault 2/1, Unclassified" bucket.

## Reclassification finding (CRITICAL — invalidates naive 2010→2024 trend)

**`STRANGULATION 1ST` (pd_cd 105) did not meaningfully exist in 2010.** Only 146 cases that year vs. 4,546 in 2024 — a 31x increase. This reflects **NY Penal Law § 121.11 / § 121.12**, the anti-strangulation statute signed November 2010 (effective immediately). 2010 captured only ~6 weeks of the new offense; by 2014 it had stabilized at ~2,400 cases/year. **Roughly 4,300 of the 12,364 absolute 2010→2024 increase (~35%) is statutory creation, not a behavioral rise.**

Three other sub-categories — `ASSAULT OTHER PUBLIC SERVICE EMPLOYEE` (108), `ASSAULT TRAFFIC AGENT` (103), `ASSAULT SCHOOL SAFETY AGENT` (102) — also have zero 2010 counts and first appear in NYPD's data between 2010 and 2019. Combined, however, they only contribute ~470 cases in 2024 (~1.6% of total), so they do not materially distort the headline.

**Adjusted growth rate excluding strangulation:** (29,501 − 4,546) − (17,137 − 146) = 24,955 − 16,991 = **+47% vs. the +72% headline.** Still a real structural rise, but a third smaller.

## Implication for policy targeting

The data does **not** support a single narrow intervention recommendation. The pre-COVID rise (2010-2019) was statutory: anti-strangulation enforcement appearing as new felony-assault volume. The post-2019 acceleration, by contrast, is overwhelmingly in pd_cd 109 — `ASSAULT 2,1,UNCLASSIFIED`, NYPD's catch-all bucket for second/first-degree assault not otherwise classified. This is a behavioral signal, but it is **not behaviorally specific**: pd_cd 109 spans intimate-partner, street, transit, and bystander assaults indistinguishably. A memo recommending "anti-strangulation enforcement" would be solving yesterday's already-counted problem; recommending "transit-assault programs" or any other narrow lane is unsupported by what we can see at this level of categorization. The defensible recommendation is a **broader assault-focused approach** (or a request for incident-level location and victim-relationship data to disaggregate pd_cd 109), not a single-driver intervention.

## Files

- Script: `scripts/pull_assault_subcategories.py`
- Aggregate data: `data/processed/aggregates/felony_assault_subcategory_yearly.parquet` (18 rows)

# Round 1 Research Findings

Research scope: eight specific factual / methodological questions raised by the
adversarial-review process. Each entry reports what independent sources (or
direct re-computation on the project's own aggregates) say, and ends with an
explicit confidence level and verdict.

## Q1 — DV-vs-non-DV split replicability

The 73% / 40% split is reproduced verbatim by Gothamist (Oct 2024) citing
"police data compiled by the state Division of Criminal Justice Services":
"the categories combined increased by 73% between 2017 and 2024" and "all
remaining felony assaults increased by 40%"
(https://gothamist.com/news/domestic-and-elder-abuse-fuel-rise-in-nyc-felony-assaults-data-shows).
Brennan Center's 2025 Trends in Crime and Safety in NYC independently reports
"40 percent of felony assaults entail violence between members of the same
household"
(https://www.brennancenter.org/our-work/research-reports/2025-trends-crime-and-safety-new-york-city).
The DCJS Domestic Violence Data series is the chained source — DCJS aggregates
NYPD DV-relationship coding annually
(https://www.criminaljustice.ny.gov/crimnet/ojsa/domestic-violence-data.html).

**The NYPD public dataset (qgea-i56i) cannot itself reproduce the split**:
schema inspection confirms no `vic_relationship`, `dom_violence_indicator`, or
similar field — only `vic_age_group`, `vic_race`, `vic_sex`. Reproduction
requires the DCJS feed which uses NYPD's internal DV-flag.

ENDGBV's 2024 Annual Report (Local Law 38) and Fact Sheet are the official
city venues for the same data; their press materials confirm DV-related felony
assault is rising but do not appear to have published the 73-vs-40 contrast in
that exact framing
(https://www.nyc.gov/site/ocdv/press-resources/annual-reports-and-fact-sheets.page).

**Confidence: high. Verdict:** the evidence would **support** the memo's
73%/40% factual claim (two independent secondary sources, anchored to the
DCJS NYPD-DV feed). However it would **not support** any claim that this can
be reproduced from the public NYPD complaint dataset alone — the relationship
field isn't there.

## Q2 — Other reclassification artifacts beyond strangulation

Three streams of reclassification credibly affect the 2010-2024 trend:

1. **Strangulation (PL §121.11/.12, eff. Nov 2010)**: the project's own
   subcategory pull shows pd_cd 105 went 146 (2010) → 4,546 (2024), netting
   ~4,400 of the +12,364 absolute increase (~35%) — already reflected in the
   memo's +47% adjusted figure.
2. **Public-service-employee assault subcategories (pd_cd 102, 103, 108)**:
   zero counts in 2010, 472 combined in 2024. Small (~4% of post-2010 increase)
   but real. Removing these would shave the +47% to roughly +44%.
3. **Expanded DV intake practices**: Vital City and Gothamist both cite NYPD
   training/intake changes since the mid-2010s as a contributor — officers now
   ask about loss-of-consciousness/bodily-control, increasing the rate at
   which strangulations and aggravated DV are charged at felony level
   (https://gothamist.com/news/domestic-and-elder-abuse-fuel-rise-in-nyc-felony-assaults-data-shows).
   No public document quantifies the marginal effect; it is bundled inside
   the strangulation rise. NYPD also stood up a dedicated DV Investigative
   Unit in October 2025
   (https://www.nyc.gov/mayors-office/news/2025/10/mayor-adams--nypd-commissioner-tisch-announce-largest-in-the-nat).

PL Article 120 amendments since 2010 include §120.19 (assault on retail
worker, 2024) — too recent to affect 2017-2024 — and tweaks to aggravated
assault on judges. None match strangulation in scale
(https://www.nysenate.gov/legislation/laws/PEN/P3THA120).

**Best estimate of fully reclassification-stripped residual: ~+40-45%**, vs
the memo's +47%. The strangulation adjustment captures the vast majority of
the artifact; further pruning is small.

**Confidence: medium. Verdict:** evidence would **support** the memo's
strangulation adjustment as the dominant reclassification correction.
**Inconclusive** about whether the residual is more like +40% or +47% —
quantifying intake-practice effects requires access to NYPD's internal DV
flag history that is not in the public dataset.

## Q3 — Cluster-solution robustness

Re-ran the 2017-2024 felony × year clustering on 16 offenses (matching
`cluster_assignments.csv`) using Ward linkage on row-z-scored 2017-indexed
trajectories.

| k | silhouette | sizes |
|--:|-----------:|-------|
| 2 | 0.377 | 10 / 6 |
| 3 | **0.438** | 10 / 3 / 3 |
| 4 | 0.425 | 10 / 3 / 2 / 1 |
| 5 | 0.307 | … |
| 6 | 0.288 | … |
| 7 | 0.300 | … |

k=3 is the global silhouette maximum and reproduces the memo's reported
value of ~0.44. By Kaufman-Rousseeuw this is in the "weak / could be
artificial" band (<0.5), as the memo concedes.

200-resample year-bootstrap (resample years with replacement, re-cluster):

- All Surge-cluster offenses retain ≥75% co-assignment with their original
  cluster mates.
- GRAND LARCENY co-clusters with FELONY ASSAULT in **80%** of bootstrap
  resamples; ROBBERY co-clusters with FELONY ASSAULT in **90%**; GLA and
  ROBBERY co-cluster together in **90%**.
- Most-unstable offenses are ARSON (0.59) and BURGLARY/MURDER cluster (~0.76).

This **contradicts** one part of the memo's framing: the precovid baseline
analysis labels GLA and ROBBERY as "COVID-rebound" rather than structural —
but the clustering on the 2017-2024 trajectory consistently and stably
groups them with FELONY ASSAULT in the Surge cluster. The two analyses are
measuring different things (post-2020 inflection vs. 2010-2019 baseline
trajectory), and the Surge cluster is partly mixing the two.

**Confidence: high. Verdict:** evidence would **support** the structural
robustness of the 3-cluster k=3 solution at this silhouette band, but
would **partially refute** the cleanness of the Surge cluster: GLA and
ROBBERY are statistically Surge by 2017-trajectory shape yet pre-COVID
data classifies them as rebounds, not structural rises. The cluster is
robust as a partition; its semantic label "Surge" is not robust to
pre-2017 context.

## Q4 — CVI-for-DV precedent

**Direct precedent for CVI-style credible-messenger work on DV:** none I can
locate in published evaluation form. Cure Violence Global lists the model
in 50+ sites in 25 cities/10 countries
(https://cvg.org/what-we-do/) — all targeting community / gun violence, not DV.

**Closest analog: focused deterrence (High Point, NC).** Sechrist & Weil's
evaluation of the Offender-Focused Domestic Violence Initiative reports
~20% reduction in IPDV calls and arrests, 1-year recidivism ~16-17%,
and a substantial fall in intimate-partner homicide
(https://pubmed.ncbi.nlm.nih.gov/29332533/,
https://nnscommunities.org/strategies/intimate-partner-violence-intervention/).
This is structurally closer to focused-deterrence (call-ins, sanctions
ladder) than to CMS/Cure Violence (street outreach + interrupters).

**Evidence-quality ranking for DV recidivism reduction (criminology consensus):**

1. **Lethality Assessment Programs (LAP)**: 35-45% reduction in female
   homicide victimization (Maryland), reduces severity and frequency of
   IPV; CDC-rated "supported intervention"
   (https://nij.ojp.gov/topics/articles/how-effective-are-lethality-assessment-programs-addressing-intimate-partner).
2. **Mandatory-arrest policies (Sherman & Berk, Minneapolis MDVE)**: arrest
   showed 13% repeat-assault vs 26% separation; replications in 5 cities
   later produced mixed results (arrest sometimes increased recidivism for
   unemployed offenders), so the consensus is "evidence-based but
   contingent" (https://en.wikipedia.org/wiki/Minneapolis_Domestic_Violence_Experiment).
3. **Focused deterrence for IPV (High Point OFDVI)**: ~20% reductions,
   replicated in Sweden (Malmö SRFV)
   (https://www.scup.com/doi/10.18261/njsp.12.2.2).
4. **Batterer-intervention programs (Duluth/CBT)**: small/null effects in
   true experiments; significant only in quasi-experimental work; Cheng
   et al. 2021 meta-analysis finds non-significant overall effect
   (https://pubmed.ncbi.nlm.nih.gov/31359840/).
5. **CVI/credible-messenger for DV**: untested at evaluation level.

**Confidence: high. Verdict:** evidence would **refute** the proposition
that porting CMS architecture to DV is the strongest-evidence move. LAP
and focused-deterrence both have substantially better-tested effect sizes
on DV outcomes specifically. CMS-for-DV would be a research bet, not an
evidence-based deployment.

## Q5 — CMS unit-cost variation

Comptroller Levine's 2024 "The Cure for Crisis" evaluation of CMS does NOT
break out per-precinct or per-site cost. It provides aggregate budget
trajectory ($4.8M FY first year → ~$100M FY25), agency-level distribution,
and a 24-vendor cumulative-payments table — vendors range from
~$63M / 3 yrs (Justice Innovation) to ~$8K / 1 yr (Wheelchairs Against
Guns), implying enormous variation but not by precinct
(https://comptroller.nyc.gov/reports/the-cure-for-crisis/).

NYC Council Data Team reports an average of ~$1.7M per CVI contract over
FY16-25 across 112 contracts ($192M total), and the 2025 Finance Committee
hearing referenced standalone-school site funding at $93K and campus
funding at $135K — both below the ~$3M/precinct average implied by
$86M / 29 sites
(https://council.nyc.gov/data/cure/,
https://citymeetings.nyc/meetings/new-york-city-council/2025-05-19-1000-am-committee-on-finance/chapter/council-member-stevens-questions-dycd-on-cure-violence-program-and-legal-services-funding/).

The $3M/precinct average bundles a violence-interrupter team, hospital-based
component, employment service component, and wraparound from up to 9 city
agencies. Per-component cost data is not public.

**Confidence: medium. Verdict:** evidence is **inconclusive** about whether
$3M/precinct is the right unit cost for budgeting a DV-CMS. The $86M / 29
arithmetic is correct on paper but conceals heterogeneous bundling. Marginal
unit cost is plausibly lower than average (because of fixed central-services
overhead), but no public document quantifies fixed-vs-variable. The memo's
$40-60M figure should be flagged as ±50% uncertain.

## Q6 — B-HEARD 35% unserved-eligible cause

Subsequent reporting and the audit's own appendix isolate **multiple
co-causes**, with a clear primary one:

- **Primary: hours-of-operation gap.** Of 13,042 unserved eligible calls,
  "over 14,000 calls determined to be eligible" came in during the overnight
  hours when the program does not operate (1am-9am). This number actually
  exceeds the total unserved gap, indicating eligibility coding was inclusive
  of overnight calls that B-HEARD never had a chance to reach.
- **Secondary: capacity.** Only 9 of 18 teams operate per shift; teams declined
  ~18% of routed calls due to unavailability per pre-audit reporting from
  THE CITY (https://www.thecity.nyc/2022/7/18/23267193/mental-health-911-b-heard-teams).
- **Tertiary: routing/protocol.** Only ~22% of mental-health 911 calls were
  routed to B-HEARD even within pilot precincts in the early period
  (CityandStateNY, https://www.cityandstateny.com/policy/2022/04/what-know-about-nycs-b-heard-mental-health-crisis-response-teams/366286/).
- **Refusal at scene:** the audit notes this exists but is unquantified; OCMH
  doesn't track it
  (https://comptroller.nyc.gov/newsroom/new-audit-comptroller-finds-over-a-third-of-eligible-mental-health-calls-did-not-get-a-b-heard-team-response-for-untracked-reasons/).

**Confidence: high. Verdict:** evidence would **support** characterizing the
35% gap as **primarily a supply problem (operating hours + team capacity)**,
secondarily a routing problem, with refusal a small unquantified residual.
This has cost implications: closing the gap mostly requires more teams /
24-hour operations, not protocol fixes — i.e. the marginal cost is real, not
zero.

## Q7 — Has the structural assault rise been named in NYC institutional reporting?

The "invisible" claim is partially refuted by independent journalism and
non-government think-tank work, but largely intact within NYC's official
institutional channels.

**Named publicly (non-NYC-government):**
- Vital City has repeatedly quantified the rise (e.g. "felony assaults rose
  for the sixth year in a row, now reaching a level not seen since 1997";
  "total felony assault counts have risen 84% since 2008")
  (https://vitalcitynyc.org/articles/crime-in-new-york-city-trends-statistics).
- Brennan Center 2025 Trends notes the frequency "began rising as far back
  as 2010"
  (https://www.brennancenter.org/our-work/research-reports/2025-trends-crime-and-safety-new-york-city).
- Gothamist (Oct 2024) names the 2017-2024 rise.

**Within NYC government:** the Mayor / NYPD year-end announcements (2024,
2025) acknowledge felony assault rose but frame it short-window (vs. 2023 or
vs. 2019), not as a 14-year structural rise. NYPD's year-end 2024 enforcement
report quantifies the recent change; it does not characterize it as a 2010+
structural shift
(https://www.nyc.gov/assets/nypd/downloads/pdf/analysis_and_planning/year-end-2024-enforcement-report.pdf).
ENDGBV / OCDV materials emphasize DV-specific framings, not the citywide
felony-assault total.

The most quantitative NYC-government acknowledgment located is NYPD
Commissioner Tisch's 2025 City Council appearance (recent oversight) and
mayoral pressers, both of which discuss recent-year increases and DV/police
assault drivers, but not the 14-year structural framing
(https://abc7ny.com/post/nypd-commissioner-jessica-tisch-faces-city-council-nycs-crime-rate-is-trending-bronx/18731712/).

**Confidence: medium. Verdict:** evidence would **partially refute** the
strong form of the memo's "invisible in NYC's institutional reporting" claim
— Vital City and Brennan Center are not NYC government but ARE NYC-focused
institutional reporting, and they have named the rise back to 2010 in
quantified form. **Supports** the narrower form: no NYC government
publication has quantified the 14-year structural rise as such; their
framings are short-window (vs prior year / vs 2019) rather than
2010-anchored.

## Q8 — Hot-spots policing for DV / household assault

Braga's Campbell meta-analyses (2012 and 2019/updated 2024) report ~29%
assault reduction overall but **do not decompose by setting (street vs
household)**. Where DV is mentioned at all in the included RCT pool, it is
typically excluded from the outcome measure
(e.g. one study measured "street violence (non-domestic violence) from 2006
through May 2008")
(https://onlinelibrary.wiley.com/doi/10.4073/csr.2012.8,
https://www.sciencedirect.com/science/article/abs/pii/S1359178924001010).

A 2024 longitudinal place-based study of "domestic abuse hot spots" in
Oxford UK explicitly questions whether the place-as-driver assumption that
underwrites hot-spots theory translates to DV: "the assumption that place
characteristics drive crime works differently for domestic abuse compared
to street crimes"
(https://academic.oup.com/policing/article/doi/10.1093/police/paae056/7739691).

The Hamilton County Sheriff's "Smart Policing" RCT did include "domestic
trouble" calls in the outcome basket and saw 23-28% reductions — but this is
a single quasi-experimental study, not the Braga effect itself
(https://pmc.ncbi.nlm.nih.gov/articles/PMC9638250/).

The Sherman/Berk Minneapolis tradition (mandatory-arrest replications) is the
canonical DV place/incident-based experimental literature; it is not what
"hot-spots policing" typically refers to.

**Confidence: high. Verdict:** evidence would **refute** generalizing Braga's
29% assault effect to DV/household assault. The meta-analytic effect comes
from street and firearm-violence place-based interventions; DV-as-outcome is
either excluded or treated as a separate research stream. Hot-spots policing
**has not been rigorously tested against DV/household assault as the primary
outcome**, so the memo's #1 evidence ranking does not transfer to the
DV-targeted recommendation.

## Files referenced in this research

Project files: `/home/zkuzma8/claude_code/nyc-strategy-artifact/data/processed/aggregates/felony_yearly.parquet`,
`felony_yearly_precovid.parquet`, `felony_assault_subcategory_yearly.parquet`,
`cluster_assignments.csv`, `cluster_summary.csv`.

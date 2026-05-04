# Round 2 Research Findings

Methodological deep-dive on eight questions raised by the round-2 peer-review
critiques. Each entry reports what published sources or direct re-computation
on the project's own aggregates show, then states confidence and verdict.
This memo does not advocate; it audits.

## Q1 — LAP identification strategy and CI

The "35–45% reduction in female homicide victimization (Maryland)" figure does
**not** come from Messing et al. It comes from Vijetha Koppa, "Can information
save lives? Effect of a victim-focused police intervention on intimate partner
homicides," *Journal of Economic Behavior & Organization* 217 (2024) 756–782
(https://www.sciencedirect.com/science/article/abs/pii/S0167268123004018,
SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2982227).

**Identification.** Staggered difference-in-differences exploiting the rolling
2005–2012 adoption of LAP across Maryland law-enforcement agencies. Not an RCT
and not a synthetic control.

**Effect size and CI.** ~2.5–3 fewer female-by-male homicides per 1M
population per year, ~37–44% reduction; effect concentrated on girlfriend
victims. The "35–45%" memo phrasing is a slightly widened paraphrase of
Koppa's 37–44% range. Published abstracts and summaries cite point estimates;
formal 95% CI bounds are not in publicly indexed abstracts and would require
the full PDF.

**Endpoint.** Jurisdiction-level female-IPH RATE per 1M population — not
per-participant homicide-victimization risk reduction.

**Messing et al. (2015 Oklahoma) is a different study**, rated **Promising**
(not "Effective" or "Supported") on CrimeSolutions
(https://crimesolutions.ojp.gov/ratedprograms/lethality-assessment-program-oklahoma).
It reports reduced violence severity / increased protective actions in 414
women across 7 jurisdictions via propensity-matched quasi-experiment — no
homicide endpoint. The CrimeSolutions rating tiers are **Effective /
Promising / No Effects** (https://crimesolutions.ojp.gov/about/glossary?ID=68),
not "Supported"; the memo's "CDC-rated 'supported intervention'" phrasing
does not map to a current CrimeSolutions or Campbell tier.

**Confidence: high. Verdict:** evidence would **partially refute** the memo's
attribution. The 35-45% figure is real but is from Koppa's staggered-DiD
study (not Messing), measures jurisdiction-level rates (not per-participant),
and the cited rating term ("supported") does not match the actual
CrimeSolutions tier ("Promising," based on the Oklahoma study, no homicide
endpoint).

## Q2 — OFDVI identification rigor

Sechrist & Weil's High Point/Lexington OFDVI evaluation (Sechrist, Weil,
Shelton, COPS final report 2016; published version Sechrist & Weil 2018,
*Journal of Interpersonal Violence*,
https://pubmed.ncbi.nlm.nih.gov/29332533/) used a **single-jurisdiction
pre/post interrupted time-series** comparing IPDV calls and arrests before
vs. after OFDVI implementation, with quarterly slopes/intercepts within
High Point and Lexington
(https://ncnsc.uncg.edu/wp-content/uploads/2013/11/COPS-OFDVI-Lexington-High-Point-Evaluation-FINAL.pdf).

**No matched-jurisdiction comparison group, no DiD, no synthetic control,
and no contemporaneous national/state IPV trend was used as a counterfactual.**
The 20% reduction is therefore exposed to confounding by national IPV
decline, agency reporting changes, and regression-to-the-mean
(adopting jurisdictions are typically high-IPV-incidence sites).

The Malmö/SRFV "replication" is a separate quasi-experimental
implementation study launched in 2021
(https://www.scup.com/doi/10.18261/njsp.12.2.2). Published findings to
date are implementation-feasibility, not confirmed effect-size replication.
The Malmö program is **not statistically independent** in any meaningful
sense — it imports the same NNSC-designed intervention model and was
selected partly because High Point's results suggested it would work; it
shares moderator structure (focused-deterrence call-ins) with the High
Point original.

Braga & Weisburd's 2019 Campbell systematic review of focused deterrence
(https://onlinelibrary.wiley.com/doi/full/10.1002/cl2.1051) finds that
nonequivalent quasi-experimental designs report effect sizes ~3.6× larger
(0.703) than matched quasi-experimental designs (0.194). High Point falls
in the weaker design category.

**Confidence: high. Verdict:** evidence would **support** the critique
that the 20% effect comes from a single-site pre/post study with no
counterfactual, and that the Malmö "replication" is not statistically
independent.

## Q3 — CMS / Cure Violence identification

**Comptroller Lander 2024 ("The Cure for Crisis").** Identification is
two-way fixed-effects difference-in-differences with staggered treatment
adoption (Callaway & Sant'Anna estimator), at both CVI service-area
(2,242 area-years) and precinct (1,463 precinct-years) levels
(https://comptroller.nyc.gov/reports/the-cure-for-crisis/).
Pre-trend tests: yes — visual parallel-trends comparison, normalizing
treated and untreated precincts to first treatment year; the report
states the parallel-trend assumption was "tested" by visual inspection,
which is weaker than formal placebo or event-study leads-and-lags
testing. The 21% point estimate (-7.4 shootings/precinct/year, from a
counterfactual baseline of ~35) at precinct level has a 95% CI of
roughly **-2.6 to -12.2 shootings**, i.e. the lower bound is ~7%
reduction and upper bound is ~35%. Service-area estimates are not
statistically significant due to small per-area shooting counts (median
4/year). **No published sensitivity analysis to alternative comparator
selection is reported.**

**John Jay REC 2017 (S. Bronx + East NY).** Quasi-experimental
matched-comparison design pairing two CVI sites to two demographically
similar non-CVI neighborhoods (Flatbush, East Harlem). Reports 37%
gun-injury reduction (S. Bronx / SOS) and 50% (East NY / Man Up Alpha)
vs. matched comparators, plus norms-change measures
(https://johnjayrec.nyc/2017/10/02/cvinsobronxeastny/,
https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1436&context=jj_pubs).
Two-site matched comparison; not a synthetic control.

**Confidence: high. Verdict:** evidence would **partially support** the
critique. The 21% figure rests on a real DiD with parallel-trend testing
(non-trivial identification) but with only visual pre-trend inspection
and no formal comparator-sensitivity analysis. The John Jay 37–50% figures
are matched two-comparator quasi-experiment, weaker than synthetic
control. Calling CMS "proven" while ranking other quasi-experiments as
"untested" is the asymmetry the critique flags.

## Q4 — Transportability literature on focused-deterrence and DV

**(a) Does a 100K-population mid-South city's effect transport to an 8M
multi-DA jurisdiction?** The transportability literature (Tipton 2014;
Stuart-Cole; Olsen-Bell-Orr-Stuart 2016) treats moderator-mismatch as the
typical reason effects attenuate, often substantially. Tipton's
generalizability index, based on the Bhattacharyya coefficient of
covariate-overlap densities, ranks 0.50–0.80 as "medium"
generalization and <0.50 as "low," with explicit warnings that
out-of-support extrapolation is unreliable
(https://journals.sagepub.com/doi/10.3102/1076998614558486).

**(b) Empirical record of attenuation.** Braga & Weisburd 2019 Campbell
review of focused deterrence
(https://onlinelibrary.wiley.com/doi/full/10.1002/cl2.1051) shows
matched-design effects ~28% the size of non-matched-design effects
(0.194 vs 0.703). The Cure Violence systematic review
(https://pmc.ncbi.nlm.nih.gov/articles/PMC12420962/) finds 68.7% of
findings show shooting reductions but only 32.5% are statistically
significant; Baltimore showed mixed/null at multiple sites. Boston
Operation Ceasefire replications in Baltimore and Minneapolis
documented implementation collapse rather than effect transport
(https://cwinship.scholars.harvard.edu/file_url/209). Bell-Olsen-Orr-Stuart
2016 estimate that purposive site selection in education trials introduces
~0.10 SD downward bias on the population average treatment effect.

**(c) Quantified moderator-mismatch attenuation guidance.** No published
framework offers a numerical "attenuation factor" specific to LAP→NYC
or High-Point-OFDVI→NYC ports. Tipton/Stuart provide the diagnostic
machinery (overlap index, weighted estimators) but require source-study
covariate data not present in the Maryland LAP or High Point OFDVI
publications.

**Confidence: high. Verdict:** evidence would **support** the critique.
The transportability literature treats moderator-mismatch attenuation as
the prior, not the exception; the empirical record in focused-deterrence
specifically shows ~3–4× design-quality attenuation and substantial
implementation-failure risk in larger replications.

## Q5 — Denominators of cited effect sizes

- **LAP "35-45%":** Koppa 2024 reports ~37–44% reduction in
  *jurisdiction-level female-IPH rate per 1M population* (≈2.5–3
  fewer homicides per 1M/yr) under staggered DiD across Maryland
  agencies. **Not** per-program-participant risk reduction.

- **OFDVI "20%":** Sechrist & Weil report ~20% reduction in
  *citywide IPDV calls and arrests in High Point*, single-jurisdiction
  pre/post (no comparator), not program-eligible-offender-only
  recidivism, not target-area-only call rates
  (https://pubmed.ncbi.nlm.nih.gov/29332533/).

- **CMS "21%":** Comptroller Lander 2024: average reduction of 7.4
  shootings per CVI-treated precinct per year vs. counterfactual
  baseline of ~35, in the *precinct-level DiD model*; 95% CI roughly
  -2.6 to -12.2 shootings; service-area estimate is not significant.
  Treatment area only — not citywide rate change
  (https://comptroller.nyc.gov/reports/the-cure-for-crisis/).

- **B-HEARD "35%":** denominator is *eligible calls in pilot precincts
  during 9am–1am operating hours*, FY22-24 (37,113 eligible total,
  13,042 unserved). 14,200 *additional* overnight (1am–9am) eligible
  calls fall outside the 35% calculation
  (https://comptroller.nyc.gov/newsroom/new-audit-comptroller-finds-over-a-third-of-eligible-mental-health-calls-did-not-get-a-b-heard-team-response-for-untracked-reasons/).

**Citywide projection.** NYC has ~29,500 annual felony assaults; ~40%
DV-coded ≈ 11,800. Maryland LAP rate-effect projection requires
identical IPH→felony-assault co-trend, which is not established. OFDVI's
20% applies to call rates in a 100K-population focused-deterrence
intervention universe; arithmetically scaling to NYC's ~5M-adult
population assumes equal moderator structure. Each effect-size's
implied citywide projection is undefined without scope assumptions
the source studies do not license.

**Confidence: high. Verdict:** evidence would **support** the critique
that none of the four cited effect sizes share a denominator structure
and that face-value citywide projection is arithmetically undefined.

## Q6 — Asymmetric-standards defense

The transportability literature does **not** have a generally accepted
ranking of "cross-outcome-class is smaller than cross-jurisdiction" or
vice versa. The framework instead asks whether the moderators driving
the source effect (mechanism) are present in the target setting
(Tipton-Olsen 2018, https://journals.sagepub.com/doi/10.3102/0013189X18781522;
Degtiar & Rose 2023 review,
https://www.annualreviews.org/content/journals/10.1146/annurev-statistics-042522-103837).

**The relevant question is mechanism preservation.** For LAP→NYC:
mechanism = first-responder risk-screening + warm handoff to advocate;
moderators include officer training, advocate capacity, victim
help-seeking culture. For CMS→DV: mechanism = credible messengers
interrupting retaliation; moderators include retaliation cycle
(arguably weaker in DV than gang violence), street-presence access
to perpetrator, peer-network structure. The mechanism for CMS-shooting
arguably is *not* preserved when ported to DV (DV typically occurs
inside private residences with intimate-partner dyads, not on streets
in retaliating peer networks); the mechanism for LAP-Maryland *is*
preserved when ported to NYC at the operational level (police +
hotline advocate exists).

This is what the literature calls a **mechanism-overlap** rather than
"distance" question. Bell-Olsen 2016 and Stuart 2017 frame it as: which
moderators differ, and which of those moderate the treatment effect?
Neither cross-outcome nor cross-jurisdiction has a universal advantage.

**Confidence: medium. Verdict:** **inconclusive.** No published
framework rank-orders "cross-outcome generalization" vs.
"cross-jurisdiction generalization" as the smaller bet. The choice is
case-specific and must be argued from mechanism-overlap, not asserted.
The memo's asymmetric standard is defensible by mechanism-overlap
reasoning but has not been argued there.

## Q7 — B-HEARD denominator reconciliation

The Comptroller's audit
(https://comptroller.nyc.gov/reports/audit-of-the-behavioral-health-emergency-assistance-response-divisions-effectiveness-in-responding-to-individuals-with-mental-health-crises-and-meeting-its-goals/)
reports three numbers using the same eligibility coding but with
overlapping/non-mutually-exclusive scope:

- 96,291 mental-health calls in pilot precincts FY22-24
- 59,178 ineligible (potentially dangerous, MH professional on scene,
  triage-incomplete) → 37,113 eligible
- 24,071 of the 37,113 eligible received B-HEARD dispatch (65%)
- 13,042 (35%) eligible did not receive dispatch — "no reason
  provided"
- **Additionally**, 14,200 calls were "determined to be eligible"
  during the 1am–9am overnight hours **outside** the 9am–1am
  operating window

The audit's phrasing — "in addition" to the 13,042 — strongly suggests
the 14,200 overnight figure is **not in** the 37,113 in-hours eligible
denominator; rather, it is a separate count of calls that *would have
been* eligible had the program been operating. The comptroller's
office has not published a fully reconciled accounting; FDNY/H+H/MOCMH
have not issued a public reconciliation either.

If the audit's "in addition" reading is correct, the **35% gap is not
overnight-driven**. The 13,042 in-hours unserved-eligible gap and the
14,200 overnight-would-be-eligible figure are distinct. Decomposition
of the in-hours 13,042 across capacity-decline, routing-failure, and
refusal is **not in the audit's published data** because OCMH does
not track reasons.

**Confidence: medium. Verdict:** **inconclusive** about full
supply-vs-routing decomposition because reasons are untracked. **Partially
refutes** R1's framing that overnight is the primary in-hours driver:
the 14,200 overnight count is plausibly a separate denominator, not
overlapping with the in-hours 13,042. R1's claim that "overnight count
exceeds the unserved gap" was true arithmetically but may have used
non-comparable scopes.

## Q8 — Leave-one-offense-out clustering robustness

Re-ran the Ward-linkage clustering on z-scored 2019-indexed felony
trajectories using `data/processed/aggregates/felony_yearly.parquet`,
dropping each of the 16 offenses one at a time and sweeping k=2..7.
Script at `/tmp/leave_one_out_cluster.py`.

**Results:**

- **Best k = 3 in 16/16 leave-one-out runs** (no flip to k=2, k=4,
  or larger).
- **Silhouette range across LOO runs (at best k):** 0.402 – 0.470;
  baseline (full 16) = 0.438. Lowest silhouette occurs when SEX CRIMES
  is dropped (0.402); highest when RAPE is dropped (0.470). All values
  remain in the Kaufman-Rousseeuw "weak / could be artificial" band
  (<0.5) but are tightly clustered around 0.43–0.45.
- **FELONY ASSAULT, CRIMINAL MISCHIEF & RELATED OF, and MISCELLANEOUS
  PENAL LAW** remain co-clustered at k=3 in **13/13** non-trio
  drops. (The three runs that drop one trio member trivially preserve
  co-clustering of the remaining two.)

The k=3 silhouette = 0.44 / Surge-cluster trio is fully robust to
single-offense removal.

**Confidence: high. Verdict:** evidence would **support** the
robustness claim. The cluster solution survives the most directly
relevant perturbation (offense-set sensitivity); k=3 is preserved
unanimously and the trio's co-clustering is unanimous across all runs
where the trio members are still present. Silhouette band remains
"weak" per Kaufman-Rousseeuw — that is a property of the underlying
trend geometry, not an artifact of any single offense.

## Files referenced

Project files: `/home/zkuzma8/claude_code/nyc-strategy-artifact/data/processed/aggregates/felony_yearly.parquet`,
`/home/zkuzma8/claude_code/nyc-strategy-artifact/data/processed/aggregates/cluster_assignments.csv`,
`/home/zkuzma8/claude_code/nyc-strategy-artifact/scripts/cluster_offenses.py`.
LOO script: `/tmp/leave_one_out_cluster.py`.

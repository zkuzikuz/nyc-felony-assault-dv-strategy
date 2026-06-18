# External Adversarial Review — "NYC has a sustained, domestic-violence-driven assault crisis"

**Reviewer role:** Independent, hostile-but-fair fact-checker. No access to the project's internal critique logs. Findings below are formed from the published article (`site/index.html`), its cited supporting memo (`memos/phase0_evidence.md`), and live web verification of the underlying sources.

**One-line bottom line up front:** The *qualitative* thesis (felony assault is rising, DV is a big part of it, the city's reporting framing obscures it, and prevention spending hasn't grown in real terms) largely survives. But several of the *specific load-bearing numbers* that give the piece its punch are wrong, stale, or applied to the wrong year — most damagingly the DV split (the headline "73% DV growth" could not be found on the cited page, and the "39% / ~11,500 of 29,501" is a 2025 figure mis-stitched onto 2024 data), the Bridge-to-Home "2,000-person target / covers ~5%" claim (the real plan is 1,000 beds, and the article contradicts itself), and a cluster of mis-cited program studies. None of these individually kills the thesis, but together they show the artifact's numeric precision is less trustworthy than its confident tone implies.

---

## 1. Thesis & claim map

**Top-line thesis:** "NYC has a sustained, domestic-violence-driven felony-assault crisis, and the city's response is not scaling to meet it."

This rests on a Minto-style pyramid. I separate load-bearing claims (thesis collapses or substantially weakens if false) from supporting claims (decorative or redundant).

### Load-bearing claims
| # | Claim | Why load-bearing |
|---|---|---|
| L1 | Felony assault is genuinely rising in NYC over the long run (~+47% behavioral, 2010-2024, after stripping strangulation reclassification). | The "crisis" exists only if the rise is real, not an artifact. |
| L2 | **DV is the dominant driver** — "~73% DV growth 2017-2024" and "~39% same-household, ~11,500 of 29,501." | The word "domestic-violence-driven" in the title lives or dies here. This is the single most load-bearing claim. |
| L3 | The rise is NYC-specific, not a national trend (national rate flat; CCJ 24-city ~+4%; peers falling). | "Crisis" framing needs NYC to be an outlier, else it's just national drift. |
| L4 | Real DV-prevention spending is flat while cases rose ~73%, so real spend per case fell ~42%. | The "response not scaling" half of the thesis. |
| L5 | The recommended levers (housing / B-HEARD / LAP+OFDVI) actually have the evidence the article claims. | The "what to do" payload; a strategy memo that recommends the wrong things fails even if the diagnosis is right. |

### Supporting / decorative claims
- Felony assault is NYC's largest violent-felony category (true, not really contested).
- The rise is broadly distributed (76/78 precincts) → justifies a categorical not hot-spots lever.
- Reporting-cadence point (Oct 2024 −1.9% vs full-year +5.8%) — rhetorically nice, low stakes.
- Cost/savings ranges ($6-15M pilot, $5-35M/yr savings) — the article itself disclaims these as "illustrative," so they are not load-bearing and I won't attack them hard.
- Mental-health bed loss (Manhattan Institute / OSC) — context for Lever 1, not core.

---

## 2. Source fact-check table

Verdicts: **VERIFIED** / **PARTIALLY-SUPPORTED** / **MISREPRESENTED** / **UNVERIFIABLE** / **FABRICATED**.

| Claim (article's exact number) | Verdict | Source URL(s) checked | Note |
|---|---|---|---|
| 2024 felony assault **29,501**; robbery 16,567; rape **1,534**; murder **363**; GL 47,808 | **MISREPRESENTED** | [Tisch/Adams Jan-2025 transcript](https://www.nyc.gov/mayors-office/news/2025/01/transcript-mayor-adams-nypd-commissioner-tisch-crime-down-2024); [NYPD pr001](https://www.nyc.gov/site/nypd/news/pr001/crime-down-across-new-york-city-2024-3-662-fewer-crimes) | Official 2024 **murder = 377** (article says 363 — undercounts ~4%). Rape ≈ **1,742** (article 1,534 — undercounts ~13%). Felony assault/robbery/GL are within ~1% but none match exactly. The article's headline 29,501 does not reconcile to any official 2024 series I could find. |
| **DV-related felony assault +73% (2017-2024)** | **UNVERIFIABLE / likely MISATTRIBUTED** | [Vital City](https://vitalcitynyc.org/articles/crime-in-new-york-city-trends-statistics); [Gothamist](https://gothamist.com/news/domestic-and-elder-abuse-fuel-rise-in-nyc-felony-assaults-data-shows) | The 73% could **not be located on the cited Vital City page** at review time. Gothamist's 73% is for **"domestic AND elderly assaults combined,"** not DV alone. Attributing a combined figure to "DV-related felony assault" overstates DV's specific share. |
| **~39% same-household / ~11,500 of 29,501** | **MISREPRESENTED (year + denominator)** | [Vital City](https://vitalcitynyc.org/articles/crime-in-new-york-city-trends-statistics) | Vital City says: *"In 2025, 39% of felony assaults were classified as domestic violence"* — and its felony-assault count is **29,841 (2025), murders 309** — i.e. the 39% is a **2025** statistic. The article applies it to **2024 (29,501)** and computes 11,500. "Same household" is also the author's gloss; the source category is "domestic violence" (family OR household, incl. intimate partners). The ~11,500 raw count is the author's arithmetic (0.39 × wrong base), not a figure any source states. |
| National aggravated-assault **rate** ~flat: 252/100k (2010) → 256/100k (2024) | **VERIFIED (numbers) but apples-to-oranges framing** | [FBI UCR 2010](https://ucr.fbi.gov/crime-in-the-u.s/2010/crime-in-the-u.s.-2010/violent-crime/aggravatedassaultmain); [FBI 2024 release](https://www.fbi.gov/news/press-releases/fbi-releases-2024-reported-crimes-in-the-nation-statistics) | Rate figures correct (252.3 / 256.1). **But the article pits NYC's +47% in COUNTS against a national RATE.** NYC's population grew 2010-2024, so NYC's *rate* growth is smaller than its count growth. The comparison is rhetorically loaded. |
| CCJ 24-city: **+4% since 2019; −4% YoY in 2024** | **VERIFIED** | [CCJ Year-End 2024](https://counciloncj.org/crime-trends-in-u-s-cities-year-end-2024-update/) | Both figures are for aggravated assault specifically. Baseline-choice caveat: "since 2019" is the post-COVID window; a 2010 baseline (used for NYC) is not available for CCJ, so the two benchmarks aren't on the same clock. |
| LA **~10%** YoY decline 2024 | **PARTIALLY-SUPPORTED** | [LAPD/Mayor 2024 EOY](https://mayor.lacity.gov/news/lapd-releases-2024-end-year-crime-statistics-city-los-angeles) | Aggravated assault fell ~11.8%; overall violent crime ~8.5%. "~10%" splits the difference; mildly fuzzy, not wrong. |
| NIBRS DV share **25.6% (2020) → 27.5% (2024)** | **VERIFIED** | [FBI CDE Domestic Relationships report](https://cde.ucr.cjis.gov/LATEST/resources/reports/Domestic%20Relationships%20and%20Violent%20Crimes%202020-2024.pdf) | Exact match. |
| HRA "DV Services" **FY17 $131.5M → FY24 $168.5M (~28% nominal)** | **VERIFIED** | [Council FY18 prelim HRA](http://council.nyc.gov/budget/wp-content/uploads/sites/54/2017/03/069-HRA.pdf); [Council FY25 plan HRA](https://council.nyc.gov/budget/wp-content/uploads/sites/54/2024/05/HRA-.pdf) | FY17 Adopted = $131,523K; FY24 Adopted = $168,494K. Exact. |
| CPI-U **~28%** FY17→FY24 → real spend flat | **VERIFIED** | BLS CPI-U (245.120 → 313.689) | +28.0%. Real spending ≈ flat. Solid. |
| Real spend per DV case **−42%** | **VERIFIED arithmetic, but COMPOUNDED** | derived | 1/1.73 − 1 = −42.2%. Correct *if* both inputs hold. It inherits all the risk of the contested 73% (see L2). |
| Council requested **$4.8M (FY24) / $8.3M (FY26)**, each zeroed | **VERIFIED** | [Council 2025-05-16 release](https://council.nyc.gov/press/2025/05/16/2872/) | $4.8M microgrants + $2M legal + $1.5M HOME+ = $8.3M, all unfunded in Exec Budget. Accurate. |
| Women's Agenda **$43M**; survivor-alarms **$186K** | **PARTIALLY-SUPPORTED ($43M) / UNVERIFIABLE ($186K)** | [069-24 release](https://www.nyc.gov/office-of-the-mayor/news/069-24/...) | $43M confirmed. **$186K alarm figure not found in any official source** — should be cut or sourced. |
| NYC FY26 **$4.22B** projected gap | **VERIFIED** | Comptroller Comments on FY2026 Adopted Budget | $4.22B baseline gap. Exact. |
| **Koppa 2024 LAP, JEBO 217:756-782, 35-45%** | **VERIFIED** | [IDEAS/RePEc](https://ideas.repec.org/a/eee/jeborg/v217y2024icp756-782.html); [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167268123004018) | Title/journal/vol/pages/state/design/effect all correct. **Undisclosed caveat:** IPH is a rare event; 35-45% relative rests on a small absolute homicide count, and the author leans on a "back-of-envelope" estimate. Article should surface this. |
| CrimeSolutions rates LAP "Promising" **at ID 345** | **MISREPRESENTED (wrong link)** | [ID 345 = Reconnecting Youth, *Negative*](https://crimesolutions.ojp.gov/ratedprograms/345); [ID 495 = LAP, Promising](https://crimesolutions.ojp.gov/ratedprograms/495) | The *rating* is right; the *URL/ID is wrong* and points to a different (negative-effect) program. Embarrassing on click-through. |
| Sechrist & Weil 2018 OFDVI **~20%** | **VERIFIED** | [PubMed 29332533](https://pubmed.ncbi.nlm.nih.gov/29332533/) | "20% reductions each in IPDV calls and arrests," single-site before-after. Accurate, incl. the no-comparator caveat. |
| Cheng et al. 2021 batterer meta-analysis: **"non-significant overall effects"** | **MISREPRESENTED** | [Cheng 2021, T,V&A 22(3)](https://journals.sagepub.com/doi/10.1177/1524838019865927); [PubMed 31359840](https://pubmed.ncbi.nlm.nih.gov/31359840/) | The meta-analysis found BIPs **significantly reduced** recidivism on criminal-justice-record measures; non-significance was only on *survivor-reported* recidivism. The article inverts the headline conclusion. (Cuts in the article's favor — it understates BIP — but it's still a misstatement of the source.) |
| Sherman & Berk MDVE **"13% arrest vs 26% separation"** | **MISREPRESENTED** | [Wikipedia/MDVE](https://en.wikipedia.org/wiki/Minneapolis_Domestic_Violence_Experiment); [JSTOR 2095575](https://www.jstor.org/stable/2095575) | Commonly cited figures are ~19% (arrest) vs ~34-37% (separate/advise). Direction right, **specific pair wrong**. |
| B-HEARD "**2024** Comptroller audit": 35% unserved, 31/78 precincts, 14,200 overnight | **VERIFIED (substance) / wrong date** | [MG24-060A](https://comptroller.nyc.gov/wp-content/uploads/2025/05/MG24-060A.pdf) | All three figures verbatim. **Audit is dated May 23, 2025**, not 2024 — article calls it a "2024 audit" repeatedly. |
| 2025 *Psychiatric Services* study: B-HEARD "reduced unnecessary ED transports" | **MISREPRESENTED (endpoint)** | [psychiatryonline 10.1176/appi.ps.20250528](https://psychiatryonline.org/doi/10.1176/appi.ps.20250528) | Study's causal DiD endpoint is precinct-level *mental-health EMS call rates*, not ED-transport reduction. ED diversion is an operational stat, not the study's finding. |
| Shem-Tov 2024 NBER: mobile crisis teams divert **5-8%** | **PARTIALLY-SUPPORTED** | [NBER w33761](https://www.nber.org/papers/w33761) | Real paper, **2025 not 2024**, and **CAHOOTS/Eugene-specific**, not "mobile crisis teams" generically. 5-8% confirmed. Paper's headline is "supplement, not substitute" — context omitted. |
| Manhattan Institute: **>700** state psych beds lost 2014-2021 | **VERIFIED** | [Manhattan Institute](https://manhattan.institute/article/systems-under-strain-deinstitutionalization-in-new-york-state-and-city-2025-update) | Exact. |
| OSC Mar 2024: **990 beds, 10.5%**, Apr 2014-Dec 2023 | **VERIFIED** | [DiNapoli release](https://www.osc.ny.gov/press/releases/2024/03/dinapoli-percentage-new-yorkers-mental-illness-rose-available-psychiatric-beds-declined) | Exact quote. |
| **$650M Bridge to Home; 2,000-person target; today 100 BTH + 900 Safe Haven covers ~5%** | **MISREPRESENTED + INTERNALLY CONTRADICTORY** | [NYC Jan-2025 release](https://www.nyc.gov/mayors-office/news/2025/01/mayor-adams-takes-unprecedented-action-curb-street-homelessness-support-people-severe); [CBS](https://www.cbsnews.com/newyork/news/bridge-to-home-nyc-mentally-ill-homeless-plan/); [amNY](https://www.amny.com/news/adams-bridge-to-home-plan-for-homelessness/) | The plan = **1,000 street beds (900 Safe Haven + 100 Bridge to Home)**. There is **no announced "2,000-person target."** So 100+900 = 1,000 is **100% of the announced plan**, not 5%. The article's prose ("covers roughly 5%") contradicts its own bed chart ("1,000 of 2,000 = 50%"), and **both** are wrong against the real 1,000-bed figure. This is the worst quantitative error in the recommendation section. |
| NYPL 121.13 Strangulation 1st = new felony Nov 2010; **in the felony-assault count** | **VERIFIED (premise sound)** | [Justia 2010 §121.13](https://law.justia.com/codes/new-york/2010/pen/part-3/title-h/article-121/121-13/); [DCJS strangulation update Apr-2012](https://www.criminaljustice.ny.gov/pio/research-update-strangulation-apr2012.pdf) | Effective Nov 11, 2010. **DCJS classifies Strangulation 1st/2nd as aggravated assault for index reporting**, so it *does* flow into "felony assault." The skeptic's intuition that Article 121 ≠ felony assault is **wrong**; the article's category logic holds. |
| Reclass "subtracted from **both endpoints**"; 4,400 of 12,364; +47% adjusted | **PARTIALLY-SUPPORTED (logic flaw, magnitude unverified)** | derived | "Both endpoints" is meaningless: the 2010 strangulation count is ~0 (law effective Nov 2010), so there's nothing to subtract at the base. The +47% is arithmetically reproducible, but the **4,400 / "35 pp" magnitude is the author's own drill-down, not a primary-sourced figure**, and is presented with more authority than it has earned. |
| CMS 21% shooting reduction (Comptroller) | **VERIFIED (date nuance)** | [The Cure for Crisis](https://comptroller.nyc.gov/reports/the-cure-for-crisis/) | "21% reduction... 35 → 28 shootings/precinct/yr." Report is **March 2025**, article implies 2024. |
| John Jay 2017: 37-50% gun-injury reductions | **VERIFIED** | [John Jay REC](https://johnjayrec.nyc/2017/10/02/cvinsobronxeastny/) | East NY −50%, S. Bronx −37%. Exact. |

---

## 3. Logical / inferential holes (ranked)

### FATAL (would force a material rewrite of a load-bearing claim)

**F1 — The DV split, the title's central claim, rests on a mis-stitched and possibly non-existent number.**
The title says "domestic-violence-driven." The proof is L2: "73% DV growth" + "39% same-household / ~11,500 of 29,501." Live check of the cited Vital City page found:
- the **39% is a 2025 figure** ("In 2025, 39% of felony assaults were classified as domestic violence"), applied by the article to a **2024 count (29,501)**;
- Vital City's own counts are **29,841 / 309 murders for 2025**, not the 29,501 / 363 the article uses;
- the **73% could not be found on the cited page at all**, and the only locatable 73% (Gothamist) is **"domestic + elderly assaults combined,"** not DV alone;
- "same household" is the author's relabel of "domestic violence" (which the source defines as family *or* household, including intimate partners not necessarily co-resident);
- and because NYPD's public data has **no victim-relationship field** (the article admits this), the entire 39%/73% edifice is a single secondary source (DCJS feed, reported via Vital City/Gothamist/Brennan) layered onto NYPD counts with mismatched denominators.

The qualitative claim ("DV is a major and fast-growing component") almost certainly survives — multiple outlets agree DV/domestic is a leading driver. But the *specific, quantified, title-justifying* version is not cleanly supported by the cited source, mixes years, and inflates DV's specific share by folding in elder abuse. For a memo whose entire brand is numeric rigor, this is the most damaging finding.

**F2 — The Bridge-to-Home recommendation is built on a fabricated denominator and contradicts itself.**
Lever 1 (the "strongest evidence, lowest political cost" recommendation) claims today's ~1,000 beds cover "roughly 5%" of a "2,000-person target." The actual January 2025 plan is **1,000 street beds**. There is no 2,000 target in the source. So the existing capacity is ~100% of the announced plan, the "5%" is wrong, and the article's own bed chart ("1,000 of 2,000 = 50%") contradicts the prose. The recommendation "double the bed count to hit 2,000" is chasing a target the city never set. This doesn't kill the housing argument (the supportive-housing evidence base is genuinely strong), but the specific quantified gap that motivates "scale up fast" is manufactured.

### SERIOUS (undermine credibility / a sub-claim, but thesis survives)

**S1 — Rates-vs-counts in the national comparison (L3).** The article's marquee contrast is NYC **+47% (counts)** vs national **flat (rate)** vs CCJ **+4% (rate)**. Counts and rates are not comparable when population changes. NYC's population grew over 2010-2024; on a per-100k basis NYC's rise would be smaller. The outlier claim probably still holds qualitatively (even a discounted NYC rate beats +4%), but the headline framing is methodologically loaded, and the article's own "Limits" section concedes the NY-vs-FBI definitional break without conceding the rates-vs-counts break.

**S2 — Baseline-shopping cuts both ways.** The article (rightly) accuses NYC's reporting of window-shopping (Oct −1.9% vs year +5.8%). But it then does its own: it uses a **2010** baseline for NYC (maximizing the rise, and conveniently the strangulation-law year) while peer benchmarks use **2019** (CCJ) or single-year 2024 (LA/Chicago/Philly). Comparing a 14-year NYC window to a 5-year peer window is not like-for-like. The piece is partly self-aware (the multi-baseline chart), but the in-brief and title lead with the largest available framing.

**S3 — Causal overreach on "DV-driven."** The correlations shown (DV category rising fast; psych beds falling) are consistent with the thesis but don't establish it. Alternatives the article underweights: (a) **reporting/recording changes** — post-#MeToo and post-2010 strangulation-law, DV incidents are more likely to be recorded as felonies; the article treats the strangulation reclass as the *only* recording artifact, but DV charging practices shifted more broadly; (b) **the DCJS "domestic" definition is broad** (family + household + intimate partner), so growth there may reflect classification drift, not behavior; (c) NYPD itself attributes the felony-assault rise to **"assaults on officers, domestic violence AND stranger attacks"** (per the Tisch 2024 announcement) — a three-way split the article compresses into "DV-driven."

**S4 — Mis-cited program evidence weakens the "what to do" section (L5).** The recommendation leans on: CrimeSolutions (wrong ID/link), Cheng 2021 (conclusion inverted), Sherman & Berk (wrong numbers), the Psychiatric Services study (wrong endpoint), Shem-Tov (wrong scope: CAHOOTS not "mobile crisis teams" generally; wrong year). Individually minor; collectively they suggest the citation layer was assembled faster than it was checked. The two *recommended* DV interventions (Koppa/LAP and Sechrist-Weil/OFDVI) are, to the article's credit, cited accurately — the errors cluster in the comparators, not the picks.

### MINOR

**M1 — Pervasive "2024 audit/report" date errors.** B-HEARD audit (May 2025), CMS report (March 2025), Shem-Tov (2025), Psychiatric Services (2025) all mis-dated as 2024 in places. Sloppy, not substantive.

**M2 — 2024 crime counts slightly off** (murder 363 vs 377; rape 1,534 vs ~1,742). Doesn't change any argument but is checkable and wrong, which corrodes trust in the harder-to-check numbers.

**M3 — "Both endpoints" strangulation subtraction is rhetorical filler** (2010 base ≈ 0). The +47% still computes; the framing oversells the rigor.

**M4 — Savings range ($5-35M).** The article disclaims this itself, so I won't pile on — but a 7× range labeled "directional" is closer to "we don't know" than the prose's confident "plausibly cost-neutral to modestly cost-saving" implies.

---

## 4. Strongest single rebuttal (the steelman)

> **"You've taken a real but ordinary trend — felony assault up, with DV as one of several contributors — and inflated it into a singular 'DV-driven crisis' by (a) attributing a combined domestic-plus-elder figure to DV alone, (b) borrowing a 2025 share statistic and pinning it on 2024, (c) comparing NYC's 14-year count growth against peers' 5-year rate growth, and (d) leaning on a DV split that NYPD's own data cannot produce and that traces to a single secondary feed. NYPD itself names three co-equal drivers — assaults on officers, DV, and stranger attacks. Strip the framing tricks and you have: felony assault is up meaningfully, DV is a meaningful slice, and prevention spending is flat. That's a legitimate finding — but it's a memo about underfunded DV services, not a 'sustained, domestic-violence-driven assault crisis.' The title is writing a check the data can't fully cash."**

The most damaging *specific* alternative explanation the article dismisses too quickly: **recording/classification change**. The article correctly isolates one recording artifact (strangulation) and then declares the rest "behavioral." But DV felony charging, mandatory-arrest enforcement, and the breadth of the DCJS "domestic" definition all plausibly inflate the DV-felony series without a proportional behavioral change. The article needed to address this for the *DV* category the way it did for *strangulation*, and it didn't.

---

## 5. Fabricated or unverifiable claims

- **$186K survivor-security alarms** (Women's Agenda DV share): **not found in any official source.** Treat as unsourced; cut or cite.
- **"73% DV-related felony-assault growth" as DV-specific:** **not locatable on the cited Vital City page;** the traceable 73% is domestic+elder combined (Gothamist). Effectively unverifiable as stated.
- **"~11,500 of 29,501" DV cases:** the author's arithmetic (0.39 × a wrong, year-mismatched base), not a figure any source states.
- **"2,000-person target" for Bridge to Home:** **no source;** the announced plan is 1,000 beds. The "5%" coverage figure derived from it is therefore fabricated.
- **"4,400 / ~35 percentage points" strangulation contribution:** author's own drill-down; plausible but **not primary-sourced** and presented with unearned authority.
- **CrimeSolutions ID 345:** points to the wrong program (Reconnecting Youth, Negative Effects); the LAP profile is ID 495.

Everything else with a verdict above either checks out or is a defensible PARTIAL.

---

## 6. Bottom line — how damaging is the cumulative critique?

**What survives (and is genuinely solid):**
- The **spending story** (L4) is the strongest part of the memo: HRA DV-Services nominal +28%, CPI +28%, Council asks zeroed three years running — all verified to the dollar from primary documents. The −42%-per-case figure is arithmetically clean (it only wobbles to the extent the 73% wobbles).
- The **strangulation reclassification** logic is sound (verified that strangulation is counted as aggravated/felony assault), even if "both endpoints" is filler and the 4,400 magnitude is the author's estimate.
- The **outlier-vs-national** direction (L3) probably holds even after the rates-vs-counts discount.
- The **recommended** interventions' anchor citations (Koppa/LAP, Sechrist-Weil/OFDVI, supportive-housing RCT base, psych-bed loss) are accurately cited.
- The strategic *judgment* — lead with housing/B-HEARD, pilot LAP/OFDVI with a binding sunset, exclude CVI-for-DV and batterer programs — is well-reasoned and unusually honest about its own uncertainty.

**What does not survive intact:**
- **The title's quantified core (L2).** "DV-driven" is defensible as direction; the specific 73%/39%/11,500 construction is not — wrong year, combined-category inflation, fabricated raw count, single-source denominator mismatch. This is the most damaging finding because it's the headline.
- **The Bridge-to-Home gap (F2).** The "covers ~5% of 2,000" is wrong twice and self-contradictory; the real plan is 1,000 beds, already roughly met. The motivating gap for Lever 1 is manufactured.
- **The citation layer's reliability.** A wrong CrimeSolutions link, an inverted Cheng conclusion, wrong MDVE numbers, a mischaracterized Psychiatric Services endpoint, mis-scoped Shem-Tov, and systematic 2024/2025 date errors. None is individually fatal, but a memo that markets itself on "three rounds of adversarial review" and "every URL classified by reputability" should not have this density of checkable errors.

**Net assessment:** This is a *good* strategy artifact with a *trustworthy thesis direction* and an *untrustworthy decimal point*. The diagnosis ("felony assault is up, DV is a major underfunded slice, the city's framing hides it") is real and the spending evidence is airtight. But the piece consistently reaches for the most dramatic available number — the largest baseline, the combined-category growth rate, a doubled bed-target denominator, a borrowed-year share — and several of those reaches don't hold. A fair editor's verdict: **publishable in substance, but the numbers need a hard re-audit before it can claim the rigor it advertises.** The single highest-priority fix is L2: either re-derive the DV split from a current, correctly-attributed source for the correct year, or soften the title from "domestic-violence-driven crisis" to something the data can actually carry.

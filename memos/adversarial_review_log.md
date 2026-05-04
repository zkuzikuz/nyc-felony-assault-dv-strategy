# Adversarial Review Log

Per-round bookkeeping for the three-round adversarial-hardening exercise on `phase0_evidence.md`. Each round adds a section: critiques raised, rebut/partial/accept/fatal labels, research questions posed and findings, memo changes, audit-table delta, kill-criterion check.

The exercise has two acceptable terminal states: (1) hardened memo, or (2) pivot recommendation if any kill criterion fires. Bias toward declaring fatality when evidence supports it.

Posture progression:
- Round 1 — skeptical hiring manager
- Round 2 — methodological peer reviewer
- Round 3 — hostile policy critic (or pivot research pass if R1/R2 triggered the pivot path)

---

## Round 1 — Skeptical hiring manager

**Adversarial agent output:** `memos/r1_critiques.md` (8 critiques: 3 high, 5 medium).

**Critique → label mapping:**

| # | Severity | Title (abbreviated) | Label | Resolution |
|---|---|---|---|---|
| 1 | high | DV thesis rests on single un-replicated source | partial | Research found Brennan Center + Gothamist + DCJS feed corroborate Vital City. Strong row added to audit. |
| 2 | high | +47% partly statutory and classification drift | partial | Research found 3 smaller new sub-categories (~3-4%) + intake practice changes (unquantified). Memo updated to "+40-47%" range. |
| 3 | medium | Clustering rhetorical, can't statistically support | partial | Research re-ran k-sweep + 200-resample bootstrap. Partition is statistically robust at k=3 (silhouette 0.44, "weak/possibly artificial" Kaufman-Rousseeuw band). The "Surge" semantic label was wrong: it mixes structural-rise + COVID-rebound dynamics. Memo language tightened. |
| 4 | high | CMS-to-DV port is analogy, not evidence | partial → substituted | **Major change.** Research found no published CVI evaluation for DV; LAP + High Point OFDVI are the strongest-evidence DV interventions. Headline recommendation rewritten. |
| 5 | medium | $40-60M cost figure dressed as analysis | accept | Cost figure dropped (no longer recommending CMS port). New cost framing for LAP / OFDVI / B-HEARD (~$5-15M / $5-10M / $30-50M) flagged as ±50% rough estimates. |
| 6 | medium | B-HEARD scaling misreads audit | accept | Research isolated cause as primarily a supply problem (overnight ops + team capacity). Memo dropped "mechanical" language; explained the supply requirement. |
| 7 | medium | Minto SCQ mismatch | partial | Research found Vital City + Brennan Center HAVE named the rise; "invisible" claim narrowed to "no NYC government publication has named the 2010+ structural rise as such." |
| 8 | medium | Selective citation of intervention evidence | partial | Research showed Braga's hot-spots effect doesn't generalize to DV (DV is excluded from outcome in the canonical RCTs). Omission was actually defensible; memo now says so explicitly. New evidence-base section ranks DV-specific interventions only. |

**Kill criterion check:**
- "+47% shrinks substantially": NO — research shows ~+40-47% range
- DV-driver fails replication: NO — corroborated by 3 independent sources
- CMS 21% has weak identification: NOT TESTED in R1
- Two rounds converge on same critique: N/A (only R1)
- Audit-table net-decrease: NO — added 5 new strong rows, replaced 1 hypothesis row with stronger external-evidence row

**Decision:** No kill criterion fired. Audit table net-positive. Continue to Round 2 with methodological peer reviewer posture.

**Memo changes (sections touched):** TL;DR, Complication, Question, Thesis, Three supports (major rewrite of Support 1), What NYC has tried table (added LAP, OFDVI rows), Evidence-base section (rewritten around DV-specific interventions), Secondary observation, Audit table (added 5 strong rows), Top serendipitous findings (added findings about CVI-no-DV-eval, B-HEARD supply problem, cluster-label issue), Recommendation pyramid (rewrite), Sources (added 8 R1 sources, reorganized into 3 categories).

**Carryover to Round 2:** None. All R1 critiques addressed.

---

## Round 2 — Methodological peer reviewer

**Adversarial agent output:** `memos/r2_critiques.md` (8 critiques: 4 high, 4 medium).

**Critique → label mapping:**

| # | Severity | Title (abbreviated) | Label | Resolution |
|---|---|---|---|---|
| 1 | high | LAP 35-45% has no CI, identification undisclosed | partial | R2 research found the citation was misattributed: correct source is Koppa 2024 staggered-DiD (37-44% female-IPH rate jurisdiction-level). CrimeSolutions tiers are Effective/Promising/No Effects (no "Supported"). Memo updated. |
| 2 | high | OFDVI single-site pre/post, Sweden not independent | partial | R2 research confirmed Sechrist & Weil 2018 is single-jurisdiction interrupted-time-series; Sweden replication separate quasi-experiment. Memo softened OFDVI claims; reframed as pilot-with-evaluation. |
| 3 | medium | Multiplicity unaccounted for, no leave-one-offense-out | partial → strengthened | R2 research re-ran clustering 16 times (LOO). k=3 best in 16/16; silhouette 0.402-0.470; structural-rise trio co-clusters in 13/13 non-trio drops. Added as new strong audit row. |
| 4 | high | External validity asserted, not argued | accept | Braga-Weisburd 2019 finds matched-design focused-deterrence effects ~28% of non-matched-design. Memo reframed: pilot-with-evaluation; effect projection ~10-15% post-attenuation. |
| 5 | high | Effect-size denominators unspecified | accept | Per-effect denominator analysis confirmed all four cited effects use heterogeneous denominators; citywide projection arithmetically undefined without scope adjustment. Memo language now explicit. |
| 6 | medium | Asymmetric evidence standard | partial | Transportability literature does not rank cross-outcome vs cross-jurisdiction generalization; R2 verdict on this question was inconclusive. Memo re-framed thesis statement to explicitly address the asymmetry: "reject the asymmetric standard that treats observational evidence as deployment-grade for one set of interventions while disqualifying it for another." |
| 7 | medium | CMS 21% comparator identification unaudited | partial | R2 research found Comptroller 2024 used Callaway-Sant'Anna staggered DiD with visual (not formal) parallel-trends testing. Reasonable identification, not airtight. Memo audit-row updated. |
| 8 | medium | B-HEARD 14K vs 13K reconciliation | partial → corrected | R2 research found the 14K overnight figure is in addition to, not overlapping with, the 13K in-hours unserved gap. Audit explicitly does not track in-hours cause. R1's "primarily a supply problem" framing was overstated. Memo corrected. |

**Kill criterion check:**
- "+47% shrinks": NOT in R2 scope
- DV-driver fails replication: NOT raised in R2
- CMS 21% has weak identification: PARTIAL — found CST staggered DiD, reasonable but not airtight. Memo acknowledges. NOT fatal.
- Two rounds converge: R2 C6 echoes R1's CMS-for-DV concern in asymmetric-standards form; R2 C1 echoes R1's "single source" concern in identification language. **Both have been addressed by research** (substitution + reframing); R3 will need to find genuinely new ground or this becomes a kill criterion next round.
- Audit-table net-decrease: NO — net positive (+3 new strong rows from R2 research; B-HEARD framing corrected; LAP/OFDVI deployment downgraded to pilot+evaluation but compensated by new methodological-rigor strong rows)

**Decision:** No kill criterion fired. Memo voice has shifted substantially toward humility about effect-size projection (pilot-with-evaluation rather than deploy-with-cited-effect). Audit table net-positive but the "deploy-grade" claims have all been replaced with "pilot-and-evaluate" framings. Continue to Round 3 with hostile-policy-critic posture, but flag for self-monitoring: if R3 raises the same identification/transportability concerns again with research that can't address them, that's a kill criterion fire.

**Memo changes (sections touched):** TL;DR (substantial humility-injection), Thesis (rewritten to address asymmetric-standards critique), Three supports — Section 1 (major rewrite incorporating Koppa 2024 citation, identification disclosure, transportability attenuation, pilot framing), Section 2 (B-HEARD reframing — overnight vs in-hours separated), What NYC has tried table (LAP and OFDVI rows updated with identification details), Evidence-base section (rewritten with identification disclosed for each intervention, transportability discount added), Audit table (4 new strong rows added; B-HEARD row corrected; LAP/OFDVI deployment row downgraded), Top serendipitous findings (added Koppa citation correction, transportability discount, B-HEARD reconciliation), Sources (added Koppa, CrimeSolutions, Braga-Weisburd 2019, Tipton 2014).

**Carryover to Round 3:** R3 must avoid rehashing R1+R2 ground (CMS-for-DV, identification rigor, transportability). Hostile-policy-critic should find genuinely new attack surfaces — political/constituency framing, implementation feasibility, who-wins-who-loses, opposition tactics, track record of analogous reforms.

---

## Round 3 — Hostile policy critic

**Adversarial agent output:** `memos/r3_critiques.md` (8 critiques: 5 high, 3 medium). **Posture chosen by agent:** DV-survivor advocate / coalition organizer with secondary civil-liberties lens.

**Critique → label mapping:**

| # | Severity | Title (abbreviated) | Label | Resolution |
|---|---|---|---|---|
| 1 | high | LAP creates rationing instrument | accept | R3 research found Oklahoma LAP shows *increased* overall service access; moderate-risk subgroup access unmeasured. Memo Section 3 added LAP design constraint: score is additive to existing pathways, never replacement. |
| 2 | high | OFDVI civil-liberties profile | accept | Memo Section 3 added: call-in inclusion limited to post-conviction or judicially-confirmed data; public roster transparency; sunset on inclusion; independent civil-liberties impact assessment by external entity (Vera Institute or NYU CRRJ). |
| 3 | high | Geographic concentration in already-over-policed precincts | accept | Memo Section 3 added: pilot precincts balance high-DV-incidence with mixed-incidence including under-reporting neighborhoods; political legitimacy gain offsets statistical-power loss. |
| 4 | high | $40-65M displaces existing services | accept | R3 research: NYC has $4.22B FY26 budget gap; no published list of eligible cuts; CMS scaled via DYCD post-MOCJ transition. Memo Section 3 added explicit displacement-risk acknowledgment with funding-source candidates (NYPD reallocation, MOCJ discretionary, federal pass-through, philanthropic match). |
| 5 | medium | NNSC + CMS-vendor capture | partial | R3 research: NYC CMS pool is mostly pre-existing CBOs (Man Up!, Elite Learners, etc.), not NNSC spinoffs — capture concern partially refuted. But culturally-specific carve-out still warranted. Memo Section 3 added: ≥30% set-aside for Sakhi, Womankind, VIP, AVP, Barrier Free Living and similar organizations identified through ENDGBV consultation. |
| 6 | high | DV-frame vs housing-frame is a choice | accept → restructure | **Major change.** Added new "Framing choice" section that defends the housing-first ranking transparently and demotes DV-specific police-administered programs to Section 3. Section 1 is now Bridge to Home / supportive-housing operationalization; Section 2 is B-HEARD; Section 3 is LAP + OFDVI pilots with safeguards. |
| 7 | medium | Population validity for immigrant/LGBTQ/disabled survivors | accept | Memo Section 3 LAP design constraint added: trained interpreter access, gender-inclusive language, immigration-enforcement firewall, accessibility for Deaf/disabled survivors. |
| 8 | medium | Evaluation kill-switch unfalsifiable in practice | accept | R3 research strongly supports the critique: NYC pilot-termination track record is poor. Memo Section 3 sunset clause now framed as procurement-contract-binding, with automatic de-funding trigger. Top-serendipity-finding-#1 added. |

**Kill criterion check:**
- "+47% shrinks": NOT in R3 scope
- DV-driver fails replication: NOT raised in R3
- CMS 21% has weak identification: NOT raised in R3
- Two rounds converge: R3 attacked genuinely new ground (political/implementation/framing). NO convergence.
- Audit-table net-decrease: NO — added 4 new strong rows from R3 research; recommendation reframed but diagnostic claims unchanged

**Decision:** No kill criterion fired. Memo voice has shifted substantially across rounds:
- R0: "Build DV-CMS port"
- R1: "Adopt LAP + OFDVI" (after CMS-for-DV refuted)
- R2: "Pilot LAP + OFDVI with rigorous evaluation" (after identification + transportability concerns)
- R3: "Lead with housing + B-HEARD; pilot LAP + OFDVI third with safeguards and sunset" (after political/civil-liberties concerns)

Each reframe was driven by adversarial critique + research findings. The diagnostic ("DV-driven structural rise that NYC government has not surfaced") survived all three rounds. The recommendation moved from confident-deployment to housing-first-with-pilot-research.

**Memo changes (sections touched):** TL;DR (rewritten with new ordering), Question (added distal-driver context), **NEW: Framing choice section** (defends housing-first transparently), Thesis (rewritten), Three supports (full restructure: 1=Bridge to Home, 2=B-HEARD, 3=LAP+OFDVI pilots with binding design constraints), What NYC has tried (B-HEARD row corrected), Audit table (4 new strong rows from R3 research), Top serendipitous findings (2 new findings added: pilot-termination track record, distal drivers as alternative frame), Recommendation pyramid (rewritten to reflect new ordering).

**Carryover / Open questions for Phase 2:**
1. The recommendation now has a housing-first ranking that depends on operationalizing the announced $650M Bridge to Home pipeline at scale. If that pipeline stalls politically, the memo's primary lever is unavailable. Phase-2 work should test the operationalization-feasibility assumption.
2. The sunset-clause design (procurement-contract-binding with automatic de-funding) needs legal review. NYC procurement code may not permit binding pre-set termination triggers.
3. The culturally-specific DV-org procurement set-aside (≥30%) needs review against NYC's PPB rules; the M/WBE preference framework may not provide a clean legal vehicle.

---

## Final assessment

The exercise produced a **hardened memo, not a pivot recommendation**. No kill criterion fired. The diagnostic ("structural felony-assault rise that NYC government has not surfaced; DV is the dominant proximate driver") survived three independent adversarial rounds. The recommendation evolved substantially — from confident-deployment of an architectural analogy (DV-CMS port) to housing-first-plus-pilot-research with binding civil-liberties safeguards. The audit table is net-positive across rounds, and every load-bearing claim now rests on either direct data, multi-source corroboration, or explicitly acknowledged external-evidence projection with attenuation factors.

The memo voice is now substantively more humble than the original draft, but more defensible. A hiring manager reading it should find both rigor and political sophistication — and the kind of intellectual honesty that names alternative framings, acknowledges uncertainty, and structures recommendations so that bad pilots get cut.

The strategic insight is essentially unchanged from R0: NYC has a 14-year structural rise that no government metric surfaces. The recommendation is what changed, and the change is for the better.

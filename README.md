# NYC Felony-Assault & Domestic-Violence Strategy

_Published June 28, 2026 by Zarren Kuzma_

A short, data-driven strategy essay arguing that felony assault is the one
violent crime in New York that keeps rising since 2017, that its largest and
fastest-growing component is domestic, and that the city's domestic-violence
prevention budget has stayed flat in real terms while the need has grown.

The essay is a static HTML artifact built for the New York City strategy and
chief-of-staff conversation.

## The artifact

`site/index.html` is the deliverable: an ~640-word essay with three charts,
anchored to a 2017 baseline (the window where NYPD category data and the DV
share are both consistent). Charts render at runtime from `site/data/chart-*.json`
via Observable Plot, with static PNG fallbacks under `site/assets/charts/`.

Open it locally:

```bash
cd site && python3 -m http.server 8137
# then visit http://localhost:8137/
```

## Repository layout

- `site/` — the published HTML artifact (essay, charts, styles).
- `memos/` — the evidence trail: Phase-0 evidence discovery, the composition
  and intervention analyses, and the two-stage independent adversarial review
  (`external_adversarial_review.md`, `adversarial_review_verdict.md`).
- `notebooks/`, `src/`, `scripts/` — the Python pipeline (DuckDB + pandas) that
  produced the figures.
- `data/` — raw and processed data (large/raw partitions are gitignored).

## Sources

Felony-assault and category counts: NYPD Complaint Data Historic. Domestic-violence
share: NY State DCJS feed as reported by Vital City. Spending: NYC Council Finance
Committee HRA reports, inflation-adjusted. Full source list is in the essay's
"Sources & method" endnote.

## Note

Built with [Claude Code](https://claude.com/claude-code); the author directs
intent, makes every decision, and is solely responsible for the argument.

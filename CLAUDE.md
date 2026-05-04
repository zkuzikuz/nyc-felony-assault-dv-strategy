# nyc-strategy-artifact

Phase 0 evidence discovery for a NYC public-data strategy memo. Three candidate theses (H1: 311 as leading indicator of crime; H4: good-news counter-narrative; H5: hyperlocal microscope) are tested against ~20 data cuts. The winning thesis becomes the spine of a Minto-pyramid HTML strategy artifact in later phases.

## Stack

Python 3.11, Jupyter, DuckDB, pandas + pyarrow, geopandas, sodapy, scipy/statsmodels, plotly + matplotlib. Data lives as hive-partitioned parquet under `data/raw/` with DuckDB views for fast querying.

## Run

```bash
# one-time setup
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # or use pyproject.toml
cp .env.example .env                        # fill in SODA_APP_TOKEN

# launch notebooks
.venv/bin/jupyter lab
```

## Project Structure

```
nyc-strategy-artifact/
  src/nyc_eda/
    __init__.py     # dataset IDs + path constants
    soda.py         # paginated SODA client; idempotent partitioned writes
    storage.py      # DuckDB views over parquet
    geo.py          # precinct + NTA boundaries; spatial joins
    cuts.py         # the 20 named cuts as functions (built post-acquisition)
    stats.py        # lagged correlations, block-bootstrap CI, permutation tests
  notebooks/
    00_acquire.ipynb           # schema sniff + bulk pulls + DuckDB registration
    10_cuts_time_geo.ipynb     # C1-C9
    11_cuts_demo_offense.ipynb # C10-C15
    20_h1_311_leading.ipynb    # H1 verdict
    21_h4_good_news.ipynb      # H4 verdict
    22_h5_hyperlocal.ipynb     # H5 verdict
    99_serendipity_review.ipynb
  data/
    raw/         # parquet, hive-partitioned by year=YYYY/month=MM (gitignored)
    interim/
    processed/cuts/  # saved figures + tables per cut
    geo/             # precinct + NTA GeoJSON
    cache.duckdb     # gitignored
  memos/
    phase0_evidence.md   # the deliverable
    serendipity_log.md   # rolling anomaly log
  scripts/
```

## Environment

Required env vars (in `.env`):
- `SODA_APP_TOKEN` — free from data.cityofnewyork.us. Without it, SODA pulls are throttled hard; H1 needs ~15M rows of 311 data so the token matters.
- `CENSUS_API_KEY` — free from api.census.gov; needed for ACS demographic joins.

## Current Status

WIP — Phase 0 (evidence discovery). See `/home/zkuzma8/.claude/plans/let-s-go-with-a-fizzy-cascade.md` for the approved plan.

## Known Issues

- NYPD YTD dataset (`5uac-w243`) has spurious complaint dates (year 1014, 2052); filter in acquisition.
- 311 modern dataset (`erm2-nwe9`) covers 2020-present only; 2010-2019 data lives in `76ig-c548` with a different schema.
- 2020 NTAs aren't always colloquial neighborhoods; use for statistical joins, not narrative naming.

## Notes

Plan is committed at `/home/zkuzma8/.claude/plans/let-s-go-with-a-fizzy-cascade.md`. Phases 1-3 (Minto structuring → visual design → HTML build) follow Phase 0; do not start them until the evidence memo picks a thesis.

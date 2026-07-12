# nyc-strategy-artifact

NYC public-data strategy memo: Phase 0 tests 3 theses (311 as crime leading indicator, good-news counter-narrative, hyperlocal) against ~20 data cuts; winner becomes a Minto-pyramid HTML artifact.

## Stack
Python 3.11, Jupyter, DuckDB, pandas/pyarrow, geopandas, sodapy, scipy/statsmodels, plotly/matplotlib. Data as hive-partitioned parquet in `data/raw/`.

## Run
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `cp .env.example .env` (set `SODA_APP_TOKEN`, `CENSUS_API_KEY`), then `.venv/bin/jupyter lab`.

## Status
Phases 0-2 complete on `master`. `site/index.html` is an ~800-word essay with 3 charts (2017 baseline); thesis is a sustained felony-assault crisis with large DV component (+46% since 2017, flat real DV-prevention budget). Adversarially reviewed. Live at zarrenkuzma.com/nyc-felony-assault-crisis/ (restyled to the zarrenkuzma.com home idiom + Fathom events 2026-07-12; deploy via tools/deploy.sh, creds in gitignored .deploy.env).

## Known Issues
- NYPD YTD dataset `5uac-w243` has spurious dates (year 1014, 2052); filter on acquisition.
- 311 `erm2-nwe9` is 2020-present; 2010-2019 lives in `76ig-c548` with a different schema.
- 2020 NTAs are statistical joins, not colloquial neighborhood names.
- Charts render from `site/data/chart-*.json`; PNGs in `site/assets/charts/` are fallbacks, regenerate via `scripts/render_sketches.py`.

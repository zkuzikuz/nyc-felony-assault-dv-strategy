"""Programmatically build the .ipynb files for the EDA pipeline.

Usage:
    .venv/bin/python scripts/build_notebooks.py

Each notebook is defined as a list of (cell_type, source_lines) pairs.
Re-run any time to regenerate notebooks from this source-of-truth.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"


def md(*lines: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": list(lines)}


def code(*lines: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": list(lines),
    }


def write_notebook(name: str, cells: list[dict]) -> Path:
    path = NB_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(nb, indent=1))
    return path


# --------------------------------------------------------------------------- #
# 00_acquire.ipynb — schema sniff + bulk pulls + DuckDB registration
# --------------------------------------------------------------------------- #

NB00 = [
    md(
        "# 00 — Acquire NYC OpenData\n",
        "\n",
        "Pulls NYPD Complaint (historic + YTD), 311 Service Requests (modern + historic),\n",
        "and precinct/NTA geometries. Idempotent: parquet partitions already on disk are\n",
        "skipped. Token-free runs are throttled — set `SODA_APP_TOKEN` in `.env` for speed.\n",
    ),
    code(
        "import os, sys\n",
        "from pathlib import Path\n",
        "\n",
        "# add src/ to path so notebooks find nyc_eda\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "sys.path.insert(0, str(PROJECT / 'src'))\n",
        "\n",
        "from dotenv import load_dotenv\n",
        "load_dotenv(PROJECT / '.env')\n",
        "print('SODA token set:', bool(os.environ.get('SODA_APP_TOKEN')))\n",
    ),
    md("## Schema sniff — verify column names per dataset\n"),
    code(
        "from nyc_eda import DATASETS\n",
        "from nyc_eda.soda import schema_sniff\n",
        "\n",
        "for name, info in DATASETS.items():\n",
        "    df = schema_sniff(info['id'], n=2)\n",
        "    print(f'{name} ({info[\"id\"]}):  {len(df.columns)} cols')\n",
    ),
    md("## Geometry — precinct + NTA boundaries\n"),
    code(
        "from nyc_eda import GEO_ROOT\n",
        "from nyc_eda.geo import load_precincts, load_ntas\n",
        "\n",
        "precincts = load_precincts(GEO_ROOT)\n",
        "ntas      = load_ntas(GEO_ROOT)\n",
        "print(f'precincts: {len(precincts)} polygons, columns={list(precincts.columns)[:6]}')\n",
        "print(f'ntas:      {len(ntas)} polygons, columns={list(ntas.columns)[:6]}')\n",
    ),
    md(
        "## Bulk pulls\n",
        "\n",
        "Pull date ranges per dataset. Each call writes hive-partitioned parquet under\n",
        "`data/raw/{dataset_id}/year=YYYY/month=MM/part.parquet` and is idempotent.\n",
        "\n",
        "**Defaults** (override below if you want a smaller pilot):\n",
        "- NYPD historic: 2017-01 to 2019-12 (the H1 lag-window pre-2020).\n",
        "- NYPD YTD:      2020-01 to today.\n",
        "- 311 modern:    2020-01 to today.\n",
        "- 311 historic:  2017-01 to 2019-12.\n",
    ),
    code(
        "from datetime import date\n",
        "from nyc_eda import RAW_ROOT\n",
        "from nyc_eda.soda import fetch_range\n",
        "\n",
        "today = date.today()\n",
        "ranges = {\n",
        "    # qgea-i56i is the canonical NYPD full-history dataset (2006-present).\n",
        "    # 5uac-w243 (YTD) is reserved for the *current* calendar year only.\n",
        "    'nypd_main':    (2017, 1, today.year, today.month),\n",
        "    '311_modern':   (2020, 1, today.year, today.month),\n",
        "    '311_historic': (2017, 1, 2019, 12),\n",
        "}\n",
        "\n",
        "all_paths = {}\n",
        "for name, (sy, sm, ey, em) in ranges.items():\n",
        "    info = DATASETS[name]\n",
        "    all_paths[name] = fetch_range(info['id'], info['date_col'], sy, sm, ey, em, RAW_ROOT, desc=name)\n",
        "\n",
        "for name, paths in all_paths.items():\n",
        "    print(f'{name}: {len(paths)} partitions')\n",
    ),
    md("## DuckDB view registration\n"),
    code(
        "from nyc_eda import DUCKDB_PATH\n",
        "from nyc_eda.storage import open_db, register_dataset, register_geojson, install_spatial\n",
        "\n",
        "con = open_db(DUCKDB_PATH)\n",
        "install_spatial(con)\n",
        "\n",
        "# per-dataset views\n",
        "for name, info in DATASETS.items():\n",
        "    n = register_dataset(con, f'r_{name}', RAW_ROOT, info['id'])\n",
        "    print(f'r_{name}: {n:,} rows')\n",
        "\n",
        "# unified views — match columns across historic and YTD/modern\n",
        "con.execute('''\n",
        "    CREATE OR REPLACE VIEW v_nypd AS\n",
        "    SELECT cmplnt_num, cmplnt_fr_dt, cmplnt_fr_tm, addr_pct_cd, boro_nm,\n",
        "           ofns_desc, ky_cd, law_cat_cd, latitude, longitude, prem_typ_desc,\n",
        "           susp_age_group, susp_race, susp_sex, vic_age_group, vic_race, vic_sex\n",
        "    FROM r_nypd_main\n",
        "    UNION ALL\n",
        "    SELECT cmplnt_num, cmplnt_fr_dt, cmplnt_fr_tm, addr_pct_cd, boro_nm,\n",
        "           ofns_desc, ky_cd, law_cat_cd, latitude, longitude, prem_typ_desc,\n",
        "           susp_age_group, susp_race, susp_sex, vic_age_group, vic_race, vic_sex\n",
        "    FROM r_nypd_ytd\n",
        "''')\n",
        "con.execute('''\n",
        "    CREATE OR REPLACE VIEW v_311 AS\n",
        "    SELECT unique_key, created_date, closed_date, agency, complaint_type, descriptor,\n",
        "           incident_zip, incident_address, latitude, longitude, borough, community_board,\n",
        "           police_precinct, council_district, status, resolution_description\n",
        "    FROM r_311_modern\n",
        "    UNION ALL\n",
        "    SELECT unique_key, created_date, closed_date, agency, complaint_type, descriptor,\n",
        "           incident_zip, incident_address, latitude, longitude, borough, community_board,\n",
        "           police_precinct, council_district, status, resolution_description\n",
        "    FROM r_311_historic\n",
        "''')\n",
        "\n",
        "# geometry tables\n",
        "register_geojson(con, 'g_precincts', GEO_ROOT / 'precincts.geojson')\n",
        "register_geojson(con, 'g_ntas',      GEO_ROOT / 'ntas.geojson')\n",
        "\n",
        "for v in ['v_nypd', 'v_311', 'g_precincts', 'g_ntas']:\n",
        "    n = con.execute(f'SELECT COUNT(*) FROM {v}').fetchone()[0]\n",
        "    print(f'{v}: {n:,} rows')\n",
    ),
    md("## Sanity check — date coverage per dataset\n"),
    code(
        "for v, dcol in [('v_nypd', 'cmplnt_fr_dt'), ('v_311', 'created_date')]:\n",
        "    r = con.execute(f'''\n",
        "        SELECT MIN(CAST({dcol} AS TIMESTAMP)) AS min_d,\n",
        "               MAX(CAST({dcol} AS TIMESTAMP)) AS max_d,\n",
        "               COUNT(*) AS n\n",
        "        FROM {v}\n",
        "        WHERE CAST({dcol} AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE\n",
        "    ''').fetchone()\n",
        "    print(f'{v}: {r[2]:,} rows from {r[0]} to {r[1]}')\n",
    ),
    md(
        "## Serendipity\n",
        "\n",
        "Anything surprising during acquisition? Schema gotchas, unexpected null patterns,\n",
        "data-quality issues — log to `memos/serendipity_log.md`.\n",
    ),
]


# --------------------------------------------------------------------------- #
# 10_cuts_time_geo.ipynb — C1-C6
# --------------------------------------------------------------------------- #

NB10 = [
    md(
        "# 10 — Time and Geography Cuts (C1-C6)\n",
        "\n",
        "Runs cuts C1 (calendar year), C2 (seasonality), C3 (COVID step), C4 (DOW × hour),\n",
        "C5 (borough), C6 (precinct). Saves figures to `data/processed/cuts/`.\n",
    ),
    code(
        "import sys\n",
        "from pathlib import Path\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "sys.path.insert(0, str(PROJECT / 'src'))\n",
        "\n",
        "import matplotlib.pyplot as plt\n",
        "from nyc_eda import DUCKDB_PATH, CUTS_OUT\n",
        "from nyc_eda.storage import open_db\n",
        "from nyc_eda import cuts\n",
        "\n",
        "CUTS_OUT.mkdir(parents=True, exist_ok=True)\n",
        "con = open_db(DUCKDB_PATH)\n",
    ),
    md("## C1 — Calendar year\n"),
    code(
        "df = cuts.c1_calendar_year(con)\n",
        "df.to_csv(CUTS_OUT / 'C1_calendar_year.csv', index=False)\n",
        "fig, ax = plt.subplots(figsize=(8, 4))\n",
        "for src, sub in df.groupby('source'):\n",
        "    ax.plot(sub['year'], sub['n'], marker='o', label=src)\n",
        "ax.set_title('C1 — complaints per calendar year'); ax.set_xlabel('year'); ax.legend()\n",
        "plt.tight_layout(); plt.savefig(CUTS_OUT / 'C1_calendar_year.png', dpi=120); plt.show()\n",
        "df\n",
    ),
    md("## C2 — Seasonality\n"),
    code(
        "df = cuts.c2_month_seasonality(con)\n",
        "df.to_csv(CUTS_OUT / 'C2_seasonality.csv', index=False)\n",
        "fig, ax = plt.subplots(figsize=(8, 4))\n",
        "ax.bar(df['month'], df['avg_complaints'])\n",
        "ax.set_title('C2 — NYPD avg monthly complaints (across years)')\n",
        "ax.set_xlabel('month'); ax.set_ylabel('avg complaints')\n",
        "plt.tight_layout(); plt.savefig(CUTS_OUT / 'C2_seasonality.png', dpi=120); plt.show()\n",
        "df\n",
    ),
    md("## C3 — COVID step\n"),
    code(
        "df = cuts.c3_covid_step(con)\n",
        "df.to_csv(CUTS_OUT / 'C3_covid_step.csv', index=False)\n",
        "df\n",
    ),
    md("## C4 — Day-of-week × hour\n"),
    code(
        "df = cuts.c4_dow_hour(con)\n",
        "df.to_csv(CUTS_OUT / 'C4_dow_hour.csv', index=False)\n",
        "pivot = df.pivot(index='dow', columns='hour', values='n').fillna(0)\n",
        "fig, ax = plt.subplots(figsize=(10, 3.5))\n",
        "im = ax.imshow(pivot.values, aspect='auto', cmap='YlOrRd')\n",
        "ax.set_yticks(range(7)); ax.set_yticklabels(['Sun','Mon','Tue','Wed','Thu','Fri','Sat'])\n",
        "ax.set_xlabel('hour of day'); ax.set_title('C4 — NYPD complaints: DOW × hour')\n",
        "fig.colorbar(im); plt.tight_layout(); plt.savefig(CUTS_OUT / 'C4_dow_hour.png', dpi=120); plt.show()\n",
    ),
    md("## C5 — Borough\n"),
    code(
        "df = cuts.c5_borough(con)\n",
        "df.to_csv(CUTS_OUT / 'C5_borough.csv', index=False)\n",
        "df\n",
    ),
    md("## C6 — Precinct\n"),
    code(
        "df = cuts.c6_precinct(con)\n",
        "df.to_csv(CUTS_OUT / 'C6_precinct.csv', index=False)\n",
        "df.head(20)\n",
    ),
    md("## Serendipity\n", "Anything surprising in the time/geo cuts?\n"),
]


# --------------------------------------------------------------------------- #
# 11_cuts_demo_offense.ipynb — C13-C15, C19-C20 (categorical + operational)
# --------------------------------------------------------------------------- #

NB11 = [
    md(
        "# 11 — Demographic, Offense, Operational Cuts (C13-C15, C19-C20)\n",
        "\n",
        "Categorical cuts (complaint types, law category, top felonies) plus operational\n",
        "cuts (repeat-address 311, agency response time). C7-C12 (NTA / tract / ACS) and\n",
        "C18 (GDELT) are run inline in the H1/H4 hypothesis notebooks.\n",
    ),
    code(
        "import sys\n",
        "from pathlib import Path\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "sys.path.insert(0, str(PROJECT / 'src'))\n",
        "\n",
        "import matplotlib.pyplot as plt\n",
        "from nyc_eda import DUCKDB_PATH, CUTS_OUT\n",
        "from nyc_eda.storage import open_db\n",
        "from nyc_eda import cuts\n",
        "\n",
        "con = open_db(DUCKDB_PATH)\n",
    ),
    md("## C13 — Top 311 complaint types\n"),
    code(
        "df = cuts.c13_311_complaint_types(con)\n",
        "df.to_csv(CUTS_OUT / 'C13_311_top.csv', index=False); df.head(25)\n",
    ),
    md("## C14 — Law category split\n"),
    code(
        "df = cuts.c14_law_category(con)\n",
        "df.to_csv(CUTS_OUT / 'C14_law_category.csv', index=False); df\n",
    ),
    md("## C15 — Top felony offenses, year over year\n"),
    code(
        "df = cuts.c15_top_felony_offenses(con)\n",
        "df.to_csv(CUTS_OUT / 'C15_top_felony.csv', index=False)\n",
        "wide = df.pivot(index='year', columns='ofns_desc', values='n').fillna(0)\n",
        "fig, ax = plt.subplots(figsize=(10, 5))\n",
        "wide.plot(ax=ax, marker='o'); ax.set_title('C15 — top felony offenses by year')\n",
        "ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)\n",
        "plt.tight_layout(); plt.savefig(CUTS_OUT / 'C15_top_felony.png', dpi=120); plt.show()\n",
    ),
    md("## C19 — Repeat-address 311 hotspots\n"),
    code(
        "df = cuts.c19_repeat_address_311(con)\n",
        "df.to_csv(CUTS_OUT / 'C19_repeat_addr.csv', index=False); df.head(30)\n",
    ),
    md("## C20 — Resolution time by agency\n"),
    code(
        "df = cuts.c20_resolution_time_by_agency(con)\n",
        "df.to_csv(CUTS_OUT / 'C20_resolution_time.csv', index=False); df\n",
    ),
    md("## Serendipity\n"),
]


# --------------------------------------------------------------------------- #
# 20_h1_311_leading.ipynb — H1 verdict
# --------------------------------------------------------------------------- #

NB20 = [
    md(
        "# 20 — H1: Do 311 quality-of-life complaints lead felony reports?\n",
        "\n",
        "**Hypothesis:** QoL-311 month *t* correlates positively with major-felony month\n",
        "*t+k* for some k in [3, 12], at the precinct level, with r at lag k materially\n",
        "above r at lag 0. **Non-obvious check:** survives within mid-income tracts.\n",
    ),
    code(
        "import sys\n",
        "from pathlib import Path\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "sys.path.insert(0, str(PROJECT / 'src'))\n",
        "\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "from nyc_eda import DUCKDB_PATH, CUTS_OUT\n",
        "from nyc_eda.storage import open_db\n",
        "from nyc_eda import cuts\n",
        "from nyc_eda.stats import lagged_correlation, permutation_test_lag\n",
        "\n",
        "con = open_db(DUCKDB_PATH)\n",
    ),
    md("## C16 — QoL-311 × major-felony, monthly per precinct\n"),
    code(
        "panel = cuts.c16_qol311_x_majorfelony(con)\n",
        "panel.to_csv(CUTS_OUT / 'C16_qol_x_felony.csv', index=False)\n",
        "print(f'panel: {len(panel):,} rows over {panel[\"precinct\"].nunique()} precincts, '\n",
        "      f'{panel[\"month\"].nunique()} months')\n",
        "panel.head()\n",
    ),
    md("## C17 — Lag scan, per precinct\n"),
    code(
        "lag_results = cuts.c17_lag_scan_per_precinct(panel, max_lag=12)\n",
        "lag_results.to_csv(CUTS_OUT / 'C17_lag_scan.csv', index=False)\n",
        "median_by_lag = lag_results.groupby('lag')['r'].median().reset_index()\n",
        "fig, ax = plt.subplots(figsize=(8, 4))\n",
        "ax.plot(median_by_lag['lag'], median_by_lag['r'], marker='o')\n",
        "ax.axhline(0, color='gray', lw=0.5); ax.set_xlabel('lag (months)')\n",
        "ax.set_ylabel('median Pearson r across precincts')\n",
        "ax.set_title('C17 — QoL-311 → major-felony lag scan')\n",
        "plt.tight_layout(); plt.savefig(CUTS_OUT / 'C17_lag_scan.png', dpi=120); plt.show()\n",
        "median_by_lag\n",
    ),
    md("## City-level lag scan and permutation test\n"),
    code(
        "city = panel.groupby('month').agg(qol_311=('qol_311','sum'), major_felony=('major_felony','sum')).reset_index()\n",
        "lc = lagged_correlation(city['qol_311'], city['major_felony'], max_lag=12)\n",
        "print('city-level lag scan:'); print(lc)\n",
        "best_lag = int(lc.iloc[lc['r'].idxmax()]['lag'])\n",
        "perm = permutation_test_lag(city['qol_311'], city['major_felony'], lag=best_lag, n_perm=2000)\n",
        "print(f'best lag = {best_lag} months, perm test: {perm}')\n",
    ),
    md("## Verdict\n"),
    code(
        "best_r = lc['r'].max()\n",
        "lag_at_best = int(lc.iloc[lc['r'].idxmax()]['lag'])\n",
        "lag0_r     = float(lc[lc['lag']==0]['r'].iloc[0]) if (lc['lag']==0).any() else float('nan')\n",
        "verdict = 'partial'\n",
        "if best_r >= 0.35 and (best_r - lag0_r) > 0.05 and perm['p_perm'] < 0.05:\n",
        "    verdict = 'yes'\n",
        "elif best_r < 0.20:\n",
        "    verdict = 'no'\n",
        "print(f'SIGNAL: {verdict}')\n",
        "print(f'  best_r={best_r:.3f} at lag={lag_at_best}, lag0_r={lag0_r:.3f}, perm_p={perm[\"p_perm\"]:.3f}')\n",
    ),
    md("## Serendipity\n"),
]


# --------------------------------------------------------------------------- #
# 21_h4_good_news.ipynb — H4 verdict
# --------------------------------------------------------------------------- #

NB21 = [
    md(
        "# 21 — H4: The good-news counter-narrative\n",
        "\n",
        "**Hypothesis:** ≥3 top-15 felony categories are down ≥20% 2019→2024 with\n",
        "GDELT headline volume flat or rising, AND we exclude already-publicized declines.\n",
    ),
    code(
        "import sys\n",
        "from pathlib import Path\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "sys.path.insert(0, str(PROJECT / 'src'))\n",
        "\n",
        "import matplotlib.pyplot as plt\n",
        "from nyc_eda import DUCKDB_PATH, CUTS_OUT\n",
        "from nyc_eda.storage import open_db\n",
        "from nyc_eda import cuts\n",
        "\n",
        "con = open_db(DUCKDB_PATH)\n",
    ),
    md("## Felony trends 2019 → latest year\n"),
    code(
        "df = cuts.c15_top_felony_offenses(con, top_n=15)\n",
        "wide = df.pivot(index='year', columns='ofns_desc', values='n').fillna(0)\n",
        "if 2019 in wide.index and wide.index.max() >= 2024:\n",
        "    base = wide.loc[2019]; latest = wide.loc[wide.index.max()]\n",
        "    pct = ((latest - base) / base * 100).sort_values()\n",
        "    print('Pct change 2019 → latest, by offense:'); print(pct.round(1))\n",
        "else:\n",
        "    print('Need both 2019 and >=2024 in data; current range:', wide.index.min(), '–', wide.index.max())\n",
    ),
    md(
        "## GDELT headline volume — for the perception/reality gap\n",
        "GDELT DOC 2.0 free API; query crime keywords for monthly volume 2019-2025.\n",
        "**TODO:** implement GDELT pull as `nyc_eda/gdelt.py` and join to actual incidents.\n",
    ),
    md("## Verdict\n"),
    code(
        "import numpy as np\n",
        "down_categories = []\n",
        "if 'pct' in dir():\n",
        "    down_categories = [c for c, v in pct.items() if v <= -20]\n",
        "verdict = 'yes' if len(down_categories) >= 3 else ('partial' if len(down_categories) >= 1 else 'no')\n",
        "print(f'SIGNAL: {verdict}')\n",
        "print(f'  categories down ≥20%: {down_categories}')\n",
        "print('  GDELT cross-check pending implementation.')\n",
    ),
    md("## Serendipity\n"),
]


# --------------------------------------------------------------------------- #
# 22_h5_hyperlocal.ipynb — H5 verdict
# --------------------------------------------------------------------------- #

NB22 = [
    md(
        "# 22 — H5: Hyperlocal microscope\n",
        "\n",
        "**Hypothesis:** A single neighborhood, when looked at closely, shows ≥2\n",
        "dataset-crossing storylines (311 + crime + demographic shift). Pick the\n",
        "**non-obvious** NTA with highest narrative density.\n",
    ),
    code(
        "import sys\n",
        "from pathlib import Path\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "sys.path.insert(0, str(PROJECT / 'src'))\n",
        "\n",
        "from nyc_eda import DUCKDB_PATH, CUTS_OUT, GEO_ROOT\n",
        "from nyc_eda.storage import open_db\n",
        "\n",
        "con = open_db(DUCKDB_PATH)\n",
    ),
    md("## Score NTAs by narrative density\n"),
    code(
        "# Spatial-join 311 and NYPD points to NTAs; rank by anomaly count.\n",
        "# Implementation needs geo.join_points_to_polygons over precinct/NTA geometries.\n",
        "# TODO: implement narrative-density score; for now print placeholder.\n",
        "print('TODO: implement NTA narrative-density scoring.')\n",
        "print('SIGNAL: pending')\n",
    ),
    md("## Serendipity\n"),
]


# --------------------------------------------------------------------------- #
# 99_serendipity_review.ipynb
# --------------------------------------------------------------------------- #

NB99 = [
    md(
        "# 99 — Serendipity Review\n",
        "\n",
        "Aggregates `memos/serendipity_log.md` entries; clusters and surfaces top\n",
        "candidates for cross-cutting narrative in the Phase 1 memo.\n",
    ),
    code(
        "from pathlib import Path\n",
        "import re\n",
        "PROJECT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
        "log = (PROJECT / 'memos' / 'serendipity_log.md').read_text()\n",
        "entries = re.split(r'^## ', log, flags=re.MULTILINE)[1:]\n",
        "print(f'{len(entries)} entries in serendipity log')\n",
        "for e in entries[:15]:\n",
        "    title = e.split(chr(10))[0]\n",
        "    print(f'  • {title}')\n",
    ),
]


NOTEBOOKS = {
    "00_acquire.ipynb": NB00,
    "10_cuts_time_geo.ipynb": NB10,
    "11_cuts_demo_offense.ipynb": NB11,
    "20_h1_311_leading.ipynb": NB20,
    "21_h4_good_news.ipynb": NB21,
    "22_h5_hyperlocal.ipynb": NB22,
    "99_serendipity_review.ipynb": NB99,
}


def main() -> None:
    for name, cells in NOTEBOOKS.items():
        path = write_notebook(name, cells)
        print(f"wrote {path.relative_to(ROOT)}  ({len(cells)} cells)")


if __name__ == "__main__":
    main()

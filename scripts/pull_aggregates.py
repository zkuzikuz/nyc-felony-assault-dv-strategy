"""Pull annual aggregates 2017-2024 via SoQL — small payloads, fast.

For the Phase 1 thesis we need yearly counts by offense and by precinct, not full
row-level data. SoQL `$select` with `COUNT(*)` and `$group` returns aggregates
directly, sidestepping the need to pull millions of rows.

Outputs (under data/processed/):
- felony_yearly.parquet           — year × offense → count (citywide)
- law_category_yearly.parquet     — year × law_cat_cd → count (citywide totals)
- felony_precinct_yearly.parquet  — year × precinct × offense → count

Idempotent on file existence.
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from nyc_eda import PROCESSED_ROOT
from nyc_eda.soda import get_client, _backoff_get


YEARS = list(range(2017, 2025))  # 2017-2024 inclusive
DATASET = "qgea-i56i"
OUT_DIR = PROCESSED_ROOT / "aggregates"


def _year_where(y: int) -> str:
    return f"cmplnt_fr_dt >= '{y}-01-01T00:00:00' AND cmplnt_fr_dt < '{y + 1}-01-01T00:00:00'"


def fetch_felony_yearly(client) -> pd.DataFrame:
    """Per-offense annual felony counts, citywide."""
    rows = []
    for y in YEARS:
        page = _backoff_get(
            client,
            DATASET,
            select="ofns_desc, COUNT(*) AS n",
            where=f"law_cat_cd = 'FELONY' AND ofns_desc IS NOT NULL AND {_year_where(y)}",
            group="ofns_desc",
            limit=500,
        )
        for r in page:
            r["year"] = y
            r["n"] = int(r["n"])
        rows.extend(page)
        print(f"  {y}: {len(page)} offense categories")
    return pd.DataFrame(rows)


def fetch_law_category_yearly(client) -> pd.DataFrame:
    """Annual counts by law category (felony / misdemeanor / violation)."""
    rows = []
    for y in YEARS:
        page = _backoff_get(
            client,
            DATASET,
            select="law_cat_cd, COUNT(*) AS n",
            where=_year_where(y),
            group="law_cat_cd",
            limit=20,
        )
        for r in page:
            r["year"] = y
            r["n"] = int(r["n"])
        rows.extend(page)
    return pd.DataFrame(rows)


def fetch_felony_precinct_yearly(client) -> pd.DataFrame:
    """Per-precinct, per-offense, annual felony counts.

    Pulled per (year, offense) to keep individual responses small. ~50 offenses x
    8 years = ~400 queries; each returns ~77 precinct rows. Total ~30K rows."""
    # First, find the top-N offense categories cumulatively to keep the matrix tractable.
    top_offs = _backoff_get(
        client,
        DATASET,
        select="ofns_desc, COUNT(*) AS n",
        where="law_cat_cd = 'FELONY' AND ofns_desc IS NOT NULL "
              "AND cmplnt_fr_dt >= '2017-01-01T00:00:00' AND cmplnt_fr_dt < '2025-01-01T00:00:00'",
        group="ofns_desc",
        order="n DESC",
        limit=20,
    )
    offenses = [r["ofns_desc"] for r in top_offs]
    print(f"  top {len(offenses)} felony offenses to track per precinct")

    rows = []
    for y in YEARS:
        for off in offenses:
            off_safe = off.replace("'", "''")
            page = _backoff_get(
                client,
                DATASET,
                select="addr_pct_cd, COUNT(*) AS n",
                where=(
                    f"law_cat_cd = 'FELONY' AND ofns_desc = '{off_safe}' "
                    f"AND addr_pct_cd IS NOT NULL AND {_year_where(y)}"
                ),
                group="addr_pct_cd",
                limit=200,
            )
            for r in page:
                r["year"] = y
                r["ofns_desc"] = off
                r["n"] = int(r["n"])
            rows.extend(page)
        print(f"  {y}: cumulative rows = {len(rows)}")
    return pd.DataFrame(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = get_client()
    try:
        targets = {
            "felony_yearly": fetch_felony_yearly,
            "law_category_yearly": fetch_law_category_yearly,
            "felony_precinct_yearly": fetch_felony_precinct_yearly,
        }
        for name, fn in targets.items():
            out = OUT_DIR / f"{name}.parquet"
            if out.exists():
                print(f"== {name}: SKIP (exists)")
                continue
            print(f"== {name}: fetching")
            t = time.time()
            df = fn(client)
            df.to_parquet(out, index=False)
            print(f"  -> {out.name}: {len(df):,} rows ({time.time() - t:.1f}s)")
    finally:
        client.close()


if __name__ == "__main__":
    main()

"""Pull annual felony-assault sub-category counts (pd_cd / pd_desc) for 2010, 2014, 2019, 2024.

Decomposes the 72% rise in FELONY ASSAULT (ky_cd=106) into NYPD's internal
classification scheme to determine whether the rise is uniform or concentrated.

Output: data/processed/aggregates/felony_assault_subcategory_yearly.parquet
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from nyc_eda import PROCESSED_ROOT
from nyc_eda.soda import get_client, _backoff_get


YEARS = [2010, 2014, 2019, 2024]
DATASET = "qgea-i56i"
OUT = PROCESSED_ROOT / "aggregates" / "felony_assault_subcategory_yearly.parquet"


def _year_where(y: int) -> str:
    return (
        f"cmplnt_fr_dt >= '{y}-01-01T00:00:00' "
        f"AND cmplnt_fr_dt < '{y + 1}-01-01T00:00:00'"
    )


def fetch(client) -> pd.DataFrame:
    rows = []
    for y in YEARS:
        page = _backoff_get(
            client,
            DATASET,
            select="pd_cd, pd_desc, COUNT(*) AS n",
            where=(
                "ofns_desc = 'FELONY ASSAULT' AND law_cat_cd = 'FELONY' "
                f"AND {_year_where(y)}"
            ),
            group="pd_cd, pd_desc",
            limit=2000,
        )
        for r in page:
            r["year"] = y
            r["n"] = int(r["n"])
        rows.extend(page)
        print(f"  {y}: {len(page)} pd_cd/pd_desc rows, total n={sum(r['n'] for r in page):,}")
    return pd.DataFrame(rows)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print(f"== {OUT.name}: SKIP (exists)")
        return
    client = get_client()
    try:
        t = time.time()
        df = fetch(client)
        df.to_parquet(OUT, index=False)
        print(f"  -> {OUT.name}: {len(df):,} rows ({time.time() - t:.1f}s)")
    finally:
        client.close()


if __name__ == "__main__":
    main()

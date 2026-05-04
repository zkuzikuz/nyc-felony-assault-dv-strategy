"""Pre-COVID baseline pull: structural-vs-COVID-recovery test for the strategy memo.

For each "still rising in 2024" felony category we want to know whether the
post-2020 rise is the continuation of a pre-2010s structural drift, or a
novel COVID-era phenomenon. To answer that we pull two earlier reference
years from the same NYPD `qgea-i56i` table — 2010 and 2014 — using the same
SoQL aggregate pattern as `pull_aggregates.py`, then index every category to
its 2019 baseline and classify it.

Outputs:
- data/processed/aggregates/felony_yearly_precovid.parquet
    year × ofns_desc → n  (years 2010, 2014 only; merge with felony_yearly.parquet
    in analysis to get the full 2010, 2014, 2017-2024 trajectory).

Usage:
    PYTHONPATH=src .venv/bin/python -m scripts.pull_precovid
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from nyc_eda import PROCESSED_ROOT
from nyc_eda.soda import get_client, _backoff_get


PRECOVID_YEARS = [2010, 2014]
DATASET = "qgea-i56i"
OUT_DIR = PROCESSED_ROOT / "aggregates"
OUT_FILE = OUT_DIR / "felony_yearly_precovid.parquet"

# Categories analysed in the precovid_baseline_check memo.
# 7 still-rising-in-2024 + 3 descending-from-peak (for contrast).
RISING_2024 = [
    "FELONY ASSAULT",
    "DANGEROUS DRUGS",
    "DANGEROUS WEAPONS",
    "CRIMINAL MISCHIEF & RELATED OF",
    "MISCELLANEOUS PENAL LAW",
    "FORGERY",
    "POSSESSION OF STOLEN PROPERTY",
]
DESCENDING = [
    "GRAND LARCENY OF MOTOR VEHICLE",  # exact ofns_desc string TBD; we'll match
    "ROBBERY",
    "GRAND LARCENY",
]


def _year_where(y: int) -> str:
    return f"cmplnt_fr_dt >= '{y}-01-01T00:00:00' AND cmplnt_fr_dt < '{y + 1}-01-01T00:00:00'"


def fetch_felony_yearly(client, years: list[int]) -> pd.DataFrame:
    rows = []
    for y in years:
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
        print(f"  {y}: {len(page)} offense categories, {sum(r['n'] for r in page):,} total felonies")
    return pd.DataFrame(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists():
        print(f"== {OUT_FILE.name}: SKIP (exists)")
    else:
        print(f"== fetching pre-COVID felony aggregates for years {PRECOVID_YEARS}")
        client = get_client()
        try:
            t = time.time()
            df = fetch_felony_yearly(client, PRECOVID_YEARS)
            df.to_parquet(OUT_FILE, index=False)
            print(f"  -> {OUT_FILE.name}: {len(df):,} rows ({time.time() - t:.1f}s)")
        finally:
            client.close()

    # Read both parquets and emit a small classification table to stdout.
    pre = pd.read_parquet(OUT_FILE)
    main_df = pd.read_parquet(OUT_DIR / "felony_yearly.parquet")
    full = pd.concat([pre, main_df], ignore_index=True)

    # What ofns_desc strings exist? (helps identify the GLA exact name)
    cats = sorted(full["ofns_desc"].unique())
    print()
    print("== sanity: distinct offense categories across all years")
    for c in cats:
        years_seen = sorted(full.loc[full["ofns_desc"] == c, "year"].unique())
        print(f"  {c}: years {years_seen}")

    # Pivot to year × offense → n
    piv = full.pivot_table(index="ofns_desc", columns="year", values="n", aggfunc="sum").fillna(0)

    # Index to 2019 = 1.00; only categories that appear in all key years.
    key_years = [2010, 2014, 2017, 2018, 2019, 2024]
    available = [y for y in key_years if y in piv.columns]
    print(f"\n== years available in pivot: {available}")

    # For each tested category, print the indexed trajectory and a structural verdict.
    targets = RISING_2024 + DESCENDING

    # Resolve "GRAND LARCENY OF MOTOR VEHICLE" to its actual ofns_desc match.
    resolved = []
    for t in targets:
        if t in piv.index:
            resolved.append(t)
            continue
        # fuzzy: anything containing "GRAND LARCENY" and "MOTOR" maps GLA
        if "MOTOR" in t.upper():
            cand = [c for c in piv.index if "GRAND LARCENY" in c and ("MOTOR" in c or "AUTO" in c)]
            if cand:
                resolved.append(cand[0])
                print(f"  resolved {t!r} -> {cand[0]!r}")
                continue
        print(f"  WARNING: {t!r} not in pivot index")
    targets = resolved

    print("\n== indexed trajectories (2019 = 1.00)")
    print(f"{'category':40s} | " + " ".join(f"{y:>6}" for y in available) + " | classification")
    print("-" * 110)

    classifications = []
    for cat in targets:
        if 2019 not in piv.columns or piv.loc[cat, 2019] == 0:
            print(f"  {cat}: missing 2019 baseline, skip")
            continue
        base = piv.loc[cat, 2019]
        idx = {y: piv.loc[cat, y] / base for y in available}

        # Classification rule:
        #   STRUCTURAL: pre-COVID baseline already trending up
        #      i.e. 2019 > 2010 AND 2019 > 2014 by >=10% (modest rise)
        #   COVID-DRIVEN: pre-2020 was flat or down, post-2020 spike drives the rise
        #      i.e. 2019 <= 2010 OR 2014 <= 2010 with no clear pre-COVID upward drift
        #   DESCENDING: 2024 < 2019 (used for contrast cases)
        v2010 = idx.get(2010, float("nan"))
        v2014 = idx.get(2014, float("nan"))
        v2019 = idx[2019]
        v2024 = idx.get(2024, float("nan"))

        if v2024 < v2019:
            cls = "DESCENDING (contrast)"
        elif v2010 < 0.95 and v2014 <= v2019 and v2014 >= v2010 * 0.95:
            # 2010 well below 2019, with non-decreasing drift through 2014 → structural
            cls = "STRUCTURAL"
        elif v2010 >= 1.05:
            # 2010 was already above 2019 → declining baseline, post-COVID rebound
            cls = "COVID-DRIVEN (rebound)"
        elif abs(v2010 - 1.0) < 0.10 and abs(v2014 - 1.0) < 0.10:
            # near-flat 2010-2019 → COVID-driven
            cls = "COVID-DRIVEN (flat baseline)"
        else:
            cls = "MIXED"

        traj = " ".join(f"{idx[y]:>6.2f}" for y in available)
        print(f"{cat:40s} | {traj} | {cls}")
        classifications.append({"category": cat, **{f"y{y}": idx[y] for y in available}, "classification": cls})

    cls_df = pd.DataFrame(classifications)
    print()
    print("== summary of 7 still-rising categories")
    rising_only = cls_df[cls_df["category"].isin(RISING_2024)]
    print(rising_only["classification"].value_counts())


if __name__ == "__main__":
    main()

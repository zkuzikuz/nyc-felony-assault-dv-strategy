"""Build the site/ data assets from the project sources.

Run once (or whenever underlying data changes):
    .venv/bin/python scripts/build_site_data.py

This copies the 14 chart PNGs from figures/sketches/ to site/assets/charts/,
copies the precinct geojson, generates per-precinct stats JSON, and writes
hand-curated baseline data for the multi-baseline interactive chart.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Map source filename in figures/sketches/ to dest filename in site/assets/charts/
RENAME_MAP = {
    "01_hero_bignumber.png": "01-hero.png",
    "02_situation_majors.png": "02-majors.png",
    "03_dv_split.png": "03-dv-split.png",
    "04_complication_stacked.png": "04-stacked.png",
    "05_trajectories.png": "05-trajectories.png",
    "06_precinct_growth.png": "06-precinct-growth.png",
    "07_beds.png": "07-beds.png",
    "08_distal.png": "08-distal.png",
    "09_bheard_breakdown.png": "09-bheard-breakdown.png",
    "10_bheard_coverage.png": "10-bheard-coverage.png",
    "11_timeline.png": "11-timeline.png",
    "12_dv_rank.png": "12-dv-rank.png",
    "13_quadrant.png": "13-quadrant.png",
    "14_baselines.png": "14-baselines.png",
}


def copy_charts(src_dir: Path, dst_dir: Path) -> None:
    """Copy the 14 sketches to dst_dir with renamed filenames."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in RENAME_MAP.items():
        src = src_dir / src_name
        if not src.exists():
            raise FileNotFoundError(f"Missing source chart: {src}")
        shutil.copy2(src, dst_dir / dst_name)


def copy_geojson(src: Path, dst: Path) -> None:
    """Copy the precinct geojson to the site data dir."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_precinct_stats(parquet_path: Path, out_path: Path) -> None:
    """Convert per-precinct felony-assault counts to a JSON the precinct-map JS reads."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(parquet_path)
    fa = df[df.ofns_desc == "FELONY ASSAULT"].copy()
    fa.addr_pct_cd = pd.to_numeric(fa.addr_pct_cd, errors="coerce")
    pivot = fa.pivot_table(
        index="addr_pct_cd", columns="year", values="n", aggfunc="sum"
    ).fillna(0)
    rows = []
    for pct in pivot.index:
        if pd.isna(pct):
            continue
        c2017 = float(pivot.loc[pct].get(2017, 0))
        c2024 = float(pivot.loc[pct].get(2024, 0))
        if c2017 == 0:
            continue
        rows.append({
            "precinct": int(pct),
            "count_2017": int(c2017),
            "count_2024": int(c2024),
            "pct_change": round((c2024 / c2017 - 1) * 100, 1),
        })
    rows.sort(key=lambda r: r["precinct"])
    out_path.write_text(json.dumps(rows, indent=2))


def write_baseline_data(out_path: Path) -> None:
    """Hand-curated values from the memo for the multi-baseline interactive chart."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "one_year": {
            "label": "1-year (2023 to 2024)",
            "value": 5.8,
            "note": "NYPD year-end 2024 reporting.",
        },
        "five_year": {
            "label": "5-year (2019 to 2024)",
            "value": 41.4,
            "note": "Indexed off 2019 (pre-COVID baseline).",
        },
        "decade": {
            "headline": 72,
            "adjusted": 47,
            "label": "Decade (2010 to 2024)",
            "note": "Adjusted figure subtracts Strangulation 1st reclassification from both endpoints.",
        },
        "national": {
            "label": "National context",
            "nyc_adjusted": 47,
            "us_national": 2,
            "ccj_24_city": 4,
            "la_yoy": -10,
            "note": "NYC's reclassification-adjusted decade rise vs FBI national rate, "
                    "Council on Criminal Justice 24-city sample, and LAPD 2024 year-over-year.",
        },
    }
    out_path.write_text(json.dumps(data, indent=2))


def main() -> None:
    site_dir = ROOT / "site"
    copy_charts(ROOT / "figures" / "sketches", site_dir / "assets" / "charts")
    copy_geojson(ROOT / "data" / "geo" / "precincts.geojson", site_dir / "data" / "precincts.geojson")
    build_precinct_stats(
        ROOT / "data" / "processed" / "aggregates" / "felony_precinct_yearly.parquet",
        site_dir / "data" / "precinct-stats.json",
    )
    write_baseline_data(site_dir / "data" / "baseline-data.json")
    print(f"Wrote site assets to {site_dir}")


if __name__ == "__main__":
    main()

"""End-to-end Phase 0 pipeline runner.

Runs all cuts that don't require unimplemented external joins (ACS, GDELT) and
saves outputs to data/processed/cuts/. Use this when iterating on cuts without
spinning up Jupyter; the notebooks are the presentable rendition of the same
operations.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/run_pipeline.py
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nyc_eda import DUCKDB_PATH, RAW_ROOT, GEO_ROOT, CUTS_OUT, DATASETS  # noqa: E402
from nyc_eda.storage import open_db, register_dataset, register_geojson, install_spatial  # noqa: E402
from nyc_eda import cuts  # noqa: E402
from nyc_eda.stats import lagged_correlation, permutation_test_lag  # noqa: E402


def register_views(con) -> None:
    install_spatial(con)
    for name, info in DATASETS.items():
        n = register_dataset(con, f"r_{name}", RAW_ROOT, info["id"])
        print(f"  r_{name}: {n:,} rows")

    # Defensive: if a partition view is empty (no data pulled), the UNION still works.
    con.execute("""
        CREATE OR REPLACE VIEW v_nypd AS
        SELECT cmplnt_num, cmplnt_fr_dt, cmplnt_fr_tm, addr_pct_cd, boro_nm,
               ofns_desc, ky_cd, law_cat_cd, latitude, longitude, prem_typ_desc,
               susp_age_group, susp_race, susp_sex, vic_age_group, vic_race, vic_sex
        FROM r_nypd_main
        UNION ALL
        SELECT cmplnt_num, cmplnt_fr_dt, cmplnt_fr_tm, addr_pct_cd, boro_nm,
               ofns_desc, ky_cd, law_cat_cd, latitude, longitude, prem_typ_desc,
               susp_age_group, susp_race, susp_sex, vic_age_group, vic_race, vic_sex
        FROM r_nypd_ytd
    """)
    con.execute("""
        CREATE OR REPLACE VIEW v_311 AS
        SELECT unique_key, created_date, closed_date, agency, complaint_type, descriptor,
               incident_zip, incident_address, latitude, longitude, borough, community_board,
               police_precinct, council_district, status, resolution_description
        FROM r_311_modern
        UNION ALL
        SELECT unique_key, created_date, closed_date, agency, complaint_type, descriptor,
               incident_zip, incident_address, latitude, longitude, borough, community_board,
               police_precinct, council_district, status, resolution_description
        FROM r_311_historic
    """)

    for v_name, geo_path in [
        ("g_precincts", GEO_ROOT / "precincts.geojson"),
        ("g_ntas", GEO_ROOT / "ntas.geojson"),
    ]:
        if geo_path.exists():
            n = register_geojson(con, v_name, geo_path)
            print(f"  {v_name}: {n} polygons")
        else:
            print(f"  {v_name}: SKIP (geojson not pulled yet)")

    for v in ["v_nypd", "v_311"]:
        n = con.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
        print(f"  {v}: {n:,} rows")


def run_basic_cuts(con) -> dict[str, str]:
    """Run cuts that work on whatever data is registered. Returns {cut_id: status}."""
    CUTS_OUT.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}

    def run(cut_id: str, fn, *args, save_csv: bool = True, **kwargs):
        try:
            df = fn(*args, **kwargs)
            if save_csv:
                df.to_csv(CUTS_OUT / f"{cut_id}.csv", index=False)
            results[cut_id] = f"OK ({len(df)} rows)"
        except Exception as e:
            results[cut_id] = f"FAIL: {type(e).__name__}: {e}"
            traceback.print_exc(file=sys.stderr)

    run("C1_calendar_year",       cuts.c1_calendar_year,        con)
    run("C2_seasonality",         cuts.c2_month_seasonality,    con)
    run("C3_covid_step",          cuts.c3_covid_step,           con)
    run("C4_dow_hour",            cuts.c4_dow_hour,             con)
    run("C5_borough",             cuts.c5_borough,              con)
    run("C6_precinct",            cuts.c6_precinct,             con)
    run("C13_311_top",            cuts.c13_311_complaint_types, con)
    run("C14_law_category",       cuts.c14_law_category,        con)
    run("C15_top_felony",         cuts.c15_top_felony_offenses, con)
    run("C19_repeat_addr",        cuts.c19_repeat_address_311,  con)
    run("C20_resolution_time",    cuts.c20_resolution_time_by_agency, con)
    return results


def run_h1_lag(con) -> dict:
    """Run the H1 lag-scan analysis end to end. Returns a verdict dict."""
    panel = cuts.c16_qol311_x_majorfelony(con)
    if panel.empty:
        return {"verdict": "no-data", "reason": "C16 panel is empty"}
    panel.to_csv(CUTS_OUT / "C16_qol_x_felony.csv", index=False)

    lag_results = cuts.c17_lag_scan_per_precinct(panel, max_lag=12)
    lag_results.to_csv(CUTS_OUT / "C17_lag_scan.csv", index=False)

    city = (
        panel.groupby("month")
        .agg(qol_311=("qol_311", "sum"), major_felony=("major_felony", "sum"))
        .reset_index()
    )
    city_lag = lagged_correlation(city["qol_311"], city["major_felony"], max_lag=12)
    city_lag.to_csv(CUTS_OUT / "C17_city_lag.csv", index=False)

    if city_lag["r"].dropna().empty:
        return {"verdict": "no-data", "reason": "no valid lag correlations"}

    best_idx = city_lag["r"].idxmax()
    best_lag = int(city_lag.loc[best_idx, "lag"])
    best_r = float(city_lag.loc[best_idx, "r"])
    lag0_row = city_lag[city_lag["lag"] == 0]
    lag0_r = float(lag0_row["r"].iloc[0]) if len(lag0_row) else float("nan")

    perm = permutation_test_lag(city["qol_311"], city["major_felony"], lag=best_lag, n_perm=2000)

    if best_r >= 0.35 and (best_r - lag0_r) > 0.05 and perm["p_perm"] < 0.05:
        verdict = "yes"
    elif best_r < 0.20:
        verdict = "no"
    else:
        verdict = "partial"
    return {
        "verdict": verdict,
        "best_lag": best_lag,
        "best_r": round(best_r, 3),
        "lag0_r": round(lag0_r, 3),
        "perm_p": round(float(perm["p_perm"]), 4),
        "n_precincts": int(panel["precinct"].nunique()),
        "n_months": int(panel["month"].nunique()),
    }


def run_h4_good_news(con) -> dict:
    """Run H4 trend analysis: which felony categories are down 2019→latest year?"""
    df = cuts.c15_top_felony_offenses(con, top_n=15)
    if df.empty:
        return {"verdict": "no-data", "reason": "C15 returned no rows"}
    wide = df.pivot(index="year", columns="ofns_desc", values="n").fillna(0)
    if 2019 not in wide.index:
        return {"verdict": "no-data", "reason": "missing 2019 baseline"}
    latest_year = int(wide.index.max())
    if latest_year < 2024:
        return {"verdict": "no-data", "reason": f"latest year is {latest_year}, need ≥2024"}
    base = wide.loc[2019]
    latest = wide.loc[latest_year]
    pct = ((latest - base) / base * 100).round(1)
    pct_sorted = pct.sort_values()
    pct_sorted.to_csv(CUTS_OUT / "H4_pct_change.csv")

    down_20 = [c for c, v in pct.items() if v <= -20]
    up_20 = [c for c, v in pct.items() if v >= 20]
    if len(down_20) >= 3:
        verdict = "yes"
    elif len(down_20) >= 1:
        verdict = "partial"
    else:
        verdict = "no"
    return {
        "verdict": verdict,
        "baseline_year": 2019,
        "compare_year": latest_year,
        "categories_down_20pct": down_20,
        "categories_up_20pct": up_20,
        "pct_change": {k: float(v) for k, v in pct_sorted.items()},
        "note": "GDELT perception/reality cross-check is pending implementation; verdict is data-trend-only.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-h1", action="store_true", help="skip H1 lag analysis")
    parser.add_argument("--skip-h4", action="store_true", help="skip H4 trend analysis")
    args = parser.parse_args()

    print(f"opening duckdb: {DUCKDB_PATH}")
    con = open_db(DUCKDB_PATH)

    print("\n=== registering views ===")
    register_views(con)

    print("\n=== running cuts ===")
    cut_results = run_basic_cuts(con)
    for cut_id, status in cut_results.items():
        print(f"  {cut_id}: {status}")

    if not args.skip_h1:
        print("\n=== H1 lag analysis ===")
        try:
            h1 = run_h1_lag(con)
            print(f"  H1 result: {h1}")
        except Exception as e:
            print(f"  H1 FAILED: {type(e).__name__}: {e}")
            traceback.print_exc(file=sys.stderr)

    if not args.skip_h4:
        print("\n=== H4 trend analysis ===")
        try:
            h4 = run_h4_good_news(con)
            print(f"  H4 verdict: {h4.get('verdict')}")
            print(f"  baseline {h4.get('baseline_year')} → compare {h4.get('compare_year')}")
            print(f"  categories down ≥20%: {h4.get('categories_down_20pct')}")
            print(f"  categories up   ≥20%: {h4.get('categories_up_20pct')}")
        except Exception as e:
            print(f"  H4 FAILED: {type(e).__name__}: {e}")
            traceback.print_exc(file=sys.stderr)

    print("\nartifacts under:", CUTS_OUT)


if __name__ == "__main__":
    main()

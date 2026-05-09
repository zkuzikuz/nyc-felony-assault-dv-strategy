"""Export per-chart data files for the Observable Plot chart modules.

Reads from data/processed/aggregates/ where applicable; writes JSON files to
site/data/<chart>.json. Re-run any time the upstream parquet files change.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "data" / "processed" / "aggregates"
OUT = ROOT / "site" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def _write(name: str, payload) -> None:
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2))
    print(f"  wrote {path.relative_to(ROOT)}")


def chart_01_hero() -> None:
    """Naive vs adjusted (excluding Strangulation 1st) yearly totals, 2010-2024."""
    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    fa_total = sub.groupby("year")["n"].sum().sort_index()
    strang = (
        sub[sub.pd_desc == "STRANGULATION 1ST"]
        .set_index("year")["n"]
        .reindex(fa_total.index, fill_value=0)
    )
    fa_excl = fa_total - strang
    pct_naive = (fa_total.iloc[-1] / fa_total.iloc[0] - 1) * 100
    pct_adj = (fa_excl.iloc[-1] / fa_excl.iloc[0] - 1) * 100

    data_years = fa_total.index.tolist()
    full_years = list(range(2010, 2025))
    naive_full = pd.Series(index=full_years, dtype=float)
    naive_full.loc[data_years] = fa_total.values
    naive_full = naive_full.interpolate()
    excl_full = pd.Series(index=full_years, dtype=float)
    excl_full.loc[data_years] = fa_excl.values
    excl_full = excl_full.interpolate()

    payload = {
        "headline_pct": int(round(pct_naive)),
        "adjusted_pct": int(round(pct_adj)),
        "data_years": [int(y) for y in data_years],
        "series": [
            {
                "year": int(y),
                "naive": float(round(naive_full.loc[y], 1)),
                "adjusted": float(round(excl_full.loc[y], 1)),
                "is_data_year": int(y) in data_years,
            }
            for y in full_years
        ],
    }
    _write("chart-01", payload)


def chart_02_felony_categories() -> None:
    """2024 violent-felony category totals, descending."""
    fy = pd.read_parquet(AGG / "felony_yearly.parquet")
    keep = ["FELONY ASSAULT", "ROBBERY", "RAPE", "MURDER & NON-NEGL. MANSLAUGHTER"]
    f2024 = fy[(fy.year == 2024) & (fy.ofns_desc.isin(keep))]
    label_map = {
        "FELONY ASSAULT": "Felony Assault",
        "ROBBERY": "Robbery",
        "RAPE": "Rape",
        "MURDER & NON-NEGL. MANSLAUGHTER": "Murder",
    }
    rows = [
        {"category": label_map[r.ofns_desc], "value": int(r.n)}
        for r in f2024.itertuples()
    ]
    rows.sort(key=lambda r: r["value"], reverse=True)
    _write("chart-02", rows)


def chart_12_dv_rank() -> None:
    rows = [
        {
            "label": "LAP (Maryland, Koppa JEBO 2024)",
            "short": "LAP",
            "lo": 35, "hi": 45, "mid": 40,
            "cost": "$3-8M / yr",
            "description": "Police screen DV calls with an 11-question lethality scale; high-risk survivors get a live advocate hotline call on scene.",
            "recommended": True,
        },
        {
            "label": "OFDVI (High Point, Sechrist & Weil 2018)",
            "short": "OFDVI",
            "lo": 12, "hi": 28, "mid": 20,
            "cost": "$2-5M / yr",
            "description": "Focused-deterrence call-in: high-risk offenders are warned of consequences and offered services.",
            "recommended": True,
        },
        {
            "label": "Mandatory arrest (Sherman & Berk MDVE)",
            "short": "MDVE",
            "lo": 5, "hi": 21, "mid": 13,
            "cost": "Statutory — minimal cost",
            "description": "Police arrest rather than separate parties at DV incidents.",
            "recommended": False,
        },
        {
            "label": "Batterer programs (Duluth / CBT)",
            "short": "Batterer",
            "lo": -5, "hi": 5, "mid": 0,
            "cost": "$3-7M / yr",
            "description": "Court-mandated cognitive-behavioral group programs for DV offenders.",
            "recommended": False,
        },
        {
            "label": "CVI / credible-messenger for DV",
            "short": "CVI-DV",
            "lo": 0, "hi": 0, "mid": 0,
            "cost": "Untested — no cost basis",
            "description": "Community-based credible-messenger intervention adapted from gun violence to DV.",
            "recommended": False,
            "untested": True,
        },
    ]
    _write("chart-12", rows)


def chart_03_dv_split() -> None:
    payload = {
        "growth": [
            {"label": "Domestic + elder assault", "pct": 73, "color": "dv"},
            {"label": "Other felony assault", "pct": 40, "color": "neutral"},
        ],
        "share": {
            "total_2024": 29501,
            "dv_share_pct": 39,
            "dv_count": 11505,
            "other_count": 17996,
        },
    }
    _write("chart-03", payload)


def chart_04_stacked() -> None:
    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    pivot = sub.pivot_table(index="year", columns="pd_desc", values="n", aggfunc="sum").fillna(0)
    pivot = pivot.sort_index()
    plot_cols = ["ASSAULT 2,1,UNCLASSIFIED", "ASSAULT POLICE/PEACE OFFICER", "STRANGULATION 1ST"]
    other = pivot.drop(columns=plot_cols, errors="ignore").sum(axis=1)
    pivot["OTHER"] = other

    rows = []
    for year in pivot.index:
        catch_all = float(pivot.loc[year, "ASSAULT 2,1,UNCLASSIFIED"])
        total = float(pivot.loc[year].drop(["OTHER"]).sum() + pivot.loc[year, "OTHER"])
        dv_layer = min(total * 0.39, catch_all)
        other_catch = catch_all - dv_layer
        rows.append({
            "year": int(year),
            "dv_in_catchall": int(round(dv_layer)),
            "other_in_catchall": int(round(other_catch)),
            "police_assault": int(pivot.loc[year, "ASSAULT POLICE/PEACE OFFICER"]),
            "strangulation": int(pivot.loc[year, "STRANGULATION 1ST"]),
            "other_subcats": int(pivot.loc[year, "OTHER"]),
            "total": int(round(total)),
        })
    baseline_2010 = rows[0]["total"]
    _write("chart-04", {"rows": rows, "baseline_2010": baseline_2010})


def chart_05_trajectories() -> None:
    fy = pd.read_parquet(AGG / "felony_yearly.parquet")
    focal = "FELONY ASSAULT"
    others = ["MURDER & NON-NEGL. MANSLAUGHTER", "RAPE", "ROBBERY"]
    keep = [focal] + others
    fy = fy[fy.ofns_desc.isin(keep) & (fy.year.between(2017, 2024))].copy()
    base17 = fy[fy.year == 2017].set_index("ofns_desc")["n"]
    label_map = {
        "FELONY ASSAULT": "Felony Assault",
        "ROBBERY": "Robbery",
        "MURDER & NON-NEGL. MANSLAUGHTER": "Murder",
        "RAPE": "Rape",
    }
    series = {}
    for ofns in keep:
        g = fy[fy.ofns_desc == ofns].sort_values("year")
        series[label_map[ofns]] = [
            {"year": int(r.year), "value": float(round(r.n / base17[ofns], 4))}
            for r in g.itertuples()
        ]
    _write("chart-05", {
        "focal": "Felony Assault",
        "series": series,
    })


def chart_07_beds() -> None:
    payload = {
        "rows": [
            {"label": "Today (existing)", "bth": 100, "safehaven": 900, "total": 1000},
            {"label": "Recommended (double over 18 months)", "bth": 200, "safehaven": 1800, "total": 2000},
        ],
        "target": 2000,
    }
    _write("chart-07", payload)


def chart_08_distal() -> None:
    bed_years = [2014, 2021]
    bed_values_raw = [3050, 2300]
    bed_index = [v / bed_values_raw[0] * 100 for v in bed_values_raw]

    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    fa_total = sub.groupby("year")["n"].sum().sort_index()
    fa_2014 = float(fa_total.loc[2014])

    payload = {
        "fa": [
            {"year": int(y), "raw": int(v), "index": float(round(v / fa_2014 * 100, 2))}
            for y, v in fa_total.items()
        ],
        "beds": [
            {"year": int(y), "raw": int(v), "index": float(round(idx, 2))}
            for y, v, idx in zip(bed_years, bed_values_raw, bed_index)
        ],
    }
    _write("chart-08", payload)


def chart_09_bheard() -> None:
    segments = [
        {"label": "Got a B-HEARD team", "value": 24071, "color": "structural"},
        {"label": "In-hours, no B-HEARD", "value": 13042, "color": "assault"},
        {"label": "Overnight (no service)", "value": 14200, "color": "dv"},
    ]
    payload = {
        "segments": segments,
        "total": sum(s["value"] for s in segments),
    }
    _write("chart-09", payload)


def chart_10_bheard_coverage() -> None:
    """Per-precinct 2024 felony-assault counts + B-HEARD coverage flag."""
    fpy = pd.read_parquet(AGG / "felony_precinct_yearly.parquet")
    fa = fpy[(fpy.ofns_desc == "FELONY ASSAULT") & (fpy.year == 2024)].copy()
    fa.addr_pct_cd = pd.to_numeric(fa.addr_pct_cd, errors="coerce")
    bheard = set(
        [25, 26, 28, 30, 32, 33, 34]
        + [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52]
        + [63, 67, 69, 71, 73, 75]
        + [104, 108, 110, 112, 114, 115]
    )
    rows = []
    for r in fa.itertuples():
        if pd.isna(r.addr_pct_cd):
            continue
        p = int(r.addr_pct_cd)
        rows.append({
            "precinct": p,
            "count_2024": int(r.n),
            "bheard": p in bheard,
        })
    rows.sort(key=lambda r: r["precinct"])

    cov_vals = [r["count_2024"] for r in rows if r["bheard"]]
    unc_vals = [r["count_2024"] for r in rows if not r["bheard"]]
    cov_mean = sum(cov_vals) / len(cov_vals) if cov_vals else 0.0
    unc_mean = sum(unc_vals) / len(unc_vals) if unc_vals else 0.0

    payload = {
        "stats": [r for r in rows],
        "summary": {
            "covered_count": len(cov_vals),
            "uncovered_count": len(unc_vals),
            "covered_mean": int(round(cov_mean)),
            "uncovered_mean": int(round(unc_mean)),
            "ratio": float(round(cov_mean / unc_mean, 2)) if unc_mean else None,
        },
    }
    _write("chart-10", payload)


def chart_11_timeline() -> None:
    payload = {
        "rows": [
            {"label": "Precinct selection + civil-liberties impact assessment", "start": 0, "end": 6, "color": "neutral"},
            {"label": "Pilot rollout (4–6 precincts)", "start": 6, "end": 18, "color": "assault"},
            {"label": "Interim evaluation", "start": 16, "end": 20, "color": "light"},
            {"label": "Phase-1 evaluation cycle", "start": 6, "end": 30, "color": "assault"},
            {"label": "Sunset gate", "start": 29, "end": 31, "color": "structural"},
        ],
        "sunset_at": 30,
    }
    _write("chart-11", payload)


def chart_13_quadrant() -> None:
    rows = [
        {"label": "LAP (Maryland)",          "x": 2.55, "y": 3.05, "color": "assault",    "size": 540, "is_anchor": True},
        {"label": "OFDVI (High Point)",      "x": 2.10, "y": 2.75, "color": "assault",    "size": 440, "is_anchor": True},
        {"label": "Mandatory arrest (MDVE)", "x": 2.85, "y": 2.85, "color": "neutral",    "size": 380, "is_anchor": False},
        {"label": "Batterer programs",       "x": 2.45, "y": 2.55, "color": "light",      "size": 380, "is_anchor": False},
        {"label": "CMS-for-DV",              "x": 0.40, "y": 2.40, "color": "dv",         "size": 380, "is_anchor": False},
        {"label": "CMS / Cure Violence",     "x": 2.50, "y": 0.55, "color": "neutral",    "size": 380, "is_anchor": False},
        {"label": "B-HEARD",                 "x": 2.00, "y": 1.20, "color": "neutral",    "size": 380, "is_anchor": False},
        {"label": "Hot-spots policing",      "x": 3.00, "y": 0.40, "color": "neutral",    "size": 380, "is_anchor": False},
        {"label": "BAM (Heller)",            "x": 2.95, "y": 0.25, "color": "neutral",    "size": 380, "is_anchor": False},
        {"label": "NYC Ceasefire",           "x": 1.60, "y": 0.30, "color": "neutral",    "size": 380, "is_anchor": False},
    ]
    _write("chart-13", {"rows": rows})


def main() -> None:
    chart_01_hero()
    chart_02_felony_categories()
    chart_03_dv_split()
    chart_04_stacked()
    chart_05_trajectories()
    chart_07_beds()
    chart_08_distal()
    chart_09_bheard()
    chart_10_bheard_coverage()
    chart_11_timeline()
    chart_12_dv_rank()
    chart_13_quadrant()


if __name__ == "__main__":
    main()

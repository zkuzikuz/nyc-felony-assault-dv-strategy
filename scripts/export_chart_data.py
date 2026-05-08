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


def main() -> None:
    chart_02_felony_categories()
    chart_12_dv_rank()


if __name__ == "__main__":
    main()

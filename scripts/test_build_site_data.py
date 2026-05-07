"""Tests for scripts/build_site_data.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_chart_renames_complete():
    """All 14 charts must be present in site/assets/charts/ with renamed paths."""
    from scripts.build_site_data import RENAME_MAP, copy_charts
    site_dir = ROOT / "site"
    copy_charts(ROOT / "figures" / "sketches", site_dir / "assets" / "charts")
    expected = {
        "01-hero.png", "02-majors.png", "03-dv-split.png",
        "04-stacked.png", "05-trajectories.png", "06-precinct-growth.png",
        "07-beds.png", "08-distal.png", "09-bheard-breakdown.png",
        "10-bheard-coverage.png", "11-timeline.png", "12-dv-rank.png",
        "13-quadrant.png", "14-baselines.png",
    }
    actual = {p.name for p in (site_dir / "assets" / "charts").glob("*.png")}
    assert expected.issubset(actual), f"Missing: {expected - actual}"
    assert len(RENAME_MAP) == 14


def test_precinct_stats_shape():
    """precinct-stats.json must include count_2017, count_2024, pct_change per precinct."""
    from scripts.build_site_data import build_precinct_stats
    out_path = ROOT / "site" / "data" / "precinct-stats.json"
    build_precinct_stats(
        ROOT / "data" / "processed" / "aggregates" / "felony_precinct_yearly.parquet",
        out_path,
    )
    data = json.loads(out_path.read_text())
    assert isinstance(data, list)
    assert len(data) >= 76, "Expected at least 76 precincts with both 2017 and 2024 data"
    sample = data[0]
    assert set(sample.keys()) == {"precinct", "count_2017", "count_2024", "pct_change"}
    assert isinstance(sample["precinct"], int)
    assert isinstance(sample["pct_change"], (int, float))


def test_baseline_data_shape():
    """baseline-data.json must include four panels with the values from the memo."""
    from scripts.build_site_data import write_baseline_data
    out_path = ROOT / "site" / "data" / "baseline-data.json"
    write_baseline_data(out_path)
    data = json.loads(out_path.read_text())
    assert set(data.keys()) == {"one_year", "five_year", "decade", "national"}
    assert data["decade"]["adjusted"] == 47
    assert data["national"]["nyc_adjusted"] == 47


def test_geojson_copied():
    """precincts.geojson must be copied to site/data/."""
    from scripts.build_site_data import copy_geojson
    src = ROOT / "data" / "geo" / "precincts.geojson"
    dst = ROOT / "site" / "data" / "precincts.geojson"
    copy_geojson(src, dst)
    assert dst.exists()
    assert dst.stat().st_size > 1000

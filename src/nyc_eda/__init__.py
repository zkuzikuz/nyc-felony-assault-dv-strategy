"""nyc_eda — exploratory analysis package for NYC open data."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
RAW_ROOT = DATA_ROOT / "raw"
GEO_ROOT = DATA_ROOT / "geo"
INTERIM_ROOT = DATA_ROOT / "interim"
PROCESSED_ROOT = DATA_ROOT / "processed"
CUTS_OUT = PROCESSED_ROOT / "cuts"
DUCKDB_PATH = DATA_ROOT / "cache.duckdb"
MEMOS_ROOT = PROJECT_ROOT / "memos"

# Canonical NYC OpenData dataset registry. Date columns are SoQL-queryable timestamps.
DATASETS = {
    # qgea-i56i is mis-named — covers 2006 through 2025 (~9.5M rows), NOT just 2006-2019.
    # Use this as the canonical NYPD source for any year up to and including the
    # most recently completed quarter. See serendipity_log.md (2026-04-26).
    "nypd_main": {
        "id": "qgea-i56i",
        "date_col": "cmplnt_fr_dt",
        "notes": "Canonical NYPD complaint table; 2006-present. Despite the name 'Historic' it is the active full-history dataset.",
    },
    "nypd_ytd": {
        "id": "5uac-w243",
        "date_col": "cmplnt_fr_dt",
        "notes": "Current calendar year only — overlaps with the tail of nypd_main. Has spurious dates (1014, 1015, 1025, etc) — filter at acquisition.",
    },
    "311_modern": {
        "id": "erm2-nwe9",
        "date_col": "created_date",
        "notes": "2020-present. ~tens of millions of rows. No BBL column — see serendipity_log.md.",
    },
    "311_historic": {
        "id": "76ig-c548",
        "date_col": "created_date",
        "notes": "2010-2019 archive; different schema from modern (has bbl, has location_type).",
    },
}

GEO_SOURCES = {
    "precincts": "https://data.cityofnewyork.us/resource/y76i-bdw7.geojson",
    "ntas":      "https://data.cityofnewyork.us/resource/9nt8-h7nd.geojson",
}

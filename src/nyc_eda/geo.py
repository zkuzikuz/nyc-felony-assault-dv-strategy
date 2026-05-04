"""Geometry helpers: precinct + NTA boundaries; point-in-polygon spatial joins."""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

from nyc_eda import GEO_SOURCES


def fetch_geojson(url: str, out_path: Path) -> Path:
    if out_path.exists():
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=180)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    return out_path


def load_precincts(geo_root: Path) -> gpd.GeoDataFrame:
    p = fetch_geojson(GEO_SOURCES["precincts"], geo_root / "precincts.geojson")
    return gpd.read_file(p).to_crs(epsg=4326)


def load_ntas(geo_root: Path) -> gpd.GeoDataFrame:
    p = fetch_geojson(GEO_SOURCES["ntas"], geo_root / "ntas.geojson")
    return gpd.read_file(p).to_crs(epsg=4326)


def join_points_to_polygons(
    df: pd.DataFrame,
    polygons: gpd.GeoDataFrame,
    polygon_id_cols: list[str],
    lat_col: str = "latitude",
    lon_col: str = "longitude",
) -> pd.DataFrame:
    """Spatial-join points (lat/lon columns) to polygons. Returns df with polygon id columns appended.
    Drops rows missing lat/lon."""
    df = df.dropna(subset=[lat_col, lon_col]).copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])
    pts = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326",
    )
    keep = [c for c in polygon_id_cols if c in polygons.columns] + ["geometry"]
    joined = gpd.sjoin(pts, polygons[keep], how="left", predicate="within")
    out_cols = [c for c in polygon_id_cols if c in polygons.columns]
    return joined.drop(columns=["geometry", "index_right"], errors="ignore")[
        list(df.columns) + out_cols
    ]

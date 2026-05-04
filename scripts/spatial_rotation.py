"""Per-precinct rotation analysis: which precincts moved which way 2019 → 2024.

For each precinct, compute its rotation signature — the per-offense change vector
2019 → 2024 — and classify it by which cluster's pattern dominates locally. The
question we want to answer: is the rotation citywide-uniform, or is the auto-theft
surge concentrated in some precincts while the violent-concentration cluster owns
others?

Outputs:
- data/processed/aggregates/precinct_rotation.csv
- data/processed/cuts/H_precinct_rotation.png  (NYC precinct map colored by dominant cluster)
- data/processed/cuts/H_rotation_dispersion.png (boxplot: each cluster's spread across precincts)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from nyc_eda import PROCESSED_ROOT, GEO_ROOT, CUTS_OUT


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    p_yearly = PROCESSED_ROOT / "aggregates" / "felony_precinct_yearly.parquet"
    p_clusters = PROCESSED_ROOT / "aggregates" / "cluster_assignments.csv"
    if not p_yearly.exists():
        sys.exit(f"missing {p_yearly} — run pull_aggregates.py first")
    if not p_clusters.exists():
        sys.exit(f"missing {p_clusters} — run cluster_offenses.py first")
    yearly = pd.read_parquet(p_yearly)
    clusters = pd.read_csv(p_clusters)
    return yearly, clusters


def precinct_rotation(yearly: pd.DataFrame, clusters: pd.DataFrame) -> pd.DataFrame:
    """For each precinct, compute total felony change by cluster 2019 → 2024."""
    df = yearly.merge(clusters[["ofns_desc", "cluster"]], on="ofns_desc", how="inner")
    keep = df["year"].isin([2019, 2024])
    df = df[keep]

    by_pc = (
        df.groupby(["addr_pct_cd", "cluster", "year"])["n"]
        .sum()
        .reset_index()
    )
    pivot = by_pc.pivot_table(
        index=["addr_pct_cd", "cluster"],
        columns="year",
        values="n",
        fill_value=0,
    ).reset_index()
    pivot.columns = ["precinct", "cluster", "n_2019", "n_2024"]
    pivot["abs_change"] = pivot["n_2024"] - pivot["n_2019"]
    pivot["pct_change"] = np.where(
        pivot["n_2019"] > 0,
        (pivot["n_2024"] - pivot["n_2019"]) / pivot["n_2019"] * 100,
        np.nan,
    ).round(1)
    return pivot


def dominant_cluster_per_precinct(rot: pd.DataFrame) -> pd.DataFrame:
    """For each precinct, identify the cluster whose absolute change is largest."""
    idx = rot.groupby("precinct")["abs_change"].idxmax()
    dom = rot.loc[idx, ["precinct", "cluster", "abs_change", "pct_change"]].rename(
        columns={"cluster": "dominant_cluster"}
    )
    return dom.reset_index(drop=True)


def map_dominant_cluster(dom: pd.DataFrame, out: Path) -> None:
    import geopandas as gpd
    geo = gpd.read_file(GEO_ROOT / "precincts.geojson").to_crs(epsg=4326)
    geo["precinct"] = geo["precinct"].astype(str).str.zfill(3)
    dom = dom.copy()
    dom["precinct"] = dom["precinct"].astype(str).str.zfill(3)
    merged = geo.merge(dom, on="precinct", how="left")

    fig, ax = plt.subplots(figsize=(8, 9))
    cluster_ids = sorted(dom["dominant_cluster"].dropna().unique())
    cmap = plt.colormaps.get_cmap("tab10").resampled(len(cluster_ids))
    color_for = {c: cmap(i) for i, c in enumerate(cluster_ids)}
    merged["color"] = merged["dominant_cluster"].map(color_for)
    merged.plot(color=merged["color"].fillna("lightgray"), edgecolor="white", linewidth=0.5, ax=ax)

    handles = [plt.Rectangle((0, 0), 1, 1, color=color_for[c]) for c in cluster_ids]
    ax.legend(handles, [f"Cluster {c}" for c in cluster_ids], loc="upper left", title="Dominant cluster (2019→2024 absolute change)")
    ax.set_title("NYPD precincts by dominant rotation cluster")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(out, dpi=130, bbox_inches="tight")
    plt.close()


def plot_dispersion(rot: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    clusters = sorted(rot["cluster"].dropna().unique())
    data = [rot[rot["cluster"] == c]["pct_change"].dropna().values for c in clusters]
    ax.boxplot(data, labels=[f"Cluster {c}" for c in clusters])
    ax.axhline(0, color="gray", lw=0.5)
    ax.set_ylabel("pct change 2019 → 2024 within precinct")
    ax.set_title("Per-precinct rotation dispersion across clusters")
    plt.tight_layout()
    plt.savefig(out, dpi=130)
    plt.close()


def main():
    yearly, clusters = load_inputs()
    print(f"per-precinct rows: {len(yearly):,}")
    print(f"cluster definitions: {clusters['cluster'].value_counts().to_dict()}")

    rot = precinct_rotation(yearly, clusters)
    dom = dominant_cluster_per_precinct(rot)

    out_dir = PROCESSED_ROOT / "aggregates"
    out_dir.mkdir(parents=True, exist_ok=True)
    rot.to_csv(out_dir / "precinct_rotation.csv", index=False)
    dom.to_csv(out_dir / "precinct_dominant_cluster.csv", index=False)

    print(f"\nrotation per (precinct × cluster): {len(rot):,} rows")
    print(f"\nDominant cluster distribution across precincts:")
    print(dom["dominant_cluster"].value_counts().to_string())

    print("\nPrecincts with the largest single absolute changes (top 10):")
    print(dom.sort_values("abs_change", ascending=False).head(10).to_string(index=False))

    CUTS_OUT.mkdir(parents=True, exist_ok=True)
    map_dominant_cluster(dom, CUTS_OUT / "H_precinct_rotation.png")
    plot_dispersion(rot, CUTS_OUT / "H_rotation_dispersion.png")
    print(f"\nartifacts: {out_dir / 'precinct_rotation.csv'}, "
          f"{CUTS_OUT / 'H_precinct_rotation.png'}, "
          f"{CUTS_OUT / 'H_rotation_dispersion.png'}")


if __name__ == "__main__":
    main()

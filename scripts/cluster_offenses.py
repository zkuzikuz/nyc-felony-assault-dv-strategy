"""Cluster felony offense categories by their 2017-2024 trend vector.

Reads data/processed/aggregates/felony_yearly.parquet, normalizes each offense's
year-over-year trajectory, and runs hierarchical (Ward) clustering. Compares the
empirical cluster solution against the heuristic 4-cluster groupings asserted in
the draft thesis.

Outputs:
- data/processed/aggregates/cluster_assignments.csv
- data/processed/cuts/H_clusters_dendrogram.png
- data/processed/cuts/H_clusters_trends.png
- prints a cluster summary table.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist

from nyc_eda import PROCESSED_ROOT, CUTS_OUT


HEURISTIC = {
    "GRAND LARCENY OF MOTOR VEHICLE": "property_surge",
    "POSSESSION OF STOLEN PROPERTY":  "property_surge",
    "FELONY ASSAULT":      "violent_concentration",
    "DANGEROUS WEAPONS":   "violent_concentration",
    "DANGEROUS DRUGS":     "violent_concentration",
    "FORGERY":             "violent_concentration",   # tentative
    "CRIMINAL MISCHIEF & RELATED OF": "violent_concentration",
    "MISCELLANEOUS PENAL LAW":        "violent_concentration",
    "ROBBERY":  "steady_state",
    "BURGLARY": "steady_state",
    "GRAND LARCENY": "steady_state",
    "SEX CRIMES":  "declining",
    "THEFT-FRAUD": "declining",
    "RAPE":        "declining",
    "OTHER STATE LAWS": "reclassification_artifact",
}

# Categories whose 2017-2024 trajectory is dominated by an NYPD reclassification,
# not an underlying behavior change. Filtered before clustering — confirmed by
# inspection of raw counts (extreme jumps from negligible bases or step changes
# that don't track other categories).
RECLASSIFICATION_OUTLIERS = ("OTHER STATE LAWS", "NYS LAWS-UNCLASSIFIED FELONY")

# Empirical cluster names (assigned after cluster IDs are determined by silhouette
# of mean 2024/2019 ratio: ratio < 1 = "Decline", ratio between 1.0 and 1.25 = "Steady",
# ratio > 1.25 = "Surge").
CLUSTER_NAMES_BY_RATIO = [
    (0.0, 1.0,  "Decline"),
    (1.0, 1.25, "Steady"),
    (1.25, float("inf"), "Surge"),
]


def load_yearly() -> pd.DataFrame:
    p = PROCESSED_ROOT / "aggregates" / "felony_yearly.parquet"
    if not p.exists():
        sys.exit(f"missing {p} — run scripts/pull_aggregates.py first")
    return pd.read_parquet(p)


def build_trend_matrix(df: pd.DataFrame, min_year_total: int = 200) -> pd.DataFrame:
    """Pivot to (offense × year) and keep only offenses with reasonable volume.

    Drops known reclassification outliers (OTHER STATE LAWS, NYS LAWS-UNCLASSIFIED
    FELONY) whose trajectory reflects category re-coding rather than offense rate."""
    wide = df.pivot(index="ofns_desc", columns="year", values="n").fillna(0).astype(int)
    keep = wide.mean(axis=1) >= min_year_total
    wide = wide.loc[keep]
    excluded = [x for x in RECLASSIFICATION_OUTLIERS if x in wide.index]
    if excluded:
        wide = wide.drop(index=excluded)
        print(f"  excluded reclassification outliers: {excluded}")
    return wide


def normalize_trends(wide: pd.DataFrame) -> pd.DataFrame:
    """For each offense, z-score the year-over-year trajectory.

    Two normalizations:
    - Index to 2019 (= 1.0) so all offenses share an anchor year.
    - Then z-score across years so magnitude doesn't dominate the cluster geometry.
    """
    if 2019 not in wide.columns:
        sys.exit("missing 2019 baseline year")
    indexed = wide.div(wide[2019], axis=0)
    z = (indexed.sub(indexed.mean(axis=1), axis=0)
                .div(indexed.std(axis=1).replace(0, 1), axis=0))
    return z


def cluster(trends: pd.DataFrame, k: int = 4):
    """Hierarchical clustering with Ward linkage; returns linkage matrix + labels."""
    Z = linkage(trends.values, method="ward")
    labels = fcluster(Z, t=k, criterion="maxclust")
    return Z, labels


def silhouette_curve(trends: pd.DataFrame, k_range=range(2, 8)) -> pd.DataFrame:
    from sklearn.metrics import silhouette_score
    rows = []
    for k in k_range:
        if k >= len(trends):
            continue
        Z = linkage(trends.values, method="ward")
        labels = fcluster(Z, t=k, criterion="maxclust")
        if len(set(labels)) < 2:
            continue
        s = silhouette_score(trends.values, labels)
        rows.append({"k": k, "silhouette": s})
    return pd.DataFrame(rows)


def plot_dendrogram(Z: np.ndarray, labels: list[str], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    dendrogram(Z, labels=labels, leaf_rotation=80, ax=ax)
    ax.set_title("Felony offense categories — Ward-linkage dendrogram (2017-2024 trend, indexed to 2019)")
    plt.tight_layout()
    plt.savefig(out, dpi=130)
    plt.close()


def plot_cluster_trends(wide_indexed: pd.DataFrame, assignments: pd.DataFrame, out: Path) -> None:
    n_clusters = assignments["cluster"].nunique()
    fig, axes = plt.subplots(1, n_clusters, figsize=(4 * n_clusters, 4), sharey=True)
    if n_clusters == 1:
        axes = [axes]
    for ax, (cl, sub) in zip(axes, assignments.groupby("cluster")):
        for off in sub["ofns_desc"]:
            if off in wide_indexed.index:
                ax.plot(wide_indexed.columns, wide_indexed.loc[off], label=off, alpha=0.85)
        ax.set_title(f"Cluster {cl} (n={len(sub)})")
        ax.set_ylabel("count, indexed to 2019 = 1.0")
        ax.axhline(1.0, color="gray", lw=0.5, linestyle="--")
        ax.legend(fontsize=7, loc="best")
        ax.set_xlabel("year")
    plt.tight_layout()
    plt.savefig(out, dpi=130)
    plt.close()


def main():
    df = load_yearly()
    print(f"loaded felony_yearly: {len(df):,} rows, "
          f"{df['ofns_desc'].nunique()} offenses, "
          f"{df['year'].nunique()} years ({df['year'].min()}-{df['year'].max()})")

    wide = build_trend_matrix(df)
    print(f"after volume filter: {len(wide)} offenses")

    trends = normalize_trends(wide)

    sil = silhouette_curve(trends)
    print("\nsilhouette by k:")
    print(sil.to_string(index=False))

    best_k = int(sil.loc[sil["silhouette"].idxmax(), "k"])
    print(f"\nbest k by silhouette: {best_k}")

    Z, labels = cluster(trends, k=best_k)
    assignments = pd.DataFrame({"ofns_desc": trends.index, "cluster": labels})
    assignments["heuristic"] = assignments["ofns_desc"].map(HEURISTIC).fillna("unclassified")

    indexed = wide.div(wide[2019], axis=0)
    by_cluster_change = (
        assignments.merge(
            indexed[2024].reset_index().rename(columns={2024: "ratio_2024_vs_2019"}),
            on="ofns_desc",
        )
        .groupby("cluster")
        .agg(
            n_offenses=("ofns_desc", "size"),
            mean_2024_index=("ratio_2024_vs_2019", "mean"),
            offenses=("ofns_desc", lambda s: ", ".join(sorted(s))),
        )
        .reset_index()
    )

    # Assign meaningful labels by mean magnitude of change.
    def _name(ratio):
        for lo, hi, label in CLUSTER_NAMES_BY_RATIO:
            if lo <= ratio < hi:
                return label
        return "Other"
    by_cluster_change["label"] = by_cluster_change["mean_2024_index"].map(_name)
    cluster_label_map = dict(zip(by_cluster_change["cluster"], by_cluster_change["label"]))
    assignments["cluster_label"] = assignments["cluster"].map(cluster_label_map)

    print("\nCluster assignments vs heuristic groupings:")
    print(assignments.sort_values(["cluster", "ofns_desc"]).to_string(index=False))
    print("\nCluster summary (mean 2024/2019 index):")
    print(by_cluster_change.to_string(index=False))

    out_dir = PROCESSED_ROOT / "aggregates"
    out_dir.mkdir(parents=True, exist_ok=True)
    assignments.to_csv(out_dir / "cluster_assignments.csv", index=False)
    by_cluster_change.to_csv(out_dir / "cluster_summary.csv", index=False)

    CUTS_OUT.mkdir(parents=True, exist_ok=True)
    plot_dendrogram(Z, list(trends.index), CUTS_OUT / "H_clusters_dendrogram.png")
    plot_cluster_trends(indexed, assignments, CUTS_OUT / "H_clusters_trends.png")
    print(f"\nartifacts: {out_dir / 'cluster_assignments.csv'}, "
          f"{CUTS_OUT / 'H_clusters_dendrogram.png'}, "
          f"{CUTS_OUT / 'H_clusters_trends.png'}")


if __name__ == "__main__":
    main()

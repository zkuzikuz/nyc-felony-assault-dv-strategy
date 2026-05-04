"""Lagged correlations, block-bootstrap CIs, permutation tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


def _corr(method: str, xs: np.ndarray, ys: np.ndarray) -> tuple[float, float]:
    if method == "spearman":
        r, p = spearmanr(xs, ys)
    else:
        r, p = pearsonr(xs, ys)
    return float(r), float(p)


def _aligned(x: pd.Series, y: pd.Series, lag: int) -> tuple[np.ndarray, np.ndarray]:
    """Align x[t] with y[t+lag], drop NAs."""
    if lag > 0:
        xs = x.iloc[:-lag].to_numpy()
        ys = y.iloc[lag:].to_numpy()
    else:
        xs = x.to_numpy()
        ys = y.to_numpy()
    valid = ~(np.isnan(xs) | np.isnan(ys))
    return xs[valid], ys[valid]


def lagged_correlation(
    x: pd.Series,
    y: pd.Series,
    max_lag: int = 12,
    method: str = "pearson",
) -> pd.DataFrame:
    """Correlate x[t] with y[t+k] for k in 0..max_lag. Returns lag, r, p, n."""
    rows = []
    for k in range(max_lag + 1):
        xs, ys = _aligned(x, y, k)
        if len(xs) < 6:
            rows.append({"lag": k, "r": np.nan, "p": np.nan, "n": len(xs)})
            continue
        r, p = _corr(method, xs, ys)
        rows.append({"lag": k, "r": r, "p": p, "n": len(xs)})
    return pd.DataFrame(rows)


def block_bootstrap_ci(
    x: pd.Series,
    y: pd.Series,
    lag: int,
    block_size: int = 3,
    n_boot: int = 2000,
    method: str = "pearson",
    seed: int = 42,
) -> dict:
    """Moving-block bootstrap CI for lagged correlation."""
    rng = np.random.default_rng(seed)
    xs, ys = _aligned(x, y, lag)
    n = len(xs)
    if n < block_size * 2:
        return {"median": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "n": n}
    n_blocks = max(1, n // block_size)
    rs = np.empty(n_boot)
    starts_max = n - block_size + 1
    for i in range(n_boot):
        starts = rng.integers(0, starts_max, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block_size) for s in starts])
        idx = idx[idx < n]
        r, _ = _corr(method, xs[idx], ys[idx])
        rs[i] = r
    return {
        "median": float(np.median(rs)),
        "ci_lo": float(np.percentile(rs, 2.5)),
        "ci_hi": float(np.percentile(rs, 97.5)),
        "n": n,
    }


def permutation_test_lag(
    x: pd.Series,
    y: pd.Series,
    lag: int,
    n_perm: int = 5000,
    method: str = "pearson",
    seed: int = 42,
) -> dict:
    """Two-sided permutation test for null of zero lagged correlation."""
    rng = np.random.default_rng(seed)
    xs, ys = _aligned(x, y, lag)
    if len(xs) < 6:
        return {"r_obs": np.nan, "p_perm": np.nan, "n": len(xs)}
    r_obs, _ = _corr(method, xs, ys)
    rs = np.empty(n_perm)
    for i in range(n_perm):
        ys_perm = rng.permutation(ys)
        rs[i], _ = _corr(method, xs, ys_perm)
    p = float((np.abs(rs) >= np.abs(r_obs)).mean())
    return {"r_obs": float(r_obs), "p_perm": p, "n": len(xs)}

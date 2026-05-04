"""Paginated SODA (NYC OpenData) client with idempotent partitioned writes."""
from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd
from sodapy import Socrata
from tqdm import tqdm

DOMAIN = "data.cityofnewyork.us"
PAGE_SIZE = 50_000
MAX_BACKOFF_ATTEMPTS = 6


def get_client() -> Socrata:
    token = os.environ.get("SODA_APP_TOKEN") or None
    return Socrata(DOMAIN, token, timeout=120)


def _backoff_get(client: Socrata, dataset_id: str, **kwargs):
    delay = 1.0
    for attempt in range(MAX_BACKOFF_ATTEMPTS):
        try:
            return client.get(dataset_id, **kwargs)
        except Exception:
            if attempt == MAX_BACKOFF_ATTEMPTS - 1:
                raise
            time.sleep(delay)
            delay *= 2


def _month_bounds(year: int, month: int) -> tuple[str, str]:
    start = f"{year:04d}-{month:02d}-01T00:00:00"
    end_y, end_m = (year + 1, 1) if month == 12 else (year, month + 1)
    end = f"{end_y:04d}-{end_m:02d}-01T00:00:00"
    return start, end


def _iter_months(start_year: int, start_month: int, end_year: int, end_month: int):
    y, m = start_year, start_month
    while (y, m) <= (end_year, end_month):
        yield y, m
        m += 1
        if m > 12:
            y += 1
            m = 1


def fetch_month(
    dataset_id: str,
    date_col: str,
    year: int,
    month: int,
    raw_root: Path,
    client: Socrata | None = None,
) -> Path:
    """Pull one month of a dataset; write hive-partitioned parquet. Idempotent: re-runs
    are no-ops if the partition file already exists."""
    out_dir = raw_root / dataset_id / f"year={year:04d}" / f"month={month:02d}"
    out_path = out_dir / "part.parquet"
    if out_path.exists():
        return out_path
    out_dir.mkdir(parents=True, exist_ok=True)

    start, end = _month_bounds(year, month)
    where = f"{date_col} >= '{start}' AND {date_col} < '{end}'"
    own_client = client is None
    client = client or get_client()
    try:
        rows: list[dict] = []
        offset = 0
        while True:
            page = _backoff_get(
                client,
                dataset_id,
                where=where,
                limit=PAGE_SIZE,
                offset=offset,
                order=f"{date_col} ASC",
            )
            if not page:
                break
            rows.extend(page)
            if len(page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
    finally:
        if own_client:
            client.close()

    if not rows:
        pd.DataFrame().to_parquet(out_path)
    else:
        pd.DataFrame.from_records(rows).to_parquet(out_path, index=False)
    return out_path


def fetch_range(
    dataset_id: str,
    date_col: str,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    raw_root: Path,
    desc: str | None = None,
) -> list[Path]:
    """Pull a range month-by-month. Idempotent."""
    months = list(_iter_months(start_year, start_month, end_year, end_month))
    client = get_client()
    paths: list[Path] = []
    try:
        for y, m in tqdm(months, desc=desc or f"pull {dataset_id}"):
            paths.append(fetch_month(dataset_id, date_col, y, m, raw_root, client=client))
    finally:
        client.close()
    return paths


def schema_sniff(dataset_id: str, n: int = 5) -> pd.DataFrame:
    """Pull a tiny sample to inspect schema/column names."""
    client = get_client()
    try:
        rows = _backoff_get(client, dataset_id, limit=n)
    finally:
        client.close()
    return pd.DataFrame.from_records(rows or [])

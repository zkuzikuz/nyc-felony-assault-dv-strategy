"""DuckDB views over hive-partitioned parquet."""
from __future__ import annotations

from pathlib import Path

import duckdb


def open_db(db_path: Path) -> duckdb.DuckDBPyConnection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def register_dataset(
    con: duckdb.DuckDBPyConnection,
    view_name: str,
    raw_root: Path,
    dataset_id: str,
) -> int:
    """Register a DuckDB view over hive-partitioned parquet. Returns row count."""
    pattern = str(raw_root / dataset_id / "year=*" / "month=*" / "part.parquet")
    con.execute(
        f"""
        CREATE OR REPLACE VIEW {view_name} AS
        SELECT *
        FROM read_parquet('{pattern}', hive_partitioning=true, union_by_name=true)
        """
    )
    return con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]


def install_spatial(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("INSTALL spatial; LOAD spatial;")


def register_geojson(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    geojson_path: Path,
) -> int:
    install_spatial(con)
    con.execute(
        f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM ST_Read('{geojson_path}')"
    )
    return con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

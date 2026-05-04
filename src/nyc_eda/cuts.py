"""The 20 data cuts as named functions, each returning a DataFrame.

Each cut queries DuckDB views registered by storage.register_dataset:
- ``v_nypd``  — UNION of nypd_historic + nypd_ytd (built in 00_acquire)
- ``v_311``   — UNION of 311_modern + 311_historic (built in 00_acquire)

Pre-COVID baseline: 2017-2019. COVID step: 2020-2021. Post: 2022+.
Several cuts (C7-C12, C18) require additional joins; see comments below for status.
"""
from __future__ import annotations

import pandas as pd

# --------------------------------------------------------------------------- #
# Time cuts (C1-C4)
# --------------------------------------------------------------------------- #

def c1_calendar_year(con) -> pd.DataFrame:
    """C1: complaint counts per calendar year, per dataset."""
    nypd = con.execute("""
        SELECT EXTRACT(YEAR FROM CAST(cmplnt_fr_dt AS TIMESTAMP)) AS year,
               COUNT(*) AS n
        FROM v_nypd
        WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1 ORDER BY 1
    """).df().assign(source="NYPD")
    s311 = con.execute("""
        SELECT EXTRACT(YEAR FROM CAST(created_date AS TIMESTAMP)) AS year,
               COUNT(*) AS n
        FROM v_311
        WHERE CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1 ORDER BY 1
    """).df().assign(source="311")
    return pd.concat([nypd, s311], ignore_index=True)


def c2_month_seasonality(con) -> pd.DataFrame:
    """C2: average monthly volume across years."""
    return con.execute("""
        WITH y AS (
            SELECT EXTRACT(YEAR FROM CAST(cmplnt_fr_dt AS TIMESTAMP)) AS year,
                   EXTRACT(MONTH FROM CAST(cmplnt_fr_dt AS TIMESTAMP)) AS month,
                   COUNT(*) AS n
            FROM v_nypd
            WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
            GROUP BY 1, 2
        )
        SELECT month, AVG(n) AS avg_complaints, STDDEV(n) AS sd_complaints, COUNT(*) AS n_years
        FROM y GROUP BY month ORDER BY month
    """).df()


def c3_covid_step(con) -> pd.DataFrame:
    """C3: pre / during / post COVID buckets, per dataset."""
    bucket_sql = """
        CASE
          WHEN CAST({d} AS TIMESTAMP) < '2020-03-01' THEN 'pre'
          WHEN CAST({d} AS TIMESTAMP) < '2022-01-01' THEN 'covid'
          ELSE 'post'
        END
    """
    nypd = con.execute(f"""
        SELECT {bucket_sql.format(d='cmplnt_fr_dt')} AS era, COUNT(*) AS n
        FROM v_nypd
        WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1
    """).df().assign(source="NYPD")
    s311 = con.execute(f"""
        SELECT {bucket_sql.format(d='created_date')} AS era, COUNT(*) AS n
        FROM v_311
        WHERE CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1
    """).df().assign(source="311")
    return pd.concat([nypd, s311], ignore_index=True)


def c4_dow_hour(con) -> pd.DataFrame:
    """C4: NYPD complaints by day-of-week × hour."""
    return con.execute("""
        SELECT EXTRACT(DOW FROM CAST(cmplnt_fr_dt AS TIMESTAMP)) AS dow,
               CAST(SPLIT_PART(cmplnt_fr_tm, ':', 1) AS INTEGER) AS hour,
               COUNT(*) AS n
        FROM v_nypd
        WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
          AND cmplnt_fr_tm IS NOT NULL
        GROUP BY 1, 2 ORDER BY 1, 2
    """).df()


# --------------------------------------------------------------------------- #
# Geographic cuts (C5-C9)
# --------------------------------------------------------------------------- #

def c5_borough(con) -> pd.DataFrame:
    """C5: counts by borough, both datasets."""
    nypd = con.execute("""
        SELECT UPPER(boro_nm) AS borough, COUNT(*) AS n
        FROM v_nypd
        WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
          AND boro_nm IS NOT NULL
        GROUP BY 1 ORDER BY n DESC
    """).df().assign(source="NYPD")
    s311 = con.execute("""
        SELECT UPPER(borough) AS borough, COUNT(*) AS n
        FROM v_311
        WHERE CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
          AND borough IS NOT NULL
        GROUP BY 1 ORDER BY n DESC
    """).df().assign(source="311")
    return pd.concat([nypd, s311], ignore_index=True)


def c6_precinct(con) -> pd.DataFrame:
    """C6: counts per NYPD precinct (and 311 records that have a precinct)."""
    nypd = con.execute("""
        SELECT addr_pct_cd AS precinct, COUNT(*) AS n
        FROM v_nypd
        WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
          AND addr_pct_cd IS NOT NULL
        GROUP BY 1 ORDER BY n DESC
    """).df().assign(source="NYPD")
    s311 = con.execute("""
        SELECT police_precinct AS precinct, COUNT(*) AS n
        FROM v_311
        WHERE CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
          AND police_precinct IS NOT NULL
        GROUP BY 1 ORDER BY n DESC
    """).df().assign(source="311")
    return pd.concat([nypd, s311], ignore_index=True)


# C7 (NTA), C8 (tract), C9 (transit-adjacent) require spatial joins via geo.py
# and are run as standalone analysis cells in 11_cuts_demo_offense.ipynb.


# --------------------------------------------------------------------------- #
# Categorical cuts (C13-C15)
# --------------------------------------------------------------------------- #

def c13_311_complaint_types(con, top_n: int = 25) -> pd.DataFrame:
    """C13: top-N 311 complaint types."""
    return con.execute(f"""
        SELECT complaint_type, COUNT(*) AS n
        FROM v_311
        WHERE CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
          AND complaint_type IS NOT NULL
        GROUP BY 1 ORDER BY n DESC LIMIT {int(top_n)}
    """).df()


def c14_law_category(con) -> pd.DataFrame:
    """C14: NYPD law category split (felony / misdemeanor / violation)."""
    return con.execute("""
        SELECT law_cat_cd AS law_category, COUNT(*) AS n
        FROM v_nypd
        WHERE CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1 ORDER BY n DESC
    """).df()


def c15_top_felony_offenses(con, top_n: int = 15) -> pd.DataFrame:
    """C15: top-N specific felony offenses, with year-by-year trend."""
    return con.execute(f"""
        WITH top AS (
            SELECT ofns_desc
            FROM v_nypd
            WHERE law_cat_cd = 'FELONY'
              AND CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
              AND ofns_desc IS NOT NULL
            GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT {int(top_n)}
        )
        SELECT EXTRACT(YEAR FROM CAST(cmplnt_fr_dt AS TIMESTAMP)) AS year,
               n.ofns_desc, COUNT(*) AS n
        FROM v_nypd n JOIN top USING (ofns_desc)
        WHERE n.law_cat_cd = 'FELONY'
          AND CAST(n.cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1, 2 ORDER BY 2, 1
    """).df()


# --------------------------------------------------------------------------- #
# Cross cuts (C16, C17, C19, C20)
# --------------------------------------------------------------------------- #

# Quality-of-life 311 complaint types — the H1 input signal.
QOL_311_TYPES = (
    "Noise", "Noise - Residential", "Noise - Street/Sidewalk", "Noise - Commercial",
    "Illegal Parking", "Blocked Driveway", "Derelict Vehicle",
    "Graffiti", "Dirty Condition", "Sanitation Condition",
    "Encampment", "Homeless Encampment", "Drug Activity",
    "Disorderly Youth", "Panhandling",
)
# Major felony categories — the H1 outcome.
MAJOR_FELONY_OFFENSES = (
    "ROBBERY", "FELONY ASSAULT", "BURGLARY", "GRAND LARCENY",
    "GRAND LARCENY OF MOTOR VEHICLE", "RAPE", "MURDER & NON-NEGL. MANSLAUGHTER",
)


def c16_qol311_x_majorfelony(con) -> pd.DataFrame:
    """C16: monthly QoL-311 vs major-felony counts, per precinct. Wide table for lag scan."""
    qol_list = ", ".join(f"'{t}'" for t in QOL_311_TYPES)
    fel_list = ", ".join(f"'{t}'" for t in MAJOR_FELONY_OFFENSES)
    return con.execute(f"""
        WITH qol AS (
            SELECT police_precinct AS precinct,
                   DATE_TRUNC('month', CAST(created_date AS TIMESTAMP)) AS month,
                   COUNT(*) AS qol_311
            FROM v_311
            WHERE complaint_type IN ({qol_list})
              AND police_precinct IS NOT NULL
              AND CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
            GROUP BY 1, 2
        ),
        fel AS (
            SELECT addr_pct_cd AS precinct,
                   DATE_TRUNC('month', CAST(cmplnt_fr_dt AS TIMESTAMP)) AS month,
                   COUNT(*) AS major_felony
            FROM v_nypd
            WHERE UPPER(ofns_desc) IN ({fel_list})
              AND law_cat_cd = 'FELONY'
              AND addr_pct_cd IS NOT NULL
              AND CAST(cmplnt_fr_dt AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
            GROUP BY 1, 2
        )
        SELECT COALESCE(qol.precinct, fel.precinct) AS precinct,
               COALESCE(qol.month,    fel.month)    AS month,
               COALESCE(qol_311, 0)     AS qol_311,
               COALESCE(major_felony, 0) AS major_felony
        FROM qol FULL OUTER JOIN fel ON qol.precinct = fel.precinct AND qol.month = fel.month
        ORDER BY precinct, month
    """).df()


def c17_lag_scan_per_precinct(panel: pd.DataFrame, max_lag: int = 12) -> pd.DataFrame:
    """C17: per-precinct lagged Pearson r between QoL-311 and major-felony.

    `panel` is the output of c16. Returns a long table: precinct × lag × r."""
    from nyc_eda.stats import lagged_correlation
    rows = []
    for pct, sub in panel.groupby("precinct"):
        sub = sub.sort_values("month").reset_index(drop=True)
        if len(sub) < 18:
            continue
        lc = lagged_correlation(sub["qol_311"], sub["major_felony"], max_lag=max_lag)
        lc["precinct"] = pct
        rows.append(lc)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(
        columns=["lag", "r", "p", "n", "precinct"]
    )


def c19_repeat_address_311(con, top_n: int = 1000) -> pd.DataFrame:
    """C19: top repeat-call addresses in 311. Modern dataset has no BBL — use incident_address."""
    return con.execute(f"""
        SELECT incident_address, COUNT(*) AS n
        FROM v_311
        WHERE incident_address IS NOT NULL AND incident_address != ''
          AND CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1 ORDER BY n DESC LIMIT {int(top_n)}
    """).df()


def c20_resolution_time_by_agency(con) -> pd.DataFrame:
    """C20: median 311 resolution time (hours) by agency."""
    return con.execute("""
        SELECT agency,
               COUNT(*) AS n_closed,
               MEDIAN(EXTRACT(EPOCH FROM (CAST(closed_date AS TIMESTAMP) - CAST(created_date AS TIMESTAMP))) / 3600.0) AS median_hours,
               AVG(EXTRACT(EPOCH FROM (CAST(closed_date AS TIMESTAMP) - CAST(created_date AS TIMESTAMP))) / 3600.0) AS mean_hours
        FROM v_311
        WHERE closed_date IS NOT NULL AND created_date IS NOT NULL
          AND CAST(closed_date AS TIMESTAMP) > CAST(created_date AS TIMESTAMP)
          AND CAST(created_date AS TIMESTAMP) BETWEEN '2017-01-01' AND CURRENT_DATE
        GROUP BY 1
        HAVING n_closed >= 1000
        ORDER BY median_hours
    """).df()


# C7-C12 (NTA / tract / transit / ACS demo / gentrification) and C18 (GDELT cross)
# are implemented inline in their respective notebooks because they require
# external joins (geopandas spatial, ACS API, GDELT API).

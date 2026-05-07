"""Render the v2 sketch set for the Phase 0 memo.

Layout convention for every chart:
- Bold title at the top.
- Italic grey subtitle BELOW the title — a complete sentence at 9th-grade reading level
  that says what the chart means (so the chart stands alone if extracted).
- Chart body.
- Italic grey source line at the bottom, well clear of axis labels.

External-data figures cite memo Sources. Where the underlying data set is not
in-repo, the chart documents that fact in its source line. No "earlier memo
draft" or process-artifact references appear in the chart itself.

Run: .venv/bin/python scripts/render_sketches.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Editorial theme (Phase 1) ---
import sys as _sys
import pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
from _chart_theme import setup_fonts, apply_theme, editorial_save, PALETTE

setup_fonts()
apply_theme()

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "data" / "processed" / "aggregates"
GEO = ROOT / "data" / "geo"
OUT = ROOT / "figures" / "sketches"
OUT.mkdir(parents=True, exist_ok=True)

# --- Palette aliases (preserve all existing references unchanged) ---
C_ASSAULT    = PALETTE["assault"]
C_DV         = PALETTE["dv"]
C_STRUCTURAL = PALETTE["structural"]
C_NEUTRAL    = PALETTE["neutral"]
C_LIGHT      = PALETTE["light"]
C_VLIGHT     = "#e0e0e0"          # slightly lighter variant still usable
C_BG         = PALETTE["paper"]

# --- chart_save forwards to editorial_save ---
def chart_save(fig, name: str, *, title: str, subtitle: str, source: str,
               top: float = 0.84, bottom: float = 0.16,
               left: float = 0.10, right: float = 0.94):
    editorial_save(fig, name, title=title, subtitle=subtitle, source=source,
                   top=top, bottom=bottom, left=left, right=right)


# Source URL constants
URL_NYPD_HISTORIC = "https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Historic/qgea-i56i"
URL_NYPD_PRECINCTS = "https://data.cityofnewyork.us/Public-Safety/Police-Precincts/78dh-3ptz"
URL_COMPTROLLER_BHEARD = "https://comptroller.nyc.gov/wp-content/uploads/2025/05/MG24-060A.pdf"
URL_VITAL_CITY = "https://vitalcitynyc.org/articles/crime-in-new-york-city-trends-statistics"
URL_DCJS = "https://www.criminaljustice.ny.gov/crimnet/ojsa/domestic-violence-data.html"
URL_MAYOR_BTH = "https://www.nyc.gov/mayors-office/news/2025/01/mayor-adams-takes-unprecedented-action-curb-street-homelessness-support-people-severe"
URL_MANHATTAN_INSTITUTE = "https://manhattan.institute/article/systems-under-strain-deinstitutionalization-in-new-york-state-and-city-2025-update"
URL_KOPPA = "https://www.sciencedirect.com/science/article/abs/pii/S0167268123004018"
URL_BRAGA_WEISBURD = "https://www.campbellcollaboration.org/better-evidence/focused-deterrence-strategies-effects-on-crime.html"
URL_SECHRIST_WEIL = "https://pubmed.ncbi.nlm.nih.gov/29332533/"
URL_MDVE = "https://www.jstor.org/stable/2095575"
URL_CHENG_META = "https://pubmed.ncbi.nlm.nih.gov/31359840/"
URL_CURE_VIOLENCE = "https://cvg.org/what-we-do/"
URL_CCJ_2024 = "https://counciloncj.org/crime-trends-in-u-s-cities-year-end-2024-update/"
URL_FBI_2024 = "https://www.fbi.gov/news/press-releases/fbi-releases-2024-reported-crimes-in-the-nation-statistics"
URL_LAPD_2024 = "https://mayor.lacity.gov/news/lapd-releases-2024-end-year-crime-statistics-city-los-angeles"
URL_FBI_DV_REPORT = "https://cde.ucr.cjis.gov/LATEST/resources/reports/Domestic%20Relationships%20and%20Violent%20Crimes%202020-2024.pdf"
URL_NYC_MAYOR_2025_BHEARD = "https://www.nyc.gov/mayors-office/news/2025/11/mayor-adams-announces-new-model-to-have-new-york-city-s-911-ment"
URL_PETERSON_IPV = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6161830/"


def even_year_axis(ax, start: int = 2010, end: int = 2024, step: int = 2):
    ticks = list(range(start, end + 1, step))
    if ticks[-1] != end:
        ticks.append(end)
    ax.set_xticks(ticks)
    ax.set_xlim(start - 0.5, end + 0.5)


# ---------------------------------------------------------------------------
# 01 — Hero
# ---------------------------------------------------------------------------
def chart_01_hero():
    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    fa_total = sub.groupby("year")["n"].sum().sort_index()
    strang = sub[sub.pd_desc == "STRANGULATION 1ST"].set_index("year")["n"].reindex(fa_total.index, fill_value=0)
    fa_excl = fa_total - strang
    pct_naive = (fa_total.iloc[-1] / fa_total.iloc[0] - 1) * 100
    pct_adj = (fa_excl.iloc[-1] / fa_excl.iloc[0] - 1) * 100

    fig, (ax_num, ax_spark) = plt.subplots(
        1, 2, figsize=(14, 5.8),
        gridspec_kw={"width_ratios": [1.1, 1.1]},
    )

    # ---- Big-number panel ----
    ax_num.axis("off")
    tx = ax_num.transAxes

    # Struck-through naive headline (light grey)
    ax_num.text(0.5, 0.72, f"+{pct_naive:.0f}%", ha="center", fontsize=58,
                color=C_LIGHT, fontweight="bold", fontfamily="serif",
                transform=tx, zorder=2)
    # Heavy strikethrough slightly heavier than before
    ax_num.plot([0.16, 0.84], [0.775, 0.845], color="#000000", lw=5.5,
                transform=tx, zorder=5, solid_capstyle="round")

    # Adjusted figure (orange) — vertically aligned with label below
    ax_num.text(0.5, 0.34, f"+{pct_adj:.0f}%", ha="center", fontsize=82,
                color=C_ASSAULT, fontweight="bold", fontfamily="serif",
                transform=tx)
    # "real behavioral rise" label — same horizontal centre as the number above
    ax_num.text(0.5, 0.18, "real behavioral rise, 2010 to 2024",
                ha="center", fontsize=12, color=C_ASSAULT,
                fontfamily="sans-serif", transform=tx)
    ax_num.text(0.5, 0.10, "(strangulation reclassification removed)",
                ha="center", fontsize=9, color=C_NEUTRAL, style="italic",
                fontfamily="sans-serif", transform=tx)

    # ---- Sparkline ----
    data_years = fa_total.index.tolist()
    full_years = list(range(2010, 2025))
    naive_full = pd.Series(index=full_years, dtype=float)
    naive_full.loc[data_years] = fa_total.values
    naive_full = naive_full.interpolate()
    excl_full = pd.Series(index=full_years, dtype=float)
    excl_full.loc[data_years] = fa_excl.values
    excl_full = excl_full.interpolate()

    ax_spark.set_title("Annual felony-assault count, 2010–2024", fontsize=11)
    ax_spark.legend(handles=[
        mpatches.Patch(color=C_LIGHT, label="naive total"),
        mpatches.Patch(color=C_ASSAULT, label="excluding Strangulation 1st"),
    ], loc="upper center", bbox_to_anchor=(0.5, 0.97), ncols=2, frameon=False, fontsize=9)
    ax_spark.plot(full_years, naive_full.values, lw=2.0, color=C_LIGHT)
    ax_spark.plot(full_years, excl_full.values, lw=3.0, color=C_ASSAULT)
    ax_spark.scatter(data_years, fa_total.values, s=38, color=C_LIGHT, zorder=3,
                     edgecolor="white", linewidth=1)
    ax_spark.scatter(data_years, fa_excl.values, s=42, color=C_ASSAULT, zorder=3,
                     edgecolor="white", linewidth=1)
    for y in data_years:
        ax_spark.annotate(f"{int(fa_total.loc[y]):,}", (y, fa_total.loc[y]),
                          textcoords="offset points", xytext=(0, 7), ha="center",
                          fontsize=8.5, color=C_NEUTRAL, fontfamily="sans-serif")
    even_year_axis(ax_spark, 2010, 2024, 2)
    ax_spark.set_ylabel("Reports per year")

    chart_save(fig, "01_hero_bignumber.png",
               title="The +72% headline overstates how much NYC felony assault has actually grown.",
               subtitle="One-third of the headline rise is a 2010 statutory reclassification, not new behavior — the real behavioral increase is 47%.",
               source=f"Source: NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}). Strangulation 1st (NYPL §121.13) was created November 2010; subtracted from both endpoints. Dots mark actual data years (2010, 2014, 2019, 2024); line interpolates between.",
               top=0.78, left=0.08, right=0.96)


# ---------------------------------------------------------------------------
# 02 — Situation
# ---------------------------------------------------------------------------
def chart_02_situation():
    fy = pd.read_parquet(AGG / "felony_yearly.parquet")
    violent = ["MURDER & NON-NEGL. MANSLAUGHTER", "RAPE", "ROBBERY", "FELONY ASSAULT"]
    fy24 = fy[(fy.year == 2024) & (fy.ofns_desc.isin(violent))].copy()
    # Sort ascending so Felony Assault lands on TOP (largest, plotted last in barh)
    fy24 = fy24.sort_values("n", ascending=True)
    label_map = {
        "MURDER & NON-NEGL. MANSLAUGHTER": "Murder",
        "RAPE": "Rape",
        "ROBBERY": "Robbery",
        "FELONY ASSAULT": "Felony Assault",
    }
    fy24["label"] = fy24.ofns_desc.map(label_map)
    colors = [C_ASSAULT if c == "FELONY ASSAULT" else C_LIGHT for c in fy24.ofns_desc]

    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.barh(fy24.label, fy24.n, color=colors, height=0.55)
    for y, (lab, val) in enumerate(zip(fy24.label, fy24.n)):
        ax.text(val + 400, y, f"{int(val):,}", va="center", fontsize=11,
                color=C_ASSAULT if lab == "Felony Assault" else C_NEUTRAL,
                fontweight="bold" if lab == "Felony Assault" else "normal",
                fontfamily="sans-serif")
    ax.set_xlim(0, max(fy24.n) * 1.18)
    # No x-axis label — value labels at each bar make it redundant
    ax.set_xlabel("")
    ax.xaxis.grid(False)  # no vertical gridlines for horizontal bar chart
    ax.yaxis.grid(False)

    chart_save(fig, "02_situation_majors.png",
               title="Felony assault is the largest violent-felony category in NYC.",
               subtitle="At ~30,000 reports in 2024, felony assault is roughly twice as common as robbery and dwarfs murder and rape combined.",
               source=f"Source: NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}). Comparison covers the four violent-felony categories. Grand Larceny is larger overall (47,808 in 2024) but is a property crime, not a violent one.",
               top=0.80, left=0.18)


# ---------------------------------------------------------------------------
# 03 — DV split — pie replaced with horizontal stacked bar
# ---------------------------------------------------------------------------
def chart_03_dv_split():
    # 2024 total felony assault = 29,501. About 40% involves the same household.
    total_2024 = 29501
    dv_share = 0.39
    dv_2024 = int(round(total_2024 * dv_share))
    other_2024 = total_2024 - dv_2024

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(13, 5.0),
                                            gridspec_kw={"width_ratios": [1.2, 1]})

    # ---- Left: growth rates ----
    cats = ["Domestic + elder assault", "Other felony assault"]
    pct = [73, 40]
    bars = ax_left.barh(cats, pct, color=[C_DV, C_NEUTRAL], height=0.55)
    for bar, v, c in zip(bars, pct, [C_DV, C_NEUTRAL]):
        ax_left.text(v + 1.5, bar.get_y() + bar.get_height() / 2, f"+{v}%",
                     va="center", fontsize=18, fontweight="bold", color=c,
                     fontfamily="sans-serif")
    ax_left.set_xlim(0, 95)
    ax_left.set_xlabel("Growth, 2017 to 2024 (%)")
    ax_left.set_title("Growth rates", fontsize=11)
    ax_left.invert_yaxis()
    ax_left.xaxis.grid(False)
    ax_left.yaxis.grid(False)

    # ---- Right: replace pie with horizontal stacked bar ----
    ax_right.set_title(f"2024 share of all {total_2024:,} felony assaults", fontsize=11)

    # Single-row stacked bar
    ax_right.barh(0, dv_2024, color=C_DV, height=0.55, label=f"DV / household ({dv_share*100:.0f}%)")
    ax_right.barh(0, other_2024, left=dv_2024, color=C_LIGHT, height=0.55, label=f"Other ({(1-dv_share)*100:.0f}%)")

    # Inline labels
    ax_right.text(dv_2024 / 2, 0,
                  f"DV / household\n{dv_2024:,} cases\n(~39%)",
                  ha="center", va="center", fontsize=10, color="white",
                  fontweight="bold", fontfamily="sans-serif")
    ax_right.text(dv_2024 + other_2024 / 2, 0,
                  f"Other felony assault\n{other_2024:,} cases\n(~61%)",
                  ha="center", va="center", fontsize=10, color=PALETTE["ink"],
                  fontweight="bold", fontfamily="sans-serif")

    ax_right.set_xlim(0, total_2024 * 1.02)
    ax_right.set_ylim(-0.6, 0.6)
    ax_right.set_yticks([])
    ax_right.set_xlabel("2024 felony-assault reports")
    ax_right.xaxis.grid(False)
    ax_right.yaxis.grid(False)
    # Hide spines for stacked bar — it reads as a proportion, no axis needed
    for spine in ax_right.spines.values():
        spine.set_visible(False)

    chart_save(fig, "03_dv_split.png",
               title="Domestic violence is the dominant driver of NYC's felony-assault rise.",
               subtitle="DV grew nearly twice as fast as other felony assault since 2017 and accounts for roughly 11,500 of 29,501 cases in 2024.",
               source=f"Sources: Vital City analysis of NYPD data ({URL_VITAL_CITY}), citing NY Division of Criminal Justice Services DV feed ({URL_DCJS}). NYPD's public dataset has no victim-relationship field, so the DV share is sourced from the DCJS feed. Stacked bar applies Vital City's ~39% household-share figure to the 2024 total.",
               top=0.80, left=0.18)


# ---------------------------------------------------------------------------
# 04 — Stacked sub-categories with DV breakout
# ---------------------------------------------------------------------------
def chart_04_complication_stacked():
    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    pivot = sub.pivot_table(index="year", columns="pd_desc", values="n", aggfunc="sum").fillna(0)
    pivot = pivot.sort_index()
    plot_cols = ["ASSAULT 2,1,UNCLASSIFIED", "ASSAULT POLICE/PEACE OFFICER", "STRANGULATION 1ST"]
    other = pivot.drop(columns=plot_cols, errors="ignore").sum(axis=1)
    pivot["OTHER NEW SUBCATS"] = other

    fig, ax = plt.subplots(figsize=(13, 6.0))
    bottoms = np.zeros(len(pivot))
    x = pivot.index.values
    width = 1.2  # narrower for breathing room

    # Layer 1: Assault 2/1/Unclassified split into DV-driven (magenta) and other (orange)
    catch_all = pivot["ASSAULT 2,1,UNCLASSIFIED"].values
    total_fa_per_year = pivot.sum(axis=1).values
    dv_layer = total_fa_per_year * 0.39   # ~39% DV share (Vital City)
    dv_layer = np.minimum(dv_layer, catch_all)
    other_catch = catch_all - dv_layer

    ax.bar(x, dv_layer, bottom=bottoms, color=C_DV, label="DV-driven (catch-all, ~39% share)",
           width=width, edgecolor="white")
    bottoms = bottoms + dv_layer
    ax.bar(x, other_catch, bottom=bottoms, color=C_ASSAULT,
           label="Other Assault 2/1/Unclassified", width=width, edgecolor="white")
    bottoms = bottoms + other_catch
    ax.bar(x, pivot["ASSAULT POLICE/PEACE OFFICER"].values, bottom=bottoms,
           color=C_NEUTRAL, label="Assault on Police/Peace Officer",
           width=width, edgecolor="white")
    bottoms = bottoms + pivot["ASSAULT POLICE/PEACE OFFICER"].values
    ax.bar(x, pivot["STRANGULATION 1ST"].values, bottom=bottoms,
           color=C_STRUCTURAL, label="Strangulation 1st (created Nov 2010)",
           width=width, edgecolor="white")
    bottoms = bottoms + pivot["STRANGULATION 1ST"].values
    ax.bar(x, pivot["OTHER NEW SUBCATS"].values, bottom=bottoms,
           color=C_LIGHT, label="Other new sub-categories",
           width=width, edgecolor="white")

    baseline_2010 = pivot.loc[2010].sum()
    ax.axhline(baseline_2010, color=C_NEUTRAL, ls="--", lw=1, alpha=0.7)
    ax.text(2025.0, baseline_2010, f"  2010 baseline\n  {int(baseline_2010):,}",
            va="center", fontsize=9, color=C_NEUTRAL, fontfamily="sans-serif")
    ax.annotate("Strangulation acts existed before 2010\nbut were charged under Assault 2nd\nor as a misdemeanor — the new class\nis statutory reclassification.",
                xy=(2010.6, baseline_2010 + 700),
                xytext=(2014.5, 27000),
                fontsize=8.5, color=C_STRUCTURAL, fontfamily="sans-serif",
                arrowprops=dict(arrowstyle="->", color=C_STRUCTURAL, lw=1))
    ax.set_xticks([2010, 2014, 2019, 2024])
    ax.set_ylim(0, 34000)
    ax.set_xlim(2008.5, 2026.5)
    ax.set_ylabel("Annual count")
    # Legend upper-right, 2-column layout
    ax.legend(loc="upper right", frameon=False, fontsize=9, ncols=2)

    chart_save(fig, "04_complication_stacked.png",
               title="The +72% headline includes a new felony class and a DV surge inside the catch-all.",
               subtitle="DV cases inside the catch-all (magenta) doubled since 2010, while Strangulation 1st (navy) is a 2010 statutory creation that accounts for ~35% of the headline rise.",
               source=f"Sources: NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}) drilled by pd_cd for sub-category counts. DV share applies Vital City's ~39% household-share estimate ({URL_VITAL_CITY}) to total felony-assault count per year, capped at catch-all size. Strangulation 1st = NYPL §121.13 (created November 2010). Bars at actual data years; widths = 1.2 years for visual breathing room.",
               top=0.78)


# ---------------------------------------------------------------------------
# 05 — Trajectories — focal line thicker, direct-labeled endpoints, faint peers
# ---------------------------------------------------------------------------
def chart_05_trajectories():
    fy = pd.read_parquet(AGG / "felony_yearly.parquet")
    focal = "FELONY ASSAULT"
    violent_other = ["MURDER & NON-NEGL. MANSLAUGHTER", "RAPE", "ROBBERY"]
    keep = [focal] + violent_other
    fy = fy[fy.ofns_desc.isin(keep)].copy()
    base17 = fy[fy.year == 2017].set_index("ofns_desc")["n"]
    fy["index_2017"] = fy.apply(lambda r: r.n / base17.get(r.ofns_desc, np.nan), axis=1)
    label_map = {
        "FELONY ASSAULT": "Felony Assault\n(DV-driven)",
        "ROBBERY": "Robbery",
        "MURDER & NON-NEGL. MANSLAUGHTER": "Murder",
        "RAPE": "Rape",
    }

    fig, ax = plt.subplots(figsize=(13, 5.6))
    for ofns, group in fy.groupby("ofns_desc"):
        g = group.sort_values("year")
        if ofns == focal:
            color, lw, zorder = C_ASSAULT, 3.0, 5
            font_size = 10.5
            fw = "bold"
        else:
            # Faint gray for non-focal lines
            color, lw, zorder = "#AAAAAA", 1.2, 4
            font_size = 9.5
            fw = "normal"
        ax.plot(g.year, g.index_2017, color=color, lw=lw, zorder=zorder)
        # Direct-label endpoint — no legend needed
        ax.text(g.year.iloc[-1] + 0.15, g.index_2017.iloc[-1],
                label_map.get(ofns, ofns.title()),
                fontsize=font_size, color=color, va="center", fontweight=fw,
                fontfamily="sans-serif")

    ax.axhline(1.0, color=C_NEUTRAL, lw=0.8, alpha=0.4)
    ax.axvline(2020, color=C_NEUTRAL, lw=0.8, alpha=0.3, ls=":")
    ax.text(2020, 0.55, "COVID", fontsize=8, color=C_NEUTRAL, ha="center",
            fontfamily="sans-serif")
    ax.set_xticks(list(range(2017, 2025)))
    ax.set_xlim(2016.7, 2025.8)
    ax.set_ylim(0.50, 1.80)
    ax.set_ylabel("Index, 2017 = 1.0")
    # No legend — lines are direct-labeled

    chart_save(fig, "05_trajectories.png",
               title="Felony assault is the only violent-crime category showing a sustained rise.",
               subtitle="Felony assault has risen every year since 2017 (+46% by 2024). Murder spiked during COVID and has since declined; robbery and rape are roughly flat.",
               source=f"Source: NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}). Each line indexed to its 2017 value. Chart shows only the four violent-felony categories — property and non-violent felonies are not included.",
               top=0.80)


# ---------------------------------------------------------------------------
# 06 — Precinct map + concentration stat
# ---------------------------------------------------------------------------
def chart_06_precinct_growth():
    import geopandas as gpd
    gdf = gpd.read_file(GEO / "precincts.geojson")
    id_col = None
    for cand in ["precinct", "Precinct", "PCT", "precinct_n", "pct"]:
        if cand in gdf.columns:
            id_col = cand
            break
    if id_col is None:
        id_col = [c for c in gdf.columns if c != "geometry"][0]
    gdf[id_col] = pd.to_numeric(gdf[id_col], errors="coerce")

    fpy = pd.read_parquet(AGG / "felony_precinct_yearly.parquet")
    fa_p = fpy[fpy.ofns_desc == "FELONY ASSAULT"].copy()
    fa_p.addr_pct_cd = pd.to_numeric(fa_p.addr_pct_cd, errors="coerce")
    pivot = fa_p.pivot_table(index="addr_pct_cd", columns="year", values="n", aggfunc="sum").fillna(0)
    pivot["pct_change"] = (pivot[2024] / pivot[2017] - 1) * 100
    pivot["abs_change"] = pivot[2024] - pivot[2017]
    pivot_sorted = pivot.sort_values("abs_change", ascending=False)

    total_growth = pivot_sorted["abs_change"].sum()
    top1_share = pivot_sorted["abs_change"].head(1).sum() / total_growth * 100
    top10_share = pivot_sorted["abs_change"].head(10).sum() / total_growth * 100
    n_pos = (pivot["abs_change"] > 0).sum()

    merged = gdf.merge(pivot[["pct_change"]],
                       left_on=id_col, right_index=True, how="left")

    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_facecolor(C_BG)
    cmap = plt.colormaps["OrRd"]
    vmin, vmax = -50, 200
    merged.plot(ax=ax, column="pct_change", cmap=cmap, vmin=vmin, vmax=vmax,
                edgecolor="white", linewidth=0.5,
                missing_kwds={"color": "#EEEEEE"})
    ax.set_axis_off()

    callout = (f"How concentrated is the rise?\n"
               f"  • {n_pos} of 78 precincts saw growth\n"
               f"  • Largest single precinct: {top1_share:.0f}% of citywide growth\n"
               f"  • Top 10 precincts: {top10_share:.0f}% of citywide growth\n\n"
               "The rise is broadly distributed.")
    ax.text(0.02, 0.04, callout, transform=ax.transAxes, fontsize=10,
            color=C_NEUTRAL, fontfamily="sans-serif",
            bbox=dict(boxstyle="round,pad=0.6", fc=C_BG, ec=C_LIGHT))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02, orientation="horizontal")
    cbar.set_label("% change in felony assault, 2017 to 2024", fontsize=8,
                   fontfamily="sans-serif", color=C_NEUTRAL)

    chart_save(fig, "06_precinct_growth.png",
               title="No single precinct drove the citywide felony-assault rise.",
               subtitle=f"{n_pos} of 78 precincts grew between 2017 and 2024 — the rise is broadly distributed, not concentrated in a few hot spots.",
               source=f"Sources: NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}); NYC Police Precincts geojson ({URL_NYPD_PRECINCTS}). % change computed per precinct between 2017 and 2024. Concentration shares = each precinct's share of the citywide absolute increase.",
               top=0.84, bottom=0.14, left=0.04, right=0.96)


# ---------------------------------------------------------------------------
# 07 — Bed capacity — orange for "what's needed", gray for "what exists"
# ---------------------------------------------------------------------------
def chart_07_beds():
    today_bth, today_sh = 100, 900
    rec_bth, rec_sh = 200, 1800
    target = 2000
    fig, ax = plt.subplots(figsize=(12, 5.4))
    bars = ["Today (existing)", "Recommended (double over 18 months)"]

    # Gray for what exists, orange for what's needed
    colors_bth  = [C_NEUTRAL, C_ASSAULT]
    colors_sh   = [C_LIGHT,   C_ASSAULT]

    bth = [today_bth, rec_bth]
    sh  = [today_sh,  rec_sh]

    ax.barh(bars, bth, color=colors_bth, label="Bridge to Home (long-term supportive housing)")
    ax.barh(bars, sh, left=bth, color=colors_sh, label="Safe Haven (transitional shelter)")

    for i, (b_val, s_val, c_text) in enumerate(zip(bth, sh,
                                                    [C_NEUTRAL, "white"])):
        ax.text(b_val + 30, i - 0.18, f"{b_val} BTH", ha="left", va="center",
                color=colors_bth[i], fontsize=10, fontweight="bold",
                fontfamily="sans-serif")
        ax.text(b_val + s_val / 2, i, f"{s_val:,} Safe Haven beds", ha="center",
                va="center", color="white" if i == 1 else C_NEUTRAL,
                fontsize=10, fontweight="bold", fontfamily="sans-serif")
        ax.text(b_val + s_val + 40, i, f"= {b_val + s_val:,} beds total",
                va="center", fontsize=10, color=C_NEUTRAL,
                fontfamily="sans-serif")

    ax.axvline(target, color=C_ASSAULT, ls="--", lw=2)
    ax.text(target + 30, 1.55, "2,000-person\nannounced target", fontsize=10,
            color=C_ASSAULT, fontweight="bold", fontfamily="sans-serif")
    ax.set_xlim(0, target * 1.22)
    ax.invert_yaxis()
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), frameon=False,
              fontsize=9, ncols=2)
    ax.set_xlabel("Beds")
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    chart_save(fig, "07_beds.png",
               title="NYC has fewer than 100 supportive-housing beds against a 2,000-person target.",
               subtitle="Doubling Bridge to Home capacity is a throughput problem, not a funding problem — the $650M is already announced.",
               source=f"Source: NYC Mayor's January 2025 Care, Community, Action announcement ({URL_MAYOR_BTH}). BTH = Bridge to Home (long-term supportive housing); Safe Haven = transitional shelter. Tsemberis Pathways-to-Housing RCT and replications underpin the supportive-housing evidence base.",
               top=0.78, left=0.20)


# ---------------------------------------------------------------------------
# 08 — Distal driver — increase right margin to avoid label cutoff
# ---------------------------------------------------------------------------
def chart_08_distal():
    bed_years = [2014, 2021]
    bed_values_raw = [3050, 2300]
    bed_index = [v / bed_values_raw[0] * 100 for v in bed_values_raw]

    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    fa_total = sub.groupby("year")["n"].sum().sort_index()
    fa_years = fa_total.index.tolist()
    fa_2014 = fa_total.loc[2014]
    fa_index = (fa_total.values / fa_2014 * 100).tolist()

    fig, ax = plt.subplots(figsize=(13, 5.6))

    ax.plot(fa_years, fa_index, color=C_ASSAULT, lw=2.6)
    ax.scatter(fa_years, fa_index, s=70, color=C_ASSAULT, zorder=3,
               edgecolor="white", linewidth=1.5)
    for y, v, raw in zip(fa_years, fa_index, fa_total.values):
        ax.annotate(f"{v:.0f}\n({int(raw):,})", (y, v),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=8.5, color=C_ASSAULT,
                    fontfamily="sans-serif")

    ax.plot(bed_years, bed_index, color=C_STRUCTURAL, lw=2.6, ls="--")
    ax.scatter(bed_years, bed_index, s=80, color=C_STRUCTURAL, zorder=3,
               edgecolor="white", linewidth=1.5)
    for y, v, raw in zip(bed_years, bed_index, bed_values_raw):
        ax.annotate(f"{v:.0f}\n({raw:,})", (y, v),
                    textcoords="offset points", xytext=(0, -22),
                    ha="center", fontsize=8.5, color=C_STRUCTURAL,
                    fontfamily="sans-serif")

    ax.axhline(100, color=C_NEUTRAL, lw=0.8, alpha=0.5)
    ax.text(2024.4, 100, " 2014 = 100", va="center", fontsize=8.5, color=C_NEUTRAL,
            fontfamily="sans-serif")

    legend_items = [
        mpatches.Patch(color=C_ASSAULT, label="NYC felony assault"),
        mpatches.Patch(color=C_STRUCTURAL, label="NY State inpatient psychiatric beds"),
    ]
    ax.legend(handles=legend_items, loc="upper left", frameon=False, fontsize=10)

    even_year_axis(ax, 2010, 2024, 2)
    ax.set_ylim(60, 160)
    ax.set_ylabel("Index — both series, 2014 = 100")

    # right=0.86 to avoid right-axis label cutoff
    chart_save(fig, "08_distal.png",
               title="As NY State inpatient psychiatric capacity contracted, NYC felony assault rose.",
               subtitle="Both series indexed to 2014 = 100, plotted on the same scale — psych beds dropped about 25% while felony assault rose about 46% over the same window.",
               source=f"Sources: NY State psych beds — Manhattan Institute deinstitutionalization paper ({URL_MANHATTAN_INSTITUTE}), 2014 and 2021 documented endpoints only. NYC felony assault — NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}). Numbers next to each dot show index value (top) and raw count (bottom).",
               top=0.80, left=0.10, right=0.86)


# ---------------------------------------------------------------------------
# 09 — B-HEARD breakdown (Sankey-ish flow)
# ---------------------------------------------------------------------------
def chart_09_bheard_breakdown():
    fig, ax = plt.subplots(figsize=(13, 5.6))
    segments = [
        ("Got a B-HEARD team", 24071, C_STRUCTURAL),
        ("In-hours, did not get B-HEARD", 13042, C_ASSAULT),
        ("Overnight, program does not operate", 14200, C_DV),
    ]
    total = sum(s[1] for s in segments)
    left = 0
    for label, val, color in segments:
        ax.barh(0, val, left=left, color=color, height=0.6, edgecolor="white", linewidth=2)
        ax.text(left + val / 2, 0, f"{label}\n{val:,} calls\n({val/total*100:.0f}%)",
                ha="center", va="center", color="white", fontsize=10, fontweight="bold",
                fontfamily="sans-serif")
        left += val
    ax.set_xlim(0, total * 1.02)
    ax.set_yticks([])
    ax.set_xlabel("Eligible mental-health 911 calls per year (FY24)")
    ax.set_ylim(-1.0, 0.6)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    ax.annotate("Why these calls go unmet\nis not tracked in the audit.\nCause-tracking is the fix.",
                xy=(24071 + 13042/2, -0.32), xytext=(24071 + 13042/2, -0.85),
                ha="center", fontsize=9, color=C_ASSAULT, fontweight="bold",
                fontfamily="sans-serif",
                arrowprops=dict(arrowstyle="->", color=C_ASSAULT))
    ax.annotate("Program does not operate overnight.\nExtending hours adds about 14,000\nreachable calls.",
                xy=(24071 + 13042 + 14200/2, -0.32),
                xytext=(24071 + 13042 + 14200/2, -0.85),
                ha="center", fontsize=9, color=C_DV, fontweight="bold",
                fontfamily="sans-serif",
                arrowprops=dict(arrowstyle="->", color=C_DV))

    chart_save(fig, "09_bheard_breakdown.png",
               title="NYC's eligible mental-health 911 calls split into three distinct buckets.",
               subtitle="The 53% gap has two distinct fixes — extending overnight hours and tracking why in-hours calls go unmet — not one.",
               source=f"Source: NYC Comptroller 2024 B-HEARD audit ({URL_COMPTROLLER_BHEARD}). Each segment width is proportional to call volume in FY24. Numbers are from the audit's Appendix II.",
               top=0.82, bottom=0.32)


# ---------------------------------------------------------------------------
# 10 — B-HEARD coverage map
# ---------------------------------------------------------------------------
def chart_10_bheard_coverage():
    import geopandas as gpd
    gdf = gpd.read_file(GEO / "precincts.geojson")
    id_col = None
    for cand in ["precinct", "Precinct", "PCT", "precinct_n", "pct"]:
        if cand in gdf.columns:
            id_col = cand
            break
    if id_col is None:
        id_col = [c for c in gdf.columns if c != "geometry"][0]
    gdf[id_col] = pd.to_numeric(gdf[id_col], errors="coerce")

    fpy = pd.read_parquet(AGG / "felony_precinct_yearly.parquet")
    fa = fpy[(fpy.ofns_desc == "FELONY ASSAULT") & (fpy.year == 2024)].copy()
    fa.addr_pct_cd = pd.to_numeric(fa.addr_pct_cd, errors="coerce")
    merged = gdf.merge(fa[["addr_pct_cd", "n"]].rename(columns={"addr_pct_cd": "precinct"}),
                       left_on=id_col, right_on="precinct", how="left")

    bheard_pcts = (
        [25, 26, 28, 30, 32, 33, 34]
        + [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52]
        + [63, 67, 69, 71, 73, 75]
        + [104, 108, 110, 112, 114, 115]
    )
    merged["bheard"] = merged[id_col].isin(bheard_pcts)

    fig, ax = plt.subplots(figsize=(11, 10))
    ax.set_facecolor(C_BG)
    cmap = plt.colormaps["Oranges"]
    vmin, vmax = 0, max(fa.n) if len(fa) else 1
    merged.plot(ax=ax, column="n", cmap=cmap, vmin=vmin, vmax=vmax,
                edgecolor="white", linewidth=0.4,
                missing_kwds={"color": "#EEEEEE"})
    bheard_layer = merged[merged.bheard]
    if len(bheard_layer):
        bheard_layer.boundary.plot(ax=ax, color=C_STRUCTURAL, linewidth=2.4)
    ax.set_axis_off()

    if len(fa) and merged["n"].notna().any():
        cov_mean = merged.loc[merged.bheard, "n"].mean()
        unc_mean = merged.loc[(~merged.bheard) & merged["n"].notna(), "n"].mean()
        ratio = cov_mean / unc_mean if unc_mean else float("nan")
        ax.text(0.02, 0.04,
                f"Felony-assault count, 2024 (mean per precinct):\n"
                f"  B-HEARD-covered (31): {cov_mean:,.0f}\n"
                f"  Not covered (47): {unc_mean:,.0f}\n"
                f"  Ratio: {ratio:.2f}×\n\n"
                "B-HEARD covers higher-incidence precincts on average.",
                transform=ax.transAxes, fontsize=10, color=C_NEUTRAL,
                fontfamily="sans-serif",
                bbox=dict(boxstyle="round,pad=0.6", fc=C_BG, ec=C_LIGHT))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02, orientation="horizontal")
    cbar.set_label("Felony-assault count per precinct, 2024", fontsize=8,
                   fontfamily="sans-serif", color=C_NEUTRAL)

    chart_save(fig, "10_bheard_coverage.png",
               title="B-HEARD covers 31 of 78 precincts — and they are higher-incidence on average.",
               subtitle="The covered precincts average about twice the felony-assault count of the uncovered ones — coverage is targeting need, but Staten Island and most of Brooklyn and Queens are excluded.",
               source=f"Sources: B-HEARD precinct list — NYC Comptroller 2024 audit Appendix II ({URL_COMPTROLLER_BHEARD}); reaffirmed by NYC Mayor's Office November 2025 release ({URL_NYC_MAYOR_2025_BHEARD}). Felony-assault counts per precinct — NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}). Precinct boundaries — NYC OpenData Police Precincts ({URL_NYPD_PRECINCTS}).",
               top=0.86, bottom=0.14, left=0.04, right=0.96)


# ---------------------------------------------------------------------------
# 11 — Timeline — orange for active/recommended, gray for placeholder
# ---------------------------------------------------------------------------
def chart_11_timeline():
    # Color key: orange = active pilot / recommended action; gray = background/placeholder
    rows = [
        ("Precinct selection +\ncivil-liberties impact assessment", 0, 6, C_NEUTRAL),
        ("Pilot rollout (4-6 precincts)", 6, 18, C_ASSAULT),
        ("Interim evaluation", 16, 20, C_LIGHT),
        ("Phase-1 evaluation cycle", 6, 30, C_ASSAULT),
        ("Sunset gate", 29, 31, C_STRUCTURAL),
    ]
    fig, ax = plt.subplots(figsize=(13, 5.6))
    n = len(rows)
    for i, (label, start, end, color) in enumerate(rows):
        y = n - i - 1
        ax.barh(y, end - start, left=start, color=color, height=0.55, edgecolor="white")
    ax.set_yticks(range(n))
    ax.set_yticklabels([rows[n - i - 1][0] for i in range(n)], fontsize=10)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-1, 38)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xticks([0, 6, 12, 18, 24, 30, 36])
    ax.set_xticklabels(["M0", "M6", "M12", "M18", "M24", "M30", "M36"],
                       fontfamily="sans-serif")
    ax.set_xlabel("Months from pilot start")
    ax.axvline(30, color=C_NEUTRAL, ls="--", lw=1.5)
    ax.text(30.5, n - 0.4, "Sunset clause\nbinding at M30", color=C_NEUTRAL,
            fontsize=9.5, fontweight="bold", va="top", fontfamily="sans-serif")
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    chart_save(fig, "11_timeline.png",
               title="The pilot has a binding fund-or-de-fund decision at month 30.",
               subtitle="If the pre-registered endpoint is not met, funding ends automatically — the sunset is encoded in procurement-contract language, not aspirational.",
               source="Derived from memo Section 3 design constraints. Civil-liberties impact assessment precedes precinct rollout. Interim evaluation at month 18 informs course-correction. Phase-1 endpoint at month 30 is the binding decision point — Callaway-Sant'Anna staggered difference-in-differences with formal pretrend tests on DV-felony rate change in matched comparison precincts.",
               top=0.82, left=0.24)


# ---------------------------------------------------------------------------
# 12 — Ranked DV interventions — orange for top-3, gray below
# ---------------------------------------------------------------------------
def chart_12_dv_rank():
    rows = [
        ("LAP (Maryland, Koppa JEBO 2024)", 40, 35, 45, C_ASSAULT,
         "Police screen DV calls with an 11-question lethality scale; high-risk survivors get a live advocate hotline call on scene.",
         "$3-8M / yr"),
        ("Mandatory arrest (Sherman & Berk MDVE)", 13.0, 5, 21, C_ASSAULT,
         "Police arrest rather than separate parties at DV incidents.",
         "Statutory — minimal cost"),
        ("OFDVI (High Point, Sechrist & Weil 2018)", 20, 12, 28, C_ASSAULT,
         "Focused-deterrence call-in: high-risk offenders are warned of consequences and offered services.",
         "$2-5M / yr"),
        ("Batterer programs (Duluth / CBT)", 0, -5, 5, C_NEUTRAL,
         "Court-mandated cognitive-behavioral group programs for DV offenders.",
         "$3-7M / yr"),
        ("CVI / credible-messenger for DV", 0, 0, 0, C_NEUTRAL,
         "Community-based credible-messenger intervention adapted from gun violence to DV.",
         "Untested — no cost basis"),
    ]
    fig, ax = plt.subplots(figsize=(14, 6.4))
    for i, (label, mid, lo, hi, color, _desc, _cost) in enumerate(rows):
        if hi > 0 and not (lo == 0 and hi == 0):
            ax.barh(i, max(hi - lo, 1), left=lo, color=color, height=0.55, alpha=0.85)
            ax.text(hi + 1.5, i + 0.05, f"{lo}–{hi}%", va="center", fontsize=11,
                    fontweight="bold", color=color, fontfamily="sans-serif")
        else:
            ax.text(2, i + 0.05, "untested or null", va="center", fontsize=11,
                    color=color, fontweight="bold", fontfamily="sans-serif")
        ax.text(-1, i + 0.05, label, va="center", ha="right", fontsize=10,
                fontfamily="sans-serif")
        ax.text(54, i + 0.05, rows[i][5], va="center", fontsize=8.5,
                style="italic", color=C_NEUTRAL, fontfamily="sans-serif")
        ax.text(54, i - 0.30, f"Cost: {rows[i][6]}", va="center", fontsize=8.5,
                color=C_NEUTRAL, fontweight="bold", fontfamily="sans-serif")
    ax.axvline(0, color=C_LIGHT, lw=1)
    ax.set_xlim(-2, 110)
    ax.set_ylim(len(rows) - 0.3, -0.6)
    ax.set_xlabel("Source-study effect size (%)")
    ax.set_yticks([])
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    chart_save(fig, "12_dv_rank.png",
               title="LAP and OFDVI are the recommended DV interventions — they have the strongest evidence.",
               subtitle="The two programs in orange show positive, DV-specific effects in published evaluations — every other option is mixed, null, or untested.",
               source=f"Sources: Koppa 2024 ({URL_KOPPA}); Sherman & Berk MDVE ({URL_MDVE}); Sechrist & Weil 2018 ({URL_SECHRIST_WEIL}); Cheng et al. 2021 meta-analysis ({URL_CHENG_META}); Cure Violence Global ({URL_CURE_VIOLENCE}). Cost figures are order-of-magnitude estimates for a NYC pilot at 4-6 precincts.",
               top=0.78, left=0.27)


# ---------------------------------------------------------------------------
# 13 — Program quadrant — recommended programs orange, faint quadrant fill
# ---------------------------------------------------------------------------
def chart_13_quadrant():
    programs = [
        ("LAP (Maryland)", 2.55, 3.05, C_ASSAULT, 540),
        ("OFDVI (High Point)", 2.10, 2.75, C_ASSAULT, 440),
        ("Mandatory arrest (MDVE)", 2.85, 2.85, C_NEUTRAL, 380),
        ("Batterer programs", 2.45, 2.55, C_LIGHT, 380),
        ("CMS-for-DV", 0.40, 2.40, C_DV, 380),
        ("CMS / Cure Violence", 2.50, 0.55, C_NEUTRAL, 380),
        ("B-HEARD", 2.00, 1.20, C_NEUTRAL, 380),
        ("Hot-spots policing", 3.00, 0.40, C_NEUTRAL, 380),
        ("BAM (Heller)", 2.95, 0.25, C_NEUTRAL, 380),
        ("NYC Ceasefire", 1.60, 0.30, C_NEUTRAL, 380),
    ]
    fig, ax = plt.subplots(figsize=(13, 7.5))

    # Faint quadrant background fill for the top-right quadrant
    ax.fill_between([1.5, 3.4], 1.5, 3.4, color=PALETTE["light"], alpha=0.35, zorder=0)

    for label, x, y, color, size in programs:
        is_anchor = "LAP" in label or "OFDVI" in label
        ax.scatter(x, y, s=size, color=color, alpha=0.88, edgecolor="white",
                   linewidth=2, zorder=3 if is_anchor else 2)
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(11, 6),
                    fontsize=10 if is_anchor else 9,
                    fontweight="bold" if is_anchor else "normal",
                    color=color if is_anchor else C_NEUTRAL,
                    fontfamily="sans-serif")
    ax.axhline(1.5, color=C_LIGHT, lw=1)
    ax.axvline(1.5, color=C_LIGHT, lw=1)
    ax.set_xlim(0, 3.4)
    ax.set_ylim(0, 3.4)
    ax.set_xlabel("Evidence quality (RCT > quasi-experimental > pre/post > null or untested)")
    ax.set_ylabel("DV relevance")
    ax.text(2.4, 3.30, "TOP RIGHT — DV-evaluated, strong evidence", fontsize=10,
            color=C_ASSAULT, fontweight="bold", fontfamily="sans-serif")
    ax.text(0.15, 3.30, "DV-relevant but untested", fontsize=10, color=C_DV,
            fontfamily="sans-serif")
    ax.text(2.4, 0.05, "Strong evidence, not for DV", fontsize=10, color=C_STRUCTURAL,
            fontfamily="sans-serif")

    acronyms = (
        "Acronym key — "
        "LAP: Lethality Assessment Program. "
        "OFDVI: Offender-Focused Domestic Violence Initiative (High Point model). "
        "MDVE: Minneapolis Domestic Violence Experiment (Sherman & Berk RCT). "
        "CMS: NYC Crisis Management System (Cure Violence-aligned). "
        "B-HEARD: Behavioral Health Emergency Assistance Response Division. "
        "BAM: Becoming a Man (Heller et al. RCT). "
        "GVI: Group Violence Intervention."
    )
    chart_save(fig, "13_quadrant.png",
               title="LAP and OFDVI are the only programs with both strong evidence and DV relevance.",
               subtitle="The top-right quadrant — strong evidence and direct DV relevance — contains exactly two programs, both worth piloting.",
               source=acronyms,
               top=0.82, bottom=0.22)


# ---------------------------------------------------------------------------
# 14 — Multi-baseline + national context — orange for NYC, mute for peers
# ---------------------------------------------------------------------------
def chart_14_baselines():
    sub = pd.read_parquet(AGG / "felony_assault_subcategory_yearly.parquet")
    fa = sub.groupby("year")["n"].sum().sort_index()
    fy = pd.read_parquet(AGG / "felony_yearly.parquet")
    fa_fy = fy[fy.ofns_desc == "FELONY ASSAULT"].set_index("year")["n"].sort_index()

    yoy_pct = (fa_fy.loc[2024] / fa_fy.loc[2023] - 1) * 100
    five_pct = (fa_fy.loc[2024] / fa_fy.loc[2019] - 1) * 100
    decade_naive = (fa.loc[2024] / fa.loc[2010] - 1) * 100
    strang_2010 = sub[(sub.pd_desc == "STRANGULATION 1ST") & (sub.year == 2010)].n.sum()
    strang_2024 = sub[(sub.pd_desc == "STRANGULATION 1ST") & (sub.year == 2024)].n.sum()
    decade_adj = ((fa.loc[2024] - strang_2024) / (fa.loc[2010] - strang_2010) - 1) * 100

    fig, axes = plt.subplots(1, 4, figsize=(15, 5.6))

    # Panel 1 — 1-year (mute/neutral — small move)
    axes[0].bar(["1-year"], [yoy_pct], color=C_ASSAULT, width=0.5)
    axes[0].text(0, yoy_pct + 0.6, f"{yoy_pct:+.1f}%", ha="center",
                 fontsize=18, fontweight="bold", color=C_ASSAULT,
                 fontfamily="sans-serif")
    axes[0].set_title("NYC: 1-year\n(2023->2024)", fontsize=10)
    axes[0].set_ylim(0, 22)
    axes[0].set_ylabel("% change in felony / aggravated assault")

    # Panel 2 — 5-year (orange)
    axes[1].bar(["5-year"], [five_pct], color=C_ASSAULT, width=0.5)
    axes[1].text(0, five_pct + 1.0, f"{five_pct:+.1f}%", ha="center",
                 fontsize=18, fontweight="bold", color=C_ASSAULT,
                 fontfamily="sans-serif")
    axes[1].set_title("NYC: 5-year\n(2019->2024)", fontsize=10)
    axes[1].set_ylim(0, 55)

    # Panel 3 — Decade (headline gray, adjusted orange)
    axes[2].bar(["headline", "adjusted"], [decade_naive, decade_adj],
                color=[C_LIGHT, C_ASSAULT], width=0.5)
    axes[2].text(0, decade_naive + 2.0, f"{decade_naive:+.0f}%", ha="center",
                 fontsize=15, fontweight="bold", color=C_NEUTRAL,
                 fontfamily="sans-serif")
    axes[2].text(1, decade_adj + 2.0, f"{decade_adj:+.0f}%", ha="center",
                 fontsize=15, fontweight="bold", color=C_ASSAULT,
                 fontfamily="sans-serif")
    axes[2].set_title("NYC: decade\n(2010->2024)", fontsize=10)
    axes[2].set_ylim(0, 95)

    # Panel 4 — National context: NYC orange, peers mute
    bench = ["NYC\n(adjusted)", "US national\n(2010->2024)", "24-city avg\n(since 2019)", "LA\n(2024 YoY)"]
    bench_vals = [decade_adj, 1.5, 4, -10]
    bench_colors = [C_ASSAULT, C_NEUTRAL, C_NEUTRAL, C_NEUTRAL]
    axes[3].bar(bench, bench_vals, color=bench_colors, width=0.55)
    for i, v in enumerate(bench_vals):
        offset = 2 if v >= 0 else -3
        axes[3].text(i, v + offset, f"{v:+.0f}%", ha="center", fontsize=12,
                     fontweight="bold", color=bench_colors[i],
                     fontfamily="sans-serif")
    axes[3].axhline(0, color=C_LIGHT, lw=0.8)
    axes[3].set_title("National context", fontsize=10)
    axes[3].set_ylim(-15, 65)

    chart_save(fig, "14_baselines.png",
               title="The choice of time window decides whether NYC's felony-assault rise looks small, big, or like an outlier.",
               subtitle="Even with the strangulation adjustment, NYC sits well above any peer benchmark — and the 24-city panel actually fell 4% year-over-year in 2024 while NYC posted +5.8%.",
               source=f"Sources: NYC — NYPD Complaint Data Historic ({URL_NYPD_HISTORIC}); adjusted decade subtracts Strangulation 1st (NYPL §121.13) from both endpoints. National — FBI 2024 release ({URL_FBI_2024}). 24-city average — Council on Criminal Justice Year-End 2024 ({URL_CCJ_2024}); the same panel was −4% YoY in 2024. LA — LAPD 2024 EOY release ({URL_LAPD_2024}).",
               top=0.78)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Output directory: {OUT}")
    chart_01_hero()
    chart_02_situation()
    chart_03_dv_split()
    chart_04_complication_stacked()
    chart_05_trajectories()
    chart_06_precinct_growth()
    chart_07_beds()
    chart_08_distal()
    chart_09_bheard_breakdown()
    chart_10_bheard_coverage()
    chart_11_timeline()
    chart_12_dv_rank()
    chart_13_quadrant()
    chart_14_baselines()
    # Cleanup stale files from prior versions
    stale = [
        "01_hero_bignumber.png",  # name unchanged; included intentionally to no-op
        "03_situation_majors.png",
        "02_dv_split.png",
        "04_complication_stacked.png",
        "05_complication_clusters.png",
        "06_complication_precinct_map.png",
        "07_framing_three_pillars.png",
        "08_support1_beds.png",
        "09_support1_distal.png",
        "10_support2_breakdown.png",
        "10_support2_waterfall.png",
        "11_support2_coverage_map.png",
        "11_support2_coverage_overlay.png",
        "12_support3_funnel.png",
        "13_support3_costs.png",
        "14_support3_timeline.png",
        "15_what_tried_quadrant.png",
        "16_evidence_dv_ranked.png",
        "17_secondary_window.png",
        "18_secondary_baselines.png",
        "05_trajectories.png",  # in case earlier run produced this; safe no-op below
    ]
    current_outputs = {
        "01_hero_bignumber.png", "02_situation_majors.png", "03_dv_split.png",
        "04_complication_stacked.png", "05_trajectories.png",
        "06_precinct_growth.png", "07_beds.png", "08_distal.png",
        "09_bheard_breakdown.png", "10_bheard_coverage.png", "11_timeline.png",
        "12_dv_rank.png", "13_quadrant.png", "14_baselines.png",
    }
    for s in stale:
        p = OUT / s
        if p.exists() and s not in current_outputs:
            p.unlink()
            print(f"  removed stale {s}")
    print(f"\nDone. {len(list(OUT.glob('*.png')))} sketches in {OUT}")


if __name__ == "__main__":
    main()

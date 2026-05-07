"""Editorial chart theme for the NYC strategy artifact.

Fonts: Newsreader (serif, titles) + Inter (sans, labels/source lines).
Palette: NYT Upshot / Atlantic / Bloomberg Graphics tier.
"""
from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
FONTS_DIR = ROOT / "figures" / "_fonts"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PALETTE = {
    # Brand colours
    "orange":      "#FF6319",  # focal accent (felony assault)
    "magenta":     "#D8127B",  # DV-specific cuts
    "navy":        "#003C71",  # structural drivers
    "ink":         "#1a1a1a",  # body text / headings
    "mute":        "#888888",  # captions, source lines
    "light":       "#e8e8e8",  # borders, hairlines
    "paper":       "#fafaf7",  # chart background (matches site bg)
    # Chart-specific semantic tokens
    "assault":     "#FF6319",
    "dv":          "#D8127B",
    "structural":  "#003C71",
    "neutral":     "#888888",
}

# ---------------------------------------------------------------------------
# Font downloads
# ---------------------------------------------------------------------------
_FONT_URLS = {
    # Newsreader — variable font (google/fonts, refs/heads/main)
    "Newsreader[opsz,wght].ttf": (
        "https://raw.githubusercontent.com/google/fonts/refs/heads/main/ofl/newsreader/"
        "Newsreader%5Bopsz%2Cwght%5D.ttf"
    ),
    "Newsreader-Italic[opsz,wght].ttf": (
        "https://raw.githubusercontent.com/google/fonts/refs/heads/main/ofl/newsreader/"
        "Newsreader-Italic%5Bopsz%2Cwght%5D.ttf"
    ),
    # Inter — v3.19 release (rsms/inter)
    "Inter-Regular.otf": (
        "https://raw.githubusercontent.com/rsms/inter/v3.19/docs/font-files/Inter-Regular.otf"
    ),
    "Inter-Medium.otf": (
        "https://raw.githubusercontent.com/rsms/inter/v3.19/docs/font-files/Inter-Medium.otf"
    ),
    "Inter-SemiBold.otf": (
        "https://raw.githubusercontent.com/rsms/inter/v3.19/docs/font-files/Inter-SemiBold.otf"
    ),
}

_FONTS_REGISTERED = False


def setup_fonts() -> None:
    """Download Newsreader + Inter (if not already present) and register with matplotlib."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    FONTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in _FONT_URLS.items():
        dest = FONTS_DIR / filename
        if dest.exists():
            continue
        try:
            print(f"  downloading font {filename} …")
            urllib.request.urlretrieve(url, dest)  # noqa: S310
        except Exception as exc:  # noqa: BLE001
            log.warning("Font download failed for %s (%s): %s — falling back to system fonts",
                        filename, url, exc)
            if dest.exists():
                dest.unlink()  # remove partial file

    # Register whatever we successfully downloaded
    for f in FONTS_DIR.glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception as exc:  # noqa: BLE001
            log.warning("Could not register font %s: %s", f.name, exc)
    for f in FONTS_DIR.glob("*.otf"):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception as exc:  # noqa: BLE001
            log.warning("Could not register font %s: %s", f.name, exc)

    _FONTS_REGISTERED = True


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

def apply_theme() -> None:
    """Apply editorial rcParams globally (call once at module import)."""
    plt.rcParams.update({
        # --- Typography ---
        "font.family":           "serif",
        "font.serif":            ["Newsreader", "Georgia", "DejaVu Serif", "serif"],
        "font.sans-serif":       ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size":             13,
        # --- Axes titles / labels ---
        "axes.titlesize":        14,
        "axes.titleweight":      "600",
        "axes.titlecolor":       PALETTE["ink"],
        "axes.labelcolor":       PALETTE["ink"],
        "axes.labelweight":      "500",
        # --- Spines ---
        "axes.spines.top":       False,
        "axes.spines.right":     False,
        "axes.spines.left":      True,
        "axes.spines.bottom":    True,
        "axes.linewidth":        0.8,
        "axes.edgecolor":        PALETTE["mute"],
        # --- Ticks ---
        "xtick.color":           PALETTE["mute"],
        "ytick.color":           PALETTE["mute"],
        "xtick.labelsize":       12,
        "ytick.labelsize":       12,
        "xtick.major.size":      3,
        "ytick.major.size":      3,
        "xtick.major.width":     0.8,
        "ytick.major.width":     0.8,
        "xtick.labelcolor":      PALETTE["mute"],
        "ytick.labelcolor":      PALETTE["mute"],
        # --- Grid ---
        "axes.grid":             True,
        "axes.axisbelow":        True,
        "grid.color":            PALETTE["light"],
        "grid.linewidth":        0.6,
        "grid.alpha":            1.0,
        # --- Figure / background ---
        "figure.facecolor":      PALETTE["paper"],
        "axes.facecolor":        PALETTE["paper"],
        "figure.dpi":            100,
        # --- Save ---
        "savefig.facecolor":     PALETTE["paper"],
        "savefig.dpi":           200,
        "savefig.bbox":          "tight",
        # --- Font embedding ---
        "pdf.fonttype":          42,
    })


# ---------------------------------------------------------------------------
# Per-axes polish
# ---------------------------------------------------------------------------

def style_axes(ax: "matplotlib.axes.Axes") -> None:
    """Post-hoc per-axes styling: horizontal-only grid, Inter tick labels."""
    # Horizontal gridlines only
    ax.xaxis.grid(False)
    ax.yaxis.grid(True)

    # Tick label font → Inter (sans-serif)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("sans-serif")
        label.set_fontsize(12)

    # Axis labels → Inter weight 500
    ax.xaxis.label.set_fontfamily("sans-serif")
    ax.xaxis.label.set_fontweight("500")
    ax.yaxis.label.set_fontfamily("sans-serif")
    ax.yaxis.label.set_fontweight("500")


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def editorial_save(
    fig: "matplotlib.figure.Figure",
    name: str,
    *,
    title: str,
    subtitle: str,
    source: str,
    top: float = 0.84,
    bottom: float = 0.10,
    left: float = 0.10,
    right: float = 0.94,
) -> None:
    """Place editorial title/subtitle and save at retina DPI.

    Typography hierarchy:
      - Title   : Newsreader 17pt, weight 600, ink, left-aligned
      - Subtitle : Inter 11.5pt, weight 400, mute, left-aligned

    Note: source text is no longer rendered into the PNG — it is placed
    in the HTML <figcaption> elements instead.  The `source` parameter is
    kept in the signature so callers do not need to change.
    """
    from pathlib import Path as _Path

    OUT = _Path(__file__).resolve().parents[1] / "figures" / "sketches"
    OUT.mkdir(parents=True, exist_ok=True)

    # Apply per-axes polish to every axes in the figure
    for ax in fig.get_axes():
        try:
            style_axes(ax)
        except Exception:  # noqa: BLE001
            pass

    # Title — Newsreader serif
    fig.text(
        left, 0.96, title,
        ha="left", va="top",
        fontsize=22, fontweight="600",
        color=PALETTE["ink"],
        fontfamily="serif",
    )
    # Subtitle — Inter sans
    fig.text(
        left, 0.91, subtitle,
        ha="left", va="top",
        fontsize=15, fontweight="400",
        color=PALETTE["mute"],
        fontfamily="sans-serif",
    )
    # Source text is intentionally NOT rendered into the PNG.
    # It lives in the HTML <figcaption> elements (see site/index.html).

    fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right)

    out = OUT / name
    fig.savefig(out, dpi=200, facecolor=PALETTE["paper"])
    plt.close(fig)
    print(f"  wrote {out.relative_to(_Path(__file__).resolve().parents[1])}")

"""Shared rose-pine styling, font registration, and the R/S/X/M color code.

Usage:
    from posterstyle import use_mode, PAL, COMP, savefig
    pal = use_mode("dawn")   # or "moon"
"""
import os
import re
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STYLE = os.path.join(ROOT, "style")
FIGS = os.path.join(ROOT, "figs")
os.makedirs(FIGS, exist_ok=True)

# ── register fonts (no system install needed) ───────────────────────────────
for _f in ("SpaceGrotesk.ttf", "Inconsolata.ttf"):
    fm.fontManager.addfont(os.path.join(STYLE, "fonts", _f))
SANS = "Space Grotesk"
MONO = "Inconsolata"

# ── rose-pine palettes (canonical hex) ──────────────────────────────────────
# https://rosepinetheme.com/palette/
# NOTE: dawn `base` is forced to pure white (#ffffff) — not rose-pine's #faf4ed —
# so figures sit flush on the white poster background. Accent hues are unchanged.
DAWN = dict(base="#ffffff", surface="#ffffff", overlay="#f2e9e1", muted="#9893a5",
            subtle="#797593", text="#575279", love="#b4637a", gold="#ea9d34",
            rose="#d7827e", pine="#286983", foam="#56949f", iris="#907aa9",
            hl_low="#f4ede8", hl_med="#dfdad9", hl_high="#cecacd")
MOON = dict(base="#232136", surface="#2a273f", overlay="#393552", muted="#6e6a86",
            subtle="#908caa", text="#e0def4", love="#eb6f92", gold="#f6c177",
            rose="#ea9a97", pine="#3e8fb0", foam="#9ccfd8", iris="#c4a7e7",
            hl_low="#2a283e", hl_med="#44415a", hl_high="#56526e")
PAL = DAWN  # rebound by use_mode

# Component color code — reused across every figure. S is the hero.
def comp_colors(pal):
    return {
        "R": pal["iris"],   # retrieval
        "S": pal["love"],   # refine-loop / stop-hook  (HERO)
        "X": pal["foam"],   # validator
        "M": pal["gold"],   # memory
        "base": pal["muted"],   # vanilla / baseline
        "good": pal["pine"],
        "bad": pal["love"],
    }
COMP = comp_colors(PAL)


def heat_cmap(pal):
    """bad(love) -> mid(gold) -> good(foam/pine) sequential, on-palette."""
    return LinearSegmentedColormap.from_list(
        "rp_heat", [pal["love"], pal["gold"], pal["foam"], pal["pine"]])


# ── runtime state set by use_mode() ─────────────────────────────────────────
SANS_ACTIVE = SANS   # the display/title face for the current variant
CAPS = False         # uppercase display (sans) text?
OUTDIR = FIGS        # where savefig writes
DPI = 600            # raster output dpi (poster-grade)


def use_mode(mode="dawn", typeface="grotesk", caps=False, dpi=600, outdir=None):
    """Apply the rose-pine style + fonts; return the active palette dict.

    typeface: "grotesk" (Space Grotesk display + Inconsolata numbers) or
              "inconsolata" (Inconsolata everywhere).
    caps:     uppercase the display (sans) text only — numbers/mono stay as-is.
    """
    global PAL, COMP, SANS_ACTIVE, CAPS, OUTDIR, DPI
    name = "rose-pine-dawn" if mode == "dawn" else "rose-pine-moon"
    plt.style.use(os.path.join(STYLE, f"{name}.mplstyle"))
    PAL = DAWN if mode == "dawn" else MOON
    COMP = comp_colors(PAL)
    SANS_ACTIVE = MONO if typeface == "inconsolata" else SANS
    CAPS = caps
    DPI = dpi
    OUTDIR = outdir or FIGS
    os.makedirs(OUTDIR, exist_ok=True)
    mpl.rcParams.update({
        "font.family": SANS_ACTIVE,
        "font.size": 13,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelsize": 13,
        "axes.labelweight": "medium",
        "figure.titlesize": 18,
        "figure.titleweight": "bold",
        "axes.grid": True,
        "axes.grid.axis": "x",
        "grid.alpha": 0.5,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.dpi": dpi,
        "savefig.bbox": "tight",
        "figure.dpi": 130,
        # background follows the palette base (white for dawn, dark for moon)
        "figure.facecolor": PAL["base"],
        "axes.facecolor": PAL["base"],
        "savefig.facecolor": PAL["base"],
        # gridlines need a touch more contrast against pure white
        "grid.color": "#e4dee4" if mode == "dawn" else "#26233a",
    })
    return PAL


def titled(ax, title, subtitle=None, pad=36, sub_mono=False, sub_size=11.5):
    """Bold main title well clear of a small subtitle pinned just above the axes."""
    ax.set_title(title, pad=pad)
    if subtitle:
        ax.text(0.5, 1.006, subtitle, transform=ax.transAxes, ha="center",
                va="bottom", fontsize=sub_size, color=PAL["subtle"],
                fontfamily=(MONO if sub_mono else SANS_ACTIVE))


def _caps_outside_math(s):
    """Uppercase everything except $...$ mathtext segments (so $\\sigma$ survives)."""
    return "".join(p if p.startswith("$") else p.upper()
                   for p in re.split(r"(\$[^$]*\$)", s))


def _apply_caps(fig):
    """Uppercase display text drawn in the active sans face; leave mono numbers
    and tick labels alone. Mathtext (e.g. $\\sigma$) is preserved."""
    for t in fig.findobj(match=mpl.text.Text):
        fams = t.get_fontfamily()
        s = t.get_text()
        if not s:
            continue
        if SANS_ACTIVE in fams and MONO not in fams:
            t.set_text(_caps_outside_math(s))


def savefig(fig, name):
    if CAPS:
        _apply_caps(fig)
    rel = os.path.relpath(OUTDIR, ROOT)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUTDIR, f"{name}.{ext}"), facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  wrote {rel}/{name}.png / .pdf")

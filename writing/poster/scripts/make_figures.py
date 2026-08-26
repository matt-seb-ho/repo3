"""Render the six SIGA poster figures in both light (dawn) and dark (moon) modes.

    python scripts/make_figures.py            # both modes
    python scripts/make_figures.py dawn       # one mode
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

import posterstyle as ps
import figdata as D


# ════════════════════════════════════════════════════════════════════════════
# F1 — Headline: reliability not ceiling (held-out-eval). Lollipop + error bars.
# ════════════════════════════════════════════════════════════════════════════
def fig1(pal):
    cells = D.HELDOUT
    y = np.arange(len(cells))[::-1]          # Vanilla on top
    means = [m for _, m, _ in cells]
    stds = [s for _, _, s in cells]
    labels = [c for c, _, _ in cells]

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    for yi, (lab, m, s) in zip(y, cells):
        is_van = lab == "Vanilla"
        col = ps.COMP["base"] if is_van else ps.COMP["S"]
        # error bar = ±1 sample std
        ax.errorbar(m, yi, xerr=s, fmt="none", ecolor=col, elinewidth=3.2,
                    capsize=7, capthick=3.2, alpha=0.55, zorder=2)
        ax.plot([0.66, m], [yi, yi], color=col, lw=1.4, alpha=0.28, zorder=1)  # stem
        ax.scatter(m, yi, s=190 if lab != "SE" else 300,
                   color=col, edgecolor=pal["base"], linewidth=1.4,
                   marker="o" if lab != "SE" else "*", zorder=4)
        ax.annotate(f"{m:.3f}", (m, yi), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=11, color=pal["text"],
                    fontweight="bold")
        ax.annotate(rf"$\sigma$={s:.3f}", (m + s, yi), textcoords="offset points",
                    xytext=(10, 0), va="center", ha="left", fontsize=10,
                    color=col, fontfamily=ps.MONO,
                    fontweight="bold" if is_van else "normal")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontfamily=ps.MONO, fontsize=12)
    ax.set_xlim(0.66, 0.90)
    ax.set_ylim(-0.7, 5.75)   # headroom so the top value label clears the subtitle
    ax.set_xlabel(r"Held-out-eval TreeSim  (mean ± across-seed $\sigma$, n=3)")
    ps.titled(ax, "Adapters buy reliability, not a higher ceiling",
              r"across-seed $\sigma$ collapses $\approx$10$\times$  (0.081 $\to$ 0.002)  while the hard-tail mean lifts +0.069")
    # callout on the Vanilla wide error bar (its left tail is clipped at xlim)
    ax.annotate("one seed → unparseable XML → 0",
                xy=(0.681, y[0]), xytext=(0.690, y[0] - 0.70),
                fontsize=9.5, color=ps.COMP["base"], ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color=ps.COMP["base"], lw=1.2,
                                connectionstyle="arc3,rad=0.2"))
    leg = [Line2D([0], [0], marker="o", color="none", markerfacecolor=ps.COMP["base"],
                  markersize=11, label="Vanilla (baseline)"),
           Line2D([0], [0], marker="o", color="none", markerfacecolor=ps.COMP["S"],
                  markersize=11, label="S-family adapter"),
           Line2D([0], [0], marker="*", color="none", markerfacecolor=ps.COMP["S"],
                  markersize=15, label="SE (self-evolved, best)")]
    ax.legend(handles=leg, loc="lower right", frameon=False, fontsize=10.5)
    fig.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════════════════
# F2 — Tail-localized gains. Slopegraph Vanilla -> SE over 10 held-out tasks.
# ════════════════════════════════════════════════════════════════════════════
def fig2(pal):
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    x0, x1 = 0, 1
    for task, v, se in D.PER_TASK:
        rescue = task in D.RESCUE_TASKS
        col = ps.COMP["S"] if rescue else pal["muted"]
        lw = 3.2 if rescue else 1.4
        alpha = 1.0 if rescue else 0.5
        z = 5 if rescue else 2
        ax.plot([x0, x1], [v, se], color=col, lw=lw, alpha=alpha, zorder=z,
                solid_capstyle="round")
        ax.scatter([x0, x1], [v, se], s=55 if rescue else 28, color=col,
                   zorder=z + 1, edgecolor=pal["base"], linewidth=1.0)
        if rescue:
            short = task.replace("AdvancedExample", "").replace("Example", "")
            ax.annotate(f"{short}\n{v:.3f} → {se:.3f}", (x1, se),
                        textcoords="offset points", xytext=(12, 0), va="center",
                        fontsize=10, color=ps.COMP["S"], fontweight="bold")
    # endpoints axis cosmetics
    ax.set_xlim(-0.32, 1.55)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xticks([x0, x1])
    ax.set_xticklabels(["Vanilla", "SE"], fontsize=14, fontweight="bold")
    ax.set_ylabel("Held-out-eval TreeSim (mean of 3 seeds)")
    ps.titled(ax, "The +0.069 gain is tail-localized",
              "two catastrophic rescues carry the lift; the other 8 tasks move within seed noise")
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", alpha=0.4)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    # "8 tasks ~flat" bracket annotation
    ax.annotate("8 tasks: within noise", (x0, 0.93), textcoords="offset points",
                xytext=(-8, 0), ha="right", va="center", fontsize=10,
                color=pal["muted"], fontstyle="italic")
    fig.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════════════════
# F3 — Human baseline. Log-x scatter: wall-clock vs deck-level quality.
# ════════════════════════════════════════════════════════════════════════════
def fig3(pal):
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    style = {
        "human":      dict(color=pal["muted"], marker="o", s=150),
        "agent_base": dict(color=ps.COMP["base"], marker="s", s=160),
        "agent_siga": dict(color=ps.COMP["S"], marker="*", s=520),
    }
    # per-label text offsets (points) to avoid collisions, esp. the two 1h experts
    OFF = {
        "Expert 1 (1h cutoff)": (-48, 14, "right"),
        "Expert 2 (1h cutoff)": (42, -20, "left"),
        "Expert 1 (no cap)":    (0, 16, "center"),
        "Vanilla CC":           (-10, -26, "center"),
        "SIGA X+M":             (0, 22, "center"),
    }
    pts = {}
    for lab, deck, lb, wall, _f, kind in D.HUMAN:
        st = style[kind]
        ax.scatter(wall, deck, edgecolor=pal["base"], linewidth=1.3, zorder=4,
                   **{k: v for k, v in st.items()})
        pts[lab] = (wall, deck)
        txt = (f"$\\geq${deck:.2f}" if lb else f"{deck:.3f}")
        dx, dy, ha = OFF[lab]
        ax.annotate(f"{lab}\n{txt} @ {wall:.0f} min", (wall, deck),
                    textcoords="offset points", xytext=(dx, dy), ha=ha,
                    fontsize=9.5, color=pal["text"], fontweight="medium")
    # 36x speed arrow: SIGA X+M vs Expert-1 no-cap (parity quality)
    (wx, dx), (we, de) = pts["SIGA X+M"], pts["Expert 1 (no cap)"]
    arr = FancyArrowPatch((we, de - 0.02), (wx + 0.4, dx - 0.0),
                          arrowstyle="-|>", mutation_scale=18,
                          color=ps.COMP["good"], lw=2.0, ls="--", zorder=3)
    ax.add_patch(arr)
    ax.annotate("same deck quality,\n≈36× faster", ((wx * we) ** 0.5, 0.79),
                ha="center", fontsize=11, color=ps.COMP["good"], fontweight="bold")
    ax.axhspan(0.90, 1.0, color=ps.COMP["good"], alpha=0.06, zorder=0)
    ax.set_xscale("log")
    ax.set_xlim(3, 400)
    ax.set_ylim(0.45, 1.0)
    ax.set_xticks([5, 10, 30, 60, 180])
    ax.set_xticklabels(["5", "10", "30", "60", "180"], fontfamily=ps.MONO)
    ax.set_xlabel("Wall-clock to author the deck  (minutes, log scale)")
    ax.set_ylabel("Deck-level TreeSim")
    ps.titled(ax, "SIGA hits expert deck quality in a fraction of the time",
              "buckleyLeverettProblem · both 1-hour experts timed out before finishing both files")
    fig.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════════════════
# F4 — Cross-model / cross-harness. Dumbbell Vanilla -> X+M (+ SE) per backbone.
# ════════════════════════════════════════════════════════════════════════════
def fig4(pal):
    rows = D.CROSS
    y = np.arange(len(rows))[::-1]
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    for yi, (h, bb, n, van, xm, se, vf, xf, sf) in zip(y, rows):
        ax.plot([van, xm], [yi, yi], color=pal["subtle"], lw=2.2, alpha=0.45, zorder=1)
        ax.scatter(van, yi, s=150, color=ps.COMP["base"], edgecolor=pal["base"],
                   linewidth=1.2, zorder=3)
        ax.scatter(xm, yi, s=170, color=ps.COMP["S"], edgecolor=pal["base"],
                   linewidth=1.2, zorder=3)
        if se is not None:
            ax.scatter(se, yi, s=150, marker="*", color=ps.COMP["M"],
                       edgecolor=pal["base"], linewidth=1.0, zorder=4)
        d = xm - van
        ax.annotate(f"+{d:.3f}", (max(van, xm), yi), textcoords="offset points",
                    xytext=(12, 0), va="center", fontsize=10.5,
                    color=ps.COMP["good"], fontweight="bold", fontfamily=ps.MONO)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{h} · {bb}\n(n={n})" for h, bb, n, *_ in rows],
                       fontsize=10.5, fontfamily=ps.MONO)
    ax.set_xlim(0.74, 0.96)
    ax.set_xlabel("val TreeSim")
    ps.titled(ax, "X+M lifts every backbone and harness",
              "the Vanilla→X+M improvement holds across 3 model families and 2 harnesses (CC, OpenHands)")
    leg = [Line2D([0], [0], marker="o", color="none", markerfacecolor=ps.COMP["base"],
                  markersize=11, label="Vanilla"),
           Line2D([0], [0], marker="o", color="none", markerfacecolor=ps.COMP["S"],
                  markersize=11, label="X+M"),
           Line2D([0], [0], marker="*", color="none", markerfacecolor=ps.COMP["M"],
                  markersize=14, label="SE")]
    ax.legend(handles=leg, loc="upper left", frameon=False, fontsize=10.5, ncol=1)
    fig.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════════════════
# F5 — OpenFOAM per-task heatmap (cells × 5 tasks). Zeros glare in non-S cells.
# ════════════════════════════════════════════════════════════════════════════
def fig5(pal):
    rows = D.OPENFOAM_PER_TASK
    M = np.array([r[1] for r in rows])
    labels = [r[0] for r in rows]
    has_S = [r[2] for r in rows]
    fig, ax = plt.subplots(figsize=(8.8, 6.2))
    cmap = ps.heat_cmap(pal)
    im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(D.OPENFOAM_TASKS)))
    ax.set_xticklabels(D.OPENFOAM_TASKS, fontsize=9.5, fontfamily=ps.MONO)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontfamily=ps.MONO, fontsize=11)
    # bold + hero-color the S-enabled row labels
    for tick, s in zip(ax.get_yticklabels(), has_S):
        if s:
            tick.set_color(ps.COMP["S"])
            tick.set_fontweight("bold")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            txt = "0" if v == 0 else f"{v:.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9.5,
                    fontfamily=ps.MONO,
                    color=pal["base"] if v > 0.62 or v == 0 else pal["text"],
                    fontweight="bold" if v == 0 else "normal")
            if v == 0:  # ring the catastrophic zeros with a dark outline that
                        # stands out against the red cell and the white cell-mesh
                ax.add_patch(plt.Rectangle((j - 0.46, i - 0.46), 0.92, 0.92, fill=False,
                                           edgecolor=pal["text"], lw=2.6, zorder=5))
    ps.titled(ax, "On OpenFOAM, only S-cells avoid zero-score failures",
              "boxed cells = required files missing (score 0) — concentrated in Vanilla and R+X", pad=40)
    ax.set_xticks(np.arange(-.5, len(D.OPENFOAM_TASKS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color=pal["base"], linewidth=1.2)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("file-text-and-coverage score", fontsize=10.5)
    cb.outline.set_visible(False)
    fig.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════════════════════
# F6 — OpenFOAM effect. Diverging bar Δ vs Vanilla, colored by S-present.
# ════════════════════════════════════════════════════════════════════════════
def fig6(pal):
    rows = [r for r in D.OPENFOAM_SUMMARY if r[2] is not None]  # drop Vanilla(ref)
    rows = sorted(rows, key=lambda r: r[2])
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    for yi, (cell, mean, d, cov, hasS, kind) in zip(y, rows):
        if kind == "baseline":
            col = pal["subtle"]
        elif hasS:
            col = ps.COMP["S"]
        else:
            col = ps.COMP["base"]
        ax.barh(yi, d, color=col, edgecolor=pal["base"], linewidth=0.8,
                height=0.66, zorder=2, alpha=0.95)
        ha = "left" if d > 0 else "right"
        off = 6 if d > 0 else -6
        ax.annotate(f"{d:+.3f}   ({cov}/5 files)", (d, yi),
                    textcoords="offset points", xytext=(off, 0), va="center",
                    ha=ha, fontsize=10, color=pal["text"], fontfamily=ps.MONO)
    ax.axvline(0, color=pal["text"], lw=1.3, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontfamily=ps.MONO, fontsize=11)
    for tick, r in zip(ax.get_yticklabels(), rows):
        if r[4]:
            tick.set_color(ps.COMP["S"]); tick.set_fontweight("bold")
    ax.set_xlim(-0.66, 0.66)
    ax.set_xlabel("Δ mean score vs Vanilla")
    ps.titled(ax, "S is the dominant transferable factor",
              "OpenFOAM factor effects:  S +0.328   M +0.192   R -0.050   X -0.073",
              sub_mono=True)
    leg = [Line2D([0], [0], marker="s", color="none", markerfacecolor=ps.COMP["S"],
                  markersize=12, label="contains S"),
           Line2D([0], [0], marker="s", color="none", markerfacecolor=ps.COMP["base"],
                  markersize=12, label="no S"),
           Line2D([0], [0], marker="s", color="none", markerfacecolor=pal["subtle"],
                  markersize=12, label="Foam-Agent baseline")]
    ax.legend(handles=leg, loc="lower right", frameon=False, fontsize=10)
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    return fig


FIGS = {"f1_reliability": fig1, "f2_tail_gains": fig2, "f3_human_baseline": fig3,
        "f4_cross_model": fig4, "f5_openfoam_heatmap": fig5, "f6_openfoam_effect": fig6}


# Font variants -> separate output folders. DPI is poster-grade (600).
# PRIMARY = inconsolata, dawn (white bg). Others are alternatives for comparison.
VARIANTS = {
    "inconsolata":  dict(typeface="inconsolata", caps=False, outdir=ps.FIGS),  # PRIMARY -> figs/
    "grotesk":      dict(typeface="grotesk",     caps=False,
                         outdir=os.path.join(ps.ROOT, "figs_alt_grotesk")),
    "grotesk_caps": dict(typeface="grotesk",     caps=True,
                         outdir=os.path.join(ps.ROOT, "figs_alt_caps")),
}
DPI = 600


def main():
    args = sys.argv[1:]
    modes = [a for a in args if a in ("dawn", "moon")] or ["dawn", "moon"]
    variants = [a for a in args if a in VARIANTS] or list(VARIANTS)
    for variant in variants:
        cfg = VARIANTS[variant]
        print(f"=== variant: {variant}  ({cfg['outdir'].split('/')[-1]}, {DPI} dpi) ===")
        for mode in modes:
            pal = ps.use_mode(mode, dpi=DPI, **cfg)
            print(f"[{mode}]")
            for name, fn in FIGS.items():
                fig = fn(pal)
                ps.savefig(fig, f"{name}_{mode}")


if __name__ == "__main__":
    main()

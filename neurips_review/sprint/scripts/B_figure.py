#!/usr/bin/env python3
"""
Thread B — LMaaJ figure. rose-pine dawn + moon, Space Grotesk labels, Inconsolata numerals.
Four different chart types (advisor's standing rule: charts over tables, and vary the type).

  (a) dumbbell     - TreeSim vs LMaaJ per cell, on one axis
  (b) stacked bar  - severity spectrum of TreeSim-flagged differences, per cell
  (c) scatter      - per-deck TreeSim vs LMaaJ, identity line, marker = rung-1/2 outcome
  (d) strip        - LMaaJ split by schema-validity outcome (execution calibration)
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/home/matt/sci/repo3/writing/poster/scripts")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import posterstyle as ps

ART = "/home/matt/sci/repo3/neurips_review/sprint/artifacts"
OUT = os.path.join(ART, "figs")
os.makedirs(OUT, exist_ok=True)

CELLS = ["F0", "F6", "SE"]
LABEL = {"F0": "Vanilla", "F6": "S+X", "SE": "SE"}
SEV = ["cosmetic", "minor", "material", "severe"]


def main():
    A = json.load(open(os.path.join(ART, "B_analysis.json")))
    decks = [r for r in csv.DictReader(open(os.path.join(ART, "B_deck_scores.csv")))]

    for mode in ("dawn", "moon"):
        pal = ps.use_mode(mode, outdir=OUT)
        C = ps.comp_colors(pal)
        ccol = {"F0": C["base"], "F6": C["X"], "SE": C["S"]}
        sevcol = {"cosmetic": pal["foam"], "minor": pal["pine"],
                  "material": pal["gold"], "severe": pal["love"]}

        fig, axs = plt.subplots(2, 2, figsize=(13.6, 10.4))
        fig.patch.set_facecolor(pal["base"])
        (ax1, ax2), (ax3, ax4) = axs

        # ---------------- (a) slope chart: the ranking is judge-dependent (headline, honest)
        JLAB = {"gemini3flash": "Gemini 3 Flash", "gpt54mini": "GPT-5.4-mini",
                "qwen3235b": "Qwen3-235B"}
        jstyle = {"gemini3flash": (pal["iris"], "o", "-"),
                  "gpt54mini": (pal["gold"], "s", "-"),
                  "qwen3235b": (pal["pine"], "^", "-")}
        xs = list(range(len(CELLS)))
        pj = A["per_judge_cell_means"]
        # TreeSim reference, rescaled reading on the same axis
        ts = [A["score_table"][c]["treesim"][0] for c in CELLS]
        ax1.plot(xs, ts, ls=(0, (4, 3)), lw=2.2, marker="D", ms=9,
                 color=pal["muted"], zorder=2, label="TreeSim")
        for j, (col, mk, ls) in jstyle.items():
            if j not in pj:
                continue
            ys_ = [pj[j]["means"][c][0] for c in CELLS]
            ax1.plot(xs, ys_, ls=ls, lw=2.6, marker=mk, ms=10, color=col,
                     zorder=3, label=JLAB.get(j, j))
        ax1.set_xticks(xs)
        ax1.set_xticklabels([LABEL[c] for c in CELLS])
        ax1.set_xlim(-0.35, len(CELLS) - 0.65)
        ax1.set_ylabel("mean score")
        ps.titled(ax1, "The cell ranking depends on which judge you ask",
                  "three judges, three different orderings; GPT-5.4-mini puts Vanilla above S+X")
        ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4,
                   frameon=False, fontsize=10.5, columnspacing=1.4, handletextpad=0.5)

        # ---------------- (b) stacked bar: severity spectrum
        for i, cell in enumerate(CELLS):
            s = A["severity_spectrum"][cell]
            left = 0.0
            for k in SEV:
                v = s[k]
                ax2.barh(i, v, left=left, color=sevcol[k], edgecolor=pal["base"], height=0.62)
                if v > 0.04:
                    ax2.text(left + v / 2, i, f"{v:.0%}", ha="center", va="center",
                             fontfamily=ps.MONO, fontsize=10.5,
                             color=pal["base"] if k in ("severe", "minor") else pal["text"])
                left += v
        ax2.set_yticks(range(len(CELLS)))
        ax2.set_yticklabels([LABEL[c] for c in CELLS])
        ax2.set_xlim(0, 1)
        ax2.set_xlabel("share of differences TreeSim scored as total failures")
        ps.titled(ax2, "Most TreeSim mismatches are not physical errors",
                  "all of these score zero under TreeSim; judges differ on the exact share")
        ax2.legend(handles=[Line2D([], [], marker="s", ls="", ms=11, color=sevcol[k], label=k)
                            for k in SEV],
                   loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4, frameon=False)

        # ---------------- (c) scatter: per-deck, marker = rung outcome
        ax3.plot([0, 1], [0, 1], ls=(0, (4, 4)), lw=1.4, color=pal["hl_high"], zorder=1)
        for cell in CELLS:
            for pas, mk, ms_ in ((True, "o", 52), (False, "X", 130)):
                xs, ysc = [], []
                for d in decks:
                    if d["cell"] != cell or not d["lmaaj"]:
                        continue
                    ok = (d.get("rung2") == "1")
                    if ok != pas:
                        continue
                    xs.append(float(d["treesim"]))
                    ysc.append(float(d["lmaaj"]))
                if xs:
                    ax3.scatter(xs, ysc, s=ms_, marker=mk, color=ccol[cell],
                                alpha=0.85 if pas else 1.0, linewidths=0.6,
                                edgecolors=pal["base"], zorder=3)
        ax3.set_xlabel("TreeSim")
        ax3.set_ylabel("LMaaJ")
        ax3.set_xlim(-0.03, 1.03)
        ax3.set_ylim(-0.03, 1.03)
        r = A["treesim_corr"]["all"]
        # Space Grotesk / Inconsolata have no Greek glyphs: render rho via mathtext.
        ps.titled(ax3, "Where the two metrics disagree",
                  f"n={r['n']} decks   Spearman $\\rho$ = {r['spearman']:+.2f}   cross = schema-invalid",
                  sub_size=10.5)
        ax3.legend(handles=[Line2D([], [], marker="o", ls="", ms=9, color=ccol[c],
                                   label=LABEL[c]) for c in CELLS],
                   loc="lower right", frameon=False)

        # ---------------- (d) strip: execution calibration
        cal = A.get("execution_calibration", {}).get("rung3", {})
        groups = [("GEOS accepts input", True), ("GEOS rejects input", False)]
        for gi, (gl, pas) in enumerate(groups):
            for metric, dx, mk in (("treesim", -0.17, "o"), ("lmaaj", 0.17, "D")):
                vals, cols = [], []
                for d in decks:
                    if not d["lmaaj"]:
                        continue
                    if (d.get("rung3") == "1") != pas:
                        continue
                    vals.append(float(d[metric]))
                    cols.append(ccol[d["cell"]])
                if not vals:
                    continue
                import random
                random.seed(0)
                xj = [gi + dx + random.uniform(-0.055, 0.055) for _ in vals]
                ax4.scatter(xj, vals, s=44, marker=mk, c=cols, alpha=0.8,
                            linewidths=0.5, edgecolors=pal["base"], zorder=3)
                m = sum(vals) / len(vals)
                ax4.plot([gi + dx - 0.11, gi + dx + 0.11], [m, m], lw=3,
                         color=pal["text"], zorder=4)
                ax4.annotate(f"{m:.3f}", (gi + dx, m), textcoords="offset points",
                             xytext=(-26 if metric == "treesim" else 26, -4),
                             ha="right" if metric == "treesim" else "left",
                             fontfamily=ps.MONO, fontsize=10.5, color=pal["text"])
        ax4.set_xticks(range(len(groups)))
        ax4.set_xticklabels([g[0] for g in groups])
        ax4.set_xlim(-0.5, len(groups) - 0.5)
        ax4.set_ylim(-0.03, 1.06)
        ax4.set_ylabel("score")
        sub = "rung 3   circle = TreeSim   diamond = LMaaJ   bar = mean"
        if cal.get("lmaaj"):
            sub += f"   LMaaJ $r_{{pb}}$ = {cal['lmaaj']['r_pointbiserial']:+.2f}"
        ps.titled(ax4, "Both metrics track what the simulator accepts", sub, sub_size=10.5)

        for ax in (ax1, ax2, ax3, ax4):
            for lbl in ax.get_xticklabels() + ax.get_yticklabels():
                lbl.set_fontfamily(ps.MONO)
        for ax in (ax1, ax2):
            for lbl in ax.get_yticklabels():
                lbl.set_fontfamily(ps.SANS_ACTIVE)
        for lbl in ax4.get_xticklabels():
            lbl.set_fontfamily(ps.SANS_ACTIVE)

        fig.tight_layout(pad=2.4, h_pad=4.2, w_pad=3.0)
        ps.savefig(fig, f"B_lmaaj_{mode}")


if __name__ == "__main__":
    main()

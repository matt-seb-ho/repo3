# Poster figure plan — SIGA

Advisor note: *"For all presentation, we should use either chart or figures to illustrate
results."* → Replace the paper's four results **tables** with abstracted, fast-to-read
**charts**, with deliberate **chart-type variety** (not six bar charts).

## Theme & type
- **Palette:** rose-pine (`h4pZ/rose-pine-matplotlib`). Rendered in two modes:
  - `dawn` — light background `#faf4ed` (**canonical for the printed poster**)
  - `moon` — dark background `#232136` (for slides/screen)
- **Fonts:** Space Grotesk (titles/labels), Inconsolata (numbers + monospaced task names).
- **Component color code, reused across every figure** (the paper asks for cross-figure
  color consistency so a figures-only reader can decode R/S/X/M):
  - **R** retrieval → iris (purple) · **S** refine-loop/stop-hook → **love (rose-red, the HERO)**
  - **X** validator → foam (teal) · **M** memory → gold · **Vanilla/baseline** → muted grey

## The six figures (one chart type each — no repeats)

| # | Source table | Story in one line | Chart type |
|---|--------------|-------------------|------------|
| **F1** | Main ablation (Tab 1) | Adapters collapse across-seed variance ~10× and lift the hard-tail mean — reliability, not ceiling | **Horizontal lollipop + error bars** |
| **F2** | Per-task held-out (Tab 1 detail) | The +0.069 gain is tail-localized: 2 catastrophic rescues, 8 tasks flat | **Slopegraph** (Vanilla→SE, 10 lines, 2 highlighted) |
| **F3** | Human baseline (Tab 2) | SIGA reaches expert deck quality at ~1/36 the wall-clock | **Log-x scatter** (time vs quality) |
| **F4** | Cross-model/harness (Tab 3) | X+M beats Vanilla on every backbone & harness | **Dumbbell / connected-dots** |
| **F5** | OpenFOAM per-task (Tab 4) | Zero-score failures concentrate in non-S cells; S-cells never zero | **Heatmap** (cells × 5 tasks) |
| **F6** | OpenFOAM summary (Tab 4) | S is the dominant transferable factor; R+X is catastrophic | **Diverging bar** (Δ vs Vanilla, colored by S) |

Optional extras (built only if useful): F7 failure-category grouped bar (missing_block drops,
bad_attribute persists); OpenFOAM factor-effect mini-bar (R/S/X/M).

## Layout
`scripts/figdata.py` (numbers transcribed verbatim from `neurips_2026.tex`), `scripts/posterstyle.py`
(theme + fonts + palette), `scripts/make_figures.py` (renders all). Output → `figs/*_dawn.{png,pdf}`
and `figs/*_moon.{png,pdf}` at 300 dpi.

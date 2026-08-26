# Poster figures — what I cooked up

Your advisor's note ("for all presentation, use chart or figures, not tables") is the
governing constraint. I turned the paper's four results **tables** into six **charts**,
deliberately using **six different chart types** so the poster has visual variety rather
than a wall of bar charts.

- **PRIMARY set = `figs/`** — Inconsolata typeface, rose-pine **dawn** palette, on a **pure
  white background** (`#ffffff`) to sit flush on the poster. Use `*_dawn.*` for the poster.
- **Theme:** [rose-pine](https://github.com/h4pZ/rose-pine-matplotlib). `*_dawn.*` = white
  background (poster); `*_moon.*` = dark background (slides/screen). Every figure is written
  as PNG (**600 dpi**, ~5400×2860 px) **and PDF (vector)** — use the PDFs in the poster for
  crisp scaling at any size.
- **Font variants** (same figures, different typography). The primary is first:
  | Folder | Display face | Numbers/labels | Notes |
  |--------|--------------|----------------|-------|
  | **`figs/`** | **Inconsolata** | Inconsolata | **the main version** — all-mono, cohesive, white bg |
  | `figs_alt_grotesk/` | Space Grotesk | Inconsolata | two-font alternative |
  | `figs_alt_caps/` | Space Grotesk **ALL CAPS** | Inconsolata | caps display; mono data labels stay mixed-case |
  Fonts are bundled in `style/fonts/` and registered at runtime — nothing installed system-wide.
  The white background applies to the `dawn` mode of every variant; `moon` stays dark.
- **Cross-figure color code** (so a figures-only reader can decode R/S/X/M everywhere):
  **R** retrieval = iris/purple · **S** refine-loop = **love/rose-red (the hero)** ·
  **X** validator = teal · **M** memory = gold · **Vanilla/baseline** = muted grey.
  S is the paper's punchline, so it always wears the signature rose-pine red.

## The six figures

| # | File | Replaces | Chart type | Headline it sells |
|---|------|----------|------------|-------------------|
| F1 | `f1_reliability` | Table 1 (main ablation) | horizontal **lollipop + error bars** | adapters collapse across-seed σ ~10× and lift the hard-tail mean — reliability, not ceiling |
| F2 | `f2_tail_gains` | Table 1 / per-task appendix | **slopegraph** | the +0.069 gain is *tail-localized*: two catastrophic rescues, eight flat tasks |
| F3 | `f3_human_baseline` | Table 2 (human baseline) | **log-x scatter** | SIGA reaches expert deck quality at ~1/36 the wall-clock |
| F4 | `f4_cross_model` | Table 3 (cross-model/harness) | **dumbbell / connected-dots** | X+M beats Vanilla on every backbone and harness |
| F5 | `f5_openfoam_heatmap` | Table 4b (OpenFOAM per-task) | **heatmap** | zero-score failures concentrate in non-S cells; S-cells never zero |
| F6 | `f6_openfoam_effect` | Table 4 (OpenFOAM summary) | **diverging bar** | S is the dominant transferable factor; R+X is catastrophic |

Chart types used: lollipop, slopegraph, scatter, dumbbell, heatmap, diverging bar — no repeats.

---

### F1 — Reliability, not ceiling  *(replaces the main ablation table)*
![F1](figs/f1_reliability_dawn.png)

The single most important figure. A horizontal lollipop where the **error bar length is the
story**: Vanilla's bar is huge (σ=0.081, driven by one seed emitting unparseable XML → 0),
and every adapter cell collapses to a tiny bar. The eye reads "wide bar → tight bars"
instantly — that's the order-of-magnitude variance drop, plus the modest mean lift to SE
(0.789, the star). This is much more legible than the 11-row × 8-column source table.

### F2 — Tail-localized gains  *(the detail behind the ablation)*
![F2](figs/f2_tail_gains_dawn.png)

A slopegraph from Vanilla→SE over the 10 held-out tasks. Two red lines shoot up (the
`ThermoPoroElasticWellbore` 0.355→0.761 and `ProppantTest` 0.541→0.825 rescues); the other
eight are flat grey. It makes the honest point visually — the aggregate gain is **not**
uniform improvement, it's two rescues. This pre-empts the "is it real?" question a reviewer
at the poster would ask.

### F3 — Human baseline  *(replaces the human-baseline table)*
![F3](figs/f3_human_baseline_dawn.png)

Time-vs-quality scatter on a **log time axis** so the 5-min vs 180-min gap is visible at a
glance. The green dashed arrow connects "Expert 1, no time cap, 0.931 @ 180 min" to
"SIGA X+M, ≥0.90 @ 5 min" — same deck quality, ≈36× faster. The two 1-hour experts sit low
(they timed out before finishing both files), anchoring the "this is genuinely hard" point.

### F4 — Cross-model / cross-harness robustness  *(replaces the generalization table)*
![F4](figs/f4_cross_model_dawn.png)

A dumbbell per backbone: grey dot = Vanilla, red dot = X+M, gold star = SE, with the
+Δ labeled. Every row's red dot sits right of its grey dot → "X+M lifts everywhere"
reads in one second. Works across three model families and two harnesses (CC + OpenHands).

### F5 — OpenFOAM per-task  *(replaces the OpenFOAM per-task table)*
![F5](figs/f5_openfoam_heatmap_dawn.png)

A heatmap (cells × 5 tasks) on a rose-pine red→teal scale. **Boxed red cells are score-0
failures (required files missing)** — they cluster in Vanilla and R+X. S-enabled rows
(red, bold labels) are uniformly warm with no boxed cells. This is the clearest possible
rendering of "the stop-hook prevents silent incompleteness."

### F6 — OpenFOAM effect summary  *(replaces the OpenFOAM summary table)*
![F6](figs/f6_openfoam_effect_dawn.png)

A diverging bar of Δ-vs-Vanilla, colored by whether the cell contains S. The S-cells (red)
stack at the top with full 5/5 coverage; R+X dives to −0.321 with 1/5 coverage. The
factor-effect readout (S +0.328 dominant) sits in the subtitle. This is the "ship S if you
ship one component" slide.

---

## Dark mode
Every figure also exists as `*_moon.png/.pdf` (dark `#232136` background) — the rose-red
pops nicely on dark for slides. Example: `figs/f1_reliability_moon.png`.

## How to regenerate / tweak
```bash
cd writing/poster
source .venv/bin/activate                       # matplotlib + numpy (see requirements.txt)
python scripts/make_figures.py                  # all 3 font variants × both modes, 600 dpi
python scripts/make_figures.py dawn             # one mode, all variants
python scripts/make_figures.py inconsolata      # primary variant, both modes
python scripts/make_figures.py inconsolata dawn # primary variant, poster mode only
```
Variants: `inconsolata` (→ `figs/`, **primary**), `grotesk` (→ `figs_alt_grotesk/`),
`grotesk_caps` (→ `figs_alt_caps/`). DPI is `DPI = 600` in `make_figures.py`; the white
background is `DAWN["base"] = "#ffffff"` in `posterstyle.py`.
- Numbers live in `scripts/figdata.py`, each block citing the source table label in
  `neurips_2026.tex` so they can be re-checked. **All values transcribed verbatim from the
  paper** — nothing recomputed.
- Styling/fonts/palette: `scripts/posterstyle.py`. Change `use_mode("dawn")` defaults there.

## Notes, caveats, and open choices for you
- **Which font variant:** compare `figs/` (two-font), `figs_inconsolata/` (all mono), and
  `figs_grotesk_caps/` (caps display) and tell me which to keep — I'll delete the others.
  The LaTeX Computer-Modern look (via `text.usetex`) is also a one-line change if you want a
  fourth option.
- **σ glyph:** neither Space Grotesk nor Inconsolata ships a Greek sigma, so I render σ via
  matplotlib mathtext (looks consistent; just flagging in case you spot the slightly
  different glyph).
- **F3 `SIGA X+M` point:** the paper reports deck-level as "≥0.90" (a lower bound), so I
  plot it at 0.90 with a "≥" label. If you have the exact number, swap it in `figdata.py`.
- **Possible 7th figure (not built, easy to add):** a grouped bar of failure categories
  (`missing_block` 6→3 drops, `bad_attribute_value` stays ~flat) — the "schema adapters fix
  block omissions, not attribute errors" story (Table `tab:bottleneck`). The paper has `-`
  entries for SE in three categories, so I left it out pending clarification on whether those
  are zeros or not-recorded. Tell me and I'll add it.
- **Poster assembly:** these are standalone result panels. If you want, I can also lay them
  out into a single poster-section composite (e.g., a 2×3 grid PDF) sized to your poster
  template.

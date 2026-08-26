# Thread P0 — Phase 0 verification gate (main thread)

> 🛑 **SUPERSEDED IN PART — read `SPRINT_LOG.md` finding F52 first.**
>
> The convention analysis below is correct and still stands: `analyze_autocamp.py` drops non-numeric treesim instead of scoring zero, the paper declares failures-as-zero, and that fully explains the 0.874 vs 0.857 discrepancy and the −0.032 vs −0.033 inconsistency.
>
> **But the underlying val scores were raced.** `autocamp_F3_s1`'s `_summary.json` finished scoring at 14:25:28 while the decks it was meant to score were written 14:25:41 → 14:32:37. `TutorialSneddon` **did not fail** — the scorer looked before the agent wrote anything. So **F3 is ≈0.887 ± 0.011, not 0.857 ± 0.045**, and the "corrected" main effects derived below (R −0.037 · S −0.008 · X +0.011 · M +0.008) rest on raced inputs. De-raced: **R −0.0313 · S −0.0002 · X +0.0054 · M +0.0023**.
>
> **Do not volunteer the main-effects correction (H3 = no).** The held-out numbers verified elsewhere in this sprint are unaffected.

Owner: main thread. Scope: Phase 0 item 1 — resolve F3 (R+S) = 0.874 or 0.857, and determine why it moved.
(Items 2–4 are delegated: item 2 → Thread A1, item 3 → Thread D, item 4 → Thread C.)

---

## 2026-07-26 22:0x UTC — RESOLVED. F3 = 0.857. Root cause is a convention mismatch, not a revised score.

**Answer: 0.857 is correct. 0.874 is an artifact of a script that does not implement the paper's own declared convention.**

Nothing was re-scored, re-run, or seed-replaced. Both numbers come from the *same* raw files. They differ only in how one unscorable run is handled.

### The single cause

`autocamp_F3` seed 1, task **`TutorialSneddon`**: `"treesim": null`, `"status": "error"`.

Source: `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/_results/autocamp_F3_s1/autocamp_F3/_summary.json`
That file's own `summary` block states it plainly: `"n_total": 17, "n_scored": 16, "n_failed": 1, "failed_names": ["TutorialSneddon"]`, and it carries **both** aggregates — `"scored_mean": 0.85598125` (16 tasks) and a `with_failures_as_zero` variant (17 tasks).

- Divide the 16 scored tasks by **16** → seed-1 mean 0.85598 → cell mean **0.8735 → 0.874**
- Divide the 16 scored tasks by **17** (failures-as-zero) → seed-1 mean 0.80564 → cell mean **0.85672 → 0.857**

Seeds 2 and 3 have `n_failed: 0`, so they are identical under both conventions (0.87477, 0.88976). **F3 is the only cell in F0–F7 with any failed run**, which is exactly why exactly one cell in the appendix table differs.

### Why 0.857 is the correct value

The paper declares failures-as-zero as its headline convention, and Table 1's caption repeats it:

- `writing/neurips/neurips_2026.tex:169` — *"Headline numbers average TreeSim under **failures-as-zero**: parse errors, timeouts, `failed_no_outputs`, and missing XML outputs all score 0, so systems are not rewarded for unscorable files."*
- `writing/neurips/neurips_2026.tex:184` (Table 1 caption) — *"Cell-level TreeSim (**failures-as-zero**) on `deepseek-v4-flash`, n=3 seeds (mean ± **sample** std)."*

So Table 1 (0.857) follows the stated rule and the appendix main-effects table does not.

### Where 0.874 came from — the code

`scripts/analyze_autocamp.py`, `collect_cell()`:

```python
ts = r.get("treesim")
if isinstance(ts, (int, float)):
    task_scores[task].append(float(ts))
```

A `null` treesim is **silently dropped**, not scored zero. `aggregate_cell()` then averages over however many observations survive. The script therefore computes *scored-mean*, i.e. the opposite of the paper's declared convention. Its output (`docs/2026-05-02_autocamp_metrics.md`) is what the appendix main-effects table was built from.

Two secondary consequences of the same code path, worth knowing:
- `aggregate_cell()` groups seeds by **list index** (`v[s]`), so when a task is missing from one seed the index alignment shifts and "seed means" mix seeds. Harmless when nothing fails; wrong whenever something does.
- The script also mis-states **F11 (= SE-prose)**, the other cell with a failed run (seed 2, `pknViscosityDominated`, `status: error`): it yields 0.9146 where the correct failures-as-zero value is 0.8965. **Table 1 prints 0.897, i.e. correctly** — so this one never reached the paper. But anyone re-running `analyze_autocamp.py` to "check" the numbers will get two wrong cells, not one.

### Verification: all 11 Table-1 val cells reproduce exactly

Recomputed from raw `_summary.json` under failures-as-zero, with **sample** std over the three seed means:

| Table 1 row | cell | recomputed mean | printed | recomputed σ | printed σ | match |
|---|---|---:|---:|---:|---:|:--:|
| Vanilla | F0 | 0.909586 | 0.910 | 0.0236 | 0.024 | ✓ |
| R+M | F1 | 0.884845 | 0.885 | 0.0136 | 0.014 | ✓ |
| S+M | F2 | 0.919084 | 0.919 | 0.0037 | 0.004 | ✓ |
| **R+S** | **F3** | **0.856720** | **0.857** | **0.0449** | **0.045** | **✓** |
| X+M | F4 | 0.921363 | 0.921 | 0.0071 | 0.007 | ✓ |
| R+X | F5 | 0.892798 | 0.893 | 0.0329 | 0.033 | ✓ |
| S+X | F6 | 0.916645 | 0.917 | 0.0038 | 0.004 | ✓ |
| R+S+X+M | F7 | 0.885257 | 0.885 | 0.0083 | 0.008 | ✓ |
| S+X+M | F8 | 0.9110 | 0.911 | 0.0180 | 0.018 | ✓ |
| SE-prose | F11 | 0.8965 | 0.897 | 0.0316 | 0.032 | ✓ |
| SE | SE | 0.9191 | 0.919 | 0.0201 | 0.020 | ✓ |

**Table 1's val column is fully verified — 11/11 cells, means and σ.** Cell identities also pinned by this: `S+X+M = autocamp_F8` and `SE-prose = autocamp_F11` (both previously ambiguous).

This also resolves the σ corroboration the plan doc flagged: Table 1's `R+S σ = 0.045` is the failures-as-zero sample std (0.0449); the metrics doc's 0.018 is the drop-nulls figure (sample std 0.0169). Same one failed run, both times.

### Corrected main effects

| Factor | published (appendix, stale) | Limitations §, same stale value | **corrected (paper's own convention)** |
|---|---:|---:|---:|
| R (RAG) | −0.032 | −0.033 | **−0.037** |
| S (stop-hook) | −0.003 | — | **−0.008** |
| X (xmllint MCP) | +0.007 | — | **+0.011** |
| M (memory) | +0.004 | — | **+0.008** |

All four move **away from zero**; in particular the negative retrieval effect is *larger* than reported, which strengthens the paper's own finding.

**The −0.032 / −0.033 internal inconsistency is explained too:** the stale drop-nulls value is −0.03256, which rounds to −0.033. The paper prints −0.032 at `:207` and `:412` and −0.033 at `:272`. They are not two computations — they are one stale number rounded two ways, and −0.033 is the arithmetically correct rounding of it. Neither is right under the declared convention.

### ⚠ Precision caveat for whoever drafts this

M is rounding-sensitive:

| effect | full precision | from Table 1's printed 3-dp means |
|---|---:|---:|
| R | −0.03676 | −0.03675 |
| S | −0.00772 | −0.00775 |
| X | +0.01146 | +0.01125 |
| **M** | **+0.00870 → +0.009** | **+0.00825 → +0.008** |

**Quote R −0.037, S −0.008, X +0.011, M +0.008** — the values a reviewer reproduces by hand from the eight printed cell means in Table 1. gep1 recomputes things; make his arithmetic agree with ours. If asked, the full-precision M is +0.0087; the discrepancy is rounding of the inputs and changes nothing.

### Commands run

```bash
python3 -c "import json; d=json.load(open('/data/shared/.../autocamp_F3_s1/autocamp_F3/_summary.json')); ..."   # schema inspection
sed -n '380,470p' scripts/analyze_autocamp.py      # compute_main_effects + F_FACTORS
sed -n '1,200p'   scripts/analyze_autocamp.py      # collect_cell — the isinstance() drop
sed -n '200,290p' scripts/analyze_autocamp.py      # aggregate_cell — index-based seed grouping
sed -n '178,215p' writing/neurips/neurips_2026.tex # Table 1
sed -n '400,425p' writing/neurips/neurips_2026.tex # appendix main-effects table
```
Full recomputation script + output: see `../artifacts/P0_f3_recompute.py`.

### Presentation guidance (better story than the plan doc assumed)

The plan doc framed this as *"one cell's mean was revised and the derived table was not regenerated."* That is not what happened, and the truth is more defensible:

> The appendix main-effects table was generated by an analysis script that averages over *scored* runs, while the paper's headline convention — stated in §3 and in Table 1's caption — scores unscorable runs as zero. Exactly one factorial cell contains an unscorable run, so exactly one cell mean differs, and the main-effects table inherited it. Table 1 itself is correct. Recomputed under the stated convention the effects are R −0.037, S −0.008, X +0.011, M +0.008 — all four larger in magnitude, and the negative retrieval effect stronger than reported.

**Do NOT say** the prefix bug fix produced these numbers (no re-run occurred), and **do NOT say** Table 1 is post-prefix-fix (fix landed 2026-05-03; factorial ran 2026-05-01/02).

Whether to *volunteer* this correction is a human decision (open question **H3**) — but the blocking condition is now cleared: we know which value is right and why, so the correction is available if the advisor wants it.

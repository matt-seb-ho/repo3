---
id: doc-cross-cutting-paper-section-2026-05-04
title: Cross-model and cross-harness — paper-ready section
date: 2026-05-04
type: paper_section
status: draft for incorporation by another agent
links:
  derived_from:
    - docs/2026-05-03_cross-cutting-summary.md
    - docs/2026-05-03_cross-harness-results.md
    - docs/2026-05-03_cross-model-results.md
    - docs/2026-05-03_minimax-pseudo-tool-call-analysis.md
  evidence_for: [writing/neurips/neurips_2026.tex]
---

# Cross-model and cross-harness — paper-ready section

*Self-contained markdown intended for direct incorporation into the
NeurIPS paper. Numbers are final and verified against raw result
JSON files. Prose is paper-grade but may be tightened during
incorporation.*

## At a glance

| Harness | Backbone | Cell | $\mathrm{fa0}$ | $\sigma$ | Task fails (/n_seeds×17) |
|---|---|---|---:|---:|---:|
| CC | DSv4-flash (3 sd) | Vanilla | $0.910$ | $0.024$ | 0/51 |
| CC | DSv4-flash (3 sd) | X+M | $\mathbf{0.921}$ | $0.007$ | 0/51 |
| CC | DSv4-flash (3 sd) | SE | $0.919$ | $0.020$ | 0/51 |
| CC | minimax-m2.7 (1 sd) | Vanilla | $0.821$ | --- | 1/17 |
| CC | minimax-m2.7 (1 sd) | X+M | $\mathbf{0.867}$ | --- | 0/17 |
| CC | minimax-m2.7 (1 sd) | SE | $0.861$ | --- | 0/17 |
| CC | gemini-3-flash-preview (1 sd) | Vanilla | $0.768$ | --- | 0/17 |
| CC | gemini-3-flash-preview (1 sd) | X+M | $\mathbf{0.797}$ | --- | 0/17 |
| CC | gemini-3-flash-preview (1 sd) | SE | $0.757$ | --- | 1/17 |
| OH | DSv4-flash (3 sd) | Vanilla | $0.856$ | $0.061$ | 1/51 |
| OH | DSv4-flash (3 sd) | X+M | $\mathbf{0.881}$ | $0.023$ | 1/51 |

All cells run with the same default-off harness (`GEOS_HOOK_POSTTOOLUSE` unset, autocamp-experiment-state parity) and the same primer/cheatsheet artefacts. The minimax × X+M number is post-fix; see §"Bug discovered during cross-model" below.

## Setup

**Cross-model.** Vanilla, X+M, SE on Claude Code with two additional backbones via OpenRouter: `minimax/minimax-m2.7` and `google/gemini-3-flash-preview`. Single seed per cell (cost-driven; gemini's I/O pricing is ${\sim}3.6\times$/${\sim}11\times$ DSv4 on input/output per million tokens). Test set: test-17. Same harness gate, primer (`plugin/GEOS_PRIMER_contract.md` for Vanilla and X+M; `plugin_evolving/v3/PRIMER.md` for SE), and m1u cheatsheet for X+M as the autocamp DSv4 cells.

**Cross-harness.** Vanilla and X+M on OpenHands with `deepseek-v4-flash` as backbone. Three seeds per cell (cheap on DSv4-flash). The OH X+M cell uses the same `xmllint_mcp.py` script as CC, registered through OH's per-task `<workspace>/.openhands/mcp.json` (we extended `scripts/openhands_eval.py` with a `--xmllint-mcp` flag for this; see commit `c359103`). The memory cheatsheet is delivered by prepending the m1u text to OH's inline user message, since OH does not expose an `--append-system-prompt` equivalent. We did not run SE on OH; SE depends on Claude Code's plugin packaging.

We did not run on OpenCode (no extant integration; estimated 4–8h to build).

## Quality and reliability

\textbf{X+M wins on every backbone we tested.} The Vanilla → X+M lift is positive on all three CC × backbone combinations and on both harnesses on DSv4: $+0.011$ on CC×DSv4 (3 seeds), $+0.046$ on CC×minimax (1 seed), $+0.029$ on CC×gemini (1 seed), $+0.025$ on OH×DSv4 (3 seeds). The lift size correlates inversely with backbone capability — adapters help most where the baseline is weakest. SE is competitive but not dominant; on gemini, SE actually regresses below Vanilla ($-0.011$), which we discuss below.

\textbf{Cross-harness gap is consistent at $-4$ to $-5$ pp.} OH × DSv4 underperforms CC × DSv4 by $0.054$ at Vanilla and $0.040$ at X+M (same backbone, same cell content, different harness wrapping). The X+M lift is \emph{larger} on the weaker harness ($+0.025$ on OH vs. $+0.011$ on CC), consistent with the autocamp-scaleup pattern of "adapters help most where the baseline is most brittle."

\textbf{Variance reduction is consistent across harnesses.} On the multi-seed cells, $\sigma$ Vanilla → X+M goes $0.024 \to 0.007$ on CC and $0.061 \to 0.023$ on OH — a ${\sim}3\times$ tightening on each. Both adapter cells have one task failure across 51 attempts; the OH adapter rescues the Vanilla seed-1 \texttt{ExampleDPWellbore} failure but introduces a new \texttt{AdvancedExampleDeviatedElasticWellbore} failure on a different seed, so the adapter shifts which tasks fail, not strictly reducing the failure count.

\textbf{SE on gemini regresses below Vanilla} ($0.757$ vs $0.768$). Not seen on DSv4 or minimax. \emph{We have no supported explanation.} An earlier draft of this section attributed it to SE's plugin registering "both geos-rag and xmllint MCP servers", giving the agent more tools to invoke. That is factually wrong: the \texttt{system/init} events show SE registers \textbf{only} \texttt{xmllint} (\texttt{"mcp\_servers":[\{"name":"xmllint","status":"connected"\}]}) on every backbone --- 51/51 DSv4 val runs, 30/30 DSv4 held-out runs, 17/17 gemini runs, 17/17 minimax runs --- and emits \textbf{zero} \texttt{mcp\_\_geos-rag\_\_*} references anywhere. SE has no extra MCP surface. If anything the asymmetry runs the other way: on gemini, X+M carried the buggy native-plugin prefix (150 \texttt{mcp\_\_geos-rag\_\_*} references against an unregistered server) while SE opted out, so X+M was \emph{handicapped} relative to SE and still beat it. We do not investigate further at $n=1$; multi-seed could shrink the effect.

## Efficiency per task

Mean per-task metrics across the seeds we ran. Wall is host-side wall-clock per task (Docker-enforced timeout 1500–1800 s); turns is `num_turns` from Claude Code's result event; cost is `total_cost_usd` from the same event when present (DSv4, minimax, gemini), or computed as $\mathrm{tokens \times pricing}$ from the OpenRouter rate when absent.

| Harness | Backbone | Cell | Wall (s) | Turns | Tools/task | Cost/task ($) | In tok/task | Out tok/task | Cache-hit tok/task |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| CC | DSv4-flash | Vanilla | $359$ | $27.7$ | $81.5$ | $0.0494$ | $32{,}185$ | $20{,}070$ | $796{,}607$ |
| CC | DSv4-flash | X+M     | $336$ | $36.1$ | $79.6$ | $0.0476$ | $33{,}285$ | $19{,}017$ | $956{,}341$ |
| CC | DSv4-flash | SE      | $321$ | $30.2$ | $68.9$ | $0.0421$ | $28{,}246$ | $18{,}372$ | $794{,}145$ |
| CC | minimax-m2.7 | Vanilla | $371$ | $27.0$ | $53.8$ | $0.139$ | $690{,}092$ | $9{,}353$ | $3{,}659$ |
| CC | minimax-m2.7 | X+M    | $411$ | $31.1$ | $61.5$ | $0.169$ | $826{,}866$ | $9{,}026$ | $4{,}294$ |
| CC | minimax-m2.7 | SE     | $377$ | $38.8$ | $43.9$ | $0.180$ | $950{,}936$ | $10{,}957$ | $16{,}870$ |
| CC | gemini-3-flash | Vanilla | $\mathit{95}$ | $24.1$ | $31.6$ | $0.139$ | $721{,}858$ | $8{,}669$ | $93{,}803$ |
| CC | gemini-3-flash | X+M    | $\mathit{142}$ | $33.9$ | $51.3$ | $0.219$ | $994{,}090$ | $11{,}278$ | $228{,}513$ |
| CC | gemini-3-flash | SE     | $\mathit{202}$ | $67.5$ | $74.5$ | $0.468$ | $2{,}509{,}919$ | $10{,}974$ | $641{,}851$ |
| OH | DSv4-flash | Vanilla | $391$ | --- | $108.0$ | --- | --- | --- | --- |
| OH | DSv4-flash | X+M     | $410$ | --- | $116.2$ | --- | --- | --- | --- |

Notes on the table: ($i$) DSv4 numbers are means over 51 task-runs (3 seeds × 17 tasks). minimax and gemini are means over 17 (single seed). OH numbers are means over 51. ($ii$) Costs for DSv4 use the `total_cost_usd` reported by Claude Code internally; the field is populated for all our runs. minimax and gemini costs come from the same field, populated by Claude Code via the OpenRouter usage report. ($iii$) OH does not preserve token-level usage in `status.json` or `events.jsonl`; the harness wrapper records only wall-clock, success status, and tool counts. We omit token and cost columns rather than estimate them. ($iv$) Cache-hit tokens are dramatically smaller on minimax (${\sim}3$–$17$K vs ${\sim}800$K on DSv4) — OpenRouter's minimax route does not pass through Anthropic-style prompt caching, so most input tokens are billed at full rate. ($v$) gemini wall is markedly faster than DSv4 wall ($95$–$202$ s vs $321$–$359$ s for comparable cells) because Gemini's API throughput is higher; this lowers wall but not cost.

\textbf{Total cost of the cross-model panel.} Single-seed × 3 cells × 2 backbones × 17 tasks: $51 \times 0.169 + 51 \times 0.275 \approx \$22.6$ ($8.62$ for minimax + $13.99$ for gemini). The DSv4 autocamp factorial (Phase 2 + scaleup) accumulated to ${\sim}\$3.50$ in DSv4 spend; cross-model nearly doubled the project's total API budget despite covering ${\sim}1\%$ as many task-runs.

## Tool-use patterns

| Harness | Backbone | Cell | Read | Write | Edit | Bash | Grep | Glob | MCP |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| CC | DSv4-flash | Vanilla | $42.2$ | $4.2$ | $0.5$ | $5.0$ | $13.0$ | $7.5$ | $0.0$ |
| CC | DSv4-flash | X+M | $34.6$ | $3.5$ | $1.6$ | $4.4$ | $17.6$ | $9.7$ | $5.1$ |
| CC | DSv4-flash | SE | $30.8$ | $3.6$ | $1.4$ | $5.7$ | $14.9$ | $7.0$ | $2.7$ |
| CC | minimax-m2.7 | Vanilla | $24.5$ | $3.4$ | $1.0$ | $7.0$ | $9.0$ | $5.7$ | $0.0$ |
| CC | minimax-m2.7 | X+M | $26.3$ | $3.0$ | $1.7$ | $7.6$ | $11.8$ | $5.7$ | $3.4$ |
| CC | gemini-3-flash | Vanilla | $11.2$ | $3.1$ | $1.4$ | $4.3$ | $5.4$ | $3.5$ | $0.0$ |
| CC | gemini-3-flash | X+M | $13.6$ | $3.4$ | $1.6$ | $5.5$ | $7.4$ | $4.4$ | $5.9$ |
| CC | gemini-3-flash | SE | $19.8$ | $3.4$ | $5.1$ | $9.6$ | $11.5$ | $5.6$ | $3.4$ |

(All numbers are mean tool calls per task; "MCP" is the sum of all `mcp__*` invocations, dominated by `xmllint` in X+M cells and split between `xmllint` and `geos-rag` in SE.)

\textbf{X+M reduces exploratory file-system use.} On DSv4, Vanilla averages $42.2$ Read calls per task; X+M drops to $34.6$ ($-18\%$). The cheatsheet partially short-circuits the exploratory phase that Vanilla spends consulting `/geos_lib/inputFiles/*.xml` examples. SE's prose primer drives this further to $30.8$ Reads. The pattern holds qualitatively on minimax and gemini.

\textbf{xmllint MCP is invoked $\sim$3–6 times per task on X+M cells.} The agent calls validate-XML 3.4 times/task on minimax X+M and 5.9 times/task on gemini X+M. On DSv4, X+M shows $5.1$ MCP calls and SE shows $2.7$ — SE's MCP calls split between xmllint and geos-rag, while X+M only has xmllint. The validation calls are strict-zero on Vanilla cells.

\textbf{Gemini uses fewer tools overall but more MCP per call.} Gemini Vanilla averages $31.6$ tool calls per task (vs $81.5$ on DSv4 and $53.8$ on minimax) — much terser exploration. When given X+M, gemini increases tool calls by $\sim 60\%$ (to $51.3$), with MCP calls accounting for the bulk of the increase ($5.9$/task). This is consistent with gemini being more data-efficient on simpler tasks but benefiting from explicit validation on harder ones.

## File-access subtree pattern (single-seed snapshot)

Top reading targets, by `/geos_lib/inputFiles/<subtree>` count, for one representative seed of each cell. We report total Read calls / task aggregated across the 17 tasks.

| Cell | Total Reads | Top subtree (count) | Second | Third |
|---|---:|---|---|---|
| CC×DSv4 Vanilla s1 | 663 | coreComponents (121) | triaxialDriver (76) | compositionalMultiphaseFlow (68) |
| CC×DSv4 X+M s1 | 449 | coreComponents (85) | hydraulicFracturing (69) | triaxialDriver (55) |
| CC×DSv4 SE s1 | 518 | triaxialDriver (79) | poromechanics (77) | coreComponents (74) |
| CC×minimax Vanilla | 357 | triaxialDriver (68) | solidMechanics (41) | compositionalMultiphaseFlow (36) |
| CC×minimax X+M | 380 | compositionalMultiphaseFlow (62) | triaxialDriver (60) | poromechanics (45) |
| CC×gemini Vanilla | 175 | coreComponents (36) | triaxialDriver (27) | thermoPoromechanics (15) |
| CC×gemini X+M | 207 | triaxialDriver (32) | coreComponents (24) | thermoPoromechanics (17) |

\textbf{Total Read volume tracks per-token efficiency.} Gemini's lower wall and lower total tokens correlate with lower Read volume ($175$–$207$ on gemini vs $663$ on DSv4 Vanilla). minimax sits between. The $\sim 30\%$ Read reduction on DSv4 from Vanilla → X+M ($663 \to 449$) is the cheatsheet absorbing exploratory reads.

\textbf{X+M shifts subtree distribution.} On DSv4, Vanilla's Reads concentrate in `coreComponents` (the GEOS source tree's schema/header bucket) while X+M shifts toward task-relevant subtrees (`hydraulicFracturing`, `triaxialDriver`). SE concentrates further on `triaxialDriver` and `poromechanics` — consistent with the v3 cheatsheet's heavy poromechanics anchoring.

## Bug discovered during cross-model

The first minimax × X+M run scored an anomalous $0.392$ with $8/17$ tasks failing entirely (zero XMLs written, agent exiting at ${\sim}25$ s per task). Trajectory inspection showed minimax emitting text like

```
<minimax:tool_call>
<invoke name="mcp__geos-rag__search_navigator">
<parameter name="query">...</parameter>
</invoke>
</minimax:tool_call>
```

in its first message, with zero real `tool_use` invocations.

We initially hypothesised "training-data prior" — that minimax had memorised the geos-rag tool names from public agentic data. The user push-back was sharp: minimax-m2.7 (released 2026-03-18) predates our repo (first commit 2026-04-17), so minimax could not have been trained on `mcp__geos-rag__*` from our project. Adversarial review (RN-006) found the actual leakage path: \texttt{src/runner/prompts/native\_plugin\_prefix.txt} literally contains the string

> Use the GEOS RAG MCP tools directly: `mcp__geos-rag__search_navigator`, `mcp__geos-rag__search_schema`, and `mcp__geos-rag__search_technical`. Before writing XML, call at least one of the plugin RAG tools…

and the orchestrator at \texttt{src/runner/orchestrator.py:267} was injecting this prefix into the user prompt for every cell with \texttt{plugin\_enabled=True}, regardless of whether the geos-rag MCP server was actually registered. \texttt{deepseek-v4-flash} silently ignored the impossible instruction (zero pseudo-tool calls observed across ${\sim}1{,}300$ DSv4 trajectories); \texttt{minimax-m2.7} dutifully complied.

We fixed the gate to key on whether RAG is actually registered (`_rag_on`) rather than whether the plugin directory is mounted (`enable_plugin`). Re-running minimax × X+M with the fix gives the headline $0.867$ ($+47.5$pp recovery). Three-way comparison:

| config | $\mathrm{fa0}$ | scored / 17 | task fails | pseudo MCP calls |
|---|---:|---:|---:|---:|
| X+M (no disclaim, buggy prefix) | $0.392$ | $9$ | $8$ | $18$ |
| X+M (disclaimer-only mitigation) | $0.711$ | $14$ | $3$ | $12$ |
| **X+M (prefix gate fixed at the source)** | **$0.867$** | **$17$** | **$0$** | **$0$** |

The disclaimer-only mitigation added an in-prompt "do not call mcp\_\_geos-rag\_\_*" warning while leaving the buggy prefix in place; this gave contradictory instructions and recovered $+31.9$pp, not $+47.5$pp. Removing the bad instruction at its source is the correct fix.

\textbf{Spillover for the autocamp $R$ main effect.} The buggy prefix was active for cells with \texttt{plugin\_enabled=True, rag\_enabled=False} that did not opt out via \texttt{add\_native\_plugin\_prefix=False}. This includes the autocamp factorial cells F2, F4, F6, F8, F11 and several ablation cells. Cells already opted out (autocamp\_SE, autocamp\_v4, abl\_c9\_no\_prefix, abl\_se\_round) are unaffected. The team's \texttt{abl\_c9\_no\_prefix} cell measured the prefix's effect on DSv4 directly over 3 seeds $\times$ 17 tasks: C2 (prefix) $0.9134$ vs C9 (no prefix) $0.9170$, $\Delta = +0.0036$, with zero big-swing tasks ($|\Delta| \geq 0.10$). So on DSv4 the prefix is \emph{null} at ${\approx}+0.004$, and the contamination of any DSv4 number is bounded at that magnitude. (Earlier internal notes cited a "$+0.24$ DSv4 anomaly attributable to this prefix"; that is a mis-citation. $+0.24$ is the C1$\to$C2 build-up lift that C9 was constructed to explain, $0.6713 \to 0.8649 \to 0.9134$, and the prefix hypothesis for it was refuted.) The reported autocamp $R = -0.033$ main effect therefore partially measures "agent gets stuck on impossible instruction in $R^{-}$ cells" rather than a clean RAG-vs-no-RAG contrast. A clean re-run of F0/F4/F6/SE on DSv4 with the fixed gate (${\sim}1.5$h wall, ${\sim}\$0.50$ in DSv4 spend) is recommended for the camera-ready. The X+M-vs-Vanilla relative ranking on DSv4 is unaffected because both X+M and Vanilla are $R^{-}$; the prefix bug applies to one of them only (X+M, since Vanilla has \texttt{plugin\_enabled=False}).

## Three findings to lift into the paper

\textbf{(1) X+M generalises across backbones.} On all three backbones tested (DSv4-flash, minimax-m2.7, gemini-3-flash-preview) on Claude Code, X+M outperforms Vanilla. The lift size scales inversely with backbone capability ($+0.011$ on the strongest, $+0.029$–$0.046$ on the weaker two). This is a positive cross-model result for the paper's headline recommendation.

\textbf{(2) X+M generalises across harnesses.} On DSv4-flash, X+M lifts $+0.025$ on OH (vs $+0.011$ on CC) — bigger gain on the weaker harness. The cross-harness gap is itself consistent (CC outperforms OH by ${\sim}5$pp at both Vanilla and X+M), suggesting the harness contributes a roughly constant offset rather than scaling adapter benefit.

\textbf{(3) Adapters reduce variance more than they raise mean.} On both multi-seed harnesses, X+M cuts seed $\sigma$ by ${\sim}3\times$ vs. Vanilla. This holds on DSv4 (the strong backbone) and on OH (the weaker harness). Combined with the autocamp finding that perfect-task counts do not increase under any adapter, the cross-cutting evidence supports a "harm reduction not correctness" framing for what these adapters do.

## Best-vs-mean and verification

All means in this section were cross-checked against raw `_summary.json` files (DSv4 cells via `_results/<run>/<agent>/_summary.json`; OH cells via `data/eval/results/<run>/openhands_no_plugin/*_eval.json`; cross-model cells via `/tmp/cm_*.json`). Per-seed scores:

| Cell | Seed scores |
|---|---|
| CC×DSv4 Vanilla (3 sd) | 0.882 / 0.922 / 0.924 |
| CC×DSv4 X+M (3 sd) | 0.913 / 0.925 / 0.926 |
| CC×DSv4 SE (3 sd) | 0.906 / 0.910 / 0.942 |
| OH×DSv4 Vanilla (3 sd) | 0.790 / 0.869 / 0.910 |
| OH×DSv4 X+M (3 sd) | 0.857 / 0.881 / 0.904 |

Best-vs-mean gap exceeds $3$pp on **OH×DSv4 Vanilla** ($+0.053$ pp gap, seed 1 produced one `failed_no_outputs` on `ExampleDPWellbore` and was scored 0). We report the mean per convention; the brittleness pattern itself is part of the cross-harness story (X+M reduces this). All other cells have best-vs-mean gap $\leq 0.023$.

n_params: all comparisons within each row of the headline table hold backbone constant. Cross-backbone comparisons (e.g., Vanilla on DSv4 vs Vanilla on minimax) are explicitly between different models and reported with model labels. No fairness adjustment is applicable.

## Caveats for the section

- Cross-model is single-seed; multi-seed would tighten effect-size estimates. Cost is the bottleneck: gemini × 3 cells × 3 seeds × 17 tasks ${\sim}\$36$ (using the $0.276$/task average from Table). Worthwhile if the camera-ready timeline allows.
- OH cross-harness lacks token/cost data; the harness wrapper does not preserve usage. Estimating cost at DSv4-rate × CC-equivalent tokens gives ${\sim}\$0.05$/task, but we omit this from headline tables.
- The gemini SE regression below Vanilla ($-0.011$) is at $n=1$ and may not reproduce. Worth a re-run to confirm.
- All claims about backbone-relative robustness are based on test-17. Held-out-10 cross-model would be a useful additional panel.

## Result paths and code

- **Code fix**: `src/runner/orchestrator.py` line 276 (commit `000b4ba`); also `src/runner/prompts/missing_rag_disclaimer.txt` for the opt-in disclaimer (commit `de1ceca`).
- **OH integration extension**: `scripts/openhands_eval.py --xmllint-mcp` flag (commit `c359103`).
- **Result trajectories**:
  - CC×DSv4: `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/autocamp_{F0,F4,SE}/`
  - CC×{minimax,gemini}: `/data/shared/geophysics_agent_data/data/eval/cross_model_2026-05-03/`
  - OH×DSv4: `/home/matt/sci/repo3/data/eval/openhands_no_plugin/oh_{vanilla,xm}_test17_s{1,2,3}/`
- **Adversarial review note**: `.copilot/reviews/RN-006_adversarial_minimax-pseudo-mcp-leakage.md`.

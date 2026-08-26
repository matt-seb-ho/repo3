# SIGA — 15-minute Talk Deck Spec

> Source paper: `writing/arxiv/neurips_2026.tex` —
> "Adapting Off-the-Shelf Coding Agents for Scientific Simulator Setup: A GEOS Case Study."
> SIGA = **Simulator-Interface Grounding Adapter.**

## Instructions for the designer

This document specifies **content and sequence**, not per-slide layout. Treat each numbered **section** below as a unit of narrative the talk must deliver in the given order. Within a section, decide slide count, split points, and what text vs. visual carries the message. Section length annotations (e.g. *~75s*) are speaking-time targets, not slide counts.

- Total target: **15 minutes**, ~12.5–13.5 min of content + buffer.
- Audience assumption: mixed ML + computational-science researchers. Don't assume GEOS familiarity; don't over-explain coding agents.
- Style: **assertion-evidence.** Each slide's title should be a claim, not a topic. The claim lives at the top; the visual/data supports it.
- When this doc says "**`[FIGURE: ...]`**" the designer should pull the named figure from the paper PDF (`writing/arxiv/neurips_2026.pdf`) or recreate it. When it says "**`[TABLE: ...]`**" the data exists in the paper but should likely be re-presented as a chart, not a full table.
- Where exact numbers appear, **use them verbatim** — they were cross-checked against the paper.

---

## 1. Title (~30s)

**Message:** Identify the paper and frame "what kind of paper this is" in one phrase.

**Content to convey:**
- Title: *Adapting Off-the-Shelf Coding Agents for Scientific Simulator Setup: A GEOS Case Study*
- Speaker, advisor, affiliation, date
- One-line subhead that signals the genre: *an empirical study of harness-level domain specialization*

---

## 2. The hook: general coding agents are not enough for scientific simulator setup (~75s)

**Message:** Set up the problem with a concrete pain point before defining anything.

**Content to convey:**
- A working scientist's natural-language intent and a runnable simulation are separated by an "expert bottleneck": **operating any advanced scientific software amounts to learning its domain-specific language (DSL).**
- Configuring this software routinely costs trained domain scientists **hours to days per study**, and is the part of the workflow that benefits *least* from general LLM reasoning ability.
- One concrete failure mode (pick one to dramatize): unknown-vocabulary substitution, silent termination on an empty/unparseable deck, or in-loop schema-violation drift.

**Visual:** `[FIGURE: Figure 1 — manual vs. SIGA workflow comparison]` is ideal here; it's the paper's own "this is the problem, this is what we do" diagram. If using all of Figure 1 is too dense, use only panel (a) here and reserve panel (b) for §6.

---

## 3. Our angle: specialize at the *harness* level, not the model (~75s)

**Message:** Announce the paper's research-level thesis before showing any system details. This is the slide your advisor will most want top-down. Bookended with §13.

**Content to convey:**
- Two layers in an agent stack: **model** (weights, training) vs. **harness** (prompts, tools, skills, memory, control flow).
- Frontier coding agents (Claude Code, OpenCode, OpenHands) are now competent at general code-editing on their own. Each prior scientific-agent system reimplemented the orchestration layer from scratch — we don't.
- **Our move:** take a fixed SOTA harness (Claude Code) and invest engineering effort *only* in the simulator-specific grounding layer above it.
- Broader research framing (this is the line to deliver out loud): *domain specialization for AI agents may live at the harness level, not the model level.* The GEOS work is the case study; the question is general.

---

## 4. Domain anchor: GEOS and why deck-authoring is the bottleneck (~60s)

**Message:** Make GEOS concrete enough that the audience trusts the task is real, without going into physics.

**Content to convey:**
- GEOS is an open-source multiphysics simulator used in subsurface science: **CO₂-storage fault-slip risk, history-matching surrogates, microseismic-cloud mapping, geothermal, induced seismicity.**
- Configuration is an XML "deck" spanning **ten canonical sections** (mesh, geometry, execution schedule, physics modules, material models, regions, numerical methods, field specs, functions, outputs). Tag names refer to specific simulator classes; attribute values must satisfy schema *and* physical constraints; cross-references must stay mutually consistent.
- This is the DSL the scientist pays the hours-to-days tax on.

**Visual:** an annotated snippet of a real GEOS XML deck (small, illustrative) or an icon-level diagram of the ten sections. **Do not** put a full deck on screen.

---

## 5. SIGA in one slide: what we built, what we found *(punchline anchor, ~60s)*

**Message:** Give the audience the whole story arc before the methods details. If anyone tunes out after this, they should still know the system and the headline result.

**Content to convey:**
- **System:** Claude Code wrapped by four grounding components, each targeting a known agent failure mode: **R** (Retrieval over simulator artifacts), **S** (Stop-hook schema verification), **X** (agent-callable XML validator), **M** (procedural-memory cheatsheet).
- **Headline (deliver as the lead claim):** *SIGA makes the off-the-shelf coding agent dramatically more reliable on real GEOS deck-authoring tasks — across-seed variance drops by roughly an order of magnitude — without sacrificing score or efficiency.*
- **Concrete numbers to anchor the claim** (held-out-eval, TreeSim, n=3 seeds):
  - **Reliability** *(the big number)*: across-seed σ **0.081 → 0.005–0.012**
  - Score: Vanilla 0.720 → best SIGA cell 0.789 (+0.069)
  - Efficiency: wall-clock 359s → 321s; tool calls 81.5 → 68.9
- The supporting framing: all three axes move the right direction; reliability is where the effect is dramatic.

**Visual:** `[FIGURE: Figure 1 panel (b) or (c)]` — SIGA workflow / valid-XML output. Pair with one **dominant large-number callout for the σ reduction**, and smaller supporting callouts for score and time.

---

## 6. Method: four grounding components, each targeting a named failure mode (~90s)

**Message:** Introduce the four components as a *design space*, not a stack. Be explicit that each piece is known prior art; the contribution is the empirical study of the combination on a real scientific workflow.

**Content to convey** (use the paper's exact names):

| Component | What it is | Failure mode it targets |
|---|---|---|
| **R** Retrieval | MCP server with `search_navigator` (Sphinx docs), `search_schema` (XSD entries), `search_technical` (example XMLs); ChromaDB + `text-embedding-3-small` | Unknown-vocabulary substitution |
| **S** Stop-hook | Termination hook: runs `xmllint --schema` against every attempted termination; returns structured repair feedback; ≤2 re-prompts | Silent-incompleteness |
| **X** Validator tool | Agent-callable `mcp__xmllint__validate_geos_xml`; same schema check, but optional; agents use it ~3×/task when enabled | In-loop schema-violation drift |
| **M** Memory cheatsheet | 775-token always-on reference appended via `--append-system-prompt`; distilled offline from 18 training trajectories | Recurring-vocabulary lookup |

**Honesty line to deliver out loud:** "Each component is known prior art individually. The contribution is the systematic empirical study of the combination on a real scientific workflow."

**Visual:** `[FIGURE: Figure 2 — SIGA agent loop execution trace]` is the right visual for showing how these components plug into the harness.

---

## 7. Initial exploration: letting the agent rewrite its own adapter (~45s)

**Message:** Flag a research direction we've started exploring. The point is *that we tried it*, not what it scored.

**Content to convey:**
- The hand-designed adapters in §6 are static. A natural next step: **let the agent propose changes to its own adapter** by reflecting on its trajectories.
- What we did: an offline reflection step that proposes modifications to the plugin (prompts, tools, skills) based on training-set trajectories. Two variants tried (**SE-prose** = prose-only changes; **SE** = full adapter modifications).
- Framing to deliver out loud: *initial exploration of a meta-harness direction.* Bounded scope, training-set trajectories only, offline. Not a self-improving system; a feasibility probe.
- We won't dwell on numbers — SE is in the ballpark of the best hand-designed cell. The contribution at this stage is having a working pipeline, not the score it produces.

---

## 8. Why we use a Resolution-IV factorial — and what it catches that one-at-a-time ablations miss (~90s)

**Message:** Justify the experimental design choice before showing any results. The concrete example is the audience-grabbing part — deliver it first, then the methodology.

**Concrete confound example to open with** (deliver verbally and visually):

> Imagine your account is protected by both a **password** and a **2FA token**. You want to know which one keeps it safe, so you do a one-at-a-time ablation.
> - Turn off the password — account is still safe (2FA caught it).
> - Turn off 2FA — account is still safe (password caught it).
>
> Strip-down ablation concludes: **neither matters.** Turn off both, of course, and the account is wide open.
>
> The components have a joint contribution that no single ablation surfaces. **One-at-a-time ablations measure marginal effects under an independence assumption — and that assumption is exactly what's wrong when your components interact.**

**Then the methodology:**
- The same structure shows up in SIGA: e.g. S (stop-hook) and X (callable validator) both invoke `xmllint`. Strip-down of either one alone could hide their joint effect; build-up from empty could rank each as low-value depending on order.
- **Resolution-IV $2^{4-1}$ fractional factorial (generator D = ABC):** 8 cells; main effects estimable clean of 2-way interaction confounding; half the runs of a full $2^4$.
- **Honest caveat to state:** because S and X both use `xmllint`, the X main effect partly conflates agent-callable validation with hook-time schema validation when S is also enabled — the paper flags this and so should the slide.
- **Three measurement axes throughout:** **score** (TreeSim, failures-as-zero), **reliability** (across-seed σ), **efficiency** (tool calls/task, wall-clock seconds/task).

**Visual:** a small 2×2 truth-table diagram of the password / 2FA example (rows = password on/off, cols = 2FA on/off, cells = ✅/❌) makes the confound legible in two seconds. Then alongside it, the 8-cell Resolution-IV design as a parallel structure.

---

## 9. Main results: the dominant gain is reliability (~90s)

**Message:** Lead with the variance collapse and the mechanism — that's where the story is. Score and efficiency are supporting evidence, not the headline.

**Content to convey:**
- **Reliability — the lead number:** across-seed σ on held-out-eval drops from Vanilla **0.081** to X+M **0.005** and S+X **0.002**. *Roughly an order of magnitude tighter across seeds.*
- **Mechanism, in one line** (quote-worthy): *"The stop-hook emerges as the dominant reliability mechanism."* The Vanilla σ=0.081 came almost entirely from one seed producing unparseable XML on `ExampleProppantTest` and scoring 0. The adapter's first-order job is to keep the harness from terminating with empty or unparseable decks.
- **Where the mean-score lift lives:** the aggregate +0.069 (Vanilla → SE on held-out-eval) is **concentrated in two catastrophic-failure rescues** — `AdvancedExampleThermoPoroElasticWellbore` (0.355 → 0.761) and `ExampleProppantTest` (0.541 → 0.825). On most tasks, every cell is in seed noise. This is consistent with reliability, not uniform quality, being the right way to describe the win.
- **Supporting numbers across the full Resolution-IV sweep:** mean TreeSim on held-out-eval — Vanilla 0.720, X+M 0.768, S+X+M 0.783, SE 0.789. Efficiency moves the same direction: wall-clock 359s → 321s; tool calls 81.5 → 68.9.

**Visual:** `[TABLE: Table 1 — main Resolution-IV results]` and `[TABLE: Table 6 — main effects]` are the source. The designer should render this as a single chart: **mean ± σ bars across cells, sorted, with the σ-collapse from Vanilla to S-enabled cells visually unmissable.** That visual *is* the slide's argument. A bar chart with error bars beats any version of the LaTeX tables.

---

## 10. Efficiency: more reliable AND faster, with no extra tool budget (~45s)

**Message:** Quick, high-impact slide — show the system isn't paying a hidden cost.

**Content to convey:**
- **Tool calls / task (val):** Vanilla 81.5 → X+M 79.6 → S+X+M 71.0 → SE **68.9**.
- **Wall-clock / task (val):** Vanilla 359s → X+M 337s → S+X+M 326s → SE **321s**.
- One useful internal finding: **cheatsheet (M) reduces Read calls by ~50%**; RAG cells make 12–13 retrieval calls/task but didn't score higher.

**Visual:** `[TABLE: Table 7 — efficiency]` → render as a small grouped bar chart (tool calls and wall-clock side by side).

---

## 11. Human baseline: SIGA matches extended-budget human quality in a fraction of the time (~75s)

**Message:** Anchor the system's absolute value, not just its lift over Vanilla.

**Content to convey** (Buckley-Leverett task, n=2 geoscience-domain volunteers new to GEOS):

| Condition | Deck-level TreeSim | Wall time |
|---|---|---|
| Human P1 (1h cap) | 0.540 | 48.2 min |
| Human P2 (1h cap) | 0.527 | 46.7 min |
| Human P1 (no cap) | **0.931** | ~180 min |
| Vanilla Claude Code | 0.751 ± 0.016 | ~7 min |
| SIGA (X+M) | **≥ 0.90** | ~5 min |

**Quote to deliver:** "*SIGA places the agent inside the time envelope of an experienced human author and at parity with extended-budget human deck quality on a representative task.*"

**Caveat to state out loud:** n=2, single task. Pilot evidence, not a population-level claim.

**Visual:** `[TABLE: Table 2 — human baseline]`, ideally rendered as a quality-vs-time scatter with the two human points (capped & uncapped) and the two agent points labeled.

---

## 12. Probing higher autonomy: less spec, more demanded of the agent (~60s)

**Message:** We *explored* the autonomy axis. The point is the exploration itself; the early observation is preliminary.

**Content to convey:**
- Setup: we stress-tested the agent by **reducing the guidance in the task specification** — Medium and Hard specification relaxation, where details the agent would normally be told are deliberately stripped. The agent has to either infer them or ask.
- To give the agent an out, we **exposed a human-consultation tool** it could invoke at any time.
- **Early observation:** across **64 interactive trials, the agent invoked the consultation tool exactly twice (3.1%)**. So far, this generation of agent tends not to ask for supervision — it presses on instead.
- Frame this as initial evidence, not a conclusion: *we don't yet know whether the agent should have asked more, or whether it found the answers elsewhere.* Either way, autonomy-under-reduced-spec is a meaningful axis to keep probing.

**Visual:** `[TABLE: Table 3 — autonomy / consultation rates]` or a simple call-out of the 3.1% number against the 64-trial denominator.

---

## 13. Domain generalization: the dominant mechanism transfers to OpenFOAM (~60s)

**Message:** Show that the *finding*, not just the system, generalizes — even from a small pilot.

**Content to convey:**
- Pilot cross-simulator transfer to **OpenFOAM**, 5 tasks from FoamGPT subset.
- Best OpenFOAM cell (**R+S**): **0.871** vs. Vanilla Claude Code **0.466** and Foam-Agent (lint-only mode) **0.569**.
- Key reproduction: **every S-enabled cell achieves full required-file coverage with no zero-score failures**; Vanilla covers 3/5, R+X covers 1/5.
- **The dominant mechanism — the stop-hook — carries again.** This is what we wanted to see.
- Caveat: 5 tasks, single seed for some cells; framed as pilot evidence.

**Visual:** `[TABLE: Table 9 — OpenFOAM transfer]` → bar chart of mean score by cell, with full-coverage annotation.

---

## 14. Back to the thesis: what this case study says about harness-level specialization (~60s)

**Message:** Close the bookend started in §3. Three sharp claims, each supported by something the audience just saw.

**Content to convey:**
- **Claim 1 — Harness-level adaptation is enough to move the needle.** A fixed SOTA coding agent, wrapped with four small adapters built from off-the-shelf parts, makes the agent dramatically more reliable on a real scientific workflow (with score and efficiency moving the right direction too) — without retraining anything.
- **Claim 2 — The bottleneck for scientific agents is at the interface, not the reasoning.** Each adapter targets an interface failure (vocabulary lookup, silent termination, schema drift). The lift comes from fixing the interface; the underlying model is unchanged.
- **Claim 3 — Measurement methodology matters as much as the system.** Resolution-IV instead of one-at-a-time ablation, multiple measurement axes instead of score-only, autonomy probes instead of fixed-spec evals — different methodological choices would have told different stories.

---

## 15. Limitations and future work (~60s)

**Message:** Be specific, not generic. Use the paper's actual future-work list — don't invent platitudes.

**Content to convey** (pick 3–4 to show; the rest are backup):
- **Multi-seed cross-model panel** (Vanilla / X+M / SE on minimax and gemini, n=3) to tighten effect-size estimates.
- **Larger OpenFOAM benchmark** (5 → 20+ tasks, multi-seed) to convert pilot transfer into a real generalization claim.
- **Execution-correctness ladder:** run agent-produced decks through actual GEOS execution to convert TreeSim into a runnability metric.
- **Cross-section consistency hook:** validate `<ElementRegion materialList>` against `<Constitutive>` block names — a natural next adapter cell.
- **Closer collaboration with domain scientists** for data collection; longer-horizon: **RL** on the harness; **expanded self-evolution** beyond offline trajectory reflection.

---

## 16. Closing slide (~15s)

**Message:** Land the talk.

**Content to convey:** one sentence that returns to the thesis from §3 + §14, e.g. *"Domain specialization for AI agents may live above the model, in the harness — and the case study suggests reliability, not raw capability, is what that layer most directly buys."*
Then: thank-you / acknowledgements / contact.

---

## Backup slides (only if asked)

Have ready, but don't put in the main flow:
- `[TABLE: Table 4 — bottleneck failure-category counts]` — for "what kinds of errors does each adapter actually fix?"
- `[TABLE: Table 5 — per-task held-out-eval]` — for "which tasks does the gain live in?"
- `[TABLE: Table 8 — cross-model and cross-harness panel]` — for "does this depend on the backbone model?"
- `[TABLE: Table 12 — human browser history]` — for "what were the humans actually doing for those 48 minutes?"
- `[TABLE: Table 14 — memory cheatsheet excerpt]` — for "what's actually in the cheatsheet?"
- Slide on the **zero-call retrievable-memory finding** (paper notes: an embedding-retrievable procedural-memory tool was invoked zero times by the agent; only always-on system-prompt memory produced lift). Strong backup for an interface-design-flavored question.

---

## Time budget summary

| Section | Target | Cumulative |
|---|---|---|
| 1 Title | 0:30 | 0:30 |
| 2 Hook | 1:15 | 1:45 |
| 3 Thesis | 1:15 | 3:00 |
| 4 GEOS | 1:00 | 4:00 |
| 5 Punchline | 1:00 | 5:00 |
| 6 Four components | 1:30 | 6:30 |
| 7 Self-evolved | 0:45 | 7:15 |
| 8 Why factorial | 1:30 | 8:45 |
| 9 Main results | 1:30 | 10:15 |
| 10 Efficiency | 0:45 | 11:00 |
| 11 Human baseline | 1:15 | 12:15 |
| 12 Autonomy | 1:00 | 13:15 |
| 13 OpenFOAM | 1:00 | 14:15 |
| 14 Thesis bookend | 1:00 | 15:15 |
| 15 Future work | 0:45 | 16:00 |
| 16 Close | 0:15 | 16:15 |

Budget is ~75 seconds over the 15-min cap as written — expect to lose that in delivery, but if it doesn't tighten naturally, the safest cuts (in order): fold §10 efficiency into §9 (–45s); shorten §13 OpenFOAM to one slide referenced from §14 (–30s); drop §7 self-evolved entirely (–45s, but losing a future-work thread).

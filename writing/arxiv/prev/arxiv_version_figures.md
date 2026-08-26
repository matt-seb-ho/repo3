# arXiv-version figure plan: Figure 1 & Figure 2

Planning notes for the figure revision. Grounded in the current paper
(`neurips_2026.tex`) so that each figure + caption can stand alone, per the
"lazy reader reads only figures/tables/captions" principle.

---

## 0. Framing notes & strategic decisions

### The two governing constraints (from the advisor + figure dogma)

1. **Standalone rule.** Every figure + caption must let a reader who skips the
   body get the impression we want. So numbers, the cost claim, and the
   component definitions all need to live *on the figure or in its caption*,
   not only in the prose.
2. **Figure-1 dogma.** Fig 1 must either (a) introduce the problem, or (b) tell
   the whole story in brief.
3. **Method-figure dogma.** There must be a figure that shows what our
   contribution is / how it works.

### The split I recommend

| Figure | Role | Dogma satisfied |
|--------|------|-----------------|
| **Fig 1** | Introduce the *problem*: intent → DSL config is the expensive bottleneck | 2(a) |
| **Fig 2** | Show the *method*: base harness + 4 grounding adapters (R/S/X/M) | 3 |

This is the split you already have in mind, and it's the right one. Fig 1 as
pure problem-intro is cleaner than trying to cram the whole story into it,
*provided* Fig 2 genuinely carries the method. Which brings me to the one
substantive content concern:

### The key content gap I want to flag (affects Fig 2)

The actual contribution of this paper is **the four grounding adapters
(R, S, X, M) and the finding that S carries the empirical weight.** The entire
results section — Table 1, the bottleneck analysis, the OpenFOAM transfer — is
organized around the R/S/X/M letters.

But the current Fig 2 is an *execution trace*: it shows a generic
gather→act→verify rollout with tool calls, and it never names R/S/X/M or marks
which boxes are SIGA-added vs. native-harness. **A lazy reader who looks only at
Fig 2 cannot learn what our contribution is**, and cannot decode Table 1's
column headers. That's the highest-leverage fix in this whole document: make
R/S/X/M the visual hero of Fig 2 and define them in-figure.

### A second, optional gap

The paper has **no results figure** — the headline finding (reliability lift /
order-of-magnitude variance reduction / hard-tail rescue) lives only in tables.
Given the advisor's philosophy, that's the single most important empirical
result and it's invisible to a figures-only reader. I put a concrete proposal
for an optional **Figure 3** at the end. You only asked about 1 & 2, so treat it
as a bonus.

### Housekeeping flagged

- `\includegraphics` on line 74 points to `assets/geos_fig1_v2.png`, which **is
  not in `assets/`** (only the old `siga_fig1.png` and `siga_fig2.png` are
  there). The new Fig 1 needs to be exported to that path.
- Both figures are referenced exactly **once** and both refs are buried
  mid-paragraph. See §4 for where to add references.

---

## 1. Figure 1 — the problem (intent → DSL bottleneck)

### WHY (purpose)

Convince the reader, before any method, that:

1. **There is a real, expensive bottleneck** between a scientist's intent and a
   runnable simulation — and it is *not* the science, it's the *translation into
   the simulator's DSL*. (This is the abstract's "advanced tool-operating
   bottleneck" and the intro's central claim.)
2. **The bottleneck has a specific shape**: extensive documentation must be used
   as a translation guide to produce an *elaborate* configuration (the XML
   deck). Show, don't tell, that the docs are large and the config is intricate.
3. **The payoff is real science** — the fancy 3D multiphysics visualizations
   establish that we operate a serious, authoritative scientific tool (CO₂
   storage, reservoir flow, geomechanics, thermo-poro-elastic coupling).
4. (Light touch) **This is the step we automate** — a thin bridge to Fig 2, so a
   figures-only reader knows the paper offers a solution, not just a complaint.

The emotional beat: *"look how much machinery a scientist must wade through just
to express what they already know they want."*

### WHAT (content spec)

The 1→2→3→4 narrative you have is good. Lock in these four nodes, each with a
visualization, left to right:

| # | Node label | Visualization | The point it makes visually |
|---|-----------|---------------|------------------------------|
| 1 | **Specify the experiment** | Simulation spec — the natural-language brief and/or a small schematic of the physical setup (e.g. the 1D Buckley–Leverett column, or a wellbore cross-section) | Intent starts in plain scientific language. *(Advisor wants this restored — agreed, it's the anchor of the "intent" side.)* |
| 2 | **Consult docs (the DSL guide)** | Screenshot of the GEOS Sphinx doc sidebar / table of contents, with a long scrollbar or many nested entries visible | Documentation is *extensive* and requires navigation — this is what costs time. |
| 3 | **Author the config (the DSL)** | XML deck snippet in an editor (use the real `buckleyLeverett_base.xml` — already in `assets/`) | The configuration is *elaborate*: nested tags, cross-references, many attributes. |
| 4 | **Run + visualize results** | The "fancy" 3D meshes: CO₂ storage, reservoir flow, wellbore geomechanics, thermo-poro-elastic coupling | Scientific authority + the payoff that justifies the cost. |

**Must-have on-figure annotations (for standalone value):**

- A **headline banner** with the thesis sentence, e.g.:
  *"Powerful scientific software ships with expressive configuration languages;
  converting intent into a runnable experiment costs domain scientists hours to
  days."*
- A **cost callout on the 2→3 span** (the doc→config translation): label it
  **"hours–days: the bottleneck."** This is the one place a number/timescale must
  appear. The paper supports it: experts new to GEOS *timed out at ~48 min on the
  easy task and didn't finish*; experienced-user estimate is "<30 min simple to a
  couple of days for compound multiphysics" (§4.3 / App. H).
- A thin **"← SIGA automates this"** marker spanning steps 2–3, pointing toward
  Fig 2. Keep it subtle so it doesn't duplicate the method figure.
- Keep the section vocabulary honest: GEOS decks span **ten canonical sections**
  forming the DSL (§3). You can label the config panel "10-section XML DSL."

**Deliberately NOT in Fig 1:** the R/S/X/M components, the agent loop, results
numbers, TreeSim. Those belong to Fig 2 / results. Fig 1 is problem-only.

### HOW (layout)

Single-column NeurIPS → **wide and short.** Target aspect ~**3.2:1**
(`width=\textwidth`, modest height).

```
┌───────────────────────────────────────────────────────────────────────────┐
│  HEADLINE: intent → runnable experiment costs hours–days (the bottleneck)  │
├──────────────┬──────────────┬──────────────┬───────────────────────────────┤
│  1 SPECIFY   │  2 DOCS      │  3 AUTHOR    │  4 RUN + VISUALIZE            │
│  experiment  │  (DSL guide) │  config(DSL) │                               │
│              │              │              │   ┌─────────┐ ┌─────────┐     │
│  [spec /     │  [Sphinx ToC │  [XML deck   │   │ CO2     │ │reservoir│     │
│   schematic] │   sidebar,   │   snippet,   │   │ storage │ │ flow    │     │
│              │   long list] │   nested]    │   ├─────────┤ ├─────────┤     │
│              │              │              │   │geomech. │ │thermo-  │     │
│              │              │              │   │         │ │poro-el. │     │
│              │              │              │   └─────────┘ └─────────┘     │
│   ──────────────▶──────────────▶──────────────▶                            │
│              └── hours–days ──┘   "← SIGA automates this"                  │
└──────────────┴──────────────┴──────────────┴───────────────────────────────┘
  narrow         narrow          narrow          WIDE (~35–40% of width)
```

Layout rules:

- A **left-to-right ribbon/arrow** along the bottom ties 1→2→3→4 into one
  workflow. Put the "hours–days" bracket under the 2→3 segment.
- **Steps 1–3 are narrow** (each ~18–20% width); **step 4 gets the remaining
  ~35–40%** as a 2×2 mini-gallery, because the visualizations are the
  "scientific authority" sell and they read best at larger size. Don't starve
  them.
- Use a consistent visual grammar: each node is a titled card; the screenshot
  artifact sits inside the card. Number badges ①②③④ top-left of each card.
- Keep palette restrained (the current figures use soft pastel section fills —
  match that). The 3D meshes provide the only saturated color; let them pop.
- Aesthetic fixes over the hasty version: align card tops, equalize gutters,
  ensure the XML snippet is legible at print size (≥ \footnotesize equivalent;
  show ~8–12 representative lines, not a full file), and crop the Sphinx
  screenshot tightly to the sidebar so "extensiveness" reads instantly.

### Draft caption (standalone)

> **Figure 1. The advanced-tool-operating bottleneck.** Running a modern
> simulator requires translating scientific intent into the tool's
> domain-specific configuration language. For GEOS, a scientist (①) specifies an
> experiment, (②) navigates extensive documentation that serves as a translation
> guide, (③) authors an elaborate 10-section XML deck, and (④) finally obtains
> results — here CO₂ storage, reservoir flow, wellbore geomechanics, and
> thermo-poro-elastic coupling. The ②→③ translation step routinely costs domain
> scientists hours to days (§4.3); it is the step SIGA automates (Fig 2).

---

## 2. Figure 2 — the method (base harness + R/S/X/M adapters)

### WHY (purpose)

This is the **method figure** — it must answer "what is SIGA and how does it
work?" The three jobs:

1. **State the design stance:** we do *not* build an agent loop; we take an
   off-the-shelf coding agent (Claude Code) as a base harness and bolt on a thin
   adapter. "Adaptation over reconstruction" (§4.1). This must be visually
   obvious: native harness machinery in one visual register, our four added
   components in another.
2. **Define R/S/X/M and the failure mode each fixes.** This is the contribution
   and the key to reading Table 1. Currently absent from the figure — the most
   important addition.
3. **Show the rollout** (gather → act → verify → run) so the reader sees *where*
   each adapter plugs into the loop. The current execution-trace content is good
   for this; we're augmenting it, not discarding it.

### WHAT (content spec)

Keep the existing three-band skeleton (**Inputs → Agent Loop → Run GEOS**) and
the real screenshots/snippets — they're effective. Add the contribution layer:

**(a) Mark the four adapters explicitly with badges + a legend.** Each adapter
gets a colored letter badge placed on the loop step where it acts, plus a
legend row defining it. This is the single most important change.

| Badge | Name | Mechanism (what it adds) | Failure mode it fixes | Where in loop |
|-------|------|--------------------------|------------------------|---------------|
| **R** | Retrieval | semantic search (MCP) over GEOS docs / examples / schema | unknown-vocabulary substitution | Gather context |
| **S** | Refine loop | schema-validating **termination hook** (mandatory; xmllint) | silent incompleteness (empty/invalid deck) | Verify results |
| **X** | Validator | agent-callable xmllint MCP tool (optional, mid-trajectory) | in-loop schema drift | Verify / act |
| **M** | Memory | 775-token procedural cheatsheet, always-on via `--append-system-prompt` | recurring-vocabulary lookup | Inputs (system primer) |

> Tip: in the legend, **flag S as the dominant transferable component** (a small
> star or "↑ carries the reliability lift"). It's the paper's punchline (§6) and
> a figures-only reader should catch it.

**(b) Visually separate SIGA-added from native harness.** Native tools
(write/read file, bash, TODO) in muted grey; the four adapters in saturated,
legend-matched colors. A light "SIGA adapter" container/outline around the four
added pieces drives home "thin wrapper, not a new agent."

**(c) Keep the concrete artifacts** (they earn the figure its credibility):
- Inputs: task brief snippet, SIGA primer snippet, GEOS repo file-tree.
- Gather: tool-call JSON for doc/example/schema search + memory read.
- Act: TODO list, file-edit diff (write-to-memory), emitted XML snippet.
- Verify: the real schema-error feedback string, e.g.
  *"element Mesh: Schemas validity error: The attribute 'xCoords' is required
  but missing."* — keep this; it makes the S/X mechanism tangible.
- Run GEOS: a couple of result visualizations (ties back to Fig 1 ④).

### HOW (layout)

Wide, three horizontal bands (as now), with a **new thin legend footer** so the
adapter definitions stay on-figure without making it tall. Target ~**2.2–2.5:1**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INPUTS            →         AGENT LOOP (Claude Code harness)      →  RUN GEOS │
│  ┌──────────┐               ┌───────────────────────────────┐     ┌────────┐  │
│  │task brief│               │ ① GATHER CONTEXT   [R][M]      │     │ 3D mesh│  │
│  ├──────────┤               │   doc/example/schema search,  │     │ result │  │
│  │primer [M]│   ─────────▶   │   read memory                 │ ──▶ │ viz    │  │
│  ├──────────┤               │ ② TAKE ACTION                 │     └────────┘  │
│  │repo tree │               │   TODOs · write mem · emit XML │                │
│  └──────────┘               │ ③ VERIFY RESULTS   [S][X]      │                │
│                             │   schema check / repair feedbk │                │
│                             └───────────────────────────────┘                │
│   (native harness tools shown in grey; SIGA adapters in color)                │
├───────────────────────────────────────────────────────────────────────────--┤
│ LEGEND:  R retrieval — unknown vocab │ S refine-loop hook ★ — silent           │
│ incompleteness │ X validator — schema drift │ M memory — recurring vocab       │
└─────────────────────────────────────────────────────────────────────────────┘
```

Layout rules:

- Keep the dominant left→right flow (Inputs → Loop → Run). The loop band is the
  widest; Inputs and Run are narrower flanks.
- Place each badge **on the sub-step where the adapter acts**, so the reader maps
  letter → location → mechanism without reading prose.
- The **legend footer is one or two thin rows** spanning full width — this keeps
  the figure wide rather than tall while making it standalone.
- Color discipline: pick four distinct hues for R/S/X/M and reuse the *exact same
  hues* if you build the optional Fig 3 and (ideally) as accents in Table 1.
  Cross-figure color consistency is a big standalone-readability win.
- Honesty note already in the paper: S and X both use xmllint, so when S is on it
  also runs xmllint (§5.2). You don't need this nuance in the figure, but don't
  draw X and S as fully independent if it misleads — the badges + legend are
  enough.

### Draft caption (standalone)

> **Figure 2. SIGA: four grounding adapters bolted onto an off-the-shelf coding
> agent.** Rather than build an agent loop, we treat Claude Code as a base
> harness (grey) and add four lightweight components (color), each targeting a
> known agent failure mode: **R** semantic retrieval over GEOS artifacts
> (unknown-vocabulary substitution), **M** an always-on procedural cheatsheet
> (recurring-vocabulary lookup), **X** an agent-callable schema validator
> (in-loop schema drift), and **S** a mandatory schema-validating termination
> hook (silent incompleteness). The agent gathers context, drafts the XML deck,
> and verifies it against the GEOS schema until valid, then runs GEOS. The
> ablation in Table 1 isolates each component; **S** carries the reliability lift
> and is the one that transfers to OpenFOAM (§6).

---

## 3. (Bonus) Figure 3 — the result, if you want one

Not requested, but strongly aligned with the advisor's philosophy: the headline
result is currently table-only and therefore invisible to a figures-only reader.
A small, wide results figure would carry RQ1 (the paper's core claim).

**WHY:** show that adapters move the **reliability** axis, not absolute quality —
the "gap between the two columns is the headline" claim (§5.1).

**WHAT (strongest single candidate):** a **per-seed dot/strip plot on
held-out-eval**, Vanilla vs S+X vs SE, with the catastrophic-failure rescues
annotated:
- Vanilla σ = 0.081 (one seed → unparseable XML → 0 on `ExampleProppantTest`)
  collapsing to σ ≈ 0.002–0.005 under adapters — the order-of-magnitude variance
  drop reads instantly as "dots spread out → dots tight."
- Annotate the two rescues: `AdvancedExampleThermoPoroElasticWellbore`
  0.355→0.761 and `ExampleProppantTest` 0.541→0.825.

**Alternative WHAT:** a grouped bar of the bottleneck categories showing
`missing_block` dropping (6→3) while `bad_attribute_value` stays flat (12/11/15)
— visualizes "schema adapters fix block omissions, not attribute errors" (§5.2),
the residual-frontier story.

**HOW:** wide, short, two small panels side by side (val | held-out-eval), reuse
the R/S/X/M color palette. ~3:1.

If you build it, it'd slot at the top of §5 (Results) and lets Table 1 become the
detailed backup rather than the only carrier of the headline.

---

## 4. Adding figure references in the text

Currently Fig 1 and Fig 2 are each referenced **once**, both mid-paragraph. The
standalone philosophy is helped by *more* explicit, well-placed callouts. Concrete
suggestions:

**Figure 1:**
- **Intro, opening of the bottleneck paragraph** (currently the "Numerical
  simulation is among the most widely used…" para, line 80): add a forward ref
  early, e.g. end the first or second sentence with "(Fig 1)". Right now the only
  Fig 1 ref is deep in the *next* paragraph (line 84). The problem statement and
  the problem figure should be adjacent.
- **Background §3** ("GEOS as a domain-specific simulator language"): line 84
  literally says "details deferred to §background" — so §3 should re-reference
  Fig 1 ("the ten canonical sections of Fig 1 ③…") to close that loop.

**Figure 2:**
- **Method §4.1** already refs it at line 120 ("an execution trace is in Fig 2").
  Upgrade this: ref Fig 2 at the *start* of §4.1 when introducing the
  adaptation-over-reconstruction stance, and again where the four components are
  introduced (§4.1, the R/S/X/M paragraph) — "the four components (Fig 2)…".
- **Results §5.1 / Table 1:** add "(components defined in Fig 2)" next to the
  first use of the R/S/X/M cell names, so the table's column headers are
  decodable from the figure.

**If Fig 3 is added:** reference it at the top of §5.1 as the visual headline,
with Table 1 as the detailed backup.

---

## 5. Summary of recommendations (priority order)

1. **[High] Fig 2: surface R/S/X/M as the visual hero** — badges on loop steps +
   a legend footer defining each component and the failure mode it fixes, with S
   flagged as the dominant/transferable one. Separate native (grey) from SIGA
   (color). This is the biggest content win; without it the method figure
   doesn't show the contribution.
2. **[High] Fig 1: keep the 1→2→3→4 problem narrative**, restore node ① (spec),
   put the "hours–days bottleneck" cost callout on the 2→3 span, and give node ④
   (visualizations) ~35–40% of the width. Add a subtle "SIGA automates this"
   bridge to Fig 2.
3. **[High] Export the new Fig 1** to `assets/geos_fig1_v2.png` — the `.tex`
   already points there but the file is missing.
4. **[Med] Add figure references** in the intro, background, and results (§4).
5. **[Med] Rewrite both captions** to be standalone (drafts above).
6. **[Low/optional] Add Fig 3** (reliability/variance result) to put the headline
   empirical finding in front of a figures-only reader.
7. **[Low] Cross-figure color consistency** for R/S/X/M across Fig 2, Fig 3, and
   ideally Table 1.

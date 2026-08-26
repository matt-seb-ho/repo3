# Unified Story: One- and Two-Liner Options

Your advisor is asking for a 1–2 sentence summary. Your prose summary in chat was ~150 words and tried to carry four distinct ideas at once: (i) agents need specialized harnesses for scientific simulators, (ii) we adapt SOTA coding agents rather than building new ones, (iii) simple recipe of well-explored ingredients, (iv) four sub-studies. That is a paper outline, not a pitch.

A 1–2 line pitch should commit to **one** noun phrase for what the paper *is*, and **one** verb phrase for what it *does*. Below are candidate framings, ordered by my recommendation.

---

## What the paper *is* (pick one noun phrase)

- **A1.** An application + empirical study of adapting off-the-shelf coding agents for scientific-simulator configuration.
- **A2.** A case study in geophysics-simulation deck authoring with a general-purpose coding agent.
- **A3.** A new benchmark and factorial study of agent grounding components for scientific simulator setup.

A1 most accurately matches the Application-track framing. A3 sounds more like a methods paper.

## What the paper *does* (pick one verb phrase)

- **B1.** …shows a simple recipe of retrieval, validation hooks, and procedural memory closes most of the gap to a domain expert and identifies which components actually carry the weight.
- **B2.** …measures which standard agent components matter, how the agent compares to humans, how it behaves under autonomy, and whether the recipe ports to a second simulator.
- **B3.** …finds that the adapter wins are concentrated in *reliability* on hard compound-physics tasks, not in average quality on easy ones, and that the dominant lever is a forced end-of-turn schema check.

B1 is the cleanest single-claim pitch. B3 is the most accurate to your actual results.

---

## Recommended one-liners (advisor-ready)

### Option 1 — application-first, recipe-style (RECOMMENDED for a non-specialist)
> We adapt an off-the-shelf coding agent (Claude Code) to author multiphysics simulation decks for the GEOS geophysics simulator, and empirically identify which standard grounding components — retrieval, schema-validation hooks, and procedural memory — actually make it reliable on this real-world scientific-software task.

### Option 2 — finding-first, more honest about scope
> Wrapping a general-purpose coding agent with a few well-explored components (retrieval, a schema-validation stop-hook, and a procedural-memory cheatsheet) closes most of the gap to a domain expert on GEOS multiphysics deck authoring; a factorial study shows that the lift is almost entirely a reliability gain on hard compound-physics tasks, carried mainly by the stop-hook.

### Option 3 — position-paper-ish, foregrounds the methodology choice
> An application paper arguing that the right way to give AI agents access to advanced scientific software is to *adapt* an existing SOTA coding agent rather than build a new harness from scratch, demonstrated on GEOS geophysics simulation setup with a benchmark, a factorial study of grounding components, and a small cross-simulator transfer.

### Option 4 — shortest possible
> An empirical study of what it takes to turn a general-purpose coding agent into a reliable assistant for authoring GEOS multiphysics simulation decks.

---

## Two-line versions (when you have one extra breath)

### Pair A (RECOMMENDED for the advisor message)
> **Line 1 (what):** We adapt an off-the-shelf coding agent (Claude Code) into a GEOS multiphysics deck-authoring assistant by wrapping it with a small package of standard components — retrieval, a schema-validation stop-hook, a procedural-memory cheatsheet, and an optional self-evolution loop.
>
> **Line 2 (why it's interesting):** A factorial study, a human baseline, an autonomy probe, and an OpenFOAM transfer test surface several reusable findings for scientific-agent design — most notably that reliability (not average quality) is what wrappers buy you, that retrievable procedural memory is ignored, and that humans aren't consulted when an executable example library is available.

### Pair B (positioning-first)
> **Line 1 (claim):** Scientific simulators are configured through complex, codebase-specific DSLs that today require expert authors; we argue that the most practical way to delegate this to AI is to adapt an existing SOTA coding agent rather than build a bespoke one.
>
> **Line 2 (delivery):** We instantiate this on GEOS, propose a simple grounding recipe of retrieval + schema-validation + procedural memory, and empirically dissect which components matter, how the agent compares to humans, and whether the recipe ports to OpenFOAM.

---

## What to drop from your current summary

These don't earn their words in a 1–2 liner. Keep them for the abstract.

- **"Agents need specialized harnesses…"** — this is a *premise* for your work, not the *claim*. Stating it suggests the paper proves it; it does not.
- **"Self-validation / self-improvement"** — the SE variant is one of several sub-studies and the data is ambiguous (`16%` fewer calls is val-only). Don't promote it to the elevator pitch.
- **The list of four sub-studies** — these are the *evidence*, not the *claim*. The pitch should commit to a claim and let the experiments support it.
- **"Recipe of well-explored ingredients"** — accurate but reads defensive. Reframe positively: "a small, off-the-shelf recipe" or "standard grounding components."

---

## A test for the one-liner

When you read it aloud to a non-NLP, non-geoscience colleague, they should be able to answer:

1. What is the paper about? → *adapting an agent for geophysics simulator setup*
2. What did you build? → *a wrapper with retrieval, a validator, and a memory file*
3. What's the headline finding? → *it works, and the validator is the part that matters*

If your draft pitch fails any of these, it's still trying to carry too much.

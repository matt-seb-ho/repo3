# Storytelling Suggestions: Method and Overall Paper

This is paired with `neurips_review.md` (the fresh-context adversarial review). The review is what a reviewer would say after reading. This document is about what you can change to make the *next* reviewer say something different.

Your advisor's framing is correct: the paper is an **Application-track empirical study**, not a method paper. The current draft, however, is written like a *method* paper that keeps apologizing for not having a novel method. The fix is not to add novelty — it is to commit to the application framing and rewrite the surrounding scaffolding to match.

There are two storytelling problems, addressed below in order:

1. **Method-section storytelling** — the local problem of how SIGA is introduced and motivated within §4.
2. **Whole-paper storytelling** — the global problem of what the paper is *about* and how the contribution is positioned.

---

## Part 1 — Method-section storytelling

### Diagnosis: what's wrong with §4 today

§4 (Method) reads as a feature catalog: "we add R, S, X, M; here is what each one is." Each component gets a paragraph that explains *what it is*, not *why an agent needs it for this task*. The result is that:

- The four components feel arbitrary (why these four? why not five?).
- The "we did not invent these" framing is implicit and reads as embarrassed.
- The "SIGA" acronym is introduced as a *system* (a thing you built), which sets reviewer expectations toward a novel method.
- The self-evolved variant (SE) is introduced as another bullet in the list, when in fact it is a different *kind* of contribution (an automated discovery method, not a hand-built one).
- The Resolution-IV factorial — which is the *empirical contribution* — appears as a sub-subsection (§4.2) inside the method, where it gets less prominence than the components themselves.

### Reframe: §4 as a "design space" rather than a "system"

The method section should narrate **the design space of grounding components for an existing coding-agent harness**, not "the SIGA system." Three small but high-leverage moves:

1. **Open §4 with the question, not the answer.** First sentence should be something like: *"What does a general-purpose coding agent need on top of itself to operate a scientific simulator? We argue four binary choices span the practical design space, and we test all four."* That immediately makes §4 an investigation, not an announcement.

2. **Motivate each component from a failure mode, not a feature.**
   Right now you have R/S/X/M defined by what they do. Replace with what they fix:
   - "**Retrieval (R)** addresses the *unknown-vocabulary* problem: GEOS uses class names the model has never reliably memorized."
   - "**Stop-hook (S)** addresses the *silent-incompleteness* problem: agents terminate with structurally invalid outputs they could have caught."
   - "**Agent-callable validator (X)** addresses the *in-loop-correction* problem: even if outputs are checked at termination, the agent can also self-check during generation."
   - "**Memory cheatsheet (M)** addresses the *recurring-vocabulary-lookup* problem: agents spend tool calls re-deriving facts an expert would remember."
   This is closer to how engineers actually pick components, and it foreshadows the bottleneck analysis (§5.2) — which is the strongest part of your paper but currently feels disconnected.

3. **Demote "SIGA" or rebrand it.** Right now SIGA is presented as the *thing*, and the components as parts of it. The data shows the opposite is true: each component has its own effect, and "SIGA" as a unified system is mostly just the bag containing them. I'd seriously consider one of:
   - Drop the acronym entirely and call it "grounding adapters for Claude Code."
   - Keep the acronym but redefine it as **a class of adapters, not a specific system** ("any grounding adapter belongs to the SIGA design space"). Then the factorial study is "exploring the SIGA design space" — much better than "we built SIGA, here are its components."
   - Rename to something less ego-laden, like "GEOS adapter for Claude Code" — but only if you're willing to give up the noun phrase.

   See the **Name** discussion below for more.

### Concrete edit: a rewritten §4.1 opening

Before:
> Our agent is a customization of Claude Code (CC), not a re-implementation of the agent loop. We add four binary SIGA components through CC-supported extension mechanisms…

After (one option):
> **What does a general-purpose coding agent need on top of itself to operate a scientific simulator?** We treat this as a design question over a small space of well-understood grounding components. Rather than re-implementing an agent loop, we use Claude Code as a fixed harness and study which off-the-shelf extension mechanisms — retrieval, termination hooks, agent-callable validators, and procedural-memory primers — actually move the needle on simulator deck authoring. Each component is introduced below by the *failure mode it is intended to address*, not by what it is.

This single rewrite (a) reframes you as an investigator, not an inventor, (b) signals Application-track values, and (c) sets up the bottleneck section to land harder.

### Make SE/SE-prose feel like a separate contribution

Right now SE is one of three bullets at the end of §4.1, with a brief mention that an offline pipeline rewrites the adapter contents. This buries what is actually one of the more interesting bits of your paper: an automatically-discovered adapter matches or beats the best hand-designed one. Two options:

- **Promote SE to its own paragraph or §4.3**, framed as "can the adapter be discovered automatically?" Make explicit that this is the *upper-bound check on the design-space study*: if a self-evolved variant in the same design space wins, the design space is well-chosen; if not, it's not.
- **Or: drop the "SE-prose" name** and just call the two variants "self-evolved adapter" and "ablation: text-only portion of self-evolved adapter." Save the reader from another acronym.

The reviewer agent flagged that the "16% fewer tool calls" claim is val-only and reverses on held-out-eval. Either soften the claim in §4 or excise it from the abstract — currently the abstract says "matches the best hand-designed cell with roughly 16% fewer tool calls" without qualifiers, and that won't survive review.

---

## Part 2 — Whole-paper storytelling

### Diagnosis: what the paper is *about* is unclear

A reader who finishes the abstract should be able to say in one sentence what this paper is contributing. Right now the abstract carries five distinct claims (reliability, quality, self-evolution, human baseline, autonomy + OpenFOAM transfer), all of equal weight, none of them obviously the headline. The result is that the reader picks whichever finding looks weakest and treats *that* as the contribution.

The four contribution bullets in §1 are also strangely balanced: a benchmark, the SIGA evaluation, two "cautionary findings," and an OpenFOAM study. The cautionary findings are arguably the most reusable for the agent-research community, but they appear in third position.

You need to **decide what the paper's spine is** and rewrite the abstract and §1 to commit to it. There are three viable spines:

### Spine 1 — "An application paper for geophysics-simulation setup"

The contribution is *the assistant itself plus its evaluation in the GEOS domain*. Audience: NeurIPS Applications + geoscience.

- Headline becomes: "We deliver a usable GEOS multiphysics deck-authoring assistant built from off-the-shelf components, evaluated against domain-expert humans."
- Numbers get rephrased in domain-relevant terms: "$8$–$36\times$ speedup over domain-expert humans," "comparable deck quality on a representative task."
- The factorial study becomes *evidence supporting the deployment decision*, not the contribution.
- The OpenFOAM transfer is supportive: "the recipe is not GEOS-specific."
- The cautionary findings are interesting side-effects.

**Risk:** NeurIPS reviewers (even Application track) will say "this belongs at a geoscience venue." You need the cautionary findings + design-space study to keep it at NeurIPS.

### Spine 2 — "An empirical study of what makes coding agents reliable on scientific software"

The contribution is *the empirical lessons about agent grounding*, with GEOS as the proving ground.

- Headline: "We empirically dissect which grounding components make a general-purpose coding agent reliable for scientific-simulator setup, using GEOS as a hard test case."
- The factorial + bottleneck analysis become the main study.
- Cautionary findings (memory-as-retrieval, consultation rate) are promoted to headline contributions because they generalize.
- The application becomes a *case study*, not the contribution.
- The OpenFOAM transfer becomes a generalization claim.
- The human baseline becomes a calibration anchor, not a headline.

**Risk:** Reviewers say "the methodology isn't novel; you only ran on one simulator." You need the application framing and the OpenFOAM transfer to defend.

### Spine 3 — "A position paper with a working demonstration"

The contribution is the *argument that adapting existing SOTA agents beats building bespoke ones*, with SIGA as the existence proof.

- Headline: "We argue that scientific-software agents should be built by adapting existing SOTA coding agents, not from scratch, and demonstrate the argument by building one for GEOS that closes most of the gap to domain experts."
- Related work becomes prominent: each "bespoke" agent (Foam-Agent, etc.) is contrasted with your "adapter" approach.
- The factorial study supports the position by showing that *cheap, well-known components* are enough.
- The Foam-Agent comparison becomes critical evidence (and you need to fix the lint-only issue).

**Risk:** Position papers need *much* sharper claims about what they're arguing for and against. You need a clearly-articulated alternative that you're rejecting (i.e., a strawman of "build it from scratch" that's fair to the existing literature). And the OpenFOAM transfer with Foam-Agent crippled to lint-only undercuts the central comparison.

### My recommendation: pick a hybrid of Spine 1 and Spine 2

Lead with **Spine 1 framing** (Application paper, GEOS-the-application) and use **Spine 2 substance** (empirical findings that generalize). Concretely:

1. Open §1 with the geophysics motivation and the size of the bottleneck — paint the human-time cost vividly. (One sentence on "CO$_2$-storage simulators take experts hours/days" is in the current draft; expand it to a short paragraph.)
2. Make the second paragraph the *position*: building bespoke agents per simulator is expensive; adapting an existing SOTA agent is cheaper and may generalize.
3. Define the design space (R/S/X/M) as *the cheapest set of moves that have been shown to work elsewhere*.
4. State the contributions in this order:
   1. A working GEOS deck-authoring assistant (with benchmark + human anchor).
   2. An empirical dissection of which grounding components actually matter.
   3. Two reusable findings about agent autonomy and memory delivery.
   4. Cross-simulator transfer evidence to OpenFOAM.
5. Make the abstract follow the same order. The current abstract leads with reliability/quality numbers, which is the *finding*, not the *contribution*.

### Headline numbers: pick three, drop the rest

The current abstract throws ~6 numbers at the reader: $40\times$, $7$pp, $16\%$, $3\%$, $8$–$36\times$, $0.871$. Five of these are debatable when scrutinized (see the review). Pick the three that hold up best:

- **$+7$pp mean TreeSim on held-out-eval.** Defensible; cite the table.
- **$\sim 3\%$ supervisor-consultation rate.** This is one of the genuinely surprising findings.
- **A wallclock anchor against humans on `buckleyLeverettProblem`.** State it as "$\sim 7$ min for the agent vs $\sim 3$h for a domain-expert volunteer" rather than "$36\times$."

Drop or qualify:
- The $40\times$ variance ratio. Replace with "eliminates zero-score failures on $\geq 2$ specific tasks." That's the underlying mechanism.
- The $16\%$ fewer tool calls. Either qualify ("on val") or drop.
- The $8\times$ human speedup. The participants timed out; the $36\times$ no-cap number is the honest one.

### Foreground the negative findings — they are your most reusable contribution

The fresh-context reviewer's strongest single observation (and I agree): the **memory-as-retrieval negative result** and the **consultation-rate finding** are more *novel as contributions* than the recipe itself. Those are claims about *agents in general*, not just GEOS. They are also the parts a NeurIPS reviewer will recognize as paper-worthy. Right now they appear in §5.2 and §5.4 in passing.

A bold version of this paper would promote them to the level of co-headline contributions in §1, give each its own subsection in §5, and structure the discussion around what they imply for scientific-agent design beyond GEOS. This costs ~0 experimental work and dramatically increases the per-page contribution density.

### Lead with reliability, not quality

The current abstract says: "First, SIGA improves reliability… Second, it improves quality… Third, a self-evolved variant…" The data clearly says reliability is the headline (the quality effect is small and tail-driven; the self-evolution effect is modest). State it that way, and the bottleneck analysis (§5.2) then plays the role of explaining the headline rather than reporting a side finding.

### Honesty moves that strengthen the paper

The reviewer flagged that several claims overshoot what the data supports. A *more honest* framing actually reads stronger to Application-track reviewers, who are trained to suspect overselling. Concrete suggestions:

- Add one sentence in §5.1: "*The held-out-eval gain is concentrated in two specific tasks; the remaining seven are within seed noise of val.*" That's already true; saying it out loud makes you look careful, not weak.
- Replace "matches the best hand-designed cell with roughly $16\%$ fewer tool calls" with "achieves comparable TreeSim with comparable tool-call counts (val: $-16\%$; held-out-eval: $+8\%$)." Same fact, no overclaim.
- Add an explicit limitation: "We did not run Foam-Agent in its native execute mode; the comparison should be revisited when that issue is resolved." (Currently this is in App.~K and Discussion; foreground it.)
- In the human baseline subsection, replace "$8$ to $36\times$ as long as the agent" with "the budget-matched comparison is bounded below by $8\times$ (humans timed out); the extended-budget comparison reaches $36\times$ on a single task." More words, much harder to attack.

---

## Part 3 — Small mechanical fixes

These are not storytelling but they will distract reviewers from the storytelling if left in.

1. **Anonymization breach in App. K.** Lines 611 of the .tex name participants "Liam" and "Sahchit" verbatim. Replace with P1/P2 before *anything else* — this is a desk-reject-class issue for blind review. (The body of the paper uses P1/P2 correctly, so this is just App. K.)
2. **`\sys` macro defined but unused.** Line 47 defines `\sys` as `\textsc{GeoAgent}`. Either use it consistently and pick a real name (see below), or remove it.
3. **Name choice.** The paper currently uses both "SIGA" and an undefined `\sys`/`GeoAgent`. Pick one and commit. My vote: keep "SIGA" but redefine as a *design-space* term as described above; drop GeoAgent entirely. Alternatively, drop SIGA and call it "the GEOS adapter for Claude Code" — costs you a noun phrase but reads less like a method paper.
4. **The R-factor result is on contaminated data.** §5.1's claim that "the only main effect that clears noise is R, with a negative sign" rests on data that App.~F (`app:cross-model-detail`) admits was contaminated by the native-plugin-prefix bug. Either (a) re-run F0/F4/F6/SE with the fix and update the number, or (b) state the contamination directly in §5.1, not just in limitations. (See the `Future work` appendix: this is listed as a $\sim$1.5h, low-cost re-run. Do it.)
5. **Title.** "Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study" reads as a method paper. If you go with the Spine-1 framing, consider something like "Adapting an Off-the-Shelf Coding Agent for Geophysics Simulation Setup: A GEOS Case Study." The commented-out alternative on line 50–51 ("Coding Agent Adaptation for Advanced Scientific Tooling: An Application Study in Automating Geophysics Simulations") is closer to the Application-track framing than the current title.

---

## Summary: minimum-effort changes that move the needle

If you do nothing else, do these five (in this order):

1. **Fix the anonymization breach in App.~K.** Trivial; non-negotiable.
2. **Rewrite the abstract** to lead with reliability (one number, one mechanism), demote the rest. ~1 hour of writing.
3. **Reorder §1 contributions** to put the cautionary findings at #1 or #2, not #3. Change the framing of contribution #2 from "definition + evaluation of SIGA" to "empirical dissection of which grounding components matter." ~30 min.
4. **Rewrite §4.1 opening** from "we built SIGA" to "we investigate the design space of grounding components." ~1 hour.
5. **Re-run F0/F4/F6/SE with the prefix-gate fix** so §5.1 doesn't rest on contaminated data. ~1.5h compute; low API cost.

Total: half a day of writing + 1.5h compute. This is the difference between a Borderline Reject and a Borderline Accept under the fresh-context reviewer's judgment.

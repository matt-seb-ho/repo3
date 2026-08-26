# SIGA contribution to MAESTRO §4.4 (Lianhui-led preliminary results)

**Where this slots in.** Section 4.4 ("Core AI: Geophysics, Mechanics and Chemistry
Collaborating Agents", leads: Maziar **and Lianhui**). Section currently has a
~½-page Maziar paragraph on NewPINNs / multi-agent geoscience and a ~½-page
Michael/Amir block (E1: Arbitrage, Multipole Attention, RCD, PRM-BiasBench,
SciML Agents; E2: neural digital twins + MatterChat). The Lianhui-led
preliminary-results paragraph is currently missing. The target length, matched to
Maziar's paragraph and to the "1 page" section budget, is **one dense paragraph
(~250–300 words)** plus optional figure.

---

## Draft paragraph (ready to paste, matched to Maziar's prose style)

> **Lianhui (UCSD), preliminary results on grounding general-purpose coding agents
> in scientific-simulator interfaces.** Translating a researcher's natural-language
> intent into a runnable simulator deck — the executable XML, input scripts, and
> namelists that function as a simulator's domain-specific language — is a
> recurring expert bottleneck repeated across the many simulations a realistic EGS
> study demands. The Lianhui group has developed and benchmarked
> **Simulator-Interface Grounding Adapters (SIGA)** [Ho et al., 2026, under
> review], a wrapper layered on top of an existing engineered coding harness
> (Claude Code) that packages four components — interface retrieval, an
> agent-callable schema validator, a forced end-of-turn self-verification stop-hook,
> and a procedural-memory cheatsheet — through the harness's supported extension
> mechanisms. Instantiated for **GEOS** (LLNL, the same multiphysics simulator
> targeted elsewhere in MAESTRO) and evaluated by a Resolution-IV 2⁴⁻¹ factorial
> on a 27-task deck-authoring benchmark spanning poromechanics, hydraulic
> fracture, thermo-poroelastic wellbore, and proppant-transport problems, the best
> SIGA cell delivers **~40× lower across-seed variance** (σ 0.081 → 0.002–0.005),
> **+7 pp mean structural similarity** on a hard-tail held-out set of compound
> multi-physics tasks (Vanilla 0.720 → self-evolved SIGA 0.789), and matches that
> quality at **~16% fewer tool calls**, with gains concentrated on the compound
> tasks where the unadapted harness collapses to unparseable output. A human
> baseline with two geoscience-domain-expert volunteers (new to GEOS) and a
> written estimate from a GEOS developer (LLNL) brackets domain-expert authoring
> at one-to-two files in a one-hour budget on an *easy* deck and "a couple of
> days" for compound multi-physics decks — placing the agent's parity-quality
> output at **8–36× wall-clock speedup** on exactly the THMC coupling problems
> MAESTRO targets. A 5-task transfer study confirms the recipe ports beyond GEOS
> XML to OpenFOAM (best SIGA cell mean score 0.871 vs 0.466 for the vanilla harness
> and 0.569 for the OpenFOAM-native Foam-Agent baseline in its lint-only execution
> mode), with forced end-of-turn verification identified as the single most
> transferable adapter mechanism. These results de-risk **§3.4 Task A** (the
> standardized EGS decision environment + coding agent that must reliably invoke
> GEOS/PFLOTRAN/DFNWorks/EGS-Sandbox) and **§3.4 Task B** (typed-interface
> subagents that replace unrestricted free-form tool calls) by establishing that
> wrapper-level grounding turns a multi-day expert-authoring bottleneck into
> minutes of agent wall-clock with quantified reliability budgets, and they
> contribute a bottleneck-analysis methodology — schema-grounding fixes
> block-level absences but not attribute-level semantic errors — that directly
> motivates the closed-loop validator-driven retry design in §3.4 Task B's
> Verification subagents.

---

## Headline numbers (quick reference for editors)

| Metric | Vanilla Claude Code | Best SIGA cell | Direction |
|---|---|---|---|
| Held-out TreeSim (mean, n=3 seeds) | 0.720 | **0.789** (SE, self-evolved) | +6.9 pp |
| Across-seed std on held-out | 0.081 | **0.002–0.005** (S+X, X+M) | ~40× reduction |
| Tool calls per task (val) | 81.5 | **68.9** (SE) | ~16% fewer |
| OpenFOAM mean score (5-task transfer) | 0.466 | **0.871** (R+S) | +0.40 |
| OpenFOAM, vs Foam-Agent (lint-only) | 0.569 | **0.871** | +0.30 |
| Human (1 h budget, domain-expert new to GEOS) | file-level 0.78–0.81, deck-level 0.53–0.54, only 1 of 2 required files | agent ~7 min, ≥ 0.90 file/deck | ~8× wall-clock |
| Human (no time cap, both files) | deck-level 0.931, ~3 h | agent ~5 min, deck-level ≥ 0.90 | ~36× wall-clock at parity quality |
| GEOS developer (LLNL) written estimate | <30 min easy / "a couple of days" compound | agent: minutes on both | — |

**Honest framing to retain in any rewrite:** SIGA's quantitative gains are scoped
against vanilla Claude Code, not against an expert human; the agent-vs-human gain
is wall-clock speedup at parity quality (not a quality-ceiling claim). This
matches the paper's discussion and avoids overclaiming to grant reviewers who may
also see the manuscript.

---

## Connection to MAESTRO tasks (what the paragraph above is claiming to de-risk)

- **§3.4 Task A — standardized EGS decision environment + trained coding agent.**
  The agent in Task A must reliably invoke GEOS, GEOSX, PFLOTRAN, DFNWorks,
  EGS-Sandbox, SW4, and learned surrogates. SIGA is direct evidence that
  wrapper-level grounding turns deck authoring from a multi-day expert task into
  minutes of agent wall-clock, on the exact GEOS interface MAESTRO targets.
- **§3.4 Task B — typed-interface subagents (Characterization / Stimulation /
  Operation / Verification).** Task B's defining design choice is "typed
  interfaces rather than unrestricted free-form tool calls". The SIGA stop-hook
  (forced end-of-turn schema validation) and validator MCP (`xmllint_validate_geos_xml`)
  are working instances of typed-interface enforcement; the OpenFOAM transfer is
  direct evidence the mechanism is not GEOS-specific.
- **§3.4 Task B Verification subagents.** SIGA's bottleneck analysis isolates
  what static grounding *cannot* fix (attribute-level semantic errors:
  `bad_attribute_value` 12 / 11 / 15 across Vanilla / X+M / S+X) — direct
  motivation for the closed-loop validator-driven retry / process-reward design.
- **Auxiliary: §3.4 Task A axis (ii) "robust step-level verification".** The
  PRM-BiasBench paragraph (Michael/Amir) is the *evaluator* story; SIGA is the
  *enforcer* story. They are complementary and worth mentioning as such if space
  permits.

---

## Suggested figure (≤ ¼ column, optional)

Two existing figures are available at `writing/neurips/assets/siga_fig1.png` and
`siga_fig2.png`. **Recommended for the grant: a slimmed Fig. 2-style bar/box
plot showing held-out TreeSim mean and across-seed σ for Vanilla, X+M, S+X, and
SE,** with an inset or caption call-out of the wall-clock-vs-human comparison.
Caption draft:

> Figure XX. SIGA wrapper-level grounding turns a multi-day expert deck-authoring
> task into minutes of agent wall-clock. On a 10-task held-out set of compound
> multi-physics GEOS decks, the best SIGA cell lifts mean structural similarity
> from 0.720 (vanilla Claude Code) to 0.789 and collapses across-seed std from
> 0.081 to ≤ 0.005, with a domain-expert one-hour budget completing only one of
> two required files at the easy end of the benchmark.

If only one figure fits and Maziar's transmissivity figure stays, drop the SIGA
figure and keep the headline-numbers table or inline statistics in the prose.

---

## Citation note (action item for Lianhui / Matt)

The SIGA paper is **currently anonymous (NeurIPS 2026 under review)**. The grant
proposal needs a real citation. Three options:

1. **De-anonymized author list + arXiv preprint URL** (recommended; matches how
   Maheswaran/Hooper/Hu/Tiwari/Gaonkar are cited in §4.4 E1). Action: post arXiv
   preprint with author names visible to reviewers and cite it as
   "Ho et al., 2026" or whatever the agreed author order is.
2. **"Anonymous, NeurIPS 2026, under review"** — acceptable but weaker.
3. **Internal LLNL-style technical report citation** if there is one.

Bibliography entry to add (placeholder; fill once option chosen):

```
Ho, M., [coauthors], Yang, L. (2026). Simulator-Interface Grounding Adapters for
Scientific Simulation Setup: A Geophysics Case Study. NeurIPS 2026 (under
review). [arXiv URL].
```

---

## Open questions for Lianhui to decide before submission

1. **Author order in the grant citation.** Need to lock the byline shown to grant
   reviewers; this also affects who is named in-line ("the Lianhui/Ho group ...")
   vs in the bib entry. The draft above uses "Lianhui group" for the in-line
   attribution.
2. **Figure-yes / figure-no.** Section 4.4 is already figure-heavy (transmissivity
   figure, "Placeholder figure: Transmissivity Experiments (artist working on
   it)" appears twice — possibly a duplication bug in the current draft). If the
   page budget is tight, the SIGA paragraph can stand without a figure.
3. **Cross-reference to §3.4.** The draft cites §3.4 Tasks A and B explicitly,
   matching Maziar's "de-risk the §3.4 Task A and §3.4 Task B deliverables"
   construction. Confirm this is the intended task mapping (vs Task C
   data-flywheel, which SIGA is less directly evidence for).
4. **Inclusion of the autonomy / human-consultation negative result** (the agent
   uses an explicit `consult_supervisor` tool only ~3% of the time, treating an
   on-disk example library as a cheaper retrieval substitute). This is one of the
   SIGA paper's four contributions and is directly relevant to MAESTRO's
   MatterChat / human-in-the-loop story (§3.4.4), but it is *cautionary* rather
   than *capability* evidence and may not fit a "preliminary results that
   de-risk MAESTRO" paragraph. The current draft omits it; flag for Lianhui to
   either insert one sentence or reserve for §3.4.4 framing.

---

## Source

- SIGA paper: `writing/neurips/neurips_2026.pdf` (31 pp, NeurIPS 2026 submission).
  Headline results: §6 (pp. 6–8), Table 1 (p. 6), Table 2 (p. 8). OpenFOAM
  transfer: §6.3 + App. G. Human baseline: §6.5 + App. K.
- Grant proposal draft: `writing/grant_proposal/maestro_doe_draft.pdf`. Lianhui
  section located at line 933–934 of the extracted text (§4.4 header). Maziar's
  prose paragraph at lines 936–955 is the style model. §3.4 Task A/B descriptions
  at lines 683–730.

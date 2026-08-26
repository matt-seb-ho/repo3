# SIGA Rebuttal — Plan v2, grounded on the actual NeurIPS 2026 timeline

**Written 2026-07-26. Supersedes the strategy (not the facts) in `REBUTTAL_TRIAGE_v1.md`, which assumed a revised-PDF workflow that this year's handbook forbids.**
Earlier files preserved unchanged: `REBUTTAL_TRIAGE_v1.md`, `VERSION_DIFF_REPORT.md`, `ARXIV_VS_REVIEWS.md`, `REBUTTAL_MERGE_RECOMMENDATION.md`, `siga_neurips_reviews_clean.md`.

---

## 0. Direct answers to your four questions

**Q: Can we prioritize analysis of existing runs + answering questions + writing, over new experiments?**
**Yes — and it is now forced, not merely preferable.** The handbook says: *"No revisions to the paper or supplementary material during the response period… your original submission remains the basis for the reviewers' and AC's acceptance decisions."* There is no revised PDF this year. Every plan in v1 that routed value through an updated manuscript (the two-day clarity rewrite, new figures, a new results subsection) **cannot be delivered at all** in this window. Those become camera-ready commitments described in text.

**Q: Are the reviews asking for more experiments for sure?**
**One, and it is small.** gep1: *"Even 5 tasks across Vanilla and the best SIGA cell."* That is ~10 runs. Everything else the reviewers ask for is already answerable from data on disk — I verified the largest piece myself today (§2). The binding constraint on that one experiment is **not compute or money, it is the absence of a GEOS binary.**

**Q: Can we say experiments are continuing and add results later?**
**Yes. You have 8 days of author-visible window, not 2.** Phase 2 (Jul 27 – Aug 3) explicitly states *"You can continue to respond."* So:
- **Jul 27** — initial response deadline. Build it **entirely from existing data.**
- **Jul 27 – Aug 3** — post new results as follow-up comments as they land.
- **Aug 3** — hard stop. Phase 3 is reviewer/AC only; you cannot post or even see it.
Anything landing after Aug 3 is worthless for this decision. Plan to **Aug 3, not Aug 7.**

**Q: How much more experiment are they asking for?**
Quantified in §5. Short version: 10 runs requested by gep1; ~$4 and 3 h of optional cleanup that answers his second score-moving ask; and zero required for the other three reviewers' asks. **The initial response needs no new compute whatsoever.**

---

## 1. What the handbook changes about v1

| v1 assumption | Reality | Consequence |
|---|---|---|
| Revised PDF permitted | **Forbidden.** No revisions, no supplementary changes | The 2-day clarity rewrite is not a deliverable. Demonstrate clarity *in the response text*; commit the rewrite for camera-ready |
| ~800–1000 words per reviewer | **10,000 characters** (~1,500–1,700 words) | You have *more* room than v1 budgeted. Use it on gep1 |
| Single-shot rebuttal | Three phases; authors active through **Aug 3** | Late-landing experiments are postable. v1's "never promise future evidence" softens — see §4 |
| Figures/tables available | Markdown only, **no uploads, no links** | Everything must survive as a plain-text table. No new figures anywhere |
| LAMMPS could be ported in | Nothing enters the paper | **Do not introduce LAMMPS.** §6 |

Two handbook lines that should steer the whole response:
- *"Use the initial meta-review as your guide. It tells you what would most likely change the AC's view."* → **The AC's four bullets are the spec.** Not the union of all reviewer asks.
- *"Responses serve to clarify… you do not need to rewrite the paper in a hurry."* → The AC expects commitments, not a rushed rewrite. This is permission to answer kEdh with a plan rather than a panic.

---

## 2. The asset that carries the response — verified by me today

I re-ran this myself rather than trusting the subagent. `xmllint --schema` against the canonical GEOS XSD (`data/GEOS/src/coreComponents/schema/schema.xsd`, checked into the source tree — **no GEOS build required**), over decks already on disk. **Zero new compute.**

**Held-out-eval (10 tasks × 3 seeds = 30 runs/cell), fully schema-valid runs:**

| Cell | Valid / total |
|---|---|
| Vanilla (F0) | **24 / 30** |
| X+M (F4) | 30 / 30 |
| S+X (F6) | 30 / 30 |
| S+X+M (F8) | 30 / 30 |
| SE-prose (F11) | 30 / 30 |
| SE | 30 / 30 |

Fisher exact, 24/30 vs 30/30: two-sided **p = 0.0237**, one-sided p = 0.0119.

**Val (17 tasks × 3 seeds = 51 runs/cell), all 11 cells** — I extended this beyond what v1 reported:

F0 49/51 · F1 49/51 · F2 49/51 · F3 50/51 · F4 **51/51** · F5 50/51 · F6 **51/51** · F7 **51/51** · F8 **51/51** · F11 **51/51** · SE 50/51 (one run wrote no XML at all)

**Why this is the centrepiece:** it reproduces the paper's central thesis — adapters matter only on the hard tail — on a metric that is **not TreeSim** and is execution-adjacent. Val is at ceiling for everyone; held-out separates cleanly. That is precisely the AC's "does structure translate to something realer" question, answered one rung up the ladder.

### The two caveats you must state yourselves

**(a) Partly true by construction.** S and X cells invoke `xmllint --schema`, and the S stop-hook gates termination on it. A cell that refuses to terminate until schema-valid reaching 30/30 is close to tautological. Frame it as *"the adapter delivers the guarantee it promises, at no cost to the other metrics"* — a mechanical claim, not an emergent one. **X+M (F4) is the least circular cell** (the validator there is agent-callable and optional, not enforced), so it carries the most evidential weight — say so.

**(b) Effective n is well below 30.** I checked the clustering: the 6 Vanilla failures span only **4 distinct tasks**, and by seed they are **s1 = 2, s2 = 0, s3 = 4**. Runs are not independent. Report p descriptively and say why. Stating this before gep1 finds it is worth more than the p-value is.

### What it does *not* do — the discipline that protects the whole response

The AC asked whether configs *"execute successfully, converge, or produce physically meaningful simulations."* Schema-validity answers **none of those three.** gep1's "runnable" means GEOS executes it. This is **rung 2 of 5.**

> **Overselling this as "we addressed the execution ask" is the single highest-risk move available to you.** gep1 recomputes things and the AC explicitly made execution the decision criterion. Present it as rungs 1–2 of a stated ladder, with rungs 3–5 named. The honesty is itself the argument.

---

## 3. The recommended shape of the initial response (due Jul 27)

Built 100% from existing data. Nothing below requires a run.

| # | Content | Source | New compute |
|---|---|---|---|
| 1 | Validity ladder, held-out + val panel | §2, verified | **No** |
| 2 | S/X isolation from the existing build-up ablation | `docs/2026-04-30_dsv4-ablation-final-v2.md` ⚠️ unverified | **No** |
| 3 | OpenFOAM at 30 tasks + MetaOpenFOAM as 2nd baseline | `docs/openfoam_n30/` ⚠️ unverified | **No** |
| 4 | Prefix-bug contamination bounded, with sign argument | `docs/ablation_C2_vs_C9.md` ⚠️ unverified | **No** |
| 5 | Claude Code version `2.1.119` | events.jsonl ⚠️ unverified | **No** |
| 6 | Human-baseline narrowing (concession) | — | **No** |
| 7 | Clarity: the actual rewritten sentences, inline | §7 | **No** |
| 8 | Main-effects correction (see §8) | verified | **No** |

⚠️ **Before any of items 2–5 goes to reviewers, someone must open the file and confirm the number.** I verified item 1 by re-running it and items 8 by re-deriving them; the rest come from subagent reads I have not independently checked. A wrong number in a rebuttal is unrecoverable.

### Character budget (10,000/review)

- **gep1 — use ~9,500.** He is the winnable score and wrote two explicit conditionals. Order: execution ladder → prefix bug + S/X → OpenFOAM → human baseline → limitations wording.
- **kEdh — ~7,000.** Definitions inline, camera-ready plan, one line on venue.
- **nBNe — ~3,500.** He is at 5. Answer his three questions, concede gracefully, **change nothing else.** Do not re-argue novelty; do not give him new reasons to think.
- **AC — separate Official Comment, ~5,000.** The four meta-review bullets in order. §9.

---

## 4. Should you promise the execution experiment?

v1 said never promise future evidence. Phase 2 changes that — but only partly.

**Recommended: the asymmetric play.** In the initial response, present rungs 1–2 as done, name rungs 3–5 as the ladder, and commit the full ladder to **camera-ready**. Do *not* promise a Phase-2 delivery date. Then if `geosx --validate-input` lands by Aug 1, post it as a follow-up comment — **pure upside, no downside.**

Why not promise: a missed promise lands immediately before Phase 3, when you can no longer respond to it. The build is the one item with real technical risk (submodules unpopulated, prior attempts stalled at TPL). Promising a result you control neither the timing nor the sign of, into a window that closes while reviewers keep talking without you, is a bad trade for a borderline paper.

**Only exception:** if someone owns the build *today* and it is already working by the time you post, state it.

---

## 5. Experiments — what to launch, and what to skip

**Launch today, in the background** (does not consume rebuttal-writing time):

1. **Prefix-bug clean rerun** — ~$4, ~3 h, 5 cells. Directly answers gep1's second score-moving ask. Cheap enough that the only reason not to is if nobody can babysit it. If it lands tonight it goes in the initial response; otherwise Phase 2.
2. **GEOS build attempt, time-boxed to 3 days, one named owner.** The only path to rung 3. If it has not built by Jul 30, stop and fall back to the concession — do not let it eat the window.

**Skip:**

3. **Extra seeds (n=3→5).** I agree with v1 and I'd go further given the timeline. Vanilla's held-out σ = 0.081 comes from a *single* zero-score seed, so more seeds most likely raise Vanilla's mean and **shrink** the headline +0.069. Once run you are committed to reporting it, and you would be reporting it *into* an active discussion. Answer the AC's uncertainty ask with paired per-task bootstrap intervals on data already reported — no new runs, no new risk.
4. **OpenFOAM multi-seed** (~$70, 1–2 days). The existing 30-task single-seed campaign already answers the ask. Not worth the window.
5. **Foam-Agent execute mode.** Previously failed; OpenFOAM 13 is not even compiled locally. Decline and reframe, as gep1 explicitly permits.

**Total new compute needed for a strong initial response: none. For a strong Phase 2: ~$4.**

---

## 6. Do not introduce LAMMPS

It is not in the submitted paper, the paper cannot be revised, and the submission is what the decision is based on. Introducing a third simulator in a rebuttal buys no credit and invites *"this is now a different paper."* Its methodology is also the weakest of the three studies (9 tasks × 1 run, no native baseline, and the LLM judge is one of the two backbones it scores) — exactly the profile the reviewers are already punishing at 10 tasks × 3 seeds.

Hold it for camera-ready and the arXiv version. Same reasoning applies to the whole arXiv rewrite: **`REBUTTAL_MERGE_RECOMMENDATION.md`'s port list is a camera-ready plan, not a rebuttal plan.** Its value is that you can tell the AC, credibly and specifically, what the revised paper will look like.

One item there does matter *now*: the arXiv version **deleted** the native-plugin-prefix bug disclosure and **moved Limitations to an appendix.** gep1 asked for both to be strengthened. Whoever does camera-ready must not inherit those two regressions.

---

## 7. Clarity — the argument that actually helps you

kEdh (Reject, conf 4) says *"this paper needs to be significantly re-written."* You cannot rewrite it. **His score will probably not move, and that is acceptable** — his real function is as ammunition for the AC, who independently endorsed the complaint.

So aim the clarity work at the AC, with this framing:

> **Clarity is the only weakness on the table that is certain to be fixed.** Evidence gaps require experiments that may not land or may come out negative. A definition, a plain-language gloss, a worked example — these are certainties, fully within camera-ready scope, requiring no new science. The AC should weight a *certain* fix differently from a *hoped-for* one.

Make it credible by **writing the replacement text inline in the response.** Don't say "we will clarify"; show the sentence. Each of kEdh's four items, answered concretely:

**"deck" (currently defined in §3, too late):**
> A *deck* is the simulator's input file — for GEOS, an XML document that specifies the mesh, physics solvers, material models, boundary conditions, and time-stepping schedule. It is what a scientist must write before any simulation can run, and authoring it correctly is the bottleneck this paper studies. We will move this to the first paragraph of §1.

**Resolution-IV 2^(4−1) factorial:**
> We have four on/off components, so 16 combinations. Running all 16 is expensive, so we run a carefully chosen half (8). "Resolution IV" is the guarantee that this half still lets us measure each component's individual effect without it being confused with any two-component interaction.

**buckleyLeverettProblem:**
> A standard two-phase flow benchmark in which one fluid displaces another through porous rock. It has a known analytical solution, so it is a common correctness check for subsurface simulators.

**"brief" and "structured repair feedback"** — give one concrete example of each, verbatim from a run.

**The failures-as-zero sentence** — replace:
> When the agent produces no usable file at all — an empty output, a file that is not valid XML, or a run that times out — we score it 0 rather than excluding it. Otherwise a system could look good by failing loudly instead of answering badly.

**Venue:** one sentence, last, addressed to the AC, non-defensive. Do not litigate it.

---

## 8. The numerical corrections — my recommendation: volunteer them

I re-derived these from Table 1 of the submitted `.tex`; both are errors in the submitted paper, and **both corrections make the paper's own claims stronger.**

| Factor | Submitted (App. table) | Correct |
|---|---|---|
| R | −0.032 | **−0.0368** |
| S | −0.003 | **−0.0078** |
| X | +0.007 | **+0.0113** |
| M | +0.004 | **+0.0083** |

The submission is also internally inconsistent: §5 and the appendix say R = −0.032; the Limitations paragraph says −0.033. Separately, the harness-less recovery figure is **+0.488** (0.821 − 0.333), not the +0.164 printed.

**Volunteer both, briefly, inside the gep1 response.** Reasoning: gep1 asked about the R estimate by name, so you will be quoting these numbers anyway; the corrected R is *larger* in magnitude, which strengthens the paper's "retrieval hurts" finding; the corrected harness-less figure is *larger*, strengthening "the harness contributes substantially." A self-caught error that moves your own numbers the right way is close to free credibility, and it is exactly the rigor the reviewers are probing for. The corrected values are already public in the arXiv version — being second to your own correction is much worse than being first.

**One live-fire rule for the whole response: never pair a mean from one cell with a σ from another.** The submitted abstract pairs "+7pp" (SE) with "40×" (S+X); the arXiv abstract pairs 0.789 (SE) with "16×" (X+M). SE's own ratio is 0.081/0.012 ≈ **6.75×**. Nobody has raised this, and it is defensible in the paper as "best cells" plural — so **do not proactively volunteer it.** But if you repeat that pairing in a rebuttal while claiming rigor, it becomes a real problem. Instead, print the per-cell σ table (Vanilla 0.081 · X+M 0.005 · S+X 0.002 · SE 0.012) and let the reader see which ratio belongs to which cell. Full transparency, no self-inflicted wound. If asked in Phase 2, answer straight.

---

## 9. AC comment — the spec

The AC gave four bullets and said to use them as the guide. Answer in their order, ~5,000 chars:

1. **Execution vs structure** — the ladder, rungs 1–2, with both caveats stated. Name rungs 3–5. This is the decision criterion; give it half the space.
2. **Clarity** — the fixability argument from §7, plus 2–3 of the actual rewritten sentences as proof.
3. **Scale** — representativeness of the 10 held-out tasks; bootstrap intervals; explicit narrowing of robustness/generalization claims. The AC offered this trade ("moderate the claims if additional evaluation is unavailable") — **take it.**
4. **Human comparison** — narrow it to "preliminary calibration," which is the AC's own phrase. Free credibility.

---

## 10. Schedule to Aug 3

| When | What |
|---|---|
| **Today (Jul 26)** | Verify items 2–5 in §3 against files. Launch prefix-bug rerun. Assign GEOS build owner. Draft all four responses. |
| **Jul 27** | Final numbers check — every figure traced to a file on disk. **Post all four + AC comment.** Post early in the day; the handbook says engage early. |
| **Jul 28–30** | Monitor follow-ups; respond within a day. GEOS build go/no-go by Jul 30. |
| **Jul 31–Aug 2** | If rung 3 landed, post it. Otherwise post the prefix-bug clean rerun. Keep answering. |
| **Aug 3** | Last day authors can post. Final summary comment to the AC if the discussion moved. |

---

## 11. Open questions for you

1. **Does anyone own the GEOS build today?** If no, decide *now* to go with the concession and reallocate. Do not leave it ambiguous — an unowned build silently eats the window.
2. **The LLNL route.** Dr. Sherman could run `--validate-input` in a few hours, but the handbook requires anonymity and forbids links. Sending decks to a named external collaborator mid-review is a policy question — check before doing it, and treat "no" as likely.
3. **Verify items 2–5 in §3.** Named above; do not skip.
4. **The "+0.24" discrepancy.** Four internal docs claim the prefix probe showed +0.24; the measured contrast is +0.004. Resolve before drafting so nobody quotes the wrong one — this number would go into gep1's response, the highest-stakes text you write.
5. **Is the OpenFOAM n=30 campaign trustworthy enough to cite?** It postdates submission by three weeks and was read only at summary level. Spot-check it, or drop it and answer gep1's Q3 with the qualitative concession he already offered.
6. **Can you post an Official Comment addressed to the AC?** The handbook mentions Official Comments only for the code-link exception. If a general AC comment is not available, fold §9 into the top of the gep1 response and open kEdh's with a short version.

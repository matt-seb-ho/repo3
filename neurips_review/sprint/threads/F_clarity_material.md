# Thread F — Clarity Material for Reviewer kEdh (sub. 31642, SIGA)

Mission: gather + verify raw material for the kEdh clarity response. **Gather only — main thread drafts prose.**
`writing/` and `/data/shared/` are READ ONLY. Nothing under either was modified.

---

## Files opened

- `/home/matt/sci/repo3/neurips_review/siga_neurips_reviews_clean.md` (full read, 159 lines)
- `/home/matt/sci/repo3/writing/neurips/neurips_2026.tex` (full read, 746 lines) — **the submitted version**
- `/home/matt/sci/repo3/writing/arxiv/neurips_2026.tex` (939 lines, targeted reads: 88–132, 265–320, 373–385)
- `/home/matt/sci/repo3/scripts/analyze_autocamp.py` (lines 385–440)

## Greps run

```
grep -n "Resolution-IV\|Resolution IV\|2^{4-1}\|2^4\|generator"  writing/neurips/neurips_2026.tex
grep -noi "deck"                                                  writing/neurips/neurips_2026.tex
grep -n "buckleyLeverett\|Buckley"                                writing/neurips/neurips_2026.tex
grep -n "strictly perfect\|perfect deck"                          writing/neurips/neurips_2026.tex
grep -n "failures-as-zero\|Headline numbers average"              writing/neurips/neurips_2026.tex
grep -rn "F_FACTORS" scripts/ src/ run/
# arXiv side:
grep -n "Resolution-IV\|2^{4-1}\|fractional\|alias\|generator\|confound"  writing/arxiv/neurips_2026.tex
grep -n "strictly perfect|failures-as-zero|Headline numbers|unscorable|brief|Buckley"  writing/arxiv/neurips_2026.tex
grep -noi "deck"                                                  writing/arxiv/neurips_2026.tex
git log --oneline -5 -- writing/arxiv/
```

---

## F1 — "Resolution-IV 2^(4−1) factorial"

### Verbatim first uses in the SUBMITTED tex (`writing/neurips/neurips_2026.tex`)

**NOTE / correction to the brief:** the parent asked me to start at `:92` and `:154`. Those are NOT the first
uses. The term appears **first in the abstract at `:67`** and then in the **intro at `:84`**, both before
`:92`. This strengthens kEdh's point: the term lands on the reader in the abstract with zero scaffolding.
All five body occurrences below.

- `:67` (abstract), verbatim clause:
  > `A Resolution-IV factorial surfaces three benefits over vanilla Claude Code.`

- `:84` (intro), verbatim clause:
  > `Our main experiment is a Resolution-IV $2^{4-1}$ factorial over four binary factors: \textbf{retrieval} over GEOS documentation, schema, and examples (\textbf{R}); a \textbf{stop-hook} verifier that checks outputs at termination (\textbf{S}); an agent-callable \texttt{xmllint} \textbf{XML} validator (\textbf{X}); and a compact \textbf{memory} cheatsheet appended to the system prompt (\textbf{M}).`

- `:92` (Contributions (ii)), verbatim clause:
  > `A definition and component-by-component evaluation of \textbf{Simulator-Interface Grounding Adapters (SIGA)} via a Resolution-IV factorial plus a self-evolved variant`

- `:154` (subsection heading):
  > `\subsection{Resolution-IV factorial and bottleneck analysis}`

- `:157` — the ONLY place the design is described, verbatim:
  > `\textbf{Cells.} Each of $\mathrm{R,S,X,M}$ is binary. Instead of the full $2^4$ design, we run a Resolution-IV $2^{4-1}$ fraction with generator $\mathrm{D}{=}\mathrm{ABC}$, giving eight cells whose main effects are not confounded with two-factor interactions.`

Other occurrences (captions/appendix, not first-use): `:184`, `:207`, `:312`, `:398`, `:404`.

**Gap: term is used at `:67` (abstract, p.1) and only explained at `:157` (§3.2). Never is
"Resolution IV" itself defined — `:157` states the consequence ("main effects not confounded with
two-factor interactions") but never says what resolution IV means, never gives the defining relation,
and never says what the two-factor interactions ARE aliased with.**

### Design confirmed from code

`/home/matt/sci/repo3/scripts/analyze_autocamp.py:396-406`, verbatim:

```python
# 4-bit factor labels for F-cells (R, S, X, M)
F_FACTORS = {
    "autocamp_F0": (0, 0, 0, 0),
    "autocamp_F1": (1, 0, 0, 1),
    "autocamp_F2": (0, 1, 0, 1),
    "autocamp_F3": (1, 1, 0, 0),
    "autocamp_F4": (0, 0, 1, 1),
    "autocamp_F5": (1, 0, 1, 0),
    "autocamp_F6": (0, 1, 1, 0),
    "autocamp_F7": (1, 1, 1, 1),
}
```

Maps 1:1 onto Table 5 (`app:cells`, tex `:320-327`): F0=Vanilla, F1=R+M, F2=S+M, F3=R+S, F4=X+M,
F5=R+X, F6=S+X, F7=R+S+X+M. Confirms the parent's stated mapping exactly.

### VERIFIED: it is a correct Resolution-IV design

Machine-checked (±1 coding, 8 runs):

```
generator check  M == R*S*X : True
defining relation I = RSXM  : True
```

Design matrix (R, S, X, M in ±1):
```
F0 [-1,-1,-1,-1]   F4 [-1,-1, 1, 1]
F1 [ 1,-1,-1, 1]   F5 [ 1,-1, 1,-1]
F2 [-1, 1,-1, 1]   F6 [-1, 1, 1,-1]
F3 [ 1, 1,-1,-1]   F7 [ 1, 1, 1, 1]
```

**Full alias structure — 8 estimable contrasts, exhaustive:**

| Estimable contrast | Aliased with |
|---|---|
| R | S×X×M |
| S | R×X×M |
| X | R×S×M |
| M | R×S×X |
| R×S | X×M |
| R×X | S×M |
| **R×M** | **S×X** |
| — | R×S×X×M (= I, the defining word) |

Shortest word in the defining relation is length 4 (RSXM) ⇒ **Resolution IV**. Each main effect is
aliased only with a 3-factor interaction; the six 2-factor interactions collapse into exactly **three
aliased pairs**: {R×S, X×M}, {R×X, S×M}, {R×M, S×X}.

**CONFIRMED: S×X is aliased with R×M.** (Verified, not asserted.)

Note the paper's `:157` writes the generator as "D = ABC" with the A,B,C,D→R,S,X,M identification left
implicit — i.e. M = R⊕S⊕X. That is itself a clarity item (see F5 #4).

### Run-count saving

- Half fraction actually run: **8 cells × 3 seeds = 24 cell-seed runs**
- Full 2⁴ factorial would be: **16 cells × 3 seeds = 48 cell-seed runs**
- Saving: **24 runs, exactly 50%** — 2× not 4×.

Task-level (val split, 17 tasks/cell): 8×3×17 = **408 task-runs** vs 16×3×17 = **816 task-runs**.
At the measured Vanilla val wall-clock of 359 s/task (`tex:680`, Table `tab:efficiency`), that is
≈40.7 h of task-compute vs ≈81.4 h — **~41 h of GPU/API time saved**.

**Discrepancy to flag to the main thread:** the arXiv rewrite at `arxiv:282` says the full factorial
costs "$4{\times}$ the runs" — that is **wrong**; 2⁴ vs 2⁴⁻¹ is 2×. The same line then correctly says
"at half the compute". Do not repeat the 4× figure in the response. (The submitted NeurIPS version does
not make this error — it says nothing quantitative at all.)

Also note the paper runs **11** cells total, not 8: it adds S+X+M (the 16th corner), SE-prose and SE
(`tex:157`, `tex:329-331`), so actual spend is 11×3 = 33 cell-seed runs vs 48 for a full factorial.
Honest framing of the saving is "8 of 16 corners for the screening design; we then bought back the one
corner main effects predicted was best."

---

## F2 — "deck" defined too late; two unreadable sentences

### Sentence 1 — "strictly perfect decks"

Appears **three** times in the submitted tex, not two.

- `tex:86` (Introduction, final sentence of the findings paragraph) — VERBATIM:
  > `The number of strictly perfect decks does not increase under any adapter.`

- `tex:216` (§Results, bottleneck) — VERBATIM:
  > `\textbf{(4) Strictly perfect tasks (TreeSim $\geq 0.999$) do not increase} under any adapter (Vanilla 7/51, X+M 6/51, SE 6/51).`
  (This is the ONLY place "strictly perfect" is operationalised — as TreeSim ≥ 0.999. It is 130 lines
  after first use.)

- `tex:281` (Conclusion) — VERBATIM clause:
  > `SIGA operates in a harm-reduction regime, not a correctness regime, and the count of strictly perfect decks is unmoved by any configuration we tried.`

### Sentence 2 — the failures-as-zero sentence

`tex:169` — VERBATIM, complete:
> `\paragraph{Metric: TreeSim.}\label{subsec:metric} We score generated decks with \textbf{TreeSim}, a tree-edit similarity in $[0,1]$ decomposed by the ten canonical GEOS sections. Headline numbers average TreeSim under \emph{failures-as-zero}: parse errors, timeouts, \texttt{failed\_no\_outputs}, and missing XML outputs all score 0, so systems are not rewarded for unscorable files.`

The sentence kEdh quotes is the second one. Undefined terms inside it: `failures-as-zero` (coined here,
never elsewhere defined), `failed_no_outputs` (a raw internal status-string from the runner, never
explained anywhere in the paper), "unscorable".

### "deck" — first use vs first definition

- **First use: `tex:67`** (abstract, two occurrences on that line):
  > `... modern simulators are configured through executable interfaces such as XML decks, input scripts, and namelists that function as domain-specific languages tied to the simulator's internal API.`
  and later in the same abstract:
  > `... by preventing unparseable or empty decks on a hard tail of compound multi-physics tasks.`

- **First definition: `tex:111`** (§3 Background, opening sentence):
  > `A GEOS deck is one or more XML files that specify a multiphysics simulation across ten canonical sections, covering the mesh, geometry, execution schedule, physics modules, material models, computational regions, numerical methods, field specifications, functions, and outputs.`

- **Gap: 44 source lines (`:67` → `:111`); more importantly the word is used 11 times before it is
  defined** — at `:67` (×2), `:76` (figure caption), `:82` (×3), `:86` (×2), `:88`, `:91`. In the
  compiled PDF that is abstract + all of §1 + §2 (≈pages 1–3) before §3 explains it. kEdh's
  "Section 3 does explain what a 'deck' is, but this comes too late" is exactly right.

### arXiv status (`writing/arxiv/neurips_2026.tex`, 939 lines)

The arXiv draft **has independently fixed F1 and part of F2**. This is strong material for the
"we already know how to fix this" argument — but see the anonymity warning below.

1. **Factorial (F1) — fixed at `arxiv:282`.** Now motivates the design before naming it. Key clause
   (verbatim from disk):
   > `A standard one-factor-at-a-time ablation ... cannot disambiguate main effects from two-factor interactions: if R and S help only when combined, neither single-factor ablation reveals this. The full $2^4 = 16$-cell factorial does, at the cost of $4{\times}$ the runs. We instead use a \emph{Resolution-IV $2^{4-1}$ fraction} with generator $\mathrm{D}{=}\mathrm{ABC}$, which gives us eight cells whose main effects are not confounded with two-factor interactions, recovering most of the information of the full factorial at half the compute.`
   Still does not give the alias structure, and contains the 4× arithmetic error noted above.

2. **failures-as-zero (F2 sentence 2) — fixed at `arxiv:310`.** The submitted sentence is now
   **commented out** at `arxiv:294` and replaced at `arxiv:302-313` with (verbatim):
   > `Generated decks are scored with TreeSim, a tree-edit similarity metric in $[0,1]$ computed over the canonical GEOS deck structure. We report failures-as-zero: parse errors, timeouts, missing XML outputs, and empty outputs all receive score 0. This convention is important because simulator setup is only useful when the returned workspace is executable or at least structurally inspectable.`
   Two real improvements: the jargon token `failed_no_outputs` is dropped in favour of plain
   "empty outputs", and a *because* clause explains why the convention exists.

3. **"strictly perfect" (F2 sentence 1) — partially fixed.** The intro sentence (`tex:86`) is **gone**
   from the arXiv intro. The Results occurrence survives at `arxiv:376` in de-bolded form and is now
   followed by a new explanatory paragraph (`arxiv:378`) giving two reasons the
   `bad_attribute_value` count stays flat. Term "strictly perfect" is still not defined at first use.

4. **"deck" (F2) — improved but the gap is not closed.** arXiv still uses "deck" in the intro
   (`arxiv:115`, "A valid input deck must satisfy syntax constraints, schema constraints, and physical
   or domain-conventional constraints, while maintaining consistent names and references across
   sections and often across files") before defining it in §3 (`arxiv:150`, same "A GEOS deck is one or
   more XML files..." sentence). The arXiv intro does however give far more surrounding context
   (`arxiv:113-115` build up simulator → input language → DSL → deck), so the term is *inferable* at
   first use even though not formally defined.

> **ANONYMITY WARNING — must be paraphrased, NOT pasted.** `writing/arxiv/` contains
> `arxiv_v1.pdf`, `arxiv_upload.zip`, `arxiv_upload_jun8.zip`, and `ARXIV_INSTRUCTIONS.md`, i.e. an
> arXiv submission package was built. I could **not** confirm from disk whether it was actually posted
> (no arXiv ID anywhere in the tree, no "posted" marker). Treat as posted. Any distinctive sentence
> from these files is Google-searchable and would deanonymize submission 31642. **Every arXiv-derived
> improvement above must be re-expressed in fresh wording in the response.**
> Additional non-obvious risk: the arXiv version **de-anonymizes people the submitted version already
> names** (submitted `tex:237/611/636` names "Dr. Chris Sherman (LLNL)", "Liam", "Sahchit"; arXiv
> `:389/806/827` replaces these with "Expert 1 / Expert 2 / a GEOS expert and developer"). Do not
> quote either naming scheme in the response.
> Also: the arXiv draft adds a **LAMMPS** transfer study (`arxiv:470`, `\subsection{Transfer to LAMMPS...}`)
> that is not in the submission. Mentioning it in a rebuttal would be new-results-out-of-scope AND an
> anonymity link. Do not mention LAMMPS.

---

## F3 — real brief + real structured repair feedback

Dispatched two parallel search agents (results appended below when they return):
- Agent 1: locate the real task-brief file, quote `buckleyLeverettProblem`'s brief in full.
- Agent 2: locate the stop-hook implementation + its exact feedback template, and a real instance in
  `events.jsonl` under the S-enabled cells.

### Prior context gathered from the tex (for the searchers)

- `tex:139` describes the S component, VERBATIM:
  > `\item \textbf{S: Stop-hook self-verification.} A termination hook checks the agent's output before CC is allowed to stop. It scans \texttt{/workspace/inputs/} for parseable XML, runs \texttt{xmllint --schema} against the canonical \texttt{.xsd}, and either allows termination or returns structured repair feedback. A per-task retry counter bounds re-prompts, with default 2 retries. Unlike agent-callable tools, this component is mandatory whenever enabled: every attempted termination passes through the hook.`
- "structured repair feedback" occurs at `tex:139` in the submitted version. It is **never exemplified
  anywhere in the paper** — no figure, no listing, no appendix. Confirmed by full read of all 746 lines.
- "brief" / "briefs" in the submitted version: `tex:88`, `:111` ("task briefs often under-specify
  choices that experts fill in with domain-conventional defaults"), `:230` ("Our headline benchmark
  hands the agent a fully detailed brief"; "Briefs are tier-rewritten by deepseek-v4-pro"), `:594`.
  **Also never exemplified** — no brief text is reproduced anywhere in the paper. kEdh's complaint #3
  is factually correct on both counts.
- S-enabled cells per `F_FACTORS`: **F2 (S+M), F3 (R+S), F6 (S+X), F7 (R+S+X+M)**, plus the added
  S+X+M cell and SE. Note the parent's brief said "F2|F6|F8|SE" — **F3 and F7 are also S-enabled** and
  `autocamp_F8` is not in `F_FACTORS` at all (the paper refers to F8/F11 at `tex:547` without ever
  defining the F-numbering; see F5 #11).

---

## Could not find / open questions (running list)

1. Whether `writing/arxiv/` was actually posted to arXiv — no arXiv ID or posting confirmation on
   disk. Treated as posted (conservative).
2. `autocamp_F8` / `autocamp_F11` — referenced in the submitted tex at `:547` but absent from
   `F_FACTORS` in `scripts/analyze_autocamp.py`. The F-numbering scheme is never defined in the paper.

---

## F4 — Buckley–Leverett gloss

### First use vs gloss location (submitted tex)

- **First use: `tex:167`** (§4 Evaluation setup, Benchmark paragraph) — VERBATIM clause:
  > `\textbf{val} contains 17 in-distribution GEOS advanced-example and tutorial tasks spanning poromechanics, hydraulic fracture, thermal coupling, and wellbore modeling (e.g., \texttt{ExampleDPWellbore}, \texttt{ExampleMandel}, \texttt{buckleyLeverettProblem}).`
  No gloss. It is presented as one of three bare task identifiers.

- **Only gloss: `tex:237`** (§5.5 Human baseline) — VERBATIM parenthetical:
  > `attempted \texttt{buckleyLeverettProblem} (1D immiscible CO$_2$/brine displacement, the easy end of our bench)`

- **Gap: 70 source lines (`:167` → `:237`), and the gloss is buried in a parenthetical inside the
  human-baseline subsection.** Confirmed: `grep -n "buckleyLeverett\|Buckley"` returns
  `:167, :237, :239, :242, :611, :632, :642, :647, :650, :653, :656, :663, :733, :737` — `:167` is the
  first, `:237` is the first with any explanation, and every earlier-in-the-paper mention has none.
  The term also carries the paper's App. `app:geos-example` (`:644-666`) and App. `app:case-study`
  (`:730-737`) as the running example, so the reader meets it repeatedly before it is explained.

### Candidate one-sentence glosses (physics only — main thread picks + polishes)

**(a) Analogy-first, shortest.**
> Buckley–Leverett is the reservoir-simulation equivalent of a textbook sanity check: a one-dimensional
> problem in which injected CO2 pushes the brine already sitting in a rock column ahead of it, standard
> precisely because the resulting displacement front has a known closed-form solution.

**(b) Mechanism-first.**
> The Buckley–Leverett problem is the classical benchmark for immiscible two-phase flow in porous
> media — inject one fluid into a rock column saturated with another and a sharp saturation front
> travels down the column at a speed set by the two fluids' relative permeabilities — and it is the
> simplest well-posed task in our benchmark.

**(c) Task-shaped, ties to why it is easy.**
> `buckleyLeverettProblem` asks the agent to configure a 1D simulation of CO2 displacing brine through
> porous rock; because the physics collapses to a single scalar conservation law with an analytical
> shock solution, the deck needs only a handful of GEOS blocks, which is why we treat it as the easy
> end of the bench.

**(d) Concrete + anchors the two-file structure the rest of the paper leans on.**
> Buckley–Leverett (1942) is the standard analytical test for one fluid displacing another through
> porous rock — here CO2 injected into a brine-filled 1D column — and in GEOS it is a compact
> two-file, 233-line deck, which makes it both our running example and the one task we could put in
> front of human participants inside an hour.

Numbers usable in any gloss, all sourced: two XML files, "the original is 172 + 61 lines" (`tex:647`);
"1D immiscible CO2/brine displacement, the easy end of our bench" (`tex:237`); vanilla CC deck-level
TreeSim 0.751 ± 0.016, agent ~7 min (`tex:239`, `tex:253`).

---

## F5 — Ranked camera-ready clarity-fix inventory (submitted tex line numbers)

Ranked by (kEdh named it explicitly) × (impact on a general NeurIPS reader). Top 12.

1. **`:139` / `:88` / `:111` / `:230` — "structured repair feedback" and "brief" are named but *never
   exemplified anywhere in 746 lines.*** No figure, listing, or appendix shows either. (kEdh #3;
   verified by full read + grep of both tex versions.) → Commit: add a boxed real hook message and a
   real task brief.
2. **`:67` → `:111` — "deck" used 11 times (`:67`×2, `:76`, `:82`×3, `:86`×2, `:88`, `:91`) before §3
   defines it at `:111`.** (kEdh #2, verbatim complaint.) → Commit: one-clause gloss at the abstract's
   first use.
3. **`:67`, `:84`, `:157` — "Resolution-IV $2^{4-1}$ factorial" lands in the *abstract* with no
   scaffolding; the only explanation is at `:157` and it never says what resolution IV means or what
   the aliases are.** (kEdh #1.) → Commit: plain-language framing at first use + an explicit alias
   table at `:157`.
4. **`:169` — "Headline numbers average TreeSim under *failures-as-zero*: parse errors, timeouts,
   `failed_no_outputs`, and missing XML outputs all score 0, so systems are not rewarded for unscorable
   files."** `failures-as-zero` is coined here; `failed_no_outputs` is a raw internal runner status
   string explained nowhere. (kEdh #2, quoted verbatim.) → Commit: rewrite in plain English with the
   *why* (already drafted in the arXiv line — paraphrase, do not paste).
5. **`:86` — "The number of strictly perfect decks does not increase under any adapter."** The
   threshold (TreeSim ≥ 0.999) appears only 130 lines later at `:216`. (kEdh #2, quoted verbatim.)
   → Commit: inline the threshold and the counts at first use.
6. **`:167` → `:237` — `buckleyLeverettProblem` used bare at `:167`; sole gloss is a parenthetical at
   `:237` inside §5.5.** (kEdh #1.) → Commit: gloss at `:167`.
7. **`:169` + `:91` — TreeSim, listed as contribution (i) at `:91`, has no reproducible definition.**
   Its entire specification is the clause "a tree-edit similarity in $[0,1]$ decomposed by the ten
   canonical GEOS sections" (`:169`). No algorithm, no citation, no aggregation/weighting rule, no
   normalization — nowhere in the paper. This is the single largest blocker to kEdh's *"practitioners
   will struggle to ... apply its findings in practice."* → Commit: formal definition + worked
   micro-example + release the scorer.
8. **`:67`, `:86` — "cell" (design-of-experiments jargon) appears in the abstract ("the best
   hand-designed cell") and intro before it is defined at `:157`.** → Commit: say "configuration" until
   §3.2.
9. **`:84` / `:161` / `:167` / `:303` — one split, four names.** "17-task validation set" (`:84`),
   "17 validation-selection tasks" (`:161`), "**val**" (`:167`); and the 10 evaluation tasks are called
   an "**ICL pool**" at `:303` — ICL never expanded — while being the identical 10 tasks listed as
   *held-out-eval* rows at `:384-393` (verified name-by-name). → Commit: one name each + a splits table.
10. **`:157` — the generator is written "$\mathrm{D}{=}\mathrm{ABC}$" without ever stating that
    A,B,C,D = R,S,X,M.** A reader cannot reconstruct the design from the paper. → Commit: write it as
    M = R⊕S⊕X and give the defining relation I = RSXM.
11. **`:104` → `:131` — "MCP" used unexpanded at `:104` ("an MCP tool exposing embedding-retrievable
    items"), expanded only at `:131`.** → Commit: expand at first use.
12. **`:547` — the F-cell numbering ("F2, F4, F6, F8, F11") is used in the Future-work appendix and
    defined nowhere in the paper**; `autocamp_F8`/`F11` are not even present in `F_FACTORS`
    (`scripts/analyze_autocamp.py:397-406`), so the labels are unresolvable even against the code.
    → Commit: replace F-numbers with factor names.

### Overflow (verified, lower impact — use only if the response has room)

13. `:312` / `:330` / `:562` / `:693` — `m1u`, an internal artifact identifier, appears in three table
    captions and the appendix with no expansion.
14. `:104` "primer" vs `:143` "memory cheatsheet" vs `:149` "`PRIMER.md`" vs `:693`
    "`memory_primer_m1u.md`" — four names, relationship never stated.
15. `:237` "contamination block" used in §5.5 but only defined at `:611` (appendix).
16. `:272` "native-plugin-prefix bug" cited in Limitations before it is explained at `:444`.
17. `:216` / `:281` "harm-reduction regime" vs "correctness regime" — coined, never defined.
18. `:47` `\newcommand{\sys}{\textsc{GeoAgent}\xspace}` is defined and never used anywhere in the
    document (dead macro; invisible to readers, cosmetic only).

### Caution on the one artifact the paper DOES show

`writing/neurips/assets/trajectory_buckleyleverett_xm.txt` (included at `tex:735`, App.
`app:case-study`) is an **editorialized reconstruction, not a raw `events.jsonl` excerpt** — it uses
`[Plan]`/`[Tool]`/`[Edit]`/`[Score]` annotations and parenthetical authorial commentary. Its synthetic
xmllint return (lines 38-41) is also internally odd: it reports `'scale' must be a numeric value` for
`scale='1e7'`, which *is* numeric. Do **not** cite this file as a verbatim log in the response; if the
response needs a concrete artifact, use a genuine one from the F3 search below.

---

## F3a — THE REAL TASK BRIEF (verified independently)

### What a "brief" is on disk

There is **no** `brief.md` / `brief.txt` / `task.md` / `prompt.md` / `spec.json`, and no JSON/YAML field
named `brief`. A brief is always a plain-text file named **`instructions.txt`**, one per task, at
`<spec_dir>/<TaskName>/instructions.txt`.

Loader (verified by direct read of `/home/matt/sci/repo3/src/runner/prompts/__init__.py:65-79`):

```python
def load_task_instructions(task_dir: Path) -> str:
    path = task_dir / "instructions.txt"
    if not path.exists():
        raise FileNotFoundError(f"instructions.txt not found in {task_dir}")
    return path.read_text()


def build_prompt(agents_context: str, task_instructions: str) -> str:
    return (
        f"{agents_context}\n\n"
        "--- BEGIN SIMULATION SPECIFICATION ---\n"
        f"{task_instructions.strip()}\n"
        "--- END SIMULATION SPECIFICATION ---"
    )
```

So the agent receives the brief **verbatim**, wrapped in
`--- BEGIN SIMULATION SPECIFICATION ---` / `--- END SIMULATION SPECIFICATION ---`, appended after
`run/AGENTS.md`. Other consumers: `scripts/openhands_eval.py:612`,
`scripts/harnessless_eval.py:203,263`, `scripts/relax_specs.py:423,465`,
`src/runner/orchestrator.py:213-228` (mounts the same file as the simulated supervisor's oracle at
`/supervisor/spec.md`).

Canonical spec dir used by every real campaign launcher (`scripts/launch_autocamp_phase1.sh:27`,
`launch_autocamp_phase2.sh:55`, `launch_autocamp_v4.sh:59`, `launch_interactive_autonomy.sh:38,86`):
**`experiments_test36_template/`**.

**v1 vs v2 warning (matters for what we quote).** Two generations of brief exist:
- **v2 (current, all paper numbers)** — `experiments_test36_template/` (36 tasks),
  `experiments_from_mined_specs/` (46), `experiments_from_mined_specs_full/experiments/` (46).
  buckleyLeverett = **3672 bytes**, all three byte-identical.
- **v1 (older, pre-2026-04-21)** — `experiments/` (46), `experiments_testset_template/` (20).
  buckleyLeverett = 5712 bytes and **names GEOS XML elements explicitly** (`InternalMesh`, `C3D8`,
  `CompositionalMultiphaseFVM`, `DeadOilFluid`, `BrooksCoreyRelativePermeability`, `PackCollection`).
  **Do NOT quote v1** — it would undercut the framing that briefs are stated in domain language, not
  GEOS vocabulary. The tex already states all numbers use v2 (`tex:306`).

Confirmed v2 is what agents actually received: the run log
`.../dsv4/autocamp_F0/autocamp_F0_s1/buckleyLeverettProblem/events.jsonl` contains `0.00202683` and
`1000 cells`, values present only in the v2 text.

### Path (canonical)

```
/data/shared/geophysics_agent_data/data/eval/experiments_test36_template/buckleyLeverettProblem/instructions.txt
```

Independently verified by me: **3672 bytes, 569 words, 36 lines**,
`md5 = 7c34ddc9503378cabd5b8da86515e920`, identical md5 to
`.../experiments_from_mined_specs/buckleyLeverettProblem/instructions.txt`.

### Trimmed excerpts — every non-`[...]` fragment machine-checked as a verbatim substring of the file

**Option A — 331 chars. Best structural showcase (intent → domain-language physics → file contract).**
```
I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. [...]
**Material and Fluid Properties**
- Permeability is 9.0e-13 m² in all directions.
- The reference porosity is 0.2 at a reference pressure of 10 MPa. [...]
[...]
XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml
```

**Option B — 316 chars. Most compact; single flowing line.**
```
I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. [...] Discretize the domain with 1000 cells in the x-direction [...] Use a Brooks-Corey relative permeability model for the gas and water phases. [...]
XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml
```

**Option C — 387 chars. Keeps the full opening sentence, which is the most quotable part.**
```
I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions.
**Physical Problem and Domain Geometry** [...] create a hexahedral mesh of length 0.1 m [...]
XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml
```

Two facts worth stating alongside whichever excerpt is used:
- Every v2 brief ends with the line `XML files to create: <filenames>` — a clean, quotable convention.
- The brief is written entirely in **domain language** (permeability, porosity, Brooks–Corey exponents,
  Newton tolerance); it never names a GEOS XML element. That is precisely why the task is a translation
  problem and why grounding helps. Good rebuttal framing.

### Brief-length statistics (for "representative")

| Spec dir (under `/data/shared/geophysics_agent_data/data/eval/`) | n | min B | max B | mean | median | gen |
|---|---|---|---|---|---|---|
| `experiments_test36_template/` **(campaign default)** | 36 | 2219 (`triaxialDriverExample`) | 6604 (`ExampleThermalLeakyWell`) | 4569 | 4222 | v2 |
| `experiments_from_mined_specs/` | 46 | 2219 | 6723 (`ExampleIsothermalHystInjection`) | 4711 | 4634 | v2 |
| `experiments/` | 46 | 4080 | 7946 (`ExampleSPE11b`) | 5611 | 5440 | v1 |
| `experiments_testset_template/` | 20 | 4080 | 6509 | 5251 | 5144 | v1 |

buckleyLeverett at 3672 B is the 9th shortest of 36 — below the 4222 B median, consistent with it being
the easy end of the bench. Usable one-liner for the response: **"briefs run 2.2k–6.7k characters
(median ≈4.2k); buckleyLeverettProblem is 3.7k."**

Shortest brief overall (if a smaller example is wanted):
`/data/shared/geophysics_agent_data/data/eval/experiments_test36_template/triaxialDriverExample/instructions.txt`
— 2219 bytes, 322 words.

### F3a not-founds

- Per-task run dirs under `autocamp_2026-05-01/dsv4/<cell>/<cell>_s<N>/<task>/` contain **no persisted
  copy of the brief or of the assembled prompt** (only `acpx_output.json`, `events.jsonl`, `stdout.txt`,
  `stderr.txt`, `status.json`, `exit_code.txt`, `tool_calls.json`, `eval_metadata.json`, `inputs/`,
  `outputs/`, `.claude_home/`). `events.jsonl` does not contain the
  `--- BEGIN SIMULATION SPECIFICATION ---` marker. The exact delivered prompt must be reconstructed via
  `build_prompt(load_agents_md(), load_task_instructions(...))`.
- `experiments_relaxed_medium/` and `experiments_relaxed_hard/` **do not exist on disk** — the
  Medium/Hard relaxed briefs described at `tex:230` and `tex:575` are referenced only by
  `scripts/relax_specs.py` and two design docs. **This is a live rebuttal risk for a different thread:
  the tex at `tex:575` claims "The 16 rewrites are committed and frozen before any run starts," but
  the output dirs are not present at the documented path.** Flagging; not my item.
- `experiments_gt/` has 46 task dirs but no `instructions.txt` (ground-truth XML only).

---

## Correction to F5 item 12 (F-cell numbering)

`autocamp_F8/` and `autocamp_F11/` **do exist** on disk
(`/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/` contains F0, F1, F2, F3, F4,
F5, F6, F7, F8, F11, SE, p_contract, p_method, v4). They are simply absent from `F_FACTORS`, which only
covers the 8 factorial corners.

Resolved from `/home/matt/sci/repo3/scripts/paper_sim_cost.py:16-17`, verbatim:
```python
    "S+X (F6)": "autocamp_F6", "R+S+X+M (F7)": "autocamp_F7", "S+X+M (F8)": "autocamp_F8",
    "SE-prose (F11)": "autocamp_F11", "SE": "autocamp_SE",
```
So **F8 = S+X+M** and **F11 = SE-prose**. Cross-checked against `docs/XN-021_bottleneck-analysis-icl10.md`
(F8 held-out-eval TreeSim mean 0.7827 ≈ paper's S+X+M 0.783 at `tex:200`; F11 0.7749 ≈ paper's SE-prose
0.775 at `tex:201`) — mapping confirmed.

Revised F5 #12: the F-numbering **is** resolvable from the code but **not from the paper**. `tex:547`
("F2, F4, F6, F8, F11") is unresolvable for any reader. Also note the numbering is non-contiguous
(F8, F11, no F9/F10), which will read as an error to a careful reviewer. → Commit: replace F-labels
with factor names throughout, or add the mapping to Table 5 (`app:cells`).

---

## F3b — THE REAL STRUCTURED REPAIR FEEDBACK (found; real instances exist)

### How I found it (route the search agent's brief did not anticipate)

Every S-enabled task dir contains two files the brief did not mention:
- `claude_settings.json` — the actual Stop-hook wiring
- `.verify_hook_events.jsonl` — a **hidden** per-invocation decision log written by the hook itself

Example (`/data/shared/.../dsv4/autocamp_F6/autocamp_F6_s1/AdvancedExampleCasedContactThermoElasticWellbore/claude_settings.json`), verbatim:
```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "command": "python3 /plugins/repo3/hooks/verify_outputs.py",
                     "timeout": 30, "type": "command" } ],
        "matcher": "" }
    ]
  }
}
```

### (A) The hook implementation and its exact templates

**`/home/matt/sci/repo3/plugin/hooks/verify_outputs.py`** (391 lines; container path
`/plugins/repo3/hooks/verify_outputs.py`). Copies also at `plugin_orchestrator/hooks/` and
`plugin_evolving/v{0,1,2,3,4}/hooks/`.

Mechanics: reads the Stop-hook JSON from stdin, lists `*.xml` under `GEOS_HOOK_INPUTS_DIR`
(default `/workspace/inputs`), and emits `{"decision": "block", "reason": "..."}` on stdout
(`_block`, lines 137-152) or `{"continue": true, "suppressOutput": true}` (`_allow_stop`, lines
120-134). Retry budget `GEOS_HOOK_MAX_RETRIES` default **2**, counter at `<parent>/.verify_retry_count`.

**Four block templates. Verbatim from source:**

1. **`no_xml`** (lines 300-308):
   > `"Stop blocked by verify_outputs hook: no .xml files found under " f"{inputs_dir}. This is a required output of the task. Produce the " "requested GEOS XML files now using the Write tool (write under " f"{inputs_dir}/) and then end your turn."`

2. **`parse_error`** (lines 322-329):
   > `f"Stop blocked by verify_outputs hook: XML parse error in {rel}: " f"{detail}.{hint} Open the file, fix the syntax, then end your turn."`

3. **`schema_error`** (lines 343-353) — **this is the "structured repair feedback" of `tex:139`:**
   > `"Stop blocked by verify_outputs hook: one or more XML files " f"under {inputs_dir} fail GEOS schema validation. " f"Schema: {schema_path}. Errors:\n\n" f"{feedback}\n\n" "Fix the offending element/attribute names against the schema " "(do NOT guess again — `xmllint` lists expected alternatives " "for unexpected-element errors and required attribute names " "for missing-attribute errors). Re-validate locally with\n" f"  xmllint --schema {schema_path} --noout <file>.xml\n" "before ending your turn."`

4. **`self_reflect`** (lines 371-384) — **off by default** (`GEOS_HOOK_SELF_REFLECT`), never used in
   any campaign. Do not present it as part of the system.

`{feedback}` is built by `_xmllint_validate` (lines 200-265): runs
`xmllint --schema <schema> --noout <file>` per file, strips the `fails to validate` summary line and
the absolute path prefix, caps at `MAX_ERRORS_PER_FILE = 8` and `MAX_FILES_REPORTED = 4` (lines 46-47),
and formats as `- <relpath>:\n  <err>\n  <err>`.

Defaults: `DEFAULT_SCHEMA_PATH = /geos_lib/src/coreComponents/schema/schema.xsd` (line 45).
Gating: schema validation runs only when `GEOS_HOOK_XMLLINT` is truthy (line 331) — consistent with
`tex:312` ("S=Stop-hook (parse-check, with xmllint when X is also on)"). So `schema_error` blocks can
only occur in S∧X cells.

### (B) A REAL delivered instance — FOUND, verbatim

**Path:**
```
/data/shared/geophysics_agent_data/data/eval/se_icl_2026-04-30/abl_c6_xmllint_hook/c6_icl_s2/ExampleVerticalPoroElastoPlasticWellbore/events.jsonl
```
Provenance verified from the sibling `eval_metadata.json`: `"claude_model": "deepseek-v4-flash"`
(**the paper's headline backbone**, `tex:171`), `"agent": "abl_c6_xmllint_hook"`, `"run_name":
"c6_icl_s2"`, `"runner": "claude_native"`, started `2026-05-01T07:30:16Z`. Task
`ExampleVerticalPoroElastoPlasticWellbore` **is one of the paper's 10 held-out-eval tasks** (`tex:303`,
`tex:390`).

This single trajectory contains **both** block types, in order. Both arrive as
`{"type":"user", ..., "isSynthetic":true}` events, and Claude Code prefixes the hook's `reason` with
`Stop hook feedback:`.

**Instance 1 — `parse_error`, 207 chars. Short enough to quote IN FULL with no ellipses:**
```
Stop hook feedback:
Stop blocked by verify_outputs hook: XML parse error in wellborePoromechanics.xml: not well-formed (invalid token): line 219, column 11. Open the file, fix the syntax, then end your turn.
```
(hook log records `parse_error`, `retries_so_far: 1`, timestamp `2026-05-01T07:35:42.975Z`)

**Instance 2 — `schema_error`, 784 chars in full. This is the "structured repair feedback".**
Full text (for the record; trim before use):
```
Stop hook feedback:
Stop blocked by verify_outputs hook: one or more XML files under /workspace/inputs fail GEOS schema validation. Schema: /geos_lib/src/coreComponents/schema/schema.xsd. Errors:

- wellborePoromechanics.xml:
  wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed.

Fix the offending element/attribute names against the schema (do NOT guess again — `xmllint` lists expected alternatives for unexpected-element errors and required attribute names for missing-attribute errors). Re-validate locally with
  xmllint --schema /geos_lib/src/coreComponents/schema/schema.xsd --noout <file>.xml
before ending your turn.
```
(hook log records `schema_error`, `retries_so_far: 2`, timestamp `2026-05-01T07:36:06.412Z`)

### Trimmed to ≤400 chars — every non-`[...]` fragment machine-checked verbatim

**Option A2 — 386 chars. RECOMMENDED: correct model (deepseek-v4-flash), paper held-out-eval task.**
```
Stop hook feedback:
Stop blocked by verify_outputs hook: [...] fail GEOS schema validation. [...]
[...] wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed.
[...] Fix the offending element/attribute names against the schema [...]
```
Narrative bonus: `porousMaterialNames` is a **renamed/stale GEOS attribute** — this is exactly
difficulty (ii) at `tex:111` ("documentation and examples may reflect older interface versions"). The
message shows the hook catching a stale-interface error the model learned from old examples.

**Option B3 — 371 chars. Pedagogically clearest (schema enumerates the legal alternatives), and it is
the paper's running example — BUT wrong backbone.**
```
Stop hook feedback:
Stop blocked by verify_outputs hook: [...] fail GEOS schema validation. [...]
[...] buckleyLeverett_base.xml:80: element HDF5: Schemas validity error : Element 'HDF5': This element is not expected. Expected is one of ( Blueprint, ChomboIO, MemoryStats, Python, Restart, Silo, TimeHistory, VTK ).
[...] Re-validate locally with
  xmllint --schema [...]
```
Source: `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/xmodel/autocamp_xmodel_best/openai_gpt-oss-120b_best_s1/buckleyLeverettProblem/events.jsonl`
(full delivered message 1143 chars). **CAVEAT: backbone is `openai/gpt-oss-120b`, which does not
appear anywhere in the paper.** If the response says "here is a real message from our runs" this is
still true, but a reviewer who later checks the artifact will find a model the paper never mentions.
**Prefer A2.** Use B3 only if the main thread decides the pedagogical clarity is worth footnoting the
model.

**Instance 1 (parse_error, 207 chars) is the safest single quote of all** — full, verbatim, zero
ellipses, correct model, paper task. Consider pairing it with A2 to show both the floor
(is it parseable?) and the structured tier (does it validate against the schema?).

### Campaign-wide hook statistics (all machine-counted from `.verify_hook_events.jsonl`)

Across 9 campaign roots, **1,635 hook invocations / 251 block events**:

| decision | reason_category | count |
|---|---|---|
| allow | `xml_clean` | 1571 |
| **block** | **`parse_error`** | **88** |
| **block** | **`no_xml`** | **83** |
| **block** | **`schema_error`** | **80** |
| allow | `no_xml_max_retries` | 40 |
| allow | `schema_error_max_retries` | 31 |
| allow | `parse_error_max_retries` | 13 |

`self_reflect`: **0** occurrences (confirmed off everywhere).

Per root: `autocamp_2026-05-01` 529 files (71 no_xml, 33 schema_error, 5 parse_error blocks — **all in
the `xmodel/` sub-campaign**); `se_icl_2026-04-30` 90 files (21 schema_error, 11 parse_error);
`dsv4_ablation_2026-04-29` 585 files (15 parse_error, 7 schema_error);
`c6prime_c1redux_2026-05-01` 81 files (11 schema_error, 3 parse_error);
`claude_code_repo3_plugin_gmem` 51 files (29 parse_error, 4 no_xml);
`claude_code_repo3_plugin` 59 files (22 parse_error, 6 no_xml);
`cross_model_2026-05-03` 33 files (6 schema_error, 2 no_xml);
`self_evolving_2026-04-30` 20 files (2 schema_error, 1 parse_error);
`autocamp_followup_2026-05-02` 177 files (2 parse_error).

### FINDING TO ESCALATE — not my item, but the main thread should know

**In the headline `dsv4` factorial campaign the stop hook never blocked once.** All 407 hook logs under
`/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/` record **410 events, 100%
`allow` / `xml_clean`, zero blocks.** Per-cell (each 51 files = 17 val tasks × 3 seeds):

```
autocamp_F2  51 files  {('allow','xml_clean'): 52}      autocamp_F7  51  {('allow','xml_clean'): 51}
autocamp_F3  51 files  {('allow','xml_clean'): 51}      autocamp_F8  51  {('allow','xml_clean'): 51}
autocamp_F6  51 files  {('allow','xml_clean'): 53}      autocamp_F11 51  {('allow','xml_clean'): 51}
autocamp_SE  51 files  {('allow','xml_clean'): 51}      autocamp_v4  50  {('allow','xml_clean'): 50}
```
Wiring is correct — the hook log exists **only** in S-enabled cells (F2, F3, F6, F7, F8, F11, SE, v4)
and is absent from S-off cells (F0, F1, F4, F5), exactly as designed. So this is a real behavioural
result, not a plumbing bug: on the **val** split, deepseek-v4-flash never once ended a turn with a
missing, unparseable, or schema-invalid deck.

Two consequences the main thread should weigh:
1. It is **consistent** with the paper's own val finding that S has essentially zero main effect
   (`tex:414`, S = $-0.003$; `tex:207`, "S ... within $\pm 0.007$"). The hook cannot help if it never
   fires. This is a *supporting* explanation the rebuttal could use.
2. But `tex:225`/`tex:268` attribute the OpenFOAM and cross-simulator reliability story to "forced
   end-of-turn verification," and `tex:211` attributes the GEOS σ reduction to preventing
   "catastrophic seed-level failures." **I did not locate the held-out-eval (10-task × 3-seed) dsv4
   hook logs** — the 51-file-per-cell counts are val only. Whether the hook fired on held-out-eval is
   unresolved and is the load-bearing question. Someone should check before the response claims the
   hook mechanism operated on the hard tail.

### F3b not-founds

- The **held-out-eval dsv4 hook logs**. Every dsv4 cell dir has exactly 51 hook logs = 17×3 = val only.
  I did not find a dsv4 held-out-eval (10×3=30) run tree carrying `.verify_hook_events.jsonl`.
  `se_icl_2026-04-30` looks like the ICL/held-out campaign (and *does* contain blocks) but its cells are
  named `abl_c6_xmllint_hook` / `abl_se_round`, not `autocamp_F*`, so I could not confirm the mapping to
  the paper's held-out-eval columns. Flagging as unresolved.
- No `schema_error` or any block instance from a **paper F-cell name** (`autocamp_F6`/`F7`/`F8`/`SE`).
  Every real instance I found is from a differently-named ablation cell (`abl_c6_xmllint_hook`,
  `abl_se_round`, `abl_c10_xmllint_hook_mem`) or from the `xmodel` cross-model sub-campaign. The
  message text is template-generated and therefore identical, but we cannot say "from cell S+X".
  Recommended phrasing: "from a stop-hook-enabled run on `deepseek-v4-flash`."
- The block `reason` string itself is **not** stored in `.verify_hook_events.jsonl` (only a `detail`
  field truncated to 500 chars, `verify_outputs.py:357`). The full delivered message survives only in
  `events.jsonl` as an `isSynthetic` user turn. Both were cross-checked and agree.

### Response-budget note

kEdh's response has 7,000 characters. Brief excerpt (~331) + hook message (~386) = **717 chars ≈ 10%**
of the budget for both of kEdh's item-3 artifacts. Adding the 207-char parse_error message brings it to
~924 chars ≈ 13%. Affordable.

---

## RESOLUTION of the escalated finding — the hook DID fire on the hard tail

`/data/shared/geophysics_agent_data/data/eval/se_icl_2026-04-30/` **is** the held-out-eval (ICL10)
campaign: 3 cell-variants × 3 seeds × **10 tasks** each (90 task runs), backbone confirmed
`deepseek-v4-flash` from `eval_metadata.json`. Cells are `abl_c6_xmllint_hook` (C6 = xmllint hook,
the S+X-family cell) and `abl_se_round` at `se_icl_v0_*` and `se_icl_v3_*` (v3 = the SE variant).

**32 block events across 9 cell-seeds on the held-out-eval split:**

| cell-seed | logs | events | blocks | breakdown |
|---|---|---|---|---|
| `abl_c6_xmllint_hook/c6_icl_s1` | 10 | 15 | **4** | 2 parse_error, 2 schema_error |
| `abl_c6_xmllint_hook/c6_icl_s2` | 10 | 16 | **6** | 4 parse_error, 2 schema_error |
| `abl_c6_xmllint_hook/c6_icl_s3` | 10 | 12 | **2** | 2 schema_error |
| `abl_se_round/se_icl_v0_s1` | 10 | 12 | **2** | 2 schema_error |
| `abl_se_round/se_icl_v0_s2` | 10 | 12 | **2** | 2 schema_error |
| `abl_se_round/se_icl_v0_s3` | 10 | 14 | **4** | 3 schema_error, 1 parse_error |
| `abl_se_round/se_icl_v3_s1` | 10 | 13 | **3** | 1 parse_error, 2 schema_error |
| `abl_se_round/se_icl_v3_s2` | 10 | 14 | **4** | 1 parse_error, 3 schema_error |
| `abl_se_round/se_icl_v3_s3` | 10 | 15 | **5** | 2 parse_error, 3 schema_error |

**This is a clean, quantitative confirmation of the paper's own mechanism claim, and it is strong
rebuttal material in its own right (relevant to gep1's S/X question as well as kEdh's item 3):**

- On **val** (17 tasks × 3 seeds, 8 S-enabled cells, 410 hook invocations): **0 blocks.** The hook never
  fired, so S could not help — which is exactly why `tex:414` measures the S main effect at $-0.003$ and
  `tex:207` puts S "within $\pm 0.007$."
- On **held-out-eval** (10 tasks × 3 seeds): **32 blocks over 123 invocations (~26%).** The hook fires
  on roughly a quarter of turns, which is precisely the hard tail where `tex:209`/`tex:211` locate the
  $+0.069$ mean lift and the ~40× variance reduction.

One sentence the main thread can use, fully sourced: *"the stop hook blocked termination 0 times in 410
invocations on the validation split but 32 times in 123 invocations on the harder held-out split — the
component is inert exactly where we report it has no effect, and active exactly where we report the
reliability gain."*

Caveat for honest phrasing: the held-out-eval cell directories are named `abl_c6_xmllint_hook` /
`abl_se_round`, not `autocamp_F6` / `autocamp_SE`. The mapping (C6 → the S+X-family cell, `se_icl_v3` →
SE) is inferred from naming and from the model/task/seed shape, **not** confirmed against a config
manifest. Say "a stop-hook-enabled cell on deepseek-v4-flash," not "cell S+X," unless another thread
confirms the mapping.

---

## Final NOT-FOUND list

1. **Whether `writing/arxiv/` was actually posted to arXiv.** No arXiv ID or posting confirmation
   anywhere on disk; `arxiv_v1.pdf`, `arxiv_upload.zip`, `arxiv_upload_jun8.zip` and
   `ARXIV_INSTRUCTIONS.md` show a package was built. **Treated as posted** — paraphrase, never paste.
2. **A block instance from a cell literally named `autocamp_F6` / `F7` / `F8` / `SE`.** All real
   instances come from `abl_c6_xmllint_hook`, `abl_se_round`, `abl_c10_xmllint_hook_mem`, or the
   `xmodel` cross-model sub-campaign. Message text is template-generated and identical; only the cell
   label cannot be asserted.
3. **No persisted copy of the brief or the assembled prompt inside any per-task run dir.** Reconstructable
   only via `build_prompt(load_agents_md(), load_task_instructions(...))`.
4. **`experiments_relaxed_medium/` and `experiments_relaxed_hard/` do not exist on disk**, though
   `tex:575` states "The 16 rewrites are committed and frozen before any run starts." Escalated for a
   different thread; not an F-item.
5. **No example of a brief or of repair feedback anywhere in either tex version** — confirmed by full
   read of the submitted 746 lines and targeted reads plus greps of the arXiv 939 lines. kEdh's item 3
   is factually correct.
6. The `self_reflect` block template exists in code (`verify_outputs.py:371-384`) but fired **0 times**
   in every campaign — do not present it as part of the system.

---

## Corroboration of the val-split zero-block finding (two independent search methods)

The zero-block result on the dsv4 val split was reached twice, by different traversals, with identical
numbers:

1. **Depth-bounded glob** — `glob("<dsv4>/*/*/*/.verify_hook_events.jsonl")`:
   407 files, 410 events, `{('allow','xml_clean'): 410}`, 0 blocks.
2. **Full recursive `find`** — `find <dsv4> -name ".verify_hook_events.jsonl"` (traverses arbitrary
   depth, including `.claude_home/` and `.uv_cache/` subtrees the glob would miss):
   407 files, 410 events, `{('allow','xml_clean'): 410}`, 0 blocks.
   `grep -rl '"decision": "block"' <dsv4> --include=".verify_hook_events.jsonl"` returned **no files**.

So no block events are hidden at deeper nesting levels, and the depth-3 glob was not undercounting.
The val-split finding (hook never fired) and the held-out-eval finding (32 blocks / 123 invocations)
both stand as reported.

---

## Second search agent returned — corroboration + two corrections

A parallel search agent independently reproduced the hook findings. Its global counts match mine
exactly (1571 `allow/xml_clean`, 88 `parse_error`, 83 `no_xml`, 80 `schema_error`), and it confirms
**zero blocks in all 14 dsv4 cells** by a third method (per-cell `grep -lF '"decision": "block"'`).
The zero-block result is now **triple-confirmed** (depth-3 glob, recursive `find`, per-cell grep).

It also added the hook-registration source (`plugin/hooks/hooks.json:4-15` for Stop; `:16-27` for a
separate `PostToolUse` hook `verify_xml_post_write.py`) and confirmed the schema-error template is
byte-identical across all seven copies of `verify_outputs.py`.

### CORRECTION 1 — the recommended instance (A2) DID complete a successful repair

I had not checked the outcome. The hook ledger at
`.../se_icl_2026-04-30/abl_c6_xmllint_hook/c6_icl_s2/ExampleVerticalPoroElastoPlasticWellbore/.verify_hook_events.jsonl`
is exactly three lines:
```
{"timestamp": "2026-05-01T07:35:42.958734+00:00", "decision": "block", "reason_category": "parse_error", "retries_so_far": 1, ...}
{"timestamp": "2026-05-01T07:36:06.404414+00:00", "decision": "block", "reason_category": "schema_error", "retries_so_far": 2, ...}
{"timestamp": "2026-05-01T07:36:27.471957+00:00", "decision": "allow", "reason_category": "xml_clean", "retries_so_far": 0, "detail": ""}
```
So A2 is a **complete two-stage repair loop that succeeded in 45 seconds** on `deepseek-v4-flash`, on a
paper held-out-eval task: unparseable → fixed → schema-invalid → fixed → clean stop. This is strictly
the best artifact we have and it strengthens the recommendation. **A2 stands as the pick.**

Conversely, **option B3 (buckleyLeverett / gpt-oss-120b) FAILED to repair** — its ledger is
block(1) → block(2) → `allow / schema_error_max_retries` (retries 3). Do **not** present B3 as showing
the hook working; it shows the retry budget being exhausted.

### CORRECTION 2 — a third instance, in a cell literally named `autocamp_SE`

`/data/shared/geophysics_agent_data/data/eval/cross_model_2026-05-03/google_gemini-3-flash-preview/autocamp_SE/google_gemini-3-flash-preview_SE_s1/ExampleMandel/events.jsonl`
(JSONL line 205, `uuid df101885-8e9f-4356-ac69-ef913e87a1c7`). Verified by me from
`eval_metadata.json`: `agent: autocamp_SE`, `claude_model: google/gemini-3-flash-preview`
(**a model the paper does report**, `tex:424`/`tex:438`), task `ExampleMandel` (a val task, `tex:167`).
Ledger is 2 lines: `block/schema_error` at 10:44:13 → `allow/xml_clean` at 10:44:30 — a clean
17-second repair.

Strengths: the only instance whose cell name matches a paper cell **and** whose model appears in the
paper. Weakness: the delivered message is **3224 chars** and dominated by raw XSD regex facets
(`[facet 'pattern'] The value '-0.01, -0.01, -0.01' is not accepted by the pattern
'.*[\[\]`$].*|\s*\{\s*([+-]?[\d]*([\d]\.?|\.[\d])[\d]*...'`) repeated across 8 `Box`/`xMin`/`xMax`
lines up to the `MAX_ERRORS_PER_FILE` cap. Unreadable when trimmed to 400 chars.

**Ranking for the response: A2 first** (readable, correct backbone, paper task, successful repair).
Keep the `autocamp_SE`/`ExampleMandel` instance in reserve only if a reviewer demands a
paper-cell-named example.

### REFINED MECHANISM for the val zero-block result — and it answers gep1, not just kEdh

Verified in `scripts/launch_autocamp_phase2.sh` (`run_seed()` at lines 41-53 passes
`GEOS_HOOK_XMLLINT="$3"`; cell→env mapping comment at lines 64-73; launches at 79-90):

```
# F2 R-S+X-M+ : xmllint=0        run_seed autocamp_F2 $SEED 0
# F6 R-S+X+M- : xmllint=1        run_seed autocamp_F6 $SEED 1
# F7 R+S+X+M+ : xmllint=1        run_seed autocamp_F7 $SEED 1
# SE          : xmllint=1, plugin override
```

Two distinct reasons the hook never blocked on val, and they matter differently:

1. **S-without-X cells (F2, F3): schema checking was off by design.** `GEOS_HOOK_XMLLINT=0`, so the
   hook only ran the `ET.parse` check. This is not a bug — it is exactly what `tex:312` documents
   ("S=Stop-hook (parse-check, with xmllint when X is also on)"). Zero blocks here means
   deepseek-v4-flash never ended a val turn with unparseable XML.
2. **S-with-X cells (F6, F7, F8, SE): schema checking WAS active and still never fired**, because the
   agent had already self-validated mid-turn with `mcp__xmllint__validate_geos_xml` (~3 calls/task,
   `tex:141`), so the deck was clean by end-of-turn.

**Reason 2 is direct mechanistic evidence on gep1's score-moving S/X confound question** (`tex:157`,
`tex:272`: "the X main effect partly conflates agent-callable validation with hook-time schema
validation when S is also enabled"). The hook ledgers show that in every S∧X cell on val, **X did all
the work and S was strictly redundant — 0 hook interventions in 410 invocations.** That is a cleaner
separation than the paper currently claims it can make, and it is measured, not argued. Whichever
thread owns gep1 should be told.

Caveat on scope: this is the **val** split. On held-out-eval the hook fired 32 times in 123
invocations, so S is *not* redundant on the hard tail. The honest two-part statement is: on
in-distribution tasks the agent's own validator makes the hook redundant; on the hard tail the hook
catches what the agent's own validation missed.

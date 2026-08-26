# Research Internship Qualification Task

## What this is

We're evaluating prospective interns for a research project on adapting LLM coding agents to scientific software (geophysics simulators). Before a formal offer, we'd like to see how you read papers and how you handle a real, unfamiliar codebase. This task is designed to take **15–20 hours total over 2–3 calendar days**. If you find yourself going much beyond that, stop and write up where you are — submitting an honest partial result is better than disappearing into a debugging hole.

There are two parts:

1. A short literature review (5 papers, one paragraph each).
2. A miniature replication of one paper's case study.

Both halves feed each other: by the time you've read the five papers, you'll have context for what's interesting and what's load-bearing in the replication target.

---

## Part 1 — Literature review

Read the following five papers. For each, write **one paragraph (~150 words)** in a single markdown file `litreview.md`. Use this structure inside each paragraph:

- What problem the paper addresses
- The method in one or two sentences
- What they evaluate on and what they claim
- The single result or design choice you find most load-bearing — i.e., if it turned out to be wrong, the contribution would collapse

**Papers:**

1. **CellVoyager** — Alber et al., *Nature Methods*, 2026. (https://www.nature.com/articles/s41592-026-03029-6)
2. **CellAgent** — Liu et al., bioRxiv 2024.05.13.593861.
3. **BixBench** — Mitchener et al., arXiv 2503.00096.
4. **GeneAgent** — Wang et al., *Nature Methods*, 2025.
5. **Biomni** — Stanford SNAP, https://github.com/snap-stanford/Biomni (the linked paper / preprint, not the README).

Then, at the end of the file, write a short **synthesis paragraph (~200 words)** answering: *Which of these five most threatens the framing of the others? How would you position CellVoyager (the replication target below) relative to the rest?*

We are not looking for comprehensive coverage. We are looking for whether you can identify what's actually doing work in a paper.

---

## Part 2 — Case-study replication: CellVoyager on COVID-19 PBMCs

CellVoyager's main qualitative result is its three case studies, where the full agent (idea generation + code execution + interpretation) autonomously analyzes a published single-cell RNA-seq dataset and produces a Jupyter notebook of new analyses. You will reproduce **one trajectory** of the **COVID-19 PBMCs case study** (Wilk et al. 2020 dataset).

This is not a numerical replication — you're producing an artifact (a notebook) and judging whether it does sensible work. The signal we care about is whether you can stand up an unfamiliar agent codebase against a non-default LLM provider, run it end-to-end, and read the output critically.

### Scope

Repository: https://github.com/zou-group/CellVoyager

Use **DeepSeek V4-flash** for hypothesis generation. The repo's hypothesis path uses LiteLLM, which supports DeepSeek natively (resolve the right model string from DeepSeek's docs and LiteLLM's provider conventions).

Run with these settings:

- `--execution-mode legacy` — avoids the Anthropic-only Claude Agent SDK execution path
- `--no-vlm` — skips a hardcoded GPT-4o vision call in the VLM codepath you'd otherwise have to wire around
- `--num-analyses 1`
- `--max-iterations 4` — the paper used 8; 4 keeps the run bounded for this task

Run **one trajectory** end-to-end. The paper's case studies are graded by the original paper's authors on creativity and biological relevance — you obviously can't replicate that grading, but you can read the output yourself and assess whether the agent did sensible work.

### Expect to patch the repo

The legacy executor constructs its OpenAI client with no custom `base_url` (see `cellvoyager/agent.py` around line 74), so it points at OpenAI's endpoint by default. To route it to DeepSeek you'll need a small patch — finding it is part of the task, not making it. If you find yourself writing more than ~15 lines of edits, stop and tell us; you're probably going down a wrong path.

### Setup steps you will need

1. Clone the repo and create the conda environment from `environment.yml`.
2. Download the COVID-19 dataset (~1.3 GB) using the `curl` command in the repo's README.
3. Get a DeepSeek API key (see "Setup notes" below — lab policy is that we don't distribute keys to non-members).
4. Find and apply the patch described above.
5. Run `python run_cellvoyager.py` with the flags listed in *Scope*.

### What to report

In a file `replication.md`:

1. **Did it run end-to-end?** If it stalled or errored, where? What did you do? Include the actual error message if relevant.
2. **Code-execution stats.** Of the code cells the agent generated, how many executed cleanly on the first try? How many needed fix attempts? Were any unfixable?
3. **Trajectory quality.** For each step in the resulting notebook, briefly note: (a) was the hypothesis sensible given the COVID-19 dataset, (b) did the code actually do what the hypothesis described, (c) is the LLM's interpretation of the output reasonable.
4. **Overlap with the paper.** For this dataset the paper highlights findings around CD8+ T cell pyroptosis, monocyte HLA class II downregulation, and plasmablast / developing-neutrophil dynamics. Did your trajectory go anywhere near these directions? If it explored elsewhere, what did it find?
5. **Cost log.** Total DeepSeek spend, broken down if you ran more than once. With DeepSeek V4-flash pricing this should come in well under **$1** for one trajectory; **$5** is a hard cap.

Include the resulting Jupyter notebook from `outputs/<run-name>/` in your submission.

### Judgment questions (answer briefly)

These matter more than whether the run succeeded:

- What surprised you most about getting this running?
- Where in the pipeline did you have to make a judgment call that wasn't specified by the paper or repo? What did you decide and why?
- The paper grades trajectories via expert biologist review. If you wanted to evaluate this kind of agent without recruiting biologists, what would you do?
- If you had another week, what one experiment would most strengthen or weaken the paper's case-study claim?

---

## Deliverables

Submit a single zip or repo link containing:

```
qualification/
├── litreview.md            # Part 1
├── replication.md          # Part 2 writeup with judgment questions
├── notebook.ipynb          # the agent's output notebook from outputs/<run-name>/
├── code/                   # any patches / scripts you wrote
│   └── README.md           # how to re-run from a fresh clone
└── notes.md                # dead ends, things you tried, time spent
```

`notes.md` is graded. Showing how you spent your time is part of the evaluation.

---

## What we're evaluating

In rough order of importance:

1. **Scientific honesty** — calibrated claims, openly reporting what didn't work, refusing to overstate from a single run.
2. **Engineering judgment** — when the repo doesn't quite work, what do you do? Do you read the source, or guess? Do you make the smallest change that works, or rewrite half the codebase?
3. **Reading depth** — can you tell what's load-bearing in a paper vs. window dressing?
4. **Communication** — can a busy reader understand your writeup in 5 minutes?

We are explicitly **not** evaluating:

- Whether the agent produced impressive biology. With one trajectory at 4 iterations on a non-default model, it may not.
- Whether everything ran smoothly. It won't, and the interesting signal is in how you handled it.
- How polished the prose is. Plain markdown is fine.

---

## Setup notes

- **API keys: you will need to supply your own DeepSeek API key.** Lab policy is that we don't distribute API keys to people who are not yet group members / onboarded, so the API spend is on you for this task. With DeepSeek V4-flash pricing ($0.14 / 1M input tokens, $0.28 / 1M output tokens) and the scope above (one trajectory, four iterations), expect a total cost well under **$1**. If you're projecting to overshoot $5, stop — you've mis-scoped something.
- The conda environment build (`environment.yml`) is heavy (scanpy + scvi-tools + jupyter stack); allow ~10 minutes.
- The COVID-19 `.h5ad` is ~1.3 GB; download early so it's not blocking you on day three.
- Per-trajectory runtime should be ~15–30 minutes once everything is wired up.
- If you hit a blocker for >2 hours, message us. Asking is not a negative signal; silently spinning is.

---

## Submission

Reply to this email with a zip attachment or repo link by **11:59pm on Sunday, May 17, 2026**. If you need an extension, ask before the deadline.

Questions about scope, ambiguity, or interpretation are encouraged — just reply to this email rather than guessing.

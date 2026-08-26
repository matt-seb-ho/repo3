## Paper: CellVoyager: AI CompBio Agent Generates New Insights by Autonomously Analyzing Biological Data

Authors: Samuel Alber, Bowen Chen, Eric Sun, Alina Isakova, Aaron J. Wilk, James Zou (Stanford University). Venue: bioRxiv preprint, June 2025 (doi: 10.1101/2025.06.03.657517).

## Overview

CellVoyager is an LLM-driven AI agent that autonomously explores single-cell RNA sequencing (scRNA-seq) datasets. Unlike prior bioinformatics agents that execute user-issued commands (e.g., CellAgent, CompBioAgent, AutoBA, BIA), CellVoyager is conditioned on prior analyses already performed (e.g., those reported in a published manuscript) and proposes, codes, and executes new analyses that complement rather than duplicate that prior work. It operates inside a Jupyter notebook environment so each analysis trajectory yields a reproducible artifact.

## Contributions

- A novel LLM agent (CellVoyager) that autonomously generates and runs scRNA-seq analyses while explicitly avoiding repetition of analyses already done by the user.
- CellBench, a new benchmark of 50 published scRNA-seq studies covering 483 reported analyses, with an LLM-as-a-judge evaluation pipeline (validated against two PhD-student raters at 89% and 85% concordance).
- Empirical evidence that CellVoyager outperforms strong base LLMs on CellBench by up to roughly 20%.
- Three real case studies (COVID-19 PBMCs, human endometrium atlas, mouse brain aging) where original paper authors evaluated agent outputs and found them creative and biologically interesting (80% of hypotheses deemed scientifically interesting).
- Demonstration of a human-in-the-loop mode where reviewer feedback is fed back into the agent to refine analyses.

## Methodology / System Design

Inputs are a processed scRNA-seq dataset and a report (in this work, a published manuscript) that supplies biological background and prior analyses. The agent first uses an LLM to summarize the report into (1) biological background, (2) analyses attempted, and (3) dataset details, then initializes a Jupyter notebook with packages from the scverse ecosystem (scanpy v1.10.3, scvi-tools v1.1.6, anndata v0.10.8, celltypist v1.6.3, etc.).

Core loop (Algorithm 1): generate an "exploration blueprint" consisting of a hypothesis plus a step-by-step plan. The agent self-critiques the blueprint, then iterates for up to T steps. At each step it generates code, executes it, and on failure attempts up to F = 3 fix attempts. Successful outputs (text and figures) are interpreted by a vision-language model, which produces a markdown interpretation appended to the notebook and informs replanning of subsequent steps. In their experiments T was capped at 8 steps per analysis, with a single round of self-reflection per blueprint. After a trajectory completes, the agent appends a short summary to a `past_analyses` list so subsequent trajectories avoid duplication. A final report is written summarizing the most promising findings.

The agent is "training-free" and uses LLMs out of the box. CellBench experiments use GPT-4o (temperature 1) and o3-mini (medium reasoning effort) via the OpenAI API. Case studies use o3-mini.

## Evaluation Tasks and Datasets

### CellBench

- 50 published scRNA-seq papers, 483 ground-truth analyses extracted by gemini-2.5-pro-preview.
- Task: given only the background section of a paper, predict which analyses the authors performed.
- Metric: micro-averaged and macro-averaged accuracy (proposed analysis matches a held-out one, judged by an LLM judge). Each model run 3 times.
- For fair comparison with non-agent baselines, only the initial idea-generation phase of CellVoyager is used (no code execution), and prompts are adjusted to predict probable held-out analyses rather than maximally novel ones.

Results (Table 1):

| Model | Micro-Avg | Macro-Avg |
| --- | --- | --- |
| GPT-4o | 49.89 (2.73) | 49.41 (2.40) |
| o3-mini | 55.25 (0.80) | 55.46 (0.58) |
| CellVoyager (GPT-4o) | 65.89 (1.81) | 68.74 (1.52) |
| CellVoyager (o3-mini) | 64.90 (1.30) | 67.90 (1.47) |

CellVoyager (GPT-4o) beats GPT-4o by 16% micro (p < 0.01) and 19.33% macro (p < 0.001). The CellVoyager (o3-mini) vs CellVoyager (GPT-4o) gap is not statistically significant.

### Three case studies (full agent with code execution)

For each, 8 trajectories generated; the 5 with highest fraction of successfully executed code cells were sent to an author of the original paper for review using a rubric (Creativity 1 to 4, Biological Relevance Y/N, Correct Methods Y/Mostly/N, Interesting Hypothesis Y/N).

- COVID-19 PBMCs (Wilk et al., severe COVID, 7 patients, 6 controls): mean creativity 2.8/4; 3/5 analyses biologically meaningful; 5/5 raised hypotheses worth deeper investigation. The pyroptosis analysis received 4/4 creativity and surfaced a novel finding that CD8+ T cells in COVID-19 patients have significantly elevated pyroptosis gene scores (p = 0.001), a direction not prominent in prior literature.
- Human endometrium atlas (Wang et al., 73,180 cells, 29 donors): mean creativity 3.4/4; 2/5 biologically meaningful; 3/5 hypotheses author wanted to investigate further. Agent identified candidate ligand-receptor signaling between stromal fibroblasts and other cell types (e.g., TGF-beta, FGF2-FGFR1, VEGFA-KDR, PDGFB-PDGFRB) across menstrual cycle phases; with author feedback it expanded to test 40 ligand-receptor pairs.
- Brain aging in mouse subventricular zone (Buckley et al., 11 cell types): mean creativity 2.4; 3/5 biologically meaningful; 4/5 hypotheses worth further investigation. Agent introduced a transcriptional-noise-vs-age analysis (Euclidean distance to subcluster centroid in PC space), absent from the original paper. Found marginal positive noise-age correlation in Astrocytes-qNSCs (r = 0.047, p = 0.0135). After author feedback, extended to all cell types and showed significant young-vs-old noise increases in oligodendrocytes (3 subclusters), microglia, and mural cells (p < 0.001), the first such observation in the subventricular zone neurogenic niche.

Across the three case studies, 12/15 hypotheses were judged interesting enough to warrant follow-up. The authors also state 80% of hypotheses overall were scientifically interesting.

### Baseline comparison for case studies

Google's Data Science Agent in Colab was tried with the same inputs but failed: superficial proposed analyses, struggles with scRNA-seq packages, repeated error loops. The authors use this as evidence that generalist data-science agents lack the domain-specific capability needed for high-dimensional single-cell data.

## Key Analysis and Discussion Takeaways

- Conditioning on prior analyses and adding self-critique plus iterative replanning meaningfully improves analysis-idea generation over base LLMs (~16 to 20 point gains on CellBench).
- The agent can rediscover known biology and surface plausibly novel directions (CD8+ T cell pyroptosis, transcriptional noise across SVZ cell types) on heavily-studied published datasets, suggesting reanalysis of public data could yield new insight at scale.
- Human-in-the-loop refinement is impactful: a single reviewer comment was often enough for the agent to substantially improve an analysis (e.g., pseudobulking before testing, expanding ligand-receptor panels, switching from correlation to young-vs-old comparisons).
- Choice of base LLM matters less than expected once wrapped in the agent scaffold: o3-mini and GPT-4o are statistically tied within CellVoyager.
- Limitations acknowledged: sequential analyses take ~30 minutes each (parallelization is future work); current scope limited to scRNA-seq though the design is modular for spatial transcriptomics, proteomics, etc.; agent leans on popular packages (scanpy) and may underutilize niche or in-house tools (mitigations include providing tool metadata or fine-tuning); more extensive literature search could improve grounding.
- Broader claim: with over 100,000 published single-cell studies, agent-driven reanalysis is a scalable path to new biological insights that human researchers cannot exhaustively pursue.

CMU
https://arxiv.org/pdf/2604.03964

---

@@@ GPT Summary

## **Paper Overview**

SKILLFOUNDRY proposes a framework for automatically building and maintaining libraries of reusable “agent skills” from heterogeneous scientific resources such as repositories, APIs, notebooks, scripts, databases, documentation, and papers. The paper argues that scientific agents are currently bottlenecked not by lack of tools, but by lack of operationalized procedural knowledge that agents can reliably execute.  

The central idea is to transform fragmented scientific know-how into executable skill packages that contain:

- task scope
- inputs/outputs
- dependencies
- execution procedures
- provenance
- validation tests

The framework continuously mines, validates, repairs, merges, and expands these skills in a closed loop.  

The authors position SKILLFOUNDRY as a “skill-centric” framework, in contrast to prior “tool-centric” systems that mainly expose APIs or executable interfaces.  

## **Main Contributions**

The paper claims four primary contributions:

1. A self-evolving framework for converting heterogeneous scientific resources into executable agent skills.
2. A validation/evaluation protocol combining:
    - library-level validation (executability, novelty)
    - downstream task evaluation
3. Empirical evidence that automatically mined skills improve scientific agent performance.
4. Demonstration that the framework can synthesize new task-specific skills for real scientific workflows.  

Conceptually, the paper’s biggest contribution is treating skills as reusable procedural abstractions rather than merely callable tools.

## **Core Methodology**

## **High-Level Pipeline**

SKILLFOUNDRY operates as a tree-guided closed-loop system with six stages:

1. Domain Tree Construction
2. Resource Mining
3. Skill Extraction
4. Skill Testing
5. Tree Expansion
6. Tree Refinement

The overview figure on page 4 illustrates this loop visually.  

The framework continuously updates a domain knowledge tree that tracks:

- covered capabilities
- validation outcomes
- linked resources
- existing skills

This tree acts both as:

- a taxonomy
- a controller for future mining decisions

## **Domain Knowledge Tree**

The domain is represented as a rooted tree:

- internal nodes = scientific domains/subdomains
- leaves = actionable skill targets

The tree stores:

- linked resources
- linked skills
- validation state
- coverage estimates

Mining prioritizes branches with:

- abundant resources
- weak verified skill coverage

rather than performing uniform search.  

The tree is dynamic:

- branches can split when new subareas emerge
- redundant or stale leaves can be pruned/merged

This makes the framework “self-evolving.”

## **Resource Mining and Skill Extraction**

For a selected branch, the system retrieves:

- repositories
- notebooks
- APIs
- workflows
- documentation
- papers

The authors emphasize “authoritative artifacts” such as official documentation and maintained repositories.  

From these artifacts, the framework extracts an “operational contract” containing:

- scope
- dependencies
- inputs
- outputs
- execution assumptions
- provenance
- examples

The extracted information is compiled into a reusable skill package.  

Importantly, the resulting skill is not just text:

- it includes machine-readable metadata
- executable scripts
- test commands
- provenance tracking
- example assets

## **Skill Validation**

The framework uses multi-stage validation before adding a skill to the library:

### **1. Execution Testing**

Checks whether the skill actually runs under the declared contract.

### **2. System Testing**

Validates infrastructure-dependent skills (e.g., SLURM/HPC environments).

### **3. Synthetic Data Testing**

Uses mock inputs when real execution is expensive or unstable.

Synthetic testing verifies:

- interface completeness
- file argument handling
- behavioral stability under controlled conditions

rather than full downstream task correctness.  

The appendix expands this into a hierarchical validation/repair loop:

- detect failures
- attempt targeted repair
- rerun tests
- benchmark “with skill” vs “without skill”
- optimize weak skills iteratively  

## **Novelty Checking and Refinement**

Skills are compared against:

- local libraries
- SkillHub
- SkillSMP

Novelty assessment considers:

- scope
- provenance
- capability overlap
- usability

Possible outcomes:

- add as new leaf
- merge with existing skill
- mark redundant
- prune/deprioritize

This updates the domain tree for future mining cycles.  

## **Implementation Details**

The framework is implemented as a staged pipeline with specialized prompts/modules for:

- tree checking
- resource search
- skill building
- testing
- optimization
- novelty checking

The authors use different GPT-5 variants for different stages:

- GPT-5.4 (high reasoning) for resource search
- GPT-5.4-medium for skill construction
- GPT-5.4-mini for validation and optimization

This reflects the authors’ belief that resource triage/search is the most reasoning-intensive component.  

## **Skill Library Statistics**

At the time of writing, the library contains:

- 286 skills
- 27 domains
- 254 subdomains
- 394 mined resources

The distribution across scientific areas is shown in Figure 2 on page 6.  

The largest categories include:

- transcriptomics
- genomics
- statistics/ML
- reproducible workflows
- scientific agents
- scientific computing

## **Novelty Results**

The authors report:

- 71.1% of mined skills are novel relative to SkillHub and SkillSMP
- 28.9% overlap with existing libraries

Novelty is determined by whether an existing skill already solves the same task.  

The framework:

- discards redundant skills
- merges complementary skills

This is one of the stronger empirical claims in the paper.

## **Runtime Analysis**

The runtime analysis shows:

Most expensive stages:

1. skill extraction
2. resource mining

Less expensive:

- testing
- tree updates

The authors emphasize that resource mining is budget-capped to avoid unbounded exploration.  

## **Evaluation Tasks**

The paper evaluates on three categories of tasks:

1. Skill-library analysis
2. MoSciBench benchmark tasks
3. Real genomics workflows
    - cell type annotation
    - scDRS workflow

## **MoSciBench Evaluation**

MoSciBench is a multimodal scientific discovery benchmark spanning:

- climate science
- biomedical engineering
- cheminformatics
- population genomics
- earth science
- psychology

The authors compare:

- same coding agent WITHOUT skills
- same coding agent WITH SKILLFOUNDRY skills

### **Main Results**

Average improvements:

- Repo-Acc:
    - 61.19% → 66.73%
- Paper-Acc:
    - 43.85% → 53.05%

Execution success remained:

- 100% in all settings

SKILLFOUNDRY improved performance on:

- 5/6 datasets

and left one unchanged.  

### **Per-Dataset Results**

Largest gains:

- health spa
- pop genetics
- cyclone

Smaller gains:

- massspecgym
- terra

No change:

- nurse stress

The authors attribute the lack of gain on nurse stress to a strong baseline.  

### **Interpretation**

The key claim is:

- gains arise from improved reasoning/procedural guidance
- not simply improved executability

because execution success was already perfect without skills.

This is an important distinction.

## **Cell Type Annotation Task**

The authors evaluate a realistic spatial transcriptomics workflow:

- annotating cell types in MERFISH data

Dataset:

- developing human heart
- 228,635 cells
- 238 genes
- 3 samples

This task tests:

- preprocessing
- clustering
- representation learning
- marker reasoning
- validation workflows

rather than isolated tool calls.  

## **Compared Systems**

### **Vanilla Codex**

Uses:

- PCA
- k-means clustering
- marker-set scoring

### **Codex + SKILLFOUNDRY**

Uses synthesized skill pipeline:

- PCA
- neighborhood graph construction
- Leiden clustering
- centroid similarity labeling
- cluster refinement
- neighborhood validation

### **SpatialAgent**

Domain-specific baseline using:

- external scRNA-seq reference datasets
- Harmony label transfer
- curated workflows

## **Results**

### **Vanilla Codex**

- Coverage: 81.1%
- Accuracy: 68.5%

### **Codex + SKILLFOUNDRY**

- Coverage: 99.2%
- Accuracy: 82.9%

### **SpatialAgent**

- Coverage: 100%
- Accuracy: 87.1%

### **Interpretation**

SKILLFOUNDRY substantially improves:

- label coverage
- annotation accuracy

even without external reference datasets.

SpatialAgent still performs best overall due to:

- expert-curated pipelines
- external references

But the gap narrows considerably.

This experiment supports the claim that the framework can synthesize task-specific skills rather than merely retrieve existing ones.

## **scDRS Workflow Evaluation**

This is arguably the strongest experiment in the paper.

Task:

- integrate GWAS summary statistics with single-cell RNA-seq
- identify disease-relevant cells/types

The authors evaluate:

- Biomni baseline
- Biomni + SKILLFOUNDRY-generated skills

Importantly:

- scDRS was NOT already part of Biomni’s predefined workflows

This makes it a transfer/generalization test.  

## **Evaluation Setup**

Data:

- TMS FACS scRNA-seq
- height GWAS

Evaluation:

- 3 replicates per setting
- blinded expert review

Metrics:

1. qualitative workflow completeness
2. RMSE against expert outputs

Qualitative criteria include:

- cell-level analysis
- cell-type analysis
- FDR correction
- heterogeneity analysis
- proper outputs/files
- identifying chondrocytes correctly

## **Results**

### **Quantitative**

Mean RMSE:

- Biomni: 0.11
- Biomni + SkillFoundry: 0.02

Two skill-augmented runs matched expert outputs exactly.  

### **Qualitative**

Only Biomni + SKILLFOUNDRY achieved:

- perfect qualitative score (7/7)

The paper also shows that the skill-enhanced version generated:

- richer
- more interpretable
- statistically complete figures

than the baseline system.  

### **Failure Analysis**

Without synthesized skills:

- Biomni often omitted critical filter-data parameters
- resulting in noisy/incomplete analyses

With skills:

- workflows became more robust and interpretable

This is an important insight:  
the value of skills is not just tool access, but procedural correctness.

## **Main Takeaways from Discussion/Analysis**

## **1. Procedural Knowledge Is the Bottleneck**

The paper repeatedly argues that:

- scientific ecosystems already contain abundant knowledge
- the missing piece is executable procedural abstraction

The framework operationalizes this idea through reusable skills rather than tools alone.

## **2. Skills Are More Than APIs**

A core conceptual distinction:

- tools expose interfaces
- skills encode workflows/procedures

The paper strongly argues that scientific agents need:

- execution guidance
- assumptions
- validation structure
- environment knowledge

not just callable APIs.

## **3. Closed-Loop Refinement Matters**

The framework is not static retrieval.

Key ingredients:

- validation
- repair
- benchmarking
- pruning
- novelty review

The authors argue this is necessary because naive accumulation would produce:

- brittle
- redundant
- low-quality skill libraries.

## **4. Internal Validation Is Not Enough**

The paper explicitly notes that:

- execution tests alone do not guarantee usefulness
- downstream workflow evaluation is necessary

This motivates their use of:

- MoSciBench
- genomics workflows
- expert review

## **5. Task-Specific Skill Synthesis Is Important**

The strongest experiments are not the static library benchmarks, but:

- generating new skills on demand
- transferring them into external agents

especially the Biomni/scDRS setting.

This suggests a future direction where:

- agents dynamically synthesize workflow abstractions for new scientific tasks.

## **6. Scientific Workflow Reliability Depends on Small Procedural Details**

The scDRS experiments highlight that:

- missing preprocessing flags
- incorrect interfaces
- incomplete workflows

can materially degrade scientific validity.

The paper argues reusable skills help standardize these fragile procedural details.

## **Limitations**

The authors acknowledge several limitations:

### **Limited Coverage**

Current library still covers only a subset of scientific domains.

### **Limited Downstream Validation**

Most skills are validated mainly through internal tests.

### **Narrow Evaluation Scope**

Experiments are concentrated in relatively few scientific domains/tasks.

### **Reliability Concerns**

The library should still be used cautiously in high-stakes scientific settings.  

## **Overall Assessment**

The paper’s strongest aspects are:

- clear conceptual distinction between tools and skills
- practical closed-loop mining/validation framework
- strong workflow-oriented genomics evaluations
- emphasis on procedural correctness

The most convincing result is probably the scDRS transfer experiment, because it demonstrates:

- external agent improvement
- workflow-level gains
- expert-evaluated scientific correctness

Potential weaknesses/open questions:

- novelty metric is somewhat heuristic
- evaluation breadth remains limited
- unclear how well the approach scales outside biomedical domains
- unclear long-term maintenance costs
- no ablation isolating which components matter most

Still, the paper presents a compelling systems-oriented vision for building reusable procedural memory for scientific agents.

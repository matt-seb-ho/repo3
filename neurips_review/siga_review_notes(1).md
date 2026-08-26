# Experiments

- LMaaJ on plausibility for secondary metric  
- Scale up experiments

# Questions for Lianhui

- How to promise writing improvements/deal with Reviewer 2  
- FOAM scale?

# Review 1: gep1

Weaknesses:

- Eval metric: TreeSim  
  - does not establish successful runs in GEOS  
    - We already know that our shit goes through GEOS linting so it definitely runs, just need to report this  
  - Does not imply physical meaningfulness  
    - Argue 1: supervision  
    - Experiment 1: LMaaJ for plausibility (checking differences in values)  
  - “Central usefulness would be much stronger with small runnability/physics-validity ladder”  
- Statistical Experimental Scale  
  - n=3 seeds, 10 held out tasks  
    - Argue: we ran more, we find that the hard tail matters most  
      - Make some reliability argument  
  - OpenFOAM  
    - Solved  
    - Report scaled results  
    - Report LAMMPS results too  
  - Human baseline  
    - Agree that it’s anecdotal but point out that it’s a tutorial task so a little bit of a lower bound (lower difficulty region)  
- Method Confounds  
  - S, X is not fully isolated  
    - Argue back that ablations   
  - Native-plugin-prefix bug  
    - Explain that the writing wasn’t updated but we did fix the numbers and then we have more refinements producing latest

# Review 2: kEdh

Weaknesses:

- Writing is too jargon-heavy (not readable for average NeurIPS reader)  
  - Some concepts can be illustrated using figures (e.g. self-evolve feedback)  
  - “Factorial” terminology may be unfamiliar  
  - “Simulation deck, brief” not defined  
  - Too AI-coded  
- Consult Lianhui  
- Realistically promise writing improvements  
- Provide definitions in response  
- Provide examples of the brief, structured, repair feedback  
- Walk through the traditional scientific simulation workflow for GEOS?

# Review 3: nBNE

Weaknesses:

- Structure:  
  - “Does not introduce new agent architecture” and “depends on existing simulator structure”  
- Treesim:  
  - Like stated above need physically meaningful output  
- Experiment scale:  
  - Larger benchmark with more diverse task types (solved with OpenFOAM and LAMMPS)

- Output validation DONE  
- Argue that GEOS is deterministic so it’s relatively ok to evaluate on the input side  
- Convergence checks:   
  - Actually run the decks through GEOS to ensure that the numbers are not so off that it doesn’t converge  
  - It’ll take time but we can get some experts to check the outputs


- Report exact claude code version
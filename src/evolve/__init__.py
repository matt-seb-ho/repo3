"""SIGA-Evolve v2: regression-gated, evidence-rich adapter search.

Replaces ``scripts/self_evolving/`` (see ``scripts/self_evolving/legacy/``).
Design and rationale: ``docs/2026-08-19_method-adoption-plan.md``.

The v1 loop (``reflect.py``) had no reward channel at all: ``run_full_evolution.sh``
never scored a round before reflecting on it, so every ``.reflection_meta.json``
records ``round_mean_treesim: 0`` and the proposer was told "mean treesim 0.0000,
n=7" with every task marked ``treesim N/A``. This package rebuilds the loop as an
actual search:

* :mod:`~evolve.manifest`   -- the adapter is an explicit, typed component set
                              (AHE "component observability"), and the stop
                              policy is *inside* the search space.
* :mod:`~evolve.evidence`   -- layered drill-down evidence corpus built from
                              ``scripts/bottleneck/extract.py`` (AHE "experience
                              observability"), replacing v1's 2500-char dump of
                              tool names.
* :mod:`~evolve.acceptance` -- Self-Harness's regression gate: no per-task cliff,
                              no aggregate regression, no efficiency regression.
* :mod:`~evolve.hygiene`    -- contamination gate; a superset of v1's ``.xml``-only
                              regex, which let ``.geos`` dependency filenames
                              through into the shipped SE adapter.

Nothing here modifies ``src/runner/`` or ``src/eval/``; both are called, never
edited (``.copilot/direction.md``).
"""

from evolve.manifest import Manifest, ComponentSpec, StopPolicy  # noqa: F401
from evolve.candidate import Candidate  # noqa: F401

__all__ = ["Manifest", "ComponentSpec", "StopPolicy", "Candidate"]

"""Experiment runner library.

Reusable pieces used by ``scripts/run_experiment.py``:

- ``contamination`` — determine which GEOS source files must be hidden from
  the agent for a given task, and materialise a sanitized (hardlink-based)
  copy of the GEOS tree that omits them.
"""

from . import contamination

__all__ = ["contamination"]

Phase: DO
Autonomy: full
Project: repo3
Updated: 2026-04-27

Researcher: present
Sleep started: 2026-04-27T20:00:00Z
Sleep ended:
max_experiments: 20
max_hours: 8
diminishing_returns: 3
Cycle: 5
Consecutive_no_improvement: 0
Consecutive_errors: 0

Current task: Sub-agent orchestration architecture for GEOS XML authoring (D-010 / XN-017).
Build a parallel, toggleable orchestrator that decomposes XML authoring across per-segment
Claude Code subagents. Test on the 17-task v2 set with DSv4-flash direct (fall back to
m2.7 via OpenRouter if DS account exhausts).

Background design exists at `docs/2026-04-27_subagent-architecture-geos.md`. This session
formalises it as D-010, builds `plugin_orchestrator/` alongside the existing `plugin/`
(no edits to `plugin/`, `src/runner/*`, `run/AGENTS.md`, `scripts/eval/*` — concurrent
OpenHands run uses those), wires up a toggle path, smoketests, and runs full eval.

Concurrent processes to NOT disturb:
- OpenHands `oh_test17_s1` campaign — owned by the previous session-task.
- Any minimax-m2.7 baseline runs left over from the memory-ablation matrix.

Plan:
1. Read DSv4-flash API docs, decide proxy/router approach for Anthropic-format → DS direct.
2. Write D-010 design memo.
3. Build `plugin_orchestrator/` (.claude-plugin/plugin.json, agents/*.md, skills/, scripts/segment_splice.py).
4. Add a parallel runner entry-point (separate file, not modifying src/runner/*).
5. Smoketest on TutorialSneddon + ExampleMandel.
6. Launch full 17-task campaign on DSv4-flash direct.
7. Score, write XN-017, update hub.md.

Session deadline: 8h or 20 cycles whichever first.

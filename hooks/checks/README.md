# Check plugins

The one part of the harness a SIGA-Evolve candidate may author as **code**.

A candidate may not rewrite `plugin/hooks/verify_outputs.py`. It may add a file
here behind a fixed interface, with a **mandatory** sibling test:

```
hooks/checks/<name>.py        def check(deck: Deck, ctx: CheckContext) -> list[Finding]
hooks/checks/<name>_test.py   REQUIRED — candidate is rejected without it
```

A plugin that has no test, fails its own test, raises on import, or exceeds its
5-second budget is rejected by `evolve.checks.validate_plugins` **before any
rollout is spent**. That fence exists because arXiv:2603.05578 (Tool-Genesis)
finds one-shot autonomous tool creation fails and interface errors compound;
free rejections are where most bad proposals should die.

Built-in checks (`parse`, `required_sections`, `cross_section_refs`,
`constraints`) live in `src/evolve/checks.py` and are the reference the proposer
is shown. Plugins here extend that set; the active set is chosen by the
`[components.stop_policy] checks = [...]` field of the candidate's manifest,
which is itself searchable.

## Writing a check

```python
from evolve.checks import Deck, CheckContext, Finding

def check(deck: Deck, ctx: CheckContext) -> list[Finding]:
    return [Finding("my_check", "error", "what is wrong", location="where")]
```

Rules:
- **Read-only.** Never write to `ctx.inputs_dir`.
- **Fast.** 5-second hard budget; a check that needs longer is a second agent.
- **stdlib + lxml only.** No network.
- **`severity="error"` blocks the agent's turn**, `"warn"` is recorded only.
  Blocking on something the agent cannot act on is worse than not checking.

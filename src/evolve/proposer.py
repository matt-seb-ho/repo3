"""The proposer: evidence in, one minimal edit plus a falsifiable prediction out.

Differences from ``reflect.py``'s proposer, each tied to a specific v1 failure:

* **It is shown the reward.** v1's prompt header read "RECENT ROUND RESULTS
  (mean treesim 0.0000, n=7)" with every task marked ``treesim N/A``, because
  the round was never scored before reflection. Worse, the prompt contained
  "if the current plugin is already working well (>=0.85 mean treesim), it's
  fine to make small additions or no changes" — a branch that, with 0.0000
  rendered, could never fire. The proposer was told it was failing
  catastrophically at every round and responded by growing the primer from
  270 B to 3159 B.
* **It edits one component per call.** v1 rewrote every file at once, so no edit
  could ever be attributed. Self-Harness's minimality is enforced structurally.
* **It must delete to add.** Components carry hard token budgets, and the ACE
  delta operators include ``delete`` for exactly this reason.
* **It must predict.** Every proposal names the tasks it expects to help and by
  how much, verified next round (AHE decision observability).
* **It is a different model from the inference model** by default. Not because
  self-distillation is the reason v1 failed — arXiv:2605.30621 finds
  harness-updating is roughly flat in base capability — but because it is free
  and removes a confound.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Sequence

from evolve.candidate import Candidate, Prediction
from evolve.evidence import RoundEvidence

FILE_BLOCK_RE = re.compile(r'<file component="([^"]+)">\s*(.*?)\s*</file>', re.DOTALL)
PREDICTION_RE = re.compile(r"<prediction>\s*(\{.*?\})\s*</prediction>", re.DOTALL)

SYSTEM_PROMPT = """\
You are improving a *grounding adapter* that sits on top of a frozen coding
agent so it can author input decks for a scientific simulator. You are not
writing the agent; you are editing the small set of artifacts the agent always
sees or is always checked against.

Ground rules, all of which are enforced mechanically after you answer:

1. EDIT EXACTLY ONE COMPONENT. Proposals touching more than one are rejected.
2. MINIMAL EDIT. Change what the evidence says is broken and nothing else.
3. HARD TOKEN BUDGETS. Components have budgets; to add, delete something first.
   A longer artifact is not a better one -- adapter cells must not cost more
   wall-clock than the bare harness.
4. NO FILENAMES, NO TASK NAMES, NO GROUND-TRUTH VALUES. Never name a specific
   input file (any extension), a task identifier, or a numeric value you saw in
   a deck. Describe physics classes, element shapes, and conventions instead.
   A candidate that leaks any of these is discarded before it is ever run.
5. NEGATIVE CONSTRAINTS ARE AS VALUABLE AS POSITIVE ONES. "Exactly k
   <Constitutive> children, no more" prevents the failure mode where an adapter
   fixes missing blocks and starts hallucinating extra ones. Constraints written
   into the constraints component are also enforced at the stop interface.
6. YOU MAY EDIT THE STOP POLICY. Retry budget, feedback shape, and which checks
   run are components too. Static gates raise the floor; feedback the agent can
   act on raises the ceiling.

Answer with exactly one <file> block and exactly one <prediction> block:

<file component="COMPONENT_NAME">
...full new contents of that component...
</file>
<prediction>
{"targets_category": "missing_block",
 "predicted_beneficiaries": ["TaskA", "TaskB"],
 "predicted_delta": 0.03,
 "rationale": "one or two sentences",
 "evidence_refs": ["L2:TaskA"]}
</prediction>

The prediction is a contract. It is checked against next round's outcomes and
recorded. An edit whose predicted beneficiaries do not move is reverted.
"""

USER_TEMPLATE = """\
## Current adapter

{components}

## Evidence from the last evaluation

{evidence}

## Components you may edit

{editable}

## Recent decisions

{history}

Propose one minimal edit.
"""


@dataclass
class ProposerConfig:
    model: str = "gemini-3-flash-preview"
    api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    api_key_env: str = "OPENROUTER_API_KEY"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout_s: int = 300
    evidence_level: int = 2
    max_tasks_shown: int = 8


class ProposerError(RuntimeError):
    pass


def _api_key(cfg: ProposerConfig) -> str:
    key = os.environ.get(cfg.api_key_env)
    if key:
        return key
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith(f"{cfg.api_key_env}="):
                    return line.split("=", 1)[1].strip().strip('"')
    raise ProposerError(f"{cfg.api_key_env} not found in env or .env")


def call_model(prompt: str, cfg: ProposerConfig, system: str = SYSTEM_PROMPT) -> str:
    body = json.dumps(
        {
            "model": cfg.model,
            "max_tokens": cfg.max_tokens,
            "temperature": cfg.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode()
    req = urllib.request.Request(
        cfg.api_url,
        data=body,
        headers={
            "Authorization": f"Bearer {_api_key(cfg)}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError as exc:
        raise ProposerError(f"proposer call failed: {exc}") from exc
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise ProposerError(f"unexpected proposer response: {data}") from exc


def render_components(candidate: Candidate) -> str:
    parts = []
    for name, spec in candidate.manifest.components.items():
        if spec.kind == "config":
            sp = candidate.manifest.stop_policy
            parts.append(
                f"=== {name} (config) ===\nretries={sp.retries} "
                f"feedback_shape={sp.feedback_shape} checks={list(sp.checks)}"
            )
            continue
        if not spec.path:
            continue
        text = candidate.files.get(spec.path, "(empty)")
        budget = f", budget {spec.budget_tokens} tokens" if spec.budget_tokens else ""
        parts.append(f"=== {name} ({spec.kind}{budget}) ===\n{text}")
    return "\n\n".join(parts)


def render_editable(candidate: Candidate) -> str:
    rows = []
    for name, spec in candidate.manifest.components.items():
        cur = ""
        if spec.path:
            from evolve.candidate import estimate_tokens

            cur = f" (currently ~{estimate_tokens(candidate.files.get(spec.path, ''))} tokens)"
        rows.append(f"- {name}: kind={spec.kind}{cur}")
    return "\n".join(rows)


def parse_response(
    text: str, candidate: Candidate
) -> tuple[str, str, Prediction]:
    """Extract ``(component, new_text, prediction)``. Raises on malformed output.

    v1 fell back to inheriting the parent on unparseable output, which silently
    consumed a proposer call. Here a malformed response is a loud, counted
    rejection.
    """
    blocks = FILE_BLOCK_RE.findall(text)
    if not blocks:
        raise ProposerError("no <file component=...> block in response")
    if len(blocks) > 1:
        raise ProposerError(
            f"proposal edits {len(blocks)} components; exactly one is allowed"
        )
    component, body = blocks[0]
    if component not in candidate.manifest.components:
        raise ProposerError(f"unknown component {component!r}")

    pm = PREDICTION_RE.search(text)
    if not pm:
        raise ProposerError("no <prediction> block in response")
    try:
        pred_raw = json.loads(pm.group(1))
    except json.JSONDecodeError as exc:
        raise ProposerError(f"prediction is not valid JSON: {exc}") from exc
    pred_raw.setdefault("component", component)
    return component, body, Prediction.from_dict(pred_raw)


def propose(
    candidate: Candidate,
    evidence: RoundEvidence,
    *,
    cfg: ProposerConfig | None = None,
    history: Sequence[dict[str, Any]] = (),
    _call: Any = None,
) -> Candidate:
    """One proposal round. ``_call`` is injectable for tests."""
    cfg = cfg or ProposerConfig()
    hist = (
        "\n".join(
            f"- {h.get('component')}: {'accepted' if h.get('accepted') else 'REJECTED'}"
            f" ({h.get('reason', '')}); prediction hit rate "
            f"{h.get('prediction_hit_rate')}"
            for h in list(history)[-6:]
        )
        or "(none yet)"
    )
    prompt = USER_TEMPLATE.format(
        components=render_components(candidate),
        evidence=evidence.render(level=cfg.evidence_level, max_tasks=cfg.max_tasks_shown),
        editable=render_editable(candidate),
        history=hist,
    )
    caller = _call or (lambda p: call_model(p, cfg))
    component, body, prediction = parse_response(caller(prompt), candidate)

    spec = candidate.manifest.components[component]
    if spec.kind == "config":
        raise ProposerError(
            "config components are edited via the manifest, not a <file> block"
        )
    if not spec.path:
        raise ProposerError(f"component {component!r} has no file path")
    child = candidate.with_edits({spec.path: body}, predictions=[prediction])
    child.validate()  # budgets + writability; raises before any rollout is spent
    return child

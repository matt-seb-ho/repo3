# Reconciling the two migrations onto serv6

**Date:** 2026-08-26
**Supersedes:** `~/migration/PROVENANCE_srv6.md` (VPS line) and
`/data/matt/migration/from-macbook/bundle/PORT_TO_NEW_SERVER.md` (MacBook line)
on every point where they disagree with this file. Both remain readable as
historical records of what each machine shipped; neither is a current
description of serv6.

srv13 was compromised. Work continued on two machines in parallel — a private
VPS (literature review, SIGA follow-up, the docker→enroot port) and a MacBook
(the NeurIPS rebuttal) — and both shipped into serv6. This file records the
single canonical result.

---

## 1. What is canonical now

| | Canonical location | Notes |
|---|---|---|
| repo3 | `~/projects/siga`, branch `feat/reconcile-migrations` | contains both lines' work; see §2 |
| repo4 / harness-evolve | `~/projects/sci-sim-op`, `master`, **on GitHub** | see §3 — both handoffs are wrong about this |
| research_agenda | `~/research-agenda`, `main` | lit reviews, method-adoption prompt |
| research-copilot | `~/projects/siga/research-copilot`, `main` @ `cd2181a` | cloned fresh 2026-08-26, gitignored |
| GEOS data volume | `/data/shared/geophysics_agent_data/data/` | **present** — see §4 |
| Agent memory | `~/.claude/projects/-home-matt/memory/` | migrated from the VPS's `-home-agent-nextp` path |
| Container runtime | **enroot**, not docker | see §5 |

`~/migration/mac-snapshot/repo3/` is the MacBook working tree, restored beside the
real checkout. Everything unique in it that belongs in git is now committed
(§2), so it is **reference-only** and disposable once you are satisfied.

## 2. repo3: what the reconciliation branch adds

History is linear: `main` (`20c8a93`, the paper state) → `feat/siga-evolve-v2`
(`9183110`) → `feat/enroot-backend` (`cb0ba73`) → `feat/reconcile-migrations`.
Each is an ancestor of the next, so the reconciliation branch is a strict
superset of every other branch. `feat/siga-evolve-v2` is still unmerged with no
PR.

On top of `feat/enroot-backend`:

1. **`.gitignore` merge.** The two lines' ignore files had diverged — the
   MacBook added the `neurips_review` artifact rules, the VPS added `.evolve/`.
   Both kept, plus macOS metadata and `misc/memp_external/`.
2. **`neurips_review/` imported** — 130 text files, the complete rebuttal
   record. It was untracked on every machine and existed only inside the
   MacBook worktree tarball. This was the single most at-risk artifact in the
   migration.
3. **Three `writing/arxiv/` commits cherry-picked** (`dd07a50`, `3f5e35b`,
   `f13d033`). They were never pushed anywhere — confirmed against
   `git ls-remote`, which has no `geosx-validator-hook` branch. They touch only
   `writing/arxiv/`, so they applied without conflict.
4. **Untracked notes, scripts and copilot state imported** — 14 May-2026
   research notes, `LN-004` + `meta_harness_reading/`, the `openfoam_n30`
   baselines, six analysis scripts, `plugin_factory/`, and `.copilot`'s
   `hub.md` / `config.yml` / `checkpoint.md` (the MacBook is a strict superset
   of the canonical copy in all three — the VPS line never wrote them).
5. **69 `writing/` text files imported** — the arXiv draft lineage, feedback
   passes, slides, grant reports, poster plan.
6. **Enroot made the documented default path** (§5).
7. **`.env.template` consolidated and tracked** (§6).

Tests after all of it: `pytest tests/` → **53 passed** (`test_evolve` 42,
`test_container_spec` 8).

### The `autocamp-experiment-state` tag — recovered, and mentioned in neither handoff

The MacBook bundle carries an annotated tag that the VPS bundle does not have
and that **GitHub does not have** (`git ls-remote --tags origin` is empty). It
marks commit `6503be1`, the exact harness state that produced the paper's
reported test-17 and Held-out-10 numbers:

> The autocamp campaign ran 2026-05-01 13:27 UTC to 2026-05-02 17:25 UTC on this
> commit. After it finished, two commits by brianzliu landed on remote main and
> pulling rebased the local `[CAMPAIGN]` commit onto them, so **main now contains
> code Brian added after the experiments ran.**

That makes it the reproducibility anchor for the published numbers, and it is
**not reachable from any branch** — only the tag keeps `6503be1` alive. It has
been fetched into `~/projects/siga` and survives there independently of the bundle,
but it is currently local-only. **Push it** (`git push origin
autocamp-experiment-state`) before deleting the MacBook bundle, or the anchor
goes back to existing in exactly one place.

### What was deliberately NOT imported

- **`plugin_evolving/v4` and `scripts/launch_autocamp_v4.sh`.** The VPS line
  quarantined both on 2026-08-19; the MacBook copy is un-quarantined. **The
  quarantine wins.** The two v4 trees are byte-identical, so nothing is lost.
  Reproduced here before deciding — `audit_lineage.py` still reports
  `[block] task_id_table … names 17 task ids`. Do not un-quarantine; see
  `plugin_evolving/_quarantine/README.md`.
- **~167 MB of binaries** under `writing/` (arXiv zips, figure PNGs, poster and
  keynote PDFs, build output) and the 11.7 MB skill-foundry PDF. This repo's
  convention is that `writing/` tracks source, not build output — canonical
  `writing/arxiv` tracked exactly 9 such files before this. They remain in
  `~/migration/mac-snapshot/` and in the migration tarballs.
- **`misc/memp_external/`** — a nested clone of an external reference repo.
- **`claude-code-project/`** and the MacBook transcript tarball — raw session
  logs, which can contain keys and file contents. Keep them inside the
  restricted migration directory; do not commit them.
- **The MacBook's `src/`, `plugin/`, `scripts/`, `run/`.** 18 commits behind
  mainline. Overwriting with them would silently revert the geosx-validate-input
  work, the OpenRouter routing fixes and the agent judge.

## 3. repo4 is no longer at risk — both handoffs are stale

Both handoff docs make restoring `repo4` the top-priority action on the grounds
that it "exists nowhere else" and is "not on GitHub". **That is no longer true.**
It is `~/projects/sci-sim-op`, pushed to public GitHub `matt-seb-ho/sci-sim-op`.
Verified here: the bundle's `master` (`96fe199`, 27 commits) is an ancestor of
`sci-sim-op`'s `master` (`1277c11`, 28 commits), so the full history is
contained. `pytest tests/` → **523 passed, 2 skipped**, exactly as documented.

Note the rename: the handoffs call it `repo4` / `harness-evolve`; on serv6 it is
`sci-sim-op`. It remains a clean-room rebuild of the same search as repo3's
`src/evolve/`, and the two overlap — **decide deliberately which line to
continue rather than maintaining both.**

## 4. The data volume is present — both handoffs are stale

Both handoffs call the missing `geophysics_agent_data` volume "the blocker".
It is present and populated at `/data/shared/geophysics_agent_data/data/`:

| Path | State |
|---|---|
| `eval/experiments_gt` | 46 entries |
| `eval/experiments` | 46 entries |
| `eval/experiments_test36_template` | 36 entries |
| `GEOS` | present, incl. `src/coreComponents/schema/schema.xsd` |
| `vector_db` | 12 entries |
| `eval/{dsv4_ablation_2026-04-29, self_evolving_2026-04-30, autocamp_2026-05-01, autocamp_followup_2026-05-02}` | present |
| `eval/tmp_geos` | present, empty, same filesystem as `GEOS/` |
| `/data/matt/geos_eval_tmp` | present, writable |

`~/projects/siga/data` and `~/projects/siga/runs` symlink into it (created 2026-08-26;
both gitignored). **Still missing:** `eval/interactive_autonomy_2026-05-03` and
`eval/experiments_relaxed_{medium,hard}`.

All host paths in `src/runner/constants.py` resolve, including the GEOSX
runtime under `/home/brian/`. The PORT doc's claim that
`DEFAULT_GEOS_PRIMER_PATH` points into `/home/brianliu/…` is stale — it is now
`REPO_ROOT / "plugin" / "GEOS_PRIMER_absolute_min.md"`.

## 5. Docker is gone; use enroot

Admins withdrew docker on serv6/9/10/11. Ignore every `docker build -t geos-eval
run/` instruction in the two handoff docs.

```bash
bash run/build_enroot_image.sh          # once per machine, ~10 min
export REPO3_CONTAINER_BACKEND=enroot
```

The image is already built on serv6 (`~/.local/share/enroot/images/geos-eval.sqsh`
plus container `geos-eval`) and verified end-to-end. `docs/ENROOT.md` is the
guide and lists the five behavioural differences from docker. Docker remains
supported and remains the default backend; its rendering is pinned
byte-for-byte by `tests/test_container_spec.py`, so **a change to
`docker_cmd.py` must be re-applied on top of the `ContainerSpec` refactor, never
reverted to the old literal command.**

`docs/README.md`, `docs/experiment_runner.md` and `src/runner/cli.py` now
document both backends. Dated session handoffs and the `neurips_review` sprint
threads still say "docker" — those are records of runs that really did happen
under docker and were left alone on purpose.

## 6. Secrets

**Every key that ever sat on srv13 is burned.** Rotate at the provider before
reuse: `OPENROUTER_API_KEY` / `GEOS_OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`,
`OPENAI_API_KEY`, `HF_ACCESS_TOKEN`, `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN`.
The MacBook's `secrets/env.template` also carried a live-looking OpenRouter key
in a plaintext comment; it is redacted in the shipped copy, but rotate anyway.

The two drops shipped two different `env.template` files. They are merged into
tracked `.env.template` at the repo root — names and non-secret paths only,
now also covering `REPO3_CONTAINER_BACKEND` / `REPO3_ENROOT_*`, which postdate
both. `.env` itself stays gitignored and does not exist yet.

## 7. Known issues carried forward

- **~50 files hardcode `/home/matt/sci/repo3`** (76 occurrences; 27 `.py`,
  18 `.sh`, 5 `.md`). That was srv13's layout; the path exists on no current
  machine, so all of them are broken as written. This is pre-existing debt
  rather than a conflict between the two migrations, so the reconciliation left
  it alone. The right pattern already exists in-repo
  (`constants.py`'s `REPO_ROOT = Path(__file__).resolve().parents[2]`) and in
  `sci-sim-op` commit `1277c11`. Enumerate with
  `grep -rln '/home/matt/sci/repo3' src/ scripts/ run/ plugin/`.
  Note `scripts/self_evolving/{reflect.py,run_round.sh}` are among them but are
  v1 code being retired.
- **repo3 tracks ~50 MB of Next.js dev cache** under
  `run/geos-agent-dashboard/.next-dev-isolated/` — the five largest tracked
  files. A `git rm -r --cached` + ignore entry would help every future clone.
- **`.copilot/status.md` is stale**, still showing the 2026-05-01 autonomous
  campaign as current. The real latest project state is the SIGA-Evolve v2 plan
  (`docs/2026-08-19_method-adoption-plan.md`).
- **`nips26_review.zip` is corrupt** (truncated, no end-of-central-directory).
  Unrecoverable and superseded by `neurips_review/`. Do not sink time into it.
- **Lit-review citations are partly unverified** — in
  `research_agenda/waypoint/`, ~28 of 69 arXiv IDs are tagged `[unverified]`.
  Re-verify before building on any of them.

## 8. Where the science stands

Unchanged by this reconciliation, but worth restating because the two docs
disagree about which line is current:

- **The published SE loop had no reward channel.** `v3` (the paper's SE cell) is
  the last link in a chain of three unconditioned rewrites, not a selected
  candidate. The paper's own held-out table is consistent: S+X+M `0.783±0.022`
  vs SE `0.789±0.012`. The headline `+0.069` is Vanilla→S+X+M — the
  *hand-designed* adapter — plus noise at n=3.
- **SIGA-Evolve v2 is built and unit-tested but has never been run.**
- **The active direction is the VPS's agenda**, not the MacBook's. The MacBook's
  four open follow-ups from 2026-05-04 (second seed, supervisor-prompt variant,
  Mode B F0 control, question-quality analysis) are unresolved threads on the
  published result, not dead ends.
- **Gating everything:** `INTEGRATION_REQUIREMENTS` R1 — the container boundary
  dropping `GEOS_EVOLVE_FEEDBACK_SHAPE` / `GEOS_EVOLVE_CHECKS`. Both env vars
  are now forwarded, but this still needs verifying by diffing the hook event
  log across two feedback shapes. Until then a search would vary a knob nothing
  reads — the same failure class that produced the reward-free v1.
- **Do not skip the compute-matched baseline** (plan §4.1, arXiv:2607.12227).

## 9. Disposable once you are satisfied

- `~/migration/mac-snapshot/` — everything unique is now in git.
- `~/migration/xfer/` bundles and `/data/matt/migration/from-macbook/bundle/`.
- `/data/matt/enroot_test/` — throwaway enroot mechanics probe.

**Keep** `/data/matt/migration/from-macbook/payloads/` — the 7.4 GB sprint
artifacts (indexed by `neurips_review/sprint/PROVENANCE.md`) and the srv13
snapshot zips exist nowhere else. Checksums for the whole MacBook drop verified
clean on 2026-08-26.

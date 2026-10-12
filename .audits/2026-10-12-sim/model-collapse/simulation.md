# Simulation audit of 2026-10-12: `model-collapse`

## How to read this document

This is the summary and index of the simulation audit on the narrow topic `model-collapse`. A fresh session reads it
first. The procedure is `docs/audits.md`, "Simulation audits". The audit starts from the spec audit of 2026-10-09: its
`Part (c)` in `.audits/2026-10-09-spec/docs-full-spec.md`, and "Watch in the first run" and "Pending" in
`.audits/2026-10-09-spec/disposition.md`.

The sections, in order:

- "Decisions": the user's, dated. They apply to every topic of this audit, and later topics link here.
- "How the runner is launched": the smoke test that settled the method `docs/audits.md` now specifies.
- "Status": per segment, its state, iterations, `E` IDs and checkpoint.
- "Found ahead of their segment": `E` findings parked until their segment opens.
- "Measurements": each with what it implies for the spec's estimates.
- "Inherited, by segment": what the spec audit asks this one to watch, sorted by the segment where it would show.
- "Pending and watch": items sidelined or postponed.

Each segment's iterations are in `segments/<segment>.md`, created when the segment opens. The runners' raw reports are
in `segments/runs/`.

Open risk: none yet on the launch itself (see below). Blindness to the real repo, which sits on the same disk, holds by
instruction only, as `docs/audits.md` expects. `.audits/runner.sh collect` lists every file a runner wrote outside its
topic.

## Decisions

All by the user, 2026-10-12.

- `Topic` — `model-collapse`, a narrow topic for iterating (`docs/audits.md`, "Topics"): an expected pool of about
  50–150 papers and a coreset of about 15–25 rows; the pool size is `UNVERIFIED` until `pool` runs. Input:
  `inputs/model-collapse.md`, drafted by the auditor and adopted by the user unchanged (commit `e02faa0`). Its seed IDs,
  `2305.17493` and `2404.01413`, were checked against Semantic Scholar.
- `Limits` — the defaults (`docs/audits.md`, "Limits"): 3 hours of wall-clock time and 300 runner turns per run. They
  replace a token budget, first set and then dropped the same day: cache reads count a context again on every turn,
  models are priced differently, and usage may be on a subscription, so neither tokens nor dollars measure what a run
  costs the user. Costs are recorded as measurements only.
- `Runner` — a headless `claude -p` session in a blind scratch copy, `/tmp/deeper-research-sim`, marked as a trusted
  workspace in `~/.claude.json` (backup `~/.claude.json.bak-2026-10-12`), so that the project's settings and hooks
  apply.

## How the runner is launched

As `docs/audits.md`, "Roles", now specifies: `.audits/runner.sh` (`build`, `run`, `collect`) and the prompt template
`.audits/runner-prompt.md`. That method was settled by a smoke test on 2026-10-12. A headless `claude -p` session,
started from the auditor's session in a scratch copy, saw the `survey-pass` agent and dispatched it, and the agent
reached Asta. The dispatch reported `subagent_tokens: 19453`; the run took 24 s and cost $0.25. `git log` in the copy
showed only its own commit. So the hand-over between the main session and its agents is tested, not the fallback.

A second launch, made only to check the trust setting, was denied by the auditor's permission classifier
(`Self-Modification`). Hence the allow rule for `runner.sh run`, the user's to add.

## Status

| segment | status | iterations | `E` IDs (by tag) | docs touched, size before → after | checkpoint |
| -- | -- | -- | -- | -- | -- |
| `plan` | open | 2 | it. 1: `E1`–`E8` (1 `blocker`, 2 `guess`, 1 `silent`, 4 `minor`; `E6` later retagged `guess`); it. 2: `E7` recurs, `E9`–`E11` (3 `guess`, 1 `minor`) | it. 1: `docs/audits.md` 33033 → 34095 B, `tools/preflight.py` 2891 → 3279 B, `tools/gates.py` 54399 → 54355 B; it. 2: `docs/formats.md` 35393 → 35581 B, `docs/dispatch.md` 18642 → 18764 B, `docs/process.md` 75704 → 74311 B, `docs/audits.md` 34095 → 34608 B, and three docs shortened (cost estimates deleted) | `sim-checkpoint-model-collapse-plan` at `ed53e80`, to move on convergence |
| `pool` | not started | 0 | — | — | — |
| `clusters` | not started | 0 | — | — | — |
| `coreset` | not started | 0 | — | — | — |
| `verification` | not started | 0 | — | — | — |
| `output` | not started | 0 | — | — | — |
| `coverage` | not started | 0 | — | — | — |

Starting state for `plan`: commit `e02faa0` (the input), with no `surveys/`, `outputs/`, `bib/` or `graphs/` files for
the topic.

## Found ahead of their segment

None yet.

## Measurements

All on `claude-opus-5-5`. Dollar figures are list-price equivalents, as the runs report them, not what the user pays.

- `plan`, iteration 1: 18 turns, 174 s, $0.84; 885k tokens counted cumulatively, 814k of them cache reads; no
  dispatches. Halted at the preflight, so not yet a full segment.
- `plan`, iteration 2: 18 turns, 206 s, $1.05; one dispatch.
- `Tokens per dispatch`, what the figure means: the Agent tool's `subagent_tokens` is the agent's final context size,
  not a cumulative count. For the Preflight agent it was 34215, and its last turn's context 33650 (from its transcript).
  So it is the unit the spec's `Tokens` line and estimates use. This settles what the 2026-10-09 audit left `UNVERIFIED`
  (`Z2`: "what those include").
- `The fixed cost of a dispatch`: the Preflight agent's context was 17.8k before its first tool call (system prompt,
  agent definition, `CLAUDE.md`, tool schemas). Reading its brief's sections added about 11k, and the five checks and
  the edit about 4k. The spec estimates "under 5k" for this dispatch, about 7 times too low. Implication: every estimate
  in the order of operations should include about 18k per dispatch plus the brief's reading. This matters most for the
  small, frequent dispatches. To fold into the roadmap's "Token accounting" item once more dispatches are measured.

To take, each against the spec's figure (from the 2026-10-09 audit's IDs):

- tokens per dispatch, and per segment, against the order of operations' estimates;
- verification tokens per row (`R6`), against 26k;
- the blind re-verification agreement rate (`T3`) and the faithfulness rate (`T2`), at `coverage`;
- the coverage radius per round (`T4`);
- the `R4` replication, at `verification`: about 8 rows read in full by the auditor, findings recorded before opening
  the evidence files, then scored as in `graphs/reasoning-legacy/r4/compare.md`;
- wall-clock time, outside calls, and pool and coreset sizes, per run.

## Inherited, by segment

From the 2026-10-09 disposition's "Watch in the first run". Each item is defined there; this list says only where it
would show.

- `plan` — `W3`, the per-brief reading lists, in every segment. `S1`, the proposed-dimensions form, is not exercised:
  the input declares its dimensions.
- `pool` — `A1`, the stopping rules for orientation and expansion; `M11` and `M12`, the fringe score and its age cohort;
  `M16`, the `new` route's exclusion of rejected papers; `T5`, `maybe` on the screening sheet; the tabletop's
  `g1.orientation` with no frontier candidate.
- `clusters` — the tabletop's guesses on `H6` at naming, the scope of a targeted expansion, and telling whether a region
  is still thin; the viewer, never rendered in a browser; the input's `expect`, which may trigger `H7`.
- `coreset` — the tabletop's guesses on the Bridges search, a dissent paper returned for the pool, and parallel `Edit`s
  of one survey file; `P31`, a `high` cluster's central claim.
- `verification` — `Z2` and `R6`, tokens per row and the appendix step; `R4`'s replication; `M1`, the quote length; `C9`
  and `R2`, the PDF bibliography cut and heading detection; `S10`, evidence for every cell; the tabletop's guess on
  replacing an uncheckable row.
- `output` — nothing specific beyond the plain check.
- `coverage` — `A3` and `T4`, the coverage sample; `T2` and `T3`, the judgement audits; `S11`, the cluster review before
  `Ended`; the return to step 3; `P15`–`P35`, untested by any simulation, in particular the simplified Revise and
  `g4.counted-rows`.

## Pending and watch

- `Aborted launch`, 2026-10-12 14:3x: the first launch of `plan` iteration 2 stopped after 28 s on the account's usage
  limit (`api_error: usage_limit_reached`, HTTP 429), before writing anything. Not an iteration and not a finding; its
  JSON is kept as `segments/runs/plan-2-aborted.json`. `runner.sh run` now prints such an API error plainly, since the
  JSON's `subtype` still read `success`. A long segment that meets the limit midway loses its iteration, and restarts
  from its checkpoint.

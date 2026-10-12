# Segment `plan`

Step 0: Plan, the two preflight rows, and `--gate G0` (`docs/audits.md`, "Segments"). Starting state: commit `e02faa0`,
with no survey, output, bib or graphs files for the topic. Spot check (`docs/audits.md`, "Spot checks per segment"): the
plan's dimensions against the input.

## Iteration 1

### Run

- `Runner` — headless `claude -p`, by `.audits/runner.sh run`, session `b3cb32d8-c302-4021-b0a7-25b61d665d62`. Prompt:
  `runs/plan-1.prompt.md`. Steering: none.
- `From` — commit `7fcf6eb` (the setup), whose topic state is that of `e02faa0`.
- `Cost` — 18 turns, 174 s, $0.84. Tokens: 885k counted cumulatively (814k of them cache reads, 62k cache writes, 9k
  output); no dispatches. Outside calls: none by the runner; `tools/preflight.py` made its own requests.
- `Raw report` — `runs/plan-1.md`; JSON result `runs/plan-1.json`.
- `Outcome` — the runner ran Plan, then `tools/preflight.py`, which exited 1 on
  `arXiv failed (API unreachable (TimeoutError), HTML 200)`. It recorded `H1`, decision `pending`, and stopped. It did
  not dispatch the Preflight agent and did not run `--gate G0`.
- `Written outside the topic` (`runner.sh collect`): `.serena/` (the user-level Serena MCP server, started in the copy)
  and `tools/__pycache__/`. Neither is the runner's doing. The runner reports one accidental breach: its `ls -R`,
  rewritten by the user-level RTK hook, listed the names of directories inside `.git`. It read no history.

### Findings

- `E1` — `blocker`. `tools/preflight.py` tries each service once, with a 60 s timeout (`tools/preflight.py:32`), and
  halts the pass on a slow but working service. The arXiv export API answered `200` to the auditor after 61 s, 46 s and
  14 s, on three calls made within minutes of the run. The only other user of that API, `tools/bib.py`, retries
  transient failures (`tools/bib.py:59-63`). So the preflight is stricter than what it guards. Showed at
  `Preflight: scripts`.
- `E2` — `guess`, in the audit's own setup, not the spec. The runner's prompt said to stop "once Gate `G0` has run,
  whether it passed or not", and also to stop at a halt. The runner took the halt as the more specific instruction and
  did not run the gate. Source: `.audits/runner-prompt.md`, which has no case for a halt before the segment's end.
- `E3` — `guess`. Nothing says whether a failing preflight may be rerun before halting. The runner did not rerun it, so
  as not to override the halt; another runner might have retried once. Same root as `E1`. Showed at
  `Preflight: scripts`.
- `E4` — `silent`. `g0.preflight` passes whenever `H1` appears in `Halts`, whatever its decision
  (`tools/gates.py:215-217`, `r_preflight`). Once a user decides to continue past `H1`, `G0` passes with no `Preflight`
  line, and the Asta tools and WebSearch are never checked. Nothing in a pass would flag it, which goes against the
  preflight's purpose (`docs/external_services.md`, "Preflight": "no pass runs on a missing service without the user
  knowing"). The runner noticed it only by reading the gate code, beyond its rows, after `--status` listed
  `G0 ready passed` with no `Preflight` line.
- `E5` — `minor`. When `tools/preflight.py` fails, its printout has nowhere to go. The row's `writes` says it goes to
  the next row, and the Preflight agent writes the whole `Preflight` line, but the pass halts before that row. The
  runner kept the printout in the `H1` entry.
- `E6` — `minor`. The `Halts` form, `<id> — <what happened> — pending`, does not say how much "what happened" holds. The
  runner tagged it `guess`; retagged, since its entry is complete and no outcome turns on it.
- `E7` — `minor`. The survey's `#` title text is not specified (`docs/formats.md`, "`surveys/<topic>.md`": "under a `#`
  title"). The runner copied the legacy survey's form. Any title is valid and the check ignores it.
- `E8` — `minor`, in `docs/audits.md`. The `plan` spot check names "the plan's dimensions and recency window", but
  `Recency window` is written by Orient, at step 1 (`docs/process.md`, "Order of operations"), in the `pool` segment.

Spot check: the `Dimensions` line against the input. 1 instance, 1 checked, 0 wrong: the input declares three
dimensions, and the line reads `declared in the input`.

### Fixes

All approved by the user, 2026-10-12. The gate suites pass after them: `tests/gates/faults.py` 84 of 84,
`tests/gates/behaviour.py` 49 of 49. Commit `8ac973a`.

- `E1` — `tools/preflight.py` tries an unreachable service twice, 90 s each, before it counts as failed; the docstring
  says so. Run for real afterwards: every check `ok`.
- `E2` — `.audits/runner-prompt.md`: stop once the segment's end is reached, "or earlier at a halt".
- `E3` — fixed by `E1`: the script handles a slow service itself, so the runner needs no rule on rerunning it.
- `E4` — deleted the `H1` exemption from `r_preflight` (`tools/gates.py`, 2 lines). A pass ended at `H1` does not need
  `G0` anyway (`docs/gates.md`, "Halts and waivers"). A pass the user continues past `H1` runs the Preflight agent, and
  a check that still fails is waived by the user through `Waivers`, which the spec already provides. New behaviour test
  5b in `tests/gates/behaviour.py`: `H1` with a decision and no `Preflight` line fails `g0.preflight`. It fails on the
  old code and passes on the new.
- `E5` — fixed by `E4`: a continued pass runs the Preflight agent, which writes the `Preflight` line with the script's
  half.
- `E6`, `E7` — not fixed: no outcome turns on them, and a rule would only add text.
- `E8` — `docs/audits.md`: the `plan` spot check is the dimensions alone; the recency window moves to `pool`'s.

Also changed, as audit setup and not findings: `runner.sh collect` no longer lists `.serena/` and `__pycache__/`; and,
by the user's decision of 2026-10-12, the budget is replaced by runaway limits (`docs/audits.md`, "Limits"), built into
`runner.sh run`.

Sizes, in bytes, before → after: `docs/audits.md` 33033 → 34095 (`E8`, and the limits, which replace the budget);
`tools/preflight.py` 2891 → 3279; `tools/gates.py` 54399 → 54355.

### Result

Another iteration: `E1` was a `blocker`, and `E4` a `silent` finding. Iteration 2 reruns from the same starting state.

## Iteration 2

### Run

- `Runner` — headless `claude -p`, session `d3ff2474-0ee7-4ecb-9d09-7a557c9d8f62`. Prompt: `runs/plan-2.prompt.md`, the
  template after `E2`'s fix. Steering: none. A first launch, at 14:3x, stopped on the account's usage limit before doing
  anything (`runs/plan-2-aborted.json`); this run is the relaunch, after the reset.
- `From` — commit `8ac973a`, with the starting state restored: no files for the topic.
- `Cost` — 18 turns, 206 s, $1.05. One dispatch, `survey-pass` "Preflight": `subagent_tokens` 34215, 16 tool uses, 114
  s.
- `Raw report` — `runs/plan-2.md`; JSON result `runs/plan-2.json`.
- `Outcome` — Plan, `tools/preflight.py` (exit 0), the Preflight agent (all five checks `ok`), then `--gate G0`, which
  passed. The auditor's own `--gate G0` passes. Nothing written outside the topic's files. The runner again reports that
  its first `ls -R`, rewritten by the user-level RTK hook, listed directory names inside `.git`; it read no history.

### Findings

The runner tagged four items `guess`. Two are settled by the spec, so they are not findings: the `Tokens` entry's scope
(`docs/formats.md`'s own example is `Preflight: 4k`), and which lines Plan writes (the `writes` column is "the only
authority", `docs/process.md`, and the runner followed it). The other two:

- `E7` recurs — `minor`. The two runners chose different titles: `# Survey: model collapse`, then `# Model collapse`.
  Two runners differing is a `guess` by definition, but no outcome turns on the title.
- `E9` — `minor`. `docs/dispatch.md` says not to take an agent's report at face value "where it matters", with no rubric
  for which reports matter. For the Preflight report the runner checked only that the line on disk matches the report
  and passes the check; another might have repeated a call. The plain check is the right level here.

Spot check: the `Dimensions` line against the input. 1 instance, 1 checked, 0 wrong.

Added on 2026-10-12, after the user's decision that a `guess` the runner reports stays a `guess`, even where the spec
already answers it (now in `docs/audits.md`, "Iterating a segment"). The text above is left as written. Under that rule:

- `E10` — `guess`. The `Tokens` entry's scope: `docs/formats.md` asks for "the brief's name and its scope", and the
  runner could not tell what to write for a brief with no scope, though the example shows `Preflight: 4k`.
- `E11` — `guess`. Which lines Plan writes: the runner wondered whether to add empty placeholders for the entry's other
  lines. The `writes` column settles it, and `G0` forbids placeholders, but the runner could not be sure.
- `E9`, above, is a `guess`, not a `minor`: the runner tagged it so, and it improvised the level of checking.
- `E6`, of iteration 1, is a `guess` too, for the same reason; it was left unfixed there.

### Fixes

- `E7` — fixed now, as a `minor`, without another run: `docs/formats.md`, "`surveys/<topic>.md`", says the `#` title is
  the input's own, if it has one. 35393 → 35424 bytes.
- `E9` — first left unfixed; after the decision above, fixed: `docs/dispatch.md` now says to check that what an agent
  wrote on disk matches its report and to run the plain check, and, where it reports on a paper, to check the row.
- `E10` — `docs/formats.md`, the `Tokens` line: "the brief's name, and its scope if it ran on part of the work".
- `E11` — `docs/process.md`, the Plan row's `writes`: "no other line, since each is written by the row that owns it".
- `E6` — `docs/formats.md`: a halt's `<what happened>` is one sentence, the failure as printed and the rows it left
  undone. Untested until a run meets a halt.

Also, by the user's decision of 2026-10-12: the spec's cost estimates are deleted (`docs/process.md`'s `tokens` column,
its planning figure and its rule to report a pass over or under the estimate; the stale figures in
`docs/verification.md`, `docs/coresets.md` and `docs/external_services.md`). Calibrated figures go to
`docs/experiments.md` once the audit ends. The gate suites pass: 84 of 84, 49 of 49.

Sizes, in bytes, before → after, for these fixes: `docs/formats.md` 35424 → 35581; `docs/dispatch.md` 18642 → 18764;
`docs/process.md` 75704 → 74311; `docs/audits.md` 34095 → 34608; `docs/verification.md` 10901 → 10745;
`docs/coresets.md` 12317 → 12339; `docs/external_services.md` 15359 → 15333.

### Result

First judged converged, and tagged `sim-checkpoint-model-collapse-plan` (commit `ed53e80`). Reopened on 2026-10-12 by
the decision above: `E6`, `E9`, `E10` and `E11` are `guess` findings, so their fixes need a rerun. Another iteration.

## Iteration 3

### Run

- `Runner` — headless `claude -p`, session `082e5454-8cba-4808-9083-92befcf7534c`. Prompt: `runs/plan-3.prompt.md`.
  Steering: none.
- `From` — commit `cf124b2`, with the starting state restored: no files for the topic.
- `Cost` — 19 turns, 441 s, $1.27. One dispatch, `survey-pass` "Preflight": `subagent_tokens` 35731, 13 tool uses, 349
  s, of which about 300 s were spent waiting on one WebSearch query (gaps of 90, 61 and 151 s, from the agent's
  transcript).
- `Raw report` — `runs/plan-3.md`; JSON result `runs/plan-3.json`.
- `Outcome` — Plan, `tools/preflight.py` (exit 0), the Preflight agent (all checks `ok`), `--gate G0`, which passed. The
  auditor's own `--gate G0` passes. Nothing written outside the topic's files. The `ls -R` listing of `.git` directory
  names recurs; no history read.
- `The last round's fixes` — all four showed as intended: the title is the input's own (`E7`);
  `Tokens: Preflight: 35731`, written without hesitation (`E10`); only Plan's three lines (`E11`); the Preflight report
  checked against the line on disk and by the plain check, as `docs/dispatch.md` now says (`E9`). `E6` was not
  exercised: no halt.

### Findings

- `E12` — `guess`. The order of the log entry's lines. Plan writes three of the template's lines, so later lines
  (`Preflight`, `Tokens`, `Gates`) must be slotted in somewhere, and the docs do not say whether the template's order
  holds. The runner kept the template's order; another might append. The check accepts either. Showed at `Plan` and
  every later write to the entry.
- `E13` — `guess`. Where a dispatch's token count comes from. `docs/dispatch.md` and `docs/formats.md` say "from the
  usage it reports", but the Preflight agent reported that it cannot see its own usage. The runner used the
  `subagent_tokens` figure the Agent tool returned. Iteration 2's runner did the same without remarking on it.
- `E14` — `minor`, as the runner tagged it. On a first pass, whether `Open work` is left empty or carries its six
  headings with no items. `docs/formats.md` answers it ("On a first pass the main session writes them empty"), and the
  runner left it empty, but the answer sits in another section than "5. Open work".

Watch, not a finding: WebSearch took about 300 s for one query in the Preflight dispatch. Orient, in `pool`, depends on
WebSearch.

Spot check: the `Dimensions` line against the input. 1 instance, 1 checked, 0 wrong.

### Fixes

The gate suites pass after them: 84 of 84, 49 of 49.

- `E12` — `docs/formats.md`, "1. Retrieval log": an entry's lines keep the template's order, so a line written later is
  put in its place.
- `E13` — `docs/formats.md`, the `Tokens` line, and `docs/dispatch.md`'s rule after every dispatch: the count is the one
  the harness returns with the agent's result (in Claude Code, the Agent tool's `subagent_tokens`), since an agent
  cannot see its own.
- `E14` — `docs/formats.md`, "5. Open work": a heading is written with its first item, so the section is empty until
  there is one. Fixed without another run, as a `minor`.

Sizes, in bytes, before → after: `docs/formats.md` 35581 → 35880; `docs/dispatch.md` 18764 → 18824.

### Result

Another iteration: `E12` and `E13` are `guess` findings. Neither comes from the last round's fixes, whose effects all
showed as intended, so the rule to stop patching does not apply.

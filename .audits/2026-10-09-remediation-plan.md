# Remediation plan for the audit of 2026-10-09

This plan is for the findings in `.audits/2026-10-09-docs-full-spec.md`. The IDs (`C1`, `M4`, …) are that audit's, and
each issue's evidence, rationale and remediation are there. This file says only what is done, in what order, and why in
that order.

## Principles

- `Decide before fixing.` Several simplifications delete code that has open findings. Fixing that code first would be
  wasted work, so the decisions come first, then the simplifications, then the fixes to what survives.
- `Code before docs.` The doc pass comes after the code, so the docs describe the final behaviour once.
- `One file group, one change.` Fixes are grouped by the file they touch, so each file changes once and parallel work
  never shares a file.
- `Every fix carries its test.` A fix to `tools/gates.py` or `tools/check.py` adds or updates its case in `tests/gates/`
  in the same commit. That is how `T8` gets done, rather than as a separate phase.
- `Not everything before the run.` The audit's main recommendation (`Z1`) is to stop growing the process and let a real
  run set the agenda. Items that only matter on a second pass of the same topic, and polish, wait until after the run.

## Decisions taken (2026-10-09, by the user)

- `Z2` adopted. Verification quotes only from the fetched full text. `snippet_search` serves only to locate passages.
  The `snippet` source level is dropped; a row is `full-text` or `abstract`.
- `Z3` adopted. The clustering measure is fixed to `combined`. The three-way choice and the tie rule go.
- `Z4` adopted. The null model is kept as a single draw, as the `no structure` guard only.
- `Z5` adopted. The temporal history is deferred: its log line, its `G2` requirement, its sheet section, its viewer
  panels and its extra clustering runs go.
- `Z7` adopted. The provisional clustering at step 2 goes. The `new` fringe route is seeded from the frontier candidates
  and the most-cited pool papers.
- `S1` decided. When the input declares no dimensions, the main session proposes names and values from the input at the
  step-0 Plan row. They are written in the `Dimensions` line in the declared form, and checked and verified like
  declared ones.

## Decisions taken in the second round (2026-10-09, by the user)

- `Z8` and `Z9` adopted, in Phase 1.
- `Topic name`: the legacy survey is renamed `reasoning-legacy`. This is done in Phase 0, because the gate tests build
  their fixture from it. `inputs/reasoning.md` stays, as the input for the rerun.
- `S2` is fixed in the procedure: after any dispatch that adds pool rows, the main session runs `late` (or `pool.py`
  before step 3) and pastes the `Pool` line before checking. The gate stays strict.
- `Z6` waits until after the run.

## Phase 0: before any change

- Confirm that the Semantic Scholar recommendations endpoint accepts a list of positive seed papers. `Z7` depends on it,
  and the audit marked it likely, not checked. One call settles it.
- Strengthen the test harness first, so that every later fix lands on a working net. These are the `T8` items:
  - `tests/gates/faults.py` asserts that the unmodified fixture passes;
  - both suites clean up in try/finally;
  - both use a unique topic name per run;
  - the no-op substitution at `tests/gates/behaviour.py:22` is fixed.
- Rename the legacy survey to `reasoning-legacy`: its survey, output, bib, `graphs/` directory, and a copy of its input
  under the new name. Point the tests and the docs that name the test source at it.
- Done when: both suites pass on an unchanged tree, a deliberately broken baseline fails `faults.py`, and
  `check.py reasoning-legacy` exits 0.

Status, 2026-10-09: done.

- `Z7`'s prerequisite holds without an API call: `tools/fringe.py:109` already sends a list of seeds
  (`positivePaperIds`) to the recommendations endpoint, and that call produced the 56 `new` candidates in
  `graphs/reasoning-legacy/fringe.json`.
- The rename is done. The survey's header and the output's first line name the new files, and the log entries keep the
  names they were written with.
- `faults.py`: the baseline passes, 48 of 48 faults are caught, and a deliberately broken baseline returns 1.
- `behaviour.py`: 20 of 20. Fixing the no-op at line 22 exposed a second hidden integrity failure in the waiver case:
  the dropped fringe row was cited in the output. The case now also asserts exit 0.
- A simulated crash after `build()` left no files behind.

## Phase 1: simplify

Apply the adopted decisions to code, tests and docs. The doc edits here are limited to what the deletion forces; the
full doc pass is Phase 3.

- `Z2` (verification):
  - `docs/verification.md`, `docs/formats.md` and `docs/gates.md`: the source levels become `full-text` and `abstract`;
  - every selected row's full text is fetched with `tools/fulltext.py`;
  - the source ranking in `tools/gates.py` is updated, and the legacy layout keeps accepting `snippet`;
  - the gate fixture's rows move from `snippet` to `full-text`, with real full-text quotes.
- `Z3`: remove the measure choice and the tie rule from `tools/cluster.py`, the viewer data and `docs/process.md`. Keep
  `text` and `refs` only as inputs to `combined`.
- `Z4`: one null draw, used only for `no structure`. Make sure `--nulls` cannot produce NaN curves.
- `Z5`: remove the history from `tools/cluster.py`'s pass path, the `Temporal stability` line and its `G2` requirement,
  the sheet section and the viewer panels. `tools/match.py history` can stay as an experiment.
- `Z7`: remove the provisional clustering row; reseed the `new` route in `tools/fringe.py`.
- `Z8`, `Z9`: if adopted.

Issues this phase resolves or makes moot:

- `M9` and `M10` go with `Z3`.
- `T1` is resolved by `Z2`, along with most of `S10`: the fallback discretion and the source ordering.
- `S3`, and the second half of `A7`, go with `Z7`.
- The history half of `M20`'s first item goes with `Z5`.

Done when: the test suites pass; `check.py reasoning` still exits 0 on the legacy survey; and a clustering run on a
scratch copy of `reasoning` still chooses about 6 clusters.

Status, 2026-10-09: done.

- `Z2`:
  - `check.py` accepts `source` `full-text` or `abstract` in the coreset layout, and `snippet` only in a legacy survey.
  - `G4` fails evidence quoted from a snippet.
  - The fixture's verified rows quote their own synthetic full texts.
  - The docs changed: `docs/verification.md` was rewritten (full text is the source, a snippet is a pointer, and
    snippets alone do not verify a row), plus `formats.md`, `gates.md`, `process.md` and `external_services.md` (the
    preflight rationale now names arXiv as the verification dependency), and `tooling.md`.
- `Z3`, `Z4`, `Z5`, `Z7`, `Z9`, done by a background agent:
  - The measure is fixed to `combined`. There is one null draw, used only for the `no structure` guard. `--rule` and
    `--nulls 0` are usage errors.
  - The history is gone from the pass path; `match.py history` remains as an experiment.
  - `fringe.py collect` needs no clustering. It seeds the `new` route from the `Orientation` frontier candidates plus up
    to 10 pool papers most cited within the pool.
  - `unstable cluster` and `broad scope` are printed notes, no longer diagnostics. `clusters.json` gains `notes` and
    `stability_from`.
  - `M13` is fixed along the way: when every cutoff is skipped, stability comes from resampling only, with a printed
    note.
  - Runtime on `reasoning-legacy` fell from 154.5 s to about 31 s, with identical assignments, clusterwise scores and
    fringe ranking. `graphs/reasoning-legacy/clusters.json` was regenerated in the new format.
  - The viewer's in-browser rendering is `UNVERIFIED`: headless Chromium could not start, so the page's script was
    checked with node only.
- `Z8`: the experiments moved to `docs/experiments.md`, indexed in `CLAUDE.md` as for human reviewers only. The history
  method is described there.
- Doc edits forced by the above, in `process.md`, `formats.md`, `tooling.md`, `dispatch.md`, `gates.md` and
  `coresets.md`:
  - the provisional-clustering row is removed;
  - `H8` now comes at step 3;
  - the `Temporal stability` line is removed, and the `G2` requirement for it goes with it;
  - the `Clustering` line format is new;
  - the `new` route's seeds are described.
- Checks: 49 of 49 faults (one new, for snippet evidence), 21 of 21 behaviours (one new, for a `snippet` source in the
  coreset layout). `check.py reasoning-legacy`, `sheets.py` and `graph.py` all pass.
- Not re-run live: the requirement that the most-cited seeds have at least one in-pool citation. It was checked offline.

## Phase 2: correctness, by file group

`2a` is the largest group and runs on its own. `2b` to `2e` touch disjoint files, so they can run in parallel, for
example as agents in separate worktrees.

### 2a. `tools/gates.py` and `tools/check.py`

Blocking items first:

- `S1`: `G0` reads proposed dimensions with values from the `Dimensions` line, and `G4` covers them.
- `M1`: quote matching with a minimum length, word-normalised, parts in order.
- `M2`: a row's `source` against its evidence; the evidence header ID against the file name.
- `C2`: a missing full text fails `--gate G4`.
- `M3`: an empty log line counts as missing; `Ended` must be well formed.
- `C3`: the "passed" note prints only when there are no failures.
- `S6`: an explicit "no rejections" record is accepted.
- `C1`: the note about trading pairs without a bridge.
- `S2`: the procedure fix is in Phase 3; here, only the `check.py` message, so that it names `late` or `pool.py` as the
  next step.

Then:

- `C4`: the safety net is kept during a pending halt.
- `C5`: the doc wording, or the reverse marker check.
- `C8`: no early return under `--gate` or `--status`.
- `M4`: parse the shapes of `Dissent searches`, `Tokens` and `Coverage test`, and the `Expansion` claim.
- `M5`: every `fringe.json` candidate has a judged row.
- `M6`: the gates a halted pass needs.
- `S4`: an overruled cluster proposal does not block convergence.

Each item gets its test case.

### 2b. `tools/inputs.py`

- `M18`: `*` and numbered bullets; the Oxford comma; duplicate sections; an empty `Topic`; `granularity: 0`; zero
  targets.
- The parser side of `S15`.

### 2c. `tools/cluster.py`, after Phase 1

- `M11`: the fringe score is ranked once, after mixing.
- `M12`: a date-based age cohort.
- `M13`: no NaN when every holdout cutoff is skipped.
- `M14`: scores computed on the intersection for sub-clusters.
- `M20`: subset rank normalisation in the holdout reruns.
- `C10`: the cluster parts — the match printout, the defaults, the exit code.
- `T9`: seeds and package versions in `params`, with versions pinned.

### 2d. `tools/assign.py`, `tools/fringe.py`, `tools/pool.py`, `tools/fulltext.py`, `tools/bib.py`

- `C9`: cut the PDF bibliography. This matters more after `Z2`, since full text becomes the only quoted source.
- `C6`: `add-fringe` uses the gate's test.
- `M15`: no year on the screening sheet.
- `M16`: rejected IDs are checked.
- `M17`: backfill the `arxiv` field.
- `A9`: clear messages instead of tracebacks.
- The plumbing parts of `C10`: the next-step hint, exit codes, the `RECLUSTER` rounding.
- The `bib.py` link parsing in `M20`.
- `T5`: batch `reject` and fringe judgements.

### 2e. `.claude/settings.json`

- `M19`: the Stop hook runs on `docs/` and `outputs/` only, and reports a missing mdformat.

Done when, for the whole phase: every finding above is fixed with a test where one applies; both suites and
`check.py reasoning` pass; and the scratch-topic simulations from the audit that showed each bug now fail or behave
correctly.

## Phase 3: spec coherence

One pass over `docs/`, `CLAUDE.md` and `.claude/agents/`, describing the code as Phases 1 and 2 left it.

- Wiring:
  - `W1`: the index row for `dispatch.md` includes `survey-pass`.
  - `W2`: an interim rule replaces the roadmap pointers.
  - `W3`: per-brief reading lists, by section, with the rationale moved out of agent reading.
  - `W4`: the bold-label references.
- Who writes what:
  - `S11`: the `writes` column becomes the single authority, with rows for `Halts`, `Waivers` and `Tokens`, and `Tokens`
    appended per dispatch.
  - `S12`: a halted parallel agent returns its Open work items.
- Rubrics:
  - `A1`: scope, and a stopping rule for Orient and Expand.
  - `A2`: frontier and impact defined; Naming records each `high` cluster's central claim.
  - `A3`: the change rubric for the coverage verdict, with every sampled candidate recorded.
- Checklist rows and briefs:
  - `A4`: the step-3 loop of targeted expansions.
  - `A5`: themes in the `Orientation` line.
  - `A6`: the Orient brief's gaps.
  - `A7`: the remaining done-when conditions.
  - `A8`: step 6's reading and checking.
  - `S4`: the step-7 rows for a proposed cluster.
- Statements:
  - `S5`: state the coverage test's statistical strength.
  - `S7`: one level rule.
  - `S9`: the measured numbers replace the stale ones.
  - `S10`: what remains after `Z2` — evidence for every non-`n/a` cell; verifying a draft is not a correction; the
    replacement search goes to Selection.
  - `S14`: the stale statements.
  - `S15`: a skeleton input in `docs/formats.md`.
  - `C10`: the doc side of the defaults.
- The doc side of `S1` and `S2`.

Done when: a fresh tabletop run of a first pass, as in the audit, finds no stalls on the rows it found before. Run it as
an agent, blind to this plan.

## Phase 4: instrument the run

What turns the run into a measurement rather than a demo:

- `T4`: `tools/coverage.py`. It prints the coreset's coverage radius (max and p90), and draws the coverage-test sample
  from the worst-covered pool papers, with the seed recorded.
- The tool half of `A3`: the sample above is written as a per-round sheet with a verdict column, as `fringe-screen.md`
  is.
- `T3`: a blind re-verification of a random 10% of rows, at least five. A fresh agent sees only the paper ID and the
  column definitions, and the agreement rate goes in the log.
- `T2`: a script that pairs each output sentence with its cited rows and evidence quotes. An independent agent judges a
  sample.
- `T6`: print one section of a survey.

Done when: each tool runs on the gate fixture, and the briefs that use them name them.

## Phase 5: the runs

1. The topic name is settled: the legacy survey is `reasoning-legacy` (Phase 0).
2. Run a smoke pass on a small new topic, about 50 pool papers, from a Topic-and-Context-only input. This exercises
   every row cheaply and catches plumbing failures before the expensive run. Log every improvisation as a spec bug.
3. Fix what the smoke pass found.
4. Rerun `reasoning` in the coreset layout. Compare the result with the legacy output: which of the legacy output's
   claims a coreset of about 50 rows reproduces, and which it loses. Record per-dispatch tokens, the `T3` agreement
   rate, the `T2` faithfulness sample, and the coverage radius with each coverage round.

## After the run

These items are deferred deliberately. Each matters only on a second pass of a topic, or should be shaped by what the
run shows.

- History checks:
  - `Z6`: decide how far to simplify them.
  - `C7`, `M7`, `M8`: fix within whatever shape `Z6` leaves; they bite on later passes and across commits.
- Later passes:
  - `S8`: keep the previous level across passes unless it falls below τ.
  - `S13`: the procedure for reusing verified rows from an earlier survey.
- Built only if the run shows the need:
  - `T7`: the `--next` driver, if the run shows the main session losing its place in the checklist.
  - `W3`'s second step: trim the reading lists further, once spec reading is measured.
- Minor:
  - the `hidden` route's fixed 60 (`M20`), which mainly matters on small pools.
- Anything the runs surface.

## Index: where each audit ID goes

| IDs | where |
| -- | -- |
| `Z2`, `Z3`, `Z4`, `Z5`, `Z7`; `Z8`, `Z9` if adopted | Phase 1 |
| `M9`, `M10`, `T1`, `S3` | moot after Phase 1 |
| `T8` | Phase 0, then with every fix |
| `S1`, `S2`, `S4`, `S6`, `C1`–`C5`, `C8`, `M1`–`M6` | Phase 2a |
| `M18` | Phase 2b |
| `M11`–`M14`, `T9` | Phase 2c |
| `C6`, `C9`, `M15`–`M17`, `A9`, `T5` | Phase 2d |
| `M19` | Phase 2e |
| `C10`, `M20` | split across Phase 2c and 2d by part; `M20`'s hidden-route item after the run |
| `W1`–`W4`, `S5`, `S7`, `S9`–`S12`, `S14`, `S15`, `A1`–`A8` | Phase 3; `S10` and `A7` only what remains after Phase 1 |
| `T2`, `T3`, `T4`, `T6`; tools for `A3` | Phase 4 |
| `Z1` | the plan as a whole; `T7` after the run |
| `Z6`, `C7`, `M7`, `M8`, `S8`, `S13`, `T7` | after the run |

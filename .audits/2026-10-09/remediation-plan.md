# Remediation plan for the audit of 2026-10-09

This plan is for the findings in `.audits/2026-10-09/docs-full-spec.md`. The IDs (`C1`, `M4`, …) are that audit's, and
each issue's evidence, rationale and remediation are there. This file says only what is done, in what order, and why in
that order. What was actually done, per ID, is in `.audits/2026-10-09/disposition.md`.

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

## Items raised after the audit (2026-10-10)

These came from a discussion of what `Z2` costs: full-text-first verification. They carry `R` IDs so that the index can
place them.

- `R1` — batch the full-text fetch. Verification runs as parallel agents. If each fetches its own papers, every process
  keeps arXiv's 3-second spacing only for itself, so together they exceed it. Instead, the main session runs
  `uv run tools/fulltext.py <topic> --abstract` once, before dispatching verification. At the measured 27 papers in 90
  seconds, that is about 3 minutes for 60 rows.

- `R2` — a section reader for full texts. A command along the lines of `fulltext.py show <topic> <id> [<pattern>]`:

  - it prints the paper's outline: every heading, with its size in tokens;
  - it prints the passages matching a pattern, each under its section heading, capped in size;
  - it can print whole sections by name. It makes "read only the matching sections" the easy path, rather than a rule an
    agent must remember. Reading the outline and the sections where unprompted caveats live (Limitations, Discussion,
    Conclusion) also raises recall for what a targeted Grep cannot know to look for.

- `R3` — record how many papers have an arXiv ID. This is an information point, not a requirement.

  - `pool.py` prints it in the `Pool` line ("N papers in scope, A with an arXiv ID"), and `check.py` prints it for the
    coreset beside the `source` tally.
  - The viewer shows it, for example as a colour mode or a count in its overview.
  - It also tells us, per topic, how much the non-arXiv backup (`R5`) would matter.

- `R4` — measure how much targeted reading misses. This is an experiment, and it decides how verification reads a paper.
  The question: does a strong agent that reads only by Grep, or by the section reader, find what a full reading finds?
  Verification has two jobs:

  - confirming the claims a draft row already makes, which targeted search does well;
  - catching what the draft left out: author-stated limitations, conditions on a result, a dissent paper that turns out
    to agree. Targeted search is weak there, because it only finds what the agent already knew to look for.

  The test bed is the 27 abstract-sourced rows of `reasoning-legacy`. Their full texts are already on disk, and the rows
  need verifying anyway. The arms:

  - `A` — a strong agent with Grep and the section reader (`R2`);
  - `B` — a cheap-model locator (for example Haiku) reads the whole paper in its own context, and returns a map of where
    the method, the setup, each headline number, the limitations and the assumptions are, with quotable sentences. The
    strong agent then reads only those places;
  - `C`, the reference — a strong agent reads the whole paper, on a subsample of about 8 papers.

  The measures, per row: tokens, by model; cells confirmed and corrected; limitations and conditions found; and what `A`
  and `B` missed relative to `C`. A locator's map is safe for precision: every quote still has to be found verbatim in
  the full text by `check.py`, so a hallucinated location fails the gate. It is not safe for recall, which is what the
  experiment measures.

  It runs outside the pass loop, so the dispatch rules of a pass do not bind it, and agent nesting does not matter
  (user, 2026-10-10). The main session orchestrates: it dispatches cheap-model locator agents (arm `B`) and strong
  agents (arms `A` and `B`) on the papers, does the reference reading of arm `C` on the subsample itself, and compares.
  To keep the reference honest, do arm `C` before reading the outputs of `A` and `B`, and record its findings first. If
  the locator is adopted, how a pass would call it is settled afterwards.

  The cost of `B` also needs current per-model pricing, which this plan does not assume.

- `R5` — a backup for papers with no fetchable full text: accept `snippet` again, for those papers only, and only from a
  tool that saves the raw `snippet_search` results, so that the quotes can be checked. This is the audit's alternative
  to `Z2`. Build it only if `R3` shows a topic where such papers are a real share of the coreset.

- `R6` — measure verification cost. Compare verification tokens per row in the smoke pass against the ~10k estimate,
  which comes from snippet-based passes. If it is much higher, check first whether agents read whole files.

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

Status, 2026-10-09: done. What was done, per ID, with its judgement calls and caveats, is in
`.audits/2026-10-09/disposition.md`.

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

Status, 2026-10-09: done. What was done, per ID, with its judgement calls and caveats, is in
`.audits/2026-10-09/disposition.md`.

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
- `R2`: the section reader in `tools/fulltext.py`.
- `R3`: the arXiv share in `pool.py`'s `Pool` line, in `check.py`'s printout, and in the viewer (`graph.py`). `check.py`
  belongs to `2a`, so add its line there, or after `2a` lands.

### 2e. `.claude/settings.json`

- `M19`: the Stop hook runs on `docs/` and `outputs/` only, and reports a missing mdformat.

Done when, for the whole phase: every finding above is fixed with a test where one applies; both suites and
`check.py reasoning` pass; and the scratch-topic simulations from the audit that showed each bug now fail or behave
correctly.

Status, 2026-10-10: done. What was done, per ID, with its judgement calls and caveats, is in
`.audits/2026-10-09/disposition.md`.

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
- `R1`: the step-5 checklist row has the main session batch-fetch full texts before dispatching verification.
- The doc side of Phase 2, as its agents reported it:
  - `docs/formats.md`:
    - inputs: sections are `##` headings, each once; bullets may be `-`, `*`, `+` or numbered; a values list may end in
      "or" or "and"; `granularity` above 0; at least one target left after the drops; prose in `Coreset Spec` as
      paragraphs or nested bullets;
    - log lines: the `Dimensions` form above; `; rejected: none` in `Expansion`; the `Expansion` traversal form
      `backward from <id> (<n>), ...`; `Dissent searches` entries separated by `|`, with `found: <id>`; the `Pool` line
      with its arXiv count;
    - the screening sheet without `year`.
  - `docs/gates.md`:
    - the new and changed requirements: `G0` proposed dimensions; `G1` every candidate screened, with reasons of a few
      words; `G3` dissent searches parsed; `G4` quote length and order, header ID, method from the full text, dissent
      evidence, a missing full text failing `--gate`; `G5` the `Coverage test` N and K, `Tokens`, `Ended`;
    - halted passes; a pending halt and the safety net;
    - `C5`'s wording.
  - `docs/verification.md`:
    - quotes of at least 6 words per part;
    - the section reader as the first way into a paper, pending `R4`;
    - `[page N]` locations for PDF text.
  - `docs/tooling.md`:
    - the `add` hint; `reject` from stdin; `fringe.py judge` and `maybe`; `collect` skipping rejected papers;
    - the `pool.py` backfill; the PDF cut; `fulltext.py show`; the viewer's arXiv mode;
    - the defaults (k 10, c 10, reps 20, nulls 1, τ 0.75, cohort 30), the new `params` keys, exit 2 on usage errors, and
      pinned versions;
    - the Stop hook's scope.
  - `docs/process.md`:
    - the fringe score (the cohort, the rescaled mix, the reading "further than 95% of its cohort", at a resolution of
      1/30);
    - the holdout re-measured on its own;
    - sub-cluster scores on the part itself;
    - the `changes:` printout;
    - seeds in `params`;
    - screening with `fringe.py judge`; `maybe` resolved before `add-fringe`;
    - the blindness claim, which now holds.
  - `docs/dispatch.md` and `.claude/agents/survey-pass.md`: screening with `fringe.py judge`.

Done when: a fresh tabletop run of a first pass, as in the audit, finds no stalls on the rows it found before. Run it as
an agent, blind to this plan.

Status, 2026-10-10: done. What was done, per ID, with its judgement calls and caveats, is in
`.audits/2026-10-09/disposition.md`, including what the tabletops found and how each finding was handled. Three
tabletops ran (20, 14 and 17 findings). The third did not converge; by agreement, its findings moved to the
disposition's "Watch in the first run" unfixed, and Phase 4 proceeds.

## Phase 4: instrument the run

First, a fix left over from Phase 3 (TODO 1): on a return to step 3, `--gate G2` and `G3` cannot pass until Revise is
done, since a `Coverage test` line makes `check.py` require every gate to `G4`. Add one sentence to `docs/process.md`,
"Returning to step 3": on a return, skip re-gating until Revise is done. The finding is in the disposition, "What the
Phase 3 tabletops left open".

What turns the run into a measurement rather than a demo:

- `T4`: `tools/coverage.py`. It prints the coreset's coverage radius (max and p90), and draws the coverage-test sample
  from the worst-covered pool papers, with the seed recorded. Until then the coverage sample is hand-drawn, and
  `docs/process.md` marks its bounds as indicative.
- The tool half of `A3`: the sample above is written as a per-round sheet with a verdict column, as `fringe-screen.md`
  is.
- `T3`: a blind re-verification of a random 10% of rows, at least five. A fresh agent sees only the paper ID and the
  column definitions, and the agreement rate goes in the log.
- `T2`: a script that pairs each output sentence with its cited rows and evidence quotes. An independent agent judges a
  sample.
- `T6`: print one section of a survey.
- `R4`: the verification-recall experiment, on `reasoning-legacy`'s 27 abstract-sourced rows. Its result decides whether
  the Verification brief uses a cheap-model locator (arm `B`) or the section reader alone (arm `A`). Record it in
  `docs/experiments.md`.

Done when: each tool runs on the gate fixture, the briefs that use them name them, and `R4` has decided the reading
method.

## Phase 5: the runs

1. The topic name is settled: the legacy survey is `reasoning-legacy` (Phase 0).
2. Run a smoke pass on a small new topic, about 50 pool papers, from a Topic-and-Context-only input. This exercises
   every row cheaply and catches plumbing failures before the expensive run. Log every improvisation as a spec bug.
3. Fix what the smoke pass found.
4. Rerun `reasoning` in the coreset layout. Compare the result with the legacy output: which of the legacy output's
   claims a coreset of about 50 rows reproduces, and which it loses. Record per-dispatch tokens, the `T3` agreement
   rate, the `T2` faithfulness sample, and the coverage radius with each coverage round.

In both runs, measure verification tokens per row (`R6`), and run the batch fetch before verification (`R1`).

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
- `R5`: the snippet backup for papers with no fetchable full text, if `R3` shows a topic that needs it.
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
| `C6`, `C9`, `M15`–`M17`, `A9`, `T5`, `R2`, `R3` | Phase 2d (`R3`'s `check.py` line in 2a) |
| `M19` | Phase 2e |
| `C10`, `M20` | split across Phase 2c and 2d by part; `M20`'s hidden-route item after the run |
| `W1`–`W4`, `S5`, `S7`, `S9`–`S12`, `S14`, `S15`, `A1`–`A8` | Phase 3; `S10` and `A7` only what remains after Phase 1 |
| `T2`, `T3`, `T4`, `T6`, `R4`; tools for `A3` | Phase 4 |
| `R1` | Phase 3 (the step-5 row), used in Phase 5 |
| `P1`–`P14` (found by Phase 3's tabletops; defined in the disposition) | Phase 3 |
| `R6` | Phase 5 |
| `R5` | after the run, if needed |
| `Z1` | the plan as a whole; `T7` after the run |
| `Z6`, `C7`, `M7`, `M8`, `S8`, `S13`, `T7` | after the run |

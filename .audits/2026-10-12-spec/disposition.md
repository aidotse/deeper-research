# Disposition: spec audit of step 2 (expand), 2026-10-12

## How to read this document

This is the third of the audit's three documents. It records what was done for each ID of the audit, `expand.md`, and of
the plan, `remediation-plan.md`, as each phase lands. The simulation findings `E15`–`E20` are defined in
`.audits/2026-10-12-sim/model-collapse/segments/pool.md`, and are accounted for here where the plan fixes them.

Each outcome entry starts with the ID, its outcome and its commit. The outcome is one of `fixed`, `adopted`, `moot`,
`partial`, `deferred` or `pending`. Then it says what was done, any departure from the plan and why, how it was
verified, and what to watch.

## By phase

| phase | IDs | commits | state |
| -- | -- | -- | -- |
| 1, independent fixes | `A4`, `A5`, `C2`, `A1` (its docs part), `E16`, `E17` | `ac34b92` | done |
| 2, the code | `A2`, `Z1`, `C1`, `C3`, `M1`, `M2`, `S5`, `S6`, `S7`, `A3`, `T1`, `T2`, `E15`, `E18`–`E20`, `P2`–`P12` | `79ae39f` | done |
| 3, the docs | see the plan | — | pending |
| 4, the simulation | — | — | pending |

## Commits

- `ac34b92` — phase 1.
- `79ae39f` — phase 2.

## Outcomes

### Phase 1: independent fixes

- `A4` — `fixed`, `ac34b92`. `.claude/agents/survey-pass.md`: "every row you select should earn its place in a role",
  followed by a sentence that the pool is different, since every paper in scope enters it. Departure: the plan proposed
  only the rewording; the second sentence was added so that the definition points the other way from before, not just
  away from scope. Verified by reading.
- `A5` — `fixed`, `ac34b92`. `inputs/model-collapse.md`'s `exclude` gains the user's line on detection, watermarking and
  curation papers. `tools/inputs.py model-collapse` exits 0. In the simulation audit, `plan` is again not rerun, since
  no line it writes reads `exclude`, and the tag `sim-checkpoint-model-collapse-plan` moved to the commit after
  `ac34b92`. Watch: whether screening agents apply the line consistently, in `pool` iteration 2's spot checks.
- `C2` — `fixed`, `ac34b92`. `docs/external_services.md`, "Fields": `fields` trims the result, and some tools add
  `authors` and `openAccessPdf` unasked.
- `A1` — `partial`, `ac34b92`. The same bullet says to ask for `externalIds`, the field that holds the arXiv ID and
  corpus ID `tools/assign.py` needs. This is the part orientation still needs. The rest, for step 2, is moot under the
  design (phase 2), and the Orient brief's own mention of the field lands with phase 3.
- `E16`, `E17` — `fixed`, `ac34b92`. A new section of `.claude/agents/survey-pass.md`, "Tools and files": only the
  repo's scripts and the agent's own tools, no programs of its own, saved or inline, no file its brief does not name,
  and a missing tool is reported, not built. The same rule for the main session in `docs/dispatch.md`, "Rules for the
  main session". Watch: in `pool` iteration 2, whether a runner with no tool for a job now stalls and reports, as
  intended.

Both gate suites pass after the phase: 84 of 84 faults, 49 of 49 behaviours.

### Phase 2: the code

Verified by both gate suites after the phase, 92 of 92 faults and 69 of 69 behaviours, and by one live run of `collect`
on a scratch topic (`P2`). Watch for all of it in `pool` iteration 2, the first real run.

- `A2`, `Z1`, `E18` — `partial`, `79ae39f`. The code of the design: `tools/expand.py` (`collect`, `collect --targeted`,
  `judge`), `tools/screen.py`, `tools/assign.py add-expand`, and `G1`'s new checks. The docs follow in phase 3; whether
  screening now fits in capped dispatches is for phase 4 to show.
- `C1`, `T1`, `T2` — `fixed`, `79ae39f`. `G1` checks `expand.json`: a backward and a forward traversal per seed and
  frontier candidate, a search per theme, every row of this pass judged and acted on, and the `Expansion` line equal to
  the one the files give. Faults `g1.expansion-*` (11) and `g1.orientation` (3).
- `C3` — `fixed`, `79ae39f`. The shared `judge` refuses a `yes` or `no` with fewer than two words, on both sheets.
- `M1` — `fixed`, `79ae39f`. Citer lists come whole from the batch endpoint, or are paged when shorter than the paper's
  count; a list past the endpoint's offset limit is marked `capped` in the line.
- `M2` — `fixed`, `79ae39f`. Both collectors drop a candidate whose title matches a pool paper (`tools/screen.py`,
  `pool_titles`).
- `S6` — `partial`, `79ae39f`. `collect` and `G1` accept seeds or frontier candidates, either one. What the main session
  does with neither is phase 3's wording.
- `S7` — `fixed`, `79ae39f`. Entries without a paper ID are counted, per source, in the line.
- `S5`, `A3` — `moot`, `79ae39f`. The sheet is the record of progress, and the counts come from the script.
- `E15` — `fixed` in the code, `79ae39f`: every row carries its abstract, or `(no abstract)` (`P1`, phase 3).
- `E19` — `fixed`, `79ae39f`: a verdict is replaced on the sheet with `judge` before `add-expand`.
- `E20` — `moot`, `79ae39f`: traversal and searches are one script run.
- `P2`–`P12` — `fixed`, `79ae39f`, as the plan describes each.

## Not mapped to a phase

None yet.

## Pending

Phases 3–4, as the plan sets them out. Phase 3, the docs, was started on 2026-10-13 with one code change it needed:
`tools/expand.py collect` takes `--query` and `--why` without `--targeted`, for an expected theme with no cluster (a
search alone, the region named by its theme), and prints `STOP: H14` when `Orientation` names neither seeds nor frontier
candidates (`S6`). Left to write, in this order:

- `docs/process.md`: the overview's expansion line; a new `H14` in "When a pass ends"; the order of operations' step 2
  rows (collect, screening in blocks of at most 100 rows, in parallel, add-expand, fetch), the fringe screening row's
  brief, and the targeted-expansion row (`collect --targeted/--query`, its 5 papers most cited within the pool, 2
  thinnest regions on `no stable level`: `A8`); step 1's themes including the input's other names (`A9`); step 2
  rewritten for the script, required work only (`A6`, `A7`, `S1`); "Screening for scope", the `(no abstract)` rule
  (`P1`) and "When to stop" for orientation only; "Fringe routes", the title match; step 3's "The Expand agent"
  sentence.
- `docs/dispatch.md`: the Screening brief in place of Expand and Fringe screening (a sheet and a row range, reads the
  input's `Topic` and `Clustering`, `W2`; blind for the fringe sheet); the Orient brief (`A9`, `externalIds`: `A1`); the
  parallel rule (screening dispatches write the sheet through the lock, not the pool).
- `docs/formats.md`: the `Expansion` template and its notes, now printed by `add-expand`; the list of script-printed
  lines; `expand.json` and `expand-screen.md` under `graphs/<topic>/`; `rejected.md`'s writers.
- `docs/tooling.md`: a section for `tools/expand.py` and `tools/screen.py`; `add-expand` under "Pool table"; "Fringe
  candidates" (two-word reasons, title match).
- `docs/external_services.md`: the Asta tools table (expansion no longer uses Asta), the Graph API's users and the
  batching and resume of `collect`.
- `docs/gates.md`: the `G1` row and the trace line for expansion.
- `.claude/agents/survey-pass.md`: "Leaving a trace" and "Reading the files" (the expansion sheet).
- Then a check of the docs against the code by a fresh agent, as the plan says.

### Watch in the next run

- `A5`, `E16`, `E17`: see their entries above.
- `P2`: whether the shared Graph API pool lets `collect` through, and how often a run must resume, until the user's
  Semantic Scholar key arrives.

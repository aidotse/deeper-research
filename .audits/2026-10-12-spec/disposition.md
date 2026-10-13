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
| 3, the docs | `S1`, `S4`, `S6`, `W1`, `W2`, `A1`, `A6`–`A9`, `Z2`, `P1`, `P13`; the docs of phase 2's IDs | `b876f00`, `97a23f0` | done |
| 4, the simulation | — | — | pending |

## Commits

- `ac34b92` — phase 1.
- `79ae39f` — phase 2.
- `b876f00` — phase 3's one code change (`S6`).
- `97a23f0` — phase 3, the docs.

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

### Phase 3: the docs

Verified by both gate suites after the phase, 92 of 92 faults and 71 of 71 behaviours, and by a fresh agent's check of
the docs against the code, whose twelve findings are in the plan: eleven fixed in the docs, one deferred (`P14`). The docs edited: `docs/process.md`, `docs/dispatch.md`, `docs/formats.md`,
`docs/tooling.md`, `docs/external_services.md`, `docs/gates.md` and `.claude/agents/survey-pass.md`.

- `A2`, `Z1`, `E18` — `fixed`, `97a23f0`. The docs of the design: the order of operations' step 2 rows (collect, screen,
  add, fetch), step 2's prose, the `Expansion` line as `add-expand` prints it, the two new files under
  `graphs/<topic>/`, and new sections in `docs/tooling.md`, "Expansion candidates" and "Screening sheets". Whether
  screening fits in capped dispatches is for phase 4 to show.
- `S1` — `fixed`, `97a23f0`. Forward traversal from the seeds and the frontier candidates is required work, in the collect
  row and step 2's prose.
- `S4` — `moot`, `97a23f0`. `rejected: none` is gone from the template, the notes and the `G1` row.
- `S6` — `fixed`, `b876f00` and `97a23f0`. A new halt, `H14`: neither seeds nor frontier candidates. `collect` prints
  `STOP: H14`; step 1 and "When a pass ends" say what the user decides.
- `W1` — `fixed`, `97a23f0`. The Expand brief is gone. The required work's done-when sits in the script rows, which the
  main session runs.
- `W2` — `fixed`, `97a23f0`. The Screening brief, in place of Expand and Fringe screening, reads the input's `Topic` and
  `Clustering`.
- `A1` — `fixed`, `97a23f0`. The Orient brief asks Asta for `externalIds`.
- `A6` — `moot`, `97a23f0`. Expansion has no stopping rule; "When to stop" keeps orientation's alone.
- `A7` — `fixed`, `97a23f0`. The `snippet_search` sentence and the date-restricted queries are gone from step 2, and the
  `Dates` bullet of `docs/external_services.md` no longer tells agents to use them for recent work.
- `A8` — `fixed`, `97a23f0`. A targeted expansion traverses from the region's 5 papers most cited within the pool, as the
  naming sheet lists them; on `no stable level`, the 2 thinnest regions, the two smallest clusters, are expanded. Both
  are stated as first guesses. Departure: the plan left the targeted round's query to "the region's theme"; the docs
  say the main session words it from the region's titles, or takes it from the `expect` line or the coverage round,
  since a cluster has no name before Naming.
- `A9` — `fixed`, `97a23f0`. The themes include every other name the input gives the topic: in the Orient brief, step 1,
  the order of operations, and `docs/formats.md`'s `Context` and `Orientation` notes.
- `Z2` — `moot`, `97a23f0`. The order of operations is rewritten for step 2. The fetch row is no longer a duplicate: pool
  rows now enter through `add-expand`, which the main session runs, so no dispatch's "After every dispatch" fetch comes
  before it. The fringe routes need that fetch first.
- `P1` — `fixed`, `97a23f0`. "Screening for scope": a `(no abstract)` row is judged from its title, and borderline is in.
- `P14` — `deferred`, with `S2`. A gap the docs check found; the docs now state it. See the plan.
- `P13` — `fixed`, `97a23f0`. Found while writing the Screening brief: the fringe sheet now numbers its rows, so that it
  too can be handed over in ranges of at most 100. Recorded in the plan.

## Not mapped to a phase

None yet.

## Pending

Phase 4: `pool` iteration 2 of the simulation audit, from the `plan` checkpoint, with a rebuilt scratch copy.

### Watch in the next run

- `A5`, `E16`, `E17`: see their entries above.
- `P2`: whether the shared Graph API pool lets `collect` through, and how often a run must resume, until the user's
  Semantic Scholar key arrives.
- Phase 3: whether the main session hands out ranges of at most 100 rows and runs them in parallel; whether screening
  agents send verdicts with `printf`, as `docs/tooling.md` shows, rather than a program; and how the main session words
  a targeted round's query.

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
| 2, the code | see the plan | — | pending |
| 3, the docs | see the plan | — | pending |
| 4, the simulation | — | — | pending |

## Commits

- `ac34b92` — phase 1.

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
  main session". Watch: whether a runner with no tool for a job now stalls and reports, as intended, in `pool` iteration
  2\.

Both gate suites pass after the phase: 84 of 84 faults, 49 of 49 behaviours.

## Not mapped to a phase

None yet.

## Pending

Phases 2–4, as the plan sets them out.

### Watch in the next run

- `A5`, `E16`, `E17`: see their entries above.

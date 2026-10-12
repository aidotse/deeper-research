# Runner report: `model-collapse`, pass of 2026-10-12, step 0

The pass halted at the second row of step 0. `tools/preflight.py` exited 1 because the arXiv API timed out. The halt is
recorded as `H1`, with the decision `pending`. Gate `G0` was not run, for the reason given under `guess` 2 below.

## 1. Rows run

1. `0 Plan` — first pass, so no `--status` call before it. `python3 tools/inputs.py model-collapse` exited 0. It read 3
   declared dimensions (`evidence`, `regime`, `modality`), the steering (`expect` and `exclude`), and the targets
   `Landscape, Assumptions, Gaps, Conditions; then Questions, Reading`. I wrote `surveys/model-collapse.md` with its
   five empty section headings. I also wrote the log entry `### Pass 2026-10-12`, with `Dimensions: declared in the
   input`, and `Halts` and `Waivers` as `none`. Done when: met.
2. `0 Preflight: scripts` — `python3 tools/preflight.py` exited 1. It printed:
   `Graph API ok | arXiv failed (API unreachable (TimeoutError), HTML 200) | uv ok | Asta key set`, then
   `STOP: H1 — preflight failed: arXiv`. Done when (`exit 0`): not met. The row says exit 1 halts the pass (`H1`).
3. `any On a halt` — I replaced `Halts: none` with the `H1` entry, decision `pending`. Then
   `python3 tools/check.py model-collapse` exited 0 (`OK`), with the note `halt pending (H1): no further gate passes
   until the user decides`. Done when ("the user has decided"): not met, and waiting on the user.

These rows were not run:

- `0 Preflight: Asta and WebSearch`. Its input is a passing script printout, and the pass had already halted.
- `0 Gate G0`. See `guess` 2.

## 2. Stalls, guesses, improvisations and tool failures

1. `Preflight: scripts` — `blocker`. The arXiv API check timed out after 60 s, while the arXiv HTML page answered 200.
   The docs say exit 1 halts the pass, so I halted. I did not dispatch the Preflight agent and did not run `G0`.
2. `Gate G0` — `guess`. Two instructions pulled in opposite directions. The run setup says to stop once `G0` has run,
   whether it passes or not. It also says to record a halt and stop. `docs/process.md` adds that each row's `done when`
   must hold before the next row starts. The halt is the more specific instruction, so I stopped before `G0`. The code
   settles the outcome anyway. In `tools/gates.py`, around line 1074, `--gate G0` fails with
   `G0 cannot pass while a halt is pending: H1`. Another agent might have run the gate to show that failure.
3. `Preflight: scripts` — `guess`. I did not rerun `tools/preflight.py` to see whether the timeout was transient. The
   docs give no retry for preflight. A pass that rerun the script until it passed would quietly override the halt.
   Another agent might have retried once.
4. `Preflight: scripts` — `guess`. I did not write a `Preflight` line. The row's `writes` column says the printout goes
   to the next row, and the Preflight agent writes the whole line. The script's half is preserved in the `Halts` entry
   and in this report.
5. `On a halt` — `guess`. The docs give the `Halts` form, `<id> — <what happened> — pending`, but not how much detail
   "what happened" should hold. I included the failing check, the checks that passed, and the fact that the Asta tools
   and WebSearch were never checked. I used commas, not semicolons, because `;` separates entries.
6. `On a halt` — `minor`, possibly a tool bug. Two oddities appeared once `H1` was recorded:
   - `python3 tools/check.py model-collapse --status` lists `G0 ready passed`, even though the log has no `Preflight`
     line. Before the halt was recorded, the plain check failed `g0.preflight`.
   - The cause is `r_preflight` in `tools/gates.py` (line 215). It returns success whenever `H1` appears in `Halts`,
     whatever the decision.

   Why this matters: once the user decides to continue, `G0` can pass with no `Preflight` line at all. The Asta tools
   and WebSearch would then never have been checked. In this run they have not been. If the user continues, the
   Preflight agent should still be dispatched before Orient.
7. `Plan` — `minor`. The docs do not settle the survey's `#` title. I used `# Survey: model collapse`, matching
   `surveys/reasoning-legacy.md`.
8. `Plan` — `minor`. The plain check run right after Plan failed `g0.preflight`. That is expected at that point, and
   Plan's `done when` does not involve the check.

## 3. Halts and waivers

- `H1` — `tools/preflight.py` exited 1 at step 0. The arXiv API was unreachable (`TimeoutError`) while the arXiv HTML
  returned 200. Graph API, `uv` and the Asta key were ok. The Asta tools and WebSearch were not checked. Status:
  `pending`, recorded in the log's `Halts` line.

  The user's options are to rerun the preflight later or to proceed without the arXiv API. If they proceed, the output's
  legend must say what was missing. Either way, the Preflight agent still has to run before Orient.
- Waivers: none.

## 4. Dispatches

None. No `Tokens` line was written, because the docs append to it per dispatch and there were none.

## 5. Reading

These went beyond the doc sections my rows strictly needed:

- `docs/dispatch.md`, read whole. I needed the main-session rules and the Preflight brief, and I read the other briefs
  along with them.
- `docs/gates.md`, read whole. Its index entry says to read it before planning a pass.
- `docs/formats.md`, lines 86–375. I needed `Dimensions`, the survey's sections and the retrieval log. The range also
  took in Clusters, Coreset, Pool and Open work.
- `docs/tooling.md`, lines 1–100. I needed the Consistency check, Preflight and Input sections.
- `tools/preflight.py`, its first 80 lines, to see what the arXiv check tests.
- `tools/gates.py`, a grep and two short excerpts (`r_preflight`, and the pending-halt hold). I read them to work out
  whether `G0` could pass while `H1` is pending, after `--status` reported it as passed.
- `surveys/reasoning-legacy.md`, its first 30 lines, to match the survey title form.
- Accidental: my first `ls -R` printed the names of directories inside `.git` (`objects/`, `refs/` and so on), because
  of the RTK wrapper. I read no git history or object contents, and nothing outside this directory.

## 6. Outside calls

- Asta: 0.
- WebSearch: 0.
- WebFetch: 0.
- The script `tools/preflight.py` made its own HTTP requests to the Graph API and arXiv. It ran once.

# Runner report: `model-collapse`, pass of 2026-10-12, step 0

The run went from `Plan` through Gate `G0`, and `G0` passed. It stopped there, before step 1 (`Orient`).

## 1. Rows run

1. `0 | Plan`. This is a first pass: `surveys/model-collapse.md` did not exist, so `tools/check.py --status` did not
   apply. `python3 tools/inputs.py model-collapse` exited 0. It found 3 declared dimensions (`evidence`, `regime`,
   `modality`), the clustering steering (`expect` and `exclude`), and the targets `Landscape`, `Assumptions`, `Gaps`,
   `Conditions`, then `Questions` and `Reading`. I wrote `surveys/model-collapse.md` with the title `# Model collapse`
   (the input's own), the five `##` headings, and the entry `### Pass 2026-10-12` with only `Dimensions: declared in
   the input`, `Halts: none` and `Waivers: none`. `Done when` was met.
2. `0 | Preflight: scripts`. `python3 tools/preflight.py` exited 0, with Graph API, arXiv and `uv` ok and the Asta key
   set. `Done when` was met.
3. `0 | Preflight: Asta and WebSearch`. I dispatched `survey-pass` with the "Preflight" brief. Its report had no
   `STOP:`. It wrote the whole `Preflight` line, all nine checks ok. I checked that the line on disk matches what the
   report says. `Done when` was met.
4. `any | After every dispatch`, for the Preflight dispatch. No pool rows were added and the coreset did not change, so
   neither `tools/bib.py` nor `tools/pool.py` was due. I appended `Tokens: Preflight: 35731`.
   `python3 tools/check.py model-collapse` exited 0 (`OK`). `Done when` was met.
5. `0 | Gate G0`. `python3 tools/check.py model-collapse --gate G0` exited 0. It printed
   `note G0 passed: add G0 <today> to the log's Gates line`. I wrote `Gates: G0 2026-10-12`, and a final plain check
   exited 0 with `declared G0; required G0–G0; next G1`. Passed.

Before the preflight line existed, I ran one plain check right after Plan. It failed only on `g0.preflight`, which was
expected at that point.

## 2. Stalls, guesses, improvisations and tool failures

- `Plan` — `guess`. The template in `docs/formats.md` ("1. Retrieval log") gives a line order, but the Plan row writes
  only three of its lines. Later lines (`Preflight`, `Tokens`, `Gates`) then have to be slotted in. I kept the
  template's order: `Gates`, `Preflight`, `Dimensions`, `Tokens`, `Halts`, `Waivers`. The docs don't say whether order
  matters. The check accepted it.
- `Plan` — `minor`. The docs leave the first-pass `Open work` section unspecified. It could be empty, or it could carry
  the six sub-headings with no items. I left it empty under its heading. The check accepted it.
- `Plan` — `minor`. Title convention: `docs/formats.md` says to use "the input's own if it has one". The input's title is
  `# Model collapse`, so I used it as is. I glanced at `surveys/reasoning-legacy.md` to check the convention (see
  `Reading`). It uses a `Survey: ...` prefix and a legacy layout, so I did not copy it.
- `After every dispatch` — `guess`. `docs/dispatch.md` says to take `Tokens` "from the usage it reports". The Preflight
  agent said it could not see its own token usage. I used the `subagent_tokens` figure the Agent tool reported, 35731.
- `Preflight: Asta and WebSearch` — `minor`. `docs/dispatch.md` says not to take a report at face value. I checked the
  line on disk against the report, and the plain check passed. I could not confirm the five service calls themselves
  without making outside calls, so I did not re-run them. That the calls succeeded rests on the agent's report.
- `Preflight: Asta and WebSearch` — `minor`. The agent took about 349 s for five cheap calls. It caused no failure.

There were no blockers and no tool failures.

## 3. Halts and waivers

None. The log's `Halts` and `Waivers` lines read `none`.

## 4. Dispatches

- `survey-pass`, brief "Preflight", step 0. Tokens: 35731. Tool uses: 13. Duration: 348974 ms (about 5 min 49 s).

## 5. Reading

- `docs/process.md`, lines 1–192: the overview, "Order of operations", "When a pass ends" and "Before a pass: the
  preflight check". These are the sections the step-0 rows need.
- `docs/dispatch.md`, whole file, which the index tells the main session to read before planning a pass. This includes
  the briefs for later steps, which these rows did not need.
- `docs/gates.md`, whole file, which the index tells the main session to read before planning a pass.
- `docs/formats.md`, lines 86–375. I needed "`Dimensions`", "`surveys/<topic>.md`" and "1. Retrieval log". I also read,
  beyond what the rows needed: "`Clustering`", "Rules the parser applies", "Paper IDs", "2. Clusters", "3. Coreset",
  "4. Pool" and "5. Open work". I read them because they fell in one contiguous range, and "5. Open work" helped decide
  how to leave that section.
- `inputs/model-collapse.md`, whole, as the Plan row requires.
- `surveys/reasoning-legacy.md`: its first 30 lines and its `##` headings, to check the title convention. This was not
  needed.
- A listing of the repository's file names. My first `ls -R` also printed the directory names inside `.git/` (`hooks/`,
  `objects/`, `refs/` and the like). That was by accident, and it showed names only. I read no git history (no log,
  diff, show or blame) and no object contents. I read no files outside this directory.

`docs/roadmap.md` is absent, as intended. I skipped it and did not create it.

## 6. Outside calls

None. I made 0 calls myself to Asta, WebSearch or WebFetch. All five service checks were made by the Preflight agent.

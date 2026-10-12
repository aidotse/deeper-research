# Runner report: `model-collapse`, pass of 2026-10-12, step 0

## 1. Rows run

1. `0 Plan` — first pass, since `surveys/model-collapse.md` did not exist. I ran `python3 tools/inputs.py model-collapse`,
   which exited 0. It read 3 declared dimensions (`evidence`, `regime`, `modality`), the `expect` and `exclude`
   steering, and the targets `Landscape, Assumptions, Gaps, Conditions; then Questions, Reading`. I wrote
   `surveys/model-collapse.md` with the input's title, the five `##` headings, and the entry `### Pass 2026-10-12` with
   `Dimensions: declared in the input`, `Halts: none` and `Waivers: none`. `done when`: met.
2. `0 Preflight: scripts` — `python3 tools/preflight.py` exited 0. It printed
   `Graph API ok (429, busy) | arXiv ok | uv ok | Asta key set`. A Graph API 429 counts as reachable (`H1`). `done when`:
   met.
3. `0 Preflight: Asta and WebSearch` — dispatched `survey-pass` "Preflight". It reported `ok`, with no `STOP:`. All five
   calls answered: `snippet_search`, `search_papers_by_relevance`, `get_paper`, `get_citations` and WebSearch. It wrote
   the whole `Preflight` line. I checked the line on disk against the report, and they match. Then I ran the "After
   every dispatch" row: appended `Tokens: Preflight: 39077`, and ran `python3 tools/check.py model-collapse`, which
   printed `OK` (exit 0). No pool rows were added and the coreset did not change, so neither `pool.py` nor `bib.py` was
   due. `done when`: met.
4. `0 Gate G0` — `python3 tools/check.py model-collapse --gate G0` printed `G0 passed` and `OK` (exit 0). I added
   `Gates: G0 2026-10-12` to the log, and the plain check after it printed `OK`. `done when`: passed.

I stopped there and did not start `1 Orient`.

## 2. Stalls, guesses, improvisations and tool failures

- `0 Preflight: Asta and WebSearch` — `minor`. I made a transcription slip in the brief. In the "verbatim" printout I
  typed the status line as `ok    Asta key set`, where the script printed `ok    Asta key: set`. I noticed it before
  sending, and added a correction line to the prompt instead of rewriting the block. The agent checked it against the
  script's source and confirmed that it does not affect the paste line. The cleaner fix would have been to paste the
  printout unchanged.
- `0 Plan` — `minor`. After writing the survey, I ran the plain `tools/check.py` (`docs/tooling.md` says to run it after
  every script that writes to the survey). It failed with `G0 g0.preflight: ... no Preflight line`. That failure was
  expected at that point, since the Plan row's `done when` requires only `tools/inputs.py` to exit 0 and the next two
  rows write `Preflight`. The docs do not say whether a check is expected after the Plan row, so I noted the failure and
  went on.
- Setup — `minor`, a tool quirk. My first directory listing (`ls -R`, rewritten by the RTK hook) printed the names of
  directories under `.git` (`objects/`, `refs/`, and so on). I then listed files with `find`, which skips `.git`. I did
  not read any git history or object contents.
- `0 Preflight: scripts` — `minor`, not a failure. The Graph API answered 429 (busy). This passes by `H1`'s definition.
  The scripts that use the Graph API later (`tools/pool.py` and others) should expect retries.

No `blocker` and no `guess`.

## 3. Halts and waivers

None. The log has `Halts: none` and `Waivers: none`.

## 4. Dispatches

- `survey-pass` "Preflight", step 0. Brief: topic `model-collapse`, scope the pass's `Preflight` line, and the
  `tools/preflight.py` printout handed over, with the correction noted in section 2. Tokens: `39077`
  (`subagent_tokens`). Tool uses: 15. Duration: 148636 ms (about 2.5 min).

## 5. Reading

Everything I read beyond the exact sections my four rows needed:

- `docs/process.md`, lines 1–192. These are the "Overview", the "Order of operations", "When a pass ends" and "Before a
  pass: the preflight check". The overview and the halt list go a little beyond step 0. I read them to see the whole
  checklist and the halt IDs before starting.
- `docs/dispatch.md`, whole. `CLAUDE.md` says the main session reads it before planning a pass. Most of its briefs
  concern later steps.
- `docs/gates.md`, whole. `CLAUDE.md` says to read it before planning a pass. Only the `G0` row and "Running a gate"
  were needed.
- `docs/formats.md`: "`Dimensions`" (lines 86–108) and lines 145–375 (`surveys/<topic>.md` through "5. Open work").
  Only "`surveys/<topic>.md`" and "1. Retrieval log" were needed for step 0. The Clusters, Coreset, Pool and Open work
  format sections came along in the same read.
- `docs/tooling.md`, lines 1–99: the intro, "Paper IDs", "Consistency check", "Preflight" and "Input". "Paper IDs" and
  most of "Consistency check" go beyond step 0.
- `docs/external_services.md`, "Preflight" only, plus its heading list.
- The heading lists of `docs/process.md`, `docs/formats.md` and `docs/tooling.md`, used to find sections.

I did not read `docs/roadmap.md` (absent on purpose), `coresets.md`, `verification.md`, `audits.md`, `experiments.md`
or `vs_deep_research.md`. I read nothing outside this directory and no git history.

## 6. Outside calls

None. I made 0 calls to Asta, WebSearch or WebFetch myself. The five preflight calls were made by the "Preflight" agent.

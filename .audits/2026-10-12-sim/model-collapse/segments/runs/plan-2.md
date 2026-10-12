# Runner report: `model-collapse`, pass of 2026-10-12, step 0

## 1. Rows run

1. `0 Plan` — first pass, since `surveys/model-collapse.md` did not exist, so no `--status` check was run first.
   `python3 tools/inputs.py model-collapse` exited 0. It found 3 dimensions (`evidence`, `regime`, `modality`), the
   `expect` and `exclude` steering, and the targets `Landscape, Assumptions, Gaps, Conditions; then Questions, Reading`.
   I wrote `surveys/model-collapse.md` with its five `##` headings and the entry `### Pass 2026-10-12`, holding
   `Dimensions: declared in the input`, `Halts: none` and `Waivers: none`. Done when: met.
2. `0 Preflight: scripts` — `python3 tools/preflight.py` exited 0: Graph API ok, arXiv ok, uv ok, Asta key set.
   Done when: met.
3. `0 Preflight: Asta and WebSearch` — dispatched `survey-pass` "Preflight". It reported `ok`, with no `STOP:`, and
   wrote the full `Preflight` line. Done when: met.
   - `any After every dispatch` — no pool rows were added and the coreset did not change, so neither `pool.py` nor
     `bib.py` was due. I appended `Tokens: Preflight: 34215`. `python3 tools/check.py model-collapse` exited 0.
4. `0 Gate G0` — `python3 tools/check.py model-collapse --gate G0` exited 0 and printed `G0 passed`. I wrote
   `Gates: G0 2026-10-12`, and the plain check still exits 0. Done when: passes.

I stopped there and did not start step 1, Orient.

## 2. Stalls, guesses, improvisations and tool failures

- `0 Plan` — `guess`. The survey's `# ` title is not specified anywhere. I used `# Model collapse`, the input's title.
- `0 Plan` — `guess`. The Plan row lists only `Dimensions`, `Halts` and `Waivers` for the new entry. So I wrote only
  those three, and no empty placeholders for the other lines. The check accepted this.
- `0 Plan` — `minor`. The first `tools/check.py` run, made after Plan, failed with `g0.preflight`. This is expected
  because the next row writes that line. The Plan row's `done when` asks only for `tools/inputs.py`, so I went on.
- `any After every dispatch` — `guess`. `docs/formats.md` says a `Tokens` entry carries "the brief's name and its
  scope". The Preflight brief has no scope worth naming, so I wrote `Preflight: 34215`. I placed the line in the
  `docs/formats.md` order, just before `Halts`.
- `any After every dispatch` — `guess`. `docs/dispatch.md` says not to take a report at face value "where it matters".
  For Preflight, I checked only that the line on disk matches the report and passes the check. I made no
  connectivity call of my own to confirm the agent's five checks.
- `0 Gate G0` — `minor`. The gate printed its own instruction, ``add `G0 <today>` ``, which made the `Gates` line
  unambiguous. I placed the line first in the entry, as the `docs/formats.md` template does.
- No tool failures, and no blockers.

## 3. Halts and waivers

None. `Halts: none` and `Waivers: none` stand in the log.

## 4. Dispatches

- `survey-pass` "Preflight", step 0. Brief: the standard header (topic, job, step, date), the scope being the
  `Preflight` line of the 2026-10-12 entry, and the verbatim printout of `tools/preflight.py`.
  - Tokens: 34215 (`subagent_tokens`).
  - Tool uses: 16.
  - Duration: 114119 ms, about 1 min 54 s.
  - Its estimate in `docs/process.md` is "under 5k". It ran about 7 times over that. The likely reason is the agent's
    fixed reading: its instructions, `CLAUDE.md`, and the spec sections the brief lists. That is `UNVERIFIED`: I did
    not see its transcript.

## 5. Reading

- I read these in full: `docs/dispatch.md` and `docs/gates.md`. I needed only the main-session rules and the Preflight
  brief from `docs/dispatch.md`, so its other briefs were extra reading.
- From `docs/process.md`, I read lines 1–197: the overview, the order of operations, "When a pass ends", and the
  preflight section. The overview's later parts were not strictly needed.
- From `docs/formats.md`, I read "`Dimensions`", "`surveys/<topic>.md`", "Paper IDs", "1. Retrieval log" and
  "5. Open work". "Paper IDs" was extra: it fell inside the range I printed.
- I printed the headings of `docs/process.md`, `docs/gates.md`, `docs/dispatch.md`, `docs/formats.md`,
  `docs/tooling.md` and `docs/external_services.md` to find sections. The `tooling` and `external_services` headings
  were not needed for my rows.
- Git disclosure: my first listing, `ls -R`, which the `rtk` hook rewrote, printed the directory names inside `.git/`
  (`hooks/`, `objects/00/`, `refs/heads/` and so on). It read no file contents, and no log, diff, show or blame. I then
  re-listed the files with `.git` excluded. I read nothing outside this directory.

## 6. Outside calls

None. I made 0 calls myself to Asta, WebSearch or WebFetch. The Preflight agent made one call each to `get_paper`,
`get_citations`, `snippet_search`, `search_papers_by_relevance` and WebSearch. That is from its report, and
`UNVERIFIED` by me. `tools/preflight.py` contacted the Graph API and arXiv, as scripts do.

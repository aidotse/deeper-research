# Remediation plan: spec audit of step 2 (expand), 2026-10-12

## How to read this document

This is the second of the audit's three documents. The audit, `expand.md`, lists 24 issues found by a blind reading of
step 2. This plan says how each will be fixed, in which order, and what the user decided along the way. The third,
`disposition.md`, records what was actually done.

The audit was requested during the simulation audit `.audits/2026-10-12-sim/model-collapse/`, after `pool` iteration 1.
That run's findings, `E15`–`E20`, are defined in `segments/pool.md` there. This plan refers to them, and fixes them
alongside the audit's IDs, since most turn out to be the same problems seen from the run's side.

The sections, in order:

- `Principles`: the rules that set the order of the work.
- `Decisions taken`: the user's answers, dated.
- `The design`: option B as it will be built, since most remediations below are parts of it.
- `Issues found during remediation`: issues the audit did not list (`P` IDs).
- `Remediations`: one entry per ID, with its fix, effort and status (the status values are the audit's).
- `Phases`: the order of the work.
- `After the run`: what is deferred, and why.

## Principles

- Decide before fixing. Every design choice below was put to the user first.
- Simpler wins where it still solves the problem. Option B removes agent work rather than adding rules for it. Step 2's
  open-ended extra work is dropped, not specified.
- Code before docs, within one phase, so that the docs describe tools that exist and pass their tests.
- Every code fix carries a test in `tests/gates/`, and both suites pass after every commit.
- The new code gets an independent review by a separate agent before it is committed (the user's request).
- The simulation is the test of the whole. `pool` iteration 2 runs only once every phase before it has landed.

## Decisions taken

All by the user, 2026-10-12.

- `A2`, `Z1`, `E18` — decided: option B. Traversal and search run by script onto a screening sheet, as the fringe routes
  already do. Agents only judge, each screening dispatch at most about 100 rows (option A, as the cap). Option C,
  rejecting from the title alone, is rejected for now: the user wants to see first what screening costs without it.
- `A5` — decided: in the input, a detection, watermarking or curation paper is in scope only if it tests its method as a
  defence against degradation across generations, or as filtering of training data. One that only cites model collapse
  as motivation is out.
- `A6` — decided: step 2's open-ended extra traversals and queries, beyond its required work, are dropped. The gaps they
  would fill are caught by targeted expansion in step 3 and by the coverage test in step 7, which exist for that.
- `Relevance searches` — decided: the agent picks the queries and the script runs them. In this plan the agent that
  picks is the Orient agent, through its `themes` (see "The design").
- `E16`, `E17` — decided: agents write no scripts of their own, and no files beyond those their brief names. A missing
  tool is reported as a stall, not worked around.
- `The input` — the user narrowed it before this audit, excluding self-training for capability gains (recorded in the
  simulation audit's `simulation.md`).
- `The audit itself` — the user chose a blind read before the change, over writing this plan directly.
- `Rate limits` (`P2`), 2026-10-13 — decided: `collect` batches its calls and resumes after a failure, which keeps a
  pass's calls to the shared unauthenticated pool few, and makes a busy spell cost a rerun. The user has applied for a
  Semantic Scholar API key, which gives every script a rate limit of its own; an answer may take two weeks. Using the
  key changes the spec's statement that no key or user identifier is sent, which the user approves with the key.
  Rejected: routing the scripts through Asta. Its `get_citations` cannot page, it has no embeddings, so the Graph API
  stays needed anyway, and a script would have to speak MCP with a key from Claude Code's config.

## The design

### What runs where

Step 2 becomes four rows, three of them scripts:

1. `Collect` — main: `python3 tools/expand.py collect <topic>`. From the latest `Orientation` line, it reads the seeds,
   the frontier candidates and the themes. It calls the Semantic Scholar Graph API directly, as `tools/fringe.py` does:

   - backward and forward: the reference and citer lists of every seed and frontier candidate, from the batch endpoint,
     up to 500 papers per call; a list shorter than the paper's count is paged from its own endpoint, so nothing is cut
     at 100;
   - searches: one relevance search per theme (`/graph/v1/paper/search`), top 50.

   It drops candidates already in the pool (by ID or by normalised title), already in `rejected.md`, already on the
   sheet, or unknown to Semantic Scholar, and keeps one of two records with the same title. It records each source's
   full result in `graphs/<topic>/expand.json`, with the totals and what was dropped and why, saving after every call so
   that a failed run resumes. It appends to the screening sheet `graphs/<topic>/expand-screen.md`, one numbered row per
   candidate, with title and abstract. The embedding check moved to `Add`, for the `yes` rows only (`P2`).

2. `Screen` — `survey-pass` "Screening", one dispatch per block of at most 100 rows, handed over as a row range. The
   agent judges each row with `tools/expand.py judge`, `yes` or `no` with a reason. Dispatches may run in parallel,
   since `judge` locks the sheet while it writes. A verdict can be replaced on the sheet until the next row, `Add`,
   runs.

3. `Add` — main: `python3 tools/assign.py add-expand <topic>`. It refuses while any row of this pass is unjudged. Each
   `yes` enters the pool through `tools/assign.py add`, which refuses a paper without a SPECTER2 embedding, and each
   `no` enters `rejected.md` with its reason. It prints the `Expansion` line, so every count in it comes from the
   script.

4. `Fetch` — main: `python3 tools/pool.py <topic>`, as now. Then the fringe rows follow, unchanged.

A targeted expansion in step 3 reuses the same three steps. It runs `collect --targeted`, given the region's papers and
its theme, which adds a targeted round to `expand.json` and new rows to the sheet. Earlier verdicts carry over.

### Why the queries are the themes

The user chose "the agent picks, the script runs". The Orient agent already names the field's phrases for its sub-topics
as `themes`, and step 2 is required to search each one. So the themes are the queries, and no extra dispatch is needed.
The Orient brief gains one rule: the themes include every other name the input gives the topic (`A9`). On a targeted
expansion, the query is the region's theme, as the Naming sheet or the coverage report gives it.

### The sheets and the screening brief

The expansion sheet takes the fringe sheet's form, with a row number added for handing over ranges. `judge` becomes one
implementation shared by both sheets, with the lock and the two-word reason test (`C3`). The "Expand" and "Fringe
screening" briefs merge into one "Screening" brief. It is handed a sheet and a row range, reads the input's `Topic` and
`exclude` (`W2`), and judges rows. A row with no abstract is judged from its title, and the rule "borderline is in"
applies (`P1`).

### What `G1` checks

`G1` checks the record, not the agent's own count. In `expand.json`: a backward and a forward traversal for every seed
and frontier candidate, and a search for every theme. On the sheet: every row judged. Every `yes` is in the pool or in
Open work, and every `no` is in `rejected.md`. The `Expansion` line must agree with `expand.json`. This replaces the
current check of the `Expansion` line's wording, and the check that any rejection exists (`C1`, `T1`, `T2`).

## Issues found during remediation

### Two Graph API checks by the plan's author, 2026-10-12

Run by the auditor of the simulation audit, not blind, at no model cost. One paged citations call each for `2305.17493`
and `2404.01413`, and one references call for `2404.01413`. Findings: one.

- `P1` — `guess`. About 11% of traversal candidates have no abstract in Semantic Scholar (64 of 551 citers, 13 of 182,
  and 5 of 30 references), and none of those citers has an arXiv ID, so arXiv cannot fill the gap. The spec screens
  "from its title and abstract", and says nothing for a candidate without one. Fix: the sheet shows `(no abstract)`. The
  Screening brief says to judge such a row from its title, and that "borderline is in" applies. The same calls also
  confirm the fix for `M1`: paging returned all 551 and all 182 citers.

### A live run of `collect`, 2026-10-12

Run by the plan's author on a scratch topic (one seed, `2404.01413`, and one theme), against the live Graph API, at no
model cost. It gave 249 rows, 20 without an abstract, about 195 tokens per row. Findings: two.

- `P2` — `blocker`. The shared unauthenticated rate limit returned 429s past the network helper's retries, twice, on a
  run of about 8 calls; the first design made about 60 calls on the `model-collapse` topic. A busy spell would halt the
  pass (`H3`) and lose the run. Fix: as decided above, batching (one batch call returns the full reference and citer
  lists of many papers: 30 and 551, and 30 and 182, for the two seeds, in 1.6 s), the embedding check moved to `Add`,
  and progress saved after every call. About 15 calls on that topic.
- `P3` — `minor`. `collect` failed when `graphs/<topic>/` did not exist. Fix: it creates it.

### Independent code review, 2026-10-13

Run by a fresh agent that read the design above, the audit's IDs and the uncommitted code, but not the plan's author's
reasoning; about 91k tokens. Findings: eight, all fixed in phase 2, with tests.

- `P4` — `other` (bug). `add-expand` matched the pool by ID only, while `collect` and `G1` also match by title, so two
  records of one paper could both enter the pool. Fix: `collect` keeps one of two same-title candidates, preferring the
  arXiv record; `add-expand` skips a `yes` whose title matches a pool paper.
- `P5` — `other` (bug). A candidate could lose its sheet row for good: `collect` died between its two writes, or
  appended while a `judge` held the lock. Fix: `collect` takes the same lock, and every run appends any candidate of
  `expand.json` without a row.
- `P6` — `other` (bug). A `no` for a pool paper, or one without an ID, failed `G1` with advice (`add-expand`) that could
  not clear it. Fix: `G1` names the real remedy, re-judging the row, and a `no` without an ID has nothing to record.
- `P7` — `gap`. A traversal that returned 404 counted as done, and an old-style arXiv ID went into a URL path unencoded.
  Fix: `G1` fails on an untraversed start paper until Open work records it; IDs go in batch bodies, and the paged
  fallback quotes them; a list past the endpoint's offset limit is marked `capped`.
- `P8` — `other` (bug). A second targeted run on one region with another query replaced the first's record. Fix: a round
  is keyed by its query too.
- `P9` — `gap`. `add-expand` and `G1` acted on every row from every pass, so a paper the user had taken out of the pool
  would be re-added. Fix: both act on this pass's candidates only.
- `P10` — `gap`. No tests for paging, `--targeted`, argument parsing, 404s, the fringe title match, or a `CorpusId`-only
  candidate. Fix: behaviour tests for each.
- `P11` — `minor`. Leftovers: the fringe sheet's header still asked for "a short reason"; unused imports; two duplicated
  parsers; a sheet parsed twice. Fix: all tidied.

### The behaviour tests, 2026-10-13

- `P12` — `other` (bug), found by the new rerun test. A rerun of a collection could append a second record of one of its
  own rows, since the title check did not see them. Fix: a rerun's own titles count as taken.

### Writing the docs, 2026-10-13

- `P13` — `gap`. The Screening brief hands each agent a range of row numbers, but only the expansion sheet had them.
  The fringe sheet holds up to 120 rows at the default `--per-route 60`, over the cap of 100 per dispatch. Fix:
  `tools/fringe.py collect` numbers its rows too, `add-fringe` reads the sheet by column name, and a behaviour test
  checks the numbering.

### The check of the docs against the code, 2026-10-13

Run by a fresh agent that read the uncommitted docs and the code, about 160k tokens. Findings: twelve, none a blocker.
Eleven were wording, fixed in the docs before the commit: a stale claim that expansion falls back to WebSearch without
Asta; the plain check after a targeted expansion's screening, which fails until `add-expand` runs; the refusal for an
`Orientation` line with no themes; when `collect` saves; `capped` in either direction; the sheet-wide count `judge`
prints; the fringe sheet renumbered by a rerun; a theme-named region; the screening sheets not read whole; a `printf`
example for `judge`, since agents may not write programs; and two refusals of the add steps. One is a gap in the code:

- `P14` — `gap`. A row an earlier pass left on the expansion sheet is left out of every later collection, and this
  pass's `add-expand` and `G1` act on this pass's rows only. So a row a halted pass left unjudged is never screened
  again, and a `yes` that lacked an embedding is never retried. The docs now say so (`docs/tooling.md`, "Expansion
  candidates"). Deferred with `S2`, which also turns on verdicts that outlive a pass: both bite only on a later pass.

## Remediations

Effort is S, M or L. Each status is the audit's.

### Moot under the design

- `A1` — moot for step 2, since the script reads canonical IDs from `externalIds`. Orientation still resolves IDs
  through Asta, so `docs/external_services.md` names the `externalIds` field, and the Orient brief asks for it. S;
  `verified by simulation`.
- `A3` — moot: `add-expand` prints the `Expansion` line, counts included. S; `verified by simulation`.
- `M1` — moot: the script pages every citer list to the end. The `Expansion` line gives each traversal's count. S;
  `verified by simulation`.
- `S5` — moot: the sheet is the record of progress. A dead screening dispatch leaves its verdicts on the sheet and its
  unjudged rows visible. S; `likely`.
- `S7` — moot: an unresolved reference is counted as dropped in `expand.json`, with its reason. S;
  `verified by simulation`.
- `A6` — moot, by the decision to drop the open-ended work. The orientation stopping rule stays. S;
  `verified against docs`.
- `S4` — moot: the `rejected: none` part goes, since `add-expand` writes every rejection. S; `verified against docs`.

### Built as part of the design (phases 2 and 3)

- `A2`, `Z1`, `E18` — the design as a whole. L; `verified by simulation`.
- `E15` — the sheet carries the abstract of every row, and screening never sees a title alone except under `P1`.
- `E19` — a verdict is replaced on the sheet with `judge` until `add-expand` runs. After that, see `S3` under "After the
  run".
- `E20` — moot: traversal and searches are one script run, with no order left to choose.
- `C1`, `T1`, `T2` — `G1`'s new checks against `expand.json` and the sheet, each with a fault test in
  `tests/gates/faults.py`. M; `verified by simulation` / `verified against code`.
- `S1` — forward traversal from the seeds and the frontier candidates becomes required work, run by the script. S;
  `verified against docs`.
- `S6` — backward traversal runs from the seeds as well as the frontier candidates. `G1` needs at least one of either.
  An orientation with no frontier candidate can then pass on the seeds. If there are neither, the pass halts, as a new
  case of an existing halt or a new one, to be settled when `docs/process.md` is edited. S; `verified against code`.
- `W1` — the Screening brief's job is the sheet, and the required work's done-when sits in the script rows, which the
  main session runs. The Expand brief, whose reading list missed the done-when, goes. S; `verified against docs`.
- `A7` — the step 2 sentence about `snippet_search` filling clusters goes. So does the instruction to use
  date-restricted queries: orientation's recency window and the fringe route `new` keep recent work represented. S;
  `verified against docs`. The user may prefer to keep a dated search per theme, at double the search volume: to confirm
  at plan review.
- `A8` — a targeted expansion traverses from the region's 5 papers most cited within the pool. On `no stable level` it
  expands the 2 thinnest regions. Both numbers are first guesses, stated as such. S; `verified against docs`. To confirm
  at plan review.
- `A9` — the Orient brief's rule that the themes include the input's other names for the topic. S; `likely`.
- `W2` — the Screening brief reads the input's `Topic` and `Clustering`. S; `verified against docs`.
- `Z2` — the order of operations is rewritten for step 2, and the duplicate fetch row goes with it. S;
  `verified against docs`.
- `M2` — `tools/fringe.py collect` and `tools/expand.py collect` both drop a candidate whose normalised title matches a
  pool paper, so that `add` and `g1.fringe-added` agree on what a duplicate is. S, with a behaviour test; `likely`.
- `C3` — the shared `judge` applies the two-word test. S, with a behaviour test; `verified against code`.

### Independent of the design (phase 1)

- `A4` — `.claude/agents/survey-pass.md:17`: the sentence becomes one that does not touch scope, such as "every row you
  select should earn its place in a role". The rule that every in-scope paper enters the pool is left to the spec. S;
  `verified against docs`.
- `A5` — the input line the user decided, in `inputs/model-collapse.md`'s `exclude`. S; `likely`.
- `C2` — `docs/external_services.md` stops claiming that Asta returns only `title`. It says `fields` trims the result,
  but some fields come back unasked. S; `verified by simulation`.
- `E16`, `E17` — the rule against agents' own scripts and stray files, in `docs/dispatch.md`'s rules and in
  `.claude/agents/survey-pass.md`. S.

## Phases

### Phase 1: independent fixes

`A4`, `A5`, `C2`, `E16`, `E17`. These are wording and one input line, so they land first, in one commit. The gate suites
run after. They come first because none of them waits on the design, and `A4` and `A5` change how every screening
verdict is made.

### Phase 2: the code

`tools/expand.py` (`collect`, `collect --targeted`, `judge`); `judge` shared with `tools/fringe.py`, with the lock and
`C3`; the title match of `M2` in both collectors; `tools/assign.py add-expand`; `G1`'s new checks and the removal of the
old ones; the gate fixture in `tests/gates/build.py` gains an `expand.json` and a judged sheet; fault and behaviour
tests for each new check and refusal. Then the independent review: a fresh agent reads the diff against this design and
the tests, and reports. Its findings are fixed, or recorded here as `P` IDs with a reason, before the commit.

This phase comes before the docs, so that the docs describe tools that exist and pass their tests. It also comes before
the simulation, since the runner must find working tools.

### Phase 3: the docs

`docs/process.md` (order of operations, step 2, "Screening for scope", targeted expansion), `docs/dispatch.md` (the
Screening brief in place of Expand and Fringe screening; the Orient brief's `A9` and `A1` rules), `docs/formats.md` (the
`Expansion` line, the two new files under `graphs/<topic>/`), `docs/tooling.md` (a section for `tools/expand.py`),
`docs/external_services.md` (the Graph API now serves expansion too), and `docs/gates.md` (the `G1` row). These cover
`S1`, `S4`, `S6`, `S7`, `W1`, `W2`, `A6`–`A9`, `Z2` and `P1`. The same review agent, or a second one, checks the docs
against the code for drift (`C` issues) before the commit.

### Phase 4: the simulation

`pool` iteration 2 of the simulation audit, from the `plan` checkpoint, with a rebuilt scratch copy. It tests the whole
design on a real topic. Its findings are `E` findings, in that audit's `segments/pool.md`. Any that bear on this
remediation are also noted in this audit's disposition.

## After the run

- `S2` — rejections and fringe verdicts outlive a change of scope. Deferred: the fix (re-screening earlier rejections
  against a changed input) is a rule for later passes, and no later pass has run yet. The narrowing of the
  `model-collapse` input narrows the scope, so earlier rejections stay right.
- `S3` — no tool retracts a rejection once recorded. Deferred: under the design, verdicts are replaced on the sheet
  before `add-expand`, which covers the case the run met (`E19`). Whether a retraction after that is needed is for the
  run to show.
- `Scope verdicts are not audited` — the audit's verification concept notes that no link re-checks screening verdicts,
  where step 7 re-checks verification. A sampled re-screening at `G1` would be the counterpart. Deferred: the
  simulation's spot checks measure the error rate first (20 of 20 right in iteration 1), and the user decides with that
  number in hand.

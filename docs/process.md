# Process

A description of our methodology. The document follows a pass in the order it runs. The overview gives the map: the
stages, every operation in order, and which source serves which job. Then each stage follows, step by step, with the
detail each step needs placed under it.

## Overview

Retrieval has four jobs, and the tools are good at different ones. Assign tools by job rather than ranking them.

- `Orientation: what is the field talking about now?` — WebSearch. Step 1.
- `Expansion: how did we get here, and who disagrees (dissent)?` — Asta. Step 2, and the dissent search in step 4.
- `Fringe: what has the field overlooked?` — the fringe scripts. The end of step 2.
- `Characterisation: what does a paper do, and what did it find?` — the paper's full text, fetched by script and read by
  section, with Asta's snippet search to find passages in it. Step 5.

Orientation and expansion need each other. A pass that uses only WebSearch produces a corpus top-heavy with preprints
and missing the methods they all cite. A pass that uses only Asta keyword search misses what the community has only just
started discussing.

How to call each service, their limits and failure modes, are in `docs/external_services.md`.

Concretely, a pass runs in eight steps, numbered 0 to 7: a preflight check, five steps that build the pool and the
coreset, then the output and the coverage test. The pool and the coreset are built in separate stages:

- `Pool` (steps 1–3) — broad and cheap. Everything in scope enters, with metadata only and no verification (see
  `docs/verification.md` for what verification means), and is clustered. Fringe candidates enter here too, so that
  clustering sees them.
- `Coreset` (steps 4–5) — small and expensive. A few papers per cluster are selected from the pool, in roles, and each
  is verified against body text. This is where the coreset idea applies (`docs/coresets.md`), and where most of the cost
  goes.
- `Output and coverage test` (steps 6–7) — the analysis is written from the coreset alone, then tested for sufficiency
  against pool papers that were not selected.

### Order of operations

This table is the pass's checklist. Run it from top to bottom, and confirm each row's `done when` before starting the
next. The rows marked `any` are not steps: they apply whenever their condition arises. The gate rows, `G0` to `G5`,
check by script that the steps before them left everything they should (`docs/gates.md`). Each operation is either a
script, which is deterministic and costs no tokens, or model judgement. In `run by`, `main` means the main session runs
the command itself, between dispatches. A quoted name, such as `survey-pass` "Orient", is a dispatch with the brief of
that name in `docs/dispatch.md` ("Briefs"), which says what the main session hands over and what comes back. A subagent
runs only the scripts its own job needs, such as `tools/assign.py add` while expanding or `tools/fulltext.py show` while
verifying.

The `writes` column is the only authority on who writes what. A capitalised name in code, such as `Pool`, is a line of
the pass's retrieval-log entry (`docs/formats.md`, "1. Retrieval log"). A line marked `Log:` or `Open work:` is written
by the agent itself when it runs alone, and returned in its report under that heading when it runs in parallel with
others; the main session then writes it, in the "After every dispatch" row. Every artifact is described in
`docs/formats.md`, the working files of `graphs/<topic>/` in its last section. Token figures are per pass. Those marked
`measured` come from previous runs in this repo; the rest are estimates, to be replaced by the per-dispatch counts in
the log's `Tokens` line.

| step | operation | run by | reads | writes | done when | tokens |
| -- | -- | -- | -- | -- | -- | -- |
| any | After every dispatch | main: `python3 tools/bib.py <topic>` if the coreset changed; if pool rows were added, `python3 tools/pool.py <topic>` while the pass is at step 3 or before, or has returned to it, and after a coverage round that proposes a cluster; otherwise `uv run tools/assign.py late <topic>` ("Late papers"), and on `RECLUSTER:` return to step 3; after Naming, `python3 tools/assign.py clusters <topic>`; then `python3 tools/check.py <topic>` | the agent's report | `Tokens`, one entry appended; the `Pool` line the fetch printed; the `Late papers` line, if `late` assigned any; `Coreset`, from the check's row count, if the coreset changed and step 5 has written the line; a parallel agent's `Log:` and `Open work:` lines | the check exits 0, apart from the open work of a return to step 3 ("Returning to step 3") or of Revise (step 7). A failure the agent cannot fix halts the pass (`H9`) | 0 |
| any | On a halt | main | a report or printout starting `STOP:` | `Halts`: the halt, with `pending`, then the user's decision in its place | the user has decided; see "When a pass ends" | est. under 5k |
| any | On a requirement the user may waive | main and user | the failing requirement | `Waivers` | the user has decided; an agent never waives anything (`docs/gates.md`) | 0 |
| any | Probe, on request | `survey-pass` "Probe" | the question; the coreset rows closest to it | Pool rows, as late papers; `Probes` | as the brief | not yet estimated |
| 0 | Plan | main: on a later pass, first `python3 tools/check.py <topic> --status`; then `python3 tools/inputs.py <topic>` | the input; on a later pass, the survey's Open work and last log entry | on a first pass, `surveys/<topic>.md` with its five section headings (`docs/formats.md`); the log entry `### Pass YYYY-MM-DD`, with `Dimensions`, declared or proposed from the input (`docs/formats.md`, "`Dimensions`"), and `Halts` and `Waivers` as `none` | `tools/inputs.py` exits 0, and on a later pass `tools/check.py` exited 0 before the new entry was written. If `tools/inputs.py` fails, the user corrects the input before the pass starts; never edit it for them | est. under 10k |
| 0 | Preflight: scripts | main: `python3 tools/preflight.py` | — | — (the printout goes to the next row) | exit 0. Exit 1 halts the pass (`H1`) | 0 |
| 0 | Preflight: Asta and WebSearch | `survey-pass` "Preflight" | the script's printout | `Preflight`, both halves | the report has no `STOP:` | est. under 5k |
| 0 | Gate `G0` | main: `python3 tools/check.py <topic> --gate G0` | — | `Gates` | passes (`docs/gates.md`) | 0 |
| 1 | Orient | `survey-pass` "Orient" | WebSearch results for the input's topic, context and questions, with and without the recency window | Pool rows, by `tools/assign.py add`; rejections, by `tools/assign.py reject`; `Orientation`, with the themes, the input's seeds and the frontier candidates; `Recency window`; `Errored queries`; Open work: papers that could not enter the pool | every frontier candidate listed is in the pool, every seed the input names is in the pool or in Open work, and orientation stopped by its rule ("Screening for scope") | est. 50–100k |
| 2 | Expand and screen | `survey-pass` "Expand" | Asta traversal and search results: titles and abstracts | Pool rows; rejections; `Expansion`; `Errored queries`, added to; Open work: papers that could not enter the pool | backward traversal done from every frontier candidate, a relevance search run for every theme in `Orientation`, expansion stopped by its rule ("Screening for scope"), and every errored query retried once (`H2` if it still fails) | about 0.85k per candidate screened (measured); 250k for 300 candidates |
| 2 | Fetch pool data | main: `python3 tools/pool.py <topic>` | — | `pool.json`; the Pool's `year`, `citations` and `cites`; `Pool` | exit 0, and `tools/check.py` notes no unfetched paper | 0 |
| 2 | Collect fringe candidates | main: `uv run tools/fringe.py collect <topic>` | — | `fringe.json`; the blind screening sheet `fringe-screen.md` | exit 0 | 0 |
| 2 | Screen fringe candidates | `survey-pass` "Fringe screening" | `fringe-screen.md` | its `in scope` and `reason` columns, by `tools/fringe.py judge` | every row `yes` or `no`, with a reason; no `maybe` left | about 0.85k per candidate (measured: 123k for 146) |
| 2 | Add fringe candidates | main: `python3 tools/assign.py add-fringe <topic>` | — | Pool rows; `Fringe`; Open work: `Papers that could not enter the pool`, for the in-scope candidates it lists without an ID | exit 0; it refuses while any row is unjudged | 0 |
| 2 | Fetch again | main: `python3 tools/pool.py <topic>` | — | as above; `Pool`, replacing the earlier one | as above | 0 |
| 2 | Gate `G1` | main: `python3 tools/check.py <topic> --gate G1` | — | `Gates` | passes | 0 |
| 3 | Cluster | main: `uv run tools/cluster.py <topic>` | — | `clusters.json`; a printout with the diagnostics, the notes and the `Clustering` line | exit 0. `STOP: H8`, or `no structure` (`H4`), halts the pass. Any other diagnostic is acted on in the next two rows ("When stability fails") | 0; about 30 s per 200 papers (measured) |
| 3 | Targeted expansion, once per region: a `thin cluster`; the thinnest regions, on `no stable level`; an `expect` theme that Naming reports missing; a cluster a coverage round proposed (step 7) | main: `python3 tools/sheets.py <topic>`; then `survey-pass` "Expand", targeted, one at a time | the region's section of `naming-sheet.md`, the missing theme, or the proposed cluster's theme and candidates; and why | Pool rows; rejections; `Expansion`, a `targeted` part naming the region by one of its papers; `Errored queries` | backward traversal from the region's most-cited papers and a relevance search on its theme, under the stopping rule ("Screening for scope") | est. 20–50k per region |
| 3 | Fetch and recluster, after a targeted expansion or on `RECLUSTER:` | main: `python3 tools/pool.py <topic>`, then `uv run tools/cluster.py <topic>`; once the clusters have names, then `python3 tools/assign.py remap <topic>` | — | `Pool`; `clusters.json`; on a return from step 7, `Late papers` ("Returning to step 3") | exit 0. Still `no stable level`: take the coarsest level and halt (`H5`). An expected cluster still missing halts (`H7`). A cluster still thin is kept, and the `Clustering rationale` says so | 0 |
| 3 | Carry names over, on a later pass | main: `python3 tools/assign.py remap <topic>` | — | the Clusters table's `computed` column | exit 0; it lists the clusters left to name | 0 |
| 3 | Write the sheets | main: `python3 tools/sheets.py <topic>` | — | `naming-sheet.md`; `fringe-sheet.md` | exit 0 | 0 |
| 3 | Name the clusters | `survey-pass` "Naming" | `naming-sheet.md`; the input; `tools/cluster.py`'s printout; the regions expanded, by paper ID, and whether each is still thin; on a later pass or a return, `tools/assign.py remap`'s printout | Clusters rows, with `computed` ids, and each `high` cluster's central claim; on a rerun, every unmatched cluster renamed or retired ("Late papers"); `Clustering`, with names for the computed ids; `Clustering rationale`; `Clusters` | every computed cluster is named once, and after `tools/assign.py clusters` the check passes. An `expect` theme with no cluster goes back to the targeted-expansion rows, once. `H6` is found here | est. 20–40k |
| 3 | Write the clusters | main: `python3 tools/assign.py clusters <topic>` | — | the Pool's `cluster` column; Open work: `Clusters not yet reviewed by the user` | `tools/check.py` passes, with no cluster cell left to fill | 0 |
| 3 | Rewrite the sheets | main: `python3 tools/sheets.py <topic>` | — | the sheets, now with names | exit 0 | 0 |
| 3 | Build the viewer | main: `python3 tools/graph.py <topic>` | — | `graph.html` | exit 0 | 0 |
| 3 | Cluster review, only on `H4`–`H8` or `H13` | main and user | the Clusters table; the `Clustering` line; the viewer | `Halts`; any manual override, in `Clustering` | the user has decided; see "Cluster review". The halt is recorded where it is found, and the rows up to the viewer still run, so that the user sees the named clusters; `G2` cannot pass until the user decides | est. under 10k |
| 3 | Gate `G2` | main: `python3 tools/check.py <topic> --gate G2` | — | `Gates` | passes | 0 |
| 4 | Set up the coreset blocks | main; on a later pass or a return from step 7, `survey-edit` for the existing rows | the Clusters table; the dimensions, declared or proposed | one `###` block per cluster, in the Clusters table's order, each with the table's header row (`docs/formats.md`, "3. Coreset"); existing rows moved to the block of the cluster their paper was computed into, and a retired cluster's block removed once empty | the blocks match the Clusters table, and no row sits in another cluster's block | est. under 5k |
| 4 | Select per cluster: anchor, frontier, dissent | `survey-pass` "Selection", one per block of clusters, in parallel | each cluster's section of `naming-sheet.md`; `tools/check.py`'s lines for those clusters; the frontier candidates in `Orientation`; abstracts and dissent searches through Asta | Coreset rows, every cell drafted from the abstract, `source` `abstract`; `Log:` `Dissent searches`, and `Demotions` on a later pass; `Open work:` empty roles, and the new rows under `Rows needing verification` | after `python3 tools/bib.py <topic>`, `tools/check.py` passes | est. 6–12k per cluster, plus 20–50k per `high` cluster for dissent |
| 4 | Bridges, only if `tools/check.py` notes a trading pair without one | `survey-pass` "Bridges", once | the Clusters table; the trading pairs `tools/check.py` notes; the coreset | `bridge:` rows; Open work: their `Rows needing verification`, and `Empty roles` for a pair left without a bridge | `tools/check.py` notes no trading pair without a bridge | not yet estimated |
| 4 | Rewrite the sheets | main: `python3 tools/sheets.py <topic>` | — | `fringe-sheet.md`, with the coreset rows marked | exit 0 | 0 |
| 4 | Fringe | `survey-pass` "Fringe selection", once | `fringe-sheet.md`; its papers' abstracts through Asta; the coreset rows | `fringe` rows; Open work: their `Rows needing verification` | `tools/check.py` passes | est. 20–40k |
| 4 | Gate `G3` | main: `python3 tools/check.py <topic> --gate G3` | — | `Gates` | passes | 0 |
| 5 | Fetch the full texts | main: `uv run tools/fulltext.py <topic> --abstract` | — | `graphs/<topic>/fulltext/` | exit 0; the papers it could not fetch are listed, and their rows are uncheckable | 0; about 3 minutes for 60 rows (measured rate: 27 papers in 90 s) |
| 5 | Characterise and verify | `survey-pass` "Verification", one per block of clusters, in parallel | the fetched full texts, through `tools/fulltext.py show` and Grep; snippet search to find passages | every cell and `source`; `graphs/<topic>/evidence/<id>.md` per row; `Log:` `Corrections to existing rows`; `Open work:` the rows still needing verification, with why | every row verified, corrected, or uncheckable (`docs/verification.md`, "Outcomes") | about 26k per row (measured, 27 rows read by the section reader: `docs/experiments.md`); 1–1.6M for 40–60 rows |
| 5 | Replace uncheckable rows, if any, except `fringe` | `survey-pass` "Selection", for the clusters that have one | the uncheckable rows and their roles | a verifiable paper in each role, the old row demoted (`Log:` `Demotions`); or `Open work:` that no verifiable paper fills it, and the row stays | the new rows have been through the fetch and verification rows again. Over 20% of rows still uncheckable halts the pass (`H10`) | est. as Selection |
| 5 | Bibliography, checks and sheets | main: `python3 tools/bib.py <topic>`, then `python3 tools/check.py <topic>`, then `python3 tools/sheets.py <topic>` | — | `bib/<topic>.bib`; `Coreset`, from the check's row count; the sheets, for step 7 | all exit 0 | 0 |
| 5 | Gate `G4` | main: `python3 tools/check.py <topic> --gate G4` | — | `Gates` | passes | 0 |
| 6 | Write the output | main | the Clusters and Coreset sections, never the pool, printed by `python3 tools/check.py <topic> --print Clusters` and `--print Coreset`; the evidence files of the rows each claim rests on | `outputs/<topic>.md` | `tools/check.py <topic>` passes, and every claim matches the rows it cites | est. 60–120k |
| 7 | Draw the coverage sample | main: `uv run tools/coverage.py draw <topic> <R>`, R being the round's number | — | `coverage-<R>.md`: ten pool papers drawn from the worst covered, with the seed and the coreset's radius | exit 0 | 0 |
| 7 | Coverage test | `survey-pass` "Coverage test" | the output; `coverage-<R>.md`; a fresh recency query over the pass's `Recency window`, extended to the day of the round; the candidates' abstracts, through Asta | the sheet's verdicts and its recency-query rows, by `tools/coverage.py judge`; the recency query, by `tools/coverage.py query`, whatever it found; Pool rows, by `tools/assign.py add`, for each recency candidate that changed a target or belongs to a proposed cluster; `Coverage test`, pasted as `tools/coverage.py line` prints it | `tools/coverage.py line` prints the line, which it does only once every candidate has a verdict and the recency query is recorded | est. 30–50k per round |
| 7 | Late papers | main: the `uv run tools/assign.py late <topic>` that "After every dispatch" runs after the Coverage test is this row; it is not run again. Not run when the round proposed a cluster | — | the Pool's `cluster` column; `clusters.json`; `Pool`; `Late papers` | exit 0. On `RECLUSTER:` (exit 3), or when the round proposed a cluster, return to step 3 ("Returning to step 3") | 0 |
| 7 | Revise | `survey-pass` "Selection" for the clusters of the papers the round counted, then step 5's rows from the fetch on, then step 6, all without their gate rows. Verification takes the new rows, and any row still `abstract` whose full text the fetch now finds. Bridges and Fringe selection do not rerun. After a return to step 3, the step 4–6 rows also run for every new, renamed or retired cluster and every cluster whose rows moved. It runs on a converging round too, when K is 1 | as there; Selection is handed each counted paper, with its change and its role (below) | rows in roles, verified; the output, revised | `tools/check.py` passes again: it fails until every counted paper is a coreset row verified from the full text, or marked uncheckable | as there |
| 7 | Draw the judgement audits, once a round has converged and its Revise is done | main: `python3 tools/audit.py reverify <topic>`, then `python3 tools/audit.py trace <topic>` | — | `reverify.md`; `faithfulness.md` | exit 0 | 0 |
| 7 | Re-verify the sample | `survey-pass` "Re-verification", a fresh agent | the sampled paper IDs; the column definitions; the full texts | the cells of `reverify.md`, by `tools/audit.py fill` | every cell filled | est. 10k per row |
| 7 | Judge the audits | main: `python3 tools/audit.py compare <topic>`; then `survey-pass` "Judgement audit" | `reverify-compare.md`; `faithfulness.md` | their verdicts, by `tools/audit.py judge`; `Judgement audit`, as `tools/audit.py line` prints it | `tools/audit.py line` prints the line, which it does only once every row has a verdict | est. 20–40k |
| 7 | End the round | main | the `Coverage test` line | on a round that did not converge, another round: back to "Draw the coverage sample" with the next R, skipping the audit rows; on `F1`, the user's review of the clusters, if given, in `Clusters` (the pass does not wait for it: see "Cluster review"), then `Ended`, in its form (`docs/formats.md`) | `F1`: no new cluster and at most one output change. Two rounds without convergence halt the pass (`H11`) | est. under 5k |
| 7 | Gate `G5` | main: `python3 tools/check.py <topic> --gate G5` | — | `Gates` | passes; the pass is over | 0 |

The expensive steps are verification, more than half the total, and screening, which grows with the pool. As a rough
planning figure, a pass on a topic of about 50 coreset rows is estimated at 2–2.5M tokens. That is an estimate, not yet
measured on a coreset pass. The figures are for planning and for reporting, never limits. The size of the pool and the
coreset follows from the rules — scope, alignment and the coverage test — and is never trimmed to meet a cost estimate.
When a pass runs well over or under the estimate, say so in the report with the reason, so that the estimates can be
corrected.

## When a pass ends

A pass ends in one of two ways. It `finishes` when the coverage test shows the coreset is sufficient. It `halts` when
something happens that the pass must not decide alone: a service or script fails, the clustering is degenerate, or a
step needs the user's permission. This list is the only definition of both. The steps refer to its IDs.

How a halt works:

1. The agent that meets the condition stops its job and records what is outstanding in Open work (`docs/formats.md`). An
   agent running in parallel with others returns those items under `Open work:` instead, since it never writes the
   shared sections.
2. A subagent cannot reach the user. It returns a report whose first line is `STOP: <id> — <the reason>`, with the
   measured numbers.
3. The main session records the halt in the log's `Halts` line with the decision `pending`, tells the user, and waits.
   The user decides whether and how the pass continues, and the decision replaces `pending`. Until then no gate after
   the last one passed can pass (`docs/gates.md`).
4. If the pass continues past something missing, such as a failed service, the output's legend says what was missing.
5. If the user decides to end the pass there, the main session completes `Tokens` and writes `Ended: halted (<id>)`.
   Such a pass needs only the gates it had passed, and its closing lines (`docs/gates.md`, "Halts and waivers").

A halt is not always a fault. `no structure`, for example, is a finding about the field.

**Finish.**

- `F1` — the coverage test converges: a round with no new cluster and at most one output change (step 7).

**Halt: services and scripts.**

- `H1` — a preflight check fails (step 0). A Graph API 429 counts as reachable: it means busy, and the scripts retry.
- `H2` — an Asta or WebSearch call still errors after the retry at the end of its step (`docs/external_services.md`,
  "Rate limits and errors").
- `H3` — a script fails after its own retries: a service error, or a crash with a Python traceback. Not `H3`: a script's
  printed `STOP: <id>`, which is that halt; a refusal that names the command to run first, such as
  `tools/assign.py clusters` before `remap`; and `tools/assign.py late` printing `RECLUSTER:` (exit 3). Failures of
  `tools/check.py` are `H9`.

**Halt: clustering, at step 3.** The main session shows the user the Clusters table and the viewer, and the pass resumes
from their decision (see "Cluster review").

- `H4` — `no structure` (see "When stability fails").
- `H5` — `no stable level`, still, after a targeted expansion and a rerun.
- `H6` — a cluster cannot be rated for alignment from the input.
- `H7` — a cluster the input expects (`expect`, in its `Clustering` section) is still missing after a targeted
  expansion.
- `H8` — the pool has fewer than 12 papers with an embedding, so no level of the grid can be computed (see "Clustering
  method"); `tools/cluster.py` prints `STOP: H8`, at step 3.

**Halt: integrity and verification.**

- `H9` — `tools/check.py` fails, and the agent whose work caused the failure cannot fix it.
- `H10` — after step 5, more than 20% of coreset rows are still `abstract`-sourced. The 20% is a first guess.

**Halt: convergence.**

- `H11` — two coverage-test rounds without convergence (step 7).

**Halt: permission.**

- `H12` — a paper should leave the pool. Deletion needs the user's explicit permission ("Rules for re-runs").

**Halt: requested by the user.**

- `H13` — the input's `Clustering` section asks for `review: before coreset`.

**Not end conditions.** These are handled inside the pass. Do not halt on them:

- a broad scope — note it in the `Clustering rationale` and continue ("When stability fails");
- `thin cluster` — expand the region and rerun;
- an unstable cluster — note it;
- clusters that trade papers — give the pair a bridge;
- an empty dissent slot — record what was searched;
- a query that returns no results — it has not errored;
- a single uncheckable row — it follows "Outcomes" in `docs/verification.md`;
- a pass that runs over or under its cost estimate — report the reason.

The main session records the end in the log's `Ended` line: `finished (F1)` or `halted (<id>)`, with the measured
numbers.

## Before a pass: the preflight check (step 0)

At the start of every pass, before any retrieval, check that every external service answers: `tools/preflight.py` for
the Graph API, arXiv, `uv` and the Asta key, then one call each to four Asta tools (`snippet_search`,
`search_papers_by_relevance`, `get_paper`, `get_citations`) and to WebSearch, by the agent. The checks are in
`docs/external_services.md` ("Preflight"). If any check fails, halt (`H1`). Never fall back silently to another method,
such as WebSearch alone.

## Stage 1: the pool

### Step 1: orient

Run WebSearch from the input's topic, its `Context`, and any research questions it states there or as targets in its
`Coreset Spec`. Collect candidate frontier papers and the vocabulary the field uses, and resolve each candidate to its
canonical ID (`docs/formats.md`, "Paper IDs"). Run orientation queries without a date restriction. In addition, run a
set of recency queries limited to the period since the last pass, or the last six months on a first pass, so that recent
work is not drowned out. Record that window in the log. It applies to the recency queries only: older work is in scope
throughout, and step 2's backward traversal is what reaches it.

Screen each candidate for scope ("Screening for scope" below). Add the in-scope ones to the pool with
`tools/assign.py add` (see step 2), and record the rest with `tools/assign.py reject`. The input's seed papers, if it
names any, enter the pool too. Then write the log's `Orientation` line: the queries; the themes, as the phrases the
field uses for its sub-topics, which step 2 searches; the input's seeds; and the frontier candidates, by ID. That line
is where step 2 starts its traversal and where step 4 looks for frontier papers, so a candidate or a theme named only in
a report is lost. A frontier candidate that cannot enter the pool, because Semantic Scholar does not know it or it has
no embedding, is not listed: it goes to Open work's `Papers that could not enter the pool`.

A frontier candidate is a paper the field currently treats as its state of the art or a turning point: in scope, and
either published within the recency window, or named as current by the sources orientation reads, such as a lab's
announcement, a leaderboard or a recent survey. An older paper that orientation finds is a pool paper, not a frontier
candidate. The distinction matters: step 2 traverses from every frontier candidate, the fringe `new` route is seeded
from them, and step 4 looks there first for frontier rows.

Use WebSearch, including OpenReview, lab blogs, system cards and release notes. It surfaces the current frontier and the
names people use for the themes. It skews recent and well-publicised, which is exactly what this job needs.

### Step 2: expand

Traverse backward from the frontier candidates, forward from the input's seeds and the frontier candidates, and run
relevance searches on the themes that step 1 named. Screen for scope. Everything in scope enters the pool.

Use Asta.

- Backward traversal (`get_paper` references) from frontier papers finds what the field is built on, which is where
  anchors come from.
- Forward traversal (`get_citations`) from the input's seeds and the frontier papers finds follow-ups, and among them
  the dissent. Step 4 repeats it from each cluster's anchor. It is targeted — searching a key paper's citers for
  challenges and extensions — not a crawl.
- `search_papers_by_relevance` and `snippet_search` fill in clusters that traversal does not reach.
- Asta supports date-restricted queries. Use them to keep recent work represented.

Traversal goes one step: the references of a frontier candidate, not the references of those references. Going further
is a judgement, under the stopping rule below.

Add each in-scope paper to the Pool table with `python3 tools/assign.py add <topic> <paper-id> ...`, never by hand.
Record each candidate judged out of scope with `python3 tools/assign.py reject <topic> <paper-id> <reason>`, or many at
once, one `<paper-id><TAB><reason>` per line on stdin: a rejection is a judgement too, and one that is not recorded can
be neither reviewed nor redone (`docs/gates.md`). If nothing was out of scope, end the `Expansion` line with
`; rejected: none`. Then the main session runs `python3 tools/pool.py <topic>`, which fetches the metadata and
clustering data for every pool paper by script (see `docs/tooling.md`). Metadata is never fetched through a model's
context.

Traversal from the frontier cannot reach papers the field has overlooked, so expansion ends with two fringe routes, run
by `tools/fringe.py collect` (see "Fringe routes" below). The script writes the candidates to a blind screening sheet,
`graphs/<topic>/fringe-screen.md`, one row per candidate. A `survey-pass` agent screens them for scope as it would any
other candidate, and records each verdict with `tools/fringe.py judge`: `yes` or `no`, with a short `reason`. A `maybe`
parks a row to come back to; it counts as unjudged until it is resolved. Then `tools/assign.py add-fringe` adds the
in-scope ones to the pool, refusing while any row is unjudged, and `tools/pool.py` runs again. This happens before
clustering, because adding them changes the clusters. The sheet stays in `graphs/<topic>/` as the record of the
screening (`docs/formats.md`, "`graphs/<topic>/`").

#### Screening for scope

Every candidate, from orientation, expansion, the fringe routes or a coverage test, is judged against the input's
`Topic`, and against `exclude` in its `Clustering` section, from its title and abstract:

- `In` — the paper's main contribution bears on the `Topic`: a method, a result, an analysis, a critique or a position
  about the topic's subject. Also in: a paper the input names.
- `Out` — the paper matches an `exclude` theme; or it touches the `Topic` only in passing, for example using a model the
  topic studies as a tool for something else, or citing the topic as motivation. A benchmark, dataset or model report is
  in only if its main finding is about the `Topic`.
- `Borderline is in` — when the abstract leaves it unclear, the paper is in. A wrong inclusion is visible and cheap: it
  sits in the pool, and the clustering places it at an edge. A wrong rejection leaves no trace in the pool at all.

The reason, for a rejection or a fringe verdict, is one line that ties the verdict to the `Topic`, such as "about image
classification; the topic is language-model reasoning". Never "not relevant".

When to stop. Orientation stops when two consecutive queries add no new frontier candidate. Expansion's required work is
in its `done when` (the order of operations). Beyond it, further traversals and queries continue only while they keep
paying: stop once a batch of about 50 screened candidates adds fewer than 5 papers to the pool. Record why expansion
stopped in the `Expansion` line (`stopped: ...`). These numbers are first guesses, to be revisited on a real pool.

#### Fringe routes

Fringe is not the dissent of the expansion job. A dissent paper engages a cluster and contradicts it, which is why
forward citations find it. A fringe paper is far from every cluster. They stand out by distance to their nearest
neighbours.

Use the scripts. Orientation and expansion both favour work that is well connected: relevance ranking rewards the
field's vocabulary, and traversal follows citations. A fringe paper is by definition poorly connected, so neither finds
it reliably. Two routes add overlooked papers to the pool at the end of step 2. Both run by script, at no model cost,
and the candidates are then screened blind: titles and abstracts in shuffled order, without the route that found them,
and without the year, which would give the route away, since `new` finds only recent work. A paper already rejected in
`rejected.md` is not collected again.

- `hidden` — papers cited by at least two pool papers, at least a year old, and the least cited overall for their age.
  The field's own work draws on them; the wider literature has not noticed them. This is where cross-field work turns
  up, such as older theory or psychology that current papers build on.
- `new` — Semantic Scholar recommendations seeded with the frontier candidates of the `Orientation` line and the pool
  papers most cited within the pool. The endpoint returns only the last two months of work, so this route catches what
  is too new to be cited.

The routes call the Semantic Scholar Graph API directly rather than going through Asta. It is the same literature either
way; the difference is that the routes need an endpoint Asta lacks and a volume no model should read. See
`docs/external_services.md`, "Semantic Scholar Graph API".

Once candidates are in the pool, step 3 measures how far each paper sits from the rest: the fringe score, defined in
"Clustering method". Step 4 chooses `fringe` rows from it.

### Step 3: cluster

A cluster is a group of papers that share an approach, a question, or a line of results: for example "process reward
models", or "does RL create reasoning capability or only select it". Clusters are computed from the pool. They are never
copied from the input, or from a previous survey's section headings.

Run the clustering method below, which chooses the level (scale from coarse to fine) from the pool's own data.
`tools/cluster.py` applies the input's `granularity` steering itself (see `docs/formats.md`), moving to another computed
level before anything is named. Then write the sheets (`tools/sheets.py`): `naming-sheet.md` and `fringe-sheet.md` in
`graphs/<topic>/`, compact summaries of the clustering report for the agents. The naming agent reads the naming sheet,
names and defines each computed cluster, rates its alignment (how directly it bears on the input's questions, or as the
input's `alignment` steering sets it), and writes the Clusters section, with each cluster's `computed` id, and the
`Clustering rationale` (see "Recording it"). For each `high` cluster, the definition also states its central claim: what
its papers hold to be true. Step 4's dissent search is judged against that sentence, so it has to be a claim a paper
could contradict, not a topic. `tools/assign.py clusters` then writes every pool paper's cluster into the Pool table.
Naming is judgement; membership is not. Do not move papers between clusters by hand. Build the graph viewer
(`tools/graph.py`); it shows the chosen parameters, each cluster's stability, and the level below.

Step 3 can loop once per region. A `thin cluster`, `no stable level`, or an `expect` theme that naming finds no cluster
for, each calls for a targeted expansion of that region ("When stability fails"). The Expand agent expands the region;
the main session fetches the new papers with `tools/pool.py` and reruns `tools/cluster.py`. These papers are not late
papers: the rerun clusters them with the rest. Once the clusters have names, the rerun is followed by
`tools/assign.py remap`, even on a first pass, and the clusters it did not match are named again. Each region is
expanded once; what is still wrong after that halts or is noted, as the order of operations says. Computed ids are
renumbered on every run, so a region is named by one of its papers, both in the `Expansion` line and when judging
whether a thin cluster after the rerun is the same region: it is if it holds that paper.

#### Clustering method

The aim is clusters that are well defined: a pass six months later should find recognisably the same ones. Stability is
measured directly, rather than assumed, so the method adapts to each literature instead of fixing a cluster count in
advance.

##### The similarity measure

A similarity measure says how alike two pool papers are, and the clustering groups papers that the measure rates as
alike. The measure is `combined`, built from two kinds of evidence in the pool's sidecar data:

- `text` — how alike the two papers' titles and abstracts are: the cosine similarity of their SPECTER2 embeddings.
- `refs` — how much of the literature the two papers build on together: the overlap of their full reference lists
  (bibliographic coupling).

Each is converted to per-paper neighbour ranks so that their scales match, and the two are mixed per pair with weight
`w = n / (n + c)` on `refs`, where `n` is the shorter of the two reference lists and `c` is 10 (`--c`). A pair with
little reference data leans on text.

Why one measure, fixed in advance. The method used to choose among `text`, `refs` and `combined` on every topic, by
stability. On `reasoning-legacy`, `combined` won clearly, and in every one of twelve replications. `refs` alone also
turns each paper without resolved references into a cluster of its own. So the choice cost compute and decided nothing
(audit of 2026-10-09, `Z3`).

##### Clustering

Clustering turns a similarity measure into groups, in three steps:

1. `Neighbour graph` — link each paper to the 10 papers the measure rates most similar to it (`k`, set with `--k`). A
   link carries that similarity as its weight. Only these nearest links are kept; the rest are dropped. Without that,
   every paper would be weakly linked to every other, and the groups would blur.
2. `Groups` — the Leiden algorithm splits the graph into groups whose papers are more strongly linked to each other than
   chance would predict, given how strongly each paper is linked overall. An analogy: finding the friend groups in a
   school from who sits with whom, discounting the people who sit with everyone.
3. `Resolution` — Leiden has one setting, the resolution, that trades few large groups against many small ones. For each
   level, the resolution is searched until the clustering has the target number of clusters, counting only clusters of
   two or more papers. If the exact target cannot be reached, the closest is used.

The result depends on a random seed, so a clustering is reproducible only with its seed recorded. `clusters.json`
records every seed the method uses in `params`, with the defaults and the package versions, which the script pins. The
stability tests check how much the seed matters.

Each target number of clusters is a level, and the method runs over a grid of levels: 3, 4, 5, 6, 8, 10, 12, 15, 18 and
22 clusters by default. Levels above a quarter of the pool's size are dropped, so that clusters average at least four
papers. A pool of fewer than 12 papers therefore leaves no level, and the pass halts (`H8`).

##### Stability tests

Stability is measured separately at each level. The tests are not steps in a sequence. They are independent ways of
disturbing the data, each compared against the same reference:

1. `Reference` — cluster the full pool once. The resolution found for the level is then held fixed for every rerun.
2. `Disturb and recluster` — each test reclusters a changed version of the data:
   - `time holdout` — keep only the papers older than a cutoff, and recompute the similarity measure on them alone,
     neighbour ranks included, as the pool would have been then. Three cutoffs, three, six and nine months back, each
     run with three random seeds: nine reruns. A cutoff that would keep less than 30% of the pool is skipped. If every
     cutoff is skipped, stability rests on resampling alone, and the report says so. It asks whether these clusters
     would have been found months ago, which is the six-month criterion run backwards.
   - `resampling` — drop a random 20% of the papers. Twenty reruns by default (`--reps`). It asks whether the clusters
     depend on which particular papers retrieval happened to find.
   - `seeds` — cluster the full pool again, with five different random seeds. It asks whether the algorithm's own
     randomness matters.
3. `Compare` — score each rerun against the reference, over the papers both contain, with the adjusted Rand index (ARI).
   ARI asks of every pair of papers whether both clusterings put them together; 1 is identical, 0 is chance.
4. `Combine` — the stability at a level is the mean of two numbers: the mean holdout ARI and the mean resampling ARI,
   with a standard error from the spread across reruns. Seed agreement is reported alongside but does not enter the
   score.

Each cluster also gets a clusterwise score, from the resampling reruns: its best overlap (Jaccard) with any cluster in
each rerun, averaged. A sub-cluster, the part of a finer-level cluster that falls inside this cluster, is scored on its
own papers, since the levels need not nest. Clusters and sub-clusters of fewer than three papers get none. The overall
score can hide a weak cluster: ARI counts pairs of papers, so a small cluster dissolving barely moves it. The
clusterwise score shows which clusters are solid, and it drives the single-cluster diagnostics in "When stability fails"
and the sub-cluster rule in "Sizing".

##### Choosing the level

Plot the stability against the number of clusters. The chosen level is the finest one whose stability reaches a
threshold `τ`, 0.75 by default, even if a coarser level dips below `τ` on the way. On `reasoning-legacy`, for example,
`τ` 0.70 would choose 12 clusters, past a dip to 0.67 at 8. Do not look for the largest single drop instead. Stability
is usually highest at the coarsest level, so the largest drop tends to be the first one, from a trivially stable split
into a still-stable one. `τ` is a convention, not a derived value, so the report also gives the level that `τ ± 0.05`
would choose. The clusters at the chosen level are the survey's clusters. The level below is kept as sub-clusters, shown
in the viewer and used by "Sizing" (step 4).

##### The null model

The same pipeline is also run once on structure-free data of the same size and shape: random vectors with the
embeddings' mean and spread, and reference lists reshuffled among papers, keeping each paper's list length and each
reference's popularity. Real stability well above the null at a level shows the structure there is real. The null model
has one job: it is the guard against `no structure` ("When stability fails"). It does not choose the level.

##### The fringe score

`tools/cluster.py` also scores every pool paper for how poorly the rest of the pool covers it. For each paper:

1. Average its similarity to its `k` nearest neighbours in the pool, once by text and once by references, and turn each
   into a distance: one minus the average.
2. Put the two distances on a common scale: each becomes a normal score, from its percentile in the pool. For
   references, the percentile is taken among the papers that have any.
3. Mix the two per paper, with weight `w = n / (n + c)` on references, where `n` is the paper's own number of resolved
   references, as in `combined`. Then rescale the mix so that every paper's score has the same spread, whatever its
   weight.
4. Rank the mixed score once, within the paper's age cohort: the 30 pool papers nearest to it by publication date. The
   score is the share of its cohort it exceeds, from 0 to 1. A pool of 30 papers or fewer is ranked as a whole.

A score of 0.95 means the paper is further from its nearest neighbours than 95% of its cohort. With a cohort of 30,
scores come in steps of about 1/30, so several papers often share the top score; the fringe sheet breaks those ties by
the mixed score, so its order is meaningful even where the scores are equal.

Each step has a reason:

- `The age cohort` — older papers sit further from current work simply because the field moved on. Without the cohort,
  the highest scores would go mostly to old papers. Nearest by date, rather than by calendar year, because a young field
  has most of its papers in its last two years, and a year-wide cohort would then hold most of the pool.
- `Per paper` — clusters can gather papers of the same period: overlooked older papers may settle into the cluster of
  the field's foundations, so a cluster-level signal can reflect age more than novelty. A fringe paper shows up as
  distance to its nearest neighbours, not as membership of an unusual cluster.
- `The weight on references` — a paper with no resolved references shares none with anything, so by references alone it
  would look maximally far from everything, for lack of data rather than for being overlooked. With the weight, such a
  paper is scored by its text alone.
- `The rescaling` — a weighted mix of two partly independent scores is less extreme than either one. Without the
  rescaling, the papers scored by text alone, those without references, would crowd both ends of the ranking.

##### Recording it

The naming agent records the clustering in the pass's entry in the retrieval log, the first section of
`surveys/<topic>.md` (see `docs/formats.md`). It copies the `Clustering` line from `tools/cluster.py`'s printout, which
the main session hands over, with the Clusters table's ids for the computed ones. That line gives the measure, the
level, the grid, `k`, `c`, the cutoffs, and the stability figures that decided the level. Next to it, the agent writes a
`Clustering rationale`: a short paragraph saying why the clusters look as they do. It covers the level and its margin
above `τ`, the spread of the clusterwise scores with the weak clusters named and diagnosed, the notes the printout
lists, and what any steering in the input's `Clustering` section changed. It interprets the figures rather than
repeating them, and it does not restate the steering request, which lives in the input. Log entries of earlier passes
are never rewritten, so each pass keeps the rationale for its own clusters. The full report stays in the sidecar, and
the viewer displays the parameters and the latest pass's rationale, so the user can see how the clusters were produced.

#### When stability fails

The coverage test has a clear consequence: add papers, or finish. The stability test needs one too. `tools/cluster.py`
diagnoses which of the cases below applies, prints each with its action, and the viewer shows them in its overview. Two
further findings need no action, and the tool prints them as notes for the `Clustering rationale`: a broad scope, and an
unstable cluster.

One rule holds in every case: never move papers between clusters by hand. The remedy is more data, a different level, or
a user override that is logged. Otherwise the clustering quietly becomes judgement again.

**The whole clustering.** No level is stable enough, or only a trivial one is. The null model says why:

- `no structure` — real stability exceeds random data's by less than 0.15 at every level. The pool may be one line of
  work, or too small to split. Halt for review (`H4`) at the level `tools/cluster.py` chose. Whether to go on with it,
  to pick a coarser one with the slider (`--level`, logged as an override), or to treat the pool as one line of work, is
  the user's call. Either way, that is a finding about the field.
- `no stable level` — structure is above random, but no level reaches `τ`. The usual cause is a thin pool: too few
  papers per region, or many papers with few resolved references (the tool reports the share with fewer than 10). Expand
  the thinnest regions in step 2 and rerun. If it is still unstable, take the coarsest level and halt for review (`H5`),
  so that the user chooses with the slider.

**A broad scope is not a failure.** Sometimes only the coarsest level reaches `τ`, and very stably (0.9 or more). The
pool then divides into a few clearly separate areas, while finer divisions are unstable. The clusters are real and
reproducible, so nothing has failed: it is a fact about the scope. `tools/cluster.py` prints it as a note. Say so in the
`Clustering rationale`, and continue at that level without halting. Whether a few broad clusters are enough for the
input is a question about the coreset, not about the clusters, and the coverage test (step 7) answers it.

**Single clusters.** The level is stable, but some clusters are not (clusterwise score below 0.6). Here instability is
information, and the action depends on the pattern:

- `thin cluster` — fewer than 10 papers. It dissolves into its neighbours, which the tool names. Expand that region in a
  targeted way and rerun. A thin cluster can be a sampling problem rather than a false one, and a handful of added
  papers may be enough to make it coherent. If it is still thin after one targeted expansion, keep it, and say so in the
  `Clustering rationale`; it does not halt the pass. The fringe routes are not rerun. A cluster of fewer than three
  papers has no clusterwise score, so the tool diagnoses it as thin on its size alone.
- `clusters trade papers` — two unstable clusters whose papers are grouped together in at least 20% of rerun pairs.
  Their boundary is open in the field itself. Keep both. At selection, give the pair a `bridge` paper, and note the
  tension for the Landscape.
- An unstable cluster that is neither of the above is printed as a note, and shown in the viewer. It does not halt the
  pass.

#### Cluster review

By default the pass does not halt here; the user reviews the clusters with the finished output. At the end of the pass,
before writing `Ended`, the main session shows the user the output, the Clusters table and the viewer, and records the
review in the `Clusters` line. The pass does not wait for it: without a review, `Clusters` keeps `not yet reviewed`. A
review given after `Ended` goes into the next pass's entry instead, since an ended entry is never rewritten. This is
affordable because verification belongs to a row, not to a cluster: a later change to the clustering costs re-selection
and the verification of new rows only (see "Changing the clusters after a pass"). Halt before selecting the coreset only
on one of the clustering conditions in "When a pass ends", `H4`–`H8`, or when the input asks for it (`H13`). Otherwise
proceed to step 4.

Apart from `H13`, these are signs that the topic was misread or the pool is degenerate. Found here, such a problem costs
a fraction of what it costs after verification. The main session shows the user the Clusters table and the viewer, and
records the halt and the user's decision in the log. Any change the user makes is recorded as a manual override.

How much detail to keep is a trade-off between detail and stability, so the level is shown to the user rather than only
reported, whenever the review happens. The viewer's similarity map lays papers out by the clustering measure itself, and
its level slider recolours the map at each computed level. If the user picks a different level, record it in the log as
a manual override, and rerun `tools/cluster.py <topic> --level <N>`, with `N` as the slider shows it. Then carry the
names over with `tools/assign.py remap` (see "Late papers").

#### Late papers

A late paper is one that reaches the pool after step 3: a coverage-test candidate that changed the output, a probe's
find, or a paper an output needs for a new claim. (Papers from a targeted expansion are not late: the recluster that
follows it places them.) It has no cluster, and nobody may give it one by hand. Late papers are added to the Pool table
like any other (`tools/assign.py add`), with an empty `cluster` cell; those rows are the queue. `tools/check.py` lists
them.

The queue is processed in batches, never paper by paper: after each dispatch that adds pool rows after step 3, and
always before a re-run of step 4. A batch is one command, `uv run tools/assign.py late <topic>`. It fetches the papers'
data, and assigns each to the cluster that its `k` nearest clustered papers favour, by the `combined` measure: each
neighbour votes for its cluster with its similarity, and the largest total wins. A paper with no positive similarity
under that measure is placed by text. Each paper is assigned against the clustering as it stood, never against other
late papers, so the result does not depend on order. The script records every assignment and prints the log's
`Late papers` line. Only then does a late paper take a role.

Recluster instead, with `tools/cluster.py`, in two cases. Both return the pass to step 3 ("Returning to step 3" below).

- `Many late papers` — late papers since the last full clustering would exceed 10% of the pool. `tools/assign.py late`
  refuses and says so. On `reasoning-legacy`, reclustering after dropping a random 20% of the papers agrees with the
  full clustering at ARI 0.76 at the chosen level, so a few late papers rarely move the clusters. A large addition can:
  adding the fringe candidates there, 118 at the time (16 of them from a route since dropped), moved the clustering to
  ARI 0.70.
- `A new cluster` — the coverage test judged that a candidate belongs to a cluster not in the Clusters table. That
  judgement never creates a cluster. It triggers a targeted expansion of the region (the `More data` lever), and the
  candidate and the expansion's papers are reclustered with the rest, even below 10%. If the region is real, it forms a
  cluster. If not, the computation places the papers in existing clusters, and the data has overruled the judgement.

After a recluster, carry the names over: `tools/cluster.py` matches the new clustering to the one the Clusters table
names, by shared papers, and `tools/assign.py remap <topic>` moves each name to the cluster it matched. Until then,
`tools/check.py` and `tools/assign.py clusters` refuse. `remap` clears the `computed` id of a named cluster that matched
nothing, and lists the new clusters. The naming agent then settles each: a new cluster that continues an old one, mostly
the same papers under a new boundary, takes the old name (rename); of two old clusters that merged, the one `remap`
matched keeps its name and the other is retired; any other unmatched cluster is retired. Retiring a cluster removes its
Clusters row, and its coreset block once the block's rows have moved to the blocks their papers were computed into. It
removes no paper. Every rename and retirement is said in the `Clustering rationale`. A clustering needs no remap until
the Clusters table has names: so not the first clustering of a first pass, but every rerun after naming, on any pass.

#### Returning to step 3

A recluster after step 3 does not get rows of its own: the pass goes back to step 3, and runs the order of operations on
from there for what changed. That reuses rows already written and checked, rather than a second set for the same work.

1. For a proposed cluster, start at step 3's "Targeted expansion" row, with the coverage report's theme and candidates
   as the region. On `RECLUSTER:`, start at "Fetch and recluster".
2. Run the step 3 rows from there on: recluster and `remap`, write the sheets, name (renaming or retiring every cluster
   `remap` did not match), write the clusters, and build the viewer.
3. Record the recluster in `Late papers`, by hand, in the second form of `docs/formats.md`, with the `changes:` line of
   `tools/cluster.py`'s printout. For a proposed cluster, set the round's `new clusters:` from the same line: the
   cluster, if it formed, which means the round has not converged; or `none (proposed <which>, not formed)`, which does
   not count against convergence.
4. Run step 4's "Set up the coreset blocks", which moves every coreset row to the block of the cluster its paper was now
   computed into, then step 7's Revise.

Until step 4 has run again, the plain check fails on what the return has yet to do: rows in another cluster's block, a
`bridge:` naming a retired cluster, roles not yet filled in a new or changed cluster, a dissent search not yet run for
it, rows not yet verified, and an `abstract` share over 20% until they are. That is the return's open work, not `H9`.
Every other failure is `H9` as usual. The open work is done when `tools/check.py` passes again.

Skip the gate rows of steps 3 to 5 on a return, until Revise is done. The pass's `Coverage test` line already makes the
plain check require every gate up to `G4`, so `--gate G2` cannot pass while the return's open work stands. The plain
check does the gates' work meanwhile, and the `Gates` line keeps the dates of the first passes.

A moved row keeps its role only if it still fills it: a moved dissent row must still contradict its new cluster's
central claim, and a `bridge:` row must still join its block's cluster to another. A round has at most one return to
step 3, since the expansion runs before the recluster.

## Stage 2: the coreset

### Step 4: select

Each coreset paper is selected to play one role in its cluster. Which roles a cluster gets follows its alignment (see
"Sizing" below). Record in the `selected because` column why each paper fills its role. Only a paper with a cluster can
take a role: one added to the pool after step 3 is a late paper, and is assigned first (see "Late papers"). Why the
roles exist, and why ranking alone is not enough, is in `docs/coresets.md` ("How coverage is achieved").

- `anchor` — what the cluster is built on. Anchors come from in-degree within the pool: usually the paper most cited by
  the other pool papers.
- `frontier` — where the cluster currently stands: its strongest recent result. `Recent` means published in the last 12
  months, or, in a cluster with nothing that recent, among its most recent papers. `Strongest` is judged in this order:
  a frontier candidate from the `Orientation` line, since WebSearch found the field discussing it; then impact, measured
  as citations per month since publication. The naming sheet lists each cluster's papers from the last 12 months, ranked
  that way. Say in `selected because` which of the two decided it.
- `dissent` — a paper that contradicts the cluster's central claim, the second sentence of its definition, breaks an
  assumption that claim depends on, or reports a negative result against it. Not dissent: a paper that names a
  limitation and then fixes it, or one that disagrees on a detail the central claim does not depend on. Dissent needs a
  dedicated search for each high-alignment cluster. Search the forward citations of the cluster's anchor and frontier
  papers, and run relevance queries phrased as challenges: "fails to", "does not", "revisiting", "limits of",
  "rethinking", etc. Quote, in `selected because`, the paper's claim that contradicts the cluster. Record each search in
  the `Dissent searches` line, naming every dissent row it found. A dissent paper must be a pool paper computed into
  that cluster. One found outside the pool is returned to the main session, which adds it, assigns it as a late paper,
  and dispatches Selection again for its cluster; one computed into another cluster cannot be this cluster's dissent,
  though it may make a `bridge`. If a search finds no dissent, record that the slot is empty and what was searched. An
  empty dissent slot is information about the cluster, not a failure.
- `bridge` — a paper that connects two clusters, for example by applying one cluster's method to another's question.
  Written `bridge:<other-cluster-id>`, in the block of the cluster the paper was computed into, which must be one of the
  two. It is optional, but bridges are where the Landscape's structure becomes visible. Where the clustering diagnostics
  report two clusters trading papers, one of them gets a bridge paper.
- `fringe` — a paper that carries an idea no other coreset row has, and that the field has so far overlooked: it sits
  far from its nearest neighbours in the pool, for its age. It is placed in the cluster it was computed into, but it
  does not represent that cluster; it represents what the clusters leave out. Fringe comes last, because its test is
  relative to the rest of the coreset. Start from the pool papers with the highest fringe scores (see "Clustering
  method"), listed in `graphs/<topic>/fringe-sheet.md`. Most papers far from their neighbours are there for a good
  reason. So keep a paper only if its `selected because` can name, in one sentence, the idea it carries that no other
  coreset row does. Five to ten per topic.

#### Sizing

A cluster gets more rows the more directly it bears on the input, not the more papers it has:

- `high` — anchor, frontier and dissent at minimum. Add a second frontier paper or a bridge where the cluster is
  internally divided.
- `medium` — anchor and frontier.
- `low` — anchor only. That is enough for the Landscape to be honest about the cluster existing.

The number of clusters is not chosen; it is the stable level found in step 3. Where the level below it splits a
high-alignment cluster into two or more sub-clusters with a clusterwise score of at least 0.6, the cluster counts as
internally divided and gets the extra frontier or bridge. Expect roughly two to four rows per cluster, plus the topic's
five to ten `fringe` rows. Past roughly 80 rows, check whether any role is filled twice. If none is, the size is
legitimate, for example on a topic with many `high` clusters; report the count and the reason.

### Step 5: characterise and verify

Characterise and verify every selected paper. See `docs/verification.md`.

Every verified row quotes the paper's own full text, fetched by `tools/fulltext.py`. The main session fetches every
coreset row's full text in one batch before it dispatches verification, with
`uv run tools/fulltext.py <topic> --abstract`. Why one batch: arXiv asks for three seconds between requests, and
parallel agents each fetching their own papers would together break that. Verification agents then only read the files,
through `tools/fulltext.py show` and Grep. Asta's `snippet_search` helps find the passage a claim rests on, but a
snippet is never the quoted source. WebSearch may corroborate a claim about a paper but must never be its only source.

A row whose paper has no fetchable full text is uncheckable. Its role is offered to a verifiable paper first: the main
session dispatches Selection again for that cluster. If no verifiable paper fills the role, the row stays, marked as
needing verification (`docs/verification.md`, "Outcomes"). A `fringe` row is not replaced, since by definition no other
paper carries its idea.

## Stage 3: output and coverage test

### Step 6: write the output

Write the output in the main session, from the Clusters section and the coreset rows alone, never from the pool. Its
analyses and format are in `docs/formats.md`. A claim that needs a paper not yet in the coreset needs that paper added
first: to the pool with `tools/assign.py add` if it is not there, as a late paper (see "Late papers"), then to the
coreset in a role, verified.

The survey is mostly its Pool table, so read only the two sections the output rests on, with
`python3 tools/check.py <topic> --print Clusters` and `--print Coreset`. A coreset of 50 rows is about 20k tokens. Write
each claim from the rows it cites, and check it against them. Where a claim turns on a detail, such as a number, its
condition or a limitation, check it against the row's evidence file, `graphs/<topic>/evidence/<id>.md`. That is a local
read, so it needs no outside call. A row whose evidence does not bear out the claim is a matter for verification:
dispatch "Verification" for that row, rather than writing the claim from memory.

### Step 7: the coverage test

This is the finishing rule (`F1`). The coreset is sufficient when adding papers stops changing the output. Measure that
directly:

1. Draw the sample: 10 to 15 candidates that are not in the coreset. The main session draws ten from the pool by script,
   with `uv run tools/coverage.py draw <topic> <R>`. It takes them at random, with the seed recorded, from the
   worst-covered quarter of the pool: the papers whose nearest coreset row is furthest from them, under the measure the
   clustering uses. Those are the papers the coreset is likeliest to leave out. The script writes them to the round's
   sheet, `graphs/<topic>/coverage-<R>.md`, with the coreset's radius: how far the worst-covered pool paper is from its
   nearest row. The agent then adds up to five candidates from a fresh recency query, run as in step 1 (WebSearch,
   limited to the pass's `Recency window`, extended to the day of the round), since new work is what the pool cannot yet
   hold. Record the query with `tools/coverage.py query`, whatever it found, so that a round without recency candidates
   shows the query ran; on a quiet topic it may find none. A candidate with no paper ID cannot join the pool or the
   coreset, so take the next result in its place, and note it in Open work's `Papers that could not enter the pool`.
2. For each candidate, read its abstract through Asta, and snippets where the abstract leaves the verdict open. Ask two
   questions. Does it belong to a cluster not yet in the Clusters table? Would it change a claim in one of the coreset's
   targets — a landscape axis, an assumption, a gap, or an answer to a question the input's `Coreset Spec` declares?
   Targets are defined in `docs/formats.md` (`Coreset Spec`).
3. Record every candidate's verdict, with a one-sentence reason, in the round's sheet, the ones that change nothing
   included, with `python3 tools/coverage.py judge <topic> <R>`; the recency candidates go in with `--recency`
   (`docs/formats.md`, "The coverage sheet"). Then `python3 tools/coverage.py line <topic> <R>` prints the round's
   `Coverage test` line for the pass's entry in the retrieval log:
   `round R: K of N sampled candidates changed the output`, counted from the sheet. It names each candidate that did,
   with the target and the reason. Paste it as printed, since `G5` compares it with the sheet; so give `judge` reasons
   that state the claim changed, such as a new gap or a revised assumption. If a verdict changes later, say because
   verification shows the reason overstated, judge it again and paste the line again. A candidate judged only to open a
   new cluster is not in K: the line names it in a placeholder under `new clusters:`, settled after the recluster
   ("Returning to step 3").

Every candidate counted in K joins the coreset, verified, in Revise. Its role follows what it changed: `dissent` if it
contradicts its cluster's central claim or breaks an assumption the claim rests on, which covers a gap that is a
tension; `bridge:<id>` if what it changed is a connection between clusters; `fringe` if it carries an idea no other row
has, within the quota; otherwise `frontier`. A paper whose role cannot be had, because its cluster is not `high` and so
states no central claim, or the `fringe` quota is full, takes `frontier` too. Its `selected because` says what it
changed. A cluster may take more rows than "Sizing" asks for this. A `dissent` row found this way needs no
`Dissent searches` entry: its trace is the `Coverage test` line.

What counts as a change. A candidate changes the output if it would add a claim to a target, remove one, or reverse one:
a new axis, assumption, gap or answer; an assumption shown not to hold; a result that turns out to depend on a condition
the output does not state. It does not change the output if it would only add a citation to a claim already made, refine
a number or a wording that leaves the claim standing, or change `Questions` or `Reading` alone, which are not targets.

The pass finishes (`F1`) when a round produces no new cluster and at most one output change. Say so in the log's `Ended`
line, in the form `docs/formats.md` gives. Either way, the papers the round counted in K are processed as late papers
("Late papers"), given their roles, and the output is revised; on a round that did not converge, sample again. Two
rounds without convergence halt the pass (`H11`). A proposed cluster goes through a targeted expansion and a recluster
before the round is judged ("Returning to step 3").

From a coverage round on, the plain check fails until every paper the round counted is a coreset row, verified from the
full text or marked uncheckable (`g4.counted-rows`), and on the open work of a return to step 3, if there was one
("Returning to step 3"). That is Revise's open work, not `H9`. Revise is done when `tools/check.py` passes again. Its
gate rows are skipped, for the same reason as on a return: the `Coverage test` line already makes the plain check
require `G3` and `G4`.

How strong this is. `F1` is a sampled test, so it bounds how much the coreset misses rather than proving it misses
nothing. If K of the ten drawn candidates change the output, the share of the worst-covered quarter that would change it
could still, at 95% confidence (a one-sided Clopper–Pearson bound), be as high as 26% for K = 0, and 39% for K = 1.
`tools/coverage.py line` prints the bound for the round. It holds for the worst-covered quarter, since the draw is
random within it. The rest of the pool sits closer to a coreset row, so it probably changes the output less often; that
is reasoned, not measured. The recency candidates are judged and counted in K like the others, but they are not a random
draw, so the bound leaves them out. Either way, "sufficient" means this much, and no more. Give the bound and the radius
of the last round in `Ended`, with the measured numbers.

Do not finish on the fraction of screened candidates already present in the survey instead. On an active topic that
fraction falls as the seeds improve, because each better seed opens a larger neighbourhood, so it may never reach any
threshold.

#### Auditing the judgements

The gates check that each judgement was recorded, not that it was right. Two audits measure how often it was right, on a
small random sample, once a round has converged and its Revise is done. Their result is the log's `Judgement audit`
line, which `G5` requires, so that every finished pass reports it.

- `Re-verification` measures verification. `tools/audit.py reverify` draws a random 10% of the rows verified from the
  full text, at least five. A fresh agent fills those rows' claim cells and dimensions from the paper's full text alone.
  It is given the paper IDs, the column definitions and the `Dimensions` line, and never sees the survey's rows or their
  evidence. `tools/audit.py compare` then sets each of its cells beside the survey's.
- `Faithfulness` measures the output. `tools/audit.py trace` draws 15 of the output's sentences that cite a coreset
  paper, or all of them if there are fewer, leaving out `Questions` and `Reading`, which recommend rather than claim,
  and sets each beside the cited rows' cells and evidence quotes.

A second agent, which wrote neither the rows nor the output, judges both sheets. Per cell of the re-verification:

- `agree` — the two state the same claim: the same method, setup, number and condition, whatever the wording;
- `partly` — neither contradicts the other, but one is more complete or more precise, such as one stating a condition
  the other omits;
- `differ` — they state different claims, or one states a claim where the other has `n/a`.

Per sentence of the output:

- `supported` — every claim in the sentence is stated in the cited rows or their evidence, a synthesis across them
  included;
- `partly` — its main claim is supported, but a detail is not, such as a number, a condition or a scope;
- `unsupported` — its main claim is not in the cited rows or their evidence.

The audits measure; they do not repair. The main session reports each `differ` and `unsupported` to the user with the
pass's end, and the user decides whether they are fixed. Fixing only the sampled cases would leave the rate describing
nothing. The rates are first measurements: nothing yet says what rate is acceptable.

## Later passes

### Rules for re-runs

On revisiting a topic, add a new dated pass to the retrieval log. A later pass may add clusters, pool entries and
coreset rows.

- **Demotion is not deletion.** If a better paper is found for a role, the old row may leave the coreset. The paper
  stays in the pool, and the log records the demotion and why.
- **Deletion needs permission.** Remove a paper from the pool only if it is conclusively shown to be factually wrong or
  out of scope, and only with the user's explicit permission. Asking is a halt (`H12`): state the argument in the
  `STOP:` report, and the main session puts it to the user.
- **Corrections are logged.** Edit a row in place and record the change in that pass's log entry.
- Where a later pass supersedes a caveat recorded in an earlier one, leave the earlier text intact and add a pointer
  saying what superseded it. The old entry is an accurate record of the pass it describes.

### Changing the clusters after a pass

The user can steer the clustering through a fixed set of levers. Each can be given in advance, in the input's
`Clustering` section, or requested after a pass. Membership is not one of them: papers are never moved between clusters
by hand.

- `Level` — a coarser or finer clustering, chosen with the viewer's slider. Merging two clusters means a coarser level;
  splitting one means a finer level.
- `Alignment` — how directly a cluster bears on the input. It sets the cluster's rows and dissent searches.
- `Names and definitions` — judgement only; edit them directly.
- `Scope` — a cluster the user does not want. Rate it `low`, which keeps one anchor so the Landscape stays honest. If it
  is genuinely out of scope, its papers leave the pool under the deletion rule above, with permission.
- `More data` — seeds or queries for a region, followed by re-clustering. This is the route for "these papers belong
  together".

A change requested after a pass runs as an incremental pass, logged as a manual override. Re-cluster if the level or the
pool changed, and carry the names over (`tools/assign.py remap`, see "Late papers"). The clusters that changed are the
ones `remap` did not match. Re-run step 4 for them, keeping every verified row that still fills a role and demoting the
rest. Verify only the new rows, then rerun the coverage test and revise the output.

Dimensions are the exception to cheap late changes. A dimension added after verification has to be re-derived from the
body text of every row, which costs a large part of a verification round. Declare dimensions in the input where
possible.

### Matching clusters across passes

On a later pass, match the new clustering to the previous one, keep the ids and names of matched clusters, and log
splits, merges, new clusters and vanished ones. `tools/cluster.py` does the matching (`tools/match.py`, `match`)
whenever a previous clustering exists, and `tools/assign.py remap` keeps the names. The main session hands both
printouts to the naming agent, which records the result under `Clustering rationale`.

When most clusters fail to match, nothing yet tells whether the field moved or the method's settings did. Until it does,
the unmatched clusters are named afresh like new ones, the `Clustering rationale` says that most clusters failed to
match, and the main session raises it with the user at the cluster review that comes with the output.

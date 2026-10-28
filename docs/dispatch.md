# Dispatch: the execution model and main-session rules

## Execution model

The two halves of the pipeline run in different contexts. (The three stages of a pass — pool, coreset, output — are
defined in `docs/process.md`.)

**`inputs/` → `surveys/` runs in subagents.** The main session reads the input, plans, runs the scripts, and dispatches.
It writes to the survey only the new survey's empty sections, the empty coreset blocks of step 4, the log lines and Open
work items its rows in the order of operations list, and the lines parallel agents return. Retrieval results stay in the
subagents' contexts and never enter the main session.

- `survey-pass` runs on a capable model and does work whose mistakes leave no trace: orientation, screening for scope,
  naming the computed clusters, selecting roles, dissent searches, verification, the coverage-test judgements, and
  probes.
- `survey-edit` runs on a cheaper model and does mechanical work that `deeper_research/check.py` can catch:
  restructuring tables, moving rows between blocks to match the computed cluster assignment, regenerating the bib. Pool
  metadata is filled by `deeper_research/pool.py`, not by an agent.

**`surveys/` → `outputs/` runs in the main session.** Reading a finished survey and writing the analysis is not
delegated. The main session also owns cluster review. When step 3 halts for review, or when the output is presented, it
shows the user the `Clusters` table and the viewer, and records their review in the log. A change the user asks for is
dispatched as an incremental pass (`docs/process.md`, "Changing the clusters after a pass").

## Rules for the main session

- Do not call outside services for a pass, but rather dispatch a subagent. A single call to check connectivity, or to
  verify one row as a subagent's report makes you doubt, is fine. Scripts in deeper_research/ are exempt: their results
  go to files, not into your context.
- Run a pass down the order of operations in `docs/process.md`: it is the checklist. Confirm each row's `done when`
  before starting the next. At each gate row, run `uv run python -m deeper_research.check <topic> --gate G<n>`, and do
  not start the next step until it passes (`docs/gates.md`). To resume a pass in a new session, start from
  `uv run python -m deeper_research.check <topic> --status`.
- Use the repo's scripts and nothing else. Neither you nor a subagent writes programs of its own, saved or inline, or
  files beyond those the order of operations names. A missing tool is a gap to report to the user, not to work around
  (`.claude/agents/survey-pass.md`, "Tools and files").
- Run the scripts of the order of operations yourself, between dispatches, and hand the next subagent the printout it
  needs. A subagent runs only the scripts its own job needs, such as `deeper_research/fulltext.py show` during
  verification. A script that fails after its own retries halts the pass (`H3`).
- Write the log lines that the `writes` column of the order of operations gives to `main`. That column is the only
  authority on who writes what. `Clustering` is printed by `deeper_research/cluster.py` but written by the naming agent,
  which replaces the computed cluster ids with names. A pass's log entry is written as the pass goes; a line may be
  updated until the pass ends, never after. The one exception is `Gates`, which takes `G5` after `Ended`, since `G5`
  checks `Ended`.
- After every dispatch, follow the "After every dispatch" row. Append the dispatch's tokens to `Tokens`, as the harness
  returns them with the result (`docs/formats.md`, "1. Retrieval log"), so that a halt or a lost session does not lose
  them. If it added pool rows, fetch them first: `uv run python -m deeper_research.pool <topic>` until step 3 is done,
  `uv run python -m deeper_research.assign late <topic>` after it. Paste the `Pool` line the fetch prints. Only then run
  `uv run python -m deeper_research.check <topic>`, while you still know which agent caused any damage. After an agent
  that changed the coreset, run `uv run python -m deeper_research.bib <topic>` first, since the check compares the two.
  A failure the agent cannot fix halts the pass (`H9`).
- Subagents may run in parallel **only on disjoint sections of the survey**. Cluster blocks partition the Coreset table
  naturally, so parallel verification or selection work splits by cluster. Group the clusters into a few blocks per
  agent, spreading the `high` ones, which cost the most. The pool is a single table, so only one agent writes to it at a
  time. Screening agents may run in parallel on disjoint row ranges of one screening sheet: they write only their rows'
  verdicts, through the sheet's `judge`, which locks the sheet while it writes, and never the pool. The log and Open
  work are shared too: agents running in parallel do not write them, but end their reports with the lines meant for
  them, under `Log:` and `Open work:`, and you write those once all have returned.
- Some work spans clusters and cannot be split: fringe selection, which is judged against the whole coreset; bridges,
  which join two clusters; and the coverage test, which reads the whole output. Run each once, by one agent, after the
  per-cluster work is done.
- Instruct subagents to write each row as they finish it, not to batch all writes to the end. Subagents die — on spend
  limits, on timeouts — and partial work on disk beats complete work lost.
- A subagent's report that starts with `STOP:` is a halt (`docs/process.md`, "When a pass ends"). Tell the user what
  halted and why, wait for their decision, and record it in the log's `Halts` line.
- Do not take a subagent's report at face value. Check that what it wrote on disk matches what it reports, and run the
  plain check ("After every dispatch"). Where it reports on a paper, check the row against the report: reports have
  overstated what a paper showed. When writing the output, check each claim against the rows it cites and their evidence
  files (`docs/process.md`, step 6).

## Briefs

A brief is what you hand a `survey-pass` agent for one job, and what it hands back. Each dispatch prompt gives:

```text
Topic: <topic>. Job: <brief name> (docs/dispatch.md, "Briefs"), step <n> of the pass of YYYY-MM-DD.
Scope: <the clusters, rows or candidates this agent owns>.
Handed over: <the printouts listed below, verbatim>.
```

A brief does not restate the method. Hand over printouts and file paths, never the contents of a file in
`graphs/<topic>/` (`docs/formats.md`, its last section). Every report follows `.claude/agents/survey-pass.md`: what was
done, what was added or changed, the judgement calls, and `STOP: <id> — <the reason>` as its first line if the job
halted.

### What each agent reads

The agent reads its own brief below, and then only the spec sections the brief lists under `Read`, by their headings.
Every agent also reads `docs/process.md`, "When a pass ends", for the halts. `CLAUDE.md` and the agent's own
instructions are loaded for it. The rest of the spec is rationale or main-session procedure, and costs reading without
changing what the agent does. If a listed section points elsewhere for something the job needs, follow that pointer.
Read the survey itself one section at a time, with `uv run python -m deeper_research.check <topic> --print <section>`,
or `--print Coreset:<cluster id>` for one block, never whole: it is mostly its Pool table.

### The briefs

- **Preflight** (step 0). Hand over: the printout of `deeper_research/preflight.py`. The agent makes one cheap call each
  to `snippet_search`, `search_papers_by_relevance`, `get_paper`, `get_citations` and WebSearch, and writes the whole
  `Preflight` line: its own five checks, then the script's half as printed. Returns: ok, or `STOP: H1`.
  - Read: `docs/external_services.md`, "Preflight"; `docs/formats.md`, "1. Retrieval log".
- **Orient** (step 1). Hand over: the recency window, which is the time since the last pass, or six months on a first
  pass; on a later pass, the previous `Orientation` line. The agent runs WebSearch, screens each candidate for scope,
  resolves the in-scope ones to their IDs, asking Asta for `externalIds`, adds them with
  `deeper_research/assign.py add`, and records the rest with `deeper_research/assign.py reject`. It adds the seed papers
  the input names. Its themes are step 2's search queries, each searched as an exact phrase, so they are written as
  papers write them, and include every other name the input gives the topic. Writes: Pool rows; rejections;
  `Orientation`, with the themes, the seeds and the frontier candidates; `Recency window`; `Errored queries`, `none` if
  none; Open work: papers that could not enter the pool. Returns: why it stopped, and the candidates it was unsure
  about.
  - Read: `docs/process.md`, "Step 1: orient" and "Screening for scope"; `docs/external_services.md`, "WebSearch and
    WebFetch", "Tools, and when to use each" and "Rate limits and errors"; `docs/formats.md`, "Paper IDs", "1. Retrieval
    log" and "5. Open work"; `docs/tooling.md`, "Pool table".
- **Screening** (step 2, and every targeted expansion). One agent per block of at most 100 rows, run in parallel. Hand
  over: the sheet's path, `graphs/<topic>/expand-screen.md` or `graphs/<topic>/fringe-screen.md`, and the range of row
  numbers (`#`) this agent owns. The agent reads the input's `Topic` and `Clustering` sections, which it screens
  against, then judges each row in its range in or out of scope from its title and abstract, and records the verdicts
  with the sheet's own `judge`, `deeper_research/expand.py judge` or `deeper_research/fringe.py judge`, in batches as it
  goes. It resolves every `maybe` before it finishes, and touches no row outside its range. On the fringe sheet it
  screens blind: it does not look up a paper's route, year or citations, which would unblind it. Writes: the `in scope`
  and `reason` cells of its rows. Returns: the rows it was unsure about, and that every row in its range is judged,
  which it confirms by reading them again: `judge`'s count of unjudged rows covers the whole sheet.
  - Read: `docs/process.md`, "Screening for scope"; `docs/tooling.md`, "Screening sheets".
- **Naming** (step 3). Hand over: the printout of `deeper_research/cluster.py`, which has the diagnostics, the notes and
  the `Clustering` line; the regions a targeted expansion covered, by paper ID or theme, and whether each is still thin;
  on a later pass, or after a rerun, the printout of `deeper_research/assign.py remap`. The agent reads
  `naming-sheet.md` and the input, and names, defines and rates every computed cluster that has no name; for each `high`
  cluster, the definition's second sentence states its central claim. After a recluster, it also settles every cluster
  `remap` did not match: renamed or retired (`docs/process.md`, "Late papers"). Writes: Clusters rows, with `computed`
  ids; `Clustering`, with the Clusters table's ids; `Clustering rationale`; `Clusters`. Returns: the ratings it was
  unsure about, and any `expect` theme with no cluster, for a targeted expansion. Halts: `H6`; `H7` only if a targeted
  expansion for that theme has already run.
  - Read: `docs/process.md`, "Step 3: cluster", "Recording it" and "When stability fails", on a later pass "Matching
    clusters across passes", and after a recluster "Late papers"; `docs/formats.md`, "2. Clusters" and "1. Retrieval
    log".
- **Selection** (step 4), one agent per block of clusters, in parallel; and in step 5, for a cluster with an uncheckable
  row. Hand over: the block's cluster ids and their alignment, and the lines of the `deeper_research/check.py` printout
  for those clusters (pool size, roles filled, in-degree leaders); the log's `Dimensions` line; in step 5, the
  uncheckable rows instead; in step 7's Revise, each paper the coverage round counted, with what it changed and its
  proposed role. The agent fills anchor, frontier and dissent per "Sizing" (`docs/process.md`, step 4), and the extra
  frontier or bridge for a `high` cluster that `naming-sheet.md` marks internally divided. A dissent row's
  `selected because` quotes the claim that contradicts the cluster's central claim. It drafts every cell from the
  abstract, dimensions included, with `source` `abstract`; verification re-derives them from the body text. On a later
  pass, it keeps every verified row that still fills a role, and demotes the rest. In step 5, it looks for another paper
  to take the uncheckable row's role, preferring one with an arXiv ID (its ID is one, or
  `jq '.papers["<id>"].arxiv' graphs/<topic>/pool.json` gives one), since those are the papers whose full text can most
  surely be fetched; the main session's next batch fetch settles it. It demotes the old row if it finds one. Writes:
  Coreset rows, in its blocks only. Returns, under `Log:`, its parts of `Dissent searches` and `Demotions`, and under
  `Open work:`, its empty roles and its new rows, for `Rows needing verification`; and, under `For the pool:`, dissent
  papers it found outside the pool, which the main session adds and assigns before dispatching Selection again for their
  cluster.
  - Read: `docs/process.md`, "Step 4: select" and "Sizing", on a later pass "Rules for re-runs", and in Revise "Step 7:
    the coverage test"; `docs/formats.md`, "3. Coreset", "1. Retrieval log" and "5. Open work";
    `docs/external_services.md`, "Tools, and when to use each" and "Rate limits and errors".
- **Bridges** (step 4), once, after selection, and only if `deeper_research/check.py` notes a pair of clusters that
  trade papers without a bridge. Hand over: those pairs; the log's `Dimensions` line. Writes: `bridge:` rows; Open work:
  their `Rows needing verification`, and an `Empty roles` entry for a pair left without a bridge. Returns: pairs left
  without a bridge, and why.
  - Read: `docs/process.md`, "Step 4: select" and "Sizing"; `docs/formats.md`, "3. Coreset" and "5. Open work";
    `docs/external_services.md`, "Tools, and when to use each".
- **Fringe selection** (step 4), once, last. Hand over: the path of `fringe-sheet.md`, rewritten after selection; the
  log's `Dimensions` line. The agent reads the abstracts through Asta (`get_paper_batch`) and the coreset rows, and
  keeps five to ten papers that each carry an idea no other row has. Writes: `fringe` rows, in the block of each paper's
  computed cluster; Open work: their `Rows needing verification`. Returns: the near misses.
  - Read: `docs/process.md`, "Step 4: select" and "The fringe score"; `docs/formats.md`, "3. Coreset" and "5. Open
    work"; `docs/external_services.md`, "Tools, and when to use each".
- **Verification** (step 5), one agent per block of clusters, in parallel. Hand over: the block's cluster ids, and which
  rows: all, or only those still `abstract` (in step 7's Revise, the new rows and any row still `abstract` whose full
  text the fetch now finds); the papers the batch fetch could not fetch; the log's `Dimensions` line. The agent follows
  `docs/verification.md`, reading the fetched full texts through `deeper_research/fulltext.py show`; it does not fetch.
  Writes: the rows' cells and `source`, and each row's evidence file. Returns, under `Log:`, its
  `Corrections to existing rows`, and under `Open work:`, its rows still needing verification, with why; and the
  uncheckable rows, for the main session to offer their roles to Selection.
  - Read: `docs/verification.md`, "Verification"; `docs/tooling.md`, "Full text"; `docs/formats.md`, "3. Coreset", "1.
    Retrieval log" and "5. Open work"; `docs/external_services.md`, "Tools, and when to use each".
- **Coverage test** (step 7), once per round. Hand over: the round's number; the path of `coverage-<R>.md`, which
  `deeper_research/coverage.py draw` has written; the pass's `Recency window`, which the fresh query extends to today.
  The agent runs the recency query and records it with `deeper_research/coverage.py query`, whatever it found; adds up
  to five of its candidates with `deeper_research/coverage.py judge --recency`, each with its title; judges every
  candidate against the output with `deeper_research/coverage.py judge`; and adds every recency candidate that changed a
  target, or belongs to a proposed cluster, with `deeper_research/assign.py add` (drawn candidates are pool papers
  already). Writes: the sheet's verdicts, recency rows and query; Pool rows; `Coverage test`, pasted as
  `deeper_research/coverage.py line` prints it. Returns: each proposed new cluster, with its region, for a targeted
  expansion; the bound the line's printout gives.
  - Read: `docs/process.md`, "Step 7: the coverage test", "Screening for scope" and "Late papers"; `docs/formats.md`,
    "`Coreset Spec`", "1. Retrieval log" and "The coverage sheet"; `docs/external_services.md`, "WebSearch and
    WebFetch", "Tools, and when to use each" and "Rate limits and errors"; `docs/tooling.md`, "Pool table" and
    "Coverage".
- **Re-verification** (step 7), once, by a fresh agent. Hand over: the path of `reverify.md`, which
  `deeper_research/audit.py reverify` has written; the log's `Dimensions` line. Nothing else: not the survey, the rows
  or their evidence, which would unblind it. The agent reads each sampled paper's full text through
  `deeper_research/fulltext.py show`, as verification does, and fills every cell from it with
  `deeper_research/audit.py fill`, writing `n/a` where the column's definition allows. It never opens `surveys/`,
  `outputs/` or `graphs/<topic>/evidence/`. Writes: the cells of `reverify.md`. Returns: the cells it was unsure about.
  - Read: `docs/process.md`, "Auditing the judgements"; `docs/formats.md`, "3. Coreset"; `docs/verification.md`,
    `What "verify" means`; `docs/tooling.md`, "Full text" and "Judgement audits".
- **Judgement audit** (step 7), once, by an agent that wrote neither the rows nor the output. Hand over: the paths of
  `reverify-compare.md` and `faithfulness.md`. The agent judges every row of both sheets by the rubric, from the sheets
  alone, and records the verdicts with `deeper_research/audit.py judge`. Writes: the verdicts; `Judgement audit`, as
  `deeper_research/audit.py line` prints it. Returns: each `differ` and `unsupported`, for the main session to report to
  the user.
  - Read: `docs/process.md`, "Auditing the judgements"; `docs/formats.md`, "1. Retrieval log"; `docs/tooling.md`,
    "Judgement audits".
- **Probe** (on request). Hand over: the question, and the coreset rows closest to it. The agent follows
  `docs/verification.md` ("Probes") and adds each paper it finds with `deeper_research/assign.py add`; they are late
  papers. Writes: `Probes`. Returns: found, with IDs, or survived a refutation attempt.
  - Read: `docs/verification.md`, "Probes"; `docs/external_services.md`, "Asta" and "WebSearch and WebFetch";
    `docs/formats.md`, "1. Retrieval log"; `docs/tooling.md`, "Pool table".

A `survey-edit` job gets the exact change to make, and the `deeper_research/check.py` failure it is to fix, if any.

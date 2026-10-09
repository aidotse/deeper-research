# Dispatch: the execution model and main-session rules

## Execution model

The two halves of the pipeline run in different contexts. (The three stages of a pass — pool, coreset, output — are
defined in `docs/process.md`.)

**`inputs/` → `surveys/` runs in subagents.** The main session reads the input, plans, runs the scripts, and dispatches.
It writes to the survey only the new survey's empty sections and the log lines listed under "Rules for the main
session". Retrieval results stay in the subagents' contexts and never enter the main session.

- `survey-pass` runs on a capable model and does work whose mistakes leave no trace: orientation, expansion and
  screening, naming the computed clusters, selecting roles, dissent searches, verification, the coverage-test
  judgements, and probes.
- `survey-edit` runs on a cheaper model and does mechanical work that `tools/check.py` can catch: restructuring tables,
  moving rows between blocks to match the computed cluster assignment, regenerating the bib. Pool metadata is filled by
  `tools/pool.py`, not by an agent.

**`surveys/` → `outputs/` runs in the main session.** Reading a finished survey and writing the analysis is not
delegated. The main session also owns cluster review. When step 3 halts for review, or when the output is presented, it
shows the user the `Clusters` table and the viewer, and records their review in the log. A change the user asks for is
dispatched as an incremental pass (`docs/process.md`, "Changing the clusters after a pass").

## Rules for the main session

- Do not call outside services for a pass, but rather dispatch a subagent. A single call to check connectivity, or to
  verify one row as a subagent's report makes you doubt, is fine. Scripts in tools/ are exempt: their results go to
  files, not into your context.
- Run a pass down the order of operations in `docs/process.md`: it is the checklist. Confirm each row's `done when`
  before starting the next. At each gate row, run `python3 tools/check.py <topic> --gate G<n>`, and do not start the
  next step until it passes (`docs/gates.md`). To resume a pass in a new session, start from
  `python3 tools/check.py <topic> --status`.
- Run the scripts of the order of operations yourself, between dispatches, and hand the next subagent the printout it
  needs. A subagent runs only the scripts its own job needs, such as `tools/fulltext.py` during verification. A script
  that fails after its own retries halts the pass (`H3`).
- Write the log lines that scripts print, and those about your own decisions: `Dimensions`, `Pool`, `Fringe`, `Coreset`,
  `Late papers`, `Gates`, `Waivers`, `Tokens`, `Halts` and `Ended`; and Open work's
  `Clusters not yet reviewed by the user`. Agents write the lines about their own work. `Clustering` is printed by
  `tools/cluster.py` but written by the naming agent, which replaces the computed cluster ids with names. A pass's log
  entry is written as the pass goes; a line may be updated until the pass ends, never after.
- Subagents may run in parallel **only on disjoint sections of the survey**. Cluster blocks partition the Coreset table
  naturally, so parallel verification or selection work splits by cluster. The pool is a single table, so only one agent
  writes to it at a time. Group the clusters into a few blocks per agent, spreading the `high` ones, which cost the
  most. The log and Open work are shared too: agents running in parallel do not write them, but end their reports with
  the lines meant for them, under `Log:` and `Open work:`, and you write those once all have returned.
- Some work spans clusters and cannot be split: fringe selection, which is judged against the whole coreset; bridges,
  which join two clusters; and the coverage test, which reads the whole output. Run each once, by one agent, after the
  per-cluster work is done.
- Instruct subagents to write each row as they finish it, not to batch all writes to the end. Subagents die — on spend
  limits, on timeouts — and partial work on disk beats complete work lost.
- Run `python3 tools/check.py <topic>` after each subagent returns, while you still know which agent caused any damage.
  After an agent that changed the coreset, run `python3 tools/bib.py <topic>` first, since the check compares the two. A
  failure the agent cannot fix halts the pass (`H9`).
- A subagent's report that starts with `STOP:` is a halt (`docs/process.md`, "When a pass ends"). Tell the user what
  halted and why, wait for their decision, and record it in the log's `Halts` line.
- Do not take a subagent's report at face value where it matters. Reports have overstated what a paper showed. Check the
  row against the report, and verify the claims an output will rest on.

## Briefs

A brief is what you hand a `survey-pass` agent for one job, and what it hands back. Each dispatch prompt gives:

```text
Topic: <topic>. Job: <brief name> (docs/dispatch.md, "Briefs"), step <n> of the pass of YYYY-MM-DD.
Scope: <the clusters, rows or candidates this agent owns>.
Handed over: <the printouts listed below, verbatim>.
```

The agent reads the spec files the index in `CLAUDE.md` names for its job, so a brief does not restate the method. Hand
over printouts and file paths, never the contents of a file in `graphs/<topic>/` (`docs/formats.md`, its last section).
Every report follows `.claude/agents/survey-pass.md`: what was done, what was added or changed, the judgement calls, and
`STOP: <id> — <the reason>` as its first line if the job halted.

- **Preflight** (step 0). Hand over: the printout of `tools/preflight.py`. The agent makes one cheap call each to
  `snippet_search`, `search_papers_by_relevance`, `get_paper`, `get_citations` and WebSearch
  (`docs/external_services.md`, "Preflight"), and writes the `Preflight` line, both halves. Returns: ok, or `STOP: H1`.
- **Orient** (step 1). Hand over: the recency window, which is the time since the last pass, or six months on a first
  pass; on a later pass, the previous `Orientation` line. The agent runs WebSearch, resolves each candidate to its ID,
  adds the in-scope ones with `tools/assign.py add`, and records the rest with `tools/assign.py reject`. Writes: Pool
  rows; rejections; `Orientation`, with the frontier candidates; `Recency window`. Returns: the themes the field names,
  as a short list of phrases, for the next brief.
- **Expand** (step 2, and every targeted expansion). Hand over: the themes from the orient report; on a targeted
  expansion, the region instead, and why: a thin cluster, `no stable level`, a missing expected cluster, or a new
  cluster the coverage test proposed. The agent traverses and searches through Asta, screens for scope, adds with
  `tools/assign.py add`, and records every rejection with `tools/assign.py reject`. Writes: Pool rows; rejections;
  `Expansion`, naming each frontier candidate it traversed; `Errored queries`; Open work: papers that could not enter
  the pool. Returns: what was traversed and searched, and `assign.py`'s refusals. One agent at a time, since it writes
  the pool.
- **Fringe screening** (step 2). Hand over: the path `graphs/<topic>/fringe-screen.md`. The agent judges each row in or
  out of scope from its title and abstract, as in expansion, without looking up its route or citations, which would
  unblind it. Writes: the `in scope` and `reason` cells, row by row. Returns: the rows it was unsure about.
- **Naming** (step 3). Hand over: the printout of `tools/cluster.py`, which has the diagnostics, the notes and the
  `Clustering` line; on a later pass, the printout of `tools/assign.py remap`. The agent reads `naming-sheet.md` and the
  input, and names, defines and rates every computed cluster that has no name. Writes: Clusters rows, with `computed`
  ids; `Clustering`, with the Clusters table's ids; `Clustering rationale`; `Clusters`. Returns: the ratings it was
  unsure about. Halts: `H6`, `H7`.
- **Selection** (step 4), one agent per block of clusters, in parallel. Hand over: the block's cluster ids and their
  alignment, and the lines of the `tools/check.py` printout for those clusters (pool size, roles filled, in-degree
  leaders). The agent fills anchor, frontier and dissent per "Sizing" (`docs/process.md`, step 4), and the extra
  frontier or bridge for a `high` cluster that `naming-sheet.md` marks internally divided. A dissent row's
  `selected because` quotes the claim that contradicts the cluster. It drafts every cell from the abstract, dimensions
  included, with `source` `abstract`; verification re-derives them from the body text. On a later pass, it keeps every
  verified row that still fills a role, and demotes the rest. Writes: Coreset rows, in its blocks only. Returns, under
  `Log:`, its parts of `Dissent searches` and `Demotions`, and under `Open work:`, its empty roles.
- **Bridges** (step 4), once, after selection, and only if `tools/check.py` notes a pair of clusters that trade papers
  without a bridge. Hand over: those pairs. Writes: `bridge:` rows. Returns: pairs left without a bridge, and why.
- **Fringe selection** (step 4), once, last. Hand over: the path of `fringe-sheet.md`, rewritten after selection. The
  agent reads the abstracts through Asta (`get_paper_batch`) and the coreset rows, and keeps five to ten papers that
  each carry an idea no other row has. Writes: `fringe` rows, in the block of each paper's computed cluster. Returns:
  the near misses.
- **Verification** (step 5), one agent per block of clusters, in parallel. Hand over: the block's cluster ids, and which
  rows: all, or only those still `abstract`. The agent follows `docs/verification.md`, fetching full text with
  `tools/fulltext.py`. Writes: the rows' cells and `source`, and each row's evidence file. Returns, under `Log:`, its
  `Corrections to existing rows`, and under `Open work:`, its rows needing verification.
- **Coverage test** (step 7), once per round. Hand over: the round's number; the per-cluster lines of the
  `tools/check.py` printout; the recency window for the fresh query. The agent draws the sample (`docs/process.md`, step
  7), using `fringe-sheet.md` for the fringe scores, judges each candidate against the output, and adds every candidate
  that changed a target with `tools/assign.py add`. Writes: Pool rows; `Coverage test`. Returns: each proposed new
  cluster, with its region, for a targeted expansion.
- **Probe** (on request). Hand over: the question, and the coreset rows closest to it. The agent follows
  `docs/verification.md` ("Probes") and adds each paper it finds with `tools/assign.py add`; they are late papers.
  Writes: `Probes`. Returns: found, with IDs, or survived a refutation attempt.

A `survey-edit` job gets the exact change to make, and the `tools/check.py` failure it is to fix, if any.

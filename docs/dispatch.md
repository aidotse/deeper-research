# Dispatch: the execution model and main-session rules

## Execution model

The two pipeline stages run in different contexts.

**`inputs/` → `surveys/` runs in subagents.** The main session reads the input, plans, and dispatches. Retrieval results
stay in the subagents' contexts and never enter the main session.

- `survey-pass` runs on a capable model and does work whose mistakes leave no trace: orientation, expansion and
  screening, naming the computed clusters, selecting roles, dissent searches, verification, the coverage-test
  judgements, and probes.
- `survey-edit` runs on a cheaper model and does mechanical work that `tools/check.py` can catch: restructuring tables,
  moving rows between blocks, regenerating the bib. Pool metadata is filled by `tools/pool.py`, not by an agent.

**`surveys/` → `outputs/` runs in the main session.** Reading a finished survey and writing the analysis is not
delegated. The main session also owns cluster review. When step 3 stops for review, or when the output is presented, it
shows the user the `Clusters` table and the viewer, and records their review in the log. A change the user asks for is
dispatched as an incremental pass (`docs/process.md`, "Changing the clusters after a pass").

## Rules for the main session

- Do not call outside services for a pass, but rather dispatch a subagent. A single call to check connectivity, or to
  verify one row as a subagent's report makes you doubt, is fine. Scripts in tools/ are exempt: their results go to
  files, not into your context.
- Subagents may run in parallel **only on disjoint sections of the survey**. Cluster blocks partition the Coreset table
  naturally, so parallel verification or selection work splits by cluster. The pool is a single table, so only one agent
  writes to it at a time.
- Instruct subagents to write each row as they finish it, not to batch all writes to the end. Subagents die — on spend
  limits, on timeouts — and partial work on disk beats complete work lost.
- Run `python3 tools/check.py <topic>` after each subagent returns, while you still know which agent caused any damage.
- Do not take a subagent's report at face value where it matters. Reports have overstated what a paper showed. Check the
  row against the report, and verify the claims an output will rest on.

# Audits: reviewing the spec and the runs

This file is the procedure for auditing this repo, and for remediating what an audit finds. It is for the main session,
and only when the user asks for an audit or for its remediation. A pass never reads it.

There are two kinds of audits:

- A `spec audit` reads the repo: the docs, the code, the tests and the agent definitions. It asks whether they are
  correct, complete (no gaps), efficient, internally consistent, and whether an agent can follow them.
- A `simulation audit` is the practical counterpart: it runs the pipeline and assess what the actually happens in the
  run. It asks whether agents following the spec actually produce what the spec says.

The typical workflow will be to first do a spec audit, followed by the more expensive simulation audit. The goal of both
counterparts is correctness, from a "static" (spec) and "dynamic" (simulation) aspect. Other than correctness, an
overarching principle here is to work against overengineerng, preferring simpler solutions that still solve the
underlying problem: it's preferable to sacrifice a small portion of functionality, if that allows us the verify
correctness and completeness of the remaining mechanism. These tradeoffs should always be made together with the user,
never on your own.

The two are kept apart on purpose. A spec audit finds a rule that contradicts another, or a case no rule covers. It
cannot find a rule that reads well but that agents misapply in practice. A simulation finds that kind, but only on the
branches the run happens to take.

## Spec audits

### The three documents

Every audit produces three documents, in one directory named by the date the audit began: `.audits/<YYYY-MM-DD>-spec/`.
The documents in an audit correspond to a specific order: identification of issues -> remediation plan -> disposition,
and the goal is to be able to reset the session between these three parts if necessary. More specifically, these parts
are the following:

1. `The audit` lists issues, and only issues. It is named for its scope, i.e. in this case `spec.md`. Each issue gets an
   ID, its evidence, why it matters. This document does not plan, and it does not decide.
2. `remediation-plan.md` builds, for each ID'd issues in the audit, a recommended remediation and organizes these into
   an overall plan. It opens with the user's answers to any questions the reviewing agent might ask regarding e.g.
   preferences in how to solve certain issues. Then come the planned remediations, in phases. The plan should group the
   remediations by logical phases, and the goal is to design these phases such that the session can be safely reset in
   between.
3. `disposition.md` records what was actually done, per phase and ID, following the ordering of the remediation plan:
   the outcome, the commit, any departure from the plan and why, how it was verified, and what to watch in the next run.

The links run one way. The audit defines its IDs. The remediation plan refers to them, and defines only the items raised
after the audit (`R`), i.e. any issues found while thinking through the remediation plan. The disposition is a
comprehensive final accounting of all of these issues. So every ID is defined in exactly one place, and a reader can
always find what it means.

Every document opens with a short section, "How to read this document". It says what the document is for, how its
organized, what each section holds, and where the other two documents are.

Each document is written at a different time:

- The audit is written once, by a blind session (see below), and is not edited afterwards, except to correct an error of
  fact.
- The plan is written with the user before any fix.
- The disposition is updated as each item or phase lands.

For both the remediation plan and the disposition, a placeholder draft with at least the section headings and correct
scaffolding is written at the time when the audit is first requested. That way it is always clear to the user in which
stage the current audit is at all times.

### Blindness and scope

The auditor is blind to earlier audits. It does not read `.audits/`, `docs/roadmap.md`, or any git history (log, diff,
blame, show). The point is a fresh reading. An auditor who has read the last audit checks whether its findings were
fixed, and misses what nobody has looked at yet. The roadmap would bias it the same way, by telling it what is already
known.

The scope is everything else in the repo: `CLAUDE.md`, `.claude/`, `docs/`, `tools/`, `tests/`, `inputs/`, `surveys/`,
`outputs/` and `bib/`. `graphs/` and every other intermediate output is out of scope: these runs belong to the
simulation audit.

The auditor may run the tools and the tests on scratch topics named `scratch-audit-*`, and removes them afterwards.
These differ from simulation audits in scope - only run tools and tests on scratch topics if its cheap, and the scope is
very limited. It calls an outside service only to test a claim the spec makes about that service, and records each call.

The work can be split across parallel agents, where results don't depend on each other, each under the same blindness
rules, only where the user approves, so ask them first if this your plan. For example, the main session reads every spec
file, while agents take the gates, the clustering stack, the pipeline scripts, etc.

### The audit document

Its sections, in order:

1. `How to read this document`.

2. `Scope and method`. What was read and what was not; how the work was split; which scratch topics and outside calls
   were used. Then the status values each issue carries:

   - `verified against code`, with file and line;
   - `verified against data`, measured on a committed file such as a survey;
   - `verified by simulation`, reproduced on a scratch topic, or by a computation stated with it;
   - `verified against docs`, a contradiction or gap visible in the docs themselves;
   - `likely`, reasoned from the code or docs but not reproduced.

   Line numbers refer to the files as they stood on the audit's date.

3. `Executive summary, in the manner of a reviewer`. Written as a reviewer writes about a paper, for a reader who has
   not seen the repo. Its parts: what the current repo state proposes; the claimed contributions, numbered; the
   value-add over a commercial deep-research product; strengths; weaknesses; and a verdict.

4. `Part (a): is the current development direction right?`, in three parts, all prose summaries: `What is load-bearing`,
   `Where the effort may be misallocated` (may be "None"), and `Simpler or partial solutions that exist` (may be
   "None").

5. `Part (b): issues by dimension`. One subsection per dimension, in this order. Each is kept even when empty, with
   "none found".

   - `C` — the docs and the code disagree.
   - `M` — method bugs: the method, as specified or as coded, gives a wrong result.
   - `S` — spec inconsistencies and gaps: two docs contradict each other, or a case is left unspecified.
   - `W` — how the docs are wired: the index, the reading lists and the cross-references. The failure is an agent that
     follows them and never reads what it needs.
   - `A` — whether the docs work as instructions for agents: where a rule-following agent would stall, guess, or decide
     differently from another. This includes judgement calls with no rubric.
   - `T` — tool work the spec needs but lacks.
   - `Z` — overengineered framings or solutions, ranked by the scope of the simplification, from the whole spec down to
     a single rule.

   Issues that bear on verification are marked `(V)`.

6. `The verification concept`. An analysis of the current verification mechanisms built into the methodology, e.g.
   quality gates (if any). The chain from a claim on a paper to how (if so) it is presented to the user, link by link,
   with the state of each link and the `(V)` issues that bear on it. Why a section of its own: verification is the
   product's quality claim, and its issues are otherwise scattered across the dimensions.

7. `Part (c): readiness for the next run`, in three parts: `Blocking: fix before the run`, `Strongly advised`. These
   become inputs for the next simulation audit.

8. `Checked and found to hold`. What was checked and found sound. It shows what the audit covered, so that a clean area
   is not mistaken for an unread one.

9. Appendices, as needed, for tables too long for the body.

Issues are numbered within their dimension (`C1`, `C2`, …), and each takes the same form: a bold heading with the ID,
the `(V)` mark if it applies, and a one-sentence statement of the issue. Then:

- `Evidence`: file and line, or the simulation that reproduced it;
- `Why it matters`: what goes wrong, and for whom;

### The remediation plan

The remediation plan takes a comprehensive look at all of the issues identified in the audit, and for each provides:

- `Remediation`: the suggested fix, with alternatives if there are several;
- `Effort` (S, M or L) and `Status` (one of the values above).

The task is *not* to fix issues, its to come up with a plan for doing so, by clustering these together into phases based
on effort and internal dependencies. For example, in case there are questions that arise from the reading of the audit
itself (e.g. different solution alternatives, potentials for simplification, etc.), always do this with the user first
(see sections below), as this may make certain remediations moot.

Its sections, in order:

1. `How to read this document`.

2. `Principles`: the rules that set the order of the work. Examples: decide before fixing, since a simplification may
   delete code that has open findings; code before docs; one change per file group; every fix carries its test.

3. `Decisions taken`, dated and attributed: the user's answers to any questions the audit raises, or that you raise
   based on a reading of the audit (when something is unclear, when there are multiple possible solutions to a problem,
   when a simplification potential is identified, etc.). One bullet per ID, saying adopted, rejected or decided, and
   what was decided. A rejected suggestion is recorded here with its reason, so that the disposition need not argue it
   again.

4. `Issues found during remediation`: issues the audit did not list, found while fixing or testing. One subsection per
   event or context that found them. Each subsection opens with how the event was run: by whom, blind to what, at what
   cost, and with how many findings. Each issue gets a `P` ID, numbered across the whole audit, a tag, the problem, and
   the suggested fix. The tags:

   - `blocker` — the agent cannot proceed, or certainly fails a gate;
   - `guess` — the agent must improvise, so two agents would differ;
   - `minor` — wording or findability.
   - `other` — you specify something else

5. The phases, in order. Each says which IDs it handles, why in that order, and what / when it should be done, for
   example: a routine fix, a test plus a fix, as part of a larger fix suite with other dependencies, in a simulation,
   etc.

6. `After the run`: what is deferred deliberately, and why.

### The disposition

Its sections, in order:

1. `How to read this document`, including the form of an outcome entry and the tags used.

2. `By phase` and `Commits`: summary tables from each phase to its commits and the IDs it handled.

3. The outcomes, one subsection per phase of the plan, in the plan's order. Each entry starts with the ID, its outcome
   and its commit. The outcome is one of `fixed`, `adopted`, `moot`, `partial`, `deferred` or `pending`. Then the entry
   says what was done, where it departs from the suggested remediation and why, how it was verified, and what to watch.

4. `Not mapped to a phase`: outcomes for IDs that no phase handled. Examples: items raised after the plan was set, and
   items parked by a decision. The outcomes are coded into one of the same categories as above.

5. `Pending`: the IDs not yet handled or left unfixed on purpose, organized by phase (where applicable), with a trailing
   subsection `Watch in the next run`: judgement calls whose effect only real data will show. The next simulation audit
   reads this section first.

## Simulation audits

A simulation audit runs the pipeline for real, on topics chosen for the purpose, and audits the result. That covers the
runs' own reports, and everything they write: `graphs/<topic>/`, the survey, the output and the bib. It asks two
questions:

- Can a blind agent follow the spec? Where do potential inconsistencies come from, where does it stall, guess, or
  improvise?
- Is what it produces right: does what is on disk satisfy the spec, and do the judgements hold up when checked?

A simulation audit starts from the latest spec audit: `Part (c): readiness for the next run` in the audit itself,
`Watch in the next run` / `Pending` in the disposition, and the remediation plan's proposed fixes for the
simulation-relevant issues.

### Segments

A whole pass run at once accumulates errors. A wrong screening verdict shapes the clusters, the clusters shape
selection, and so on. By the end of the pass, a failure's cause may be several steps back. Fixing everything one run
found, then running again, also tends not to converge.

So a simulation audit runs the pass one segment at a time, and iterates each segment until it converges before moving
on. The end of a segment is its checkpoint (see "Starting states / checkpoints"), and a checkpoint has to do four
things:

- `Complete state`: the files on disk fully determine what the next segment starts from.
- `Judgeable state`: the auditor can tell from the segment's outputs alone whether the segment went right.
- `Frozen randomness`: anything that varies between runs, mainly retrieval, is fixed before the next segment starts.
- `Proportionate cost`: iterating the segment is cheap compared with the whole pass.

| segment | steps | ends at |
| -- | -- | -- |
| `plan` | 0: plan and preflight | `--gate G0` |
| `pool` | 1–2: orientation, expansion and screening, the pool, the fringe candidates | `--gate G1` |
| `clusters` | 3: clustering, targeted expansion, naming | `--gate G2` |
| `coreset` | 4: selection, bridges, fringe selection | `--gate G3` |
| `verification` | 5: the full texts, verification, replacing uncheckable rows | `--gate G4` |
| `output` | 6: the output | the plain `tools/check.py <topic>`, after the "Write the output" row |
| `coverage` | 7: the coverage rounds, Revise, the judgement audits | `--gate G5` |

A segment ends at a gate by default. A gate passes only when every record its steps should leave exists
(`docs/gates.md`), and that is what makes the files a complete state to restore. It is also where the runner stops
anyway, since a pass does not start the next step before the gate passes. Segments are named for what they build, not
for their gate. Why: a remediation may move or merge a gate, and the segments should not change with it.

The catch is that the gates were placed for a real pass: where an error becomes expensive to undo, or where the next
step is costly. That serves the first property, but not always the other three. Three segments depart from the default:

- `output` and `coverage` split what would be one segment ending at `G5`. Step 7 is not downstream of the steps before
  it. Revise reruns selection, the fetch, verification and the output, without their gate rows, and a proposed cluster
  or `RECLUSTER:` returns the pass to step 3 (`docs/process.md`, "Returning to step 3"). One segment would also bundle
  three kinds of judgement: the output's sentences, the coverage verdicts and the judgement audits. So the output gets a
  segment of its own, which ends when the plain check passes. The main path of `coverage` is a round that converges,
  with its Revise when it counted one paper. A round that does not converge, and a return to step 3, are steered
  branches ("Steered branches"). A fault found in work that step 7 reruns, such as a Revise row verified wrongly, is a
  fault of the brief that did the work. Its fix reopens that brief's segment, as any fix to an earlier segment does.
- `verification` iterates on a subset. It is more than half the cost of a pass, at about 26k tokens per row
  (`docs/process.md`, "Order of operations"), and each row is verified on its own. So when the segment opens, the
  auditor draws a random subset of about 5–8 rows, covering every role present if it can, and records it in the
  segment's file. Each iteration verifies only those rows: the runner is told which rows, as steering, runs step 5's
  rows for them alone, and does not run the gate. Once the subset has converged, the whole segment runs once from the
  same checkpoint, up to `--gate G4`, as its confirmation. A `blocker`, `guess` or `silent` finding in that run adds the
  rows that showed it to the subset, and the segment iterates again. A confirmation run (see "Topics") runs the segment
  whole, like every other.
- `pool` cannot freeze its own randomness. Each iteration retrieves again, and WebSearch's results drift between calls.
  Whether Asta's are stable is `UNVERIFIED`. So a difference between two iterations of `pool` may come from the fix,
  from the agents' variability, or from new retrieval results. Its convergence is judged from the runner's report and
  the screening spot checks, never by comparing the pools of two iterations.

Segments also spread the cost. Each iteration pays only for its own segment, and a spend limit or a dead session loses
at most one segment's work. We should be able to take on separate segments in different fresh sessions (sequentially).

### The documents

A simulation audit lives in `.audits/<YYYY-MM-DD>-sim/`, with one directory per topic. It does not use a spec audit's
three documents. A spec audit has three moments far apart: blind findings, the suggested fix plan, and the outcome after
fixing, each with its own document. In a simulation, the same three steps recur in every iteration, minutes apart, in
the same session. Split across three files, each iteration would touch all three, and the plan would only repeat the
fixes. So a simulation audit is organised by segment, and the iteration is the unit of record.

Per topic, in `.audits/<YYYY-MM-DD>-sim/<topic>/`:

- `simulation.md`, the summary and index. A fresh session reads it first. It holds, in order:

  - `How to read this document`, including any open risk;
  - the user's decisions: the topic and what it is for (narrow, confirmation or wide; see "Topics"), and any limits
    other than the defaults ("Limits"). A decision that applies to every topic is taken in the first topic's file, and
    the later ones link to it;
  - a status table, per segment: open, converged or not started; the iterations so far; each iteration's `E` IDs and
    their count by tag; the size of the specs / docs its fixes touched, before and after; and the checkpoint's tag;
  - `Found ahead of their segment`: see below;
  - the measurements, each with what it implies for the spec's estimates;
  - Any pending, sidelined, or postponed items, and things to watch in the next run.

- `segments/<segment>.md`, one per segment, such as `segments/clusters.md`, created when the segment opens. Each
  iteration appends one section, `## Iteration <k>`, with four parts in this order:

  1. `Run`: who ran it, from which checkpoint, at what cost, with a link to the raw report, and any steering.
  2. `Findings`: each with its `E` ID, its tag, the problem, and where it showed. They are written in full before any
     fix, and not edited afterwards. Why: this keeps the honesty a separate audit document gives a spec audit, since a
     finding cannot be reworded to fit its fix.
  3. `Fixes`: per `E` ID, what changed, the commit, and any user decision with its date; or why the finding was not
     fixed.
  4. `Result`: converged, or another iteration, and why.

- `segments/runs/`: the runners' raw reports, as `<segment>-<iteration>.md`, and the checkpoints' copies of ignored
  files (see "Starting states").

`E` IDs are numbered across the whole simulation audit, spanning across topics and segments, so that each ID is unique
in the respective simulation directory. Each is defined in the segment file of the iteration that found it. The status
table lists it, so that any ID can be found from `simulation.md`.

The files grow one segment at a time. A segment's file is created only once the segment before it has converged, and no
issue of a later segment is worked before then. An issue that shows up ahead of its segment, such as a `clusters` runner
noticing a gap in the Verification brief, gets its `E` ID under `Found ahead of their segment` in `simulation.md`. It
moves into its segment's first iteration when that segment opens. Why: a fix made for a later segment, before the
earlier ones are stable, is a fix on ground that may still move.

A confirmation run (see "Topics") uses the same layout, with exactly one iteration per segment. The runner goes through
the whole pass with no restored checkpoints and no fixes between segments. It may pause at the end of each segment for
the review, as long as nothing changes before it goes on. The auditor tags each segment's end as a checkpoint, as usual,
so that a finding can be traced later. If every segment is clean, `simulation.md` says so: the pass ran end to end, with
no retries. A `blocker` sends the auditor back to the segment concerned, in the iterated topic. Other findings are
recorded in their segment's file, and fixed after the run.

If a segment shows that a whole area of the spec is wrong, rather than a few rules, the auditor stops and proposes to
the user a spec audit of that area, with its three documents.

### Roles

- `The auditor` is the main session of the audit's own session. It is not blind: it knows the spec, and has read the
  last disposition. It prepares each segment's starting state, launches the runner, reviews what the runner did and
  produced, writes the findings and makes the fixes. It decides when a segment has converged.
- `The runner` plays the pass's main session for one segment, from the docs alone, and dispatches `survey-pass` agents
  as the docs say. Retrieval, scripts and agents are all real. It is blind to `.audits/`, `docs/roadmap.md`,
  `docs/audits.md`, `tests/`, and git history. It is never told what the last iteration found. Why: a runner that knows
  where the last one stumbled steps around the spot, and the fix goes untested.
- `The user's part`: halts, waivers and the cluster review are the user's to decide in a pass. In a simulation the
  auditor decides them, and records each decision as steering, so that it is not mistaken for the spec working. A
  decision that would change the audit's plan goes to the real user.

How the runner is launched. The runner is a separate, headless Claude Code session (`claude -p`), which the auditor
launches with `.audits/runner.sh`. It works in a scratch copy of the repo, `/tmp/deeper-research-sim`. The copy leaves
out `.audits/`, `docs/roadmap.md`, `docs/audits.md` and `tests/`, and has a one-commit git history of its own, so the
repo's history is not there to read. The runner dispatches real `survey-pass` agents, as a main session does, so the
hand-over between the main session and its agents is tested too (smoke test, 2026-10-12). The real repo sits on the same
disk, so blindness to it holds by instruction only. The runner reports any breach, and `runner.sh collect` lists every
file it wrote outside its topic.

Each iteration runs `runner.sh build` after restoring the checkpoint, then `runner.sh run <prompt> <out.json>`, then
`runner.sh collect <topic>`, which copies the topic's files back into the repo. The prompt is built from
`.audits/runner-prompt.md`. It names the rows to run and where to stop, gives the steering, and asks for the report
below. It says nothing else about the audit. A halt ends the run with its decision pending. The auditor's decision goes
in as steering, by `runner.sh run` with the session's id, which resumes the session.

Two setup steps are the user's to make or approve, once per machine. Why the user's: they widen what an agent may do, so
an agent does not take them on its own. The scratch directory is marked as a trusted workspace (`hasTrustDialogAccepted`
in `~/.claude.json`), so that the project's settings and hooks apply in the copy. And an allow rule for
`.audits/runner.sh run` goes in `.claude/settings.local.json`, since a session that launches another needs explicit
permission.

The runner's report lists every place it stalled, guessed, improvised or met a tool failure. Each comes with the
checklist row, the tag it would give, and what it did instead. The report also gives the halts and how they were
decided, the tokens per dispatch, and anything it read beyond its segment's rows. The raw reports are kept in the
topic's `segments/runs/`, as `<segment>-<iteration>.md` ("The documents").

### Starting states / checkpoints

Each segment starts from the converged end of the one before, its checkpoint. A checkpoint is a commit, not a copy. When
a segment converges, the auditor commits the topic's files in their usual places (the input, the survey, the output, the
bib, and `graphs/<topic>/`) and tags the commit `sim-checkpoint-<topic>-<segment>`. Git then stores each version once,
and a fresh session can restore any checkpoint. Only the files the repo ignores, such as the full texts, the sheets and
the viewer, are copied, to the topic's `segments/runs/checkpoints/<segment>/`, which is ignored too. On a fresh clone,
where that copy is missing, they are regenerated by `tools/fulltext.py`, `tools/sheets.py` and `tools/graph.py`.

To restore a checkpoint, the auditor deletes the topic's files, checks them out from the tag, and copies the ignored
files back. Deleting first matters: a checkout from a tag does not remove the files a failed iteration added, such as
its evidence files.

Every iteration of a segment starts by restoring the checkpoint before it. So from `clusters` on, every iteration meets
the same papers and the same clusters. A difference between iterations then comes from the fix, or from the agents' own
variability, and not from new retrieval results. `pool` is the exception, since it does the retrieval itself
("Segments").

A fix to a row of an earlier segment reopens that segment, unless the auditor can show the change cannot alter what the
segment writes. A reopened segment runs again from its own checkpoint. The segments after it then run once each, to
confirm, rather than being iterated again, unless that run finds something.

### Iterating a segment

1. Restore the checkpoint.
2. The runner runs the segment, up to its end ("Segments").
3. The auditor reviews three things: the runner's report; the result of the check that ends the segment, and the plain
   check; and the segment's outputs against the spec, judgement by judgement, with the additional spot checks below.
4. Every issue becomes an `E` finding, in the segment's file, under the iteration that found it.
5. The auditor fixes, after any decision the user must take. The gate test suites pass after every fix.
6. The segment runs again, from the same checkpoint.

Issues are tagged with the following:

- `blocker` — the runner cannot proceed, or certainly fails the check that ends its segment;
- `guess` — the runner must improvise, so two runners would differ;
- `silent` — the output breaks the spec, or a judgement is wrong, and the runner did not notice. This is the worst kind,
  because nothing in a real pass would flag it. See section below for assessing `silent` findings.
- `minor` — wording or findability.

A segment converges when one run after the last fix has no `blocker`, `guess` or `silent` finding. A `minor` finding is
fixed without another run. The catch: one clean run is weak evidence, because agents vary from run to run. The
confirmation runs below are the second test.

Fixes simplify where they can. Each added rule can collide with the rules already there, which is how fix rounds fail to
converge. So:

- Prefer a fix that deletes or shortens a rule to one that adds a rule, if no features are sacrificed.
- Record, per iteration, the size of the docs the fixes touched, before and after.
- If a segment's second run finds new `blocker`, `guess` or `silent` issues caused by the first round's fixes, stop
  patching. The next fix is a reassessment with potential simplification of that segment's rows, proposed to the user
  before it is made.

### Spot checks per segment

A runner cannot report what it does not notice. These checks look for `silent` findings. They are judgements, made by
the auditor reading the segment's outputs: no script can tell whether a screening verdict is right, or whether a cell
says what the paper says. The gates are the scripted checks, and they only check that each judgement left a record.

Each check below names a kind of judgement the segment made. An instance is one judgement of that kind: one screening
verdict on one candidate, one cluster's name, one row's role, one cell of a verified row, one sentence of the output.
The auditor checks every instance where they are few, and a random sample where they are many. Random, because an
auditor who picks the cases drifts towards the suspicious or the easy ones; a random sample also makes the share found
wrong an estimate of the error rate. Each check records how many instances there were, how many it checked, and how many
it found wrong. We also check randomly because checking all instances in cases where there are many could potentially be
more costly than the audit itself.

- `plan`, all: the plan's dimensions, against the input.
- `pool`, about ten verdicts each way, in scope and out: screening verdicts, against the input's topic and exclusions;
  and the recency window, against the input.
- `clusters`, all clusters: each cluster's name and definition, against the papers in its section of the naming sheet.
- `coreset`, all rows: each role against its definition, and each `dissent` quote against the paper's abstract.
- `verification`, every row of the subset, and on the segment's confirmation about five rows from outside it: verified
  cells against the full text. This is where a reference reading belongs. The auditor reads the rows' full texts in
  full, and records its own findings before opening the rows' evidence files. Then it scores each row by the share of
  those findings it states.
- `output`, about ten sentences of the output, drawn at random, against the rows they cite. These are drawn before the
  pass's own faithfulness sample exists, so they cover sentences that sample may miss.
- `coverage`, in three parts:
  - all coverage verdicts, about ten per round, against the candidates' abstracts;
  - the pass's own faithfulness sample of 15 output sentences (`docs/process.md`, "Auditing the judgements"), each of
    its verdicts checked again;
  - every sentence Revise changed, against its rows. Revise rewrites the output after the `output` segment's check, so
    nothing else looks at these sentences, unless the pass's sample happens to draw them.

### Steered branches

Some branches a run rarely takes: a halt, a coverage round that does not converge and its Revise, a return to step 3, an
uncheckable row, a trading pair that needs a bridge. Once a segment's main path has converged, the auditor may force
such a branch by editing the checkpoint, for example by planting a coverage verdict. Each steered branch is run and
iterated like a segment, and recorded as steered.

### Topics

The user writes an input for each topic. Three kinds serve different ends:

- `A narrow topic`, for iterating: a pool of about 50–150 papers and a coreset of about 15–25 rows, so that each
  iteration is cheap.
- `A confirmation run`, once every segment has converged: a whole pass from step 0, by a blind runner, with no steering
  and no restored checkpoints. On a topic with a reference point, such as an earlier survey, it also measures which of
  that survey's claims the coreset reproduces. It is recorded as one iteration per segment ("The documents").
- `A wide topic`, to find where the method bends with scale: the pool size at which screening cost, outside services or
  the tools stop being practical. It runs as a confirmation run.

### What to record

Per run: tokens per dispatch, wall-clock time, the outside calls made, and the pool and coreset sizes. Per segment: each
quantity the spec estimates, against what the run measured. Examples are verification tokens per row in `verification`,
and the judgement-audit rates and the coverage radius per round in `coverage`. Measurements go in `simulation.md`, each
with what it implies for the spec's estimates.

These are data for correcting the spec's estimates, never limits. A run is not stopped for what it costs. Tokens and
dollars both make poor limits: cache reads count a context again on every turn, models are priced differently, and usage
may be on a subscription.

### Limits

What a limit guards against is a runner that loops or hangs. So `runner.sh run` bounds each run by two measures of the
run itself, both set at about three times what a normal run should take:

- `Wall-clock time`, 3 hours by default, by `timeout`. This is the main limit, because it catches everything, including
  an agent that loops within one of the runner's turns, and a hung outside call.
- `The runner's turns`, 300 by default, by `claude -p --max-turns`. It counts the runner's own turns only, not its
  agents'.

A segment that needs other values sets them per run, and `simulation.md` records them. When a limit trips, the iteration
ends there. Nothing else is lost, since the segment restarts from its checkpoint. The trip is itself a finding: the
auditor reads the partial state and the session's transcript to find where the runner went round in circles.

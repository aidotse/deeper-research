# Audits: reviewing the spec and the runs

This file is the procedure for auditing this repo, and for remediating what an audit finds. It is for the main session,
and only when the user asks for an audit or for its remediation. A pass never reads it.

There are two kinds of audit:

- A `spec audit` reads the repo: the docs, the code, the tests and the agent definitions. It asks whether they are
  right, whether they agree, and whether an agent can follow them.
- A `simulation audit` runs the pipeline and reads what the run leaves behind. It asks whether agents following the spec
  actually produce what the spec says.

The two are kept apart on purpose. A spec audit finds a rule that contradicts another, or a case no rule covers. It
cannot find a rule that reads well but that agents misapply in practice. A simulation finds that kind, but only on the
branches the run happens to take.

## The three documents

Every audit produces three documents, in one directory named by the date the audit began: `.audits/<YYYY-MM-DD>/` for a
spec audit, `.audits/<YYYY-MM-DD>-simulation/` for a simulation audit.

1. `The audit` lists issues, and only issues. It is named for its scope, such as `docs-full-spec.md` or `simulation.md`.
   Each issue gets an ID, its evidence, why it matters, and a suggested remediation. It does not plan, and it does not
   decide.
2. `remediation-plan.md` opens with the user's answers to the questions a reviewer would ask: which suggestions are
   adopted, which are rejected, and how the questions the audit left open are decided. Then come the planned
   remediations, in phases.
3. `disposition.md` records what was actually done, per ID: the outcome, the commit, any departure from the plan and
   why, how it was verified, and what to watch in the next run.

The links run one way. The audit defines its IDs. The plan refers to them, and defines only the items raised after the
audit (`R`). The disposition refers to both, and defines the issues found while remediating (`P`). So every ID is
defined in exactly one place, and a reader can always find what it means.

Every document opens with a short section, "How to read this document". It says what the document is for, what each
section holds, and where the other two documents are. Why this matters: the next session arrives cold, often with only
the disposition as its input, and must be able to find any ID from there.

Each document is written at a different time:

- The audit is written once, by a blind session, and is not edited afterwards, except to correct an error of fact.
- The plan is written with the user before any fix. As each phase lands, it gets one status line; the detail goes into
  the disposition.
- The disposition is updated as each phase lands, in the same commit as the phase.

A directory is kept while its audit is open. Once a newer audit supersedes it, the user deletes it; git history keeps
it.

## Spec audits

### Blindness and scope

The auditor is blind to earlier audits. It does not read `.audits/`, `docs/roadmap.md`, or any git history (log, diff,
blame, show). The point is a fresh reading. An auditor who has read the last audit checks whether its findings were
fixed, and misses what nobody has looked at yet. The roadmap would bias it the same way, by telling it what is already
known.

The scope is everything else in the repo: `CLAUDE.md`, `.claude/`, `docs/`, `tools/`, `tests/`, `inputs/`, `surveys/`,
`outputs/` and `bib/`. `graphs/` is out of scope. The intermediate outputs of runs belong to the simulation audit.

The auditor may run the tools and the tests on scratch topics named `zz-audit-*`, and removes them afterwards. It calls
an outside service only to test a claim the spec makes about that service, and records each call.

The work can be split across parallel agents, each under the same blindness rules. For example, the main session reads
every spec file, while agents take the gates, the clustering stack, the pipeline scripts, and a tabletop of a first
pass. A tabletop is a pass played from the docs alone: the agent plays the main session and each brief, runs the offline
scripts, and imagines the retrieval.

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
   not seen the repo. Its parts: what the repo proposes; the claimed contributions, numbered; the value-add over a
   commercial deep-research product; strengths; weaknesses; and a verdict.

4. `Part (a): is the development direction right?`, in three parts: `What is load-bearing`,
   `Where the effort is misallocated`, and `Simpler or partial solutions that exist`.

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

6. `The verification concept, in one place`. The chain from paper to user, link by link, with the state of each link and
   the `(V)` issues that bear on it. Why a section of its own: verification is the product's quality claim, and its
   issues are otherwise scattered across the dimensions.

7. `Part (c): readiness for the next run`, in three parts: `Blocking: fix before the run`, `Strongly advised`, and
   `How to run it`. The last is the starting point for the next simulation audit.

8. `Checked and found to hold`. What was checked and found sound. It shows what the audit covered, so that a clean area
   is not mistaken for an unread one.

9. Appendices, as needed, for tables too long for the body.

Issues are numbered within their dimension (`C1`, `C2`, …), and each takes the same form: a bold heading with the ID,
the `(V)` mark if it applies, and a one-sentence statement of the issue. Then:

- `Evidence`: file and line, or the simulation that reproduced it;
- `Why it matters`: what goes wrong, and for whom;
- `Remediation`: the suggested fix, with alternatives if there are several;
- `Effort` (S, M or L) and `Status` (one of the values above).

### The remediation plan

Its sections, in order:

1. `How to read this document`.
2. `Principles`: the rules that set the order of the work. Examples: decide before fixing, since a simplification may
   delete code that has open findings; code before docs; one change per file group; every fix carries its test.
3. `Decisions taken`, dated and attributed: the user's answers to the questions the audit raises. One bullet per ID,
   saying adopted, rejected or decided, and what was decided. A rejected suggestion is recorded here with its reason, so
   that the disposition need not argue it again.
4. `Items raised after the audit`, as `R` IDs, each with the context needed to act on it.
5. The phases, in order. Each says which IDs it handles, what is done, why in that order, and when it is done: a test, a
   suite, a tabletop, or a simulation. When a phase lands, it gets a status line pointing to the disposition.
6. `After the run`: what is deferred deliberately, and why.
7. `Index: where each ID goes`: a table from every ID to its phase, or to moot, deferred, or after the run. Every ID of
   the audit appears in it exactly once.

### The disposition

Its sections, in order:

1. `How to read this document`, including the form of an outcome entry and the tags used.

2. `Issues found during remediation`: issues the audit did not list, found while fixing or testing. One subsection per
   event that found them, such as a phase's tabletop. Each subsection opens with how the event was run: by whom, blind
   to what, at what cost, and with how many findings. Each issue gets a `P` ID, numbered across the whole audit, a tag,
   the problem, and the suggested fix. The tags:

   - `blocker` — the agent cannot proceed, or certainly fails a gate;
   - `guess` — the agent must improvise, so two agents would differ;
   - `minor` — wording or findability.

3. `By phase` and `Commits`: tables from each phase to its commits and the IDs it handled.

4. `Watch in the next run`: judgement calls whose effect only real data will show, and findings left unfixed on purpose.
   Each says what to look for and where it would show. The next simulation audit reads this section first.

5. The outcomes, one subsection per phase of the plan, in the plan's order. Each entry starts with the ID, its outcome
   and its commit. The outcome is one of `fixed`, `adopted`, `moot`, `partial`, `deferred` or `pending`. Then the entry
   says what was done, where it departs from the suggested remediation and why, how it was verified, and what to watch.

6. `Not mapped to a phase`: outcomes for IDs that no phase handled. Examples: items raised after the plan was set, and
   items parked by a decision.

7. `Pending`: the IDs not yet handled, each with its phase.

## Simulation audits

A simulation audit runs the pipeline for real, on topics chosen for the purpose, and audits the result. That covers the
runs' own reports, and everything they write: `graphs/<topic>/`, the survey, the output and the bib. It asks two
questions:

- Can a blind agent follow the spec? Where does it stall, guess, or improvise?
- Is what it produces right? Does what is on disk satisfy the spec, and do the judgements hold up when checked?

A simulation audit starts from the latest spec audit's disposition: its `Watch in the next run`, its `Pending`, and its
plan's `How to run it`.

Open before the first simulation audit: how the runner is launched. The method assumes a blind runner that dispatches
real `survey-pass` agents, and whether that can be done is `UNVERIFIED` ("Roles", below). Settle it first, and state the
answer in the audit's "How to read this document". If only the fallback works, the hand-over between the main session
and its agents goes untested, and the audit must say so.

### Why in segments

A whole pass run at once accumulates errors. A wrong screening verdict shapes the clusters, the clusters shape
selection, and so on. By the end of the pass, a failure's cause may be several steps back. Fixing everything one run
found, then running again, also tends not to converge. In this repo, three successive tabletops of a first pass found
20, 14 and 17 issues, the later ones mostly caused by the fixes to the earlier.

So a simulation audit runs the pass one segment at a time, and iterates each segment until it converges before moving
on. A segment ends at a gate, because a gate is where the files alone say whether the steps were done.

| segment | steps | ends at |
| -- | -- | -- |
| `G0` | 0: plan and preflight | `--gate G0` |
| `G1` | 1–2: orientation, expansion and screening, the pool, the fringe candidates | `--gate G1` |
| `G2` | 3: clustering, targeted expansion, naming | `--gate G2` |
| `G3` | 4: selection, bridges, fringe selection | `--gate G3` |
| `G4` | 5: the full texts, verification, replacing uncheckable rows | `--gate G4` |
| `G5` | 6–7: the output, the coverage rounds, Revise, the judgement audits | `--gate G5` |

Segments also spread the cost. Each iteration pays only for its own segment, and a spend limit or a dead session loses
at most one segment's work.

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

How the runner is launched. The preferred way is a separate, headless Claude Code session (`claude -p`), working in a
scratch copy of the repo from which `.audits/`, `docs/roadmap.md` and `docs/audits.md` are removed. Such a session can
dispatch real `survey-pass` agents, as a main session does. Whether it can be launched from the auditor's session, and
dispatch subagents of its own, is `UNVERIFIED`; the first simulation audit settles it. The fallback is a subagent that
plays each brief itself, as a tabletop does. That tests the docs, but not the hand-over between the main session and its
agents. Either way, blindness to git history holds by instruction only, and the runner reports any breach.

The runner's report lists every place it stalled, guessed, improvised or met a tool failure. Each comes with the
checklist row, the tag it would give, and what it did instead. The report also gives the halts and how they were
decided, the tokens per dispatch, and anything it read beyond its segment's rows. The raw reports are kept in `runs/`,
as `<topic>-<segment>-<iteration>.md`.

### Starting states

Each segment starts from the converged end of the one before, its checkpoint. When a segment converges, the auditor
saves the topic's files as that segment's checkpoint: the input, the survey, the output, the bib, and `graphs/<topic>/`.
That includes untracked files such as the full texts. The tracked files are committed; the untracked ones are archived
outside git, at a path the plan records.

Every iteration of a segment starts by restoring the checkpoint before it. So every iteration meets the same papers and
the same clusters. A difference between iterations then comes from the fix, or from the agents' own variability, and not
from new retrieval results.

A fix to a row of an earlier segment reopens that segment, unless the auditor can show the change cannot alter what the
segment writes. A reopened segment runs again from its own checkpoint. The segments after it then run once each, to
confirm, rather than being iterated again, unless that run finds something.

### Iterating a segment

1. Restore the checkpoint.
2. The runner runs the segment, up to its gate.
3. The auditor reviews three things: the runner's report; the gate's result and the plain check; and the segment's
   outputs against the spec, judgement by judgement, with the spot checks below.
4. Every issue becomes an `E` finding in the audit document, under the segment and iteration that found it.
5. The auditor fixes, after any decision the user must take. The gate test suites pass after every fix.
6. The segment runs again, from the same checkpoint.

The tags are a tabletop's three, plus one for errors only the review finds:

- `blocker` — the runner cannot proceed, or certainly fails a gate;
- `guess` — the runner must improvise, so two runners would differ;
- `silent` — the output breaks the spec, or a judgement is wrong, and the runner did not notice. This is the worst kind,
  because nothing in a real pass would flag it;
- `minor` — wording or findability.

A segment converges when one run after the last fix has no `blocker`, `guess` or `silent` finding. A `minor` finding is
fixed without another run. The catch: one clean run is weak evidence, because agents vary from run to run. The
confirmation runs below are the second test.

Fixes simplify where they can. Each added rule can collide with the rules already there, which is how fix rounds fail to
converge. So:

- Prefer a fix that deletes or shortens a rule to one that adds a rule.
- Record, per iteration, the size of the docs the fixes touched, before and after.
- If a segment's second run finds new `blocker`, `guess` or `silent` issues caused by the first round's fixes, stop
  patching. The next fix is a simplification of that segment's rows, proposed to the user before it is made.

### Spot checks per segment

A runner cannot report what it does not notice. These checks look for `silent` findings. Each is a sample drawn at
random, with its size and its result recorded.

- `G0`: the plan's dimensions and recency window, against the input.
- `G1`: about ten screening verdicts each way, in scope and out, against the input's topic and exclusions.
- `G2`: each cluster's name and definition, against the papers in its section of the naming sheet.
- `G3`: each role against its definition, and each `dissent` quote against the paper's abstract.
- `G4`: verified cells against the full text. This is where a reference reading belongs. The auditor reads about eight
  rows' full texts in full, and records its own findings before opening the rows' evidence files. Then it scores each
  row by the share of those findings it states.
- `G5`: output sentences against their rows, and coverage verdicts against the candidates' abstracts. The pass's own
  judgement audits (`docs/process.md`, "Auditing the judgements") cover part of this. The auditor checks their verdicts
  too.

### Steered branches

Some branches a run rarely takes: a halt, a coverage round that does not converge, a Revise, a return to step 3, an
uncheckable row, a trading pair that needs a bridge. Once a segment's main path has converged, the auditor may force
such a branch by editing the checkpoint, for example by planting a coverage verdict. Each steered branch is run and
iterated like a segment, and recorded as steered.

### Topics

The user writes an input for each topic. Three kinds serve different ends:

- `A narrow topic`, for iterating: a pool of about 50–150 papers and a coreset of about 15–25 rows, so that each
  iteration is cheap.
- `A confirmation run`, once every segment has converged: a whole pass from step 0, by a blind runner, with no steering
  and no restored checkpoints. On a topic with a reference point, such as an earlier survey, it also measures which of
  that survey's claims the coreset reproduces. A `blocker` sends the auditor back to the segment concerned. Other
  findings are recorded, and fixed in a later phase.
- `A wide topic`, to find where the method bends with scale: the pool size at which screening cost, outside services or
  the tools stop being practical. It runs as a confirmation run.

### What to record

Per run: tokens per dispatch, wall-clock time, the outside calls made, and the pool and coreset sizes. Per segment: each
quantity the spec estimates, against what the run measured. Examples are verification tokens per row in `G4`, and the
judgement-audit rates and the coverage radius per round in `G5`. Measurements go in the disposition, each with what it
implies for the spec's estimates.

The plan sets a budget per segment and per confirmation run. When a run goes well over it, the auditor stops and reports
to the user.

### The documents

A simulation audit has its own three documents, in `.audits/<YYYY-MM-DD>-simulation/`. All three are organised by
segment, the unit of a checkpoint, with one section per segment in the same order, so that the three line up.

Unlike a spec audit's, they are built one segment at a time. Segment N's sections open only once segment N−1 has
converged, and no issue of segment N is worked before then. An issue that shows up ahead of its segment, such as a `G2`
runner noticing a gap in the Verification brief, is recorded under its own segment and waits there. Why: a fix made for
a later segment, before the earlier ones are stable, is a fix made on ground that may still move.

- `simulation.md`, the audit. How to read it, including any open risk such as how the runner is launched; then the
  topics, the segments and the method; then one section per segment, with one subsection per iteration: its run, its
  review, and its `E` findings. `E` IDs are numbered across the whole audit, and defined here only.
- `remediation-plan.md`. How to read it; the user's decisions, such as the topics, the budget, and how the runner is
  launched; then one phase per segment, added when the segment opens, each listing its fixes as they are decided; then
  the confirmation runs. Its index maps every `E` ID to its phase.
- `disposition.md`. How to read it; a convergence table giving, per segment, the iterations, the findings per iteration
  by tag, and the size of the docs touched; then the outcomes per segment; the measurements; `Watch in the next run`;
  `Not mapped to a phase`; and `Pending`.
- `runs/`: the runners' raw reports.

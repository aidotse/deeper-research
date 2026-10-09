# Gates: checking that a pass did what it should

A pass is long, it runs across many agents, and an agent can die or skip a step. This file describes how the harness
checks, from the files alone, what a pass has done and what remains. It is written for the main session, which runs the
checks, and for anyone reviewing a pass.

It is not about whether a paper's claims are true. That is verification, in `docs/verification.md`.

## What the checks can and cannot tell you

`tools/check.py` checks **records, not judgement**. It can tell that the fringe candidates were screened, that every
`high` cluster had a dissent search, that every row still `abstract`-sourced is listed as needing verification. It
cannot tell whether a screening verdict was right, whether a dissent paper really contradicts its cluster, or whether a
claim is supported by the text retrieved. Those stay with the agents, with the main session's spot checks
(`docs/dispatch.md`), and with the user's review.

The two halves meet in one rule: **every judgement leaves a trace**. A judgement nobody wrote down cannot be reviewed,
audited or redone, and the worst failures of a pass are the silent ones (`.claude/agents/survey-pass.md`). So the checks
require the trace even where they cannot assess it:

- a candidate screened out of scope is recorded with its reason: `tools/assign.py reject` in orientation and expansion,
  the `in scope` and `reason` columns of `fringe-screen.md` for the fringe routes;
- a `dissent` row's `selected because` quotes the paper's claim that contradicts the cluster;
- a verified row keeps the verbatim quotes its claims rest on, in `graphs/<topic>/evidence/<id>.md`
  (`docs/verification.md`, "Recording the evidence");
- an empty role is recorded in Open work with what was searched;
- a halt is recorded with the user's decision.

## Two kinds of check

`python3 tools/check.py <topic>` runs both.

- **Integrity**: whatever exists must be well formed. A malformed row, a paper twice, a cluster name that is not a
  computed cluster, a coreset paper missing from the bib, an uncited `[abstract-only]`. These apply at every moment, to
  whatever is on disk. The full list is in `docs/tooling.md` ("Consistency check").
- **Gates**: what each step must have left behind. A missing log line, unscreened fringe candidates, a `high` cluster
  with no dissent search. These apply once the pass has reached the step, as below.

## The gates

A gate sits where an error becomes expensive to undo, or where the next step is costly. Each gate's requirements include
every earlier gate's.

| gate | after step | before | what it confirms |
| -- | -- | -- | -- |
| `G0` ready | 0 | any retrieval | the pass's log entry exists with its `Dimensions` line; the preflight passed (`H1` otherwise); no template placeholder left in the entry or in Open work; no log line written twice |
| `G1` pool complete | 2 | clustering | the frontier candidates are listed in `Orientation` and are in the pool, and `Expansion` names each as traversed; `Recency window`; every errored query was retried, and `H2` is recorded if one still failed; rejections were recorded this pass; every pool paper is fetched; the fringe routes were collected this pass, every candidate was judged with a reason, every `yes` is in the pool or in Open work; `Fringe` and `Pool` agree with the files |
| `G2` clusters named | 3 | selection | the clustering is from this pass; every Clusters row is complete; every pool paper's cluster is written; `Clustering`, `Temporal stability`, `Clustering rationale` and `Clusters` are present, use the Clusters table's ids, and agree with `clusters.json` and the table; `no structure` or a persisting `no stable level` is recorded as `H4` or `H5`; `review: before coreset` is recorded as `H13` |
| `G3` coreset selected | 4 | verification, about half the cost of a pass | every role the cluster's alignment requires is filled, or recorded under Open work's `Empty roles`; every `high` cluster appears in `Dissent searches`; every dissent row quotes its contradiction; every pair of clusters that trade papers has a bridge, and every internally divided `high` cluster a second frontier or a bridge, or an `Empty roles` entry; five to ten `fringe` rows; no empty cell; no row for a paper without a cluster; provisional dimensions named in `Dimensions` |
| `G4` verified | 5 | the output | every row verified against body text has its evidence file, covering `method summary`, `result` and each dimension not `n/a`, and every `full-text` quote is found in the fetched full text, ignoring punctuation and line breaks; every row still `abstract` is listed in Open work's `Rows needing verification`; more than 20% of them is recorded as `H10`; `Coreset` agrees with the table |
| `G5` pass ended | 7 | `Ended` stands | the output exists, with every `Questions` and `Reading` entry citing a coreset paper; each `Coverage test` line is well formed; `finished (F1)` follows a converged round, two unconverged rounds are recorded as `H11`, and `halted (<id>)` matches `Halts`; every candidate that changed the output is an assigned coreset row; no late paper is left unassigned; `Tokens`, `Halts` and `Ended` are present |

Each requirement has an ID, such as `g3.fringe-quota`, which the check prints when it fails. The code is
`tools/gates.py`, one function per requirement.

## Running a gate

The order of operations in `docs/process.md` has a row for each gate. There the main session runs:

```text
python3 tools/check.py <topic> --gate G2
```

It fails unless every requirement of `G0` to `G2` holds. When it passes, it says so, and the main session adds the gate
to the log's `Gates` line: `- **Gates:** G0 2026-10-09, G1 2026-10-09, G2 2026-10-10`. Do not start the next step before
the gate passes. A failure the responsible agent cannot fix halts the pass (`H9`).

Between gates, the plain `python3 tools/check.py <topic>`, run after every dispatch (`docs/dispatch.md`), checks the
gates the pass has already reached. It works that out from two sources:

- the `Gates` line: the gates the main session has passed;
- evidence in the files that a later step has started, as a safety net in case the `Gates` line was not kept: a
  `Clustering` line means step 3 ran, so `G1` must hold; a `Dissent searches` line, or Coreset rows on a first pass,
  means step 4 ran, so `G2` must hold; and so on to `Ended`, which requires `G5`.

## What has been done, and what remains

```text
python3 tools/check.py <topic> --status
```

prints every gate with its open requirements: what the run has accomplished, and exactly what remains before the next
gate. Use it to resume a pass in a new session, after a crash or a spend limit, rather than reconstructing the state
from reports that were lost with their sessions. Open work says what is outstanding in the survey's content; `--status`
says where the pass stands in the process.

## Halts and waivers

A halt (`docs/process.md`, "When a pass ends") is recorded in the log's `Halts` line as
`<id> — <what happened> — <the user's decision, YYYY-MM-DD>`. While the user has not decided, the decision is `pending`.
A pending halt holds every gate after the last one passed: `--gate` fails until the user decides.

Some requirements can be legitimately unmet, such as a topic whose coreset has only four ideas worth a `fringe` row. The
user may then waive the requirement. The main session records it in the log's `Waivers` line, as
`<requirement id> — <why> — <the user's decision, YYYY-MM-DD>`, and only with the user's decision. A waived requirement
is reported, not failed. An agent never waives anything.

## History

The check also compares the survey with the last commit, where one exists. It fails if:

- an earlier pass's log entry was changed, other than by adding to it, since entries are never rewritten
  (`docs/process.md`, "Rules for re-runs");
- a pool paper was removed without `H12` or a logged merge;
- a coreset row was removed without a `Demotions` or `Corrections` entry;
- a row's `source` was lowered.

It notes, without failing, an input changed since the last commit: only the user edits the input.

## Beyond the checks: auditing judgement

The checks show that each judgement was recorded. Whether the judgements are right is measured differently: by an
independent agent re-judging a small random sample, without seeing the original verdicts, and recording the agreement
rate. This is a proposal, not yet part of a pass; see `docs/roadmap.md`.

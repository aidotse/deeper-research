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

- a candidate screened out of scope is recorded with its reason: `tools/assign.py reject` in orientation; the `in scope`
  and `reason` columns of `expand-screen.md` for expansion, which `tools/assign.py add-expand` copies into
  `rejected.md`, and of `fringe-screen.md` for the fringe routes;
- a `dissent` row's `selected because` quotes the paper's claim that contradicts the cluster;
- a verified row keeps the verbatim quotes its claims rest on, in `graphs/<topic>/evidence/<id>.md`
  (`docs/verification.md`, "Recording the evidence");
- an empty role is recorded in Open work with what was searched;
- a halt is recorded with the user's decision.

## Two kinds of check

`python3 tools/check.py <topic>` runs both.

- **Integrity**: whatever exists must be well formed. A malformed row, a paper twice, a cluster name that is not a
  computed cluster, a coreset paper missing from the bib, an `abstract`-sourced citation without its `[abstract-only]`
  marker, or a marker that follows no cited ID. These apply at every moment, to whatever is on disk. The full list is in
  `docs/tooling.md` ("Consistency check").
- **Gates**: what each step must have left behind. A missing log line, unscreened fringe candidates, a `high` cluster
  with no dissent search. These apply once the pass has reached the step, as below.

## The gates

A gate sits where an error becomes expensive to undo, or where the next step is costly. Each gate's requirements include
every earlier gate's.

| gate | after step | before | what it confirms |
| -- | -- | -- | -- |
| `G0` ready | 0 | any retrieval | the pass's log entry exists; its `Dimensions` line says `declared in the input`, or, when the input declares none, proposes them, each with at least two values (`docs/formats.md`, "`Dimensions`"); the preflight passed (`H1` otherwise); `Halts` and `Waivers` written, as `none` if nothing happened; no template placeholder left in the entry or in Open work; no log line written twice |
| `G1` pool complete | 2 | clustering | `Orientation` names seeds or frontier candidates, and themes, and its frontier candidates are in the pool; `Recency window`; `expand.json` holds this pass's first collection, with a backward and a forward traversal from every seed and frontier candidate and a search for every theme, and a start paper Semantic Scholar did not find is in Open work; every candidate of this pass has a row on `expand-screen.md`, judged `yes` or `no` with a reason of at least two words; every `yes` is in the pool or in Open work, every `no` is in `rejected.md`, and no `no` is a pool paper; `Expansion` is the line `tools/assign.py add-expand` prints; every errored query was retried, and `H2` is recorded if one still failed; every pool paper is fetched; the fringe routes were collected this pass; every candidate in `fringe.json` has a row on the screening sheet, judged `yes` or `no` with a reason of at least two words; every `yes` is in the pool or in Open work; `Fringe` and `Pool` agree with the files |
| `G2` clusters named | 3 | selection | the clustering is from this pass; every Clusters row is complete, and every `high` cluster's definition states its central claim in a second sentence; every pool paper's cluster is written; `Clustering`, `Clustering rationale` and `Clusters` are present and not empty, use the Clusters table's ids, and agree with `clusters.json` and the table; `no structure` or a persisting `no stable level` is recorded as `H4` or `H5`; `review: before coreset` is recorded as `H13` |
| `G3` coreset selected | 4 | verification, more than half the cost of a pass | every role the cluster's alignment requires is filled, or recorded under Open work's `Empty roles`; every `high` cluster has an entry in `Dissent searches`, and every paper an entry says it found is a `dissent` row of that cluster, or named in `Demotions`; every dissent row quotes its contradiction; every pair of clusters that trade papers has a bridge, and every internally divided `high` cluster a second frontier or a bridge, or an `Empty roles` entry; five to ten `fringe` rows; no empty cell; no row for a paper without a cluster; one column per dimension, declared or proposed, and no other extra column |
| `G4` verified | 5 | the output | every row verified against the full text has its evidence file, headed by its own ID, with evidence for every cell that is not `n/a`; its `method summary` rests on a full-text quote; no quote comes from a snippet; every `full-text` quote has at least 6 words in each part between `...`, and is found in the fetched full text with its parts in order, ignoring case, punctuation and line breaks; a verified dissent row's quoted claim is among its evidence quotes; every row still `abstract` is listed in Open work's `Rows needing verification`; more than 20% of them is recorded as `H10`; `Coreset` agrees with the table; once a coverage round has run, every paper it counted is a coreset row verified from the full text or marked uncheckable |
| `G5` pass ended | 7 | `Ended` stands | the output exists, with every `Questions` and `Reading` entry citing a coreset paper; each `Coverage test` line is well formed, with at least 10 sampled candidates, as many IDs named as K, and `new clusters:`, and agrees with its round's sheet: every candidate judged, N its rows, the IDs counted in K its `changes` rows, a proposed cluster not reported as `none`, the recency query recorded, and the line as `tools/coverage.py line` prints it, up to `new clusters:`; `finished (F1)` follows a converged round, two unconverged rounds are recorded as `H11`, and `halted (<id>)` matches `Halts`; `Ended` reads `finished (F1)` or `halted (<id>)`; no late paper is left unassigned; the judgement audits are judged in full, and `Judgement audit` is the line `tools/audit.py line` prints; `Tokens` is a list of `<dispatch>: <tokens>`; `Tokens`, `Halts` and `Ended` are present and not empty |

Each requirement has an ID, such as `g3.fringe-quota`, which the check prints when it fails. The code is
`tools/gates.py`, one function per requirement.

## Running a gate

The order of operations in `docs/process.md` has a row for each gate. There the main session runs:

```text
python3 tools/check.py <topic> --gate G2
```

It fails unless every requirement of `G0` to `G2` holds, and nothing else fails either: the integrity checks and the
history checks count too. Only then does it say that the gate passed, and the main session adds the gate to the log's
`Gates` line: `- **Gates:** G0 2026-10-09, G1 2026-10-09, G2 2026-10-10`. Do not start the next step before the gate
passes. A failure the responsible agent cannot fix halts the pass (`H9`).

Between gates, the plain `python3 tools/check.py <topic>`, run after every dispatch (`docs/dispatch.md`), checks the
gates the pass has already reached. It works that out from two sources:

- the `Gates` line: the gates the main session has passed;
- evidence in the files that a later step has started, as a safety net in case the `Gates` line was not kept: a
  `Clustering` line means step 3 ran, so `G1` must hold; a `Dissent searches` line, or Coreset rows on a first pass,
  means step 4 ran, so `G2` must hold; and so on to `Ended`, which requires `G5`.

The check requires the higher of the two. The safety net is why papers added after a gate must be fetched before the
check runs: a pool paper added at step 7 fails `G1`'s `g1.fetched` until `tools/assign.py late` has fetched it and its
`Pool` line is pasted (`docs/process.md`, the "After every dispatch" row).

One requirement depends on a file that is not in git: a `full-text` quote can be found only in a fetched full text. If
the file is missing, as on a fresh clone, the plain check notes the quotes it could not check, and `--gate G4` or later
fails until `tools/fulltext.py` fetches it again. A gate is never passed on quotes nobody checked.

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
A pending halt holds every gate after the last one passed: `--gate` fails until the user decides. The plain check still
checks every gate the files show the pass has reached, so the work already done stays checked while the pass waits.

A pass the user decides to end at a halt is closed with `Ended: halted (<id>)`, its `Tokens` and its `Halts`. It then
needs only the gates it declared in its `Gates` line, plus those closing lines, so a legitimately halted topic still
passes the check. A halt still `pending` gets no such relief.

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
- a row's `source` was lowered;
- a cell of a verified row (`source` `full-text`, or `snippet` in an older commit) was changed without a
  `Corrections to existing rows` entry naming the paper. A row still `abstract` is a draft, which verification rewrites
  freely.

It notes, without failing, an input changed since the last commit: only the user edits the input.

## Beyond the checks: auditing judgement

The checks show that each judgement was recorded. Whether the judgements are right is measured differently: on a small
random sample, by agents that did not make them. A pass does this for two judgements, verification and the output's
faithfulness to its rows, and reports the rates in its `Judgement audit` line (`docs/process.md`, "Auditing the
judgements"). `G5` checks that the audits were done, not what they found. The other judgements, such as scope, dissent
and the coverage verdict, are not yet audited, so a passing gate says nothing about how often they are wrong.

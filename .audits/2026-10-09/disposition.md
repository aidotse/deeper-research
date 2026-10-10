# Disposition of the audit of 2026-10-09

What happened to each finding of `.audits/2026-10-09/docs-full-spec.md`, by ID. The audit defines the findings, and
`.audits/2026-10-09/remediation-plan.md` says what is done in what order (and defines the `R` items, raised after the
audit). This file says what was actually done, and it is the place to look when auditing a run.

Remediation also surfaces issues the audit did not list. Those are defined here, in the first section, with their own ID
prefix, the problem and the suggested remediation, and are then treated like any other finding.

Each outcome entry gives:

- `outcome` — fixed, adopted, moot, partial, deferred, or pending (with its phase);
- `commit` — where the change landed;
- what was done, where it departs from the suggested remediation, and why;
- how it was verified;
- what to watch in a real run.

The entries are ordered by ID, in the audit's sections, then `R` and `P`. To read by phase instead, use "By phase"
below. Update the file as each phase lands, in the same commit. An ID not yet handled is listed only under "Pending",
with its phase.

## Issues found during remediation

### `P` — Phase 3's tabletops

Phase 3's done-when was a fresh tabletop of a first pass, by an agent blind to `.audits/`, the roadmap and git history,
playing the main session and each brief from the docs alone. Two ran on 2026-10-10, at about 210k tokens each. The first
met none of the stalls the audit's own tabletop had found, and found 20 new ones; all were fixed in `558e816`. The
second, run on the fixed docs with the same prompt, found none of those 20 as first described. Its 14 findings are
below: 7 left by incomplete fixes or caused by them (marked `after a fix`), and 7 new. This list keeps only the current
issues; the first run's are in git history (`920b823`). A third run, the last, did not converge, and its findings were
not fixed: they are under "Watch in the first run", "What the Phase 3 tabletops left open".

Tags: `blocker` (cannot proceed, or certainly fails a gate), `guess` (must improvise, so two agents would differ),
`minor` (wording or findability).

- `P1` — `blocker`, after a fix. "After every dispatch" wrote `Coreset` once the coreset changed, which is right after
  Selection. But `check.py` takes a `Coreset` line as proof that step 4 is done, and so requires `G3` before Bridges and
  Fringe selection have run: `g3.fringe-quota` fails, and in the trading-pair branch `g3.bridges` too. Confirmed on the
  gate fixture. Suggested: write `Coreset` only from step 5's row on, or infer `G3` from a `fringe` row.
- `P2` — `guess`, trips `G5`. Step 7 said the counted papers are added only when a round does not converge. But
  `g5.changed-in-coreset` needs the K = 1 paper of a converging round as an assigned coreset row too. Confirmed on the
  fixture. Suggested: the counted papers of an `F1` round also go through Late papers and Revise before `Ended`.
- `P3` — `guess`. Selection's dissent search finds papers outside the pool through forward citations, but the brief
  gives it no way to add them, parallel agents may not write the pool, and a paper needs a cluster before a role; a
  dissent paper computed into another cluster cannot sit in this one's block. Suggested: Selection returns such papers;
  the main session adds them, runs `late`, and dispatches again.
- `P4` — `guess`. `H5` (and `H4`) is raised at the Cluster row, before naming and the viewer, but the review must show
  the named Clusters table and the viewer, and the review row came after `G2`, which cannot pass while the halt is
  pending. Suggested: state that the rows up to the viewer run while the halt is pending, and put the review before
  `G2`.
- `P5` — `guess`, after a fix. Naming must write the action taken for a cluster "still thin after one targeted
  expansion", but nothing hands it which regions were expanded, or the same-region judgement. Suggested: hand over the
  regions expanded, by paper ID, and whether each is still thin.
- `P6` — `guess`, after a fix. The "pool.py only" exception covered only the coverage dispatch, so after the targeted
  expansion for a proposed cluster the rule said `late`, which assigns the batch to existing clusters before the
  recluster. In a round with no proposed cluster, `late` had already run after the dispatch, and the `Late papers` line
  it printed was in no row's `writes`. Suggested: extend the exception to the step-7 expansion, and give the line to
  "After every dispatch".
- `P7` — `guess`, after a fix. Between the step-7 rename and the move, the check fails on rows in the wrong block, on a
  retired cluster's block, and on a `bridge:` naming a retired cluster, none of which the Revise exemption listed; read
  strictly, `H9`. Suggested: exempt rows not yet moved, and retarget `bridge:` cells.
- `P8` — `guess`, after a fix. A counted coverage paper takes "dissent for a contradiction", but it lands in whatever
  cluster `late` gives it, which may not be `high` and so has no central claim; a `fringe` row may exceed the quota; and
  Selection has no hand-over for "place this paper in this role". Suggested: a fallback role, and a Revise hand-over.
- `P9` — `guess`. Proposed dimensions carry names and values but no meaning, and no brief hands agents the `Dimensions`
  line, so Selection can invent a value (an integrity failure) and Verification "re-derives" a dimension it has no
  definition of. Suggested: a one-clause definition per proposed dimension, and the line in every brief that drafts or
  verifies cells.
- `P10` — `minor`. `add-fringe` lists in-scope candidates without an ID "for Open work", and `g1.fringe-added` needs
  them there, but the row's `writes` omitted Open work. Suggested: add it.
- `P11` — `minor`. In `Expansion`, a "not" anywhere in a traversal part voids it, and `(35, note)` does not match
  `(<n>)`: `backward from A (40), B (35, references not all resolved)` fails `g1.expansion` for both. Confirmed by
  running it. Suggested: say the bracket holds only the count, or relax the pattern.
- `P12` — `minor`, after a fix. Step 2's bullet said forward traversal starts from the seeds and the frontier papers;
  its prose and done-when said only from the seeds. Suggested: pick one.
- `P13` — `minor`. The `CLAUDE.md` index's "when to read" column reads as whole files for `survey-pass`, against the
  brief's section lists; and the Bridges brief listed no Asta section, though it reads abstracts through Asta.
  Suggested: have the index defer to the briefs, and add the section.
- `P14` — `minor`. Whether the main session waits for the user to accept proposed dimensions before Preflight was not
  stated. Suggested: say whether the plan report is blocking.

### `P` — Phase 4's simulation

Phase 4 was tested by a partial simulation that ran for real. A blind agent (no `.audits/`, roadmap, `tests/` or git
history) played the main session of a pass on a scratch copy of the gate fixture, `zz-sim`, from step 7 to the end, and
played each brief itself. Every script ran, and full texts were fetched from arXiv; only outside retrieval (WebSearch,
Asta) was imagined. It was steered through two coverage rounds, the first not converging, with a recency candidate and a
Revise. It reached `F1` and `--gate G5` passed. About 200k tokens, on 2026-10-10. It found no `blocker`, 12 `guess` and
9 `minor`; its full report, with the run log, is `.audits/2026-10-09/phase4-simulation.md`. Three recur from the third
tabletop of Phase 3, left unfixed then by agreement (marked `recurs`). None is fixed yet: whether to fix and simulate
again, or leave them to the first run, is the user's call. Tags as above.

- `P15` — `guess`. Revise is "done when `tools/check.py` passes again", but the plain check passed right after round 1,
  before any counted paper was a coreset row; only `G5` checks that. Suggested: once a `Coverage test` line exists, the
  plain check fails on each counted ID not yet an assigned coreset row.
- `P16` — `guess`. "End the round" says "another round" without saying where to re-enter, and the audit rows sit between
  Revise and End the round. Suggested: on a round that did not converge, return to "Draw the coverage sample" with R+1,
  skipping the audit rows.
- `P17` — `guess`. The fresh recency query's window is unclear: the pass's `Recency window` ended before step 7.
  Suggested: the pass's window, extended to the day of the round.
- `P18` — `guess`. The recency query (text, window, result count) is recorded nowhere, so a round with no recency rows
  looks like one where the query never ran. Suggested: `coverage.py` writes a `recency query:` line on the sheet.
- `P19` — `guess`. The role for a counted paper does not cover a `Gaps` change that is a tension or an open problem.
  Suggested: map each kind of change to a role.
- `P20` — `guess`. Dissent rows added through the coverage test have no `Dissent searches` entry, and nothing says
  whether they need one. Suggested: say not, or define `<cluster>: coverage round R -> found: <id>`.
- `P21` — `guess`. When verification contradicts a coverage verdict's reason, nothing says what to do. Re-running
  `coverage.py judge` overwrote the verdict silently, and `G5` passed with a stale `Coverage test` line. Suggested:
  `judge` reports replaced verdicts; Revise re-judges and re-pastes the line; `G5` compares the whole line with
  `coverage.py line`, as it does for `Judgement audit`.
- `P22` — `guess`. Which step-4 rows Revise reruns is unclear (Fringe and Bridges). Suggested: Selection for the counted
  papers; Bridges only on the check's note; Fringe only for a counted paper proposed as `fringe`.
- `P23` — `guess`. Revise's batch fetch also fetched two older `abstract` rows listed as having no body text; nothing
  says whether Verification now takes them. Suggested: say so, or have `fulltext.py` print rows that have become
  fetchable.
- `P24` — `guess`, `recurs`. Whether `Ended` waits for the user's cluster review: "Cluster review" says before `Ended`,
  the row says "if given", and `G5` accepts "not yet reviewed". Suggested: say plainly which.
- `P25` — `guess`. The faithfulness rubric does not cover `Reading` and `Questions` sentences that claim nothing about a
  paper ("start here"). Suggested: `trace` leaves those two sections out.
- `P26` — `guess`. `Ended`'s "measured numbers" have no form. Suggested: give it: last round's K of N, the bound, the
  radius, the rounds, the coreset size.
- `P27` — `minor`. The Coverage test brief and row say to `add` every candidate that changed a target; drawn candidates
  are pool papers already. Suggested: "each recency candidate that ...".
- `P28` — `minor`. `coverage.py judge --recency` writes the bare ID as the paper cell, against "title, linked by its
  ID", and does not check the paper exists. Suggested: take the title from the pool or Semantic Scholar.
- `P29` — `minor`, `recurs`. The step-7 `Late papers` row reruns the `late` that "After every dispatch" just ran.
  Suggested: say the row is that run.
- `P30` — `minor`, `recurs`. The Selection brief's `Read` list leaves out step 7's paragraph on counted papers' roles.
  Suggested: add it for the Revise use.
- `P31` — `minor`. `G2` does not check that a `high` cluster's definition states its central claim, which step-7
  `dissent` rows are judged against. Suggested: a `g2` requirement.
- `P32` — `minor`. `--gate G5` says "add `G5 <today>` to `Gates`" when it is already there. Suggested: only when
  missing; likewise for every gate.
- `P33` — `minor`. `coverage.py line` joins reasons as ".,". Suggested: strip the reason's final full stop.
- `P34` — `minor`. The entry had no `Waivers` line and every gate passed, though the format says it is written as
  `none`. Suggested: `G0` requires it.
- `P35` — `minor`. `docs/tooling.md` says `trace` draws 15 sentences; with 9 it takes all. Suggested: "15, or all if
  fewer".

## By phase

| phase | commits | IDs handled |
| -- | -- | -- |
| 0 | `5d18f12` | the rename to `reasoning-legacy`; `T8` in part |
| 1 | `532e697` | `Z2`–`Z5`, `Z7`–`Z9`, `M13`; moot with them: `M9`, `M10`, `T1`, `S3`, half of `A7`, the history half of `M20` |
| 2 | `d600a69`, `4d8e9a2`, `46d9dfd`, `4dc8dff`, `cda762a`, `f99ec2c`, `c43ba0c` | `C1`–`C6`, `C8`, `C9`, `M1`–`M6`, `M11`, `M12`, `M14`–`M19`, `S6`, `A9`, `T5`, `T9`, `R2`, `R3`; the code side of `C10`, `M20`, `S1`, `S2`, `S4`, `S15`; `T8` in part |
| 3 | `558e816`, and "Remediation phase 3: a second tabletop" | `W1`–`W4`, `S5`, `S7`, `S9`–`S12`, `S14`, `A1`–`A8`, `R1`, `P1`–`P14`; the doc side of `C10`, `S1`, `S2`, `S4`, `S15`; the code side of `S10` and `A2`; `T8` in part |
| 4 | "Remediation phase 4: instrument the run" | TODO 1 (the third tabletop's blocker); `T2`, `T3`, `T4`, `T6`, `R4`, the tool half of `A3`; `T8` in part; `P15`–`P35` found, open |
| 5 | pending | `R6`, and `Z1` in practice |
| after the run | pending | `Z6`, `C7`, `M7`, `M8`, `S8`, `S13`, `T7`, `W3` step 2, `M20`'s hidden route, `R5`, the rest of `T8` |

## Commits

| phase | commit | what |
| -- | -- | -- |
| 0 | `5d18f12` | rename to `reasoning-legacy`; harden the gate tests |
| 1 | `532e697` | simplify verification and clustering (`Z2`–`Z5`, `Z7`–`Z9`) |
| 2a, 2e | `d600a69` | `tools/gates.py`, `tools/check.py`; the Stop hook |
| 2b | `4d8e9a2` | `tools/inputs.py` |
| 2d | `46d9dfd`, `4dc8dff` | `assign.py`, `fringe.py`, `pool.py`, `bib.py`, `sheets.py`; `C6` |
| 2c | `cda762a` | `tools/cluster.py`, `tools/match.py` |
| 2d | `f99ec2c` | `tools/fulltext.py`, `tools/graph.py` |
| 2 | `c43ba0c` | the arXiv backfill of `reasoning-legacy`'s pool |
| 3 | `558e816`, and "Remediation phase 3: a second tabletop" | the spec pass over `docs/`, `CLAUDE.md` and the agents; `S10`'s gate change; `A2`'s sheet column; the first tabletop's fixes |
| 4 | "Remediation phase 4: instrument the run" | `tools/coverage.py`, `tools/audit.py`, `check.py --print`, two `G5` requirements; the `R4` experiment and its records; the simulation's findings |

## Watch in the first run

### Judgement calls

These are judgement calls whose effect only real data will show. When auditing the run, check these first.

- `M11`, the fringe score. The audit proposed mixing the raw text and reference distances, then ranking once. That
  failed: reference distances sit near 0.95 and text distances near 0.08, so a raw mix sank every paper without
  references to the bottom. The fix instead:

  - turns each distance into a normal score, from its percentile in the pool;
  - mixes the two with the existing weight;
  - rescales the mix so that every paper's score has the same spread;
  - ranks once within the paper's age cohort.

  Why the rescaling: a weighted mix of two partly independent scores is less extreme than either one. Without it, papers
  scored by text alone still crowded both ends. Watch:

  - Scores now come in steps of 1/30, the cohort size. On `reasoning-legacy` the top 7 all score 0.967–0.968, so their
    order comes from the tie-break on the mixed score. The order is meaningful; the score alone does not show it.
  - Zero-reference papers in the top 8 went from 5 to 1. But their mean score is still above the pool's (0.637 against
    about 0.49). Whether that is a real signal is `UNVERIFIED`. If a run's fringe list again leans towards papers
    without references, start here.

- `Z2`, the cost of verifying from full text. The estimate before Phase 4 was the ~10k per row of snippet-based passes.
  `R4` measured about 26k per row: 27 rows verified by strong agents reading with the section reader and Grep, by the
  harness's per-agent token counts (what those include is `UNVERIFIED`). `docs/process.md` now plans with 26k per row
  and 2–2.5M per pass, up from 1–1.5M. `R6` measures it again inside a real pass, where agents verify a block of rows
  and also write evidence files. The risks to check, in order:

  - an agent that `Read`s a whole full text pulls in 10–70k tokens at once. If verification tokens per row come out
    high, look here first;
  - Grep may need more tries than one semantic snippet query, especially in PDF text, where words are hyphenated across
    lines;
  - parallel verification agents that each fetch their own papers exceed arXiv's 3-second spacing together. `R1` (the
    main session fetches in one batch) is the fix, due in Phase 3. The measured rate is 27 papers in 90 seconds, so
    about 3 minutes for 60 rows, once per pass;
  - a paper with no fetchable full text stays `abstract`, where snippets could once have verified it. Too many of those
    trip `H10`. All 195 papers of `reasoning-legacy` have an arXiv ID, so this field is safe; another field may not be.
    `R3` now shows the share per topic, and `R5` is the reserve.

  Asta with a key allows 10 requests per second, against arXiv's one per 3 seconds. But a single `snippet_search` has
  been seen to hang for over two minutes, so Asta is not clearly faster in practice.

- `Z2`, what targeted reading misses. `R4` measured it: reading by the section reader and Grep found about 90% of what a
  whole reading of the paper found, on 8 papers, and most of what it missed was in appendices or footnotes. So the
  verification method gained a step: read the appendix sections a result turns on. That step was added after the
  measurement and is itself untested; watch whether it raises tokens per row, and whether evidence files cite
  appendices. The measurement's limits are in `docs/experiments.md`: one reference reader, not blind scoring, 8 papers.

- The viewer has never been rendered in a browser. Headless Chromium could not start here, so both the Phase 1 changes
  (panels removed with `Z3` and `Z5`) and the `R3` colour mode were checked in node only. Open
  `graphs/<topic>/graph.html` once before relying on it.

- `M12`, the age cohort: the 30 papers nearest by publication date. Cohorts of 20 to 50 barely changed the top of the
  list on `reasoning-legacy`. A pool of 30 or fewer is ranked as a whole. That is fine for a smoke pass, but there the
  correction does nothing.

- `M1`, the quote length: at least 6 words per elided part. Short result quotes ("achieves 92.1% on GSM8K" is 5 words)
  must be quoted with more of their sentence. If verification agents keep failing `g4.evidence` on short quotes, revisit
  the threshold before loosening the rule.

- `S1`, proposed dimensions: the `Dimensions` line form is `` proposed: `<name>` — values: `<a>`, `<b>`; ... ``. The
  form is strict, and an agent may get it wrong at the Plan step. The failure message gives the form.

- `C9`, the PDF bibliography cut: tested on synthetic text only, because no local full text came from a PDF. An appendix
  not headed "Appendix" or "Supplementary material" is cut along with the bibliography. `UNVERIFIED` on real pypdf
  output. Check the first PDF-sourced paper by hand.

- `M16`, rejected papers in `fringe.py collect`: excluding them from the `new` route relies on the recommendations
  endpoint returning `externalIds` when asked. `UNVERIFIED`. If it does not, a second check on the fetched records still
  excludes them, but that route can come up short of its count.

- `T5`, `maybe` on the screening sheet: a parking state the spec does not mention. It counts as unjudged, so
  `add-fringe` and `G1` refuse while any remain.

- `W3`, the per-brief reading lists. Each brief in `docs/dispatch.md` now lists the sections its agent reads, and
  `docs/coresets.md` left agent reading. Whether the lists are enough is untested in a real run: an agent that keeps
  following pointers out of its sections, or improvises for want of one, is a list to fix. Spec reading is now counted
  in `Tokens`, since each dispatch's usage includes it.

- `A1`, the stopping rules. Orientation stops after two queries with no new frontier candidate; expansion, beyond its
  required work, once a batch of about 50 screened candidates adds fewer than 5 papers. Both numbers are first guesses.
  Too early a stop shows as a thin pool and `thin cluster` diagnostics; too late, as screening cost.

- `S10`, evidence for every cell not `n/a`. `G4` now requires evidence for `method name`, `datasets / models` and
  `metric` too. One quote may cover several cells, so the cost should be small, but it adds to verification tokens per
  row, which `R6` measures.

- `A3` and `T4`, the coverage sample. `tools/coverage.py draw` now draws ten pool papers at random from the
  worst-covered quarter, and the hand weighting the spec had (toward thin clusters, plus a few high fringe scores) is
  gone, since the worst-covered papers subsume both in intent. That is a judgement call: a high-fringe-score paper far
  from its age cohort but near a coreset row is no longer sampled. If the first run's coverage rounds look too easy,
  start here. The bound the line prints holds only for the worst-covered quarter, and leaves the recency candidates out.
  Distances are in rank units of the `combined` measure, so a radius of 0.45 means a paper whose nearest coreset row is,
  on average, outside its nearest 45% of the pool: interpret the radius relative to other rounds and topics, not in
  absolute terms. On the gate fixture's 19 rows the radius was 0.451, p90 0.215.

- `T2` and `T3`, the judgement audits. Both are new on every pass, at about 50–100k tokens. Nothing yet says what rate
  is acceptable, and the audits measure without repairing: each `differ` or `unsupported` goes to the user. The
  re-verifying agent is blind to the rows only by instruction (it could open the survey); check its report says it did
  not. The comparison verdicts `agree`, `partly`, `differ` are judged by a second agent; whether two judges agree on
  them is itself unmeasured.

- `S11`, the user's cluster review. It is now taken before `Ended`, when the output is shown; a review after `Ended`
  goes into the next pass's entry. If users routinely review later, the `Clusters` line of a finished pass will always
  read "not yet reviewed".

- `Returning to step 3`. A recluster after step 3, for a proposed cluster or on `RECLUSTER:`, now reruns the step-3 rows
  and step 4's block set-up, and leans on one exemption ("the return's open work") until the check passes again. Neither
  tabletop exercised this version. If the first run reaches it, check that the main session could tell that open work
  from a real failure.

- `R2`, the section reader (`fulltext.py show`): its PDF heading detection is a guess. Letter-prefixed headings such as
  "B Additional results" are not detected. Whether verification uses it at all is for `R4` to decide.

### What the Phase 3 tabletops left open

Phase 3 tested the docs by tabletop: a partial simulation of a first pass, in which a blind agent played the main
session and each brief from the docs alone, ran the offline scripts on a scratch fixture, and imagined the retrieval.
Three such runs were made on 2026-10-10, each after fixing what the one before found. The issues of the first two are
the `P` items above. They did not converge: the counts were 20, 14 and 17. The second run's issues came mostly from the
first round's fixes; the third's sit mostly on rarer branches and finer detail. The third run's findings were therefore
not fixed (user, 2026-10-10), and are listed below, each with the fix the tabletop suggested, for the first run to
confirm or dismiss. The agent of the third run broke one blindness rule once, a `git status` to confirm its cleanup; it
read no history.

That three rounds did not converge may itself be a finding. Each fix added rules, and new rules collided with old ones,
which is what the audit's `Z1` warned of. If the first run stumbles where these findings say, the answer may be to
simplify rather than to add a rule: shorter wording, fewer special cases in the order of operations, or a simpler
process at the branch concerned, as was done for the step-7 recluster ("Returning to step 3").

The third run's findings, 17 in all (1 `blocker`, 8 `guess`, 8 `minor`):

- `blocker`: on a return to step 3, `--gate G2` cannot pass. A `Coverage test` line makes `check.py` require `G0`–`G4`,
  and `--gate` passes only when nothing fails, so the return's open work fails it; Revise's `G3` likewise, and `g4.h10`
  while new rows await verification. Confirmed on the fixture. Fix: on a return, skip re-gating until Revise is done.
  Fixed in Phase 4 (TODO 1), as suggested, and extended to Revise without a return, which met the same wall: its `G3`
  and `G4` gate rows are skipped too, since the `Coverage test` line already makes the plain check require them.
- `guess`: `H6` at naming. An unratable cluster cannot get a valid row, yet the rows up to the viewer must run, and
  nothing says who applies the user's rating later. Fix: a provisional rating, marked in `alignment reason`, and a
  Naming re-dispatch for the decision.
- `guess`: Selection's Revise hand-over. Its `Read` list lacks step 7's role paragraph (extra rows allowed, the
  `frontier` fallback), so it may demote a row to make room; and the Coverage brief does not return a proposed role.
  Fix: add the paragraph to the list; have Coverage propose the role.
- `guess`: Bridges has no search method or candidate list. Fix: `sheets.py` lists the papers each trading pair
  exchanges, as the starting point.
- `guess`: replacing an uncheckable row can loop, since the old row is demoted before the replacement is fetched. Fix:
  demote only once the replacement verifies; one attempt per role.
- `guess`: rejecting a candidate with no ID. `assign.py reject` needs one, and the Coverage brief does not say where an
  out-of-scope fresh-query candidate is recorded. Fix: record rejections only for candidates with an ID; name the
  coverage case.
- `guess`: a targeted expansion's scope: "most-cited papers" has no number, `no stable level` names no regions, and new
  thin clusters after the rerun could each claim an expansion. Fix: the region's top 3 by in-degree; new thin clusters
  after the rerun are kept, not expanded.
- `guess`: a dissent paper returned for the pool has no pending form in `Dissent searches`. Fix:
  `-> returned for the pool: <id>`, rewritten on the re-dispatch.
- `guess`: telling whether a region is "still thin" needs `jq` on `clusters.json`'s `assignment`, which is undocumented.
  Fix: print each region paper's cluster, or document the call.
- `minor`: the main session rewrites the Coverage agent's `new clusters:`, but no `writes` cell gives it that line; and
  an unformed proposal has no provisional form.
- `minor`: `Late papers` may need both forms in one pass, and a second line fails `g0.labels`. Fix: append with `|`.
- `minor`: re-passing `G2`–`G4` after a return has no `Gates` form. Fix: append with the new date.
- `minor`: the Bridges and Fringe-selection briefs do not say to draft every cell from the abstract, as Selection's
  does.
- `minor`: "Fetch pool data" and "Late papers" rerun what "After every dispatch" just ran; say so.
- `minor`: `g1.orientation` needs at least one frontier candidate; a quiet topic has no rule. Fix: allow `none`.
- `minor`, `UNVERIFIED`: parallel agents `Edit` one survey file, and a read-modify-write race could lose an edit that
  shows only at `--gate G3`. Fix: re-read the whole Coreset section, or serialise writes.
- `minor`: whether the main session waits for the user's cluster review before `Ended` is not stated.

## C — the docs and the code disagree

- `C1` — fixed, `d600a69`. `check.py` notes a trading pair without a bridge as soon as there are Coreset rows and `G3`
  is not yet required, saying to run the Bridges row. Built from `r_bridges`, the requirement `G3` later enforces.
  Verified: behaviour case 6k.
- `C2` — fixed, `d600a69`. A full text that is not fetched fails `--gate G4` and later. It stays a note in the plain
  check, so that a fresh clone without full texts still passes the plain check. Verified: behaviour case 6b.
- `C3` — fixed, `d600a69`. The "G<n> passed" note moved to `check.py`, after every failure is known. Verified: behaviour
  case 6d, with an integrity failure.
- `C4` — fixed, `d600a69`. A pending halt no longer replaces the inferred gates; it only fails `--gate`. Verified:
  behaviour case 6e.
- `C5` — fixed, `d600a69`, by the reverse check rather than by rewording. A marker after the legend that follows no
  cited ID fails. A marker after a verified paper is allowed, since a number may be abstract-only even in a verified
  row. The check applies to the coreset layout only: the legacy output mentions the marker in prose after its legend,
  and would fail. Verified: behaviour case 6l.
- `C6` — fixed, `4dc8dff`. `add-fringe` uses `gates.judged`, the test `G1` uses. It also refuses a `fringe.json`
  candidate with no sheet row. Verified by simulation: `maybe`, a blank reason, and deleted rows are all refused.
- `C8` — fixed, `d600a69`. `--gate` and `--status` run on a survey with no log entry. Verified: behaviour case 6f.
- `C9` — fixed, `f99ec2c`. PDF text is cut from the last references heading that is followed by a reference list, up to
  an explicit appendix heading, and a `[bibliography removed]` line marks the cut. Watch: see above.
- `C10` — fixed, `46d9dfd` and `cda762a`:
  - The `add` hint names `pool.py` before step 3, or `assign.py late` after it.
  - Usage errors exit 2 in `pool.py`, `fringe.py`, `cluster.py` and `match.py`.
  - The `RECLUSTER` message gives the count and the exact share.
  - `cluster.py`'s match printout lists splits, merges, new and vanished clusters on one `changes:` line. Tested on
    synthetic cases only: `reasoning-legacy` has no named clusters to match.
  - The defaults are written to `params.defaults`. Doc side, Phase 3: `docs/tooling.md` gives every default and says
    they are first guesses, not "the spec's"; the `params` keys, the pinned versions, exit 2 and the `changes:` line are
    documented.

## M — method bugs

- `M1` — fixed, `d600a69`. Quotes are matched on whole words, at least 6 per part, with the parts in order and each
  within 3000 characters of the last. Line-break hyphenation is handled by matching two readings of the text: words
  joined across the break (`im-` / `proves`), and not joined, so that a compound broken at its hyphen also matches.
  Verified: faults for an empty quote, a vacuous elision, a 3-word fragment, and parts out of order. Watch: the
  threshold, see above.

- `M2` — fixed, `d600a69`:

  - An evidence file must be headed by its row's ID.
  - A `full-text` row's `method summary` must rest on a full-text quote, since the abstract may carry a number but never
    the method (`docs/verification.md`). That is stricter than the audit's "at least one full-text entry".
  - New requirement `g4.dissent-evidence`: a verified dissent row's quoted claim must be among its evidence quotes. This
    is `M4`'s last bullet, placed at `G4` because that is where the evidence exists.

  Verified: faults for each.

- `M3` — fixed, `d600a69`. A line that is empty after stripping counts as missing, and `Ended` must read `finished (F1)`
  or `halted (<id>)`. Verified: faults for an empty `Clustering rationale`, `Ended` and `Halts`, and a malformed
  `Ended`.

- `M4` — fixed, `d600a69`:

  - `Dissent searches` is parsed per cluster. Every `found:` ID must be a dissent row of that cluster, or be named in
    `Demotions`.
  - `Tokens` must be `<step>: <n>` pairs.
  - A `Coverage test` round needs N ≥ 10, and as many IDs as K. Only IDs that open an entry are counted, so an ID inside
    "what it changed" is not.
  - `Expansion` counts a candidate as traversed only in a part that opens with a direction and gives it a count
    (`backward from <id> (40)`), and has no "not".

  Verified: a fault for each.

- `M5` — fixed, `d600a69`. Every `fringe.json` candidate needs a sheet row, and a reason must be at least two words.
  Verified: faults for deleted rows and for a reason of `x`.

- `M6` — fixed, `d600a69`. A pass ended at a halt, with the user's decision recorded, needs only the gates it declared,
  plus its closing lines (`Tokens`, `Halts`, `Ended`). A halt still pending gets no relief. Verified: behaviour case 6g,
  both ways.

- `M11` — fixed, `cda762a`, by another method than the audit's. See "Watch in the first run".

- `M12` — fixed, `cda762a`: the 30 papers nearest by date, falling back to mid-year when a paper has only a year. Both
  2021 papers in `reasoning-legacy` now have a cohort of 30, from 2021 to 2024. Before, each was ranked against all 195
  papers. The 2021 paper `2104.03113` stays fourth: it is far from the older papers too.

- `M13` — fixed in Phase 1, `532e697`. When every holdout cutoff is skipped, stability comes from resampling only, with
  a printed note.

- `M14` — fixed, `cda762a`. Each part (finer cluster ∩ coarse cluster) is scored on its own. For a whole cluster this
  reproduces the clusterwise score exactly. The shared 0.48 the audit found splits into 0.12, 0.16 and 0.36. No
  `divided` flag changed.

- `M15` — fixed, `46d9dfd`. The sheet has no `year` column, and `fringe.py` reads sheets by header, so older six-column
  sheets still parse.

- `M16` — fixed, `46d9dfd` and `d600a69`:

  - `collect` excludes rejected IDs.
  - `add` and `add-fringe` warn, naming the rejection.
  - `check.py` notes a paper both rejected and in the pool.

  Verified: behaviour case 6m, and simulation. Watch: `externalIds`, see above.

- `M17` — fixed, `46d9dfd`. Records without the `arxiv` key get only `arxiv` and `corpus`, by a light call. The rest of
  each record and its `fetched` date stay as they were, so `clusters.json` still matches `pool.json`. A full refetch
  remains `--refresh`. The backfill ran on `reasoning-legacy` (`c43ba0c`): 2 calls, 195 of 195 records now have `arxiv`,
  and no other key changed.

- `M18` — fixed, `4d8e9a2`. `*`, `+` and numbered bullets are accepted rather than failed. mdformat rewrites `*` as `-`
  and keeps numbers, so the input reads the same before and after the hook. The Oxford comma, a duplicate section, an
  empty `Topic`, `granularity: 0` and zero targets all fail. Lazy continuation lines are joined, for the same reason as
  `*`. Verified: `inputs/reasoning.md` and `inputs/reasoning-legacy.md` parse byte-identically before and after.

- `M19` — fixed, `d600a69`. The Stop hook formats `docs/` and `outputs/` only. A missing mdformat is a non-blocking
  error. `CLAUDE.md` and `.audits/` are no longer formatted automatically, so run `mdformat` on them by hand.

- `M20`:

  - The holdout normalisation is fixed, `cda762a`: holdout reruns recompute the measure on the subset, in `cluster.py`
    and in `match.py`. Stability at the chosen level went from 0.789 to 0.799, holdout ARI from 0.819 to 0.839, and the
    level is unchanged. `recursive.py` still slices the full-pool normalisation, since only its docstring was in scope.
  - The fixed `hidden` route size: pending, after the run.
  - `bib.py` links, fixed, `46d9dfd`: the first link per row, as `check.py` takes it.

- `M9`, `M10` — moot with `Z3`.

## S — spec inconsistencies and gaps

- `S1` — fixed, `d600a69` and Phase 3. Without declared dimensions, `check.py` reads the proposed ones from the current
  entry's `Dimensions` line, and checks values, columns and evidence against them, as for declared ones. Each needs at
  least two values. `g3.dimension-columns` now also applies to declared dimensions: no extra column, and none missing.
  Verified: faults for a malformed and a one-value proposal, and behaviour case 6j. Doc side: the main session proposes
  them at the Plan row and reports them with the plan (`docs/formats.md`, "`Dimensions`"); the log form is in the
  template; `G0` and `G3` in `docs/gates.md` say what is checked. The proposal does not wait for the user's approval:
  they see it in the plan report, and can stop the pass there.
- `S2` — fixed, `d600a69` and Phase 3. The `check.py` messages name `pool.py` or `assign.py late` and say to paste the
  `Pool` line. The procedure is a standing row of the order of operations, "After every dispatch": append `Tokens`,
  fetch any added pool rows (`pool.py` up to step 3, and on a return to it; `late` after), paste `Pool`, then check.
  Selection and the other row-adding agents list their new rows under `Rows needing verification`, so a Revise round no
  longer trips `g4.abstract-listed`. One wrinkle remains: during step 3's targeted-expansion loop, and on a return to
  step 3, this pass's `clusters.json` exists, so `check.py` suggests `late`, while the procedure says `pool.py` (the
  recluster places the papers). Both satisfy the gate; the row says which to run.
- `S3` — moot with `Z7`.
- `S4` — fixed, `d600a69` and Phase 3. The code already accepted `new clusters: none (proposed <x>, not formed)` as
  converged, and behaviour case 6i pins it. A proposed cluster now returns the pass to step 3 ("Returning to step 3"): a
  targeted expansion, a recluster even below 10%, and the main session records the outcome from the `changes:` line,
  formed or `none (proposed <x>, not formed)`. See `P6`–`P8` for why it no longer has step-7 rows of its own.
- `S6` — fixed, `d600a69`. `; rejected: none` at the end of `Expansion` replaces `rejected.md`. Verified: behaviour case
  6h.
- `S5` — fixed, Phase 3. `docs/process.md`, step 7, gives the one-sided 95% bounds (recomputed: 26/39%, 22/34% and
  18/28% for N = 10, 12, 15 at K = 0/1), and asks for the last round's bound in `Ended`. `docs/coresets.md` says the
  same in brief. The claim that the targeted sample makes the bounds pessimistic is marked as reasoned, not measured.
  The scripted sample and a sequential rule are not done: the first is Phase 4 (`T4`), the second was not adopted.
- `S7` — fixed, Phase 3. One rule: the finest level whose stability reaches `τ`, even past a dip. The docstrings in
  `tools/cluster.py` said the same two things as the doc and were aligned.
- `S9` — fixed, Phase 3. The "survive losing 20%" line now gives the resampling ARI at the chosen level, 0.76, read from
  `clusters.json`. The late-assignment figure is the audit's out-of-sample 13 of 15. The fringe-addition figure, ARI
  0.70, keeps its number with the caveat that 16 of the 118 papers came from a route since dropped: re-measuring needs
  `fringe.py analyse`, an experiment that rewrites files, and the number only illustrates a point.
- `S10` — fixed, Phase 3, partly in code. Beyond `Z2`:
  - Evidence for every cell not `n/a`, enforced: `r_evidence` now requires `method name`, `datasets / models` and
    `metric` as well. The audit asked only for the statement; stating a rule the gate did not check would have been a
    new `C`-class mismatch. Fixture and a new fault updated: 71 of 71 faults.
  - Verifying a draft is not a correction: outcomes are now Verified, Corrected (an already-verified row only) and
    Uncheckable.
  - The replacement search goes to Selection, dispatched by the main session in a new step-5 row; `fringe` rows are not
    replaced.
  - "Publication grade" is still defined by its standard, not by observable criteria. Left as is: the evidence rules are
    the observable part.
- `S11` — fixed, Phase 3. The `writes` column of the order of operations is declared the only authority, and
  `docs/formats.md` and `docs/dispatch.md` defer to it. Changes:
  - standing rows marked `any`: "After every dispatch" (`Tokens` appended, `Log:` and `Open work:` lines written), "On a
    halt" (`Halts`), "On a requirement the user may waive" (`Waivers`), and "Probe" (`Probes`, which had no row);
  - the Plan row writes `Halts` and `Waivers` as `none`;
  - `Log:` and `Open work:` mark what a parallel agent returns rather than writes;
  - `Preflight`: the agent writes the whole line;
  - `Errored queries`: Orient writes it, `none` if none, and later dispatches add to it;
  - Open work's `Clusters not yet reviewed`: the "Write the clusters" row;
  - the user's review: taken before `Ended`, or recorded in the next pass's entry;
  - the coreset blocks: `docs/dispatch.md` now lists them among the main session's writes.
- `S12` — fixed, Phase 3: a halted parallel agent returns its items under `Open work:` (`docs/process.md`, "When a pass
  ends"; `.claude/agents/survey-pass.md`).
- `S14` — fixed, Phase 3:
  - `Preflight` is "the `Preflight` line", not "the first line";
  - the coverage-test format in step 7 has `round R:` and `new clusters:`;
  - `reasoning-exhaustive` was already gone from `docs/tooling.md` (Phase 0); the roadmap's mentions are updated;
  - the legacy output's legend no longer blames Asta's index: the rows were never verified, and their full texts have
    since been fetched;
  - the Asta-corpus claim is stated once, as likely, with the one `paperId` check, and the two places that asserted it
    are hedged;
  - `H4` halts at the grid's coarsest level, 3 clusters, and treating the pool as one is the user's call;
  - `left out X` in the `Fringe` line is defined: in-scope candidates without any ID.
- `S15` — fixed, `4d8e9a2` and Phase 3. A known section at the wrong heading level gets its own message. A prose bullet
  in `Coreset Spec` still fails: a top-level bullet in neither form is more likely a mistyped target than prose, so
  prose belongs in paragraphs or nested bullets. `docs/formats.md` now opens the input section with a skeleton input
  (verified to parse, filled in, on a scratch topic) and a list of every rule the parser applies. Each input section is
  its own heading, which also serves `W4`.

## W — how the docs are wired

- `W1` — fixed, Phase 3. The `CLAUDE.md` index gives `docs/dispatch.md` to `survey-pass` too, for its own brief.
- `W2` — fixed, Phase 3. The three pointers into the roadmap are gone:
  - "most clusters fail to match" has an interim rule: name the unmatched clusters afresh, say so in the rationale, and
    raise it at the cluster review;
  - `docs/gates.md` says that nothing measures the judgements' accuracy yet;
  - the third, in `docs/formats.md`, went in Phase 1 (`532e697`).
- `W3` — step 1 done, Phase 3. Each brief in `docs/dispatch.md` has a `Read` list of spec sections, checked by script:
  all 65 names resolve to headings. Every agent also reads "When a pass ends". `.claude/agents/survey-pass.md` says to
  read those sections only, and how to find one by Grep. `docs/coresets.md` is now for the main session only, and the
  rationale in `docs/process.md` ("Clustering method") is on no agent's list except the parts naming and fringe
  selection need. Step 2, trimming further once spec reading is measured, is after the run. Watch: see above.
- `W4` — fixed, Phase 3. "Recording it" and the other labels of "Clustering method", "Sizing", "Outcomes", each input
  section, and "The coverage sheet" are headings now.

## A — the docs as instructions for agents

- `A1` — fixed, Phase 3. `docs/process.md`, "Screening for scope": in, out, and borderline-is-in, each tied to the
  `Topic`, with a one-line reason that names the topic. Stopping rules for orientation and expansion, recorded in
  `Expansion`'s new `stopped:` part. Traversal depth is one step from the frontier candidates. Watch: see above.
- `A2` — fixed, Phase 3, with a small code change. A frontier paper is recent (within the recency window, else among the
  cluster's newest) and strongest: an `Orientation` frontier candidate first, then citations per month since
  publication. `tools/sheets.py` now prints that number beside each cluster's most recent papers, counted to the fetch
  date. Naming writes each `high` cluster's central claim as the second sentence of its `definition`. A new column was
  considered and rejected, since it would change the Clusters table's checks for no gain. Dissent is defined against
  that sentence, with two named non-cases.
- `A3` — fixed: the rubric in Phase 3, the tool in Phase 4. What counts as a change (a claim added, removed or reversed;
  not an added citation or a refinement), the evidence level (abstracts, snippets for doubt), and the service for the
  fresh recency query (WebSearch, as in step 1) are stated. `tools/coverage.py` draws the sample with a recorded seed
  and writes `coverage-<R>.md`; the agent records verdicts with `coverage.py judge`, adding recency candidates with
  `--recency`; `coverage.py line` prints the `Coverage test` line, so K and N are counted by script. A new requirement,
  `g5.coverage-sheets`, checks each round's line against its sheet: every candidate judged, N the sheet's rows, K's IDs
  its `changes` rows, a proposed cluster not reported as `none`. Four faults test it.
- `A4` — fixed, Phase 3. Step 3 has explicit rows for a targeted expansion, once per region, and for fetching with
  `pool.py` and reclustering. A rerun after naming is followed by `remap`, on any pass. `H7` is reached only after the
  targeted expansion Naming triggers. Papers from step 3's expansions are not late papers.
- `A5` — fixed, Phase 3. `Orientation` carries `themes:` and `seeds from the input:`, before `frontier candidates:`,
  since `check.py` reads candidates to the end of the line.
- `A6` — fixed, Phase 3. Orient writes `Errored queries` and Open work; a frontier candidate that cannot enter the pool
  goes to Open work rather than the list; the input's seeds have their slot, and Expand traverses forward from them.
- `A7` — fixed. The provisional-clustering half went with `Z7`. Phase 3: the Plan row's done-when now runs
  `check.py --status` before the new entry is written, since the entry fails `g0.preflight` until Preflight writes.
- `A8` — fixed in the docs, Phase 3. Step 6 reads the Clusters and Coreset sections by line offset, and checks each
  claim against its rows and evidence files, which are local reads; a doubtful row goes back to Verification. The
  section printer (`T6`) and the faithfulness check (`T2`) are Phase 4.
- `A9` — fixed, `46d9dfd` and `f99ec2c`. Missing surveys, sections, `pool.json`, `fringe.json` and sheets now give a
  message that says what to run first. An unreadable PDF counts as not fetched.

## T — tool work

- `T1` — resolved by `Z2`: quotes come only from the fetched full text, which `G4` checks.
- `T2` — fixed, Phase 4. `tools/audit.py trace` draws 15 output sentences that cite a coreset paper (seeded) and writes
  `faithfulness.md`: each sentence beside its cited rows' cells and evidence quotes, once per paper. A "Judgement audit"
  agent, which wrote neither the rows nor the output, judges each `supported`, `partly` or `unsupported`
  (`docs/process.md`, "Auditing the judgements"). Departure: the audit measures and does not repair; each `unsupported`
  goes to the user, since fixing only the sampled sentences would leave the rate describing nothing.
- `T3` — fixed, Phase 4, as a standing part of every pass rather than the first run only. `tools/audit.py reverify`
  draws 10% of the full-text rows, at least five; a fresh agent fills their claim cells and dimensions from the full
  text alone (`fill`), given the paper IDs, the column definitions and the `Dimensions` line; `compare` sets each cell
  beside the survey's, and the Judgement audit agent marks it `agree`, `partly` or `differ`. `audit.py line` prints the
  `Judgement audit` line with both rates; `g5.judgement-audit` requires it, recomputes it from the sheets, and fails on
  any unjudged row. Three faults test it. Departure: the audit had said "compare cell by cell" without saying who; a
  second agent judges, since free-text cells cannot be compared by string.
- `T4` — fixed, Phase 4: `tools/coverage.py radius [--loo]` prints the coreset's radius (max, p90, mean) under the
  `combined` measure and the ten worst-covered pool papers; `--loo` prints each row's leave-one-out growth. `draw` takes
  the coverage sample from the worst-covered quarter (`A3`). Departure: distances are 1 minus the `combined` similarity,
  which is rank-based, rather than the SPECTER2 cosine distance of the audit's simulation; that keeps one measure for
  clustering and coverage and makes a distance read as a share of the pool. The radius is reported, not gated.
- `T5` — fixed, `46d9dfd`:
  - `assign.py reject` reads `id<TAB>reason` lines on stdin, all or none.
  - `fringe.py judge` reads `s2<TAB>yes|no|maybe<TAB>reason` lines, refusing the whole batch on any bad line.
- `T6` — fixed, Phase 4: `tools/check.py <topic> --print <section>[:<cluster id>]` prints one section or one cluster's
  block with its line span, checking nothing. The docs that told agents to find line offsets with `grep -n` now point to
  it (step 6, the briefs' reading note, `.claude/agents/survey-pass.md`). Three behaviours test it.
- `T8` — partial, Phase 0 (`5d18f12`) and `d600a69`:
  - Done: the baseline assertion, cleanup at exit, a unique topic per run, and the waiver no-op. Fixing the no-op
    exposed a second hidden integrity failure in the waiver case: the dropped fringe row was cited in the output. The
    case now asserts exit 0. A deliberately broken baseline returns 1, and a simulated crash leaves no files behind.
  - Counts: 48 faults and 20 behaviours after Phase 0, 49 and 21 after Phase 1 (one new each, for `snippet` evidence and
    a `snippet` source in the coreset layout).
  - Phase 2 grew the suites from 49 faults and 21 behaviours to 70 and 35. Phase 3 added two faults (`S10`, and
    `r_errored` below) and one behaviour (the halt dash): 72 and 36. Phase 4 added seven faults (`g5.coverage-sheets`,
    `g5.judgement-audit`) and eight behaviours (`--print`, a coverage round through `tools/coverage.py`): 79 and 44. The
    fixture now carries a coverage sheet and the audit sheets, written through the tools' own functions.
  - Still untested, from the audit's list: `g1.errored` without a retry outcome, the stale date in `g1.rejected`,
    `g2.diagnosis-halts` for `H5`, `g5.converged` for `H11`, history's pool removal and input-changed note, and a
    dedicated test per integrity check.
- `T9` — fixed, `cda762a`. Seeds and package versions are in `params.seeds` and `params.versions`, and the script
  headers pin numpy 2.5.3, scikit-learn 1.9.1, igraph 1.0.0, leidenalg 0.12.0 and scipy 1.18.1. `history.json` and
  `match-simulation.json` record neither.

## Z — simplifications

- `Z1` — adopted as the plan's principle "Not everything before the run". It is carried out by Phase 5.
- `Z2` — adopted, `532e697`:
  - A row's `source` is `full-text` or `abstract`; `snippet` stays valid only in legacy surveys.
  - `G4` fails evidence quoted from a snippet.
    - `docs/verification.md` was rewritten: the full text is the source, a snippet is a pointer, and snippets alone do
      not verify a row. The preflight rationale in `docs/external_services.md` now names arXiv as the verification
      dependency.
  - The fixture's verified rows quote their own synthetic full texts, one of them hyphenated across a line break.
  - The cost questions it raised became `R1`, `R2`, `R4` and `R6`. See "Watch in the first run".
- `Z3` — adopted, `532e697`. The measure is fixed to `combined`, and `--rule` is a usage error.
- `Z4` — adopted, `532e697`. One null draw, used only for `no structure`. `--nulls 0` is a usage error.
- `Z5` — adopted, `532e697`. The history is out of the pass, and `match.py history` stays as an experiment
  (`docs/experiments.md`). The `Temporal stability` log line and its `G2` requirement went with it, as did the sheet
  section and the viewer panels. Clustering runtime fell from 154.5 s to about 31 s, with identical assignments,
  clusterwise scores and fringe ranking. `graphs/reasoning-legacy/clusters.json` was regenerated in the new format, with
  `notes` and `stability_from` added and the history fields removed. The `Clustering` log line has a new format.
- `Z6` — deferred until after the run (user, 2026-10-09).
- `Z7` — adopted, `532e697`. The prerequisite held without an API call: `fringe.py` already sent `positivePaperIds`, and
  that call produced the 56 `new` candidates on record. The `new` route is seeded from the frontier candidates, plus up
  to 10 pool papers most cited within the pool. That those seeds need at least one in-pool citation was checked offline
  only. The provisional-clustering row is gone from the order of operations, and `H8` now comes at step 3.
- `Z8` — adopted, `532e697`. The experiments are in `docs/experiments.md`, indexed for human reviewers only.
- `Z9` — adopted, `532e697`. `unstable cluster` and `broad scope` are printed notes, not diagnostics.

## R — items raised after the audit

- `R1` — done, Phase 3. Step 5 has a row before verification: the main session runs
  `uv run tools/fulltext.py <topic> --abstract` once, and verification agents do not fetch. The Verification brief hands
  over the papers the batch could not fetch.

- `R2` — done, `f99ec2c`:
  `uv run tools/fulltext.py show <topic> <id> [<pattern>] [--section <name>]... [--max <tokens>]`. It prints verbatim
  lines, so its passages are quotable. Whether verification adopts it is for `R4`.

- `R3` — done, `46d9dfd`, `d600a69` and `f99ec2c`:

  - the `Pool` line reads "N papers in scope, A with an arXiv ID";
  - `check.py` prints the counts for the coreset and the pool;
  - the viewer has an "arXiv ID" colour mode and an overview count, checked in node only.

  On `reasoning-legacy`, all 195 pool papers have an arXiv ID.

- `R4` — done, Phase 4. Run as designed (user, 2026-10-10), outside the pass loop: arm `A` (strong agents, section
  reader and Grep) and arm `B` (Haiku locators mapping each whole paper, then strong agents reading the mapped places)
  on all 27 `abstract`-sourced rows of `reasoning-legacy`; arm `C`, the main session reading 8 whole papers, recorded
  before any `A` or `B` output was opened. Result: `A` found 90% of `C`'s findings at about 26k tokens per row; `B`
  found 84% at about 35k Haiku plus 27k strong tokens per row; `A` beat `B` on 7 of 8 papers. The Haiku maps had wrong
  line numbers (3 of 8), passages from another paper in the batch (1), and an invented limitation (1). Decision:
  verification reads with the section reader alone; a step to read the appendix sections a result turns on was added,
  since most of `A`'s misses were there. Departures: a spend limit stopped five agents mid-run, so the missing papers
  were rerun, and some token counts are unknown; the rerun prompt for `B` added that map line numbers may be off.
  Scoring was by the main session, not blind. Records: `graphs/reasoning-legacy/r4/` (`README.md`, `tokens.md`,
  `compare.md`) and `docs/experiments.md`. The 27 rows' results were not written back into `reasoning-legacy`, which
  Phase 5 reruns.

- `R5` — parked (user, 2026-10-10). Supporting papers without arXiv is likely overengineering for now; a snippet backup
  would be a nice reserve. Build it only if `R3` shows a topic where such papers are a real share of the coreset.

## P — issues found during remediation

All in the commit after `920b823`, "Remediation phase 3: a second tabletop". These fixes have not been tabletopped.

The second tabletop's findings clustered on one path, the recluster at step 7, where the first round's fixes had added
three rows (rename, move rows, a step-7 targeted expansion) that collided with other rules. Rather than patch them a
third time, the step-7 recluster now returns the pass to step 3: `docs/process.md`, "Returning to step 3". The three
rows are gone, and the step-3 and step-4 rows serve both cases (user's decision, 2026-10-10). That settles `P6` and
`P7`, and most of `P8`, by construction.

- `P1` — fixed, as first suggested: `Coreset` is refreshed after a dispatch only once step 5's row has written it.
  `inferred()` was left as it is.
- `P2` — fixed, as suggested: Revise runs on a converging round too, and "End the round" requires every counted paper to
  be an assigned coreset row.
- `P3` — fixed, as suggested. Selection returns out-of-pool dissent papers under `For the pool:`; the main session adds
  and assigns them, and dispatches Selection again. A paper computed into another cluster may make a `bridge`, not this
  cluster's dissent.
- `P4` — fixed, as suggested: the Cluster review row sits before `G2`, and says the rows up to the viewer run while the
  halt is pending.
- `P5` — fixed, as suggested, in the Naming row and brief.
- `P6` — fixed by the return to step 3: while the pass has returned to step 3, "After every dispatch" fetches with
  `pool.py`, as before step 3. `late` runs only in the Late papers row, and when it does, "After every dispatch" writes
  its `Late papers` line. A recluster's line is written by hand, in the stated form.
- `P7` — fixed by the return to step 3: rows are moved by step 4's "Set up the coreset blocks", now also a `survey-edit`
  job on a return, and one exemption, "the return's open work", lists rows in another block and `bridge:` cells naming a
  retired cluster. Retargeting a bridge is left to Selection, since it is a judgement.
- `P8` — fixed. A counted paper whose matching role cannot be had (its cluster states no central claim, or the `fringe`
  quota is full) takes `frontier`, and says what it changed. Selection's Revise hand-over gives each counted paper, its
  change and its proposed role.
- `P9` — fixed, as suggested. The proposed form carries a bracketed clause after the values, which the parser already
  ignores; checked. Selection, Bridges, Fringe selection and Verification are handed the `Dimensions` line.
- `P10` — fixed, as suggested.
- `P11` — fixed in the docs: the bracket holds the count only, and a note goes in a part of its own. The pattern was not
  relaxed.
- `P12` — fixed: forward from the seeds and the frontier candidates, in the prose and the bullet.
- `P13` — fixed, as suggested.
- `P14` — fixed: the plan report does not block; the user can stop the pass, or change the dimensions in the input.
- `P15`–`P35` — open, found by Phase 4's simulation (defined above). Not fixed, pending the user's decision: fix them
  and simulate again, or leave them to the first run, as Phase 3's third tabletop was. Three (`P24`, `P29`, `P30`) are
  the third tabletop's findings recurring.

## Pending

- Phase 4's simulation findings, `P15`–`P35`: fix and simulate again, or leave to the first run (the user's call).
- Phase 5: `R6`, and `Z1` in practice.
- After the run: `Z6`, `C7`, `M7`, `M8`, `S8`, `S13`, `T7`, `W3` step 2, `M20`'s hidden route, `R5`, and the rest of
  `T8`.

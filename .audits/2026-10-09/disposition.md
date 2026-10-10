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

### `P` — Phase 3's tabletop

Phase 3's done-when was a fresh tabletop of a first pass, by an agent blind to `.audits/`, the roadmap and git history,
playing the main session and each brief from the docs alone. It ran on 2026-10-10, at about 220k tokens. It met none of
the stalls the audit's own tabletop had found, and found these 20 new ones, mostly on paths Phase 3 had just written.
Tags: `blocker` (cannot proceed, or certainly fails a gate), `guess` (must improvise, so two agents would differ),
`minor` (wording or findability); `fails open` marks a check that passes when it should fail.

- `P1` — `blocker`. After a recluster at step 7, coreset rows sit in the blocks of clusters they no longer belong to,
  and `check.py` fails; no row of the order of operations moves them. A moved `dissent` row then fails
  `g3.dissent-searched`, and its quote answers the wrong cluster's claim; the block it left can lose its anchor. `remap`
  says to "retire, merge or rename" unmatched clusters, which no doc defines. Confirmed on a scratch fixture. Suggested:
  a row after the recluster in which `survey-edit` moves rows to their computed blocks, then Selection re-checks the
  roles of moved and orphaned rows, dissent included; define retirement.
- `P2` — `blocker`. After any recluster once names exist, Naming's done-when ("`check.py` passes") cannot be met: the
  pool's cluster cells differ from the new assignment until `assign.py clusters`, the next row, runs. At step 7 the
  safety net also requires `G3` for the new cluster before its selection has run. A literal rule-follower halts (`H9`).
  Confirmed on a scratch fixture. Suggested: run `assign.py clusters` straight after Naming; exempt a newly named
  cluster from `G3` and `G4` until its Revise rows run.
- `P3` — `blocker`, `fails open`. `halts()` in `tools/gates.py` took the decision from the first `—` after the halt ID,
  so `H2 — query "prm survey" — 429 after 3 retries — pending` read as decided, and `--gate` passed. Confirmed by
  running it. Suggested: take the text after the entry's last `—` as the decision.
- `P4` — `guess`. Once a `Coverage test` line exists, `G4` is required, so Revise's first new rows make the `Coreset`
  line's count stale, and new `abstract` rows can push the share over 20% (`g4.h10`) before verification; only main
  rewrites `Coreset`. The `h10` part is read from code, not run. Suggested: refresh `Coreset` after every dispatch;
  apply `g4.h10` only at the `--gate G4` row.
- `P5` — `guess`. Step 3's targeted expansion runs before `sheets.py`, so the Expand agent gets only `cluster.py`'s
  printout for the region; its done-when ("as the Expand row") has no meaning for a region. Suggested: write the sheets
  first, hand over the cluster's naming-sheet section, and give a regional done-when.
- `P6` — `guess`. After the rerun, a thin cluster cannot be told to be the same region or a new one: `cluster.py`
  matches clusterings only once names exist, and renumbers clusters by size, so the computed id in `Expansion` is
  reused. Suggested: always match against the previous `clusters.json`, named or not.
- `P7` — `guess`. "Frontier candidate" is undefined, yet the list sets `G1`'s traversal requirement, the fringe `new`
  route's seeds, and step 4's frontier priority; one agent lists 8, another 25. Suggested: define it, for example "in
  scope and within the recency window, or named by the field as current".
- `P8` — `guess`. Step 2 says to traverse forward "from anchors", which are only chosen at step 4. Suggested: "from the
  seeds and frontier candidates".
- `P9` — `guess`. The frontier's impact criterion cannot be applied from the naming sheet: it shows only the three
  newest papers per cluster, which on `reasoning-legacy` all read 0.0 citations per month. Suggested: list every paper
  in the window by citations per month.
- `P10` — `guess`. "Uncheckable: say so in the row" has no cell to go in, and an extra column fails
  `g3.dimension-columns`. Suggested: name the cell.
- `P11` — `guess`. Step 5's replacement Selection cannot know which papers are fetchable: it may not fetch, and the
  full-text section is not on its reading list. Suggested: main pre-fetches the candidates, or the brief states a proxy.
- `P12` — `guess`. "After every dispatch" runs `assign.py late` after a coverage round, but the proposed-cluster path
  wants the expansion first and at most one recluster per round; `late` can return `RECLUSTER:` and make it two. On the
  recluster path, nothing prints a `Late papers` line. Suggested: after a round that proposes a cluster, fetch with
  `pool.py` only and defer `late`.
- `P13` — `guess`. Every candidate counted in a coverage round must become an assigned coreset row, but its role is
  unstated; a `new cluster` verdict is not said to count, or not, in K; and a recency find Semantic Scholar does not
  know cannot enter the pool at all. Suggested: state the role, the K rule, and the unknown-paper case.
- `P14` — `guess`. The coverage sample has no drawing procedure: the agent hand-picks, while the stated bound assumes a
  random draw. Suggested: a script that draws by the stated weights, with a seed.
- `P15` — `guess`. `no structure` said to halt "with the coarsest level, 3 clusters", but `cluster.py` still chooses its
  level by `τ`; getting 3 takes `--level 3`, logged as a user override. Suggested: have `cluster.py` choose the coarsest
  level on `no structure`.
- `P16` — `minor`. `Dissent searches` parsing drops an entry with a `;` inside "what was searched", or `→` for `->`, and
  then reports it missing. Confirmed by running it. Suggested: state both constraints in `docs/formats.md`.
- `P17` — `minor`, `fails open`. `r_errored` read the line as clean whenever it began with `none`, so entries appended
  after Orient's `none` skipped the `H2` check. Read from code. Suggested: say "replace `none`", or parse the entries
  regardless.
- `P18` — `minor`. An empty `method name` fails `g3.cells`, but the doc says only "if the paper introduces one"; and
  proposed dimensions have no guidance to include `n/a`. Suggested: say "write `n/a`", and allow it among proposed
  values.
- `P19` — `minor`. A bridge row must sit in the block of the cluster its paper was computed into, one of the two; that
  rule was only in `docs/tooling.md`, which the Bridges brief does not list. Suggested: one sentence at step 4.
- `P20` — `minor`. The `G5` row adds to `Gates` after `Ended` is written, against "a line may be updated until the pass
  ends, never after". Suggested: run `G5` before `Ended`, or exempt `Gates`.

## By phase

| phase | commits | IDs handled |
| -- | -- | -- |
| 0 | `5d18f12` | the rename to `reasoning-legacy`; `T8` in part |
| 1 | `532e697` | `Z2`–`Z5`, `Z7`–`Z9`, `M13`; moot with them: `M9`, `M10`, `T1`, `S3`, half of `A7`, the history half of `M20` |
| 2 | `d600a69`, `4d8e9a2`, `46d9dfd`, `4dc8dff`, `cda762a`, `f99ec2c`, `c43ba0c` | `C1`–`C6`, `C8`, `C9`, `M1`–`M6`, `M11`, `M12`, `M14`–`M19`, `S6`, `A9`, `T5`, `T9`, `R2`, `R3`; the code side of `C10`, `M20`, `S1`, `S2`, `S4`, `S15`; `T8` in part |
| 3 | `558e816` | `W1`–`W4`, `S5`, `S7`, `S9`–`S12`, `S14`, `A1`–`A8`, `R1`, `P1`–`P20`; the doc side of `C10`, `S1`, `S2`, `S4`, `S15`; the code side of `S10` and `A2`; `T8` in part |
| 4 | pending | `T2`, `T3`, `T4`, `T6`, `R4`, the tool half of `A3`, `P14` |
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
| 3 | `558e816` | the spec pass over `docs/`, `CLAUDE.md` and the agents; `S10`'s gate change; `A2`'s sheet column; the tabletop's fixes (`P1`–`P20`) |

## Watch in the first run

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

- `Z2`, the cost of verifying from full text. The estimate is the same order of tokens per row as snippet-based
  verification, possibly somewhat higher. It is `UNVERIFIED`: the ~10k-per-row baseline comes from snippet-based passes,
  and no row has yet been verified from a fetched full text. `R6` measures it. The reasoning: the paper lands on disk at
  no token cost, and the agent reads only Grep hits and a few sections, which cost about what a `snippet_search` call
  returned (about 700 tokens per call, two or more calls per row). The risks to check, in order:

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

- `Z2`, what targeted reading misses. Verification has two jobs. Confirming the claims a draft already makes suits Grep,
  since the agent knows what to look for. Catching what the draft left out (an author-stated limitation, a condition on
  a result, a dissent paper that in fact agrees) does not, since Grep finds only what the agent already suspects. The
  expectation is high recall on the first job and lower on the second, `UNVERIFIED` until `R4` measures it. Until then,
  read rows for missing caveats more sceptically than for wrong numbers.

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

- `A3`, the coverage sheet. Until Phase 4's tool writes it, the Coverage agent writes `coverage-<R>.md` itself, and no
  gate checks it. Check that the first run's sheets have a row for every sampled candidate.

- `S11`, the user's cluster review. It is now taken before `Ended`, when the output is shown; a review after `Ended`
  goes into the next pass's entry. If users routinely review later, the `Clusters` line of a finished pass will always
  read "not yet reviewed".

- `R2`, the section reader (`fulltext.py show`): its PDF heading detection is a guess. Letter-prefixed headings such as
  "B Additional results" are not detected. Whether verification uses it at all is for `R4` to decide.

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
  fetch any added pool rows (`pool.py` until step 3 is done, `late` after it), paste `Pool`, then check. Selection and
  the other row-adding agents list their new rows under `Rows needing verification`, so a Revise round no longer trips
  `g4.abstract-listed`. One wrinkle remains: during step 3's targeted-expansion loop, this pass's `clusters.json`
  exists, so `check.py` suggests `late`, while the procedure says `pool.py` (the rerun clusters the papers). Both
  satisfy the gate; the row says which to run.
- `S3` — moot with `Z7`.
- `S4` — fixed, `d600a69` and Phase 3. The code already accepted `new clusters: none (proposed <x>, not formed)` as
  converged, and behaviour case 6i pins it. Step 7 now has a targeted-expansion row for each proposed cluster, and the
  Late papers row reclusters after it even below 10%. The main session records the outcome from the `changes:` line:
  formed, or `none (proposed <x>, not formed)`.
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
- `A3` — rubric half fixed, Phase 3. What counts as a change (a claim added, removed or reversed; not an added citation
  or a refinement), the evidence level (abstracts, snippets for doubt), and the service for the fresh recency query
  (WebSearch, as in step 1) are stated. Every sampled candidate is recorded in `coverage-<R>.md`, written for now by the
  Coverage agent; the tool that draws the sample and writes the sheet is Phase 4.
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
- `T5` — fixed, `46d9dfd`:
  - `assign.py reject` reads `id<TAB>reason` lines on stdin, all or none.
  - `fringe.py judge` reads `s2<TAB>yes|no|maybe<TAB>reason` lines, refusing the whole batch on any bad line.
- `T8` — partial, Phase 0 (`5d18f12`) and `d600a69`:
  - Done: the baseline assertion, cleanup at exit, a unique topic per run, and the waiver no-op. Fixing the no-op
    exposed a second hidden integrity failure in the waiver case: the dropped fringe row was cited in the output. The
    case now asserts exit 0. A deliberately broken baseline returns 1, and a simulated crash leaves no files behind.
  - Counts: 48 faults and 20 behaviours after Phase 0, 49 and 21 after Phase 1 (one new each, for `snippet` evidence and
    a `snippet` source in the coreset layout).
  - Phase 2 grew the suites from 49 faults and 21 behaviours to 70 and 35. Phase 3 added two faults (`S10`, and
    `r_errored` below) and one behaviour (the halt dash): 72 and 36.
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

- `R4` — pending, Phase 4. Settled so far (user, 2026-10-10): it runs outside the pass loop, with the main session as
  orchestrator. The main session dispatches cheap-model locators and strong agents, and does the reference reading (arm
  `C`) itself. It records arm `C`'s findings before reading arms `A` and `B`, so that their maps cannot shape what it
  notices. The design is in the plan.

- `R5` — parked (user, 2026-10-10). Supporting papers without arXiv is likely overengineering for now; a snippet backup
  would be a nice reserve. Build it only if `R3` shows a topic where such papers are a real share of the coreset.

## P — issues found during remediation

All in `558e816`, unless said otherwise. The fixes were not tabletopped again.

- `P1` — fixed, as suggested. Step 7 has a "Rename after a recluster" row (Naming settles every cluster `remap` did not
  match) and a "Move the coreset rows" row (`assign.py clusters`, then `survey-edit` for rows in the wrong block). "Late
  papers" defines rename, merge and retire: retiring removes a Clusters row, and its block once emptied, and no paper.
  Revise re-selects for every cluster whose rows changed, and keeps a moved dissent row only if it contradicts its new
  cluster's claim.
- `P2` — fixed, partly as suggested. "After every dispatch" runs `assign.py clusters` after Naming, before the check.
  For Revise, no code exemption: a rule says a Revise round's own open work (a new cluster's roles and dissent search,
  rows not yet verified, the `abstract` share) is not `H9`, and Revise is done when the check passes again. Why not
  exempt in code: a gate that relaxes itself mid-round is the kind of hole the audit closed elsewhere. Watch: whether
  the main session can tell open work from a real failure.
- `P3` — fixed, as suggested, in `tools/gates.py`: entries are split on `; H<n> —`, and the decision is what follows the
  entry's last `—`. Verified: behaviour case 2b.
- `P4` — fixed in part. `Coreset` is refreshed in "After every dispatch" whenever the coreset changed. `g4.h10` was left
  as it is: the Revise rule of `P2` covers a share over 20% while rows await verification.
- `P5` — fixed, as suggested: the targeted-expansion row writes the sheets first, hands over the region's section of
  `naming-sheet.md`, and has a regional done-when (backward traversal from the region's most-cited papers, and a search
  on its theme, under the stopping rule).
- `P6` — fixed in the docs, not as suggested. A region is named by one of its papers, in `Expansion` and when judging a
  thin cluster after the rerun: it is the same region if it holds that paper. Matching unnamed clusterings in
  `cluster.py` would also work, but the paper rule is enough for a once-per-region loop.
- `P7` — fixed, close to the suggestion: in scope, and within the recency window or named as current by the sources
  orientation reads. An older find is a pool paper.
- `P8` — fixed, as suggested; step 4 repeats forward traversal from each anchor.
- `P9` — fixed, with code. `tools/sheets.py` lists each cluster's papers from the last 12 months, top 5 by citations per
  month, counted to the fetch date. "Recent" for the frontier role is now the last 12 months rather than the recency
  window, so the sheet and the rule agree.
- `P10` — fixed: an uncheckable row's `selected because` ends `(uncheckable: <why>)`.
- `P11` — fixed by the proxy: the replacement search prefers papers with an arXiv ID, and the next batch fetch settles
  it.
- `P12` — fixed, as suggested. After a round that proposes a cluster, `pool.py` alone fetches the new rows, and the Late
  papers row reclusters after the expansion. On the recluster path the main session writes `Late papers` in a stated
  form, from `cluster.py`'s `changes:` line.
- `P13` — fixed. A candidate counted in K takes the role that matches its change (dissent, frontier, bridge, or fringe
  within the quota), even above the sizing minimum; a `new cluster` verdict goes under `new clusters:`, not in K; an
  unknown paper is redrawn and noted in Open work.
- `P14` — deferred to Phase 4 (`T4`, the scripted draw). Until then, `docs/process.md` marks the bounds as indicative.
- `P15` — fixed in the docs, not as suggested: `H4` halts at the level `cluster.py` chose, and a coarser level, or one
  cluster, is the user's call. Changing `cluster.py` would have fixed the level by rule where the user decides anyway.
- `P16` — fixed, as suggested, in `docs/formats.md`.
- `P17` — fixed both ways: the doc says the first entry replaces `none`, and `r_errored` reads entries before looking
  for `none`. Verified: a second `g1.errored` fault.
- `P18` — fixed, as suggested.
- `P19` — fixed, as suggested, at step 4's `bridge`.
- `P20` — fixed by the exemption: `Gates` takes `G5` after `Ended`, since `G5` checks `Ended`.

## Pending

- Phase 4: `T2`, `T3`, `T4`, `T6`, `R4`, the tool half of `A3`, and `P14`.
- Phase 5: `R6`, and `Z1` in practice.
- After the run: `Z6`, `C7`, `M7`, `M8`, `S8`, `S13`, `T7`, `W3` step 2, `M20`'s hidden route, `R5`, and the rest of
  `T8`.

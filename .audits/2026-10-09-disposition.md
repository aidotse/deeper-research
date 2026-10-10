# Disposition of the audit of 2026-10-09

What happened to each finding of `.audits/2026-10-09-docs-full-spec.md`, by ID. The plan,
`.audits/2026-10-09-remediation-plan.md`, says what is done in what order. This file says what was actually done, and it
is the place to look when auditing a run.

Each entry gives:

- `outcome` — fixed, adopted, moot, partial, deferred, or pending (with its phase);
- `commit` — where the change landed;
- what was done, where it departs from the audit's remediation, and why;
- how it was verified;
- what to watch in a real run.

Update it as each phase lands. An ID not yet handled is listed only under "Pending", with its phase.

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
  - The defaults are written to `params.defaults`. The doc side is Phase 3.

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

- `S1` — fixed in code, `d600a69`. Without declared dimensions, `check.py` reads the proposed ones from the current
  entry's `Dimensions` line, and checks values, columns and evidence against them, as for declared ones. Each needs at
  least two values. `g3.dimension-columns` now also applies to declared dimensions: no extra column, and none missing.
  Verified: faults for a malformed and a one-value proposal, and behaviour case 6j. The doc side is Phase 3.
- `S2` — partial. The `check.py` messages name `pool.py` or `assign.py late` and say to paste the `Pool` line
  (`d600a69`). The procedure is Phase 3.
- `S3` — moot with `Z7`.
- `S4` — partial. The code already accepted `new clusters: none (proposed <x>, not formed)` as converged, and behaviour
  case 6i now pins it. The step-7 rows are Phase 3.
- `S6` — fixed, `d600a69`. `; rejected: none` at the end of `Expansion` replaces `rejected.md`. Verified: behaviour case
  6h.
- `S10` — mostly resolved by `Z2`. The rest is Phase 3.
- `S15` — partial, `4d8e9a2`. A known section at the wrong heading level gets its own message. A prose bullet in
  `Coreset Spec` still fails: a top-level bullet in neither form is more likely a mistyped target than prose, so prose
  belongs in paragraphs or nested bullets. The skeleton input is Phase 3.

## A — the docs as instructions for agents

- `A7` — the half about the provisional clustering is moot with `Z7`. The rest is Phase 3.
- `A9` — fixed, `46d9dfd` and `f99ec2c`. Missing surveys, sections, `pool.json`, `fringe.json` and sheets now give a
  message that says what to run first. An unreadable PDF counts as not fetched.

## T — tool work

- `T1` — resolved by `Z2`: quotes come only from the fetched full text, which `G4` checks.
- `T5` — fixed, `46d9dfd`:
  - `assign.py reject` reads `id<TAB>reason` lines on stdin, all or none.
  - `fringe.py judge` reads `s2<TAB>yes|no|maybe<TAB>reason` lines, refusing the whole batch on any bad line.
- `T8` — partial, Phase 0 (`5d18f12`) and `d600a69`:
  - Done: the baseline assertion, cleanup at exit, a unique topic per run, and the waiver no-op.
  - Phase 2 grew the suites from 49 faults and 21 behaviours to 70 and 35.
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
  - The cost questions it raised became `R1`, `R2`, `R4` and `R6`.
- `Z3` — adopted, `532e697`. The measure is fixed to `combined`, and `--rule` is a usage error.
- `Z4` — adopted, `532e697`. One null draw, used only for `no structure`. `--nulls 0` is a usage error.
- `Z5` — adopted, `532e697`. The history is out of the pass, and `match.py history` stays as an experiment
  (`docs/experiments.md`). Clustering runtime fell from 154.5 s to about 31 s, with identical assignments.
- `Z6` — deferred until after the run (user, 2026-10-09).
- `Z7` — adopted, `532e697`. The prerequisite held without an API call: `fringe.py` already sent `positivePaperIds`, and
  that call produced the 56 `new` candidates on record. The `new` route is seeded from the frontier candidates, plus up
  to 10 pool papers most cited within the pool. That those seeds need at least one in-pool citation was checked offline
  only.
- `Z8` — adopted, `532e697`. The experiments are in `docs/experiments.md`, indexed for human reviewers only.
- `Z9` — adopted, `532e697`. `unstable cluster` and `broad scope` are printed notes, not diagnostics.

## R — items raised after the audit

- `R2` — done, `f99ec2c`:
  `uv run tools/fulltext.py show <topic> <id> [<pattern>] [--section <name>]... [--max <tokens>]`. It prints verbatim
  lines, so its passages are quotable. Whether verification adopts it is for `R4`.

- `R3` — done, `46d9dfd`, `d600a69` and `f99ec2c`:

  - the `Pool` line reads "N papers in scope, A with an arXiv ID";
  - `check.py` prints the counts for the coreset and the pool;
  - the viewer has an "arXiv ID" colour mode and an overview count, checked in node only.

  On `reasoning-legacy`, all 195 pool papers have an arXiv ID.

## Pending

- Phase 3: `W1`–`W4`, `S2` (the procedure), `S4` (the rows), `S5`, `S7`, `S9`, `S10`, `S11`, `S12`, `S14`, `S15` (the
  skeleton), `A1`–`A8`, the doc side of `S1` and `C10`, `R1`, and the doc changes listed in the plan's Phase 3.
- Phase 4: `T2`, `T3`, `T4`, `T6`, `R4`.
- Phase 5: `R6`, and `Z1` in practice.
- After the run: `Z6`, `C7`, `M7`, `M8`, `S8`, `S13`, `T7`, `W3` step 2, `M20`'s hidden route, `R5`, and the rest of
  `T8`.

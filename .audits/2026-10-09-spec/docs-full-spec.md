# Audit: the full spec, blind (2026-10-09)

## How to read this document

This is a blind audit of the whole spec and code, written on 2026-10-09. It lists issues only; it does not plan or
decide. What is done about each issue, and in what order, is in `.audits/2026-10-09/remediation-plan.md`; what was
actually done is in `.audits/2026-10-09/disposition.md`. The procedure is `docs/audits.md`.

The sections, in order:

- "Scope and method": what was read, how, and the status values each issue carries.
- "Executive summary, in the manner of a reviewer": the short version, for a reader new to the repo.
- "Part (a)": whether the development direction is right.
- "Part (b)": the issues, by dimension: `C`, `M`, `S`, `W`, `A`, `T` and `Z`. Each issue has an ID, its evidence, why it
  matters, a suggested remediation, an effort and a status. Issues marked `(V)` bear on verification.
- "The verification concept, in one place": the `(V)` issues, link by link.
- "Part (c)": what had to be fixed before the first end-to-end run, and how to run it.
- "Checked and found to hold", and an appendix.

Line numbers refer to the files as they stood on 2026-10-09, and many have since moved.

## Scope and method

This audit is blind to earlier ones. It did not read `.audits/`, `docs/roadmap.md` or any git history (log, diff, blame,
show). Its scope was every other file in `docs/`, `CLAUDE.md`, `.claude/agents/*.md`, `.claude/settings.json`, all of
`tools/` (the docstring only for `tools/recursive.py`), and `tests/`. Claims were checked against the docs, the code,
and the data in `graphs/reasoning/`, `surveys/reasoning.md`, `outputs/reasoning.md` and `inputs/reasoning.md`.

The work was split five ways. The main session read every spec file and checked the verification chain against the data.
Four parallel agents, each under the same blindness rules, audited: the gates (`tools/check.py`, `tools/gates.py`,
`tests/gates/`); the clustering stack (`tools/cluster.py`, `match.py`, `fringe.py`, `sheets.py`, the clustering parts of
`assign.py`); the pipeline scripts (`assign.py`, `pool.py`, `inputs.py`, `bib.py`, `fulltext.py`, `preflight.py`,
`net.py`, `asta_config.py`, `graph.py`, `settings.json`); and a tabletop run of a first pass, playing the main session
and each `survey-pass` brief from the docs alone. Simulations ran on scratch topics (`zz-audit-*`), all removed
afterwards; `graphs/reasoning/` was left unchanged. One Asta call was made (`get_paper`, to test a claim in
`docs/external_services.md`). No other outside service was called, apart from a handful of Graph API and arXiv fetches
by the scripts under test.

Status values used below:

- `verified against code` — read in the code, with file and line.
- `verified against data` — measured on the committed data in `graphs/reasoning/` or the survey.
- `verified by simulation` — reproduced by running the tools on a scratch topic, or by a computation stated with it.
- `verified against docs` — a contradiction or gap visible in the docs themselves.
- `likely` — reasoned from the code or docs but not reproduced.

Line numbers refer to the files as they stood on 2026-10-09.

## Executive summary, in the manner of a reviewer

**What the repo proposes.** The repo is a harness that lets LLM agents produce literature surveys that a researcher can
trust and navigate. Its central idea is the *coreset*: rather than collecting everything a citation crawl reaches, the
harness builds a broad, cheap *pool* of in-scope papers (metadata only), computes a map of the pool's themes, and then
selects a small set of papers, a few per theme, each playing an explicit role. The roles are anchor, frontier, dissent,
bridge and fringe. Every selected paper is then verified against the paper's own body text, with the verbatim evidence
recorded. The final analysis (`outputs/<topic>.md`) may cite only verified coreset papers, and it marks anything resting
on an abstract alone.

**Claimed contributions.**

1. `Job-based retrieval.` Web search for the current frontier, a scholarly index (Asta) for backward and forward
   traversal and for dissent, and two scripted *fringe* routes for overlooked work. The insight is that each source has
   a characteristic bias, and that mixing them by job counters those biases.
2. `A computed, stability-tested map.` Clusters come from embeddings and bibliographic coupling, not from the model's
   opinion. The level of detail is chosen by measured stability under resampling and time holdouts, against a null
   model. This makes the map reproducible and auditable rather than an artefact of one run.
3. `Role-based selection.` Selection is by role, against the consensus bias of ranking by citations. In particular a
   deliberate dissent search per important cluster, and a fringe role for points the rest of the pool covers badly.
4. `Claim-level verification with provenance.` Each claim is checked to "publication grade" against body text, with
   quotes recorded. The output carries an `[abstract-only]` marker wherever that failed.
5. `Process integrity by script.` Six gates and a history check confirm, from the files alone, that every judgement left
   a trace: rejections recorded, dissent searched and quoted, evidence filed, halts decided by the user.
6. `An explicit stopping rule.` A sampled coverage test stands in for "sufficiency": stop when adding pool papers stops
   changing the output's targets.

**The value-add over a commercial "deep research" product.** It is mainly epistemic hygiene: traceable provenance per
claim, reproducible structure, a stopping rule that is stated rather than implicit, and a principled refusal to make
absence claims or field statistics from a coverage-selected sample. `docs/coresets.md` is unusually honest about that
last point. For a researcher who will act on the output, as with the `reasoning` input (a PhD student choosing
directions), that hygiene is the product.

**Strengths.**

- The framing is clear and self-critical. `docs/coresets.md` states its own open questions, and the spec forbids
  presenting inferred detail as retrieved.
- The scripted parts are solid. They are deterministic: a default rerun reproduced the committed `clusters.json`
  exactly. They are also network-robust, and the gate test suites pass (48 of 48 injected faults, 20 of 20 behaviours).
- The existing legacy output traces its claims to survey rows faithfully, in the main session's spot checks.

**Weaknesses.**

- `Never run end to end.` The pipeline as specified has never produced a survey in the coreset layout. The only survey,
  `reasoning`, is in the legacy layout, and `tools/check.py` skips all cluster, role, pool and gate checks on it. Every
  gate has been exercised only on a synthetic fixture.
- `Sufficiency is asserted, not measured.` The central claim is borrowed by analogy from k-center covering, yet no tool
  computes a covering quantity. Sufficiency rests on a 10–15 candidate sample judged by an LLM. That sample is
  consistent with up to 18–39% of unsampled papers changing the output when it "converges". Minimality is not tested at
  all.
- `The verification gate checks the form of the evidence, not its truth.` The default source, `snippet`, leaves quotes
  nothing can check afterwards. Full-text quote matching accepts empty and one-word quotes. Nothing checks that a quote
  supports its cell, or that an output sentence matches its row.
- `Engineering effort is unevenly spread.` The clustering-stability machinery is elaborate. Three measures, a null
  model, temporal history and match simulation changed no decision on the one real pool. Meanwhile the weakest links in
  the quality chain are judgement steps with no rubric: scope screening, dissent, the coverage-test verdict.
- `The process is heavy for LLM agents to follow from prose.` The spec is about 190 KB. The checklist has 37 rows, 6
  gates and 13 halt conditions. The tabletop simulation found 22 places where a rule-following agent would stall, guess,
  or trip a gate.

**Verdict.** The direction is right at the level of the idea. The coreset-with-verification design is the
differentiating contribution, and it is worth finishing. The architecture is over-built in the clustering and
gate-bookkeeping layers, and under-built where the quality claim actually lives: measured verification accuracy, a
measured coverage quantity, and rubrics for the judgement calls. The most valuable next step is not more machinery. It
is a small end-to-end run after a short list of blocking fixes (see "Readiness for the first end-to-end run"), letting
the failures that run exposes set the agenda.

## Part (a): is the development direction right?

### What is load-bearing

- `Pool versus coreset, roles, verification against body text, the output's provenance marker.` These are the product.
  Keep them.
- `One computed clustering with a stability check, plus late assignment and remap.` These make the map reproducible and
  let a pass grow incrementally. Keep them.
- `Gates as records of judgement.` The idea that every judgement leaves a trace is sound, and it is what makes an audit
  like this one possible. Keep it, but make the records' shape checkable (M3, M4).

### Where the effort is misallocated

The quality of an output depends on four judgement steps more than on anything computed: scope screening, role selection
(especially dissent), verification, and the coverage verdict. For each, the spec records that a judgement was made but
has no rubric, no measured agreement, and in two cases no trace of the negative verdicts (A1–A3). By contrast, the
clustering layer has three measures, a two-standard-error tie rule, a null model, a four-snapshot temporal history, a
match simulation and a recursive experiment. On `reasoning`, the measure choice was decisive (combined 0.722 vs refs
0.671 vs text 0.646). The null model never decided anything. The history feeds only rationale text, and four of its six
statements are hedged "probably" (Z3–Z5).

### Simpler or partial solutions that exist

- `Full-text-first verification` (Z2). `tools/fulltext.py` fetched all 27 abstract-sourced `reasoning` papers from arXiv
  HTML in about 90 seconds, at no model cost. If every verified row quotes the fetched full text, every quote becomes
  mechanically checkable. Snippet search then serves only to locate the passage. This closes the largest hole in the
  verification gate and removes a source level.
- `A covering quantity, computed` (T4). The coreset idea is k-center covering: the quality of a subset is its
  worst-covered point. On the `reasoning` pool (195 papers, SPECTER2 embeddings), the main session computed the coverage
  radius of 20, 40 and 60-paper subsets in under a second. With 40 papers, greedy k-center gives a worst-case cosine
  distance of 0.073, against 0.108 for random subsets. The radius is no substitute for the LLM judgement of "would this
  change a claim", since embedding distance is not semantic change. But it gives a measured sufficiency proxy, a
  principled way to draw the coverage-test sample (the worst-covered papers), and a cheap minimality proxy (how much the
  radius grows when a row is removed).
- `A driver instead of a prose checklist` (Z1, T7). Half the rows of the order of operations are "main: run script X".
  `check.py --status` already infers where a pass stands. A `next` command that prints the next row, its command or its
  brief, and its done-when would turn the main session's hardest job, following a 37-row table from prose, into
  following printed instructions.
- `Fewer clustering options` (Z3, Z4). Fix the measure to `combined` and keep one null draw as a `no structure` guard.
  This removes two thirds of the compute and two of the method bugs found (M9, M10).

## Part (b): issues by dimension

Issues that bear on verification, the quality-gating mechanism, are marked `(V)`. A synthesis of them follows the
dimension lists, in "The verification concept".

### C — the docs and the code disagree

**C1. The `Bridges` row never fires: `check.py` has no note about clusters that trade papers.**

- Evidence:
  - The trigger is `docs/process.md:77` and `docs/dispatch.md:106`: run Bridges "only if `tools/check.py` notes a
    trading pair without one".
  - None of `tools/check.py`'s notes, lines 198–486, mentions trading pairs. Only the gate requirement `g3.bridges` does
    (`tools/gates.py:436-447`).
  - After Selection on a first pass, the safety net infers only `G2` (`tools/gates.py:755-772`).
- Why it matters: the missing bridge first shows up at `--gate G3`, which runs after Fringe selection. So bridges get
  added after fringe, which breaks "fringe comes last" (`docs/process.md:523`).
- Remediation: add the note to `check.py`, built from the `clusters trade papers` diagnostics in `clusters.json`.
- Effort: S. Status: verified against code.

**C2. (V) A missing full-text file downgrades the full-text quote check to a note.**

- Evidence:
  - `docs/gates.md:50` and `docs/verification.md:55` say every `full-text` quote is found in the fetched full text.
  - The code only adds a note when the file is absent (`tools/gates.py:567-569`, `821-823`).
  - `fulltext/` is not in git (`docs/formats.md:317`).
  - Simulation: deleting `fulltext/` and inventing a `full-text` quote passes `--gate G4` and `G5`.
- Why it matters: on a fresh clone, or a reviewer's machine, no full-text quote is ever checked. An agent can also skip
  the check by deleting the file.
- Remediation: fail under `--gate G4` when the file is missing, and keep the note otherwise. Alternatively, record a
  hash of each full text in the evidence file, so that a re-fetch can be demanded and checked.
- Effort: S. Status: verified by simulation.

**C3. `--gate` prints "G<n> passed" while exiting 1.**

- Evidence: `tools/gates.py:819` looks only at gate-prefixed failures, and ignores integrity and history failures. The
  doc says it fails unless every requirement holds (`docs/gates.md:64`).
  - Simulation: with bib entries dropped, `--gate G4` printed "G4 passed: add G4 <today> to the log's Gates line" next
    to `FAIL in coreset but not bib`, and exited 1.
- Why it matters: the main session may paste the gate into the `Gates` line on the strength of the note.
- Remediation: print the note only when the failure list is empty.
- Effort: S. Status: verified by simulation, and against code.

**C4. A pending halt switches off the safety net in the plain check.**

- Evidence: `tools/gates.py:788-791` sets the required gate to the declared one, overriding inference. The doc says only
  that `--gate` fails while a halt is pending (`docs/gates.md:91`).
  - Simulation: a full pass on disk, `Halts: H2 — … — pending`, `Gates: G0`, and an injected empty cell. The plain check
    exited 0.
- Why it matters: while a pass waits on the user, the after-every-dispatch check stops checking what was already
  reached.
- Remediation: required = max(inferred, declared). Use the pending halt only to fail `--gate`.
- Effort: S. Status: verified by simulation.

**C5. "An uncited `[abstract-only]`" has no code.**

- Evidence: `docs/gates.md:34` lists it as an integrity failure. `tools/check.py:466-476` checks only the opposite: an
  abstract-sourced citation without its marker.
  - Simulation: a marker after a verified paper, and a free-standing marker, both pass.
- Remediation: either change the doc wording to "an unmarked abstract-sourced citation", or add the reverse check.
- Effort: S. Status: verified by simulation.

**C6. `assign.py add-fringe` is weaker than `G1`.**

- Evidence: `tools/assign.py:188-194` refuses only a blank `in scope` cell. It treats `maybe` as no, and accepts a blank
  reason. `tools/gates.py:262-267` rejects both. `docs/tooling.md:89-90` says it refuses unjudged rows.
  - Simulation: `add-fringe` exited 0 and printed the `Fringe` line; `G1` then failed `g1.fringe-screened`.
- Remediation: reuse the gate's test in `add-fringe`.
- Effort: S. Status: verified by simulation.

**C7. History accepts any mention of an ID as "a record".**

- Evidence: `docs/gates.md:104-105` requires `H12` or a logged merge for a pool removal, and a `Demotions` or
  `Corrections` entry for a coreset removal. The code accepts the ID appearing anywhere in those lines
  (`tools/gates.py:725-747`).
  - Simulation: a removal recorded as `Demotions: none (see <id>)` passes.
  - Simulation: a second, unlogged edit to a verified row whose ID is already in `Corrections` passes.
- Remediation: parse the entry forms `<id> — <role> in <cluster>, replaced by <id>` and `<id> — <old> -> <new>`.
- Effort: S. Status: verified by simulation.

**C8. `--gate G0` passes, and `--status` prints nothing, on a survey with no log entry.**

- Evidence: `tools/gates.py:784-785` returns early when there is no entry, no rows and no clusters. `docs/gates.md:46`
  says `G0` needs the log entry, and `docs/dispatch.md:31-32` says to resume from `--status`.
  - Simulation: on an empty skeleton, `--gate G0` printed `OK` and exited 0.
- Remediation: skip the early return when `--gate` or `--status` is given.
- Effort: S. Status: verified by simulation.

**C9. The PDF fallback keeps the bibliography.**

- Evidence: `docs/tooling.md:196` and `tools/fulltext.py:20` say the bibliography is dropped. That holds for HTML only;
  `tools/fulltext.py:169-177` and `195-197` keep it in PDF text.
- Why it matters: Grep for a claim's terms can hit a reference title, and a quote from the bibliography would pass G4.
- Remediation: cut the PDF text at the references heading, or document the difference.
- Effort: S. Status: verified against code.

**C10. Small mismatches.**

- Evidence:
  - `assign.py add` prints "next: `python3 tools/pool.py`" (`tools/assign.py:179,219`; also `docs/tooling.md:87-88`),
    but `pool.py` is the main session's job (`docs/process.md:59`).
  - `cluster.py`'s match printout lists only `vanished` clusters (`tools/cluster.py:625-627`). The spec wants splits,
    merges, new and vanished clusters logged (`docs/process.md:626-628`).
  - `docs/tooling.md:137` says the defaults "are the spec's", but the spec gives no value for `c` or for the number of
    null draws. The code uses 10 and 2 (`tools/cluster.py:447-449`).
  - Usage errors exit 1, not 2, in `tools/pool.py:115`, `tools/fringe.py:246` and `tools/cluster.py:445`.
  - The `RECLUSTER` message reads "would be 10% of the pool, above 10%" at 10.3%, from rounding
    (`tools/assign.py:269-271`).
- Effort: S. Status: verified against code; the `RECLUSTER` wording by simulation.

### M — method bugs

**M1. (V) Full-text quote matching accepts vacuous quotes.**

- Evidence: each `...`-separated part is matched on its own, anywhere in the text, as a bare letter stream with word
  boundaries stripped. There is no minimum length (`tools/gates.py:539-571`).
  - Simulation: each of these passed G4 and G5: an empty quote `""`; a quote of only `"..."`; the single word
    `"Results"`; the fragment `"on GSM8K the"`; and `"pro ... ves ... all model sizes"`, with "pro" matched inside
    "improves".
- Why it matters: the check exists to show a quote is not a paraphrase. A trivial quote satisfies it.
- Remediation:
  - require a non-empty quote, with at least about 8 words per part;
  - match on word-normalised text, keeping spaces;
  - require the parts in order, within a window.
- Effort: S. Status: verified by simulation.

**M2. (V) A row's `source` and its evidence are never cross-checked.**

- Evidence: `tools/gates.py:543-582`.
  - Simulation: a `full-text` row whose evidence lines all say `snippet` passes.
  - Simulation: an evidence file copied from another paper passes. Its `# Evidence: <id>` header is never compared with
    the file name.
- Remediation: require at least one `full-text` entry for a `full-text` row, and check the header ID.
- Effort: S. Status: verified by simulation.

**M3. An empty log line satisfies every "line present" requirement.**

- Evidence: `need_lines` tests `not c.L.get(l)`, but an empty label is stored as `[""]`, which is truthy
  (`tools/gates.py:152`).
  - Simulation: emptying `Tokens`, `Halts` and `Ended` passes G5.
  - Simulation: an unconverged coverage round (`5 of 12`) plus an empty `Ended:` passes G5, because `r_converged` skips
    when `Ended` is empty (`tools/gates.py:651-657`).
  - Simulation: emptying `Clustering rationale`, `Temporal stability` and `Recency window` passes G2.
- Remediation: treat a value that is empty after `strip()` as missing. Require `Ended` to match `finished (F1)` or
  `halted (H\d+)`.
- Effort: S. Status: verified by simulation, and against code.

**M4. Several record checks accept any token.**

- Evidence and simulated results:
  - `r_dissent_quoted` accepts any quoted string of 12 or more characters (`tools/gates.py:40`, `431-434`).
    `is "a paper about reasoning models"` passes.
  - `r_dissent_searched` needs only the cluster id as a word (`tools/gates.py:420-423`). `Dissent searches: one two`
    passes. The ids after `found:` are never checked.
  - `Tokens: lots` passes.
  - `Coverage test: round 1: 0 of 0` passes. N has no lower bound, though the spec says 10–15. K is not compared with
    the number of IDs named.
  - `Expansion: we did NOT traverse <ids>` passes `g1.expansion`, a substring check.
- Why it matters: `docs/gates.md:11-27` promises checks of records, not judgement. These do not check even the record's
  shape.
- Remediation:
  - parse `Dissent searches` per cluster, as `<id>: <what> -> found: <id> | none found`, and require each found id to be
    a dissent row of that cluster;
  - require the dissent quote to appear in that row's evidence file once verified;
  - parse `Tokens` as `<step>: <n>` pairs;
  - require N ≥ 10, and as many IDs as K.
- Effort: S–M. Status: verified by simulation.

**M5. Fringe screening can be hollowed out by deleting sheet rows.**

- Evidence: `r_fringe_screened` iterates over the sheet's rows only, never over the candidates in `fringe.json`
  (`tools/gates.py:250-267`).
  - Simulation: deleting 143 of 146 rows, all the `no` verdicts, passes `--gate G1`. A reason of just `x` also passes.
- Remediation: require every candidate in `fringe.json` to have a well-formed, judged row.
- Effort: S. Status: verified by simulation.

**M6. A pass ended by a halt can never pass `check.py` again.**

- Evidence: `tools/gates.py:792-793` caps the required gate at G4 when `Ended` says halted. The docs never say which
  gates a halted pass needs.
  - Simulation: a first pass halted at step 3 (`H4`, user decided to stop), with no coreset. Both the plain check and
    `--gate G2` exit 1, on six G3 and G4 requirements.
- Why it matters: `docs/process.md:114` notes that a halt is not always a fault. Yet a legitimately halted topic fails
  every later check, and that looks like `H9`.
- Remediation: for a halted pass with a recorded decision, require only the gates up to the last declared one, plus a
  "closed" check that `Tokens`, `Halts` and `Ended` agree. Document this in `docs/gates.md`.
- Effort: S. Status: verified by simulation.

**M7. History compares earlier log entries by substring.**

- Evidence: `tools/gates.py:721` tests `l not in now` against the whole log.
  - Simulation: deleting `- **Halts:** none` from an earlier entry passes, because the current entry has the same line.
  - Simulation: moving the earlier entry after the current one passes.
- Remediation: compare the old entry's lines with the entry of the same date, in order.
- Effort: S. Status: verified by simulation.

**M8. History uses HEAD as its baseline.**

- Evidence: `tools/gates.py:713-715`.
  - Simulation: with no commit, an uncorrected edit to a verified row passes.
  - Simulation: after a mid-pass commit, an unrecorded pool removal passes.
  - No hook runs `check.py` before a commit (`.claude/settings.json`).
- Why it matters: any commit launders whatever came before it.
- Remediation: record the commit at the start of the pass in its log entry, and compare against that.
- Effort: M. Status: verified by simulation.

**M9. Under `refs`, papers with no references become singleton clusters.**

- Evidence:
  - `tools/cluster.py:125` links only pairs with positive similarity, so a paper with no resolved references becomes an
    isolated node, and Leiden gives it its own label.
  - `n_clusters` ignores singletons (`tools/cluster.py:139-140`), but `clusters` and `assignment` keep them
    (`tools/cluster.py:516-534`).
  - Simulation: `refs` at targets 3, 6 and 10 on `reasoning` gives 16, 19 and 23 label groups, 13 of them singletons.
  - Data: the 9-month simulated pass in `graphs/reasoning/match-simulation.json` chose `refs`, with 7 fragments.
- Why it matters: if `refs` wins, the log says "6 clusters" but the naming agent receives 19 ids. Each singleton is
  diagnosed `thin cluster`, with the action "expand this region".
- Remediation: attach zero-reference papers by text, as `combined` does. Or drop `refs` as a candidate (Z3).
- Effort: S. Status: verified by simulation, and against data.

**M10. The standard errors understate the run-to-run spread 2–3x, so the tie rule is miscalibrated.**

- Evidence: `tools/cluster.py:221-264`; spec at `docs/process.md:305-309`, `331-332`.
  - Simulation: 12 replications of the curves with varied seeds. The measured spread of the grid mean was 0.009 (text),
    0.015 (refs) and 0.014 (combined). The reported SEs were 0.0054, 0.0048 and 0.0045.
  - The SE leaves out the randomness of the fixed reference partition, and it treats the 9 nested holdout runs as
    independent.
- Why it matters: on `reasoning` it changed nothing. `combined` won in 12 of 12 replications, and the level was 6 in 11
  of 12. But the rule's stated confidence is not real.
- Remediation: replicate over several reference seeds, and use paired differences between measures. Or drop the
  three-way choice (Z3).
- Effort: M. Status: verified by simulation.

**M11. The mixed fringe score is not a percentile, so papers without references rise to the top.**

- Evidence: `tools/cluster.py:312-316` averages two percentiles with a per-paper weight. The doc's reading, "0.95 means
  further than 95% of papers its age" (`docs/process.md:367`), holds only under `text`.
  - Simulation: papers with zero references fill 5 of the top 8 mixed scores, against 1 of the top 8 text-only scores.
- Why it matters: `fringe-sheet.md` drives the `fringe` role. Its top slots go to papers that lack reference data, which
  is the artefact the weight was meant to remove (`docs/process.md:374-376`).
- Remediation: re-rank the mixed score within the age cohort, or mix distances first and rank once.
- Effort: S. Status: verified by simulation.

**M12. The age correction of the fringe score is close to a no-op.**

- Evidence: the cohort is integer `year` ±1 (`tools/cluster.py:301-309`), not publication date as the doc implies
  (`docs/process.md:361-362`).
  - Data, years in `pool.json`: 2021: 2, 2022: 4, 2023: 11, 2024: 15, 2025: 81, 2026: 82.
  - So a 2025 paper ranks against 178 of 195 papers, and a 2026 paper against 163.
  - The 2021 cohort has 6 papers, under 10, so it falls back to the whole pool. A 2021 paper ranks fourth on the fringe
    list, at 0.93.
- Why it matters: on a young field the correction does not separate "old" from "overlooked", which is its whole purpose.
- Remediation: use a date window, for example the nearest N papers by date, or regress distance on age.
- Effort: S. Status: verified against data (main session and clustering agent independently).

**M13. All holdout cutoffs skipped gives NaN stability, and silently skips the `no structure` check.**

- Evidence: `tools/cluster.py:470-471` can leave the cutoffs empty. Then `nan < 0.15` is False. The spec does not cover
  the case (`docs/process.md:322-324`).
  - Simulation: with no cutoffs, stability is `nan`, and the tool reports "no level reaches 0.75; coarsest level used".
- When it happens: whenever less than 30% of the pool is older than three months, which is plausible on a hot topic.
- Remediation: fall back to resampling only, and say so.
- Effort: S. Status: verified by simulation.

**M14. Sub-cluster scores assume the levels are nested, and Leiden levels are not.**

- Evidence: `tools/cluster.py:520-529` gives each part (finer cluster ∩ coarse cluster) the finer cluster's whole score.
  - Data: one score, 0.48, is attached to sub-clusters inside c2, c4 and c6. It is one finer cluster straddling three
    parents.
- Why it matters: "internally divided" can be triggered by a score that belongs mostly to papers outside the cluster.
  That adds a row to the coreset (`docs/process.md:536-538`).
- Remediation: score the intersection itself.
- Effort: S. Status: verified against data.

**M15. The fringe screening sheet is not blind: its `year` column gives away the route.**

- Evidence: `tools/fringe.py:139-141` writes the year.
  - Data, `graphs/reasoning/fringe.json`: all 54 dated `new` candidates are from 2026. No `hidden` candidate is from
    2026, and `hidden` reaches back to 1965.
- Why it matters: `docs/process.md:232-236` and `docs/tooling.md:125` claim screening is blind to the route.
- Remediation: drop the year from the sheet, or narrow the claim.
- Effort: S. Status: verified against data (main session and pipeline agent independently).

**M16. Rejected papers are never cross-checked.**

- Evidence: `tools/fringe.py:88-95` excludes only papers already in the pool. `assign.py add` and `add-fringe` never
  read `rejected.md`.
  - Simulation: rejecting `2310.01798` and then adding it succeeds, and `check.py` raises nothing.
- Why it matters: a rejected reference is exactly what the `hidden` route collects. It can be screened twice, with two
  opposite verdicts on record.
- Remediation: exclude rejected IDs in `fringe.py`; warn in `add`; note the conflict in `check.py`.
- Effort: S–M. Status: the add/check part verified by simulation; the fringe re-surfacing is likely.

**M17. `pool.py` never backfills the `arxiv` field into older records.**

- Evidence: `tools/pool.py:131-134` fetches only papers with no record.
  - Data: none of the 195 records in `graphs/reasoning/pool.json` has an `arxiv` key.
- Why it matters: the check against a `CorpusId` row whose paper has an arXiv ID (`tools/check.py:284`,
  `docs/tooling.md:113-115`) silently does nothing for those records.
- Remediation: refetch records that lack the key, or note that `--refresh` is needed.
- Effort: S. Status: verified against data.

**M18. `inputs.py` silently drops some well-meant input.**

- Evidence:
  - Only `- ` bullets count (`tools/inputs.py:50-61`). A dimension written as a `*` bullet gives zero dimensions and
    exit 0, which contradicts "a typo cannot silently drop a request" (`docs/tooling.md:76-78`). The Stop hook later
    rewrites `*` as `-`, so the same input reads differently before and after the first turn.
  - The values regex (`tools/inputs.py:29`) drops the last value after an Oxford comma: "`a`, `b`, or `c`" gives {a, b}.
  - Two `## Dimensions` sections: the first is discarded. An empty `## Topic` passes. `granularity: 0` passes.
  - Dropping all three default targets leaves zero targets, which makes the coverage test vacuous.
- Remediation: fail on each of these.
- Effort: S. Status: verified by simulation.

**M19. The Stop hook's `mdformat .` rewrites generated and in-progress files.**

- Evidence: `.claude/settings.json`, the Stop hook.
  - Simulation: it rewrote 28 of 113 rows of a fresh `fringe-screen.md`, both sheets, the survey skeleton's log lines,
    and a user input. `2>/dev/null || true` also hides a missing mdformat.
- Why it matters: the hook runs whenever a main-session turn ends. Background `survey-pass` agents may be editing
  `surveys/<topic>.md` or a sheet at that moment, and could get "modified since read" errors, or lose a write to the
  race (likely, not reproduced). It also rewrites the user's input, which only the user should edit.
- Remediation: limit the hook to `docs/` and `outputs/`.
- Effort: S. Status: rewriting verified by simulation; the race is likely.

**M20. Smaller method issues.**

- Evidence:
  - The holdout reruns slice the full-pool rank normalisation (`tools/cluster.py:184-185`), while history and simulate
    recompute it on the subset (`tools/match.py:139-145`). Measured holdout ARI: 0.776 against 0.801. The effect is
    small and conservative.
  - The `hidden` route keeps a fixed 60 candidates. On a 15-paper scratch pool, that was 60 of 104 candidates, with
    median citations of 498, so it is not selective there.
  - `bib.py` takes every link in the Coreset section (`tools/bib.py:36-37`), and `check.py` the first per row
    (`tools/check.py:152-154`). A row with a second link would break bib parity (likely; no impact today).
- Effort: S each. Status: as stated per item.

### S — spec inconsistencies and gaps

**S1. `Dimensions` has no owner, and two incompatible timings.**

- Evidence:
  - `docs/formats.md:50-52`: if the input declares none, propose them "at step 3", and say so "in the report", without
    saying whose report.
  - `docs/process.md:53`: the step-0 Plan row writes `Dimensions`. `docs/gates.md:46`: `G0` requires it.
  - `tools/gates.py:171-179`: when nothing is declared, `G0` requires the word "proposed". "proposed and adopted
    provisionally: TBD" would pass, while the template's `<name>` fails as a placeholder.
  - No brief proposes dimensions. Naming is silent (`docs/dispatch.md:93-97`). Selection drafts dimension cells as if
    they already exist (`docs/dispatch.md:102-103`).
  - Provisional dimensions escape the value check (`docs/formats.md:52`) and the G4 evidence check, which covers only
    declared ones (`r_evidence`).
  - Simulation: an input without `## Dimensions` fails `g0.dimensions`.
- Why it matters: any input without dimensions is blocked at the first gate, and the user's minimal input, Topic and
  Context only, is the common case.
- Remediation: the main session proposes dimensions at the Plan row, from the input, in the same form as declared ones
  (name and values). The `Dimensions` line carries them, `check.py` reads values from it, and G4 covers them.
- Effort: S–M. Status: verified by simulation, and against code.

**S2. Papers added after `G1` make the plain check fail, which reads as `H9`.**

- Evidence:
  - The coverage test, probes, targeted expansions and step 6 add pool rows with `assign.py add`. The main session then
    runs `check.py` (`docs/dispatch.md:52-54`), with `G1` already inferred.
  - `g1.fetched` and `g1.pool-line` then fail until `pool.py` or `late` runs and the new `Pool` line is pasted
    (`tools/gates.py:243-245`, `307-317`).
  - The Late papers row (`docs/process.md:86`) omits the `Pool` line that `assign.py late` prints. Simulation: after
    `late`, `check.py` failed `g1.pool-line`.
  - During Revise, the `Coverage test` line makes the safety net infer G4. New abstract-drafted rows then fail
    `g4.abstract-listed` (`tools/gates.py:494-496`), and the Selection brief never lists them in Open work.
- Why it matters: a rule-following main session halts, or improvises, at every coverage round.
- Remediation:
  - after any dispatch that adds pool rows, run `late`, or `pool.py` before step 3, and paste `Pool` before checking;
  - add `Pool` to the Late papers row's `writes`;
  - have Selection list its new rows under `Rows needing verification`.
- Effort: M. Status: verified by simulation, and against code.

**S3. On a later pass, the step-2 provisional clustering breaks `check.py` and `G1`.**

- Evidence:
  - `docs/process.md:60` runs `cluster.py` at step 2. `docs/process.md:494-495` and `docs/tooling.md:35-36` say to run
    `remap` once, after step 3.
  - Once the Clusters table has names, `cluster.py` records an un-remapped `previous` (`tools/cluster.py:580-592`), and
    `check.py:328-331` fails.
  - Simulation: after naming and a rerun, the check fails with "names have not been carried over; run remap".
- Remediation: a `--provisional` mode that writes a separate file for `fringe.py`. Better, remove the provisional
  clustering (Z7).
- Effort: M. Status: verified by simulation.

**S4. The coverage test's "new cluster" path is not wired, and a proposal the data overrules still blocks convergence.**

- Evidence:
  - The Coverage brief returns proposed clusters "for a targeted expansion" (`docs/dispatch.md:119-120`). No step-7 row
    dispatches that expansion.
  - The Late papers row reclusters only on `RECLUSTER:` (`docs/process.md:86`), but `docs/process.md:487-490` requires a
    recluster for a proposed cluster.
  - Convergence requires `new clusters: none` (`converged()` in `tools/gates.py`). So a proposal that the recluster
    overruled still counts against convergence, pushing toward `H11`.
- Remediation: add the rows. Record an overruled proposal as `new clusters: none (proposed <x>, not formed)`.
- Effort: M. Status: verified against code, and by simulation (tabletop).

**S5. (V) The coverage test is weak evidence of sufficiency, and the spec does not say how weak.**

- Evidence: `docs/process.md:563-578` and `docs/coresets.md:109-113`. `F1` finishes on a round of 10–15 candidates with
  no new cluster and at most one change.
  - Computation (one-sided 95% upper bound, Clopper–Pearson): N=15, K=1 gives 0.28; N=12, K=1 gives 0.34; N=10, K=1
    gives 0.39. With K=0 the bounds are 0.18, 0.22 and 0.26.
- Why it matters: a pass that "finishes" is consistent with a fifth to two fifths of unsampled pool papers changing the
  output. The sample's lean toward thinly covered clusters helps, since it targets the likely failures. But the strength
  of `F1` should be stated, not implied by the word "sufficient".
- Remediation:
  - report the bound with each round;
  - draw the sample by script, from the worst-covered papers (T4), with the seed recorded;
  - consider a sequential rule, e.g. two clean rounds.
- Effort: S to state, M to change. Status: verified by simulation (computation).

**S6. `g1.rejected` requires at least one rejection.**

- Evidence: `tools/gates.py:233-240`; `docs/gates.md:47`.
- Why it matters: a clean pass that rejected nothing cannot pass `G1` without a waiver.
- Remediation: accept an explicit "no rejections" record.
- Effort: S. Status: verified by simulation, and against code.

**S7. The spec gives two incompatible rules for the level.**

- Evidence: `docs/process.md:341-343` says both "finest one whose stability still reaches τ" and "the last level before
  the curve falls off". The code implements "finest" (`tools/cluster.py:280-283`).
  - Data: `reasoning`'s τ sensitivity at 0.70 gives 12 clusters, skipping a dip to 0.67 at 8 clusters. "Last before the
    curve falls off" would give 6.
- Remediation: keep one rule and state it.
- Effort: S. Status: verified against data.

**S8. The six-month stability aim is not borne out by the simulated earlier passes.**

- Evidence: the aim is at `docs/process.md:270-271` and `docs/coresets.md:85-87`. Data in
  `graphs/reasoning/match-simulation.json`: ARI against today's clustering is 0.68 at 3 months back, 0.86 at 6 months,
  and 0.39 at 9 months, where that pass chose `refs` and no level reached τ.
- Why it matters: high within-pool stability did not predict agreement across passes. Near τ the level flips.
- Remediation: on later passes, keep the previous level unless it falls below τ (hysteresis). Report the measured
  cross-pass agreement instead of the aim.
- Effort: M. Status: verified against data.

**S9. Numeric claims that are stale or overstated.**

- Evidence:
  - "The clusters survive losing 20% of the papers" (`docs/process.md:485`): the resampling ARI at the chosen level is
    0.76. In simulation, removing a random 10% gave ARI 0.79, and the diagnostics changed.
  - The late-assignment figure, 15 of 15 (`docs/tooling.md:105-107`), is in-sample. Out of sample it was 13 of 15. The
    two misses included `2402.03300`, the top paper of its full-pool cluster.
  - The "118 fringe candidates … ARI 0.70" figure (`docs/process.md:486`) includes 16 papers from a `followers` route
    that `fringe.py` no longer has (`graphs/reasoning/fringe.json`).
- Remediation: replace each with the measured number.
- Effort: S. Status: verified by simulation, and against data.

**S10. (V) The verification rules leave room for two agents to verify the same row differently.**

- Evidence:
  - When to fall back to full text is left to the agent ("typically twice", `docs/verification.md:14-22`).
  - A row with both snippet and full-text evidence has no `source` rule. The code ranks the two equally
    (`tools/gates.py:42`), so `full-text` to `snippet` is not "lowering" (`docs/verification.md:85`).
  - Evidence is required only for `method summary`, `result` and the dimensions (`docs/verification.md:48-49`). It is
    not required for `method name`, `datasets / models` or `metric`, though the doc lists all of them as checked.
  - Rewriting a first-pass draft is free under `docs/gates.md:108`, but "Corrected" requires a log entry
    (`docs/verification.md:74`). On a first pass, every row could be logged as a correction, or none.
  - An uncheckable row may stay "only if no verifiable paper can fill its role" (`docs/verification.md:78`). That needs
    a re-selection the Verification brief does not cover.
  - "Publication grade" is defined by the standard of a hypothetical publication, not by observable criteria.
- Why it matters: the verification step is where most of the cost goes, and its result is not reproducible across
  agents. That agreement has never been measured.
- Remediation:
  - state the full-text rule (Z2 makes it moot);
  - require evidence for every non-`n/a` cell;
  - state that verifying a draft is not a correction;
  - give the replacement search to the Selection brief.
- Effort: M. Status: verified against docs and code.

**S11. Who writes which log line is inconsistent.**

Main-session lines:

- `Preflight`: the script half is "printed by scripts, ready to paste" (`docs/formats.md:158-159`), and the main session
  writes script lines (`docs/dispatch.md:36`). But the Preflight brief writes "both halves" (`docs/dispatch.md:77`).
- `Halts` and `Waivers`: no row writes `Halts: none`, yet `G5` requires the line. `Waivers` has no row at all.
- `Tokens`: written only at the end (`docs/process.md:88`), though the format is per dispatch (`docs/formats.md:151`).
  Per-dispatch usage is lost on a halt, or across sessions.
- Open work's "Clusters not yet reviewed": `g2.clusters-line` requires it when Naming writes "not yet reviewed". It is
  the main session's line (`docs/dispatch.md:38`), but no row says so.

Agent lines:

- `Dissent searches`, `Demotions` and `Corrections`: the `writes` column (`docs/process.md:76`, `81`) has the parallel
  Selection and Verification agents write them. `docs/dispatch.md:45-46` forbids parallel agents to write the log.
- `Errored queries`: assigned only to Expand. But Orient, dissent searches, Verification, Coverage and Probe can all hit
  errors (`docs/external_services.md:84-88`), and parallel agents cannot write the line.

Other:

- `Clusters` "reviewed by user": the review happens with the finished output by default (`docs/process.md:451`), but a
  line is "never" updated after the pass ends (`docs/dispatch.md:40-41`). The review has nowhere to go.
- The coreset blocks: `docs/dispatch.md:8-9` limits the main session's survey writes to empty sections and log lines,
  but `docs/process.md:75` has it set up the coreset blocks.

Remediation: make the `writes` column the single authority, with an explicit "returned under `Log:`" marker for parallel
jobs, and rows for `Halts`, `Waivers` and `Tokens`. Append `Tokens` after every dispatch.

- Effort: S. Status: verified against docs and code. The full line-by-writer table is in the appendix.

**S12. A halted parallel agent receives contradictory orders.**

- Evidence: on a halt, write the outstanding work to Open work (`.claude/agents/survey-pass.md:37`,
  `docs/process.md:106`). Parallel agents never write Open work (`.claude/agents/survey-pass.md:33-35`,
  `docs/dispatch.md:45-46`).
- Remediation: on a halt, a parallel agent returns its items under `Open work:`.
- Effort: S. Status: verified against docs.

**S13. Reusing verified rows from an earlier survey has no procedure.**

- Evidence: `CLAUDE.md:19-22` promises it. No step in `docs/process.md` does it, and G4 looks for evidence only under
  `graphs/<topic>/evidence/` (`evidence_path` in `tools/gates.py`).
- Why it matters: the legacy `reasoning` survey's 168 snippet-verified rows have no evidence files. So reuse is not
  possible at all under G4 without re-verification.
- Remediation: an import procedure that copies rows with their evidence files and logs the origin. State that a row
  without an evidence file is not reusable as verified.
- Effort: M. Status: verified against docs, code and data.

**S14. Stale or inconsistent statements.**

- Evidence:
  - `docs/external_services.md:173` calls the Preflight line "the first line" of the log. The template puts `Gates`
    first (`docs/formats.md:116`).
  - The Coverage test format at `docs/process.md:571` lacks `round R:` and `new clusters:`, which the code requires.
  - `docs/tooling.md:244-245` names the test source by a rename (`reasoning-exhaustive`) that has not happened.
  - `outputs/reasoning.md:10-12` explains `[abstract-only]` as "because Asta has no full text indexed for that paper".
    Yet `graphs/reasoning/fulltext/` holds full text for all 27 abstract-sourced rows; they were fetched but never
    verified.
  - `docs/external_services.md:29` marks "Asta's paper tools run on the Semantic Scholar corpus" as `UNVERIFIED`, while
    lines 21 and 108 assert it. One data point: Asta's `get_paper` for `ARXIV:2408.03314` returns `paperId`
    `8292083dd8f6ae898ea0ee54a6b97997d1a51c9d`, the same as the `s2` field in `pool.json`. That supports the claim but
    does not prove it.
  - `H4` allows "possibly one" cluster (`docs/process.md:423`), but the grid starts at 3 (`tools/cluster.py:55`).
  - "Left out X" in the `Fringe` line (`docs/formats.md:123-124`) is undefined. The code counts in-scope candidates
    without an ID, which a reader will likely take as the out-of-scope count.
- Effort: S each. Status: verified against docs, code and data.

**S15. The input format leaves out what the parser requires.**

- Evidence:
  - `docs/formats.md:3-71` never says that sections are `##` headings. `# Topic` and `### Topic` both fail
    (`tools/inputs.py:39`).
  - "Other prose in the section is allowed" in `Coreset Spec` (`docs/formats.md:22`), but a prose bullet fails
    (`tools/inputs.py:136-138`).
- Remediation: add a skeleton input to `docs/formats.md`.
- Effort: S. Status: verified by simulation.

### W — how the docs are wired

**W1. `survey-pass` is told to read `docs/dispatch.md`, but the index gives that file to the main session only.**

- Evidence: `CLAUDE.md:43` against `.claude/agents/survey-pass.md:28` and the brief template at
  `docs/dispatch.md:65,70`.
- Why it matters: an agent following the index literally never reads its own brief, and the brief does not restate the
  method.
- Remediation: add `survey-pass` ("Briefs", at dispatch) to the index row.
- Effort: S. Status: verified against docs.

**W2. Spec files point into `docs/roadmap.md`, which agents may not read.**

- Evidence: `docs/process.md:630`, read by `survey-pass`, defers the "most clusters fail to match" case to the roadmap.
  Also `docs/formats.md:319` and `docs/gates.md:116`.
- Why it matters: behaviour in that case is undefined for the agent that meets it.
- Remediation: state an interim rule in the spec, such as "halt for review", and drop the pointers.
- Effort: S. Status: verified against docs.

**W3. The reading load per dispatch is large, and the estimates leave it out.**

- Evidence: per `CLAUDE.md:41-52` and `.claude/agents/survey-pass.md:17-20`, a `survey-pass` agent reads these whole
  files before working:

  | file | bytes |
  | -- | -- |
  | `docs/process.md` | 51,907 |
  | `docs/formats.md` | 25,131 |
  | `docs/tooling.md` | 19,337 |
  | `docs/external_services.md` | 14,695 |
  | `docs/dispatch.md` | 10,886 |
  | `docs/verification.md` | 7,160 |
  | `CLAUDE.md` | 4,936 |
  | `.claude/agents/survey-pass.md` | 4,895 |

  At about 4 characters per token, that is roughly 30–35k tokens per dispatch.

- The cost per pass: a first pass dispatches about 16 agents (Preflight, Orient, Expand, Fringe screening, Naming, about
  four Selection and four Verification agents, Bridges, Fringe selection, one or two Coverage rounds). That is about
  0.5M tokens of spec reading, against a planning figure of 1–1.5M for the whole pass (`docs/process.md:91-93`). The
  Preflight agent alone, estimated "under 5k", must read `process.md` "before any retrieval".

- Remediation:

  - give each brief its own reading list, by section;
  - move rationale (much of `docs/process.md` "Clustering method", `docs/coresets.md`) out of agent reading;
  - count spec reading in the estimates, and measure it in the first run.

- Effort: M. Status: likely (computed from file sizes, not measured).

**W4. Some references point to bold paragraph labels rather than headings.**

- Evidence: "Recording it", "Sizing", "Outcomes" and `Coreset Spec` resolve, but not as headings.
- Why it matters: little. It makes them harder to find by Grep.
- Effort: S. Status: verified against docs.

### A — whether the docs work as instructions for agents

**A1. There is no scope rubric, and no stopping rule for retrieval.**

- Evidence: "Screen for scope" (`docs/process.md:200-201`), and fringe screening "as in expansion"
  (`docs/dispatch.md:91`), have only the `Topic` and `exclude` behind them (`docs/formats.md:64`). Expand's traversal
  depth and the number of Orient queries are unstated.
- Why it matters: `.claude/agents/survey-pass.md:22-26` itself names a silent scope error as the main risk. Two agents
  will build different pools, and the pool bounds everything the coreset can cover.
- Remediation:
  - a short rubric: in, out, and borderline-is-in, each with a reason tied to the `Topic`;
  - a stopping rule for Orient and Expand, e.g. stop when a batch of N screened candidates yields fewer than M new
    in-scope papers.
- Effort: M. Status: verified against docs.

**A2. The selection criteria are undefined.**

- Evidence:
  - A frontier paper is "recent, high-impact" (`docs/process.md:510-511`), and neither word is defined.
  - Dissent must contradict "the cluster's consensus" (`docs/process.md:512-517`), but no file records a cluster's
    consensus. The `definition` column is one sentence.
  - The gate checks only for a quote of 12 or more characters (M4).
- Remediation:
  - define recency as the recency window, and impact as citations per month, printed by a script;
  - have Naming record each `high` cluster's central claim, so that dissent is judged against something written down.
- Effort: M. Status: verified against docs and code.

**A3. (V) The coverage-test judgement is under-specified, and leaves no trace for most candidates.**

- Evidence: `docs/process.md:563-572` and `docs/formats.md:145-147` record only the candidates that changed something.
  - The sampled IDs, the weighting and any seed are not recorded, which breaks "every judgement leaves a trace"
    (`docs/gates.md:17`).
  - The evidence the verdict rests on, abstract or snippets, is unstated.
  - What counts as "would change a claim" is unstated: an extra citation, a refinement, or only a reversal.
  - Which service runs the "fresh recency query" is unstated.
  - `K of N` is a hand count, against `docs/formats.md:162`.
- Why it matters: this is the stopping rule, and `docs/coresets.md:159-160` already admits that agreement between two
  agents is unmeasured.
- Remediation:
  - a per-round sheet, written by script, with every sampled ID and a verdict column (as `fringe-screen.md` does);
  - a change rubric: a new, removed or reversed claim in a target counts; an added citation does not;
  - name the evidence level and the query service.
- Effort: M. Status: verified against docs.

**A4. The step-3 loop of targeted expansions is missing from the checklist.**

- Evidence:
  - The Cluster row is done when "each diagnostic's action [is] taken" (`docs/process.md:66`). For a thin cluster or
    `no stable level`, that action is a targeted expansion and a rerun (`docs/process.md:426-427`, `439-443`). No rows
    exist for that loop.
  - `H7` is "found" by Naming (`docs/process.md:69`), but it needs a targeted expansion first
    (`docs/process.md:136-137`), which Naming cannot dispatch.
  - A rerun after naming needs `remap`, against "a first pass needs no remap" (`docs/process.md:494-495`).
  - `docs/process.md:470` calls targeted-expansion papers "late", but here they are simply reclustered.
- Remediation: add explicit sub-rows for the loop, and say when `remap` applies on a first pass.
- Effort: M. Status: verified by simulation (tabletop).

**A5. The themes from Orient are not persisted.**

- Evidence: Orient returns the themes only in its report (`docs/dispatch.md:81-82`). Expand's done-when depends on them
  (`docs/process.md:58`). The `Orientation` line has no field for them (`docs/formats.md:119`).
- Why it matters: after a crash the themes are lost, and no gate can check the condition.
- Remediation: add `themes:` to the `Orientation` line.
- Effort: S. Status: verified against docs.

**A6. The Orient brief has gaps.**

- Evidence:
  - Its writes omit `Errored queries` and Open work.
  - A frontier candidate that is not in Semantic Scholar makes the row's done-when unreachable (`docs/process.md:57`,
    `docs/formats.md:106-107`).
  - Seed papers that the input names as anchor candidates (`docs/formats.md:11-12`) have no slot in `Orientation`.
- Effort: S. Status: verified against docs.

**A7. Several rows' done-when conditions are unreachable or misleading as written.**

- Evidence:
  - Step 0's Plan row expects `check.py` to exit 0, but once a later pass's entry exists, it fails `g0.preflight` until
    Preflight has written its line (`docs/process.md:53`). Simulated on the first-pass skeleton, with the same logic.
  - The provisional clustering at step 2 prints diagnostics with actions ("no stable level -> expand … halt (H5)"), and
    `check.py` then says "name the computed clusters". The row says only that it is not logged (`docs/process.md:60`).
    Simulated.
- Remediation: correct the done-when conditions, and suppress the diagnostics of a provisional run (Z7 removes it).
- Effort: S. Status: verified by simulation.

**A8. Step 6 leaves the main session without a way to check the claims it writes.**

- Evidence:
  - The main session must "verify the claims an output will rest on" (`docs/dispatch.md:57-58`), but may make only
    single outside calls (`docs/dispatch.md:26-27`).
  - Nothing helps it read only the Clusters and Coreset sections of a survey that the Pool table dominates
    (`surveys/reasoning.md` is 392 KB).
  - The size itself is fine: 50 rows at about 375 tokens each is about 19k tokens.
- Remediation: a section-print helper (T6), and a bounded check of the output's claims (T2).
- Effort: S. Status: verified against docs; the size estimate is likely.

**A9. Common slips crash with tracebacks, which the spec classes as `H3`.**

- Evidence:
  - `assign.py add` and `pool.py` on a topic with no survey raise `FileNotFoundError` (simulated).
  - `add-fringe` without `fringe.json` crashes.
  - `bib.py` and `fulltext.py --abstract` raise `KeyError` without a `## Coreset` section.
  - `docs/process.md:126-128` treats a traceback as `H3`.
- Remediation: exit with a message that says what to run first.
- Effort: S. Status: verified by simulation and against code.

### T — tool work the spec needs but lacks

**T1. (V) Snippet quotes are checked against nothing.**

- Evidence: `tools/gates.py:564-566` checks `full-text` entries only. The spec promises no more
  (`docs/verification.md:55`).
  - Simulation: every verified row's evidence replaced by
    `— snippet — "zqxj this sentence appears in no paper anywhere"` passes the plain check, `--gate G4` and `--gate G5`.
    The gate fixture itself has fifteen rows sharing the quote "we report accuracy gains", and passes G5.
  - Data: 168 of the 195 legacy rows are `snippet`-sourced.
- Why it matters: for the default source, the evidence file is unverifiable decoration. A fabricated quote passes.
- Remediation: make full text the quoted source (Z2). Failing that, have a tool persist the raw `snippet_search` results
  per paper, so that snippet quotes can be matched too.
- Effort: M. Status: verified by simulation, and against data.

**T2. (V) Nothing checks that an output sentence is supported by the row it cites.**

- Evidence: `docs/formats.md:288-297` and `tools/check.py:459-487` check that cited IDs are coreset rows, and that
  markers are present. But verification is per row, while the user reads the output. The main session writes the output
  from the rows, and could add details from its own memory that no row contains.
  - Spot check: three claims in `outputs/reasoning.md:18-40` were compared with their rows (`2605.23950`, `2507.14843`,
    `2609.04518`), and all three were faithful. So this is a gap in the mechanism, not an observed failure.
- Remediation: a script that extracts each output sentence with its cited IDs, next to those rows' cells and evidence
  quotes. An independent agent then judges a sample, blind to the writer.
- Effort: M. Status: gap verified against code; the faithfulness of the existing output verified against data, on three
  claims.

**T3. (V) Nothing measures how accurate the judgements are.**

- Evidence: `docs/gates.md:112-116` proposes an independent re-judging of a random sample, but none is built.
- Why it matters: every quality claim the repo makes rests on agent judgements: scope, dissent, verification, the
  coverage verdict. Their error rate is unknown. A first end-to-end run is the cheapest moment to measure it.
- Remediation: for the first run, re-verify a random 10% of rows (at least five) with a fresh agent that sees only the
  paper ID and the column definitions. Compare cell by cell, and record the agreement rate in the log.
- Effort: M. Status: verified against docs.

**T4. There is no computed covering quantity.**

- Evidence: no code in `tools/` mentions a radius or k-center (searched). `docs/coresets.md:22-38` grounds the design in
  k-center covering.
  - Simulation on the `reasoning` pool (195 papers, SPECTER2, cosine distance; median pairwise distance 0.095):

    | k | greedy k-center: max / p90 / mean | random subsets (50 draws): max / p90 / mean |
    | -- | -- | -- |
    | 20 | 0.088 / 0.078 / 0.058 | 0.114 / 0.076 / 0.053 |
    | 40 | 0.073 / 0.065 / 0.045 | 0.108 / 0.068 / 0.043 |
    | 60 | 0.062 / 0.059 / 0.036 | 0.097 / 0.063 / 0.035 |

  - Computed in under a second.
- Why it matters: a measured coverage figure would give the coverage test a principled sample (the worst-covered pool
  papers), a number to report beside the LLM verdict, and a minimality proxy (the growth of the radius when a row is
  removed). The table also shows a caveat: in SPECTER2 space, distances are compressed. The average coverage of random
  subsets is as good as greedy's; only the worst case differs. That supports the spec's choice of fringe as the role
  that covers outliers.
- Remediation: `tools/coverage.py <topic>`. It prints the coreset's radius (max and p90) under the chosen measure, and
  the worst-covered pool papers for the coverage-test sample. On request, it also prints each row's leave-one-out radius
  increase.
- Effort: M. Status: verified by simulation (feasibility).

**T5. There are no batch tools for screening judgements.**

- Evidence: `assign.py reject` takes one ID per call (`tools/assign.py:346-372`), and expansion screens about 250
  candidates. Fringe verdicts are hand `Edit`s to rows of about 850 characters.
- Remediation: `reject` reads many `id<TAB>reason` lines from stdin; a `fringe.py judge` command writes verdicts.
- Effort: S. Status: likely.

**T6. There is no way to print one section of a survey.**

- Evidence: an agent editing its block of a 392 KB survey, or the main session writing the output, has to Read with
  offsets it does not know.
- Remediation: `check.py <topic> --print Clusters|Coreset[:<cluster>]|Open-work`, or line offsets in the check's
  printout.
- Effort: S. Status: likely.

**T7. There is no driver for the order of operations.**

- Evidence: the main session follows 37 rows from prose (`docs/process.md:51-89`). The tabletop found 22 places where
  that fails (A1–A9, S1–S12).
- Remediation: `check.py <topic> --next` prints the next row, with its command or brief template filled in (topic, step,
  scope, the printouts to hand over) and its done-when. It reuses the `--status` inference.
- Effort: M. Status: likely.

**T8. The test suites have blind spots.**

- Evidence:
  - `tests/gates/faults.py` never asserts that the unmodified fixture passes, so a requirement that always fails would
    count as "caught".
  - Untested branches: `g1.errored` without a retry outcome; `g1.rejected` stale-date; `g2.diagnosis-halts` for `H5`;
    `g5.converged` for `H11` and halted mismatch; history's pool removal and input-changed note.
  - `tests/gates/behaviour.py:22` is a no-op substitution, so the waiver test runs with an integrity failure present.
  - Neither suite uses try/finally, and both use the fixed topic `zz-gate`, so a crash leaves files and two runs
    collide.
  - No integrity check in `docs/tooling.md:24-44` has a dedicated test.
- Remediation: a baseline assertion, the missing cases, try/finally, and a unique topic name per run.
- Effort: M. Status: verified against code.

**T9. Seeds and package versions are not recorded.**

- Evidence: seeds 0, 1 and 1000+d are fixed in `tools/cluster.py:480`, `488` and `560`, and appear in neither `params`
  nor the log line. The inline dependencies at `tools/cluster.py:1-4` and `tools/match.py:1-4` carry no versions.
  `docs/process.md:297` says "reproducible only with its seed recorded".
- Why it matters: determinism holds today (a rerun reproduced the committed file). A future resolution of leidenalg,
  igraph or numpy could change results silently (likely).
- Remediation: record seeds and versions in `params`; pin the versions.
- Effort: S. Status: verified against code; the drift risk is likely.

### Z — overengineered framings or solutions, ranked by the scope of the simplification

**Z1 (whole spec). Stop growing the process before it has run, and move sequencing from prose into a driver.**

- Evidence:
  - The spec is about 190 KB, with 37 checklist rows, 6 gates, 13 halt conditions and about 70 gate requirements.
  - It was built and audited without a single coreset-layout survey: `reasoning` is legacy, and the gates have run only
    on a synthetic fixture.
  - The tabletop found 22 instruction failures, and the gate audit found about 19 holes.
- The simplification: freeze new features. Run a walking-skeleton pass (see the readiness section). Replace the prose
  checklist with `check.py --next` (T7). Replace whole-file spec reading with per-brief cards (W3). Let the run's
  failures set the agenda.
- Why it matters: most findings in this audit are friction between rules, not missing rules. Each new rule adds
  interactions. The tabletop found that the existing ones already collide: S1, S2, S3, S11, A4.
- Effort: L. Status: verified against docs and data (the layout and the tabletop findings).

**Z2 (verification). Make full text the quoted source, and drop `snippet` as a source level.**

- The simplification: always run `tools/fulltext.py` for every selected row. It is a free script; it fetched 27 papers
  in 90 seconds. Use `snippet_search` only to find where in the paper to look. Every evidence quote then comes from the
  fetched text, and G4 checks every quote, after M1 and C2.
- What it removes: the uncheckable-snippet branch (T1), the snippet-versus-full-text ordering question (S10), and most
  of the agent's discretion over when to fall back.
- What remains: `abstract` for papers with no fetchable text. That is mostly non-arXiv work, which is exactly the
  uncheckable case `docs/verification.md:76-83` already handles.
- Caveat: arXiv HTML is missing for some papers, and the PDF fallback has hyphenation and bibliography noise (C9).
  Expect some rows to need word-stem Grep.
- Effort: M. Status: verified against data (fetch feasibility); the full design is likely.

**Z3 (clustering). Fix the measure to `combined`, and drop the three-way choice and the tie rule.**

- Evidence:
  - Ties already go to `combined`, and it won outright on `reasoning` and in 12 of 12 replications.
  - The only `refs` win in the simulations is the degenerate 9-month pass (M9).
  - This removes two thirds of the compute, along with M9 and M10.
- Effort: M. Status: verified against data and by simulation.

**Z4 (clustering). Drop the null model, or keep one draw as a `no structure` guard.**

- Evidence: the null model is about two thirds of the runtime, 60 of 90 stability computations. On `reasoning` it never
  decided anything: the excess over the null was 0.54–0.64, far above the 0.15 threshold, and the null rule is not the
  default.
- Caveat: `--nulls 0` currently yields NaN curves through the empty-mean path, so this needs a small code change.
- Effort: M. Status: verified against data.

**Z5 (clustering). Defer the temporal history ("since when each cluster exists").**

- Evidence: nothing depends on it (`docs/process.md:379-380`). It carries an optimism caveat, and on `reasoning` four of
  six statements are hedged "probably", because the first snapshot's stability is 0.40.
- What it removes: a log line, a G2 requirement, a sheet section, viewer panels, and three clustering runs per pass.
- Effort: S–M. Status: verified against data.

**Z6 (gates). Simplify the history checks to what they can enforce.**

- Evidence: the cell-level edit and removal matching against HEAD is complex and leaky (C7, M7, M8). The commit boundary
  it relies on is not under the pass's control.
- The simplification: enforce two things exactly. First, the earlier log entries are byte-identical, against the
  pass-start commit recorded in the entry. Second, `source` never falls. Leave cell-level edits to the human diff review
  that commits already allow.
- Effort: M. Status: likely.

**Z7 (step 2). Remove the provisional clustering, which exists only to seed the `new` route.**

- Evidence: it adds a row, prints misleading diagnostics (A7), and breaks later passes (S3).
- The simplification: seed the recommendations from the frontier candidates and the most-cited pool papers instead of
  from clusters. Semantic Scholar's recommendations endpoint accepts a list of positive seed papers (likely; not checked
  in this audit). The `new` route's per-cluster balance would be lost, which is acceptable for a candidate generator.
- Effort: S–M. Status: likely.

**Z8 (docs). Move the experiments out of the core docs.**

- Evidence: `tools/recursive.py`, `match.py simulate` and `fringe.py analyse` take sections of `docs/tooling.md` and
  rows of the `docs/formats.md` graphs table, which every agent reads.
- Effort: S. Status: verified against docs.

**Z9 (smallest). Fold the minor diagnostics into the report text.**

- Evidence: `unstable cluster` and `broad scope` drive no action. `thin cluster` and `clusters trade papers` do.
- Effort: S. Status: verified against docs.

Not proposed for simplification: the roles and the sizing rules. They are what makes the output's Landscape and
Assumptions sections possible. The graph viewer is large (a 1,664-line template plus vendored libraries) but off the
critical path; freeze it rather than cut it.

## The verification concept, in one place

The chain from paper to user has five links. Here is the state of each.

1. `Selection drafts the row from the abstract.` This is acceptable as a draft. The dissent quote is taken from the
   abstract, so it is checked only if verification re-confirms the role, which `docs/verification.md:32-33` requires. No
   gate confirms it (M4).
2. `Verification checks each cell against body text.` The cell list is right, and the rule that dimensions are
   re-derived, not copied, is a good one. But the agent that re-derives sees the drafted values, so anchoring is likely.
   Evidence is required for only three kinds of cell (S10).
3. `Evidence is recorded verbatim.` For `full-text`, matching exists but accepts vacuous quotes (M1). It is skipped when
   the file is missing (C2), and never cross-checked against the row's `source` (M2). For `snippet`, the default source,
   nothing is checkable (T1). On the existing data, no evidence file exists at all: the legacy survey predates
   `evidence/`.
4. `The output cites only verified rows, with markers.` The marker check works. All 12 abstract-sourced papers cited in
   `outputs/reasoning.md` are marked at every citation. But no check ties an output sentence to its row (T2).
5. `Someone measures whether 1–4 are right.` Not built (T3).

The upshot: the gate proves that a verification ritual happened, not that verification succeeded. The cheapest large
improvement is Z2 with M1, M2 and C2, all effort S to M, which makes link 3 mechanical. The most informative addition
for the first run is T3, because it puts a number on links 2 and 4. Until then, "publication grade" is an aspiration,
not a measured property.

## Part (c): readiness for the first end-to-end run

### Blocking: fix before the run

- `S1` — the Dimensions owner and timing. Any input without dimensions fails `G0`.
- `W1` — the index entry for `dispatch.md`. Otherwise agents do not read their briefs.
- `S2`, `S6`, `C1` — the post-`G1` additions, the zero-rejections rule, and the Bridges trigger. Each one trips a
  rule-following main session.
- `M3`, `M1`, `M2`, `C2`, `C3` — the cheap gate holes. Without them, a passing G4 or G5 means little.
- `M19` — narrow the Stop hook, before background agents edit the survey.
- `A1`, `A2`, `A3` — minimal rubrics for scope, frontier and dissent, and the coverage verdict, plus a recorded sample.
- The topic name. If the run reuses `reasoning`, commit the rename of the legacy survey first. Otherwise history fails
  on both legacy entries and on every removed row (verified by simulation, against HEAD). This audit could not confirm
  the plan to reuse the name; it is inferred from `docs/tooling.md:244-245`.

### Strongly advised

- `Z2` — full-text-first verification.
- `T3` — a blind re-verification sample.
- `S11` — `Tokens` appended per dispatch, so that W3's spec-reading cost is measured rather than estimated.
- `M11`, `M12` — fix the fringe score before the `fringe` role is filled from it.
- `S3`, or `Z7` — only if the run is a later pass.

### How to run it

Run `reasoning` again in the coreset layout. The legacy survey (195 rows) and its output give a reference point. The
question to answer is how many of the legacy output's claims a coreset of about 50 rows reproduces, and which ones it
loses. That is the first real evidence on sufficiency and minimality the repo would have. Expect about 1–1.5M tokens,
plus about 0.5M for spec reading (W3).

Record per-dispatch tokens, every halt, and every place the agent improvised. Each improvisation is a spec bug.

## Checked and found to hold

Gates and checks:

- Both gate test suites pass: `tests/gates/faults.py` catches 48 of 48 faults (20.5 s), and `tests/gates/behaviour.py`
  shows 20 of 20 behaviours (4.4 s). Both clean up after a successful run.
- Every G0–G5 requirement in the `docs/gates.md` table has a function in `tools/gates.py`, and each has at least one
  fault test, apart from the exceptions in S1, S6 and C5.
- A pending halt makes `--gate` fail. `H1` satisfies `g0.preflight`. A waiver is reported, not failed. `--gate G9` is a
  usage error (exit 2).
- History fails, as specified, on:
  - a really changed earlier entry;
  - an unrecorded coreset removal;
  - `source` lowered from snippet to abstract;
  - an uncorrected edit to a verified cell.
- An abstract-sourced row may be rewritten freely. A correction logged in an earlier pass does not satisfy the edit
  check.
- The first-pass safety net infers G3 from verified rows, and G4 from an output alone.
- `check.py` makes no network calls: its only subprocess is a local `git show`. It runs in 0.05 s on `reasoning`, and
  0.27 s with `--gate G5` on the fixture.
- On the legacy `reasoning` survey, `check.py` exits 0, and the output-marker checks apply. All 12 abstract-sourced
  cited papers are marked at every citation, and the legend precedes the first `##`.

Clustering and fringe, spec against code:

- The three measures, k=10, Leiden with resolution bisection counting clusters of two or more, the grid, the
  quarter-pool cap, and `STOP: H8` under 12 papers.
- Stability as the mean of holdout and resampling ARI, with 3/6/9-month cutoffs × 3 seeds, the 30% skip, 20% resampling
  × 20, and 5 seeds reported only.
- Clusterwise Jaccard, excluding clusters under 3 papers; τ=0.75 with the ±0.05 report.
- The null-model construction; the thresholds 0.15, 0.9, 0.6, 10 papers and 20%.
- The fringe score's structure, before M11 and M12.
- The history's four equal-count segments, five seeds, majority rule, first-seen rule, and the hedges.
- Late assignment by k-NN vote with the text fallback, against clustered papers only; the 10% refusal with exit 3;
  `remap` carrying matched names and refusing `clusters` until it has run.
- The fringe routes' definitions; candidates without embeddings dropped; the sheet shuffled.

Determinism and printouts:

- A default rerun of `cluster.py` reproduced the committed `graphs/reasoning/clusters.json` exactly, apart from
  `generated`. The `history` block equals `history.json`.
- The printed `Clustering`, `Temporal stability`, `Pool`, `Fringe`, `Late papers` and preflight lines match
  `docs/formats.md:117-144`.

Scripts and plumbing:

- Scripts documented as `python3` run without numpy, because their heavy imports are lazy. Those documented as `uv run`
  need it.
- Exit codes: `check.py` 1 and 2; `preflight.py` 1 with `STOP: H1`; `cluster.py` `STOP: H8`; `late` exit 3 with
  `RECLUSTER:`; `fulltext.py` exit 0 on an unfetchable paper.
- Paper IDs: pre-2007 arXiv IDs work end to end. `math.GT/…`, versioned IDs and the `arXiv:` prefix are refused. A
  `CorpusId` for a paper with an arXiv ID is refused, and the error names the arXiv ID. An unknown ID is listed for Open
  work. Duplicates under two IDs, and identical titles, fail; near-identical titles get a note.
- `net.py` makes 8 attempts on 429/5xx, dropped connections and timeouts. `bib.py` and `fulltext.py` retry as
  documented, and space arXiv requests 3 s apart.
- `fulltext.py`: HTML first, PDF fallback with the `(pdf)` header and `[page N]` markers, existing files kept.
- `bib.py` keeps entries verbatim, drops removed papers, and writes `eprint` or `corpusid`.
- Privacy: no key, email or user identifier is sent in any request or `User-Agent`. `asta_config.py` never prints the
  key.
- Hooks: the session-start hook runs `asta_config.py`; `mcp__asta__*` is pre-approved.
- The viewer claims spot-checked in the template hold: hash state, the histogram, the similarity map, the level slider,
  hollow and tinted hues, "Since when".

Data claims in the docs:

- About 2 minutes per 200 papers: 1m45s for 195.
- 3,772 distinct cited papers and 7,760 references.
- 116 fringe candidates on `reasoning` (hidden 60, new 56).
- ARI 0.70 after adding fringe candidates (0.699), though see S9.
- Sheet sizes of 2.8k and 0.8k tokens (2,790 and 817).
- `pool.json` about 400k tokens (1.63 MB). The file sizes in the `docs/formats.md` graphs table are within 5%.
- The full texts of the 27 abstract-sourced rows came from HTML, at about 9–68k tokens each.

Docs and the existing output:

- Every quoted brief name in the order of operations exists in `docs/dispatch.md`. Every `docs/X.md ("Section")`
  reference resolves, though W4 notes that some resolve to bold labels.
- Three spot-checked claims in `outputs/reasoning.md` match their survey rows, including the numbers (8.5–13.0 and
  2.5–5.0 points; the 3.6:1 ratio; 2.14% to 9.27%).
- Asta's `get_paper` returns the same Semantic Scholar `paperId` as the scripts' `pool.json` for `2408.03314`. This
  supports the corpus claim in `docs/external_services.md`.

## Appendix: log line → writer, according to each doc

`!` marks a conflict or a gap.

- `Gates`
  - `process.md`: main, at the gate rows.
  - `dispatch.md`: main.
  - `formats.md`: main, via `gates.md`.
- `Preflight` `!`
  - `process.md`: the Preflight agent; the script row writes "—".
  - `dispatch.md`: the brief has the agent write both halves, but the main-session rules give script-printed lines to
    main.
  - `formats.md`: the script half is paste-ready; the writer is unstated.
- `Orientation`, `Recency window`, `Expansion`
  - `process.md`: Orient, Orient, Expand.
  - `dispatch.md`: the same.
  - `formats.md`: unstated.
- `Errored queries` `!`
  - `process.md`: Expand only.
  - `dispatch.md`: Expand only.
  - `formats.md`: unstated; `external_services.md` has whoever meets an error write it, at any step.
- `Fringe`, `Pool`, `Late papers`
  - `process.md`: main.
  - `dispatch.md`: main.
  - `formats.md`: printed by script.
- `Clustering`, `Temporal stability`
  - `process.md`: printed by main's script run, written by Naming.
  - `dispatch.md`: Naming.
  - `formats.md`: printed by script; the writer is unstated.
- `Clustering rationale`
  - `process.md`: Naming.
  - `dispatch.md`: Naming.
  - `formats.md`: unstated.
- `Clusters` `!`
  - `process.md`: Naming.
  - `dispatch.md`: Naming.
  - `formats.md`: unstated. The user's review would update it after `Ended`, which is not allowed.
- `Dimensions` `!`
  - `process.md`: main, at step 0.
  - `dispatch.md`: main.
  - `formats.md`: proposed "at step 3", by an unnamed writer.
- `Dissent searches`, `Demotions` `!`
  - `process.md`: the Selection agents write them directly.
  - `dispatch.md`: parallel agents return them under `Log:`, and main writes them.
  - `formats.md`: unstated.
- `Coreset`
  - `process.md`: main, at step 5.
  - `dispatch.md`: main.
  - `formats.md`: from a script count.
- `Corrections to existing rows` `!`
  - `process.md`: the Verification agents.
  - `dispatch.md`: returned by parallel agents, written by main. Merges have no writer.
  - `formats.md`: unstated.
- `Coverage test` `!`
  - `process.md`: the Coverage agent.
  - `dispatch.md`: the Coverage agent.
  - `formats.md`: the round format, which the example at `process.md:571` lacks.
- `Probes` `!`
  - `process.md`: no row.
  - `dispatch.md`: the Probe agent.
  - `formats.md`: unstated.
- `Tokens` `!`
  - `process.md`: main, at the end only.
  - `dispatch.md`: main.
  - `formats.md`: per dispatch.
- `Halts` `!`
  - `process.md`: main, on a halt. No row writes "none", which G5 requires.
  - `dispatch.md`: main.
  - `formats.md`: unstated.
- `Waivers` `!`
  - `process.md`: no row.
  - `dispatch.md`: main.
  - `formats.md`: main, via `gates.md`.
- `Ended`
  - `process.md`: main.
  - `dispatch.md`: main.
  - `formats.md`: unstated.
- Open work, "Clusters not yet reviewed" `!`
  - `process.md`: no row.
  - `dispatch.md`: main.
  - `formats.md`: unstated. G2 requires it when Naming writes "not yet reviewed".

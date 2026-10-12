# zz-sim step-7 simulation report

## 1. Run log

- `pre` — `python3 tools/check.py zz-sim --status` — exit 0; G0–G4 passed, G5 open on `g5.coverage`, `g5.judgement-audit`, `g5.end-lines`.
- `7 Draw the coverage sample (R=1)` — `uv run tools/coverage.py draw zz-sim 1` — exit 0; 10 candidates, seed 1, from 44 worst-covered of 176; radius max 0.451, p90 0.215, mean 0.112.
- `7 Coverage test (R=1)`, played as `survey-pass` "Coverage test" — read the brief's `Read` list plus "When a pass ends" and `.claude/agents/survey-pass.md`. Recency query IMAGINED: WebSearch "chain-of-thought monitoring evasion reasoning models" limited to 2026-04-09..2026-10-09, one result kept: `2609.31121` (real arXiv ID; title "Monitor Jailbreaking: Evading Chain-of-Thought Monitoring Without Encoded Reasoning"); abstracts via Asta IMAGINED. `coverage.py judge zz-sim 1` (10 verdicts) exit 0; `judge --recency` (1 row) exit 0; `assign.py add zz-sim 2609.31121` exit 0 (one 429 retried); `coverage.py line zz-sim 1` exit 0: "round 1: 3 of 11 sampled candidates changed the output (2506.14374: Assumptions, 2605.27901: Assumptions, 2609.31121: Gaps); new clusters: none"; bound 51%. Line written to the log by the agent (it ran alone).
- `any After every dispatch` (after Coverage test) — pool rows added after step 3, so the row says `assign.py late` before the check; the plain check run first (to see the state) exited 1 on `g1.fetched` and `g1.pool-line` for 2609.31121, as `docs/gates.md` predicts.
- `any After every dispatch` (cont.) / `7 Late papers` — `uv run tools/assign.py late zz-sim` — exit 0; fetched 1 paper, `Pool: 196 papers in scope, 196 with an arXiv ID; metadata fetched 2026-09-29 to 2026-10-10`; `Late papers: ... (2609.31121 -> two) ... 1 of 196 (1%)`; no `RECLUSTER:`. Pasted `Pool`, `Late papers`, appended `Tokens` (imagined 40k). `python3 tools/check.py zz-sim` exit 0 (next G5; new anchor/in-degree notes because the refetch filled the `cites` column).
- `7 Revise` -> `4 Set up the coreset blocks` — no return to step 3, blocks already match the Clusters table; nothing to do.
- `7 Revise` -> `4 Select per cluster`, played as `survey-pass` "Selection" (clusters two, three), handed 2605.27901 (Assumptions, proposed `dissent` in two), 2609.31121 (Gaps tension, proposed `dissent` in two, its late cluster), 2506.14374 (Assumptions, cluster three is `medium` so `frontier`). Cells drafted from IMAGINED Asta abstracts, `source` `abstract`. (My first insert script also hit the Pool table — my own scripting error, fixed; not a spec finding.) `python3 tools/bib.py zz-sim` exit 0 (22 entries, 3 fetched); main wrote Open work `Rows needing verification`, `Coreset: 22 rows`, `Tokens`. `tools/check.py` exit 1 on `g4.h10` only (23% abstract) — the expected Revise open work.
- `7 Revise` -> `4 Bridges` — skipped: the check notes no trading pair without a bridge.
- `7 Revise` -> `4 Rewrite the sheets` — `python3 tools/sheets.py zz-sim` exit 0.
- `7 Revise` -> `4 Fringe` — skipped: no counted paper takes a `fringe` role (guess; see findings).
- `7 Revise` -> `5 Fetch the full texts` — `uv run tools/fulltext.py zz-sim --abstract` exit 0; fetched 5 HTML texts: the 3 new rows plus 2501.12948 and 2503.11926, which Open work listed as "no body text".
- `7 Revise` -> `5 Characterise and verify`, played as `survey-pass` "Verification" (rows 2605.27901, 2609.31121, 2506.14374 only) — real reading via `fulltext.py show`; three evidence files written; rows rewritten to `full-text`. The imagined abstract drafts were wrong on several cells (2605.27901 `measures` monitorability -> faithfulness, `pressure` none -> prompt-level; 2609.31121 `pressure` prompt-level -> monitor-in-reward, `method name` n/a -> monitor jailbreaking). Verification also showed my round-1 reason for 2506.14374 ("no accuracy gain") overstated: the paper says accuracy is "not degraded" and sometimes improves. Re-ran `coverage.py judge zz-sim 1` for that row: it silently overwrote the verdict (exit 0); regenerated and replaced the `Coverage test` line. `bib.py` exit 0; `check.py` exit 0 (9% abstract).
- `7 Revise` -> `5 Replace uncheckable rows` — none uncheckable; skipped.
- `7 Revise` -> `5 Bibliography, checks and sheets` — `bib.py` exit 0, `check.py` exit 0, `sheets.py` exit 0.
- `7 Revise` -> `6 Write the output` — added two Assumptions claims (2506.14374, 2605.27901) and one Gaps tension (2609.31121), checked against the evidence files; `check.py` exit 0.
- `7 Draw the judgement audits` / `Re-verify` / `Judge the audits` — skipped for round 1: the round did not converge (K=3).
- `7 End the round` (R=1) — K papers 2506.14374, 2605.27901, 2609.31121 are all assigned coreset rows; not F1 (3 output changes), one unconverged round so far, so another round.
- `7 Draw the coverage sample (R=2)` — `uv run tools/coverage.py draw zz-sim 2` exit 0; 10 candidates, seed 2, from 42 worst-covered of 166; radius max 0.449, p90 0.203, mean 0.101.
- `7 Coverage test (R=2)`, played as `survey-pass` — IMAGINED recency WebSearch over the same window returned only papers already in the pool, so no recency row (nothing records that the query ran). `coverage.py judge zz-sim 2` exit 0; `coverage.py line zz-sim 2` exit 0: "round 2: 1 of 10 ... (2608.20290: Assumptions ...); new clusters: none"; bound 39%. No pool rows added (2608.20290 already in the pool, cluster one). Line written as a second `Coverage test` line under the first. `check.py` exit 0.
- `any After every dispatch` — no pool rows added, coreset unchanged: only `Tokens` appended and the check (exit 0).
- `7 Late papers` (R=2) — `uv run tools/assign.py late zz-sim` exit 0; "no late papers to assign", printed a `Pool` line identical to the current one and no `Late papers` line; log left as is.
- `7 Revise` (R=2, converging round with K=1) — played `survey-pass` "Selection" (cluster one): 2608.20290 drafted as `dissent` from an IMAGINED abstract; main wrote Open work, `Coreset: 23 rows`, `Tokens`; `bib.py` exit 0; `check.py` exit 1 on `g3.dissent-quoted` (my draft lacked a quoted claim) and `g4.abstract-listed` (my own edit missed Open work); both fixed. Bridges, Fringe: skipped. `fulltext.py zz-sim --abstract` exit 0 (1 fetched, 2 cached). Played "Verification": the real text supports the dissent (self-training arms do not gain on low-base problems; authors limit it to their regime); evidence file written, row to `full-text`. `bib.py`, `check.py`, `sheets.py` exit 0. Output: one Assumptions claim added; `check.py` exit 0.
- `7 Draw the judgement audits` — `python3 tools/audit.py reverify zz-sim` exit 0 (5 rows, seed 1: 2201.11903, 2312.06942, 2312.08935, 2503.08679, 2608.20290); `python3 tools/audit.py trace zz-sim` exit 0 (9 of 9 citing sentences, seed 1).
- `7 Re-verify the sample`, played as `survey-pass` "Re-verification" — not blind in this simulation (I wrote 2608.20290's row); filled 45 cells with `audit.py fill` exit 0.
- `7 Judge the audits` — `audit.py compare zz-sim` exit 0 (45 cells); played "Judgement audit": `audit.py judge zz-sim reverify` exit 0, `audit.py judge zz-sim faithfulness` exit 0; `audit.py line zz-sim` exit 0: "re-verification: 23 of 45 cells agree, 10 partly, 12 differ, over 5 rows (seed 1); faithfulness: 4 of 9 sentences supported, 3 partly, 2 unsupported (seed 1)". Line written; `check.py` exit 0. The 12 `differ` cells (method name, elicitation and pressure on the four synthetic rows) and the 2 `unsupported` sentences (S2, S6, both on synthetic rows) are for the user.
- `7 End the round` (R=2) — F1: no new cluster, 1 output change; 2608.20290 is an assigned coreset row. No user review of the clusters available, so `Clusters` stays "not yet reviewed". Wrote `Ended: finished (F1); ...` with the round-2 bound (39%) and radius (max 0.449, p90 0.203, mean 0.101).
- `7 Gate G5` — `python3 tools/check.py zz-sim --gate G5` exit 0, "all passed"; added `G5 2026-10-10` to `Gates`. Afterwards I rewrote the now-false Open work reason "no body text" for 2501.12948 and 2503.11926 (see findings); G5 re-run, exit 0.
- Probe (not a pass step): restoring round 1's stale `Coverage test` line, whose reason no longer matched the sheet, still passed `--gate G5`. I then restored the current line.

## 2. Findings

### Blockers

- None. Every row could be run, and no gate failed for a reason the spec does not explain.

### Guesses

- `guess` — `docs/process.md`, step 7 "Revise", and its paragraph "While Revise is under way". The spec says Revise is done "when `tools/check.py` passes again". But after round 1's Coverage test and `assign.py late`, the plain check already passed (exit 0) before any counted paper was a coreset row. Only `G5` catches a counted paper missing from the coreset. So "check passes" cannot tell you Revise is done. Fix: once a `Coverage test` line exists, make the plain check fail on each counted ID that is not yet a coreset row, as `G5` does.
- `guess` — `docs/process.md` order of operations, "End the round". It says "another round", but not where to re-enter the table. The audit rows sit between Revise and End the round, gated on convergence. I skipped the audits after round 1 and went back to "Draw the coverage sample" with R=2. Fix: in "End the round", write "on a round that did not converge, return to 'Draw the coverage sample' with R+1, skipping the audit rows".
- `guess` — `docs/process.md`, step 7 item 1, and the Coverage test brief, on the recency window. Should the "fresh recency query" use the pass's recorded `Recency window` (it ends 2026-10-09, before step 7 ran) or a window extended to today? I used the recorded window. Fix: say "the pass's `Recency window`, extended to the day of the round".
- `guess` — `docs/process.md`, step 7, and `docs/formats.md`, "The coverage sheet". The fresh recency query (its text, window and result count) is recorded nowhere. In round 2 my imagined query returned nothing new. The sheet therefore has no recency rows, and that cannot be told apart from a round where the query was never run. This breaks "every judgement leaves a trace" and the errored-query rules. Fix: have `coverage.py` record a `recency query: "<q>" (<window>): <n> results, <m> kept` header line on the sheet, or add a part for it to the `Coverage test` line.
- `guess` — `docs/process.md`, step 7, "Every candidate counted in K joins the coreset ... in the role that matches what it changed". The mapping covers a contradiction or broken assumption, a newer result, a connection, and a new idea. It does not cover a `Gaps` change that is a tension: 2609.31121 is a monitoring result that contradicts the monitoring cluster. I chose `dissent`. Fix: map each target change type to a role, including `Gaps` tensions and stated open problems.
- `guess` — `docs/process.md`, step 4 "dissent", and `docs/formats.md`, `Dissent searches`. The three dissent rows added in Revise came from coverage rounds, not from a dissent search. The spec does not say whether they need a `Dissent searches` entry, and no gate asked for one. I left `Dissent searches` unchanged; their trace is the `Coverage test` line and `selected because`. Fix: say so explicitly, or define an entry form such as `two: coverage round 1 -> found: <id>`.
- `guess` — `tools/coverage.py judge` against `docs/tooling.md` "Coverage", and the Verification brief. Verification showed my round-1 reason for 2506.14374 was overstated: I wrote "no accuracy gain", but the paper says accuracy is "not degraded" and sometimes improves. No brief says how a verified fact flows back into a coverage verdict. Re-running `judge` silently overwrote the verdict (exit 0, no message). `G5` does not compare the `Coverage test` line's reason text with the sheet: the stale line still passed. Fix: (a) have `judge` print "replaced verdict for <id>"; (b) state that Revise re-judges a counted candidate whose reason verification contradicts, then re-pastes the line; (c) have `G5` compare the whole line with `coverage.py line`'s output, as it does for `Judgement audit`.
- `guess` — `docs/process.md`, "Revise" ("the step 4–6 rows"), and the Fringe row ("once"). It is unclear which step-4 rows rerun when no counted paper takes their role, such as Fringe selection. I skipped Fringe and Bridges (the check noted no trading pair). Fix: say that Revise runs Selection for the counted papers, Bridges only on the check's note, Fringe only for a counted paper proposed as `fringe`, and then the fetch, verify, bib, check, sheets and output rows.
- `guess` — `docs/process.md`, step 5 "Fetch the full texts" inside Revise, and the Verification brief. `fulltext.py --abstract` fetched every `abstract` row, including 2501.12948 and 2503.11926. Open work lists both as "no body text", and arXiv now served their HTML. Revise is scoped "for the papers the round counted in K", so I verified only those. That leaves two rows `abstract` whose full text is on disk, and an Open work reason that had become false. I rewrote the reason. Fix: say whether Revise's Verification also takes every `abstract` row that the fetch now has text for. Alternatively, have `fulltext.py` print "now fetchable: <ids>" for rows listed as uncheckable.
- `guess` — `docs/process.md`, "Cluster review" and the "End the round" row ("the user's review of the clusters, if given"). Should the main session wait for the user's review before writing `Ended`? "Cluster review" says the review happens "before writing `Ended`", but the row says "if given". I wrote `Ended` without a review, and `Clusters` still reads "not yet reviewed". `G5` accepted this. Fix: say plainly whether `Ended` waits, or that an absent review is recorded as "not yet reviewed" and moves to the next pass.
- `guess` — `docs/process.md`, "Auditing the judgements", the faithfulness rubric. It does not cover sentences that make no claim about the paper's content, such as `Reading` "2606.28438 — start here" or `Questions` "Builds on 2506.09401". I judged them `partly`. Fix: exclude `Reading` and `Questions` entries from `trace`, or give the rubric a rule for recommendation sentences.
- `guess` — `docs/formats.md` `Ended` ("<the measured numbers>") and `docs/process.md` step 7 ("Give the bound and the radius of the last round in `Ended`, with the measured numbers"). Which numbers count as "measured" is left open. I gave round 2's K of N, new clusters, bound, radius (max, p90, mean), the number of rounds and the coreset size. Fix: give the exact form.

### Minor

- `minor` — the Coverage test brief and the order-of-operations row both write "Pool rows, by `tools/assign.py add`, for each candidate that changed a target". Drawn candidates are pool papers already (`add` printed "2 already there", a no-op). Only recency candidates need adding. Fix: "for each recency candidate that ...".
- `minor` — `tools/coverage.py judge --recency` does not match `docs/formats.md`, "The coverage sheet" (`paper`: "title, linked by its ID"). It wrote the bare ID as the link text (`[2609.31121](...)`), and it accepted the ID without checking that the paper exists. Fix: fetch the title, or have the docs allow the ID.
- `minor` — order of operations: after the Coverage test dispatch, the "After every dispatch" row runs `assign.py late`, and so does the next row, "Late papers". One run satisfies both. Fix: note that the Late papers row is that fetch.
- `minor` — the Selection brief's `Read` list (Revise use) leaves out `docs/process.md` "Step 7: the coverage test". That section holds the role rule for counted papers, including `frontier` when the cluster is not `high`. Played as Selection, I relied on the main session handing over the role. Fix: add that paragraph to the brief's `Read` list for Revise.
- `minor` — `G2` does not check that a `high` cluster's definition has the second sentence, its central claim. Clusters `one` and `two` have none here, so step-7 `dissent` rows have no stated claim to contradict. Fix: add a `g2` requirement for it.
- `minor` — `tools/check.py --gate G5` prints "G5 passed: add `G5 <today>` to the log's `Gates` line" even when `Gates` already lists G5 (its own header shows `declared ... G5`). Fix: print it only when G5 is missing.
- `minor` — `coverage.py line` concatenates the full reasons, so each entry ends ".," (for example "does not state., 2605.27901: ..."). Fix: strip the trailing period.
- `minor` — `docs/formats.md`, "1. Retrieval log", says `Halts` and `Waivers` are written as `none` when the entry is created. This entry has no `Waivers` line, yet G0–G5 all passed. Fix: have `G0` (or `G5`) require `Waivers`.
- `minor` — `docs/tooling.md` "Judgement audits" says `trace` draws 15 sentences. The output had only 9 citing sentences and `trace` took all of them. The docs do not say this. Fix: "15, or all if fewer".

### Briefs played: unclear parts

- `Coverage test` — which recency window applies, where the query is recorded, and which candidates need `assign.py add` (see above).
- `Selection` (Revise) — the role for a `Gaps`-tension change, whether coverage-found dissent goes in `Dissent searches`, and the step-7 role rule missing from `Read`.
- `Verification` (Revise) — whether it takes the old `abstract` rows whose text is now fetched, and what to do when verification contradicts a coverage verdict's reason.
- `Re-verification` — clear. Blindness cannot be simulated when one agent plays every role.
- `Judgement audit` — the rubric for `Reading` and `Questions` sentences.

### Notes

- External retrieval was imagined: the WebSearch recency queries in both rounds, and the Asta abstracts behind the Selection drafts. Full texts were fetched for real by `tools/fulltext.py`, and verification used them. The imagined abstract drafts got several cells wrong, and real verification corrected them.
- Token figures added to `Tokens` for the played dispatches are imagined estimates.

## 3. Final `python3 tools/check.py zz-sim --gate G5`

```
layout:  coreset
coreset: 23 rows, 23 unique paper IDs
columns: 14 across 6 block(s)
source:  {'abstract': 2, 'full-text': 21}
arXiv:   23 of 23 coreset papers have an arXiv ID
         9% abstract-sourced; after step 5, more than 20% halts the pass (H10)
evidence:    empirical 23
measures:    capability 21, faithfulness 1, monitorability 1
elicitation: elicited 22, observational 1
pressure:    none 19, n/a 2, prompt-level 1, monitor-in-reward 1
clusters: 6 (high 2, medium 2, low 2)
pool:    196 papers, 196 with an arXiv ID
  one [high]: pool 64; coreset anchor 1, dissent 2, fringe 4, frontier 2
    in-degree leader(s) within the pool: 2501.12948 (41)
  two [high]: pool 40; coreset anchor 1, bridge 1, dissent 3, frontier 1
    in-degree leader(s) within the pool: 2507.11473 (35)
  three [medium]: pool 30; coreset anchor 1, frontier 2
    in-degree leader(s) within the pool: 2312.06942 (17)
  four [medium]: pool 29; coreset anchor 1, frontier 1
    in-degree leader(s) within the pool: 2201.11903 (82)
  five [low]: pool 28; coreset anchor 1
    in-degree leader(s) within the pool: 2402.03300 (69)
  six [low]: pool 5; coreset anchor 1, fringe 1
    in-degree leader(s) within the pool: 2605.23950 (1)
bib:     23 entries
output:  9 cited IDs
gates:   pass of 2026-10-09; declared G0 G1 G2 G3 G4 G5; required G0–G5; all passed

note  one: anchor ['2501.12599'] is not the in-degree leader ['2501.12948'] (41); fine if deliberate
note  two: anchor ['2503.08679'] is not the in-degree leader ['2507.11473'] (35); fine if deliberate
note  four: anchor ['2110.14168'] is not the in-degree leader ['2201.11903'] (82); fine if deliberate
note  five: anchor ['2312.08935'] is not the in-degree leader ['2402.03300'] (69); fine if deliberate
note  1 abstract-sourced paper(s) cited in the output: ['2501.12948']
note  G5 passed: add `G5 <today>` to the log's `Gates` line
OK
exit 0
```

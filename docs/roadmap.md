# Roadmap: open items

Everything in this file is open: decisions still to take, fixes, known gaps, proposals, and claims to verify. None of it
is spec; do not follow an item in a pass until it is moved into the relevant `docs/` file. Each item carries the context
it needs, and only that. When an item is done, adopted into the spec, or dropped, delete it; git history keeps the
record, including the findings and decisions that were once kept here.

## Decisions needed before the next real pass

### How a previous survey's papers enter the pool

`CLAUDE.md` says a survey listed as `Context` in an input is a source, not a template: its papers enter the new pool and
are re-clustered from scratch. No procedure says how they enter. Options: the main session adds them by script, as in
scope; or they are screened against the new input like any other candidate, with rejections recorded. Screening is
recommended, since the new input may scope the topic differently. Needed for the fresh coreset run, whose input lists
the old survey as `Context`.

### Reused verified rows and the evidence gate

`CLAUDE.md` lets a verified row be reused without re-verification, since verification belongs to the row, not to the
survey it came from. But the `G4` gate (`g4.evidence`, `docs/gates.md`) requires every verified row to have an evidence
file with verbatim quotes from the fetched full text, and the 195 rows of `reasoning-legacy` have none: their evidence
was never kept, and 168 of them were verified from snippets, which `G4` no longer accepts. As written, every reused row
would fail `G4`. Scheduled for after the first run (audit of 2026-10-09, `S13`). Options: re-verify reused rows (about
10k tokens each); accept an evidence file that records the reuse (the survey and date it was verified in, evidence not
kept), listed in a note and sampled first by the `G4` judgement audit, if adopted (recommended); or waive the
requirement per row.

## The fresh coreset run

The first real pass, run end to end on `reasoning`, as a measured simulation of the whole method: what goes to plan and
what does not. It runs as a simulation audit (`docs/audits.md`): a narrow topic first, iterated segment by segment, then
`reasoning` as a confirmation run, then a wide topic. The handover is in `.audits/2026-10-09-spec/disposition.md`,
"Phase 5: handed to a simulation audit". The legacy survey is now `reasoning-legacy`, and `inputs/reasoning.md` is the
input for the rerun.

- `Measure` — pool size against coreset size, per cluster and in total; tokens per dispatch against the estimates in the
  order of operations (`docs/process.md`); every gate failure and halt, and what resolved it; every place the main
  session or an agent improvised, each a spec bug; and the judgement-audit agreement rates, where built.

## Small fixes

- `Viewer labels` — on the citation map, the large group labels overlap nodes where the map is dense.

## Known gaps, not yet built

### Theme searches, and the Semantic Scholar key

`tools/expand.py collect` searches each theme on the Graph API's bulk endpoint, `/paper/search/bulk`: the theme as an
exact phrase in title or abstract, keeping the 50 most-cited matches. It moved there on 2026-10-13, when the relevance
search endpoint, `/paper/search`, refused every unauthenticated call for about two hours while the other endpoints
answered (simulation audit, `pool` iteration 2, `E21`). The two differ: relevance ranking finds papers that word a theme
differently, while an exact phrase finds only papers that use it, and sorting by citations favours older work. A theme
that is a description rather than a phrase papers use matches little or nothing: 4 of 9 themes tried on `model-collapse`
matched none (the auditor's probes, recorded under `E21` in the simulation audit's `segments/pool.md`).

- `The key` — the user applied for a Semantic Scholar API key on 2026-10-13; an answer may take two weeks. With it,
  every script gets a rate limit of its own (1 request per second, introductory). Using it changes the spec's statement
  that no key or user identifier is sent (`docs/external_services.md`, "Credentials and privacy"), which the user
  approves when the key arrives. Every script must then pace itself to the key's limit.
- `The comparison` — once the relevance endpoint answers reliably, run both on the same themes of a real pass, and
  compare: the overlap of the two result sets; how many of each are judged in scope; what each finds that traversal did
  not; and how many themes match nothing as a phrase. Then choose one, or keep both, with the reason in the spec.
- `Meanwhile, watch` — whether orientation writes its themes as phrases papers use, now that the Orient brief asks for
  it, and how many themes the `Expansion` line shows matching nothing.

### Discovery lag

A paper on arXiv but not yet in Semantic Scholar is invisible to Asta, and `tools/pool.py` cannot fetch its embedding or
references. A search of arXiv's own listings during orientation would find it; clustering would still need a fallback.

### Matching clusters across passes

So that cluster ids and names persist across passes, and splits, merges and vanished clusters are logged. Partly built
(2026-10-08): `tools/cluster.py` matches every new clustering to the previous one with `match()`, prints the changes on
one `changes:` line, and `tools/assign.py remap` carries names over to matched clusters; tested on a swapped-id fixture.
What remains: the diagnosis for when most clusters fail to match (below; the spec has an interim rule, in
`docs/process.md`, "Matching clusters across passes"), and the seeded-clustering option. The design so far (2026-10-05):

- `No guarantee` — a later pass can produce a different clustering: the level can change, new papers change the
  similarity scale, the graph and the resolution, and the field can genuinely restructure. Matching is possible because
  a later pass keeps the old papers, so clusters are compared by members on the shared papers, never by name. The time
  holdout already simulates an earlier pass, so per-cluster stability predicts which clusters will match.
- `Many-to-many and graded` — each old cluster is `matched`, `split`, `merged`, `absorbed` or `vanished`; each new
  cluster not accounted for is `new` (mostly new papers) or `reshuffled`. Rules in the `tools/match.py` docstring; the
  majority threshold (0.5) and the 3-paper fragment limit are first guesses. Matched clusters keep id and name.
- `When most clusters fail to match`, report it, and tell the two causes apart: cluster the old papers alone with the
  new pass's settings. Agreement with the old pass means the new papers changed things (the field moved); the reverse
  means the change came from settings or instability.
- `A total remap is affordable`: verification belongs to rows, so rows survive; names, role selection and the Landscape
  are redone, with no re-verification.
- `Option, untested: seeded clustering` — Leiden accepts an initial partition (`initial_membership` in
  `leidenalg.find_partition`), so a later pass could start from the old clusters and move only what the data demands.
  This makes matching likelier but biases towards the old structure and could hide real change. If used, run both a
  fresh and a seeded clustering, prefer the seeded one only if it is about as stable, and log the comparison.
- `Levels nest` — in the simulation, earlier passes at a finer level merged or were absorbed into today's coarser
  clusters, and a coarser one split; nothing vanished. Matching across passes then looks like matching across levels of
  one hierarchy, which connects it to the proposal "Recursive clustering with a shakedown" below.

Simulated on `reasoning` (2026-10-05, `uv run tools/match.py simulate reasoning`, seconds), the pool as it stood 3, 6
and 9 months ago, clustered by the full method (measure, then level) and matched to today's level 6:

- `6 months ago` (123 papers): combined, level 5. All 5 clusters matched; the agent-harness cluster is `new` (all its
  papers are newer). ARI with today 0.86.
- `3 months ago` (158 papers): combined, level 8. 4 matched (RL, theory of chain-of-thought, test-time compute,
  monitorability); an RL-algorithms group (15 papers) absorbed into RL, a faithfulness group (13) absorbed into
  monitorability, two safety groups (13, 12) merged into attack surface; harnesses `reshuffled`. ARI 0.68. Part of the
  change is settings (old pass against the old papers at today's settings: 0.73), part new papers (0.81).
- `9 months ago` (112 papers): refs, and no level reached `τ`, so the coarsest, 3 clusters, plus 7 fragments; a real
  pass would have stopped for review. RL and monitorability matched; a 56-paper cluster split into theory of
  chain-of-thought, test-time compute and attack surface. ARI 0.39, mostly from settings (0.47, against 0.84 for new
  papers).
- `Caveats`: an earlier pass is simulated by dropping newer papers from today's curated corpus, so retrieval differences
  between passes are not simulated, and the result is optimistic; pools of 112–158 papers.

### Token accounting

The spec no longer carries cost estimates (user, 2026-10-12): a stale one misleads, and no rule decided by one. The
`Tokens` log line still records each dispatch's usage. The simulation audit of 2026-10-12 measures costs per dispatch,
with the model that ran them (`.audits/2026-10-12-sim/model-collapse/simulation.md`, "Measurements"). Once it ends, put
the calibrated figures in `docs/experiments.md`, for human reviewers, noting that they depend on the model.

## Proposals to discuss

### Judgement audits

The gates (`docs/gates.md`) check that every judgement was recorded, not that it was right. To measure that, at a gate,
an independent `survey-pass` agent re-judges a small random sample without seeing the original verdicts, and the
agreement rate goes into a new log line, `Audits`:

- at `G1`: about 20 screening decisions, in and out of scope, drawn from the Pool, `rejected.md` and `fringe-screen.md`;
- at `G3`: every `dissent` row (does it contradict its cluster?), and the alignment ratings of the `high` clusters;
- at `G4`: about 5 verified rows, re-verified from the body text;
- at `G5`: two or three coverage-test candidates (would this change a claim?).

It measures the error rate of each kind of judgement rather than proving any single call right, as the coverage test
does for the coreset as a whole. Estimated 50–100k tokens per pass, under 10% of one. Below a first-guess agreement (say
80%), the gate would flag the disagreements for the main session, and halt if they concentrate in one kind of judgement.
Two pieces are now part of every pass, with their rates in the log's `Judgement audit` line: a blind re-verification of
10% of the rows, and a check of the output's sentences against the rows they cite (`docs/process.md`, "Auditing the
judgements"). The rest above is still a proposal. Prerequisite, done: the traces the audits sample (rejections recorded
by `tools/assign.py reject`, dissent rows quoting their contradiction). Also done: each verified row's evidence, kept in
`graphs/<topic>/evidence/` (2026-10-09), so that the cheapest audit, whether a quote supports its cell, needs no new
search.

`G3` comes first, because it is the last point before verification spends more than half the pass, and today nothing
checks a judgement before then. The plan, decided with the user on 2026-10-12:

- `Pilot` — not part of the simulation audit's main run, and not in the spec. Once the simulation has passed as it
  stands, restore the converged `coreset` checkpoint (`sim-checkpoint-<topic>-coreset`) and run the pilot from it, as a
  steered branch (`docs/audits.md`, "Steered branches"). The auditor dispatches a fresh `survey-pass` agent. It
  re-judges every `dissent` row (does the paper contradict its cluster's central claim?) and the alignment rating of
  every `high` cluster, from the abstracts and the Clusters table, without seeing the rows' quotes. The auditor compares
  the agent's verdicts with its own: for the `dissent` rows, those of the segment's spot check; for the alignment
  ratings, which no spot check covers, verdicts it records before reading the agent's. The catch: a converged checkpoint
  holds no `dissent` row the auditor judged wrong, so on its own it can show the agent's false alarms but never a catch.
  So the auditor first plants two or three `dissent` rows it knows do not contradict their cluster, and records which.
  The runner never sees the audit, so the pilot measures whether a blind agent judges well, not whether a runner can
  carry out the step from the docs. Record the agreement rates, the planted rows caught, and the cost.
- `Adopt` — only after the pilot: a step-4 row in `docs/process.md`, a brief in `docs/dispatch.md`, a log line in
  `docs/formats.md`, a `tools/audit.py` subcommand, and a `G3` requirement that the audit was judged in full. Then
  `docs/audits.md` follows: the `coreset` segment's `steps` gain the audit, and its spot check re-checks the pass's own
  verdicts, as `coverage` does with the faithfulness sample. The segment still ends at `--gate G3`.
- `Open: measure or repair` — the step-7 audits measure and never repair. At `G3` the dissent rows are few enough to
  check every one, so the audit could also send a row judged not to contradict its cluster back to Selection, before
  verification is spent on it. Decide with the pilot's disagreement rate in hand.

The other gates' audits (`G1` screening, `G5` coverage verdicts) wait for the `G3` pilot's result.

### Pool recall

The pool is grown mainly by citation traversal from step 1's frontier candidates, plus relevance and snippet search and
the two fringe routes. Three concerns, raised by the user on 2026-10-09:

- `Shadow papers` — concurrent work on the same idea that does not cite its twin, and is not cited by it. Backward
  traversal cannot reach it; text search finds it only if the agent's queries match its vocabulary, which is often not
  yet settled for new work. No route covers papers older than about two months (the `new` route's limit) and younger
  than a year (the `hidden` route's floor) that are not yet cited.
- `Prior work traversal skipped` — on `reasoning`, 198 papers outside the pool are cited by at least five pool papers,
  and the `hidden` route offered one of them, since it picks the least cited by design. `reasoning` is a curated legacy
  survey, not an expansion's pool, so this overstates a real pass's gap, and many of the 198 will be infrastructure
  (model reports, benchmarks) that screening would reject.
- `Size` — 195 papers looks thin for a topic as active as test-time compute and reasoning (the relevant literature
  probably runs to thousands, `UNVERIFIED`). As designed, pool size is capped by screening cost, about 0.85k tokens per
  candidate, not by fetching or clustering, which are cheap scripts. And the coverage test checks the coreset against
  the pool, not the pool against the field, so a thin pool gives a coreset that looks sufficient while missing whole
  regions. Pool recall is currently unmeasured.

Proposed, to build and pilot together:

1. `Route: co-cited` — outside papers cited by at least k pool papers, whatever their citation count. The data is
   already in `pool.json`; a script ranks them, and they are screened blind like the fringe candidates.
2. `Route: coupled` — outside papers that cite at least k pool papers, ranked by the share of their references that are
   pool papers (bibliographic coupling), restricted to a recent window (about the last twelve months). This is the one
   that finds shadow papers: a concurrent twin cites the same foundations. It needs one new script fetch, the citers of
   pool papers from the Graph API, within the window.
3. `A recall estimate` — capture–recapture between fairly independent routes (text search against `coupled`): the
   overlap of their in-scope finds estimates how many both missed. Routes are never fully independent (all favour
   well-connected work), so it is a lower bound on what is missing. Log it in a `Recall` line, as a diagnostic only;
   `process.md` rightly forbids using "share already found" as a stopping rule.
4. `Cheaper screening`, so that a larger pool is affordable. Two options, either guarded by the `G1` judgement audit:
   - `A similarity prefilter that only accepts` — candidates very close (SPECTER2) to existing pool papers enter without
     an agent reading them; everything else, the far band included, is screened as now. It must never auto-reject the
     far band: far from the pool is what a fringe paper is, and cross-field work (the spec's own example of fringe) is
     far in text yet in scope. Rejecting it would also distort the fringe score silently, since the score is a
     percentile within the pool: with the tail gone, the top percentiles would go to merely unusual papers, and step 4
     would still fill its quota without any check failing. The risk of accepting is inclusion of a near but off-topic
     paper, which is visible and correctable, unlike a wrong rejection. The distance routes (`hidden`, `new`, `coupled`)
     are exempt, and the `G1` audit oversamples far candidates, where scope is hardest to judge.
   - `Screening by a cheaper model` — no geometric bias; its error rate is what the audit measures.

Caps per route (say 50 candidates each, about 85k tokens of screening for both) keep the cost bounded until the recall
estimate shows whether more is needed. Open: k for each route (first guesses 3–5), the coupling window, the prefilter's
acceptance threshold, and whether cheaper screening is safe enough to adopt.

### Recursive clustering with a shakedown

Conservative by design; tested on `reasoning`, not adopted. Best taken in a dedicated session: decide the open points,
build the nameability test, and rerun `tools/recursive.py` on the fresh pool, the real test, before anything moves into
the spec.

Round 1 is the global clustering. In each later round, every leaf is tried as 2–6 parts, and a part becomes a new leaf
only if it passes three tests, cheapest first:

1. `Real` (script) — with the rounds above held fixed, disturb the pool and recluster at the same resolutions: the part
   comes back (0.6 or more).
2. `Found again` (script, the shakedown) — on each disturbed version of the parent, the split decision is made again
   from scratch (resolution, number of parts, test 1): the part comes back. The rounds above are held fixed, since they
   already passed; otherwise every rerun would need its own shakedown. One shakedown per round, about a minute on 200
   papers, no tokens.
3. `Nameable` (model, not built) — a blind name-and-assign test: one agent writes a one-sentence description of each
   part that sets it apart from its siblings; a second, seeing only the descriptions, assigns a shuffled sample of the
   parts' papers to them. Assignment well above chance (say 80%) passes. Only splits that passed 1 and 2 reach it: a
   handful per pass, perhaps 5–10k tokens each.

Parts that fail join a remainder (`partial-confirmed`), or the whole split is refused (`confirmed`).

The user's position (2026-10-03): do not over-split; stay coarse unless the evidence clearly shows a meaningful further
split. Prefers `partial` over all-or-nothing, and accepts a messier tree for it. Agrees that earlier rounds are held
fixed in the shakedown, and wants the coarse bias kept and documented. The motivation, from the user: global levels
impose one granularity on the whole pool, while some clusters need decomposing and others do not.

`partial` drops the whole-split `τ` gate on purpose: that gate scores a split as a whole with pair-counting ARI, so a
split with one robust part and two loose ones fails it, which is the all-or-nothing behaviour `partial` avoids.

- `For` — selective resolution (one area can be finer than another); each area gets its own similarity scale and
  resolution; a natural hierarchy for the Landscape; a part that survives the shakedown is likely to survive the next
  pass, which is itself a disturbed pool, so cross-pass matching gets easier.
- `Against` — a deeper tree means more tests, so some pass by chance; a misassignment at the top is locked in below;
  sizing must work on leaves, whose number is not chosen; cross-pass matching becomes tree matching; remainders are
  defined by exclusion and reproduce poorly (0.34 here), so they need their own treatment in naming and sizing.
- `Built-in coarse bias` — the shakedown reruns on 80% of the data, so every cluster shrinks, and a split near a
  threshold tends to fail. In effect the 20-paper minimum becomes about 25. Intended, and to be stated in the spec.
  Evaluations of the method must scale size thresholds to the rerun's share of the pool, or the bias is applied twice.
- `Nameability in both directions` — a part that cannot be told apart from its siblings by name means the split went too
  far (a gate). A cluster that cannot be named suggests it lumps several things (a signal, never a trigger: if no split
  passes, flag the cluster in the `Clustering rationale` as possibly a grab-bag). A clear cluster name does not block a
  split that passes the tests. A stable split that fails nameability is kept as one leaf but noted in the rationale as a
  possible unnamed theme, since new groupings are the hardest to name in existing vocabulary.
- `Terminology` — "level" is the global cluster count (level 6 = six clusters in one step); in a tree, use "round" or
  "depth". Round 1 of the tree is the global level.
- `Alternative` — use recursion only for sizing: clusters stay global, and a cluster with a confirmed internal split
  gets extra rows for its parts, extending the current sub-cluster rule in `docs/process.md` (step 4, "Sizing"). This
  gets selective resolution for coverage without naming fragile clusters.
- `Open` — the part threshold (0.6, or `τ`); whether round 1 should itself pass a shakedown (the global level is 5 to 10
  clusters across from-scratch reruns, and parts score lower when it is not 6); only the chosen candidate is shaken; and
  the real test is the fresh pool.

Evidence on `reasoning` (2026-10-02/03, `tools/recursive.py`): the global level-6 clustering is round 1; each of its
clusters is then reclustered on its own (own similarity scale, resolution and stability tests) and split into 2–6 parts
if a rule accepts it, and so on. Clusters under 20 papers are not split. Rules: `tau` (the split's local stability
reaches `τ`); `strict` (as `tau`, and every part of 3+ papers comes back end to end at 0.6 or more, with the rounds
above reclustered at fixed resolutions); `partial` (the parts that come back are kept, the rest merge into one remainder
leaf; no whole-split `τ` gate); and `confirmed` and `partial-confirmed`, which add a shakedown to `strict` and `partial`
(above). Every method is also rerun from scratch on the 3 time holdouts and 10 resamples of 80%.

- `Where it splits` — `tau` and `strict` split only theory of chain-of-thought (29 papers), into latent reasoning (14),
  Reflexion-style agents (10) and chain-of-thought prompting (5), at local stability 0.83. `partial` also carves a
  51-paper core out of RL (remainder 13) and a 9-paper group out of test-time compute (remainder 19), from splits with
  local stability of only 0.33 and 0.37. The two safety clusters never split. A null-model guard changed nothing: inside
  clusters, splits into two were not trivially stable (0.10–0.42).
- `Shakedown` — under `confirmed` the chain-of-thought split is made in only 8 of 29 reruns, its parts score 0.56, 0.51
  and 0.35, and it is rejected: the result is exactly the global level 6. Under `partial-confirmed` every split is made
  again (29, 29 and 27 of 29) and all are kept: chain-of-thought parts 0.93, 0.83, 0.71; RL core 0.72; test-time compute
  group 0.63. So what flips with sample size is `strict`'s whole-split `τ` gate, not the parts.
- `From scratch` (holdout ARI, resample ARI, AMI with blocks A–Q; size thresholds scaled to each rerun's share of the
  pool): global level 6 0.78, 0.71, 0.54; `confirmed` the same; global at 8 clusters 0.64, 0.67, 0.51; `strict` (8
  clusters) 0.70, 0.67, 0.56; global at 10 0.71, 0.69, 0.52; `partial-confirmed` (10) 0.59, 0.62, 0.58. Per part under
  `partial-confirmed`: latent reasoning 0.78 and agents 0.65 reproduce; chain-of-thought prompting (5 papers) 0.40, the
  test-time compute group 0.34 and the RL remainder 0.34 do not; the RL core 0.75.
- `Corrections made on the way`: a first version capped round 1 at 6 clusters, which flattered recursion; the fragility
  of the chain-of-thought parts was first blamed on the parent's boundary moving, but the parent comes back 84–100%
  intact in every rerun; and the from-scratch reruns first applied the 20-paper minimum unscaled, so a rerun on 80% met
  a stricter rule than the original, which halved the scores of the parts.
- `Post hoc, not a rule`: a part threshold of 0.75 (equal to `τ`) instead of 0.6 in the shakedown would have kept
  exactly latent reasoning and agents, with chain-of-thought prompting as the remainder: 7 clusters.
- `Reproduce` — `uv run tools/recursive.py reasoning-legacy --rules strict,partial,confirmed,partial-confirmed`, about
  five minutes on 16 cores; `graphs/reasoning-legacy/recursive.json` holds this run. The script's docstring defines
  every rule. Disturbed data throughout: 3 time-holdout cutoffs × 3 seeds, plus 20 resamples of 80% (29 reruns). Two
  diagnostics were run ad hoc and not kept; rebuild them if needed: (1) for each from-scratch rerun, which clusters
  split and how much of the parent stays together (showed the parent intact, the split rarely made); (2) each part's
  from-scratch score, separated by whether round 1 came back at 6 clusters (ruled out round-1 count as the main cause,
  and found the unscaled-minimum artefact).

### Smaller ideas

- A direct minimality test: remove a row and check whether the output changes. Only sufficiency is tested now.
- Field statistics from a random pool sample, labelled from abstracts, run on demand like a probe.
- Persistence across resolutions (Markov stability) as a threshold-free level rule.
- A per-cluster diagnostic: held together by text but not citations suggests a topic label; by citations but not text,
  one lab or school.
- More fringe routes: queries in neighbouring fields' vocabulary (physics, cognitive science, formal methods); snippet
  search for unfollowed "future work" statements in anchors; workshop papers and OpenReview.

## To revisit on a real pool

The first guesses: `τ` = 0.75; `k` = 10; `c` = 10; the fringe score's age cohort of 30 papers; the diagnostic thresholds
(0.15 excess over random, 0.9 for "broad", 0.6 for "unstable", 10 papers for "thin", 20% for "trading"); the fringe
quota; in `tools/cluster.py`, 0.6 for a stable sub-cluster (`SUBCLUSTER_SCORE`), 10 references for the thin-reference
share (`THIN_REFS`) and 30% for the smallest time holdout (`MIN_HOLDOUT_SHARE`); 20% `abstract`-sourced rows for halt
`H10`; and 10% late additions before a recluster (`docs/process.md`, "Late papers"); orientation's stopping rule (two
queries without a new frontier candidate, `docs/process.md`, "Screening for scope"); a targeted expansion's 5 papers
most cited within the pool, and the 2 thinnest regions on `no stable level` (`docs/process.md`, step 3); the 50 results
kept per theme search (`SEARCH_LIMIT` in `tools/expand.py`); at least 6 words per quoted part (`QUOTE_WORDS` in
`tools/gates.py`); and at least 10 candidates per coverage-test round.

Their basis so far is one curated corpus, `reasoning`, not a real pool: `combined` wins clearly (grid-mean stability
0.722 ± 0.004, against `refs` 0.671 and `text` 0.646). Level: 6 clusters at 0.79; 8 clusters drops to 0.67. `τ` 0.70
would give 12 clusters, 0.80 would give 5. Structure-free data scores about 0.25 at every level. `text` alone at 3
clusters (0.59) is barely above its null (0.56). Agreement with blocks A–Q: 0.54 (AMI). The hand blocks keep more
citation links inside clusters than any computed clustering (4.2 times chance, against 2.7–3.4).

## Claims to verify

These were stated from memory in discussion and have not been checked against retrieved text. Verify before relying on
them in the spec or an output.

- SPECTER-family models were trained partly on citation relationships, so embeddings already carry citation signal.
- Modularity clustering is equivalent to a Potts model (Reichardt & Bornholdt, 2006).
- Markov stability is due to Delvenne, Yaliraki & Barahona (2010); the gap statistic to Tibshirani, Walther & Hastie
  (2001).
- The NeurIPS 2025 map (jalammar) was built by embedding abstracts, clustering, and naming clusters with an LLM.

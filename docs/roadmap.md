# Roadmap

The continuity file. It records where the work stands, so that a new session or a session after compaction can resume
without the conversation that produced it. It is for the main session only. Anything under "Open items" is not part of
the spec; do not follow it in a pass until it is moved into the relevant `docs/` file.

## State (2026-10-09)

- `Spec` — `docs/coresets.md`, `docs/process.md`, `docs/formats.md`, `docs/verification.md`, `docs/dispatch.md`,
  `docs/gates.md`, `docs/tooling.md` and `docs/external_services.md` are current, including everything adopted through
  the audit of 2026-10-05 to 2026-10-09 (`.audits/2026-10-05-docs-and-tools.md`, now closed).
- `Branch` — the audit's work is on the branch `audit-phases-1-4`, four commits ahead of `main`, not merged or pushed;
  merging is the user's call.
- `Surveys` — `surveys/reasoning.md` is the only topic. It is a legacy survey, written before the coreset spec: no
  Clusters or Pool section, 195 papers all fully characterised (about 10k tokens each, roughly 2M in total), grouped in
  hand-drawn blocks A–Q. It is the test corpus for everything below.
- `Tools` — all built and tested on `reasoning`: `tools/check.py`, `tools/bib.py`, `tools/pool.py`, `tools/cluster.py`,
  `tools/fringe.py`, `tools/fulltext.py`, `tools/graph.py` (viewer), plus the experiments `tools/recursive.py` and
  `tools/match.py`. Added on 2026-10-08 (audit Phases 2–3): `tools/assign.py` (the Pool table writer, late papers,
  remap), `tools/inputs.py`, `tools/sheets.py`, `tools/preflight.py`, `tools/asta_config.py` and `tools/net.py`; on
  2026-10-09, `tools/gates.py`, the gates `tools/check.py` runs. The coreset-layout paths were tested on a temporary
  topic built from `reasoning`'s data, since no real coreset survey exists yet. See `docs/tooling.md`. Python tools that
  need numpy and Leiden run with `uv run`; the rest are standard library.
- `Data` — everything derived from a survey lives in `graphs/<topic>/`. For `reasoning`: `graph.html` (viewer),
  `pool.json` (embeddings, reference lists), `clusters.json` (clustering report), `references.json` (legacy reference
  cache), the fringe experiment's `fringe.json`, `fringe-screen.md` and `fringe-analysis.json`, the recursive clustering
  experiment's `recursive.json`, and the cross-pass matching simulation's `match-simulation.json` and `history.json`.

## Decisions taken

All adopted into the spec on 2026-09-29 unless marked otherwise.

- **Clusters are computed, not drawn.** `tools/cluster.py` compares three similarity measures (`text`: SPECTER2
  embeddings; `refs`: shared references; `combined`: both, rank-normalised and weighted by how much reference data a
  pair has). Stability is the mean of time-holdout and resampling agreement, over a grid of cluster counts; seed
  agreement is reported, not scored. The measure is chosen by grid-averaged stability, with ties going to `combined`.
  The data for both measures is always fetched, and the comparison reruns for every topic, so the choice adapts to each
  literature. The agent names clusters; membership is never changed by hand, and only the user overrides, with the
  override logged. Spec: `docs/process.md`, "Clustering method".

- **The level is the finest with stability at least `τ` = 0.75**, reported with the levels `τ ± 0.05` would pick. A
  "largest drop" rule was tried and rejected: stability is highest at the coarsest level, so the first drop is always
  the largest. A threshold-free rule (largest excess over a structure-free null model) was also tried. It confirms the
  structure is real, but its null curve is flat, so it reduces to "most stable"; it is reported, not used. How much
  detail to keep is a trade-off between detail and stability, and the user judges it during cluster review with the
  viewer's level slider on the similarity map.

- **When stability fails, the action is defined.** Whole clustering: `no structure`, `no stable level`, `broad scope`
  (reclassified 2026-10-02 as a reported finding, not a failure: the pass continues, and the coverage test judges
  whether broad clusters suffice). Single clusters: `thin cluster` (expand the region), `clusters trade papers` (keep
  both, require a bridge), `unstable cluster` (flag). Instability is information, not a defect: the user reads the two
  trading safety clusters as an open boundary in the field. Spec: `docs/process.md`, "When stability fails".

- **Citation communities are only a diagnostic.** Louvain communities came from the viewer, not the method. They remain
  one colour mode and feed the cohesion figures, with no names of their own.

- **A `fringe` role**, five to ten per topic, for overlooked papers carrying an idea no other coreset row has. Two
  expansion routes feed it at the end of step 2, `hidden` and `new`; a third, `followers`, was tested and dropped.
  Fringe candidates enter the pool before clustering, and `fringe` rows are chosen last in step 4, by an age-corrected
  distance to nearest neighbours plus a one-sentence idea test. Spec: `docs/process.md` (step 4 and "Fringe routes").

- **Order of operations.** `docs/process.md` opens with a table of every operation in a pass: pool or coreset stage,
  script or model judgement, what the model reads and decides, and tokens. The pool is broad and cheap (steps 1–3); the
  coreset is small and expensive (steps 4–5). The stability test (step 3, script) checks the clusters; the coverage test
  (last, judgement) checks the coreset.

- **External services have their own doc** (2026-09-30), `docs/external_services.md`: which service is used by whom, how
  to call each Asta tool, rate limits, credentials, and an extended preflight check that runs as step 0 of every pass.
  Measured while writing it: the unauthenticated Graph API answered 429 to a single request, so 429 counts as reachable;
  and one `snippet_search` call took over two minutes, so a call silent for five minutes counts as errored.

- **The coreset's targets** (2026-09-30): the coreset is stable against the output's `Landscape`, `Assumptions` and
  `Gaps` by default, plus anything the input's `Coreset Spec` declares. `Questions` and `Reading` are derived, so they
  are not targets. In the spec: `docs/formats.md` (the user's `Coreset Spec` section), the coverage test's question in
  `docs/process.md`, and `docs/coresets.md`.

- **Coresets have their own doc** (2026-09-30), `docs/coresets.md`: the definition and its two tests, the origin in
  Sener and Savarese's k-center coreset, covering versus weighted coresets, pool versus coreset, how roles achieve
  coverage, and why a coreset gives neither absence claims nor field statistics. Other docs keep a short, local version
  and point to it.

- **Full text from arXiv for verification** (2026-10-01), `tools/fulltext.py`: a paper's arXiv HTML, flattened to
  verbatim text, with a PDF fallback. Used when snippet search has no body text or a claim rests on a table or caption;
  `source` is then `full-text`, which previously had no defined route. WebFetch is ruled out for verification because it
  returns a model's paraphrase. It closes body-text lag only, not discovery lag. Spec: `docs/verification.md`,
  `docs/external_services.md` ("arXiv"), `docs/tooling.md`.

- **No blocking cluster checkpoint by default** (2026-10-01). A pass runs straight through, and the user reviews the
  clusters with the output. It stops before the coreset only when the input asks (`review: before coreset`), a
  whole-clustering diagnostic fires, a cluster cannot be rated for alignment, or an expected cluster is missing. The
  reason: verification belongs to a row, so a late clustering change costs re-selection and new rows only. The user's
  levers (level, alignment, names, scope, more data) can be given in advance in the input's new `Clustering` section, or
  requested afterwards as an incremental pass. Spec: `docs/process.md` (step 3, "Changing the clusters after a pass"),
  `docs/formats.md`.

- **A clustering rationale per pass** (2026-10-02): at step 3 the naming agent writes a `Clustering rationale` paragraph
  into the pass's log entry, interpreting the figures (level margin, weak clusters, how decisive the measure was, what
  input steering changed). The viewer shows the latest pass's rationale. Spec: `docs/process.md` ("Recording it"),
  `docs/formats.md`.

- **Cluster history** (2026-10-05, proposed by the user): after choosing the level, `tools/cluster.py` reports since
  when each cluster exists, as post-processing that never changes the clusters. Four date segments of equal paper count
  (narrower in a publication burst); each cumulative snapshot clustered with today's measure and cluster count at five
  seeds and matched to today (`cluster_history` in `tools/match.py`); one first-seen date per cluster, not per map. Lack
  of data is stated, not corrected (the user's choice: no subsampling, and a size-matched control was declined): an
  unfound cluster with fewer than 10 papers in the snapshot is "too few papers", otherwise "grouped differently". A find
  in a snapshot below `τ` is hedged as "probably". Optimistic, since old papers in today's pool are those still
  relevant. Recorded as a `Temporal stability` log line and interpreted in the `Clustering rationale`; the viewer shows
  a stacked column per snapshot (segments per today's cluster, solid if found, faint if not) and a "Since when" line per
  cluster. Considered and not built: a full flow (Sankey) chart between the snapshots' own clusters, busier and, on
  `reasoning`, showing nothing more. Spec: `docs/process.md` ("Since when each cluster exists"), `docs/formats.md`.

- **Pool metadata is filled by script**, `tools/pool.py`, never through a model's context.

- **Docs structure.** `CLAUDE.md` holds what every session needs, plus a table of who reads which `docs/` file and when.
  `docs/responses.md` (formatting and voice) is imported into it. Terminal replies use top-level `#` headers and
  `inline code` for accents, because only those render visibly.

- **`docs/surveys.md` dissolved** (2026-10-05, the user's request). About four-fifths of it repeated `docs/coresets.md`,
  `docs/process.md` and `docs/formats.md`. Its unique content moved to where it is applied. `Sizing` and the role
  definitions went to `docs/process.md` step 4, merged with how each role is found, so roles are defined once. The
  cluster definition and examples went to step 3, and the hint that fringe rows feed `Questions` to `docs/formats.md`.
  `docs/coresets.md` remains the one place for why the roles and sizing are as they are.

- **Audit decisions D1–D6** (2026-10-05, with the user). Full wording, and where each one goes, in
  `.audits/2026-10-05-docs-and-tools.md` ("Decisions"). D3, D5 and D6 were written into the spec on 2026-10-08 (audit
  Phase 1), apart from their code changes: the end conditions are in `docs/process.md`, "When a pass ends"; the
  `[abstract-only]` marker in `docs/formats.md` and `docs/verification.md`; the targets in `docs/formats.md`
  (`Coreset Spec`). D1, D2 and D4 followed on 2026-10-08 with their tools (audit Phase 3): late papers in
  `docs/process.md` ("Late papers") and `tools/assign.py`; paper IDs in `docs/formats.md` ("Paper IDs") and every tool;
  parseable dimensions in `docs/formats.md` and `tools/inputs.py`. One implementation choice under D1: the queue is the
  Pool rows with an empty `cluster` cell, which `tools/check.py` lists, rather than a separate Open work field, so that
  it has one source.

  - `D1` — papers that reach the pool after step 3 are queued. Each coverage-test round, and each re-run of step 4,
    processes the queue as one batch: nearest-cluster assignment by script, or a recluster when the coverage test judges
    a new cluster (after a targeted expansion) or when late additions exceed 10% of the pool.
  - `D2` — every paper can enter the pool and the coreset. Pre-2015 arXiv IDs are supported. Without an arXiv ID, the
    canonical ID is `CorpusId:<n>`. Of duplicate records, the arXiv one is kept.
  - `D3` — every error halts the pass, including all preflight failures, except a Graph API 429. Errored queries and
    failed scripts halt it too. All finish and halt conditions go into one list with IDs (audit issue S11).
  - `D4` — the input declares dimensions with their allowed values in a parseable form, and the tools read it.
  - `D5` — `UNVERIFIED` in replies, reports and docs; `source` per row; `[abstract-only]` in outputs, replacing
    "provisional", with a legend in every output.
  - `D6` — "targets" names the parts of an output the coreset must stay stable against, and is defined in the
    `Coreset Spec` entry of `docs/formats.md`.

## Findings on the `reasoning` corpus

Caveat for all of these: one corpus, and a curated survey rather than a real pool. Rerun on the fresh pool.

- `Clustering` — `combined` wins clearly (grid-mean stability 0.722 ± 0.004, against `refs` 0.671 and `text` 0.646).
  Level: 6 clusters at 0.79; 8 clusters drops to 0.67. `τ` 0.70 would give 12 clusters, 0.80 would give 5.
  Structure-free data scores about 0.25 at every level. `text` alone at 3 clusters (0.59) is barely above its null
  (0.56). Agreement with blocks A–Q: 0.54 (AMI). The hand blocks keep more citation links inside clusters than any
  computed clustering (4.2 times chance, against 2.7–3.4).
- `The six clusters` — RL and reasoning capability (64 papers, stability 0.93), test-time compute and verification (28,
  0.89), theory of chain-of-thought (29, 0.83), chain-of-thought monitorability (39, 0.54), test-time compute as attack
  surface and evaluation awareness (30, 0.51), agent harnesses (5, 0.18). Diagnostics: harnesses is a thin cluster,
  absorbed by the two safety clusters; monitorability and attack surface trade papers (41% of rerun pairs).
- `Measures` — embedding cosines bunch in a narrow band (90% between 0.86 and 0.94). Shared references are not mostly
  zero on this set: 59% of pairs share at least one.
- `Fringe` — 146 candidates, screened blind by a `survey-pass` agent (118 in scope). `hidden` papers sit significantly
  further from their nearest neighbours (p < 0.001), but at cluster level they gather with the 2021–2023 foundations, so
  their clustering mostly reflects age; per paper, the most outlying are cross-field (1965 automata theory, 1984
  dual-process psychology). `new` papers turned the thin harness cluster into a coherent 17-paper one. Distance to
  nearest neighbours is the fringe signal; cluster consistency is not. Adding candidates moved the base clustering (ARI
  0.70), which is why fringe routes run before clustering. Highest fringe scores on the base set: theory of learning
  dynamics and model collapse, and safety evaluations (sabotage, evaluation awareness). The user judged them acceptable
  matches.
- `Fringe score and missing references` (2026-10-08, audit M1) — 16 pool papers have fewer than 10 resolved references,
  13 of them none, though all have abstracts. By references alone such a paper looks far from everything, so the score
  now weights references per paper by `w = n / (n + c)`, as `combined` does (`docs/process.md`). Effect on `reasoning`:
  the top 8 is the same set (top 20: 18 kept; rank correlation 0.93), and 5 of the 8 still have no resolved references,
  because those papers are far by text too. What moved were textually ordinary papers without references, from about
  rank 70–90 to the bottom half. Median score, fewer than 10 references against the rest: 0.75 against 0.45 before, 0.67
  against 0.47 after. The remaining gap may be real: papers whose references Semantic Scholar does not parse include lab
  reports (sabotage evaluations, in-context scheming), which also read differently.
- `Recursive clustering` (2026-10-02/03, `tools/recursive.py`) — the global level-6 clustering is round 1; each of its
  clusters is then reclustered on its own (own similarity scale, resolution and stability tests) and split into 2–6
  parts if a rule accepts it, and so on. Clusters under 20 papers are not split. Rules: `tau` (the split's local
  stability reaches `τ`); `strict` (as `tau`, and every part of 3+ papers comes back end to end at 0.6 or more, with the
  rounds above reclustered at fixed resolutions); `partial` (the parts that come back are kept, the rest merge into one
  remainder leaf; no whole-split `τ` gate); and `confirmed` and `partial-confirmed`, which add a shakedown to `strict`
  and `partial` (see "Ideas raised"). Every method is also rerun from scratch on the 3 time holdouts and 10 resamples of
  80%.
  - `Where it splits` — `tau` and `strict` split only theory of chain-of-thought (29 papers), into latent reasoning
    (14), Reflexion-style agents (10) and chain-of-thought prompting (5), at local stability 0.83. `partial` also carves
    a 51-paper core out of RL (remainder 13) and a 9-paper group out of test-time compute (remainder 19), from splits
    with local stability of only 0.33 and 0.37. The two safety clusters never split. A null-model guard changed nothing:
    inside clusters, splits into two were not trivially stable (0.10–0.42).
  - `Shakedown` — under `confirmed` the chain-of-thought split is made in only 8 of 29 reruns, its parts score 0.56,
    0.51 and 0.35, and it is rejected: the result is exactly the global level 6. Under `partial-confirmed` every split
    is made again (29, 29 and 27 of 29) and all are kept: chain-of-thought parts 0.93, 0.83, 0.71; RL core 0.72;
    test-time compute group 0.63. So what flips with sample size is `strict`'s whole-split `τ` gate, not the parts.
  - `From scratch` (holdout ARI, resample ARI, AMI with blocks A–Q; size thresholds scaled to each rerun's share of the
    pool): global level 6 0.78, 0.71, 0.54; `confirmed` the same; global at 8 clusters 0.64, 0.67, 0.51; `strict` (8
    clusters) 0.70, 0.67, 0.56; global at 10 0.71, 0.69, 0.52; `partial-confirmed` (10) 0.59, 0.62, 0.58. Per part under
    `partial-confirmed`: latent reasoning 0.78 and agents 0.65 reproduce; chain-of-thought prompting (5 papers) 0.40,
    the test-time compute group 0.34 and the RL remainder 0.34 do not; the RL core 0.75.
  - `Corrections made on the way`: a first version capped round 1 at 6 clusters, which flattered recursion; the
    fragility of the chain-of-thought parts was first blamed on the parent's boundary moving, but the parent comes back
    84–100% intact in every rerun; and the from-scratch reruns first applied the 20-paper minimum unscaled, so a rerun
    on 80% met a stricter rule than the original, which halved the scores of the parts.
  - `Post hoc, not a rule`: a part threshold of 0.75 (equal to `τ`) instead of 0.6 in the shakedown would have kept
    exactly latent reasoning and agents, with chain-of-thought prompting as the remainder: 7 clusters.
  - `Reproduce` — `uv run tools/recursive.py reasoning --rules strict,partial,confirmed,partial-confirmed`, about five
    minutes on 16 cores; `graphs/reasoning/recursive.json` holds this run. The script's docstring defines every rule.
    Disturbed data throughout: 3 time-holdout cutoffs × 3 seeds, plus 20 resamples of 80% (29 reruns). Two diagnostics
    were run ad hoc and not kept; rebuild them if needed: (1) for each from-scratch rerun, which clusters split and how
    much of the parent stays together (showed the parent intact, the split rarely made); (2) each part's from-scratch
    score, separated by whether round 1 came back at 6 clusters (ruled out round-1 count as the main cause, and found
    the unscaled-minimum artefact).
- `Matching across passes, simulated` (2026-10-05, `uv run tools/match.py simulate reasoning`, seconds) — the pool as it
  stood 3, 6 and 9 months ago, clustered by the full method (measure, then level), matched to today's level 6:
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
  - `Caveats`: an earlier pass is simulated by dropping newer papers from today's curated corpus, so retrieval
    differences between passes are not simulated, and the result is optimistic; pools of 112–158 papers.
- `Cluster history` (2026-10-05, `uv run tools/match.py history reasoning`, seconds) — the pool divided by date into 4
  segments of equal paper count (cutoffs 2025-03-24, 2025-10-09, 2026-05-25: segments of about four years, six, seven
  and four months); each cumulative snapshot clustered with today's measure and cluster count at 5 seeds, and matched to
  today. Snapshots: 48 papers (only 4 clusters reachable, stability 0.40), 97 (0.72), 146 (0.84). Per cluster: theory of
  chain-of-thought, test-time compute and attack surface are already there in the earliest snapshot; RL probably first
  appears in the pool of 2025-10-09 (hedged because that snapshot's stability, 0.72, is below `τ`; 5 papers before
  that); monitorability in the pool of 2026-05-25 (9 papers before); agent harnesses only today. Every unmatched case
  was "too few papers yet", never "grouped differently", so on this pool the history is one of emergence, not
  restructuring. Caveat: a match in an unstable snapshot (0.40) is weak evidence.
- `Semantic Scholar recommendations` — accept negative examples, but they change little (16 of 20 results the same), and
  the endpoint returns only the last two months of papers.
- `Costs` — measured: screening about 0.85k tokens per candidate (123k for 146); `tools/cluster.py` about two minutes
  per 200 papers. From earlier passes: verification about 10k per row. Estimated pass total for about 50 coreset rows:
  1–1.5M tokens.
- `Retrieval` — a pass that used only WebSearch produced a corpus top-heavy with preprints and missing the methods they
  all cite. This is the reason `docs/process.md` pairs orientation with expansion.
- `Old stopping rule` — the fraction of screened candidates already present in the survey measured 4–12% on the best
  seeds, and could never have reached its threshold. This is why the coverage test replaced it.

## Open items

**Small, not blocking:** on the citation map, the large group labels overlap nodes where the map is dense.

**Proposed, not yet spec: judgement audits** (2026-10-09). The gates (`docs/gates.md`) check that every judgement was
recorded, not that it was right. To measure that, at a gate, an independent `survey-pass` agent re-judges a small random
sample without seeing the original verdicts, and the agreement rate goes into a new log line, `Audits`:

- at `G1`: about 20 screening decisions, in and out of scope, drawn from the Pool, `rejected.md` and `fringe-screen.md`;
- at `G3`: every `dissent` row (does it contradict its cluster?), and the alignment ratings of the `high` clusters;
- at `G4`: about 5 verified rows, re-verified from the body text;
- at `G5`: two or three coverage-test candidates (would this change a claim?).

It measures the error rate of each kind of judgement rather than proving any single call right, as the coverage test
does for the coreset as a whole. Estimated 50–100k tokens per pass, under 10% of one. Below a first-guess agreement (say
80%), the gate would flag the disagreements for the main session, and halt if they concentrate in one kind of judgement.
Prerequisite, now done: the traces the audits sample (rejections recorded by `tools/assign.py reject`, dissent rows
quoting their contradiction). Also done: each verified row's evidence, kept in `graphs/<topic>/evidence/` (2026-10-09),
so that the cheapest audit, whether a quote supports its cell, needs no new search. `reasoning`'s 195 legacy rows have
none; their evidence was never kept, and only re-verification would recover it. Pilot it on the fresh coreset run, and
adopt it into `docs/gates.md` once the agreement rates of a real pass are known.

**Proposed, not yet spec: pool recall** (2026-10-09; for a fresh session, before the fresh coreset run). The pool is
grown mainly by citation traversal from step 1's frontier candidates, plus relevance and snippet search and the two
fringe routes. Three concerns, raised by the user:

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
threshold, and whether cheaper screening is safe enough to adopt.

**Not yet built:**

- Discovery lag: a paper on arXiv but not yet in Semantic Scholar is invisible to Asta, and `tools/pool.py` cannot fetch
  its embedding or references. A search of arXiv's own listings during orientation would find it; clustering would still
  need a fallback.

- Matching clusters across passes, so that ids and names persist and splits, merges and vanished clusters are logged.
  Partly built (2026-10-08): `tools/cluster.py` matches every new clustering to the previous one with `match()`, and
  `tools/assign.py remap` carries names over to matched clusters; tested on a swapped-id fixture. What remains: the
  diagnosis for when most clusters fail to match (below), a log format for the remap result beyond the `Late papers`
  line, and the seeded-clustering option. The design so far (2026-10-05):

  - `No guarantee` — a later pass can produce a different clustering: the level can change, new papers change the
    similarity scale, the graph and the resolution, and the field can genuinely restructure. Matching is possible
    because a later pass keeps the old papers, so clusters are compared by members on the shared papers, never by name.
    The time holdout already simulates an earlier pass, so per-cluster stability predicts which clusters will match.
  - `Many-to-many and graded` — each old cluster is `matched`, `split`, `merged`, `absorbed` or `vanished`; each new
    cluster not accounted for is `new` (mostly new papers) or `reshuffled`. Rules in the `tools/match.py` docstring; the
    majority threshold (0.5) and the 3-paper fragment limit are first guesses. Matched clusters keep id and name.
  - `When most clusters fail to match`, report it, and tell the two causes apart: cluster the old papers alone with the
    new pass's settings. Agreement with the old pass means the new papers changed things (the field moved); the reverse
    means the change came from settings or instability.
  - `A total remap is affordable`: verification belongs to rows, so rows survive; names, role selection and the
    Landscape are redone, with no re-verification.
  - `Option, untested: seeded clustering` — Leiden accepts an initial partition (`initial_membership` in
    `leidenalg.find_partition`), so a later pass could start from the old clusters and move only what the data demands.
    This makes matching likelier but biases towards the old structure and could hide real change. If used, run both a
    fresh and a seeded clustering, prefer the seeded one only if it is about as stable, and log the comparison.
  - `Levels nest` — in the simulation, earlier passes at a finer level merged or were absorbed into today's coarser
    clusters, and a coarser one split; nothing vanished. Matching across passes then looks like matching across levels
    of one hierarchy, which connects it to the recursive-clustering proposal ("Ideas raised").

- Per-step token accounting in the retrieval log, from the fresh run on, to replace the estimates in the order of
  operations.

**Ready to run:** the full text of all 27 `abstract`-sourced rows in `surveys/reasoning.md` is cached in
`graphs/reasoning/fulltext/`. Twelve of them are cited by the output, which marks them `[abstract-only]`; verifying
those would let the markers go. Optional, since `reasoning` is to be renamed `reasoning-exhaustive`.

**First guesses to revisit on a real pool:** `τ` = 0.75; `k` = 10; `c` = 10; the diagnostic thresholds (0.15 excess over
random, 0.9 for "broad", 0.6 for "unstable", 10 papers for "thin", 20% for "trading"); the fringe quota; in
`tools/cluster.py`, 0.6 for a stable sub-cluster (`SUBCLUSTER_SCORE`), 10 references for the thin-reference share
(`THIN_REFS`) and 30% for the smallest time holdout (`MIN_HOLDOUT_SHARE`); 20% `abstract`-sourced rows for halt `H10`;
and, from D1, 10% late additions before a recluster.

**Ideas raised, not adopted or tested:**

- A direct minimality test: remove a row and check whether the output changes. Only sufficiency is tested now.

- Field statistics from a random pool sample, labelled from abstracts, run on demand like a probe.

- Measuring whether two agents agree on the coverage test's "would this change a claim". Now part of the judgement
  audits below.

- Recursive clustering with a shakedown, conservative by design (tested on `reasoning`, see Findings; not adopted).
  Round 1 is the global clustering. In each later round, every leaf is tried as 2–6 parts, and a part becomes a new leaf
  only if it passes three tests, cheapest first:

  1. `Real` (script) — with the rounds above held fixed, disturb the pool and recluster at the same resolutions: the
     part comes back (0.6 or more).
  2. `Found again` (script, the shakedown) — on each disturbed version of the parent, the split decision is made again
     from scratch (resolution, number of parts, test 1): the part comes back. The rounds above are held fixed, since
     they already passed; otherwise every rerun would need its own shakedown. One shakedown per round, about a minute on
     200 papers, no tokens.
  3. `Nameable` (model, not built) — a blind name-and-assign test: one agent writes a one-sentence description of each
     part that sets it apart from its siblings; a second, seeing only the descriptions, assigns a shuffled sample of the
     parts' papers to them. Assignment well above chance (say 80%) passes. Only splits that passed 1 and 2 reach it: a
     handful per pass, perhaps 5–10k tokens each.

  Parts that fail join a remainder (`partial-confirmed`), or the whole split is refused (`confirmed`).

  The user's position (2026-10-03): do not over-split; stay coarse unless the evidence clearly shows a meaningful
  further split. Prefers `partial` over all-or-nothing, and accepts a messier tree for it. Agrees that earlier rounds
  are held fixed in the shakedown, and wants the coarse bias kept and documented. The motivation, from the user: global
  levels impose one granularity on the whole pool, while some clusters need decomposing and others do not.

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
  - `Nameability in both directions` — a part that cannot be told apart from its siblings by name means the split went
    too far (a gate). A cluster that cannot be named suggests it lumps several things (a signal, never a trigger: if no
    split passes, flag the cluster in the `Clustering rationale` as possibly a grab-bag). A clear cluster name does not
    block a split that passes the tests. A stable split that fails nameability is kept as one leaf but noted in the
    rationale as a possible unnamed theme, since new groupings are the hardest to name in existing vocabulary.
  - `Terminology` — "level" is the global cluster count (level 6 = six clusters in one step); in a tree, use "round" or
    "depth". Round 1 of the tree is the global level.
  - `Alternative` — use recursion only for sizing: clusters stay global, and a cluster with a confirmed internal split
    gets extra rows for its parts, extending the current sub-cluster rule in `docs/process.md` (step 4, "Sizing"). This
    gets selective resolution for coverage without naming fragile clusters.
  - `Open` — the part threshold (0.6, or `τ`); whether round 1 should itself pass a shakedown (the global level is 5 to
    10 clusters across from-scratch reruns, and parts score lower when it is not 6); only the chosen candidate is
    shaken; and the real test is the fresh pool.

- Persistence across resolutions (Markov stability) as a threshold-free level rule.

- A per-cluster diagnostic: held together by text but not citations suggests a topic label; by citations but not text,
  one lab or school.

- More fringe routes: queries in neighbouring fields' vocabulary (physics, cognitive science, formal methods); snippet
  search for unfollowed "future work" statements in anchors; workshop papers and OpenReview.

## Next steps, in order

1. The user reviews the spec in detail. An audit of the spec, agent files and tools (2026-10-05) is in
   `.audits/2026-10-05-docs-and-tools.md`: issues with remediations, six decisions for the user, and a phased action
   plan. Phases 0–4 are done (2026-10-08 and 2026-10-09), including the dry read, and so is the follow-up: the gates
   (`docs/gates.md`, `tools/gates.py`), adopted 2026-10-09.
2. Decide before the fresh run (raised 2026-10-09), in a fresh session: the pool-recall proposal above (new routes, a
   recall estimate, cheaper screening), and two smaller points:
   - `How a previous survey's papers enter the pool` — `CLAUDE.md` says a survey listed as `Context` is a source whose
     papers enter the new pool, but no procedure says how: added by script as in scope, or screened against the new
     input like any candidate (recommended, since the new input may scope the topic differently).
   - `Reused verified rows and the evidence gate` — `CLAUDE.md` lets a verified row be reused without re-verification,
     but `g4.evidence` requires an evidence file, and `reasoning`'s rows have none. Options: re-verify reused rows
     (about 10k tokens each); accept an evidence file that records the reuse (the survey and date it was verified in,
     evidence not kept), listed in a note and sampled first by the G4 audit (recommended); or waive per row.
3. The fresh coreset run:
   - Rename the old topic everywhere to `reasoning-exhaustive`: `inputs/`, `surveys/`, `outputs/`, `bib/` and
     `graphs/reasoning/` (its pool, clustering, fringe sheet and full texts). Left in place, `graphs/reasoning/` would
     feed the old fringe judgements and clustering into the new pass.
   - Write a new `inputs/reasoning.md` that lists `surveys/reasoning-exhaustive.md` as `Context`, with
     `review: before coreset` in its `Clustering` section, since this is the first real run.
   - Run steps 0–3 down the checklist, passing gates `G0` to `G2`, to the `H13` review in the viewer, with token
     accounting (`Tokens`) from the first dispatch.
   - Pilot the judgement audit that falls inside this stretch, `G1`'s screening sample; the `G3`–`G5` audits wait for
     the coreset stage.
4. On that real pool, revisit the first-guess thresholds and the findings above.

Separately, at any point: a dedicated session on recursive clustering with a shakedown (see "Ideas raised" and the
Findings entry). Decide the open points, build the nameability test, and rerun `tools/recursive.py` on the fresh pool,
the real test, before anything moves into the spec.

## Claims recalled but not verified

These were stated from memory in discussion and have not been checked against retrieved text. Verify before relying on
them in the spec or an output.

- SPECTER-family models were trained partly on citation relationships, so embeddings already carry citation signal.
- Modularity clustering is equivalent to a Potts model (Reichardt & Bornholdt, 2006).
- Markov stability is due to Delvenne, Yaliraki & Barahona (2010); the gap statistic to Tibshirani, Walther & Hastie
  (2001).
- The NeurIPS 2025 map (jalammar) was built by embedding abstracts, clustering, and naming clusters with an LLM.

Checked on 2026-09-29: the Semantic Scholar recommendations endpoint accepts negative examples (see Findings). Checked
on 2026-09-30: Sener & Savarese's coreset is a k-center covering (arXiv `1708.00489`, body text; see
`docs/coresets.md`).

# Roadmap

The continuity file. It records where the work stands, so that a new session or a session after compaction can resume
without the conversation that produced it. It is for the main session only. Anything under "Open items" is not part of
the spec; do not follow it in a pass until it is moved into the relevant `docs/` file.

## State (2026-09-29)

- `Spec` — `docs/surveys.md` (formerly `docs/method.md`), `docs/process.md`, `docs/formats.md`, `docs/verification.md`,
  `docs/dispatch.md`, `docs/tooling.md` and `docs/external_services.md` are current, including everything adopted on
  2026-09-29 (below). The user has **not yet reviewed the spec in detail**; that is the next step. The user is also
  consolidating `CLAUDE.md` by hand.
- `Surveys` — `surveys/reasoning.md` is the only topic. It is a legacy survey, written before the coreset spec: no
  Clusters or Pool section, 195 papers all fully characterised (about 10k tokens each, roughly 2M in total), grouped in
  hand-drawn blocks A–Q. It is the test corpus for everything below.
- `Tools` — all built and tested on `reasoning`: `tools/check.py`, `tools/bib.py`, `tools/pool.py`, `tools/cluster.py`,
  `tools/fringe.py`, `tools/fulltext.py`, `tools/graph.py` (viewer). See `docs/tooling.md`. Python tools that need numpy
  and Leiden run with `uv run`; the rest are standard library.
- `Data` — everything derived from a survey lives in `graphs/<topic>/`. For `reasoning`: `graph.html` (viewer),
  `pool.json` (embeddings, reference lists), `clusters.json` (clustering report), `references.json` (legacy reference
  cache), and the fringe experiment's `fringe.json`, `fringe-screen.md` and `fringe-analysis.json`.

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
- **When stability fails, the action is defined.** Whole clustering: `no structure`, `no stable level`,
  `scope too broad`. Single clusters: `thin cluster` (expand the region), `clusters trade papers` (keep both, require a
  bridge), `unstable cluster` (flag). Instability is information, not a defect: the user reads the two trading safety
  clusters as an open boundary in the field. Spec: `docs/process.md`, "When stability fails".
- **Citation communities are only a diagnostic.** Louvain communities came from the viewer, not the method. They remain
  one colour mode and feed the cohesion figures, with no names of their own.
- **A `fringe` role**, five to ten per topic, for overlooked papers carrying an idea no other coreset row has. Two
  expansion routes feed it at the end of step 2, `hidden` and `new`; a third, `followers`, was tested and dropped.
  Fringe candidates enter the pool before clustering, and `fringe` rows are chosen last in step 4, by an age-corrected
  distance to nearest neighbours plus a one-sentence idea test. Spec: `docs/surveys.md`, `docs/process.md` ("Fringe
  routes").
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
- **Pool metadata is filled by script**, `tools/pool.py`, never through a model's context.
- **Docs structure.** `CLAUDE.md` holds what every session needs, plus a table of who reads which `docs/` file and when.
  `docs/responses.md` (formatting and voice) is imported into it. Terminal replies use top-level `#` headers and
  `inline code` for accents, because only those render visibly.

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
- `Semantic Scholar recommendations` — accept negative examples, but they change little (16 of 20 results the same), and
  the endpoint returns only the last two months of papers.
- `Costs` — measured: screening about 0.85k tokens per candidate (123k for 146); `tools/cluster.py` about two minutes
  per 200 papers. From earlier passes: verification about 10k per row. Estimated pass total for about 50 coreset rows:
  1–1.5M tokens.

## Open items

**Tool gaps, to close before a real pass:**

- No script runs the non-agent preflight checks; they are commands in `docs/external_services.md`.

- Screened fringe candidates have to be added to the Pool table by the screening agent; no tool does it.

- Pool rows have no cluster id between step 2 and step 3, and `tools/check.py` rejects an unknown pool `cluster`.

- The computed assignment (`c1`, `c2`, …) is not written into the Pool table's `cluster` column, nor mapped to the
  agent's named cluster ids.

- `tools/check.py` does not check the `Clustering` log line, or that pool `cluster` values match the computed
  assignment.

**Not yet built:**

- The input's `Clustering` steering has no tool support yet. `tools/cluster.py` chooses the level by rule, and a
  `granularity` preference can only be approximated with `--tau`; it needs a `--level` option. `tools/check.py` reads no
  input file at all, so a typo such as `review: before-coreset` would silently skip the stop it asks for. It needs an
  input check: known section names, known `Clustering` fields, and allowed values.

- Discovery lag: a paper on arXiv but not yet in Semantic Scholar is invisible to Asta, and `tools/pool.py` cannot fetch
  its embedding or references. A search of arXiv's own listings during orientation would find it; clustering would still
  need a fallback.

- Matching clusters across passes, so that ids and names persist and splits, merges and vanished clusters are logged.
  Needed before a topic's second pass.

- Per-step token accounting in the retrieval log, from the fresh run on, to replace the estimates in the order of
  operations.

**Ready to run:** the full text of all 27 `abstract`-sourced rows in `surveys/reasoning.md` is cached in
`graphs/reasoning/fulltext/`. Twelve of them are cited by the output, which marks them provisional; verifying those
would let the markers go. Optional, since `reasoning` is to be renamed `reasoning-exhaustive`.

**First guesses to revisit on a real pool:** `τ` = 0.75; `k` = 10; `c` = 10; the diagnostic thresholds (0.15 excess over
random, 0.9 for "broad", 0.6 for "unstable", 10 papers for "thin", 20% for "trading"); the fringe quota.

**Ideas raised, not adopted or tested:**

- A direct minimality test: remove a row and check whether the output changes. Only sufficiency is tested now.

- Field statistics from a random pool sample, labelled from abstracts, run on demand like a probe.

- Measuring whether two agents agree on the coverage test's "would this change a claim".

- Persistence across resolutions (Markov stability) as a threshold-free level rule.

- A per-cluster diagnostic: held together by text but not citations suggests a topic label; by citations but not text,
  one lab or school.

- More fringe routes: queries in neighbouring fields' vocabulary (physics, cognitive science, formal methods); snippet
  search for unfollowed "future work" statements in anchors; workshop papers and OpenReview.

## Next steps, in order

1. The user reviews the spec in detail.
2. Close the tool gaps above.
3. The fresh coreset run: rename the old input, survey and output to `reasoning-exhaustive`; create a new
   `inputs/reasoning.md` that lists the old survey as Context; set `review: before coreset` in its `Clustering` section,
   since this is the first real run, and run steps 1–3 to that review, in the viewer, with token accounting from the
   start.
4. On that real pool, revisit the first-guess thresholds and the findings above.

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

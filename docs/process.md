# Process

A description of our methodology. The document follows a pass in the order it runs. The overview gives the map: the
stages, every operation in order, and which source serves which job. Then each stage follows, step by step, with the
detail each step needs placed under it.

## Overview

Retrieval has four jobs, and the tools are good at different ones. Assign tools by job rather than ranking them.

- `Orientation: what is the field talking about now?` — WebSearch. Step 1.
- `Expansion: how did we get here, and who disagrees (dissent)?` — Asta. Step 2, and the dissent search in step 4.
- `Fringe: what has the field overlooked?` — the fringe scripts. The end of step 2.
- `Characterisation: what does a paper do, and what did it find?` — Asta's snippet search, or the paper's full text from
  arXiv. Step 5.

Orientation and expansion need each other. A pass that uses only WebSearch produces a corpus top-heavy with preprints
and missing the methods they all cite. A pass that uses only Asta keyword search misses what the community has only just
started discussing.

How to call each service, their limits and failure modes, are in `docs/external_services.md`.

Concretely, a pass runs in eight steps, numbered 0 to 7: a preflight check, five steps that build the pool and the
coreset, then the output and the coverage test. The pool and the coreset are built in separate stages:

- `Pool` (steps 1–3) — broad and cheap. Everything in scope enters, with metadata only and no verification (see
  `docs/verification.md` for what verification means), and is clustered. Fringe candidates enter here too, so that
  clustering sees them.
- `Coreset` (steps 4–5) — small and expensive. A few papers per cluster are selected from the pool, in roles, and each
  is verified against body text. This is where the coreset idea applies (`docs/coresets.md`), and where most of the cost
  goes.
- `Output and coverage test` (steps 6–7) — the analysis is written from the coreset alone, then tested for sufficiency
  against pool papers that were not selected.

### Order of operations

Each operation is either a script, which is deterministic and costs no tokens, or model judgement, done by the agent
named. The main session runs the scripts in this table, between dispatches; a subagent runs only the scripts its own job
needs, such as `tools/fulltext.py` during verification (see `docs/dispatch.md`). Token figures are per pass. Those
marked `measured` come from previous runs in this repo; the rest are estimates, to be replaced by the per-step token
accounting in the retrieval log.

| step | stage | operation | by | what the model reads, and what it does | tokens |
| -- | -- | -- | -- | -- | -- |
| 0 | pool | Preflight | script: `tools/preflight.py`, then `survey-pass` | The script checks the Graph API, arXiv, `uv` and the Asta key; the agent makes one cheap call each to four Asta tools and WebSearch. Halts the pass if any check fails (`H1`). See `docs/external_services.md`. | est. under 5k |
| 1 | pool | Orient | `survey-pass` | Reads WebSearch results for the input's topic, questions and a recency window. Collects frontier candidates and the field's vocabulary, and resolves each to its canonical ID. | est. 50–100k |
| 2 | pool | Expand | `survey-pass` | Reads Asta traversal and search results: titles and abstracts. Judges each candidate in or out of scope, and adds the in-scope ones with `tools/assign.py add`. | about 0.85k per candidate screened (measured); 250k for 300 candidates |
| 2 | pool | Fetch pool data | script: `tools/pool.py` | — Fetches citations, reference lists and embeddings; fills `year`, `citations`, `cites`. | 0 |
| 2 | pool | Provisional clustering | script: `tools/cluster.py` | — Seeds the `new` fringe route. | 0; about 2 min per 200 papers (measured) |
| 2 | pool | Collect fringe candidates | script: `tools/fringe.py collect` | — Runs the `hidden` and `new` routes; writes the blind screening sheet. | 0 |
| 2 | pool | Screen fringe candidates | `survey-pass` | Reads the sheet: titles and abstracts, shuffled, without the route. Marks each in or out of scope on the sheet. | about 0.85k per candidate (measured: 123k for 146) |
| 2 | pool | Add fringe candidates | script: `tools/assign.py add-fringe` | — Adds the in-scope candidates to the Pool table; prints the log's `Fringe` line. | 0 |
| 2 | pool | Fetch again | script: `tools/pool.py` | — The same fetch, for the added papers. | 0 |
| 3 | pool | Cluster | script: `tools/cluster.py` | — Chooses the measure and level by stability, applies the input's `granularity` steering, and writes each paper's fringe score. This is the stability test. | 0; about 2 min per 200 papers (measured) |
| 3 | pool | Write the sheets | script: `tools/sheets.py` | — Writes the naming sheet and the fringe sheet. | 0 |
| 3 | pool | Name the clusters | `survey-pass` | Reads the naming sheet and the input. Writes one Clusters row per computed cluster: name, definition, alignment, reason and `computed` id; and the `Clustering rationale` in the log. Does not change membership. | est. 20–40k |
| 3 | pool | Carry names over, on a later pass | script: `tools/assign.py remap` | — Only when the Clusters table already has names: moves them to the clusters they matched; the agent names the rest. | 0 |
| 3 | pool | Write the clusters | script: `tools/assign.py clusters` | — Writes each pool paper's named cluster into the Pool table. | 0 |
| 3 | pool | Rewrite the sheets | script: `tools/sheets.py` | — So that the fringe sheet for step 4 shows the names. | 0 |
| 3 | pool | Build the viewer | script: `tools/graph.py` | — | 0 |
| 3 | pool | Cluster review, only if triggered | main session and user | Runs only when step 3 halts (see "Cluster review"). Reads the Clusters table and the `Clustering` log line; the user reviews in the viewer. Records the review and any override. | est. under 10k |
| 4 | coreset | Anchors | script, then `survey-pass` | In-degree within the pool comes from the file: `tools/check.py` prints each cluster's in-degree leaders, and the naming sheet lists each cluster's most-cited pool papers with titles. The agent confirms the pick and writes `selected because`. | est. 1–2k per cluster |
| 4 | coreset | Frontier | `survey-pass` | Reads the abstracts of each cluster's recent, high-impact pool papers and step 1's candidates. Picks the strongest recent result. | est. 5–10k per cluster |
| 4 | coreset | Dissent | `survey-pass` | Searches forward citations and runs challenge queries, for each high-alignment cluster. Reads the results and judges whether a paper really contradicts the cluster. | est. 20–50k per high-alignment cluster |
| 4 | coreset | Fringe | `survey-pass` | Reads the fringe sheet, the abstracts of its papers, and the coreset rows chosen so far. Keeps five to ten that each carry an idea no other row has. | est. 20–40k |
| 5 | coreset | Characterise and verify | `survey-pass` | Runs `snippet_search` at least twice per row, reads the snippets, and checks every cell against them. See `docs/verification.md`. | about 10k per row (earlier passes); 400–600k for 40–60 rows |
| 5 | coreset | Bibliography and checks | script: `tools/bib.py`, `tools/check.py` | — | 0 |
| 6 | output | Write the output | main session | Reads the Clusters section and the coreset: the rows, not the pool. Writes the Landscape, Assumptions, Gaps, Questions and Reading. | est. 60–120k |
| 7 | output | Coverage test | `survey-pass` | Reads the output and 10–15 unselected pool papers, including a few high fringe scores. For each, judges whether it opens a new cluster or would change a claim. | est. 30–50k per round |
| 7 | output | Late papers | script: `tools/assign.py late`, or `tools/cluster.py` then `tools/assign.py remap` | — Assigns the round's added papers to clusters, or reclusters and carries the names over (see "Late papers"). | 0 |

The expensive steps are verification, about half the total, and screening, which grows with the pool. As a rough
planning figure, a pass on a topic of about 50 coreset rows is estimated at 1–1.5M tokens. That is an estimate, not yet
measured on a coreset pass. The figures are for planning and for reporting, never limits. The size of the pool and the
coreset follows from the rules — scope, alignment and the coverage test — and is never trimmed to meet a cost estimate.
When a pass runs well over or under the estimate, say so in the report with the reason, so that the estimates can be
corrected.

## When a pass ends

A pass ends in one of two ways. It `finishes` when the coverage test shows the coreset is sufficient. It `halts` when
something happens that the pass must not decide alone: a service or script fails, the clustering is degenerate, or a
step needs the user's permission. This list is the only definition of both. The steps refer to its IDs.

How a halt works:

1. The agent that meets the condition stops its job and writes what is outstanding to Open work (`docs/formats.md`).
2. A subagent cannot reach the user. It returns a report whose first line is `STOP: <id> — <the reason>`, with the
   measured numbers.
3. The main session tells the user and waits. The user decides whether and how the pass continues. The decision goes
   into the log's `Halts` line.
4. If the pass continues past something missing, such as a failed service, the output's legend says what was missing.

A halt is not always a fault. `no structure`, for example, is a finding about the field.

**Finish.**

- `F1` — the coverage test converges: a round with no new cluster and at most one output change (step 7).

**Halt: services and scripts.**

- `H1` — a preflight check fails (step 0). A Graph API 429 counts as reachable: it means busy, and the scripts retry.
- `H2` — an Asta or WebSearch call still errors after the retry at the end of its step (`docs/external_services.md`,
  "Rate limits and errors").
- `H3` — a script fails after its own retries: a service error, or a crash with a Python traceback. Not `H3`: a script's
  printed `STOP: <id>`, which is that halt; a refusal that names the command to run first, such as
  `tools/assign.py clusters` before `remap`; and `tools/assign.py late` printing `RECLUSTER:` (exit 3). Failures of
  `tools/check.py` are `H9`.

**Halt: clustering, at step 3.** The main session shows the user the Clusters table and the viewer, and the pass resumes
from their decision (see "Cluster review").

- `H4` — `no structure` (see "When stability fails").
- `H5` — `no stable level`, still, after a targeted expansion and a rerun.
- `H6` — a cluster cannot be rated for alignment from the input.
- `H7` — a cluster the input expects (`expect`, in its `Clustering` section) is still missing after a targeted
  expansion.
- `H8` — the pool has fewer than 12 papers with an embedding, so no level of the grid can be computed (see "Clustering
  method"); `tools/cluster.py` prints `STOP: H8`. Checked before the first `tools/cluster.py` run, at step 2.

**Halt: integrity and verification.**

- `H9` — `tools/check.py` fails, and the agent whose work caused the failure cannot fix it.
- `H10` — after step 5, more than 20% of coreset rows are still `abstract`-sourced. The 20% is a first guess.

**Halt: convergence.**

- `H11` — two coverage-test rounds without convergence (step 7).

**Halt: permission.**

- `H12` — a paper should leave the pool. Deletion needs the user's explicit permission ("Rules for re-runs").

**Halt: requested by the user.**

- `H13` — the input's `Clustering` section asks for `review: before coreset`.

**Not end conditions.** These are handled inside the pass. Do not halt on them:

- `broad scope` — report it and continue ("When stability fails");
- `thin cluster` — expand the region and rerun;
- `unstable cluster` — flag it;
- clusters that trade papers — give the pair a bridge;
- an empty dissent slot — record what was searched;
- a query that returns no results — it has not errored;
- a single uncheckable row — it follows "Outcomes" in `docs/verification.md`;
- a pass that runs over or under its cost estimate — report the reason.

Record the end in the log's `Ended` line: `finished (F1)` or `halted (<id>)`, with the measured numbers.

## Before a pass: the preflight check (step 0)

At the start of every pass, before any retrieval, check that every external service answers: `tools/preflight.py` for
the Graph API, arXiv, `uv` and the Asta key, then one call each to four Asta tools (`snippet_search`,
`search_papers_by_relevance`, `get_paper`, `get_citations`) and to WebSearch, by the agent. The checks are in
`docs/external_services.md` ("Preflight"). If any check fails, halt (`H1`). Never fall back silently to another method,
such as WebSearch alone.

## Stage 1: the pool

### Step 1: orient

Run WebSearch from the input's topic, motivation and any stated research questions. Collect candidate frontier papers
and the vocabulary the field uses, and resolve each candidate to its canonical ID (`docs/formats.md`, "Paper IDs"). Run
orientation queries without a date restriction. In addition, run a set of recency queries limited to the period since
the last pass, or the last six months on a first pass, so that recent work is not drowned out. Record that window in the
log. It applies to the recency queries only: older work is in scope throughout, and step 2's backward traversal is what
reaches it.

Use WebSearch, including OpenReview, lab blogs, system cards and release notes. It surfaces the current frontier and the
names people use for the themes. It skews recent and well-publicised, which is exactly what this job needs.

### Step 2: expand

Traverse backward from the frontier candidates, and run relevance searches on the themes that step 1 named. Screen for
scope. Everything in scope enters the pool.

Use Asta.

- Backward traversal (`get_paper` references) from frontier papers finds what the field is built on, which is where
  anchors come from.
- Forward traversal (`get_citations`) from anchors and frontier papers finds follow-ups, and among them the dissent. It
  is targeted — searching a key paper's citers for challenges and extensions — not a crawl.
- `search_papers_by_relevance` and `snippet_search` fill in clusters that traversal does not reach.
- Asta supports date-restricted queries. Use them to keep recent work represented.

Add each in-scope paper to the Pool table with `python3 tools/assign.py add <topic> <paper-id> ...`, never by hand. Then
run `python3 tools/pool.py <topic>`, which fetches the metadata and clustering data for every pool paper by script (see
`docs/tooling.md`). Metadata is never fetched through a model's context.

Traversal from the frontier cannot reach papers the field has overlooked, so expansion ends with two fringe routes, run
by `tools/fringe.py collect` (see "Fringe routes" below). Screen their candidates like any others, on the screening
sheet; `tools/assign.py add-fringe` adds the in-scope ones to the pool. Then run `tools/pool.py` again. This happens
before clustering, because adding them changes the clusters.

#### Fringe routes

Fringe is not the dissent of the expansion job. A dissent paper engages a cluster and contradicts it, which is why
forward citations find it. A fringe paper is far from every cluster. They stand out by distance to their nearest
neighbours.

Use the scripts. Orientation and expansion both favour work that is well connected: relevance ranking rewards the
field's vocabulary, and traversal follows citations. A fringe paper is by definition poorly connected, so neither finds
it reliably. Two routes add overlooked papers to the pool at the end of step 2. Both run by script, at no model cost,
and the candidates are then screened blind: titles and abstracts in shuffled order, without the route that found them.

- `hidden` — papers cited by at least two pool papers, at least a year old, and the least cited overall for their age.
  The field's own work draws on them; the wider literature has not noticed them. This is where cross-field work turns
  up, such as older theory or psychology that current papers build on.
- `new` — Semantic Scholar recommendations seeded with each cluster's papers. The endpoint returns only the last two
  months of work, so this route catches what is too new to be cited. It needs clusters to seed from, so run
  `tools/cluster.py` once provisionally first; the real clustering follows once the pool is complete.

The routes call the Semantic Scholar Graph API directly rather than going through Asta. It is the same literature either
way; the difference is that the routes need an endpoint Asta lacks and a volume no model should read. See
`docs/external_services.md`, "Semantic Scholar Graph API".

Once candidates are in the pool, step 3 measures how far each paper sits from the rest: the fringe score, defined in
"Clustering method". Step 4 chooses `fringe` rows from it.

### Step 3: cluster

A cluster is a group of papers that share an approach, a question, or a line of results: for example "process reward
models", or "does RL create reasoning capability or only select it". Clusters are computed from the pool. They are never
copied from the input, or from a previous survey's section headings.

Run the clustering method below, which chooses the similarity measure and the level (scale from coarse to fine) from the
pool's own data. `tools/cluster.py` applies the input's `granularity` steering itself (see `docs/formats.md`), moving to
another computed level before anything is named. Then write the sheets (`tools/sheets.py`). The naming agent reads the
naming sheet, names and defines each computed cluster, rates its alignment (how directly it bears on the input's
questions, or as the input's `alignment` steering sets it), and writes the Clusters section, with each cluster's
`computed` id, and the `Clustering rationale` (see "Recording it"). `tools/assign.py clusters` then writes every pool
paper's cluster into the Pool table. Naming is judgement; membership is not. Do not move papers between clusters by
hand. Build the graph viewer (`tools/graph.py`); it shows the chosen parameters, each cluster's stability, and the level
below.

#### Clustering method

The aim is clusters that are well defined: a pass six months later should find recognisably the same ones. Stability is
measured directly, rather than assumed, so the method adapts to each literature instead of fixing a measure or a cluster
count in advance.

**Similarity measures.** A similarity measure says how alike two pool papers are. The clustering groups papers that the
measure rates as alike, so a different measure can give different clusters. Three measures are built from the pool's
sidecar data, and the method runs on all three:

- `text` — how alike the two papers' titles and abstracts are: the cosine similarity of their SPECTER2 embeddings.
- `refs` — how much of the literature the two papers build on together: the overlap of their full reference lists
  (bibliographic coupling).
- `combined` — both, each converted to per-paper neighbour ranks so their scales match, and mixed per pair with weight
  `w = n / (n + c)` on `refs`, where `n` is the shorter of the two reference lists. A pair with little reference data
  leans on text.

**Clustering.** Clustering turns a similarity measure into groups, in three steps:

1. `Neighbour graph` — link each paper to the 10 papers the measure rates most similar to it (`k`, set with `--k`). A
   link carries that similarity as its weight. Only these nearest links are kept; the rest are dropped. Without that,
   every paper would be weakly linked to every other, and the groups would blur.
2. `Groups` — the Leiden algorithm splits the graph into groups whose papers are more strongly linked to each other than
   chance would predict, given how strongly each paper is linked overall. An analogy: finding the friend groups in a
   school from who sits with whom, discounting the people who sit with everyone.
3. `Resolution` — Leiden has one setting, the resolution, that trades few large groups against many small ones. For each
   level, the resolution is searched until the clustering has the target number of clusters, counting only clusters of
   two or more papers. If the exact target cannot be reached, the closest is used.

The result depends on a random seed, so a clustering is reproducible only with its seed recorded. The stability tests
check how much that matters.

Each target number of clusters is a level, and the method runs over a grid of levels: 3, 4, 5, 6, 8, 10, 12, 15, 18 and
22 clusters by default. Levels above a quarter of the pool's size are dropped, so that clusters average at least four
papers. A pool of fewer than 12 papers therefore leaves no level, and the pass halts (`H8`).

**Choosing the measure.** There is no default measure: the choice is made on every topic, from its own pool, with the
stability tests below. Each measure's stability at a level is an estimate, the mean over many reruns, with a standard
error saying how much that mean would move if the reruns were repeated. To compare measures, average each one's
stability over the whole grid of levels, and combine the levels' standard errors. The measure with the highest average
wins, unless another measure is within two standard errors of it — a gap that small is probably noise — in which case
the two are tied. Ties go to `combined`, because it uses both kinds of evidence, and falls back on text for pairs with
little reference data.

Comparing at a single level would not work, because the ranking can flip from level to level. For example, a measure can
match another exactly at two levels and lose to it at a third, yet lead clearly on average over the grid. Cross-scored
cohesion (silhouette under `text` and under `refs`) is reported alongside but does not decide: on a single-topic pool it
sits near zero for every measure.

**Stability tests.** Stability is measured separately for each measure at each level. The tests are not steps in a
sequence. They are independent ways of disturbing the data, each compared against the same reference:

1. `Reference` — cluster the full pool once. The resolution found for the level is then held fixed for every rerun.
2. `Disturb and recluster` — each test reclusters a changed version of the data:
   - `time holdout` — keep only the papers older than a cutoff. Three cutoffs, three, six and nine months back, each run
     with three random seeds: nine reruns. A cutoff that would keep less than 30% of the pool is skipped. It asks
     whether these clusters would have been found months ago, which is the six-month criterion run backwards.
   - `resampling` — drop a random 20% of the papers. Twenty reruns by default (`--reps`). It asks whether the clusters
     depend on which particular papers retrieval happened to find.
   - `seeds` — cluster the full pool again, with five different random seeds. It asks whether the algorithm's own
     randomness matters.
3. `Compare` — score each rerun against the reference, over the papers both contain, with the adjusted Rand index (ARI).
   ARI asks of every pair of papers whether both clusterings put them together; 1 is identical, 0 is chance.
4. `Combine` — the stability of a measure at a level is the mean of two numbers: the mean holdout ARI and the mean
   resampling ARI, with a standard error from the spread across reruns. Seed agreement is reported alongside but does
   not enter the score.

Each cluster also gets a clusterwise score, from the resampling reruns: its best overlap (Jaccard) with any cluster in
each rerun, averaged. Clusters and sub-clusters of fewer than three papers get none. The overall score can hide a weak
cluster: ARI counts pairs of papers, so a small cluster dissolving barely moves it. The clusterwise score shows which
clusters are solid, and it drives the single-cluster diagnostics in "When stability fails" and the sub-cluster rule in
"Sizing".

**Choosing the level.** Plot the chosen measure's stability against the number of clusters. The chosen level is the
finest one whose stability still reaches a threshold `τ`, 0.75 by default: the last level before the curve falls off
into instability. Do not look for the largest single drop instead. Stability is usually highest at the coarsest level,
so the largest drop tends to be the first one, from a trivially stable split into a still-stable one. `τ` is a
convention, not a derived value, so the report also gives the level that `τ ± 0.05` would choose. The clusters at the
chosen level are the survey's clusters. The level below is kept as sub-clusters, shown in the viewer and used by
"Sizing" (step 4).

**The null model.** The same pipeline is also run on structure-free data of the same size and shape: random vectors with
the embeddings' mean and spread, and reference lists reshuffled among papers, keeping each paper's list length and each
reference's popularity. Real stability well above the null at a level shows the structure there is real. The report also
gives the threshold-free choice: the level with the largest excess over the null (`--rule null`). On a pool where null
stability is flat across levels, this rule reduces to "most stable" and picks the coarsest level. It is recorded
alongside, and does not decide by default.

**The fringe score.** `tools/cluster.py` also scores every pool paper for how poorly the rest of the pool covers it. For
each paper:

1. Average its similarity to its `k` nearest neighbours in the pool, and turn that into a distance: one minus the
   average.
2. Rank that distance among papers of about the same age, within one year either side, as a percentile from 0 to 1. If
   fewer than 10 papers share that age, rank it against the whole pool.
3. Score text and references separately. If the clustering chose `text`, use the text percentile. If it chose `refs` or
   `combined`, mix the two percentiles per paper, with weight `w = n / (n + c)` on references, where `n` is the paper's
   own number of resolved references, as in `combined`.

A score of 0.95 means the paper is further from its nearest neighbours than 95% of papers its age. The age correction is
there because older papers sit further from current work simply because the field moved on. Without it, the highest
scores would go mostly to old papers. The score is per paper, not per cluster, for a related reason. Clusters can gather
papers of the same period: overlooked older papers may settle into the cluster of the field's foundations, so a
cluster-level signal can reflect age more than novelty. A fringe paper shows up as distance to its nearest neighbours,
not as membership of an unusual cluster.

The weight on references is there because a paper with no resolved references shares none with anything, so by
references alone it would look maximally far from everything, for lack of data rather than for being overlooked. With
the weight, such a paper is scored by its text alone.

**Since when each cluster exists.** The stability test says whether the clusters are trustworthy now. It does not say
whether a cluster has existed for a while or only just formed. After choosing the level, `tools/cluster.py` answers that
separately, as post-processing: nothing above depends on it, and it never changes the clusters.

1. `Snapshots` — divide the pool by publication date into four segments with the same number of papers each. A burst of
   publications then gets narrower segments. Each snapshot is the pool as it stood at the end of a segment, so it
   includes everything earlier.
2. `Cluster and match` — cluster each snapshot with today's measure and number of clusters, at five seeds, and match it
   to today's clusters by shared papers (`tools/match.py`). A cluster is found in a snapshot if a majority of seeds find
   it.
3. `First seen` — the earliest snapshot from which a cluster is found in every later one. The result is one date per
   cluster, not one for the whole map, which the newest cluster would always drag to "today".

Where a cluster is not found, the report says why, from how many of its papers the snapshot already had. Fewer than 10
is a lack of data, not a change in the field: "too few papers". More means its papers existed but were grouped
differently, which is a real change. No papers are discarded to equalise snapshot sizes. A snapshot whose own stability
is below `τ` is itself unreliable, so what it finds is hedged: "probably since …".

Read the result with one caveat. Snapshots are drawn from today's pool, whose older papers are the ones still relevant
enough to be found and cited today. The history is therefore optimistic: a real earlier pass would have looked messier.
A cluster that formed only recently is a hint for the `frontier` role and the recency queries.

**Recording it.** Each pass records its clustering in its entry in the retrieval log, the first section of
`surveys/<topic>.md` (see `docs/formats.md`). The log's `Clustering` line records the measure, the level, the grid, `k`,
`c`, the cutoffs, and the stability figures that decided them. Next to it, the agent that names the clusters writes a
`Clustering rationale`: a short paragraph saying why the clusters look as they do. It covers the level and its margin
above `τ`, the spread of the clusterwise scores with the weak clusters named and diagnosed, how decisive the measure
choice was, what any steering in the input's `Clustering` section changed, and which clusters are long-standing and
which are recent, from the `Temporal stability` line. It interprets the figures rather than repeating them, and it does
not restate the steering request, which lives in the input. Log entries are never rewritten, so each pass keeps the
rationale for its own clusters. The full report stays in the sidecar, and the viewer displays the parameters and the
latest pass's rationale, so the user can see how the clusters were produced.

#### When stability fails

The coverage test has a clear consequence: add papers, or finish. The stability test needs one too. `tools/cluster.py`
diagnoses which of the cases below applies, prints each with its action, and the viewer shows them in its overview.

One rule holds in every case: never move papers between clusters by hand. The remedy is more data, a different level, or
a user override that is logged. Otherwise the clustering quietly becomes judgement again.

**The whole clustering.** No level is stable enough, or only a trivial one is. The null model says why:

- `no structure` — real stability exceeds random data's by less than 0.15 at every level. The pool may be one line of
  work, or too small to split. Use very few clusters, possibly one, and halt for review (`H4`); that is a finding about
  the field.
- `no stable level` — structure is above random, but no level reaches `τ`. The usual cause is a thin pool: too few
  papers per region, or many papers with few resolved references (the tool reports the share with fewer than 10). Expand
  the thinnest regions in step 2 and rerun. If it is still unstable, take the coarsest level and halt for review (`H5`),
  so that the user chooses with the slider.

**A broad scope is not a failure.** Sometimes only the coarsest level reaches `τ`, and very stably (0.9 or more). The
pool then divides into a few clearly separate areas, while finer divisions are unstable. The clusters are real and
reproducible, so nothing has failed: it is a fact about the scope. `tools/cluster.py` reports it as `broad scope`. Say
so in the `Clustering rationale`, and continue at that level without halting. Whether a few broad clusters are enough
for the input is a question about the coreset, not about the clusters, and the coverage test (step 7) answers it.

**Single clusters.** The level is stable, but some clusters are not (clusterwise score below 0.6). Here instability is
information, and the action depends on the pattern:

- `thin cluster` — fewer than 10 papers. It dissolves into its neighbours, which the tool names. Expand that region in a
  targeted way and rerun. A thin cluster can be a sampling problem rather than a false one, and a handful of added
  papers may be enough to make it coherent. A cluster of fewer than three papers has no clusterwise score, so the tool
  does not diagnose it. Treat it as thin.
- `clusters trade papers` — two unstable clusters whose papers are grouped together in at least 20% of rerun pairs.
  Their boundary is open in the field itself. Keep both. At selection, give the pair a `bridge` paper, and note the
  tension for the Landscape.
- `unstable cluster` — neither of the above. Flag it in the report and the viewer. It does not halt the pass.

#### Cluster review

By default the pass does not halt here; the user reviews the clusters with the finished output. This is affordable
because verification belongs to a row, not to a cluster: a later change to the clustering costs re-selection and the
verification of new rows only (see "Changing the clusters after a pass"). Halt before selecting the coreset only on one
of the clustering conditions in "When a pass ends", `H4`–`H8`, or when the input asks for it (`H13`). Otherwise proceed
to step 4.

Apart from `H13`, these are signs that the topic was misread or the pool is degenerate. Found here, such a problem costs
a fraction of what it costs after verification. The main session shows the user the Clusters table and the viewer, and
records the halt and the user's decision in the log. Any change the user makes is recorded as a manual override.

How much detail to keep is a trade-off between detail and stability, so the level is shown to the user rather than only
reported, whenever the review happens. The viewer's similarity map lays papers out by the clustering measure itself, and
its level slider recolours the map at each computed level. If the user picks a different level, record it in the log as
a manual override, and rerun `tools/cluster.py <topic> --level <N>`, with `N` as the slider shows it. Then carry the
names over with `tools/assign.py remap` (see "Late papers").

#### Late papers

A late paper is one that reaches the pool after step 3: a coverage-test candidate that changed the output, a probe's
find, a paper an output needs for a new claim, or a paper from a targeted expansion. It has no cluster, and nobody may
give it one by hand. Late papers are added to the Pool table like any other (`tools/assign.py add`), with an empty
`cluster` cell; those rows are the queue. `tools/check.py` lists them.

The queue is processed in batches, never paper by paper: once per coverage-test round, and before any re-run of step 4.
A batch is one command, `uv run tools/assign.py late <topic>`. It fetches the papers' data, and assigns each to the
cluster that its `k` nearest clustered papers favour, by the chosen measure: each neighbour votes for its cluster with
its similarity, and the largest total wins. A paper with no positive similarity under that measure is placed by text.
Each paper is assigned against the clustering as it stood, never against other late papers, so the result does not
depend on order. The script records every assignment and prints the log's `Late papers` line. Only then does a late
paper take a role.

Recluster instead, with `tools/cluster.py`, in two cases:

- `Many late papers` — late papers since the last full clustering would exceed 10% of the pool. `tools/assign.py late`
  refuses and says so. The clusters survive losing 20% of the papers, so a few late papers rarely move them, but a large
  addition can: adding the 118 fringe candidates on `reasoning` moved the clustering to ARI 0.70.
- `A new cluster` — the coverage test judged that a candidate belongs to a cluster not in the Clusters table. That
  judgement never creates a cluster. It triggers a targeted expansion of the region (the `More data` lever); the
  expansion's in-scope papers join the batch, and the batch is reclustered. If the region is real, it forms a cluster.
  If not, the computation places its papers in existing clusters, and the data has overruled the judgement.

After a recluster, carry the names over: `tools/cluster.py` matches the new clustering to the one the Clusters table
names, by shared papers, and `tools/assign.py remap <topic>` moves each name to the cluster it matched. Until then,
`tools/check.py` and `tools/assign.py clusters` refuse. On a first pass there are no names yet, so the provisional
clustering of step 2 needs no remap; on a later pass, run `remap` once, after the clustering of step 3. Clusters that
did not match, and new ones, are named again (step 3), and step 4 is re-run for them. Expansions run before their batch
is processed, so a round has at most one recluster, and two rounds without convergence halt the pass (`H11`).

## Stage 2: the coreset

### Step 4: select

Each coreset paper is selected to play one role in its cluster. Which roles a cluster gets follows its alignment (see
"Sizing" below). Record in the `selected because` column why each paper fills its role. Why the roles exist, and why
ranking alone is not enough, is in `docs/coresets.md` ("How coverage is achieved").

- `anchor` — what the cluster is built on. Anchors come from in-degree within the pool: usually the paper most cited by
  the other pool papers.
- `frontier` — where the cluster currently stands: its strongest recent result. Frontier papers come from step 1, where
  WebSearch usually surfaces them, and from recent, high-impact pool entries.
- `dissent` — a paper that contradicts the cluster's consensus, breaks one of its assumptions, or reports a negative
  result against its central claim. Dissent needs a dedicated search for each high-alignment cluster. Search the forward
  citations of the cluster's anchor and frontier papers, and run relevance queries phrased as challenges: "fails to",
  "does not", "revisiting", "limits of", "rethinking", etc. If a search finds no dissent, record that the slot is empty
  and what was searched. An empty dissent slot is information about the cluster, not a failure.
- `bridge` — a paper that connects two clusters, for example by applying one cluster's method to another's question.
  Written `bridge:<other-cluster-id>`. It is optional, but bridges are where the Landscape's structure becomes visible.
  Where the clustering diagnostics report two clusters trading papers, one of them gets a bridge paper.
- `fringe` — a paper that carries an idea no other coreset row has, and that the field has so far overlooked: it sits
  far from its nearest neighbours in the pool, for its age. It is placed in the cluster it was computed into, but it
  does not represent that cluster; it represents what the clusters leave out. Fringe comes last, because its test is
  relative to the rest of the coreset. Start from the pool papers with the highest fringe scores (see "Clustering
  method"). Most papers far from their neighbours are there for a good reason. So keep a paper only if its
  `selected because` can name, in one sentence, the idea it carries that no other coreset row does. Five to ten per
  topic.

**Sizing.** A cluster gets more rows the more directly it bears on the input, not the more papers it has:

- `high` — anchor, frontier and dissent at minimum. Add a second frontier paper or a bridge where the cluster is
  internally divided.
- `medium` — anchor and frontier.
- `low` — anchor only. That is enough for the Landscape to be honest about the cluster existing.

The number of clusters is not chosen; it is the stable level found in step 3. Where the level below it splits a
high-alignment cluster into two or more sub-clusters with a clusterwise score of at least 0.6, the cluster counts as
internally divided and gets the extra frontier or bridge. Expect roughly two to four rows per cluster, plus the topic's
five to ten `fringe` rows. Past roughly 80 rows, check whether any role is filled twice. If none is, the size is
legitimate, for example on a topic with many `high` clusters; report the count and the reason.

### Step 5: characterise and verify

Characterise and verify every selected paper. See `docs/verification.md`.

The sources are Asta's `snippet_search`, or the paper's own full text from arXiv, fetched by `tools/fulltext.py` when
snippets do not reach the claim. WebSearch may corroborate a claim about a paper but must never be its only source.

## Stage 3: output and coverage test

### Step 6: write the output

Write the output in the main session, from the Clusters section and the coreset rows alone, never from the pool. Its
analyses and format are in `docs/formats.md`.

### Step 7: the coverage test

This is the finishing rule (`F1`). The coreset is sufficient when adding papers stops changing the output. Measure that
directly:

1. Draw a sample of 10–15 candidates that are not in the coreset. Weight it toward the clusters with the fewest coreset
   rows relative to their pool size, include new material from a fresh recency query, and include a few of the highest
   fringe scores not selected.
2. For each candidate, ask two questions. Does it belong to a cluster not yet in the Clusters table? Would it change a
   claim in one of the coreset's targets — a landscape axis, an assumption, a gap, or an answer to a question the
   input's `Coreset Spec` declares? Targets are defined in `docs/formats.md` (`Coreset Spec`). `Questions` and `Reading`
   are not targets, and a change to them alone does not count.
3. Record the result in the pass's entry in the retrieval log, as a `Coverage test` line:
   `K of N sampled candidates changed the output`. Name each candidate that did, with what it changed: the target and
   the claim, such as a new gap or a revised assumption. Name any new cluster too. Each round gets its own line. The
   format is in `docs/formats.md` ("1. Retrieval log").

The pass finishes (`F1`) when a round produces no new cluster and at most one output change. Say so in the log's `Ended`
line, with the numbers. Otherwise, add the papers that changed things to the pool, process them as a batch of late
papers (see "Late papers"), give them their proper roles, revise the output, and sample again. Two rounds without
convergence halt the pass (`H11`).

Do not finish on the fraction of screened candidates already present in the survey instead. On an active topic that
fraction falls as the seeds improve, because each better seed opens a larger neighbourhood, so it may never reach any
threshold.

## Later passes

### Rules for re-runs

On revisiting a topic, add a new dated pass to the retrieval log. A later pass may add clusters, pool entries and
coreset rows.

- **Demotion is not deletion.** If a better paper is found for a role, the old row may leave the coreset. The paper
  stays in the pool, and the log records the demotion and why.
- **Deletion needs permission.** Remove a paper from the pool only if it is conclusively shown to be factually wrong or
  out of scope, and only with the user's explicit permission. Asking is a halt (`H12`): state the argument in the
  `STOP:` report, and the main session puts it to the user.
- **Corrections are logged.** Edit a row in place and record the change in that pass's log entry.
- Where a later pass supersedes a caveat recorded in an earlier one, leave the earlier text intact and add a pointer
  saying what superseded it. The old entry is an accurate record of the pass it describes.

### Changing the clusters after a pass

The user can steer the clustering through a fixed set of levers. Each can be given in advance, in the input's
`Clustering` section, or requested after a pass. Membership is not one of them: papers are never moved between clusters
by hand.

- `Level` — a coarser or finer clustering, chosen with the viewer's slider. Merging two clusters means a coarser level;
  splitting one means a finer level.
- `Alignment` — how directly a cluster bears on the input. It sets the cluster's rows and dissent searches.
- `Names and definitions` — judgement only; edit them directly.
- `Scope` — a cluster the user does not want. Rate it `low`, which keeps one anchor so the Landscape stays honest. If it
  is genuinely out of scope, its papers leave the pool under the deletion rule above, with permission.
- `More data` — seeds or queries for a region, followed by re-clustering. This is the route for "these papers belong
  together".

A change requested after a pass runs as an incremental pass, logged as a manual override. Re-cluster if the level or the
pool changed, and carry the names over (`tools/assign.py remap`, see "Late papers"). The clusters that changed are the
ones `remap` did not match. Re-run step 4 for them, keeping every verified row that still fills a role and demoting the
rest. Verify only the new rows, then rerun the coverage test and revise the output.

Dimensions are the exception to cheap late changes. A dimension added after verification has to be re-derived from the
body text of every row, which costs a large part of a verification round. Declare dimensions in the input where
possible.

### Matching clusters across passes

On a later pass, match the new clustering to the previous one, keep the ids and names of matched clusters, and log
splits, merges, new clusters and vanished ones. `tools/cluster.py` does the matching (`tools/match.py`, `match`)
whenever a previous clustering exists, and `tools/assign.py remap` keeps the names; record its output under
`Clustering rationale`. What is not yet built is the diagnosis for when most clusters fail to match; see
`docs/roadmap.md`.

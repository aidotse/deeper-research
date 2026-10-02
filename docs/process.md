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
and missing the methods they all cite; this has happened in this repo. A pass that uses only Asta keyword search misses
what the community has only just started discussing.

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
named. Token figures are per pass. Those marked `measured` come from previous runs in this repo; the rest are estimates,
to be replaced by the per-step token accounting in the retrieval log.

| step | stage | operation | by | what the model reads, and what it does | tokens |
| -- | -- | -- | -- | -- | -- |
| 0 | pool | Preflight | `survey-pass` | Makes one cheap call to each external service and records the outcome. Stops the pass if a required one fails. See `docs/external_services.md`. | est. under 5k |
| 1 | pool | Orient | `survey-pass` | Reads WebSearch results for the input's topic, questions and a recency window. Collects frontier candidates and the field's vocabulary, and resolves each to an arXiv ID. | est. 50–100k |
| 2 | pool | Expand | `survey-pass` | Reads Asta traversal and search results: titles and abstracts. Judges each candidate in or out of scope. | about 0.85k per candidate screened (measured); 250k for 300 candidates |
| 2 | pool | Fetch pool data | script: `tools/pool.py` | — Fetches citations, reference lists and embeddings; fills `year`, `citations`, `cites`. | 0 |
| 2 | pool | Provisional clustering | script: `tools/cluster.py` | — Seeds the `new` fringe route. | 0; about 2 min per 200 papers (measured) |
| 2 | pool | Collect fringe candidates | script: `tools/fringe.py collect` | — Runs the `hidden` and `new` routes; writes the blind screening sheet. | 0 |
| 2 | pool | Screen fringe candidates | `survey-pass` | Reads the sheet: titles and abstracts, shuffled, without the route. Judges scope, and adds the in-scope papers to the pool. | about 0.85k per candidate (measured: 123k for 146) |
| 2 | pool | Fetch again | script: `tools/pool.py` | — The same fetch, for the added papers. | 0 |
| 3 | pool | Cluster | script: `tools/cluster.py` | — Chooses the measure and level by stability, and writes each paper's fringe score. This is the stability test. | 0; about 2 min per 200 papers (measured) |
| 3 | pool | Name the clusters | `survey-pass` | Reads each computed cluster's most-cited titles, its sub-clusters and the input. Writes the name, definition, alignment and reason. Does not change membership. | est. 20–40k |
| 3 | pool | Build the viewer | script: `tools/graph.py` | — | 0 |
| 3 | pool | Cluster review, only if triggered | main session and user | Runs only when step 3 stops (see "Cluster review"). Reads the Clusters table and the `Clustering` log line; the user reviews in the viewer. Records the review and any override. | est. under 10k |
| 4 | coreset | Anchors | script, then `survey-pass` | In-degree within the pool comes from the file, and `tools/check.py` reports each cluster's leader. The agent confirms the pick and writes `selected because`. | est. 1–2k per cluster |
| 4 | coreset | Frontier | `survey-pass` | Reads the abstracts of each cluster's recent, high-impact pool papers and step 1's candidates. Picks the strongest recent result. | est. 5–10k per cluster |
| 4 | coreset | Dissent | `survey-pass` | Searches forward citations and runs challenge queries, for each high-alignment cluster. Reads the results and judges whether a paper really contradicts the cluster. | est. 20–50k per high-alignment cluster |
| 4 | coreset | Fringe | `survey-pass` | Reads the abstracts of the highest fringe scores, and the coreset rows chosen so far. Keeps five to ten that each carry an idea no other row has. | est. 20–40k |
| 5 | coreset | Characterise and verify | `survey-pass` | Runs `snippet_search` at least twice per row, reads the snippets, and checks every cell against them. See `docs/verification.md`. | about 10k per row (earlier passes); 400–600k for 40–60 rows |
| 5 | coreset | Bibliography and checks | script: `tools/bib.py`, `tools/check.py` | — | 0 |
| 6 | output | Write the output | main session | Reads the Clusters section and the coreset: the rows, not the pool. Writes the Landscape, Assumptions, Gaps, Questions and Reading. | est. 60–120k |
| 7 | output | Coverage test | `survey-pass` | Reads the output and 10–15 unselected pool papers, including a few high fringe scores. For each, judges whether it opens a new cluster or would change a claim. | est. 30–50k per round |

The expensive steps are verification, about half the total, and screening, which grows with the pool. As a rough
planning figure, a pass on a topic of about 50 coreset rows is estimated at 1–1.5M tokens. That is an estimate, not yet
measured on a coreset pass. The figures are for planning and for reporting, never limits. The size of the pool and the
coreset follows from the rules — scope, alignment and the coverage test — and is never trimmed to meet a cost estimate.
When a pass runs well over or under the estimate, say so in the report with the reason, so that the estimates can be
corrected.

## Before a pass: the preflight check (step 0)

At the start of every pass, before any retrieval, check that every external service answers. The checks, and what to do
when one fails, are in `docs/external_services.md` ("Preflight"). If any part of any API of any external service is
unavailable, **stop and tell the user**: do not fall back silently to other methods like WebSearch alone.

## Stage 1: the pool

### Step 1: orient

Run WebSearch from the input's topic, motivation and any stated research questions. Collect candidate frontier papers
and the vocabulary the field uses, and resolve each candidate to an arXiv ID. Run orientation queries without a date
restriction. In addition, run a set of recency queries limited to the period since the last pass, or the last six months
on a first pass, so that recent work is not drowned out. Record that window in the log. It applies to the recency
queries only: older work is in scope throughout, and step 2's backward traversal is what reaches it.

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

Then run `python3 tools/pool.py <topic>`, which fetches the metadata and clustering data for every pool paper by script
(see `docs/tooling.md`). Metadata is never fetched through a model's context.

Traversal from the frontier cannot reach papers the field has overlooked, so expansion ends with two fringe routes, run
by `tools/fringe.py collect` (see "Fringe routes" below). Screen their candidates like any others, add the in-scope ones
to the pool, and run `tools/pool.py` again. This happens before clustering, because adding them changes the clusters.

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

Run the clustering method below, which chooses the similarity measure and the level (see below) from the pool's own
data. Then name and define each computed cluster, rate its alignment, and write the Clusters section. Naming is
judgement; membership is not. Do not move papers between clusters by hand. Apply the input's `Clustering` steering, if
any (see `docs/formats.md`), and build the graph viewer (`tools/graph.py`); it shows the chosen parameters, each
cluster's stability, and the level below.

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
22 clusters by default.

**Choosing the measure.** There is no default measure: the choice is made on every topic, from its own pool. Compare the
three measures' stability curves, from the stability tests below, averaged over the whole grid, not at one level. A
measure must win by more than two standard errors; single levels may go either way. Within that margin it is a tie, and
the tie goes to `combined`, because it is the one cohesive under both text and references. Cross-scored cohesion (silhouette under `text` and under `refs`) is reported alongside but does not decide: on a single-topic pool it sits near zero for every measure.

**Stability tests.** Stability is measured separately for each measure at each level. The tests are not steps in a
sequence. They are independent ways of disturbing the data, each compared against the same reference:

1. `Reference` — cluster the full pool once. The resolution found for the level is then held fixed for every rerun.
2. `Disturb and recluster` — each test reclusters a changed version of the data:
   - `time holdout` — keep only the papers older than a cutoff. Three cutoffs, three, six and nine months back, each run
     with three random seeds: nine reruns. It asks whether these clusters would have been found months ago, which is the
     six-month criterion run backwards.
   - `resampling` — drop a random 20% of the papers. Twenty reruns by default (`--reps`). It asks whether the clusters
     depend on which particular papers retrieval happened to find.
   - `seeds` — the full pool again, with five different random seeds. It asks whether the algorithm's own randomness
     matters.
3. `Compare` — score each rerun against the reference, over the papers both contain, with the adjusted Rand index (ARI).
   ARI asks of every pair of papers whether both clusterings put them together; 1 is identical, 0 is chance.
4. `Combine` — the stability of a measure at a level is the mean of two numbers: the mean holdout ARI and the mean
   resampling ARI, with a standard error from the spread across reruns. Seed agreement is reported alongside but does
   not enter the score.

Each cluster also gets a clusterwise score, from the resampling reruns: its best overlap (Jaccard) with any cluster in
each rerun, averaged. Clusters of fewer than three papers get none.

**Choosing the level.** Plot the chosen measure's stability against the number of clusters. The chosen level is the
finest one whose stability still reaches a threshold `τ`, 0.75 by default: the last level before the curve falls off
into instability. Do not look for the largest single drop instead. Stability is usually highest at the coarsest level,
so the largest drop tends to be the first one, from a trivially stable split into a still-stable one. `τ` is a
convention, not a derived value, so the report also gives the level that `τ ± 0.05` would choose. The clusters at the
chosen level are the survey's clusters. The level below is kept as sub-clusters, shown in the viewer and used by
"Sizing".

**The null model.** The same pipeline is also run on structure-free data of the same size and shape: random vectors with
the embeddings' mean and spread, and reference lists reshuffled among papers, keeping each paper's list length and each
reference's popularity. Real stability well above the null at a level shows the structure there is real. The report also
gives the threshold-free choice: the level with the largest excess over the null (`--rule null`). On a pool where null
stability is flat across levels, as on the first topic, this rule reduces to "most stable" and picks the coarsest level.
It is recorded alongside, and does not decide by default.

**The fringe score.** `tools/cluster.py` also scores every pool paper for how poorly the rest of the pool covers it. For
each paper:

1. Average its similarity to its `k` nearest neighbours in the pool, and turn that into a distance: one minus the
   average.
2. Rank that distance among papers of about the same age, within one year either side, as a percentile from 0 to 1. If
   fewer than 10 papers share that age, rank it against the whole pool.
3. Use the measure the clustering chose. With `combined`, score text and references separately and average the two
   percentiles.

A score of 0.95 means the paper is further from its nearest neighbours than 95% of papers its age. The age correction is
there because older papers sit further from current work simply because the field moved on. Without it, the highest
scores would go mostly to old papers. The score is per paper, not per cluster, for a related reason: in the fringe test
on the first topic, `hidden` papers gathered in the cluster of the field's older foundations, so their clustering mostly
reflected age. Fringe papers did not stand out by switching clusters, only by distance to their nearest neighbours.

**Recording it.** The retrieval log's `Clustering` line records the measure, the level, the grid, `k`, `c`, the cutoffs,
and the stability figures that decided them. The full report stays in the sidecar, and the viewer displays the
parameters, so the user can see how the clusters were produced.

#### When stability fails

The coverage test has a clear consequence: add papers, or stop. The stability test needs one too. `tools/cluster.py`
diagnoses which of the cases below applies, prints each with its action, and the viewer shows them in its overview.

One rule holds in every case: never move papers between clusters by hand. The remedy is more data, a different level, or
a user override that is logged. Otherwise the clustering quietly becomes judgement again.

**The whole clustering.** No level is stable enough, or only a trivial one is. The null model says why:

- `no structure` — real stability exceeds random data's by less than 0.15 at every level. The pool may be one line of
  work, or too small to split. Use very few clusters, possibly one, and stop for review; that is a finding about the
  field.
- `no stable level` — structure is above random, but no level reaches `τ`. The usual cause is a thin pool: too few
  papers per region, or many papers with few resolved references (the tool reports the share). Expand the thinnest
  regions in step 2 and rerun. If it is still unstable, take the coarsest level and stop for review, so that the user
  chooses with the slider.
- `scope too broad` — only the coarsest level reaches `τ`, and very stably (0.9 or more). The pool probably mixes
  unrelated topics, which separate cleanly while everything finer collapses. Ask the user whether the input should be
  split into two topics.

**Single clusters.** The level is stable, but some clusters are not (clusterwise score below 0.6). Here instability is
information, and the action depends on the pattern:

- `thin cluster` — fewer than 10 papers. It dissolves into its neighbours, which the tool names. Expand that region in a
  targeted way and rerun. On the first topic, adding ten recent papers turned a 5-paper cluster at 0.18 into a coherent
  17-paper one.
- `clusters trade papers` — two unstable clusters whose papers are grouped together in at least 20% of rerun pairs.
  Their boundary is open in the field itself. Keep both. At selection, give the pair a `bridge` paper, and note the
  tension for the Landscape.
- `unstable cluster` — neither of the above. Flag it in the report and the viewer. It does not stop the pass.

#### Cluster review

By default the pass does not stop here; the user reviews the clusters with the finished output. This is affordable
because verification belongs to a row, not to a cluster: a later change to the clustering costs re-selection and the
verification of new rows only (see "Changing the clusters after a pass"). Stop and show the user the Clusters table
before selecting the coreset only when one of these holds:

- the input's `Clustering` asks for `review: before coreset`;
- a whole-clustering diagnostic fires: `no structure`, `no stable level` or `scope too broad` (see "When stability
  fails");
- a cluster cannot be rated for alignment from the input;
- a cluster the input expects is still missing after a targeted expansion.

The last three are signs that the topic was misread or the pool is degenerate. Found here, such a problem costs a
fraction of what it costs after verification. Record whether the pass stopped, and why, in the log. Any change the user
makes is recorded as a manual override.

How much detail to keep is a trade-off between detail and stability, so the level is shown to the user rather than only
reported, whenever the review happens. The viewer's similarity map lays papers out by the clustering measure itself, and
its level slider recolours the map at each computed level. If the user picks a different level, record it in the log as
a manual override.

## Stage 2: the coreset

### Step 4: select

Fill each cluster's roles according to "Sizing" in `docs/surveys.md`, and record in the `selected because` column why
each paper fills its role.

- Anchors come from in-degree within the pool.
- Frontier papers come from step 1 and from recent, high-impact pool entries.
- Dissent needs a dedicated search for each high-alignment cluster. Search the forward citations of the cluster's anchor
  and frontier papers, and run relevance queries phrased as challenges: "fails to", "does not", "revisiting", "limits
  of", "rethinking". If a search finds no dissent, record that the slot is empty and what was searched. An empty dissent
  slot is information about the cluster, not a failure.
  - Where the clustering diagnostics report two clusters trading papers, one of them gets a `bridge:<other-id>` paper.
- Fringe comes last, because its test is relative to the rest of the coreset. Start from the pool papers with the
  highest fringe scores (see "Clustering method"). Keep a paper only if its `selected because` can name, in one
  sentence, the idea it carries that no other coreset row does. Five to ten per topic.

### Step 5: characterise and verify

Characterise and verify every selected paper. See `docs/verification.md`.

The sources are Asta's `snippet_search`, or the paper's own full text from arXiv, fetched by `tools/fulltext.py` when
snippets do not reach the claim. WebSearch may corroborate a claim about a paper but must never be its only source.

## Stage 3: output and coverage test

### Step 6: write the output

Write the output in the main session, from the Clusters section and the coreset rows alone, never from the pool. Its
analyses and format are in `docs/formats.md`.

### Step 7: the coverage test

This is the stopping rule. The coreset is sufficient when adding papers stops changing the output. Measure that
directly:

1. Draw a sample of 10–15 candidates that are not in the coreset. Weight it toward the clusters with the fewest coreset
   rows relative to their pool size, include new material from a fresh recency query, and include a few of the highest
   fringe scores not selected.
2. For each candidate, ask two questions. Does it belong to a cluster not yet in the Clusters table? Would it change a
   claim in one of the coreset's targets — a landscape axis, an assumption, a gap, or an answer to a question the
   input's `Coreset Spec` declares? `Questions` and `Reading` are not targets; see `docs/coresets.md`.
3. Record the result as `K of N sampled candidates changed the output`, and name the ones that did.

Stop when a round produces no new cluster and at most one output change. Say so in the log, with the numbers. Otherwise,
add the papers that changed things in their proper roles, revise the output, and sample again. Two rounds without
convergence stop the pass: report to the user and ask how to proceed.

This replaces an earlier rule based on the fraction of screened candidates already present in the survey. On an active
topic that fraction falls as the seeds improve, because each better seed opens a larger neighbourhood. On this repo's
first topic it measured 4–12% on the best seeds and could never have reached its threshold.

## Later passes

### Rules for re-runs

On revisiting a topic, add a new dated pass to the retrieval log. A later pass may add clusters, pool entries and
coreset rows.

- **Demotion is not deletion.** If a better paper is found for a role, the old row may leave the coreset. The paper
  stays in the pool, and the log records the demotion and why.
- **Deletion needs permission.** Remove a paper from the pool only if it is conclusively shown to be factually wrong or
  out of scope. Present the argument to the user and get explicit permission first.
- **Corrections are logged.** Edit a row in place and record the change in that pass's log entry.
- Where a later pass supersedes a caveat recorded in an earlier one, leave the earlier text intact and add a pointer
  saying what superseded it. The old entry is an accurate record of the pass it describes.

### Changing the clusters after a pass

The user steers the clustering through a fixed set of levers. Each can be given in advance, in the input's `Clustering`
section, or requested after a pass. Membership is not one of them: papers are never moved between clusters by hand.

- `Level` — a coarser or finer clustering, chosen with the viewer's slider. Merging two clusters means a coarser level;
  splitting one means a finer level.
- `Alignment` — how directly a cluster bears on the input. It sets the cluster's rows and dissent searches.
- `Names and definitions` — judgement only; edit them directly.
- `Scope` — a cluster the user does not want. Rate it `low`, which keeps one anchor so the Landscape stays honest. If it
  is genuinely out of scope, its papers leave the pool under the deletion rule above, with permission.
- `More data` — seeds or queries for a region, followed by re-clustering. This is the route for "these papers belong
  together".

A change requested after a pass runs as an incremental pass, logged as a manual override. Re-cluster if the level or the
pool changed. Re-run step 4 for the clusters that changed, keeping every verified row that still fills a role and
demoting the rest. Verify only the new rows, then rerun the coverage test and revise the output.

Dimensions are the exception to cheap late changes. A dimension added after verification has to be re-derived from the
body text of every row, which costs a large part of a verification round. Declare dimensions in the input where
possible.

### Matching clusters across passes

On a later pass, match the new clustering to the previous one, keep the ids and names of matched clusters, and log
splits, merges, new clusters and vanished ones. Not yet built; see `docs/roadmap.md`.

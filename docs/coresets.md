# Coresets: the framing behind the spec

This file collects what the repo means by a coreset, where the idea comes from, and what follows from it. The rest of
the spec applies these ideas in context and keeps its own descriptions short; this is where the reasoning lives. Read it
when a design question turns on what the coreset is for, or when a rule elsewhere seems arbitrary.

## Definition

A coreset is the smallest set of papers that represents the ideas in a body of work well enough that the output's
answers are stable. Two tests define it:

- `Sufficiency` — adding more papers from the pool should not significantly change the output.
- `Minimality` — taking a paper away from the coreset should change it.

"The output's answers" means the coreset's targets. By default these are the output's `Landscape`, `Assumptions` and
`Gaps`. An input may declare others in its `Coreset Spec`, such as specific research questions. The working definition
is in `docs/formats.md` (`Coreset Spec`). The targets need a fixed list because the coverage test counts only changes to
them: counting a change to the reading list, for example, could keep the test from ever converging.

## Where the idea comes from

The term is borrowed from active learning, specifically from Sener and Savarese's core-set approach (ICLR 2018; arXiv
`1708.00489`, verified from body text). Their problem: choose which unlabelled points to label, on a fixed budget. Their
hypothesis is "that a good way to choose points to be labelled is to cover the unlabelled data points as closely as
possible with labeled points". They cast it as the k-center problem: "choose k center points such that the largest
distance between a data point and its nearest center is minimized" (snippet, "Robust k-Center").

That is a covering construction. The quality of the subset is measured by its worst-covered point: the radius of balls
around the chosen points needed to cover everything. It is exactly the property we want, with the analogy mapped like
this:

| active learning | this repo |
| -- | -- |
| unlabelled data points | the pool |
| points chosen for labelling | the coreset |
| labelling a point, which is expensive | verifying a row, about 10k tokens each |
| the model trained on the labels | the output written from the rows |
| every point near a chosen point | every idea in the pool represented by a row |

One difference is deliberate. Sener and Savarese's robust variant allows a bounded number of outliers to go uncovered,
because for training a classifier an outlier is noise. For a literature survey an outlier may be the most valuable paper
in the pool. The `fringe` role exists to cover exactly those points (see `How coverage is achieved`).

There is a second family of coresets, in computational geometry, that approximates sums rather than covering points.
Feldman and Langberg (STOC 2011; arXiv `1106.1379`) frame a coreset as a "compressed representation" of a set of
functions, from which a sum over the whole set can be approximated (abstract). That family approximates totals and
averages, and it does so by sampling points non-uniformly and weighting them: their k-median construction draws "a
non-uniform random sample" and returns "a weighted ε-coreset" (snippet, "From bicriteria to coresets"). Our coreset is
of the covering kind and carries no weights. The difference is what decides whether a coreset can give field statistics;
see `What a coreset cannot tell you`.

## Why not collect everything

The naive alternative is to traverse citations from seed papers until some limit. The spec does not do only this, for
three reasons:

- `It never finishes` — for an active topic, the literature grows faster than it can be read. A traversal has no natural
  stopping point, only an arbitrary one.
- `It dilutes` — every extra paper takes attention from the themes and pivots an analysis turns on. A survey of 200
  papers in which 20 carry the argument is harder to use than a survey of 40 in which all of them do.
- `It cannot be verified` — verification to publication grade costs about 10k tokens per row. That is affordable for 50
  rows, not for 500. A small set is what makes every row trustworthy.

## Pool and coreset

The coreset is selected from a larger set, the pool, and the two are built in separate stages.

- `Pool` — every in-scope paper found during retrieval, with metadata only: title, year, citations, and which pool
  papers it cites, plus embeddings and reference lists fetched by script. It is broad and cheap. It is used to find the
  clusters, to supply the citation structure anchors are chosen from, to test the coreset's coverage, and to draw from
  when a role needs a paper. No output cites a pool paper.
- `Coreset` — a few papers per cluster, selected in roles and verified against body text. It is small and expensive. It
  is the only thing an output (i.e. `outputs/<topic>.md`) may cite.

The pool is not the field. It is what our retrieval reached. Everything the coreset approximates, it approximates
relative to the pool. This is why retrieval deliberately mixes tools and routes (`docs/process.md`, "Overview" and
"Fringe routes"): a coreset cannot cover an idea the pool never saw.

## How coverage is achieved

Covering requires a notion of distance and a map of the space. The spec builds both from the pool, then fills the map in
roles.

`Clusters are the map.` They are computed from the pool by a similarity measure, from text and shared references, at a
level of detail chosen by measured stability (`docs/process.md`, "Clustering method"). Stability here means that two
analyses six months apart should find recognisably the same clusters. Clusters that shift with every rerun would make
the coreset's coverage an artefact of the run.

`Roles fill the map.` Ranking alone would select consensus, so each coreset paper plays a role in its cluster:

- `anchor` and `frontier` — the cluster's foundation and its current state. They are typical members, which is what the
  Landscape needs.
- `dissent` — a paper that contradicts the cluster's consensus. It is searched for deliberately, because a pivot is
  under-cited at the moment it matters, and a cluster represented only by its most-cited papers looks more settled than
  it is.
- `bridge` — a paper connecting two clusters. The `Gaps` target pulls bridges in: an unrepresented connection between
  two clusters is a gap, so a pool paper bridging them changes the output, and the coverage test adds it.
- `fringe` — a paper carrying an idea no other row has, far from its nearest neighbours in the pool for its age. This is
  the covering argument applied directly. Anchors and frontier papers cover the dense parts of the space; a far-out
  point is covered only if it is chosen itself. The fringe score, a paper's age-corrected distance to its nearest
  neighbours, measures how poorly the rest of the pool covers it.

`Sizing follows alignment, not size.` A cluster gets more rows the more directly it bears on the input, not the more
papers it has (`docs/process.md`, step 4, "Sizing"). A covering needs one representative per region, however dense the
region.

## How the two tests are applied

`Sufficiency is tested directly`, by the coverage test (`docs/process.md`, step 7). It samples pool papers not in the
coreset, and for each asks whether it opens a new cluster or would change a claim in the output's targets. The coreset
is sufficient when a round changes almost nothing. This is a sampled test, so sufficiency is established with the
confidence a sample of 10–15 allows, not proven. The sample leans toward thinly covered clusters and high fringe scores,
which is where a failure is most likely.

`Minimality is not tested directly.` No step removes a row and checks whether the output changes. It is approximated
instead by the role structure, which gives each row a distinct job, and by the sizing rules: about two to four rows per
cluster, and past about 80 rows, a check that no role is filled twice. Size alone is not an error: a topic with many
`high` clusters can legitimately need more. A direct removal test is an open item.

Two different stabilities are in play, and they are easy to confuse:

- `Cluster stability` — step 3, by script. Do the clusters come back under resampling and over time?
- `Coreset stability` — the coverage test, by judgement. Does the output survive more papers?

## What a coreset cannot tell you

`Absence.` A coreset shows what a field contains. By construction it cannot show what a field lacks: a covering says
every pool paper is near a row, and nothing about papers the pool never contained. So an output never claims that nobody
has done something. Gaps are stated in forms a coreset can support (`docs/formats.md`), and absence is checked only by a
probe, on demand (`docs/verification.md`).

`Field statistics.` A covering says nothing about how many papers stand behind each representative. An analogy: a map
with one pin per city approximates the geography well, but counting pins does not estimate population, because a village
and a capital each get one pin.

The error is bias, not noise, and it matters which. A random sample gives noisy but unbiased proportions, and a larger
sample sharpens them. The coreset is selected systematically away from proportions:

- `One anchor per cluster` — a cluster of ten papers and one of a thousand count the same, so small clusters are
  over-represented.
- `Dissent is searched for` — so negative results and broken assumptions are over-represented.
- `Fringe is chosen for being atypical` — so fringe rows are, by construction, the least representative papers in the
  pool.

A bigger coreset does not shrink this error. For example, if dissent papers tend to be elicitation studies, the share of
`elicited` rows reflects the dissent quota more than the field. This is why dimensions are for comparing papers and
characterising clusters, never for field statistics (`docs/formats.md`, "Analytic dimensions"). A cluster-level
statement such as "both this cluster's anchor and its frontier are `elicited`" is fine: it characterises a cluster
without counting the field.

When a field statistic is wanted, measure it on the pool, not the coreset. Draw a random sample of pool papers, label
the dimension from their abstracts, and report the share with its uncertainty. At about 1k tokens per paper this is
cheap, and it is a designed measurement rather than a by-product. It describes the literature retrieval reached, not the
whole field, and should say so. This is not yet part of a pass; like a probe, it would run on demand.

## Open questions

- `Minimality` has no direct test (see above).
- `Sufficiency` is judged by a model reading the output, not by a metric. Whether two agents would agree on "would this
  change a claim" has not been measured.
- `The covering is only as good as the pool.` Retrieval bias toward well-publicised or recent work becomes coverage
  bias. The fringe routes and mixed retrieval tools mitigate this; nothing measures it.
- `Field statistics from a pool sample` are proposed above, not adopted.

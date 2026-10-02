# What a survey is for

A survey in this repo is a **coreset**: the smallest set of papers that represents the ideas in a body of work well
enough that the output's answers are stable. Adding papers from the pool should not change them, and removing a coreset
paper should. It is not a list of everything published in that space. The framing, where it comes from, and what it
rules out are in `docs/coresets.md`. This file covers the concepts a pass works with and how the coreset is sized.

Three consequences run through the rest of the spec:

- **Coverage of ideas, not volume of papers.** Every distinct cluster of work is represented. No cluster is listed
  exhaustively.
- **Every row is verified to publication grade.** A small set is what makes this affordable. See `docs/verification.md`.
- **Absence is not claimed by default.** A coreset can show what a field contains, not what it lacks. Checking whether
  something exists is a targeted follow-up, run on demand. See `docs/verification.md`.

# Concepts

**Cluster.** A group of papers that share an approach, a question, or a line of results — for example "process reward
models", or "does RL create reasoning capability or only select it". Clusters are computed from the pool, by the
clustering method in `docs/process.md` (step 3): the similarity measure and the level of detail are both chosen by
measured stability, so they adapt to each literature. They are not copied from the input or from a previous survey's
section headings. Each cluster has a short kebab-case id, a name, a one-sentence definition, and an **alignment** rating
(`high`, `medium` or `low`) saying how directly it bears on the input's questions, with a reason.

**Role.** Each coreset paper is selected to play one role in its cluster:

- `anchor` — what the cluster is built on. Usually the paper most cited by the other papers in the pool.
- `frontier` — where the cluster currently stands: its strongest recent result. WebSearch is usually what surfaces it.
- `dissent` — a paper that contradicts the cluster's consensus, breaks one of its assumptions, or reports a negative
  result against its central claim.
- `bridge` — a paper that connects two clusters, for example by applying one cluster's method to another's question.
  Written `bridge:<other-cluster-id>`. Optional, but bridges are where the Landscape's structure becomes visible.
- `fringe` — a paper that carries an idea no other coreset paper has, and that the field has so far overlooked: it sits
  far from its nearest neighbours in the pool, for its age. It is placed in the cluster it was computed into, but it
  does not represent that cluster; it represents what the clusters leave out.

The roles exist because ranking alone selects consensus. A pivot is almost by definition under-cited at the moment it
matters, so no citation ranking will surface it, and a cluster represented only by its most-cited papers looks more
settled than it is. Dissent in particular has to be searched for deliberately.

Fringe is the same argument taken one step further. Anchors and frontier papers are typical members of their clusters,
which is right for the Landscape but leaves the edges of the field uncovered. A coreset represents ideas, not the
average paper, and a paper carrying an idea nothing else covers is an uncovered point. Most papers far from their
neighbours are there for a good reason, so a `fringe` pick must name the idea it carries. Fringe papers are the first
place to look for the output's Questions.

**Pool.** Every in-scope candidate screened during retrieval, labelled with its cluster and nothing more expensive than
that: title, year, citation count, and which other pool papers it cites. Its clustering data — full reference lists and
text embeddings — is fetched by script into a sidecar file, at no model cost. The pool is cheap to build and is never
cited by an output. It exists to find the clusters, to supply the citation structure that anchors are chosen from, to
measure what the coreset covers, and to draw from when the coreset needs another paper. Coreset papers are also pool
papers.

**Coreset.** The subset of the pool that is fully characterised and verified. These rows are the only papers an output
may cite.

# Sizing

A cluster gets more rows the more directly it bears on the input, not the more papers it has. How many papers a cluster
gets follows its alignment:

- `high` — anchor, frontier and dissent at minimum. Add a second frontier paper or a bridge where the cluster is
  internally divided.
- `medium` — anchor and frontier.
- `low` — anchor only. That is enough for the Landscape to be honest about the cluster existing.

The number of clusters is not chosen; it is the stable level found in step 3. Where the level below it splits a
high-alignment cluster into stable sub-clusters, the cluster counts as internally divided and gets the extra frontier or
bridge. Expect roughly two to four rows per cluster. On top of that, `fringe` has a quota per topic, not per cluster:
five to ten rows. Past roughly 80 rows, check whether any role is filled twice. If none is, the size is legitimate, for
example on a topic with many `high` clusters; report the count and the reason.

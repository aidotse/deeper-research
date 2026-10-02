# File formats

## `inputs/<topic>.md`

An .md file with at least one section, and several optional ones:

- `Topic`: what we want to research. This is a topic scoping exercise.

- `Context` (optional): individual items to condition the search on. This may be core motivation, specific links to
  websites (e.g. with instructions on what to look for), seed papers, hand-written notes, open questions, a past
  `surveys/<other_topic>.md`, etc. Where the input names seed papers, they enter the pool at step 1 as frontier or
  anchor candidates.

- `Coreset Spec` (optional): the attributes that actually define and guide how the coreset is defined (how these are
  answered should not significantly change as we add more papers to the coreset, only when taking away papers from the
  coreset). By default these must include:

  - `Landscape` — the general clusters, the axes that actually separate them, and where the bridges and tensions are.

  - `Assumptions` — the assumptions the body of work rests on, e.g. such that breaking one would have high research
    value. Dissent papers are the first evidence for which assumptions are fragile.

  - `Gaps` — open problems. Gaps are not absence claims (a coreset cannot establish that nobody has done something), so
    a gap is admissible in one of three forms by default: (other types are fine; ask which are wanted if the request
    does not make it clear):

    - **Stated open problems** — what the coreset papers themselves say is unresolved, cited to the paper saying it.
    - **Tensions** — two clusters, or a cluster and its dissent, whose assumptions or results are incompatible.
    - **Unrepresented connections** — two clusters that bear on each other with no bridge paper in the coreset. Phrase
      this as "not represented in the coreset", never as "has not been studied", and suggest it as a probe.

- `Dimensions` (optional): cross-cutting attributes to extract for every coreset paper. See `Analytic dimensions` below.
  If the input declares none, propose a meaningful set at step 3 and adopt it provisionally, saying so in the report.
  Declaring dimensions here is cheaper: one added after verification must be re-derived for every row.

- `Clustering` (optional): steering for step 3, so that the pass need not stop for review. Any of:

  - `granularity` — `coarser` or `finer` than the stability rule chooses, or a target number of clusters. Applied by
    moving along the computed levels; a level below `τ` is flagged in the report.
  - `expect` — themes the user expects to see as clusters. A missing one triggers a targeted expansion of that region,
    and stops the pass if it is still missing.
  - `exclude` — themes to treat as out of scope when screening.
  - `alignment` — themes to rate `high` or `low`, overriding the agent's reading of the `Topic`.
  - `review` — `before coreset` to stop for review at step 3. By default the clusters are reviewed with the output.

  See `docs/process.md`, step 3 and "Changing the clusters after a pass".

## `surveys/<topic>.md`

The factual cache for a topic, and the only input to its output `outputs/<topic.md>`. It contains five sections, in this
order, and nothing else. This subsection section describes only the *formatting*; for more survey semantics see
`docs/surveys.md`.

It is descriptive about the papers: no judgements of quality or importance. Selection is the exception. Choosing a
coreset is a judgement, so each coreset row records why it was chosen (`Coreset` section), and the `Clusters` section
records the alignment reasoning. Those judgements are logged so that they can be reviewed, not hidden in a subagent's
context.

### 1. Retrieval log

One entry per pass, in date order:

```text
### Pass YYYY-MM-DD

- **Preflight:** snippet_search ok | search_papers_by_relevance ok | get_paper ok | get_citations ok | WebSearch ok |
  Graph API ok | arXiv ok | uv ok | ASTA_API_KEY set
- **Orientation (WebSearch):** "<exact query>", ...
- **Expansion:** <which papers were traversed, in which direction, with counts>; queries "<exact query>", ...
- **Errored queries:** none | "<query>" (429, failed after 3 retries)
- **Recency window:** <the window>, applied to the recency queries only
- **Pool:** N papers in scope
- **Clustering:** measure <text | refs | combined> (grid mean ARI: text X ± se, refs Y ± se, combined Z ± se); level N
  clusters by rule <tau | null> (grid <counts>; finest level with stability >= τ: S; next level M clusters at S';
  null-model rule: L clusters); τ=<τ>, k=<k>, c=<c>;
  holdout cutoffs <dates>; diagnostics: none | <each case, and the action taken>; manual overrides: none | <what the
  user changed>
- **Clusters:** N (H high, M medium, L low); stopped for review: no | <trigger>; reviewed by user YYYY-MM-DD | not yet
  reviewed
- **Dissent searches:** <cluster id>: <what was searched> -> <found: id | none found>
- **Coreset:** N rows
- **Coverage test:** round R: K of N sampled candidates changed the output (<ids>); new clusters: none | <which>
- **Corrections to existing rows:** <id> — <old text> -> <new text>, and why
- **Stopped because:** <which condition, with the measured numbers>
```

### 2. Clusters

One table:

| column | contents |
| -- | -- |
| `id` | short kebab-case id, used everywhere else to refer to the cluster |
| `name` | human-readable name |
| `definition` | one sentence: what papers in this cluster have in common |
| `alignment` | `high`, `medium` or `low` |
| `alignment reason` | one sentence tying the rating to the input |

Do not write coreset or pool counts into this table. `tools/check.py` computes them from the file, and hand-maintained
counts drift.

### 3. Coreset

One `###` block per cluster, headed `### <cluster-id> — <name>`, in the same order as the Clusters table. Every block
uses the same columns:

| column | contents |
| -- | -- |
| `paper` | title, linked to its arXiv page |
| `venue+year` | publication venue and year; `arXiv YYYY-MM` if unpublished |
| `role` | `anchor`, `frontier`, `dissent`, `fringe`, or `bridge:<cluster-id>` |
| `selected because` | one sentence on why this paper fills this role, e.g. "highest in-degree in cluster (31)" |
| `method name` | the method's actual name, if the paper introduces one |
| `method summary` | two sentences on what the paper does and how, including the assumptions the result depends on |
| `datasets / models` | the datasets and models of the headline evaluation |
| `metric` | the metric of the headline evaluation |
| `result` | the headline number, with its baseline and comparison condition, e.g. "+2.3 top-1 over X at equal FLOPs"; `n/a` if the paper reports no quantitative result |
| *(declared dimensions)* | one column per dimension declared in the input, or generated and accepted as suggestion. |
| `source` | `abstract`, `snippet` or `full-text`: what the row was verified against. Always the last column. |

### 4. Pool

One table, listing every in-scope screened paper, coreset papers included:

| column | contents |
| -- | -- |
| `paper` | title, linked to its arXiv page |
| `year` | publication year |
| `cluster` | cluster id, as computed in step 3 |
| `citations` | total citation count as reported by Semantic Scholar, with the retrieval date in the log |
| `cites` | space-separated bare arXiv IDs of the other pool papers this paper cites |

The `cites` column is the pool's citation graph. In-degree within the pool, which is what anchors are chosen from, is
computed from it, and so is any visualisation of the topic. `year`, `citations` and `cites` are filled by
`tools/pool.py`, never by hand.

The data that clustering needs — full reference lists, including references outside the pool, and (e.g. SPECTER2)
embeddings — is too large for a markdown table. It lives in the pool sidecar, `graphs/<topic>/pool.json`, with the
clustering report in `graphs/<topic>/clusters.json` and the viewer, `graphs/<topic>/graph.html`, alongside. Both are
part of the survey's record: they are what makes the clustering reproducible offline.

### 5. Open work

What is known to be outstanding, so that work survives a session ending mid-pass:

```text
## Open work

- **Clusters not yet reviewed by the user:** <ids>
- **Empty roles:** <cluster id> — <role> — <what was searched>
- **Rows needing verification:** <id> — <why it is not yet verified>
- **Coverage-test candidates not yet assessed:** <id>
- **Probes requested:** "<question>" — <status>
```

Keep it current as work proceeds. A subagent that leaves something outstanding must write it here before finishing, not
only in its report to the main session. Reports live in one session's context and are lost when it ends.

### Analytic dimensions

The standard columns capture what a paper *is*. Understanding a body of work usually also needs attributes that
*separate* papers, and those are topic-specific. Some examples include:

- For safety and security work: the threat model (what the attacker controls, what they know, whether the demonstration
  is on a deployed system or a simulation); and whether a capability was elicited by the authors — deliberately trained
  or prompted in — or arose spontaneously from ordinary training. These are routinely blurred in the literature, and
  they change what a result means entirely.
- For theory work: whether a claim is proven or an empirical fit, and the assumptions a proof depends on.
- For any claim about a monitor or detector: whether the result holds under optimisation pressure aimed at it, under
  pressure not aimed at it, or only without training pressure at all.

Declared dimensions become columns and must be filled for every coreset row, to them comparable across the coreset. An
attribute noted only in prose, or only in a subagent's report, is an anecdote.

Use dimensions to compare papers and to characterise clusters, never as field statistics. The coreset is chosen for
coverage, so its proportions are biased by design, not merely noisy: "40 of 50 coreset rows are `elicited`" describes
the selection, not the field. If a share is wanted, it has to be measured on a random sample of the pool. See
`docs/coresets.md`, "What a coreset cannot tell you".

## `bib/<topic>.bib`

BibTeX for every coreset row; the pool has no bib entries. Regenerate it with `python3 tools/bib.py <topic>` rather than
assembling it by hand, so that the survey and the bibliography cannot drift apart. The script keeps existing entries
verbatim, so citation keys stay stable. It fetches only missing IDs from the arXiv API, and drops entries whose papers
have left the coreset.

## `outputs/<topic>.md`

The response to the prompt in `inputs/<topic>.md`, based only on the coreset in `surveys/<topic>.md`. This is where
interpretation, salience and qualitative judgement belong. Build a canonical summary and analysis based on the coreset
spec dimensions in the input. For example, if `Assumptions` is part of that spec, give a representative summary of the
assumptions made by the search work in the coreset, and rank them by likelihood and feasiblity, linking back to the most
informative dissent papers coreset-wide. In addition, always include at least the following two subsections:

- `Questions` — candidate research questions, with the coreset papers each builds on.

- `Reading` — a prioritised reading list for anyone jumping into this topic, with a one-line rationale per entry.

Outputs are regenerable views over surveys, and may be rewritten freely.

Mark any proposed concept or idea that goes beyond the survey material with its closest prior art from the coreset. If
an output needs a claim not present in the survey, add the paper to the coreset first, in a role, and verify it.

Outputs must carry their provenance. Every coreset row should be verified, so the default is that everything an output
cites has been checked against body text. Where a row could not be — its `source` is `abstract` — every claim resting on
it is marked provisional in the output. Run `python3 tools/check.py <topic>` before treating an output as finished: it
lists every `abstract`-sourced paper the output cites.

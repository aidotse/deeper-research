# File formats

## `inputs/<topic>.md`

An .md file with at least one section, and several optional ones:

- `Topic`: what we want to research. This is a topic scoping exercise.

- `Context` (optional): individual items to condition the search on. This may be core motivation, specific links to
  websites (e.g. with instructions on what to look for), seed papers, hand-written notes, open questions, a past
  `surveys/<other_topic>.md`, etc. Where the input names seed papers, they enter the pool at step 1 as frontier or
  anchor candidates.

- `Coreset Spec` (optional): the coreset's **targets**. The targets are the parts of the output that the coreset must
  stay stable against: adding pool papers should not change what the output says about them, and removing a coreset
  paper should. They are what the coverage test checks (`docs/process.md`, step 7), so that test counts a change to a
  target, and nothing else. Why the coreset is defined this way is in `docs/coresets.md`.

  If the section is omitted, the targets are `Landscape`, `Assumptions` and `Gaps`. An input may add more, such as
  specific research questions. `Questions` and `Reading` are derived from the targets, so they are never targets
  themselves. The default targets:

  - `Landscape` — the general clusters, the axes that actually separate them, and where the bridges and tensions are.

  - `Assumptions` — the assumptions the body of work rests on, e.g. such that breaking one would have high research
    value. Dissent papers are the first evidence for which assumptions are fragile.

  - `Gaps` — open problems. Gaps are not absence claims (a coreset cannot establish that nobody has done something), so
    a gap is admissible in one of three forms by default. An input may ask for other forms. If it is unclear which are
    wanted, the main session asks the user when planning the pass.

    - **Stated open problems** — what the coreset papers themselves say is unresolved, cited to the paper saying it.
    - **Tensions** — two clusters, or a cluster and its dissent, whose assumptions or results are incompatible.
    - **Unrepresented connections** — two clusters that bear on each other with no bridge paper in the coreset. Phrase
      this as "not represented in the coreset", never as "has not been studied", and suggest it as a probe.

- `Dimensions` (optional): cross-cutting attributes to extract for every coreset paper. See `Analytic dimensions` below.
  Declare each as a top-level bullet that opens with its name and its allowed values, in this form, so that the tools
  can read it; any explanation may follow:

  ```text
  - **`evidence`** — values: `proven`, `derived`, `empirical`, `fitted`, `position`. What kind of claim ...
  ```

  `tools/check.py` checks every coreset row's values against these, and the viewer offers a colour mode per dimension.
  If the input declares none, propose a meaningful set at step 3 and adopt it provisionally, saying so in the report and
  in the log's `Dimensions` line; its values are then not checked. Declaring dimensions here is cheaper: one added after
  verification must be re-derived for every row.

- `Clustering` (optional): steering for the clustering (step 3) and for screening (step 2), so that the pass need not
  halt for review. One top-level bullet per field, in the form `` - `field`: value ``. Any of:

  - `granularity` — `coarser` or `finer` than the stability rule chooses, or a number of clusters: a level's target in
    the grid, or the number it reached. `tools/inputs.py` checks only that it is a number; `tools/cluster.py` stops with
    the levels it can offer if it is not one of them. It applies the steering by moving along the computed levels,
    before naming; a level below `τ` is flagged in the report.
  - `expect` — themes the user expects to see as clusters. A missing one triggers a targeted expansion of that region,
    and halts the pass (`H7`) if it is still missing.
  - `exclude` — themes to treat as out of scope. Applied at screening, in step 2.
  - `alignment` — themes to rate, overriding the agent's reading of the `Topic`, separated by `;`, each ending in
    `high`, `medium` or `low`, for example `` - `alignment`: process reward models — `high`; agents — `low`  ``.
  - `review` — `before coreset` to halt for review at step 3 (`H13`). By default the clusters are reviewed with the
    output.

  See `docs/process.md`, step 3 and "Changing the clusters after a pass". `python3 tools/inputs.py <topic>` shows what
  the tools read from the input, and fails on an unknown section, field or value; `tools/check.py` runs the same check.

## `surveys/<topic>.md`

The factual cache for a topic, and the only input to its output `outputs/<topic>.md`. It contains five sections, in this
order, and nothing else. This section describes only the *formatting*. What the pool and coreset are for is in
`docs/coresets.md`; how each section is produced, including roles and sizing, is in `docs/process.md`.

It is descriptive about the papers: no judgements of quality or importance. Selection is the exception. Choosing a
coreset is a judgement, so each coreset row records why it was chosen (`Coreset` section), and the `Clusters` section
records the alignment reasoning. Those judgements are logged so that they can be reviewed, not hidden in a subagent's
context.

### Paper IDs

Every paper has one canonical ID, used in every table, sidecar, bib entry and output, and by every tool:

- `arXiv ID` — where the paper has one: `2504.13837`; the 2007–2014 form `1412.6980`; or the pre-2007 form
  `hep-th/9901001`, written without a subject class (`math/0309136`, not `math.GT/0309136`, which Semantic Scholar does
  not resolve).
- `Corpus ID` — otherwise, Semantic Scholar's numeric ID, written `CorpusId:6628106`. Asta and the Graph API both accept
  it. Not the DOI: many papers lack one, and its characters are awkward in tables.

A survey row links its paper to `https://arxiv.org/abs/<id>`, or to `https://api.semanticscholar.org/CorpusId:<n>`,
which redirects to the paper's page. The tools read the ID from that link, so no other link form is allowed.

A Semantic Scholar record without an arXiv ID may still have one. A preprint and its venue version are often two
records, and only one of them carries the arXiv ID; the other's open-access PDF may be on arXiv. The tools look in both
places. `tools/check.py` fails on a `CorpusId` row whose paper has an arXiv ID, on one paper listed under two IDs, and
on two pool rows with the same title, and notes near-identical titles. Keep the arXiv record, and merge the other into
it: its venue goes into `venue+year`. Log the merge under `Corrections to existing rows`. A merge is not a deletion, so
it needs no permission.

A paper that is not in Semantic Scholar at all cannot yet enter the pool: nothing can fetch its references or embedding.
Nor can one without a SPECTER2 embedding, which clustering needs. Record either in Open work.

### 1. Retrieval log

One entry per pass, in date order:

```text
### Pass YYYY-MM-DD

- **Preflight:** snippet_search ok | search_papers_by_relevance ok | get_paper ok | get_citations ok | WebSearch ok |
  Graph API ok | arXiv ok | uv ok | Asta key set
- **Orientation (WebSearch):** "<exact query>", ...
- **Expansion:** <which papers were traversed, in which direction, with counts>; queries "<exact query>", ...
- **Errored queries:** none | "<query>" (429, failed after 3 retries; retried at the end of the step: <outcome>)
- **Recency window:** <the window>, applied to the recency queries only
- **Fringe:** collected YYYY-MM-DD: hidden H, new W candidates (U unique); in scope S; added to the pool A, of which
  C without an arXiv ID; left out X
- **Pool:** N papers in scope; metadata fetched <date> | <first date> to <last date>
- **Clustering:** measure <text | refs | combined> (grid mean stability: text X ± se, refs Y ± se, combined Z ± se);
  level N clusters by rule <tau | null>[, moved by <granularity steering | user override> (<value>)], stability S; next finer level M clusters at S' | no finer level; τ ± 0.05
  would give A | B clusters; null-model rule: L clusters; grid <counts>; τ=<τ>, k=<k>, c=<c>; holdout cutoffs
  <dates>; diagnostics: none | <case>: <detail> -> <action taken>; ...; manual overrides: none | level <value> (--level) | <what else the user changed>
- **Temporal stability:** 4 equal-count segments; snapshots <date> (N papers, stability S), ...; <per cluster, separated
  by " | ": its id from the Clusters table and since when it exists, e.g. "since 2025-10-09; before that, too few papers
  (5)", "probably since 2025-03-24 or earlier (that snapshot's stability 0.40)", "new since 2026-05-25; before that,
  its papers were grouped differently (merged)">
- **Clustering rationale:** <a short paragraph: why the clusters look as they do — the level and its margin above τ;
  the spread of cluster scores, with weak clusters named and diagnosed; how decisive the measure choice was; what any
  steering in the input's `Clustering` section changed; and which clusters are long-standing and which recent>
- **Clusters:** N (H high, M medium, L low); halted for review: no | <id>; reviewed by user YYYY-MM-DD | not yet
  reviewed
- **Dimensions:** declared in the input | proposed and adopted provisionally: <name>, ...
- **Dissent searches:** <cluster id>: <what was searched> -> <found: id | none found>
- **Coreset:** N rows
- **Demotions:** none | <id> — <role> in <cluster id>, replaced by <id>, and why
- **Late papers:** none | YYYY-MM-DD: N assigned to their nearest cluster (<id> -> <cluster id>, ...); late since the
  last full clustering: M of P (X%) | reclustered (<why>); remap: <which clusters matched, split, merged, new>
- **Coverage test:** round R: K of N sampled candidates changed the output (<id>: <what it changed>, ...); new
  clusters: none | <which> (one line per round; "what it changed" names the target and the claim, e.g. "gap: <the new
  gap>" or "assumption: <which one>, revised")
- **Probes:** none | "<question>": searched <phrasings, citation traversals, WebSearch, date ranges> -> found: <ids> |
  survived a refutation attempt
- **Corrections to existing rows:** <id> — <old text> -> <new text>, and why
- **Tokens:** <step>: <tokens>, ... (per dispatch, as reported; from the fresh run on)
- **Halts:** none | <id> — <what happened> — <the user's decision, YYYY-MM-DD>; ...
- **Ended:** finished (F1) | halted (<id>); <the measured numbers>
```

The `F1` and `H` IDs are defined in `docs/process.md`, "When a pass ends". Six lines, or parts of them, are printed by
scripts, ready to paste: the script half of `Preflight` by `tools/preflight.py`; `Pool` by `tools/pool.py`, which
`tools/assign.py late` also runs; `Fringe` and `Late papers` by `tools/assign.py`; and `Clustering` and
`Temporal stability` by `tools/cluster.py`. Replace the computed cluster ids (`c1`, `c2`, …) with the Clusters table's
ids, and each `<action taken>` with what was done. Every other number in the log comes from a script's printout or a
tool's result, never from counting by hand.

### 2. Clusters

One table:

| column | contents |
| -- | -- |
| `id` | short kebab-case id, used everywhere else to refer to the cluster |
| `name` | human-readable name |
| `definition` | one sentence: what papers in this cluster have in common |
| `alignment` | `high`, `medium` or `low` |
| `alignment reason` | one sentence tying the rating to the input |
| `computed` | the id the clustering gave this cluster in `graphs/<topic>/clusters.json`: `c1`, `c2`, … |

The `computed` column ties each name to a computed cluster. Every computed cluster has exactly one row, and
`tools/assign.py` writes pool memberships through it. After a recluster, `tools/assign.py remap` updates it (see
`docs/process.md`, "Late papers").

Do not write coreset or pool counts into this table. `tools/check.py` computes them from the file, and hand-maintained
counts drift.

### 3. Coreset

One `###` block per cluster, headed `### <cluster-id> — <name>`, in the same order as the Clusters table. Every block
uses the same columns:

| column | contents |
| -- | -- |
| `paper` | title, linked by its ID (see "Paper IDs") |
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
| `paper` | title, linked by its ID (see "Paper IDs") |
| `year` | publication year |
| `cluster` | cluster id, as computed in step 3; empty until then, and for a late paper until it is assigned |
| `citations` | total citation count as reported by Semantic Scholar, with the retrieval dates in the log's `Pool` line |
| `cites` | space-separated IDs of the other pool papers this paper cites |

The `cites` column is the pool's citation graph. In-degree within the pool, which is what anchors are chosen from, is
computed from it, and so is any visualisation of the topic. Nothing in this table is written by hand. Rows are added by
`tools/assign.py add` and `add-fringe`; `year`, `citations` and `cites` are filled by `tools/pool.py`; and `cluster` is
written by `tools/assign.py clusters` and `late`.

The data that clustering needs — full reference lists, including references outside the pool, and (e.g. SPECTER2)
embeddings — is too large for a markdown table. It lives in the pool sidecar, `graphs/<topic>/pool.json`, with the
clustering report in `graphs/<topic>/clusters.json` alongside. These two files are part of the survey's record: they are
what makes the clustering reproducible offline. The viewer, `graphs/<topic>/graph.html`, is not: it is rebuilt from them
and is not committed.

### 5. Open work

What is known to be outstanding, so that work survives a session ending mid-pass:

```text
## Open work

- **Clusters not yet reviewed by the user:** <ids>
- **Empty roles:** <cluster id> — <role> — <what was searched>
- **Rows needing verification:** <id> — <why it is not yet verified>
- **Coverage-test candidates not yet assessed:** <id>
- **Probes requested:** "<question>" — <status>
- **Papers that could not enter the pool:** <title or ID> — <why: not in Semantic Scholar, or no SPECTER2 embedding>
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

Declared dimensions become columns and must be filled for every coreset row, to make them comparable across the coreset.
An attribute noted only in prose, or only in a subagent's report, is an anecdote.

Use dimensions to compare papers and to characterise clusters, never as field statistics. The coreset is chosen for
coverage, so its proportions are biased by design, not merely noisy: "40 of 50 coreset rows are `elicited`" describes
the selection, not the field. If a share is wanted, it has to be measured on a random sample of the pool. See
`docs/coresets.md`, "What a coreset cannot tell you".

## `bib/<topic>.bib`

BibTeX for every coreset row; the pool has no bib entries. Regenerate it with `python3 tools/bib.py <topic>` rather than
assembling it by hand, so that the survey and the bibliography cannot drift apart. The script keeps existing entries
verbatim, so citation keys stay stable. It fetches only missing IDs, from the arXiv API, or from Semantic Scholar for a
paper without an arXiv ID, and drops entries whose papers have left the coreset. An entry carries `eprint` for an arXiv
paper and `corpusid` for any other.

## `outputs/<topic>.md`

The response to the prompt in `inputs/<topic>.md`, based only on the coreset in `surveys/<topic>.md`. This is where
interpretation, salience and qualitative judgement belong.

It has one section per target (see `Coreset Spec` above): by default `Landscape`, `Assumptions` and `Gaps`. Build each
as a canonical summary and analysis of the coreset. For example, `Assumptions` gives a representative summary of the
assumptions the work in the coreset makes, ranks them by likelihood and feasibility, and links back to the most
informative dissent papers coreset-wide. After the targets, always include these two sections:

- `Questions` — candidate research questions, with the coreset papers each builds on. The `fringe` rows are the first
  place to look for them.

- `Reading` — a prioritised reading list for anyone jumping into this topic, with a one-line rationale per entry.

Outputs are regenerable views over surveys, and may be rewritten freely.

Mark any proposed concept or idea that goes beyond the survey material with its closest prior art from the coreset. If
an output needs a claim not present in the survey, add the paper to the coreset first, in a role, and verify it.

Outputs must carry their provenance. Every coreset row should be verified, so the default is that everything an output
cites has been checked against body text. Where a row could not be — its `source` is `abstract` — every claim resting on
it is marked `[abstract-only]`, next to the paper's ID. Every output opens with a short legend explaining the marker,
and saying what was missing if the pass continued past a halt (`docs/process.md`, "When a pass ends"). Run
`python3 tools/check.py <topic>` before treating an output as finished: it lists every `abstract`-sourced paper the
output cites.

# File formats

## `inputs/<topic>.md`

The user writes the input, and only the user edits it. It is a markdown file of `##` sections, each at most once, in any
order. Only `Topic` is required. `python3 tools/inputs.py <topic>` prints what the tools read from it, and fails on
anything it cannot read (see "Rules the parser applies" below); `tools/check.py` runs the same check. Never edit an
input for the user: if it fails, the user corrects it before the pass starts.

### A skeleton input

```text
# <a title; lines before the first `##` section are ignored>

## Topic

<what to research, in a sentence or a paragraph>

## Context

- <a motivation, a link with what to look for there, a seed paper by ID, a note, an open question>
- <a previous survey to draw on: `surveys/<other-topic>.md`>

## Coreset Spec

<prose is allowed here as paragraphs, or as bullets nested under a target>

- **`<Name>`** — <what the output must say about it>
- `drop`: `Gaps`

## Dimensions

- **`<name>`** — values: `<a>`, `<b>`, or `<c>`. <what the dimension separates, and how to tell the values apart>

## Clustering

- `granularity`: coarser
- `expect`: <a theme>; <another theme>
- `exclude`: <a theme>
- `alignment`: <a theme> — `high`; <another theme> — `low`
- `review`: before coreset
```

### `Topic`

What we want to research. This is a topic scoping exercise: the `Topic` is what screening judges scope against
(`docs/process.md`, "Screening for scope").

### `Context`

Optional. Individual items to condition the search on: core motivation, specific links to websites (e.g. with
instructions on what to look for), seed papers, hand-written notes, open questions, a past `surveys/<other_topic>.md`,
etc. Seed papers the input names enter the pool at step 1, and are listed in the `Orientation` line (`docs/process.md`,
step 1).

### `Coreset Spec`

Optional. The coreset's **targets**: the parts of the output that the coreset must stay stable against. Adding pool
papers should not change what the output says about them, and removing a coreset paper should. They are what the
coverage test checks (`docs/process.md`, step 7), so that test counts a change to a target, and nothing else. Why the
coreset is defined this way is in `docs/coresets.md`.

If the section is omitted, the targets are `Landscape`, `Assumptions` and `Gaps`. An input may add more, such as
specific research questions, one top-level bullet per added target, in the form
`` - **`<Name>`** — <what the output must say about it> ``. The defaults still apply unless dropped with a bullet
`` - `drop`: `<Name>`  ``. Other prose is allowed as paragraphs, or as bullets nested under a target; a top-level bullet
in neither form fails, since it is more likely a mistyped target. `tools/inputs.py` prints the targets it reads. Each
target gets its own section in the output. Research questions placed in `Context` steer the search but are not targets,
so the coverage test does not check them. `Questions` and `Reading` are derived from the targets, so they are never
targets themselves. The default targets:

- `Landscape` — the general clusters, the axes that actually separate them, and where the bridges and tensions are.

- `Assumptions` — the assumptions the body of work rests on, e.g. such that breaking one would have high research value.
  Dissent papers are the first evidence for which assumptions are fragile.

- `Gaps` — open problems. Gaps are not absence claims (a coreset cannot establish that nobody has done something), so a
  gap is admissible in one of three forms by default. An input may ask for other forms. If it is unclear which are
  wanted, the main session asks the user when planning the pass.

  - **Stated open problems** — what the coreset papers themselves say is unresolved, cited to the paper saying it.
  - **Tensions** — two clusters, or a cluster and its dissent, whose assumptions or results are incompatible.
  - **Unrepresented connections** — two clusters that bear on each other with no bridge paper in the coreset. Phrase
    this as "not represented in the coreset", never as "has not been studied", and suggest it as a probe.

### `Dimensions`

Optional. Cross-cutting attributes to extract for every coreset paper; see "Analytic dimensions" below. Declare each as
a top-level bullet that opens with its name, lowercase, and its allowed values, in this form, so that the tools can read
it; any explanation may follow, in the bullet or in prose or nested bullets under it. Every top-level bullet in the
section is read as a dimension, and `tools/inputs.py` fails on one not in this form:

```text
- **`evidence`** — values: `proven`, `derived`, `empirical`, `fitted`, or `position`. What kind of claim ...
```

`tools/check.py` checks every coreset row's values against these, and the viewer offers a colour mode per dimension.

If the input declares none, the main session proposes a set at step 0, in the Plan row, from the input: a name and at
least two values per dimension, with `n/a` among them if some papers will have no value, and after the values, in
brackets, one clause on what the dimension separates and how to tell its values apart (no backticks or semicolons inside
it, which the check reads as the line's structure). It writes them in the log's `Dimensions` line, in the form given
there ("1. Retrieval log"), and says so when it reports the plan to the user. The pass does not wait for an answer: the
user can stop it there, or change the dimensions in the input. Proposed dimensions are then treated exactly like
declared ones: `tools/check.py` reads them from that line, checks the rows' values and columns against them, and `G4`
requires evidence for them. Declaring dimensions in the input is still better: the user chooses them, and one added
after verification must be re-derived for every row.

### `Clustering`

Optional. Steering for the clustering (step 3) and for screening (step 2), so that the pass need not halt for review.
One top-level bullet per field, in the form `` - `field`: value ``. Any of:

- `granularity` — `coarser` or `finer` than the stability rule chooses, or a number of clusters above 0: a level's
  target in the grid, or the number it reached. `tools/inputs.py` checks only that it is a number; `tools/cluster.py`
  stops with the levels it can offer if it is not one of them. It applies the steering by moving along the computed
  levels, before naming; a level below `τ` is flagged in the report.
- `expect` — themes the user expects to see as clusters. A missing one triggers a targeted expansion of that region, and
  halts the pass (`H7`) if it is still missing.
- `exclude` — themes to treat as out of scope. Applied at screening, in step 2.
- `alignment` — themes to rate, overriding the agent's reading of the `Topic`, separated by `;`, each ending in `high`,
  `medium` or `low`, for example `` - `alignment`: process reward models — `high`; agents — `low`  ``.
- `review` — `before coreset` to halt for review at step 3 (`H13`). By default the clusters are reviewed with the
  output.

See `docs/process.md`, step 3 and "Changing the clusters after a pass".

### Rules the parser applies

`tools/inputs.py` fails, so that a typo cannot silently drop a request, on:

- a section that is not one of the five above, a section given twice, or a known section at another heading level than
  `##` (`# Topic`, `### Topic`);
- a missing or empty `Topic`;
- a `Dimensions` bullet not in the form above, or with no values;
- a `Coreset Spec` bullet that is neither a target nor a `drop`, a `drop` of a name that is not a default target, an
  added target named `Questions` or `Reading`, or no target left after the drops;
- a `Clustering` field that is unknown, a `granularity` that is not `coarser`, `finer` or a number above 0, a `review`
  other than `before coreset`, or an `alignment` entry that does not end in `high`, `medium` or `low`.

A bullet is any list item: `-`, `*`, `+` or numbered (`1.`, `1)`). A bullet may wrap onto the following lines, indented
or not. A list of values may end in "or" or "and", with or without a comma before it. mdformat rewrites `*` and `+` as
`-`, and the input reads the same before and after.

## `surveys/<topic>.md`

The factual cache for a topic, and the only input to its output `outputs/<topic>.md`. It contains five sections, in this
order, and nothing else: under a `# ` title, the `##` headings `Retrieval log`, `Clusters`, `Coreset`, `Pool` and
`Open work`. On a first pass the main session writes them empty; `tools/assign.py add` writes the Pool table's header
with its first row. This section describes only the *formatting*. What the pool and coreset are for is in
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

- **Gates:** G0 YYYY-MM-DD, G1 YYYY-MM-DD, ... (each gate as it passes; `docs/gates.md`)
- **Preflight:** snippet_search ok | search_papers_by_relevance ok | get_paper ok | get_citations ok | WebSearch ok |
  Graph API ok | arXiv ok | uv ok | Asta key set
- **Orientation (WebSearch):** "<exact query>", ...; themes: "<phrase>", ...; seeds from the input: none | <id>, ...;
  frontier candidates: <id>, ...
- **Expansion:** backward from <id> (<n>), <id> (<n>), ...; forward from <id> (<n>), ...; queries "<exact query>"
  (<n>), ...; targeted, <region, by one of its paper IDs> (<why>): <traversals and queries, as above>; stopped: <why>[; rejected: none]
- **Errored queries:** none | "<query>" (429, failed after 3 retries; retried at the end of the step: ok | failed)
- **Recency window:** <the window>, applied to the recency queries only
- **Fringe:** collected YYYY-MM-DD: hidden H, new W candidates (U unique); in scope S; added to the pool A, of which
  C without an arXiv ID; left out X
- **Pool:** N papers in scope, A with an arXiv ID; metadata fetched <date> | <first date> to <last date>
- **Clustering:** measure combined; level N clusters by rule tau[, moved by <granularity steering | user override>
  (<value>)], stability S; next finer level M clusters at S' | no finer level; τ ± 0.05 would give A | B clusters; grid
  <counts>; τ=<τ>, k=<k>, c=<c>; holdout cutoffs <dates> | none (all skipped; stability from resampling only);
  diagnostics: none | <case>: <detail> -> <action taken>; ...; manual overrides: none | level <value> (--level) | <what
  else the user changed>
- **Clustering rationale:** <a short paragraph: why the clusters look as they do — the level and its margin above τ;
  the spread of cluster scores, with weak clusters named and diagnosed; the notes the printout lists; and what any
  steering in the input's `Clustering` section changed>
- **Clusters:** N (H high, M medium, L low); halted for review: no | <id>; reviewed by user YYYY-MM-DD | not yet
  reviewed
- **Dimensions:** declared in the input | proposed: `<name>` — values: `<a>`, `<b>` (<what it separates>); `<name>` —
  values: `<a>`, `<b>`, `<c>` (<what it separates>); ...
- **Dissent searches:** <cluster id>: <what was searched> -> found: <id>, ...; <cluster id>: <what was searched> ->
  none found; ...
- **Coreset:** N rows
- **Demotions:** none | <id> — <role> in <cluster id>, replaced by <id>, and why
- **Late papers:** none | YYYY-MM-DD: N assigned to their nearest cluster (<id> -> <cluster id>, ...); late since the
  last full clustering: M of P (X%) | YYYY-MM-DD: reclustered (<why>); remap: <the `changes:` line of
  `tools/cluster.py`'s printout>
- **Coverage test:** round R: K of N sampled candidates changed the output (<id>: <what it changed>, ...); new
  clusters: none | none (proposed <which>, not formed) | <which>
- **Judgement audit:** re-verification: A of C cells agree, P partly, D differ, over N rows (seed S); faithfulness: F of
  M sentences supported, P' partly, U unsupported (seed S')
- **Probes:** none | "<question>": searched <phrasings, citation traversals, WebSearch, date ranges> -> found: <ids> |
  survived a refutation attempt
- **Corrections to existing rows:** none | <id> — <old text> -> <new text>, and why
- **Tokens:** <dispatch>: <tokens>, ...
- **Halts:** none | <id> — <what happened> — <the user's decision, YYYY-MM-DD> | pending; ...
- **Waivers:** none | <requirement id> — <why> — <the user's decision, YYYY-MM-DD>; ...
- **Ended:** finished (F1) | halted (<id>); <the measured numbers>
```

The `F1` and `H` IDs are defined in `docs/process.md`, "When a pass ends". Who writes each line is in the order of
operations, column `writes` (`docs/process.md`): that column is the only authority on it. An agent running in parallel
with others never writes the log; it returns its lines under `Log:`, and the main session writes them.

Seven lines, or parts of them, are printed by scripts, ready to paste: the script half of `Preflight` by
`tools/preflight.py`, which the Preflight agent completes; `Pool` by `tools/pool.py`, which `tools/assign.py late` also
runs; `Fringe` and `Late papers` by `tools/assign.py`; `Clustering` by `tools/cluster.py`; `Coverage test` by
`tools/coverage.py line`; and `Judgement audit` by `tools/audit.py line`. Replace the computed cluster ids (`c1`, `c2`,
…) with the Clusters table's ids, and each `<action taken>` with what was done. Every other number in the log comes from
a script's printout or a tool's result, never from counting by hand.

What some lines need, beyond their form:

- `Orientation` — the themes are the phrases the field uses for its sub-topics, which step 2 searches. The seeds are the
  papers the input names. A frontier candidate is listed only once it is in the pool; one that cannot enter goes to Open
  work's `Papers that could not enter the pool` instead.
- `Expansion` — each traversal names the paper it started from, its direction, and in brackets how many candidates it
  gave to screen; each query is quoted verbatim, with its count. `tools/check.py` counts a frontier candidate as
  traversed only in a part that opens with `backward`, `forward` or `both`, in the form `<id> (<n>)`. The bracket holds
  the count and nothing else, and the part must not contain the word "not": a note belongs in a part of its own. A
  targeted expansion adds its own part. `stopped` says why expansion ended (`docs/process.md`, "Screening for scope").
  If no candidate was judged out of scope this pass, the line ends `; rejected: none`, in place of entries in
  `rejected.md`.
- `Late papers` — `tools/assign.py late` prints the first form. After a recluster nothing prints it: the main session
  writes the second form, from `tools/cluster.py`'s `changes:` line.
- `Fringe` — `left out` counts the in-scope candidates that have neither an arXiv ID nor a `CorpusId`, so could not be
  added; they belong in Open work.
- `Errored queries` — `none` until a query errors; the first entry replaces the `none`.
- `Dissent searches` — one entry per searched cluster, separated by `;` or `|`, so neither may appear inside "what was
  searched", and the arrow is `->`, not `→`; an entry the check cannot read counts as missing. Every ID after `found:`
  must be a `dissent` row of that cluster, or be named in `Demotions`. A `dissent` row a coverage round added has no
  entry here; its trace is the `Coverage test` line.
- `Coverage test` — one line per round, printed from the round's sheet and pasted as printed: `tools/check.py` compares
  it with the sheet, up to `new clusters:`. "What it changed" names the target and the claim, such as "Gaps:
  <the new gap>" or "Assumptions: <which one>, revised". Only the IDs that open an entry are counted, and there must be
  K of them: the sheet's `changes` rows. A proposed cluster that the recluster did not form is recorded as
  `none (proposed <which>, not formed)`.
- `Judgement audit` — printed from the three audit sheets (`docs/process.md`, "Auditing the judgements"), and pasted as
  printed: `tools/check.py` recomputes it.
- `Tokens` — one entry per dispatch, appended when it returns, from the usage it reports: the brief's name and its
  scope, without commas or colons, then the tokens, without thousands separators, for example
  `Preflight: 4k, Orient: 81k, Selection c1+c2: 64200`.
- `Halts` and `Waivers` are written as `none` when the entry is created, so that a pass that met neither says so.
- `Ended` — `finished (F1)` or `halted (<id>)`, then the measured numbers: the last round's K of N and its bound, the
  radius (max and p90) that round's sheet records, the number of rounds, and the coreset's rows, for example
  `finished (F1); round 2: 0 of 12, bound 26%; radius 0.45, p90 0.22; 2 rounds; 54 rows`.

### 2. Clusters

One table:

| column | contents |
| -- | -- |
| `id` | short kebab-case id, used everywhere else to refer to the cluster |
| `name` | human-readable name |
| `definition` | one sentence: what papers in this cluster have in common. For a `high` cluster, a second sentence states its central claim: what its papers hold to be true, which a `dissent` row must contradict (`docs/process.md`, step 4) |
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
| `selected because` | one sentence on why this paper fills this role, e.g. "highest in-degree in cluster (31)"; for `dissent`, quoting the paper's claim that contradicts the cluster |
| `method name` | the method's actual name, if the paper introduces one; `n/a` if it does not. No cell is left empty |
| `method summary` | two sentences on what the paper does and how, including the assumptions the result depends on |
| `datasets / models` | the datasets and models of the headline evaluation |
| `metric` | the metric of the headline evaluation |
| `result` | the headline number, with its baseline and comparison condition, e.g. "+2.3 top-1 over X at equal FLOPs"; `n/a` if the paper reports no quantitative result |
| *(dimensions)* | one column per dimension: declared in the input, or proposed in the log's `Dimensions` line. No other column is allowed. |
| `source` | `full-text` or `abstract`: what the row was verified against (`docs/verification.md`). Always the last column. Legacy surveys may also carry `snippet`, from before verification quoted the full text. |

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
clustering report in `graphs/<topic>/clusters.json` alongside; see "`graphs/<topic>/`" below.

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

Keep it current as work proceeds. A subagent that leaves something outstanding must record it here before finishing, not
only in its report to the main session: reports live in one session's context and are lost when it ends. An agent
running in parallel with others returns its items under `Open work:` instead, and the main session writes them (as for
the log). An item is removed once it is done: a verified row leaves `Rows needing verification`, for example.

What goes under each heading:

- `Clusters not yet reviewed by the user` — written by the main session after naming, and emptied when the user reviews
  the clusters.
- `Empty roles` — a role a cluster's alignment requires that selection could not fill, with what was searched.
- `Rows needing verification` — every coreset row still `abstract`-sourced, with why: not yet verified, or no full text
  could be fetched. Selection lists its new rows here; verification removes the ones it verifies.
- `Coverage-test candidates not yet assessed` — sampled candidates a coverage round did not reach.
- `Probes requested` — a probe the user asked for, with its status.
- `Papers that could not enter the pool` — a paper judged in scope that Semantic Scholar does not know, that has no
  SPECTER2 embedding, or that has no ID at all.

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
an output needs a claim not present in the survey, add the paper to the coreset first, in a role, and verify it. A paper
not yet in the pool enters it as a late paper, and takes a role only once assigned (`docs/process.md`, "Late papers").

Outputs must carry their provenance. Every coreset row should be verified, so the default is that everything an output
cites has been checked against body text. Where a row could not be — its `source` is `abstract` — every claim resting on
it is marked `[abstract-only]`, right after the paper's ID. A marker that follows no cited ID fails the check, since it
qualifies nothing. Every output opens with a short legend explaining the marker, and saying what was missing if the pass
continued past a halt (`docs/process.md`, "When a pass ends"). Run `python3 tools/check.py <topic>` before treating an
output as finished: it lists every `abstract`-sourced paper the output cites.

## `graphs/<topic>/`

The working files of a pass: everything the scripts compute that is too large, or too numeric, for the survey. Scripts
write them, never agents, with these exceptions: the screening agent fills two columns of `fringe-screen.md`, through
`tools/fringe.py judge`; the coverage-test agent fills the verdicts of `coverage-<R>.md`, through
`tools/coverage.py judge`; the audit agents fill the audit sheets, through `tools/audit.py`; and the verifying agents
write `evidence/` (`docs/verification.md`, "Recording the evidence"). Sizes are from `reasoning-legacy` (about 200 pool
papers).

| file | what it holds | written by | read by | in git |
| -- | -- | -- | -- | -- |
| `pool.json` (1.6 MB) | per pool paper: date, citation count, full reference list, SPECTER2 embedding, fetch date | `tools/pool.py` (step 2, and inside `tools/assign.py late`) | every script that clusters, scores or draws the pool | yes |
| `clusters.json` (140 KB) | the clustering report: levels, stability, the null curve, assignment, sub-clusters, fringe scores, diagnostics and notes, the match to the previous clustering, and late assignments | `tools/cluster.py` (step 3, and any recluster); `tools/assign.py late` and `remap` add to it | `tools/sheets.py`, `assign.py`, `check.py`, `graph.py` | yes |
| `fringe.json` (1.3 MB) | the fringe candidates: route, metadata, references, embedding; the seeds of the `new` route | `tools/fringe.py collect` (step 2) | `tools/assign.py add-fringe` | yes |
| `rejected.md` | the candidates judged out of scope in orientation and expansion: paper, date, reason | `tools/assign.py reject` (steps 1 and 2, targeted expansions) | reviewers; `tools/check.py` (`G1`) | yes: the judgements are part of the pass's record |
| `fringe-screen.md` (120 KB, about 30k tokens) | the blind screening sheet: one row per candidate, shuffled, without its route or year, with the agent's `in scope` (`yes` or `no`; `maybe` while undecided) and `reason` | `tools/fringe.py collect` writes the rows, keeping earlier judgements on a rerun; the screening agent fills `in scope` and `reason` with `tools/fringe.py judge` (step 2) | `tools/assign.py add-fringe` | yes: the judgements are part of the pass's record |
| `naming-sheet.md` (about 3k tokens) | per computed cluster: size, stability, diagnostics and notes, most-cited papers, most recent papers with their citations per month, sub-clusters | `tools/sheets.py` (step 3) | the naming agent (step 3) and the selection agents (step 4) | no: regenerable |
| `fringe-sheet.md` (about 1k tokens) | the highest fringe scores, with year, cluster, reference count, and whether the paper is a coreset row | `tools/sheets.py` (step 3) | the fringe-selection agent (step 4) | no: regenerable |
| `coverage-<R>.md` | coverage-test round R: one row per sampled candidate, with how it was drawn, its verdict and the reason; the seed and the coreset's radius (see below) | `tools/coverage.py draw` (step 7); the verdicts and the recency-query rows by the coverage-test agent, with `tools/coverage.py judge` | the coverage-test agent; `tools/check.py` (`G5`); reviewers, auditors | yes: the judgements are part of the pass's record |
| `reverify.md`, `reverify-compare.md`, `faithfulness.md` | the judgement audits (`docs/process.md`, "Auditing the judgements"): the re-verified sample, each of its cells beside the survey's with a verdict, and the sampled output sentences beside their rows and evidence with a verdict | `tools/audit.py` (step 7); the cells and verdicts by the audit agents, with `tools/audit.py fill` and `judge` | the audit agents; `tools/check.py` (`G5`); reviewers | yes: the judgements are part of the pass's record |
| `graph.html` (1.3 MB) | the viewer | `tools/graph.py` (step 3) | the user, in a browser | no: regenerable |
| `evidence/<id>.md` | per verified coreset row: the verbatim quotes each claim rests on, and where they are in the paper | the verifying agent (step 5), one file per row, so parallel agents never share one | reviewers, auditors; `tools/check.py` (`G4`), which finds every full-text quote in the full text | yes: it is the record behind `source` |
| `fulltext/<id>.txt` (10–70k tokens each) | a paper's full text, flattened, without its bibliography | `tools/fulltext.py`: the main session's batch fetch before verification (step 5) | the verifying agent, through `tools/fulltext.py show` and Grep | no: third-party text, regenerable |
| `references.json` | reference lists for a survey without a pool | `tools/graph.py` | `tools/graph.py` | yes |
| `history.json`, `match-simulation.json`, `recursive.json`, `fringe-analysis.json` | reports of experiments that are not part of a pass (`docs/experiments.md`) | the experiment scripts | people | yes |

`pool.json` and `clusters.json` are what make the clustering reproducible offline, `fringe.json` with `fringe-screen.md`
is the record of what the fringe routes found and how it was screened, `rejected.md` the record of what expansion
screened out, the coverage sheets the record of every coverage-test verdict, the audit sheets the record of how often
the judgements held, and `evidence/` the record behind each verified row; so all of them are committed.

**Never Read a JSON file here, or `graph.html`, whole.** They are mostly embeddings and numbers: `pool.json` alone is
about 400k tokens. What an agent needs from them reaches it in three ways:

- a script's printout, which the main session hands over with the job (`docs/dispatch.md`, "Briefs");
- a sheet: `naming-sheet.md`, `fringe-sheet.md`, `fringe-screen.md`, `coverage-<R>.md` and the audit sheets. These are
  written to be read whole;
- `jq`, for one field, never a whole record, which carries the embedding, for example
  `jq '.papers["2504.13837"] | {date, citations, reference_count}' graphs/<topic>/pool.json`.

A full text is read through `tools/fulltext.py show` and Grep, at the sections a claim turns on, never whole
(`docs/verification.md`).

### The coverage sheet

One file per coverage-test round, `graphs/<topic>/coverage-<R>.md`, with one row per sampled candidate, the ones that
changed nothing included. `tools/coverage.py draw` writes it, with a header giving the date, the seed, the set drawn
from and the coreset's radius; the agent fills `verdict` and `reason`, and adds the recency query's candidates, with
`tools/coverage.py judge`, and records the recency query in the header with `tools/coverage.py query`, never by editing
the file:

| column | contents |
| -- | -- |
| `paper` | title, linked by its ID |
| `drawn as` | `worst-covered` or `recency query` (`docs/process.md`, step 7) |
| `distance` | how far the paper is from its nearest coreset row; empty for a recency candidate, which is not yet in the pool |
| `nearest row` | that row's paper ID |
| `verdict` | `no change`, `changes <target>`, or `new cluster` |
| `reason` | one sentence: the claim it would change and how, or why it changes nothing |

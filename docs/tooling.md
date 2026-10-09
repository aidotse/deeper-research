# Tooling

The scripts in `tools/`. The outside services some of them call, and the rules for calling them, are in
`docs/external_services.md`. They are listed in the order a pass uses them, after two that apply throughout: the paper
IDs every tool keys on, and the consistency check.

The files they write in `graphs/<topic>/`, with who reads each, are listed in `docs/formats.md` ("`graphs/<topic>/`").
**Never Read a JSON file there, or `graph.html`, whole**: `pool.json` alone is about 400k tokens. Use the script's
printout, the sheets, or `jq` for one field.

## Paper IDs

Every tool keys on the canonical paper ID of `docs/formats.md` ("Paper IDs"): the arXiv ID, or `CorpusId:<n>` for a
paper without one. The patterns are defined once, in `tools/check.py` (`ARXIV_ID`, `PAPER_ID`, `LINK`), and imported
everywhere.

## Consistency check

`python3 tools/check.py <topic> [--gate G<n>] [--status]` checks a topic's artifacts. Run it after every dispatch, after
every script that writes to the survey, and at each gate row of the checklist. It exits 1 on failure and 2 on a usage
error; a failure the responsible agent cannot fix halts the pass (`H9` in `docs/process.md`, "When a pass ends"). It
runs two kinds of check.

**Integrity**: whatever exists must be well formed, at every moment.

- the input's format, as `tools/inputs.py` reads it, including the `Coreset Spec` targets;
- the survey's five sections, in order;
- Clusters: ids unique and kebab-case, alignments valid, and every row with a `computed` id; and, if it has rows, a
  `graphs/<topic>/clusters.json` to name;
- Pool: the required columns, a paper link per row, unique IDs, and only known clusters; no paper listed twice, under
  two IDs or as two records with the same title; and no `CorpusId` row for a paper that has an arXiv ID;
- once `clusters.json` and the Clusters table exist: every computed cluster named exactly once, and every pool paper's
  `cluster` equal to its computed cluster. An empty cell is a late paper awaiting assignment, or, if `clusters.json`
  already assigns the paper, a cell `tools/assign.py clusters` has yet to write. A new clustering not yet remapped fails
  until `tools/assign.py remap` runs; this applies only once the Clusters table has names, so never to the provisional
  clustering of a first pass;
- once the Coreset has rows: one row per unique paper ID, the required columns, `source` last and parsable, and one
  column count throughout; dimension values within the sets the input declares; blocks headed by known cluster ids, in
  the Clusters table's order; valid roles, and every `bridge:` target a known cluster other than the row's own; every
  coreset paper in the pool, and in the block of the cluster it was computed into; coreset and bib holding the same IDs;
- once the output exists: every paper ID it cites in the coreset; every citation of an `abstract`-sourced paper followed
  directly by `[abstract-only]`, with only whitespace, bold markers and punctuation between them, and no other ID, and,
  if the output cites any such paper, a legend before its first `##` section; a section per target, then `Questions` and
  `Reading` (`docs/formats.md`).

**Gates**: what each step must have left behind, from `G0` (ready) to `G5` (pass ended). They are described in
`docs/gates.md`, and coded in `tools/gates.py`, one function per requirement. The check works out which gates the pass
has reached from the log's `Gates` line and from evidence in the files; `--gate G<n>` also requires every gate up to
`G<n>`. `--status` prints every gate with its open requirements. Against the last commit, it also checks that earlier
log entries are intact, that no pool paper, coreset row or `source` level was lost without a record, and that no
verified row was edited without a logged correction. Gates apply to surveys in the coreset layout only.

It also prints, without failing:

- the number of coreset rows, and per cluster: pool size, coreset rows by role, missing roles, and in-degree leaders
  within the pool;
- where a cluster's anchor is not its in-degree leader within the pool. That can be deliberate, but it should be;
- coreset columns that are not declared dimensions;
- the `source` tally, the share of `abstract`-sourced rows against `H10`'s 20%, and which `abstract`-sourced papers the
  output cites;
- phrases in the output that claim absence, which only a probe supports;
- requirements the user has waived, and an input changed since the last commit;
- pool papers not yet fetched, and late papers awaiting assignment.

Surveys written before the coreset structure (no Clusters section) get only the integrity checks that apply to them.

## Preflight

`python3 tools/preflight.py` runs the preflight checks that need no agent: the Graph API, the arXiv API and HTML, `uv`,
and the Asta key. It prints their part of the log's `Preflight` line, and exits 1 on any failure, which halts the pass
(`H1`). The Asta tools and WebSearch are checked by the agent (`docs/external_services.md`, "Preflight").

## Input

`python3 tools/inputs.py <topic>` prints what the tools read from `inputs/<topic>.md`: the declared dimensions with
their allowed values, the `Clustering` steering, and the coreset's targets from `Coreset Spec`. It fails on an unknown
section, a missing `Topic`, a dimension without values, or an unknown `Clustering` field or value, so a typo cannot
silently drop a request. `tools/check.py`, `tools/graph.py` and `tools/cluster.py` read the input through it. The format
is in `docs/formats.md`.

## Pool table

`tools/assign.py` writes papers and their clusters into the Pool table, so that nothing in it is written by hand:

- `python3 tools/assign.py add <topic> <paper-id> ...` adds papers by arXiv ID or `CorpusId`, each a title linked by its
  ID, with the other cells empty. It refuses a `CorpusId` whose paper has an arXiv ID, and lists for Open work a paper
  Semantic Scholar does not know or that has no SPECTER2 embedding, which clustering needs. Run `tools/pool.py`
  afterwards.
- `python3 tools/assign.py add-fringe <topic>` adds the candidates marked `yes` on the fringe screening sheet, and
  prints the log's `Fringe` line. It refuses while any candidate is still unjudged.
- `python3 tools/assign.py clusters <topic>` writes each pool paper's computed cluster into the `cluster` column, under
  the name the Clusters table's `computed` column gives it.
- `uv run tools/assign.py late <topic>` processes the late papers as one batch: it runs `tools/pool.py` in full, which
  fetches their data and prints its own `Pool` line, assigns each to the cluster its `k` nearest clustered papers
  favour, each voting with its similarity, records the assignment in `clusters.json` (`late`), writes the column, and
  prints the log's `Late papers` line. If late papers would exceed 10% of the pool, it assigns nothing, prints
  `RECLUSTER:` and exits 3: recluster instead.
- `python3 tools/assign.py reject <topic> <paper-id> <reason>` records a candidate judged out of scope in
  `graphs/<topic>/rejected.md`, with the date and the reason, so that the judgement can be reviewed (`docs/gates.md`).
  It refuses a paper already in the pool: leaving the pool needs the user's permission (`H12`).
- `python3 tools/assign.py remap <topic>` runs after a recluster. It moves each name to the new cluster it matched,
  clears the ones that did not match, and lists the new clusters to name. Until it has run, `clusters` refuses, so old
  names cannot land on new clusters.

See `docs/process.md`, step 3 and "Late papers". On a test topic built from `reasoning-legacy`, the nearest-cluster rule
put all 15 held-out papers in the cluster the full clustering had chosen. That is an optimistic test, since those papers
had taken part in that clustering.

## Pool metadata

`python3 tools/pool.py <topic>` fetches publication dates, citation counts, full reference lists and SPECTER2 embeddings
for every paper in a survey from the Semantic Scholar API, unauthenticated, into the pool sidecar
`graphs/<topic>/pool.json`, and fills the pool's `year`, `citations` and `cites` columns. It fetches by arXiv ID or
`CorpusId`, and records each paper's arXiv ID where Semantic Scholar knows it, from `externalIds` or an open-access PDF
on arXiv; `tools/check.py` uses that to catch a `CorpusId` row for a paper that has an arXiv ID. It runs outside any
model's context, so it costs no tokens. It saves after every batch of 100 papers, and each record carries the date it
was fetched. Later runs fetch only new papers; `--refresh` refetches all. It ends by printing the log's `Pool` line,
with the range of fetch dates.

## Fringe candidates

`uv run tools/fringe.py collect <topic>` runs the two fringe routes of `docs/process.md`, `hidden` and `new`, at the end
of step 2. It needs a clustering to seed the `new` route, so run `tools/cluster.py` provisionally first. It fetches the
candidates' data into `graphs/<topic>/fringe.json`, and writes a blind screening sheet, `fringe-screen.md`, for a
`survey-pass` agent: shuffled, with the route hidden. A rerun keeps the judgements already on the sheet. The agent marks
each `yes` or `no`, and `tools/assign.py add-fringe` adds the in-scope ones to the pool. `fringe.json` records each
candidate's arXiv ID or, failing that, its `CorpusId`. A candidate without a SPECTER2 embedding is dropped before the
sheet, since no clustering could place it.

`tools/cluster.py` writes each pool paper's fringe score to its report, and prints the highest. Step 4 chooses `fringe`
rows from the fringe sheet (see "Sheets").

## Clustering

`uv run tools/cluster.py <topic>` runs the clustering method of `docs/process.md`: all three measures, the grid of
levels, the stability tests, and the choice of measure and level. Options: `--rule` (`tau` or `null`), `--tau`, `--k`,
`--c`, `--reps`, `--nulls` and `--levels`; the defaults are the spec's. It applies the input's `granularity` steering;
`--level coarser|finer|N` does the same as a user override, and takes precedence; `N` may be a level's target or the
number of clusters it reached, as the viewer's slider shows it. After a rerun, carry the names over with
`tools/assign.py remap`. A pool with fewer than 12 embedded papers stops with `STOP: H8`. When a previous
`clusters.json` exists, it matches the new clustering to it by shared papers and prints the result, for
`tools/assign.py remap`. It takes about two minutes for 200 papers, most of it the null model. It writes the report to
`graphs/<topic>/clusters.json`. It prints each cluster's size, stability and sub-clusters, the stability diagnostics of
`docs/process.md` ("When stability fails") with their actions, the highest fringe scores with each paper's number of
resolved references, and the retrieval log's `Clustering` and `Temporal stability` lines, in the form `docs/formats.md`
gives, ready to paste once the ids and actions are filled in. It needs `uv`, which installs its Python dependencies on
first use.

## Sheets

`python3 tools/sheets.py <topic>` writes two compact sheets next to `clusters.json`, for the agents that would otherwise
need the large JSON files. `naming-sheet.md` (step 3) gives, per computed cluster: its size and stability, since when it
exists, its diagnostics, its most-cited and most recent papers, and its sub-clusters, marked "internally divided" when
at least two of them score 0.6 or more. `fringe-sheet.md` (step 4) lists the highest fringe scores, with year, cluster,
reference count and whether the paper is already a coreset row. On `reasoning-legacy` they come to about 2.8k and 0.8k
tokens. Rerun it after naming, so that the sheets show the names.

## Graph viewer

`python3 tools/graph.py <topic>` reads `surveys/<topic>.md` and writes `graphs/<topic>/graph.html`: one self-contained
page that opens straight from the file system, with no server and no network. Nodes are papers, sized by how often the
other papers in the set cite them; edges are citations within the set. The map names groups only; paper names appear as
you zoom in, most-cited first, and full titles on hover. It offers three layouts: a citation map; tiles grouped by the
chosen attribute; and a timeline, with submission date left to right and one row per survey cluster. On the citation
map, a dragged paper pulls its links like elastic and springs back when released. Colour follows the chosen attribute:
cluster, citation community, declared dimension or verification source. It uses the eight hues of the `dataviz`
reference palette, validated in both light and dark mode; past eight groups the hues repeat as hollow rings, then as
tinted fills, rather than adding hues that colourblind readers could not tell apart. Every group is also named on the
map, in the list and in the table. It also has search, a date histogram to filter by dragging, a group list with each
group's papers, a side panel showing a paper's full survey row or a group's cohesion and outside links, and a table
view. The URL hash records the current view, so a view can be bookmarked.

Its main job is cluster review. Alongside the survey's own clusters it computes **citation communities** (Louvain
modularity over the citation graph) and reports, for each cluster, the share of its citation links that stay inside it.
A cluster whose papers mostly cite other clusters is a label, not a neighbourhood, and is worth questioning.

Where `tools/cluster.py` has run, the viewer also shows how the clusters were produced: the chosen measure and level,
`k`, `c`, `τ`, the stability curves with the null model's curve and the chosen level marked, each cluster's clusterwise
stability, the sub-clusters of the level below, and since when each cluster exists (a stacked column per date snapshot,
and a "Since when" line per cluster). A `Similarity map` layout places papers by the clustering's own neighbour graph,
and a level slider recolours the map at each computed level, for choosing the level by eye during review. The similarity
map's layout is seeded, so it is the same on every load.

A coreset survey carries its own graph in the pool's `cites` column, so nothing is fetched. A survey without a pool has
its references fetched from the Semantic Scholar API and cached in `graphs/<topic>/references.json`; pass `--refresh` to
refetch. A paper is placed on the timeline by the month its arXiv ID encodes, or, without an arXiv ID, by its
publication date from the pool sidecar; its title links to its arXiv page or Semantic Scholar page. The viewer's code is
`tools/graph_template.html`, and its libraries are vendored in `tools/vendor/`.

## Full text

`uv run tools/fulltext.py <topic> <id> [<id> ...]` fetches papers' full text from arXiv into
`graphs/<topic>/fulltext/<id>.txt` (a slash or colon in the ID becomes `_`), for verification; `--abstract` fetches
every coreset row still `abstract`-sourced. The text is arXiv's HTML rendering flattened to plain text: markdown
headings per section, `[caption]` lines for figure and table captions, tables one row per line with cells separated by
`|`, and equations as their LaTeX source. The bibliography is dropped. Where arXiv has no HTML, it falls back to the
PDF's text, marked `(pdf)` in the file's header, with `[page N]` markers; words there are often hyphenated across line
breaks, so search for word stems. A paper without an arXiv ID is fetched from the open-access PDF Semantic Scholar lists
for it, if that link serves a PDF; publishers' links often serve a web page, or refuse. A paper with no fetchable full
text is listed in a note and the exit status stays 0: it is the uncheckable outcome of `docs/verification.md`, not a
failure. No model is involved, so the text is verbatim. Existing files are kept; `--refresh` refetches. On
`reasoning-legacy`, all 27 abstract-sourced rows came from HTML, at 9–68k tokens per paper, in 90 seconds.

## Bibliography

`python3 tools/bib.py <topic>` regenerates `bib/<topic>.bib` from the coreset: from the arXiv API, or from Semantic
Scholar for a paper without an arXiv ID. See `docs/formats.md`.

## Experiments, not part of a pass

`uv run tools/recursive.py <topic>` is an experiment, not part of a pass. It clusters recursively instead of at one
global level: each cluster of the global clustering is split on its own until no split passes, under several stopping
rules (`--rules`, see its docstring), including a shakedown that redoes each split decision on disturbed data. It
compares each result with the global method by rerunning both from scratch on time holdouts and resamples. It reads
`clusters.json` and writes `graphs/<topic>/recursive.json`; it takes about five minutes on 200 papers.

`uv run tools/match.py simulate <topic>` is an experiment, not part of a pass. The module's `match()` function, which
matches two clusterings by shared members, is also what `tools/cluster.py` uses to match a new clustering to the
previous one. `simulate` treats the pool as it stood 3, 6 and 9 months ago as earlier passes, reruns the full clustering
method on each, and matches it to today's clustering. It writes `graphs/<topic>/match-simulation.json`.

`uv run tools/match.py history <topic>` runs, on its own, the cluster history that `tools/cluster.py` already runs after
every clustering: four date segments of equal paper count, each cumulative snapshot clustered with today's settings, and
per cluster since when it exists, or why it is not yet found. It writes `graphs/<topic>/history.json`.

`uv run tools/fringe.py analyse <topic>` is the experiment behind the fringe routes: it reclusters with the screened
candidates added, and reports per route how they behave. It is not part of a pass. Its report is
`graphs/<topic>/fringe-analysis.json`.

## Small helpers

`python3 tools/asta_config.py` reports whether the Asta MCP server is configured with an API key, without printing the
key; the session-start hook and the preflight check run it (`docs/external_services.md`). `tools/net.py` is the HTTP
retry that every fetching script shares: it retries a 429, a 500, 502, 503 or 504, a dropped connection or a timeout,
and raises anything else.

## Tests

`python3 tests/gates/faults.py` and `python3 tests/gates/behaviour.py` test the gates of `tools/check.py`. Both build a
temporary topic, `zz-gate-<pid>`, from the data of the legacy survey `reasoning-legacy` (`tests/gates/build.py`). The
name is unique per run, so two runs never share files, and every file a run wrote is removed when it exits, even after a
crash. `faults.py` first confirms that the unmodified fixture passes `--gate G5`, since a fault is only caught if the
baseline passes. It then injects at least one fault per gate requirement and confirms that its own requirement catches
it. `behaviour.py` checks what single requirements cannot show: waivers, a pending halt, progress inferred mid-pass and
by the safety net, the history checks, and `tools/assign.py reject`. Run both after any change to `tools/check.py` or
`tools/gates.py`; each exits 1 on a miss. A change to a requirement comes with its test case, in the same commit.

## Formatting

Markdown in this repo is formatted with mdformat, configured in `.mdformat.toml`. It runs automatically when a turn
ends. Do not hand-align table pipes or adjust whitespace; it will be normalised regardless.

For info: mdformat installed with `uv tool install mdformat --with mdformat-gfm --with mdformat-front-matters`.

To format manually: `mdformat .` from the repo root. To check without writing: `mdformat --check .`

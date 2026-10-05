# Tooling

The scripts in `tools/`. The outside services some of them call, and the rules for calling them, are in
`docs/external_services.md`.

## Consistency check

`python3 tools/check.py <topic>` verifies that a topic's artifacts agree. Run it after every subagent returns, after
regenerating a bib, and before treating an output as finished. It exits 1 on failure, so it can gate a pass.

Hard checks, any of which fail the run:

- Coreset row count equals its count of unique arXiv IDs. A mismatch means a duplicated row or a malformed link.
- Every row has a parsable `source` cell, and it is the last column. Every block has the same column count.
- Declared dimension values are within their allowed sets.
- Cluster ids are unique and alignments valid. Every coreset block is headed by a known cluster id, every `role` is
  valid, and every `bridge:` target is a known cluster.
- Pool IDs are unique, every pool `cluster` is known, and every coreset paper is in the pool.
- Coreset and bib contain the same IDs, checked in both directions.
- Every arXiv ID cited in the output is in the coreset.

It also prints notes, which are not failures:

- per-cluster counts of coreset rows by role, and pool size;
- high-alignment clusters missing an anchor, frontier or dissent. An empty dissent slot is legitimate if Open work
  records what was searched;
- where a cluster's anchor is not its in-degree leader within the pool. That can be deliberate, but it should be;
- the number of `fringe` rows, when it is outside the quota of five to ten per topic;
- the `source` tally, and any `abstract`-sourced papers the output cites, each of which needs a provisional marker.

Surveys written before the coreset structure (no Clusters section) get only the checks that apply to them.

The tools key on arXiv IDs. A paper without one cannot yet enter the coreset; record it in Open work.

## Graph viewer

`python3 tools/graph.py <topic>` reads `surveys/<topic>.md` and writes `graphs/<topic>/graph.html`: one self-contained
page that opens straight from the file system, with no server and no network. Nodes are papers, sized by how often the
other papers in the set cite them; edges are citations within the set. The map names groups only; paper names appear as
you zoom in, most-cited first, and full titles on hover. It offers three layouts: a citation map; tiles grouped by the
chosen attribute; and a timeline, with submission date left to right and one row per survey cluster. On the citation
map, a dragged paper pulls its links like elastic and springs back when released. Colour follows the chosen attribute:
cluster, citation community, declared dimension or verification source. It also has search, a date histogram to filter
by dragging, a group list with each group's papers, a side panel showing a paper's full survey row or a group's cohesion
and outside links, and a table view. The URL hash records the current view, so a view can be bookmarked.

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
refetch. The viewer's code is `tools/graph_template.html`, and its libraries are vendored in `tools/vendor/`.

## Pool metadata

`python3 tools/pool.py <topic>` fetches publication dates, citation counts, full reference lists and SPECTER2 embeddings
for every paper in a survey from the Semantic Scholar API, unauthenticated, into the pool sidecar
`graphs/<topic>/pool.json`, and fills the pool's `year`, `citations` and `cites` columns. It runs outside any model's
context, so it costs no tokens. Later runs fetch only new papers; `--refresh` refetches all.

## Clustering

`uv run tools/cluster.py <topic>` runs the clustering method of `docs/process.md`: all three measures, the grid of
levels, the stability tests, and the choice of measure and level. Options: `--rule` (`tau` or `null`), `--tau`, `--k`,
`--c`, `--reps`, `--nulls` and `--levels`; the defaults are the spec's. It takes about two minutes for 200 papers, most
of it the null model. It writes the report to `graphs/<topic>/clusters.json` and prints the figures the retrieval log's
`Clustering` and `Temporal stability` lines need, the stability diagnostics of `docs/process.md` ("When stability
fails") with their actions, and the highest fringe scores. It needs `uv`, which installs its Python dependencies on
first use.

## Fringe candidates

`uv run tools/fringe.py collect <topic>` runs the two fringe routes of `docs/process.md`, `hidden` and `new`, at the end
of step 2. It needs a clustering to seed the `new` route, so run `tools/cluster.py` provisionally first. It fetches the
candidates' data into `graphs/<topic>/fringe.json`, and writes a blind screening sheet, `fringe-screen.md`, for a
`survey-pass` agent: shuffled, with the route hidden. The in-scope candidates are then added to the pool.

`uv run tools/fringe.py analyse <topic>` is the experiment behind the fringe routes: it reclusters with the screened
candidates added, and reports per route how they behave. It is not part of a pass. Its report is
`graphs/<topic>/fringe-analysis.json`.

`tools/cluster.py` writes each pool paper's fringe score to its report, and prints the highest; step 4 chooses `fringe`
rows from them.

`uv run tools/recursive.py <topic>` is an experiment, not part of a pass. It clusters recursively instead of at one
global level: each cluster of the global clustering is split on its own until no split passes, under several stopping
rules (`--rules`, see its docstring), including a shakedown that redoes each split decision on disturbed data. It
compares each result with the global method by rerunning both from scratch on time holdouts and resamples. It reads
`clusters.json` and writes `graphs/<topic>/recursive.json`; it takes about five minutes on 200 papers.

`uv run tools/match.py simulate <topic>` is an experiment, not part of a pass. Its `match()` function is the draft rule
for matching clusters across passes, by shared members. `simulate` treats the pool as it stood 3, 6 and 9 months ago as
earlier passes, reruns the full clustering method on each, and matches it to today's clustering. It writes
`graphs/<topic>/match-simulation.json`.

`uv run tools/match.py history <topic>` runs, on its own, the cluster history that `tools/cluster.py` already runs after
every clustering: four date segments of equal paper count, each cumulative snapshot clustered with today's settings, and
per cluster since when it exists, or why it is not yet found. It writes `graphs/<topic>/history.json`.

## Full text

`uv run tools/fulltext.py <topic> <id> [<id> ...]` fetches papers' full text from arXiv into
`graphs/<topic>/fulltext/<id>.txt`, for verification; `--abstract` fetches every coreset row still `abstract`-sourced.
The text is arXiv's HTML rendering flattened to plain text: markdown headings per section, `[caption]` lines for figure
and table captions, tables one row per line with cells separated by `|`, and equations as their LaTeX source. The
bibliography is dropped. Where arXiv has no HTML, it falls back to the PDF's text, marked `(pdf)` in the file's header,
with `[page N]` markers; words there are often hyphenated across line breaks, so search for word stems. No model is
involved, so the text is verbatim. Existing files are kept; `--refresh` refetches. On `reasoning`, all 27
abstract-sourced rows came from HTML, at 9–68k tokens per paper, in 90 seconds.

## Bibliography

`python3 tools/bib.py <topic>` regenerates `bib/<topic>.bib` from the coreset. See `docs/formats.md`.

## Formatting

Markdown in this repo is formatted with mdformat, configured in `.mdformat.toml`. It runs automatically when a turn
ends. Do not hand-align table pipes or adjust whitespace; it will be normalised regardless.

For info: mdformat installed with `uv tool install mdformat --with mdformat-gfm --with mdformat-front-matters`.

To format manually: `mdformat .` from the repo root. To check without writing: `mdformat --check .`

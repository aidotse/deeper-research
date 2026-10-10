# Tooling

The scripts in `tools/`. The outside services some of them call, and the rules for calling them, are in
`docs/external_services.md`. They are listed in the order a pass uses them, after two that apply throughout: the paper
IDs every tool keys on, and the consistency check. A script that takes arguments exits 2 on a usage error. A script that
needs a file an earlier step writes, and finds it missing, says which command to run first, rather than failing with a
traceback.

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
  until `tools/assign.py remap` runs; this applies only once the Clusters table has names, so never to the first
  clustering of a first pass;
- once the Coreset has rows: one row per unique paper ID, the required columns, `source` last and either `full-text` or
  `abstract` (`snippet` only in a legacy survey), and one column count throughout; dimension values within the sets the
  input declares; blocks headed by known cluster ids, in the Clusters table's order; valid roles, and every `bridge:`
  target a known cluster other than the row's own; every coreset paper in the pool, and in the block of the cluster it
  was computed into; coreset and bib holding the same IDs;
- once the output exists: every paper ID it cites in the coreset; every citation of an `abstract`-sourced paper followed
  directly by `[abstract-only]`, with only whitespace, bold markers and punctuation between them, and no other ID, and,
  if the output cites any such paper, a legend before its first `##` section; in the coreset layout, no marker after the
  legend that follows no cited ID; a section per target, then `Questions` and `Reading` (`docs/formats.md`).

**Gates**: what each step must have left behind, from `G0` (ready) to `G5` (pass ended). They are described in
`docs/gates.md`, and coded in `tools/gates.py`, one function per requirement. The check works out which gates the pass
has reached from the log's `Gates` line and from evidence in the files; `--gate G<n>` also requires every gate up to
`G<n>`, and says the gate passed only when nothing at all fails. `--status` prints every gate with its open
requirements, and both run on a survey whose pass has no log entry yet. When the input declares no dimensions, the check
reads the proposed ones from the current entry's `Dimensions` line, and checks against them as if declared. Against the
last commit, it also checks that earlier log entries are intact, that no pool paper, coreset row or `source` level was
lost without a record, and that no verified row was edited without a logged correction. Gates apply to surveys in the
coreset layout only.

It also prints, without failing:

- the number of coreset rows, and per cluster: pool size, coreset rows by role, missing roles, and in-degree leaders
  within the pool;
- where a cluster's anchor is not its in-degree leader within the pool. That can be deliberate, but it should be;
- coreset columns that are not declared dimensions;
- the `source` tally, the share of `abstract`-sourced rows against `H10`'s 20%, and which `abstract`-sourced papers the
  output cites;
- how many coreset papers, and how many pool papers, have an arXiv ID: the papers whose full text can most surely be
  fetched;
- phrases in the output that claim absence, which only a probe supports;
- requirements the user has waived, a halt still pending, and an input changed since the last commit;
- pool papers not yet fetched, and late papers awaiting assignment, with the command that processes them;
- clusters that trade papers without a bridge yet, as soon as there are Coreset rows, so that the Bridges row runs
  before fringe selection;
- full-text quotes it could not check because the full text is not fetched: a note in the plain check, a failure under
  `--gate G4` or later;
- papers both rejected and in the pool, since one of the two judgements is wrong.

Surveys written before the coreset structure (no Clusters section) get only the integrity checks that apply to them.

## Preflight

`python3 tools/preflight.py` runs the preflight checks that need no agent: the Graph API, the arXiv API and HTML, `uv`,
and the Asta key. It prints their part of the log's `Preflight` line, and exits 1 on any failure, which halts the pass
(`H1`). The Asta tools and WebSearch are checked by the agent (`docs/external_services.md`, "Preflight").

## Input

`python3 tools/inputs.py <topic>` prints what the tools read from `inputs/<topic>.md`: the declared dimensions with
their allowed values, the `Clustering` steering, and the coreset's targets from `Coreset Spec`. It fails on anything it
cannot read, such as an unknown or repeated section, an empty `Topic` or an unknown `Clustering` value, so a typo cannot
silently drop a request; the full list is in `docs/formats.md` ("Rules the parser applies"). `tools/check.py`,
`tools/graph.py` and `tools/cluster.py` read the input through it. The format is in `docs/formats.md`.

## Pool table

`tools/assign.py` writes papers and their clusters into the Pool table, so that nothing in it is written by hand:

- `python3 tools/assign.py add <topic> <paper-id> ...` adds papers by arXiv ID or `CorpusId`, each a title linked by its
  ID, with the other cells empty. It refuses a `CorpusId` whose paper has an arXiv ID, and lists for Open work a paper
  Semantic Scholar does not know or that has no SPECTER2 embedding, which clustering needs. It warns on a paper already
  in `rejected.md`, naming the rejection. Its last line names the next step: `tools/pool.py` before step 3, or
  `tools/assign.py late` after it, for the main session to run, pasting the `Pool` line it prints.
- `python3 tools/assign.py add-fringe <topic>` adds the candidates marked `yes` on the fringe screening sheet, and
  prints the log's `Fringe` line. It refuses while any candidate is unjudged: with no row on the sheet, marked neither
  `yes` nor `no` (a `maybe` included), or with a reason under two words. It uses the same test as `G1`.
- `python3 tools/assign.py clusters <topic>` writes each pool paper's computed cluster into the `cluster` column, under
  the name the Clusters table's `computed` column gives it.
- `uv run tools/assign.py late <topic>` processes the late papers as one batch: it runs `tools/pool.py` in full, which
  fetches their data and prints its own `Pool` line, assigns each to the cluster its `k` nearest clustered papers
  favour, each voting with its similarity, records the assignment in `clusters.json` (`late`), writes the column, and
  prints the log's `Late papers` line. If late papers would exceed 10% of the pool, it assigns nothing, prints
  `RECLUSTER:` with the count and the exact share, and exits 3: recluster instead.
- `python3 tools/assign.py reject <topic> <paper-id> <reason>` records a candidate judged out of scope in
  `graphs/<topic>/rejected.md`, with the date and the reason, so that the judgement can be reviewed (`docs/gates.md`).
  Without a paper ID, it reads one `<paper-id><TAB><reason>` per line from stdin, and records them all, or none if any
  line is wrong. It refuses a paper already in the pool: leaving the pool needs the user's permission (`H12`).
- `python3 tools/assign.py remap <topic>` runs after a recluster. It moves each name to the new cluster it matched,
  clears the ones that did not match, and lists the new clusters to name. Until it has run, `clusters` refuses, so old
  names cannot land on new clusters.

See `docs/process.md`, step 3 and "Late papers". On `reasoning-legacy`, 15 papers were held out of a clustering and then
assigned by the nearest-cluster rule: 13 went to the cluster the full clustering chose for them. One of the two misses,
`2402.03300`, was the top paper of its cluster in the full clustering, so a late paper's cluster is a good guess, not a
certainty.

## Pool metadata

`python3 tools/pool.py <topic>` fetches publication dates, citation counts, full reference lists and SPECTER2 embeddings
for every paper in a survey from the Semantic Scholar API, unauthenticated, into the pool sidecar
`graphs/<topic>/pool.json`, and fills the pool's `year`, `citations` and `cites` columns. It fetches by arXiv ID or
`CorpusId`, and records each paper's arXiv ID where Semantic Scholar knows it, from `externalIds` or an open-access PDF
on arXiv; `tools/check.py` uses that to catch a `CorpusId` row for a paper that has an arXiv ID. It runs outside any
model's context, so it costs no tokens. It saves after every batch of 100 papers, and each record carries the date it
was fetched. Later runs fetch only new papers; `--refresh` refetches all. A record fetched before records kept the arXiv
ID gets that ID, and its `CorpusId`, by one light call per 100 papers; the rest of the record, and its fetch date, stay
as they were. It ends by printing the log's `Pool` line: the papers in scope, how many have an arXiv ID, and the range
of fetch dates.

## Fringe candidates

`uv run tools/fringe.py collect <topic>` runs the two fringe routes of `docs/process.md`, `hidden` and `new`, at the end
of step 2. It needs no clustering: it seeds the `new` route from the frontier candidates of the latest pass's
`Orientation` line, plus up to 10 pool papers most cited within the pool, and records the seeds in `fringe.json`. A
frontier candidate not in the pool is skipped with a warning. It fetches the candidates' data into
`graphs/<topic>/fringe.json`, and writes a blind screening sheet, `fringe-screen.md`, for a `survey-pass` agent:
shuffled, with the route and the year hidden. A paper already in `rejected.md` is not collected. A rerun keeps the
judgements already on the sheet.

`python3 tools/fringe.py judge <topic>` writes the agent's verdicts into the sheet, from stdin: one
`<s2><TAB>yes|no|maybe<TAB><reason>` per line, where `<s2>` is the row's first cell. It refuses the whole batch if any
line names an ID not on the sheet, gives another verdict, or has no reason. A `maybe` parks a row to come back to: it
counts as unjudged until it becomes `yes` or `no`. Then `tools/assign.py add-fringe` adds the in-scope ones to the pool.
`fringe.json` records each candidate's arXiv ID or, failing that, its `CorpusId`. A candidate without a SPECTER2
embedding is dropped before the sheet, since no clustering could place it.

`tools/cluster.py` writes each pool paper's fringe score to its report, and prints the highest. Step 4 chooses `fringe`
rows from the fringe sheet (see "Sheets").

## Clustering

`uv run tools/cluster.py <topic>` runs the clustering method of `docs/process.md`: the `combined` measure, the grid of
levels, the stability tests, one null draw, the choice of level, and the fringe score. Options, with their defaults:
`--k 10`, `--c 10`, `--reps 20`, `--nulls 1` (at least 1), `--tau 0.75` and `--levels 3,4,5,6,8,10,12,15,18,22`. The
fringe score's age cohort is 30 papers. These are first guesses, not derived values. A usage error, such as a bad option
or `--nulls 0`, exits 2. It applies the input's `granularity` steering; `--level coarser|finer|N` does the same as a
user override, and takes precedence; `N` may be a level's target or the number of clusters it reached, as the viewer's
slider shows it. After a rerun, carry the names over with `tools/assign.py remap`. A pool with fewer than 12 embedded
papers stops with `STOP: H8`. When a previous `clusters.json` exists, it matches the new clustering to it by shared
papers and prints the result, for `tools/assign.py remap`: where each new cluster came from, then one `changes:` line
listing the splits, merges, new and vanished clusters. It takes about 30 seconds for 200 papers. It writes the report to
`graphs/<topic>/clusters.json`. It prints each cluster's size, stability and sub-clusters, the stability diagnostics of
`docs/process.md` ("When stability fails") with their actions, the notes that need no action, the highest fringe scores
with each paper's number of resolved references, and the retrieval log's `Clustering` line, in the form
`docs/formats.md` gives, ready to paste once the ids and actions are filled in. It needs `uv`, which installs its Python
dependencies on first use, at the versions pinned in the script's header. The report's `params` records the settings
used, `defaults` (the default of each), `seeds` (every random seed the method uses) and `versions` (Python and each
package), so that a run can be reproduced exactly.

## Sheets

`python3 tools/sheets.py <topic>` writes two compact sheets next to `clusters.json`, for the agents that would otherwise
need the large JSON files. `naming-sheet.md` (step 3) gives, per computed cluster: its size and stability, its
diagnostics and notes, its most-cited and most recent papers, and its sub-clusters, marked "internally divided" when at
least two of them score 0.6 or more. `fringe-sheet.md` (step 4) lists the highest fringe scores, with year, cluster,
reference count and whether the paper is already a coreset row. On `reasoning-legacy` they come to about 2.8k and 0.8k
tokens. Rerun it after naming, so that the sheets show the names. Each cluster's most recent papers carry their
citations per month since publication, counted to the date the citations were fetched: the frontier role's measure of
impact (`docs/process.md`, step 4).

## Graph viewer

`python3 tools/graph.py <topic>` reads `surveys/<topic>.md` and writes `graphs/<topic>/graph.html`: one self-contained
page that opens straight from the file system, with no server and no network. Nodes are papers, sized by how often the
other papers in the set cite them; edges are citations within the set. The map names groups only; paper names appear as
you zoom in, most-cited first, and full titles on hover. It offers three layouts: a citation map; tiles grouped by the
chosen attribute; and a timeline, with submission date left to right and one row per survey cluster. On the citation
map, a dragged paper pulls its links like elastic and springs back when released. Colour follows the chosen attribute:
cluster, citation community, declared dimension, verification source, or whether the paper has an arXiv ID, which the
overview also counts. It uses the eight hues of the `dataviz` reference palette, validated in both light and dark mode;
past eight groups the hues repeat as hollow rings, then as tinted fills, rather than adding hues that colourblind
readers could not tell apart. Every group is also named on the map, in the list and in the table. It also has search, a
date histogram to filter by dragging, a group list with each group's papers, a side panel showing a paper's full survey
row or a group's cohesion and outside links, and a table view. The URL hash records the current view, so a view can be
bookmarked.

Its main job is cluster review. Alongside the survey's own clusters it computes **citation communities** (Louvain
modularity over the citation graph) and reports, for each cluster, the share of its citation links that stay inside it.
A cluster whose papers mostly cite other clusters is a label, not a neighbourhood, and is worth questioning.

Where `tools/cluster.py` has run, the viewer also shows how the clusters were produced: the measure and the chosen
level, `k`, `c`, `τ`, the stability curve with the null model's curve and the chosen level marked, each cluster's
clusterwise stability, the diagnostics and notes, and the sub-clusters of the level below. A `Similarity map` layout
places papers by the clustering's own neighbour graph, and a level slider recolours the map at each computed level, for
choosing the level by eye during review. The similarity map's layout is seeded, so it is the same on every load.

A coreset survey carries its own graph in the pool's `cites` column, so nothing is fetched. A survey without a pool has
its references fetched from the Semantic Scholar API and cached in `graphs/<topic>/references.json`; pass `--refresh` to
refetch. A paper is placed on the timeline by the month its arXiv ID encodes, or, without an arXiv ID, by its
publication date from the pool sidecar; its title links to its arXiv page or Semantic Scholar page. The viewer's code is
`tools/graph_template.html`, and its libraries are vendored in `tools/vendor/`.

## Full text

`uv run tools/fulltext.py <topic> <id> [<id> ...]` fetches papers' full text from arXiv into
`graphs/<topic>/fulltext/<id>.txt` (a slash or colon in the ID becomes `_`), for verification: every verified row quotes
it (`docs/verification.md`). `--abstract` fetches every coreset row still `abstract`-sourced: the main session runs it
once before dispatching verification (`docs/process.md`, step 5), since requests are spaced three seconds apart and
parallel fetches would break that. On `reasoning-legacy`, 27 papers took 90 seconds, at 9–68k tokens per paper, all from
HTML.

The text is arXiv's HTML rendering flattened to plain text: markdown headings per section, `[caption]` lines for figure
and table captions, tables one row per line with cells separated by `|`, and equations as their LaTeX source. Where
arXiv has no HTML, it falls back to the PDF's text, marked `(pdf)` in the file's header, with `[page N]` markers; words
there are often hyphenated across line breaks, so search for word stems. A paper without an arXiv ID is fetched from the
open-access PDF Semantic Scholar lists for it, if that link serves a PDF; publishers' links often serve a web page, or
refuse. No model is involved, so the text is verbatim. Existing files are kept; `--refresh` refetches.

The bibliography is dropped, so that a search for a claim's terms cannot hit a reference title, and no quote can come
from one. In HTML it is its own element. In PDF text, it is cut from the last `References` or `Bibliography` heading
that a list of references follows, up to an `Appendix` or `Supplementary material` heading if one comes after it, and a
`[bibliography removed]` line marks the cut. An appendix headed otherwise, such as "A Proofs", is cut with the
bibliography. This cut has been tested on synthetic text only, so check the first PDF-sourced paper by hand.

A paper with no fetchable full text is listed in a note, and the exit status stays 0: it is the uncheckable outcome of
`docs/verification.md`, not a failure. An unreadable PDF counts as not fetched. A failure of arXiv itself, after
retries, exits non-zero.

`uv run tools/fulltext.py show <topic> <id> [<pattern>] [--section <name>]... [--max <tokens>]` reads a fetched file by
section, so that an agent reads only what it needs:

- with no pattern, the outline: every heading, with the size of its section in tokens;
- with a pattern, a case-insensitive regular expression, each matching passage under its section heading;
- with `--section`, whole sections whose heading starts with the name, section numbers optional; with a pattern too, it
  searches only those.

Passages are printed verbatim, so they can be quoted, with the file's line numbers, to read on from. Output is capped at
`--max` tokens, 6000 by default, with a note when cut. PDF text has no markup: its sections are its pages (`page 3`) and
the lines that look like headings, and a heading such as "B Additional results" is not detected.

## Bibliography

`python3 tools/bib.py <topic>` regenerates `bib/<topic>.bib` from the coreset: from the arXiv API, or from Semantic
Scholar for a paper without an arXiv ID. It takes each row's paper from the first link in the row, as `tools/check.py`
does. See `docs/formats.md`.

## Experiments

`tools/recursive.py`, `tools/match.py simulate` and `history`, and `tools/fringe.py analyse` are experiments, not part
of a pass. No step runs them and no agent needs them. They are described in `docs/experiments.md`, for human reviewers.

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
ends, on `docs/` and `outputs/` only; if mdformat is not installed, the hook says so. It leaves alone the files agents
may be editing at that moment (surveys and sheets) and the user's inputs. Do not hand-align table pipes or adjust
whitespace in the files it formats; it will be normalised regardless.

For info: mdformat installed with `uv tool install mdformat --with mdformat-gfm --with mdformat-front-matters`.

To format other files by hand, name them, for example `mdformat CLAUDE.md .audits`. Never run it on `inputs/`, which
only the user edits, or on a survey while agents are working on it. To check without writing: `mdformat --check docs`.

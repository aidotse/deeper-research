# Experiments: scripts that are not part of a pass

These scripts test ideas about the method. No pass runs them, no gate reads their reports, and no agent needs them for
its job. This file is for human reviewers; agents skip it. What a pass does is in `docs/process.md`, and the scripts it
runs are in `docs/tooling.md`.

Each writes a report to `graphs/<topic>/`, which is committed, so that the evidence behind a proposal stays reviewable.

## Recursive clustering

`uv run tools/recursive.py <topic>` clusters recursively instead of at one global level: each cluster of the global
clustering is split on its own until no split passes, under several stopping rules (`--rules`, see its docstring),
including a shakedown that redoes each split decision on disturbed data. It compares each result with the global method
by rerunning both from scratch on time holdouts and resamples. It reads `clusters.json` and writes
`graphs/<topic>/recursive.json`; it takes about five minutes on 200 papers.

## Matching across simulated passes

`uv run tools/match.py simulate <topic>` treats the pool as it stood 3, 6 and 9 months ago as earlier passes, reruns the
full clustering method on each, and matches it to today's clustering by shared members. It writes
`graphs/<topic>/match-simulation.json`. The module's `match()` function is also what `tools/cluster.py` uses, in a pass,
to match a new clustering to the previous one.

## Since when each cluster exists

`uv run tools/match.py history <topic>` asks whether each cluster has existed for a while or only just formed. A pass
used to run this after every clustering. It was taken out of the pass because nothing depended on it and its results
were mostly hedged (audit of 2026-10-09, `Z5`). It writes `graphs/<topic>/history.json`.

The method:

1. `Snapshots` — divide the pool by publication date into four segments with the same number of papers each. A burst of
   publications then gets narrower segments. Each snapshot is the pool as it stood at the end of a segment, so it
   includes everything earlier.
2. `Cluster and match` — cluster each snapshot with today's measure and number of clusters, at five seeds, and match it
   to today's clusters by shared papers. A cluster is found in a snapshot if a majority of seeds find it.
3. `First seen` — the earliest snapshot from which a cluster is found in every later one. The result is one date per
   cluster, not one for the whole map, which the newest cluster would always drag to "today".

Where a cluster is not found, the report says why, from how many of its papers the snapshot already had. Fewer than 10
is a lack of data, not a change in the field: "too few papers". More means its papers existed but were grouped
differently, which is a real change. No papers are discarded to equalise snapshot sizes. A snapshot whose own stability
is below `τ` is itself unreliable, so what it finds is hedged: "probably since …".

Read the result with one caveat. Snapshots are drawn from today's pool, whose older papers are the ones still relevant
enough to be found and cited today. The history is therefore optimistic: a real earlier pass would have looked messier.

## Fringe routes

`uv run tools/fringe.py analyse <topic>` is the experiment behind the fringe routes: it reclusters with the screened
candidates added, and reports per route how they behave. Its report is `graphs/<topic>/fringe-analysis.json`.

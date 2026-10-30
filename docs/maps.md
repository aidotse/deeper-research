# Survey maps

Each survey in this repository has an interactive map: its papers as nodes, coloured by cluster and sized by how often
the other papers cite them, with the citations between them as edges. The map can also lay the papers out as tiles or on
a timeline, show the citation communities next to the survey's own clusters, and show how the clusters were computed.
[Tooling](tooling.md#graph-viewer) describes everything the viewer shows.

Each map opens in a new tab:

- [Model collapse](graphs/model-collapse.html){target="\_blank"}: a pass in progress. Its pool is built but not yet
    clustered, so the map shows the citation graph and its communities only.
- [Test-time compute and reasoning in LLMs](graphs/reasoning-legacy.html){target="\_blank"}: the legacy survey, built
    before the coreset method.

These pages are rebuilt from the repository's data each time the site is published, so they show the surveys as of the
latest release.

## Build a map yourself

A map is one self-contained HTML file, which opens straight from disk with no server and no network. To build one from a
clone of the repository:

```bash
uv sync
uv run python -m deeper_research.graph <topic>    # writes graphs/<topic>/graph.html
```

Then open `graphs/<topic>/graph.html` in a browser. `<topic>` is the name of a survey in `surveys/`, such as
`model-collapse`. `uv run poe graphs` builds every topic's map at once.

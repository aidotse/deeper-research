# deeper-research

[![CI](https://github.com/aidotse/deeper-research/actions/workflows/ci.yml/badge.svg)](https://github.com/aidotse/deeper-research/actions/workflows/ci.yml)
[![Tests](https://aidotse.github.io/deeper-research/exported/tests.svg)](https://aidotse.github.io/deeper-research/exported/pytest.html)
[![Coverage](https://aidotse.github.io/deeper-research/exported/coverage.svg)](https://aidotse.github.io/deeper-research/exported/coverage/)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/mit)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

A literature research agent harness: it builds trustworthy literature surveys with LLM agents, in
[Claude Code](https://code.claude.com/docs/en/overview). It does this in three moves:

- It gathers a broad, cheap pool of in-scope papers, starting from a user query.
- It computes a stable map of the pool's themes, from embeddings and shared references rather than the model's opinion.
- It picks a small coreset of papers per theme, each in a stated role (anchor, frontier, dissent, bridge, fringe), and
    checks each against the paper's body text with quotes recorded.

The value over commercial deep-research tools is about:

- Evidence: every claim traces to its source, the structure is reproducible, and the stopping rule is stated. The output
    does not try to prove a negative: it refuses to claim "nobody has done X", and does not read paper counts as field
    statistics.
- Coresets: a principled method for finding the papers that matter within the wider pool. A coreset, a concept from the
    active learning literature, is the smallest set of papers that answers the input's questions stably: adding more
    papers from the pool should not change the answers much, while taking one away should. Every paper in it is verified
    to publication grade. It is not a list of everything published, and that is what keeps the resulting map small
    enough to explore by hand. See
    [`docs/coresets.md`](https://github.com/aidotse/deeper-research/blob/main/docs/coresets.md).

## How it works

For a topic `<topic>`, the pipeline runs:

```text
inputs/<topic>.md  ->  surveys/<topic>.md  ->  outputs/<topic>.md, plus bib/<topic>.bib
```

You write the input: the topic, its context and seed papers, and what you want the survey to answer
([`docs/formats.md`](https://github.com/aidotse/deeper-research/blob/main/docs/formats.md)). The main Claude Code
session and its subagents produce the rest, running the scripts of the `deeper_research` package for every step that can
be computed rather than judged. The steps of a pass are in
[`docs/process.md`](https://github.com/aidotse/deeper-research/blob/main/docs/process.md), and `CLAUDE.md` is the
agents' entry point to the docs.

## Getting started

You need [uv](https://docs.astral.sh/uv/), [Claude Code](https://code.claude.com/docs/en/overview), and an API key for
[Asta](https://allenai.org/asta), the Allen Institute's scientific-literature MCP server.

```bash
uv sync                                        # create .venv with the package and its dev tools
uv run pre-commit install                      # git hooks, including the Conventional Commits check
claude mcp add --transport http asta https://asta-tools.allen.ai/mcp/v1 --header "x-api-key: $ASTA_API_KEY"
uv run python -m deeper_research.preflight     # check the outside services the scripts call
```

Then write `inputs/<topic>.md` and ask Claude Code, in this repository, to run a pass for `<topic>`. How each outside
service is called, and what is sent to it, is in
[`docs/external_services.md`](https://github.com/aidotse/deeper-research/blob/main/docs/external_services.md).

## Development

The repo is built on the [PyMaxQ](https://github.com/aidotse/pymaxq) template. Tasks run through
[poethepoet](https://github.com/nat-n/poethepoet), and CI calls the same tasks:

```bash
uv run poe lint        # pre-commit over the whole repo: ruff, mypy, gitleaks, zizmor, mdformat, file hygiene
uv run poe test        # pytest with coverage
uv run poe test-all    # the test suite on every supported Python version, via nox
uv run poe docs        # build the documentation site
```

`main` is protected: work on a branch and write [Conventional Commits](https://www.conventionalcommits.org/), from which
releases and the changelog are cut. The full developer guide is
[`docs/user-guide.md`](https://github.com/aidotse/deeper-research/blob/main/docs/user-guide.md).

## Documentation

The documentation site is at <https://aidotse.github.io/deeper-research/>. Its
[Survey maps](https://aidotse.github.io/deeper-research/maps/) page has an interactive citation map of each survey, and
says how to build one locally: `uv run python -m deeper_research.graph <topic>` writes `graphs/<topic>/graph.html`.

## Authors

Mauricio Munoz | <mauricio.munoz@ai.se>

## License

[MIT License](https://opensource.org/license/mit)

______________________________________________________________________

Repo generated using [PyMaxQ](https://github.com/aidotse/pymaxq) 🚀

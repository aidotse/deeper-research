# Changelog

All notable changes to this project are documented in this file.

This file is managed by [Commitizen](https://commitizen-tools.github.io/commitizen/) and is updated automatically on
each `poe bump` (driven by [Conventional Commits](https://www.conventionalcommits.org/)). Do not edit it by hand.

## v0.1.0 (2026-10-30)

### BREAKING CHANGE

- `python3 tools/<mod>.py ...` is now
`uv run python -m deeper_research.<mod> ...`.

### Feat

- **docs**: publish every survey's map on the docs site
- scaffold the repo from the PyMaxQ template

### Fix

- delete local statusline
- **graph**: break ties in a community's cluster mix by cluster id
- **types**: reconcile the modules' annotations where they meet
- **expand**: import screen.Papers, which collect() uses since the WIP snapshot

### Refactor

- **cluster,match,recursive**: full type annotations and docstrings under strict lint
- **coverage,audit,fringe**: full type annotations and docstrings under strict lint
- **gates**: full type annotations and docstrings under strict lint
- **assign,expand,pool**: full type annotations and docstrings under strict lint
- **fulltext,bib,preflight,asta_config**: full type annotations and docstrings under strict lint
- **check,inputs,net,screen,graph,sheets**: full type annotations and docstrings under strict lint
- move tools/ into the deeper_research package

# R4: how much targeted reading misses

An experiment, not part of a pass (`.audits/2026-10-09/remediation-plan.md`, `R4`; results in `docs/experiments.md`).
Each of the 27 `abstract`-sourced rows of `reasoning-legacy` is verified against its full text,
`graphs/reasoning-legacy/fulltext/<id>.txt`, by up to three arms:

- `A` — a strong agent reading by the section reader (`uv run tools/fulltext.py show reasoning-legacy <id>`) and Grep;
- `B` — a cheap-model locator reads the whole paper and writes a map (`B/map-<id>.md`); a strong agent then reads only
  the places the map gives;
- `C` — the reference: the main session reads the whole paper, on 8 of the 27.

Inputs, the same for every arm: `drafts/<id>.md` (the row as drafted from the abstract) and `dims.md` (the dimension
definitions). Each arm writes `<arm>/<id>.md` in the form below.

## Result form

```text
# R4 arm <X>: <id>

## Cells

- `<cell>`: confirmed | corrected | uncheckable — <the value you would write> — "<verbatim quote from the full text>"
  (<section, or line number>)

## Limitations and conditions

- "<verbatim quote>" (<section, or line number>) — <what it limits: a result, its scope, an assumption it rests on>

## Other findings

- <anything a reader of the row should know that the draft leaves out or gets wrong; `none` if none>

## Reads

- <arm B only: the places read; under "beyond the map", any place the map did not point to, and why>
```

One bullet per cell, for every cell of the draft except `venue+year`. "Limitations and conditions" lists every
limitation the authors state, every condition a headline result depends on, and every assumption it rests on, that you
found; `none found` if none. Quotes are verbatim from the full text, at least six words.

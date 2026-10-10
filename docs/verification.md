# Verification and probes

## Verification

Every coreset row is verified when it is selected, before the output is written. The standard is **publication grade**:
a row is verified when every claim it makes is one we would be willing to assert in a publication of our own, citing
this paper, on the strength of what was retrieved.

The standard is claim-level. The point is not to collect a quote per cell, but to be able to stand behind each sentence.

### What "verify" means

Verify against the paper's full text, in `graphs/<topic>/fulltext/<id>.txt`. The main session fetches it for every row
before dispatching verification (`docs/process.md`, step 5); do not fetch papers yourself, since parallel fetches break
arXiv's request spacing. The text is the paper's own: arXiv's HTML rendering, the PDF where arXiv has no HTML, or, for a
paper without an arXiv ID, the open-access PDF Semantic Scholar lists. Every quote a verified row rests on comes from
this file, which is what lets `tools/check.py` confirm that each quote is verbatim. If the file is missing, the paper
could not be fetched, and the row is uncheckable ("Outcomes" below).

A whole paper is 10–70k tokens, so never Read it end to end. Read it by section, with the section reader (`R` below
stands for `uv run tools/fulltext.py show <topic> <id>`):

1. `R` alone prints the outline: every heading, with its size in tokens. Start here, to see where the method, the setup
   and the results are.
2. `R '<pattern>'` prints each passage matching a regular expression, under its section heading, with line numbers to
   read on from. Use it for the terms a claim turns on: a number, a dataset, the method's name.
3. `R --section <name>` prints whole sections by heading, such as `--section Method`. Read the sections where authors
   state what limits their result even when no one asks: `Limitations`, `Discussion` and `Conclusion`. A pattern only
   finds what you already suspect; these sections are where the caveats you did not suspect live.

Output is capped (`--max`, 6000 tokens by default). Grep on the file works too. In PDF text, words are often hyphenated
across line breaks, so search for word stems, and the "sections" are its pages and the lines that look like headings.

`Snippet search` can also help to find a passage: call `mcp__asta__snippet_search` with `paper_ids=ARXIV:<id>`, or
`paper_ids=CorpusId:<n>` for a paper without an arXiv ID, to learn where the claim is discussed, then find that passage
in the full text. A snippet is a pointer, not evidence. Quote the full text, never the snippet: nothing can check a
snippet afterwards, so a quote from one would be a claim presented as retrieved. Set `source` to `full-text`.

4. Read the outline's appendix headings too, and the appendix sections a result turns on: robustness checks, failure
   cases, ablations, the training or evaluation details a number depends on. Appendices are where a result's conditions
   most often live, and they are the part of a paper a targeted reading most often skips.

Read for what the draft row left out as carefully as for what it got wrong. This way of reading was measured against
reading whole papers: it found about 90% of what a whole reading found, at about 26k tokens per row, and most of what it
missed sat in appendices, hence step 4. Mapping the paper first with a cheaper model found less (about 84%) and cost
more, so it is not used (`docs/experiments.md`, "Reading a paper for verification").

Then check every cell:

- `method name` — the paper actually calls it that.
- `method summary` — what the paper does and how, including the assumptions or setup the result depends on.
- `datasets / models` — the actual evaluation setup, not models or datasets named in passing.
- `metric` and `result` — the headline number, its baseline and its comparison condition.
- every declared dimension — re-derived from the body text, **not** copied from the row's existing prose. Reading a
  classification out of an unverified summary and then marking it verified launders a guess into a fact.
- `role` and `selected because` — still true in the light of the body text. A paper selected as dissent that turns out
  to agree with its cluster is a selection error, not a characterisation detail. For a dissent row, find the claim
  `selected because` quotes in the full text, and record it as evidence for `selected because`. If the full text words
  it differently from the abstract, quote the full text's words in both places.

### Recording the evidence

Write down what each claim rests on, as you verify it, in `graphs/<topic>/evidence/<id>.md` (a slash or colon in the ID
becomes `_`, as for full texts). The sections you read are otherwise lost when your context ends, and a row nobody can
trace back to its text cannot be reviewed or audited. One bullet per piece of evidence:

```text
# Evidence: <id>

- `method summary` — full-text, 3 Method — "<the sentence that says what the paper does>"
- `result`, `evidence` — full-text, 4 Results — "<the sentence with the headline number> ... <its condition>"
```

- `cells` — the cells the quote supports, each in backticks. One quote may support several cells. Every cell whose value
  is not `n/a` needs evidence: `method name`, `method summary`, `datasets / models`, `metric`, `result`, and each
  dimension. A verified dissent row also needs its `selected because` claim.
- `source` — `full-text`, or `abstract` for a number the authors state only in the abstract (see below), then, after a
  comma, where in the paper: the section heading or the `[page N]` marker of the full-text file.
- `quote` — verbatim, in double quotes. Elide with `...`, never paraphrase. Each part between elisions has at least 6
  words, so that it shows where the claim comes from: "achieves 92.1% on GSM8K" is too short, so quote more of its
  sentence. The parts must appear in the paper in the order given, each within about a page of the one before. A
  sentence or two is enough; this is a pointer for a reviewer, not a copy of the paper.

The file opens with `# Evidence: <id>`, the row's own ID. The `method summary` must rest on a full-text quote, since the
abstract can carry a number but never the method.

`tools/check.py` requires the file for every row not `abstract`-sourced, and finds every `full-text` quote in the
fetched full text, ignoring case, punctuation and line breaks, with words hyphenated across a line break joined
(`docs/gates.md`, `G4`). A quote it cannot find there is a paraphrase, which is a claim presented as retrieved. Evidence
marked `snippet` fails. A correction replaces the evidence it corrects.

Four rules decide the edge cases:

- **A cell may be less informative, but never unsupported.** If the paper's numbers appear only inside figure images,
  which no text source contains, the cell says so and reports only what the text supports, such as the direction of an
  effect. That row is verified. A cell asserting a number nobody retrieved is not.
- **The abstract is the paper's own text.** A number the authors state only in the abstract may be reported, marked
  `[abstract-only]` in its cell. The abstract alone is never enough for the method, the setup, or the conditions of the
  result.
- **Author-stated limitations travel with the claim.** If the authors restrict their result to one model family, one
  domain or a synthetic setting, the row says so.
- **Asta returning nothing is evidence about the index, not about the paper.**

### Outcomes

Each row ends in exactly one of three states:

- **Verified** — every cell checked against the full text, with the evidence recorded; set `source` to `full-text`. A
  row drafted from the abstract is rewritten freely as it is verified: correcting a draft is what verification is for,
  so it is not logged as a correction.
- **Corrected** — a row that was already verified, in this pass or an earlier one, turns out wrong in a cell. Fix the
  cell in place, replace the evidence it rested on, and log the old and new text under `Corrections to existing rows`.
  Corrections of verified rows are never silent.
- **Uncheckable** — no full text could be fetched: for an arXiv paper, neither HTML nor PDF; for any other, no
  open-access PDF that `tools/fulltext.py` can fetch. Snippets alone do not verify a row. Leave `source` as `abstract`,
  end its `selected because` with `(uncheckable: <why>)`, and list it under "Rows needing verification" in Open work,
  with the reason. Do not look for a replacement yourself: report the row, and the main session dispatches Selection to
  look for a verifiable paper in its role (`docs/process.md`, step 5). The row stays only if none is found, or if it is
  a `fringe` row, which by definition no other paper can replace. The output marks every claim resting on it
  `[abstract-only]` (`docs/formats.md`). Re-check on a later pass, since open-access copies appear over time. This
  should be rare for arXiv papers, and is common for papers without one. If more than 20% of rows end here, the pass
  halts (`H10` in `docs/process.md`, "When a pass ends").

`source` ratchets upward. It is never lowered to express doubt; doubt belongs in the row's text and in the log.

**Verifying the whole coreset** is this operation applied to every row of the coreset. It is safe to run at any time:
verified rows are cheap to re-check and cannot be made worse, and the operation is resumable. Dispatch it in disjoint
cluster blocks. Expect roughly 10k tokens per row. That figure comes from earlier passes that verified from snippets;
reading from the full text has not yet been measured.

## Probes

A probe answers "does work on X exist?". It is the only route by which an output may say that something is absent, and
it is **run on demand, not by default**. The user asks for one, or an output proposes one as an unrepresented connection
and the user asks for it to be run. Probing every cluster as a matter of routine spends effort on questions nobody
asked.

A probe is adversarial: its goal is to find the work that would refute "X does not exist". It searches the whole index,
not just the pool:

- several independent phrasings of X, including the vocabulary of neighbouring fields;
- forward citations of the coreset papers closest to X;
- WebSearch, for work that never reached arXiv;
- date restrictions, so that very recent work is not drowned out.

Record in the log what the probe searched and what it found. Report the result as either "found: <papers>", which enter
the coreset in a role, or "survived a refutation attempt: <what was searched>". Never report absence more strongly than
the search that tested it. A paper a probe finds is a late paper: add it to the pool with `tools/assign.py add`; it
takes a role only once `tools/assign.py late` has assigned it a cluster (`docs/process.md`, "Late papers").

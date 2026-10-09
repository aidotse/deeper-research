# Verification and probes

## Verification

Every coreset row is verified when it is selected, before the output is written. The standard is **publication grade**:
a row is verified when every claim it makes is one we would be willing to assert in a publication of our own, citing
this paper, on the strength of what was retrieved.

The standard is claim-level. The point is not to collect a quote per cell, but to be able to stand behind each sentence.

### What "verify" means

Verify against the paper's full text. Fetch it with `uv run tools/fulltext.py <topic> <id>` (see `docs/tooling.md`). The
script costs no tokens, and its text is the paper's own: arXiv's HTML rendering, the PDF where arXiv has no HTML, or,
for a paper without an arXiv ID, the open-access PDF Semantic Scholar lists. Every quote a verified row rests on comes
from this file, which is what lets `tools/check.py` confirm that each quote is verbatim.

A whole paper is 10–70k tokens, so do not read it end to end. Find the passages each claim turns on, and read only
those. There are two ways to find them, and either or both may be used:

- `Grep` — search the file for the terms the claim turns on. Words in PDF text are often hyphenated across line breaks,
  so search for word stems.
- `Snippet search` — call `mcp__asta__snippet_search` with `paper_ids=ARXIV:<id>`, or `paper_ids=CorpusId:<n>` for a
  paper without an arXiv ID, to learn where the claim is discussed. Then find that passage in the full text with Grep.

A snippet is a pointer, not evidence. Quote the full text, never the snippet: nothing can check a snippet afterwards, so
a quote from one would be a claim presented as retrieved. Set `source` to `full-text`.

Then check every cell:

- `method name` — the paper actually calls it that.
- `method summary` — what the paper does and how, including the assumptions or setup the result depends on.
- `datasets / models` — the actual evaluation setup, not models or datasets named in passing.
- `metric` and `result` — the headline number, its baseline and its comparison condition.
- every declared dimension — re-derived from the body text, **not** copied from the row's existing prose. Reading a
  classification out of an unverified summary and then marking it verified launders a guess into a fact.
- `role` and `selected because` — still true in the light of the body text. A paper selected as dissent that turns out
  to agree with its cluster is a selection error, not a characterisation detail.

### Recording the evidence

Write down what each claim rests on, as you verify it, in `graphs/<topic>/evidence/<id>.md` (a slash or colon in the ID
becomes `_`, as for full texts). The sections you read are otherwise lost when your context ends, and a row nobody can
trace back to its text cannot be reviewed or audited. One bullet per piece of evidence:

```text
# Evidence: <id>

- `method summary` — full-text, 3 Method — "<the sentence that says what the paper does>"
- `result`, `evidence` — full-text, 4 Results — "<the sentence with the headline number> ... <its condition>"
```

- `cells` — the cells the quote supports, each in backticks. Every verified row needs at least `method summary`,
  `result`, and each declared dimension whose value is not `n/a`.
- `source` — `full-text`, or `abstract` for a number the authors state only in the abstract (see below), then, after a
  comma, where in the paper: the section heading or the `[page N]` marker of the full-text file.
- `quote` — verbatim, in double quotes. Elide with `...`, never paraphrase. A sentence or two is enough; this is a
  pointer for a reviewer, not a copy of the paper.

`tools/check.py` requires the file for every row not `abstract`-sourced, and finds every `full-text` quote in the
fetched full text, ignoring punctuation and line breaks (`docs/gates.md`, `G4`). A quote it cannot find there is a
paraphrase, which is a claim presented as retrieved. Evidence marked `snippet` fails. A correction replaces the evidence
it corrects.

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

**Outcomes.** Each row ends in exactly one of three states:

- **Confirmed** — set `source` to `full-text`, with the evidence recorded.
- **Corrected** — fix the cell in place, set `source`, and log the old and new text in the current pass's entry.
  Corrections are never silent.
- **Uncheckable** — no full text can be fetched: for an arXiv paper, neither HTML nor PDF; for any other, no open-access
  PDF that `tools/fulltext.py` can fetch. Snippets alone do not verify a row. Leave `source` as `abstract` and say so in
  the row. Such a row may stay in the coreset only if no verifiable paper can fill its role, and it is listed under
  "Rows needing verification" in Open work. The output marks every claim resting on it `[abstract-only]`
  (`docs/formats.md`). Re-check on a later pass, since open-access copies appear over time. This should be rare for
  arXiv papers. It is common for papers without one; a `fringe` row of that kind will usually stay, because by
  definition no other paper carries its idea. If more than 20% of rows end here, the pass halts (`H10` in
  `docs/process.md`, "When a pass ends").

`source` ratchets upward. It is never lowered to express doubt; doubt belongs in the row's text and in the log.

**Verifying the whole coreset** is this operation applied to every row of the coreset. It is safe to run at any time:
verified rows are cheap to re-check and cannot be made worse, and the operation is resumable. Dispatch it in disjoint
cluster blocks. Expect roughly 10k tokens per row.

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

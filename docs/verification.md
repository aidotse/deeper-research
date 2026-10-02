# Verification and probes

## Verification

Every coreset row is verified when it is selected, before the output is written. The standard is **publication grade**:
a row is verified when every claim it makes is one we would be willing to assert in a publication of our own, citing
this paper, on the strength of what was retrieved.

The standard is claim-level. The point is not to collect a snippet per cell, but to be able to stand behind each
sentence.

### What "verify" means

Call `mcp__asta__snippet_search` with `paper_ids=ARXIV:<id>`, typically twice: once for the method and once for the
headline result. Add further queries wherever a claim in the row is still unsupported.

Fall back to the paper's full text in two cases: when snippet search returns no body text for the paper, and when a
claim rests on a table or a figure caption, which snippets exclude. Fetch it with
`uv run tools/fulltext.py <topic> <id>` (see `docs/tooling.md`), then search the file with Grep for the terms the claim
turns on, and read only the matching sections. A whole paper is 10–70k tokens, so do not read it end to end. Quote what
you rely on, and set `source` to `full-text`.

Then check every cell:

- `method name` — the paper actually calls it that.
- `method summary` — what the paper does and how, including the assumptions or setup the result depends on.
- `datasets / models` — the actual evaluation setup, not models or datasets named in passing.
- `metric` and `result` — the headline number, its baseline and its comparison condition.
- every declared dimension — re-derived from the body text, **not** copied from the row's existing prose. Reading a
  classification out of an unverified summary and then marking it verified launders a guess into a fact.
- `role` and `selected because` — still true in the light of the body text. A paper selected as dissent that turns out
  to agree with its cluster is a selection error, not a characterisation detail.

Four rules decide the edge cases:

- **A cell may be less informative, but never unsupported.** If the paper's numbers appear only inside figure images,
  which no text source contains, the cell says so and reports only what the text supports, such as the direction of an
  effect. That row is verified. A cell asserting a number nobody retrieved is not.
- **The abstract is the paper's own text.** A number the authors state only in the abstract may be reported, marked as
  coming from the abstract. The abstract alone is never enough for the method, the setup, or the conditions of the
  result.
- **Author-stated limitations travel with the claim.** If the authors restrict their result to one model family, one
  domain or a synthetic setting, the row says so.
- **Asta returning nothing is evidence about the index, not about the paper.**

**Outcomes.** Each row ends in exactly one of three states:

- **Confirmed** — set `source` to `snippet` or `full-text`.
- **Corrected** — fix the cell in place, set `source`, and log the old and new text in the current pass's entry.
  Corrections are never silent.
- **Uncheckable** — no body text is available: snippet search returns none, and arXiv has neither HTML nor PDF. Leave
  `source` as `abstract` and say so in the row. Such a row may stay in the coreset only if no verifiable paper can fill
  its role, and it is listed under "Rows needing verification" in Open work. Indexing lags publication, so re-check on a
  later pass. Since `tools/fulltext.py` exists, this should be rare for arXiv papers.

`source` ratchets upward. It is never lowered to express doubt; doubt belongs in the row's text and in the log.

**Verifying the whole coreset** is this operation applied to every row. It is safe to run at any time: verified rows are
cheap to re-check and cannot be made worse, and the operation is resumable. Dispatch it in disjoint cluster blocks.
Expect roughly 10k tokens per row.

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
the search that tested it.

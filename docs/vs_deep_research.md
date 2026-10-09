# How this harness differs from Deep Research

For information only, not instructions.

Frontier chat assistants offer "Deep Research" modes, which also search the literature and write a cited report, and it
is natural to ask what this repo does that they do not. The short answer: Deep Research answers a question, while this
harness builds a verified, reusable map of a literature and answers questions from that map. Most of the differences
below follow from that.

A caveat first. Deep Research products are known here only from their public descriptions. Their internals are not
documented, and they change often. Read the comparison as typical behaviour, not as a specification of any one product.

## Where the approaches differ

- `What the product is` — Deep Research produces a report in one run, and the next question starts over. This harness
  produces a persistent survey: a pool of papers, computed clusters, verified coreset rows and a retrieval log. Outputs
  are views over the survey and can be regenerated. A later pass extends the survey rather than redoing it. See
  `docs/formats.md`.
- `How papers are chosen` — Deep Research follows relevance: whatever the search engine ranks highly for the query. That
  favours consensus and well-publicised work. This harness selects for coverage. Clusters are computed first, and each
  is filled in roles; dissenting and overlooked (`fringe`) papers are searched for deliberately, because ranking does
  not surface them. See `docs/coresets.md`.
- `What counts as verified` — Deep Research cites sources, but a citation shows where a claim came from, not that the
  source supports it. Here every coreset row is checked against the paper's body text. Each claim records whether it
  came from the abstract, a snippet or the full text, and anything unchecked is marked `[abstract-only]` in the output.
  See `docs/verification.md`.
- `When it stops` — Deep Research stops on a time or search budget. This harness stops on a measured test: when sampled
  papers left out of the coreset no longer change the output. See `docs/process.md`, step 7.
- `Where it searches` — Deep Research searches the web. This harness combines web search with a scholarly index,
  Semantic Scholar's citation graph, embeddings and full-text snippets. That is what makes citation traversal, stable
  clustering and body-text verification possible. See `docs/external_services.md`.
- `What it refuses to claim` — this harness never claims that something does not exist without a targeted probe, and
  never reads field statistics off the coreset, because the coreset is selected for coverage, not in proportion to the
  literature. Deep Research reports do not typically draw these lines.
- `Who steers` — here the user steers the clustering through the input, and reviews the computed clusters in an
  interactive viewer: before the expensive stage if they ask for it, or if the clustering signals a misread topic, and
  otherwise with the output, where requested changes are applied incrementally. Deep Research typically asks a few
  clarifying questions at the start, then runs unattended.
- `Auditability` — the retrieval log records every query, the clustering parameters and the stability figures that chose
  them, every correction and every user override. A result can be traced and rerun. A Deep Research run cannot be
  inspected in the same way.

## Where Deep Research is the better tool

It is far faster and cheaper: minutes, against an estimated one to one and a half million tokens and several hours for a
pass here. It is also broader across non-academic sources. For a one-off question, or a topic you will not return to, it
is the right choice.

## Using both

The two complement each other rather than compete. A Deep Research report fits naturally into this harness's first step,
orientation, which surfaces the current frontier and the field's vocabulary. It can be listed as an item in an input's
`Context`. It is then treated like any web source: the papers it names enter the pool, and nothing from it is cited
until the paper behind it has been verified.

This harness earns its cost when three things hold:

- the topic will be revisited over months;
- the claims have to be publication grade;
- the goal is to find under-explored directions, not to summarise the consensus.

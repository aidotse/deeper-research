# Audit 2026-10-05: spec, agent files and tools

Scope: every file in `docs/`, `CLAUDE.md`, `.claude/agents/*.md`, `.claude/settings.json`, and all of `tools/` (for
`tools/recursive.py`, the docstring only). Claims were checked against the code, against the data in
`graphs/reasoning/`, and against the live Asta tool schemas. `CLAUDE-old.md` is out of scope: it is a superseded first
draft.

Nothing was changed during the audit. This file is the action plan. Each issue has an ID, the evidence, why it matters,
a suggested remediation, its dependencies, and a rough effort (`S`, `M`, `L`). The plan at the end orders the work.

Status labels: `verified` means checked against code or data in this audit. `likely` means strong but not tested
directly; the remediation says how to confirm it.

## What was checked and holds

So that a new session does not redo this work:

- Every figure in `docs/roadmap.md` "Findings" reproduces from `graphs/reasoning/*.json`. That covers:
  - grid means 0.722 / 0.671 / 0.646;
  - τ sensitivity 12 / 6 / 5 clusters;
  - AMI 0.54;
  - the six cluster sizes and stabilities;
  - the history cutoffs and snapshot stabilities 0.40 / 0.72 / 0.84;
  - the simulation ARIs;
  - 3,772 distinct and 7,760 total references;
  - 146 fringe candidates, 118 in scope.
- The stability tests, the null model, the measure tie rule, the level rule, the `When stability fails` thresholds, the
  fringe score definition and the cluster history all match `docs/process.md`.
- The viewer features listed in `docs/tooling.md` exist in `tools/graph_template.html`: the similarity map with seeded
  layout, the level slider, the date histogram filter, the URL hash, and "Since when".
- The Asta parameters in `docs/external_services.md` match the live schemas: default limits of 50 and 100, snippets of
  about 500 words without captions or bibliography, up to 100 `paper_ids`, `publication_date_range`, `inserted_before`,
  and `fields` defaulting to `title`.
- `bib.py` and `fulltext.py` behave as documented: 3-second spacing, retries, verbatim text, and caching.

## Decisions (resolved with the user, 2026-10-05)

These are recorded under "Decisions taken" in `docs/roadmap.md`. They are not spec until they are written into the files
each one names.

- `D1 — late papers: queue them, then assign or recluster in batches`.

  - Late papers are any that reach the pool after step 3: coverage-test candidates, probe hits, papers an output needs
    for a new claim, and papers found by an expansion that a "new cluster" judgement triggered.
  - They go into a queue, a new Open work field `Late papers awaiting assignment`, not straight into a cluster.
  - The queue is processed in batches: once per coverage-test round, and before any re-run of step 4. A batch costs one
    `tools/pool.py` fetch, followed by one of two actions:
    - Default: assign each paper to its nearest cluster by the chosen measure, by script. Assign against the clustering
      as it stood, never against other queued papers, so that the result does not depend on order. Log every assignment.
    - Recluster instead, by rerunning `tools/cluster.py`, in two cases: when the coverage test judged that a candidate
      belongs to a cluster not in the table, or when late additions since the last full clustering exceed 10% of the
      pool. The 10% is a first guess.
  - A "new cluster" judgement never creates a cluster directly. It triggers a targeted expansion of that region (the
    `More data` lever). The expansion's in-scope papers join the same batch, and the batch is then reclustered. If the
    region is real, it forms a cluster. If not, the computation places its papers in existing clusters, and the data has
    overruled the judgement.
  - Recursion is bounded. Expansions run before their batch is processed, so a round has at most one recluster. Across
    rounds, two coverage rounds without convergence halt the pass (`H11` in S11).
  - Why batches and a threshold: the stability test shows the clusters survive losing 20% of the papers, so a few late
    papers rarely move them. A large addition can, though. Adding the 118 fringe candidates on `reasoning` moved the
    base clustering to ARI 0.70.
  - Dependency: a mid-pass recluster needs cross-pass matching to carry names and verified rows over (S4). Interim: run
    `match()` from `tools/match.py` by hand, and log its output.
  - Goes into: `docs/process.md` (a new "Late papers" subsection, referenced from steps 4–7 and from the probe section),
    `docs/formats.md` (the Open work field and a log line), and T3.

- `D2 — every paper can enter the pool, and so the coreset`.

  - Pre-2015 arXiv IDs (`NNNN.NNNN` and `archive/NNNNNNN`) are supported everywhere (C4).
  - Papers without an arXiv ID are allowed in the pool. Since the coreset is a subset of the pool, they can enter the
    coreset too.
  - `Canonical ID` — the arXiv ID where one exists; otherwise `CorpusId:<n>`, Semantic Scholar's numeric ID, which both
    Asta and the Graph API accept. Not the DOI: many papers lack one, and its characters are awkward in tables.
  - `Link` — the arXiv page; otherwise a DOI or Semantic Scholar page. The Semantic Scholar URL form for a `CorpusId` is
    `UNVERIFIED`; check it before building.
  - `Bib` — Graph API metadata for papers without an arXiv ID.
  - `Verification` — `snippet_search` with `CorpusId:`. For full text, the paper's open-access PDF link from the Graph
    API, where there is one. Otherwise the row is uncheckable. One consequence: an uncheckable `fringe` row will usually
    stay, because by definition no other paper carries its idea. It is marked `[abstract-only]` (D5).
  - `Duplicates` — a preprint and its venue version can be two Semantic Scholar records. `tools/check.py` flags pool
    rows with near-identical titles. The user's rule: keep the arXiv record, and merge the other into it. Its venue goes
    into `venue+year`. The merge is logged under `Corrections to existing rows`. It is not a deletion, so it needs no
    permission.
  - Papers not in Semantic Scholar at all still cannot enter (the roadmap's discovery-lag item). Record them in Open
    work.
  - Goes into: every tool (T6); `docs/formats.md` (the `paper` column and ID rules); `docs/verification.md`;
    `docs/external_services.md`, where "resolve to an arXiv ID" becomes "resolve to an arXiv ID or a `CorpusId`"; and
    `docs/tooling.md`.

- `D3 — every error halts the pass, and all end conditions live in one list`.

  - Every failed preflight check halts the pass, including arXiv, `uv` and a missing Asta key. The reason: no failure
    may lead to a silent fallback that compromises the quality or repeatability of a pass. Halting at preflight is also
    cheaper than discovering an arXiv or `uv` failure at step 5.
  - One exception: a Graph API 429 still counts as reachable. It means "busy", the scripts retry, and no other method
    takes over.
  - The rule continues after preflight. Errored queries are retried at the end of their step, and any that still fail
    halt the pass. A script that fails after its own retries halts it too.
  - A subagent that halts returns a `STOP:` report to the main session (A3). The main session tells the user, who
    decides whether to proceed. Proceeding is logged, and the output's legend says what was missing.
  - All finish and halt conditions go into one canonical list with stable IDs (S11), and other docs point to it.

- `D4 — the input declares dimensions in a parseable form`, for example:

  ```text
  - **`evidence`** — values: `proven`, `derived`, `empirical`, `fitted`, `position`
  ```

  `tools/check.py` and `tools/graph.py` read the dimensions from the input instead of hardcoding them (C3, T4).

- `D5 — three markers, each with one job`.

  - `UNVERIFIED` — in replies, reports and docs: a claim not checked against any retrieved text.
  - `source` — per survey row: what the row was verified against.
  - `[abstract-only]` — in outputs, on any claim that rests on an `abstract`-sourced row. Inside a row, on a cell value
    taken from the abstract alone. `outputs/reasoning.md` already uses this marker.
  - `[abstract-only]` replaces "provisional" in this sense. The docs also use "provisional" for the provisional
    clustering in step 2 and for provisionally adopted dimensions, so it is ambiguous.
  - Every output opens with a short legend explaining the marker, as `outputs/reasoning.md` does in "How to read
    provenance".
  - `tools/check.py` turns its current note into a failure: an `abstract`-sourced paper cited in the output on a line
    without the marker.
  - Goes into: `CLAUDE.md` (one line), `docs/verification.md`, `docs/formats.md`, `docs/external_services.md:192`,
    `docs/tooling.md:29`, `docs/vs_deep_research.md:25` and `tools/check.py:282`.

- `D6 — the term "targets"`, defined where it is introduced.

  - Definition: the targets are the parts of an output that the coreset must stay stable against. Adding pool papers
    should not change what the output says about them, and removing a coreset paper should. By default they are
    `Landscape`, `Assumptions` and `Gaps`. An input's `Coreset Spec` may add more, such as specific research questions.
    `Questions` and `Reading` are derived from the targets, so they are not targets themselves.
  - Why it needs a fixed name: the coverage test, the stopping rule, asks whether a candidate "would change a claim in
    one of the targets". The agent running it must know exactly which output changes count. Counting a reading-list
    change, for example, could stop the test from ever converging.
  - Goes into: the `Coreset Spec` entry in `docs/formats.md`, with a pointer to `docs/coresets.md` for the reasoning. It
    replaces "attributes" (`formats.md:14`) and "coreset spec dimensions" (`formats.md:200`). The uses in
    `docs/coresets.md` and step 7 of `docs/process.md` stay, and point to the definition.

## Issues

### C — the docs and the code disagree

- `C1 — the printed Clustering log line does not match the template` (`verified`, effort S)

  - Evidence: `tools/cluster.py:523-526` prints `grid mean stability`, with no `by rule`, `τ=`, null-model level or
    `diagnostics:` field. The template in `docs/formats.md:73-77` has all of these and says `grid mean ARI`.
  - Why it matters: `docs/tooling.md` presents the printout as the log line. An agent that pastes it writes a log line
    that does not conform.
  - Remediation: make `cluster.py` print the exact template, including the τ ± 0.05 levels and the diagnostics. Rename
    the template's `grid mean ARI` to `grid mean stability` to match the code.

- `C2 — check.py does not report in-degree leaders before anchors are chosen` (`verified`, effort S)

  - Evidence: the step-4 row of `docs/process.md:55` says `tools/check.py` "reports each cluster's leader". In fact
    `tools/check.py:223-230` reports the leader only when an anchor already exists and differs from it.
  - Remediation: always print each cluster's in-degree leader or leaders. Alternatively, put the leaders in the naming
    brief (T2).

- `C3 — dimensions are hardcoded to the reasoning topic` (`verified`, effort M, depends on D4)

  - Evidence: `tools/check.py:37-42` (`DIMS`) and `tools/graph.py:49` (`DIMENSIONS`).
  - Why it matters: on a new topic, its dimensions go unchecked and get no colour mode in the viewer. A reused name with
    different values fails the check.
  - Remediation: parse the dimensions from `inputs/<topic>.md` (see T4).

- `C4 — the arXiv ID regex misses pre-2015 IDs` (`verified`, effort S, D2)

  - Evidence: `tools/check.py:29` matches only `\d{4}\.\d{5}`, while `tools/fulltext.py:42` accepts 4 or 5 digits.
    Missed examples: `1412.6980` (Adam), and `1106.1379`, which `docs/coresets.md` itself cites.
  - Why it matters: `pool.py`, `graph.parse` and therefore `cluster.py` drop such rows silently. `check.py` fails loudly
    only for coreset rows.
  - Remediation: define one shared regex in `check.py` that covers `NNNN.NNNN(N)` and the old `archive/NNNNNNN` form,
    and import it in every tool. Also check `BARE_ARXIV`, `bib.py`'s ID extraction and `graph.arxiv_month`.

- `C5 — scripts lose a whole run on failure, and retry only on 429` (`verified`, effort S)

  - Evidence: `pool.py`, `graph.py` and `fringe.py` write their cache only after the last batch, and retry only on HTTP
    `429`. `docs/external_services.md:111` says "the scripts cache what they have already fetched".
  - Remediation: write the cache after every batch. Retry on 5xx responses and on `URLError` or timeouts as well.

- `C6 — the citation retrieval date is wrong for older rows` (`verified`, effort S)

  - Evidence: `tools/pool.py:121` overwrites `fetched` on every run that fetches anything, while older records keep
    their old counts. `pool.py:133` then prints "citations as of <fetched>".
  - A related gap: `docs/formats.md` (Pool, `citations`) says the date is "in the log", but the log template has no
    field for it.
  - Remediation: store a `fetched` date per record. Add the date range to the log's `Pool` line (see S8).

- `C7 — settings.json pre-approval is probably ignored` (`likely`, effort S)

  - Evidence: `.claude/settings.json:2` has `"allow"` at the top level. Claude Code reads permission rules from
    `permissions.allow`; compare `.claude/settings.local.json`.
  - Remediation: move the rule under `"permissions": {"allow": [...]}`. Confirm with `/permissions` in a session.

- `C8 — the ASTA_API_KEY check tests the wrong thing` (`verified` for shell semantics, effort S)

  - Evidence: in the `claude mcp add` command (`docs/external_services.md:37`), the shell expands `$ASTA_API_KEY` when
    the server is added. Whether Asta has a key therefore depends on the stored MCP config, not on the environment
    variable in later sessions.
  - A second problem: the preflight row (`external_services.md:172`) relies on the session-start warning. That warning
    goes to the main session, but the preflight runs in a subagent, which cannot see it.
  - Remediation: check the MCP config instead, for example `claude mcp get asta`, without printing the key. Or have the
    main session pass the result to the preflight agent. Rewrite the hook's message to match.

- `C9 — cluster.py behaviour the spec does not mention` (`verified`, effort S)

  - Evidence:
    - The grid is trimmed to at most n/4 clusters (`tools/cluster.py:387`).
    - A holdout cutoff is dropped if it keeps under 30% of the pool (`MIN_HOLDOUT_SHARE`, `:48`).
    - "Internally divided" means two or more sub-clusters scoring at least 0.6 (`SUBCLUSTER_SCORE`, `:450`).
    - `THIN_REFS` = 10 sets the reported reference share.
    - Clusters under 3 papers get no clusterwise score (`:334`).
  - Why it matters: a 2-paper cluster can never be diagnosed as `thin cluster`, because the diagnostics only consider
    clusters that have a score.
  - Remediation: document these in `docs/process.md` ("Clustering method", "When stability fails", "Sizing"). Add
    `SUBCLUSTER_SCORE`, `THIN_REFS` and `MIN_HOLDOUT_SHARE` to the roadmap's list of first guesses. Diagnose clusters
    under 3 papers as `thin` explicitly.

- `C10 — small inaccuracies` (`verified`, effort S)

  - `docs/external_services.md` says every Asta tool returns only `title` unless `fields` asks for more. In fact
    `snippet_search` has no `fields` parameter.
  - `docs/roadmap.md` says RL "first appears in the pool of 2025-10-09". The data hedges it as "probably", because that
    snapshot's stability was 0.72.
  - `mdformat --check` fails on `docs/verification.md`, whose line 58 is unwrapped. Run `mdformat .`.

### M — a method bug

- `M1 — the fringe score rewards missing reference data` (`verified` on data, effort S, then rerun)

  - Evidence: `tools/cluster.py:279-300`. A paper with no resolved references has zero `refs` similarity to everything,
    so it ranks near the top of its age cohort on the reference half of the score.
  - On `reasoning`, 5 of the top 8 fringe scores belong to papers with 0 references. Papers with fewer than 10
    references have a median score of 0.75, against 0.45 for the rest.
  - The `combined` measure already guards against this with `w = n/(n+c)`; the fringe score does not.
  - Remediation: weight the two halves per paper the same way: `w * refs_rank + (1 - w) * text_rank`, with `w` from the
    paper's own reference count. Alternatively, use text only below `THIN_REFS`. Then rerun on `reasoning`, and update
    the roadmap's fringe findings and the "highest fringe scores" sentence.

### S — inconsistencies and gaps in the spec

- `S1 — the preflight rules contradict each other` (effort S, depends on D3)

  - Evidence: `docs/process.md:74-75` says that if any part of any service is unavailable, stop. The table in
    `docs/external_services.md:162-172` says to proceed for the Graph API, arXiv, `uv` and the key.
  - A further gap: the `uv` row says `uv` is needed before the first `cluster.py` or `fulltext.py` run. In fact
    `cluster.py` already runs in step 2 (provisional clustering), and `fringe.py` needs `uv` too.
  - Remediation: superseded by D3. Every failed check halts the pass; `process.md` step 0 points to `H1` in S11, and the
    preflight table's "if it fails" column becomes "halt" throughout. Fix the `uv` row as well.

- `S2 — no procedure maps computed cluster ids to named ids` (effort M, the tool is T3)

  - The spec never tells the naming agent how the `c1…cN` ids from `clusters.json` become kebab-case ids. It also never
    says who fills the Pool `cluster` column, or how the `Temporal stability` line's ids get replaced (`match.log_line`
    says "the agent replaces computed ids", but only in its docstring).
  - Consequence: from step 1 to step 3, `check.py` fails (unknown pool `cluster`, no Coreset, no bib). Yet
    `docs/dispatch.md:31` says to run it after every subagent.
  - Remediation: record the mapping in one place, for example a `computed` column in the Clusters table, or a
    `cluster_names` map in `clusters.json`. A script fills the Pool column from it (T3). Document this in step 3 of
    `process.md`, under "Recording it".

- `S3 — papers that arrive after step 3 have no cluster` (effort M, depends on D1)

  - Evidence: the coverage test in `docs/process.md` (step 7) adds papers and can declare a "new cluster";
    `docs/verification.md` (Probes) sends found papers into the coreset; `docs/formats.md` (outputs) adds papers to the
    coreset for new claims. None of these says how the new paper gets a cluster, while every other rule forbids
    assigning one by hand.
  - Remediation: write the D1 procedure (queue, batches, nearest-cluster assignment or recluster) into `process.md`, as
    a short "Late papers" subsection that steps 4–7 and the probe section all point to.

- `S4 — incremental passes depend on matching, which is not built` (effort S for the docs; the tool belongs to the
  roadmap item)

  - Evidence: "Changing the clusters after a pass" (`docs/process.md`) re-runs step 4 "for the clusters that changed".
    Telling which clusters changed after a recluster needs cross-pass matching, which is not built.
  - Remediation: until matching is built, say so in that section, with an interim rule. One option: use
    `tools/match.py`'s `match()` by hand on the two assignments, and log its output. Note in the roadmap that matching
    is needed for incremental passes too, not only for second passes.

- `S5 — papers without an arXiv ID` (effort S for the docs, M for the tools; depends on D2)

  - Evidence: `docs/tooling.md:33` mentions only the coreset, but `check.py` also fails on pool rows without an arXiv
    link. 11 of 118 in-scope fringe candidates on `reasoning` have no arXiv ID, 6 of them from `hidden`. Open work has
    no field to record them.
  - Remediation: apply D2 (T6). Papers not in Semantic Scholar at all go into a new Open work field.

- `S6 — three uncertainty markers, and provenance tracked per row instead of per claim` (effort S, depends on D5)

  - Evidence: `CLAUDE.md` uses `UNVERIFIED` and asks every claim to carry its provenance. `docs/verification.md:39-40`
    says an abstract-only number is "marked", without saying how. The `source` column holds one value per row.
  - Remediation: write the D5 scheme into every place D5 lists.

- `S7 — the Coreset Spec section is muddled` (effort S, depends on D6)

  - Evidence:
    - `docs/formats.md:14-16`: an "(optional)" section that "by default must include" three items.
    - "Attributes", "targets" (`coresets.md`) and "coreset spec dimensions" (`formats.md:200`) all name the same thing.
      The last one collides with `Dimensions`.
    - "Ask which are wanted" does not say who asks whom, or when.
    - The output format never says the output must contain `Landscape`, `Assumptions` and `Gaps` sections. Only
      `Questions` and `Reading` are listed as required.
  - Remediation: write "If omitted, the targets are `Landscape`, `Assumptions` and `Gaps`; an input may add more." Use
    `targets` everywhere. In the outputs section, require one section per target, plus `Questions` and `Reading`. Say
    that the main session asks the user, at planning time.

- `S8 — the retrieval log template is missing fields the spec requires` (effort S)

  - Missing:
    - fringe collection and screening: candidates per route, in scope, added to the pool, excluded for lacking an arXiv
      ID;
    - demotions (required by "Rules for re-runs");
    - probes: what was searched and what was found (required by `docs/verification.md`);
    - the citation retrieval date (C6);
    - the τ ± 0.05 levels (C1);
    - provisionally adopted dimensions (`formats.md`, `Dimensions`);
    - preflight failures the user chose to proceed past;
    - per-step tokens (roadmap).
  - Also: `docs/external_services.md:78` refers to `Queries run`, which is not a field. Either add it, or point to the
    `Orientation` and `Expansion` fields.
  - Remediation: extend the template in `docs/formats.md`, then update `cluster.py`'s printout (C1) to match.

- `S9 — smaller inconsistencies` (effort S)

  - "Stage" means the two pipeline stages in `docs/dispatch.md`, but the three process stages in `docs/process.md`.
    Rename one of them, for example "pipeline halves" or "phases".
  - The `exclude` steering is listed under "steering for step 3" in `docs/formats.md`, but it applies at screening, in
    step 2.
  - `docs/formats.md:148-149` calls `graph.html` part of the survey's record, but `.gitignore` excludes it, and "Both"
    follows a list of three items. Say that `pool.json` and `clusters.json` are the record, and the viewer is rebuilt
    from them.
  - `CLAUDE.md:53` says a proposal becomes spec when moved "into file in `docs/`", but `docs/roadmap.md` is itself in
    `docs/`. Say "into one of the spec files in the index table".
  - Step 3 lists naming before steering. `granularity` steering has to apply before naming.
  - Typos:
    - "This subsection section" (`formats.md:51`)
    - "to them comparable" (`formats.md:181`)
    - "feasiblity" and "the search work" (`formats.md:201`)
    - `outputs/<topic.md>` (`formats.md:50`, `coresets.md:71`)

- `S10 — check.py misses things the spec requires` (effort S)

  - Not checked:
    - `medium` clusters with no anchor or frontier, and `low` clusters with no anchor (only `high` is noted);
    - Coreset blocks in the same order as the Clusters table;
    - every cluster having a block;
    - a bridge for each pair of clusters that trade papers (would need `clusters.json`);
    - required column names, including `selected because`;
    - a bridge pointing to its own cluster.
  - Remediation: add these as notes or failures, inside the stage-aware check (T1).

- `S11 — the end conditions are scattered, overloaded and incomplete` (effort S, from D3)

  - Evidence: the conditions are spread over four files: `docs/process.md` (step 0, step 3's "When stability fails" and
    "Cluster review", step 7, and "Rules for re-runs"), `docs/formats.md` (`Clustering`) and `docs/external_services.md`
    (Preflight). "Stop" means both the successful end of a pass ("Stop when a round produces no new cluster…") and a
    halt. Several failures have no stop at all.

  - Remediation: add a section "When a pass ends" to `docs/process.md`, holding the list below. Every local mention
    elsewhere points to its ID. The log's `Stopped because` line becomes
    `Ended: finished (F1) | halted (<id>), <the measured numbers>`.

  - Draft list. Entries marked "new" are missing from the docs today.

    - `Finish` — the pass has done its job.
      - `F1` — the coverage test converges: a round with no new cluster and at most one output change (step 7).
    - `Halt` — the subagent returns a `STOP:` report, and the main session tells the user and waits. The user's decision
      is logged.
      - Services and scripts:
        - `H1` — a preflight check fails (step 0). A Graph API 429 counts as reachable.
        - `H2` — a query still errors after the end-of-step retry. New.
        - `H3` — a script fails after its own retries: `pool.py`, `fringe.py`, `cluster.py`, `bib.py` or `fulltext.py`.
          New.
      - Clustering, at step 3. The user reviews in the viewer, and the pass resumes from their decision:
        - `H4` — `no structure`.
        - `H5` — `no stable level`, still, after a targeted expansion and rerun.
        - `H6` — a cluster cannot be rated for alignment from the input.
        - `H7` — a cluster the input expects (`expect`) is still missing after a targeted expansion.
        - `H8` — the pool is too small to cluster: fewer than 12 papers. `cluster.py` keeps only levels of at most n/4
          clusters, and the smallest level is 3, so the grid is empty and the script would fail (read from
          `cluster.py:387`, not run). New.
      - Integrity and verification:
        - `H9` — `tools/check.py` fails, and the agent that caused it cannot fix it. New.
        - `H10` — after step 5, more than 20% of coreset rows are still `abstract`-sourced. The 20% is a first guess;
          `reasoning` is at 14%. New.
      - Convergence:
        - `H11` — two coverage-test rounds without convergence (step 7).
      - Permission:
        - `H12` — removing a paper from the pool (the deletion rule).
      - Requested by the user:
        - `H13` — `review: before coreset` in the input's `Clustering` section.
    - `Not end conditions` — listed so that nobody halts on them: `broad scope`; `thin cluster` (expand and rerun);
      `unstable cluster`; clusters that trade papers; an empty dissent slot; a single uncheckable row; a pass that runs
      over or under its cost estimate.

### W — how the docs are wired

- `W1 — the index is incomplete` (effort S). The `CLAUDE.md` index has no row for `docs/vs_deep_research.md` (add it as
  "humans only, not instructions"). It also lists `docs/responses.md` nowhere, though that file is imported.
- `W2 — dead cross-references` (effort S). `"Sources by job"` in `docs/coresets.md:74` and `docs/external_services.md:5`
  points to a heading that no longer exists; it is now "Overview" in `docs/process.md`. `Queries run` is covered in S8.
- `W3 — process.md never points to dispatch.md` (effort S). The "by" column of the order-of-operations table does not
  say who runs each script: the main session or the subagent. Add a "run by" convention and a pointer to
  `docs/dispatch.md`.
- `W4 — known gaps live only in the main-session roadmap` (effort S). Subagents never read `docs/roadmap.md`, so they
  meet the tool gaps unprepared. Add a one-line "Interim:" note in the spec wherever a gap bites (S2, S3, S4, S5).
  Remove each note when its gap closes.
- `W5 — the agent file's reading list contradicts the index` (effort S). `.claude/agents/survey-pass.md:16-18` says to
  read `verification.md` before starting. The index says to read it only before verifying or probing. Make the agent
  file defer to the index's "when to read" column.

### A — making the docs work as agent instructions

The docs explain why very well. They are weaker on who does what, with which inputs, and when a step is done.

- `A1 — responsibilities are written in the passive voice` (effort M). Examples: "Each pass records its clustering",
  "Record whether the pass stopped". Give each step in `docs/process.md` an owner, its inputs, its output artifact, and
  a done-criterion. Extending the order-of-operations table with "inputs", "writes" and "done when" columns may be
  enough.
- `A2 — no dispatch briefs` (effort M). Nothing says what the main session hands each `survey-pass` job, or what that
  job returns. Add a short brief per job type to `docs/dispatch.md`: preflight, orient, expand and screen, fringe
  screening, naming, per-cluster selection, fringe selection, verification, coverage test, probe. One conflict to
  resolve on the way: `survey-pass.md:27` asks for "the numbers the retrieval log needs", while `:38-39` says not to
  compute tallies. Say that numbers come from script output (`check.py`, `cluster.py`), never from hand counts.
- `A3 — subagents cannot tell the user` (effort S). Rewrite every "stop and tell the user" that a subagent may reach as
  "return a report that starts with `STOP:` and the reason". The main session then tells the user. This affects
  `process.md` step 0, `external_services.md` (Preflight) and step 3's review triggers.
- `A4 — large files with no warning` (effort S). `graphs/<topic>/pool.json` (1.6 MB), `fringe.json` (1.3 MB) and
  `clusters.json` (152 KB) should carry a "never Read whole; use the script's printout or `jq`" rule in
  `docs/tooling.md` and in the `survey-pass` agent file. Naming (step 3) and fringe selection need compact sheets
  instead (T2).
- `A5 — some work cannot be split by cluster` (effort S). `docs/dispatch.md:26-28` splits work by cluster. Fringe
  selection is relative to the whole coreset, bridges span two clusters, and the coverage test reads the whole output.
  State that these run once, serially, after the per-cluster work.
- `A6 — survey-edit's scope` (effort S). `survey-edit` has Asta tools it never needs; remove them. Its description
  allows "moving rows between blocks", which brushes against "membership is never changed by hand". Say that it moves
  rows only to match the computed assignment.
- `A7 — a one-screen pass checklist` (effort S, after A1). For each step: the command or dispatch, the artifact written,
  and the check that confirms it. This could open `docs/process.md`, or sit in `docs/dispatch.md`.

### T — tool work this plan needs

- `T1 — a stage-aware check.py` (effort M). `--stage pool|coreset|output`, so it is useful from step 1. The `pool` stage
  checks the Pool table, the sidecar and the cluster mapping. The `coreset` stage adds roles and the bib. The `output`
  stage adds the cross-reference to the output. It also absorbs S10.

- `T2 — compact sheets for naming and fringe selection` (effort S). For example `cluster.py --brief`, or a
  `naming-sheet.md` written alongside `clusters.json`. Per cluster: size, stability, in-degree leaders with titles,
  sub-clusters, and diagnostics. A fringe sheet lists the top fringe scores with their reference counts.

- `T3 — a pool writer` (effort M, depends on D1 and D2). One script to:

  - add the in-scope screened fringe candidates to the Pool table, with their links (D2);
  - write the computed cluster ids into the Pool `cluster` column, through the name mapping (S2);
  - process the late-paper queue in batches, by the D1 rule.

  This closes three roadmap tool gaps at once.

- `T4 — an input parser and checker` (effort M, depends on D4). It reads `Dimensions` with their allowed values, and
  validates the `Clustering` fields (known keys, allowed values such as `review: before coreset`). `check.py` and
  `graph.py` import it. This also covers the roadmap item "check.py reads no input file at all".

- `T5 — a preflight script` (effort S). `tools/preflight.sh` runs the non-agent checks: Graph API, arXiv API and HTML,
  `uv`, and the Asta config (C8). It prints the matching part of the `Preflight` log line. This is an existing roadmap
  gap.

- `T6 — support papers without an arXiv ID` (effort L, from D2). Introduce the canonical ID (arXiv ID, else
  `CorpusId:<n>`) in one shared module and use it in every tool:

  - `check.py` — the ID regexes, the output cross-reference, the duplicate-title check;
  - `pool.py` and `fringe.py` — fetch by either ID;
  - `bib.py` — Graph API metadata for papers without an arXiv ID;
  - `fulltext.py` — the open-access PDF fallback;
  - `graph.py` — the timeline date from `pool.json` instead of the arXiv ID.

  Do C4 first; it is the same change in miniature.

## Action plan

Each phase leaves the repo consistent, so the work can stop between phases. When an item changes the spec, also record
it under "Decisions taken" in `docs/roadmap.md`, as `CLAUDE.md` requires.

1. `Phase 0 — decisions`. Done on 2026-10-05; see "Decisions" above and `docs/roadmap.md`.

2. `Phase 1 — doc-only fixes` (one session). Start with S11, the list of end conditions, since S1 and A3 point to it.
   Then S1, S6, S7, S9, W1, W2, W3, W5, A3, A5, A6, C10, and the documentation half of C9. These are low-risk edits, and
   they remove most of the confusion a fresh agent would hit.

   Done on 2026-10-08. Notes for later phases:

   - S11 is `docs/process.md`, "When a pass ends", with the IDs as drafted. The log's `Stopped because` line became
     `Halts` (each halt and the user's decision) and `Ended`. The `Halts` line also covers S8's "preflight failures the
     user chose to proceed past".
   - `H9` carries an interim note: `check.py` fails by design before step 4, so only its other failures count until T1
     makes it stage-aware. Remove the note with T1.
   - W3 chose a convention: the main session runs the order-of-operations scripts between dispatches and hands their
     printout on; a subagent runs only the scripts its own job needs (`fulltext.py`, `check.py`). A2's briefs should
     build on this.
   - C8, partly: the key check now relies on the main session saying in the dispatch brief whether the session-start
     warning appeared. The `$ASTA_API_KEY` expansion problem remains for Phase 2.
   - C5, docs only: `external_services.md` no longer claims the scripts cache partial runs. It carries an "Interim" note
     instead; remove it when C5 is fixed.
   - D5's code half is still open: `check.py`'s note now asks for an `[abstract-only]` marker, but it is still a note,
     not the per-line failure D5 asks for. Do it in Phase 2.
   - The A2 conflict about numbers in reports is resolved in `survey-pass.md`: numbers come from script or tool output,
     never from the agent's own counting.
   - Not done here, by design: C1's template rename (with S8 in Phase 2), C2's doc row (with the code fix), and the
     Interim notes of W4 for S2–S5 (Phases 3 and 4).

3. `Phase 2 — small code fixes` (one session). C7 (settings), C1 (log line, together with the S8 template), C4 (regex),
   C5 (caching and retries), C6 (per-record dates), C2, C8. Then M1, followed by a rerun of `tools/cluster.py reasoning`
   and an update of the roadmap's fringe findings. Run `python3 tools/check.py reasoning` and `mdformat --check .` at
   the end.

   Done on 2026-10-08. Notes for later phases:

   - C4: one `ARXIV_ID` in `tools/check.py`, imported everywhere (`ID`, `ARXIV`, `BARE_ARXIV`, `EPRINT`; `bib.py`'s Atom
     parsing; `fulltext.py`; `graph.arxiv_month`). Tested live: Semantic Scholar and the arXiv API resolve
     `hep-th/9901001` and `1412.6980`. Semantic Scholar does not resolve the subject-class form `math.GT/0309136`, only
     `math/0309136`, so the pattern accepts only the canonical form, and a non-canonical link fails loudly.
   - C5: `tools/net.py` is the shared retry (429, 5xx, connection errors, timeouts) for `pool.py`, `graph.py`,
     `fringe.py`, `bib.py` and `fulltext.py`. `pool.py` and `graph.py` save after every batch. `fringe.py collect` still
     keeps no cache (documented); a failed run is rerun whole.
   - C6: `pool.json` records carry their own `fetched` date; the file-level date is migrated into each record on the
     next run. `pool.py` prints the log's `Pool` line with the date range; `clusters.json`'s `pool_fetched` is now a
     list of dates.
   - C7: done. Confirm with `/permissions` in a new session that `mcp__asta__*` shows as allowed.
   - C8: `tools/asta_config.py` reads the effective Asta MCP entry (local, then project, then user scope) and reports
     whether an `x-api-key` header is set, never printing it. The session hook and the preflight row use it. Verified on
     this machine: user scope, key set.
   - C1 with S8: `cluster.py` prints the `Clustering` line in the template's exact form, including the `τ ± 0.05` levels
     and the diagnostics with an `<action taken>` placeholder. The template also gained `Fringe`, `Dimensions`,
     `Demotions`, `Probes` and `Tokens` lines, and the `Pool` line its dates. A later `check.py` could flag a log line
     still holding a `<...>` placeholder.
   - C2: `check.py` prints each cluster's in-degree leaders every run. Found on the way: `cluster.py`'s `top` list
     ranked papers by citation degree (citing plus cited), not in-degree; fixed.
   - D5's code half: `check.py` fails on an `abstract`-sourced citation in the output not directly followed by
     `[abstract-only]`, and on a missing legend. `outputs/reasoning.md` had three such passages (nine citations); the
     markers were added, with no change to any claim.
   - Also: the scripts' User-Agent says `deeper-research`, after the repo's rename.
   - M1: done, with the per-paper weight. The rerun reproduced the clustering exactly (same assignment, grid means,
     level, stabilities, diagnostics and history). The fix was right in mechanism but M1 overstated its effect: the top
     8 fringe scores are the same set, and 5 of them still have no resolved references, because those papers are far by
     text too (all have abstracts, so a title-only embedding is ruled out). What moved were textually ordinary papers
     without references, out of the middle of the ranking. Details in the roadmap's Findings.

4. `Phase 3 — tools for the fresh run` (two sessions). T1, T2, T3, T4, T5, C3, S10, then T6. Document each tool in
   `docs/tooling.md` as it lands, and remove the matching "Interim:" note (W4) and roadmap gap.

   Done on 2026-10-08, in one session. The coreset-layout paths were tested on a temporary topic built from
   `reasoning`'s data (all 195 papers, its clustering, a 21-row coreset, a short output), then deleted. Notes:

   - T4 and C3: `tools/inputs.py` reads `Dimensions` (the D4 form) and `Clustering` (`` - `field`: value ``), and fails
     on unknown sections, fields and values. `inputs/reasoning.md` gained a `values:` lead per dimension; its prose is
     unchanged, and the parsed sets equal the old hardcoded ones. `check.py`, `graph.py` and `cluster.py` read it.
   - T1 and S10: `check.py --stage pool|coreset|output`, inferred when omitted. `H9`'s interim note is gone. Beyond
     S10's list, it now fails when a coreset row sits in a block other than the cluster its paper was computed into.
     Each new check was tested by breaking the fixture (eight faults, all caught).
   - S2 and T3: the mapping is a `computed` column in the Clusters table. `tools/assign.py` has `add`, `add-fringe`,
     `clusters`, `late` and `remap`; nothing in the Pool table is written by hand any more.
   - D1, an implementation choice: the late-paper queue is the Pool rows with an empty `cluster` cell, listed by
     `check.py`, not a separate Open work field, so that it has one source. Assignment is a similarity-weighted vote of
     the `k` nearest clustered papers under the chosen measure, falling back to text when a paper shares nothing under
     `refs`. On 15 papers held out of the fixture's clustering, it matched the full clustering 15 of 15 times
     (optimistic: those papers had shaped that clustering). Above 10% late, it refuses and exits 3.
   - S4: `cluster.py` matches each new clustering to the previous one, and `assign.py remap` carries names over. Tested
     by swapping two computed ids before a recluster: remap restored them. `assign.py clusters` and `check.py` refuse a
     new clustering until it is remapped, since otherwise old names would land silently on new clusters.
   - Granularity: `cluster.py` applies the input's `granularity` itself, and `--level coarser|finer|N` overrides it.
   - T2: a separate `tools/sheets.py` rather than `cluster.py --brief`, so the sheets can be rewritten after naming
     without reclustering. On `reasoning`: about 2.8k and 0.8k tokens. They are gitignored.
   - T5: `tools/preflight.py` (Python, not shell), using `asta_config.py` for the key.
   - T6 and D2: the link form `https://api.semanticscholar.org/CorpusId:<n>` was checked: it redirects (301) to the
     paper's page. Tested end to end with three real fringe candidates without an arXiv ID (the 1965 automata and 1984
     dual-process papers among them): pool, citation graph, late assignment, coreset row, bib entry, output citation.
     Two findings:
     - A Semantic Scholar record can lack an arXiv ID that the paper has. `CorpusId:248562643` is the preprint record of
       `2205.03401`, whose arXiv ID sits on the separate NeurIPS record, and the titles differ. Its open-access PDF link
       points to arXiv, so `check.arxiv_of` reads it from there, and `check.py` fails on a `CorpusId` row with an arXiv
       ID.
     - Publishers' open-access links can serve a web page, not a PDF (the AMS link did), so `fulltext.py` accepts only a
       body that starts with `%PDF`. Rows it cannot fetch stay uncheckable.
   - Not done: `check.py` still does not check the log lines (kept as a roadmap tool gap).

   Verification after Phase 3 (2026-10-08). A fresh agent checked every tool claim in the docs against the code, and
   found 21 discrepancies; the tool docstrings were checked separately. Fixed, with the code bugs first:

   - `cluster.py` treated any existing `clusters.json` as the clustering the names refer to, including the provisional
     run of step 2. On a first pass this blocked `assign.py clusters` after naming, and `remap` would have moved names
     wrongly. Now a previous clustering is recorded only when the Clusters table has names, and unremapped reruns keep
     the named clustering as the baseline. Tested: two unnamed runs recorded nothing; after naming, a `--level 5` rerun
     then a default rerun kept the baseline, and all 195 papers kept their names after `remap`.
   - `--level N` rejected the cluster counts the viewer's slider shows, when a measure missed its target (`text` reached
     14 and 23 for 15 and 22); it now accepts either.
   - A pool under 12 embedded papers crashed `cluster.py` with a division by zero; it now prints `STOP: H8`.
   - `fulltext.py` crashed on a publisher's 403 for an open-access link, and exited 1 for papers with no full text,
     which read as `H3`. Now an unfetchable paper is a note with exit 0; only a failure of arXiv itself is an error.
   - `inputs.py` silently skipped a malformed dimension bullet; it now fails.
   - Papers without a SPECTER2 embedding could enter the pool but never be clustered, and stayed "late" for ever.
     `assign.py add` now refuses them, and `check.py` lists them for Open work instead.
   - `H3` is now defined precisely: a service error or a crash, not a script's own `STOP:`, a refusal that names the
     command to run first, or `assign.py late`'s `RECLUSTER:` (renamed from `STOP`, which collided with halts).
   - Doc fixes: the late-paper vote is similarity-weighted; the `Clustering` template shows steering and `--level`; the
     order of operations gained `remap` and the second `sheets.py` run; the Graph API caller list, the `uv` users, the
     exact retried 5xx codes, the preflight example, the fringe shortlist size, and several smaller points.
   - Stale docstrings in `assign.py`, `bib.py`, `match.py`, `inputs.py`, `check.py`, `cluster.py`, `fringe.py` and
     `pool.py`.

5. `Phase 4 — the agent-facing layer` (one session, after Phase 3, so that it describes the real tools). A1, A2, A4, A7,
   and S2–S5 written as procedures, including the D1 late-paper procedure and the D2 ID rules. Finish with a dry read:
   start a fresh agent with only `CLAUDE.md` and the index, ask it to plan a pass for a toy input, and compare its plan
   with the checklist.

   Done on 2026-10-09, in one session.

   - A1 and A7: the order-of-operations table in `docs/process.md` now has `run by` (the command, or the brief to
     dispatch with), `reads`, `writes` (down to the log lines) and `done when`, and is the pass checklist;
     `docs/dispatch.md` says to run a pass down it. Passive phrasings that hid an owner were rewritten.
   - A2: `docs/dispatch.md` has a prompt template and eleven briefs. New rules: the main session writes the log lines
     scripts print (except `Clustering` and `Temporal stability`, which the naming agent writes with names); parallel
     agents return their log and Open work lines under `Log:` and `Open work:` instead of editing shared sections;
     `tools/bib.py` runs before `tools/check.py` after any coreset change, since the check compares the two.
   - A4: "never Read a JSON file in `graphs/<topic>/`, or `graph.html`, whole" is in `docs/formats.md`,
     `docs/tooling.md` and both agent files, pointing to printouts, the sheets, and `jq` for one field.
   - Found on the way (raised by the user): no doc said what the files in `graphs/<topic>/` are, who writes and reads
     them, or which are committed; `docs/process.md` mentioned "the screening sheet" without naming it.
     `docs/formats.md` now ends with an inventory of `graphs/<topic>/`. Also found: step 1's frontier candidates had no
     persistent home (now in the pool and the `Orientation` line), and `tools/fringe.py collect` overwrote the screening
     judgements on a rerun (it now carries them over; the parser read back all 146 on `reasoning`).
   - Dry read: a fresh agent given only `CLAUDE.md` and a toy input (state-space models) planned a first pass. Its plan
     matched the checklist row for row. It raised 15 points; 14 were real gaps, all small, and fixed: preflight was
     still tied to the step 1 agent in `docs/external_services.md`; the survey skeleton's headings were unstated; how an
     input adds targets; who creates the coreset blocks; that selection drafts every cell (`tools/check.py` fails on an
     empty dimension); bridges only for trading pairs, with divided clusters handled by selection; sheet rewrites before
     fringe selection and the coverage test; a thin cluster that stays thin; log lines updated only during their pass;
     token figures from the usage each dispatch reports; `check.py`'s row count and remap rule; the "internally divided"
     rule in the sheet. The fifteenth (reading `formats.md`, `tooling.md` and `external_services.md` while planning) is
     what the index already prescribes.

6. Then continue with "Next steps" 3 and 4 of `docs/roadmap.md`: the fresh coreset run.

Recommended order of value, if time is short: S11 with S1, C7 and W2 (wrong instructions, minutes to fix); then M1 and
C4 (silent errors in the data); then S2 and S3 with T3 (needed before any real pass).

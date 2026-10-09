# Remediation check 2026-10-09: did we do what the audit of 2026-10-05 says was done?

Scope: every claim of completed work in `.audits/2026-10-05-docs-and-tools.md`, and in the commit messages that carried
it out. That covers the decisions D1–D6, the issues C, M, S, W, A and T, the "Done" notes under Phases 1–4 (including
the Phase 3 verification and the Phase 4 dry read), the follow-up on `tools/check.py` (its 40-row table and its ticked
todo), and commits `880af9a`, `0ceb621`, `901d5ca`, `f96f5de`, `8c9b6de` and `5a451bb`. Everything was judged against
the repo at `5a451bb`, with git history used only to settle what a claim meant, or to re-check a figure.

This is not a new audit. Problems seen in passing that no audit claim covers are listed in the appendix, unjudged, for
the blind audit.

Nothing in the repo was changed, apart from regenerating the two gitignored sheets in `graphs/reasoning/`.

## Method

1. Every remediation, note and commit claim was broken into single, checkable claims, below.
2. Each was checked against the current docs and code, read in full: every file in `docs/`, `CLAUDE.md`,
   `.claude/agents/*.md`, `.claude/settings.json`, every script in `tools/` except `recursive.py` and the viewer
   template (grepped for the palette), and `tests/gates/`.
3. Each replaced wording was searched for across the repo, to catch a rule changed in one file but still stated the old
   way in another: `Stopped because`, `grid mean ARI`, `coreset spec dimension`, `attributes`, `provisional`,
   `Sources by job`, `Queries run`, `--stage`, `preflight.sh`, `Late papers awaiting`, `stop and tell`, `tell the user`,
   `into file in`, the five typos of S9, `Interim`, `Decisions taken`, `resolve to an arXiv ID`, `stage`, `Stop when`,
   `proceed`. No stale use is left in the spec, the agent files or the tools. The hits in `surveys/reasoning.md` are
   earlier log entries, which are never rewritten.
4. What could be re-run was re-run (next section). Claims that rest only on fixtures deleted after use are marked
   `UNVERIFIED`; their code paths were read instead.

Verdicts: `done` — the repo does what the claim says. `done as amended` — done in another form, and the change is
recorded in the audit's notes, a commit message or the spec. `partial` — the gap is named. `not done` and `regressed` —
none found.

## Re-runs

| what | result |
| -- | -- |
| `python3 tools/check.py reasoning` | exit 0, `OK` |
| `python3 tools/inputs.py reasoning` | exit 0; 4 dimensions, targets `Landscape, Assumptions, Gaps` |
| `mdformat --check .` | exit 0 |
| `python3 tests/gates/faults.py` | 43 of 43 faults caught, exit 0; the tree was clean afterwards |
| `python3 tests/gates/behaviour.py` | 17 of 17 behaviours as expected, exit 0; the tree was clean afterwards |
| `python3 tools/preflight.py` | exit 0: Graph API ok, arXiv ok, uv ok, Asta key set |
| `python3 tools/asta_config.py` | user scope, `x-api-key` set |
| Semantic Scholar, live | `hep-th/9901001`, `1412.6980` and `math/0309136` resolve; `math.GT/0309136` does not |
| arXiv API, live | `hep-th/9901001` resolves |
| `https://api.semanticscholar.org/CorpusId:6628106` | 301 to the paper's page |
| `CorpusId:248562643`, live | no `ArXiv` in `externalIds`; open-access PDF `arxiv.org/pdf/2205.03401`; `check.arxiv_of` returns `2205.03401` |
| `clusters.json`, `65c94d5` against `HEAD` | assignment, measure, level, grid means, cluster stabilities, diagnostics and history identical; top 8 fringe scores the same set, 5 of them with 0 references; `top` lists reordered by in-degree |
| `pool.json` | 195 of 195 records carry `fetched`; no file-level date left |
| `fringe-screen.md` carry-over parser | reads back 146 of 146 judgements |
| `fringe.json` routes | `hidden` 60 + `new` 56 = 116, as `docs/external_services.md` says |
| `python3 tools/sheets.py reasoning` | 2,789 and 816 tokens ("about 2.8k and 0.8k") |
| `tools/inputs.py` on a scratch input, then deleted | a malformed bullet starting `- **` fails; one without bold is skipped silently (gap 3) |

## Summary

Of about 230 claims, all but the eleven below are `done` or `done as amended`. Nothing has regressed, and no stale
wording survives in the spec. The gaps, most consequential first:

01. `D1 and S3 — the late-paper procedure is not reached from where late papers arise` (`partial`). D1 asked for the
    "Late papers" subsection to be referenced from steps 4–7 and from the probe section. It is referenced from step 7
    (`docs/process.md:573-574`, and the checklist row at `:86`), "Cluster review" (`:465`) and "Changing the clusters"
    (`:613`). It is not referenced from step 6, nor from the outputs rule "add the paper to the coreset first, in a
    role" (`docs/formats.md:287-288`), nor from "Probes" (`docs/verification.md:106-107`, "found: <papers>, which enter
    the coreset in a role"). Those are two of the four routes by which a late paper arrives. The Probe brief does say
    "they are late papers" (`docs/dispatch.md:122`), and `g3.assigned` fails a coreset row for an unassigned paper, so
    the error is caught, but the instruction an agent reads at the point of action is missing.
02. `C9 — a cluster under 3 papers is not diagnosed as thin` (`partial`). The remediation said to diagnose such clusters
    as `thin` explicitly. `tools/cluster.py:350` still skips clusters without a score, so it never prints a diagnosis
    for them, and the naming sheet shows "none (fewer than 3 papers)". The spec chose another route: "the tool does not
    diagnose it. Treat it as thin" (`docs/process.md:442-443`). That may be a sound choice, but no note records it, and
    it leaves the call to an agent where the audit wanted a script.
03. `Phase 3 verification — "inputs.py silently skipped a malformed dimension bullet; it now fails"` (`partial`).
    `tools/inputs.py:80` fails only bullets that start with `- **`. On a scratch input,
    `` - `evidence` — values: `a`, `b` `` and `- evidence2 — values: …` were both dropped without a message,
    `dimensions: 0`. A dimension declared one backtick-pair off is silently unchecked and gets no colour mode: the
    failure C3 set out to remove.
04. `Follow-up row 39 — "no verified cell changed without a Corrections entry"` (`partial`). Todo item 4 says rows 37–39
    are done. `tools/gates.py:687-720` checks removed rows and a lowered `source`, not changed cells. `docs/gates.md`
    ("History") does not claim the cell check, so the spec is honest, but the audit's todo overstates it.
05. `Follow-up row 11 — Pool line against pool.json` (`partial`). `g1.pool-line` (`tools/gates.py:306-311`) checks the
    paper count only, not the fetch-date range the row names. `docs/gates.md:47` says "`Fringe` and `Pool` agree with
    the files", which reads as the whole line.
06. `Follow-up row 12 — a logged --level override` (`partial`). `g2.clustering-line` checks measure and level against
    `clusters.json`, not the `manual overrides` field. Not recorded as dropped.
07. `tools/assign.py late`'s docstring is stale (`partial`, Phase 3 verification: "stale docstrings in `assign.py`" and
    "the late-paper vote is similarity-weighted"). `tools/assign.py:28-29` still says "the cluster most common among its
    k nearest clustered papers". The code (`:283-290`) and every doc use the similarity-weighted vote.
08. `docs/tooling.md:241` — "`faults.py` injects one fault per gate requirement" (`partial`). `tools/gates.py` has 43
    requirements; `faults.py` covers 40 of them (43 faults, four of them for `g4.evidence`). `g0.entry`, `g3.assigned`
    and `g3.dimension-columns` have no fault of their own; `g3.assigned` fires only as a side effect of the `g2.written`
    fault.
09. `Counts in the audit file and a commit are stale` (`partial`, records only). Todo item 3 says 39 requirements, item
    6 "39 of 39" faults and "16 of 16" behaviours; commit `901d5ca` says 40 requirements, 43 faults and 17 behaviours.
    The code has 43 requirements, and the tests run 43 faults and 17 behaviours.
10. `docs/external_services.md:114-115` — the fringe shortlist sentence is garbled: "Only the shortlist, up to 60 per
    route (116 on `reasoning`), papers, is worth a model's attention" (Phase 3 verification, "the fringe shortlist
    size"). The figure is right; the sentence is not.
11. `C7 — live confirmation` (`UNVERIFIED`). `.claude/settings.json` now nests the rule under `permissions.allow`, which
    is the fix. The audit asked for confirmation with `/permissions` in a new session; the `/permissions` output in this
    session listed two unrelated approvals and did not show `mcp__asta__*`.

`UNVERIFIED`, because they rest on fixtures deleted after use and were not rebuilt (the code paths were read and match):
the 15-of-15 late-assignment holdout, still cited in `docs/tooling.md:105-107`; the remap swap test; Phase 3's eight
faults (superseded by `tests/gates/`); the end-to-end run with three papers without an arXiv ID; the AMS link serving a
web page; and the two-unnamed-runs and `--level 5` baseline tests of the Phase 3 verification.

## Fixes, made in the same session

Every gap above was fixed after this report was written, on the user's instruction. The inventory below records the
state as found.

01. `D1 and S3` — fixed. Step 4 (`docs/process.md`, "Step 4: select") says that only a paper with a cluster takes a
    role; step 6 says how a paper a claim needs enters, as a late paper; the outputs rule (`docs/formats.md`, outputs)
    and "Probes" (`docs/verification.md`) point to "Late papers", the latter naming `tools/assign.py add` and `late`.
02. `C9` — fixed in code, as the audit asked. `diagnose` in `tools/cluster.py` reports a cluster without a clusterwise
    score as `thin cluster` ("no stability score (fewer than 3 papers)"); `docs/process.md` ("When stability fails")
    says so. Tested by calling `diagnose` with a 2-paper cluster. `reasoning` has no cluster that small, so its
    committed `clusters.json` is unchanged and still valid.
03. `inputs.py` — fixed. Every top-level bullet in `Dimensions` must be a dimension in the D4 form, or the input fails;
    `docs/formats.md` (`Dimensions`) says so. Tested: both malformed bullets fail; prose, the bold form and nested
    bullets pass; `inputs/reasoning.md` passes.
04. `Row 39` — fixed. `history` in `tools/gates.py` fails a verified row (`snippet` or `full-text`) whose cells changed
    since the last commit without a `Corrections to existing rows` entry naming it; an `abstract` row stays free to
    rewrite. `docs/gates.md` ("History") and `docs/tooling.md` describe it. Three new behaviour tests.
05. `Row 11` — fixed. `g1.pool-line` also requires `metadata fetched <dates>` to match the fetch dates in `pool.json`.
    The fixture's `Pool` line now carries the real dates; a new fault.
06. `Row 12` — fixed. `g2.clustering-line` also requires the line's rule, with any steering or override, to be the one
    in `clusters.json`, and a `--level` override to be logged under `manual overrides`, and only then. A new fault.
07. `assign.py late` docstring — fixed.
08. `Faults per requirement` — fixed: new faults for `g0.entry`, `g3.assigned` and `g3.dimension-columns`, so every
    requirement has its own. `docs/tooling.md` now says "at least one fault per gate requirement". The `g0.entry` fault
    found a real bug: with no `### Pass` entry, `tools/check.py` crashed in `g1.rejected`, comparing a date with `None`,
    instead of reporting `g0.entry`. Fixed in `tools/gates.py` (`Ctx.date`).
09. `Counts` — on a closer look, "39 of 39 faults" and "16 of 16 behaviours" were right when written; item 8 added the
    four evidence faults and one behaviour. Only the requirement count was off. A dated correction was added to item 3
    of the audit file. Commit `901d5ca`'s message cannot be changed.
10. `docs/external_services.md` sentence — fixed.
11. `C7` — confirmed by the user: `/permissions` lists `mcp__asta__*` as allowed.

After the fixes: `python3 tests/gates/faults.py` 48 of 48; `python3 tests/gates/behaviour.py` 20 of 20;
`python3 tools/check.py reasoning` OK; `python3 tools/inputs.py reasoning` exit 0; `mdformat --check .` passes.

## Claim inventory

### Decisions

| # | claim | verdict | evidence |
| -- | -- | -- | -- |
| D1.1 | late papers defined: coverage-test candidates, probe finds, papers an output needs, targeted-expansion papers | done | `docs/process.md:469-470` |
| D1.2 | the queue is an Open work field `Late papers awaiting assignment` | done as amended | the Pool rows with an empty `cluster` cell, listed by `tools/check.py` (`docs/process.md:471-472`, `tools/check.py:358-361`); recorded in the Phase 3 note |
| D1.3 | batches once per coverage round and before any re-run of step 4 | done | `docs/process.md:474` |
| D1.4 | a batch costs one `tools/pool.py` fetch | done | `tools/assign.py:253` |
| D1.5 | nearest cluster by the chosen measure, against the clustering as it stood, every assignment logged | done as amended | similarity-weighted vote of the `k` nearest, text fallback (`tools/assign.py:273-292`); recorded in the Phase 3 note; `late` in `clusters.json` and the `Late papers` line |
| D1.6 | recluster on a new-cluster judgement or above 10% late | done | `docs/process.md:482-490`; `tools/assign.py:266-271` (`RECLUSTER:`, exit 3) |
| D1.7 | a new-cluster judgement only triggers a targeted expansion, then a recluster | done | `docs/process.md:487-490`; `docs/dispatch.md:83-85`, `:119-120` |
| D1.8 | at most one recluster per round; `H11` | done | `docs/process.md:496-497` |
| D1.9 | interim: `match()` by hand | done as amended | superseded: `tools/cluster.py:576-589` matches, `tools/assign.py remap` carries names |
| D1.10 | the subsection is referenced from steps 4–7 and the probe section | partial | gap 1 |
| D1.11 | `docs/formats.md`: a log line (and the Open work field) | done | `docs/formats.md:142-143`; field as amended (D1.2) |
| D2.1 | pre-2015 arXiv IDs supported everywhere | done | `tools/check.py:44`, imported by `graph.py`, `bib.py:60`, `fulltext.py`, `assign.py`, `pool.py`; live re-check |
| D2.2 | papers without an arXiv ID may enter pool and coreset | done | `docs/formats.md:85-106`; `tools/check.py:51` (`LINK`) |
| D2.3 | canonical ID: arXiv, else `CorpusId:<n>`, not the DOI | done | `docs/formats.md:87-93` |
| D2.4 | link form checked before building | done | `docs/formats.md:95-96`; 301 re-checked live |
| D2.5 | bib from Graph API metadata | done | `tools/bib.py:71-90`, `corpusid` field `:115` |
| D2.6 | verification: `snippet_search` with `CorpusId:`, open-access PDF, uncheckable fringe usually stays | done | `docs/verification.md:14-15`, `:76-83`; `tools/fulltext.py:180-197` |
| D2.7 | duplicates flagged; keep the arXiv record; merge logged; not a deletion | done | `tools/check.py:275-303`; `docs/formats.md:98-103`; `tools/gates.py:707` accepts a logged merge |
| D2.8 | papers not in Semantic Scholar recorded in Open work | done | `docs/formats.md:105-106`, `:235` |
| D2.9 | `docs/external_services.md`: "an arXiv ID or a `CorpusId`" | done | `docs/external_services.md:154-156` |
| D2.10 | every tool, and `docs/tooling.md` | done | T6 below; `docs/tooling.md:11-15`, `:85-88`, `:113-118`, `:127`, `:186-187`, `:198-199` |
| D3.1 | every failed preflight check halts, including arXiv, `uv` and the key | done | `docs/external_services.md:176-178`, `:195-205`; `tools/preflight.py:59-62` |
| D3.2 | a Graph API 429 counts as reachable | done | `docs/process.md:122`; `tools/preflight.py:44` |
| D3.3 | errored queries retried at the end of the step; still failing halts | done | `docs/external_services.md:83-88` (`H2`) |
| D3.4 | a script failing after its retries halts | done | `docs/process.md:125-128` (`H3`); `tools/net.py` |
| D3.5 | `STOP:` report; the main session tells the user; proceeding logged; legend says what was missing | done | `docs/process.md:104-112`; `docs/dispatch.md:55-56`; `docs/formats.md:151`, `:291-293` |
| D3.6 | one canonical list with stable IDs | done | S11 |
| D4 | dimensions declared in a parseable form, read by `check.py` and `graph.py` | done | `docs/formats.md:41-52`; `tools/inputs.py:28-29`; `tools/check.py:506`; `tools/graph.py:85-86`; caveat in gap 3 |
| D5.1 | `UNVERIFIED`, `source` and `[abstract-only]` each with one job | done | `CLAUDE.md:63-66` |
| D5.2 | `[abstract-only]` on a cell value from the abstract | done | `docs/verification.md:64-65` |
| D5.3 | `[abstract-only]` replaces "provisional" in this sense | done | wording sweep; the remaining "provisional" uses are the provisional clustering and dimensions |
| D5.4 | every output opens with a legend | done | `docs/formats.md:292-293`; `tools/check.py:474-476` |
| D5.5 | `check.py` fails an unmarked `abstract` citation | done | `tools/check.py:464-473`; `outputs/reasoning.md` passes |
| D5.6 | written into `CLAUDE.md`, `verification.md`, `formats.md`, `external_services.md:192`, `tooling.md:29`, `vs_deep_research.md:25`, `check.py:282` | done | the old lines now: `docs/external_services.md:207-208`, `docs/tooling.md:41-44` and `:59-60`, `docs/vs_deep_research.md:25` |
| D6 | "targets" defined in `Coreset Spec`, pointing to `coresets.md`; replaces "attributes" and "coreset spec dimensions" | done | `docs/formats.md:14-25`; `docs/coresets.md:15-18`; `docs/process.md:563-566`; neither old term left |

### Issues: C and M

| # | claim | verdict | evidence |
| -- | -- | -- | -- |
| C1 | `cluster.py` prints the exact template, with `τ ± 0.05` and diagnostics; template says `grid mean stability` | done | `tools/cluster.py:414-426`; `docs/formats.md:125-128` |
| C2 | in-degree leaders always printed | done | `tools/check.py:365-371`, `:396-398`, `:447`; `tests/gates` never exercises it, since the fixture's `cites` is empty (`tests/gates/build.py:89`) |
| C3 | dimensions parsed from the input, not hardcoded | done | `DIMS` and `DIMENSIONS` gone; `tools/check.py:506`, `tools/graph.py:86` |
| C4 | one shared regex for every arXiv form, imported everywhere | done | `tools/check.py:44`; `BARE_ID`, `BIB_ID`, `bib.py:60`, `graph.arxiv_month`, `fulltext.py:42` |
| C5 | cache after every batch; retry 5xx, connection errors, timeouts | done | `tools/net.py:16-40`; `tools/pool.py:126-134`; `tools/graph.py:160-197`; `fringe.py collect` has no cache, documented (`docs/external_services.md:125`) |
| C6 | per-record `fetched`; date range in the `Pool` line | done | `tools/pool.py:60`, `:66-68`, `:149`; `docs/formats.md:124`, `:211` |
| C7 | the rule under `permissions.allow` | done (file); live check `UNVERIFIED` | `.claude/settings.json:2-6`; gap 11 |
| C8 | check the stored MCP config, not the variable; hook message rewritten | done | `tools/asta_config.py`; `.claude/settings.json:8-17`; `docs/external_services.md:40-46` |
| C9.1 | document the n/4 trim, 30% holdout, 0.6 sub-cluster score, `THIN_REFS`, no score under 3 | done | `docs/process.md:301-302`, `:323`, `:336`, `:426`, `:536` |
| C9.2 | the three constants in the roadmap's first guesses | done | `docs/roadmap.md:270-274` |
| C9.3 | diagnose clusters under 3 papers as `thin` explicitly | partial | gap 2 |
| C10.1 | `snippet_search` has no `fields` | done | `docs/external_services.md:65-66` |
| C10.2 | RL "probably" first appears | done | written at `880af9a` (`docs/roadmap.md:231` then); the findings were later removed with the rest, by `5a451bb` |
| C10.3 | `mdformat --check` passes | done | re-run |
| M1.1 | fringe score weighted per paper by `w = n/(n+c)` | done | `tools/cluster.py:289-316`; `docs/process.md:363-376` |
| M1.2 | rerun on `reasoning`, findings updated | done | git comparison above; findings written at `880af9a` (`docs/roadmap.md:170` then), removed by `5a451bb` |

### Issues: S

| # | claim | verdict | evidence |
| -- | -- | -- | -- |
| S1 | every failed check halts; step 0 points to `H1`; the `uv` row fixed | done | `docs/process.md:172-178`; `docs/external_services.md:176-190` |
| S2 | the name mapping in one place; a script fills the Pool column; documented in step 3 | done | `docs/formats.md:174-178`; `tools/assign.py:225-245`; `docs/process.md:263`, `:400-403` |
| S2b | `check.py` usable before step 3 | done as amended | integrity checks apply to what exists, gates by progress (`tools/gates.py:726-768`); behaviour test "mid-pass" passes |
| S3 | the D1 procedure in a "Late papers" subsection that steps 4–7 and probes point to | partial | written (`docs/process.md:467-497`); pointers: gap 1 |
| S4 | interim rule for incremental passes; roadmap note | done as amended | matching built; `docs/process.md:612-615`, `:621-627`; roadmap item updated (`docs/roadmap.md:52-58`) |
| S5 | apply D2; an Open work field for papers not in Semantic Scholar | done | `docs/formats.md:235`; `docs/tooling.md:85-88` |
| S6 | the D5 scheme everywhere D5 lists | done | D5 |
| S7.1 | "If omitted, the targets are …; an input may add more" | done | `docs/formats.md:19-25` |
| S7.2 | `targets` everywhere | done | wording sweep |
| S7.3 | one output section per target, then `Questions` and `Reading` | done | `docs/formats.md:275-284`; `tools/check.py:479-483` |
| S7.4 | the main session asks the user, at planning time | done | `docs/formats.md:33-34` |
| S8 | the log template gains the eight missing fields; `Queries run` resolved | done | `docs/formats.md:116-153` (`Fringe`, `Demotions`, `Probes`, `Pool` dates, `τ ± 0.05`, `Dimensions`, `Halts`, `Tokens`); `docs/external_services.md:84-85` |
| S9.1 | "stage" disambiguated | done | `docs/dispatch.md:5-6` ("two halves"); `docs/process.md:23-33` |
| S9.2 | `exclude` applies at screening | done | `docs/formats.md:54`, `:63` |
| S9.3 | `pool.json` and `clusters.json` are the record; the viewer is rebuilt | done | `docs/formats.md:313`, `:319-321` |
| S9.4 | `CLAUDE.md`: "one of the spec files in the index table" | done | `CLAUDE.md:56` |
| S9.5 | `granularity` applies before naming | done | `docs/process.md:257-259` |
| S9.6 | five typos | done | none found by search |
| S10 | `check.py` checks roles by alignment, block order, a block per cluster, trading-pair bridges, required columns, self-bridges | done | `tools/check.py:193-195`, `:409-410`, `:425-426`; `g3.roles`, `g3.bridges` |
| S11.1 | "When a pass ends", `F1`, `H1`–`H13`, "Not end conditions" | done | `docs/process.md:98-170` |
| S11.2 | local mentions point to the IDs | done | `docs/process.md:60`, `:66`, `:81`, `:428`, `:575`, `:591`; `docs/external_services.md:86-87`, `:123-124`, `:176`; `docs/verification.md:82-83`; `docs/formats.md:62`, `:66` |
| S11.3 | `Stopped because` becomes `Ended` | done as amended | `Halts` and `Ended` (`docs/formats.md:151-153`); recorded in the Phase 1 note |

### Issues: W, A and T

| # | claim | verdict | evidence |
| -- | -- | -- | -- |
| W1 | index rows for `vs_deep_research.md` and `responses.md` | done | `CLAUDE.md:51-52` |
| W2 | "Sources by job" points to "Overview" | done | `docs/coresets.md:76`; `docs/external_services.md:5` |
| W3 | "run by" convention and a pointer to `dispatch.md` | done | `docs/process.md:39-43`; `docs/dispatch.md:33-35` |
| W4 | "Interim:" notes where a gap bites, removed as gaps close | done | no `Interim` note left; the S2–S5 gaps are closed |
| W5 | the agent file defers to the index | done | `.claude/agents/survey-pass.md:16-19` |
| A1 | each step's owner, inputs, artifact and done-criterion | done | `docs/process.md:51-89` |
| A2 | a brief per job type; numbers from scripts, never hand counts | done | `docs/dispatch.md:60-125`, eleven briefs; `.claude/agents/survey-pass.md:27-28` |
| A3 | "stop and tell the user" becomes a `STOP:` report | done | `docs/process.md:107-108`; `docs/external_services.md:176-177`; `.claude/agents/survey-pass.md:37-39` |
| A4 | never Read the large files whole, in `tooling.md` and the agent file | done | `docs/tooling.md:8-9`; `docs/formats.md:323-331`; both agent files |
| A5 | cross-cluster work runs once, serially, after per-cluster work | done | `docs/dispatch.md:47-49` |
| A6 | `survey-edit` loses Asta; moves rows only to match the computed assignment | done | `.claude/agents/survey-edit.md:4-8`, `:27-28` |
| A7 | a one-screen pass checklist | done as amended | the order-of-operations table is the checklist (`docs/process.md:37`; `docs/dispatch.md:29-32`) |
| T1 | a stage-aware `check.py` that absorbs S10 | done as amended | `--stage` replaced by integrity plus gates; recorded in follow-up todo 2 and `901d5ca` |
| T2 | compact naming and fringe sheets | done as amended | `tools/sheets.py`, not `--brief`; recorded in the Phase 3 note |
| T3 | one script for fringe additions, the cluster column and late batches | done | `tools/assign.py` (`add-fringe`, `clusters`, `late`) |
| T4 | input parser: dimensions, `Clustering` fields and values; imported by `check.py` and `graph.py` | done | `tools/inputs.py`; caveat in gap 3 |
| T5 | a preflight script | done as amended | `tools/preflight.py`, Python; recorded in the Phase 3 note |
| T6 | the canonical ID in one module, used by every tool listed | done | `tools/check.py:37-57`; `pool.py:42`, `fringe.py:62`, `bib.py:73-90`, `fulltext.py:180-197`, `graph.py:64-74` |

### The action plan's notes

| # | claim | verdict | evidence |
| -- | -- | -- | -- |
| P1.1 | `Halts` and `Ended` replace `Stopped because`; `Halts` covers proceeding past a preflight failure | done | `docs/formats.md:151-153`; `docs/external_services.md:207-208` |
| P1.2 | `H9`'s interim note, to remove with T1 | done | removed (`docs/process.md:143`) |
| P1.3 | W3's convention | done | W3 |
| P1.4 | C8 partly; the rest in Phase 2 | done | C8 |
| P1.5 | C5's interim note, to remove when fixed | done | removed; C5 |
| P1.6 | the A2 numbers conflict resolved in `survey-pass.md` | done | A2 |
| P2.1 | C4: one `ARXIV_ID`; live resolution; only the canonical old form accepted | done | C4; live re-check |
| P2.2 | C5: `tools/net.py` shared by five scripts; `pool.py` and `graph.py` save per batch | done | C5; `net` imported by `pool`, `graph`, `fringe`, `bib`, `fulltext` |
| P2.3 | C6: migration; `clusters.json`'s `pool_fetched` a list | done | `pool.json` re-check; `tools/cluster.py:560` |
| P2.4 | C8: `asta_config.py` reads local, project, user scope | done | `tools/asta_config.py:29-39` |
| P2.5 | C1 with S8; "a later `check.py` could flag a placeholder" | done | `g0.placeholders` (`tools/gates.py:159-162`) |
| P2.6 | C2, and `cluster.py`'s `top` ranked by in-degree | done | `tools/cluster.py:508-515`; git comparison |
| P2.7 | D5's code half; three passages of `outputs/reasoning.md` marked | done | `tools/check.py` passes on `reasoning` |
| P2.8 | User-Agent `deeper-research` | done | `bib.py:55`, `fulltext.py:45`, `preflight.py:25` |
| P2.9 | M1, with the rerun reproducing exactly | done | git comparison |
| P3.1 | `inputs.py` reads `Dimensions` and `Clustering`; `values:` leads in `inputs/reasoning.md`; `check`, `graph`, `cluster` read it | done | re-run of `inputs.py`; `tools/cluster.py:387-391` |
| P3.2 | a coreset row in a block other than its computed cluster fails | done | `tools/check.py:433-435` |
| P3.3 | eight Phase 3 faults caught | `UNVERIFIED` | fixture deleted; superseded by `tests/gates/` |
| P3.4 | `computed` column; `assign.py` with five subcommands; nothing in the Pool table written by hand | done | `tools/assign.py`; `docs/formats.md:214-217` |
| P3.5 | late queue as empty cells; weighted vote; 15 of 15 on held-out papers; refuses above 10% | done; the 15 of 15 `UNVERIFIED` | D1.2, D1.5, D1.6 |
| P3.6 | `cluster.py` matches; `remap` carries names; swap test; `clusters` and `check` refuse until remapped | done; the swap test `UNVERIFIED` | `tools/cluster.py:576-589`; `tools/assign.py:227-230`, `:301-332`; `tools/check.py:328-331` |
| P3.7 | granularity applied by `cluster.py`; `--level coarser\|finer\|N` | done | `tools/cluster.py:385-411` |
| P3.8 | sheets about 2.8k and 0.8k tokens, gitignored | done | re-run; `.gitignore` |
| P3.9 | `CorpusId` link form; end-to-end with three papers | done; the end-to-end run `UNVERIFIED` | live 301 |
| P3.10 | `CorpusId:248562643` is `2205.03401`; `check.py` fails a `CorpusId` row with an arXiv ID | done | live lookup; `tools/check.py:284-285` |
| P3.11 | `fulltext.py` accepts only `%PDF` | done; the AMS example `UNVERIFIED` | `tools/fulltext.py:194` |
| P3.12 | "check.py does not check the log lines" kept as a gap | done as amended | closed by the gates; roadmap item removed |
| V3.1 | the named clustering is the baseline; unnamed runs record nothing | done; the runs `UNVERIFIED` | `tools/cluster.py:576-589` |
| V3.2 | `--level N` accepts the reached count | done | `tools/cluster.py:400-402` |
| V3.3 | a pool under 12 embedded papers prints `STOP: H8` | done | `tools/cluster.py:455-459` |
| V3.4 | `fulltext.py`: a publisher's 403 is a note; exit 0 for unfetchable papers | done | `tools/fulltext.py:188-192`, `:244-248` |
| V3.5 | `inputs.py` fails a malformed dimension bullet | partial | gap 3 |
| V3.6 | `assign.py add` refuses papers without an embedding; `check.py` lists them | done | `tools/assign.py:161-162`; `tools/check.py:354-357` |
| V3.7 | `H3` defined precisely; `RECLUSTER:` | done | `docs/process.md:125-128`; `tools/assign.py:268` |
| V3.8 | doc fixes: weighted vote, template with steering and `--level`, `remap` and second `sheets.py` in the checklist, Graph API callers, `uv` users, 5xx codes, preflight example, shortlist size | done, except the shortlist sentence | `docs/formats.md:126-128`; `docs/process.md:67`, `:71`; `docs/external_services.md:101-106`, `:122`, `:189`, `:213-214`; gap 10 |
| V3.9 | stale docstrings fixed in eight tools | partial | gap 7; the other seven read correctly |
| P4.1 | A1 and A7: the checklist columns; `dispatch.md` says to run down it | done | A1, A7 |
| P4.2 | A2: template, eleven briefs, who writes which line, `Log:` and `Open work:`, `bib.py` before `check.py` | done | `docs/dispatch.md:36-54`, `:62-125` |
| P4.3 | A4 in `formats.md`, `tooling.md` and both agent files | done | A4 |
| P4.4 | an inventory of `graphs/<topic>/`; "the screening sheet" named | done | `docs/formats.md:297-331`; `docs/process.md:219-224` |
| P4.5 | frontier candidates in the pool and the `Orientation` line | done | `docs/process.md:191-193`; `g1.orientation` |
| P4.6 | `fringe.py collect` carries judgements over; 146 read back | done | `tools/fringe.py:150-158`; re-run |
| P4.7 | the dry read's 14 fixes | done | preflight in its own brief (`docs/external_services.md:172-173`); skeleton headings (`docs/formats.md:74-77`); adding targets (`:19-23`); blocks set up by the main session (`docs/process.md:75`); every cell drafted (`docs/dispatch.md:102-103`); bridges for trading pairs only, divided clusters in selection (`docs/process.md:77`; `docs/dispatch.md:100-101`); sheet rewrites (`docs/process.md:78`, `:82`); a thin cluster that stays thin (`:440-442`); lines updated only during their pass (`docs/dispatch.md:40-41`); tokens from usage (`docs/formats.md:150`); the row count and remap rule (`docs/process.md:82`; `docs/tooling.md:33-36`); "internally divided" in the sheet (`docs/tooling.md:153-154`) |

### The follow-up on what `check.py` should enforce

Rows of the assessment table, by the requirement that holds each (`tools/gates.py`, unless noted):

| row | verdict | where |
| -- | -- | -- |
| 1 | done | `need_lines` in `g0.dimensions`, `g0.preflight`, `g1.orientation`, `g1.expansion`, `g1.errored`, `g1.fringe-line`, `g1.pool-line`, `g2.lines`, `g4.coreset-line`, `g5.coverage`, `g5.end-lines`; `Dissent searches` required only where a `high` cluster exists |
| 2 | done | `g0.placeholders`; computed ids in `g2.lines` |
| 3 | done | `g0.labels` |
| 4 | done | `g0.preflight`, all nine checks |
| 5–7 | done | `g1.orientation`, `g1.expansion`, `g1.errored` |
| 8 | done | `g1.fetched` |
| 9–10 | done | `g1.fringe-collected`, `g1.fringe-screened`, `g1.fringe-added`, `g1.fringe-line` |
| 11 | partial | gap 5 |
| 12 | partial | gap 6 |
| 13 | done as amended | `assign.py late`'s refusal and `g5.late-empty`; recorded in todo 3 |
| 14 | done | `g5.late-empty`, `g3.assigned` |
| 15–16 | done | `g2.named`, `g2.lines`, `g2.clusters-line` |
| 17–18 | done | `g2.review`, `g2.diagnosis-halts` |
| 19 | done as amended | left to the checklist; recorded in todo 3 |
| 20–24 | done | `g3.roles`, `g3.dissent-searched`, `g3.bridges`, `g3.divided`, `g3.fringe-quota` with `Waivers` |
| 25 | done as amended | left out; recorded in todo 4 |
| 26 | done | `g3.cells` |
| 27–29 | done | `g4.abstract-listed`, `g4.h10`, `g4.coreset-line` |
| 30 | done | `g0.dimensions`, `g3.dimension-columns` |
| 31 | done | `tools/check.py:479-483`, from `read_targets` |
| 32 | done | `g5.cite-entries` |
| 33 | done | a note (`tools/check.py:484-487`) |
| 34–35 | done | `g5.converged`, `g5.changed-in-coreset` |
| 36 | done as amended | left out; recorded in todo 4 |
| 37–38 | done | `history`, `tools/gates.py:696-707` |
| 39 | partial | gap 4 |
| 40 | done | a note (`tools/gates.py:717-719`) |

Todo items: 1 (format changes: `Waivers`, target bullets, `pending`, `ok | failed`, `Gates`) done,
`docs/formats.md:14-25`, `:115`, `:120`, `:151-152`; 2 (`gates.py`, `--stage` gone) done; 3 done, with the stale count
(gap 9); 4 partial (gap 4); 5 (`reject`, quoted dissent, `add-fringe` saving IDs) done, `tools/assign.py:203-204`,
`:345-366`; 6 done, with the stale counts (gap 9), re-run; 7 (`docs/gates.md` indexed, gate rows, docs updated, the
roadmap item removed, judgement audits proposed) done, `CLAUDE.md:48`, `docs/process.md:56-89`,
`docs/roadmap.md:104-121`; 8 (evidence files, `g4.evidence`, four faults) done, `docs/verification.md:35-57`,
`tools/gates.py:521-560`, re-run.

### Commit messages

| commit | claims beyond the audit file | verdict |
| -- | -- | -- |
| `880af9a` | the files it lists; `CLAUDE-old.md` removed; `tooling.md` reordered by pass | done |
| `0ceb621` | as Phase 4 | done |
| `901d5ca` | 40 requirements; 43 of 43 faults; 17 of 17 behaviours; `--status`; pending halts hold gates | done; the count is 43 (gap 9) |
| `f96f5de` | eight validated hues, then rings, then tints, in the viewer and the history chart | done: `tools/graph_template.html:379-390`, `:577-580`; `docs/tooling.md:166-169` |
| `8c9b6de` | `tests/gates/` in the repo, finding the legacy source under either name, documented | done: `tests/gates/build.py:14`; `docs/tooling.md:237-245` |
| `5a451bb` | `CLAUDE.md` describes the roadmap as open items; `formats.md` no longer says it reads every experiment report | done: `CLAUDE.md:54-58`; `docs/formats.md:317` |

## Appendix: seen in passing, not judged

Not covered by any claim above. Listed for the blind audit, which should find them on its own if they matter.

- `surveys/reasoning.md:543-544` (Open work, not a log entry) still says abstract-sourced rows are "marked provisional
  in the output"; the output's marker is `[abstract-only]`.
- `g1.rejected` (`tools/gates.py:233-239`) requires at least one rejection recorded in the pass. A pass that rejected
  nothing fails `G1` unless the user waives it.
- `docs/formats.md:317` calls `match-simulation.json` evidence for a proposal; the roadmap now files matching under
  "Known gaps", not "Proposals".
- A 2-paper cluster appears on the naming sheet as "stability none (fewer than 3 papers)", without the hint that the
  spec treats it as thin.

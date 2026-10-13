# Segment `pool`

Steps 1–2: Orient, Expand and screen, the pool fetch, the fringe routes and their screening, and `--gate G1`
(`docs/audits.md`, "Segments"). Starting state: checkpoint `sim-checkpoint-model-collapse-plan` (commit `1f90b53`): the
survey with step 0's entry, `G0` passed. This segment retrieves, so its iterations cannot be compared by their pools;
convergence is judged from the runner's report and the spot checks. Spot checks (`docs/audits.md`, "Spot checks per
segment"): about ten screening verdicts each way, in scope and out, against the input's topic and exclusions; and the
recency window, against the input.

Watch (from `simulation.md`, "Inherited, by segment", and `plan`): the stopping rules (`A1`); the fringe score and its
cohort (`M11`, `M12`); the `new` route's exclusion of rejected papers (`M16`); `maybe` on the screening sheet (`T5`);
`g1.orientation` with no frontier candidate; each Expand agent's context size, from its transcript; WebSearch latency,
which took about 300 s for one query in `plan`'s iteration 3.

## Iteration 1

### Run

- `Runner` — headless `claude -p`, session `a5fa5552-53ef-4bfc-9d89-f62aaeff9861`. Prompt: `runs/pool-1.prompt.md`.
  Steering: none.
- `From` — checkpoint `sim-checkpoint-model-collapse-plan` (commit `f06b260`, the segment's opening, whose topic state
  is the checkpoint's).
- `Outcome` — cut off by the account's usage limit (`usage_limit_reached`, HTTP 429) after 56 min, 15 runner turns,
  $14.31, during the Expand dispatch. The runner wrote no report. The findings below come from the two agents'
  transcripts, the files the run left, and the auditor's spot checks. The partial survey, `rejected.md`, and the scripts
  the Expand agent wrote for itself are kept in `runs/pool-1-partial/`.
- `Dispatches` — `survey-pass` "Orient": 157053 tokens (from the log's `Tokens`), 92 turns, 17 min, final context 155k;
  21 WebSearch queries, 17 frontier candidates, all within the recency window. `survey-pass` "Expand": cut off; 187
  turns, 38 min, context 17.7k at its start, 271k at mid-run, 448k at its last turn, no compaction (the model's window
  is 1M).
- `Where it stopped` — Expand had traversed backward from all 17 frontier candidates (810 candidates, by the `Expansion`
  line's counts) and forward from both seeds (491 and 182) and from the frontier candidates (7); the relevance searches
  on the themes were still to run. The pool stood at 169 papers, against the narrow topic's expected 50–150, and
  `rejected.md` at about 1200 rejections.

### Findings

- `E15` — `silent`. Most screening verdicts were made from titles alone. `docs/process.md`, "Screening for scope",
  judges every candidate "from its title and abstract". The Expand agent's traversal calls fetched only titles and IDs
  (`get_paper` with `references.title,references.externalIds`, 16 calls; `get_citations` with `title,externalIds`, 4
  calls). It fetched abstracts for a few batches and for the relevance-search results, and printed them for six
  candidates it was unsure of. Nothing in the run flags this. The spot check found no wrong verdict (below), so the
  harm, if any, is not yet shown.
- `E16` — `guess`. With about 1200 candidates to screen, the Expand agent built its own screening toolchain: eight
  scripts in `/tmp/mc-tools/` (`proc.py`, `mk.py`, `auto.py`, …) that print candidates as ID and title, take verdicts as
  short codes (`GEN`, `DET`, `ONCE`, `OTH`, `BIO`, …) expanded into canned reasons, and assign a default code to every
  undecided candidate of a result set (all of one query's results became `BIO`, "a biomedical paper on cellular
  autophagy"). The spec offers `tools/assign.py reject`, "many at once on stdin", and no more. 356 rejections share one
  canned reason, which ties the verdict to the topic only generically.
- `E17` — `guess`. The Expand agent kept its working files outside the repository, in `/tmp/mc-expand/` and
  `/tmp/mc-tools/`, and read the harness's saved tool results under `~/.claude/projects/`. No doc says where an agent
  keeps working files. `runner.sh collect` could not see them.
- `E18` — `blocker`. Screening the expansion in one agent does not scale to this topic. One Expand dispatch took on
  about 1500 candidates; its context reached 448k tokens and it had not finished after 38 minutes. On a model with a
  200k window it would have compacted several times mid-screening; here the run hit the usage limit first. The volume
  comes from the spec's own rules: backward traversal from every frontier candidate (17 here, so 810 candidates), plus
  forward traversal from the seeds.
- `E19` — `guess`. The agent corrected 50-odd rejection reasons by rewriting `rejected.md` with an inline script,
  bypassing `tools/assign.py reject`, which the file's header names as its only writer. No tool amends a recorded
  rejection.
- `E20` — `guess`. The order of required and optional work in Expand. Its `done when` requires backward traversal from
  every frontier candidate and a relevance search per theme; forward traversal is beyond the required work, under the
  stopping rule. The agent ran forward traversal from the seeds (673 candidates) before the required relevance searches,
  and the run ended before those. Whether it applied the stopping rule within the forward traversal is not visible.

Spot checks:

- Screening verdicts, a random sample (seed 20261012) of 10 rejections and 10 pool papers, each judged by the auditor
  against its abstract, fetched with Asta: 20 checked, 0 wrong. All 10 rejections are right; one carries a reason that
  fits poorly (`2608.05466`, recursive task synthesis with no model retrained, given "an RL or reasoning post-training
  method"). Two of the 10 pool papers are borderline and in by "borderline is in" (`2510.18814`, `2608.20290`, rounds of
  self-training on a model's own outputs).
- The recency window against the input: 1 checked, 0 wrong. The input names none; the log gives the last six months, as
  `docs/process.md`, "Step 1: orient", sets for a first pass.

### Fixes

Decided by the user: option B with A's cap, and the input narrowed (`simulation.md`, "Decisions"). A scoped spec audit
of step 2 came first, in `.audits/2026-10-12-spec/`, and its remediation is the fix for all six: `E16`, `E17` in
`ac34b92`; `E15`, `E18`–`E20` in `79ae39f` (code) and `97a23f0` (docs). Its disposition says what each became.

### Result

Not converged: the fixes go to iteration 2.

## Iteration 2

### Run

- `Runner` — headless `claude -p`, session `1526c065-0ee9-4b06-8f8c-b24ee2259c65`. Prompt: `runs/pool-2.prompt.md`,
  the same as iteration 1's. Steering: none at launch.
- `From` — checkpoint `sim-checkpoint-model-collapse-plan` (commit `748c7a5`), the topic's files unchanged since; a
  scratch copy built from `d530389`.
- `First leg` — halted at `H3` after 23 min, 27 runner turns, $5.93 (the runner's own `total_cost_usd`). `survey-pass`
  "Orient": 183098 tokens, 69 tool uses, 15 min; 14 frontier candidates, both seeds; the pool at 71 papers.
  `tools/expand.py collect` saved all 32 traversals (backward and forward from 16 start papers: 1,209 unique papers,
  forward from `2305.17493` 551 and from `2404.01413` 182, nothing capped), then failed on the first theme search with
  429s past `tools/net.py`'s retries; the rerun resumed and failed the same way. The runner recorded `H3`, `pending`.
- `Decision` — the auditor probed the search endpoint: `/paper/search` answered 429 to every call for at least 10
  minutes, while `/paper/{id}` and `/paper/search/bulk` answered 200. The user chose to wait for the search endpoint
  and resume the session (2026-10-13), rather than switch to bulk search or wait for the Semantic Scholar key. A
  background probe tries it every 5 minutes for up to 2 hours; the decision goes in by `runs/pool-2-resume.prompt.md`.

### Findings

- `E21` — `blocker`. The unauthenticated Graph API's relevance search, `/paper/search`, can refuse every call for long
  spells, while its other endpoints answer. `collect`'s resume, the fix for `P2`, cannot help when the one call left
  keeps failing. Every pass now hinges on it until the user's Semantic Scholar key arrives. That the search endpoint has
  a tighter anonymous limit than the rest is the auditor's inference from these probes, `UNVERIFIED`. The probes: the
  search endpoint answered 429 to 3 calls at about 15:45, then to 16 probes 5 minutes apart from 15:51 to 17:07; in the
  same spell `/paper/{id}` answered 200, and `/paper/search/bulk` answered 200 to most calls and 429 to some (2 of 7 in
  one set). On the bulk endpoint, the theme as an exact phrase, sorted by citations, matched: "model collapse" 931, with
  a paper titled "MODELING COLLAPSE AND ACCRETION IN TURBULENT GAS C…" (the probe printed 50 characters) among the top
  three, so the match is stemmed; "model autophagy" 114; "self-consuming generative models" 12; "knowledge collapse" 24;
  "AI autophagy" 5; "strong model collapse" 2; "accumulating real and synthetic data" 1; and none for "synthetic data
  verification model collapse", "model collapse scaling laws", "linguistic diversity decline synthetic text" and
  "recursive training diffusion models". Without quotes, every word is required, and the most-cited matches were off
  topic: for "self consuming generative models" (207 matches), a survey of deep-learning tools came first. Fix: below.

- `E22` — `minor`, in the audit's harness, not the spec. `runner.sh`'s fixed tool allowlist is not enforced: the runner
  ran `cat`, `sed -n`, `awk` and `sed -i` (to append its `Tokens` entry to the survey), none of them on the list, and
  its transcript shows no denial. Nothing in the user's or the copy's settings allows them. The cause is not
  established: a global hook that rewrites shell commands may be approving them, `UNVERIFIED`. Why it matters: the
  allowlist is how the audit sees a runner reach outside the spec's tools, as a tool failure in its report. Fix: the
  user's, since it concerns permissions; reported to the user.

More findings follow once the run ends.

### Fixes

- `E21` — decided by the user, 2026-10-13: the theme searches move to the bulk endpoint, and a comparison with
  relevance search is kept as future work (`docs/roadmap.md`, "Theme searches, and the Semantic Scholar key").
  `tools/expand.py`: each theme is searched as an exact phrase, its 50 most-cited matches kept and its total recorded;
  the `Expansion` line prints `"<theme>" (<kept> of <matched>)`; a search saved by the old code is run again on
  resume; an empty theme is refused. The Orient brief and step 1 ask for themes written as papers write them. Reviewed
  by a fresh agent (six findings, all fixed: one wording each in step 3 and the roadmap, four small ones in the code
  and tests). Both gate suites pass, 92 of 92 and 74 of 74. The halted session resumes with the fixed script and docs
  copied into the scratch copy, as steering (`runs/pool-2-resume.prompt.md`): the change cannot alter what Orient
  wrote, since only the collect row and those after it search.


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

Pending: `E18` needs a decision from the user, and `E15`–`E17`, `E19` and `E20` turn on it.

### Result

Pending.

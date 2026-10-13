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
- `Second leg` — the session resumed with the fix for `E21` (below) at 17:22, reread the two sections, recorded the
  decision in `Halts`, and reran `collect`. It finished in 4.5 min: the 32 saved traversals were kept, the 17 theme
  searches ran on the bulk endpoint. 9 of the 17 searches, and 2 of the batch calls fetching abstracts, met 429s that
  `tools/net.py`'s retries absorbed, at most 4 retries for one call. 1,302 new candidates went onto the sheet; left out were 64 already in the pool, 7 rejected
  earlier and 3 duplicates of another record. The runner then dispatched 14 "Screening" agents at once, in ranges of
  100 rows, and the account's usage limit cut the run off 10 s later. The agents had made 3 or 4 reads each and written
  no verdict. `runs/pool-2b.json` holds only the error, since the cut came in the run's last turn.
- `Theme matches` — kept of matched, from `collect`'s output: "model collapse" 50 of 931, "model autophagy" 50 of 114,
  "iterative retraining" 50 of 105, "knowledge collapse" 24, "self-consuming generative models" 12, "recursive
  retraining" 8, "self-consuming training loops" 6, "AI autophagy" 5, "strong model collapse" 2, "accumulating real
  and synthetic data" 1, "networked self-consuming generative models" 1; and none for 6 themes: "synthetic data
  verification model collapse", "curated self-consuming retraining", "machine-generated text detection model collapse",
  "model collapse scaling laws", "linguistic diversity decline synthetic text", "recursive training diffusion models".
  Orient wrote these themes before the brief asked for phrases as papers write them, so this run does not test that
  instruction.
- `Third leg` — resumed after the limit reset, with `runs/pool-2c.prompt.md`: the interruption, and that no verdict
  was written; carry on from the screening row. The runner dispatched 14 "Screening" agents again, in ranges that
  partition the sheet (1–100 to 1201–1300, and 1301–1302), and all 14 judged their rows in about 6 min. The headless
  session then ended: its turn closed while it waited for the last agent's notification, and `claude -p` exits when a
  turn ends (`runs/pool-2c.json`).
- `Fourth leg` — `runs/pool-2d.prompt.md`: the session had ended, the last agent was done; carry on. `add-expand` added
  134 papers (pool 205) and reported one paper judged `no` on the sheet but in the pool, `2308.07462`, through a second
  record; a re-judging "Screening" agent kept the `no`, and the runner halted on `H12`, `pending`.
- `Decision` — the auditor decided `H12` as steering, 2026-10-13: keep the paper, by "borderline is in"; the re-judging
  agent had called the `yes` defensible too (`runs/pool-2e.prompt.md`).
- `Fifth leg` — the runner recorded the decision, judged row 1015 `yes` itself as the decision's record, fetched the
  pool, ran the fringe routes (120 candidates, two blind "Screening" agents of 60 rows, 19 in scope), fetched again,
  and ran `G1`: passed. The pool is 224 papers, 177 with an arXiv ID. The auditor reran `--gate G1` and the plain check
  in the repo after `runner.sh collect`: both pass, with one note of near-identical titles.
- `Cost` — the session's `total_cost_usd` is $24.13 over five legs, about 46 min of running. Dispatches: Orient 183098
  tokens; 14 expansion "Screening" agents of 33562–90594 tokens (final contexts 62k–89k; the notifications' own figures,
  130k–264k, count something else, `UNVERIFIED` what); the re-judge 48291; two fringe agents 63324 and 66568. The 14
  agents killed by the limit reported no tokens. The raw report: `runs/pool-2-report.md`.

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

- `E23` — `minor`. The runner's screening ranges overlapped: it dispatched rows 1201–1302 and also 1301–1302, so two
  agents owned rows 1301 and 1302 at once. The brief tells each agent that other agents own the other rows. `judge`
  holds a lock, so the cost is a duplicated judgement, last write kept, not a corrupted sheet. The docs say blocks of
  at most 100 rows but not that the ranges partition the sheet. Seen in the second leg, before the cutoff; the third
  leg's dispatch partitioned the sheet correctly.
- `E24` — `silent`. `collect` drops a second record of one paper only when the titles match exactly
  (`tools/expand.py`, the `keep` and `sheet_titles` tests, by `title_key`). Records whose titles differ by a word reach
  the sheet as separate rows, are judged separately, and can be judged both ways. Here: `2308.07462` at rows 965 (`yes`)
  and 1015 (`no`), which became `H12`, a user decision about what is really one paper; `2305.16960` at rows 978 and
  1016 (both `no`, harmless); and "Multilingual Arbitrage" (`2408.14960`, row 827, `no`) against "Multilingual
  Arbitration" (row 996, no arXiv ID, `yes`), now a pool row whose other record was judged out. The plain check notes a
  fourth pair already in the pool, `2505.21677` and `CorpusId:278959832`. Nothing in the run flagged the first three.
- `E25` — `guess`. Screening in parallel ranges settles the same scope boundary differently from range to range. The
  runner listed the kinds with rows on both sides: loops with no retraining (a text corpus or retrieval index fed with
  generated text); studies of how much text is AI-generated; "knowledge collapse" of human knowledge, one of Orient's own
  themes; synthetic data used once but studied for degradation; iterated learning; performative prediction (about 30
  rows rejected as one call in 501–600, while `2607.15623`, row 1061, was let in). Each agent was consistent within its
  range. The input's `Clustering` exclusions do not settle these kinds, and nothing reconciles ranges. The spot check
  (below) found the inclusions it questions in exactly these kinds.
- `E26` — `guess`. The sheet shows at most 700 characters of an abstract (`tools/screen.py`, `ABSTRACT_CHARS`), and 1,033
  of the 1,077 abstracts here are longer (mean 1,308, median 1,282). The deciding sentence can fall past the cut: row
  1061's tie to the topic, "data feedback loops in language modeling", is in its last sentence. The brief says to judge
  "from its title and abstract" and names no lookup. Agents improvised: most fetched fuller abstracts or tldrs from
  Asta, one ran `snippet_search`, two used WebSearch, and one tried WebFetch on OpenReview. On the fringe sheet this
  partly unblinded 14 rows: Asta's reply carries an arXiv link, which gives the year away. Both fringe agents say no
  verdict changed, `UNVERIFIED`.
- `E27` — `guess`. Orient kept second records of pool papers out of the pool by writing them to `rejected.md`, with
  reasons that begin "not out of scope": `CorpusId:271448069` (the Nature version of the seed `2305.17493`, which the
  agent marks `UNVERIFIED`) and `CorpusId:282047062`. `docs/formats.md`, "Paper IDs", covers merging two pool rows, not
  keeping a second record out. `rejected.md` now lists in-scope papers. Citers of the Nature version do not count
  toward the seed's in-degree, `UNVERIFIED` how many.
- `E28` — `guess`. The recency window's dates. The runner ended the window on the day the queries ran, 2026-10-13; the
  pass is dated 2026-10-12, and `docs/process.md` says "the last six months" without saying up to which day. Orient
  counted a paper as inside the window by its Semantic Scholar publication date, which left `2608.21366`, `2602.16601`
  and `2503.03150` off the frontier list; all three are in the pool. The docs name no date to use.
- `E29` — `guess`. "How a halt works", step 1, records what is outstanding in Open work, but none of Open work's fixed
  headings fits the rows a halt leaves undone. The runner wrote them into each `Halts` sentence instead.
- `E30` — `guess`. The `add-expand` row says a `no` for a pool paper "is re-judged on the sheet", not by whom, nor that
  the re-judge may keep the `no`. The runner dispatched one "Screening" agent for the row and told it of the other
  record; a re-judge that keeps the `no` leads to `H12`, as here. With `E24` fixed, the case arises only for a paper
  whose second record no test catches.
- `E31` — `minor`. The runner broke two reading rules: one inline `python3 -I -c` that read `expand.json`, and one
  `git diff --stat` run by mistake. It kept the `Expansion` line in `/tmp/claude-1000/expansion-line.txt`, a file no row
  names. The 301–400 agent used one read-only inline `awk`. The runner reported all of them itself. Runner and agents
  otherwise used only the spec's tools: every verdict went through `judge`, by `printf`, in 1 to 4 batches per agent.
- `E32` — `minor`, in the audit's harness. Twice a leg ended with no work lost but the run stopped: the account's usage
  limit cut the second leg 10 s after a dispatch, and `claude -p` ended the third leg while the runner waited for a
  notification. Each needed a resume prompt that only restated the state.
- `E33` — `guess`. Orient treated Asta's "Title match not found" replies as empty results, not as errored queries.
  `docs/external_services.md`, "Errored queries", does not say which they are.

Spot checks:

- Screening verdicts, a random sample (seed 20261013) of 10 `yes` and 10 `no` rows from a snapshot of the expansion
  sheet, each judged by the auditor against the full abstract (from the sheet, or from Asta past the cut): 20 checked.
  All 10 rejections are right; 5 of them were judged from the title alone (`(no abstract)`), rightly. 7 of the 10
  inclusions are right (`2607.15623` only by its abstract's last sentence, past the cut). 3 are in `E25`'s kinds and
  outside the `Topic` as written, though "borderline is in" can defend each: row 578, a single round of corrupted
  training data with no loop, which the input excludes; row 896, a position paper on AI output feeding back into human
  knowledge; row 655, LLM-generated text fed into a retrieval index, no model retrained.
- The recency window against the input: 1 checked; its end date is `E28`.
- Duplicates on the sheet: the arXiv IDs of all 1,302 candidates, by script: 2 pairs, plus the pair found by title
  (`E24`).

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

- `E22` — the user's; open.
- `E25` — decided by the user, 2026-10-13: reconcile after screening, rather than voting. Voting averages out an
  agent's misreading, but these splits come from a boundary the input leaves open, which three voters split as well, at
  three times the cost. Proposed: a row after the screening, one agent that reads only the verdicts and reasons, groups
  rows that turn on the same scope question, and flags each group judged both ways; each flagged group gets one
  decision, with "borderline is in" breaking ties, applied through `judge`.
- Proposed, awaiting the user:
  - `E24` — `collect` treats records that share an arXiv ID or a corpus ID, or whose titles the plain check's test calls
    near-identical, as one paper, before the sheet; the same test against the pool and `rejected.md`.
  - `E26` — the sheet shows the whole abstract, and the brief says the sheet is all the agent reads: no lookups. This
    also closes the unblinding on the fringe sheet. Cost: about 15k more tokens per 100-row range, `UNVERIFIED`.
  - `E27` — the docs say a second record of a pool paper is never rejected: `collect`'s tests keep it off the sheet
    (with `E24`), and one found in the pool is merged under `Corrections`. The two entries in this run's `rejected.md`
    go with the iteration's state.
  - `E28` — the docs say the window ends on the day the recency queries run, and that a paper's date is its first
    arXiv version where it has one, else Semantic Scholar's publication date.
  - `E29` — "How a halt works": the rows a halt leaves undone go in its `Halts` sentence, not Open work.
  - `E30` — the `add-expand` row: a "Screening" agent re-judges the row, told of the pool record; a kept `no` is `H12`.
  - `E33` — `docs/external_services.md`: "Title match not found" is an empty result, not an error.
  - `E23`, `E31` — no spec change: `E23` did not recur, and the runner reported `E31` itself. `E32` — no change; a
    resume prompt that restates the state is enough.

### Result

Not converged: `E24` is `silent` and `E25`–`E30`, `E33` are `guess`. Confirmed fixed from iteration 1: `E16`–`E18`
(every verdict through `judge`, no own scripts, contexts at 62k–89k against 448k), `E15` (abstracts on the sheet) and
`E20` (the work is fixed by script). The fixes go to iteration 3, which runs the segment again from the checkpoint.

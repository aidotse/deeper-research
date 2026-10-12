# Spec audit of step 2 (expand and screen): the audit

## How to read this document

This is the audit, the first of three documents, of a scoped spec audit. The scope is step 2 of the pipeline, "expand":
how the pool grows after orientation, and how each candidate paper is screened for scope. Two documents sit beside this
one in `.audits/2026-10-12-spec/`. `remediation-plan.md` will plan a fix for each issue here. `disposition.md` will
record what was done.

This document lists issues and nothing else. It does not plan fixes and it does not decide between options. Its sections
follow `docs/audits.md`, "The audit document":

- `Scope and method` says what was read, what was run, and what each status value means.
- `Executive summary` and `Part (a)` judge step 2 as a reviewer would.
- `Part (b)` lists the issues, one subsection per dimension (`C`, `M`, `S`, `W`, `A`, `T`, `Z`). An issue marked `(V)`
  bears on verification.
- `The verification concept` follows one candidate paper from retrieval to its recorded verdict.
- `Part (c)` says what to fix before a real run of step 2 on `inputs/model-collapse.md`.
- `Checked and found to hold` lists what was examined and found sound.
- `Appendix A` holds the cost computation that several issues rest on.

## Scope and method

What was read, in full or by the sections named:

- `docs/audits.md`, from its start to the end of "The audit document", and `CLAUDE.md`.
- `docs/process.md`: the Overview, "Order of operations" (all rows, with attention to steps 1 to 3), "When a pass ends",
  "Step 1: orient" as the interface, "Step 2: expand" with "Screening for scope" and "Fringe routes", step 3 up to
  "Returning to step 3" for what it needs from the pool, and "Rules for re-runs".
- `docs/dispatch.md` in full.
- `docs/formats.md`: the input format, "Paper IDs", "1. Retrieval log", "4. Pool", "5. Open work", and
  "`graphs/<topic>/`".
- `docs/tooling.md`: the introduction, "Consistency check", "Pool table", "Pool metadata", "Fringe candidates", "Small
  helpers" and "Tests".
- `docs/external_services.md`: "The services", "Asta" with its subsections, "Semantic Scholar Graph API", "Credentials
  and privacy" and "Preflight".
- `docs/gates.md` in full; the `pool` lines of `docs/coresets.md`.
- Code: `tools/assign.py` in full, `tools/fringe.py` (`collect` and `judge`), `tools/pool.py` in full, `tools/gates.py`
  (parsing, the `G0` and `G1` requirements, the runner and the history check), and the ID helpers of `tools/check.py`.
- `tests/gates/build.py` (the fixture) and the `G1` cases of `tests/gates/faults.py` and `tests/gates/behaviour.py`.
- `.claude/agents/survey-pass.md` and `inputs/model-collapse.md`.

What was not read: `.audits/`, `docs/roadmap.md`, git history, `graphs/`, anything outside the repo, and
`surveys/model-collapse.md`. The work was not split across agents.

What was run:

- `python3 tests/gates/faults.py`: 84 of 84 faults caught. `python3 tests/gates/behaviour.py`: 49 of 49 behaviours as
  expected.
- `python3 tools/inputs.py model-collapse`: exit 0.
- One scratch topic, `scratch-audit-expand`, built with the gate fixture (`ZZ_GATE_TOPIC=scratch-audit-expand`, through
  `tests/gates/build.py`). On it, `python3 tools/check.py scratch-audit-expand --gate G1` was run three times: on the
  fixture as built, with the `Expansion` line's `backward from` changed to `forward from`, and with its only query
  removed. All three passed `G1`. The topic was removed with the fixture's own `clean()`, and no `scratch-audit-*` file
  remains under `surveys/` or `graphs/`.

Outside calls, five in all, each to test a claim the spec makes about Asta:

1. `get_paper` `ARXIV:2404.01413`, fields `title,url,year,publicationDate`: it returned the Semantic Scholar `paperId`
   and the requested fields, and no arXiv ID or corpus ID.
2. `get_paper` `ARXIV:2404.01413`, fields `title,externalIds,corpusId,citationCount,referenceCount`: these fields work,
   though Asta's tool description does not list them. It returned `ArXiv` `2404.01413`, `CorpusId` 268856698, 30
   references and 182 citations.
3. `get_paper` `ARXIV:2305.17493`, fields `title,citationCount,referenceCount`: 30 references and 551 citations.
4. `get_citations` `ARXIV:2404.01413`, fields `title,externalIds,abstract`, `limit` 2: two records, both arXiv `2610.*`
   papers (October 2026). Each also carried `authors` and `openAccessPdf`, which were not requested. The response gives
   no total count. The two records came to about 2,900 characters.
5. `get_paper` `ARXIV:2404.01413`, fields `references`: 30 entries, each holding only `paperId` and `title`. One had
   `paperId` `null`. The response also carried the paper's 14 authors and its `openAccessPdf`, which were not requested.

Retrieved text was treated as data.

Each issue carries one status value:

- `verified against code`, with file and line;
- `verified against data`, measured on a committed file;
- `verified by simulation`, reproduced on the scratch topic, by an outside call listed above, or by a computation stated
  with it (Appendix A);
- `verified against docs`, a contradiction or gap visible in the docs themselves;
- `likely`, reasoned from the code or docs but not reproduced.

Line numbers refer to the files as they stood on 2026-10-12.

## Executive summary, in the manner of a reviewer

`What step 2 proposes.` After orientation has found the current frontier by web search, step 2 grows the pool through
Asta. The agent traverses one hop backward from each frontier candidate, one hop forward from the seeds and the frontier
candidates, and runs a relevance search for each theme orientation named. Every candidate is screened for scope from its
title and abstract. In-scope papers enter the Pool table through a script, and out-of-scope ones are recorded with a
reason in `rejected.md`. Two fringe routes then run by script: papers the pool cites but the wider literature ignores,
and very recent recommendations. Their candidates go onto a blind sheet, an agent screens them, and the in-scope ones
are added. A gate, `G1`, checks the records before clustering.

`Claimed contributions.`

1. A pool built from two complementary retrieval jobs, so that it is neither top-heavy with preprints nor blind to new
   work.
2. A screening rubric with an explicit lean: a borderline paper goes in, because a wrong inclusion is visible and a
   wrong rejection is not.
3. A trace for every negative verdict: `rejected.md` for expansion, and the screening sheet for the fringe routes.
4. Fringe routes that reach poorly connected work by script, screened blind to the route that found them.
5. A gate that refuses to cluster until the pool's records are complete.

`Value over a commercial deep-research product.` A commercial tool shows what it cited, not what it looked at and
discarded. Step 2 records rejections with reasons, and that is a real difference. The blind fringe screening has no
counterpart in such tools at all.

`Strengths.` The script side is solid. Entry to the pool is by script only, with refusals for unknown papers, papers
without an embedding and non-canonical IDs. Metadata never passes through a model. The fringe pipeline (collect, blind
sheet, judge, add) is the best-designed part: its candidate set is reproducible from `fringe.json`, every verdict sits
beside its candidate, and the gate checks that every candidate has one. The rubric's asymmetry argument is sound.

`Weaknesses.` The agent side of step 2 is not feasible as written on a realistic topic. On the example input, the
required traversals and searches return on the order of 1,200 candidate records. That is about 440,000 tokens of tool
results for one agent, and the brief allows only one Expand agent at a time with no rule for splitting the work
(Appendix A). The tools' interface is also unspecified at two points an agent cannot avoid. Asta does not return the
canonical ID that `tools/assign.py` requires unless the agent asks for an unlisted field. And forward traversal silently
truncates: a seed with 551 citers yields the 100 that Asta returns by default, apparently the newest. Finally, the trace
for expansion is thinner than the spec claims. The candidate set of each traversal survives only as a hand-counted
number. `G1` cannot tell whether expansion's screening was recorded at all, and it accepts a forward traversal where
backward is required.

`Verdict.` The design is right, and the fringe half is close to ready. The expansion half needs work before a real run:
a way to split or cap the work, a stated path from Asta's results to canonical IDs, and a record of each traversal's
candidates that a script, not an agent's count, produces. Without these, the first real run will stall or improvise at
exactly the points where the spec most wants a trace.

## Part (a): is the current development direction right?

### What is load-bearing

The pool is what the coreset approximates. `docs/coresets.md` (lines 75–77 and 172) says it plainly: a coreset cannot
cover an idea the pool never saw. So step 2's completeness bounds everything downstream, including the coverage test,
which samples only from the pool. Three things carry that weight. The first is the screening rubric and its lean toward
inclusion. The second is the traversal duties: what must be traversed, and how far. The third is the record of negative
verdicts, which is the only place a wrong rejection can be seen. Script-only entry and script-only metadata are also
load-bearing, because they keep the pool's numbers out of any model's hands.

### Where the effort may be misallocated

The spec spends its precision on the parts that are already safe and leaves the risky part loose. The fringe routes,
which add up to 120 candidates, have a script, a blind sheet, an atomic judging tool, a refusal test shared with the
gate, and four `G1` requirements. Expansion, which screens roughly ten times as many candidates, has prose instructions,
a hand-written log line parsed by regular expression, and one gate requirement that passes on a single rejection from
any step. The effort that went into fringe screening is the right kind of effort. It was spent on the smaller route.

### Simpler or partial solutions that exist

The repo already holds the simpler solution, in the fringe routes. `docs/external_services.md` (lines 111–123) argues
that the fringe routes use the Graph API by script for two reasons. One is volume: thousands of records that no model
should read. The other is reproducibility: a script applies the same rule every time. Both reasons apply to expansion's
traversals just as strongly. Reference lists and citer lists are exactly the bulk data the Graph API serves by script,
with paging, canonical IDs and totals. A `collect`-style script for the backward and forward traversals could write a
screening sheet in the fringe sheet's form. The agent would then only judge, as in fringe screening. Relevance searches
could stay with the agent. This would remove the ID problem, the truncation problem and the counting problem at once,
and it would make the candidate set of every traversal a committed record. The cost is the loss of the agent's freedom
to steer traversal, which the spec already limits to one hop. This is listed as `Z1`. Whether to adopt it is the user's
call.

## Part (b): issues by dimension

### C — the docs and the code disagree

**C1 (V) — `G1` counts a frontier candidate as traversed in any direction, while the spec and `docs/gates.md` require a
backward traversal.**

- `Evidence`: `tools/gates.py:249` accepts a part opening with `backward`, `forward` or `both`. `docs/gates.md:48` says
  `G1` checks the form `backward from <id> (<n>)`. The done-when at `docs/process.md:63` requires "backward traversal
  done from every frontier candidate". On `scratch-audit-expand`, changing `backward from` to `forward from` still
  passed `--gate G1`. The fault tests (`tests/gates/faults.py:52-53`) cover only a missing ID and the word "not".
- `Why it matters`: backward traversal is where anchors come from (`docs/process.md:227-228`). A pass that traversed
  only forward passes the gate meant to catch it. The reviewer reading `docs/gates.md` believes a check exists that does
  not.
- Status: `verified by simulation`.

**C2 — Asta's paper tools return fields that were not requested, contrary to the spec's statement that they return only
`title` unless asked.**

- `Evidence`: `docs/external_services.md:68-71` says "every paper tool returns only `title` unless `fields` asks for
  more" and calls fields "the main lever on screening cost". Outside calls 4 and 5 returned `authors` and
  `openAccessPdf`, with its long licence disclaimer, without being asked.
- `Why it matters`: by rough measure the unrequested fields are about a third of each citer record. The cost estimates
  an agent or a planner makes from the spec are therefore low. The lever is real but weaker than stated.
- Status: `verified by simulation` (calls 4 and 5). This is the docs against the service, not against repo code.

**C3 — `tools/fringe.py judge` accepts a one-word reason, which `tools/assign.py add-fringe` and `G1` then refuse.**

- `Evidence`: `tools/fringe.py:281` refuses only an empty reason. `tools/gates.py:313-316` (`judged`), used by
  `tools/assign.py:229-232` and by `g1.fringe-screened`, requires at least two words. `docs/tooling.md:155-157`
  describes `judge` as refusing only a missing reason, and `docs/tooling.md:111` describes the two-word test for
  `add-fringe`.
- `Why it matters`: the screening agent gets a clean write and finishes. The main session then finds at `add-fringe`
  that rows are "unjudged", after the agent has gone. That costs a second dispatch for a check the writing tool could
  have made.
- Status: `verified against code`.

### M — method bugs

**M1 (V) — Forward traversal is silently truncated to the newest 100 citers, and the log cannot show it.**

- `Evidence`: `get_citations` defaults to 100 results and has no offset parameter (Asta's tool signature;
  `docs/external_services.md:59`). The seed `2305.17493` has 551 citers and `2404.01413` has 182 (calls 2 and 3). The
  first two citers returned for `2404.01413` were both from October 2026 (call 4), which suggests newest first. The
  `Expansion` line records each traversal as `<id> (<n>)`, the count of candidates it gave (`docs/formats.md:194` and
  `249-250`). For a truncated traversal that count is 100, the same as for a paper with exactly 100 citers.
- `Why it matters`: forward traversal exists to find follow-ups and dissent (`docs/process.md:229-231`). The oldest
  citers are the ones cut off, and they include the earliest replies to a seed. On the example input, the "curse of
  recursion" seed's early critics are exactly what the input asks for: "I want both sides represented". The pool is then
  biased toward recent work in a way no record shows. The newest-first ordering is `likely` and was not established.
- Status: `verified by simulation` for the counts and the missing offset; `likely` for the ordering.

**M2 — The `hidden` fringe route can propose a second record of a paper already in the pool.**

- `Evidence`: `tools/fringe.py:162`, `177` and `205` exclude pool papers by Semantic Scholar `paperId` only.
  `docs/formats.md:172-176` says a preprint and its venue version are often two records. `tools/assign.py:252-255` adds
  a `yes` candidate by its arXiv ID or else its corpus ID, without a title check. `tools/check.py` then fails on two
  pool rows with the same title (`docs/formats.md:174-175`).
- `Why it matters`: the venue record of a pool paper, cited by two pool papers, is just the kind of record the route
  ranks as "least cited for its age". If screened `yes`, it enters as a duplicate. The check then fails after
  `add-fringe`, a main-session step whose failure the spec calls `H9`. Meanwhile `g1.fringe-added`
  (`tools/gates.py:344`) treats a title match as already present, so the gate and the add step disagree on what a
  duplicate is.
- Status: `likely`.

### S — spec inconsistencies and gaps

**S1 — Forward traversal is required by step 2's prose but by no done-when and no gate.**

- `Evidence`: `docs/process.md:222` and `229-231` require forward traversal from the seeds and the frontier candidates.
  The done-when at `docs/process.md:63` lists only backward traversal, the theme searches, the stopping rule and the
  retries. `G1` checks neither the seeds' forward traversal nor that the seeds are in the pool
  (`tools/gates.py:231-253`; `docs/gates.md:48`).
- `Why it matters`: the agent cannot tell whether forward traversal is required work or optional work under the stopping
  rule. On the example input the two seeds stand for the two sides of the debate, so skipping their citers drops most of
  the dissent.
- Status: `verified against docs`.

**S2 (V) — A rejection, or a fringe verdict, outlives a change of scope with no rule to revisit it.**

- `Evidence`: `tools/fringe.py:168-170` never collects a paper in `rejected.md` again, on any later pass.
  `tools/fringe.py:232-240` carries earlier sheet verdicts over on a rerun, and `G1` accepts them
  (`tools/gates.py:319-331` checks only that a verdict exists). The input may change between passes
  (`docs/gates.md:126`), and `docs/process.md`, "Rules for re-runs" (lines 784-797), says nothing about earlier
  verdicts.
- `Why it matters`: if the user widens the `Topic`, papers rejected under the old scope stay out of the fringe routes
  for good. The record shows them as judged, so nothing flags them. This is the silent failure the rubric's lean toward
  inclusion is meant to prevent.
- Status: `verified against code` for the persistence; the scope-change case is `verified against docs` as a gap.

**S3 (V) — Two opposite verdicts on one paper have no place to be reconciled and no way to be closed.**

- `Evidence`: `tools/assign.py:141-148` warns on adding a rejected paper and says "say in the log which one stands and
  why". No log line in `docs/formats.md:186-231` has that role. There is no tool to retract a rejection, and `reject`
  refuses a pool paper (`tools/assign.py:417-418`). `tools/gates.py:1099-1104` notes every paper in both the pool and
  `rejected.md`, on every run, for good.
- `Why it matters`: a reconciled conflict keeps raising the same note in every later check, which trains the main
  session to ignore it. The agent must also invent where to write the reconciliation.
- Status: `verified against code`.

**S4 — `rejected: none` is defined two ways, and a later targeted expansion can make it false.**

- `Evidence`: `docs/process.md:241` says to write it "if nothing was out of scope" in expansion. `docs/formats.md:254`
  says "if no candidate was judged out of scope this pass", which includes orientation. A targeted expansion in step 3
  appends its own part (`docs/formats.md:195` and `252-253`), so the line no longer "ends" with `rejected: none`, and
  its rejections leave the earlier `rejected: none` false. `tools/gates.py:274` searches for the phrase anywhere.
- `Why it matters`: small. The record can say two contradictory things, and the gate does not notice.
- Status: `verified against docs`.

**S5 — A partly done expansion leaves no record of what was done.**

- `Evidence`: the Expand brief writes the `Expansion` line as a report of what was traversed
  (`docs/dispatch.md:111-113`). Nothing says to write it as the work goes. The write-as-you-go rule names rows
  (`docs/dispatch.md:57-58`; `.claude/agents/survey-pass.md:73-74`). Open work has no heading for unfinished expansion
  (`docs/formats.md:346-355`).
- `Why it matters`: given the volume in Appendix A, an Expand agent may well die mid-job. Its pool rows and rejections
  survive, because the scripts write them at once. But which traversals and queries it finished is lost. The next agent
  must either redo them or guess. `--status` cannot help, since `G1` does not check the parts it would need to see
  (`T1`).
- Status: `likely`.

**S6 — An orientation with no frontier candidate cannot pass `G1`, and no rule covers it.**

- `Evidence`: `tools/gates.py:235-236` fails `G1` when `Orientation` lists no frontier candidate. No halt in
  `docs/process.md:129-169` and no rule in step 1 or step 2 covers this case.
- `Why it matters`: on a quiet or old topic, the main session meets a gate it cannot pass and has no step to take except
  asking for a waiver. A waiver needs the user's decision, and no rule tells the main session to ask for one.
- Status: `verified against code`.

**S7 — An unresolved reference cannot be screened, added or rejected, and the spec does not say what to do with it.**

- `Evidence`: call 5 returned a reference with `paperId` `null`. `tools/assign.py` takes only canonical IDs (lines
  182-186 and 413-414). Open work's `Papers that could not enter the pool` covers papers judged in scope
  (`docs/formats.md:372-373`). It does not cover a candidate that cannot even be screened.
- `Why it matters`: each such candidate is silently dropped, and the traversal's count still includes it. On one
  frontier paper it was 1 of 30.
- Status: `verified by simulation` (call 5).

### W — how the docs are wired

**W1 — For the first expansion, the Expand brief gives no done-when, and its Read list omits the row that holds it.**

- `Evidence`: `docs/dispatch.md:108-109` states the job's done-when for a targeted expansion only. The first expansion's
  done-when is in `docs/process.md:63`, in "Order of operations", which the brief's Read list
  (`docs/dispatch.md:115-116`) does not include. "When to stop" points there (`docs/process.md:271-272`), and the
  pointer rule (`docs/dispatch.md:86`) lets the agent follow it.
- `Why it matters`: the agent reaches its required work only through a pointer inside another section. An agent that
  reads only its listed sections will treat backward traversal and the theme searches as optional.
- Status: `verified against docs`.

**W2 — Neither the Expand nor the Fringe screening brief tells the agent to read the input, against which it screens.**

- `Evidence`: screening judges against the input's `Topic` and `exclude` (`docs/process.md:257-258`). The briefs at
  `docs/dispatch.md:105-121` list docs sections only. Nothing says to read `inputs/<topic>.md`, or which parts of it.
- `Why it matters`: an agent will almost surely infer it. But the input's `Context` holds search instructions for the
  example topic (`A9`), and whether the agent reads them is left to chance.
- Status: `verified against docs`.

### A — whether the docs work as instructions for agents

**A1 — Asta's results do not carry the canonical IDs that `tools/assign.py` requires, and the spec never says how to get
them.**

- `Evidence`: `tools/assign.py add` and `reject` accept only an arXiv ID or `CorpusId:<n>` (`tools/assign.py:182-186`
  and `413-414`; `docs/formats.md:161-167`). By default Asta returns a Semantic Scholar `paperId` (call 1). A reference
  list carries only `paperId` and `title` (call 5). Asking for `externalIds` returns both canonical IDs (call 2), but
  Asta's tool description does not list that field. `docs/external_services.md:51-79` does not mention it either.
- `Why it matters`: every add and every reject in step 2 needs this step. An agent that follows the spec's field advice
  ("ask for what the decision needs") will request `abstract` and get no usable ID. It will then stall, or improvise
  through title search, WebFetch or extra calls, each agent differently. Backward traversal also needs a second call for
  the abstracts, since a reference list carries none, and the spec does not say so.
- Status: `verified by simulation` (calls 1, 2 and 5).

**A2 — Step 2's required work is too large for one agent, and the spec gives no way to split it or cap it.**

- `Evidence`: Appendix A. On the example input, the required traversals and searches return about 1,200 candidate
  records, or about 440,000 tokens of tool results. Lifting the citation cap raises it to about 630,000. The brief
  allows one Expand agent at a time (`docs/dispatch.md:114`) and hands over "nothing on a first expansion"
  (`docs/dispatch.md:105`), so there is no scope to split by. `docs/process.md:103-104` says the pool is "never trimmed
  to save cost".
- `Why it matters`: the agent will exhaust its context or its spend limit partway, and lose the record of what it did
  (`S5`). The main session has no rule for dispatching the rest. Splitting by traversal or by theme across sequential
  agents would work, but nothing defines it, so two runs will split differently or not at all.
- Status: `verified by simulation` (the computation in Appendix A, from measured record sizes and counts, with stated
  assumptions).

**A3 — The per-traversal counts the `Expansion` line requires can only be counted by hand, which the spec forbids.**

- `Evidence`: `docs/formats.md:242` says every number in the log comes from a script or a tool's result, "never from
  counting by hand". `.claude/agents/survey-pass.md:32-33` and `49-50` say the same. Yet `docs/formats.md:249-250`
  requires each traversal's candidate count, and neither `get_citations` nor a reference list returns a total (calls 4
  and 5).
- `Why it matters`: a rule-following agent is caught between two rules. Some agents will count lists of 100 in context,
  and others will refuse. `G1` reads these counts as proof of traversal (`tools/gates.py:250`), so a wrong count is
  accepted.
- Status: `verified by simulation` (calls 4 and 5).

**A4 (V) — The agent definition tells the screening agent to admit only papers that will earn a role, against the spec's
rule that everything in scope enters.**

- `Evidence`: `.claude/agents/survey-pass.md:17` says "every paper you add should earn its place in a role". That
  definition is loaded into every Expand agent. `docs/process.md:223` says "Everything in scope enters the pool", and
  `docs/process.md:265-266` says a borderline paper is in.
- `Why it matters`: this sentence pulls screening in the opposite direction to the rubric's lean. A wrong rejection is
  the one error the spec calls invisible, and here the agent's own instructions invite it. Pool papers that never take a
  role are what the coverage test samples, so they must be there.
- Status: `verified against docs`.

**A5 (V) — On the example input, the rubric gives opposite verdicts for whole families of papers.**

- `Evidence`: the input's `Topic` names "detecting generated content before it enters a training set" and "curating or
  verifying synthetic data" as in-scope mitigations (`inputs/model-collapse.md:8-9`). The rubric's `Out` rule excludes a
  paper that cites the topic "as motivation" (`docs/process.md:262-264`). The input's `exclude` drops "synthetic data
  used once for training" and "self-training for capability gains" (`inputs/model-collapse.md:49-52`). A watermarking or
  AI-text-detection paper that opens with model collapse as its motivation is in by the `Topic`, out by the rubric, and
  borderline, hence in, by `docs/process.md:265`.
- `Why it matters`: AI-text detection and synthetic-data curation are large literatures. Two agents can disagree on
  hundreds of candidates, and the pool's size and shape swing with them. Only a human can settle this, and the spec has
  no point at which the agent asks. `docs/gates.md:133-134` confirms that scope judgements are not audited.
- Status: `likely`.

**A6 — The stopping rule's unit, "a batch of about 50 screened candidates", is undefined, and so is the work it would
stop.**

- `Evidence`: `docs/process.md:271-274`. A "batch" might be one call's results, a rolling window, or a group of calls.
  Asta returns 50 per search and 100 per citation call by default (`docs/external_services.md:55` and `59`). The rule
  governs "further traversals and queries" beyond the required work, and the spec does not say which ones to try: second
  hops, more queries, or citers of non-frontier papers.
- `Why it matters`: two agents stop at different points, and the reason recorded in `stopped:` cannot be checked against
  anything. `G1` does not read `stopped:` at all (`T1`).
- Status: `verified against docs`.

**A7 — Two retrieval instructions in step 2 cannot be followed as written.**

- `Evidence`: `docs/process.md:232` says `search_papers_by_relevance` and `snippet_search` "fill in clusters that
  traversal does not reach", but there are no clusters until step 3. `snippet_search` returns passages, not candidate
  lists (`docs/external_services.md:60`). `docs/process.md:233` says to use date-restricted queries "to keep recent work
  represented", with no rule for which queries or what window.
- `Why it matters`: small, but each agent will interpret these differently, and nothing records what it chose.
- Status: `verified against docs`.

**A8 — The targeted expansion's work is not sized.**

- `Evidence`: `docs/process.md:71` and `docs/dispatch.md:108-109` require backward traversal from "the region's
  most-cited papers". They do not say how many, or whether "most-cited" means within the pool or overall. On
  `no stable level`, `docs/process.md:71` and `485` say to expand "the thinnest regions", without saying how many.
- `Why it matters`: the size of each targeted expansion, and so whether a thin cluster recovers, depends on an unstated
  choice.
- Status: `verified against docs`.

**A9 — It is unclear whether the input's search instructions bind step 2.**

- `Evidence`: the example input's `Context` says the phenomenon has four names and "searches should cover all of them"
  (`inputs/model-collapse.md:17-18`). Step 2 searches "the themes that step 1 named" (`docs/process.md:222-223`). Themes
  are "the phrases the field uses for its sub-topics" (`docs/formats.md:246`), and a synonym of the topic is not a
  sub-topic. `docs/formats.md:51-54` says `Context` conditions the search, but names only step 1.
- `Why it matters`: if orientation does not list the synonyms as themes, the Expand agent has no instruction to search
  "model autophagy" or "self-consuming". Each name reaches its own sub-community, so the pool would miss one.
- Status: `likely`.

### T — tool work the spec needs but lacks

**T1 (V) — `G1` checks less of step 2 than its done-when requires.**

- `Evidence`: `tools/gates.py:241-253` checks only that each frontier candidate appears as traversed. It does not check
  a query per theme, the seeds in the pool, their forward traversal, or a `stopped:` part. On `scratch-audit-expand`, an
  `Expansion` line with no query passed `--gate G1`. So did the fixture's own line, which has no `stopped:` part, with
  an `Orientation` line that names no theme (`tests/gates/build.py:111-112`).
- `Why it matters`: three of the four parts of the done-when at `docs/process.md:63` are unchecked. A pass can skip
  every relevance search and reach clustering. `--status` cannot show a resumed session what remains of step 2.
- Status: `verified by simulation`.

**T2 (V) — Nothing records the candidate set of a traversal or query, and nothing reconciles what was screened against
what was recorded.**

- `Evidence`: the `Expansion` line keeps one count per traversal (`docs/formats.md:249-250`). Pool rows carry no
  provenance (`docs/formats.md:325-331`). `rejected.md` rows carry a date and a reason, but no step and no source
  (`tools/assign.py:384-391`). `g1.rejected` passes on any one rejection dated this pass, orientation's included
  (`tools/gates.py:278-279`).
- `Why it matters`: `docs/gates.md:17-19` promises that "every judgement leaves a trace". For expansion, an agent that
  screened 400 candidates and recorded 20 rejections passes. So does one that recorded none for expansion but rejected
  one paper at orientation. A reviewer cannot rebuild the candidate set, since Asta's results change over time (`M1`).
  So the screening can be neither checked for completeness nor redone. The fringe routes have this record, in
  `fringe.json` and the sheet. Expansion does not.
- Status: `verified against code`.

### Z — overengineered framings or solutions

Ranked by the scope of the simplification.

**Z1 — Step 2's traversals are run by an agent through Asta, where the spec's own argument calls for a script.**

- `Evidence`: `docs/external_services.md:111-123` argues for scripts on grounds of volume and reproducibility, for the
  fringe routes. Expansion's traversals face the same volume (Appendix A) and need the same reproducibility (`T2`). The
  collect, blind sheet, judge and add pipeline already exists (`tools/fringe.py`; `tools/assign.py:215-267`).
- `Why it matters`: the agent-driven design is what produces `A1`, `A2`, `A3`, `M1`, `S5` and `T2`. A script-driven
  traversal would remove most of them, and leave the agent the judgement alone. This is a framing to weigh, not a
  decided fix. Scope: the traversal half of step 2.
- Status: `likely`.

**Z2 — The "Fetch pool data" row repeats a fetch that the "After every dispatch" row has just run.**

- `Evidence`: `docs/process.md:54` runs `tools/pool.py` after any dispatch that added pool rows, before step 3. The very
  next row, `docs/process.md:64`, runs it again.
- `Why it matters`: it is harmless, since the second run fetches nothing. But it is one more row for the main session to
  track, and a reader may wonder what the second fetch is for. Scope: one row.
- Status: `verified against docs`.

## The verification concept

For this scope, verification means that a screening verdict on a candidate paper is traceable, reviewable and redoable.
Traceable means a reader can find the verdict and what it rests on. Reviewable means a reader can judge whether it was
right. Redoable means someone can repeat the screening and compare. The chain runs in six links.

1. `The candidate set.` What a traversal or query returned. For the fringe routes it is recorded in full in
   `fringe.json`, by a deterministic rule from the pool, so it can be rebuilt. For expansion it is recorded as one
   hand-counted number per traversal, and the services' answers drift. A citation traversal is also cut off at 100
   records without trace. State: weak for expansion. Issues: `M1`, `A3`, `T2`, `S7`.
2. `Identity.` Each candidate must be resolved to a canonical ID before it can be recorded either way. The scripts
   enforce the form strictly. The path from Asta's results to that form is unspecified. State: enforced at the end,
   unspecified at the start. Issue: `A1`.
3. `The verdict.` An out-of-scope verdict leaves a row in `rejected.md`, with a reason tied to the `Topic`. An in-scope
   verdict leaves only the pool row, with no reason and no provenance. That is defensible, since inclusion is the cheap
   error. A fringe verdict, either way, sits beside its candidate's title and abstract on the sheet. That is the
   strongest link in the chain: a reviewer can redo the judgement from the sheet alone. State: good for fringe, partial
   for expansion. Issues: `A4`, `A5`, `S2`, `S3`.
4. `Entry.` `tools/assign.py add` and `add-fringe` write the pool, with refusals for unknown papers, papers without an
   embedding and non-canonical IDs. `tools/check.py` enforces integrity: unique IDs, no duplicate titles, and no
   `CorpusId` row for an arXiv paper. State: sound. Issue: `M2`, at the edge.
5. `Metadata.` `tools/pool.py` fetches year, citations, references and embeddings by script, and the `Pool` line is
   checked against `pool.json`. State: sound.
6. `The gate.` `G1` checks that records exist. For the fringe routes it checks completeness: every candidate has a
   judged row, and every `yes` is in the pool or Open work. For expansion it checks one traversal per frontier
   candidate, in any direction, and one rejection from any step. State: thorough for fringe, thin for expansion. Issues:
   `C1`, `T1`, `T2`.

What no link does: audit whether scope verdicts are right. `docs/gates.md:133-134` says so openly. There is no sample
re-screening, as there is a sample re-verification at step 7. Given `A4` and `A5`, scope is the judgement in step 2 most
likely to drift between agents, and the one whose errors leave the least trace.

## Part (c): readiness for the next run

The next run is a real run of step 2 on `inputs/model-collapse.md`.

### Blocking: fix before the run

- `A2` — the first expansion has no split and no cap. As specified, one agent must take about 440,000 tokens of tool
  results. Decide how the work is divided across sequential agents, or how it is bounded, before dispatching.
- `A1` — state how an agent obtains a canonical ID from Asta's results (the `externalIds` field, or a tool that accepts
  Semantic Scholar IDs). Without it, every add and reject depends on improvisation.
- `M1` — decide how forward traversal handles a paper with more than 100 citers, and how the log records a truncated
  traversal. The two seeds of the example input have 551 and 182 citers.

### Strongly advised

- `A4` — remove or reword the "earn its place in a role" sentence in the agent definition before any screening runs.
- `A5` — settle with the user, in the input, whether detection, watermarking and curation papers motivated by model
  collapse are in scope. Otherwise the pool's size depends on which agent screens.
- `S5` — have the Expand agent write the `Expansion` line part by part as it goes, so that a dead agent leaves a
  resumable record.
- `C1` and `T1` — make `G1` check what the done-when requires: backward traversal, a query per theme, and the seeds.
- `S1` — say whether forward traversal from the seeds is required work.
- `A3` — give the counts a source other than the agent's counting, or drop the rule for these counts.
- `A6` and `A9` — define the stopping rule's batch, and say whether the input's search instructions bind step 2.
- `C3` — make `tools/fringe.py judge` apply the two-word test, so that the fringe screening agent learns of it while it
  is still running.

## Checked and found to hold

- `tools/assign.py add` refuses a non-canonical ID, a paper unknown to Semantic Scholar, a paper without a SPECTER2
  embedding, and a `CorpusId` whose paper has an arXiv ID, and lists each for Open work (`tools/assign.py:180-212`). It
  matches `docs/tooling.md:104-108`.
- `tools/assign.py reject` validates every stdin line before writing any, refuses a pool paper with `H12`, and skips a
  repeat on the same day (`tools/assign.py:394-442`). The behaviour tests cover it.
- `tools/assign.py add-fringe` refuses while any row is unjudged, using the gate's own test, and refuses rows not in
  `fringe.json` (`tools/assign.py:215-239`). Its `Fringe` line matches the template at `docs/formats.md:198-199`, and
  `g1.fringe-line` checks the parts that can drift.
- `tools/fringe.py collect` excludes rejected papers by either canonical ID (`tools/fringe.py:170`). It hides route,
  year and citation counts from the sheet, and seeds the `new` route deterministically from the `Orientation` line, as
  `docs/process.md:284-294` and `docs/tooling.md:147-153` describe.
- `tools/pool.py` fetches only new papers, saves after each batch, and prints a `Pool` line that `g1.pool-line` checks
  against `pool.json` (`tools/pool.py:158-182`; `tools/gates.py:377-387`).
- `g1.errored` requires a retry outcome for every errored query, and `H2` for one that still failed
  (`tools/gates.py:256-269`). This matches `docs/external_services.md:86-91`.
- The single-writer rule for the pool is consistent across `docs/dispatch.md:49-51`, `docs/dispatch.md:114` and the
  order of operations.
- The fringe screening sheet is affordable: about 120 rows at up to 700 characters of abstract each is roughly 25,000
  tokens. That agrees with the 30,000 tokens in `docs/formats.md:447`.
- Backward traversal itself is cheap to list: both seed papers have 30 references (calls 2 and 3), at about 20 tokens
  per reference entry.
- Asta accepts `ARXIV:` IDs and returns the requested fields, as `docs/external_services.md:65-67` says.
- `inputs/model-collapse.md` parses cleanly, with its `expect` and four `exclude` themes read as intended.
- Both gate test suites pass: 84 of 84 faults, and 49 of 49 behaviours.

## Appendix A: the cost of step 2's required work on the example input

The computation behind `A2`. Measured values come from the outside calls listed in "Scope and method". Assumed values
are marked `UNVERIFIED`.

Measured:

- A citer record with its abstract, as `get_citations` returns it, is about 1,450 characters. Two records came to about
  2,900. At four characters per token, that is about 360 tokens per record.
- A reference entry, with `paperId` and title only, is about 85 characters, or about 20 tokens.
- The seeds have 551 citers (`2305.17493`) and 182 citers (`2404.01413`), and 30 references each.

Assumed, `UNVERIFIED`:

- 10 frontier candidates, each with about 40 references and about 20 citers, since most are recent.
- 8 themes in `Orientation`, each searched once at Asta's default of 50 results.
- A search result, or a batch-fetched abstract, costs about the same 360 tokens as a citer record.

The required work, by the done-when at `docs/process.md:63` and the prose at `docs/process.md:222`:

| part | records | tokens |
| -- | -- | -- |
| backward: reference lists, titles only | 10 × 40 = 400 | 400 × 20 ≈ 8,000 |
| backward: abstracts for screening, by a second call | 400 | 400 × 360 ≈ 144,000 |
| forward from the seeds, at the default limit of 100 | 2 × 100 = 200 | 200 × 360 ≈ 72,000 |
| forward from the frontier candidates | 10 × 20 = 200 | 200 × 360 ≈ 72,000 |
| relevance searches, one per theme | 8 × 50 = 400 | 400 × 360 ≈ 144,000 |
| total | about 1,200 | about 440,000 |

Without the default limit, the seeds alone give 551 + 182 = 733 citers, or about 264,000 tokens. The total then rises to
about 632,000 tokens.

Overlap between traversals does not reduce this. Each tool returns its whole result whether or not the agent has seen a
paper before. These figures are tool results only. They leave out the agent's reading of the spec, its reasoning, and
its calls to `tools/assign.py`.

The result is about 440,000 tokens in one agent's context, under a brief that allows one Expand agent at a time. That is
more than twice a 200,000-token context window. The context window of the `survey-pass` model is `UNVERIFIED`.

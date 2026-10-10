# R4: arms A and B against the reference C

Scored by the main session after arm C was recorded, knowing which arm wrote each file: the scoring is not blind. Each "item" is one finding of arm C on a paper: a corrected cell,
a limitation or condition, or another finding. An arm scores 1 if its file states the same finding, 0.5 if it states
part of it, 0 if it does not. Findings an arm made that C did not are listed as extras; they are not scored, since C is
a reference, not ground truth.

## Per paper

### 2603.21676 (15 items)

- A 15/15. B 14/15: misses only the stale `snippet_search` note in the draft.
- Extras: A, no accuracy comparison against token chain-of-thought; the out-of-range depth-embedding check (5.2). B,
  caught a hallucinated limitation in its locator's map ("Claude Sonnet 3.5" minigames, not in this paper) and
  discarded it.

### 2601.23086 (16 items)

- A 15/16: misses that the prompts and XML tags were made salient for small models.
- B 13.5/16: misses obfuscation arising with no penalty in 2 runs, and the exclusion of failed runs and parse failures;
  states the out-of-format test's scope only in part.
- Disagreement on a cell: A and B both set `pressure` to `monitor-in-reward`; C kept `training-incidental` for the
  headline (summary-penalty) condition. The definition admits both readings; it is a judgement call, not a miss.
- Extras: A, the overseer penalty is small and applies only to successful hacks; monitor prompts were iterated. B, the
  obfuscation strategies; safety training breaking through as a post-answer warning.

### 2605.06367 (16 items)

- A 14.5/16: misses the Trouser exception to the variance ordering; says only in part that the DDPM check covers
  memorisation gaps alone.
- B 14/16: misses the Trouser exception and the memorisation-threshold robustness check.
- Extras, both: the scaling assumptions on centroids and variances; strong imbalance must scale with N; the
  generalisation-memorisation trade-off of Result 3. A: the centroid check on DDPM uses a filtered subset.
- B's locator map had wrong line numbers throughout (its "L393–403" limitations are at L261); B found the passages by
  content.

### 2608.20256 (13 items)

- A 13/13.
- B 10.5/13: misses the out-of-distribution routing split being inferred from length, and the flattened phase-2
  reward with the balance term annealed; says only in part that GSM8K accuracy falls below the base.
- Extras: B, savings erode as Long lengthens; Long-only training alone beats the base, so part of the gain is training,
  not routing; hand-set reward constants. A, the AIME reduction is 12% in the text and 13% in the table.
- B's locator map gave `measures: monitorability`, wrong for this paper; B did not use it.

### 2608.13545 (17 items)

- A 14.5/17: misses the 88B/80B inconsistency and that the smallest model beats the control in scope; says only that the
  post-training null is budget-bound, not that post-training helps a little.
- B 14/17: misses the Gemini-rewritten cooldown data, the tokenisation ablation, and the Grade 8 inconsistency.
- Extras: A, post-training depends on chat data folded into pretraining; the draft omits the scaling probe. B,
  out-of-scope answers are confident confabulations; Grade 6 does not separate the models.

### 2608.29188 (18 items)

- A 13.5/18: misses the Shapley split (65.5% of the solve-probability gain is execution), the weak recovery of the deep
  access tail (0.087), GRPO re-collapsing after SFT, and that the 67% drop is measured from step 50 because the base
  model is under 3% format-valid; gives the PPO configuration but not its single seed.
- Extras: A, checkpoint sampling's coverage gain costs pass@1 (0.161 vs 0.278); the interventions are scored on 100
  problems; Countdown leaves only 6–10 tokens after the entrance, which favours the entrance account.
- B 14.5/18: misses the Shapley split, the deep access tail, and GRPO re-collapsing after SFT; gives the PPO
  configuration but not its seed. Found the step-50 baseline, which A missed.
- Extras: B, no decoding setting reaches step-50 coverage; the mechanism rests on a first-order surrogate; the draft omits
  entrance-budgeted allocation.
- B's locator map held two passages from other papers in its batch (a KV-cache memory claim and "most suspicious 1% of
  commits will be reviewed"); B found they were not at the mapped lines and ignored them.

### 2609.01274 (18 items)

- A 15.5/18: misses the GPQA readout caliber (±3–4 pp across batches) and that every RL target already has several Base
  matches within ±3 pp, so the rule selects rather than discovers; states the four unrecoverable self-consistency cells
  only in general terms.
- Extras: A, the three-seed replication varies decoding seeds on a fixed policy pool, not pools or recipes.
- B 15/18: misses the same three as A, and the unrecoverable cells entirely.
- Extras: B, the anchor cell alone cost about 461 H100 GPU-hours; AIME's policy pool has 6 policies. Most of the map's
  line numbers were wrong; B relocated every passage by content.

### 2609.08650 (16 items)

- A 14.5/16: misses the 1024-token training generations and that the strongest baseline differs by model (on Qwen3-4B
  plain GRPO beats AttnRL); states the Section 2 setup difference only as "setup-specific".
- Extras: A, no large-k pass@k against the base, so the create-versus-select crossover is untested; out-of-domain gains
  small and mixed; the forking ablation's pass@8 differences are within a point.
- B 12.5/16: misses the wall-clock cost (2.3x GRPO), the 1024-token training generations, and the different setup of
  the Section 2 analysis; does not mention the out-of-domain evaluation. Found the strongest-baseline point, as C did.
- Extras: B, DATPO is not best on every benchmark (MATH500 pass@8, AMC23 avg@64); maj@k is compared with the method's
  own avg@k, not against baselines; the training-dynamics attribution has no ablation. B read beyond the map (Table 2),
  because the map gave no k values or per-baseline numbers.

## Totals

| arm | items found (of 129) | share | tokens per row | model |
| -- | -- | -- | -- | -- |
| A: section reader and Grep | 115.5 | 90% | about 26k (577k over 22 rows with known counts) | strong |
| B: locator map, then targeted reading | 108 | 84% | about 35k (Haiku, 948k over 27 rows) plus about 27k strong (272k over 10 rows) | Haiku + strong |
| C: whole paper, the reference | 129 by definition | — | about 31k read, 3k written | main session |

Per paper, A scored higher than B on 7 of the 8 papers, and B higher on one (2608.29188).

What A missed was mostly in appendices or footnotes: 9.5 of its 13.5 missed items. Examples: the Shapley split, the
deep access tail, the re-collapse after SFT and the single seed in 2608.29188; the GPQA caliber and the unrecoverable
cells in 2609.01274; the Trouser exception in 2605.06367; the training generation length in 2609.08650; the prompt
saliency in 2601.23086. The rest were in main-text tables or asides.

What B missed overlapped with A's misses and added main-text conditions its map did not point to (the
out-of-distribution routing proxy and the flattened phase-2 reward in 2608.20256; the Gemini rewrites, the tokeniser
ablation and the Grade 8 inconsistency in 2608.13545; the wall-clock cost in 2609.08650). Its readers repeatedly
read beyond or around the map, because the map's line numbers were wrong (3 of 8 maps), it held passages from other
papers (1 map) or a hallucinated limitation (1 map), or it lacked the numbers a cell needed (1 map).

Each arm also found real things the reference missed (the extras above), so C is a reference, not ground truth.

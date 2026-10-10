# R4 token log (from the task notifications)

| arm | agent | papers | tokens | tool uses | minutes |
| -- | -- | -- | -- | -- | -- |
| B locator (Haiku) | 4 | 2504.17704 2608.00583 2609.04518 | 72575 | 19 | 1.8 |
| B locator (Haiku) | 9 | 2603.12163 2608.25593 2609.19465 | 130084 | 20 | 2.1 |
| B locator (Haiku) | 6 | 2510.15020 2608.20256 2609.09030 | 94392 | 20 | 2.1 |
| B locator (Haiku) | 1 | 2410.21514 2603.21676 2608.29188 | 125019 | 16 | 2.1 |
| B locator (Haiku) | 3 | 2503.24235 2605.06367 2609.01274 | 111093 | 25 | 2.4 |
| B locator (Haiku) | 8 | 2601.23086 2608.24949 2609.15989 | 79559 | 25 | 2.4 |
| B locator (Haiku) | 2 | 2502.05171 2603.30036 2608.29464 | 100601 | 21 | 2.5 |
| B locator (Haiku) | 5 | 2507.14417 2608.13545 2609.08650 | 105099 | 16 | 2.5 |
| B locator (Haiku) | 7 | 2512.18311 2608.20290 2609.13997 | 129977 | 24 | 3.0 |
| A (strong) | 4 | 2504.17704 2601.23086 2605.06367 2608.20290 2608.29464 2609.09030 | 149049 | 33 | 4.7 |
| A (strong) | 2 | 2502.05171 2510.15020 2603.21676 2608.13545 2608.25593 2609.04518 2609.15989 | 171246 | 57 | 5.8 |

Arm C (the main session, whole papers) was recorded in full before any arm A or B output was opened. Its reading cost,
from the Read tool's own counts where it gave them and characters / 4 otherwise: 2608.20256 ~12k, 2603.21676 ~17k,
2608.13545 ~19k, 2601.23086 ~29k plus the checklist by grep, 2609.08650 ~39k, 2608.29188 ~40k, 2609.01274 ~42k,
2605.06367 ~45k of 87k (Appendix F skimmed); about 245k input tokens for 8 papers, ~31k per paper, plus ~3k written per
paper.

`subagent_tokens` is the figure the harness reports per agent; whether it counts cached re-reads of the context is
UNVERIFIED, so it is comparable across arms but is not a bill.
| A (strong) | 1 | 2410.21514 2507.14417 2603.12163 2608.00583 2608.24949 2609.01274 2609.13997 | 188686 | 58 | 7.1 |
| A (strong) | 3 | 2503.24235 2512.18311 2603.30036 2608.20256 2608.29188 (+2 unfinished) | unknown: stopped by the spend limit | — | — |
| A (strong) | 3 rerun | 2609.08650 2609.19465 | 67929 | 20 | 2.3 |
| B reader | 1–4 | 13 of 27 written before the spend limit stopped all four | unknown | — | — |
| B reader | rerun 2 | 2609.08650 2609.09030 2609.13997 2609.15989 2609.19465 | 133857 | 27 | 4.7 |
| B reader | rerun 1 | 2608.24949 2608.29188 2608.29464 2609.01274 2609.04518 | 138080 | 37 | 5.5 |

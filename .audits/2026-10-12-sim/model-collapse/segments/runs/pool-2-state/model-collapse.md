# Model collapse

## Retrieval log

### Pass 2026-10-12

- **Gates:** G0 2026-10-12, G1 2026-10-13
- **Preflight:** snippet_search ok | search_papers_by_relevance ok | get_paper ok | get_citations ok | WebSearch ok |
  Graph API ok (429, busy) | arXiv ok | uv ok | Asta key set
- **Orientation (WebSearch):** "model collapse generative models trained on synthetic data arXiv", "self-consuming
  generative models loop arXiv", "model autophagy disorder self-consuming generative models go MAD", "iterative
  retraining generative models on their own data stability theory", "model collapse mitigation accumulate real data
  verification synthetic data", "model collapse language models scaling laws synthetic data strong model collapse",
  "recursive training language models loss of tails diversity linguistic collapse", "is model collapse inevitable web
  data partly AI-generated debate", "model collapse arXiv 2026 new paper recursive training synthetic data",
  "self-consuming loop generative models 2026 arXiv theory", "model collapse ICML 2026 OR NeurIPS 2026 synthetic data
  feedback loop", "\"model collapse\" diffusion models iterative retraining 2026", "detecting AI-generated text in
  pretraining data to prevent model collapse 2026", "model collapse large language models fine-tuning generations
  synthetic text arXiv 2606 OR 2607 OR 2608", "openreview model collapse synthetic data recursion 2026 submission",
  "recursive training vision-language models image generators collapse 2026 study", "\"AI models collapse when trained
  on recursively generated data\" Nature preprint \"The Curse of Recursion\" arXiv 2305.17493 version", "synthetic data
  feedback loop generative model degradation generations new preprint September 2026", "AI autophagy recursive training
  LLM collapse study 2026", "model collapse real data ratio theorem new arXiv paper August 2026", "\"model collapse\"
  text-to-image OR speech OR multimodal recursive generations preprint 2026 mitigation curation"; themes: "model
  collapse", "self-consuming generative models", "model autophagy", "recursive retraining", "iterative retraining",
  "self-consuming training loops", "AI autophagy", "accumulating real and synthetic data", "synthetic data verification
  model collapse", "curated self-consuming retraining", "machine-generated text detection model collapse", "strong model
  collapse", "model collapse scaling laws", "linguistic diversity decline synthetic text", "knowledge collapse",
  "recursive training diffusion models", "networked self-consuming generative models"; seeds from the input: 2305.17493,
  2404.01413; frontier candidates: 2605.04127, 2605.07724, 2605.20602, 2606.13732, 2606.13796, 2606.28438, 2607.09705,
  2607.17043, 2609.12353, CorpusId:292022319, 2609.18560, 2609.18878, 2610.09409, 2610.09415
- **Expansion:** backward from 2305.17493 (27), 2404.01413 (29), 2605.04127 (100), 2605.07724 (51), 2605.20602 (21), 2606.13732 (79), 2606.13796 (72), 2606.28438 (54), 2607.09705 (1), 2607.17043 (35), 2609.12353 (52), CorpusId:292022319 (41), 2609.18560 (104), 2609.18878 (18), 2610.09409 (41), 2610.09415 (62); forward from 2305.17493 (551), 2404.01413 (182), 2605.04127 (1), 2605.07724 (0), 2605.20602 (0), 2606.13732 (0), 2606.13796 (0), 2606.28438 (2), 2607.09705 (0), 2607.17043 (1), 2609.12353 (0), CorpusId:292022319 (0), 2609.18560 (0), 2609.18878 (0), 2610.09409 (1), 2610.09415 (1); queries "model collapse" (50 of 931), "self-consuming generative models" (12 of 12), "model autophagy" (50 of 114), "recursive retraining" (8 of 8), "iterative retraining" (50 of 105), "self-consuming training loops" (6 of 6), "AI autophagy" (5 of 5), "accumulating real and synthetic data" (1 of 1), "synthetic data verification model collapse" (0 of 0), "curated self-consuming retraining" (0 of 0), "machine-generated text detection model collapse" (0 of 0), "strong model collapse" (2 of 2), "model collapse scaling laws" (0 of 0), "linguistic diversity decline synthetic text" (0 of 0), "knowledge collapse" (24 of 24), "recursive training diffusion models" (0 of 0), "networked self-consuming generative models" (1 of 1); 1376 unique, left out: in the pool 64, rejected earlier 7, on the sheet already 0, another record 3, not found 0; 74 without a paper ID; screened 1302: in scope 141, rejected 1161
- **Errored queries:** none
- **Recency window:** 2026-04-13 to 2026-10-13, applied to the recency queries only. WebSearch has no date filter, so
  the recency queries are the ones that name 2026 or a 2026 month; a candidate counts as inside the window by its
  Semantic Scholar publication date
- **Fringe:** collected 2026-10-13: hidden 60, new 60 candidates (120 unique); in scope 19; added to the pool 19, of which 11 without an arXiv ID; left out 0
- **Pool:** 224 papers in scope, 177 with an arXiv ID; metadata fetched 2026-10-13
- **Dimensions:** declared in the input
- **Tokens:** Preflight: 39077, Orient: 183098, Screening expand 1-100: 68054, Screening expand 101-200: 67011,
  Screening expand 201-300: 63472, Screening expand 301-400: 74070, Screening expand 401-500: 65967, Screening expand
  501-600: 85206, Screening expand 601-700: 81248, Screening expand 701-800: 72512, Screening expand 801-900: 73176,
  Screening expand 901-1000: 75800, Screening expand 1001-1100: 80318, Screening expand 1101-1200: 90594, Screening
  expand 1201-1300: 70807, Screening expand 1301-1302: 33562, Screening expand 1015 rejudged: 48291, Screening fringe 1-60: 63324,
  Screening fringe 61-120: 66568
- **Halts:** H3 — `tools/expand.py collect` failed twice after its retries with "the Graph API failed after its
  retries (HTTP Error 429: )", after all 32 seed and frontier traversals were saved, leaving the theme searches and
  the rest of step 2 (screening, add-expand, fetch, fringe routes, fetch again, G1) undone — continue, with
  `tools/expand.py` changed to search each theme on the bulk search endpoint, which answers, 2026-10-13; H12 —
  `tools/assign.py add-expand` reported 2308.07462 "judged `no` on the sheet but in the pool", since its two records
  were judged apart (expand-screen row 965 `yes`, row 1015 `no`), and row 1015, re-judged, stays `no` (a single
  comparison of ChatGPT and human vocabulary, citing model collapse as motivation), leaving the rest of step 2 (fetch
  pool data, fringe routes, fetch again, G1) undone — keep 2308.07462 in the pool, by "borderline is in", and re-judge
  row 1015 `yes`, 2026-10-13
- **Waivers:** none

## Clusters

## Coreset

## Pool

| paper | year | cluster | citations | cites |
| -- | -- | -- | -- | -- |
| [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) | 2023 |  | 551 |  |
| [Is Model Collapse Inevitable? Breaking the Curse of Recursion by Accumulating Real and Synthetic Data](https://arxiv.org/abs/2404.01413) | 2024 |  | 182 | 2209.03942 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.16822 2402.07712 |
| [Self-Consuming Generative Models with Co-Evolving Human Preferences](https://arxiv.org/abs/2610.09415) | 2026 |  | 1 | 2209.03942 2307.01850 2310.00429 2402.07043 2402.07087 2404.01413 2404.05090 2405.08027 2407.09499 2412.17646 2502.18865 2505.09768 2510.16657 2511.09002 2511.12742 2601.05184 2605.04266 2605.29267 2610.09409 |
| [Stability and Diversity of Networked Self-Consuming Generative Ecosystems](https://arxiv.org/abs/2610.09409) | 2026 |  | 1 | 2209.03942 2305.17493 2307.01850 2310.00429 2402.07043 2402.07087 2403.07857 2404.01413 2404.05090 2405.08027 2407.09499 2408.16333 2411.13852 2412.17646 2412.18148 2502.18865 2503.08117 2504.03814 2505.09768 2505.21677 2510.16657 2511.12742 2601.05184 2605.29267 2610.09415 CorpusId:270380115 |
| [Self-Training Doesn't Flatten Language - It Restructures It: Surface Markers Amplify While Deep Syntax Dies](https://arxiv.org/abs/2605.20602) | 2026 |  | 0 | 2307.01850 2311.16822 2402.07043 2403.07183 2404.01413 2404.05090 2406.07016 2410.12954 2507.03933 CorpusId:285804007 |
| [Curated Synthetic Data Doesn't Have to Collapse: A Theoretical Study of Generative Retraining with Pluralistic Preferences](https://arxiv.org/abs/2605.07724) | 2026 |  | 0 | 2305.17493 2307.01850 2404.01413 2407.09499 2511.09002 2511.12804 |
| [Preventing Model Collapse: A Fisher-Rao Perspective on the Dynamics of Training with Synthetic Data](https://arxiv.org/abs/2609.18878) | 2026 |  | 0 | 2307.01850 2311.16822 2404.01413 2404.02305 2404.02325 2406.07515 CorpusId:284724154 |
| [Position: the Stochastic Parrot in the Coal Mine. Model Collapse is a Threat to Low-Resource Communities](https://arxiv.org/abs/2605.04127) | 2026 |  | 1 | 2003.12694 2305.17493 2307.01850 2310.00429 2311.12202 2402.07043 2402.07712 2403.07857 2404.01413 2404.05090 2410.04840 2410.15234 2410.16713 2412.14689 2501.03937 2503.03150 2504.08755 CorpusId:270380115 CorpusId:287992263 CorpusId:6567063 CorpusId:7123287 |
| [Model Collapse: On Recursion, Noise, and Uncharted Machine Visions](https://arxiv.org/abs/2607.09705) | 2026 |  | 0 |  |
| [When Sample Selection Bias Precipitates Model Collapse](https://arxiv.org/abs/2606.13732) | 2026 |  | 0 | 2002.05715 2209.03942 2211.08095 2305.17493 2307.01850 2310.00429 2402.07712 2403.07857 2404.01413 2404.03242 2406.07515 2407.09499 2410.04840 2410.16713 2410.22812 2503.03150 2505.09768 2509.16499 2510.16657 2511.03492 2605.04127 |
| [Recursively Trained Diffusion Models: Limiting Collapse Distribution and Spectral Characterization](https://arxiv.org/abs/2606.13796) | 2026 |  | 0 | 2305.17493 2307.01850 2310.00429 2402.07043 2402.07712 2402.11778 2404.01413 2408.16333 2410.04840 2410.22812 2412.08175 2501.03937 2505.19046 2509.16499 2509.22341 2602.16601 |
| [Learning from Synthetic Data without Model Collapse in Iterative Instruction Tuning](https://arxiv.org/abs/2607.17043) | 2026 |  | 1 | 2305.17493 2402.07043 2402.07712 2406.07515 2410.16713 2412.14689 2502.08924 2502.15654 2601.15468 |
| [SynthSentry: Detecting Synthetic Data Contamination in Language Model Training Data](https://arxiv.org/abs/2609.12353) | 2026 |  | 0 | 2305.17493 2306.06130 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07087 2402.07712 2402.11778 2404.01413 2405.13977 2406.07515 2407.05013 2407.09499 2408.16333 2502.18865 2509.04796 2509.22341 2510.16657 2511.03492 2605.23054 2606.28438 CorpusId:287661814 |
| [Reviewing Model Collapse and Countermeasures](https://arxiv.org/abs/2608.21366) | 2026 |  | 0 | 2211.08095 2305.17493 2307.01850 2310.00429 2402.07043 2402.07712 2404.05090 2410.04840 2412.08175 2505.08803 |
| [Quantifying Error Propagation and Model Collapse in Diffusion Models](https://arxiv.org/abs/2602.16601) | 2026 |  | 4 | 2307.01850 2310.00429 2402.07043 2402.07712 2402.11778 2404.01413 2407.17493 2408.16333 2410.04840 2410.22812 2412.08175 2412.17646 2501.03937 2505.19046 2505.21677 2509.16499 2509.22341 |
| [Position: Model Collapse Does Not Mean What You Think](https://arxiv.org/abs/2503.03150) | 2025 |  | 38 | 2209.03942 2305.17493 2306.06130 2307.01850 2310.00429 2311.12202 2311.16822 2402.07043 2402.07087 2402.07712 2403.07857 2404.01413 2404.02325 2404.05090 2410.04840 2410.16713 2410.22812 2412.14689 2412.17646 CorpusId:271447829 |
| [Language Generation with Replay: A Learning-Theoretic View of Model Collapse](https://arxiv.org/abs/2603.11784) | 2026 |  | 6 | 2305.17493 2306.06130 2307.01850 2310.00429 2311.12202 2311.16822 2402.07043 2402.07712 2402.11778 2404.01413 2404.02325 2404.05090 2406.07515 2407.12835 2410.04840 2410.22812 2412.17646 2501.19273 2502.18865 2505.19046 2509.25135 |
| [Learning from Synthetic Data: Limitations of ERM](https://arxiv.org/abs/2601.15468) | 2026 |  | 4 | 2211.08095 2307.01850 2310.00429 2404.01413 2404.05090 2406.07515 2407.09499 2410.08942 2410.16713 2410.22812 2412.17646 2501.19273 2502.08924 2505.19046 |
| [A Note on Shumailov et al. (2024): 'AI Models Collapse When Trained on Recursively Generated Data'](https://arxiv.org/abs/2410.12954) | 2024 |  | 216 |  |
| [Recursive Learning Without Collapse: A Weighting-Based Stabilization Framework](https://arxiv.org/abs/2502.18049) | 2025 |  | 9 | 2305.17493 2307.01850 2310.00429 2402.07043 2402.07712 2404.01413 2410.04840 2410.16713 2410.22812 |
| [Multi-modal Synthetic Data Training and Model Collapse: Insights from VLMs and Diffusion Models](https://arxiv.org/abs/2505.08803) | 2025 |  | 6 | 2307.01850 2404.05090 |
| [Collapse or Thrive? Perils and Promises of Synthetic Data in a Self-Generating World](https://arxiv.org/abs/2410.16713) | 2024 |  | 61 | 2002.05715 2209.03942 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07087 2402.07712 2404.01413 2404.02325 2404.03242 2404.05090 2407.09499 2410.22812 |
| [A Closer Look at Model Collapse: From a Generalization-to-Memorization Perspective](https://arxiv.org/abs/2509.16499) | 2025 |  | 22 | 2307.01850 2310.00429 2311.12202 2402.07043 2402.07712 2402.11778 2403.07857 2404.01413 2404.05090 2406.07515 2407.09499 2407.17493 2408.16333 2410.04840 2410.16713 2410.22812 2412.08175 2412.14689 2412.17646 2502.09963 2502.18865 2503.03150 |
| [Escaping Model Collapse via Synthetic Data Verification: Near-term Improvements and Long-term Convergence](https://arxiv.org/abs/2510.16657) | 2025 |  | 7 | 2307.01850 2310.00429 2402.07043 2402.07712 2402.11778 2404.01413 2406.07515 2407.09499 2407.12835 2410.04840 2410.16713 2410.22812 2412.14689 2412.17646 2502.08924 2502.18049 2502.18865 2503.03150 2505.09768 2505.13947 2505.19046 2509.22341 |
| [Self-Correcting Self-Consuming Loops for Generative Model Training](https://arxiv.org/abs/2402.07087) | 2024 |  | 41 | 2305.17493 2306.06130 2307.01850 2310.00429 |
| [Self-Consuming Generative Models with Adversarially Curated Data](https://arxiv.org/abs/2505.09768) | 2025 |  | 12 | 2209.03942 2307.01850 2310.00429 2402.07087 2403.07857 2404.01413 2404.03242 2405.08027 2407.09499 2408.16333 |
| [Self-Consuming Generative Models Go MAD](https://arxiv.org/abs/2307.01850) | 2023 |  | 371 | 2211.08095 2303.01255 2305.17493 2306.06130 2306.07899 |
| [Towards Theoretical Understandings of Self-Consuming Generative Models](https://arxiv.org/abs/2402.11778) | 2024 |  | 37 | 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.16822 |
| [Improving Fairness and Mitigating MADness in Generative Models](https://arxiv.org/abs/2405.13977) | 2024 |  | 6 | 2307.01850 2311.16822 |
| [On the Stability of Iterative Retraining of Generative Models on their own Data](https://arxiv.org/abs/2310.00429) | 2023 |  | 122 | 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 |
| [Convergence Dynamics and Stabilization Strategies of Co-Evolving Generative Models](https://arxiv.org/abs/2503.08117) | 2025 |  | 2 | 2209.03942 2303.01255 2306.06130 2307.01850 2310.00429 2311.09807 2311.12202 2402.07043 2402.07087 2402.07712 2403.07857 2404.01413 2404.02325 2404.03502 2407.09499 2412.17646 CorpusId:270380115 |
| [Self-Improving Diffusion Models with Synthetic Data](https://arxiv.org/abs/2408.16333) | 2024 |  | 44 | 2307.01850 2310.00429 2402.07043 2402.07087 2402.07712 2403.07857 2404.01413 CorpusId:270380115 |
| [Strong Model Collapse](https://arxiv.org/abs/2410.04840) | 2024 |  | 75 | 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.16822 2402.07043 2402.07087 2402.07712 2404.05090 2407.09499 2407.12835 2408.16333 CorpusId:270380115 |
| [Beyond Model Collapse: Scaling Up with Synthesized Data Requires Verification](https://arxiv.org/abs/2406.07515) | 2024 |  | 51 | 2002.05715 2203.12788 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.16822 2402.07043 2402.07087 2402.07712 2404.05090 2407.12835 2408.16333 |
| [The Curious Decline of Linguistic Diversity: Training Language Models on Synthetic Text](https://arxiv.org/abs/2311.09807) | 2023 |  | 152 | 2305.17493 2307.01850 |
| [Knowledge Collapse in LLMs: When Fluency Survives but Facts Fail under Recursive Synthetic Training](https://arxiv.org/abs/2509.04796) | 2025 |  | 2 | 2402.07043 2403.07857 2404.01413 2404.03502 2404.05090 2407.12835 2410.04840 2410.15234 2410.16713 CorpusId:270380115 |
| [Rate of Model Collapse in Recursive Training](https://arxiv.org/abs/2412.17646) | 2024 |  | 27 | 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2402.07043 2402.07712 2404.01413 2404.02325 2404.05090 2407.12835 |
| [A Tale of Tails: Model Collapse as a Change of Scaling Laws](https://arxiv.org/abs/2402.07043) | 2024 |  | 160 | 2002.05715 2203.12788 2211.08095 2303.01255 2305.17493 2306.06130 2306.07899 2307.01850 2310.00429 2311.09807 2311.16822 2402.07712 |
| [How Bad is Training on Synthetic Data? A Statistical Analysis of Language Model Collapse](https://arxiv.org/abs/2404.05090) | 2024 |  | 99 | 2305.17493 2307.07367 2311.16822 2402.07043 2402.07712 2402.11778 |
| [A Probabilistic Perspective on Model Collapse](https://arxiv.org/abs/2505.13947) | 2025 |  | 6 |  |
| [Understanding Hallucinations in Diffusion Models through Mode Interpolation](https://arxiv.org/abs/2406.09358) | 2024 |  | 123 | 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.16822 2402.07043 2402.11778 2404.01413 |
| [A Theoretical Perspective: How to Prevent Model Collapse in Self-consuming Training Loops](https://arxiv.org/abs/2502.18865) | 2025 |  | 23 | 2306.06130 2307.01850 2310.00429 2311.16822 2402.07043 2402.07087 2402.07712 2402.11778 2403.07857 2404.01413 2404.02325 2404.05090 2406.07515 2407.09499 2408.16333 2410.04840 2501.19273 CorpusId:270380115 CorpusId:276282656 |
| [Model Collapse in the Self-Consuming Chain of Diffusion Finetuning: A Novel Perspective from Quantitative Trait Modeling](https://arxiv.org/abs/2407.17493) | 2024 |  | 12 | 2209.03942 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07087 2402.07712 2402.11778 2404.01413 2404.02325 2406.07515 2407.09499 2408.16333 2410.04840 2412.14689 2502.08924 2502.18865 |
| [When Models Don't Collapse: On the Consistency of Iterative MLE](https://arxiv.org/abs/2505.19046) | 2025 |  | 11 | 2211.08095 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07712 2402.11778 2404.01413 2404.02325 2404.05090 2406.07515 2407.09499 2410.04840 2410.16713 2410.22812 2502.08924 2502.18049 2502.18865 2503.03150 |
| [Model Collapse Demystified: The Case of Regression](https://arxiv.org/abs/2402.07712) | 2024 |  | 96 | 2002.05715 2209.03942 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.16822 2402.07043 2402.07087 CorpusId:270380115 |
| [ForTIFAI: fending off recursive training induced failure for AI model collapse](https://arxiv.org/abs/2509.08972) | 2025 |  | 2 | 2305.17493 2307.01850 2402.07043 2404.01413 2408.16333 2410.04840 2502.15654 2503.03150 |
| [Nepotistically Trained Generative-AI Models Collapse](https://arxiv.org/abs/2311.12202) | 2023 |  | 38 | 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 |
| [Machine-generated text detection prevents language model collapse](https://arxiv.org/abs/2502.15654) | 2025 |  | 21 | 2305.17493 2307.01850 2310.00429 2311.09807 2311.16822 2402.07043 2404.01413 2408.16333 2410.12954 2412.14689 CorpusId:270380115 |
| [Learning by Surprise: Adaptive Mitigation of Model Collapse in Large Language Models](https://arxiv.org/abs/2410.12341) | 2024 |  | 1 | 2211.08095 2303.01255 2306.06130 2306.13723 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07712 2404.01413 2404.05090 2406.07515 2410.12954 2412.14689 2412.17646 2502.15654 2502.18865 2503.03150 2504.03814 CorpusId:276282656 |
| [How to Synthesize Text Data without Model Collapse?](https://arxiv.org/abs/2412.14689) | 2024 |  | 27 | 2002.05715 2306.06130 2307.01850 2310.00429 2311.16822 2402.07043 2402.07712 2404.01413 2404.05090 2406.07515 2407.09499 2410.04840 2410.16713 |
| [Synthetic Eggs in Many Baskets: The Impact of Synthetic Data Diversity on LLM Fine-Tuning](https://arxiv.org/abs/2511.01490) | 2025 |  | 1 | 2307.01850 2311.09807 2402.07043 2410.12954 2503.03150 |
| [Self-Consuming Generative Models with Curated Data Provably Optimize Human Preferences](https://arxiv.org/abs/2407.09499) | 2024 |  | 43 | 2211.08095 2303.01255 2305.17493 2307.01850 2310.00429 2311.16822 2402.07043 2402.07087 2402.07712 2403.07857 2404.01413 2404.03242 |
| [Losing our Tail, Again: (Un)Natural Selection & Multilingual LLMs](https://arxiv.org/abs/2507.03933) | 2025 |  | 1 | 2305.17493 2306.06130 2307.01850 2308.07462 2401.05749 2404.04286 2503.03150 CorpusId:6567063 CorpusId:7123287 |
| [Model Collapse in Recursive Synthetic Data Training: Mechanisms, Evaluation, and Mitigation Strategies](https://api.semanticscholar.org/CorpusId:292022319) | 2026 |  | 0 | 2211.08095 2307.01850 2310.00429 2311.09807 2402.07043 2402.07087 2402.07712 2402.11778 2403.07857 2404.05090 2406.07515 2410.04840 2410.08942 2502.15654 2502.18865 2509.16499 CorpusId:276282656 |
| [Large Language Models are Shannon Lossy Compressors Not Solomonoff Induction Estimators: Self-improvement and Singularity Are Not Near Without Symbolic Model Synthesis](https://arxiv.org/abs/2601.05280) | 2026 |  | 1 | 2307.01850 2402.07043 2402.07087 2402.11778 2404.01413 2410.16713 2412.14689 2412.17646 |
| [Universality of the π2/6 Pathway in Avoiding Model Collapse](https://arxiv.org/abs/2410.22812) | 2024 |  | 27 | 2002.05715 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2402.07043 2402.07712 2404.01413 2404.02325 2404.05090 2407.09499 2408.16333 2410.16713 CorpusId:270380115 |
| [A theoretical basis for model collapse in recursive training](https://arxiv.org/abs/2506.09401) | 2025 |  | 1 | 2305.17493 2307.01850 2402.07043 2402.07712 2404.01413 2404.02325 2412.17646 |
| [Model Non-Collapse: Minimax Bounds for Recursive Discrete Distribution Estimation](https://arxiv.org/abs/2501.19273) | 2025 |  | 5 | 2307.01850 2310.00429 2402.07712 2402.11778 2404.01413 2404.02325 2404.05090 2410.04840 2410.16713 2410.22812 2412.17646 2502.08924 2502.18049 2502.18865 2503.03150 CorpusId:270380115 |
| [Countering Model Collapse in Iterative Self-Training via Dynamic Center-Edge Sampling](https://api.semanticscholar.org/CorpusId:285822124) | 2026 |  | 0 | 2402.07043 2404.01413 2412.14689 |
| [When AI Reviews Its Own Code: Recursive Self-Training Collapse in Code LLMs](https://arxiv.org/abs/2606.28438) | 2026 |  | 2 | 2305.17493 2402.07043 2402.07087 2404.05090 2407.09499 2412.14689 2412.17646 2502.18865 |
| [The evolution of sex for artificial intelligence: a population-genetic framework for multigenerational model populations](https://arxiv.org/abs/2609.18560) | 2026 |  | 0 | 1005.2714 2307.01850 2310.00429 2311.09807 2401.05749 2402.07043 2403.07183 2404.01413 2406.07515 2407.17493 2410.04840 2410.16713 2412.17646 2501.05707 2503.02103 2509.20101 2509.22341 2510.16657 2604.08554 |
| [SIGMA: Scalable Spectral Insights for LLM Model Collapse](https://arxiv.org/abs/2601.03385) | 2026 |  | 0 | 2305.17493 2307.01850 2404.05090 2410.04840 2412.14689 2506.15690 |
| [A Markovian View of Iterative-Feedback Loops in Image Generative Models: Neural Resonance and Model Collapse](https://arxiv.org/abs/2602.19033) | 2026 |  | 0 | 2209.03942 2211.08095 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07087 2402.11778 2404.01413 2407.17493 2509.16499 |
| [Why Less is More (Sometimes): A Theory of Data Curation](https://arxiv.org/abs/2511.03492) | 2025 |  | 11 | 2203.12788 2209.03942 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.09807 2311.16822 2402.07043 2402.07087 2402.07712 2403.07857 2404.01413 2404.05090 2406.07515 2407.12835 2408.16333 2410.04840 2410.08942 |
| [Fairness Feedback Loops: Training on Synthetic Data Amplifies Bias](https://arxiv.org/abs/2403.07857) | 2024 |  | 89 | 2209.03942 2211.08095 2305.17493 2306.06130 2306.07899 2307.01850 CorpusId:2289219 |
| [Clinical Model Autophagy: The Risk of Interpretative Drift in Recursive Medical AI](https://api.semanticscholar.org/CorpusId:287065505) | 2026 |  | 0 |  |
| [Preventing Model Collapse Under Overparametrization: Optimal Mixing Ratios for Interpolation Learning and Ridge Regression](https://arxiv.org/abs/2509.22341) | 2025 |  | 9 | 2211.08095 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.12202 2311.16822 2402.07043 2402.07712 2404.01413 2406.07515 2410.04840 2410.16713 2410.22812 2502.18049 |
| [Analyzing and Mitigating Model Collapse in Rectified Flow Models](https://arxiv.org/abs/2412.08175) | 2024 |  | 11 |  |
| [AI-generated data contamination erodes pathological variability and diagnostic reliability](https://arxiv.org/abs/2601.12946) | 2026 |  | 4 |  |
| [Preventing Model Collapse via Contraction-Conditioned Neural Filters](https://arxiv.org/abs/2512.00757) | 2025 |  | 0 | 2307.01850 2505.13947 |
| [LLM Web Dynamics: Tracing Model Collapse in a Network of LLMs](https://arxiv.org/abs/2506.15690) | 2025 |  | 7 | 2303.01255 2305.17493 2307.01850 2310.00429 2311.12202 2402.07087 2403.07857 2404.05090 2406.11938 2410.12954 2410.16713 2412.17646 2502.18049 2503.03150 2506.00077 |
| [Steering an Active Learning Workflow Towards Novel Materials Discovery via Queue Prioritization](https://arxiv.org/abs/2509.25538) | 2025 |  | 1 | 2305.17493 |
| [The Economics of Model Collapse: Equilibrium, Welfare, and Optimal Provenance Subsidies in Synthetic Data Markets](https://arxiv.org/abs/2605.20279) | 2026 |  | 0 | 2303.01255 2307.01850 2310.00429 2311.16822 2402.07043 2404.01413 |
| [Will Large-scale Generative Models Corrupt Future Datasets?](https://arxiv.org/abs/2211.08095) | 2022 |  | 83 | CorpusId:11770707 CorpusId:2289219 |
| [The Collapse of GPT](https://api.semanticscholar.org/CorpusId:278637235) | 2025 |  | 0 |  |
| [Artificial Artificial Artificial Intelligence: Crowd Workers Widely Use Large Language Models for Text Production Tasks](https://arxiv.org/abs/2306.07899) | 2023 |  | 190 | 2305.17493 |
| [When Updating Stops Being Learning: Rethinking LLM Self-Evolution via learnable information gain](https://arxiv.org/abs/2609.36535) | 2026 |  | 0 | 2002.05715 2307.01850 2310.00429 2402.07043 2404.01413 2404.05090 2407.05013 2410.04840 2505.21444 |
| [A Shocking Amount of the Web is Machine Translated: Insights from Multi-Way Parallelism](https://arxiv.org/abs/2401.05749) | 2024 |  | 58 |  |
| [Capability Degradation in Small Language Models Under Low-Signal Data Corruption](https://api.semanticscholar.org/CorpusId:290519022) | 2026 |  | 1 |  |
| [Retraining Seeks Stable Signals](https://arxiv.org/abs/2607.15623) | 2026 |  | 1 | 2209.03942 2307.01850 2310.00429 2402.07043 2404.01413 |
| [Large Language Models Suffer From Their Own Output: An Analysis of the Self-Consuming Training Loop](https://arxiv.org/abs/2311.16822) | 2023 |  | 101 | 2305.17493 2306.06130 2306.07899 2307.01850 2310.00429 2311.09807 |
| [When Your Own Output Becomes Your Training Data: Noise-to-Meaning Loops and a Formal RSI Trigger](https://arxiv.org/abs/2505.02888) | 2025 |  | 1 | 2305.17493 |
| [Human-AI Interactions and Societal Pitfalls](https://arxiv.org/abs/2309.10448) | 2023 |  | 17 | 2305.17493 |
| [Mitigating Tail Narrowing in LLM Self-Improvement via Socratic-Guided Sampling](https://arxiv.org/abs/2411.00750) | 2024 |  | 20 | 2305.17493 2307.01850 2311.09807 2402.07043 2407.05013 |
| [Characterizing Model Behavior Under Synthetic Data Training: An Empirical Study Across Scales and Mixing Ratios](https://arxiv.org/abs/2510.05133) | 2025 |  | 0 | 2305.17493 2307.01850 |
| [Decoupling Token Roles in Autoregressive Pretraining](https://arxiv.org/abs/2609.33405) | 2026 |  | 0 | 2402.07043 2404.01413 2502.15654 |
| [One Symptom, Three Levers: A Critical Review of On-Policy Self-Distillation](https://arxiv.org/abs/2608.25936) | 2026 |  | 0 | 2002.05715 2404.01413 |
| [Delving into LLM-assisted writing in biomedical publications through excess vocabulary](https://arxiv.org/abs/2406.07016) | 2024 |  | 252 | 2403.07183 |
| [Convergence and Stability Analysis of Self-Consuming Generative Models with Heterogeneous Human Curation](https://arxiv.org/abs/2511.09002) | 2025 |  | 3 | 2211.08095 2303.01255 2310.00429 2311.12202 2407.09499 |
| [Can Large Reasoning Models Self-Train?](https://arxiv.org/abs/2505.21444) | 2025 |  | 66 | 2305.17493 2307.01850 2310.00429 2402.07087 2404.01413 2406.07515 |
| [From Collapse to Improvement: Statistical Perspectives on the Evolutionary Dynamics of Iterative Training on Contaminated Sources](https://arxiv.org/abs/2602.10531) | 2026 |  | 0 | 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 2311.09807 2311.12202 2402.07043 2402.07712 2402.11778 2404.01413 2404.05090 2407.09499 2407.12835 CorpusId:270380115 |
| [Break Step: Recursive Training Resonates with Replayed Sampling Noise](https://arxiv.org/abs/2609.11149) | 2026 |  | 0 | 2307.01850 2310.00429 2311.09807 2311.16822 2402.07043 2402.07087 2402.07712 2404.01413 2404.05090 2406.07515 2410.04840 2410.16713 2503.03150 |
| [AI-Associated Lexical Shifts Across 34 Languages: Cross-Lingual Convergence and Diachronic Uptake in News Writing](https://arxiv.org/abs/2605.25358) | 2026 |  | 2 | 2305.17493 2406.07016 2410.12954 2412.18148 CorpusId:12098535 |
| [Wikipedia in the Era of LLMs: Evolution and Risks](https://arxiv.org/abs/2503.02879) | 2025 |  | 7 | 2305.17493 2403.07183 2502.20258 CorpusId:275314181 |
| [Combining Generative Artificial Intelligence (AI) and the Internet: Heading towards Evolution or Degradation?](https://arxiv.org/abs/2303.01255) | 2023 |  | 56 | 2211.08095 |
| [Stabilizing Self-Consuming Diffusion Models with Latent Space Filtering](https://arxiv.org/abs/2511.12742) | 2025 |  | 7 | 2209.03942 2305.17493 2307.01850 2310.00429 2402.11778 2406.07515 2408.16333 2410.12954 2410.16713 2502.15654 2502.18865 2503.02103 2505.09768 CorpusId:273502601 |
| [Learning with Synthetic Data via SGD in High-Dimensional Linear Regression](https://arxiv.org/abs/2609.09572) | 2026 |  | 0 |  |
| [How Much Is an AI Token Worth? Scaling Laws for Wild AI-Generated Web Text](https://arxiv.org/abs/2609.40295) | 2026 |  | 0 | 2402.07043 2404.01413 2404.05090 2410.04840 2410.16713 2412.17646 2503.03150 |
| [From Valid to Useful: Post-Verification Acquisition for Recursive Self-Improving Recommendation](https://arxiv.org/abs/2610.04302) | 2026 |  | 0 | 2307.01850 2404.01413 |
| [When Competition Consumes Diversity: A Theoretical Framework for Generative Collapse](https://api.semanticscholar.org/CorpusId:284476304) | 2025 |  | 0 | 2307.01850 2405.13977 |
| [A solvable model of learning generative diffusion: theory and insights](https://arxiv.org/abs/2501.03937) | 2025 |  | 11 | 2410.12954 |
| [Can Generative Artificial Intelligence Survive Data Contamination? Theoretical Guarantees under Contaminated Recursive Training](https://arxiv.org/abs/2602.16065) | 2026 |  | 0 | 2211.08095 2303.01255 2305.17493 2310.00429 2311.16822 2402.07043 2402.07712 2403.07183 2404.01413 2406.07515 2407.12835 2410.04840 2410.22812 2412.17646 2505.19046 |
| [What happens when generative AI models train recursively on each others'outputs?](https://arxiv.org/abs/2505.21677) | 2025 |  | 5 | 2211.08095 2306.06130 2307.01850 2402.07712 2404.01413 2404.02325 2404.03502 2407.12835 2410.16713 2410.22812 2412.18148 2502.15654 2503.03150 2505.19046 CorpusId:270380115 CorpusId:273502601 |
| [Spiral of Silence: How is Large Language Model Killing Information Retrieval? - A Case Study on Open Domain Question Answering](https://arxiv.org/abs/2404.10496) | 2024 |  | 12 | 2305.17493 2307.01850 |
| [Beyond Model Collapse: Scaling Up with Synthesized Data Requires Reinforcement](https://api.semanticscholar.org/CorpusId:270380115) | 2024 |  | 42 |  |
| [Large language models reduce public knowledge sharing on online Q&A platforms](https://arxiv.org/abs/2307.07367) | 2023 |  | 100 | 2305.17493 2306.07899 2307.01850 2403.07857 |
| [The Risks of Autonomy: Dynamic Auditing of Self-Editing Language Models in Critical Infrastructure](https://api.semanticscholar.org/CorpusId:287661814) | 2026 |  | 1 |  |
| [AI and the problem of knowledge collapse](https://arxiv.org/abs/2404.03502) | 2024 |  | 87 | 2305.17493 2311.09807 2311.12202 2402.07043 |
| [SynthLineage: Submodular-Guided Corpus Distillation and Knowledge Graph Provenance for Collapse-Resistant LLM Fine-Tuning](https://api.semanticscholar.org/CorpusId:291929661) | 2026 |  | 0 |  |
| [When LLMs Play the Telephone Game: Cumulative Changes and Attractors in Iterated Cultural Transmissions](https://api.semanticscholar.org/CorpusId:271039487) | 2024 |  | 12 |  |
| [The Necessity of Imperfection:Reversing Model Collapse via Simulating Cognitive Boundedness](https://arxiv.org/abs/2512.01354) | 2025 |  | 1 | 2305.17493 2307.01850 |
| [Multilingual Arbitration: Optimizing Data Pools to Accelerate Multilingual Progress](https://api.semanticscholar.org/CorpusId:280017631) | 2025 |  | 4 |  |
| [Data Feedback Loops: Model-driven Amplification of Dataset Biases](https://arxiv.org/abs/2209.03942) | 2022 |  | 83 | CorpusId:256943162 |
| [On the Dangers of Bootstrapping Generation for Continual Learning and Beyond](https://arxiv.org/abs/2512.11867) | 2025 |  | 1 | 2211.08095 2305.17493 2307.01850 |
| [Theoretical Proof that Auto-regressive Language Models Collapse when Real-world Data is a Finite Set](https://arxiv.org/abs/2412.14872) | 2024 |  | 4 | 2209.03942 2307.01850 2310.00429 2402.07043 2402.07712 2404.01413 2404.05090 2407.09499 2410.16713 |
| [Content Platform GenAI Regulation via Compensation](https://arxiv.org/abs/2604.06194) | 2026 |  | 0 | 2305.17493 2310.00429 |
| [The Fairness Collapse Phenomenon: Bias Amplification in Language Models Trained on Synthetic Data](https://arxiv.org/abs/2608.04268) | 2026 |  | 0 | 2305.17493 2307.01850 2311.09807 2402.07043 2404.05090 2407.09499 2410.16713 2412.14689 2604.26965 |
| [Explaining and Preventing Alignment Collapse in Iterative RLHF](https://arxiv.org/abs/2605.04266) | 2026 |  | 4 |  |
| [Delving into: the quantification of Ai-generated content on the internet (synthetic data)](https://arxiv.org/abs/2504.08755) | 2025 |  | 23 | 2307.01850 2402.11271 2408.16333 |
| [Compositionality and systematicity emerge from iterated learning in deep linear networks](https://api.semanticscholar.org/CorpusId:287992263) | 2026 |  | 1 | 2003.12694 CorpusId:10250779 CorpusId:1391836 CorpusId:21203381 CorpusId:6567063 CorpusId:7123287 |
| [Breaking the Spiral: A Utility-Driven Optimization Framework for Balanced Information Retrieval in the LLM Era](https://api.semanticscholar.org/CorpusId:284861474) | 2026 |  | 2 |  |
| [Multiagent Finetuning: Self Improvement with Diverse Reasoning Chains](https://arxiv.org/abs/2501.05707) | 2025 |  | 104 |  |
| [Playing with words: Comparing the vocabulary and lexical diversity of ChatGPT and humans](https://arxiv.org/abs/2308.07462) | 2023 |  | 39 | 2305.17493 2306.06130 2402.07043 2404.02325 |
| [Human-AI Interactions in the Communication Era: Autophagy Makes Large Models Achieving Local Optima](https://api.semanticscholar.org/CorpusId:281305478) | 2024 |  | 16 |  |
| [Feature Selective Model Collapse in Diffusion Models: Total Replacement versus Fixed-Budget Training](https://arxiv.org/abs/2610.01318) | 2026 |  | 0 | 2305.17493 2310.00429 2311.12202 2402.07043 2402.07712 2404.01413 2404.05090 2407.17493 2410.04840 2410.16713 2412.14689 2505.19046 2509.16499 |
| [Observations and Remedies for Large Language Model Bias in Self-Consuming Performative Loop](https://arxiv.org/abs/2601.05184) | 2026 |  | 3 | 2211.08095 2305.17493 2307.01850 2310.00429 2311.09807 2311.16822 2402.07043 2402.07087 2402.07712 2403.07857 2404.03242 2404.05090 2407.09499 2408.16333 2410.12954 2410.16713 2411.13852 2505.09768 2511.12742 CorpusId:273502601 |
| [Why Self-Training Helps and Hurts: Denoising vs. Signal Forgetting](https://arxiv.org/abs/2602.14029) | 2026 |  | 0 | 2305.17493 2310.00429 2402.07712 2404.01413 2410.22812 2502.18049 2509.22341 |
| [Tracking the perspectives of interacting language models](https://arxiv.org/abs/2406.11938) | 2024 |  | 17 | 2305.17493 |
| [SPECTRUM: Proximal Spectral Modulation for Looped Self-Distillation](https://arxiv.org/abs/2610.07237) | 2026 |  | 0 | 2404.01413 |
| [Gaussian mixture models as a proxy for interacting language models](https://arxiv.org/abs/2506.00077) | 2025 |  | 4 | 2305.17493 2406.11938 |
| [Human-AI Coevolution](https://arxiv.org/abs/2306.13723) | 2023 |  | 115 | 2211.08095 2305.17493 2306.06130 2307.01850 2311.09807 2402.07043 2402.07712 |
| [Self-Distillation Amplifies Regularization in Hilbert Space](https://arxiv.org/abs/2002.05715) | 2020 |  | 298 |  |
| [What happens when generative AI models train recursively on each others' generated outputs?](https://api.semanticscholar.org/CorpusId:278959832) | 2025 |  | 2 |  |
| [AI models fed AI-generated data quickly spew nonsense](https://api.semanticscholar.org/CorpusId:271447829) | 2024 |  | 15 |  |
| [Generative AI Degrades Online Communities](https://api.semanticscholar.org/CorpusId:268018326) | 2024 |  | 15 |  |
| [Distilling the Effects of Language Model Contamination](https://api.semanticscholar.org/CorpusId:273589341) | 2024 |  | 1 | 2209.03942 2211.08095 2305.17493 2306.06130 CorpusId:11770707 CorpusId:226357748 |
| [ReGain: Restoring Subject Fidelity in Personalization on Synthetic Images](https://arxiv.org/abs/2609.38680) | 2026 |  | 0 | 2307.01850 2310.00429 2404.01413 2407.17493 2408.16333 |
| [Entropy Collapse: A Universal Failure Mode of Intelligent Systems](https://arxiv.org/abs/2512.12381) | 2025 |  | 4 | 2305.17493 2307.01850 2402.07043 2404.01413 |
| [Stabilizing Self-consuming Training Loop on Music Generation Based on Music Embeddings](https://api.semanticscholar.org/CorpusId:282440959) | 2025 |  | 0 |  |
| [Progress or Regress? Self-Improvement Reversal in Post-training](https://arxiv.org/abs/2407.05013) | 2024 |  | 30 |  |
| [When LLMs Play the Telephone Game: Cultural Attractors as Conceptual Tools to Evaluate LLMs in Multi-turn Settings](https://arxiv.org/abs/2407.04503) | 2024 |  | 18 | 2305.17493 2402.07043 2404.01413 2404.03502 2406.11938 2410.16713 CorpusId:10250779 CorpusId:264108087 CorpusId:7123287 |
| [Iterated learning and the evolution of language.](https://api.semanticscholar.org/CorpusId:7123287) | 2014 |  | 331 |  |
| [NOVA: Fundamental Limits of Knowledge Discovery Through AI](https://arxiv.org/abs/2605.15219) | 2026 |  | 0 | 2404.01413 2404.05090 |
| [Maximizing the Potential of Synthetic Data: Insights from Random Matrix Theory](https://arxiv.org/abs/2410.08942) | 2024 |  | 7 | 2203.12788 2305.17493 2307.01850 2311.09807 2402.07712 2404.01413 2404.05090 CorpusId:270380115 |
| [When Medical LLMs Eat Their Own Output: The Effects of Recursive Self-Training on German Medical Text](https://api.semanticscholar.org/CorpusId:290639868) | 2026 |  | 0 | 2305.17493 2307.01850 2406.07016 2406.07515 2410.16713 |
| [Heat Death of Generative Models in Closed-Loop Learning](https://arxiv.org/abs/2404.02325) | 2024 |  | 33 | 2303.01255 2305.17493 2306.06130 2307.01850 2310.00429 |
| [Collapse of Self-trained Language Models](https://arxiv.org/abs/2404.02305) | 2024 |  | 10 |  |
| [Preventing Curriculum Collapse in Self-Evolving Reasoning Systems](https://arxiv.org/abs/2603.13309) | 2026 |  | 2 | 2305.17493 2410.04840 |
| [Automating Data Annotation under Strategic Human Agents: Risks and Potential Solutions](https://arxiv.org/abs/2405.08027) | 2024 |  | 14 | 2209.03942 2305.17493 2310.00429 2403.07857 CorpusId:226357748 CorpusId:256943162 |
| [Dealing with Synthetic Data Contamination in Online Continual Learning](https://arxiv.org/abs/2411.13852) | 2024 |  | 6 | 2211.08095 2306.06130 2404.03242 |
| [Towards Understanding the Interplay of Generative Artificial Intelligence and the Internet](https://arxiv.org/abs/2306.06130) | 2023 |  | 79 | 2211.08095 2303.01255 2305.17493 CorpusId:11770707 |
| [Are We in the AI-Generated Text World Already? Quantifying and Monitoring AIGT on Social Media](https://arxiv.org/abs/2412.18148) | 2024 |  | 51 | 2311.16822 |
| [Market Design for AI: Beyond the Copyright Binary](https://arxiv.org/abs/2606.12260) | 2026 |  | 0 | 2305.17493 2307.01850 2307.07367 |
| [Semantic Data Pollution: A New Challenge For Cybersecurity and Standardization of AI Models in Smart Factories](https://api.semanticscholar.org/CorpusId:292531124) | 2026 |  | 0 |  |
| [Analysis of Linguistic Effects of Self-Consuming Training](https://api.semanticscholar.org/CorpusId:285804007) | 2025 |  | 1 |  |
| [The Anti-Ouroboros Effect: Emergent Resilience in Large Language Models from Recursive Selective Feedback](https://arxiv.org/abs/2509.10509) | 2025 |  | 0 | 2305.17493 2404.01413 2404.05090 2406.07515 2412.17646 2503.03150 2504.03814 2506.15690 |
| [Human-AI Co-Evolution and Epistemic Collapse: A Dynamical Systems Perspective](https://arxiv.org/abs/2605.06347) | 2026 |  | 0 | 2305.17493 |
| [AI and its consequences for the written word](https://api.semanticscholar.org/CorpusId:266833247) | 2024 |  | 9 | 2305.17493 |
| [LLM as a Broken Telephone: Iterative Generation Distorts Information](https://arxiv.org/abs/2502.20258) | 2025 |  | 17 | 2203.12788 2305.17493 2311.09807 2402.07043 2402.11778 2404.03502 2406.11938 CorpusId:271039487 |
| [Structural Drift: The Population Dynamics of Sequential Learning](https://arxiv.org/abs/1005.2714) | 2010 |  | 8 | CorpusId:6567063 |
| [Preventing Model Collapse when Training LLMs with Synthetic Data](https://api.semanticscholar.org/CorpusId:284724154) | 2025 |  | 1 |  |
| [The Alignment Game: A Theory of Long-Horizon Alignment Through Recursive Curation](https://arxiv.org/abs/2511.12804) | 2025 |  | 2 | 2305.17493 2402.07712 2407.09499 2505.13947 |
| [Iterative Finetuning is Mostly Idempotent](https://arxiv.org/abs/2605.01130) | 2026 |  | 0 | 2307.01850 2311.09807 2402.07043 2404.01413 2404.04286 2404.05090 2410.15234 2604.26965 |
| [An Information-Theoretic Criterion for Efficient Data Synthesis](https://arxiv.org/abs/2605.16379) | 2026 |  | 0 | 2307.01850 2402.07043 2404.01413 |
| [Iterated Learning: A Framework for the Emergence of Language](https://api.semanticscholar.org/CorpusId:6567063) | 2003 |  | 315 |  |
| [From infant robots to recursive models: historical consciousness and the exhausting of exhaustion by generative AIs](https://api.semanticscholar.org/CorpusId:285417849) | 2026 |  | 0 |  |
| [When AI Eats Itself: On the Caveats of AI Autophagy in the Era of Generative AI](https://api.semanticscholar.org/CorpusId:269791198) |  |  | 0 |  |
| [Entropy-Reservoir Bregman Projection: An Information-Geometric Unification of Model Collapse](https://arxiv.org/abs/2512.14879) | 2025 |  | 1 | 2305.17493 |
| [Human innovation and the creative agency of the world in the age of generative AI](https://api.semanticscholar.org/CorpusId:268913832) | 2024 |  | 20 | 2305.17493 |
| [When AI Eats Itself: On the Caveats of AI Autophagy](https://arxiv.org/abs/2405.09597) | 2024 |  | 4 |  |
| [A Dominant Supplier Slows Recursive Drift More Than It Steers It](https://arxiv.org/abs/2609.11146) | 2026 |  | 0 | 2307.01850 2310.00429 2311.09807 2402.07043 2402.07087 2404.01413 2404.05090 2406.07515 2410.16713 2503.03150 2505.21677 2506.15690 2512.15011 |
| [When and How Human Curation Backfires: Preference Alignment under Multi-Model Self-Consuming Loop](https://arxiv.org/abs/2605.29267) | 2026 |  | 2 | 2209.03942 2307.01850 2310.00429 2402.11778 2403.07857 2404.01413 2404.03242 2404.05090 2405.08027 2406.07515 2407.09499 2410.04840 2410.15234 2502.18865 2503.08117 2505.09768 2511.09002 2511.12742 2601.05184 |
| [Markovian Generation Chains in Large Language Models](https://arxiv.org/abs/2603.11228) | 2026 |  | 3 | 2311.09807 2404.01413 2404.03502 2404.05090 2407.04503 2502.20258 2503.03150 |
| [Epistemic diversity across language models mitigates knowledge collapse](https://arxiv.org/abs/2512.15011) | 2025 |  | 2 | 2310.00429 2402.07043 2404.01413 2404.03502 2406.07515 2412.14872 2502.08924 2502.09963 2502.18865 2503.03150 2506.15690 CorpusId:275314181 CorpusId:276282656 |
| [EpiCaR: Knowing What You Don't Know Matters for Better Reasoning in LLMs](https://arxiv.org/abs/2601.06786) | 2026 |  | 2 | 2305.17493 |
| [Minimax bounds for watermarked and masked recursive discrete distribution estimation](https://arxiv.org/abs/2608.31091) | 2026 |  | 0 | 2307.01850 2310.00429 2402.07712 2402.11778 2404.01413 2404.02325 2404.05090 2410.04840 2410.16713 2412.17646 2501.19273 2502.08924 2502.18865 2505.13947 2505.19046 2505.21677 2509.16499 2511.03492 2601.15468 2603.11784 CorpusId:270380115 |
| [Superficial Self-Improved Reasoners Benefit from Model Merging](https://arxiv.org/abs/2503.02103) | 2025 |  | 23 | 2211.08095 2305.17493 2307.01850 2310.00429 2311.09807 2311.12202 2402.07087 2404.05090 2406.07515 |
| [Bias Amplification: Large Language Models as Increasingly Biased Media](https://arxiv.org/abs/2410.15234) | 2024 |  | 23 | 2209.03942 2307.01850 2311.09807 2402.07043 2402.07712 2403.07857 2404.03242 2404.05090 2407.09499 2410.12954 CorpusId:270380115 |
| [MONAL: Model Autophagy Analysis for Modeling Human-AI Interactions](https://arxiv.org/abs/2402.11271) | 2024 |  | 6 | 2305.17493 2306.07899 2311.16822 |
| [Learning in an Echo Chamber: Online Learning with Replay Adversary](https://arxiv.org/abs/2509.25135) | 2025 |  | 5 | 2305.17493 2306.07899 2307.01850 2412.18148 |
| [Data Value in the Age of Scaling: Understanding LLM Scaling Dynamics Under Real-Synthetic Data Mixtures](https://arxiv.org/abs/2511.13640) | 2025 |  | 2 | 2305.17493 2402.07043 2402.07712 2404.05090 2406.07515 2407.12835 2410.04840 |
| [Escaping Collapse: The Strength of Weak Data for Large Language Model Training](https://arxiv.org/abs/2502.08924) | 2025 |  | 17 | 2211.08095 2307.01850 2310.00429 2402.07043 2402.07087 2402.07712 2404.01413 2404.05090 2406.07515 2407.09499 2410.08942 2410.16713 2410.22812 2412.17646 2503.03150 |
| [LSTM in Recursive Feedback Loops: A Study on Textual Evolution and Complexity](https://api.semanticscholar.org/CorpusId:283013968) | 2025 |  | 1 |  |
| [Would Deep Generative Models Amplify Bias in Future Models?](https://arxiv.org/abs/2404.03242) | 2024 |  | 36 | 2209.03942 2211.08095 |
| [ForTIFAI: Fending Off Recursive Training Induced Failure for AI Models](https://api.semanticscholar.org/CorpusId:281252123) | 2025 |  | 0 |  |
| [Self-Generated Feedback Destabilizes Test-Time Training: A Causal Decomposition of Long-Horizon Adaptation](https://arxiv.org/abs/2610.05076) | 2026 |  | 0 | 2307.01850 2311.16822 2404.01413 2404.02325 |
| [Are LLMs becoming similarly creative? Evidence from three years of models](https://arxiv.org/abs/2608.19437) | 2026 |  | 3 | 2305.17493 2505.21677 |
| [Neon: Negative Extrapolation From Self-Training Improves Image Generation](https://arxiv.org/abs/2510.03597) | 2025 |  | 5 | 2307.01850 2310.00429 2402.07043 2404.01413 2408.16333 CorpusId:270380115 |
| [Bias Amplification: Language Models as Increasingly Biased Media](https://api.semanticscholar.org/CorpusId:273502601) | 2024 |  | 15 |  |
| [The Impact of AI-Generated Text on the Internet](https://arxiv.org/abs/2604.26965) | 2026 |  | 9 | 2307.01850 2401.05749 2402.07712 2403.07183 2404.01413 2406.07016 2410.04840 2412.18148 2503.03150 2504.08755 |
| [First-Extinction Law for Resampling Processes](https://arxiv.org/abs/2509.20101) | 2025 |  | 1 | 2402.07712 2404.01413 2404.05090 2502.15654 2503.03150 |
| [Monitoring AI-Modified Content at Scale: A Case Study on the Impact of ChatGPT on AI Conference Peer Reviews](https://arxiv.org/abs/2403.07183) | 2024 |  | 304 | CorpusId:12098535 |
| [Step-On-Feet Tuning: Scaling Self-Alignment of LLMs via Bootstrapping](https://arxiv.org/abs/2402.07610) | 2024 |  | 17 | 2305.17493 2306.06130 2307.01850 2311.16822 |
| [No Model Required: Text Entropy Rate Filtering Mitigates Iterative Fine-Tuning Collapse](https://arxiv.org/abs/2610.01493) | 2026 |  | 0 | 2307.01850 2310.00429 2311.09807 2311.16822 2404.01413 2406.07515 2410.12341 2412.14689 2502.18865 2510.16657 |
| [Explainability guided model collapse mitigation for synthetic data driven wireless decision systems](https://api.semanticscholar.org/CorpusId:290010541) | 2026 |  | 0 | 2305.17493 2404.01413 |
| [Model Collapse as Cultural Evolution](https://arxiv.org/abs/2605.23054) | 2026 |  | 1 | 2307.01850 2311.09807 2311.16822 2402.07043 2402.07712 2404.04286 2404.05090 2406.07515 2410.04840 2410.12954 2503.03150 CorpusId:10250779 CorpusId:1391836 CorpusId:7123287 |
| [A Note on Generalization in Variational Autoencoders: How Effective Is Synthetic Data&Overparameterization?](https://arxiv.org/abs/2310.19653) | 2023 |  | 2 | 2305.17493 2307.01850 2310.00429 2311.12202 |
| [Drift and selection in LLM text ecosystems](https://arxiv.org/abs/2604.08554) | 2026 |  | 1 | 2211.08095 2307.01850 2310.00429 2311.09807 2311.12202 2402.07087 2404.01413 2406.07515 CorpusId:7123287 |
| [N EPOTISTICALLY T RAINED G ENERATIVE I MAGE M ODELS C OLLAPSE](https://api.semanticscholar.org/CorpusId:277510910) |  |  | 0 |  |
| [Countering Language Drift with Seeded Iterated Learning](https://arxiv.org/abs/2003.12694) | 2020 |  | 91 | CorpusId:10250779 CorpusId:21203381 CorpusId:7123287 |
| [What Matters in LLM-generated Data: Diversity and Its Effect on Model Fine-Tuning](https://arxiv.org/abs/2506.19262) | 2025 |  | 2 | 2305.17493 2311.09807 2311.16822 2402.07043 2402.07712 2404.01413 2404.05090 2406.07515 2410.04840 2410.16713 2410.22812 2412.14689 |
| [A Lifecycle-Oriented Survey of Emerging Threats and Vulnerabilities in Large Language Models](https://api.semanticscholar.org/CorpusId:281957554) | 2025 |  | 8 | 2402.07043 2404.01413 2404.03502 2406.07515 |
| [Epidemiology of Model Collapse: Modeling Synthetic Data Contamination via Bilayer SIR Dynamics](https://arxiv.org/abs/2606.05168) | 2026 |  | 0 | 2307.01850 2403.07183 2404.01413 2404.05090 2410.04840 |
| [Recursive Training Loops in LLMs: How training data properties modulate distribution shift in generated data?](https://arxiv.org/abs/2504.03814) | 2025 |  | 4 | 2211.08095 2303.01255 2305.17493 2306.06130 2310.00429 2311.09807 2311.12202 2311.16822 2402.07043 2402.07712 2410.12954 2410.16713 2503.03150 CorpusId:264108087 CorpusId:271039487 CorpusId:273502601 |
| [On the caveats of AI autophagy](https://api.semanticscholar.org/CorpusId:276282656) | 2025 |  | 27 | 2211.08095 2303.01255 2306.06130 2307.01850 2310.00429 2311.09807 2311.12202 2311.16822 2402.07087 2402.07712 2402.11778 2404.01413 2404.03242 2407.09499 2408.16333 CorpusId:270380115 |
| [Clean data for training statistical MT: the case of MT contamination](https://api.semanticscholar.org/CorpusId:11770707) | 2014 |  | 12 |  |
| [Effective Synthetic Data Curation Requires Group-Level Signals](https://arxiv.org/abs/2610.00779) | 2026 |  | 0 | 2311.09807 2410.04840 2412.14689 |
| [MT Detection in Web-Scraped Parallel Corpora](https://api.semanticscholar.org/CorpusId:2289219) | 2011 |  | 35 |  |
| [Error Amplification When Updating Deployed Machine Learning Models](https://api.semanticscholar.org/CorpusId:256943162) | 2022 |  | 9 |  |
| [Cultural reinforcement learning: a framework for modeling cumulative culture on a limited channel](https://api.semanticscholar.org/CorpusId:264108087) | 2023 |  | 11 |  |
| [Natural Language From Artificial Life](https://api.semanticscholar.org/CorpusId:21203381) | 2002 |  | 283 |  |
| [Bias Amplification in Language Model Evolution: An Iterated Learning Perspective](https://arxiv.org/abs/2404.04286) | 2024 |  | 23 | 2002.05715 2003.12694 |
| [Understanding Linguistic Evolution by Visualizing the Emergence of Topographic Mappings](https://api.semanticscholar.org/CorpusId:1391836) | 2006 |  | 140 |  |
| [Regurgitative Training: The Value of Real Data in Training Large Language Models](https://arxiv.org/abs/2407.12835) | 2024 |  | 22 |  |
| [Generating on Generated: An Approach Towards Self-Evolving Diffusion Models](https://arxiv.org/abs/2502.09963) | 2025 |  | 6 |  |
| [Detecting Fake Content with Relative Entropy Scoring](https://api.semanticscholar.org/CorpusId:12098535) | 2008 |  | 117 |  |
| [Iterated learning: Intergenerational knowledge transmission reveals inductive biases](https://api.semanticscholar.org/CorpusId:10250779) | 2007 |  | 228 |  |
| [Do Large Language Models Capture the Diversity in their Training Data?](https://arxiv.org/abs/2609.02275) | 2026 |  | 0 |  |
| [Death by AI: Will large language models diminish Wikipedia?](https://api.semanticscholar.org/CorpusId:275314181) | 2025 |  | 19 | 2404.03502 |
| [Hidden Risks of Machine Learning Applied to Healthcare: Unintended Feedback Loops Between Models and Future Data Causing Model Degradation](https://api.semanticscholar.org/CorpusId:226357748) | 2020 |  | 44 |  |
| [Recursive LLM Degradation in Biomedical Question Answering: A Cross-Generation Study](https://arxiv.org/abs/2609.34257) | 2026 |  | 0 | 2307.01850 2402.07087 2402.11778 2410.16713 2412.14689 2412.17646 2502.18865 2505.09768 |
| [Improving Generative Model Self-Training with Geometrically Modified Outputs](https://arxiv.org/abs/2609.35512) | 2026 |  | 0 | 2307.01850 2406.07515 2408.16333 2510.03597 |
| [Synthetic Loops and Biased Mirrors: Rethinking AI Trained on AI-Generated Data](https://api.semanticscholar.org/CorpusId:292722347) | 2026 |  | 0 |  |
| [Evaluating Distributional Distortion in Neural Language Modeling](https://arxiv.org/abs/2203.12788) | 2022 |  | 27 |  |

## Open work

- **Papers that could not enter the pool:** CorpusId:290898084 (Self-Verification Provably Prevents Model Collapse in
  Recursive Synthetic Training, NeurIPS 2025) — no SPECTER2 embedding, and no arXiv record found; CorpusId:279904145
  (The Imminent Risk of AI Data Dead Loops: Model Collapse and Content, IJSR 2025) — no SPECTER2 embedding;
  CorpusId:283482831 (Russian version of Giant component of truncated scale-free graphs: theory and applications to
  creation of datasets) — no SPECTER2 embedding; CorpusId:286099713 (Giant component of truncated scale-free graphs:
  theory and applications to creation of datasets) — no SPECTER2 embedding; CorpusId:274772988 (On Generated vs
  Collected Data) — no SPECTER2 embedding; CorpusId:272309897 (The Perils of Generative Model Inbreeding: Evaluating the
  Consequences of Cross-Model Training in Large Language Models) — no SPECTER2 embedding; CorpusId:274963310 (AI
  Cannibalism and the Law) — no SPECTER2 embedding

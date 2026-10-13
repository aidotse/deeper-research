# Rejected candidates: model-collapse

Candidates screened out of scope, one row per judgement: in orientation, by `tools/assign.py reject`; in expansion and
targeted expansions, copied from `expand-screen.md` by `tools/assign.py add-expand`. The fringe routes' judgements are in
`fringe-screen.md`. See docs/gates.md.

| paper | date | reason |
| -- | -- | -- |
| [2503.19551](https://arxiv.org/abs/2503.19551) | 2026-10-13 | synthetic data used once in LM pre-training with no recursive loop; the topic is recursive training across generations |
| [2510.01631](https://arxiv.org/abs/2510.01631) | 2026-10-13 | single-round synthetic data in LLM pre-training (n=1), no recursive loop; excluded by the input as synthetic data used once |
| [2507.04219](https://arxiv.org/abs/2507.04219) | 2026-10-13 | machine unlearning method that uses deliberately triggered collapse as a tool; the topic is degradation under recursive training |
| [2510.01171](https://arxiv.org/abs/2510.01171) | 2026-10-13 | mode collapse from preference alignment and a prompting remedy, no recursion over generations; the topic is recursive training |
| [2510.08123](https://arxiv.org/abs/2510.08123) | 2026-10-13 | synthetic data selection for one-off classifier augmentation, no recursive loop; excluded by the input as synthetic data used once |
| [2502.11266](https://arxiv.org/abs/2502.11266) | 2026-10-13 | LLM writing assistance homogenising human-written text, with no model trained on generated data; the topic is recursive training |
| [CorpusId:284117431](https://api.semanticscholar.org/CorpusId:284117431) | 2026-10-13 | inference-time text-image generation loops with no retraining of any model; the topic is training generation after generation |
| [2601.06586](https://arxiv.org/abs/2601.06586) | 2026-10-13 | machine-generated text detector motivated by misinformation and misconduct, not tested against degradation across generations or as training-data filtering |
| [CorpusId:271448069](https://api.semanticscholar.org/CorpusId:271448069) | 2026-10-13 | not out of scope: Nature 2024 venue version of the seed 2305.17493, merged into the arXiv record (docs/formats.md, Paper IDs) so one paper is not listed twice |
| [CorpusId:282047062](https://api.semanticscholar.org/CorpusId:282047062) | 2026-10-13 | not out of scope: ICMI 2025 venue version of 2505.08803 (same authors, near-identical title), merged into the arXiv record so one paper is not listed twice |
| [2608.22118](https://arxiv.org/abs/2608.22118) | 2026-10-13 | collapse of LLM answers when retrieving self-authored documents at inference, with no retraining; the topic is training on generated data |
| [2602.16136](https://arxiv.org/abs/2602.16136) | 2026-10-13 | retrieval and RAG pipelines consuming AI-generated web content, with no model retrained on it; the topic is recursive training |
| [2607.07663](https://arxiv.org/abs/2607.07663) | 2026-10-13 | survey of recursive self-improvement for capability gains, collapse only as one failure mode; excluded by the input as self-training for capability |
| [2510.08095](https://arxiv.org/abs/2510.08095) | 2026-10-13 | optimal synthetic-to-real ratio for a single training run, no recursive loop; excluded by the input as synthetic data used once |
| [2310.02727](https://arxiv.org/abs/2310.02727) | 2026-10-13 | statistical testing for EU AI Act conformity; unrelated to recursive training |
| [2407.06322](https://arxiv.org/abs/2407.06322) | 2026-10-13 | continual learning via model merging; not about recursive training on generated data |
| [2309.12284](https://arxiv.org/abs/2309.12284) | 2026-10-13 | bootstrapped math questions for capability gains; synthetic data used once |
| [2307.02192](https://arxiv.org/abs/2307.02192) | 2026-10-13 | dataset of AI-generated C programs for vulnerability study; not about recursive training |
| [2302.01735](https://arxiv.org/abs/2302.01735) | 2026-10-13 | semi-supervised medical segmentation; collapse within one training run |
| [2604.25203](https://arxiv.org/abs/2604.25203) | 2026-10-13 | synthetic data for training guardrail classifiers; used once, no recursive loop |
| [CorpusId:276419881](https://api.semanticscholar.org/CorpusId:276419881) | 2026-10-13 | review of oncology chatbots and misinformation; not model collapse |
| [CorpusId:206659415](https://api.semanticscholar.org/CorpusId:206659415) | 2026-10-13 | spermidine biology; unrelated to generative models |
| [2304.05977](https://arxiv.org/abs/2304.05977) | 2026-10-13 | text-to-image reward model; not about recursive training |
| [CorpusId:273146626](https://api.semanticscholar.org/CorpusId:273146626) | 2026-10-13 | about fairness for crowdworkers; not recursive training |
| [CorpusId:272997644](https://api.semanticscholar.org/CorpusId:272997644) | 2026-10-13 | evaluation of one-shot synthetic text generation; no recursive loop |
| [2205.13026](https://arxiv.org/abs/2205.13026) | 2026-10-13 | user preference dynamics under recommender systems; not generative models trained on generated data |
| [CorpusId:118543265](https://api.semanticscholar.org/CorpusId:118543265) | 2026-10-13 | Banach fixed-point theorem paper, from title; unrelated to model collapse |
| [CorpusId:250390701](https://api.semanticscholar.org/CorpusId:250390701) | 2026-10-13 | bias amplification in one-shot distillation; no recursion over generations |
| [CorpusId:9671500](https://api.semanticscholar.org/CorpusId:9671500) | 2026-10-13 | human-participant language transmission experiments; not about generative models trained on generated data |
| [2504.11369](https://arxiv.org/abs/2504.11369) | 2026-10-13 | benchmark for machine-generated text detection; not tested against collapse |
| [2106.05931](https://arxiv.org/abs/2106.05931) | 2026-10-13 | latent score-based generative model method; no recursive training |
| [CorpusId:123005604](https://api.semanticscholar.org/CorpusId:123005604) | 2026-10-13 | optimal transport convexity for gases, from title; unrelated to model collapse |
| [CorpusId:55426484](https://api.semanticscholar.org/CorpusId:55426484) | 2026-10-13 | parabolic equation solutions, from title; unrelated to model collapse |
| [2402.04333](https://arxiv.org/abs/2402.04333) | 2026-10-13 | instruction data selection for targeted tuning; not about generated-data recursion |
| [2309.00770](https://arxiv.org/abs/2309.00770) | 2026-10-13 | survey of LLM bias and fairness; not about recursive training |
| [2403.13187](https://arxiv.org/abs/2403.13187) | 2026-10-13 | evolutionary model merging recipes; not about training on generated data |
| [CorpusId:271157792](https://api.semanticscholar.org/CorpusId:271157792) | 2026-10-13 | perspective on generative AI in neuroimaging; unrelated to model collapse |
| [CorpusId:281715020](https://api.semanticscholar.org/CorpusId:281715020) | 2026-10-13 | psychology of human-GenAI relationships; not recursive model training |
| [2212.10560](https://arxiv.org/abs/2212.10560) | 2026-10-13 | self-generated instructions for capability gains; excluded self-training theme, no degradation across generations |
| [1710.07457](https://arxiv.org/abs/1710.07457) | 2026-10-13 | learning Wasserstein embeddings; unrelated to model collapse |
| [2407.03129](https://arxiv.org/abs/2407.03129) | 2026-10-13 | prompt sensitivity of bias evaluation; no recursive training |
| [CorpusId:221130142](https://api.semanticscholar.org/CorpusId:221130142) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2607.02723](https://arxiv.org/abs/2607.02723) | 2026-10-13 | human repetitive AI information-seeking behaviour; the topic is recursive training of generative models |
| [2403.08381](https://arxiv.org/abs/2403.08381) | 2026-10-13 | diffusion endpoint singularities; single-model generation quality, not collapse |
| [CorpusId:38527911](https://api.semanticscholar.org/CorpusId:38527911) | 2026-10-13 | SVM pruning (title only); the topic is recursive training of generative models |
| [1909.05858](https://arxiv.org/abs/1909.05858) | 2026-10-13 | controllable generation model release; not about training on generated data |
| [CorpusId:263196333](https://api.semanticscholar.org/CorpusId:263196333) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2401.17958](https://arxiv.org/abs/2401.17958) | 2026-10-13 | probability-flow ODE convergence theory for one diffusion model; no recursive training |
| [2206.00364](https://arxiv.org/abs/2206.00364) | 2026-10-13 | diffusion design space and FID gains; unrelated to model collapse |
| [2110.00800](https://arxiv.org/abs/2110.00800) | 2026-10-13 | state-dependent performative prediction via stochastic approximation; not generative recursive training |
| [2502.02508](https://arxiv.org/abs/2502.02508) | 2026-10-13 | RL post-training for LLM reasoning search; excluded self-training for capability |
| [2102.08921](https://arxiv.org/abs/2102.08921) | 2026-10-13 | sample-level fidelity metrics for generative models; not about recursive training |
| [CorpusId:39050909](https://api.semanticscholar.org/CorpusId:39050909) | 2026-10-13 | climate change and disasters; unrelated to model collapse |
| [CorpusId:9120526](https://api.semanticscholar.org/CorpusId:9120526) | 2026-10-13 | discourse markers linguistics; not about generative models |
| [CorpusId:263893386](https://api.semanticscholar.org/CorpusId:263893386) | 2026-10-13 | active learning for social-network content classification; the topic is recursive training of generative models |
| [2305.15047](https://arxiv.org/abs/2305.15047) | 2026-10-13 | AI-text detector not tested as collapse defence or data filter; excluded detection theme |
| [2503.22006](https://arxiv.org/abs/2503.22006) | 2026-10-13 | LLM-generated data for encoder continual pretraining, used once; no recursion |
| [2311.01193](https://arxiv.org/abs/2311.01193) | 2026-10-13 | position on contextual confidence in human communication; not about recursive model training |
| [CorpusId:269943406](https://api.semanticscholar.org/CorpusId:269943406) | 2026-10-13 | about political economy of foundation models; not recursive training |
| [CorpusId:282237002](https://api.semanticscholar.org/CorpusId:282237002) | 2026-10-13 | critical theory of LLM embeddings as capital; not about model collapse |
| [CorpusId:238031096](https://api.semanticscholar.org/CorpusId:238031096) | 2026-10-13 | crowd behaviour and risk in a stadium incident; the topic is recursive training of generative models |
| [2405.09673](https://arxiv.org/abs/2405.09673) | 2026-10-13 | LoRA versus full finetuning forgetting; not about generated training data |
| [CorpusId:122218527](https://api.semanticscholar.org/CorpusId:122218527) | 2026-10-13 | Markov process theory, from title; unrelated to model collapse |
| [CorpusId:269911671](https://api.semanticscholar.org/CorpusId:269911671) | 2026-10-13 | LLM use in parliaments; unrelated to model collapse |
| [2601.00856](https://arxiv.org/abs/2601.00856) | 2026-10-13 | comment on human cognition study with ChatGPT; not model training |
| [2309.06180](https://arxiv.org/abs/2309.06180) | 2026-10-13 | LLM serving memory system; unrelated to recursive training |
| [CorpusId:247763982](https://api.semanticscholar.org/CorpusId:247763982) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2601.09765](https://arxiv.org/abs/2601.09765) | 2026-10-13 | taxonomy of AI existential risk; not about model collapse |
| [CorpusId:279920321](https://api.semanticscholar.org/CorpusId:279920321) | 2026-10-13 | predictive algorithms retrained on their own selected decisions; selection-bias feedback, not generative models |
| [1806.03915](https://arxiv.org/abs/1806.03915) | 2026-10-13 | decentralized Wasserstein barycenter algorithm; unrelated to model collapse |
| [2002.06673](https://arxiv.org/abs/2002.06673) | 2026-10-13 | founding performative prediction framework for predictive models; not generative recursive training |
| [2310.00426](https://arxiv.org/abs/2310.00426) | 2026-10-13 | text-to-image diffusion model report; no recursive training on generated data |
| [2607.18268](https://arxiv.org/abs/2607.18268) | 2026-10-13 | synthetic data used once to train guardrail SLMs; no recursion over generations |
| [2512.19691](https://arxiv.org/abs/2512.19691) | 2026-10-13 | auditing LLM-assisted benchmark labels; no recursive training |
| [CorpusId:218493891](https://api.semanticscholar.org/CorpusId:218493891) | 2026-10-13 | review of AI in education; unrelated to model collapse |
| [2408.10718](https://arxiv.org/abs/2408.10718) | 2026-10-13 | benchmark of LLMs judging code; not about recursive training on generated data |
| [CorpusId:232234454](https://api.semanticscholar.org/CorpusId:232234454) | 2026-10-13 | remote-sensing tree classification CNN; the topic is recursive training of generative models |
| [2605.11666](https://arxiv.org/abs/2605.11666) | 2026-10-13 | data synthesis for reasoning capability gains via RLVR; excluded self-training theme |
| [2402.03214](https://arxiv.org/abs/2402.03214) | 2026-10-13 | detection of AI art, citing model collapse only as motivation; excluded detection theme |
| [2506.19882](https://arxiv.org/abs/2506.19882) | 2026-10-13 | position on a conference refutations track; model collapse cited only as one example debate |
| [CorpusId:288714344](https://api.semanticscholar.org/CorpusId:288714344) | 2026-10-13 | systems-theory analysis of generative AI in art, by its title; not training on generated data |
| [CorpusId:283673249](https://api.semanticscholar.org/CorpusId:283673249) | 2026-10-13 | self-play alignment for capability gain; excluded self-training theme |
| [2509.06770](https://arxiv.org/abs/2509.06770) | 2026-10-13 | multi-turn prompting refinement quality; no training on generated data |
| [CorpusId:276120174](https://api.semanticscholar.org/CorpusId:276120174) | 2026-10-13 | code-switched misinformation review; unrelated to model collapse |
| [2406.00832](https://arxiv.org/abs/2406.00832) | 2026-10-13 | best-of-n alignment theory; no recursion over generations |
| [2503.01155](https://arxiv.org/abs/2503.01155) | 2026-10-13 | population-based weight-space evolution of LLMs; not about recursive training on generated data |
| [2401.06883](https://arxiv.org/abs/2401.06883) | 2026-10-13 | privacy-preserving synthetic tabular data used once; no recursive loop |
| [2609.32902](https://arxiv.org/abs/2609.32902) | 2026-10-13 | knowledge capacity loss in low-bit quantized LMs; no training on generated data |
| [1909.03935](https://arxiv.org/abs/1909.03935) | 2026-10-13 | membership inference against generative models; privacy, not collapse |
| [CorpusId:4120195](https://api.semanticscholar.org/CorpusId:4120195) | 2026-10-13 | title: Fisher's population genetics book; biology, not generative models |
| [CorpusId:275863356](https://api.semanticscholar.org/CorpusId:275863356) | 2026-10-13 | data justice and AI data governance; not model collapse |
| [2605.01047](https://arxiv.org/abs/2605.01047) | 2026-10-13 | unlearning package hallucinations; not recursive training |
| [CorpusId:118347220](https://api.semanticscholar.org/CorpusId:118347220) | 2026-10-13 | optimal transport monograph, from title; unrelated to model collapse |
| [CorpusId:271099002](https://api.semanticscholar.org/CorpusId:271099002) | 2026-10-13 | software engineering challenges for FMware; unrelated to model collapse |
| [2102.06701](https://arxiv.org/abs/2102.06701) | 2026-10-13 | theory of neural scaling laws; no recursive training on generated data |
| [2603.18161](https://arxiv.org/abs/2603.18161) | 2026-10-13 | how LLM assistance changes human writing; no training on generated data |
| [2404.14387](https://arxiv.org/abs/2404.14387) | 2026-10-13 | survey of LLM self-evolution for capability gains; excluded self-training theme |
| [CorpusId:5959100](https://api.semanticscholar.org/CorpusId:5959100) | 2026-10-13 | fungal protein kinase biology; the topic is recursive training of generative models |
| [2601.05574](https://arxiv.org/abs/2601.05574) | 2026-10-13 | research integrity and AI in academia; not about recursive model training |
| [2312.02418](https://arxiv.org/abs/2312.02418) | 2026-10-13 | embedding-based pruning of low-quality code data; not about generated data across generations |
| [CorpusId:22978068](https://api.semanticscholar.org/CorpusId:22978068) | 2026-10-13 | cellular autophagy in chemoresistance; not model autophagy of generative models |
| [2503.08893](https://arxiv.org/abs/2503.08893) | 2026-10-13 | profiling LM weaknesses on benchmarks; not about recursive training |
| [2410.02089](https://arxiv.org/abs/2410.02089) | 2026-10-13 | RL with execution feedback for code; unrelated to model collapse |
| [CorpusId:268417271](https://api.semanticscholar.org/CorpusId:268417271) | 2026-10-13 | prompt-tuning for debiasing; not about recursive training |
| [2405.10853](https://arxiv.org/abs/2405.10853) | 2026-10-13 | federated LLM pre-training; no generated-data recursion |
| [2410.12613](https://arxiv.org/abs/2410.12613) | 2026-10-13 | model kinship for iterative weight merging; not about training on generated data |
| [2209.11215](https://arxiv.org/abs/2209.11215) | 2026-10-13 | diffusion sampling theory; no recursive training on generated data |
| [2305.07922](https://arxiv.org/abs/2305.07922) | 2026-10-13 | code model architecture and pretraining; not about model collapse |
| [CorpusId:296321](https://api.semanticscholar.org/CorpusId:296321) | 2026-10-13 | linguistic complexity theory; not about generative models |
| [2306.01693](https://arxiv.org/abs/2306.01693) | 2026-10-13 | fine-grained human feedback for RLHF; not about recursive training |
| [1802.05957](https://arxiv.org/abs/1802.05957) | 2026-10-13 | GAN training stabilisation; no recursion over generations |
| [CorpusId:238531423](https://api.semanticscholar.org/CorpusId:238531423) | 2026-10-13 | NTK generalization prediction (no abstract); not recursive generative training |
| [2511.12863](https://arxiv.org/abs/2511.12863) | 2026-10-13 | data valuation with asymmetric Shapley; not model collapse |
| [CorpusId:260211177](https://api.semanticscholar.org/CorpusId:260211177) | 2026-10-13 | AI content detection tools comparison (no abstract); not about recursive training |
| [CorpusId:272633175](https://api.semanticscholar.org/CorpusId:272633175) | 2026-10-13 | essay on generative AI and memory; not about recursive training |
| [2406.12397](https://arxiv.org/abs/2406.12397) | 2026-10-13 | flaws of one round of synthetic Q-A data; no recursion over generations |
| [CorpusId:271576544](https://api.semanticscholar.org/CorpusId:271576544) | 2026-10-13 | title is about data generation in exploration geochemistry; unrelated to generative model retraining |
| [2503.08223](https://arxiv.org/abs/2503.08223) | 2026-10-13 | position on edge-device data and compute for scaling; not recursive training |
| [CorpusId:290172162](https://api.semanticscholar.org/CorpusId:290172162) | 2026-10-13 | framework for AI and web coevolution; no training on generated data |
| [2502.17268](https://arxiv.org/abs/2502.17268) | 2026-10-13 | converting monologues into task-oriented dialogue data; no recursive generative training |
| [2112.10752](https://arxiv.org/abs/2112.10752) | 2026-10-13 | latent diffusion method; not about training on generated data |
| [CorpusId:286137751](https://api.semanticscholar.org/CorpusId:286137751) | 2026-10-13 | title: retrieval-augmented diffusion super-resolution; not about recursive training |
| [1511.06068](https://arxiv.org/abs/1511.06068) | 2026-10-13 | overfitting regularizer; no generated-data recursion |
| [2306.08568](https://arxiv.org/abs/2306.08568) | 2026-10-13 | code instruction tuning with Evol-Instruct; synthetic data used once, no recursion |
| [CorpusId:280700683](https://api.semanticscholar.org/CorpusId:280700683) | 2026-10-13 | title is about observability of latent states; unrelated to recursive training |
| [2510.03777](https://arxiv.org/abs/2510.03777) | 2026-10-13 | inference-time sampling diversity; no training on generated data |
| [2606.22495](https://arxiv.org/abs/2606.22495) | 2026-10-13 | agentic AI and environment determinism; not recursive training |
| [2512.15053](https://arxiv.org/abs/2512.15053) | 2026-10-13 | prompt orchestration framework; not about recursive training |
| [CorpusId:24506384](https://api.semanticscholar.org/CorpusId:24506384) | 2026-10-13 | title: adaptive walks on fitness landscapes; biology, not generative models |
| [2608.19230](https://arxiv.org/abs/2608.19230) | 2026-10-13 | citation selection monoculture across models; no training on generated data |
| [2601.10926](https://arxiv.org/abs/2601.10926) | 2026-10-13 | guidance on choosing LLMs for social science; not about recursive training |
| [2512.18748](https://arxiv.org/abs/2512.18748) | 2026-10-13 | curated code-doc dataset flagging AI text as one quality filter; not tested against collapse |
| [2403.02990](https://arxiv.org/abs/2403.02990) | 2026-10-13 | survey of LLM data augmentation; collapse not its subject |
| [2211.01916](https://arxiv.org/abs/2211.01916) | 2026-10-13 | score-based model convergence bounds; single model, not collapse |
| [2405.17977](https://arxiv.org/abs/2405.17977) | 2026-10-13 | individualized alignment via system messages; not about recursive training |
| [CorpusId:285804450](https://api.semanticscholar.org/CorpusId:285804450) | 2026-10-13 | prompt drift in deployed LLMs; not about training on generated data |
| [CorpusId:291244936](https://api.semanticscholar.org/CorpusId:291244936) | 2026-10-13 | critique models for math reasoning gains; excluded capability theme |
| [2411.04905](https://arxiv.org/abs/2411.04905) | 2026-10-13 | code LLM training cookbook; model report not about collapse |
| [2604.03647](https://arxiv.org/abs/2604.03647) | 2026-10-13 | unsupervised self-evolution of MLLMs for reasoning gains; excluded self-training theme |
| [CorpusId:269696779](https://api.semanticscholar.org/CorpusId:269696779) | 2026-10-13 | caregiving language model development; unrelated to model collapse |
| [2508.02853](https://arxiv.org/abs/2508.02853) | 2026-10-13 | annotator disagreement modelling with synthetic annotations; no recursive loop |
| [CorpusId:2832081](https://api.semanticscholar.org/CorpusId:2832081) | 2026-10-13 | title: complementary learning systems in brain; not about training on generated data |
| [2412.06712](https://arxiv.org/abs/2412.06712) | 2026-10-13 | temporal merging of multimodal experts; not about recursive training on generated data |
| [2203.15556](https://arxiv.org/abs/2203.15556) | 2026-10-13 | compute-optimal scaling of model size and tokens; not about training on generated data |
| [CorpusId:274824037](https://api.semanticscholar.org/CorpusId:274824037) | 2026-10-13 | teacher-student pseudo labels for crop segmentation; not model collapse |
| [CorpusId:15349458](https://api.semanticscholar.org/CorpusId:15349458) | 2026-10-13 | machine translation evaluation metric; not about model collapse |
| [CorpusId:270272631](https://api.semanticscholar.org/CorpusId:270272631) | 2026-10-13 | GAN augmentation for pathology detection once; no recursive loop |
| [CorpusId:286264506](https://api.semanticscholar.org/CorpusId:286264506) | 2026-10-13 | economic model of human knowledge collapse from AI reliance; no model trained on generated data |
| [2312.05114](https://arxiv.org/abs/2312.05114) | 2026-10-13 | privacy metrics for synthetic data release; no recursive training on generated data |
| [CorpusId:4056326](https://api.semanticscholar.org/CorpusId:4056326) | 2026-10-13 | cellular autophagy in memory erasure; not model autophagy of generative models |
| [1705.08848](https://arxiv.org/abs/1705.08848) | 2026-10-13 | optimal transport domain adaptation; unrelated to model collapse |
| [2402.11260](https://arxiv.org/abs/2402.11260) | 2026-10-13 | lifelong-learning adapter method for LLMs; not about recursive training on generated data |
| [CorpusId:278787872](https://api.semanticscholar.org/CorpusId:278787872) | 2026-10-13 | self-improvement for length generalization gains; excluded capability self-training |
| [CorpusId:281510374](https://api.semanticscholar.org/CorpusId:281510374) | 2026-10-13 | federated learning for edge resource allocation; not about model collapse |
| [2609.17699](https://arxiv.org/abs/2609.17699) | 2026-10-13 | synthetic data generation framework; synthetic data used once, no recursive loop |
| [2303.13592](https://arxiv.org/abs/2303.13592) | 2026-10-13 | prompting LLMs to generate code-mixed text; not about training on generated data across generations |
| [1907.05600](https://arxiv.org/abs/1907.05600) | 2026-10-13 | introduces score-matching generative model; not about recursive training |
| [2506.09643](https://arxiv.org/abs/2506.09643) | 2026-10-13 | sign language production as one-time data augmentation; no recursion |
| [2301.10226](https://arxiv.org/abs/2301.10226) | 2026-10-13 | LLM output watermarking for misuse, not tested against recursive degradation; excluded watermarking theme |
| [CorpusId:42933599](https://api.semanticscholar.org/CorpusId:42933599) | 2026-10-13 | statistics textbook on nonparametric estimation, by its title; general background, not recursive training |
| [CorpusId:237934792](https://api.semanticscholar.org/CorpusId:237934792) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [CorpusId:158843618](https://api.semanticscholar.org/CorpusId:158843618) | 2026-10-13 | 2018 SSRN essay on the changing role of academics (per S2 tldr; title alone is uninformative); not about recursive training on generated data |
| [CorpusId:403317](https://api.semanticscholar.org/CorpusId:403317) | 2026-10-13 | GPU inference for topic models; not about training on generated data |
| [CorpusId:26687093](https://api.semanticscholar.org/CorpusId:26687093) | 2026-10-13 | philosophy of mind and objectivity; unrelated to generative models |
| [2509.25004](https://arxiv.org/abs/2509.25004) | 2026-10-13 | RLVR curriculum for reasoning gains; excluded self-training for capability |
| [2308.09067](https://arxiv.org/abs/2308.09067) | 2026-10-13 | linguistic comparison of human and LLM news text; no training on generated data |
| [CorpusId:289691545](https://api.semanticscholar.org/CorpusId:289691545) | 2026-10-13 | about mathematics practice and AI; not recursive training |
| [CorpusId:248247064](https://api.semanticscholar.org/CorpusId:248247064) | 2026-10-13 | active learning for social-network content classification; the topic is recursive training of generative models |
| [2504.12427](https://arxiv.org/abs/2504.12427) | 2026-10-13 | position on compensating training data labour; not degradation across generations |
| [2601.22146](https://arxiv.org/abs/2601.22146) | 2026-10-13 | synthetic instruction data used once for pretraining; no recursive loop |
| [2006.05531](https://arxiv.org/abs/2006.05531) | 2026-10-13 | molecular conformer dataset; unrelated to recursive training |
| [2609.37891](https://arxiv.org/abs/2609.37891) | 2026-10-13 | fully synthetic pretraining corpus for LLMs; synthetic data used once, no recursive loop |
| [CorpusId:270668346](https://api.semanticscholar.org/CorpusId:270668346) | 2026-10-13 | title is about recommender systems and health; not recursive training |
| [2412.04346](https://arxiv.org/abs/2412.04346) | 2026-10-13 | robust performative prediction for predictive models; not generative models trained on generated data |
| [2507.13614](https://arxiv.org/abs/2507.13614) | 2026-10-13 | linguistic profiling of human versus LLM text; no training on generated data |
| [CorpusId:280390782](https://api.semanticscholar.org/CorpusId:280390782) | 2026-10-13 | philosophical critique of output homogenization; no recursive training |
| [2402.17801](https://arxiv.org/abs/2402.17801) | 2026-10-13 | economic model of copyright and AI development; no recursion on generated data |
| [2608.20318](https://arxiv.org/abs/2608.20318) | 2026-10-13 | benchmark for agents designing training algorithms for self-improvement; not distribution degradation from generated data |
| [2102.09672](https://arxiv.org/abs/2102.09672) | 2026-10-13 | improved diffusion model training; no recursive training |
| [CorpusId:189874512](https://api.semanticscholar.org/CorpusId:189874512) | 2026-10-13 | 2016 medical-journal editorial (title only, venue checked); the topic is recursive training of generative models |
| [2604.11546](https://arxiv.org/abs/2604.11546) | 2026-10-13 | evaluates LLM watermark spoofing robustness; not tested against model collapse |
| [2406.19593](https://arxiv.org/abs/2406.19593) | 2026-10-13 | synthetic multimodal VQA dataset used once; no recursive loop |
| [1904.08783](https://arxiv.org/abs/1904.08783) | 2026-10-13 | gender bias in contextual embeddings; not about recursive training |
| [CorpusId:326772](https://api.semanticscholar.org/CorpusId:326772) | 2026-10-13 | GAN convergence of one training run; no recursion |
| [CorpusId:292665458](https://api.semanticscholar.org/CorpusId:292665458) | 2026-10-13 | about AI misuse in scientific publishing; not recursive training |
| [2604.25110](https://arxiv.org/abs/2604.25110) | 2026-10-13 | position on one-step knowledge distillation losses; no recursive generations |
| [2506.08872](https://arxiv.org/abs/2506.08872) | 2026-10-13 | human EEG study of LLM-assisted writing; not model training |
| [2405.11612](https://arxiv.org/abs/2405.11612) | 2026-10-13 | sociotechnical risks of generative AI for information access; collapse not its subject |
| [2312.09241](https://arxiv.org/abs/2312.09241) | 2026-10-13 | synthetic math dataset used once for fine-tuning; no recursive loop |
| [2106.05527](https://arxiv.org/abs/2106.05527) | 2026-10-13 | diffusion score training technique; unrelated to model collapse |
| [2510.08236](https://arxiv.org/abs/2510.08236) | 2026-10-13 | political bias in LLMs; not about model collapse |
| [2608.11348](https://arxiv.org/abs/2608.11348) | 2026-10-13 | inference-time self-feeding to detect backdoors; no training on generated data |
| [2503.07660](https://arxiv.org/abs/2503.07660) | 2026-10-13 | position on superalignment research; unrelated to recursive training on generated data |
| [CorpusId:270278744](https://api.semanticscholar.org/CorpusId:270278744) | 2026-10-13 | philosophical essay on AI-generated content; not recursive training |
| [CorpusId:282687846](https://api.semanticscholar.org/CorpusId:282687846) | 2026-10-13 | Pl@ntNet human label aggregation (tldr); not training generative models on generated data |
| [2503.08684](https://arxiv.org/abs/2503.08684) | 2026-10-13 | retriever source bias toward LLM text; retrieval, not training on generated data |
| [2408.05842](https://arxiv.org/abs/2408.05842) | 2026-10-13 | role-playing game engine; unrelated to model collapse |
| [CorpusId:196194557](https://api.semanticscholar.org/CorpusId:196194557) | 2026-10-13 | parallel corpus resource; unrelated to model collapse |
| [2309.10105](https://arxiv.org/abs/2309.10105) | 2026-10-13 | catastrophic forgetting from fine-tuning; not about training on generated data |
| [CorpusId:123265791](https://api.semanticscholar.org/CorpusId:123265791) | 2026-10-13 | finite element modelling of concrete beams; unrelated to generative models |
| [2604.08553](https://arxiv.org/abs/2604.08553) | 2026-10-13 | pseudo-labels for LLM graph learning; not recursive generative training |
| [astro-ph/9810321](https://arxiv.org/abs/astro-ph/9810321) | 2026-10-13 | magnetized cloud MHD simulations; unrelated to generative models |
| [CorpusId:280593993](https://api.semanticscholar.org/CorpusId:280593993) | 2026-10-13 | title concerns how humans change working with GenAI; not model retraining |
| [CorpusId:276783017](https://api.semanticscholar.org/CorpusId:276783017) | 2026-10-13 | targeted data synthesis for capability gains; synthetic data used once, no degradation question |
| [CorpusId:17747353](https://api.semanticscholar.org/CorpusId:17747353) | 2026-10-13 | psychology of hope and suicidal ideation; unrelated to generative models |
| [CorpusId:271273824](https://api.semanticscholar.org/CorpusId:271273824) | 2026-10-13 | about copyright and patent law for AI outputs; not recursive training |
| [2410.18982](https://arxiv.org/abs/2410.18982) | 2026-10-13 | O1 replication progress report; not about recursive training degradation |
| [2102.08570](https://arxiv.org/abs/2102.08570) | 2026-10-13 | optimising performative risk of predictive models; not generative models trained on generated data |
| [CorpusId:283765823](https://api.semanticscholar.org/CorpusId:283765823) | 2026-10-13 | securing local LLM assistants for research; not about recursive training |
| [2308.09911](https://arxiv.org/abs/2308.09911) | 2026-10-13 | noisy correspondence in person re-identification; unrelated to recursive training |
| [2607.05694](https://arxiv.org/abs/2607.05694) | 2026-10-13 | calibrating LLM watermark hyperparameters for detection; not tested as a defence against degradation across generations |
| [CorpusId:268261060](https://api.semanticscholar.org/CorpusId:268261060) | 2026-10-13 | title is about AI and scientific understanding; not recursive training |
| [2503.06413](https://arxiv.org/abs/2503.06413) | 2026-10-13 | generative augmentation loop for anomaly detection capability; not degradation over generations |
| [2408.04693](https://arxiv.org/abs/2408.04693) | 2026-10-13 | MoE fine-tuning cost characterisation; unrelated to model collapse |
| [2505.18591](https://arxiv.org/abs/2505.18591) | 2026-10-13 | Bayesian meta-reinforcement learning; not generative recursion |
| [2509.10147](https://arxiv.org/abs/2509.10147) | 2026-10-13 | AI agent economies framework; not about recursive training on generated data |
| [2408.04237](https://arxiv.org/abs/2408.04237) | 2026-10-13 | AI-text detector motivated by disinformation; not tested against collapse |
| [CorpusId:289810732](https://api.semanticscholar.org/CorpusId:289810732) | 2026-10-13 | watermarking under jailbreaks, not tested as a collapse defence; excluded theme |
| [1908.04319](https://arxiv.org/abs/1908.04319) | 2026-10-13 | repetition from likelihood training in one model; no recursion over generations |
| [2405.01820](https://arxiv.org/abs/2405.01820) | 2026-10-13 | ethical risks of synthetic data used once; no recursive loop |
| [1610.04420](https://arxiv.org/abs/1610.04420) | 2026-10-13 | domain adaptation theory with optimal transport; unrelated to model collapse |
| [2406.12655](https://arxiv.org/abs/2406.12655) | 2026-10-13 | review of code-generation benchmarks and metrics; not about model collapse |
| [2308.03977](https://arxiv.org/abs/2308.03977) | 2026-10-13 | rendered synthetic images for representation learning used once; no recursive loop |
| [2402.14658](https://arxiv.org/abs/2402.14658) | 2026-10-13 | code generation with execution feedback; not about recursive training degradation |
| [CorpusId:280322222](https://api.semanticscholar.org/CorpusId:280322222) | 2026-10-13 | medical reasoning via verifiable problems; capability training, no degradation question |
| [CorpusId:275692081](https://api.semanticscholar.org/CorpusId:275692081) | 2026-10-13 | projects exhaustion of human data stocks, by its title; motivation for synthetic data, not about training on generated data |
| [2309.14225](https://arxiv.org/abs/2309.14225) | 2026-10-13 | adversarial imitation for humanoid locomotion; no recursive generative retraining |
| [2104.07540](https://arxiv.org/abs/2104.07540) | 2026-10-13 | PLM-generated datasets used once for embeddings; no recursive loop |
| [CorpusId:275584851](https://api.semanticscholar.org/CorpusId:275584851) | 2026-10-13 | detects mosaic augmentation in image datasets; not generated-data recursion |
| [2203.13474](https://arxiv.org/abs/2203.13474) | 2026-10-13 | open code model for program synthesis; not about model collapse |
| [2410.13850](https://arxiv.org/abs/2410.13850) | 2026-10-13 | influence functions for diffusion attribution; no recursive training |
| [CorpusId:4797951](https://api.semanticscholar.org/CorpusId:4797951) | 2026-10-13 | title: Wright's population genetics; biology, not generative models |
| [1911.11288](https://arxiv.org/abs/1911.11288) | 2026-10-13 | 3D autolabeling with shape priors; synthetic data used for perception, no recursive generative loop |
| [2505.12453](https://arxiv.org/abs/2505.12453) | 2026-10-13 | federated recommender security; unrelated to model collapse |
| [CorpusId:272202679](https://api.semanticscholar.org/CorpusId:272202679) | 2026-10-13 | argument about LLMs and human cognition; not recursive training |
| [2403.07974](https://arxiv.org/abs/2403.07974) | 2026-10-13 | contamination-free code benchmark; not about recursive training on generated data |
| [2407.03502](https://arxiv.org/abs/2407.03502) | 2026-10-13 | synthetic post-training data generated once; cites collapse only as motivation |
| [CorpusId:1353923](https://api.semanticscholar.org/CorpusId:1353923) | 2026-10-13 | software quality and code review practices; not about model collapse |
| [2410.04699](https://arxiv.org/abs/2410.04699) | 2026-10-13 | user study of human reliance on LLM suggestions; not model training |
| [CorpusId:46865883](https://api.semanticscholar.org/CorpusId:46865883) | 2026-10-13 | historical Hungarian corpus creation (title only); the topic is recursive training of generative models |
| [2401.13481](https://arxiv.org/abs/2401.13481) | 2026-10-13 | effect of AI ideas on human idea diversity; humans, not models trained on generated data |
| [CorpusId:274060377](https://api.semanticscholar.org/CorpusId:274060377) | 2026-10-13 | about RLHF reward dropout; not training on generated data across generations |
| [2312.02120](https://arxiv.org/abs/2312.02120) | 2026-10-13 | synthetic instruction data used once for code models; no recursive loop |
| [CorpusId:129729693](https://api.semanticscholar.org/CorpusId:129729693) | 2026-10-13 | volcanic column simulation; unrelated to generative models |
| [CorpusId:274927982](https://api.semanticscholar.org/CorpusId:274927982) | 2026-10-13 | AI text detection study; not tested against degradation across generations |
| [CorpusId:221542306](https://api.semanticscholar.org/CorpusId:221542306) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2510.05197](https://arxiv.org/abs/2510.05197) | 2026-10-13 | predicting pass@k scaling; not training on generated data |
| [math/0111020](https://arxiv.org/abs/math/0111020) | 2026-10-13 | Fisher information in the central limit theorem; unrelated to model collapse |
| [2402.18463](https://arxiv.org/abs/2402.18463) | 2026-10-13 | AI content effect on an art community platform; not training of models |
| [2507.00054](https://arxiv.org/abs/2507.00054) | 2026-10-13 | reward-guided distillation for reasoning in small models; one-time synthetic data for capability |
| [CorpusId:286946559](https://api.semanticscholar.org/CorpusId:286946559) | 2026-10-13 | AI in remanufacturing supply chains, by its title; unrelated to recursive training |
| [CorpusId:292383792](https://api.semanticscholar.org/CorpusId:292383792) | 2026-10-13 | review of LLMs in patent work, by its title; not training on generated data |
| [CorpusId:272567168](https://api.semanticscholar.org/CorpusId:272567168) | 2026-10-13 | ethical evaluation of ChatGPT; unrelated to model collapse |
| [2405.01797](https://arxiv.org/abs/2405.01797) | 2026-10-13 | strategic classification with imitative agents; not generative models trained on generated data |
| [CorpusId:220260639](https://api.semanticscholar.org/CorpusId:220260639) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [CorpusId:514983](https://api.semanticscholar.org/CorpusId:514983) | 2026-10-13 | title: complementary learning systems neuroscience theory; not about training on generated data |
| [1812.03596](https://arxiv.org/abs/1812.03596) | 2026-10-13 | task-free continual learning method; forgetting, not training on generated data |
| [CorpusId:2057420](https://api.semanticscholar.org/CorpusId:2057420) | 2026-10-13 | Wasserstein GAN training objective; within one run, no recursion |
| [CorpusId:61806147](https://api.semanticscholar.org/CorpusId:61806147) | 2026-10-13 | GAN survey; collapse means GAN mode collapse, an excluded theme |
| [CorpusId:285586641](https://api.semanticscholar.org/CorpusId:285586641) | 2026-10-13 | active learning loop for materials discovery gains; not degradation across generations |
| [2605.30650](https://arxiv.org/abs/2605.30650) | 2026-10-13 | survey of trustworthy AI in fintech; not generative models trained on generated data |
| [2209.00771](https://arxiv.org/abs/2209.00771) | 2026-10-13 | optimising performative risk under weak convexity; not generative models trained on generated data |
| [2508.16168](https://arxiv.org/abs/2508.16168) | 2026-10-13 | tropical cyclone forecasting with diffusion; no recursive training |
| [1912.10389](https://arxiv.org/abs/1912.10389) | 2026-10-13 | sociocultural data collection practices; not about synthetic-data recursion |
| [2410.12766](https://arxiv.org/abs/2410.12766) | 2026-10-13 | variance collapse in non-local weight merging; different collapse, no generated data |
| [CorpusId:285576591](https://api.semanticscholar.org/CorpusId:285576591) | 2026-10-13 | LLM adoption in parliaments; not about model collapse |
| [CorpusId:272599308](https://api.semanticscholar.org/CorpusId:272599308) | 2026-10-13 | human-AI ensembling for idea generation; not training on generated data |
| [CorpusId:122025212](https://api.semanticscholar.org/CorpusId:122025212) | 2026-10-13 | psychometric cognitive diagnosis model; not about generative-model recursion |
| [CorpusId:288165952](https://api.semanticscholar.org/CorpusId:288165952) | 2026-10-13 | title: data augmentation failures in remote sensing detection; not recursive training of generative models |
| [CorpusId:161234019](https://api.semanticscholar.org/CorpusId:161234019) | 2026-10-13 | title: review of Darwin's book; biology, not generative model training |
| [CorpusId:14678361](https://api.semanticscholar.org/CorpusId:14678361) | 2026-10-13 | RL from human feedback shaping (no abstract); title not about model collapse |
| [2402.05070](https://arxiv.org/abs/2402.05070) | 2026-10-13 | pluralistic alignment roadmap; not about recursive training |
| [2609.12472](https://arxiv.org/abs/2609.12472) | 2026-10-13 | LLM text watermarking for identifying generated text; not tested as a defence against degradation across generations |
| [CorpusId:285630214](https://api.semanticscholar.org/CorpusId:285630214) | 2026-10-13 | roles of generative AI in misinformation; not about recursive training |
| [1611.01257](https://arxiv.org/abs/1611.01257) | 2026-10-13 | Wikipedia social movement study; not about generative models |
| [2406.11073](https://arxiv.org/abs/2406.11073) | 2026-10-13 | limits of machine-text detectors; not tested against collapse across generations |
| [2310.13595](https://arxiv.org/abs/2310.13595) | 2026-10-13 | history and risks of RLHF reward models; not about recursive training on generated data |
| [CorpusId:270075908](https://api.semanticscholar.org/CorpusId:270075908) | 2026-10-13 | real-time image dehazing hardware; unrelated to model collapse |
| [CorpusId:61156458](https://api.semanticscholar.org/CorpusId:61156458) | 2026-10-13 | cellular autophagy in pancreatic cancer; not model autophagy of generative models |
| [2404.18353](https://arxiv.org/abs/2404.18353) | 2026-10-13 | security of LLM-generated C code; no recursive training |
| [CorpusId:267774337](https://api.semanticscholar.org/CorpusId:267774337) | 2026-10-13 | title is about ethnography and AI language; not recursive training |
| [1803.09010](https://arxiv.org/abs/1803.09010) | 2026-10-13 | dataset documentation practice; not about training on generated data |
| [2607.00871](https://arxiv.org/abs/2607.00871) | 2026-10-13 | gated self-modification of coding agents for capability; not distribution degradation |
| [CorpusId:5048884](https://api.semanticscholar.org/CorpusId:5048884) | 2026-10-13 | distributed computing on anonymous networks (title only); the topic is recursive training of generative models |
| [2310.02527](https://arxiv.org/abs/2310.02527) | 2026-10-13 | teacher-LLM curriculum for instruction tuning, synthetic data used for capability; no degradation question |
| [CorpusId:292289389](https://api.semanticscholar.org/CorpusId:292289389) | 2026-10-13 | resolved as Intellectual Property and Creative Machines, an economics paper; not recursive training |
| [2305.00054](https://arxiv.org/abs/2305.00054) | 2026-10-13 | data valuation method; not about training on generated data across generations |
| [2604.18649](https://arxiv.org/abs/2604.18649) | 2026-10-13 | legal position on copyright infringement in training; not about recursive training degradation |
| [2507.00075](https://arxiv.org/abs/2507.00075) | 2026-10-13 | theory of self-improvement capability gains; excluded self-training theme |
| [CorpusId:286245019](https://api.semanticscholar.org/CorpusId:286245019) | 2026-10-13 | explainability architecture for regulated ML; not about model collapse |
| [CorpusId:35373864](https://api.semanticscholar.org/CorpusId:35373864) | 2026-10-13 | cellular autophagy in hepatocellular carcinoma; not model autophagy of generative models |
| [2003.06228](https://arxiv.org/abs/2003.06228) | 2026-10-13 | RNN wavefunctions for quantum spin systems; iterative retraining here is not training on generated data |
| [CorpusId:11080756](https://api.semanticscholar.org/CorpusId:11080756) | 2026-10-13 | machine translation evaluation metric; not about model collapse |
| [2502.10510](https://arxiv.org/abs/2502.10510) | 2026-10-13 | data mixture optimisation; no recursion over generated data |
| [2412.15115](https://arxiv.org/abs/2412.15115) | 2026-10-13 | LLM technical report; main finding not about model collapse |
| [2507.00808](https://arxiv.org/abs/2507.00808) | 2026-10-13 | interactive TTS style refinement; not training on generated data |
| [2501.02869](https://arxiv.org/abs/2501.02869) | 2026-10-13 | medical instruction dataset and DPO alignment; not recursive training |
| [2210.11610](https://arxiv.org/abs/2210.11610) | 2026-10-13 | self-training on own outputs for reasoning gains; excluded capability self-improvement |
| [2508.17465](https://arxiv.org/abs/2508.17465) | 2026-10-13 | bias in Stable Diffusion outputs; no recursive training loop |
| [CorpusId:17817780](https://api.semanticscholar.org/CorpusId:17817780) | 2026-10-13 | physiological signal reconstruction (title only); the topic is recursive training of generative models |
| [2502.04468](https://arxiv.org/abs/2502.04468) | 2026-10-13 | iterative diffusion fine-tuning for conditional sampling; capability method, not degradation over generations |
| [1310.4375](https://arxiv.org/abs/1310.4375) | 2026-10-13 | Wasserstein barycenter algorithms; unrelated to model collapse |
| [CorpusId:287031496](https://api.semanticscholar.org/CorpusId:287031496) | 2026-10-13 | synthetic health data with federated learning used once; no recursive loop |
| [2609.34374](https://arxiv.org/abs/2609.34374) | 2026-10-13 | bias correction for AI-feedback preference labels in alignment; single-round synthetic labels, not recursive training |
| [CorpusId:273547059](https://api.semanticscholar.org/CorpusId:273547059) | 2026-10-13 | production text watermarking for misuse, not tested against degradation; excluded watermarking theme |
| [CorpusId:17595679](https://api.semanticscholar.org/CorpusId:17595679) | 2026-10-13 | cellular autophagy in neonatal enterocolitis; not model autophagy of generative models |
| [2601.05414](https://arxiv.org/abs/2601.05414) | 2026-10-13 | audit of LLM sampling from specified distributions; no training on generated data |
| [CorpusId:117973861](https://api.semanticscholar.org/CorpusId:117973861) | 2026-10-13 | Gaussian Hilbert space mathematics, from title; unrelated to collapse |
| [2606.28343](https://arxiv.org/abs/2606.28343) | 2026-10-13 | crowding and marginalisation in retrieval-augmented agents; not training on generated data |
| [CorpusId:9094329](https://api.semanticscholar.org/CorpusId:9094329) | 2026-10-13 | empirical software engineering study of code reviews; not about model collapse |
| [CorpusId:286780793](https://api.semanticscholar.org/CorpusId:286780793) | 2026-10-13 | federated threat detection security; not about model collapse |
| [CorpusId:275956059](https://api.semanticscholar.org/CorpusId:275956059) | 2026-10-13 | AI agents for cloud threat detection; not about model collapse |
| [2105.05233](https://arxiv.org/abs/2105.05233) | 2026-10-13 | diffusion image synthesis quality; no recursive training |
| [2603.26130](https://arxiv.org/abs/2603.26130) | 2026-10-13 | AI code review benchmark; unrelated to recursive generative training |
| [CorpusId:18315359](https://api.semanticscholar.org/CorpusId:18315359) | 2026-10-13 | bacteriophage experimental evolution; unrelated to generative models |
| [CorpusId:270286396](https://api.semanticscholar.org/CorpusId:270286396) | 2026-10-13 | cultural analysis of chatbots as animation; unrelated to model collapse |
| [CorpusId:285189184](https://api.semanticscholar.org/CorpusId:285189184) | 2026-10-13 | game-theoretic welfare of AI-democratized content markets; no model training on generated data |
| [2503.08741](https://arxiv.org/abs/2503.08741) | 2026-10-13 | multimodal synthetic instruction data used once; no recursive loop |
| [2605.23278](https://arxiv.org/abs/2605.23278) | 2026-10-13 | theory of what next-token prediction learns from real text; not about training on generated data |
| [2307.09288](https://arxiv.org/abs/2307.09288) | 2026-10-13 | Llama 2 model report; no finding about model collapse |
| [1312.6114](https://arxiv.org/abs/1312.6114) | 2026-10-13 | VAE method paper; no recursive training on generated data |
| [2505.19550](https://arxiv.org/abs/2505.19550) | 2026-10-13 | about testing for general intelligence; unrelated to recursive training on generated data |
| [1204.2606](https://arxiv.org/abs/1204.2606) | 2026-10-13 | privacy via random projection; unrelated to model collapse |
| [2510.07192](https://arxiv.org/abs/2510.07192) | 2026-10-13 | data poisoning attacks in pretraining; not about recursive training on model outputs |
| [2410.22118](https://arxiv.org/abs/2410.22118) | 2026-10-13 | inference acceleration effect on bias; no recursive training |
| [2011.07018](https://arxiv.org/abs/2011.07018) | 2026-10-13 | privacy of synthetic data publishing; no recursive training across generations |
| [2311.03099](https://arxiv.org/abs/2311.03099) | 2026-10-13 | DARE delta-parameter merging; not about recursive training on generated data |
| [CorpusId:275404638](https://api.semanticscholar.org/CorpusId:275404638) | 2026-10-13 | occupational bias in word embeddings; not training on generated data |
| [2404.12691](https://arxiv.org/abs/2404.12691) | 2026-10-13 | data provenance and consent infrastructure; not recursive training on generated data |
| [CorpusId:341628](https://api.semanticscholar.org/CorpusId:341628) | 2026-10-13 | title: evolution of recombination; biology, not generative models |
| [2401.12970](https://arxiv.org/abs/2401.12970) | 2026-10-13 | AI-text detection method not tested against degradation; excluded detection theme |
| [2410.07163](https://arxiv.org/abs/2410.07163) | 2026-10-13 | LLM unlearning optimization; collapse here is within one training run, no recursion |
| [CorpusId:107948922](https://api.semanticscholar.org/CorpusId:107948922) | 2026-10-13 | seismic collapse risk of concrete buildings; unrelated to generative models |
| [2211.15533](https://arxiv.org/abs/2211.15533) | 2026-10-13 | source code dataset release; not about model collapse |
| [CorpusId:18319233](https://api.semanticscholar.org/CorpusId:18319233) | 2026-10-13 | cellular autophagy in ischemic stroke; not model autophagy of generative models |
| [CorpusId:289810553](https://api.semanticscholar.org/CorpusId:289810553) | 2026-10-13 | uses 'collapse' for tokenizer fragmentation of domain terms with an attention adapter; no training on model-generated data across generations |
| [2405.20469](https://arxiv.org/abs/2405.20469) | 2026-10-13 | robustness of models trained once on synthetic images; no recursive loop |
| [CorpusId:267770019](https://api.semanticscholar.org/CorpusId:267770019) | 2026-10-13 | survey of LLMs annotating data; no recursive training over generations |
| [CorpusId:278433924](https://api.semanticscholar.org/CorpusId:278433924) | 2026-10-13 | MLOps framework for radiology; not generative recursion |
| [CorpusId:279075149](https://api.semanticscholar.org/CorpusId:279075149) | 2026-10-13 | position paper on expert orchestration of LLMs; not about training on generated data |
| [2407.02030](https://arxiv.org/abs/2407.02030) | 2026-10-13 | debiasing LLMs via contact prompts; not model collapse |
| [CorpusId:282266837](https://api.semanticscholar.org/CorpusId:282266837) | 2026-10-13 | LLM text detection in the wild for misinformation; excluded detection not tested against collapse |
| [2510.09426](https://arxiv.org/abs/2510.09426) | 2026-10-13 | model report trained once on curated synthetic data; no recursive loop, excluded single-use synthetic theme |
| [2506.16653](https://arxiv.org/abs/2506.16653) | 2026-10-13 | security and sycophancy risks of coding LLMs; not recursive training |
| [2204.07683](https://arxiv.org/abs/2204.07683) | 2026-10-13 | self-refinement for unsupervised domain adaptation; no recursive generative retraining |
| [CorpusId:241651379](https://api.semanticscholar.org/CorpusId:241651379) | 2026-10-13 | critical history of ImageNet; not about generated data |
| [2404.18445](https://arxiv.org/abs/2404.18445) | 2026-10-13 | human creators' supply of training data on Unsplash; not training on model-generated data |
| [2501.07886](https://arxiv.org/abs/2501.07886) | 2026-10-13 | post-training under unreliable supervision; label refinement for capability, not generational degradation |
| [2606.03165](https://arxiv.org/abs/2606.03165) | 2026-10-13 | metrics for LLM lexical overuse from preference learning; not training on generated data |
| [CorpusId:287891343](https://api.semanticscholar.org/CorpusId:287891343) | 2026-10-13 | philosophical critique of longtermism; not about model collapse |
| [2604.20855](https://arxiv.org/abs/2604.20855) | 2026-10-13 | agentic web exploration for creative synthesis; not about model degradation |
| [1810.04805](https://arxiv.org/abs/1810.04805) | 2026-10-13 | BERT model paper; no finding about recursive training |
| [2403.14117](https://arxiv.org/abs/2403.14117) | 2026-10-13 | design space of writing assistants; unrelated to model collapse |
| [2502.17144](https://arxiv.org/abs/2502.17144) | 2026-10-13 | RNN variational Monte Carlo for antiferromagnets; the topic is recursive training of generative models |
| [CorpusId:284726680](https://api.semanticscholar.org/CorpusId:284726680) | 2026-10-13 | essay on data scale and interpretive depth; not about recursive training |
| [2304.01373](https://arxiv.org/abs/2304.01373) | 2026-10-13 | LLM training-dynamics suite; no recursive training |
| [CorpusId:6211281](https://api.semanticscholar.org/CorpusId:6211281) | 2026-10-13 | human sentence comprehension theory; not about generative model training |
| [CorpusId:292270710](https://api.semanticscholar.org/CorpusId:292270710) | 2026-10-13 | title is about audio-visual semantics via language-guided synthesis; not recursive training |
| [CorpusId:246025955](https://api.semanticscholar.org/CorpusId:246025955) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2402.04376](https://arxiv.org/abs/2402.04376) | 2026-10-13 | weighted mixing of real and surrogate data in one training round; excluded one-shot synthetic use |
| [2206.07271](https://arxiv.org/abs/2206.07271) | 2026-10-13 | about human detection of AI-written self-presentations; no training on generated data, the topic's subject |
| [1906.02243](https://arxiv.org/abs/1906.02243) | 2026-10-13 | energy cost of NLP training; not about model collapse |
| [2006.03463](https://arxiv.org/abs/2006.03463) | 2026-10-13 | energy-latency adversarial attacks; unrelated to recursive generative training |
| [CorpusId:281834832](https://api.semanticscholar.org/CorpusId:281834832) | 2026-10-13 | breast cancer risk prediction network; no recursive training on generated data |
| [CorpusId:272759754](https://api.semanticscholar.org/CorpusId:272759754) | 2026-10-13 | AIoT and blockchain data trust; unrelated to model collapse |
| [2106.05095](https://arxiv.org/abs/2106.05095) | 2026-10-13 | pseudo-label self-training for segmentation gains; excluded self-training theme, no generational degradation |
| [CorpusId:263824644](https://api.semanticscholar.org/CorpusId:263824644) | 2026-10-13 | title on authorship and producers; no indication of training on generated data |
| [2502.15916](https://arxiv.org/abs/2502.15916) | 2026-10-13 | speech dataset governance framework; not model collapse |
| [2207.01780](https://arxiv.org/abs/2207.01780) | 2026-10-13 | code generation via reinforcement learning; not about model collapse |
| [CorpusId:281499946](https://api.semanticscholar.org/CorpusId:281499946) | 2026-10-13 | secure multi-cloud LLM data pipelines; not about recursive training |
| [2410.14208](https://arxiv.org/abs/2410.14208) | 2026-10-13 | teacher synthesizes data for student once; no recursive degradation studied |
| [2308.03549](https://arxiv.org/abs/2308.03549) | 2026-10-13 | Chinese medical LLM training pipeline; not about training on generated data |
| [2405.19266](https://arxiv.org/abs/2405.19266) | 2026-10-13 | pediatric medical LLM; unrelated to model collapse |
| [2402.15602](https://arxiv.org/abs/2402.15602) | 2026-10-13 | minimax rates for diffusion score estimation; no recursive training |
| [CorpusId:289420478](https://api.semanticscholar.org/CorpusId:289420478) | 2026-10-13 | multimodal LLM for industrial fault diagnosis; unrelated to recursive training |
| [CorpusId:268910228](https://api.semanticscholar.org/CorpusId:268910228) | 2026-10-13 | media analysis of AI hype; unrelated to model collapse |
| [CorpusId:195064188](https://api.semanticscholar.org/CorpusId:195064188) | 2026-10-13 | approximate multiplier hardware design; the topic is recursive training of generative models |
| [2106.09667](https://arxiv.org/abs/2106.09667) | 2026-10-13 | backdoor poisoning attacks on CLIP; not model collapse across generations |
| [CorpusId:151675170](https://api.semanticscholar.org/CorpusId:151675170) | 2026-10-13 | 2004 humanities book chapter (title only, venue checked); the topic is recursive training of generative models |
| [1910.03771](https://arxiv.org/abs/1910.03771) | 2026-10-13 | NLP software library; not about model collapse |
| [CorpusId:277227974](https://api.semanticscholar.org/CorpusId:277227974) | 2026-10-13 | error propagation in biological databases from synthetic data; database curation, not model degradation over generations |
| [2405.00254](https://arxiv.org/abs/2405.00254) | 2026-10-13 | heterogeneous RLHF feedback; not about recursive training |
| [2607.10803](https://arxiv.org/abs/2607.10803) | 2026-10-13 | parameter importance and weight-perturbation failure in LLMs; collapse here is not recursive training |
| [CorpusId:275315009](https://api.semanticscholar.org/CorpusId:275315009) | 2026-10-13 | about malicious npm package detection; unrelated to recursive training |
| [CorpusId:285177805](https://api.semanticscholar.org/CorpusId:285177805) | 2026-10-13 | LLM detection of malicious npm updates; unrelated to generated-data training |
| [CorpusId:290436620](https://api.semanticscholar.org/CorpusId:290436620) | 2026-10-13 | diffusion data augmentation for few-shot classification; synthetic data used once, an excluded theme |
| [CorpusId:22643337](https://api.semanticscholar.org/CorpusId:22643337) | 2026-10-13 | biomedical autophagy in cancer therapy (title only); the topic is recursive training of generative models |
| [2306.02707](https://arxiv.org/abs/2306.02707) | 2026-10-13 | imitation learning from GPT-4 traces for capability; synthetic data used once, an excluded theme |
| [CorpusId:272771240](https://api.semanticscholar.org/CorpusId:272771240) | 2026-10-13 | software studies book on programming culture (tldr); unrelated to model collapse |
| [2311.10741](https://arxiv.org/abs/2311.10741) | 2026-10-13 | data equity briefing for generative AI; not about degradation from recursive training |
| [CorpusId:267213265](https://api.semanticscholar.org/CorpusId:267213265) | 2026-10-13 | medical LLM model report; not about recursive training |
| [CorpusId:288112148](https://api.semanticscholar.org/CorpusId:288112148) | 2026-10-13 | resolved via OpenReview as Multilingual Arbitrage: one-shot synthetic data routing, cites collapse as motivation only |
| [CorpusId:249951086](https://api.semanticscholar.org/CorpusId:249951086) | 2026-10-13 | data-free black-box adversarial attack with GANs; GAN mode collapse, an excluded theme |
| [2306.04634](https://arxiv.org/abs/2306.04634) | 2026-10-13 | robustness of LLM watermarks to rewriting, not tested as a collapse defence; excluded theme |
| [CorpusId:171958512](https://api.semanticscholar.org/CorpusId:171958512) | 2026-10-13 | Buddhist philosophy of two truths (title only); the topic is recursive training of generative models |
| [1411.7766](https://arxiv.org/abs/1411.7766) | 2026-10-13 | face attribute prediction and CelebA dataset; not model collapse |
| [CorpusId:273650692](https://api.semanticscholar.org/CorpusId:273650692) | 2026-10-13 | AI literacy framework for translators; unrelated to model collapse |
| [1904.09751](https://arxiv.org/abs/1904.09751) | 2026-10-13 | decoding-induced text degeneration in one model; no recursion over generations |
| [CorpusId:308212](https://api.semanticscholar.org/CorpusId:308212) | 2026-10-13 | unsupervised feature learning analysis, from title; unrelated to model collapse |
| [2411.04956](https://arxiv.org/abs/2411.04956) | 2026-10-13 | privacy and re-identification in video diffusion; no recursive training loop |
| [CorpusId:31993898](https://api.semanticscholar.org/CorpusId:31993898) | 2026-10-13 | machine learning textbook; not about recursive training |
| [2501.09368](https://arxiv.org/abs/2501.09368) | 2026-10-13 | rewriting pretraining data into instruction pairs, used once; no recursion |
| [2501.05559](https://arxiv.org/abs/2501.05559) | 2026-10-13 | continual learning forgetting via model averaging; not about recursive training on generated data |
| [2602.03541](https://arxiv.org/abs/2602.03541) | 2026-10-13 | agent-based model of human cultural collapse from AI use; cites model collapse only as motivation |
| [2001.09768](https://arxiv.org/abs/2001.09768) | 2026-10-13 | philosophy of AI alignment; not about recursive training |
| [2312.07000](https://arxiv.org/abs/2312.07000) | 2026-10-13 | alignment of LLMs for honesty; not about training on generated data |
| [2308.13565](https://arxiv.org/abs/2308.13565) | 2026-10-13 | domain-specific LLMs for natural science; not about training on generated data |
| [CorpusId:84848284](https://api.semanticscholar.org/CorpusId:84848284) | 2026-10-13 | title: conservation genetics migration rule; not about generative models |
| [CorpusId:237470387](https://api.semanticscholar.org/CorpusId:237470387) | 2026-10-13 | cancer grade prediction from gene expression; the topic is recursive training of generative models |
| [2412.03824](https://arxiv.org/abs/2412.03824) | 2026-10-13 | about data governance capacities for frontier AI; not recursive training on generated data |
| [2508.16692](https://arxiv.org/abs/2508.16692) | 2026-10-13 | history and philosophy of AGI forecasting; not model collapse |
| [2011.03885](https://arxiv.org/abs/2011.03885) | 2026-10-13 | stateful performative prediction with strategic manipulation; not generative recursive training |
| [2502.04194](https://arxiv.org/abs/2502.04194) | 2026-10-13 | selecting in-distribution SFT responses from other LLMs; one-time synthetic data, no recursion |
| [CorpusId:2691726](https://api.semanticscholar.org/CorpusId:2691726) | 2026-10-13 | title: catastrophic forgetting in connectionist nets; not about training on generated data |
| [CorpusId:274684521](https://api.semanticscholar.org/CorpusId:274684521) | 2026-10-13 | legal analysis of AI-content labelling in China; cites degradation as motivation, tests no defence |
| [2405.13267](https://arxiv.org/abs/2405.13267) | 2026-10-13 | diffusion augmentation for astronomy images once; no recursive loop |
| [2511.04666](https://arxiv.org/abs/2511.04666) | 2026-10-13 | general theory of forgetting in learners; not about training on generated data |
| [CorpusId:239690879](https://api.semanticscholar.org/CorpusId:239690879) | 2026-10-13 | seismic horizon semi-supervised learning; the topic is recursive training of generative models |
| [CorpusId:140630797](https://api.semanticscholar.org/CorpusId:140630797) | 2026-10-13 | stratovolcano flank collapse analogue models; unrelated to generative models |
| [CorpusId:9742008](https://api.semanticscholar.org/CorpusId:9742008) | 2026-10-13 | cellular autophagy in oncogenic signalling; not model autophagy of generative models |
| [2305.14718](https://arxiv.org/abs/2305.14718) | 2026-10-13 | offline RL algorithm for LM alignment; not about recursive training degradation |
| [CorpusId:845669](https://api.semanticscholar.org/CorpusId:845669) | 2026-10-13 | information-theoretic inequalities, from title; unrelated to model collapse |
| [2509.23963](https://arxiv.org/abs/2509.23963) | 2026-10-13 | robustness of Chinchilla scaling laws; not model collapse |
| [CorpusId:280599973](https://api.semanticscholar.org/CorpusId:280599973) | 2026-10-13 | AI in 6G networks; unrelated to model collapse |
| [CorpusId:289584273](https://api.semanticscholar.org/CorpusId:289584273) | 2026-10-13 | review of continual learning for deployed LLMs; not about training on generated data |
| [1910.10683](https://arxiv.org/abs/1910.10683) | 2026-10-13 | T5 transfer learning study; no training on generated data |
| [CorpusId:12129661](https://api.semanticscholar.org/CorpusId:12129661) | 2026-10-13 | title: novelty search in evolutionary computation; not about training on generated data |
| [2406.11704](https://arxiv.org/abs/2406.11704) | 2026-10-13 | model report promoting synthetic data generation; no recursive degradation studied |
| [2411.02460](https://arxiv.org/abs/2411.02460) | 2026-10-13 | code-switching curriculum for multilingual LLMs; not model collapse |
| [2203.14465](https://arxiv.org/abs/2203.14465) | 2026-10-13 | iterative self-training for reasoning gains; excluded capability self-improvement |
| [CorpusId:277320679](https://api.semanticscholar.org/CorpusId:277320679) | 2026-10-13 | deepfake image detection with VLMs; detection not tested against collapse |
| [2402.19450](https://arxiv.org/abs/2402.19450) | 2026-10-13 | functional reasoning benchmarks and contamination gap; not model collapse |
| [CorpusId:289388143](https://api.semanticscholar.org/CorpusId:289388143) | 2026-10-13 | position on differential privacy in generative AI; not about training on generated data |
| [2510.25817](https://arxiv.org/abs/2510.25817) | 2026-10-13 | survey of data-efficient LLM post-training; synthetic data not studied recursively |
| [CorpusId:57246310](https://api.semanticscholar.org/CorpusId:57246310) | 2026-10-13 | ImageNet dataset paper; unrelated to recursive training on generated data |
| [2505.00661](https://arxiv.org/abs/2505.00661) | 2026-10-13 | generalization from in-context learning versus finetuning; no training on generated data across generations |
| [2408.16673](https://arxiv.org/abs/2408.16673) | 2026-10-13 | diversity loss from cross-entropy in one SFT run; no recursion over generations |
| [2401.08092](https://arxiv.org/abs/2401.08092) | 2026-10-13 | resource-efficient foundation model survey; not model collapse |
| [1905.10044](https://arxiv.org/abs/1905.10044) | 2026-10-13 | yes/no QA benchmark; not about training on generated data |
| [2107.03374](https://arxiv.org/abs/2107.03374) | 2026-10-13 | Codex code model evaluation; not about recursive training on generated data |
| [CorpusId:263802405](https://api.semanticscholar.org/CorpusId:263802405) | 2026-10-13 | synthetic healthcare data applications and privacy; no recursive training |
| [1711.09601](https://arxiv.org/abs/1711.09601) | 2026-10-13 | continual learning regulariser for forgetting; not model collapse from generated data |
| [CorpusId:211088712](https://api.semanticscholar.org/CorpusId:211088712) | 2026-10-13 | cellular autophagy in liver disease; not model autophagy of generative models |
| [2602.22519](https://arxiv.org/abs/2602.22519) | 2026-10-13 | information-theoretic theory of agency; not about recursive generative training |
| [2501.01834](https://arxiv.org/abs/2501.01834) | 2026-10-13 | agent collaboration for image captioning; not training on generated data loops |
| [2501.02059](https://arxiv.org/abs/2501.02059) | 2026-10-13 | closed-loop molecule generation retrained on new simulation data for capability gains; not degradation over generations |
| [2211.05414](https://arxiv.org/abs/2211.05414) | 2026-10-13 | prompt-based debiasing of language models; no recursion |
| [CorpusId:2352990](https://api.semanticscholar.org/CorpusId:2352990) | 2026-10-13 | score matching extensions, from title; estimation method, not collapse |
| [2601.20687](https://arxiv.org/abs/2601.20687) | 2026-10-13 | RL distillation for small on-premise models; not about recursive degradation |
| [CorpusId:283559176](https://api.semanticscholar.org/CorpusId:283559176) | 2026-10-13 | position on counterfactual world models (tldr); not recursive training |
| [2206.14486](https://arxiv.org/abs/2206.14486) | 2026-10-13 | data pruning and scaling laws on real data; not recursive training on generated data |
| [CorpusId:83340584](https://api.semanticscholar.org/CorpusId:83340584) | 2026-10-13 | title: outbreeding depression in biology; not about generative models |
| [CorpusId:62233163](https://api.semanticscholar.org/CorpusId:62233163) | 2026-10-13 | Turkish linguistics; not about generative models |
| [2408.03560](https://arxiv.org/abs/2408.03560) | 2026-10-13 | coreset selection for instruction finetuning; no generated-data recursion |
| [1906.07029](https://arxiv.org/abs/1906.07029) | 2026-10-13 | robot semantic mapping by label propagation; the topic is recursive training of generative models |
| [2602.03417](https://arxiv.org/abs/2602.03417) | 2026-10-13 | knowledge graph resource for factual grounding; not about recursive training |
| [2503.16444](https://arxiv.org/abs/2503.16444) | 2026-10-13 | filtered synthetic dialogue data for XAI explanations, used once; no recursion |
| [2511.21909](https://arxiv.org/abs/2511.21909) | 2026-10-13 | Wizard-of-Oz emotion dialogue corpus; not about generated-data training |
| [2304.14885](https://arxiv.org/abs/2304.14885) | 2026-10-13 | survey of Fisher-Rao distance formulas; not about recursive training |
| [CorpusId:124656337](https://api.semanticscholar.org/CorpusId:124656337) | 2026-10-13 | Wasserstein metric formula (no abstract); mathematical tool, not model collapse |
| [CorpusId:278373736](https://api.semanticscholar.org/CorpusId:278373736) | 2026-10-13 | GenAI and platform market power; economics, not model collapse |
| [2402.00530](https://arxiv.org/abs/2402.00530) | 2026-10-13 | instruction-tuning data filtering for efficiency; not about filtering generated data against collapse |
| [CorpusId:283923576](https://api.semanticscholar.org/CorpusId:283923576) | 2026-10-13 | AI text detection for social media; not tested as defence against degradation |
| [2310.11158](https://arxiv.org/abs/2310.11158) | 2026-10-13 | measures LLM creativity via divergent association; not about recursive training |
| [CorpusId:289768722](https://api.semanticscholar.org/CorpusId:289768722) | 2026-10-13 | instruction generation to boost reasoning; synthetic data for capability, no degradation question |
| [2001.08361](https://arxiv.org/abs/2001.08361) | 2026-10-13 | language model scaling laws; no recursion over generated data |
| [CorpusId:46915842](https://api.semanticscholar.org/CorpusId:46915842) | 2026-10-13 | biography of Stefan Banach; unrelated to recursive training of generative models |
| [2310.07849](https://arxiv.org/abs/2310.07849) | 2026-10-13 | LLM synthetic data used once for text classification; no recursive loop |
| [1911.02150](https://arxiv.org/abs/1911.02150) | 2026-10-13 | multi-query attention for fast decoding; not about model collapse |
| [1001.4456](https://arxiv.org/abs/1001.4456) | 2026-10-13 | astrophysical gas cloud collapse simulation; unrelated to generative models |
| [CorpusId:5560643](https://api.semanticscholar.org/CorpusId:5560643) | 2026-10-13 | score matching and denoising autoencoders, from title; not about collapse |
| [2606.23607](https://arxiv.org/abs/2606.23607) | 2026-10-13 | linear mode connectivity model merging; not about recursive training on generated data |
| [CorpusId:1648083](https://api.semanticscholar.org/CorpusId:1648083) | 2026-10-13 | distance metrics in high dimensions for indexing; unrelated to recursive training of generative models |
| [CorpusId:207063850](https://api.semanticscholar.org/CorpusId:207063850) | 2026-10-13 | regularized least squares rates; generic learning theory, not collapse |
| [CorpusId:284790390](https://api.semanticscholar.org/CorpusId:284790390) | 2026-10-13 | one-shot linguistic comparison of synthetic and human Spanish corpora; no recursive training loop |
| [1812.05159](https://arxiv.org/abs/1812.05159) | 2026-10-13 | example forgetting within one training run; not about generated training data |
| [CorpusId:2342929](https://api.semanticscholar.org/CorpusId:2342929) | 2026-10-13 | remanufacturing planning ML (title only); the topic is recursive training of generative models |
| [CorpusId:290490787](https://api.semanticscholar.org/CorpusId:290490787) | 2026-10-13 | philosophical reading of Turing 1950; not about generative model training |
| [2110.14168](https://arxiv.org/abs/2110.14168) | 2026-10-13 | math word problem dataset and verifiers; not about model collapse |
| [CorpusId:24451062](https://api.semanticscholar.org/CorpusId:24451062) | 2026-10-13 | title: speciation genetics; not about generative model training |
| [2402.01680](https://arxiv.org/abs/2402.01680) | 2026-10-13 | survey of LLM multi-agent systems; not about recursive training on generated data |
| [2405.15815](https://arxiv.org/abs/2405.15815) | 2026-10-13 | social route to human-like AI via novel data generation; not about models degrading on generated data |
| [CorpusId:209388289](https://api.semanticscholar.org/CorpusId:209388289) | 2026-10-13 | cellular autophagy in liver fibrosis; not model autophagy of generative models |
| [2303.18223](https://arxiv.org/abs/2303.18223) | 2026-10-13 | general LLM survey; model collapse at most in passing |
| [CorpusId:263774758](https://api.semanticscholar.org/CorpusId:263774758) | 2026-10-13 | bioethics commentary on personalized LLMs; cites self-consuming models only in passing |
| [CorpusId:269648877](https://api.semanticscholar.org/CorpusId:269648877) | 2026-10-13 | about evaluating generative models on synthetic distributions; no recursive training loop |
| [2404.08555](https://arxiv.org/abs/2404.08555) | 2026-10-13 | critical analysis of RLHF reward models; not model collapse |
| [1909.04499](https://arxiv.org/abs/1909.04499) | 2026-10-13 | language drift under task reward within one fine-tuning run; no recursion over generations |
| [2203.02923](https://arxiv.org/abs/2203.02923) | 2026-10-13 | molecular diffusion model; no recursion over generated data |
| [2505.20313](https://arxiv.org/abs/2505.20313) | 2026-10-13 | neurosymbolic reasoning chapter; not training on generated data |
| [CorpusId:18622530](https://api.semanticscholar.org/CorpusId:18622530) | 2026-10-13 | unsupervised sentiment classification (title only); the topic is recursive training of generative models |
| [2403.03852](https://arxiv.org/abs/2403.03852) | 2026-10-13 | diffusion sampler acceleration theory; unrelated to model collapse |
| [CorpusId:272803517](https://api.semanticscholar.org/CorpusId:272803517) | 2026-10-13 | title is about crowdworker fairness; not recursive training |
| [CorpusId:2397530](https://api.semanticscholar.org/CorpusId:2397530) | 2026-10-13 | title: population genetics of recombination; not about generative models |
| [2604.26653](https://arxiv.org/abs/2604.26653) | 2026-10-13 | platform for generating agent-trace training data; synthetic data used once, no recursion |
| [2407.08583](https://arxiv.org/abs/2407.08583) | 2026-10-13 | survey of data and multimodal LLM co-development; collapse not its subject |
| [2308.03686](https://arxiv.org/abs/2308.03686) | 2026-10-13 | diffusion convergence bounds; no recursive training on generated data |
| [2404.08788](https://arxiv.org/abs/2404.08788) | 2026-10-13 | CLIP detector for AI images; not tested as defence against collapse |
| [CorpusId:145487058](https://api.semanticscholar.org/CorpusId:145487058) | 2026-10-13 | sociology of family patterns; unrelated to generative models |
| [2408.09849](https://arxiv.org/abs/2408.09849) | 2026-10-13 | filtering for LLM self-improvement gains; excluded capability self-training |
| [CorpusId:276399437](https://api.semanticscholar.org/CorpusId:276399437) | 2026-10-13 | AI history and interior design industry; not model collapse |
| [CorpusId:278311895](https://api.semanticscholar.org/CorpusId:278311895) | 2026-10-13 | synthetic question-decomposition data used once; no recursive loop |
| [2102.07698](https://arxiv.org/abs/2102.07698) | 2026-10-13 | performative gradient descent for predictive models; not generative recursive training |
| [2504.13143](https://arxiv.org/abs/2504.13143) | 2026-10-13 | image editing benchmark built with GPT-4o instructions; no recursive training loop |
| [CorpusId:267809175](https://api.semanticscholar.org/CorpusId:267809175) | 2026-10-13 | ethics of synthetic data for data sharing; no recursive training over generations |
| [2212.09660](https://arxiv.org/abs/2212.09660) | 2026-10-13 | code-switching NLP survey; unrelated to model collapse |
| [CorpusId:231194222](https://api.semanticscholar.org/CorpusId:231194222) | 2026-10-13 | biomedical autophagy in pancreatitis (title only); the topic is recursive training of generative models |
| [CorpusId:269516240](https://api.semanticscholar.org/CorpusId:269516240) | 2026-10-13 | typology of synthetic data in social science; not recursive training |
| [CorpusId:262580630](https://api.semanticscholar.org/CorpusId:262580630) | 2026-10-13 | position on risks of large LMs generally; recursion on generated data not its subject |
| [CorpusId:290809333](https://api.semanticscholar.org/CorpusId:290809333) | 2026-10-13 | learner cognitive dependency on generative AI in education; not models trained on generated data |
| [2603.20116](https://arxiv.org/abs/2603.20116) | 2026-10-13 | RL adaptation of surgical vision-language models; not about generated-data training |
| [CorpusId:279508460](https://api.semanticscholar.org/CorpusId:279508460) | 2026-10-13 | private data selection and quantization for LLM fine-tuning; no recursive generated-data training |
| [2508.16204](https://arxiv.org/abs/2508.16204) | 2026-10-13 | evolutionary model merging method; not about recursive training on generated data |
| [CorpusId:286685797](https://api.semanticscholar.org/CorpusId:286685797) | 2026-10-13 | data warehouse root cause analysis; not about model collapse |
| [2412.11385](https://arxiv.org/abs/2412.11385) | 2026-10-13 | sources of LLM lexical overrepresentation; not training on generated data |
| [2302.00560](https://arxiv.org/abs/2302.00560) | 2026-10-13 | opinionated writing assistants shifting users' views; no training on generated data |
| [2311.12793](https://arxiv.org/abs/2311.12793) | 2026-10-13 | synthetic caption dataset used once for training; no recursive loop |
| [2502.17578](https://arxiv.org/abs/2502.17578) | 2026-10-13 | power-law scaling of repeated-sampling success; not about training on generated data |
| [2504.12563](https://arxiv.org/abs/2504.12563) | 2026-10-13 | diverse synthetic data generation for domain adaptation; one-time use, no recursion |
| [2010.12643](https://arxiv.org/abs/2010.12643) | 2026-10-13 | synthetic QA augmentation used once; no recursive retraining |
| [1412.1897](https://arxiv.org/abs/1412.1897) | 2026-10-13 | fooling image classifiers; adversarial examples, not model collapse |
| [CorpusId:278776996](https://api.semanticscholar.org/CorpusId:278776996) | 2026-10-13 | hardware fuzzing with reinforcement learning; not generative recursion |
| [CorpusId:272962036](https://api.semanticscholar.org/CorpusId:272962036) | 2026-10-13 | AI as theoretical tool for cognitive science; not recursive training |
| [CorpusId:1063711](https://api.semanticscholar.org/CorpusId:1063711) | 2026-10-13 | generic statistical model reference (no abstract); title not about recursive training |
| [2509.22872](https://arxiv.org/abs/2509.22872) | 2026-10-13 | AI safety as regulatory avoidance; policy, not recursive training |
| [2405.14061](https://arxiv.org/abs/2405.14061) | 2026-10-13 | observability of LLM latent states; unrelated to recursive training |
| [CorpusId:14651832](https://api.semanticscholar.org/CorpusId:14651832) | 2026-10-13 | statistics of rare events (no abstract); general statistics, not generative recursion |
| [1810.03993](https://arxiv.org/abs/1810.03993) | 2026-10-13 | model documentation framework; not about recursive training on generated data |
| [2602.14286](https://arxiv.org/abs/2602.14286) | 2026-10-13 | statistical watermark detection method; not tested against model collapse |
| [2602.04895](https://arxiv.org/abs/2602.04895) | 2026-10-13 | privacy amplification by synthetic data release; not recursive training |
| [2007.11865](https://arxiv.org/abs/2007.11865) | 2026-10-13 | African language dataset challenge; no recursive training on generated data |
| [CorpusId:147204347](https://api.semanticscholar.org/CorpusId:147204347) | 2026-10-13 | interpreting in conversation; not about generative models |
| [CorpusId:156269421](https://api.semanticscholar.org/CorpusId:156269421) | 2026-10-13 | philosophy of reference; not about generative models |
| [CorpusId:286312989](https://api.semanticscholar.org/CorpusId:286312989) | 2026-10-13 | diffusion augmentation for EEG classification; synthetic data used once, no recursive loop |
| [CorpusId:10619940](https://api.semanticscholar.org/CorpusId:10619940) | 2026-10-13 | biomedical autophagy in osteoarthritis (title only); the topic is recursive training of generative models |
| [CorpusId:17869271](https://api.semanticscholar.org/CorpusId:17869271) | 2026-10-13 | SVM classifiers with PCNNs (title only); the topic is recursive training of generative models |
| [2306.15546](https://arxiv.org/abs/2306.15546) | 2026-10-13 | foundation models and federated learning overview; not about recursive training on generated data |
| [2108.07258](https://arxiv.org/abs/2108.07258) | 2026-10-13 | broad foundation-model report; not focused on recursive training on generated data |
| [CorpusId:4799072](https://api.semanticscholar.org/CorpusId:4799072) | 2026-10-13 | cellular autophagy in T cell memory; not model autophagy of generative models |
| [CorpusId:268531336](https://api.semanticscholar.org/CorpusId:268531336) | 2026-10-13 | about malware detection in npm with LLMs; unrelated to recursive training |
| [CorpusId:7436244](https://api.semanticscholar.org/CorpusId:7436244) | 2026-10-13 | semi-supervised POS tagging (title only); self-training for task gains, not generational degradation |
| [2406.10710](https://arxiv.org/abs/2406.10710) | 2026-10-13 | synthetic data used once for Text2Cypher fine-tuning; no recursive loop |
| [2312.10057](https://arxiv.org/abs/2312.10057) | 2026-10-13 | bias from generative AI in writing research papers; not about model training on generated data |
| [CorpusId:124328950](https://api.semanticscholar.org/CorpusId:124328950) | 2026-10-13 | Markov diffusion operator mathematics, from title; unrelated to model collapse |
| [CorpusId:268585539](https://api.semanticscholar.org/CorpusId:268585539) | 2026-10-13 | title is about AI trajectories for managers; not recursive training |
| [2603.18361](https://arxiv.org/abs/2603.18361) | 2026-10-13 | synthetic commonsense data generation used once for diversity; no recursion |
| [2303.09556](https://arxiv.org/abs/2303.09556) | 2026-10-13 | diffusion training loss weighting; unrelated to model collapse |
| [CorpusId:290752396](https://api.semanticscholar.org/CorpusId:290752396) | 2026-10-13 | book on Locke's theory of perception; unrelated to recursive training |
| [2311.02294](https://arxiv.org/abs/2311.02294) | 2026-10-13 | philosophy of meaning in LLMs; not about training on generated data |
| [2605.13807](https://arxiv.org/abs/2605.13807) | 2026-10-13 | recurrent neural quantum states for Monte Carlo; the topic is recursive training of generative models |
| [2311.05304](https://arxiv.org/abs/2311.05304) | 2026-10-13 | data valuation in federated learning; not about recursive training on generated data |
| [2308.08638](https://arxiv.org/abs/2308.08638) | 2026-10-13 | GAN debiasing by training once on rebalanced generated data; no recursive loop over generations |
| [CorpusId:276520314](https://api.semanticscholar.org/CorpusId:276520314) | 2026-10-13 | dataset for AI-versus-human text detection; excluded detection not tested against collapse |
| [1206.6389](https://arxiv.org/abs/1206.6389) | 2026-10-13 | poisoning attacks on SVMs; adversarial, not recursive generative training |
| [CorpusId:41282673](https://api.semanticscholar.org/CorpusId:41282673) | 2026-10-13 | quantum optics collapse and revival; unrelated to generative models |
| [2403.13257](https://arxiv.org/abs/2403.13257) | 2026-10-13 | toolkit for merging LLM checkpoints; not about recursive training on generated data |
| [2603.14372](https://arxiv.org/abs/2603.14372) | 2026-10-13 | game-theoretic incentives for content creators with LLM spillovers; not about training on generated data |
| [CorpusId:280959733](https://api.semanticscholar.org/CorpusId:280959733) | 2026-10-13 | review of ophthalmology AI agents; unrelated to model collapse |
| [CorpusId:39200055](https://api.semanticscholar.org/CorpusId:39200055) | 2026-10-13 | cellular autophagy in dendrimer hepatotoxicity; not model autophagy of generative models |
| [CorpusId:6107490](https://api.semanticscholar.org/CorpusId:6107490) | 2026-10-13 | submodular maximization survey, from title; unrelated to model collapse |
| [2311.09402](https://arxiv.org/abs/2311.09402) | 2026-10-13 | diffusion-generated chest X-rays used once to supplement training; no recursive loop |
| [2504.15432](https://arxiv.org/abs/2504.15432) | 2026-10-13 | single-step training of classifiers on LLM labels; synthetic data used once, no recursive loop |
| [CorpusId:47161883](https://api.semanticscholar.org/CorpusId:47161883) | 2026-10-13 | cellular autophagy in cardiac injury; not model autophagy of generative models |
| [CorpusId:120070817](https://api.semanticscholar.org/CorpusId:120070817) | 2026-10-13 | cosmological structure formation; unrelated to generative models |
| [2403.08763](https://arxiv.org/abs/2403.08763) | 2026-10-13 | continual pretraining with replay under distribution shift; data is not model-generated |
| [CorpusId:268329310](https://api.semanticscholar.org/CorpusId:268329310) | 2026-10-13 | Marxist theory of AI and knowledge; not recursive training |
| [CorpusId:291424904](https://api.semanticscholar.org/CorpusId:291424904) | 2026-10-13 | theory of knowledge storage in LLMs; not about recursive training on generated data |
| [1904.07734](https://arxiv.org/abs/1904.07734) | 2026-10-13 | continual learning evaluation scenarios; catastrophic forgetting, not recursive generated data |
| [2407.02446](https://arxiv.org/abs/2407.02446) | 2026-10-13 | RLHF trade-off with next-token prediction; no recursion over generations |
| [2309.08589](https://arxiv.org/abs/2309.08589) | 2026-10-13 | self-education via chain-of-thought for skill gains; excluded self-training-for-capability theme |
| [CorpusId:285115161](https://api.semanticscholar.org/CorpusId:285115161) | 2026-10-13 | LLM-generated text detector; not tested against collapse or as data filtering |
| [2502.01612](https://arxiv.org/abs/2502.01612) | 2026-10-13 | self-improvement for length generalization gains; excluded self-training for capability |
| [CorpusId:225140128](https://api.semanticscholar.org/CorpusId:225140128) | 2026-10-13 | tunnel excavation collapse model test; unrelated to generative models |
| [2409.00764](https://arxiv.org/abs/2409.00764) | 2026-10-13 | position on AI and software engineering; not model collapse |
| [2410.02707](https://arxiv.org/abs/2410.02707) | 2026-10-13 | hallucination representations inside LLMs; not recursive training |
| [1912.00844](https://arxiv.org/abs/1912.00844) | 2026-10-13 | solar elemental abundances in astronomy; unrelated to generative models |
| [CorpusId:84301227](https://api.semanticscholar.org/CorpusId:84301227) | 2026-10-13 | title: genetics of sex; biology, not generative models |
| [2303.08774](https://arxiv.org/abs/2303.08774) | 2026-10-13 | GPT-4 technical report; not about model collapse |
| [2602.06610](https://arxiv.org/abs/2602.06610) | 2026-10-13 | energy-aware surrogate-assisted metaheuristics; the topic is recursive training of generative models |
| [2606.11583](https://arxiv.org/abs/2606.11583) | 2026-10-13 | LLM-GNN co-teaching for few-shot graph learning; not recursive generative training |
| [CorpusId:271827670](https://api.semanticscholar.org/CorpusId:271827670) | 2026-10-13 | medical AI for gastric lesion detection; unrelated to model collapse |
| [2212.08073](https://arxiv.org/abs/2212.08073) | 2026-10-13 | self-improvement for harmlessness, a capability gain, not degradation over generations |
| [1512.03385](https://arxiv.org/abs/1512.03385) | 2026-10-13 | residual networks for image recognition; unrelated to recursive training on generated data |
| [CorpusId:263742917](https://api.semanticscholar.org/CorpusId:263742917) | 2026-10-13 | blockchain for medical data collection; unrelated to model collapse |
| [2604.06268](https://arxiv.org/abs/2604.06268) | 2026-10-13 | template collapse within one RL training run; no recursion over generations |
| [2308.14840](https://arxiv.org/abs/2308.14840) | 2026-10-13 | security risks of generative AI workshop report; not about recursive training |
| [1805.06370](https://arxiv.org/abs/1805.06370) | 2026-10-13 | continual learning framework; not about recursive training on generated data |
| [2307.15217](https://arxiv.org/abs/2307.15217) | 2026-10-13 | survey of RLHF limitations; not about recursive training |
| [1805.11233](https://arxiv.org/abs/1805.11233) | 2026-10-13 | iterative weight quantization for compression; the topic is recursive training of generative models |
| [2607.11997](https://arxiv.org/abs/2607.11997) | 2026-10-13 | model merging and expert training duration; not about recursive training on generated data |
| [CorpusId:263775936](https://api.semanticscholar.org/CorpusId:263775936) | 2026-10-13 | clinical predictive models altering their own retraining data; predictive not generative, data not model-generated |
| [2603.22213](https://arxiv.org/abs/2603.22213) | 2026-10-13 | synthetic data for knowledge injection used once; no recursive training loop |
| [CorpusId:272724558](https://api.semanticscholar.org/CorpusId:272724558) | 2026-10-13 | title is a captioned dataset of generated images; no recursive training |
| [CorpusId:244758187](https://api.semanticscholar.org/CorpusId:244758187) | 2026-10-13 | ARIMA load forecasting noise robustness; unrelated to generative model retraining |
| [2509.02072](https://arxiv.org/abs/2509.02072) | 2026-10-13 | one-time LLM data augmentation for accident report classification; no recursion |
| [2402.19173](https://arxiv.org/abs/2402.19173) | 2026-10-13 | code model and dataset report; not about model collapse |
| [CorpusId:233325478](https://api.semanticscholar.org/CorpusId:233325478) | 2026-10-13 | cancer cell macropinocytosis biology; the topic is recursive training of generative models |
| [2310.01973](https://arxiv.org/abs/2310.01973) | 2026-10-13 | federated Wasserstein distance computation; not about model collapse |
| [CorpusId:291935241](https://api.semanticscholar.org/CorpusId:291935241) | 2026-10-13 | synthetic persona corpus used once for fine-tuning; no recursive loop |
| [CorpusId:288704874](https://api.semanticscholar.org/CorpusId:288704874) | 2026-10-13 | discourse-level text watermarking for attribution; not tested against model collapse |
| [CorpusId:206800425](https://api.semanticscholar.org/CorpusId:206800425) | 2026-10-13 | submodular maximization approximations, from title; unrelated to model collapse |
| [2302.13007](https://arxiv.org/abs/2302.13007) | 2026-10-13 | ChatGPT text augmentation used once; no recursive retraining loop |
| [2402.15943](https://arxiv.org/abs/2402.15943) | 2026-10-13 | software-engineering challenges of building on foundation models; the topic is recursive training on generated data |
| [2210.02747](https://arxiv.org/abs/2210.02747) | 2026-10-13 | flow matching generative modeling; no recursive training |
| [2405.17767](https://arxiv.org/abs/2405.17767) | 2026-10-13 | neural collapse in language models; excluded topic |
| [2402.09656](https://arxiv.org/abs/2402.09656) | 2026-10-13 | LLM collapse from model editing; degradation from edits, not training on generated data |
| [2406.01574](https://arxiv.org/abs/2406.01574) | 2026-10-13 | language understanding benchmark; not about model collapse |
| [CorpusId:274510208](https://api.semanticscholar.org/CorpusId:274510208) | 2026-10-13 | title is about trust and embodiment in generative AI; not recursive training |
| [2410.04760](https://arxiv.org/abs/2410.04760) | 2026-10-13 | diffusion sampler acceleration; unrelated to model collapse |
| [2402.09668](https://arxiv.org/abs/2402.09668) | 2026-10-13 | data selection for efficient pretraining; not about training on generated data across generations |
| [2311.16302](https://arxiv.org/abs/2311.16302) | 2026-10-13 | benchmarking data-selection scores on weakly labelled data; not about generated data loops |
| [2211.08411](https://arxiv.org/abs/2211.08411) | 2026-10-13 | long-tail knowledge vs pretraining document counts; data is not model-generated |
| [1803.05457](https://arxiv.org/abs/1803.05457) | 2026-10-13 | science QA benchmark; not about training on generated data |
| [2308.12240](https://arxiv.org/abs/2308.12240) | 2026-10-13 | KL convergence of diffusion models; single model, not collapse |
| [CorpusId:258665195](https://api.semanticscholar.org/CorpusId:258665195) | 2026-10-13 | acoustic indoor localization signal identification; the topic is recursive training of generative models |
| [2407.01344](https://arxiv.org/abs/2407.01344) | 2026-10-13 | robust performative stochastic optimisation; not generative models trained on generated data |
| [2305.03610](https://arxiv.org/abs/2305.03610) | 2026-10-13 | data curation for image captioning with one-off generated replacements; no recursive loop |
| [CorpusId:276614536](https://api.semanticscholar.org/CorpusId:276614536) | 2026-10-13 | review of medical imaging foundation models; not recursive training |
| [CorpusId:23035729](https://api.semanticscholar.org/CorpusId:23035729) | 2026-10-13 | cell-biology autophagy (title only); the topic is recursive training of generative models |
| [2211.01095](https://arxiv.org/abs/2211.01095) | 2026-10-13 | fast diffusion sampler; unrelated to model collapse |
| [CorpusId:269305916](https://api.semanticscholar.org/CorpusId:269305916) | 2026-10-13 | about data governance policy for generative AI, not training on generated data (judged from title; no abstract or tldr) |
| [CorpusId:10798313](https://api.semanticscholar.org/CorpusId:10798313) | 2026-10-13 | title: recombination and mutation genetics; not about generative models |
| [CorpusId:784813](https://api.semanticscholar.org/CorpusId:784813) | 2026-10-13 | SVM pruning methods (title only); the topic is recursive training of generative models |
| [CorpusId:198324334](https://api.semanticscholar.org/CorpusId:198324334) | 2026-10-13 | differentially private optimal transport for domain adaptation; unrelated to collapse |
| [2502.04390](https://arxiv.org/abs/2502.04390) | 2026-10-13 | knowledge updates with contradictory facts; not about training on generated data |
| [2406.01757](https://arxiv.org/abs/2406.01757) | 2026-10-13 | position on foundation-model disparities; not about training on generated data |
| [CorpusId:263621147](https://api.semanticscholar.org/CorpusId:263621147) | 2026-10-13 | review of LLMs in radiology; not about training on generated data |
| [2403.12196](https://arxiv.org/abs/2403.12196) | 2026-10-13 | LLM malware detection for npm; unrelated to model collapse |
| [2105.15004](https://arxiv.org/abs/2105.15004) | 2026-10-13 | kernel regression error rates; generic theory tool, not model collapse |
| [2506.14126](https://arxiv.org/abs/2506.14126) | 2026-10-13 | overtraining experts harms model merging; not about recursive training on generated data |
| [2510.13537](https://arxiv.org/abs/2510.13537) | 2026-10-13 | continual merging of LoRA adapters on device; not about training on generated data |
| [CorpusId:5490143](https://api.semanticscholar.org/CorpusId:5490143) | 2026-10-13 | psycholinguistic parsing model; not about recursive training |
| [CorpusId:277494969](https://api.semanticscholar.org/CorpusId:277494969) | 2026-10-13 | commentary on LLMs and literacy education; not model collapse |
| [2608.01522](https://arxiv.org/abs/2608.01522) | 2026-10-13 | self-evolving curriculum for math reinforcement fine-tuning gains; excluded self-training theme |
| [2208.05314](https://arxiv.org/abs/2208.05314) | 2026-10-13 | diffusion convergence under manifold hypothesis; single model, not collapse |
| [CorpusId:18268744](https://api.semanticscholar.org/CorpusId:18268744) | 2026-10-13 | CIFAR image dataset report; not about generated data |
| [1708.06733](https://arxiv.org/abs/1708.06733) | 2026-10-13 | backdoored networks in supply chain; security, not model collapse |
| [2407.09502](https://arxiv.org/abs/2407.09502) | 2026-10-13 | synergies between artificial life and LLMs; not about training on generated data |
| [2005.14165](https://arxiv.org/abs/2005.14165) | 2026-10-13 | GPT-3 model report; main finding is few-shot scaling, not collapse |
| [2501.00274](https://arxiv.org/abs/2501.00274) | 2026-10-13 | LLM text evaluation rubric; unrelated to model collapse |
| [2505.00022](https://arxiv.org/abs/2505.00022) | 2026-10-13 | German pretraining dataset with one-shot synthetic data; excluded synthetic-data-used-once theme |
| [2311.11388](https://arxiv.org/abs/2311.11388) | 2026-10-13 | perspective on machine-mediated cultural evolution; recursive model training at most in passing |
| [2210.00266](https://arxiv.org/abs/2210.00266) | 2026-10-13 | long-tailed class-incremental learning; not about training on generated data |
| [2605.19483](https://arxiv.org/abs/2605.19483) | 2026-10-13 | explains memorization within one SGD training run; builds on collapse theory but studies no recursive training on generated data |
| [CorpusId:273263196](https://api.semanticscholar.org/CorpusId:273263196) | 2026-10-13 | overview of trustworthy AI topics; not model collapse |
| [CorpusId:160025533](https://api.semanticscholar.org/CorpusId:160025533) | 2026-10-13 | GPT-2 model paper (no abstract); not about model collapse |
| [2311.12022](https://arxiv.org/abs/2311.12022) | 2026-10-13 | question-answering benchmark; not about recursive training on generated data |
| [2309.05196](https://arxiv.org/abs/2309.05196) | 2026-10-13 | human co-writing diversity study; no model trained on generated data |
| [2407.09241](https://arxiv.org/abs/2407.09241) | 2026-10-13 | sociolinguistic perspective on language modeling; not recursive training |
| [2006.11239](https://arxiv.org/abs/2006.11239) | 2026-10-13 | introduces diffusion models; not about recursive training on generated data |
| [CorpusId:267514952](https://api.semanticscholar.org/CorpusId:267514952) | 2026-10-13 | panel on computing paradigms for LLMs; not about recursive training |
| [2607.24717](https://arxiv.org/abs/2607.24717) | 2026-10-13 | per-example pretraining data curation; not a defence against recursive degradation |
| [2303.13221](https://arxiv.org/abs/2303.13221) | 2026-10-13 | synthetic images used once for few-shot detection; excluded one-shot synthetic data use |
| [CorpusId:62824717](https://api.semanticscholar.org/CorpusId:62824717) | 2026-10-13 | gradient flows in probability space, from title; general mathematics, not collapse |
| [CorpusId:19763068](https://api.semanticscholar.org/CorpusId:19763068) | 2026-10-13 | Fisher and Shannon information inequalities, from title; unrelated to collapse |
| [2601.01966](https://arxiv.org/abs/2601.01966) | 2026-10-13 | provenance audit of LLM-refined training prompts for governance; not tested against collapse |
| [2410.07672](https://arxiv.org/abs/2410.07672) | 2026-10-13 | weak-to-strong alignment via multi-agent preference optimization; not recursive degradation |
| [CorpusId:122547084](https://api.semanticscholar.org/CorpusId:122547084) | 2026-10-13 | classical distribution theory of quadratic forms (no abstract); not model collapse |
| [2208.08227](https://arxiv.org/abs/2208.08227) | 2026-10-13 | multilingual code benchmark; not about model collapse |
| [CorpusId:52255687](https://api.semanticscholar.org/CorpusId:52255687) | 2026-10-13 | NLP dataset documentation practice; not about training on generated data |
| [2006.09011](https://arxiv.org/abs/2006.09011) | 2026-10-13 | training techniques for score models; unrelated to model collapse |
| [2305.09235](https://arxiv.org/abs/2305.09235) | 2026-10-13 | downstream errors from one-off synthetic data use; no recursive generations |
| [CorpusId:62722358](https://api.semanticscholar.org/CorpusId:62722358) | 2026-10-13 | 1978 problem-solving book per Asta metadata; predates generative-model recursion |
| [CorpusId:275588103](https://api.semanticscholar.org/CorpusId:275588103) | 2026-10-13 | DPO on curated data to reduce sycophancy; not recursive training |
| [CorpusId:287040877](https://api.semanticscholar.org/CorpusId:287040877) | 2026-10-13 | autoethnography of generative AI art; not about models trained on generated data |
| [CorpusId:229292566](https://api.semanticscholar.org/CorpusId:229292566) | 2026-10-13 | second-language collocation testing; the topic is recursive training of generative models |
| [2010.02502](https://arxiv.org/abs/2010.02502) | 2026-10-13 | diffusion sampling method; a model the topic studies used, not collapse itself |
| [2301.01928](https://arxiv.org/abs/2301.01928) | 2026-10-13 | self-supervised pretraining on event camera data; no recursive generative training |
| [1906.02659](https://arxiv.org/abs/1906.02659) | 2026-10-13 | object recognition geographic bias; unrelated to model collapse |
| [2302.06590](https://arxiv.org/abs/2302.06590) | 2026-10-13 | developer productivity experiment with Copilot; not about model collapse |
| [CorpusId:250360850](https://api.semanticscholar.org/CorpusId:250360850) | 2026-10-13 | fairness and strategic manipulation in classification, by its title; not generative recursive training |
| [CorpusId:189824904](https://api.semanticscholar.org/CorpusId:189824904) | 2026-10-13 | hyperdimensional computing hardware; the topic is recursive training of generative models |
| [2404.01712](https://arxiv.org/abs/2404.01712) | 2026-10-13 | certified machine unlearning; not about recursive training |
| [CorpusId:12243515](https://api.semanticscholar.org/CorpusId:12243515) | 2026-10-13 | stochastic calculus textbook, from title; unrelated to model collapse |
| [2510.10681](https://arxiv.org/abs/2510.10681) | 2026-10-13 | rephrasing web data for pretraining once; no recursive loop |
| [2501.18962](https://arxiv.org/abs/2501.18962) | 2026-10-13 | budget allocation for verifier-filtered iterative bootstrapping to maximize gains; excluded self-training for capability |
| [1812.06224](https://arxiv.org/abs/1812.06224) | 2026-10-13 | CNN architecture compression via PCA; the topic is recursive training of generative models |
| [2609.31688](https://arxiv.org/abs/2609.31688) | 2026-10-13 | post-training for output diversity; no recursive training over generations |
| [2010.11300](https://arxiv.org/abs/2010.11300) | 2026-10-13 | long-term effect of fairness constraints on qualification; not generative recursive training |
| [2412.16468](https://arxiv.org/abs/2412.16468) | 2026-10-13 | survey of superalignment; not model collapse |
| [2408.07666](https://arxiv.org/abs/2408.07666) | 2026-10-13 | survey of model merging methods; not about recursive training on generated data |
| [CorpusId:14276605](https://api.semanticscholar.org/CorpusId:14276605) | 2026-10-13 | title: modifier gene evolution theory; biology, not generative models |
| [2512.13316](https://arxiv.org/abs/2512.13316) | 2026-10-13 | federated learning with synthetic samples; no recursive generations |
| [2407.12999](https://arxiv.org/abs/2407.12999) | 2026-10-13 | GenAI policy workshop report; not about recursive training |
| [CorpusId:272927932](https://api.semanticscholar.org/CorpusId:272927932) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [CorpusId:5935426](https://api.semanticscholar.org/CorpusId:5935426) | 2026-10-13 | image label collection (title only); the topic is recursive training of generative models |
| [CorpusId:270863179](https://api.semanticscholar.org/CorpusId:270863179) | 2026-10-13 | histopathology image synthesis method; no recursive training loop |
| [2605.16245](https://arxiv.org/abs/2605.16245) | 2026-10-13 | AI-mediated communication shifting human opinion; no model training on generated data |
| [1704.00028](https://arxiv.org/abs/1704.00028) | 2026-10-13 | WGAN gradient penalty, one training run; no recursion |
| [2607.20446](https://arxiv.org/abs/2607.20446) | 2026-10-13 | LLM detection of AI-written student work; not tested as defence against collapse or as training-data filtering |
| [CorpusId:284415493](https://api.semanticscholar.org/CorpusId:284415493) | 2026-10-13 | philosophy of learning with generative AI; not about model collapse |
| [CorpusId:2153364](https://api.semanticscholar.org/CorpusId:2153364) | 2026-10-13 | optimal transport tutorial; unrelated to recursive generative training |
| [2205.12393](https://arxiv.org/abs/2205.12393) | 2026-10-13 | continual instruction tuning of LMs; not about recursive training on generated data |
| [1908.09203](https://arxiv.org/abs/1908.09203) | 2026-10-13 | GPT-2 release policy report; not about model collapse |
| [2605.26711](https://arxiv.org/abs/2605.26711) | 2026-10-13 | theory of mixture identifiability and grounding in sequence models; not recursive training |
| [CorpusId:763574](https://api.semanticscholar.org/CorpusId:763574) | 2026-10-13 | cellular autophagy in tumor fibroblasts; not model autophagy of generative models |
| [2603.16900](https://arxiv.org/abs/2603.16900) | 2026-10-13 | research agenda for human-AI social dynamics; not about model collapse |
| [2011.13456](https://arxiv.org/abs/2011.13456) | 2026-10-13 | score-based SDE generative modeling; a model studied, not collapse itself |
| [2308.08998](https://arxiv.org/abs/2308.08998) | 2026-10-13 | self-training on own samples for alignment gains; excluded capability self-improvement |
| [2505.23121](https://arxiv.org/abs/2505.23121) | 2026-10-13 | multi-turn multimodal context modelling; not training on generated data |
| [2304.10819](https://arxiv.org/abs/2304.10819) | 2026-10-13 | auditing synthetic datasets for bias and privacy; no recursive training |
| [2507.21053](https://arxiv.org/abs/2507.21053) | 2026-10-13 | flow-matching policy gradient RL algorithm; not recursive generative training |
| [1509.01626](https://arxiv.org/abs/1509.01626) | 2026-10-13 | character-level CNNs for text classification; unrelated to recursive training |
| [2408.10666](https://arxiv.org/abs/2408.10666) | 2026-10-13 | poisoning attacks on recommender systems; the topic is recursive training of generative models |
| [2406.20094](https://arxiv.org/abs/2406.20094) | 2026-10-13 | persona-driven synthetic data creation, used once; no recursion studied |
| [2603.09463](https://arxiv.org/abs/2603.09463) | 2026-10-13 | merging collapse of task-specialist models; different collapse, no training on generated data |
| [CorpusId:8592977](https://api.semanticscholar.org/CorpusId:8592977) | 2026-10-13 | Wasserstein barycenter mathematics, from title; unrelated to model collapse |
| [2403.06098](https://arxiv.org/abs/2403.06098) | 2026-10-13 | text-to-video prompt dataset; no recursive training studied |
| [2510.22107](https://arxiv.org/abs/2510.22107) | 2026-10-13 | diverse conditional image generation method; no recursive training |
| [2602.16201](https://arxiv.org/abs/2602.16201) | 2026-10-13 | survey of long-tail knowledge failures in LLMs; not about recursive training on generated data |
| [CorpusId:268290394](https://api.semanticscholar.org/CorpusId:268290394) | 2026-10-13 | about poisoning attacks on text-to-image models; not recursive training |
| [2211.08403](https://arxiv.org/abs/2211.08403) | 2026-10-13 | variance collapse in weight interpolation; different collapse, no generated data |
| [CorpusId:282900844](https://api.semanticscholar.org/CorpusId:282900844) | 2026-10-13 | human-centric counselling dialogue dataset; dataset report, not about recursive training |
| [2306.01708](https://arxiv.org/abs/2306.01708) | 2026-10-13 | weight-merging interference method; not about recursive training on generated data |
| [2405.01470](https://arxiv.org/abs/2405.01470) | 2026-10-13 | dataset of chatbot interaction logs; not about recursive training degradation |
| [CorpusId:283611328](https://api.semanticscholar.org/CorpusId:283611328) | 2026-10-13 | market competition in generative AI; not about model collapse |
| [2310.05792](https://arxiv.org/abs/2310.05792) | 2026-10-13 | derivative-free optimisation for performative prediction; not generative recursive training |
| [CorpusId:221115870](https://api.semanticscholar.org/CorpusId:221115870) | 2026-10-13 | GAN review for computer vision; GAN mode collapse, an excluded theme |
| [2310.13828](https://arxiv.org/abs/2310.13828) | 2026-10-13 | prompt-specific data poisoning of text-to-image models; adversarial, not recursive generated data |
| [2510.06108](https://arxiv.org/abs/2510.06108) | 2026-10-13 | data selection for reasoning fine-tuning; no generated-data recursion |
| [2410.18851](https://arxiv.org/abs/2410.18851) | 2026-10-13 | essay on generative AI homogenising human intention in programming; no model retraining loop |
| [CorpusId:278803459](https://api.semanticscholar.org/CorpusId:278803459) | 2026-10-13 | editorial on IS research methods and GenAI; not model collapse |
| [1906.04043](https://arxiv.org/abs/1906.04043) | 2026-10-13 | human-aided generated-text detection tool; excluded detection theme, no training-data filtering |
| [2604.09022](https://arxiv.org/abs/2604.09022) | 2026-10-13 | renders 3D-scene image dataset; cites model autophagy only as motivation, tests no recursive loop |
| [CorpusId:208704414](https://api.semanticscholar.org/CorpusId:208704414) | 2026-10-13 | protein folding summary; unrelated to generative models |
| [CorpusId:285552937](https://api.semanticscholar.org/CorpusId:285552937) | 2026-10-13 | zero-knowledge private ML inference; not about model collapse |
| [2311.11003](https://arxiv.org/abs/2311.11003) | 2026-10-13 | score-model convergence guarantees; no recursion over generations |
| [2402.13446](https://arxiv.org/abs/2402.13446) | 2026-10-13 | survey of LLM data annotation and synthesis; no recursive training |
| [CorpusId:14459742](https://api.semanticscholar.org/CorpusId:14459742) | 2026-10-13 | nonlinear programming textbook, from title; unrelated to model collapse |
| [CorpusId:14674248](https://api.semanticscholar.org/CorpusId:14674248) | 2026-10-13 | word-embedding document distance, from title; unrelated to recursive generative training |
| [2509.16551](https://arxiv.org/abs/2509.16551) | 2026-10-13 | pretraining on LLM-simplified text once; synthetic data with no recursive loop |
| [CorpusId:283565604](https://api.semanticscholar.org/CorpusId:283565604) | 2026-10-13 | graph attention for cognitive diagnosis; unrelated to generated-data training |
| [2302.00482](https://arxiv.org/abs/2302.00482) | 2026-10-13 | flow matching method; no generated-data recursion |
| [2305.16960](https://arxiv.org/abs/2305.16960) | 2026-10-13 | alignment via simulated social interactions for capability; no degradation over generations |
| [2512.10435](https://arxiv.org/abs/2512.10435) | 2026-10-13 | detecting paraphrased plagiarism in science; not about model collapse |
| [2402.10379](https://arxiv.org/abs/2402.10379) | 2026-10-13 | software library for synthetic data workflows; not about recursive training or degradation |
| [2502.04849](https://arxiv.org/abs/2502.04849) | 2026-10-13 | diffusion sampler convergence analysis; no recursion over generations |
| [CorpusId:272778340](https://api.semanticscholar.org/CorpusId:272778340) | 2026-10-13 | policy obligations for AI content detection; not tested as defence against collapse |
| [1906.07337](https://arxiv.org/abs/1906.07337) | 2026-10-13 | bias measurement in BERT; not about recursive training |
| [2304.03442](https://arxiv.org/abs/2304.03442) | 2026-10-13 | LLM agents simulating human behaviour; not about training on generated data |
| [2405.18432](https://arxiv.org/abs/2405.18432) | 2026-10-13 | recovering fine-tuning model trees; not about training on generated data |
| [CorpusId:274033467](https://api.semanticscholar.org/CorpusId:274033467) | 2026-10-13 | legal and economic data circulation in China; unrelated to training on generated data |
| [CorpusId:86616140](https://api.semanticscholar.org/CorpusId:86616140) | 2026-10-13 | adversarial evasion hardening of classifiers (title only); the topic is recursive training of generative models |
| [CorpusId:280666861](https://api.semanticscholar.org/CorpusId:280666861) | 2026-10-13 | federated learning data engineering pipelines; title gives no generated-data recursion |
| [2406.08464](https://arxiv.org/abs/2406.08464) | 2026-10-13 | alignment data synthesis used once; no recursive retraining |
| [2408.14960](https://arxiv.org/abs/2408.14960) | 2026-10-13 | routes synthetic data through multiple teachers once; cites collapse only as motivation |
| [2406.14532](https://arxiv.org/abs/2406.14532) | 2026-10-13 | self-generated math data for reasoning gains; excluded self-training theme, not degradation over generations |
| [CorpusId:268784030](https://api.semanticscholar.org/CorpusId:268784030) | 2026-10-13 | AI in breast imaging review; unrelated to model collapse |
| [2509.26442](https://arxiv.org/abs/2509.26442) | 2026-10-13 | stochastic approximation convergence for RL; not about generative recursion |
| [2101.09258](https://arxiv.org/abs/2101.09258) | 2026-10-13 | maximum-likelihood diffusion training; unrelated to model collapse |
| [CorpusId:268042493](https://api.semanticscholar.org/CorpusId:268042493) | 2026-10-13 | Nash equilibria in decision-dependent games; not generative models trained on generated data |
| [2410.18639](https://arxiv.org/abs/2410.18639) | 2026-10-13 | training data attribution in diffusion; no recursive training |
| [CorpusId:261398391](https://api.semanticscholar.org/CorpusId:261398391) | 2026-10-13 | evaluating AI text detectors for academic integrity; not collapse defence |
| [2402.11176](https://arxiv.org/abs/2402.11176) | 2026-10-13 | knowledge-aware fine-tuning method; not about training on generated data |
| [2305.01210](https://arxiv.org/abs/2305.01210) | 2026-10-13 | code generation evaluation framework; not about model collapse |
| [CorpusId:284847457](https://api.semanticscholar.org/CorpusId:284847457) | 2026-10-13 | position on synthetic health data for digital twins; no recursive training loop |
| [CorpusId:273901618](https://api.semanticscholar.org/CorpusId:273901618) | 2026-10-13 | single-step distillation: inheritance of properties from synthetic data, no recursive generations |
| [2302.07194](https://arxiv.org/abs/2302.07194) | 2026-10-13 | diffusion score estimation on low-dimensional data; no recursion over generations |
| [2009.10297](https://arxiv.org/abs/2009.10297) | 2026-10-13 | code synthesis evaluation metric; not about model collapse |
| [2407.18421](https://arxiv.org/abs/2407.18421) | 2026-10-13 | releases a synthetic dialogue dataset used once; no recursive loop |
| [CorpusId:292566742](https://api.semanticscholar.org/CorpusId:292566742) | 2026-10-13 | synthetic augmentation for few-shot text classification; synthetic data used once, an excluded theme |
| [2601.06373](https://arxiv.org/abs/2601.06373) | 2026-10-13 | dementia patient simulation agent; not about training on generated data |
| [2010.10013](https://arxiv.org/abs/2010.10013) | 2026-10-13 | GAN training algorithm within one run; no recursion over generations |
| [2309.13192](https://arxiv.org/abs/2309.13192) | 2026-10-13 | efficient fine-tuning for energy; no recursive generative training |
| [1301.3781](https://arxiv.org/abs/1301.3781) | 2026-10-13 | word2vec word representations; unrelated to model collapse |
| [2002.08155](https://arxiv.org/abs/2002.08155) | 2026-10-13 | pretrained code representation model; not about model collapse |
| [CorpusId:280040441](https://api.semanticscholar.org/CorpusId:280040441) | 2026-10-13 | federated fine-tuning energy study; not model collapse |
| [CorpusId:276783897](https://api.semanticscholar.org/CorpusId:276783897) | 2026-10-13 | self-training for reasoning gains via offline RL; question is the gain, excluded theme |
| [2406.16756](https://arxiv.org/abs/2406.16756) | 2026-10-13 | fairness in performative prediction for predictive models; not generative recursive training |
| [2310.05130](https://arxiv.org/abs/2310.05130) | 2026-10-13 | zero-shot machine-text detector not tested as collapse defence; excluded detection theme |
| [2606.05408](https://arxiv.org/abs/2606.05408) | 2026-10-13 | convergence of inference-time LLM program mutation chains; no model training on generated data |
| [CorpusId:124181096](https://api.semanticscholar.org/CorpusId:124181096) | 2026-10-13 | optimal transport textbook, from title; unrelated to model collapse |
| [2509.14786](https://arxiv.org/abs/2509.14786) | 2026-10-13 | data-constrained pretraining recipes; no recursive training on generated data |
| [2406.15481](https://arxiv.org/abs/2406.15481) | 2026-10-13 | code-switching red-teaming for safety; not model collapse |
| [2310.05442](https://arxiv.org/abs/2310.05442) | 2026-10-13 | rethinking NLP task evaluation; not about recursive training on generated data |
| [CorpusId:205262313](https://api.semanticscholar.org/CorpusId:205262313) | 2026-10-13 | human perceptual categorization experiments; the topic is recursive training of generative models |
| [2203.05482](https://arxiv.org/abs/2203.05482) | 2026-10-13 | averaging fine-tuned weights; not about recursive training on generated data |
| [2301.11305](https://arxiv.org/abs/2301.11305) | 2026-10-13 | generated-text detection method not tested as a defence against recursive degradation |
| [2406.01860](https://arxiv.org/abs/2406.01860) | 2026-10-13 | iterated in-context learning to elicit priors; no retraining on generated data |
| [CorpusId:37645299](https://api.semanticscholar.org/CorpusId:37645299) | 2026-10-13 | 2003 Health Service Journal article per Asta metadata; predates generative-model recursion, likely a misresolved citation |
| [2406.14517](https://arxiv.org/abs/2406.14517) | 2026-10-13 | LLM watermarking for detection; not tested as defence against collapse |
| [1703.04730](https://arxiv.org/abs/1703.04730) | 2026-10-13 | influence functions for interpretability; unrelated to model collapse |
| [CorpusId:123113460](https://api.semanticscholar.org/CorpusId:123113460) | 2026-10-13 | time reversal of diffusion processes, from title; probability theory, not collapse |
| [2405.17922](https://arxiv.org/abs/2405.17922) | 2026-10-13 | SGD for performative prediction with nonconvex loss; not generative models trained on generated data |
| [CorpusId:276318376](https://api.semanticscholar.org/CorpusId:276318376) | 2026-10-13 | about co-teaching optimization with SAM; not generative recursive training |
| [2304.05613](https://arxiv.org/abs/2304.05613) | 2026-10-13 | multilingual evaluation of ChatGPT; not model collapse |
| [1409.1556](https://arxiv.org/abs/1409.1556) | 2026-10-13 | image classification architecture; unrelated to model collapse |
| [2609.01597](https://arxiv.org/abs/2609.01597) | 2026-10-13 | survey of verbal feedback for language agents; not about training on generated data degrading models |
| [2307.08189](https://arxiv.org/abs/2307.08189) | 2026-10-13 | position on small open-source language models; not about recursive training |
| [2308.12488](https://arxiv.org/abs/2308.12488) | 2026-10-13 | survey of ChatGPT evaluations; not about recursive training |
| [2401.12070](https://arxiv.org/abs/2401.12070) | 2026-10-13 | machine-text detector not tested against degradation or for training-data filtering; excluded detection theme |
| [CorpusId:208036281](https://api.semanticscholar.org/CorpusId:208036281) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [CorpusId:271926161](https://api.semanticscholar.org/CorpusId:271926161) | 2026-10-13 | survey of LLM data augmentation; synthetic data used once, no recursive loop |
| [CorpusId:22882861](https://api.semanticscholar.org/CorpusId:22882861) | 2026-10-13 | title: rehearsal against catastrophic forgetting; continual learning, not degradation across model generations |
| [CorpusId:289686779](https://api.semanticscholar.org/CorpusId:289686779) | 2026-10-13 | healthcare AI equity perspective; recursive retraining is one listed bias source in passing, not its subject |
| [CorpusId:199370376](https://api.semanticscholar.org/CorpusId:199370376) | 2026-10-13 | title: commonsense benchmark; not about training on generated data |
| [CorpusId:122004897](https://api.semanticscholar.org/CorpusId:122004897) | 2026-10-13 | eigenvalue perturbation bounds, from title; unrelated to model collapse |
| [2510.26707](https://arxiv.org/abs/2510.26707) | 2026-10-13 | value alignment dynamics during post-training; no recursive generations |
| [2203.07814](https://arxiv.org/abs/2203.07814) | 2026-10-13 | competitive programming code generation system; not about model collapse |
| [CorpusId:285608224](https://api.semanticscholar.org/CorpusId:285608224) | 2026-10-13 | alignment trilemma among value holders (tldr); not training on generated data |
| [2401.16454](https://arxiv.org/abs/2401.16454) | 2026-10-13 | user simulator for generating training dialogues once; no recursive degradation question |
| [2605.24743](https://arxiv.org/abs/2605.24743) | 2026-10-13 | reweights synthetic trajectories for one-off offline RL fine-tuning; no recursive training loop |
| [2411.18810](https://arxiv.org/abs/2411.18810) | 2026-10-13 | improves compositional text-to-image generation via seeds; no degradation over generations |
| [CorpusId:284550241](https://api.semanticscholar.org/CorpusId:284550241) | 2026-10-13 | LLM jailbreak defence; not about recursive training |
| [2310.01377](https://arxiv.org/abs/2310.01377) | 2026-10-13 | AI feedback dataset used once; no recursion over generations |
| [CorpusId:61019113](https://api.semanticscholar.org/CorpusId:61019113) | 2026-10-13 | title: catastrophic interference in sequential learning; not about generated training data |
| [2310.03003](https://arxiv.org/abs/2310.03003) | 2026-10-13 | LLM inference energy benchmark; not model collapse |
| [2410.18194](https://arxiv.org/abs/2410.18194) | 2026-10-13 | compression-based training data selection for target tasks; not about generated data or collapse |
| [CorpusId:53730186](https://api.semanticscholar.org/CorpusId:53730186) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [CorpusId:144678254](https://api.semanticscholar.org/CorpusId:144678254) | 2026-10-13 | psycholinguistics of dialogue; not about generative models |
| [CorpusId:121987403](https://api.semanticscholar.org/CorpusId:121987403) | 2026-10-13 | paired comparison statistics; not about recursive training |
| [2412.18219](https://arxiv.org/abs/2412.18219) | 2026-10-13 | class-incremental learning with adapter merging; not about generated training data |
| [2405.04219](https://arxiv.org/abs/2405.04219) | 2026-10-13 | experience refinement for software agents; no retraining degradation studied |
| [2208.07331](https://arxiv.org/abs/2208.07331) | 2026-10-13 | causal effect of predictions on outcomes; not generative recursive training |
| [CorpusId:123624130](https://api.semanticscholar.org/CorpusId:123624130) | 2026-10-13 | stochastic differential equations textbook, from title; unrelated to collapse |
| [2404.10995](https://arxiv.org/abs/2404.10995) | 2026-10-13 | clipped SGD under performative data shift; not generative models trained on generated data |
| [2411.04637](https://arxiv.org/abs/2411.04637) | 2026-10-13 | tutorial on LLM-assisted labeling; synthetic data used once, no recursion |
| [1606.05250](https://arxiv.org/abs/1606.05250) | 2026-10-13 | reading comprehension dataset; not about training on generated data |
| [CorpusId:231829607](https://api.semanticscholar.org/CorpusId:231829607) | 2026-10-13 | interview study of data quality practices; not about generated data loops |
| [2504.18116](https://arxiv.org/abs/2504.18116) | 2026-10-13 | self-training on own filtered reasoning traces for capability gain; excluded self-training theme |
| [CorpusId:283328592](https://api.semanticscholar.org/CorpusId:283328592) | 2026-10-13 | AI in artistic practice; not about recursive training |
| [2305.03053](https://arxiv.org/abs/2305.03053) | 2026-10-13 | merging vision models across tasks; not about recursive training on generated data |
| [CorpusId:279238118](https://api.semanticscholar.org/CorpusId:279238118) | 2026-10-13 | watermarking method by speculative sampling; no test against degradation across generations |
| [2410.18075](https://arxiv.org/abs/2410.18075) | 2026-10-13 | performative prediction in federated learning; not generative models trained on generated data |
| [2404.13076](https://arxiv.org/abs/2404.13076) | 2026-10-13 | LLM evaluator self-preference bias; not about recursive training across generations |
| [CorpusId:290450940](https://api.semanticscholar.org/CorpusId:290450940) | 2026-10-13 | review of AI-generated text detection framed by misuse; not tested against degradation across generations |
| [CorpusId:281219659](https://api.semanticscholar.org/CorpusId:281219659) | 2026-10-13 | general LLM survey; touches recursive training at most in passing |
| [CorpusId:291117487](https://api.semanticscholar.org/CorpusId:291117487) | 2026-10-13 | membership inference on models trained once on LLM-generated data; no recursive loop |
| [CorpusId:24553488](https://api.semanticscholar.org/CorpusId:24553488) | 2026-10-13 | deep model compression (title only); the topic is recursive training of generative models |
| [CorpusId:289980375](https://api.semanticscholar.org/CorpusId:289980375) | 2026-10-13 | semi-automated QA extraction for fine-tuning data; no recursive training on generated data |
| [2608.09490](https://arxiv.org/abs/2608.09490) | 2026-10-13 | task-vector weight-space composition; not about training on generated data |
| [2406.17324](https://arxiv.org/abs/2406.17324) | 2026-10-13 | measures ChatGPT word use in astronomy papers; no training on generated data |
| [CorpusId:282149666](https://api.semanticscholar.org/CorpusId:282149666) | 2026-10-13 | multi-LLM evaluator assessment method; not about recursive training |
| [1905.00076](https://arxiv.org/abs/1905.00076) | 2026-10-13 | distilling ensemble uncertainty into one model; single distillation, no recursive loop |
| [2207.14255](https://arxiv.org/abs/2207.14255) | 2026-10-13 | fill-in-the-middle training transformation; not about generated-data recursion |
| [2006.06887](https://arxiv.org/abs/2006.06887) | 2026-10-13 | stochastic optimisation for performative prediction; not generative models trained on generated data |
| [1612.00796](https://arxiv.org/abs/1612.00796) | 2026-10-13 | elastic weight consolidation for forgetting; not recursive training on generated data |
| [CorpusId:55716626](https://api.semanticscholar.org/CorpusId:55716626) | 2026-10-13 | historical linguistics of English; not about generative models |
| [1706.03762](https://arxiv.org/abs/1706.03762) | 2026-10-13 | Transformer architecture paper; not about recursive training |
| [2502.05923](https://arxiv.org/abs/2502.05923) | 2026-10-13 | iterative rule induction and synthetic data for classification gains; not degradation over generations |
| [2304.06879](https://arxiv.org/abs/2304.06879) | 2026-10-13 | performatively stable classifiers with neural networks; not generative models trained on generated data |
| [2302.10149](https://arxiv.org/abs/2302.10149) | 2026-10-13 | adversarial poisoning of web datasets; not degradation from training on generated data |
| [1907.11692](https://arxiv.org/abs/1907.11692) | 2026-10-13 | BERT pretraining replication study; no recursive generative training |
| [CorpusId:113611201](https://api.semanticscholar.org/CorpusId:113611201) | 2026-10-13 | latent class model of pedestrian injuries; unrelated to generative model retraining |
| [2601.22285](https://arxiv.org/abs/2601.22285) | 2026-10-13 | predicting model merging success; not about recursive training on generated data |
| [2301.02241](https://arxiv.org/abs/2301.02241) | 2026-10-13 | curation of web image-text data for efficiency; not generated data or recursion |
| [CorpusId:270765512](https://api.semanticscholar.org/CorpusId:270765512) | 2026-10-13 | compares keyword usage of human and AI writing (tldr); no training on generated data |
| [CorpusId:80628558](https://api.semanticscholar.org/CorpusId:80628558) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2306.13384](https://arxiv.org/abs/2306.13384) | 2026-10-13 | diffusion synthesis of histology images; no recursive training |
| [2502.00012](https://arxiv.org/abs/2502.00012) | 2026-10-13 | complexity theory for AI governance; synthetic-data feedback loops mentioned only in passing |
| [2302.12580](https://arxiv.org/abs/2302.12580) | 2026-10-13 | membership inference against synthetic data; privacy, not model collapse |
| [2401.00974](https://arxiv.org/abs/2401.00974) | 2026-10-13 | generative model selection for one-off synthetic fraud training data; no recursive loop |
| [CorpusId:15068](https://api.semanticscholar.org/CorpusId:15068) | 2026-10-13 | atmospheric longwave irradiance; unrelated to generative models |
| [2601.16863](https://arxiv.org/abs/2601.16863) | 2026-10-13 | runtime mixture-of-models deliberation protocol; not about training on generated data |
| [2204.05999](https://arxiv.org/abs/2204.05999) | 2026-10-13 | code infilling model; not about model collapse |
| [CorpusId:23284154](https://api.semanticscholar.org/CorpusId:23284154) | 2026-10-13 | empirical Bayes selection bias; unrelated to generative model collapse |
| [2602.23446](https://arxiv.org/abs/2602.23446) | 2026-10-13 | error floors from human supervision channel; not about training on generated data |
| [CorpusId:268418167](https://api.semanticscholar.org/CorpusId:268418167) | 2026-10-13 | prompt engineering to debias image generation; not about recursive training |
| [2410.21526](https://arxiv.org/abs/2410.21526) | 2026-10-13 | weights LLM-generated data for one-shot augmentation; no recursive loop |
| [2412.18925](https://arxiv.org/abs/2412.18925) | 2026-10-13 | verifier-guided medical reasoning training; excluded self-training for capability |
| [CorpusId:17905356](https://api.semanticscholar.org/CorpusId:17905356) | 2026-10-13 | cellular autophagy in tumor metabolism; not model autophagy of generative models |
| [CorpusId:15485387](https://api.semanticscholar.org/CorpusId:15485387) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2303.05615](https://arxiv.org/abs/2303.05615) | 2026-10-13 | review of a statistical distribution family; no recursive training of generative models |
| [CorpusId:270330320](https://api.semanticscholar.org/CorpusId:270330320) | 2026-10-13 | defense department risks of fielding LLMs; not model collapse |
| [2508.18771](https://arxiv.org/abs/2508.18771) | 2026-10-13 | empirical study of AI code review tools; unrelated to model collapse |
| [2103.03874](https://arxiv.org/abs/2103.03874) | 2026-10-13 | math problem-solving dataset; not about model collapse |
| [CorpusId:266741058](https://api.semanticscholar.org/CorpusId:266741058) | 2026-10-13 | editorial for a special issue on algorithms in society; title names no generated-data training subject |
| [2602.19021](https://arxiv.org/abs/2602.19021) | 2026-10-13 | security risk index for agentic AI pipelines; not about model collapse |
| [CorpusId:281013651](https://api.semanticscholar.org/CorpusId:281013651) | 2026-10-13 | translation quality standards; not generative model recursion |
| [1906.09531](https://arxiv.org/abs/1906.09531) | 2026-10-13 | importance-weighting bias correction of one generative model; no recursion over generations |
| [2504.05831](https://arxiv.org/abs/2504.05831) | 2026-10-13 | robust preference alignment under synthetic-data shift; one-time synthetic data, no recursion |
| [2403.06857](https://arxiv.org/abs/2403.06857) | 2026-10-13 | caregiving RAG language model; unrelated to model collapse |
| [2402.06957](https://arxiv.org/abs/2402.06957) | 2026-10-13 | architectural backdoors in neural networks; unrelated to recursive training |
| [1609.07843](https://arxiv.org/abs/1609.07843) | 2026-10-13 | language model architecture; no training on generated data |
| [CorpusId:280697392](https://api.semanticscholar.org/CorpusId:280697392) | 2026-10-13 | detecting AI-written news for integrity; excluded detection not tested against collapse |
| [CorpusId:16895865](https://api.semanticscholar.org/CorpusId:16895865) | 2026-10-13 | variational inference method for generative models (no abstract); not recursion |
| [2403.19754](https://arxiv.org/abs/2403.19754) | 2026-10-13 | one-round distillation data generation guarding tails; no recursive generational loop |
| [CorpusId:291188683](https://api.semanticscholar.org/CorpusId:291188683) | 2026-10-13 | human cognitive-commons knowledge collapse per S2 TLDR, no abstract; not models trained on generated data |
| [CorpusId:283924298](https://api.semanticscholar.org/CorpusId:283924298) | 2026-10-13 | federated feature store architecture; not about model collapse |
| [2507.01643](https://arxiv.org/abs/2507.01643) | 2026-10-13 | vision backbone for multimodal LLMs; not recursive generative training |
| [2608.14652](https://arxiv.org/abs/2608.14652) | 2026-10-13 | weather forecasting data scaling via super-resolution; no recursive generative loop |
| [CorpusId:282016009](https://api.semanticscholar.org/CorpusId:282016009) | 2026-10-13 | audio-text contrastive learning method; no recursive generated-data training |
| [CorpusId:286695553](https://api.semanticscholar.org/CorpusId:286695553) | 2026-10-13 | machine unlearning for fairness; not about recursive training |
| [CorpusId:273789709](https://api.semanticscholar.org/CorpusId:273789709) | 2026-10-13 | environmental impact of LLMs versus human labour; not model collapse |
| [CorpusId:287241101](https://api.semanticscholar.org/CorpusId:287241101) | 2026-10-13 | error accumulation in AI interactions generally; no training on generated data studied |
| [2108.07732](https://arxiv.org/abs/2108.07732) | 2026-10-13 | program synthesis benchmarks; not about recursive training on generated data |
| [2503.07315](https://arxiv.org/abs/2503.07315) | 2026-10-13 | group-robust reweighting for subpopulation shift; the topic is recursive training of generative models |
| [1704.05426](https://arxiv.org/abs/1704.05426) | 2026-10-13 | NLI dataset; not about training on generated data |
| [CorpusId:268523514](https://api.semanticscholar.org/CorpusId:268523514) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2510.05136](https://arxiv.org/abs/2510.05136) | 2026-10-13 | survey of linguistic features of AI text; not about training on it |
| [1903.07759](https://arxiv.org/abs/1903.07759) | 2026-10-13 | ML surrogate models for accelerator design; the topic is recursive training of generative models |
| [CorpusId:31405423](https://api.semanticscholar.org/CorpusId:31405423) | 2026-10-13 | parabolic PDE fundamental solution bounds; unrelated to model collapse |
| [CorpusId:141164509](https://api.semanticscholar.org/CorpusId:141164509) | 2026-10-13 | code-switching syntax; not about generative models |
| [2506.09681](https://arxiv.org/abs/2506.09681) | 2026-10-13 | diffusion model Wasserstein error bounds for one model; no recursion over generations |
| [2402.12847](https://arxiv.org/abs/2402.12847) | 2026-10-13 | instruction tuning for knowledge learning; no recursion on generated data |
| [2211.04325](https://arxiv.org/abs/2211.04325) | 2026-10-13 | forecasts human text data stock; mentions synthetic data only as a way forward |
| [CorpusId:221404528](https://api.semanticscholar.org/CorpusId:221404528) | 2026-10-13 | Parkinson's protein clearance biology; the topic is recursive training of generative models |
| [CorpusId:290289424](https://api.semanticscholar.org/CorpusId:290289424) | 2026-10-13 | survey of physicians' generative AI use as search engine; the topic is recursive training of generative models |
| [CorpusId:275938171](https://api.semanticscholar.org/CorpusId:275938171) | 2026-10-13 | software supply chain security directions; not generative recursion |
| [CorpusId:280976807](https://api.semanticscholar.org/CorpusId:280976807) | 2026-10-13 | semiconductor defect prediction with GNNs; the topic is recursive training of generative models |
| [2508.11933](https://arxiv.org/abs/2508.11933) | 2026-10-13 | machine-generated text detection for disinformation; excluded detection not tested against collapse |
| [2401.14196](https://arxiv.org/abs/2401.14196) | 2026-10-13 | code model report; not about model collapse |
| [CorpusId:123178801](https://api.semanticscholar.org/CorpusId:123178801) | 2026-10-13 | Luce's choice theory book, by its title; unrelated to recursive training of generative models |
| [2601.09966](https://arxiv.org/abs/2601.09966) | 2026-10-13 | economics of data deals for creators; cites the data feedback loop only as motivation |
| [CorpusId:286105580](https://api.semanticscholar.org/CorpusId:286105580) | 2026-10-13 | book on cliches in culture; not about generative models trained on generated data |
| [CorpusId:288131977](https://api.semanticscholar.org/CorpusId:288131977) | 2026-10-13 | semi-supervised audio-text contrastive learning with pseudo-text; not recursive generative training |
| [CorpusId:283015940](https://api.semanticscholar.org/CorpusId:283015940) | 2026-10-13 | synthetic training data for speaker attribution, used once; no recursion |
| [2509.13047](https://arxiv.org/abs/2509.13047) | 2026-10-13 | one-time synthetic QA for domain fine-tuning; no recursive loop |
| [2410.13098](https://arxiv.org/abs/2410.13098) | 2026-10-13 | replaces human with synthetic data in one training round; no recursive loop |
| [2306.05685](https://arxiv.org/abs/2306.05685) | 2026-10-13 | LLM-as-a-judge evaluation benchmarks; not about recursive training on generated data |
| [CorpusId:4979494](https://api.semanticscholar.org/CorpusId:4979494) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2402.13866](https://arxiv.org/abs/2402.13866) | 2026-10-13 | domain-specific accounting LLM fine-tuning; not about training on generated data |
| [2310.16608](https://arxiv.org/abs/2310.16608) | 2026-10-13 | review of performative prediction for predictive models; no generative models retrained on own outputs |
| [2403.07175](https://arxiv.org/abs/2403.07175) | 2026-10-13 | collapse during sequential ROME model editing; not training on generated data |
| [2402.06049](https://arxiv.org/abs/2402.06049) | 2026-10-13 | LLM agents debating humans; not about training on generated data |
| [2602.17787](https://arxiv.org/abs/2602.17787) | 2026-10-13 | market equilibria among generative model platforms; no training on generated data |
| [1901.08680](https://arxiv.org/abs/1901.08680) | 2026-10-13 | GAN training with multiple discriminators, one run; no recursion |
| [CorpusId:73457468](https://api.semanticscholar.org/CorpusId:73457468) | 2026-10-13 | biomedical autophagy in myeloma (title only); the topic is recursive training of generative models |
| [CorpusId:224931474](https://api.semanticscholar.org/CorpusId:224931474) | 2026-10-13 | epistemic logic of argumentation and Gettier; the topic is recursive training of generative models |
| [1606.04671](https://arxiv.org/abs/1606.04671) | 2026-10-13 | progressive networks for transfer without forgetting; not about generated training data |
| [2512.18412](https://arxiv.org/abs/2512.18412) | 2026-10-13 | few-shot graph classifier without backpropagation; unrelated to generated-data training |
| [2411.06624](https://arxiv.org/abs/2411.06624) | 2026-10-13 | about fairness metrics selection; not recursive training |
| [2409.12314](https://arxiv.org/abs/2409.12314) | 2026-10-13 | poisoning-induced implosion in one model; no recursion over generations |
| [CorpusId:291266844](https://api.semanticscholar.org/CorpusId:291266844) | 2026-10-13 | style and stance in Reddit discourse using LLM annotation; not training on generated data |
| [CorpusId:284965919](https://api.semanticscholar.org/CorpusId:284965919) | 2026-10-13 | self-healing ML retraining under concept drift; not training on generated data |
| [CorpusId:23181630](https://api.semanticscholar.org/CorpusId:23181630) | 2026-10-13 | cellular autophagy in liver metabolism; not model autophagy of generative models |
| [CorpusId:55996241](https://api.semanticscholar.org/CorpusId:55996241) | 2026-10-13 | Greenland ice-sheet modelling; unrelated to generative models |
| [2411.02207](https://arxiv.org/abs/2411.02207) | 2026-10-13 | representational divergence limits model merging; not about generated training data |
| [CorpusId:117043182](https://api.semanticscholar.org/CorpusId:117043182) | 2026-10-13 | supermartingale convergence theorem, from title; general probability, not collapse |
| [2205.01068](https://arxiv.org/abs/2205.01068) | 2026-10-13 | language model release report; no finding about recursive training or collapse |
| [2305.02806](https://arxiv.org/abs/2305.02806) | 2026-10-13 | submodular recommendation under bias; not about recursive generative training |
| [CorpusId:269742384](https://api.semanticscholar.org/CorpusId:269742384) | 2026-10-13 | semi-synthetic dataset for hardware debugging LLMs; one-time synthetic data |
| [CorpusId:235097394](https://api.semanticscholar.org/CorpusId:235097394) | 2026-10-13 | bias evaluation of pretrained transformers; no recursive training |
| [2403.13372](https://arxiv.org/abs/2403.13372) | 2026-10-13 | fine-tuning framework software; not about model collapse |
| [2310.11501](https://arxiv.org/abs/2310.11501) | 2026-10-13 | caricature in LLM persona simulations; not about training on generated data |
| [CorpusId:282667830](https://api.semanticscholar.org/CorpusId:282667830) | 2026-10-13 | critical study of synthetic data quality notions; no recursive training loop |
| [2602.12172](https://arxiv.org/abs/2602.12172) | 2026-10-13 | one-off distillation data synthesis method; no recursive loop |
| [2505.01484](https://arxiv.org/abs/2505.01484) | 2026-10-13 | watermarking scheme for LLM text provenance; not tested against collapse |
| [2312.00506](https://arxiv.org/abs/2312.00506) | 2026-10-13 | human writers using LLM ideas lose collective diversity; no model trained on generated data |
| [2607.19292](https://arxiv.org/abs/2607.19292) | 2026-10-13 | safety perspective on hidden failures; touches the topic at most in passing |
| [2606.15078](https://arxiv.org/abs/2606.15078) | 2026-10-13 | economic theory of human cognitive debt from AI use; not model training on generated data |
| [2412.17417](https://arxiv.org/abs/2412.17417) | 2026-10-13 | synthetic preference data for VLM hallucination alignment, used once; no recursion |
| [2203.00526](https://arxiv.org/abs/2203.00526) | 2026-10-13 | iterative weighted retraining for molecule optimization, a capability gain, not degradation |
| [2305.07759](https://arxiv.org/abs/2305.07759) | 2026-10-13 | synthetic dataset used once to train small LMs; no recursive loop |
| [CorpusId:270286471](https://api.semanticscholar.org/CorpusId:270286471) | 2026-10-13 | history of open source and Copilot; not recursive training |
| [CorpusId:278788950](https://api.semanticscholar.org/CorpusId:278788950) | 2026-10-13 | self-learning to raise response diversity as a capability gain; no degradation over generations per title and tldr |
| [2402.08250](https://arxiv.org/abs/2402.08250) | 2026-10-13 | survey of AI fairness in biomedicine; unrelated to model collapse |
| [2405.20003](https://arxiv.org/abs/2405.20003) | 2026-10-13 | uncertainty quantification for LLM hallucination; not about model collapse |
| [CorpusId:280475882](https://api.semanticscholar.org/CorpusId:280475882) | 2026-10-13 | complex systems lessons for AI governance; synthetic-data feedback loops mentioned only in passing |
| [CorpusId:282541047](https://api.semanticscholar.org/CorpusId:282541047) | 2026-10-13 | title is about quantitative text analysis methods; not recursive training |
| [2405.13708](https://arxiv.org/abs/2405.13708) | 2026-10-13 | vision for end-user software engineering; not model collapse |
| [CorpusId:1152227](https://api.semanticscholar.org/CorpusId:1152227) | 2026-10-13 | score matching estimation, from title; not about recursive training |
| [CorpusId:58941274](https://api.semanticscholar.org/CorpusId:58941274) | 2026-10-13 | solar cell impedance modelling; unrelated to generative models |
| [CorpusId:6421230](https://api.semanticscholar.org/CorpusId:6421230) | 2026-10-13 | title: speciation population genetics; not about generative models |
| [2204.08281](https://arxiv.org/abs/2204.08281) | 2026-10-13 | decision-dependent risk minimisation in dynamic environments; not generative recursive training |
| [1810.08575](https://arxiv.org/abs/1810.08575) | 2026-10-13 | iterated amplification for capability gains; not degradation over generations |
| [CorpusId:281450285](https://api.semanticscholar.org/CorpusId:281450285) | 2026-10-13 | industrial policy on data and compute control; not recursive training |
| [2402.06627](https://arxiv.org/abs/2402.06627) | 2026-10-13 | test-time in-context feedback loops and reward hacking; no training on generated data |
| [CorpusId:24175064](https://api.semanticscholar.org/CorpusId:24175064) | 2026-10-13 | cellular autophagy in fish ovary; not model autophagy of generative models |
| [CorpusId:4487024](https://api.semanticscholar.org/CorpusId:4487024) | 2026-10-13 | customer lifetime Pareto/NBD model; unrelated to generative models |
| [2103.00020](https://arxiv.org/abs/2103.00020) | 2026-10-13 | CLIP pretraining method; no recursive training on generated data |
| [2509.17304](https://arxiv.org/abs/2509.17304) | 2026-10-13 | optimisation algorithm for performative prediction of predictive models; not generative models trained on generated data |
| [2404.04566](https://arxiv.org/abs/2404.04566) | 2026-10-13 | green LLMs for software engineering review; not model collapse |
| [1503.03585](https://arxiv.org/abs/1503.03585) | 2026-10-13 | introduces diffusion probabilistic models; not about recursive training |
| [2406.11931](https://arxiv.org/abs/2406.11931) | 2026-10-13 | code model report; no recursive training on generated data |
| [2106.13822](https://arxiv.org/abs/2106.13822) | 2026-10-13 | multilingual summarization dataset; unrelated to model collapse |
| [CorpusId:143438619](https://api.semanticscholar.org/CorpusId:143438619) | 2026-10-13 | sociology of the corporate elite; unrelated to generative models |
| [CorpusId:271369338](https://api.semanticscholar.org/CorpusId:271369338) | 2026-10-13 | title is about intellectual property law; not recursive training |
| [CorpusId:29848296](https://api.semanticscholar.org/CorpusId:29848296) | 2026-10-13 | pharyngeal airway collapse model; unrelated to generative models |
| [2601.02871](https://arxiv.org/abs/2601.02871) | 2026-10-13 | simulator-generated dialogue data used once for agent training; no recursion |
| [1705.08690](https://arxiv.org/abs/1705.08690) | 2026-10-13 | generative replay as a continual learning tool against forgetting; does not study degradation across generations |
| [CorpusId:278114149](https://api.semanticscholar.org/CorpusId:278114149) | 2026-10-13 | LLM performance on medical board exams; not recursive training |
| [CorpusId:10319744](https://api.semanticscholar.org/CorpusId:10319744) | 2026-10-13 | original GAN paper; one training run, no recursion |
| [1904.06991](https://arxiv.org/abs/1904.06991) | 2026-10-13 | evaluation metric for generative models; a tool, not about recursive training |
| [2203.06176](https://arxiv.org/abs/2203.06176) | 2026-10-13 | random matrix theory of generalization; not recursive generative training |
| [CorpusId:291056064](https://api.semanticscholar.org/CorpusId:291056064) | 2026-10-13 | review of human-AI complementarity in organisations; unrelated to recursive training |
| [2610.01674](https://arxiv.org/abs/2610.01674) | 2026-10-13 | system to generate post-training datasets; synthetic data used once, an excluded theme |
| [2506.14012](https://arxiv.org/abs/2506.14012) | 2026-10-13 | LLM code-switching evaluation; not model collapse |
| [CorpusId:279839105](https://api.semanticscholar.org/CorpusId:279839105) | 2026-10-13 | morphing airfoil aerodynamic optimization; the topic is recursive training of generative models |
| [2601.06160](https://arxiv.org/abs/2601.06160) | 2026-10-13 | inference-time exploration against reasoning collapse; no training on generated data |
| [CorpusId:272330241](https://api.semanticscholar.org/CorpusId:272330241) | 2026-10-13 | title: projecting exhaustion of human text data for scaling; synthetic data recursion at most motivation |
| [2502.11466](https://arxiv.org/abs/2502.11466) | 2026-10-13 | Gibbs self-training for code generation gains; excluded self-training for capability |
| [2302.00138](https://arxiv.org/abs/2302.00138) | 2026-10-13 | selects synthetic samples for one-time augmentation; no recursive loop, excluded |
| [CorpusId:226096901](https://api.semanticscholar.org/CorpusId:226096901) | 2026-10-13 | Japanese summary of the BERT paper; not about recursive training |
| [2401.01335](https://arxiv.org/abs/2401.01335) | 2026-10-13 | self-play fine-tuning for capability gains; excluded self-training theme, no degradation question |
| [CorpusId:289811444](https://api.semanticscholar.org/CorpusId:289811444) | 2026-10-13 | tokenizer metrics for Hindi and Marathi; unrelated to model collapse |
| [CorpusId:277996148](https://api.semanticscholar.org/CorpusId:277996148) | 2026-10-13 | LLM agents debating humans; not training on generated data |
| [2204.06125](https://arxiv.org/abs/2204.06125) | 2026-10-13 | text-to-image generation method; not model collapse |
| [CorpusId:278825051](https://api.semanticscholar.org/CorpusId:278825051) | 2026-10-13 | generative hardware fuzzer; unrelated to model collapse |
| [2208.03306](https://arxiv.org/abs/2208.03306) | 2026-10-13 | parallel training of expert LMs; not about training on generated data |
| [1505.04597](https://arxiv.org/abs/1505.04597) | 2026-10-13 | U-Net segmentation architecture; unrelated to model collapse |
| [CorpusId:271770633](https://api.semanticscholar.org/CorpusId:271770633) | 2026-10-13 | history and risks of RLHF; not recursive training on generated data |
| [1905.07830](https://arxiv.org/abs/1905.07830) | 2026-10-13 | commonsense inference benchmark; not about recursive training on generated data |
| [2607.24300](https://arxiv.org/abs/2607.24300) | 2026-10-13 | agents rewriting heuristic policies with self-authored tests; not generative models retrained on generated data |
| [2308.12950](https://arxiv.org/abs/2308.12950) | 2026-10-13 | code model release; not about model collapse |
| [CorpusId:244639533](https://api.semanticscholar.org/CorpusId:244639533) | 2026-10-13 | GAN for time series anomaly detection; GAN mode collapse, an excluded theme |
| [1604.06651](https://arxiv.org/abs/1604.06651) | 2026-10-13 | utility measures for statistical disclosure synthetic data; no recursive loop |
| [CorpusId:237195013](https://api.semanticscholar.org/CorpusId:237195013) | 2026-10-13 | medical X-ray detection with augmentation (title only); the topic is recursive training of generative models |
| [CorpusId:260447696](https://api.semanticscholar.org/CorpusId:260447696) | 2026-10-13 | book on crowd labour; not about generative models trained on generated data |
| [CorpusId:220663293](https://api.semanticscholar.org/CorpusId:220663293) | 2026-10-13 | software engineering study of code review; not about model collapse |
| [2409.12186](https://arxiv.org/abs/2409.12186) | 2026-10-13 | code model technical report; synthetic data used once, no recursive retraining |
| [CorpusId:285216092](https://api.semanticscholar.org/CorpusId:285216092) | 2026-10-13 | MLOps CI/CD reference architecture; title gives no generated-data recursion |
| [CorpusId:280016965](https://api.semanticscholar.org/CorpusId:280016965) | 2026-10-13 | human-validated code-switched dataset; not about recursive training |
| [CorpusId:286779234](https://api.semanticscholar.org/CorpusId:286779234) | 2026-10-13 | review of privacy-preserving synthetic data generation; no recursive training |
| [2402.00699](https://arxiv.org/abs/2402.00699) | 2026-10-13 | dataset of pre-trained model reuse in software; not about generated training data |
| [2306.11393](https://arxiv.org/abs/2306.11393) | 2026-10-13 | creative practices of text-to-image communities; not about training on generated data |
| [2407.01492](https://arxiv.org/abs/2407.01492) | 2026-10-13 | pretraining data mixture regression; no generated-data recursion |
| [CorpusId:964287](https://api.semanticscholar.org/CorpusId:964287) | 2026-10-13 | summarization evaluation metric ROUGE, from title; unrelated to model collapse |
| [CorpusId:214047809](https://api.semanticscholar.org/CorpusId:214047809) | 2026-10-13 | BCI model compression in hyperdimensional space; the topic is recursive training of generative models |
| [2312.07853](https://arxiv.org/abs/2312.07853) | 2026-10-13 | visible-infrared person re-identification; unrelated to recursive training |
| [2201.03299](https://arxiv.org/abs/2201.03299) | 2026-10-13 | CNN regularisation survey; not model collapse |
| [2504.12229](https://arxiv.org/abs/2504.12229) | 2026-10-13 | watermark reliability under human mimicry; detection not tested against collapse |
| [2512.14624](https://arxiv.org/abs/2512.14624) | 2026-10-13 | minimax score estimation theory; not about recursive training on generated data |
| [2310.07251](https://arxiv.org/abs/2310.07251) | 2026-10-13 | position on ethical reasoning in LLMs; unrelated to recursive training |
| [CorpusId:275041601](https://api.semanticscholar.org/CorpusId:275041601) | 2026-10-13 | survey of synthetic content detection; not tested as a defence against collapse |
| [2407.08699](https://arxiv.org/abs/2407.08699) | 2026-10-13 | forgetting in language transfer via merging; not about generated training data |
| [1411.1784](https://arxiv.org/abs/1411.1784) | 2026-10-13 | conditional GAN architecture; no recursive training |
| [CorpusId:234596271](https://api.semanticscholar.org/CorpusId:234596271) | 2026-10-13 | cellular autophagy in ovarian dysfunction; not model autophagy of generative models |
| [CorpusId:280653623](https://api.semanticscholar.org/CorpusId:280653623) | 2026-10-13 | self-training on own filtered reasoning traces for capability gain; excluded self-training theme |
| [CorpusId:3897405](https://api.semanticscholar.org/CorpusId:3897405) | 2026-10-13 | reverse-time diffusion equations, from title; probability theory, not collapse |
| [CorpusId:51612601](https://api.semanticscholar.org/CorpusId:51612601) | 2026-10-13 | conditional GAN for cartoon colouring; GAN mode collapse, an excluded theme |
| [2311.04378](https://arxiv.org/abs/2311.04378) | 2026-10-13 | impossibility of strong watermarking, not tested as a collapse defence; excluded theme |
| [CorpusId:13502795](https://api.semanticscholar.org/CorpusId:13502795) | 2026-10-13 | title: evolutionary biology of sex and recombination; not generative models |
| [2503.05683](https://arxiv.org/abs/2503.05683) | 2026-10-13 | lifelong knowledge editing benchmark; not about training on generated data |
| [CorpusId:278775641](https://api.semanticscholar.org/CorpusId:278775641) | 2026-10-13 | categorizing LM inputs for performance analysis; not about model collapse |
| [2309.08133](https://arxiv.org/abs/2309.08133) | 2026-10-13 | copyright law and the generative-AI supply chain; not about model degradation |
| [CorpusId:280668719](https://api.semanticscholar.org/CorpusId:280668719) | 2026-10-13 | viewpoint on synthetic medical images used for training; no recursive loop |
| [2607.21673](https://arxiv.org/abs/2607.21673) | 2026-10-13 | self-poisoning feedback in an OOD detector memory bank; not generative models trained on generated data |
| [2209.04836](https://arxiv.org/abs/2209.04836) | 2026-10-13 | permutation alignment for weight merging; not about recursive training on generated data |
| [2604.11188](https://arxiv.org/abs/2604.11188) | 2026-10-13 | math reasoning data synthesis for capability gains; mode collapse of the synthesizer, not generational degradation |
| [CorpusId:263775366](https://api.semanticscholar.org/CorpusId:263775366) | 2026-10-13 | bioethics commentary on responsible AI as a moat; cites self-consuming models only in passing |
| [2510.13928](https://arxiv.org/abs/2510.13928) | 2026-10-13 | continual pretraining on low-quality human tweets; junk is not model-generated, no recursion |
| [CorpusId:123564748](https://api.semanticscholar.org/CorpusId:123564748) | 2026-10-13 | infinite-dimensional stochastic equations, from title; unrelated to collapse |
| [CorpusId:290051941](https://api.semanticscholar.org/CorpusId:290051941) | 2026-10-13 | survey of transformers by input modality, by its title; not training on generated data |
| [CorpusId:286836412](https://api.semanticscholar.org/CorpusId:286836412) | 2026-10-13 | compact models for health dialogue summarisation; no recursive training |
| [CorpusId:47019332](https://api.semanticscholar.org/CorpusId:47019332) | 2026-10-13 | adversarial evasion-robust classification; the topic is recursive training of generative models |
| [2508.00238](https://arxiv.org/abs/2508.00238) | 2026-10-13 | LLM-associated words in human speech; linguistics, not model training on generated data |
| [2310.15296](https://arxiv.org/abs/2310.15296) | 2026-10-13 | diffusion-enhanced topic modelling; not about training on generated data |
| [2601.17096](https://arxiv.org/abs/2601.17096) | 2026-10-13 | cultural behaviour of LLMs across languages; not about model collapse |
| [2506.00051](https://arxiv.org/abs/2506.00051) | 2026-10-13 | position on orchestrating expert models; not recursive training |
| [2404.06787](https://arxiv.org/abs/2404.06787) | 2026-10-13 | private Wasserstein distance computation; unrelated to model collapse |
| [CorpusId:19665636](https://api.semanticscholar.org/CorpusId:19665636) | 2026-10-13 | biomedical autophagy in liver cells (title only); the topic is recursive training of generative models |
| [2309.16777](https://arxiv.org/abs/2309.16777) | 2026-10-13 | test system for ChatGPT word knowledge; not about recursive training |
| [2006.16923](https://arxiv.org/abs/2006.16923) | 2026-10-13 | ethics audit of vision datasets; not about training on generated data |
| [2406.12845](https://arxiv.org/abs/2406.12845) | 2026-10-13 | reward modeling for RLHF; no recursive training on generated data |
| [CorpusId:290651823](https://api.semanticscholar.org/CorpusId:290651823) | 2026-10-13 | cloud infrastructure observability with foundation models; not about model collapse |
| [2204.14198](https://arxiv.org/abs/2204.14198) | 2026-10-13 | visual language model report; not about training on generated data |
| [2506.04689](https://arxiv.org/abs/2506.04689) | 2026-10-13 | rewriting discarded web text for pretraining; synthetic data used once, no recursion |
| [CorpusId:220586099](https://api.semanticscholar.org/CorpusId:220586099) | 2026-10-13 | cellular autophagy in Parkinson's disease; not model autophagy of generative models |
| [CorpusId:137257926](https://api.semanticscholar.org/CorpusId:137257926) | 2026-10-13 | finite element modelling of timber beams; unrelated to generative models |
| [CorpusId:1430482](https://api.semanticscholar.org/CorpusId:1430482) | 2026-10-13 | cellular autophagy in ischemic astrocytes; not model autophagy of generative models |
| [astro-ph/0412243](https://arxiv.org/abs/astro-ph/0412243) | 2026-10-13 | stellar core collapse simulations; unrelated to generative models |
| [2412.15652](https://arxiv.org/abs/2412.15652) | 2026-10-13 | teacher-guided data-efficient LMM tuning; one-time synthetic data |
| [2205.11487](https://arxiv.org/abs/2205.11487) | 2026-10-13 | text-to-image model report; no recursive training on generated data |
| [2410.20796](https://arxiv.org/abs/2410.20796) | 2026-10-13 | rephrased synthetic text for pretraining, used once; excluded synthetic-data-used-once theme |
| [2312.14751](https://arxiv.org/abs/2312.14751) | 2026-10-13 | hazards of accessible fine-tuning of open models; not about training on generated data |
| [2404.01268](https://arxiv.org/abs/2404.01268) | 2026-10-13 | measures LLM-modified text prevalence in papers; no training on generated data studied |
| [CorpusId:264403242](https://api.semanticscholar.org/CorpusId:264403242) | 2026-10-13 | synthetic captions to improve image generation, by its title; synthetic data used once, an excluded theme |
| [2510.15317](https://arxiv.org/abs/2510.15317) | 2026-10-13 | improving multimodal SFT data quality once; no recursive loop |
| [2505.09598](https://arxiv.org/abs/2505.09598) | 2026-10-13 | energy footprint of LLM inference; unrelated to recursive training |
| [CorpusId:291149383](https://api.semanticscholar.org/CorpusId:291149383) | 2026-10-13 | review of data synthesis for LLM reasoning gains; self-training for capability, an excluded theme |
| [CorpusId:53592270](https://api.semanticscholar.org/CorpusId:53592270) | 2026-10-13 | AdamW optimizer weight decay, from title; unrelated to model collapse |
| [2401.06829](https://arxiv.org/abs/2401.06829) | 2026-10-13 | LLM watermarking method, not tested as a defence against collapse; excluded theme |
| [2310.05178](https://arxiv.org/abs/2310.05178) | 2026-10-13 | LLM tuned to generate smart-contract code; not about training on generated data |
| [CorpusId:281308354](https://api.semanticscholar.org/CorpusId:281308354) | 2026-10-13 | literary reflections on AI-generated literature; not recursive training |
| [2512.17592](https://arxiv.org/abs/2512.17592) | 2026-10-13 | stitching disjointly trained models; not about training on generated data |
| [1606.03498](https://arxiv.org/abs/1606.03498) | 2026-10-13 | GAN training techniques within one run; no recursion |
| [CorpusId:286738516](https://api.semanticscholar.org/CorpusId:286738516) | 2026-10-13 | information literacy framework for human-AI conversation; not about recursive training |
| [CorpusId:269826337](https://api.semanticscholar.org/CorpusId:269826337) | 2026-10-13 | hyperdimensional computing image classification; the topic is recursive training of generative models |
| [2605.30529](https://arxiv.org/abs/2605.30529) | 2026-10-13 | synthetic data for clinical coding retrieval; synthetic data used once, an excluded theme |
| [2105.00717](https://arxiv.org/abs/2105.00717) | 2026-10-13 | synthetic data for model selection, used once; no recursive generative loop |
| [2301.03988](https://arxiv.org/abs/2301.03988) | 2026-10-13 | code model tech report on data filtering; not about recursive training |
| [2607.09202](https://arxiv.org/abs/2607.09202) | 2026-10-13 | continual learning forgetting as task interference; not about generated training data |
| [2007.10022](https://arxiv.org/abs/2007.10022) | 2026-10-13 | sparse CNN filter regularization; the topic is recursive training of generative models |
| [2406.03356](https://arxiv.org/abs/2406.03356) | 2026-10-13 | crowdsourced label aggregation for plant identification; not generated-data recursion |
| [2406.04064](https://arxiv.org/abs/2406.04064) | 2026-10-13 | measuring social bias in LLMs; no recursive training |
| [CorpusId:286019891](https://api.semanticscholar.org/CorpusId:286019891) | 2026-10-13 | essay on ChatGPT and human imagination; not about training on generated data |
| [2401.17435](https://arxiv.org/abs/2401.17435) | 2026-10-13 | LLM-generated data used once for choice prediction; no recursive loop |
| [CorpusId:286647069](https://api.semanticscholar.org/CorpusId:286647069) | 2026-10-13 | reasoning collapse within one RL training run of agents; no recursion over generations |
| [CorpusId:264752010](https://api.semanticscholar.org/CorpusId:264752010) | 2026-10-13 | Gaussian measure theory, from truncated title; unrelated to model collapse |
| [CorpusId:285832240](https://api.semanticscholar.org/CorpusId:285832240) | 2026-10-13 | title: hallucination detection for vision-language models; unrelated to recursive training |
| [2603.03140](https://arxiv.org/abs/2603.03140) | 2026-10-13 | persona analysis of AI agent posts on a social platform; not about training on generated data |
| [2310.17944](https://arxiv.org/abs/2310.17944) | 2026-10-13 | survey of trustworthy edge intelligence; unrelated to model collapse |
| [2510.04226](https://arxiv.org/abs/2510.04226) | 2026-10-13 | measures LLM output epistemic diversity across models; no recursive training on generated data |
| [2312.09390](https://arxiv.org/abs/2312.09390) | 2026-10-13 | weak-to-strong supervision for alignment; not recursive training on generated data |
| [2605.28664](https://arxiv.org/abs/2605.28664) | 2026-10-13 | activation steering to generate safety-classifier data; synthetic data used once, an excluded theme |
| [2202.05830](https://arxiv.org/abs/2202.05830) | 2026-10-13 | fast diffusion samplers; no recursive training |
| [2507.17578](https://arxiv.org/abs/2507.17578) | 2026-10-13 | one-time synthetic voice data for ASR fine-tuning; no recursive loop |
| [CorpusId:291221498](https://api.semanticscholar.org/CorpusId:291221498) | 2026-10-13 | apology sincerity detection with multilingual transformers; unrelated to recursive training |
| [CorpusId:49217999](https://api.semanticscholar.org/CorpusId:49217999) | 2026-10-13 | software engineering case study of code review; not about model collapse |
| [2410.02184](https://arxiv.org/abs/2410.02184) | 2026-10-13 | LLM-based code evaluation; unrelated to model collapse |
| [1906.12340](https://arxiv.org/abs/1906.12340) | 2026-10-13 | self-supervision for robustness; no generated-data loop |
| [2304.11771](https://arxiv.org/abs/2304.11771) | 2026-10-13 | economics of AI assistance for workers; not model training |
| [1610.03256](https://arxiv.org/abs/1610.03256) | 2026-10-13 | flat-start HMM/DNN speech training; the topic is recursive training of generative models |
| [CorpusId:59832877](https://api.semanticscholar.org/CorpusId:59832877) | 2026-10-13 | title: spatial evolutionary algorithms book; not about generative model training |
| [CorpusId:280243570](https://api.semanticscholar.org/CorpusId:280243570) | 2026-10-13 | negative labeling for mineral prospectivity mapping; not generative models |
| [CorpusId:266232277](https://api.semanticscholar.org/CorpusId:266232277) | 2026-10-13 | eating detection from wrist motion; the topic is recursive training of generative models |
| [CorpusId:43188859](https://api.semanticscholar.org/CorpusId:43188859) | 2026-10-13 | linear algebra textbook; not about recursive training of generative models |
| [2508.00965](https://arxiv.org/abs/2508.00965) | 2026-10-13 | LLM-generated adversarial NLI data used to fortify a classifier; synthetic augmentation, no recursive generative loop |
| [2307.02599](https://arxiv.org/abs/2307.02599) | 2026-10-13 | evading AI-text detectors; detection not tested as a collapse defence |
| [2412.08905](https://arxiv.org/abs/2412.08905) | 2026-10-13 | model report using synthetic data once for training; no recursive loop studied |
| [CorpusId:291086866](https://api.semanticscholar.org/CorpusId:291086866) | 2026-10-13 | generative stylistic completion of music; no recursive training loop |
| [2602.01227](https://arxiv.org/abs/2602.01227) | 2026-10-13 | position on token priority in SFT; not about generated-data degradation |
| [CorpusId:284401216](https://api.semanticscholar.org/CorpusId:284401216) | 2026-10-13 | review of prompt engineering; not about training on generated data |
| [CorpusId:281508763](https://api.semanticscholar.org/CorpusId:281508763) | 2026-10-13 | federated data modeling for LLM deployment; not about model collapse |
| [2306.06626](https://arxiv.org/abs/2306.06626) | 2026-10-13 | diffusion probability paths; no training on generated data |
| [2403.15475](https://arxiv.org/abs/2403.15475) | 2026-10-13 | perspective on LLMs in agriculture; unrelated to model collapse |
| [CorpusId:122007719](https://api.semanticscholar.org/CorpusId:122007719) | 2026-10-13 | mathematical note on Wasserstein distances, by its title; background tool, not the topic |
| [2412.11145](https://arxiv.org/abs/2412.11145) | 2026-10-13 | position on superalignment learning paradigm; not model collapse |
| [2403.07750](https://arxiv.org/abs/2403.07750) | 2026-10-13 | synthetic captions and embeddings used once for VLM training; no recursion |
| [2608.20290](https://arxiv.org/abs/2608.20290) | 2026-10-13 | measurement audit of self-improvement capability gains; excluded self-training theme |
| [2501.03941](https://arxiv.org/abs/2501.03941) | 2026-10-13 | privacy metrics for synthetic data; no recursive training |
| [1111.6453](https://arxiv.org/abs/1111.6453) | 2026-10-13 | submodular optimization monograph; unrelated to model collapse |
| [2509.04479](https://arxiv.org/abs/2509.04479) | 2026-10-13 | interpretability of rare-token neurons; not training on generated data |
| [CorpusId:278762359](https://api.semanticscholar.org/CorpusId:278762359) | 2026-10-13 | LLMs in advertising research overview; not recursive training |
| [2503.14023](https://arxiv.org/abs/2503.14023) | 2026-10-13 | survey of LLM synthetic data generation for tasks; synthetic data used once, no recursion studied |
| [CorpusId:4410317](https://api.semanticscholar.org/CorpusId:4410317) | 2026-10-13 | cellular autophagy in muscle biology; not model autophagy of generative models |
| [CorpusId:199089871](https://api.semanticscholar.org/CorpusId:199089871) | 2026-10-13 | composite shell optimization with surrogate networks; the topic is recursive training of generative models |
| [CorpusId:17380852](https://api.semanticscholar.org/CorpusId:17380852) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [1905.00569](https://arxiv.org/abs/1905.00569) | 2026-10-13 | group retention and fairness in sequential decisions; not generative models trained on generated data |
| [2603.23848](https://arxiv.org/abs/2603.23848) | 2026-10-13 | benchmark of belief drift in conversational agents; not about recursive training |
| [1806.00035](https://arxiv.org/abs/1806.00035) | 2026-10-13 | precision/recall evaluation metric for generative models; not about recursive training |
| [2505.16245](https://arxiv.org/abs/2505.16245) | 2026-10-13 | length-controlled preference data selection for diversity; single training round, no recursion |
| [1808.06226](https://arxiv.org/abs/1808.06226) | 2026-10-13 | subword tokenizer tool; unrelated to model collapse |
| [CorpusId:282576026](https://api.semanticscholar.org/CorpusId:282576026) | 2026-10-13 | standard for labelling machine-generated content; not tested as collapse defence |
| [2508.06811](https://arxiv.org/abs/2508.06811) | 2026-10-13 | fine-tuning lineages on Hugging Face; model family trees, not training on generated data |
| [2602.08344](https://arxiv.org/abs/2602.08344) | 2026-10-13 | RL for parallel thinking in reasoning models; not about training on generated data |
| [1606.09282](https://arxiv.org/abs/1606.09282) | 2026-10-13 | continual learning without old data; not generative recursion |
| [1806.07268](https://arxiv.org/abs/1806.07268) | 2026-10-13 | GAN equilibrium training within one run; no recursion |
| [2608.00003](https://arxiv.org/abs/2608.00003) | 2026-10-13 | self-refining LLM agent for CFD simulation; not about model degradation from generated data |
| [2304.08466](https://arxiv.org/abs/2304.08466) | 2026-10-13 | diffusion samples used once to augment ImageNet; no recursive loop |
| [1306.0895](https://arxiv.org/abs/1306.0895) | 2026-10-13 | Sinkhorn optimal transport computation; unrelated to model collapse |
| [2003.02800](https://arxiv.org/abs/2003.02800) | 2026-10-13 | filter pruning during training; the topic is recursive training of generative models |
| [CorpusId:264360120](https://api.semanticscholar.org/CorpusId:264360120) | 2026-10-13 | wearable physiological signals across menstrual cycle; the topic is recursive training of generative models |
| [2212.10522](https://arxiv.org/abs/2212.10522) | 2026-10-13 | generating humorous paper titles; unrelated to model collapse |
| [2508.10975](https://arxiv.org/abs/2508.10975) | 2026-10-13 | synthetic pretraining data generation at scale; synthetic data used once, no recursion |
| [2412.01948](https://arxiv.org/abs/2412.01948) | 2026-10-13 | general review of AI-generated content history; not about recursive training degradation |
| [2408.10437](https://arxiv.org/abs/2408.10437) | 2026-10-13 | embedding analysis of generative AI content; no recursive training studied |
| [2506.05101](https://arxiv.org/abs/2506.05101) | 2026-10-13 | privacy amplification of synthetic data in linear regression; no recursive training over generations |
| [2305.01569](https://arxiv.org/abs/2305.01569) | 2026-10-13 | text-to-image preference dataset; not about recursive training |
| [2505.16339](https://arxiv.org/abs/2505.16339) | 2026-10-13 | LLM-assisted code review field study; unrelated to model collapse |
| [2502.14948](https://arxiv.org/abs/2502.14948) | 2026-10-13 | solver-verifier self-play for coding gains; excluded self-training for capability |
| [CorpusId:291373414](https://api.semanticscholar.org/CorpusId:291373414) | 2026-10-13 | curator agent for diverse single-round synthetic fine-tuning data; synthetic data used once, no recursive loop |
| [2407.01490](https://arxiv.org/abs/2407.01490) | 2026-10-13 | property inheritance through one round of distilled synthetic data; no recursive loop |
| [2002.09797](https://arxiv.org/abs/2002.09797) | 2026-10-13 | generic fidelity/diversity metrics for generative models; not about recursive training |
| [CorpusId:279728007](https://api.semanticscholar.org/CorpusId:279728007) | 2026-10-13 | personalized federated graph learning for recommendation; the topic is recursive training of generative models |
| [2410.24198](https://arxiv.org/abs/2410.24198) | 2026-10-13 | self-generated verified instruction data for code skill gains; excluded self-training |
| [2412.01477](https://arxiv.org/abs/2412.01477) | 2026-10-13 | synthetic images used once for object detection; no recursive loop |
| [2511.04478](https://arxiv.org/abs/2511.04478) | 2026-10-13 | synthetic test cases for refining LLM judges; no recursive training |
| [CorpusId:250446558](https://api.semanticscholar.org/CorpusId:250446558) | 2026-10-13 | incentive mechanisms for strategic classification; not generative recursive training |
| [CorpusId:273575751](https://api.semanticscholar.org/CorpusId:273575751) | 2026-10-13 | editorial on AI in psychological therapy; unrelated to recursive training |
| [CorpusId:284923358](https://api.semanticscholar.org/CorpusId:284923358) | 2026-10-13 | dual-agent news verification; not about model collapse |
| [CorpusId:164982547](https://api.semanticscholar.org/CorpusId:164982547) | 2026-10-13 | economics of intellectual property and depression; the topic is recursive training of generative models |
| [CorpusId:8870132](https://api.semanticscholar.org/CorpusId:8870132) | 2026-10-13 | weakly supervised Mandarin parsing (title only); the topic is recursive training of generative models |
| [CorpusId:231850887](https://api.semanticscholar.org/CorpusId:231850887) | 2026-10-13 | quantization retraining for object detectors; the topic is recursive training of generative models |
| [2505.19145](https://arxiv.org/abs/2505.19145) | 2026-10-13 | position on statistics for LLMs; its listed areas do not include recursive training or collapse |
| [2601.13572](https://arxiv.org/abs/2601.13572) | 2026-10-13 | merging RL-trained agentic models; not about recursive training on generated data |
| [CorpusId:25205506](https://api.semanticscholar.org/CorpusId:25205506) | 2026-10-13 | cellular autophagy inhibitor in cancer; not model autophagy of generative models |
| [2412.06843](https://arxiv.org/abs/2412.06843) | 2026-10-13 | safety fine-tuning with semantic loss; not training over generations of generated data |
| [CorpusId:279918633](https://api.semanticscholar.org/CorpusId:279918633) | 2026-10-13 | title: prompt-based medical relation extraction; unrelated to model collapse |
| [CorpusId:255595257](https://api.semanticscholar.org/CorpusId:255595257) | 2026-10-13 | cell-biology autophagy study; the topic is recursive training of generative models |
| [2210.01745](https://arxiv.org/abs/2210.01745) | 2026-10-13 | decision-making under outcome performativity; not generative recursive training |
| [2503.04569](https://arxiv.org/abs/2503.04569) | 2026-10-13 | value-driven decision-making on generated scenarios; synthetic data used once |
| [2310.08618](https://arxiv.org/abs/2310.08618) | 2026-10-13 | opinion on deep learning in nanophotonics; unrelated to model collapse |
| [CorpusId:146609382](https://api.semanticscholar.org/CorpusId:146609382) | 2026-10-13 | title: history of Darwinian natural selection argument; biology, not generative models |
| [2405.01810](https://arxiv.org/abs/2405.01810) | 2026-10-13 | welfare-aware strategic learning for decision policies; not generative recursive training |
| [CorpusId:260610225](https://api.semanticscholar.org/CorpusId:260610225) | 2026-10-13 | biomedical autophagy in Parkinson's (title only); the topic is recursive training of generative models |
| [2509.02896](https://arxiv.org/abs/2509.02896) | 2026-10-13 | LLM cascades for data processing cost; unrelated to recursive training |
| [2411.16345](https://arxiv.org/abs/2411.16345) | 2026-10-13 | self-training for reasoning gains with pseudo feedback; excluded capability self-training |
| [CorpusId:13658192](https://api.semanticscholar.org/CorpusId:13658192) | 2026-10-13 | cellular autophagy in osteoarthritis; not model autophagy of generative models |
| [CorpusId:4656023](https://api.semanticscholar.org/CorpusId:4656023) | 2026-10-13 | sinusoidal parameter quantization (title only); the topic is recursive training of generative models |
| [CorpusId:271173425](https://api.semanticscholar.org/CorpusId:271173425) | 2026-10-13 | critical discourse studies view of LLMs; not recursive training |
| [CorpusId:145644958](https://api.semanticscholar.org/CorpusId:145644958) | 2026-10-13 | university audit culture; not about generative models |
| [CorpusId:290671235](https://api.semanticscholar.org/CorpusId:290671235) | 2026-10-13 | book on policymakers learning from the public; unrelated to recursive training |

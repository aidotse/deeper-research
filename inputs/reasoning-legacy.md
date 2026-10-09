## Topic

I've identified one area of research that I find especially interesting: test-time compute / reasoning capabilities in
LLMs. I find this interesting, because it seems the whole agentic body of work largely depends on this core capability,
and clearly as of 2024/2025 we are no longer in regime where scaling is along the train time compute dimension, but
rather the interesting tricks and such that we can do post-training. Without knowing much detail, it seems to me that
this (in addition to harness design for runtime behavior) is where most of the performance gains have been coming
recently, but please correct me if you would argue otherwise.

## Context

- I'd like to prioritize research directions that overlap with the focus of my PhD advisor's group, see details here
  https://stefsmlab.github.io/.

- I'd like to prioritize research directions that overlap with AI safety & security topics. Most of the funding for this
  work will actually be coming from the national defense budget, which makes these popular topics that should be easy to
  fund. So I need to be able to "sell" these research ideas as having some implications for this space.

## Dimensions

Extract these for every paper, in addition to the standard columns. Use `n/a` where a dimension genuinely does not
apply, rather than leaving it blank or guessing.

- **`evidence`** — values: `proven`, `derived`, `empirical`, `fitted`, `position`. What kind of claim the paper's
  central result is:

  - `proven` — a theorem with stated assumptions.
  - `derived` — an approximation or limit argument (mean-field, asymptotic) that is not a proof of the general case.
  - `empirical` — a measured result from experiments.
  - `fitted` — a model fitted to observed data, where the model is the contribution.
  - `position` — a survey, roadmap or position paper with no original result.

  This exists because theory-sounding language is routinely applied to fitted regularities, and a theory group needs to
  know which is which before building on anything.

- **`measures`** — values: `capability`, `faithfulness`, `monitorability`, `control-protocol`, `n/a`. What property the
  paper's headline evaluation actually measures. For safety work the important distinction is `faithfulness` (does the
  stated reasoning reflect the computation that drove the answer, usually tested by injecting a cue) versus
  `monitorability` (can a monitor reading the trace detect a target behaviour). These are constantly conflated,
  including in paper titles. Use `capability` for ordinary performance work, `control-protocol` for protocol-level
  safety evaluations, `n/a` for position papers.

- **`elicitation`** — values: `elicited`, `observational`, `spontaneous`, `n/a`. Whether the behaviour studied was
  `elicited` (the authors deliberately trained, fine-tuned or prompted it in), `observational` (found in an existing
  system the authors did not construct, but with autonomy unverified), or `spontaneous` (arose from ordinary training or
  deployment, with the paper's design able to distinguish that from elicitation). `n/a` where no behaviour is being
  elicited at all.

  This matters for the funding framing above. A capability that has to be trained in is a different risk object from one
  that emerges by itself, and defence questions are almost always about the second.

- **`pressure`** — values: `monitor-in-reward`, `training-incidental`, `prompt-level`, `none`, `n/a`. For any claim that
  a monitor, detector or metric holds up, what kind of pressure it was tested against: `monitor-in-reward` (the monitor
  was folded into the training objective), `training-incidental` (training pressure not aimed at the monitor, e.g. a
  length penalty), `prompt-level` (in-context attack, no training anywhere), or `none` (observational, no pressure
  applied). `n/a` where nothing is being stress-tested.

  Results are routinely quoted across these categories as if comparable. They are not: the most dramatic published
  numbers come from prompt-level attacks, which is the weakest of the three threat models.

# Model collapse

## Topic

Model collapse: what happens when generative models are trained, generation after generation, on data that earlier
generative models produced. I want to understand when the model's distribution degrades (losing its tails, narrowing,
drifting), when it does not, and why. This covers the theory of recursive training, the experiments on language and
image models, and the proposed mitigations, such as keeping real data in the mix, curating or verifying synthetic data,
and detecting generated content before it enters a training set.

## Context

- The field disagrees on whether collapse is inevitable. Two seed papers stand for the two sides: `2305.17493` (the
  "curse of recursion", which argues that collapse follows from recursive training) and `2404.01413` (which argues that
  accumulating synthetic data alongside real data, rather than replacing it, avoids collapse). I want both sides
  represented, and the conditions under which each holds.
- The same phenomenon goes by several names: model collapse, self-consuming generative models, model autophagy, and
  recursive or iterative retraining. Searches should cover all of them.
- An open question I care about: does any of this matter at today's scale, given that web data is only partly generated,
  and is mixed with real data rather than replacing it?

## Coreset Spec

- **`Conditions`** — the conditions under which collapse is claimed to occur, or to be avoided: the data regime, the
  model family and the number of generations. Say what kind of evidence backs each claim.

## Dimensions

Use `n/a` where a dimension genuinely does not apply, rather than leaving it blank or guessing.

- **`evidence`** — values: `proven`, `derived`, `empirical`, or `position`. What kind of claim the paper's central
  result is: `proven` is a theorem with stated assumptions; `derived` is an approximation or limit argument that is not
  a proof of the general case; `empirical` is a measured result from experiments; `position` is a survey or position
  paper with no original result.

- **`regime`** — values: `replace`, `accumulate`, `curated`, `mixed`, or `n/a`. How each generation's training data is
  built, in the paper's main setting: `replace` trains each generation only on the previous one's outputs; `accumulate`
  adds synthetic data to the real data kept from before; `curated` filters, verifies or reweights the synthetic data
  before training; `mixed` compares several of these as its main result. This matters because the two sides of the
  debate mostly study different regimes.

- **`modality`** — values: `text`, `image`, `toy`, `multiple`, or `n/a`. What the main experiments or the theory model:
  `toy` is a simple statistical model such as Gaussians or linear regression, and `multiple` is more than one of the
  others.

## Clustering

- `expect`: mitigations of model collapse
- `exclude`: mode collapse in GANs, a failure within one training run, with no recursion over generations; neural
  collapse, the geometry of last-layer features; synthetic data used once for training, with no recursive loop

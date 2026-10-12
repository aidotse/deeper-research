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

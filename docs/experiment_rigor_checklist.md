# Experiment Rigor Checklist

## Completed In v4

- [x] High-fidelity local MuJoCo simulator benchmark.
- [x] Seven random seeds.
- [x] Five evaluation splits.
- [x] Four iterative acquisition rounds.
- [x] Implemented non-oracle baselines: random, task label, state diversity, uncertainty, active failure prediction.
- [x] Oracle failure-strata upper bound.
- [x] Mean and 95 percent confidence intervals.
- [x] Paired comparisons against the strongest non-oracle baseline.
- [x] Ablations for mechanism clustering, rare reweighting, trace features, uncertainty term, and tail objective.
- [x] Stress sweep over combined-tail severity.
- [x] Negative cases.
- [x] Reproducible CSV outputs and figures.

## Still Missing For ICLR Main

- [ ] Real-robot validation.
- [ ] External public benchmark validation.
- [ ] Independent baseline implementations from prior robot-learning papers.
- [ ] Large-scale learned representation training beyond local logistic classifiers and heuristic selectors.
- [ ] Manual full-paper related-work synthesis.
- [ ] Public videos or hardware traces.

Decision: fail ICLR main empirical-rigor gate because the implemented evidence refutes the central downstream claim.

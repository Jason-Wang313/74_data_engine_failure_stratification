# Novelty Boundary Map

## Crowded Territory

- Active failure prediction for robot policies.
- Uncertainty sampling for data acquisition.
- Task-balanced data engines.
- Diversity coresets over state/action features.
- Failure-mode and effect analysis outside robotics.
- Large robot failure-reasoning datasets.

## Intended Novelty

The intended contribution was to acquire robot data by uncovered physical failure mechanisms, not only by task labels, uncertainty, or generic diversity.

## Actual Boundary After v4 Evidence

The mechanism boundary is not strong enough for ICLR main because the proposed engine loses the downstream robust-success comparison. Rare failure recall improves in some settings, but the action selector does not benefit. The novelty therefore remains an idea seed, not a submission-ready empirical contribution.

## Revival Boundary

Revival would require a new method that converts failure-strata coverage into better control, plus real robot or external benchmark evidence against strong active-learning baselines.

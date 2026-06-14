# Submission Attack Log

## Attack Outcome

The paper does not survive the submission-hardening attack.

## Failed Gate

Required gate: `failure_stratified_engine` must beat the strongest non-oracle baseline on `combined_tail_stress` with a meaningful paired effect while preserving rare recall, macro F1, and safety.

Observed:

- Strongest non-oracle baseline: `failure_prediction_active_learning`.
- Proposed success: 0.643 +/- 0.058.
- Baseline success: 0.675 +/- 0.055.
- Paired success difference: -0.032 +/- 0.047.
- Proposed macro F1: 0.357.
- Baseline macro F1: 0.380.
- Proposed safety violation rate: 0.206.
- Baseline safety violation rate: 0.190.

## Terminal Action

Archive the paper. Do not submit as an ICLR-main paper.

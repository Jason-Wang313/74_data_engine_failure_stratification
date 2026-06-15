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

## 2026-06-15 Continuation Audit

Attack: Rare-failure recall is not enough unless it improves robust selector success while preserving macro-F1 and safety.

Verdict: Fatal. The verified CSVs contain 15,120 rollout-pool rows, 3,780 held-out rollout rows, 1,225 round metric rows, 210 ablation-round rows, and 168 stress raw rows across 7 seeds. On `combined_tail_stress`, `failure_stratified_engine` reaches 0.643 robust success versus 0.675 for `failure_prediction_active_learning`, with paired success difference -0.032 +/- 0.047. It improves paired rare recall by 0.053, but loses macro-F1 by 0.023 and worsens safety by 0.016.

Action: Keep KILL_ARCHIVE and preserve the reproducible negative result without claiming ICLR-main readiness.

# Paper 74 Terminal Audit - 2026-06-21

Paper: `data_engine_failure_stratification`

Decision: `KILL_ARCHIVE`

ICLR-main ready: no

## Verification Performed

1. Source compile gate passed with `python -m py_compile src/run_experiment.py`.
2. Frozen full run completed with empty stderr.
3. CSV integrity and count gates passed through `scripts/validate_submission_artifacts.py`.
4. Evidence scale matched the reported claims:
   - Rollout-pool rows: 31,104
   - Held-out rollout rows: 7,776
   - Round metric rows: 6,480
   - Raw seed metric rows: 1,080
   - Aggregate seed rows: 240
   - Fixed-risk seed rows: 6,600
   - Ablation-round rows: 384
   - Stress raw rows: 336
   - Seeds: 0, 1, 2, 3, 4, 5, 6, 7
5. Baselines were present: random, task-label, coreset, uncertainty, active failure prediction, calibrated failure risk, tail-risk active learning, hybrid diversity-risk, balanced failure replay, gradient-boosted failure active, random-forest failure active, v4, v5, oracle-strata, and oracle-success upper bound.
6. PDF rebuild completed and `C:/Users/wangz/Downloads/74.pdf` was refreshed.
7. Final hard LaTeX scan found no overfull boxes, unresolved citations, undefined references, or rerun warnings.
8. Bright citation boxes are configured with `citebordercolor={0 1 0}` and `pdfborder={0 0 1.6}`.
9. Visual PDF QA inspected representative rendered pages 1, 2, 4, 6, 8, 15, and 25.
10. No visible Desktop copy of `74.pdf` was present after the audit.

## Fatal Evidence

The proposed data engine fails the ICLR-main decision rule. On the hard-regime aggregate, `failure_stratified_engine_v5` reaches 0.467 robust success while `balanced_failure_replay` reaches 0.475. The paired lower bound is not positive (-0.008 +/- 0.016).

The combined/extreme aggregate also fails: v5 reaches 0.528 while `balanced_failure_replay` reaches 0.539, with paired difference -0.012 +/- 0.023.

The fixed-risk gate fails at budget 0.10: v5 reaches 0.021 +/- 0.016 hard-regime success while `random_forest_failure_active` reaches 0.042 +/- 0.022.

The diagnostic gate fails on `combined_tail_stress`: v5 rare recall 0.604 and macro F1 0.337 trail `task_label_stratification` rare recall 0.630 and macro F1 0.343.

The ablation suite undermines the mechanism. Removing every claimed v5 component matches or beats full v5 within the frozen tolerance.

## Decision

Paper 74 remains `KILL_ARCHIVE`. It is a reproducible negative result: failure-stratified acquisition does not produce decisive downstream robust-selection gains under strong baselines, fixed-risk constraints, and ablation-necessity checks.


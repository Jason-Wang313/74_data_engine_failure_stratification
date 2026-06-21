# ICLR Main Gate

Paper: 74 data_engine_failure_stratification

Hardening version: v5 expanded

Gate verdict: KILL_ARCHIVE

Evidence digest: 535eade69162c7f9

## Why It Fails

The v5 expanded rebuild produced real local evidence, but the central claim fails:

- `failure_stratified_engine_v5` reaches 0.467 +/- 0.043 hard-regime robust success.
- The strongest non-oracle hard-regime baseline, `balanced_failure_replay`, reaches 0.475 +/- 0.046.
- The hard-regime paired success difference is -0.008 +/- 0.016 against the proposed method.
- The combined/extreme paired success difference is -0.012 +/- 0.023 against `balanced_failure_replay`.
- The proposed method loses the fixed-risk budget 0.10 gate: 0.021 +/- 0.016 versus 0.042 +/- 0.022 for `random_forest_failure_active`.
- The proposed method trails `task_label_stratification` on combined-tail rare recall and macro F1.
- Ablations do not support the mechanism: removing calibration, diversity, mechanism deficit, rare reweighting, tail risk, trace features, or using the old score matches or beats full v5.

## Remaining Main-Track Blockers

- No real-robot evaluation.
- No external public robotics benchmark validation.
- The proposed data engine does not beat the strongest non-oracle baseline on robust downstream selection.
- Fixed-risk success is worse than a strong tree-based active failure baseline.
- The ablation suite does not identify the claimed v5 components as necessary.
- Prior work on active failure prediction, uncertainty sampling, robot failure reasoning data, and failure-mode stratification leaves little novelty unless the downstream evidence wins.

The only honest main-conference-safe decision is to archive rather than overclaim.

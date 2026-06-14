# ICLR Main Gate

Paper: 74 data_engine_failure_stratification

Hardening version: v4

Gate verdict: KILL_ARCHIVE

Evidence digest: 2f03eac6ae613740

## Why It Fails

The v4 rebuild produced real local evidence, but the central claim fails:

- `failure_stratified_engine` reaches 0.643 +/- 0.058 robust selector success on `combined_tail_stress`.
- The strongest non-oracle baseline, `failure_prediction_active_learning`, reaches 0.675 +/- 0.055.
- The paired success difference is -0.032 +/- 0.047 against the proposed method.
- The proposed method improves rare failure recall over active failure prediction by 0.053, but loses macro failure F1 by 0.023 and worsens safety by 0.016 in paired seed means.
- Ablations do not support the proposed mechanism: removing mechanism clustering or the tail objective reaches 0.675 +/- 0.069 success, above the full failure-stratified variant.

## Remaining Main-Track Blockers

- No real-robot evaluation.
- No external public robotics benchmark validation.
- The proposed data engine does not beat the strongest non-oracle baseline on robust downstream selection.
- Stress sweeps collapse at high stress for all methods, indicating the local benchmark is diagnostic rather than a polished benchmark contribution.
- Prior work on active failure prediction, uncertainty sampling, robot failure reasoning data, and failure-mode stratification leaves little novelty unless the downstream evidence wins.

The only honest main-conference-safe decision is to archive rather than overclaim.

# Final Audit

Paper: 74 data_engine_failure_stratification

Version: v4

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- MuJoCo tabletop data-engine benchmark with physics-derived failure mechanisms.
- Seven seeds: 0 through 6.
- Five splits and four acquisition rounds.
- 15,120 rollout-pool rows.
- 3,780 held-out rollout rows.
- 1,225 round metric rows.
- 245 seed-level metric rows.
- 6 ablation summary rows.
- 168 stress-sweep raw rows.
- 12 negative cases.

## Gate Result

The proposed method fails the decisive gate.

- `failure_stratified_engine`: 0.643 +/- 0.058 combined-tail robust success.
- `failure_prediction_active_learning`: 0.675 +/- 0.055 combined-tail robust success.
- Paired success difference: -0.032 +/- 0.047.
- Paired rare-recall difference: +0.053.
- Paired macro-F1 difference: -0.023.
- Paired safety reduction: -0.016, meaning worse safety.

## Audit Conclusion

The repo is now a real negative-result artifact. It should not be submitted to ICLR main.

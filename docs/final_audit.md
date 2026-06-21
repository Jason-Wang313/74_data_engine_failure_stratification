# Final Audit

Paper: 74 data_engine_failure_stratification

Version: v5 expanded

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- MuJoCo tabletop data-engine benchmark with physics-derived failure mechanisms.
- Eight seeds: 0 through 7.
- Nine evaluation splits and five acquisition rounds.
- Fifteen acquisition methods, including strong CPU-light baselines and oracle diagnostics.
- 31,104 rollout-pool rows.
- 7,776 held-out rollout rows.
- 6,480 round metric rows.
- 1,080 seed-level metric rows.
- 240 aggregate seed rows.
- 6,600 fixed-risk seed rows.
- 384 ablation round rows.
- 336 stress-sweep raw rows.
- 12 negative cases.
- 25-page generated manuscript with bright boxed clickable citations.
- Downloads-only PDF: `C:/Users/wangz/Downloads/74.pdf`.
- PDF SHA256: `535EADE69162C7F949693D9B477570C3AE8ACCC51FC6BD545AD3B38DE568AE57`.

## Gate Result

The proposed method fails the frozen expanded gate.

- Hard-regime aggregate: `failure_stratified_engine_v5` 0.467 +/- 0.043 versus `balanced_failure_replay` 0.475 +/- 0.046.
- Hard-regime paired success difference against `balanced_failure_replay`: -0.008 +/- 0.016.
- Combined/extreme aggregate: v5 0.528 versus `balanced_failure_replay` 0.539.
- Combined/extreme paired success difference: -0.012 +/- 0.023.
- Combined-tail diagnostic gate fails: v5 rare recall 0.604 and macro F1 0.337 trail `task_label_stratification` rare recall 0.630 and macro F1 0.343.
- Fixed-risk hard-regime budget 0.10 fails: v5 0.021 +/- 0.016 versus `random_forest_failure_active` 0.042 +/- 0.022.
- Ablation necessity fails: every v5 ablation matches or beats full v5 within the frozen tolerance.

## Audit Conclusion

The repo is now a stronger negative-result artifact. It should not be submitted to ICLR main. The central failure is not insufficient manuscript polish; it is that mechanism-stratified acquisition does not convert failure-label pressure into better downstream robust selection under hostile baselines and fixed-risk gates.

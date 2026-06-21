# Child Status 74

Current stage: v5 expanded MuJoCo rebuild terminal
Last update: 2026-06-21 13:35:00 +0800
PDF: C:/Users/wangz/Downloads/74.pdf
PDF SHA256: 535EADE69162C7F949693D9B477570C3AE8ACCC51FC6BD545AD3B38DE568AE57
GitHub: https://github.com/Jason-Wang313/74_data_engine_failure_stratification
Submission-hardening version: v5-expanded
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Evidence: frozen 8-seed MuJoCo data-engine benchmark with 31,104 rollout-pool rows, 7,776 held-out rollout rows, 6,480 round metric rows, 6,600 fixed-risk seed rows, 384 ablation rows, and 336 stress rows. `failure_stratified_engine_v5` reaches 0.467 +/- 0.043 hard-regime success, while `balanced_failure_replay` reaches 0.475 +/- 0.046; paired lower bound is not positive (-0.008 +/- 0.016). At fixed-risk budget 0.10, v5 reaches 0.021 +/- 0.016 versus 0.042 +/- 0.022 for `random_forest_failure_active`.

2026-06-21 expanded audit: plan-first protocol, development log, frozen full experiment, generated 25-page manuscript, bright boxed citation settings, clean hard LaTeX scan, visual PDF QA, Downloads-only PDF placement, validation script, and public GitHub target were checked. Decision remains KILL_ARCHIVE because hard-regime, combined/extreme, paired lower-bound, fixed-risk, diagnostic, and ablation-necessity gates fail.

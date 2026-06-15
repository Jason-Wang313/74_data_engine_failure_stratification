# Child Status 74

Current stage: v4 real MuJoCo rebuild terminal
Last update: 2026-06-15 06:50:19 +0100
PDF: C:/Users/wangz/Downloads/74.pdf
GitHub: https://github.com/Jason-Wang313/74_data_engine_failure_stratification
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Evidence: seven-seed MuJoCo data-engine benchmark. `failure_stratified_engine` reaches 0.643 +/- 0.058 combined-tail robust selector success, while `failure_prediction_active_learning` reaches 0.675 +/- 0.055; paired success difference is -0.032 +/- 0.047.

2026-06-15 continuation audit: code compilation, CSV integrity, evidence scale, PDF rebuild, Downloads-only PDF placement, and public GitHub target were rechecked. Decision remains KILL_ARCHIVE because rare-recall gains do not translate into higher robust selector success, macro-F1, or safety.

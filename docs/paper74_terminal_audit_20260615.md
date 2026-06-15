# Paper 74 Terminal Audit - 2026-06-15

Paper: `data_engine_failure_stratification`
Decision: `KILL_ARCHIVE`
ICLR-main ready: no

## Verification Performed

1. Source compile gate passed with `python -m py_compile src/run_experiment.py`.
2. CSV integrity gate passed for all result CSVs: files are present, nonempty, finite, and schema-readable. Blank `failure_labels` values are expected for no-failure cases.
3. Evidence scale matched the reported claims:
   - Rollout-pool rows: 15,120
   - Held-out rollout rows: 3,780
   - Round metric rows: 1,225
   - Ablation-round rows: 210
   - Stress raw rows: 168
   - Seeds: 0, 1, 2, 3, 4, 5, 6
4. Baselines were present: `random_sampling`, `task_label_stratification`, `state_diversity_coreset`, `uncertainty_sampling`, `failure_prediction_active_learning`, and `oracle_failure_strata`.
5. PDF rebuild completed and `C:/Users/wangz/Downloads/74.pdf` was refreshed.
6. No BibTeX sort warnings or unresolved citation/fatal LaTeX errors were present in the final checked logs.
7. No visible Desktop copy of `74.pdf` was present after the audit.

## Fatal Evidence

The proposed data engine fails the ICLR-main decision rule. On `combined_tail_stress`, `failure_stratified_engine` reaches 0.643 robust selector success while `failure_prediction_active_learning` reaches 0.675. The paired failure-stratified-minus-active-learning success difference is -0.032 +/- 0.047.

The main positive signal is rare recall: paired rare-recall difference is +0.053. However, that signal does not rescue the submission claim because macro-F1 is lower by 0.023 and paired safety reduction is -0.016, meaning safety is worse.

The ablation suite also undermines the mechanism. `failure_stratified_full` reaches 0.651 robust success, while removing mechanism clustering or removing the tail objective reaches 0.675.

At stress level 1.00, `failure_stratified_engine` and `failure_prediction_active_learning` both reach 0.014 robust success, so the stress sweep does not provide a hidden win.

## Decision

Paper 74 remains `KILL_ARCHIVE`. It is a reproducible negative result: failure stratification improves one diagnostic but not the decisive downstream selector outcome.

## Revival Requirements

To revive this paper, a future version would need a failure-stratified data engine that decisively beats active failure prediction on robust selector success, while preserving or improving macro-F1, rare recall, and safety under tail stress.


# Paper 74 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15
Paper: 74 - `data_engine_failure_stratification`
Target venue posture: ICLR main only if supported by decisive downstream evidence
Current terminal label entering audit: `KILL_ARCHIVE`

## Goal

Rebuild and audit Paper 74 as a real submission candidate rather than a cosmetic manuscript. The audit must decide whether the MuJoCo data-engine failure-stratification evidence can honestly support an ICLR-main submission, or whether the paper remains a terminal negative result.

## Decision Rule

Upgrade from `KILL_ARCHIVE` only if all of the following are true:

1. `failure_stratified_engine` decisively beats the strongest non-oracle baseline, especially `failure_prediction_active_learning`, on `combined_tail_stress` robust selector success.
2. The paired confidence interval supports a real positive effect rather than a loss or ambiguous tie.
3. Rare-failure recall gains do not come at the cost of macro-F1 or safety.
4. Ablations show mechanism clustering and tail objectives are necessary for downstream success.
5. Stress-sweep results remain favorable under the hardest shifts.
6. The evidence is reproducible from checked-in code, raw CSVs, and a clean PDF build.

If any of these gates fail, preserve `KILL_ARCHIVE` and document the exact failure mode.

## Evidence Gates

Run these checks before changing the decision:

1. Code integrity: compile the experiment source with `python -m py_compile src/run_experiment.py`.
2. Result integrity: verify all required CSVs exist, are nonempty, finite, and schema-valid.
3. Scale check: confirm the recorded evidence includes 15,120 rollout-pool rows, 3,780 held-out rollout rows, 1,225 round metric rows, 210 ablation rows, and 168 stress rows.
4. Baseline check: verify `random_sampling`, `task_label_stratification`, `state_diversity_coreset`, `uncertainty_sampling`, `failure_prediction_active_learning`, and `oracle_failure_strata` are present.
5. Stress check: confirm `combined_tail_stress` and stress-sweep outcomes are represented.
6. Ablation check: confirm whether the full failure-stratified engine beats removed-component variants.
7. Paper build: run LaTeX/BibTeX to produce a clean PDF and copy only the numbered PDF to `C:/Users/wangz/Downloads/74.pdf`.
8. Artifact hygiene: confirm no numbered PDF is copied to the visible Desktop.
9. GitHub hygiene: confirm the matching public GitHub repository exists and the local commit is pushed.
10. Root-report hygiene: update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

## Expected Risk

The existing evidence summary reports that `failure_stratified_engine` reaches 0.643 combined-tail robust success while `failure_prediction_active_learning` reaches 0.675, with paired success difference -0.032 +/- 0.047. The proposed method improves rare recall but loses macro-F1 and safety. Unless direct verification contradicts that result, Paper 74 cannot honestly become submission-ready in this pass.

## Execution Order

1. Re-check repository cleanliness and result inventory.
2. Run code and CSV integrity gates.
3. Rebuild the paper PDF and repair recoverable build warnings.
4. Write a terminal audit with exact evidence and rejection rationale.
5. Update child status, local audit docs, and root reports.
6. Commit and push the Paper 74 repository.
7. Verify `Downloads/74.pdf`, no Desktop copy, public GitHub visibility, clean git state, and root report consistency.


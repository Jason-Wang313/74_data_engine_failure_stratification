# Plan

Rebuild paper 74 `data_engine_failure_stratification` as a real ICLR-main-gated robotics artifact, not a polished template.

## Executed v4 Scope

- Built a MuJoCo tabletop manipulation benchmark with pusher-block contact, fixtures, walls, pocket contact, friction/mass shifts, actuator limits, sensor dropout, and mechanism labels.
- Implemented iterative data-engine acquisition rounds over random sampling, task-label stratification, state-diversity coreset, uncertainty sampling, active failure prediction, the proposed failure-stratified engine, and oracle failure strata.
- Evaluated seven seeds, five splits, four acquisition rounds, paired statistics, ablations, stress sweeps, negative cases, and generated figures.
- Compiled a terminal archive manuscript and canonical PDF to Downloads only.

## Terminal Result

The central submission claim failed. `failure_stratified_engine` does not beat the strongest non-oracle baseline on `combined_tail_stress`; the repository is a reproducible negative-result archive, not an ICLR-main submission.

## 2026-06-15 Continuation Plan

1. Re-audit the real MuJoCo data-engine evidence before making any submission-readiness claim.
2. Confirm the experiment source compiles and all raw CSVs are present, finite, and at the claimed scale.
3. Rebuild the PDF, repair recoverable LaTeX/BibTeX issues, and copy only `74.pdf` to Downloads.
4. Preserve `KILL_ARCHIVE` unless failure stratification decisively beats active failure prediction on robust selector success while preserving macro-F1 and safety.
5. Update child docs, root reports, and GitHub state before moving to Paper 75.

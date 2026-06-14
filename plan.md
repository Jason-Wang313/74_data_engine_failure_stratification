# Plan

Rebuild paper 74 `data_engine_failure_stratification` as a real ICLR-main-gated robotics artifact, not a polished template.

## Executed v4 Scope

- Built a MuJoCo tabletop manipulation benchmark with pusher-block contact, fixtures, walls, pocket contact, friction/mass shifts, actuator limits, sensor dropout, and mechanism labels.
- Implemented iterative data-engine acquisition rounds over random sampling, task-label stratification, state-diversity coreset, uncertainty sampling, active failure prediction, the proposed failure-stratified engine, and oracle failure strata.
- Evaluated seven seeds, five splits, four acquisition rounds, paired statistics, ablations, stress sweeps, negative cases, and generated figures.
- Compiled a terminal archive manuscript and canonical PDF to Downloads only.

## Terminal Result

The central submission claim failed. `failure_stratified_engine` does not beat the strongest non-oracle baseline on `combined_tail_stress`; the repository is a reproducible negative-result archive, not an ICLR-main submission.

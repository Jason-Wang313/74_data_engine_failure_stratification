# Paper 74 Development Log - 2026-06-21

## Context

The v4 paper was already a real MuJoCo negative result, but it was below the expanded submission-hardening standard: fewer pages than requested, a narrower method set, no fixed-risk gate, no hard-regime aggregate, no v5 method-development attempt, and no generated 25+ page manuscript pipeline.

## Changes Made Before Freeze

- Added a plan-first v5 protocol in `docs/paper74_expanded_submission_plan_20260621.md`.
- Expanded default full scale from seven to eight seeds and from four to five acquisition rounds.
- Added four harder evaluation splits:
  - `compound_sensor_actuator_shift`
  - `fixture_geometry_shift`
  - `rare_mechanism_combo`
  - `out_of_distribution_tail`
- Added stronger CPU-light acquisition baselines:
  - `calibrated_failure_risk`
  - `tail_risk_active_learning`
  - `hybrid_diversity_risk`
  - `balanced_failure_replay`
  - `gradient_boosted_failure_active`
  - `random_forest_failure_active`
  - `greedy_oracle_success_upper`
- Added `failure_stratified_engine_v5`, which uses predicted mechanism deficits, rare-failure pressure, observable tail-risk proxy, uncertainty, cluster deficit, diversity, calibration pressure, and predicted failure probability.
- Added hard-regime and combined/extreme aggregate metrics.
- Added fixed-risk success tables at budgets 0.05, 0.10, 0.15, 0.20, and 0.30.
- Added v5 ablations for mechanism deficit, rare reweighting, tail-risk term, calibration term, diversity term, trace features, and old-score fallback.

## Development Probe

A tiny quick-mode probe was run only to catch runtime/schema problems:

```powershell
$env:PAPER74_QUICK='1'
$env:PAPER74_SEED_COUNT='1'
$env:PAPER74_INIT_SCENARIOS='3'
$env:PAPER74_POOL_SCENARIOS='5'
$env:PAPER74_TEST_SCENARIOS='2'
$env:PAPER74_STRESS_SCENARIOS='2'
$env:PAPER74_ROUNDS='1'
$env:PAPER74_BUDGET_PER_ROUND='4'
python src\run_experiment.py
```

Probe result: the runner completed and produced the expanded CSV family. The tiny probe was not used for scientific claims. It did show that the v5 gates correctly kill the method when the hard-regime margin, paired lower bound, and ablation necessity tests fail.

## Freeze Boundary

After this log, no further result-driven method tuning is allowed. The next full run uses the frozen protocol documented in `docs/paper74_protocol_freeze_20260621.md`; any negative outcome must be reported honestly.


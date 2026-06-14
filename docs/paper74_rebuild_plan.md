# Paper 74 Rebuild Plan: Data Engine Failure Stratification

Date: 2026-06-14

## Goal

Rebuild Paper 74 into a real ICLR-main-target robotics submission candidate, or terminate it honestly as `STRONG_REVISE` / `KILL_ARCHIVE` if the evidence does not justify submission. The central question is whether a robot data engine should select new data by uncovered physical failure mechanisms rather than by task labels, random sampling, uncertainty alone, or generic diversity.

## Core Claim To Test

Robot data engines often over-sample easy task labels while under-covering rare physical failure modes such as slip, jamming, actuator saturation, fixture collision, perception dropout, and contact-chain misprediction. A failure-stratified data engine should identify these mechanism strata from rollouts and choose new data that improves tail robustness and failure prediction more than task-balanced or uncertainty-only selection.

## High-Fidelity Benchmark

Build a MuJoCo tabletop manipulation data-engine benchmark with a pusher, movable objects, fixtures, walls, friction/mass shifts, actuator limits, and sensor noise. Generate an initial unlabeled rollout pool plus held-out test suites where each rollout has:

- Task label and environment parameters.
- Success/failure outcome.
- Failure mechanism labels inferred from physics traces: slip, jam, fixture collision, wall collision, actuator saturation, missed contact chain, sensor dropout, and timeout.
- State/action trace summaries, contact graph events, forces/impulses, progress, and safety events.

The experiment should simulate iterative data-engine rounds: choose new rollouts to label/add, train a failure predictor or robust action selector, evaluate held-out tail failures, then repeat.

Evaluation splits:

- `nominal_task_balance`: common task labels with mild shifts.
- `rare_slip_failures`: high friction/mass/contact-noise combinations.
- `jammed_fixture_failures`: fixture geometry creates rare jams.
- `actuator_limit_failures`: low-control authority and heavy objects.
- `combined_tail_stress`: rare failure mechanisms overlap.

## Methods To Implement

- `random_sampling`: uniform data selection from the unlabeled pool.
- `task_label_stratification`: balances by task/environment label only.
- `state_diversity_coreset`: selects diverse state/action embeddings.
- `uncertainty_sampling`: selects high predictive uncertainty examples.
- `failure_prediction_active_learning`: selects examples likely to be failures.
- `failure_stratified_engine`: proposed method; clusters/infer failure mechanisms and balances acquisition across uncovered mechanism strata.
- `oracle_failure_strata`: upper bound with true failure-mechanism labels.

## Metrics

- Held-out task success or robust-selector success.
- Failure-mechanism macro F1.
- Rare failure recall.
- Tail-risk reduction on combined stress.
- Calibration error for failure probabilities.
- Coverage of failure strata after each acquisition round.
- Data efficiency: performance versus number of added rollouts.
- Safety violation rate.

## Experimental Rigor

- Use seven random seeds unless runtime becomes impossible.
- Use multiple acquisition budgets and at least four acquisition rounds.
- Report mean, 95 percent confidence intervals, and paired comparisons against the strongest non-oracle baseline.
- Include ablations: no mechanism clustering, no rare-strata reweighting, no temporal/contact features, no uncertainty term, no safety/tail objective.
- Include stress sweeps over failure rarity, sensor noise, actuator limits, friction/mass shift, and fixture geometry.
- Save raw rollout-pool records, acquisition choices, per-round metrics, per-seed summaries, pairwise statistics, ablations, stress tables, negative cases, and figures.

## Submission Gate

The paper can only move above archive if `failure_stratified_engine` beats the best non-oracle data-selection baseline on `combined_tail_stress` with a meaningful paired effect, improves rare failure recall and macro failure-mechanism F1, and does not worsen safety. If uncertainty sampling, diversity coreset, task-label stratification, or an active failure predictor matches or beats it, the paper remains `KILL_ARCHIVE` or at best `STRONG_REVISE`.

## Deliverables

- Replace the synthetic scaffold with a reproducible MuJoCo failure-data-engine benchmark runner.
- Generate rollout-pool CSVs, acquisition logs, metrics, pairwise statistics, ablations, stress sweeps, negative cases, and figures.
- Rewrite README, claims, novelty boundary, hostile review, reproducibility checklist, final audit, and ICLR gate around actual evidence.
- Rewrite `paper/main.tex` as either a real negative-result paper or a submission-candidate manuscript.
- Compile `paper/main.pdf`, copy exactly to `C:/Users/wangz/Downloads/74.pdf`, and do not copy any PDF to Desktop.
- Commit and push the final Paper 74 repo, then update shared root reports before moving to Paper 75.

## Terminal Outcome

The v4 full run completed on 2026-06-14 with seven seeds, four acquisition rounds, 15,120 rollout-pool rows, and 3,780 held-out rollout rows. The submission gate failed: `failure_stratified_engine` reached 0.643 +/- 0.058 robust success on `combined_tail_stress`, while `failure_prediction_active_learning` reached 0.675 +/- 0.055. The terminal decision is `KILL_ARCHIVE`.

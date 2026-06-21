# 74 Data Engine Failure Stratification

Submission-hardening version: v5 expanded

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository contains the expanded Paper 74 rebuild: a MuJoCo tabletop manipulation data-engine benchmark, 15 acquisition methods, a strengthened `failure_stratified_engine_v5`, strong CPU-light baselines, oracle diagnostics, 8-seed evaluation, 9 splits, uncertainty intervals, paired statistics, hard-regime aggregates, fixed-risk budgets, ablations, stress sweeps, negative cases, generated figures, and a 25-page ICLR-style negative archive manuscript.

The evidence does not support ICLR-main submission. The proposed v5 method does not survive hostile review: hard-regime success is 0.467 versus 0.475 for `balanced_failure_replay`; the hard-regime paired lower bound is not positive (-0.008 +/- 0.016); combined/extreme success is 0.528 versus 0.539 for `balanced_failure_replay`; fixed-risk hard-regime success at budget 0.10 is 0.021 versus 0.042 for `random_forest_failure_active`; combined-tail rare recall and macro F1 trail `task_label_stratification`; and all v5 ablations match or beat full v5 within the frozen tolerance.

## Main Result

Frozen full run:

- Rollout-pool rows: 31,104.
- Held-out rollout rows: 7,776.
- Round metric rows: 6,480.
- Seed-level summary rows: 1,080.
- Aggregate seed rows: 240.
- Fixed-risk seed rows: 6,600.
- Ablation round rows: 384.
- Stress-sweep raw rows: 336.
- Negative cases: 12.
- Seeds: 0 through 7.
- Acquisition rounds: 5.
- Budget per round: 36 rollouts.
- Runtime: 6021.58 seconds.

Hard-regime aggregate:

- `balanced_failure_replay`: 0.475 +/- 0.046 robust success.
- `failure_stratified_engine_v5`: 0.467 +/- 0.043 robust success.
- Paired v5-minus-replay success difference: -0.008 +/- 0.016.

Fixed-risk hard-regime budget 0.10:

- `random_forest_failure_active`: 0.042 +/- 0.022 success at budget.
- `failure_stratified_engine_v5`: 0.021 +/- 0.016 success at budget.

The paper is retained as a reproducible negative-result archive.

## Reproduce

```powershell
python src\run_experiment.py
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Validate artifacts:

```powershell
python scripts\validate_submission_artifacts.py
```

Canonical local PDF: `C:/Users/wangz/Downloads/74.pdf`

PDF SHA256: `535EADE69162C7F949693D9B477570C3AE8ACCC51FC6BD545AD3B38DE568AE57`

No PDF is copied to the visible Desktop.

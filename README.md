# 74 Data Engine Failure Stratification

Submission-hardening version: v4

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository now contains a real Paper 74 rebuild: a MuJoCo tabletop manipulation data-engine benchmark, implemented acquisition baselines, a proposed failure-stratified data engine, oracle failure-strata upper bound, seven-seed evaluation, uncertainty intervals, paired statistics, ablations, stress sweeps, negative cases, figures, and a rewritten archive manuscript.

The evidence does not support ICLR-main submission. On the decisive `combined_tail_stress` split, `failure_stratified_engine` reaches 0.643 +/- 0.058 robust selector success, while the strongest non-oracle baseline, `failure_prediction_active_learning`, reaches 0.675 +/- 0.055. The paired success difference is -0.032 +/- 0.047. Failure stratification improves rare failure recall against that baseline, but loses macro failure F1 and robust downstream selection.

## Main Result

Full run:

- Rollout-pool rows: 15,120.
- Held-out rollout rows: 3,780.
- Round metric rows: 1,225.
- Seed-level summary rows: 245.
- Ablation round rows: 210.
- Stress-sweep raw rows: 168.
- Seeds: 0 through 6.
- Acquisition rounds: 4.
- Budget per round: 32 rollouts.
- Runtime: 4264.02 seconds.

Combined-tail summary:

- `failure_prediction_active_learning`: 0.675 +/- 0.055 robust success, macro F1 0.380, rare recall 0.638.
- `random_sampling`: 0.675 +/- 0.055 robust success, macro F1 0.366, rare recall 0.663.
- `uncertainty_sampling`: 0.675 +/- 0.055 robust success, macro F1 0.372, rare recall 0.687.
- `state_diversity_coreset`: 0.667 +/- 0.067 robust success, macro F1 0.372, rare recall 0.696.
- `task_label_stratification`: 0.659 +/- 0.073 robust success, macro F1 0.360, rare recall 0.648.
- `failure_stratified_engine`: 0.643 +/- 0.058 robust success, macro F1 0.357, rare recall 0.691.

The paper is retained as a reproducible negative-result archive.

## Reproduce

```powershell
python src\run_experiment.py
```

Outputs are written under `results/` and `figures/`.

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/74.pdf`

No PDF is copied to the visible Desktop.

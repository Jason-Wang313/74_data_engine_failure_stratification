# Reproducibility Checklist

## Environment

- Python package requirements are listed in `requirements.txt`.
- Core dependencies: `mujoco`, `numpy`, `matplotlib`, and `scikit-learn`.
- The experiment runner is `src/run_experiment.py`.

## Reproduce Evidence

```powershell
python src\run_experiment.py
```

Expected full-run artifacts:

- `results/rollout_pool.csv`
- `results/heldout_rollouts.csv`
- `results/acquisition_log.csv`
- `results/round_metrics.csv`
- `results/raw_seed_metrics.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep.csv`
- `results/stress_sweep_raw.csv`
- `results/negative_cases.csv`
- `results/training_summary.csv`
- `figures/failure_engine_final_success.png`
- `figures/failure_engine_stress_sweep.png`

## Quick Smoke

```powershell
$env:PAPER74_QUICK='1'
python src\run_experiment.py
```

Unset or set `PAPER74_QUICK=0` for the full seven-seed run.

## PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical PDF: `C:/Users/wangz/Downloads/74.pdf`.

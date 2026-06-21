# Paper 74 Protocol Freeze - 2026-06-21

Paper: `data_engine_failure_stratification`

Protocol status: frozen before the full v5 run.

## Frozen Command

```powershell
Remove-Item Env:PAPER74_QUICK -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_SEED_COUNT -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_INIT_SCENARIOS -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_POOL_SCENARIOS -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_TEST_SCENARIOS -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_STRESS_SCENARIOS -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_ROUNDS -ErrorAction SilentlyContinue
Remove-Item Env:PAPER74_BUDGET_PER_ROUND -ErrorAction SilentlyContinue
python src\run_experiment.py
```

## Frozen Scale

- Seeds: 0 through 7.
- Evaluation splits: 9.
- Policies per scenario: 6.
- Initial scenarios per split: 18.
- Pool scenarios per split: 54.
- Held-out scenarios per split: 18.
- Stress scenarios per seed/level: 10.
- Acquisition rounds: 5.
- Acquisition budget per round: 36.
- Methods: 15.
- Ablation methods: 8.
- Stress methods: 7.
- Fixed-risk budgets: 0.05, 0.10, 0.15, 0.20, 0.30.
- Execution mode: CPU-only, single Python process, `n_jobs=1` for random forest.

## Frozen Decision Gates

The decision is `STRONG_REVISE` only if all of the following pass:

- `failure_stratified_engine_v5` beats the strongest non-oracle baseline by at least 0.04 mean robust success on the hard-regime aggregate.
- The hard-regime paired lower bound against the strongest non-oracle baseline is positive.
- `failure_stratified_engine_v5` beats the strongest non-oracle baseline by at least 0.04 mean robust success on the combined/extreme aggregate.
- The combined/extreme paired lower bound against the strongest non-oracle baseline is positive.
- On `combined_tail_stress`, v5 does not lose rare failure recall or macro failure F1 against the strongest non-oracle robust-success baseline.
- At fixed-risk budget 0.10, v5 has best or tied-best hard-regime success among non-oracle methods.
- No v5 ablation matches or beats full v5 on combined-tail robust success within 0.005.
- At maximum stress, v5 is not more than 0.03 robust-success behind the strongest non-oracle baseline.

If any central gate fails, the terminal decision is `KILL_ARCHIVE`.


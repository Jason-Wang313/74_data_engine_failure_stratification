# Paper 74 Expanded Submission Plan - 2026-06-21

Paper: `data_engine_failure_stratification`

Target: rebuild the paper to the expanded v5 standard before deciding whether it is submission-worthy. The default outcome is not optimism; the outcome is whatever survives hostile review.

## Non-Negotiable Rules

- Do not optimize for pretty results. Optimize for a result that survives hostile review.
- Improve the method during development, then freeze the final protocol and report all predefined results honestly.
- Keep execution CPU-only and RAM-light: single-process full runs, small classical models, no GPU-only dependencies, no large checkpoints, and no uncontrolled parallel fan-out.
- Do not pad the manuscript to reach 25 pages. Page count must come from theory, protocol, baselines, ablations, stress results, negative cases, and reproducibility detail.
- Store the final numbered PDF only at `C:/Users/wangz/Downloads/74.pdf`.
- Do not copy any PDF to the visible Desktop.

## Claim Under Test

The strongest possible version of Paper 74 is:

> A robot data engine should acquire rollouts by uncovered physical failure mechanisms because mechanism coverage gives better tail-robust policy selection than random sampling, task-label balancing, state diversity, uncertainty sampling, active failure prediction, calibrated risk selection, and hybrid diversity-risk baselines.

The v5 paper can only be promoted if this claim wins on downstream robot-selection metrics, not merely on prettier failure-label diagnostics.

## Development Phase

Before freezing, I will improve the proposed method in ways a real author could defend:

- Add a stronger proposed method variant, `failure_stratified_engine_v5`, with explicit mechanism deficits, rare-label reweighting, tail-risk pressure, calibration pressure, and diversity penalties.
- Keep the v4 method as a historical baseline so improvements are measurable.
- Add stronger CPU-light baselines:
  - `calibrated_failure_risk`
  - `tail_risk_active_learning`
  - `hybrid_diversity_risk`
  - `balanced_failure_replay`
  - `greedy_oracle_success_upper`
- Add harder evaluation regimes:
  - existing five splits
  - `compound_sensor_actuator_shift`
  - `fixture_geometry_shift`
  - `rare_mechanism_combo`
  - `out_of_distribution_tail`
- Add fixed-risk analysis: success at safety/failure-risk budgets, not just unconstrained success.
- Add mechanism calibration analysis: macro F1, rare recall, calibration error, and rare-label coverage are all reported.
- Add negative-case mining that compares the proposed method to the strongest baseline and explains when mechanism coverage fails to convert into better action selection.

## Frozen Full Protocol

After development probes, freeze a single full protocol with:

- At least 8 seeds unless a pilot shows runtime is prohibitive; never fewer than the old 7-seed v4 baseline.
- At least 5 acquisition rounds and at least 36 examples per round, unless the dev runtime forces a documented CPU-light adjustment.
- Main method-evaluation rows across all final methods and all evaluation splits.
- Raw acquisition logs for every selected rollout.
- Per-seed, per-method, per-split metrics.
- Pairwise comparisons against the strongest non-oracle baseline selected by frozen rules.
- Ablation rows for the proposed v5 method:
  - no mechanism deficit
  - no rare reweighting
  - no tail-risk term
  - no calibration term
  - no diversity penalty
  - no trace features
- Stress sweep across at least five severity levels, including maximum stress.
- Fixed-risk tables for budgets such as 0.05, 0.10, and 0.15.

## Submission Gates

`STRONG_REVISE` is allowed only if every gate below is satisfied:

- Main hard-regime success: proposed v5 beats the strongest non-oracle baseline by at least 0.04 mean robust success.
- Paired evidence: the paired lower bound against the strongest non-oracle baseline is positive on `combined_tail_stress` and on the aggregate hard regime.
- Fixed-risk evidence: proposed v5 has the best or tied-best success at safety/risk budget 0.10.
- Mechanism evidence: proposed v5 improves rare failure recall without losing macro F1 against the strongest baseline.
- Ablation necessity: removing any claimed core component must not match or beat full v5 on the primary hard-regime success metric.
- Stress robustness: proposed v5 must not collapse earlier than the strongest baseline in maximum-stress analysis.
- Honesty constraints: the paper must disclose no hardware, no public benchmark, no videos, and no large checkpoint validation unless those artifacts actually exist.

If any central gate fails, the final paper remains `KILL_ARCHIVE` even if it has some positive diagnostics.

## Theory Expansion

The manuscript will add a real conceptual section:

- Define failure-stratified acquisition as coverage over latent physical failure mechanisms.
- Explain why mechanism coverage is only useful if the learned selector can exploit it.
- State a failure mode: label-space coverage can be non-causal for downstream action choice when the selector class is misspecified or when rare mechanisms require policies absent from the candidate set.
- Tie empirical gates to this theory: rare recall alone is insufficient; robust downstream success and fixed-risk success are required.

## Manuscript And Citation Requirements

- Generate an expanded ICLR-style manuscript of at least 25 pages, earned by evidence and appendices.
- Use bright boxed clickable citation links through `hyperref` settings, with in-text citations routing to the bibliography.
- Use real references and avoid fake bibliographic entries.
- Include method, theory, benchmark, frozen protocol, main results, paired tests, fixed-risk tests, ablations, stress sweeps, negative cases, limitations, and reproducibility.
- Validate PDF page count, citation/link settings, artifact placement, and root status consistency.

## Deliverables

- Updated runner with frozen v5 experiments.
- Generated result CSVs, tables, figures, summaries, validation script, and audit docs.
- `paper/main.tex`, `paper/references.bib`, and `paper/main.pdf`.
- Final `C:/Users/wangz/Downloads/74.pdf` only.
- Public GitHub repo push.
- Updated root `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, `MASTER_SUBMISSION_REPORT.md`, and `SUBMISSION_AUDIT_MATRIX.csv`.


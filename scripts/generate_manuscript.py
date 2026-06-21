from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"

METHOD_ALIASES = {
    "random_sampling": "random",
    "task_label_stratification": "task-label",
    "state_diversity_coreset": "coreset",
    "uncertainty_sampling": "uncertainty",
    "failure_prediction_active_learning": "fail-active",
    "calibrated_failure_risk": "cal-risk",
    "tail_risk_active_learning": "tail-risk",
    "hybrid_diversity_risk": "hybrid",
    "balanced_failure_replay": "replay",
    "gradient_boosted_failure_active": "hgb-active",
    "random_forest_failure_active": "rf-active",
    "failure_stratified_engine": "fs-v4",
    "failure_stratified_engine_v5": "fs-v5",
    "oracle_failure_strata": "oracle-strata",
    "greedy_oracle_success_upper": "oracle-success",
    "failure_stratified_v5_full": "full-v5",
    "failure_stratified_v5_no_mechanism_deficit": "no-mech-deficit",
    "failure_stratified_v5_no_rare_reweighting": "no-rare",
    "failure_stratified_v5_no_tail_risk": "no-tail",
    "failure_stratified_v5_no_calibration_term": "no-cal",
    "failure_stratified_v5_no_diversity_penalty": "no-diversity",
    "failure_stratified_v5_no_trace_features": "no-trace",
    "failure_stratified_v5_old_score": "old-score",
}

SPLIT_ALIASES = {
    "nominal_task_balance": "nominal",
    "rare_slip_failures": "rare-slip",
    "jammed_fixture_failures": "jammed",
    "actuator_limit_failures": "actuator",
    "combined_tail_stress": "combined",
    "compound_sensor_actuator_shift": "sensor-actuator",
    "fixture_geometry_shift": "fixture-shift",
    "rare_mechanism_combo": "rare-combo",
    "out_of_distribution_tail": "ood-tail",
    "hard_regime": "hard",
    "combined_extreme": "comb/extreme",
}


def read_csv(name: str) -> List[Dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def method_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(METHOD_ALIASES.get(name, name)) + "}"


def split_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(SPLIT_ALIASES.get(name, name)) + "}"


def f(value: str | float, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return tex_escape(value)


def ci95(values: Sequence[float]) -> float:
    if len(values) <= 1:
        return 0.0
    import math

    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return 1.96 * math.sqrt(var) / math.sqrt(len(values))


def pm(row: Dict[str, str], mean_key: str, ci_key: str, digits: int = 3) -> str:
    return f"${f(row[mean_key], digits)} \\pm {f(row[ci_key], digits)}$"


def group_rows(rows: Iterable[Dict[str, str]], fields: Sequence[str]) -> Dict[tuple[str, ...], List[Dict[str, str]]]:
    grouped: Dict[tuple[str, ...], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[field] for field in fields), []).append(row)
    return grouped


def sort_float(rows: Iterable[Dict[str, str]], key: str, reverse: bool = True) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda row: float(row[key]), reverse=reverse)


def summary_fields() -> Dict[str, str]:
    text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    fields = {"summary_text": text}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    return fields


def figure(path: str, caption: str, width: str = "0.95") -> str:
    return "\n".join(
        [
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width={width}\linewidth]{{../figures/{path}}}",
            r"\caption{" + caption + r"}",
            r"\end{figure}",
        ]
    )


def chunked_table(
    caption: str,
    label: str,
    headers: Sequence[str],
    align: str,
    rows: Sequence[Sequence[str]],
    chunk_size: int = 36,
    size: str = r"\scriptsize",
) -> str:
    out: List[str] = [size, r"\setlength{\tabcolsep}{2pt}"]
    for chunk_idx in range(0, len(rows), chunk_size):
        chunk = rows[chunk_idx : chunk_idx + chunk_size]
        out.append(r"\begin{center}")
        if chunk_idx == 0:
            out.append(r"\refstepcounter{table}\label{" + label + r"}\textbf{Table \thetable: " + tex_escape(caption) + r"}\\[0.4ex]")
        else:
            out.append(r"\textbf{Table \ref{" + label + r"} continued}\\[0.4ex]")
        out.append(r"\begin{tabular}{" + align + "}")
        out.append(r"\toprule")
        out.append(" & ".join(headers) + r" \\")
        out.append(r"\midrule")
        for row in chunk:
            out.append(" & ".join(row) + r" \\")
        out.append(r"\bottomrule")
        out.append(r"\end{tabular}")
        out.append(r"\end{center}")
    out.append(r"\normalsize")
    return "\n".join(out)


def write_references() -> None:
    refs = r"""@inproceedings{todorov2012mujoco,
  title={MuJoCo: A physics engine for model-based control},
  author={Todorov, Emanuel and Erez, Tom and Tassa, Yuval},
  booktitle={2012 IEEE/RSJ International Conference on Intelligent Robots and Systems},
  pages={5026--5033},
  year={2012},
  doi={10.1109/IROS.2012.6386109}
}

@techreport{settles2009active,
  title={Active Learning Literature Survey},
  author={Settles, Burr},
  institution={University of Wisconsin--Madison},
  number={1648},
  year={2009},
  url={https://burrsettles.com/pub/settles.activelearning.pdf}
}

@inproceedings{sener2018active,
  title={Active Learning for Convolutional Neural Networks: A Core-Set Approach},
  author={Sener, Ozan and Savarese, Silvio},
  booktitle={International Conference on Learning Representations},
  year={2018},
  url={https://arxiv.org/abs/1708.00489}
}

@article{pedregosa2011scikit,
  title={Scikit-learn: Machine Learning in Python},
  author={Pedregosa, Fabian and Varoquaux, Ga{\"e}l and Gramfort, Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel, Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss, Ron and Dubourg, Vincent and others},
  journal={Journal of Machine Learning Research},
  volume={12},
  pages={2825--2830},
  year={2011},
  url={https://jmlr.org/papers/v12/pedregosa11a.html}
}

@article{breiman2001random,
  title={Random Forests},
  author={Breiman, Leo},
  journal={Machine Learning},
  volume={45},
  number={1},
  pages={5--32},
  year={2001},
  doi={10.1023/A:1010933404324}
}

@article{friedman2001greedy,
  title={Greedy Function Approximation: A Gradient Boosting Machine},
  author={Friedman, Jerome H.},
  journal={The Annals of Statistics},
  volume={29},
  number={5},
  pages={1189--1232},
  year={2001},
  doi={10.1214/aos/1013203451}
}

@article{angelopoulos2021gentle,
  title={A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification},
  author={Angelopoulos, Anastasios N. and Bates, Stephen},
  journal={arXiv preprint arXiv:2107.07511},
  year={2021},
  url={https://arxiv.org/abs/2107.07511}
}

@inproceedings{dasari2020robonet,
  title={RoboNet: Large-Scale Multi-Robot Learning},
  author={Dasari, Sudeep and Ebert, Frederik and Tian, Stephen and Nair, Suraj and Bucher, Bernadette and Schmeckpeper, Karl and Singh, Siddharth and Levine, Sergey and Finn, Chelsea},
  booktitle={Conference on Robot Learning},
  year={2020},
  url={https://arxiv.org/abs/1910.11215}
}

@inproceedings{walke2023bridgedata,
  title={BridgeData V2: A Dataset for Robot Learning at Scale},
  author={Walke, Homer and Black, Kevin and Lee, Abraham and Kim, Moo Jin and Du, Max and Zheng, Chongyi and Zhao, Tony and Hansen-Estruch, Philippe and Vuong, Quan and He, Andre and Myers, Vivek and Fang, Kuan and Finn, Chelsea and Levine, Sergey},
  booktitle={Conference on Robot Learning},
  year={2023},
  url={https://arxiv.org/abs/2308.12952}
}

@article{oneill2023openx,
  title={Open X-Embodiment: Robotic Learning Datasets and RT-X Models},
  author={{Open X-Embodiment Collaboration} and O'Neill, Abby and Rehman, Abdul and Gupta, Abhinav and others},
  journal={arXiv preprint arXiv:2310.08864},
  year={2023},
  url={https://arxiv.org/abs/2310.08864}
}

@inproceedings{khazatsky2024droid,
  title={DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset},
  author={Khazatsky, Alexander and Pertsch, Karl and Nair, Suraj and Balakrishna, Ashwin and Dasari, Sudeep and Karamcheti, Siddharth and others},
  booktitle={Robotics: Science and Systems},
  year={2024},
  url={https://arxiv.org/abs/2403.12945}
}

@article{romer2025fiper,
  title={Failure Prediction at Runtime for Generative Robot Policies},
  author={R{\"o}mer, Ralf and Kobras, Adrian and Worbis, Luca and Schoellig, Angela P.},
  journal={Advances in Neural Information Processing Systems},
  year={2025},
  url={https://arxiv.org/abs/2510.09459}
}

@article{pacaud2025guardian,
  title={Guardian: Detecting Robotic Planning and Execution Errors with Vision-Language Models},
  author={Pacaud, Paul and Garcia, Ricardo and Chen, Shizhe and Schmid, Cordelia},
  journal={arXiv preprint arXiv:2512.01946},
  year={2025},
  url={https://arxiv.org/abs/2512.01946}
}
"""
    (PAPER / "references.bib").write_text(refs, encoding="utf-8")


def main() -> None:
    PAPER.mkdir(exist_ok=True)
    write_references()
    metrics = read_csv("metrics.csv")
    aggregate = read_csv("aggregate_metrics.csv")
    pairwise = read_csv("pairwise_stats.csv")
    aggregate_pairwise = read_csv("aggregate_pairwise_stats.csv")
    fixed = read_csv("fixed_risk_metrics.csv")
    ablation = read_csv("ablation_metrics.csv")
    stress = read_csv("stress_sweep.csv")
    round_metrics = read_csv("round_metrics.csv")
    negatives = read_csv("negative_cases.csv")
    training = read_csv("training_summary.csv")[0]
    fields = summary_fields()
    reason = fields.get("reason", "")

    hard_rows = sort_float([r for r in aggregate if r["split"] == "hard_regime"], "mean_robust_success")
    ce_rows = sort_float([r for r in aggregate if r["split"] == "combined_extreme"], "mean_robust_success")
    combined_rows = sort_float([r for r in metrics if r["split"] == "combined_tail_stress"], "mean_robust_success")
    fixed_hard_010 = sort_float(
        [r for r in fixed if r["split"] == "hard_regime" and r["risk_budget"] == "0.10"],
        "mean_success_at_budget",
    )
    ablation_rows = sort_float(ablation, "mean_robust_success")
    max_stress = sort_float([r for r in stress if r["stress_level"] == "1.00"], "mean_robust_success")

    def result_rows(rows: Sequence[Dict[str, str]]) -> List[List[str]]:
        return [
            [
                method_tex(r["method"]),
                pm(r, "mean_robust_success", "ci95_robust_success"),
                f(r["mean_failure_macro_f1"]),
                f(r["mean_rare_failure_recall"]),
                f(r["mean_tail_risk"]),
                f(r["mean_safety_violation_rate"]),
            ]
            for r in rows
        ]

    intro_tables = [
        chunked_table(
            "Hard-regime aggregate. This is the primary frozen gate: the proposed v5 method must beat the strongest non-oracle baseline by at least 0.04 robust success and have a positive paired lower bound.",
            "tab:hard",
            ["Method", "Success", "Macro F1", "Rare recall", "Tail", "Safety"],
            "lccccc",
            result_rows(hard_rows),
            chunk_size=20,
        ),
        chunked_table(
            "Combined/extreme aggregate. This tests whether the mechanism-stratified engine is useful when rare failure modes overlap.",
            "tab:ce",
            ["Method", "Success", "Macro F1", "Rare recall", "Tail", "Safety"],
            "lccccc",
            result_rows(ce_rows),
            chunk_size=20,
        ),
        chunked_table(
            "Fixed-risk hard-regime success at budget 0.10. Abstentions count as failures; high coverage is useful only if selected actions remain successful.",
            "tab:fixed010",
            ["Method", "Success@0.10", "Coverage", "Safety", "Tail"],
            "lcccc",
            [
                [
                    method_tex(r["method"]),
                    pm(r, "mean_success_at_budget", "ci95_success_at_budget"),
                    f(r["mean_coverage_at_budget"]),
                    f(r["mean_safety_at_budget"]),
                    f(r["mean_tail_at_budget"]),
                ]
                for r in fixed_hard_010
            ],
            chunk_size=20,
        ),
        chunked_table(
            "Combined-tail split. This split alone would make v5 look somewhat better on success, but the diagnostic and aggregate gates prevent overclaiming.",
            "tab:combined",
            ["Method", "Success", "Macro F1", "Rare recall", "Tail", "Safety"],
            "lccccc",
            result_rows(combined_rows),
            chunk_size=20,
        ),
        chunked_table(
            "V5 ablations on combined-tail stress. The full method must not be matched by removing claimed core components.",
            "tab:ablation",
            ["Ablation", "Success", "Macro F1", "Rare recall", "Tail", "Safety"],
            "lccccc",
            result_rows(ablation_rows),
            chunk_size=20,
        ),
        chunked_table(
            "Maximum-stress comparison at severity 1.00.",
            "tab:maxstress",
            ["Method", "Success", "Macro F1", "Rare recall", "Tail", "Safety"],
            "lccccc",
            result_rows(max_stress),
            chunk_size=20,
        ),
    ]

    full_metric_rows = [
        [
            method_tex(r["method"]),
            split_tex(r["split"]),
            pm(r, "mean_robust_success", "ci95_robust_success"),
            f(r["mean_failure_macro_f1"]),
            f(r["mean_rare_failure_recall"]),
            f(r["mean_tail_risk"]),
            f(r["mean_calibration_error"]),
            f(r["mean_safety_violation_rate"]),
        ]
        for r in sort_float(metrics, "mean_robust_success")
    ]
    pairwise_rows = [
        [
            split_tex(r["split"]),
            method_tex(r["comparison"]),
            f(r["paired_success_diff"]),
            f(r["ci95_success_diff"]),
            f(r["paired_macro_f1_diff"]),
            f(r["paired_rare_recall_diff"]),
            f(r["paired_safety_reduction"]),
            tex_escape(r["reference_better_seeds"]),
        ]
        for r in pairwise
    ]
    aggregate_pairwise_rows = [
        [
            split_tex(r["split"]),
            method_tex(r["comparison"]),
            f(r["paired_success_diff"]),
            f(r["ci95_success_diff"]),
            f(r["paired_macro_f1_diff"]),
            f(r["paired_rare_recall_diff"]),
            f(r["paired_safety_reduction"]),
            tex_escape(r["reference_better_seeds"]),
        ]
        for r in aggregate_pairwise
    ]
    fixed_rows = [
        [
            method_tex(r["method"]),
            split_tex(r["split"]),
            tex_escape(r["risk_budget"]),
            pm(r, "mean_success_at_budget", "ci95_success_at_budget"),
            f(r["mean_coverage_at_budget"]),
            f(r["mean_safety_at_budget"]),
            f(r["mean_tail_at_budget"]),
        ]
        for r in fixed
    ]
    stress_rows = [
        [
            method_tex(r["method"]),
            tex_escape(r["stress_level"]),
            pm(r, "mean_robust_success", "ci95_robust_success"),
            f(r["mean_failure_macro_f1"]),
            f(r["mean_rare_failure_recall"]),
            f(r["mean_tail_risk"]),
            f(r["mean_safety_violation_rate"]),
        ]
        for r in stress
    ]
    round_combined_summary: List[Dict[str, str]] = []
    for (method, round_idx), rows in sorted(group_rows([r for r in round_metrics if r["split"] == "combined_tail_stress"], ["method", "round"]).items()):
        success_vals = [float(r["robust_success"]) for r in rows]
        rare_vals = [float(r["rare_failure_recall"]) for r in rows]
        coverage_vals = [float(r["failure_coverage"]) for r in rows]
        round_combined_summary.append(
            {
                "method": method,
                "round": round_idx,
                "mean_robust_success": f"{sum(success_vals) / len(success_vals):.5f}",
                "ci95_robust_success": f"{ci95(success_vals):.5f}",
                "mean_rare_failure_recall": f"{sum(rare_vals) / len(rare_vals):.5f}",
                "ci95_rare_failure_recall": f"{ci95(rare_vals):.5f}",
                "mean_failure_coverage": f"{sum(coverage_vals) / len(coverage_vals):.5f}",
                "ci95_failure_coverage": f"{ci95(coverage_vals):.5f}",
            }
        )
    round_table_rows = [
        [
            method_tex(r["method"]),
            tex_escape(r["round"]),
            pm(r, "mean_robust_success", "ci95_robust_success"),
            pm(r, "mean_rare_failure_recall", "ci95_rare_failure_recall"),
            pm(r, "mean_failure_coverage", "ci95_failure_coverage"),
        ]
        for r in round_combined_summary
    ]
    negative_rows = [
        [
            tex_escape(r.get("seed", "")),
            tex_escape(r.get("scenario_id", "").replace("test_combined_tail_stress_", "cts_")),
            r"\texttt{" + tex_escape(r.get("chosen_policy", "").replace("friction_probe", "fric-probe").replace("_", "-")) + "}",
            tex_escape(r.get("failure_labels", "").replace(";", ", ")),
            f(r.get("final_progress", "0")),
            f(r.get("safety_violation", "0")),
            tex_escape("coverage pressure did not convert to safe selection"),
        ]
        for r in negatives
    ]
    neg_table = chunked_table(
        "Representative negative cases mined from the frozen v5 run.",
        "tab:negcases",
        ["Seed", "Scenario", "Policy", "Failures", "Progress", "Safety", "Lesson"],
        r"p{0.035\linewidth}p{0.13\linewidth}p{0.12\linewidth}p{0.23\linewidth}p{0.055\linewidth}p{0.045\linewidth}p{0.21\linewidth}",
        negative_rows,
        chunk_size=12,
        size=r"\tiny",
    )
    all_metrics_table = chunked_table(
        "All method/split summary rows from the frozen v5 run.",
        "tab:allmetrics",
        ["Method", "Split", "Success", "Macro F1", "Rare recall", "Tail", "Calib", "Safety"],
        "llcccccc",
        full_metric_rows,
        chunk_size=34,
        size=r"\tiny",
    )
    pairwise_table = chunked_table(
        "Per-split paired comparisons. Positive success differences favor fs-v5.",
        "tab:pairwise",
        ["Split", "Comparison", "Succ diff", "CI", "Macro diff", "Rare diff", "Safety red.", "Better seeds"],
        "llcccccc",
        pairwise_rows,
        chunk_size=36,
        size=r"\tiny",
    )
    aggregate_pairwise_table = chunked_table(
        "Aggregate paired comparisons. These rows drive the hard-regime and combined/extreme lower-bound gates.",
        "tab:aggpair",
        ["Split", "Comparison", "Succ diff", "CI", "Macro diff", "Rare diff", "Safety red.", "Better seeds"],
        "llcccccc",
        aggregate_pairwise_rows,
        chunk_size=36,
        size=r"\tiny",
    )
    fixed_table = chunked_table(
        "All fixed-risk summaries over all splits, aggregate splits, and risk budgets.",
        "tab:fixedall",
        ["Method", "Split", "Budget", "Success", "Coverage", "Safety", "Tail"],
        "lllcccc",
        fixed_rows,
        chunk_size=42,
        size=r"\tiny",
    )
    stress_table = chunked_table(
        "All stress-sweep summary rows.",
        "tab:stressall",
        ["Method", "Stress", "Success", "Macro F1", "Rare recall", "Tail", "Safety"],
        "llccccc",
        stress_rows,
        chunk_size=42,
        size=r"\tiny",
    )
    round_table = chunked_table(
        "Combined-tail acquisition learning curves by round. These rows report data efficiency rather than final-only performance.",
        "tab:roundcombined",
        ["Method", "Round", "Success", "Rare recall", "Coverage"],
        "llccc",
        round_table_rows,
        chunk_size=30,
        size=r"\tiny",
    )

    tex = rf"""\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\input{{math_commands.tex}}
\usepackage{{amsmath,amssymb,amsthm}}
\usepackage{{hyperref}}
\usepackage{{url}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{microtype}}
\hypersetup{{colorlinks=false,citebordercolor={{0 1 0}},linkbordercolor={{1 .45 0}},urlbordercolor={{0 .65 1}},pdfborder={{0 0 1.6}}}}
\newtheorem{{proposition}}{{Proposition}}
\newtheorem{{theorem}}{{Theorem}}
\title{{Failure-Stratified Robot Data Engines Fail a Hard-Regime Acquisition Audit}}
\author{{Anonymous Authors}}
\begin{{document}}
\maketitle

\begin{{abstract}}
We rebuild \emph{{Data Engine Failure Stratification}} as an adversarial robot-data acquisition audit. The strongest version of the claim is that acquiring new rollouts by uncovered physical failure mechanisms should improve tail-robust policy selection beyond random sampling, task balancing, coreset diversity, uncertainty sampling, active failure prediction, calibrated risk selection, tree-based failure acquisition, and hybrid diversity-risk baselines. We implement a MuJoCo tabletop manipulation benchmark with {tex_escape(fields.get("rollout_pool_rows", ""))} rollout-pool rows, {tex_escape(fields.get("heldout_rollout_rows", ""))} held-out rollout rows, {tex_escape(fields.get("round_metric_rows", ""))} per-round metric rows, {tex_escape(fields.get("ablation_rows", ""))} ablation rows, {tex_escape(fields.get("stress_rows", ""))} stress rows, 9 evaluation splits, 15 acquisition methods, 8 seeds, fixed-risk gates, paired comparisons, and negative-case mining. The frozen decision is \textbf{{KILL\_ARCHIVE}}. On the hard-regime aggregate, \texttt{{fs-v5}} reaches 0.467 success while \texttt{{replay}} reaches 0.475; the paired lower bound is not positive. At fixed-risk budget 0.10, \texttt{{fs-v5}} reaches 0.021 success while \texttt{{rf-active}} reaches 0.042. We report the negative result rather than polishing an unsupported submission story.
\end{{abstract}}

\section{{Decision Discipline}}
This manuscript is written as a submission-readiness audit, not a success narrative. The paper can only be promoted if mechanism-stratified acquisition improves downstream action selection under hostile baselines and stress tests. The recorded terminal reason is:

\begin{{quote}}\small
{tex_escape(reason)}
\end{{quote}}

The result is still useful: it shows that better pressure on failure mechanisms can fail to improve the robot decision that matters. This is the exact failure mode a hostile reviewer would ask about.

\section{{Problem Setup}}
We use MuJoCo contact dynamics \citep{{todorov2012mujoco}} to construct a planar pushing data-engine task. Each scenario has a pusher, movable block, pocket, walls, and a fixture. Policies differ in how they approach the block: center pushing, angle compensation, slow safe pushing, aggressive pushing, fixture avoidance, and friction probing. Rollouts vary friction, mass, actuator authority, sensor dropout, noise, block position, pocket offset, and fixture geometry.

For scenario $i$ and candidate policy $a \in \mathcal{{A}}$, the simulator returns success $Y_{{i,a}}$, safety violation $S_{{i,a}}$, tail risk $T_{{i,a}}$, and a multi-label failure vector
\[
  z_{{i,a}} \in \{{0,1\}}^8
\]
covering slip, jam, fixture collision, wall collision, actuator saturation, missed contact, sensor dropout, and timeout. A data engine observes an initial labeled set $D_0$, chooses batches $B_t$ from a rollout pool, trains a failure predictor, and is evaluated by a robust selector that chooses the candidate policy with lowest predicted failure probability on held-out scenarios.

\section{{Why Mechanism Coverage Can Fail}}
Failure stratification sounds intuitively right: if the robot has not seen jams, slips, or actuator-limit failures, it should acquire more of them. The audit tests whether that intuition survives the selector bottleneck.

\begin{{proposition}}[Failure-label coverage is not sufficient]
There exist two acquisition policies $q_1$ and $q_2$ such that $q_1$ covers every failure mechanism at least as often as $q_2$, but the robust selector trained on $q_1$ has lower held-out success.
\end{{proposition}}
\begin{{proof}}[Sketch]
Let the candidate policy set omit the action needed to recover from one rare mechanism. Acquiring more examples of that mechanism can improve its label recall while leaving the selector unable to choose a successful policy. If $q_2$ acquires fewer rare labels but better calibrates the failure probability on selectable actions, $q_2$ can have higher downstream success. Thus label coverage does not imply control utility.
\end{{proof}}

\begin{{proposition}}[Active failure prediction is a hard baseline]
If downstream selection uses predicted failure probability, then an acquisition policy that directly samples high predicted-failure and high-uncertainty points can dominate mechanism balancing whenever the mechanism model is misspecified.
\end{{proposition}}
\begin{{proof}}[Sketch]
Mechanism balancing estimates an intermediate vector $z$ and uses it to choose data. Active failure prediction targets the scalar loss used by the selector. Under misspecification, the intermediate estimate can be higher variance or non-causal for action choice, while direct failure acquisition reduces error in the selector's objective.
\end{{proof}}

\begin{{theorem}}[Ablation necessity gate]
If removing a proposed component leaves success within $\epsilon$ of full v5 and does not worsen the frozen safety diagnostics, the experiment does not identify that component as necessary for the claimed mechanism.
\end{{theorem}}
\begin{{proof}}[Sketch]
The full and ablated systems are evaluated under the same seeded simulator and held-out splits. If the ablation is practically indistinguishable on the primary downstream metric, the data are compatible with the component being irrelevant. A submission claim of necessity would therefore overstate the evidence.
\end{{proof}}

\section{{Related Work Pressure}}
The benchmark sits between active learning and robot-data curation. General active learning already motivates uncertainty and high-risk example selection \citep{{settles2009active}}, while coreset active learning makes diversity a strong batch-selection baseline \citep{{sener2018active}}. Our classical implementations use scikit-learn \citep{{pedregosa2011scikit}}, random forests \citep{{breiman2001random}}, and gradient boosting \citep{{friedman2001greedy}}; the fixed-risk analysis is motivated by calibrated and distribution-free uncertainty ideas \citep{{angelopoulos2021gentle}}. Large robot-data efforts such as RoboNet, BridgeData V2, Open X-Embodiment, and DROID show that robot learning increasingly depends on data scale and data diversity \citep{{dasari2020robonet,walke2023bridgedata,oneill2023openx,khazatsky2024droid}}. Recent robot failure-prediction and failure-reasoning work makes the baseline pressure sharper: if direct failure prediction or failure-data synthesis already targets deployment risk, a new failure-stratified engine needs downstream evidence, not just prettier labels \citep{{romer2025fiper,pacaud2025guardian}}.

\section{{Methods}}
The audit includes 15 acquisition strategies. \texttt{{random}} samples uniformly. \texttt{{task-label}} balances the task/split label. \texttt{{coreset}} uses state/trace diversity. \texttt{{uncertainty}} selects near the failure classifier's decision boundary. \texttt{{fail-active}} chooses high predicted failure plus uncertainty. \texttt{{cal-risk}} adds calibration pressure. \texttt{{tail-risk}} emphasizes observable tail-risk parameters. \texttt{{hybrid}} mixes predicted failure, uncertainty, tail risk, and diversity. \texttt{{replay}} balances predicted under-covered failure mechanisms without the v5 cluster machinery. \texttt{{hgb-active}} and \texttt{{rf-active}} use stronger tree-based failure acquisition. \texttt{{fs-v4}} is the historical failure-stratified engine. \texttt{{fs-v5}} is the improved proposed method. \texttt{{oracle-strata}} and \texttt{{oracle-success}} are upper-bound diagnostics and are never counted as non-oracle baselines.

\section{{Frozen Protocol}}
The protocol was frozen before the full run: seeds 0--7, 9 splits, 18 initial scenarios per split, 54 pool scenarios per split, 18 held-out scenarios per split, 5 acquisition rounds, budget 36 per round, 15 methods, 8 v5 ablations, 7 stress methods, and stress levels 0.00--1.00. The run is CPU-only and single-process. The training summary records {tex_escape(training.get("seed_count", ""))} seeds, {tex_escape(training.get("methods", ""))} methods, {tex_escape(training.get("ablation_methods", ""))} ablations, {tex_escape(training.get("stress_methods", ""))} stress methods, and {tex_escape(training.get("sim_steps_per_rollout", ""))} simulator steps per rollout.

\section{{Main Results}}
The hard-regime aggregate is decisive because it averages the splits most likely to reveal deployment failure: combined tail stress, compound sensor/actuator shift, fixture geometry shift, rare mechanism combinations, and out-of-distribution tail cases. Table~\ref{{tab:hard}} shows that \texttt{{fs-v5}} does not beat the strongest non-oracle baseline. Table~\ref{{tab:ce}} repeats the result on the combined/extreme aggregate.

{intro_tables[0]}

{intro_tables[1]}

{figure("failure_engine_final_success.png", "Combined-tail success by final method. The split alone would allow a tempting positive story, but the aggregate, fixed-risk, diagnostic, and ablation gates reject that story.")}

\section{{Fixed-Risk Evaluation}}
In a deployment-facing data engine, high success is less useful if the selector only succeeds by taking unbounded predicted risk. Table~\ref{{tab:fixed010}} counts abstentions as failures under a strict risk budget of 0.10. The proposed v5 method is not best; \texttt{{rf-active}} and \texttt{{tail-risk}} have higher hard-regime fixed-risk success.

{intro_tables[2]}

\section{{Combined-Tail Split}}
Table~\ref{{tab:combined}} is the split most favorable to the proposed method: \texttt{{fs-v5}} ties \texttt{{fs-v4}} at 0.688 success and is above many non-oracle baselines on success. The gate still fails because the rare-recall and macro-F1 diagnostics are not better than \texttt{{task-label}}, and the broader hard-regime aggregate trails \texttt{{replay}}.

{intro_tables[3]}

\section{{Ablation Results}}
Table~\ref{{tab:ablation}} is the most damaging mechanistic evidence. Removing calibration, diversity, mechanism deficit, rare weighting, tail risk, trace features, or reverting to the old score matches or beats full v5 within the frozen tolerance. That means the claimed v5 components are not identified as necessary.

{intro_tables[4]}

{figure("failure_engine_ablation_success.png", "Ablation success on combined-tail stress. Full v5 is not protected by its claimed components.")}

\section{{Data Efficiency}}
Acquisition papers should not only report the final point after a large budget. We therefore also inspect round-by-round performance on the combined-tail split. Figure~\ref{{fig:roundsuccess}} and Figure~\ref{{fig:roundrare}} show that the proposed method does not produce a clean data-efficiency separation: rare recall moves, but downstream success remains largely tied with strong non-oracle selectors. The full per-round table appears in Appendix~\ref{{sec:roundappendix}}.

\begin{{figure}}[t]
\centering
\includegraphics[width=0.92\linewidth]{{../figures/failure_engine_success_by_round.png}}
\caption{{Combined-tail robust success by acquisition round.}}
\label{{fig:roundsuccess}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\includegraphics[width=0.92\linewidth]{{../figures/failure_engine_rare_recall_by_round.png}}
\caption{{Combined-tail rare failure recall by acquisition round.}}
\label{{fig:roundrare}}
\end{{figure}}

\section{{Stress Sweep}}
The stress sweep tests whether the proposed engine collapses later than strong baselines as severity increases. Table~\ref{{tab:maxstress}} reports the maximum-stress endpoint. The proposed method is not meaningfully ahead of the strongest non-oracle method.

{intro_tables[5]}

{figure("failure_engine_stress_sweep.png", "Stress sweep over combined-tail severity. The proposed method does not establish a robust maximum-stress advantage.")}

\section{{Negative Cases}}
Negative cases show the selector-level failure mode: the data engine may acquire or predict rare mechanisms, yet the trained robust selector still chooses a tail-risk policy. This is not a formatting problem; it is a scientific failure of the central mechanism-to-control link.

{neg_table}

\section{{Limitations}}
This is not a hardware paper. It has no real-robot validation, no videos, no external public benchmark run, and no large policy checkpoint. Those missing pieces would keep even a positive result at \texttt{{STRONG\_REVISE}} rather than main-conference ready. Because the central frozen gates fail, the honest decision is lower: \texttt{{KILL\_ARCHIVE}}.

\section{{Conclusion}}
The expanded v5 audit gives Paper 74 every reasonable local chance: more splits, more baselines, a stronger proposed method, hard-regime aggregates, fixed-risk selection, ablations, stress sweeps, and a full appendix. The result remains negative. Failure stratification is not enough unless mechanism coverage changes the action selector's downstream decisions under the hard regimes reviewers will care about.

\appendix
\section{{Complete Main Metrics}}
{all_metrics_table}

\section{{Pairwise Comparisons Against \texttt{{fs-v5}}}}
{pairwise_table}

\section{{Aggregate Pairwise Comparisons}}
{aggregate_pairwise_table}

\section{{Fixed-Risk Appendix}}
{fixed_table}

\section{{Stress Appendix}}
{stress_table}

\section{{Per-Round Data-Efficiency Appendix}}\label{{sec:roundappendix}}
{round_table}

\bibliographystyle{{iclr2026_conference}}
\bibliography{{references}}

\end{{document}}
"""
    tex = re.sub(r"\n{3,}", "\n\n", tex)
    (PAPER / "main.tex").write_text(tex, encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'}")


if __name__ == "__main__":
    main()

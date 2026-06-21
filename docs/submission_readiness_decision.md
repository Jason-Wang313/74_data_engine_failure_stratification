# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Reason: The v5 expanded rebuild provides real local MuJoCo evidence, but the evidence refutes the main claim under hostile-review gates. `failure_stratified_engine_v5` does not beat the strongest non-oracle baseline on hard-regime or combined/extreme aggregates, has non-positive paired lower bounds, loses the fixed-risk budget 0.10 gate, trails `task_label_stratification` on combined-tail rare recall and macro F1, and is not supported by ablations.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: a substantially stronger method that converts failure-strata coverage into downstream selector gains under hard-regime aggregate, fixed-risk, ablation-necessity, and external/hardware validation gates.

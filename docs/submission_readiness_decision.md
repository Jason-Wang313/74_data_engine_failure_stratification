# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Reason: The v4 rebuild provides real local MuJoCo evidence, but the evidence refutes the main claim. `failure_stratified_engine` does not beat `failure_prediction_active_learning` on combined-tail robust selector success and is worse on macro failure F1 and safety.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: a substantially stronger method that converts failure-strata coverage into downstream control gains, validated on real robots or external high-fidelity benchmarks.

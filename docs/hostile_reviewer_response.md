# Hostile Reviewer Response

## Reviewer Claim

Failure stratification is just active failure prediction with a more complicated acquisition heuristic. Unless it improves downstream selection, the mechanism language is decorative.

## Evidence-Based Response

The hostile reviewer is right for this rebuild. The proposed `failure_stratified_engine` does not beat `failure_prediction_active_learning` on the decisive `combined_tail_stress` metric. It reaches 0.643 +/- 0.058 robust success versus 0.675 +/- 0.055 for active failure prediction, with paired success difference -0.032 +/- 0.047.

## Reviewer Claim

Rare failure recall is not enough if the policy selector still fails.

## Evidence-Based Response

Also correct. The proposed engine improves paired rare recall by 0.053 against active failure prediction, but loses macro F1 by 0.023 and worsens paired safety by 0.016. The added mechanism coverage does not convert into robust action selection.

## Reviewer Claim

The ablations should show that mechanism clustering and tail objectives matter.

## Evidence-Based Response

They do not. Removing mechanism clustering or removing the tail objective reaches 0.675 +/- 0.069 robust success, above the full ablated failure-stratified variant at 0.651 +/- 0.103. This undermines the proposed mechanism.

## Terminal Response

We accept the rejection. The correct action is archive, not rhetorical strengthening.

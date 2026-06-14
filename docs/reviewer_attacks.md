# Reviewer Attacks

## Attack 1: The Main Metric Is Lost

The proposed method loses combined-tail robust success to active failure prediction: 0.643 +/- 0.058 versus 0.675 +/- 0.055.

Answer: accept. This is fatal for ICLR main.

## Attack 2: Rare Recall Is A Proxy

The method improves rare recall but not control.

Answer: accept. Proxy metric gains are not enough.

## Attack 3: Ablations Refute The Mechanism

Removing mechanism clustering and removing the tail objective both match or exceed the full method in robust success.

Answer: accept. The mechanism is not validated.

## Attack 4: The Benchmark Is Local

The evidence is MuJoCo-only and lacks external benchmark or real-robot validation.

Answer: accept. Even a positive local result would need more validation; the result is negative.

## Attack 5: Prior Work Is Crowded

Failure prediction, uncertainty sampling, and failure-mode analysis already exist.

Answer: accept. Without a downstream win, the novelty boundary is insufficient.

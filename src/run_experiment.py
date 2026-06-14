from __future__ import annotations

import csv
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, recall_score
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler


BASE_SEED = 1211606508
QUICK_MODE = os.getenv("PAPER74_QUICK", "0") == "1"
SEED_COUNT = int(os.getenv("PAPER74_SEED_COUNT", "1" if QUICK_MODE else "7"))
SEEDS = list(range(SEED_COUNT))
INIT_SCENARIOS = int(os.getenv("PAPER74_INIT_SCENARIOS", "6" if QUICK_MODE else "18"))
POOL_SCENARIOS = int(os.getenv("PAPER74_POOL_SCENARIOS", "10" if QUICK_MODE else "54"))
TEST_SCENARIOS = int(os.getenv("PAPER74_TEST_SCENARIOS", "5" if QUICK_MODE else "18"))
STRESS_SCENARIOS = int(os.getenv("PAPER74_STRESS_SCENARIOS", "4" if QUICK_MODE else "10"))
ROUNDS = int(os.getenv("PAPER74_ROUNDS", "2" if QUICK_MODE else "4"))
BUDGET_PER_ROUND = int(os.getenv("PAPER74_BUDGET_PER_ROUND", "10" if QUICK_MODE else "32"))
STEPS = 54
DT = 0.025

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

FAILURES = [
    "slip",
    "jam",
    "fixture_collision",
    "wall_collision",
    "actuator_saturation",
    "missed_contact",
    "sensor_dropout",
    "timeout",
]
RARE_FAILURES = ["slip", "jam", "fixture_collision", "actuator_saturation", "sensor_dropout"]

METHODS = [
    "random_sampling",
    "task_label_stratification",
    "state_diversity_coreset",
    "uncertainty_sampling",
    "failure_prediction_active_learning",
    "failure_stratified_engine",
    "oracle_failure_strata",
]

ABLATION_METHODS = [
    "failure_stratified_full",
    "failure_stratified_no_mechanism_clustering",
    "failure_stratified_no_rare_reweighting",
    "failure_stratified_no_trace_features",
    "failure_stratified_no_uncertainty_term",
    "failure_stratified_no_tail_objective",
]

STRESS_METHODS = [
    "uncertainty_sampling",
    "failure_prediction_active_learning",
    "failure_stratified_engine",
    "oracle_failure_strata",
]

POLICIES = [
    "center_push",
    "angle_compensated",
    "slow_safe",
    "aggressive",
    "fixture_avoid",
    "friction_probe",
]

MODEL_XML = """
<mujoco model="data_engine_failure_stratification">
  <compiler angle="radian"/>
  <option timestep="0.025" gravity="0 0 0" integrator="implicitfast"/>
  <default>
    <joint damping="0.16"/>
    <geom solref="0.012 1" solimp="0.90 0.95 0.001" friction="0.68 0.08 0.02"/>
  </default>
  <worldbody>
    <geom name="floor" type="plane" pos="0 0 -0.02" size="1.0 1.0 0.02"
          contype="0" conaffinity="0" rgba="0.90 0.89 0.84 1"/>
    <geom name="top_wall" type="box" pos="0 0.46 0.035" size="0.62 0.018 0.07"
          rgba="0.30 0.34 0.36 1"/>
    <geom name="bottom_wall" type="box" pos="0 -0.46 0.035" size="0.62 0.018 0.07"
          rgba="0.30 0.34 0.36 1"/>
    <geom name="pocket_back" type="box" pos="0.42 0 0.035" size="0.018 0.16 0.07"
          rgba="0.20 0.42 0.32 1"/>
    <geom name="fixture_post" type="box" pos="0.12 0.18 0.035" size="0.040 0.085 0.07"
          rgba="0.52 0.31 0.18 1"/>
    <body name="pusher" pos="0 0 0.035">
      <joint name="pusher_x" type="slide" axis="1 0 0" range="-0.55 0.52" damping="0.18"/>
      <joint name="pusher_y" type="slide" axis="0 1 0" range="-0.43 0.43" damping="0.18"/>
      <geom name="pusher_tip" type="sphere" size="0.035" mass="0.45" rgba="0.05 0.05 0.06 1"/>
    </body>
    <body name="block" pos="0 0 0.035">
      <joint name="block_x" type="slide" axis="1 0 0" range="-0.46 0.43" damping="0.12"/>
      <joint name="block_y" type="slide" axis="0 1 0" range="-0.41 0.41" damping="0.12"/>
      <geom name="block_geom" type="box" size="0.060 0.055 0.035" mass="0.38" rgba="0.72 0.16 0.12 1"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="pusher_x_motor" joint="pusher_x" gear="1" ctrllimited="true" ctrlrange="-38 38"/>
    <motor name="pusher_y_motor" joint="pusher_y" gear="1" ctrllimited="true" ctrlrange="-38 38"/>
  </actuator>
</mujoco>
"""


@dataclass(frozen=True)
class SplitSpec:
    name: str
    task_id: int
    block_y: float
    pocket_y: float
    fixture_x: float
    fixture_y: float
    friction: float
    mass_scale: float
    actuator_limit: float
    sensor_dropout: float
    noise: float
    failure_rarity: float


@dataclass(frozen=True)
class RolloutConfig:
    split: SplitSpec
    seed: int
    scenario: int
    policy: str
    pusher: Tuple[float, float]
    block: Tuple[float, float]
    pocket: Tuple[float, float]
    fixture: Tuple[float, float]
    friction: float
    mass_scale: float
    actuator_limit: float
    sensor_dropout: float
    noise: float
    stress_level: float | None = None


@dataclass
class RolloutRecord:
    row_id: str
    split: str
    scenario_id: str
    seed: int
    scenario: int
    policy: str
    task_id: int
    success: int
    failures: np.ndarray
    pre_features: np.ndarray
    trace_features: np.ndarray
    feature_names_pre: List[str]
    feature_names_trace: List[str]
    final_progress: float
    safety_violation: float
    tail_risk: float
    trajectory: str


@dataclass
class BinaryModel:
    scaler: StandardScaler | None
    model: LogisticRegression | None
    constant: float | None


SPLITS = [
    SplitSpec("nominal_task_balance", 0, 0.00, 0.00, 0.18, 0.28, 0.58, 1.00, 1.00, 0.03, 0.006, 0.10),
    SplitSpec("rare_slip_failures", 1, 0.06, -0.03, 0.18, 0.25, 0.95, 1.20, 0.88, 0.06, 0.010, 0.45),
    SplitSpec("jammed_fixture_failures", 2, 0.07, -0.05, 0.10, 0.08, 0.70, 1.25, 0.86, 0.05, 0.010, 0.55),
    SplitSpec("actuator_limit_failures", 3, -0.02, 0.03, 0.16, -0.24, 0.72, 1.70, 0.58, 0.06, 0.012, 0.58),
    SplitSpec("combined_tail_stress", 4, 0.075, -0.065, 0.12, 0.20, 0.94, 1.45, 0.68, 0.14, 0.014, 0.80),
]
SPLIT_BY_NAME = {s.name: s for s in SPLITS}
POLICY_INDEX = {p: i for i, p in enumerate(POLICIES)}


def ci95(values: Sequence[float]) -> float:
    vals = np.array(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * np.std(vals, ddof=1) / math.sqrt(len(vals)))


def make_model() -> mujoco.MjModel:
    return mujoco.MjModel.from_xml_string(MODEL_XML)


def geom_id(model: mujoco.MjModel, name: str) -> int:
    return mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, name)


def body_id(model: mujoco.MjModel, name: str) -> int:
    return mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)


def configure_model(model: mujoco.MjModel, cfg: RolloutConfig) -> None:
    for geom_name in ["pusher_tip", "block_geom", "top_wall", "bottom_wall", "pocket_back", "fixture_post"]:
        gid = geom_id(model, geom_name)
        model.geom_friction[gid, 0] = cfg.friction
    model.body_mass[body_id(model, "block")] = 0.38 * cfg.mass_scale
    model.geom_pos[geom_id(model, "pocket_back"), :2] = np.array([cfg.pocket[0], cfg.pocket[1]], dtype=float)
    model.geom_pos[geom_id(model, "fixture_post"), :2] = np.array([cfg.fixture[0], cfg.fixture[1]], dtype=float)


def reset_data(model: mujoco.MjModel, cfg: RolloutConfig) -> mujoco.MjData:
    configure_model(model, cfg)
    data = mujoco.MjData(model)
    data.qpos[:4] = np.array([cfg.pusher[0], cfg.pusher[1], cfg.block[0], cfg.block[1]], dtype=float)
    data.qvel[:4] = 0.0
    mujoco.mj_forward(model, data)
    return data


def config_rng(seed: int, scenario: int, split_name: str, purpose: str) -> np.random.Generator:
    offset = sum((i + 5) * ord(c) for i, c in enumerate(f"{split_name}_{purpose}"))
    return np.random.default_rng(BASE_SEED + 65537 * seed + 313 * scenario + offset)


def make_config(split: SplitSpec, seed: int, scenario: int, policy: str, purpose: str = "pool", stress_level: float | None = None) -> RolloutConfig:
    rng = config_rng(seed, scenario, split.name if stress_level is None else f"{split.name}_{stress_level:.2f}", purpose)
    if stress_level is None:
        rarity = split.failure_rarity
        block_y = split.block_y + rng.normal(0.0, 0.020 + 0.010 * rarity)
        pocket_y = split.pocket_y + rng.normal(0.0, 0.016 + 0.006 * rarity)
        fixture = (
            split.fixture_x + rng.normal(0.0, 0.012),
            split.fixture_y + rng.normal(0.0, 0.018 + 0.010 * rarity),
        )
        friction = split.friction * rng.normal(1.0, 0.055 + 0.020 * rarity)
        mass_scale = split.mass_scale * rng.normal(1.0, 0.050 + 0.020 * rarity)
        actuator_limit = split.actuator_limit * rng.normal(1.0, 0.035)
        sensor_dropout = split.sensor_dropout
        noise = split.noise
    else:
        rarity = float(stress_level)
        block_y = rng.normal(0.0, 0.020) + 0.090 * stress_level
        pocket_y = rng.normal(0.0, 0.018) - 0.080 * stress_level
        fixture = (
            0.18 - 0.095 * stress_level + rng.normal(0.0, 0.014),
            0.25 - 0.20 * stress_level + rng.normal(0.0, 0.020),
        )
        friction = 0.58 + 0.42 * stress_level + rng.normal(0.0, 0.025)
        mass_scale = 1.0 + 0.85 * stress_level + rng.normal(0.0, 0.045)
        actuator_limit = 1.0 - 0.43 * stress_level + rng.normal(0.0, 0.025)
        sensor_dropout = 0.03 + 0.18 * stress_level
        noise = 0.006 + 0.014 * stress_level
    block = (-0.13 + rng.normal(0.0, 0.014), float(np.clip(block_y, -0.34, 0.34)))
    pusher = (-0.42 + rng.normal(0.0, 0.010), float(np.clip(block[1] + rng.normal(0.0, 0.030), -0.35, 0.35)))
    return RolloutConfig(
        split=split,
        seed=seed,
        scenario=scenario,
        policy=policy,
        pusher=pusher,
        block=block,
        pocket=(0.42, float(np.clip(pocket_y, -0.23, 0.23))),
        fixture=(float(np.clip(fixture[0], -0.05, 0.25)), float(np.clip(fixture[1], -0.33, 0.33))),
        friction=float(np.clip(friction, 0.35, 1.25)),
        mass_scale=float(np.clip(mass_scale, 0.70, 2.25)),
        actuator_limit=float(np.clip(actuator_limit, 0.45, 1.25)),
        sensor_dropout=float(np.clip(sensor_dropout, 0.0, 0.38)),
        noise=float(noise),
        stress_level=stress_level,
    )


def contact_flags(model: mujoco.MjModel, data: mujoco.MjData) -> Dict[str, int]:
    flags = {"pusher_block": 0, "block_fixture": 0, "block_wall": 0, "block_pocket": 0}
    for idx in range(data.ncon):
        c = data.contact[idx]
        n1 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, c.geom1)
        n2 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, c.geom2)
        pair = frozenset([n1, n2])
        if pair == frozenset(["pusher_tip", "block_geom"]):
            flags["pusher_block"] = 1
        if pair == frozenset(["block_geom", "fixture_post"]):
            flags["block_fixture"] = 1
        if pair in {frozenset(["block_geom", "top_wall"]), frozenset(["block_geom", "bottom_wall"])}:
            flags["block_wall"] = 1
        if pair == frozenset(["block_geom", "pocket_back"]):
            flags["block_pocket"] = 1
    return flags


def policy_target(policy: str, step: int, data: mujoco.MjData, cfg: RolloutConfig, observed_block: np.ndarray) -> Tuple[np.ndarray, float]:
    pusher = np.array(data.qpos[:2], dtype=float)
    block = observed_block
    pocket = np.array(cfg.pocket, dtype=float)
    fixture = np.array(cfg.fixture, dtype=float)
    behind = block + np.array([-0.078, 0.0])
    if policy == "center_push":
        target_y = 0.75 * block[1] + 0.25 * pocket[1]
        gain = 1.0
    elif policy == "angle_compensated":
        target_y = block[1] + 0.55 * (pocket[1] - block[1])
        gain = 1.05
    elif policy == "slow_safe":
        target_y = block[1] + 0.70 * (pocket[1] - block[1])
        gain = 0.72
    elif policy == "aggressive":
        target_y = block[1] + 0.18 * (pocket[1] - block[1])
        gain = 1.35
    elif policy == "fixture_avoid":
        away = -np.sign(fixture[1] - block[1]) * 0.060
        target_y = block[1] + 0.50 * (pocket[1] - block[1]) + away
        gain = 0.95
    elif policy == "friction_probe":
        target_y = block[1] + 0.45 * (pocket[1] - block[1])
        gain = 0.45 if step < 14 else 1.05
    else:
        target_y = block[1]
        gain = 1.0
    if pusher[0] < block[0] - 0.070:
        target = np.array([behind[0], target_y], dtype=float)
    else:
        target = np.array([pocket[0] + 0.015, target_y], dtype=float)
    return target, gain


def pre_feature_vector(cfg: RolloutConfig) -> Tuple[np.ndarray, List[str]]:
    policy_onehot = np.zeros(len(POLICIES), dtype=float)
    policy_onehot[POLICY_INDEX[cfg.policy]] = 1.0
    names = [
        "task_id",
        "block_x",
        "block_y",
        "pocket_y",
        "fixture_x",
        "fixture_y",
        "friction",
        "mass_scale",
        "actuator_limit",
        "sensor_dropout",
        "noise",
        "failure_rarity",
    ] + [f"policy_{p}" for p in POLICIES]
    vals = np.array(
        [
            cfg.split.task_id,
            cfg.block[0],
            cfg.block[1],
            cfg.pocket[1],
            cfg.fixture[0],
            cfg.fixture[1],
            cfg.friction,
            cfg.mass_scale,
            cfg.actuator_limit,
            cfg.sensor_dropout,
            cfg.noise,
            cfg.split.failure_rarity if cfg.stress_level is None else cfg.stress_level,
        ],
        dtype=float,
    )
    return np.concatenate([vals, policy_onehot]), names


def simulate_rollout(model: mujoco.MjModel, cfg: RolloutConfig, row_id: str, scenario_id: str) -> RolloutRecord:
    rng = config_rng(cfg.seed, cfg.scenario, cfg.split.name, cfg.policy)
    data = reset_data(model, cfg)
    pusher_block_steps = 0
    fixture_steps = 0
    wall_steps = 0
    pocket_steps = 0
    saturation_steps = 0
    dropout_steps = 0
    high_slip_steps = 0
    energy = 0.0
    max_abs_y = abs(cfg.block[1])
    max_block_speed = 0.0
    max_lateral_speed = 0.0
    last_progress = 0.0
    stagnation_steps = 0
    samples: List[str] = []
    stale_block = np.array(cfg.block, dtype=float)
    for step in range(STEPS):
        true_block = np.array(data.qpos[2:4], dtype=float)
        if rng.random() < cfg.sensor_dropout:
            observed_block = stale_block
            dropout_steps += 1
        else:
            observed_block = true_block + rng.normal(0.0, cfg.noise, size=2)
            stale_block = observed_block.copy()
        target, gain = policy_target(cfg.policy, step, data, cfg, observed_block)
        pusher = np.array(data.qpos[:2], dtype=float)
        pvel = np.array(data.qvel[:2], dtype=float)
        ctrl = gain * (70.0 * (target - pusher) - 9.0 * pvel)
        ctrl += np.array([8.0 * gain, 0.0])
        limit = 38.0 * cfg.actuator_limit
        clipped = np.clip(ctrl, -limit, limit)
        if np.any(np.abs(ctrl) > limit * 0.98):
            saturation_steps += 1
        data.ctrl[:2] = clipped
        before_vel = np.array(data.qvel[:2], dtype=float)
        mujoco.mj_step(model, data)
        data.qpos[:] = np.clip(data.qpos[:], [-0.55, -0.43, -0.46, -0.41], [0.52, 0.43, 0.43, 0.41])
        data.qvel[:] = np.clip(data.qvel[:], -1.8, 1.8)
        mujoco.mj_forward(model, data)
        flags = contact_flags(model, data)
        pusher_block_steps += flags["pusher_block"]
        fixture_steps += flags["block_fixture"]
        wall_steps += flags["block_wall"]
        pocket_steps += flags["block_pocket"]
        block = np.array(data.qpos[2:4], dtype=float)
        block_vel = np.array(data.qvel[2:4], dtype=float)
        max_abs_y = max(max_abs_y, abs(float(block[1])))
        max_block_speed = max(max_block_speed, float(np.linalg.norm(block_vel)))
        max_lateral_speed = max(max_lateral_speed, abs(float(block_vel[1])))
        if flags["pusher_block"] and abs(block_vel[1]) > 0.28:
            high_slip_steps += 1
        progress = float(np.clip((block[0] - cfg.block[0]) / max(0.08, cfg.pocket[0] - cfg.block[0]), 0.0, 1.30))
        if progress - last_progress < 0.0015 and (flags["block_fixture"] or flags["block_wall"]) and step > 10:
            stagnation_steps += 1
        last_progress = progress
        energy += float(np.sum(np.abs(clipped * before_vel)) * DT)
        if step % 11 == 0 or step == STEPS - 1:
            active = ",".join(k for k, v in flags.items() if v) or "none"
            samples.append(f"{step}:b({block[0]:.3f},{block[1]:.3f}):p{progress:.2f}:c[{active}]")
    block = np.array(data.qpos[2:4], dtype=float)
    final_progress = float(np.clip((block[0] - cfg.block[0]) / max(0.08, cfg.pocket[0] - cfg.block[0]), 0.0, 1.30))
    y_error = float(abs(block[1] - cfg.pocket[1]))
    contact_rate = pusher_block_steps / STEPS
    fixture_rate = fixture_steps / STEPS
    wall_rate = wall_steps / STEPS
    pocket_rate = pocket_steps / STEPS
    saturation_rate = saturation_steps / STEPS
    dropout_rate = dropout_steps / STEPS
    slip_rate = high_slip_steps / max(1, pusher_block_steps)
    jam_rate = stagnation_steps / STEPS
    safety = float(fixture_rate > 0.20 or wall_rate > 0.18 or max_abs_y > 0.405)
    success = int(final_progress > 0.82 and y_error < 0.12 and pocket_rate > 0.04 and fixture_rate < 0.30 and wall_rate < 0.25)
    failures = np.array(
        [
            slip_rate > 0.22 or max_lateral_speed > 0.55,
            jam_rate > 0.08,
            fixture_rate > 0.12,
            wall_rate > 0.10,
            saturation_rate > 0.30,
            contact_rate < 0.12,
            dropout_rate > 0.16 and (success == 0 or y_error > 0.16),
            success == 0 and final_progress < 0.80,
        ],
        dtype=int,
    )
    if success == 0 and not failures.any():
        failures[-1] = 1
    trace_names = [
        "final_progress",
        "y_error",
        "contact_rate",
        "fixture_rate",
        "wall_rate",
        "pocket_rate",
        "saturation_rate",
        "dropout_rate",
        "slip_rate",
        "jam_rate",
        "max_abs_y",
        "max_block_speed",
        "max_lateral_speed",
        "energy",
        "safety_violation",
    ]
    trace_features = np.array(
        [
            final_progress,
            y_error,
            contact_rate,
            fixture_rate,
            wall_rate,
            pocket_rate,
            saturation_rate,
            dropout_rate,
            slip_rate,
            jam_rate,
            max_abs_y,
            max_block_speed,
            max_lateral_speed,
            energy,
            safety,
        ],
        dtype=float,
    )
    pre, pre_names = pre_feature_vector(cfg)
    tail_risk = float((success == 0) or fixture_rate > 0.12 or wall_rate > 0.10 or saturation_rate > 0.35)
    return RolloutRecord(
        row_id=row_id,
        split=cfg.split.name,
        scenario_id=scenario_id,
        seed=cfg.seed,
        scenario=cfg.scenario,
        policy=cfg.policy,
        task_id=cfg.split.task_id,
        success=success,
        failures=failures,
        pre_features=pre,
        trace_features=trace_features,
        feature_names_pre=pre_names,
        feature_names_trace=trace_names,
        final_progress=final_progress,
        safety_violation=safety,
        tail_risk=tail_risk,
        trajectory=";".join(samples),
    )


def generate_records_for_split(model: mujoco.MjModel, split: SplitSpec, seed: int, start_scenario: int, count: int, purpose: str, stress_level: float | None = None) -> List[RolloutRecord]:
    rows: List[RolloutRecord] = []
    for local_idx in range(count):
        scenario = start_scenario + local_idx
        scenario_id = f"{purpose}_{split.name}_{seed}_{scenario}"
        for policy in POLICIES:
            cfg = make_config(split, seed, scenario, policy, purpose=purpose, stress_level=stress_level)
            row_id = f"{scenario_id}_{policy}"
            rows.append(simulate_rollout(model, cfg, row_id, scenario_id))
    return rows


def generate_seed_dataset(seed: int) -> Tuple[List[RolloutRecord], List[RolloutRecord], Dict[str, List[RolloutRecord]]]:
    model = make_model()
    init_rows: List[RolloutRecord] = []
    pool_rows: List[RolloutRecord] = []
    test_by_split: Dict[str, List[RolloutRecord]] = {}
    scenario_offset = 0
    for split in SPLITS:
        init_rows.extend(generate_records_for_split(model, split, seed, scenario_offset, INIT_SCENARIOS, "init"))
        scenario_offset += INIT_SCENARIOS + 5
        pool_rows.extend(generate_records_for_split(model, split, seed, scenario_offset, POOL_SCENARIOS, "pool"))
        scenario_offset += POOL_SCENARIOS + 5
        test_by_split[split.name] = generate_records_for_split(model, split, seed, scenario_offset, TEST_SCENARIOS, "test")
        scenario_offset += TEST_SCENARIOS + 50
    return init_rows, pool_rows, test_by_split


def feature_matrix(rows: Sequence[RolloutRecord], use_trace: bool = False) -> np.ndarray:
    if use_trace:
        return np.vstack([np.concatenate([r.pre_features, r.trace_features]) for r in rows])
    return np.vstack([r.pre_features for r in rows])


def labels_success(rows: Sequence[RolloutRecord]) -> np.ndarray:
    return np.array([r.success for r in rows], dtype=int)


def labels_failures(rows: Sequence[RolloutRecord]) -> np.ndarray:
    return np.vstack([r.failures for r in rows]).astype(int)


def fit_binary(x: np.ndarray, y: np.ndarray) -> BinaryModel:
    if len(np.unique(y)) < 2:
        return BinaryModel(scaler=None, model=None, constant=float(np.mean(y)))
    scaler = StandardScaler().fit(x)
    model = LogisticRegression(max_iter=260, class_weight="balanced", C=1.0)
    model.fit(scaler.transform(x), y)
    return BinaryModel(scaler=scaler, model=model, constant=None)


def predict_binary(model: BinaryModel, x: np.ndarray) -> np.ndarray:
    if model.constant is not None or model.model is None or model.scaler is None:
        return np.ones(len(x), dtype=float) * float(model.constant or 0.0)
    return model.model.predict_proba(model.scaler.transform(x))[:, 1]


def fit_failure_models(rows: Sequence[RolloutRecord]) -> Tuple[BinaryModel, List[BinaryModel]]:
    x = feature_matrix(rows, use_trace=False)
    success = labels_success(rows)
    failure_model = fit_binary(x, 1 - success)
    failure_labels = labels_failures(rows)
    mechanism_models = [fit_binary(x, failure_labels[:, idx]) for idx in range(failure_labels.shape[1])]
    return failure_model, mechanism_models


def predict_mechanisms(models: List[BinaryModel], x: np.ndarray) -> np.ndarray:
    probs = np.vstack([predict_binary(model, x) for model in models]).T
    return probs


def calibration_error(probs: np.ndarray, labels: np.ndarray, bins: int = 8) -> float:
    probs = np.asarray(probs, dtype=float)
    labels = np.asarray(labels, dtype=float)
    total = len(labels)
    if total == 0:
        return 0.0
    err = 0.0
    for lo in np.linspace(0.0, 1.0, bins, endpoint=False):
        hi = lo + 1.0 / bins
        mask = (probs >= lo) & (probs < hi if hi < 1.0 else probs <= hi)
        if np.any(mask):
            err += float(np.sum(mask) / total) * abs(float(np.mean(probs[mask])) - float(np.mean(labels[mask])))
    return err


def robust_selector_success(rows: Sequence[RolloutRecord], failure_model: BinaryModel) -> Tuple[float, float, float]:
    by_scenario: Dict[str, List[RolloutRecord]] = {}
    for row in rows:
        by_scenario.setdefault(row.scenario_id, []).append(row)
    successes: List[float] = []
    safeties: List[float] = []
    tail_risks: List[float] = []
    for group in by_scenario.values():
        x = feature_matrix(group, use_trace=False)
        failure_probs = predict_binary(failure_model, x)
        chosen = group[int(np.argmin(failure_probs))]
        successes.append(float(chosen.success))
        safeties.append(float(chosen.safety_violation))
        tail_risks.append(float(chosen.tail_risk))
    return float(np.mean(successes)), float(np.mean(safeties)), float(np.mean(tail_risks))


def evaluate_rows(rows: Sequence[RolloutRecord], selected: Sequence[RolloutRecord]) -> Dict[str, float]:
    failure_model, mechanism_models = fit_failure_models(selected)
    x = feature_matrix(rows, use_trace=False)
    y_fail = 1 - labels_success(rows)
    fail_probs = predict_binary(failure_model, x)
    mech_probs = predict_mechanisms(mechanism_models, x)
    mech_pred = (mech_probs >= 0.5).astype(int)
    mech_true = labels_failures(rows)
    macro_f1 = float(f1_score(mech_true, mech_pred, average="macro", zero_division=0))
    rare_idx = [FAILURES.index(name) for name in RARE_FAILURES]
    rare_recall = float(recall_score(mech_true[:, rare_idx], mech_pred[:, rare_idx], average="macro", zero_division=0))
    robust_success, safety_rate, tail_risk = robust_selector_success(rows, failure_model)
    return {
        "robust_success": robust_success,
        "failure_macro_f1": macro_f1,
        "rare_failure_recall": rare_recall,
        "tail_risk": tail_risk,
        "calibration_error": calibration_error(fail_probs, y_fail),
        "safety_violation_rate": safety_rate,
    }


def failure_coverage(rows: Sequence[RolloutRecord]) -> float:
    labels = labels_failures(rows)
    return float(np.mean(np.sum(labels, axis=0) > 0))


def choose_batch(method: str, selected: List[int], pool: List[RolloutRecord], budget: int, rng: np.random.Generator, ablation: str | None = None) -> List[int]:
    remaining = [idx for idx in range(len(pool)) if idx not in selected]
    if len(remaining) <= budget:
        return remaining
    selected_rows = [pool[idx] for idx in selected]
    remaining_rows = [pool[idx] for idx in remaining]
    if method == "random_sampling":
        return list(rng.choice(remaining, size=budget, replace=False))
    if method == "task_label_stratification":
        counts = {task: sum(1 for idx in selected if pool[idx].task_id == task) for task in range(len(SPLITS))}
        chosen: List[int] = []
        for _ in range(budget):
            rem = [idx for idx in remaining if idx not in chosen]
            target_task = min(counts, key=counts.get)
            candidates = [idx for idx in rem if pool[idx].task_id == target_task] or rem
            pick = int(rng.choice(candidates))
            chosen.append(pick)
            counts[pool[pick].task_id] += 1
        return chosen
    if method == "state_diversity_coreset":
        x_pool = feature_matrix(pool, use_trace=True)
        scaler = StandardScaler().fit(x_pool)
        xs = scaler.transform(x_pool)
        chosen: List[int] = []
        current = selected.copy()
        for _ in range(budget):
            rem = [idx for idx in remaining if idx not in chosen]
            if current:
                d = euclidean_distances(xs[rem], xs[current]).min(axis=1)
                pick = rem[int(np.argmax(d))]
            else:
                pick = int(rng.choice(rem))
            chosen.append(pick)
            current.append(pick)
        return chosen
    if not selected_rows:
        return list(rng.choice(remaining, size=budget, replace=False))
    failure_model, mechanism_models = fit_failure_models(selected_rows)
    x_rem_pre = feature_matrix(remaining_rows, use_trace=False)
    fail_probs = predict_binary(failure_model, x_rem_pre)
    uncertainty = 1.0 - np.abs(fail_probs - 0.5) * 2.0
    if method == "uncertainty_sampling" or ablation == "failure_stratified_no_mechanism_clustering":
        order = np.argsort(-uncertainty)
        return [remaining[int(i)] for i in order[:budget]]
    if method == "failure_prediction_active_learning":
        score = fail_probs + 0.20 * uncertainty
        order = np.argsort(-score)
        return [remaining[int(i)] for i in order[:budget]]
    if method == "oracle_failure_strata":
        counts = np.sum(labels_failures(selected_rows), axis=0)
        chosen: List[int] = []
        for _ in range(budget):
            rem = [idx for idx in remaining if idx not in chosen]
            desired = int(np.argmin(counts))
            candidates = [idx for idx in rem if pool[idx].failures[desired] == 1] or rem
            scores = np.array([1.0 + 0.4 * np.sum(pool[idx].failures) + pool[idx].tail_risk for idx in candidates])
            pick = candidates[int(np.argmax(scores))]
            chosen.append(pick)
            counts += pool[pick].failures
        return chosen
    if method == "failure_stratified_engine":
        use_trace = ablation != "failure_stratified_no_trace_features"
        x_all = feature_matrix(pool, use_trace=use_trace)
        scaler = StandardScaler().fit(x_all)
        xs_all = scaler.transform(x_all)
        k = min(9, max(3, len(pool) // 45))
        km = KMeans(n_clusters=k, random_state=BASE_SEED + len(selected), n_init=6)
        clusters = km.fit_predict(xs_all)
        selected_counts = np.bincount(clusters[selected], minlength=k) if selected else np.zeros(k)
        rem_clusters = clusters[remaining]
        mech_probs = predict_mechanisms(mechanism_models, x_rem_pre)
        rare_score = np.mean(mech_probs[:, [FAILURES.index(name) for name in RARE_FAILURES]], axis=1)
        tail_bonus = np.array([row.tail_risk for row in remaining_rows], dtype=float)
        cluster_need = 1.0 / (1.0 + selected_counts[rem_clusters])
        if ablation == "failure_stratified_no_rare_reweighting":
            rare_score[:] = np.mean(mech_probs, axis=1)
        if ablation == "failure_stratified_no_uncertainty_term":
            uncertainty[:] = 0.0
        if ablation == "failure_stratified_no_tail_objective":
            tail_bonus[:] = 0.0
        score = 0.45 * cluster_need + 0.32 * rare_score + 0.17 * uncertainty + 0.22 * tail_bonus
        order = np.argsort(-score)
        return [remaining[int(i)] for i in order[:budget]]
    return list(rng.choice(remaining, size=budget, replace=False))


def run_acquisition_method(
    method: str,
    init_rows: List[RolloutRecord],
    pool_rows: List[RolloutRecord],
    test_by_split: Dict[str, List[RolloutRecord]],
    seed: int,
    ablation: str | None = None,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[int]]:
    rng = np.random.default_rng(BASE_SEED + 1009 * seed + sum(ord(c) for c in method))
    selected = list(range(len(init_rows)))
    pool = init_rows + pool_rows
    round_rows: List[Dict[str, str]] = []
    acquisition_rows: List[Dict[str, str]] = []
    for round_idx in range(ROUNDS + 1):
        selected_rows = [pool[idx] for idx in selected]
        for split, test_rows in test_by_split.items():
            metrics = evaluate_rows(test_rows, selected_rows)
            round_rows.append(
                {
                    "method": method if ablation is None else ablation,
                    "seed": str(seed),
                    "round": str(round_idx),
                    "split": split,
                    "selected_examples": str(len(selected_rows)),
                    "failure_coverage": f"{failure_coverage(selected_rows):.5f}",
                    **{k: f"{v:.5f}" for k, v in metrics.items()},
                }
            )
        if round_idx == ROUNDS:
            break
        batch = choose_batch(method, selected, pool, BUDGET_PER_ROUND, rng, ablation=ablation)
        for rank, idx in enumerate(batch):
            row = pool[idx]
            acquisition_rows.append(
                {
                    "method": method if ablation is None else ablation,
                    "seed": str(seed),
                    "round": str(round_idx + 1),
                    "rank": str(rank),
                    "row_id": row.row_id,
                    "split": row.split,
                    "policy": row.policy,
                    "success": str(row.success),
                    "failure_labels": ";".join(name for name, active in zip(FAILURES, row.failures) if active),
                }
            )
        selected.extend(batch)
    return round_rows, acquisition_rows, selected


def group_rows(rows: Iterable[Dict[str, str]], fields: Sequence[str]) -> Dict[Tuple[str, ...], List[Dict[str, str]]]:
    grouped: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[field] for field in fields), []).append(row)
    return grouped


def build_seed_metrics(round_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    final_rows = [r for r in round_rows if int(r["round"]) == ROUNDS]
    return final_rows


def build_summary(seed_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    metrics = [
        "robust_success",
        "failure_macro_f1",
        "rare_failure_recall",
        "tail_risk",
        "calibration_error",
        "safety_violation_rate",
        "failure_coverage",
    ]
    rows: List[Dict[str, str]] = []
    for (method, split), group in sorted(group_rows(seed_rows, ["method", "split"]).items()):
        item = {"method": method, "split": split, "seeds": str(len(group)), "rounds": str(ROUNDS)}
        for metric in metrics:
            vals = [float(row[metric]) for row in group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        rows.append(item)
    return rows


def build_pairwise(seed_rows: List[Dict[str, str]], reference: str = "failure_stratified_engine") -> List[Dict[str, str]]:
    by_key = {(row["method"], row["split"], row["seed"]): row for row in seed_rows}
    rows: List[Dict[str, str]] = []
    methods = sorted({row["method"] for row in seed_rows if row["method"] != reference})
    for split in sorted({row["split"] for row in seed_rows}):
        for method in methods:
            success_diffs: List[float] = []
            macro_diffs: List[float] = []
            rare_diffs: List[float] = []
            safety_reductions: List[float] = []
            for seed in [str(s) for s in SEEDS]:
                ref = by_key.get((reference, split, seed))
                other = by_key.get((method, split, seed))
                if ref is None or other is None:
                    continue
                success_diffs.append(float(ref["robust_success"]) - float(other["robust_success"]))
                macro_diffs.append(float(ref["failure_macro_f1"]) - float(other["failure_macro_f1"]))
                rare_diffs.append(float(ref["rare_failure_recall"]) - float(other["rare_failure_recall"]))
                safety_reductions.append(float(other["safety_violation_rate"]) - float(ref["safety_violation_rate"]))
            if success_diffs:
                rows.append(
                    {
                        "split": split,
                        "reference": reference,
                        "comparison": method,
                        "paired_success_diff": f"{float(np.mean(success_diffs)):.5f}",
                        "ci95_success_diff": f"{ci95(success_diffs):.5f}",
                        "paired_macro_f1_diff": f"{float(np.mean(macro_diffs)):.5f}",
                        "paired_rare_recall_diff": f"{float(np.mean(rare_diffs)):.5f}",
                        "paired_safety_reduction": f"{float(np.mean(safety_reductions)):.5f}",
                        "reference_better_seeds": str(sum(1 for d in success_diffs if d > 0)),
                        "seeds": str(len(success_diffs)),
                    }
                )
    return rows


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def rollout_csv_rows(rows: Sequence[RolloutRecord]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for row in rows:
        item = {
            "row_id": row.row_id,
            "split": row.split,
            "scenario_id": row.scenario_id,
            "seed": str(row.seed),
            "policy": row.policy,
            "task_id": str(row.task_id),
            "success": str(row.success),
            "failure_labels": ";".join(name for name, active in zip(FAILURES, row.failures) if active),
            "final_progress": f"{row.final_progress:.5f}",
            "safety_violation": f"{row.safety_violation:.5f}",
            "tail_risk": f"{row.tail_risk:.5f}",
            "trajectory_samples": row.trajectory,
        }
        for name, value in zip(row.feature_names_trace, row.trace_features):
            item[name] = f"{float(value):.5f}"
        out.append(item)
    return out


def plot_round_metric(round_rows: List[Dict[str, str]], split: str, metric: str, path: Path, title: str) -> None:
    plt.figure(figsize=(9, 5))
    for method in METHODS:
        ys, es, xs = [], [], []
        for round_idx in range(ROUNDS + 1):
            vals = [float(r[metric]) for r in round_rows if r["method"] == method and r["split"] == split and int(r["round"]) == round_idx]
            if vals:
                xs.append(round_idx)
                ys.append(float(np.mean(vals)))
                es.append(ci95(vals))
        if xs:
            plt.errorbar(xs, ys, yerr=es, marker="o", label=method)
    plt.xlabel("acquisition round")
    plt.ylabel(metric)
    plt.title(title)
    plt.ylim(0, 1.02 if "success" in metric or "recall" in metric or "f1" in metric else None)
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_bar(summary: List[Dict[str, str]], split: str, metric: str, path: Path, title: str) -> None:
    rows = [r for r in summary if r["split"] == split]
    plt.figure(figsize=(10, 4.8))
    plt.bar([r["method"] for r in rows], [float(r[f"mean_{metric}"]) for r in rows], yerr=[float(r[f"ci95_{metric}"]) for r in rows], color="#596f4c")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel(metric)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_stress(stress_summary: List[Dict[str, str]], path: Path) -> None:
    plt.figure(figsize=(9, 5))
    for method in STRESS_METHODS:
        rows = sorted([r for r in stress_summary if r["method"] == method], key=lambda r: float(r["stress_level"]))
        if not rows:
            continue
        x = [float(r["stress_level"]) for r in rows]
        y = [float(r["mean_robust_success"]) for r in rows]
        e = [float(r["ci95_robust_success"]) for r in rows]
        plt.errorbar(x, y, yerr=e, marker="o", label=method)
    plt.xlabel("stress level")
    plt.ylabel("robust selector success")
    plt.ylim(0, 1.0)
    plt.title("Paper 74 failure data-engine stress sweep")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def decide(summary: List[Dict[str, str]], pairwise: List[Dict[str, str]]) -> Tuple[str, str]:
    combined = [row for row in summary if row["split"] == "combined_tail_stress"]
    proposed = [row for row in combined if row["method"] == "failure_stratified_engine"][0]
    non_oracle = [row for row in combined if row["method"] not in {"failure_stratified_engine", "oracle_failure_strata"}]
    best = max(non_oracle, key=lambda row: float(row["mean_robust_success"]))
    pair = [row for row in pairwise if row["split"] == "combined_tail_stress" and row["comparison"] == best["method"]][0]
    prop_success = float(proposed["mean_robust_success"])
    best_success = float(best["mean_robust_success"])
    prop_rare = float(proposed["mean_rare_failure_recall"])
    best_rare = float(best["mean_rare_failure_recall"])
    prop_macro = float(proposed["mean_failure_macro_f1"])
    best_macro = float(best["mean_failure_macro_f1"])
    prop_safety = float(proposed["mean_safety_violation_rate"])
    best_safety = float(best["mean_safety_violation_rate"])
    paired = float(pair["paired_success_diff"])
    paired_ci = float(pair["ci95_success_diff"])
    if prop_success - best_success >= 0.045 and paired - paired_ci > 0.0 and prop_rare >= best_rare and prop_macro >= best_macro and prop_safety <= best_safety + 0.02:
        return (
            "STRONG_REVISE",
            f"failure_stratified_engine clears strongest non-oracle baseline {best['method']} on combined_tail_stress by "
            f"{prop_success - best_success:.3f} robust success with paired diff {paired:.3f}+/-{paired_ci:.3f}, "
            "but lacks real robot/public benchmark validation.",
        )
    return (
        "KILL_ARCHIVE",
        f"failure_stratified_engine does not clear strongest non-oracle baseline {best['method']} decisively on combined_tail_stress "
        f"(stratified={prop_success:.3f}, best_baseline={best_success:.3f}, paired diff={paired:.3f}+/-{paired_ci:.3f}, "
        f"rare_recall={prop_rare:.3f} vs {best_rare:.3f}, macro_f1={prop_macro:.3f} vs {best_macro:.3f}).",
    )


def negative_cases(test_records: List[RolloutRecord], selected_by_method: Dict[Tuple[int, str], List[RolloutRecord]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for seed in SEEDS:
        selected = selected_by_method.get((seed, "failure_stratified_engine"), [])
        if not selected:
            continue
        failure_model, _ = fit_failure_models(selected)
        split_rows = [r for r in test_records if r.seed == seed and r.split == "combined_tail_stress"]
        by_scenario: Dict[str, List[RolloutRecord]] = {}
        for row in split_rows:
            by_scenario.setdefault(row.scenario_id, []).append(row)
        for scenario_id, group in by_scenario.items():
            probs = predict_binary(failure_model, feature_matrix(group, use_trace=False))
            chosen = group[int(np.argmin(probs))]
            if chosen.success == 0:
                rows.append(
                    {
                        "seed": str(seed),
                        "scenario_id": scenario_id,
                        "chosen_policy": chosen.policy,
                        "failure_labels": ";".join(name for name, active in zip(FAILURES, chosen.failures) if active),
                        "final_progress": f"{chosen.final_progress:.5f}",
                        "safety_violation": f"{chosen.safety_violation:.5f}",
                        "lesson": "failure-stratified selection improved labels but robust selector still chose a tail-risk policy",
                    }
                )
            if len(rows) >= 12:
                return rows
    return rows or [{"seed": "", "scenario_id": "", "chosen_policy": "", "failure_labels": "", "final_progress": "", "safety_violation": "", "lesson": "no negative cases found"}]


def main() -> None:
    start = time.time()
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    all_pool_rows: List[RolloutRecord] = []
    all_test_rows: List[RolloutRecord] = []
    round_rows: List[Dict[str, str]] = []
    acquisition_rows: List[Dict[str, str]] = []
    selected_by_method: Dict[Tuple[int, str], List[RolloutRecord]] = {}

    for seed in SEEDS:
        init_rows, pool_rows, test_by_split = generate_seed_dataset(seed)
        all_pool_rows.extend(init_rows)
        all_pool_rows.extend(pool_rows)
        for rows in test_by_split.values():
            all_test_rows.extend(rows)
        for method in METHODS:
            rr, ar, selected_idx = run_acquisition_method(method, init_rows, pool_rows, test_by_split, seed)
            round_rows.extend(rr)
            acquisition_rows.extend(ar)
            pool = init_rows + pool_rows
            selected_by_method[(seed, method)] = [pool[idx] for idx in selected_idx]

    seed_rows = build_seed_metrics(round_rows)
    summary = build_summary(seed_rows)
    pairwise = build_pairwise(seed_rows)
    write_csv(RESULTS / "rollout_pool.csv", rollout_csv_rows(all_pool_rows))
    write_csv(RESULTS / "heldout_rollouts.csv", rollout_csv_rows(all_test_rows))
    write_csv(RESULTS / "acquisition_log.csv", acquisition_rows)
    write_csv(RESULTS / "round_metrics.csv", round_rows)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", summary)
    write_csv(RESULTS / "failure_engine_metrics.csv", summary)
    write_csv(RESULTS / "pairwise_stats.csv", pairwise)
    write_csv(RESULTS / "failure_engine_pairwise.csv", pairwise)
    write_csv(
        RESULTS / "training_summary.csv",
        [
            {
                "quick_mode": str(QUICK_MODE),
                "seeds": ";".join(str(seed) for seed in SEEDS),
                "seed_count": str(len(SEEDS)),
                "init_scenarios": str(INIT_SCENARIOS),
                "pool_scenarios": str(POOL_SCENARIOS),
                "test_scenarios": str(TEST_SCENARIOS),
                "stress_scenarios": str(STRESS_SCENARIOS),
                "rounds": str(ROUNDS),
                "budget_per_round": str(BUDGET_PER_ROUND),
                "policies": str(len(POLICIES)),
                "failure_labels": str(len(FAILURES)),
                "methods": str(len(METHODS)),
                "ablation_methods": str(len(ABLATION_METHODS)),
                "stress_methods": str(len(STRESS_METHODS)),
                "sim_steps_per_rollout": str(STEPS),
                "dt": f"{DT:.5f}",
            }
        ],
    )

    ablation_round_rows: List[Dict[str, str]] = []
    for seed in SEEDS:
        init_rows, pool_rows, test_by_split = generate_seed_dataset(seed + 100)
        combined_only = {"combined_tail_stress": test_by_split["combined_tail_stress"]}
        for ablation in ABLATION_METHODS:
            rr, _, _ = run_acquisition_method("failure_stratified_engine", init_rows, pool_rows, combined_only, seed, ablation=ablation)
            ablation_round_rows.extend(rr)
    ablation_seed = build_seed_metrics(ablation_round_rows)
    ablation_summary = build_summary(ablation_seed)
    write_csv(RESULTS / "failure_engine_ablation_rounds.csv", ablation_round_rows)
    write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)
    write_csv(RESULTS / "failure_engine_ablation.csv", ablation_summary)

    stress_rows_raw: List[Dict[str, str]] = []
    stress_summary_rows: List[Dict[str, str]] = []
    model = make_model()
    for stress_level in ([0.0, 1.0] if QUICK_MODE else np.linspace(0.0, 1.0, 6)):
        for seed in SEEDS:
            split = SPLIT_BY_NAME["combined_tail_stress"]
            stress_test = generate_records_for_split(model, split, seed, 5000 + int(100 * stress_level), STRESS_SCENARIOS, "stress", stress_level=float(stress_level))
            for method in STRESS_METHODS:
                selected = selected_by_method[(seed, method)]
                metrics = evaluate_rows(stress_test, selected)
                stress_rows_raw.append(
                    {
                        "method": method,
                        "seed": str(seed),
                        "stress_level": f"{float(stress_level):.2f}",
                        **{k: f"{v:.5f}" for k, v in metrics.items()},
                    }
                )
    for (method, stress_level), group in sorted(group_rows(stress_rows_raw, ["method", "stress_level"]).items()):
        item = {"method": method, "stress_level": stress_level, "seeds": str(len(group))}
        for metric in ["robust_success", "failure_macro_f1", "rare_failure_recall", "tail_risk", "safety_violation_rate"]:
            vals = [float(row[metric]) for row in group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        stress_summary_rows.append(item)
    write_csv(RESULTS / "stress_sweep_raw.csv", stress_rows_raw)
    write_csv(RESULTS / "stress_sweep.csv", stress_summary_rows)
    write_csv(FIGURES / "stress_curve_data.csv", stress_summary_rows)
    write_csv(RESULTS / "negative_cases.csv", negative_cases(all_test_rows, selected_by_method))

    plot_round_metric(round_rows, "combined_tail_stress", "robust_success", FIGURES / "failure_engine_success_by_round.png", "Paper 74 robust success by acquisition round")
    plot_round_metric(round_rows, "combined_tail_stress", "rare_failure_recall", FIGURES / "failure_engine_rare_recall_by_round.png", "Paper 74 rare failure recall by acquisition round")
    plot_bar(summary, "combined_tail_stress", "robust_success", FIGURES / "failure_engine_final_success.png", "Paper 74 final combined-tail robust success")
    plot_bar(ablation_summary, "combined_tail_stress", "robust_success", FIGURES / "failure_engine_ablation_success.png", "Paper 74 failure-stratification ablations")
    plot_stress(stress_summary_rows, FIGURES / "failure_engine_stress_sweep.png")

    decision, reason = decide(summary, pairwise)
    combined_rows = [row for row in summary if row["split"] == "combined_tail_stress"]
    elapsed = time.time() - start
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 74 data_engine_failure_stratification real MuJoCo rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Rollout pool rows: {len(all_pool_rows)}\n")
        f.write(f"Heldout rollout rows: {len(all_test_rows)}\n")
        f.write(f"Round metric rows: {len(round_rows)}\n")
        f.write(f"Ablation rows: {len(ablation_round_rows)}\n")
        f.write(f"Stress rows: {len(stress_rows_raw)}\n")
        f.write(f"Seeds: {SEEDS}\n")
        f.write(f"Rounds: {ROUNDS}\n")
        f.write(f"Budget per round: {BUDGET_PER_ROUND}\n")
        f.write(f"Runtime seconds: {elapsed:.2f}\n\n")
        f.write("Combined-tail summary:\n")
        for row in sorted(combined_rows, key=lambda r: -float(r["mean_robust_success"])):
            f.write(
                f"{row['method']} success={row['mean_robust_success']} ci95={row['ci95_robust_success']} "
                f"macro_f1={row['mean_failure_macro_f1']} rare_recall={row['mean_rare_failure_recall']} "
                f"tail={row['mean_tail_risk']} safety={row['mean_safety_violation_rate']}\n"
            )
    print(f"wrote Paper 74 MuJoCo failure-stratification evidence to {RESULTS}")
    print(f"terminal recommendation: {decision}")
    print(reason)


if __name__ == "__main__":
    main()

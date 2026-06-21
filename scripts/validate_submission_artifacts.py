from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOWNLOADS = Path.home() / "Downloads"
DESKTOP = Path.home() / "Desktop"
PDF = DOWNLOADS / "74.pdf"

EXPECTED_COUNTS = {
    "rollout_pool.csv": 31104,
    "heldout_rollouts.csv": 7776,
    "round_metrics.csv": 6480,
    "raw_seed_metrics.csv": 1080,
    "metrics.csv": 135,
    "failure_engine_metrics.csv": 135,
    "pairwise_stats.csv": 126,
    "failure_engine_pairwise.csv": 126,
    "aggregate_seed_metrics.csv": 240,
    "aggregate_metrics.csv": 30,
    "aggregate_pairwise_stats.csv": 28,
    "fixed_risk_seed_metrics.csv": 6600,
    "fixed_risk_metrics.csv": 825,
    "failure_engine_ablation_rounds.csv": 384,
    "ablation_metrics.csv": 8,
    "failure_engine_ablation.csv": 8,
    "stress_sweep_raw.csv": 336,
    "stress_sweep.csv": 42,
    "negative_cases.csv": 12,
    "training_summary.csv": 1,
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pdf_page_count(path: Path) -> int:
    try:
        from pypdf import PdfReader  # type: ignore

        return len(PdfReader(str(path)).pages)
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore

            return len(PdfReader(str(path)).pages)
        except Exception:
            result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())
            raise RuntimeError("could not determine PDF page count")


def main() -> None:
    for name, expected in EXPECTED_COUNTS.items():
        path = RESULTS / name
        require(path.exists(), f"missing {path}")
        rows = read_rows(path)
        require(len(rows) == expected, f"{name} has {len(rows)} rows, expected {expected}")

    summary = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    require("Terminal recommendation: KILL_ARCHIVE" in summary, "summary lacks KILL_ARCHIVE decision")
    require("Rollout pool rows: 31104" in summary, "summary lacks final rollout-pool row count")
    require("Fixed-risk seed rows: 6600" in summary, "summary lacks fixed-risk row count")
    require("Ablation rows: 384" in summary, "summary lacks ablation row count")
    require("Stress rows: 336" in summary, "summary lacks stress row count")

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    require("citebordercolor={0 1 0}" in tex, "bright citation boxes are not configured")
    require("pdfborder={0 0 1.6}" in tex, "PDF border width is not configured")
    require("failure_stratified_engine_v5" in tex or "fs-v5" in tex, "v5 method is absent from manuscript")

    require(PDF.exists(), f"missing Downloads PDF {PDF}")
    require(not (DESKTOP / "74.pdf").exists(), "Desktop copy of 74.pdf exists")
    pages = pdf_page_count(PDF)
    require(pages >= 25, f"PDF has {pages} pages, expected at least 25")

    digest = hashlib.sha256(PDF.read_bytes()).hexdigest().upper()
    print(f"validated Paper 74 artifacts: pages={pages}, sha256={digest}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise


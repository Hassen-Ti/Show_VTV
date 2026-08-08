#!/usr/bin/env python3
"""Benchmark 10 architectures agentiques sur provocateur×physicien."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.benchmark_architectures import export_csv, export_json, run_architecture_benchmark

OUT = ROOT / "docs" / "product"


def main() -> None:
    rows = run_architecture_benchmark()
    export_csv(rows, OUT / "architecture_benchmark.csv")
    export_json(rows, OUT / "architecture_benchmark.json")

    print("=== 10 ARCHITECTURES — Provocateur physicien (1 round agent mock) ===\n")
    for r in rows:
        print(
            f"{r.rank:2d}. {r.architecture_name:22s} | score={r.quality_score:.3f} | "
            f"steps={r.steps_executed:2d} | tactic={r.tactic_used:18s} | "
            f"plan={r.has_plan} reflect={r.has_reflection}"
        )
    print(f"\nÉcrit : {OUT}/architecture_benchmark.csv")


if __name__ == "__main__":
    main()

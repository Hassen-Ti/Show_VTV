#!/usr/bin/env python3
"""Benchmark 10 architectures agentiques sur provocateur×physicien."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.benchmark_architectures import export_csv, export_json, run_architecture_benchmark


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "docs" / "product",
        help="Directory for CSV/JSON exports (default: docs/product)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    rows = run_architecture_benchmark()
    export_csv(rows, out / "architecture_benchmark.csv")
    export_json(rows, out / "architecture_benchmark.json")

    print("=== 10 ARCHITECTURES — Provocateur physicien (1 round agent mock) ===\n")
    for r in rows:
        print(
            f"{r.rank:2d}. {r.architecture_name:22s} | score={r.quality_score:.3f} | "
            f"steps={r.steps_executed:2d} | tactic={r.tactic_used:18s} | "
            f"plan={r.has_plan} reflect={r.has_reflection}"
        )
    print(f"\nÉcrit : {out}/architecture_benchmark.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Génère les dataframes benchmark personas (full + top 10 + mind tests)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.benchmark import (
    all_persona_combos,
    build_persona,
    export_csv,
    export_json,
    mind_micro_benchmark,
    run_full_benchmark,
    top10_balanced_cast,
    top_n,
)

OUT_DIR = ROOT / "docs" / "product"


def main() -> None:
    rows = run_full_benchmark()
    top = top_n(rows, 10)
    cast = top10_balanced_cast(rows)

    export_csv(rows, OUT_DIR / "persona_benchmark_full.csv")
    export_csv(top, OUT_DIR / "persona_top10.csv")
    export_csv(cast, OUT_DIR / "persona_top10_cast.csv")
    export_json(top, OUT_DIR / "persona_top10.json")
    export_json(cast, OUT_DIR / "persona_top10_cast.json")

    mind_rows = []
    for personality, domain in all_persona_combos():
        persona = build_persona(personality, domain)
        micro = mind_micro_benchmark(persona)
        mind_rows.append({"persona_id": f"{personality}_{domain}", "personality": personality, "domain": domain, **micro})

    import csv

    mind_path = OUT_DIR / "persona_mind_tests.csv"
    with mind_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=mind_rows[0].keys())
        writer.writeheader()
        writer.writerows(mind_rows)

    print("=== TOP 10 RANG GLOBAL (3 scénarios agent / persona) ===\n")
    for r in top:
        print(
            f"{r.rank:2d}. {r.display_name:32s} | {r.conclave_role:14s} | "
            f"score={r.final_score:.3f} | agent={r.agent_composite:.3f} | "
            f"scénarios={r.agent_scenarios_passed}/3 | tactic={r.agent_tactic_used}"
        )

    print("\n=== TOP 10 CAST ÉQUILIBRÉ (4 Flux + 3 Archive + 3 Protocole) ===\n")
    for i, r in enumerate(cast, 1):
        print(
            f"{i:2d}. {r.display_name:32s} | {r.conclave_role:14s} | "
            f"score={r.final_score:.3f} | opp_drift={r.agent_opponent_drift:.3f}"
        )

    print(f"\nDataframes écrits dans {OUT_DIR}/")
    print("  - persona_benchmark_full.csv (15 lignes, 26 métriques)")
    print("  - persona_top10.csv (classement brut)")
    print("  - persona_top10_cast.csv (casting plateau recommandé)")
    print("  - persona_mind_tests.csv (tests algorithmiques mind)")


if __name__ == "__main__":
    main()

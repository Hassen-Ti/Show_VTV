"""Tests benchmark personas : top 10, dataframe, simulation agent."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.benchmark import (
    all_persona_combos,
    build_persona,
    export_csv,
    mind_micro_benchmark,
    run_full_benchmark,
    top10_balanced_cast,
    top_n,
)
from show.personas.registry import DOMAINS, PERSONALITIES

BENCHMARK_CSV = ROOT / "docs" / "product" / "persona_benchmark_full.csv"
TOP10_CSV = ROOT / "docs" / "product" / "persona_top10.csv"
TOP10_CAST_CSV = ROOT / "docs" / "product" / "persona_top10_cast.csv"
MIND_CSV = ROOT / "docs" / "product" / "persona_mind_tests.csv"


@pytest.fixture(scope="module")
def benchmark_rows():
    return run_full_benchmark()


def test_fifteen_combinations_scored(benchmark_rows):
    assert len(benchmark_rows) == len(PERSONALITIES) * len(DOMAINS) == 15
    ranks = [r.rank for r in benchmark_rows]
    assert ranks == list(range(1, 16))


def test_top10_unique_personas(benchmark_rows):
    top = top_n(benchmark_rows, 10)
    assert len(top) == 10
    ids = [r.persona_id for r in top]
    assert len(ids) == len(set(ids))


def test_all_top10_pass_agent_sim(benchmark_rows):
    top = top_n(benchmark_rows, 10)
    failed = [r.persona_id for r in top if not r.agent_pass]
    assert not failed, f"Top 10 avec agent_pass=False: {failed}"


def test_scores_are_ordered(benchmark_rows):
    scores = [r.final_score for r in benchmark_rows]
    assert scores == sorted(scores, reverse=True)


def test_each_personality_represented_in_balanced_cast(benchmark_rows):
    cast = top10_balanced_cast(benchmark_rows)
    personalities = {r.personality for r in cast}
    assert personalities == set(PERSONALITIES.keys())
    assert len(cast) == 10


def test_provocateur_physicien_in_top10(benchmark_rows):
    """Preset par défaut UI — doit rester compétitif."""
    top_ids = {r.persona_id for r in top_n(benchmark_rows, 10)}
    assert "provocateur_physicien" in top_ids


def test_export_dataframes(benchmark_rows):
    export_csv(benchmark_rows, BENCHMARK_CSV)
    export_csv(top_n(benchmark_rows, 10), TOP10_CSV)
    export_csv(top10_balanced_cast(benchmark_rows), TOP10_CAST_CSV)
    assert BENCHMARK_CSV.exists()
    assert TOP10_CSV.exists()
    assert TOP10_CAST_CSV.exists()
    with BENCHMARK_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 15
    required = {
        "rank",
        "persona_id",
        "personality",
        "domain",
        "final_score",
        "agent_pass",
        "agent_scenarios_passed",
        "agent_opponent_drift",
        "trait_composite",
        "agent_composite",
        "conclave_role",
    }
    assert required <= set(rows[0].keys())


def test_mind_micro_benchmark_all_combos():
    rows = []
    for personality, domain in all_persona_combos():
        persona = build_persona(personality, domain)
        micro = mind_micro_benchmark(persona)
        rows.append(
            {
                "persona_id": f"{personality}_{domain}",
                "personality": personality,
                "domain": domain,
                **micro,
            }
        )
    MIND_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MIND_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    assert len(rows) == 15
    # Provocateur : haute stubbornness → faible révision stance
    prov = next(r for r in rows if r["persona_id"] == "provocateur_physicien")
    dipl = next(r for r in rows if r["persona_id"] == "diplomate_philosophe")
    assert prov["stance_revision_delta"] < dipl["stance_revision_delta"]


def test_top10_print_summary(benchmark_rows, capsys):
    top = top_n(benchmark_rows, 10)
    for r in top:
        print(f"{r.rank:2d}. {r.display_name:30s} score={r.final_score:.3f} agent={r.agent_pass}")
    out = capsys.readouterr().out
    assert "score=" in out

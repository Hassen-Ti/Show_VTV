"""Tests benchmark 10 architectures sur un persona fixe."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.architectures import ARCHITECTURES
from show.personas.benchmark_architectures import run_architecture_benchmark

ARCH_CSV = ROOT / "docs" / "product" / "architecture_benchmark.csv"


@pytest.fixture(scope="module")
def arch_rows():
    return run_architecture_benchmark()


def test_ten_architectures_evaluated(arch_rows):
    assert len(arch_rows) == len(ARCHITECTURES) == 10


def test_all_architectures_pass_agent(arch_rows):
    failed = [r.architecture_id for r in arch_rows if not r.agent_pass]
    assert not failed, failed


def test_scores_ordered(arch_rows):
    scores = [r.quality_score for r in arch_rows]
    assert scores == sorted(scores, reverse=True)


def test_reflexion_or_plan_in_top3(arch_rows):
    top3 = {r.architecture_id for r in arch_rows[:3]}
    assert top3 & {"reflexion", "plan_execute", "rewoo"}


def test_export_architecture_dataframe(arch_rows):
    ARCH_CSV.parent.mkdir(parents=True, exist_ok=True)
    from show.personas.benchmark_architectures import export_csv

    export_csv(arch_rows, ARCH_CSV)
    with ARCH_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 10
    assert "architecture_id" in rows[0]
    assert "quality_score" in rows[0]
def test_traces_capture_full_outputs():
    from show.personas.benchmark_architectures import run_architecture_benchmark_with_traces

    _, traces = run_architecture_benchmark_with_traces()
    assert len(traces) == 10
    t = traces[0]
    assert len(t.pipeline) >= 5
    assert t.pipeline[0].input_turn is not None
    assert t.pipeline[0].input_mind is not None
    assert t.show_initial
    assert t.show_final
    assert t.on_air_response
    assert t.inner_monologue
    guest_a_steps = [s for s in t.pipeline if s.agent == "guest_a"]
    guest_b_steps = [s for s in t.pipeline if s.agent == "guest_b"]
    assert guest_a_steps
    assert guest_b_steps


def test_viewer_html_generated(tmp_path):
    from show.personas.benchmark_architectures import run_architecture_benchmark_with_traces

    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_architecture_viewer import generate_html

    _, traces = run_architecture_benchmark_with_traces()
    out = tmp_path / "lab.html"
    generate_html(traces, out)
    html = out.read_text(encoding="utf-8")
    assert "V.TV — GRAPH TRACE LAB" in html
    assert traces[0].architecture_id in html
    assert "Input — turn" in html
    assert "ShowState global" in html

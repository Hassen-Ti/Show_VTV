"""Tests lab philosophe réflexif — 10 questions solo."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.reflection_lab import (
    PHILOSOPHER_QUESTIONS,
    run_philosopher_lab,
    run_single_question,
    make_philosopher_persona,
)


@pytest.fixture(scope="module")
def lab():
    return run_philosopher_lab()


def test_ten_questions(lab):
    assert len(lab.questions) == len(PHILOSOPHER_QUESTIONS) == 10


def test_philosopher_reflexion_architecture(lab):
    assert lab.architecture_id == "reflexion"
    assert lab.domain == "philosophe"
    assert lab.personality == "cerebral"


def test_every_question_has_final_response(lab):
    missing = [q.question_id for q in lab.questions if not q.final_response.strip()]
    assert not missing, missing


def test_pipeline_and_outputs_per_question(lab):
    for q in lab.questions:
        assert len(q.pipeline) >= 8, q.question_id
        assert q.all_outputs.get("par_etape"), q.question_id
        assert q.all_outputs.get("tour_final"), q.question_id
        assert "reflect" in q.all_outputs["par_etape"] or any(
            s.step == "reflect" for s in q.pipeline
        )


def test_deliver_step_has_llm_response(lab):
    q = lab.questions[0]
    deliver = next(s for s in q.pipeline if s.step == "deliver")
    assert deliver.llm_calls
    assert deliver.llm_calls[-1].response


def test_viewer_html(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_philosopher_viewer import generate_html

    lab = run_philosopher_lab()
    out = tmp_path / "phil.html"
    generate_html(lab, out)
    html = out.read_text(encoding="utf-8")
    assert "PHILOSOPHE RÉFLEXIF" in html
    assert lab.questions[0].final_response[:40] in html
    assert "Réponse finale" in html

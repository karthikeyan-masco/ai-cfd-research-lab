import pytest
from ai_cfd_lab.debate.protocol import DebateEngine
from ai_cfd_lab.providers.demo import DemoProvider


def test_debate_completes_and_preserves_disagreement():
    result = DebateEngine(DemoProvider(), max_rounds=2).run(
        "Why does a simulated compressible boundary layer differ from a reference profile?"
    )
    assert result.status == "completed"
    assert len(result.initial_submissions) == 2
    assert len(result.critiques) == 2
    assert len(result.rebuttals) == 4
    assert result.final_verdict
    assert result.unresolved_issues


def test_empty_question_rejected():
    with pytest.raises(ValueError):
        DebateEngine(DemoProvider()).run("  ")


def test_round_limit_validated():
    with pytest.raises(ValueError):
        DebateEngine(DemoProvider(), max_rounds=0)

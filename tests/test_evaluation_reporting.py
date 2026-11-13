from ai_cfd_lab.evaluation.experiment_registry import ExperimentRegistry
from ai_cfd_lab.evaluation.reporting import render_report


def test_empty_report():
    assert "No experiments found" in render_report([])


def test_report_scores_and_missing_values(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments.db")
    registry.save("normal-shock-m2", "demo", {"theory_score": 100, "cfd_score": 75, "coordinator_score": 100})
    registry.save("normal-shock-m2", "demo", {"theory_score": 50})
    report = render_report(registry.list_runs("normal-shock-m2"), "normal-shock-m2")
    assert "Runs: **2**" in report
    assert "75.00%" in report
    assert "75.00%** over 2 scored run(s)" in report
    assert "N/A" in report


def test_invalid_score_not_counted():
    record = {"run_id": "r", "challenge_id": "c", "provider": "demo", "timestamp": "t", "results": {"theory_score": float("nan"), "cfd_score": True}}
    report = render_report([record])
    assert "no valid percentage scores" in report

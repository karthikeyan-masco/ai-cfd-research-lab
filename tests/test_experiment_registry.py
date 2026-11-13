
from ai_cfd_lab.evaluation.experiment_registry import (
    ExperimentRegistry,
)


def test_save_and_retrieve_experiment(tmp_path):
    database = tmp_path / "experiments.db"
    registry = ExperimentRegistry(database)

    run_id = registry.save(
        challenge_id="normal-shock-m2",
        provider="demo",
        results={
            "theory_score": 100,
            "cfd_score": 75,
            "coordinator_score": 100,
        },
    )

    record = registry.get(run_id)

    assert record is not None
    assert record["challenge_id"] == "normal-shock-m2"
    assert record["results"]["theory_score"] == 100


def test_list_experiments(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments.db")

    registry.save("normal-shock-m2", "demo", {"score": 100})
    registry.save("sod-x070-t020", "demo", {"score": 80})

    assert len(registry.list_runs()) == 2
    assert len(registry.list_runs("normal-shock-m2")) == 1


def test_unknown_experiment(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments.db")

    assert registry.get("nonexistent") is None

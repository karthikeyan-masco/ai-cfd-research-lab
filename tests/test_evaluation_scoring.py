import json
import math
import subprocess
import sys

import pytest

from ai_cfd_lab.evaluation.challenges import get_challenge
from ai_cfd_lab.evaluation.scoring import evaluate_predictions


@pytest.fixture
def challenge():
    return get_challenge("normal-shock-m2")


def test_exact_reference_passes(challenge):
    result = evaluate_predictions(challenge, dict(challenge.reference().reference_values))
    assert result.passed == result.total == 4
    assert result.score_percent == 100


def test_missing_invalid_and_incorrect(challenge):
    result = evaluate_predictions(challenge, {"M2": 0.57735, "p2_p1": 5, "rho2_rho1": float("nan")})
    assert [q.status for q in result.quantities] == ["pass", "fail", "invalid", "missing"]
    assert result.score_percent == 25


def test_extra_keys_do_not_improve_score(challenge):
    result = evaluate_predictions(challenge, {"M2": 0.57735, "made_up": 42})
    assert result.unexpected_keys == ("made_up",)
    assert result.passed == 1


def test_tolerance_boundary(challenge):
    ref = challenge.reference().reference_values["p2_p1"]
    result = evaluate_predictions(challenge, {"p2_p1": ref + 0.004}, relative_tolerance=0, absolute_tolerance=0.005)
    assert result.quantities[1].status == "pass"
    result = evaluate_predictions(challenge, {"p2_p1": ref + 0.006}, relative_tolerance=0, absolute_tolerance=0.005)
    assert result.quantities[1].status == "fail"


@pytest.mark.parametrize("bad", [True, "4.5", None, float("inf"), -float("inf"), complex(1, 2)])
def test_invalid_values(challenge, bad):
    result = evaluate_predictions(challenge, {"p2_p1": bad})
    assert result.quantities[1].status == "invalid"


@pytest.mark.parametrize("rtol,atol", [(-1, 0), (0, -1), (float("nan"), 0), (0, float("inf"))])
def test_bad_tolerances(challenge, rtol, atol):
    with pytest.raises(ValueError):
        evaluate_predictions(challenge, {}, relative_tolerance=rtol, absolute_tolerance=atol)


def test_cli_roundtrip(tmp_path):
    p = tmp_path / "predictions.json"
    p.write_text(json.dumps({"M2": 0.5773502692, "p2_p1": 4.5, "rho2_rho1": 2.66666667, "T2_T1": 1.6875}), encoding="utf-8")
    proc = subprocess.run([sys.executable, "-m", "ai_cfd_lab.evaluation.scoring", "--id", "normal-shock-m2", "--predictions", str(p)], capture_output=True, text=True, check=True)
    result = json.loads(proc.stdout)
    assert result["score_percent"] == 100
    assert len(result["quantities"]) == 4

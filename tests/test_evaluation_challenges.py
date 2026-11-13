import math
import pytest
from ai_cfd_lab.evaluation import all_challenges, get_challenge


def test_challenge_ids_unique():
    ids = [c.id for c in all_challenges()]
    assert len(ids) == 3
    assert len(ids) == len(set(ids))


def test_normal_shock_reference():
    r = get_challenge("normal-shock-m2").reference().reference_values
    assert r["M2"] == pytest.approx(1 / math.sqrt(3), abs=1e-12)
    assert r["p2_p1"] == pytest.approx(4.5)
    assert r["rho2_rho1"] == pytest.approx(8 / 3)
    assert r["T2_T1"] == pytest.approx(1.6875)


def test_oblique_shock_reference():
    r = get_challenge("oblique-shock-m2-theta10").reference().reference_values
    assert r["beta_deg"] == pytest.approx(39.31393184, abs=1e-6)
    assert r["M2"] == pytest.approx(1.64052223, abs=1e-6)


def test_sod_reference():
    r = get_challenge("sod-x070-t020").reference().reference_values
    assert r["rho"] == pytest.approx(0.2655737117, abs=1e-8)
    assert r["u"] == pytest.approx(0.9274526200, abs=1e-8)
    assert r["p"] == pytest.approx(0.3031301781, abs=1e-8)


def test_unknown_challenge():
    with pytest.raises(KeyError):
        get_challenge("does-not-exist")


def test_reference_reproducible():
    c = get_challenge("normal-shock-m2")
    assert c.reference() == c.reference()

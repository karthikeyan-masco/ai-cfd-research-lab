import math
import pytest
from ai_cfd_lab.benchmarks.shocks import normal_shock, oblique_shock_weak_beta, oblique_shock_properties


def test_normal_shock_mach_2_gamma_14():
    result = normal_shock(2.0, 1.4)
    assert result["M2"] == pytest.approx(0.577350269, rel=1e-7)
    assert result["p2_p1"] == pytest.approx(4.5)
    assert result["rho2_rho1"] == pytest.approx(2.6666666667)
    assert result["T2_T1"] == pytest.approx(1.6875)


def test_normal_shock_rejects_subsonic():
    with pytest.raises(ValueError):
        normal_shock(0.8)


def test_oblique_shock_mach_2_ten_degrees():
    result = oblique_shock_properties(2.0, 10.0)
    assert result["beta_deg"] == pytest.approx(39.3139, abs=0.02)
    assert result["M2"] > 1
    assert result["p2_p1"] > 1


def test_oblique_shock_rejects_detached_case():
    with pytest.raises(ValueError):
        oblique_shock_weak_beta(2.0, 45.0)

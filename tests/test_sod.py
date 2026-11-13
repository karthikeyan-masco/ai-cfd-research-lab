import pytest
from ai_cfd_lab.benchmarks.sod import sod_exact, sod_star_state


def test_sod_star_state_standard():
    state = sod_star_state(1.4)
    assert state["p_star"] == pytest.approx(0.30313, abs=2e-5)
    assert state["u_star"] == pytest.approx(0.92745, abs=2e-5)


def test_sod_initial_conditions_at_zero_time():
    assert sod_exact(0.25, 0.0)["rho"] == 1.0
    assert sod_exact(0.75, 0.0)["rho"] == 0.125


def test_sod_regions_are_physical():
    left = sod_exact(0.3, 0.2)
    star = sod_exact(0.55, 0.2)
    right = sod_exact(0.9, 0.2)
    assert left["rho"] > 0 and left["p"] > 0
    assert star["rho"] > 0 and star["p"] > 0
    assert right["rho"] > 0 and right["p"] > 0
    assert right["region"] == "right_initial"

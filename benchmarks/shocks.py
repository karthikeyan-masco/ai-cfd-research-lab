from __future__ import annotations
import math


def normal_shock(M1: float, gamma: float = 1.4) -> dict[str, float]:
    """Calorically perfect gas normal-shock ratios; M1 > 1."""
    if M1 <= 1:
        raise ValueError("Upstream Mach number must be greater than 1.")
    if gamma <= 1:
        raise ValueError("gamma must be greater than 1.")
    m2_sq = (1 + 0.5 * (gamma - 1) * M1**2) / (gamma * M1**2 - 0.5 * (gamma - 1))
    p2_p1 = 1 + 2 * gamma / (gamma + 1) * (M1**2 - 1)
    rho2_rho1 = ((gamma + 1) * M1**2) / ((gamma - 1) * M1**2 + 2)
    t2_t1 = p2_p1 / rho2_rho1
    return {
        "M2": math.sqrt(m2_sq),
        "p2_p1": p2_p1,
        "rho2_rho1": rho2_rho1,
        "T2_T1": t2_t1,
    }


def theta_from_beta(M1: float, beta_rad: float, gamma: float = 1.4) -> float:
    """Return flow deflection theta in radians from the theta-beta-M relation."""
    if M1 <= 1 or gamma <= 1:
        raise ValueError("Require M1 > 1 and gamma > 1.")
    mu = math.asin(1.0 / M1)
    if not mu < beta_rad < math.pi / 2:
        raise ValueError("beta must lie between Mach angle and 90 degrees.")
    numerator = 2 / math.tan(beta_rad) * (M1**2 * math.sin(beta_rad)**2 - 1)
    denominator = M1**2 * (gamma + math.cos(2 * beta_rad)) + 2
    return math.atan(numerator / denominator)


def oblique_shock_weak_beta(M1: float, theta_deg: float, gamma: float = 1.4) -> float:
    """Solve weak attached-shock beta in degrees by bisection."""
    if M1 <= 1 or gamma <= 1:
        raise ValueError("Require M1 > 1 and gamma > 1.")
    theta = math.radians(theta_deg)
    if theta <= 0:
        raise ValueError("Deflection angle must be positive.")
    mu = math.asin(1.0 / M1)
    lo, hi = mu + 1e-9, math.pi / 2 - 1e-9
    # Find theta maximum (detachment limit).
    a, b = lo, hi
    for _ in range(100):
        x1 = a + (b-a)/3
        x2 = b - (b-a)/3
        if theta_from_beta(M1, x1, gamma) < theta_from_beta(M1, x2, gamma):
            a = x1
        else:
            b = x2
    beta_peak = 0.5 * (a+b)
    theta_max = theta_from_beta(M1, beta_peak, gamma)
    if theta >= theta_max:
        raise ValueError(f"No weak attached solution: theta must be below about {math.degrees(theta_max):.5g} deg.")
    left, right = lo, beta_peak
    for _ in range(100):
        mid = 0.5 * (left + right)
        if theta_from_beta(M1, mid, gamma) < theta:
            left = mid
        else:
            right = mid
    return math.degrees(0.5 * (left + right))


def oblique_shock_properties(M1: float, theta_deg: float, gamma: float = 1.4) -> dict[str, float]:
    beta_deg = oblique_shock_weak_beta(M1, theta_deg, gamma)
    beta = math.radians(beta_deg)
    Mn1 = M1 * math.sin(beta)
    ns = normal_shock(Mn1, gamma)
    M2 = ns["M2"] / math.sin(beta - math.radians(theta_deg))
    return {
        "beta_deg": beta_deg,
        "Mn1": Mn1,
        "M2": M2,
        "p2_p1": ns["p2_p1"],
        "rho2_rho1": ns["rho2_rho1"],
        "T2_T1": ns["T2_T1"],
    }

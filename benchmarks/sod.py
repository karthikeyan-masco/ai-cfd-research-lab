from __future__ import annotations
import math


def _pressure_function(p: float, state: tuple[float, float, float], gamma: float) -> tuple[float, float]:
    rho, u, p_i = state
    a = math.sqrt(gamma * p_i / rho)
    if p > p_i:  # shock
        A = 2 / ((gamma + 1) * rho)
        B = (gamma - 1) / (gamma + 1) * p_i
        root = math.sqrt(A / (p + B))
        f = (p - p_i) * root
        df = root * (1 - 0.5 * (p - p_i) / (p + B))
    else:  # rarefaction
        pr = p / p_i
        f = 2 * a / (gamma - 1) * (pr ** ((gamma - 1) / (2 * gamma)) - 1)
        df = (1 / (rho * a)) * pr ** (-(gamma + 1) / (2 * gamma))
    return f, df


def sod_star_state(gamma: float = 1.4) -> dict[str, float]:
    """Exact star-region pressure/velocity for standard Sod initial data."""
    left = (1.0, 0.0, 1.0)
    right = (0.125, 0.0, 0.1)
    p = 0.30313
    for _ in range(100):
        fl, dfl = _pressure_function(p, left, gamma)
        fr, dfr = _pressure_function(p, right, gamma)
        new_p = p - (fl + fr + right[1] - left[1]) / (dfl + dfr)
        new_p = max(new_p, 1e-12)
        if abs(new_p - p) < 1e-13:
            p = new_p
            break
        p = new_p
    fl, _ = _pressure_function(p, left, gamma)
    fr, _ = _pressure_function(p, right, gamma)
    u = 0.5 * (left[1] + right[1] + fr - fl)
    return {"p_star": p, "u_star": u}


def sod_exact(x: float, time: float, x0: float = 0.5, gamma: float = 1.4) -> dict[str, float]:
    """Exact standard Sod solution at x,t; initial states rhoL=1,pL=1 and rhoR=.125,pR=.1."""
    if time < 0:
        raise ValueError("time must be non-negative.")
    if gamma <= 1:
        raise ValueError("gamma must be greater than 1.")
    if time == 0:
        if x < x0:
            return {"rho": 1.0, "u": 0.0, "p": 1.0, "region": "left_initial"}
        return {"rho": 0.125, "u": 0.0, "p": 0.1, "region": "right_initial"}

    g = gamma
    rhoL, uL, pL = 1.0, 0.0, 1.0
    rhoR, uR, pR = 0.125, 0.0, 0.1
    aL = math.sqrt(g*pL/rhoL)
    aR = math.sqrt(g*pR/rhoR)
    star = sod_star_state(g)
    ps, us = star["p_star"], star["u_star"]
    xi = (x - x0) / time

    if ps > pL:
        raise NotImplementedError("This implementation targets the standard Sod configuration with a left rarefaction.")
    # Left rarefaction head and tail.
    head = uL - aL
    a_star_L = aL * (ps/pL) ** ((g-1)/(2*g))
    tail = us - a_star_L
    if xi < head:
        return {"rho": rhoL, "u": uL, "p": pL, "region": "left_initial"}
    if xi <= tail:
        u = 2/(g+1) * (aL + 0.5*(g-1)*uL + xi)
        a = 2/(g+1) * (aL + 0.5*(g-1)*(uL-xi))
        rho = rhoL * (a/aL) ** (2/(g-1))
        p = pL * (a/aL) ** (2*g/(g-1))
        return {"rho": rho, "u": u, "p": p, "region": "left_fan"}

    rho_star_L = rhoL * (ps/pL) ** (1/g)
    if xi <= us:
        return {"rho": rho_star_L, "u": us, "p": ps, "region": "left_star"}

    # Right-moving shock.
    shock_speed = uR + aR * math.sqrt((g+1)/(2*g)*(ps/pR) + (g-1)/(2*g))
    if xi <= shock_speed:
        # Density jump across right shock.
        ratio = (ps/pR + (g-1)/(g+1)) / ((g-1)/(g+1)*ps/pR + 1)
        return {"rho": rhoR*ratio, "u": us, "p": ps, "region": "right_star"}
    return {"rho": rhoR, "u": uR, "p": pR, "region": "right_initial"}

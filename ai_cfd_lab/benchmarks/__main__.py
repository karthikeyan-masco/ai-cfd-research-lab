from __future__ import annotations
import argparse
import json
from ai_cfd_lab.benchmarks.shocks import normal_shock, oblique_shock_properties
from ai_cfd_lab.benchmarks.sod import sod_exact


def main():
    parser = argparse.ArgumentParser(description="Ideal-gas compressible-flow benchmark utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    n = sub.add_parser("normal-shock")
    n.add_argument("--mach", type=float, required=True)
    n.add_argument("--gamma", type=float, default=1.4)
    o = sub.add_parser("oblique-shock")
    o.add_argument("--mach", type=float, required=True)
    o.add_argument("--theta-deg", type=float, required=True)
    o.add_argument("--gamma", type=float, default=1.4)
    s = sub.add_parser("sod")
    s.add_argument("--x", type=float, required=True)
    s.add_argument("--time", type=float, required=True)
    s.add_argument("--x0", type=float, default=0.5)
    s.add_argument("--gamma", type=float, default=1.4)
    a = parser.parse_args()
    if a.command == "normal-shock":
        result = normal_shock(a.mach, a.gamma)
    elif a.command == "oblique-shock":
        result = oblique_shock_properties(a.mach, a.theta_deg, a.gamma)
    else:
        result = sod_exact(a.x, a.time, a.x0, a.gamma)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

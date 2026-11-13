"""Deterministic numerical scoring for benchmark predictions.

Run: python -m ai_cfd_lab.evaluation.scoring --id normal-shock-m2 --predictions predictions.json
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from .challenges import Challenge, get_challenge


@dataclass(frozen=True)
class QuantityScore:
    name: str
    status: str
    reference: float
    predicted: float | None
    absolute_error: float | None
    relative_error: float | None
    allowed_error: float


@dataclass(frozen=True)
class EvaluationResult:
    challenge_id: str
    challenge_version: int
    passed: int
    total: int
    score_percent: float
    quantities: tuple[QuantityScore, ...]
    unexpected_keys: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_predictions(
    challenge: Challenge,
    predictions: Mapping[str, object],
    *,
    relative_tolerance: float = 0.01,
    absolute_tolerance: float = 1e-8,
) -> EvaluationResult:
    """Score one point for each finite value within abs+relative tolerance.

    Missing and invalid values score zero. Unknown fields are reported but
    do not affect the denominator. Zero references use the absolute tolerance.
    """
    if not (math.isfinite(relative_tolerance) and relative_tolerance >= 0):
        raise ValueError("relative_tolerance must be finite and nonnegative")
    if not (math.isfinite(absolute_tolerance) and absolute_tolerance >= 0):
        raise ValueError("absolute_tolerance must be finite and nonnegative")
    if not isinstance(predictions, Mapping):
        raise TypeError("predictions must be a mapping of quantity names to numbers")

    reference = challenge.reference().reference_values
    quantities = []
    for key in challenge.output_keys:
        expected = float(reference[key])
        allowed = absolute_tolerance + relative_tolerance * abs(expected)
        if key not in predictions:
            quantities.append(QuantityScore(key, "missing", expected, None, None, None, allowed))
            continue
        value = predictions[key]
        # Reject bool, strings, NaN, infinity and complex numbers.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            quantities.append(QuantityScore(key, "invalid", expected, None, None, None, allowed))
            continue
        try:
            actual = float(value)
        except (OverflowError, ValueError):
            quantities.append(QuantityScore(key, "invalid", expected, None, None, None, allowed))
            continue
        if not math.isfinite(actual):
            quantities.append(QuantityScore(key, "invalid", expected, None, None, None, allowed))
            continue
        error = abs(actual - expected)
        relative_error = error / abs(expected) if expected != 0 else (0.0 if error == 0 else None)
        status = "pass" if error <= allowed else "fail"
        quantities.append(QuantityScore(key, status, expected, actual, error, relative_error, allowed))

    passed = sum(item.status == "pass" for item in quantities)
    return EvaluationResult(
        challenge_id=challenge.id,
        challenge_version=challenge.version,
        passed=passed,
        total=len(quantities),
        score_percent=100 * passed / len(quantities) if quantities else 0.0,
        quantities=tuple(quantities),
        unexpected_keys=tuple(sorted(str(k) for k in predictions if k not in reference)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Score numerical CFD benchmark predictions")
    parser.add_argument("--id", required=True, help="Challenge ID")
    parser.add_argument("--predictions", required=True, type=Path, help="JSON object containing predicted quantities")
    parser.add_argument("--rtol", type=float, default=0.01, help="Relative tolerance (default: 0.01)")
    parser.add_argument("--atol", type=float, default=1e-8, help="Absolute tolerance (default: 1e-8)")
    args = parser.parse_args()
    data = json.loads(args.predictions.read_text(encoding="utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid JSON constant: {x}")))
    result = evaluate_predictions(get_challenge(args.id), data, relative_tolerance=args.rtol, absolute_tolerance=args.atol)
    print(json.dumps(result.to_dict(), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

"""Evaluate structured numerical predictions from debate agents.

Prediction requests are separate from debate submissions. No values are
extracted heuristically from free-form explanations.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_cfd_lab.debate.protocol import DebateEngine
from ai_cfd_lab.providers.demo import DemoProvider
from ai_cfd_lab.providers.openai_compatible import OpenAICompatibleProvider
from .challenges import Challenge, get_challenge
from .scoring import evaluate_predictions


@dataclass(frozen=True)
class PredictionAttempt:
    stage: str
    role: str
    predictions: dict[str, Any]
    error: str | None = None

    def score(self, challenge: Challenge) -> dict[str, Any]:
        result = evaluate_predictions(challenge, self.predictions).to_dict()
        return {"stage": self.stage, "role": self.role,
                "predictions": self.predictions, "error": self.error, "evaluation": result}


def request_predictions(provider: Any, challenge: Challenge, role: str,
                        *, stage: str, context: str = "") -> PredictionAttempt:
    """Request a strict JSON object. Invalid output is recorded, not guessed."""
    keys = list(challenge.output_keys)
    system = ("You are a scientific numerical prediction agent. Return ONLY a JSON "
              "object whose keys are the requested quantities and whose values are "
              "finite JSON numbers. Do not return markdown or prose. "
              "If you cannot calculate a value, omit that key. "
              "Do not invent data.")
    prompt = (f"RESEARCH QUESTION: {challenge.prompt}\n"
              f"INPUTS: {json.dumps(dict(challenge.inputs))}\n"
              f"OUTPUT KEYS: {json.dumps(keys)}\n"
              f"STAGE: {stage}\nCONTEXT: {context}\n"
              "Return the numerical JSON object only.")
    try:
        raw = provider.complete(system_prompt=system, user_prompt=prompt, role=role)
        parsed = json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        if not isinstance(parsed, dict):
            raise ValueError("prediction response is not a JSON object")
        # The scoring engine handles missing, invalid, and extra keys.
        # Ensure arbitrary provider output is JSON serializable in reports.
        json.dumps(parsed, allow_nan=False)
        return PredictionAttempt(stage, role, parsed)
    except (ValueError, TypeError) as exc:
        return PredictionAttempt(stage, role, {}, f"Invalid prediction response: {exc}")


def evaluate_debate(challenge: Challenge, provider: Any, *, rounds: int = 1) -> dict[str, Any]:
    """Compare independent pre-debate predictions to a post-debate coordinator prediction.

    The debate text itself is not scored as a numerical answer. Scores are
    descriptive only; no causal improvement claim follows from one run.
    """
    initial = [request_predictions(provider, challenge, role, stage="initial")
               for role in ("theory", "cfd")]
    debate = DebateEngine(provider, max_rounds=rounds).run(challenge.prompt)
    final = request_predictions(provider, challenge, "coordinator", stage="final",
                                context=debate.final_verdict)
    scored = [attempt.score(challenge) for attempt in [*initial, final]]
    return {
        "challenge_id": challenge.id,
        "challenge_version": challenge.version,
        "provider": type(provider).__name__,
        "rounds": rounds,
        "reference": dict(challenge.reference().reference_values),
        "attempts": scored,
        "debate": debate.to_dict(),
        "note": "Numerical scores only; not a measure of reasoning quality or causal debate benefit.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate four-agent debate numerically")
    parser.add_argument("--id", required=True, help="Benchmark challenge ID")
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--provider", choices=("demo", "api"), default="demo")
    parser.add_argument("--out", type=Path, help="Optional JSON output file")
    args = parser.parse_args()
    provider = DemoProvider() if args.provider == "demo" else OpenAICompatibleProvider.from_env()
    report = evaluate_debate(get_challenge(args.id), provider, rounds=args.rounds)
    output = json.dumps(report, indent=2, allow_nan=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()


"""Run with: python -m ai_cfd_lab.evaluation --all"""

import argparse
import json

from .challenges import all_challenges, get_challenge


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute deterministic CFD benchmark references"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--id", help="Compute one challenge by ID")

    args = parser.parse_args()

    challenges = (
        all_challenges()
        if args.all
        else (get_challenge(args.id),)
    )

    records = []

    for challenge in challenges:
        record = {
            "id": challenge.id,
            "title": challenge.title,
            "prompt": challenge.prompt,
            "kind": challenge.kind,
            "inputs": dict(challenge.inputs),
            "output_keys": list(challenge.output_keys),
            "version": challenge.version,
            "reference": dict(
                challenge.reference().reference_values
            ),
        }

        records.append(record)

    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()

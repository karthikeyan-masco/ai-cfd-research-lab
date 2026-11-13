
import json
import subprocess
import sys


def test_evaluation_cli_all():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_cfd_lab.evaluation",
            "--all",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    challenges = json.loads(result.stdout)

    assert len(challenges) == 3

    ids = {challenge["id"] for challenge in challenges}

    assert "normal-shock-m2" in ids
    assert "oblique-shock-m2-theta10" in ids
    assert "sod-x070-t020" in ids

    normal_shock = next(
        challenge
        for challenge in challenges
        if challenge["id"] == "normal-shock-m2"
    )

    assert abs(normal_shock["reference"]["p2_p1"] - 4.5) < 1e-10

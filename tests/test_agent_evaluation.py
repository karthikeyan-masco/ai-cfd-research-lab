import json
import subprocess
import sys

from ai_cfd_lab.evaluation.agent_evaluation import evaluate_debate, request_predictions
from ai_cfd_lab.evaluation.challenges import get_challenge
from ai_cfd_lab.providers.demo import DemoProvider


class ExactPredictionProvider(DemoProvider):
    def complete(self, *, system_prompt, user_prompt, role):
        if "scientific numerical prediction agent" in system_prompt:
            return json.dumps({"M2": 0.5773502691896257, "p2_p1": 4.5,
                               "rho2_rho1": 8 / 3, "T2_T1": 1.6875})
        return super().complete(system_prompt=system_prompt, user_prompt=user_prompt, role=role)


class BrokenPredictionProvider(DemoProvider):
    def complete(self, *, system_prompt, user_prompt, role):
        if "scientific numerical prediction agent" in system_prompt:
            return "```json\n{broken}\n```"
        return super().complete(system_prompt=system_prompt, user_prompt=user_prompt, role=role)


def test_exact_predictions_score_all():
    result = evaluate_debate(get_challenge("normal-shock-m2"), ExactPredictionProvider())
    assert len(result["attempts"]) == 3
    assert all(x["evaluation"]["score_percent"] == 100 for x in result["attempts"])
    assert result["debate"]["status"] == "completed"


def test_invalid_predictions_are_not_guessed():
    result = evaluate_debate(get_challenge("normal-shock-m2"), BrokenPredictionProvider())
    assert all(x["evaluation"]["score_percent"] == 0 for x in result["attempts"])
    assert all(x["error"] for x in result["attempts"])


def test_demo_is_not_misrepresented_as_physics_solution():
    result = evaluate_debate(get_challenge("normal-shock-m2"), DemoProvider())
    assert all(x["evaluation"]["score_percent"] == 0 for x in result["attempts"])


def test_cli_json():
    completed = subprocess.run([sys.executable, "-m", "ai_cfd_lab.evaluation.agent_evaluation",
                                "--id", "normal-shock-m2", "--provider", "demo"],
                               check=True, capture_output=True, text=True)
    result = json.loads(completed.stdout)
    assert result["challenge_id"] == "normal-shock-m2"
    assert len(result["attempts"]) == 3

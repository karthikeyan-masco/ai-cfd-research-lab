from __future__ import annotations
import json
from ai_cfd_lab.agents.prompts import ROLE_PROMPTS, JSON_INSTRUCTIONS
from ai_cfd_lab.debate.models import Submission


class Specialist:
    def __init__(self, role: str, provider):
        if role not in ROLE_PROMPTS:
            raise ValueError(f"Unknown agent role: {role}")
        self.role = role
        self.provider = provider

    def analyse(self, question: str, context: str = "") -> Submission:
        prompt = (
            f"RESEARCH QUESTION: {question}\n\n"
            f"DEBATE CONTEXT:\n{context or 'No prior submissions.'}\n\n"
            "Provide your independent technical analysis. Be explicit about missing information."
        )
        raw = self.provider.complete(
            system_prompt=ROLE_PROMPTS[self.role] + "\n" + JSON_INSTRUCTIONS,
            user_prompt=prompt,
            role=self.role,
        )
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError("Agent response must be a JSON object.")
            return Submission.from_dict(parsed, agent_fallback=self.role)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"{self.role} returned invalid structured output: {raw[:500]}") from exc

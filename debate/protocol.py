from __future__ import annotations
from ai_cfd_lab.agents.specialists import Specialist
from ai_cfd_lab.agents.prompts import ROLE_PROMPTS, JSON_INSTRUCTIONS
from ai_cfd_lab.debate.models import DebateRecord, Submission


class DebateEngine:
    """Bounded scientific debate. No tools or shell commands are executed by agents."""

    def __init__(self, provider, max_rounds: int = 3):
        if not 1 <= max_rounds <= 5:
            raise ValueError("max_rounds must be between 1 and 5.")
        self.provider = provider
        self.max_rounds = max_rounds
        self.theory = Specialist("theory", provider)
        self.cfd = Specialist("cfd", provider)
        self.reviewer = Specialist("reviewer", provider)

    @staticmethod
    def _format_submissions(items: list[Submission]) -> str:
        if not items:
            return "No submissions."
        chunks = []
        for item in items:
            chunks.append(
                f"AGENT: {item.agent}\nHYPOTHESIS: {item.hypothesis}\n"
                f"REASONING: {item.reasoning}\nEVIDENCE: {item.evidence}\n"
                f"ASSUMPTIONS: {item.assumptions}\nUNCERTAINTIES: {item.uncertainties}\n"
                f"PROPOSED TESTS: {item.proposed_tests}"
            )
        return "\n\n".join(chunks)

    def _coordinator_verdict(self, question: str, record: DebateRecord) -> Submission:
        context = (
            "INITIAL SUBMISSIONS:\n" + self._format_submissions(record.initial_submissions)
            + "\n\nREVIEWER CRITIQUES:\n" + self._format_submissions(record.critiques)
            + "\n\nREBUTTALS:\n" + self._format_submissions(record.rebuttals)
        )
        raw = self.provider.complete(
            system_prompt=ROLE_PROMPTS["coordinator"] + "\n" + JSON_INSTRUCTIONS,
            user_prompt=f"RESEARCH QUESTION: {question}\n\n{context}\n\nProduce the final synthesis.",
            role="coordinator",
        )
        import json
        try:
            return Submission.from_dict(json.loads(raw), "Research Coordinator")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Coordinator returned invalid JSON: {raw[:500]}") from exc

    def run(self, question: str) -> DebateRecord:
        if not question or not question.strip():
            raise ValueError("Research question cannot be empty.")
        question = question.strip()
        record = DebateRecord(question=question)

        # Independent first-pass submissions: neither specialist sees the other's answer.
        record.initial_submissions = [
            self.theory.analyse(question),
            self.cfd.analyse(question),
        ]

        for round_index in range(self.max_rounds):
            context = (
                f"ROUND {round_index + 1}\n"
                + self._format_submissions(record.initial_submissions)
                + "\n\nPREVIOUS CRITIQUES:\n"
                + self._format_submissions(record.critiques)
            )
            critique = self.reviewer.analyse(question, context)
            record.critiques.append(critique)

            # Bounded rebuttal: both specialists receive the same critique.
            rebuttal_context = (
                context + "\n\nREVIEWER CRITIQUE:\n" + self._format_submissions([critique])
            )
            record.rebuttals.append(self.theory.analyse(question, rebuttal_context))
            record.rebuttals.append(self.cfd.analyse(question, rebuttal_context))

            # Avoid unnecessary repeated debate when reviewer explicitly requests no more tests
            # only if the configured round limit has been reached; otherwise continue.
        verdict = self._coordinator_verdict(question, record)
        record.final_verdict = verdict.reasoning or verdict.hypothesis
        record.unresolved_issues = verdict.uncertainties
        record.recommended_tests = verdict.proposed_tests
        record.status = "completed"
        return record

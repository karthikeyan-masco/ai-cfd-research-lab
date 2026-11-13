from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Submission:
    agent: str
    hypothesis: str
    reasoning: str
    evidence: list[str] = field(default_factory=list)
    equations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)
    proposed_tests: list[str] = field(default_factory=list)
    confidence: float = 0.5
    response_to_critique: str = ""

    def __post_init__(self) -> None:
        self.confidence = min(1.0, max(0.0, float(self.confidence)))
        for name in ("evidence", "equations", "assumptions", "uncertainties", "proposed_tests"):
            value = getattr(self, name)
            if not isinstance(value, list):
                raise TypeError(f"{name} must be a list")

    @classmethod
    def from_dict(cls, data: dict[str, Any], agent_fallback: str = "Unknown") -> "Submission":
        allowed = {
            "agent", "hypothesis", "reasoning", "evidence", "equations",
            "assumptions", "uncertainties", "proposed_tests", "confidence",
            "response_to_critique",
        }
        clean = {k: v for k, v in data.items() if k in allowed}
        clean.setdefault("agent", agent_fallback)
        clean.setdefault("hypothesis", "No explicit hypothesis supplied.")
        clean.setdefault("reasoning", "")
        for key in ("evidence", "equations", "assumptions", "uncertainties", "proposed_tests"):
            if not isinstance(clean.get(key, []), list):
                clean[key] = [str(clean[key])]
        return cls(**clean)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DebateRecord:
    question: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    initial_submissions: list[Submission] = field(default_factory=list)
    critiques: list[Submission] = field(default_factory=list)
    rebuttals: list[Submission] = field(default_factory=list)
    final_verdict: str = ""
    unresolved_issues: list[str] = field(default_factory=list)
    recommended_tests: list[str] = field(default_factory=list)
    status: str = "in_progress"

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "created_at": self.created_at,
            "initial_submissions": [x.to_dict() for x in self.initial_submissions],
            "critiques": [x.to_dict() for x in self.critiques],
            "rebuttals": [x.to_dict() for x in self.rebuttals],
            "final_verdict": self.final_verdict,
            "unresolved_issues": self.unresolved_issues,
            "recommended_tests": self.recommended_tests,
            "status": self.status,
        }

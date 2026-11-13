from __future__ import annotations
from ai_cfd_lab.debate.models import DebateRecord


def to_markdown(record: DebateRecord) -> str:
    lines = [
        "# AI CFD Lab — Debate Report", "",
        f"**Question:** {record.question}", "",
        f"**Status:** {record.status}", "",
        "## Initial independent submissions",
    ]
    for s in record.initial_submissions:
        lines += [f"### {s.agent}", f"**Hypothesis:** {s.hypothesis}", s.reasoning, "",
                  f"**Evidence:** {', '.join(s.evidence) or 'None supplied'}",
                  f"**Assumptions:** {', '.join(s.assumptions) or 'None stated'}", ""]
    lines += ["## Reviewer critiques"]
    for s in record.critiques:
        lines += [f"### {s.agent}", s.hypothesis, s.reasoning, "",
                  f"**Proposed tests:** {', '.join(s.proposed_tests) or 'None'}", ""]
    lines += ["## Final verdict", record.final_verdict, "",
              "## Unresolved issues"]
    lines += [f"- {x}" for x in record.unresolved_issues] or ["- None recorded"]
    lines += ["", "## Recommended tests"]
    lines += [f"- {x}" for x in record.recommended_tests] or ["- None recorded"]
    lines += ["", "> Confidence scores are agent self-assessments, not calibrated probabilities. "
              "LLM outputs are not scientific validation."]
    return "\n".join(lines)

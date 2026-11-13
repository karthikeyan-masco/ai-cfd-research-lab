"""Render human-readable comparisons of saved evaluation experiments."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

from .experiment_registry import ExperimentRegistry


def _score(value: Any) -> float | None:
    """Accept finite numeric scores from 0 to 100, excluding booleans."""
    import math
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and 0 <= number <= 100 else None


def _format_score(value: Any) -> str:
    score = _score(value)
    return f"{score:.2f}%" if score is not None else "N/A"


def _extract_scores(results: Mapping[str, Any]) -> dict[str, float | None]:
    """Read explicit percentage fields; never infer from unrelated metrics."""
    return {
        name: _score(results.get(key))
        for name, key in (
            ("Theory", "theory_score"),
            ("CFD", "cfd_score"),
            ("Coordinator", "coordinator_score"),
        )
    }


def render_report(records: list[dict[str, Any]], challenge_id: str | None = None) -> str:
    """Create a Markdown report from ExperimentRegistry.list_runs() records."""
    title = "AI CFD Laboratory: Evaluation Report"
    lines = [f"# {title}", "", f"Challenge filter: `{challenge_id or 'all'}`", "", f"Runs: **{len(records)}**", ""]
    if not records:
        return "\n".join(lines + ["No experiments found.", ""])

    lines.extend([
        "| Run ID | Challenge | Provider | Timestamp (UTC) | Theory | CFD | Coordinator |",
        "|---|---|---|---|---:|---:|---:|",
    ])
    for record in records:
        results = record.get("results", {})
        if not isinstance(results, dict):
            results = {}
        scores = _extract_scores(results)
        safe = lambda x: str(x).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {safe(record.get('run_id', ''))} | {safe(record.get('challenge_id', ''))} | "
            f"{safe(record.get('provider', ''))} | {safe(record.get('timestamp', ''))} | "
            f"{_format_score(scores['Theory'])} | {_format_score(scores['CFD'])} | "
            f"{_format_score(scores['Coordinator'])} |"
        )
    lines.extend(["", "## Summary", ""])
    for role in ("Theory", "CFD", "Coordinator"):
        values = []
        for record in records:
            results = record.get("results", {})
            if isinstance(results, dict):
                score = _extract_scores(results)[role]
                if score is not None:
                    values.append(score)
        if values:
            lines.append(f"- {role}: mean **{sum(values)/len(values):.2f}%** over {len(values)} scored run(s).")
        else:
            lines.append(f"- {role}: no valid percentage scores available.")
    lines.extend([
        "", "Scores are only comparable when benchmarks, scoring rules, and model settings are comparable.",
        "Missing scores are shown as N/A, never as zero. This report does not establish scientific reasoning quality.", "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize stored CFD agent evaluation runs")
    parser.add_argument("--db", default="reports/experiments.db", help="SQLite experiment registry path")
    parser.add_argument("--challenge", help="Optional benchmark challenge ID")
    parser.add_argument("--out", help="Optional Markdown output path")
    args = parser.parse_args()
    registry = ExperimentRegistry(args.db)
    markdown = render_report(registry.list_runs(args.challenge), args.challenge)
    if args.out:
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(markdown, encoding="utf-8")
        print(f"Saved report: {destination}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()

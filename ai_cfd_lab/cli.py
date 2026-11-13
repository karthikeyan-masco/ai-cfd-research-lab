from __future__ import annotations
import argparse
import json
from pathlib import Path
from ai_cfd_lab.debate.protocol import DebateEngine
from ai_cfd_lab.debate.report import to_markdown
from ai_cfd_lab.providers.demo import DemoProvider


def main():
    parser = argparse.ArgumentParser(description="AI CFD Research Laboratory debate prototype")
    parser.add_argument("--question", default="For a Mach 2 normal shock, calculate downstream properties and identify numerical checks.")
    parser.add_argument("--demo", action="store_true", help="Use deterministic offline demo provider.")
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--out", default="reports/latest")
    args = parser.parse_args()

    provider = DemoProvider()
    if not args.demo:
        import os
        if os.getenv("AI_CFD_API_KEY") and os.getenv("AI_CFD_MODEL"):
            from ai_cfd_lab.providers.openai_compatible import OpenAICompatibleProvider
            provider = OpenAICompatibleProvider()
        else:
            print("No API credentials found; using offline demo provider. Set AI_CFD_API_KEY and AI_CFD_MODEL for live LLM use.")

    record = DebateEngine(provider, max_rounds=args.rounds).run(args.question)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text(to_markdown(record), encoding="utf-8")
    print(to_markdown(record))
    print(f"\nSaved: {out.with_suffix('.json')} and {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()

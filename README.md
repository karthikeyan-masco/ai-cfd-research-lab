# AI CFD Research Laboratory — Milestone 1

A debate-driven, evidence-aware multi-agent prototype for compressible-flow research.

## What this repository contains

- Four roles: Theory Specialist, CFD Numerics Specialist, Critical Reviewer, Research Coordinator.
- A three-round structured debate protocol with explicit hypotheses, evidence, assumptions, uncertainties and proposed tests.
- A provider interface with a deterministic offline demo provider. No API key is needed to run the demo or tests.
- Optional OpenAI-compatible chat-completions provider (configure endpoint/model/key through environment variables).
- Compressible-flow benchmark utilities:
  - normal-shock relations,
  - oblique-shock theta-beta-M relation and weak-shock angle solver,
  - exact Sod shock-tube Riemann solution (ideal gas, 1-D).
- Unit tests and a small Streamlit dashboard.

This is a research-workflow prototype, not a validated autonomous CFD solver. LLM outputs are hypotheses until checked against equations, source data or controlled computation.

## Requirements

- Python 3.10+
- Core tests and CLI demo use only the Python standard library.
- Optional dashboard: `streamlit`
- Optional API provider: `httpx`

## Quick start

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -e ".[dev]"
pytest
python -m ai_cfd_lab.cli --question "For a Mach 2.0 normal shock, calculate downstream properties and identify numerical checks."
```

Run the offline demo (no credentials required):

```bash
python -m ai_cfd_lab.cli --demo
```

Run the dashboard:

```bash
pip install -e ".[ui]"
streamlit run app/dashboard.py
```

## Optional LLM provider

The provider uses an OpenAI-compatible `/chat/completions` endpoint.

```bash
export AI_CFD_BASE_URL="https://api.openai.com/v1"
export AI_CFD_API_KEY="your-key"
export AI_CFD_MODEL="your-model-name"
python -m ai_cfd_lab.cli --question "..."
```

On PowerShell:

```powershell
$env:AI_CFD_BASE_URL="https://api.openai.com/v1"
$env:AI_CFD_API_KEY="your-key"
$env:AI_CFD_MODEL="your-model-name"
```

The key is read from the environment and is never written into the repository. Do not commit secrets.

## Architecture

```text
Question
  |
  v
Coordinator -> independent Theory + CFD proposals
  |                         |
  +------> Reviewer <-------+
              |
          critique/rebuttal rounds (bounded)
              |
         evidence/test requests
              |
        final coordinator synthesis
              |
       JSON + Markdown report
```

The initial implementation runs the agents sequentially for predictable cost and reproducibility. The provider interface allows different models to be assigned per role in a later iteration.

## Evidence policy

Every agent response is parsed into a structured submission. The coordinator does not treat confidence scores or majority agreement as proof. The reviewer can mark a claim as unsupported, and the final report preserves unresolved issues. Numerical benchmark functions are deterministic and independently tested.

## First benchmark checks

```bash
python -m ai_cfd_lab.benchmarks normal-shock --mach 2.0
python -m ai_cfd_lab.benchmarks oblique-shock --mach 2.0 --theta-deg 10
python -m ai_cfd_lab.benchmarks sod --x 0.7 --time 0.2
```

The Sod command reports the exact ideal-gas solution at a requested location and time for the standard initial condition.

## Project structure

```text
ai_cfd_lab/
  agents/       role prompts and structured agent wrappers
  debate/       state, protocol, evaluation and report generation
  benchmarks/   analytical compressible-flow benchmarks
  providers/    offline and API-backed model providers
  tests/        benchmark and debate tests
  app/          Streamlit interface
  cli.py        command-line entry point
```

## Safety and limitations

- No OpenFOAM execution is included in this milestone.
- No agent can execute shell commands or alter files.
- API output is untrusted input and is validated before use.
- Numerical functions implement ideal-gas assumptions; state those assumptions when interpreting results.
- The oblique-shock solver returns the weak attached-shock solution. It raises an error if no attached solution exists for the requested deflection.
- The Sod solver assumes a calorically perfect gas, zero initial velocity and a single initial discontinuity.

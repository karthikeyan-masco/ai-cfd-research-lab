# Milestone 2.3: Agent numerical evaluation

Extract this ZIP into the project root `C:\Masco\ai_cfd_lab`.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ai_cfd_lab.evaluation.agent_evaluation --id normal-shock-m2 --provider demo --out reports\m2_3_demo.json
```

The offline demo provider is not a physics solver and returns no structured numerical predictions; expect **0%**, not 100%. This is intentional. To evaluate real model predictions, configure the existing OpenAI-compatible provider and use `--provider api`. The API provider requires credentials and may incur charges.

Scores are per-output accuracy against deterministic benchmarks; they do not establish reasoning correctness, calibration, or that debate causes improvement. Initial predictions are requested separately from the debate, and final predictions are requested after the coordinator verdict. No shell commands are executed by agents.

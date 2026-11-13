# Milestone 2.2 patch

Extract this archive into the project root `C:\Masco\ai_cfd_lab`, preserving folders.

Run:

```powershell
.\.venv\Scripts\python.exe -m ai_cfd_lab.evaluation.scoring --id normal-shock-m2 --predictions examples/normal_shock_predictions.json
.\.venv\Scripts\python.exe -m pytest -q
```

Scoring is deterministic and independent of agent prose. The default threshold is `abs(error) <= 1e-8 + 0.01 * abs(reference)`; one point per required quantity. Missing, invalid or out-of-tolerance values receive zero. Unknown keys are reported but do not affect the denominator. `relative_error` is null for nonzero error when reference is zero. This does not validate units, equations, numerical methods or physical assumptions.

This patch does not alter existing files or automatically parse free-form LLM responses. Structured predictions are supplied as JSON.

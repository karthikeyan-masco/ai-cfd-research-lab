# Milestone 2.4: Reporting module

Extract this patch into the project root (`C:\Masco\ai_cfd_lab`).

This patch depends on `ai_cfd_lab/evaluation/experiment_registry.py` from the previous step.

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Generate a report from the default database:

```powershell
.\.venv\Scripts\python.exe -m ai_cfd_lab.evaluation.reporting --db reports\experiments.db --out reports\summary.md
```

**Note:** The previous agent-evaluation CLI saves a JSON file, but does not automatically insert that file into SQLite. Until a separate integration is implemented, this report displays only experiments explicitly saved using `ExperimentRegistry.save(...)`.

The report recognizes percentage fields named `theory_score`, `cfd_score`, and `coordinator_score` (range 0 to 100). Other result schemas are displayed as N/A rather than silently misinterpreted.

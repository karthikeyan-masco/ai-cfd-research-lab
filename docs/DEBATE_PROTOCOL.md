# Scientific Debate Protocol

## Required output from each specialist

1. Hypothesis — a falsifiable explanation or proposed interpretation.
2. Reasoning — physical or numerical rationale.
3. Evidence — references, computed values or supplied observations; never invented.
4. Equations — governing relations relevant to the claim.
5. Assumptions — explicit simplifications.
6. Uncertainties — missing or weakly constrained information.
7. Proposed tests — actions that could distinguish competing explanations.
8. Confidence — subjective self-assessment only.

## Rules

- First-pass theory and CFD agents work independently.
- The reviewer receives both submissions and actively searches for unsupported reasoning.
- Specialists receive the critique and can revise or defend their positions.
- Debate is bounded to a configurable maximum of three rounds.
- Coordinator may return an inconclusive verdict.
- Majority vote is not a correctness criterion.
- A claim is not marked verified merely because multiple agents repeat it.
- Calculations must be produced by deterministic benchmark or analysis code and stored with inputs.
- Published evidence must retain bibliographic metadata and page/section references.
- No LLM-generated shell command is executed.

## Future extension

Add typed evidence objects with provenance:
`source_type`, `source_id`, `locator`, `input_hash`, `tool_version`, `result_hash`,
`units`, `uncertainty`, and `verification_status`.

from __future__ import annotations
import json


class DemoProvider:
    """Deterministic offline provider for wiring tests and demonstrations."""

    def complete(self, *, system_prompt: str, user_prompt: str, role: str) -> str:
        question = user_prompt.split("RESEARCH QUESTION:", 1)[-1].strip().splitlines()[0]
        if role == "theory":
            data = {
                "agent": "Theory Specialist",
                "hypothesis": "Establish the governing ideal-gas compressible-flow relations before attributing discrepancies to physics.",
                "reasoning": "The question must be reduced to a clearly specified physical state and assumptions. Analytical relations provide an independent baseline.",
                "evidence": ["No case-specific numerical or experimental evidence has yet been supplied."],
                "equations": ["For a normal shock, use conservation of mass, momentum and energy with a calorically perfect gas."],
                "assumptions": ["Ideal gas", "Constant ratio of specific heats unless stated otherwise"],
                "uncertainties": ["The actual gas model and boundary conditions are not specified."],
                "proposed_tests": ["Compute an analytical benchmark using the stated upstream state.", "Check dimensional consistency and conservation residuals."],
                "confidence": 0.72
            }
        elif role == "cfd":
            data = {
                "agent": "CFD Numerics Specialist",
                "hypothesis": "A numerical explanation cannot be selected until mesh, scheme, time-step and convergence evidence are inspected.",
                "reasoning": "Shock-capturing accuracy depends on spatial resolution, numerical flux, limiter, CFL and iterative or temporal convergence.",
                "evidence": ["No mesh, solver log or field data was supplied."],
                "equations": ["Check finite-volume conservation and the relevant nondimensional stability criteria."],
                "assumptions": ["The solver is intended to solve the compressible conservation equations."],
                "uncertainties": ["Mesh topology, numerical flux, order of accuracy and convergence history are unknown."],
                "proposed_tests": ["Perform systematic mesh refinement.", "Compare at least two suitable shock-capturing schemes.", "Check mass, momentum and energy conservation."],
                "confidence": 0.78
            }
        elif role == "reviewer":
            data = {
                "agent": "Critical Reviewer",
                "hypothesis": "The current evidence is insufficient to identify a unique physical or numerical cause.",
                "reasoning": "Both initial specialists correctly identify missing information, but neither has case-specific evidence. Agreement on a plausible checklist is not proof.",
                "evidence": ["The question contains no numerical configuration, reference dataset or measured result."],
                "equations": [],
                "assumptions": ["The supplied problem statement is complete as received."],
                "uncertainties": ["No unique diagnosis can be established."],
                "proposed_tests": ["Request the exact geometry, gas properties, boundary conditions, mesh, solver settings and comparison data."],
                "confidence": 0.94
            }
        else:
            data = {
                "agent": "Research Coordinator",
                "hypothesis": "The next defensible step is to define a reproducible benchmark and collect missing case information.",
                "reasoning": "The specialists agree that a diagnosis requires evidence. Do not select a root cause by majority vote.",
                "evidence": ["The submitted discussion contains no case-specific computational results."],
                "equations": [],
                "assumptions": [],
                "uncertainties": ["Root cause remains undetermined."],
                "proposed_tests": ["Run a verified analytical benchmark before investigating a complex CFD case."],
                "confidence": 0.9
            }
        return json.dumps(data)

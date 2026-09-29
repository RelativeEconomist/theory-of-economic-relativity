"""
Public TER research API.

Researchers and test authors should primarily import from here:

    from research.ter import (
        AgentSpec,
        AgentGroup,
        Scenario,
        ScenarioResult,
        AgentResult,
        DecisionProcess,
        ValuationRule,
        RealityRule,
        TransitionRule,
        ObservationRule,
        UpdateRule,
        RealityResult,
        Schedule,
        run_scenario,
    )

Framework internals (AgentState, register_rule, get_rule, build_agent,
select_action) are not part of this surface. They remain importable from
their own modules for advanced or internal use, but should not normally
be needed to define or run a scenario.
"""

from pathlib import Path

from research.ter.reality import RealityResult
from research.ter.rules import (
    DecisionProcess,
    ObservationRule,
    RealityRule,
    TransitionRule,
    UpdateRule,
    ValuationRule,
)
from research.ter.runner import run_scenario
from research.ter.schedule import Schedule
from research.ter.scenario import AgentGroup, AgentResult, AgentSpec, Scenario, ScenarioResult

__version__ = (Path(__file__).resolve().parents[2] / "VERSION").read_text().strip()

__all__ = [
    "AgentSpec",
    "AgentGroup",
    "Scenario",
    "ScenarioResult",
    "AgentResult",
    "DecisionProcess",
    "ValuationRule",
    "RealityRule",
    "TransitionRule",
    "ObservationRule",
    "UpdateRule",
    "RealityResult",
    "Schedule",
    "run_scenario",
    "__version__",
]

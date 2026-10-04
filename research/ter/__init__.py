"""
Public TER research API.

Researchers and test authors should primarily import from here:

    from research.ter import (
        AgentSpec,
        AgentGroup,
        Scenario,
        ScenarioResult,
        AgentResult,
        RealityResult,
        Schedule,
        run_scenario,
    )

Shared rule functions are imported directly from research.ter.rules.
Framework internals (AgentState, build_agent, select_action) remain
importable from their own modules for advanced or internal use, but should
not normally be needed to define or run a scenario.
"""

from pathlib import Path

from research.ter.reality import RealityResult
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
    "RealityResult",
    "Schedule",
    "run_scenario",
    "__version__",
]

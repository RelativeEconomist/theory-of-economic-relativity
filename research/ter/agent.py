from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class AgentState:
    """
    Minimal executable representation of the TER agent decision state.

    TER mapping:
    G     -> objective
    M     -> model_of_reality
    F     -> actual_feasible_set
    F_hat -> perceived_feasible_set
    V     -> valuation + value function
    H     -> horizon
    D     -> decision_process

    name is not a TER primitive. It is carried over from AgentSpec so
    agents remain identifiable through execution (e.g. ScenarioResult.agent).

    valuation is not a new TER primitive. It is implementation storage
    for TER V -- declarative valuation data (e.g. a static value map)
    that a value rule reads, kept separate from model_of_reality (M) so
    valuation data is not stored inside the agent's model of reality.

    decision_parameters is likewise not a new TER primitive. It is
    implementation configuration for D (e.g. a search depth), kept
    separate from model_of_reality for the same reason.
    """

    objective: Any
    model_of_reality: Any
    actual_feasible_set: list[Any]
    perceived_feasible_set: list[Any]
    value: Callable[[Any, "AgentState"], float]
    horizon: Any
    decision_process: Callable[["AgentState"], Any]
    name: str
    valuation: dict[str, Any]
    decision_parameters: dict[str, Any]

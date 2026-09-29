from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from research.ter.agent import AgentState
from research.ter.immutable import freeze, thaw


@dataclass(frozen=True)
class Observation:
    """
    What one agent receives about a realized outcome at one decision
    point: the only path from reality back to the agent (Model 5.5).

        O_t -> information available to agent i -> (G, M, F_hat, V, H)_i,t+1

    TER does not assume agents observe the full system outcome, or
    observe it without error. The scenario's observation rule decides,
    per agent, what arrives here; an agent with no Observation at a
    point learns nothing from it. data is frozen, so what an agent was
    told cannot be rewritten after the fact.
    """

    agent: str
    step: int
    data: Mapping[str, Any]

    def __post_init__(self):
        object.__setattr__(self, "data", freeze(dict(self.data)))

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


@dataclass(frozen=True)
class UpdateView:
    """
    What an agent's update rule is permitted to read: the agent's own
    current decision-relevant state, and nothing about reality except
    the Observation it is handed alongside.

    F_t, the RealityResult, other agents' state, and the decision/value
    callables are deliberately absent. An update rule turning an
    observation into a new M or F_hat cannot reach around the
    information the agent actually received.

    Every field is an independent mutable copy: an update rule may build
    its return value from them freely without touching live state.
    """

    name: str
    objective: Any
    model_of_reality: Any
    perceived_feasible_set: list[Any]
    horizon: Any
    valuation: dict[str, Any]
    decision_parameters: dict[str, Any]


# The agent-side components an update rule may replace. D and V's rule
# (the callables) are fixed for the run; changing them is out of scope
# until a specification needs it.
UPDATABLE_FIELDS = frozenset({
    "objective",
    "model_of_reality",
    "perceived_feasible_set",
    "horizon",
    "valuation",
    "decision_parameters",
})


def update_view(agent: AgentState) -> UpdateView:
    return UpdateView(
        name=agent.name,
        objective=thaw(agent.objective),
        model_of_reality=thaw(agent.model_of_reality),
        perceived_feasible_set=thaw(agent.perceived_feasible_set),
        horizon=thaw(agent.horizon),
        valuation=thaw(agent.valuation),
        decision_parameters=thaw(agent.decision_parameters),
    )

from dataclasses import dataclass
from typing import Any, Callable

from research.ter.agent import AgentState


@dataclass(frozen=True)
class DecisionView:
    """
    The decision-side view of an agent: exactly what TER Model 5.1's D is
    permitted to read.

        C = D(F_hat, G, M, V, H)

    perceived_feasible_set, objective, model_of_reality, value, and
    horizon are F_hat, G, M, V, and H respectively. valuation,
    decision_parameters, and name are the same implementation-only
    storage AgentState carries alongside V and D elsewhere in TER (see
    AgentState's docstring); they accompany this view for the same
    reason.

    F_t (the objective feasible state of reality) is deliberately
    absent: it is part of the objective environment the agent's action
    encounters, but it is not a direct input to D. Whether F_t permits
    C, and what outcome follows, are Model 5.2 concerns, handled only
    after C is selected, on the reality/outcome side
    (research.ter.outcome.is_actually_feasible, then the reality
    function). Leaving F_t out of this view is what makes that boundary
    mechanical rather than a matter of decision-rule discipline.
    """

    objective: Any
    model_of_reality: Any
    perceived_feasible_set: list[Any]
    value: Callable[[Any, "DecisionView"], float]
    horizon: Any
    name: str
    valuation: dict[str, Any]
    decision_parameters: dict[str, Any]


def _decision_view(agent: AgentState) -> DecisionView:
    return DecisionView(
        objective=agent.objective,
        model_of_reality=agent.model_of_reality,
        perceived_feasible_set=agent.perceived_feasible_set,
        value=agent.value,
        horizon=agent.horizon,
        name=agent.name,
        valuation=agent.valuation,
        decision_parameters=agent.decision_parameters,
    )


def select_action(agent: AgentState):
    """
    Execute TER Model 5.1:

        C = D(F_hat, G, M, V, H)

    The specific behavior of D is supplied by the model or test. TER does
    not require optimization.

    D is called with a DecisionView, not the full AgentState: F_t is not
    a direct input to D. Whether F_t permits C is checked later, on the
    reality/outcome side, without rewriting C.
    """
    if not agent.perceived_feasible_set:
        raise ValueError("Perceived feasible set cannot be empty.")

    selected = agent.decision_process(_decision_view(agent))

    if selected not in agent.perceived_feasible_set:
        raise ValueError(
            "Decision process selected an action outside the perceived feasible set."
        )

    return selected
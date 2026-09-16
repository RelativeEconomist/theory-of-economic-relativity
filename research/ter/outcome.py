from dataclasses import dataclass
from typing import Any

from research.ter.agent import AgentState


@dataclass(frozen=True)
class RealityView:
    """
    The reality-side view of an agent: exactly what TER Model 5.2's R is
    permitted to read.

        O = R(C, F, P, S)

    name identifies which agent a joint action/outcome entry belongs to
    -- the same bookkeeping role AgentResult already keys results by; it
    is not a TER primitive. actual_feasible_set is F. C arrives as R's
    own `actions` argument (parallel to `agents` by position), and P/S
    are `state`/`parameters` -- neither travels on this view.

    model_of_reality (M), perceived_feasible_set (F_hat), valuation (V),
    decision_parameters, and the decision/value callables are
    deliberately absent. Those are decision-side inputs to D (Model
    5.1); R computing what actually happens from what an agent merely
    believes, perceives as an option, or privately values would treat
    belief as reality. Leaving them off this view is what makes that
    boundary mechanical rather than a matter of reality-rule discipline.
    """

    name: str
    actual_feasible_set: list[Any]


def reality_view(agent: AgentState) -> RealityView:
    """
    Project an AgentState down to the reality-side view a reality
    function is allowed to see.
    """
    return RealityView(
        name=agent.name,
        actual_feasible_set=agent.actual_feasible_set,
    )


def is_actually_feasible(agent: Any, action: Any) -> bool:
    """
    Check the TER Model 5.2 reality boundary:

        C_i,t in F_i,t   or   C_i,t not in F_i,t

    Returns whether the agent's selected action is actually feasible.

    Accepts either a full AgentState or a RealityView -- both carry
    actual_feasible_set, which is all this check reads.

    This checks membership only. It does not determine the realized
    outcome, does not re-run the agent's decision process, and does not
    select a fallback action. The consequence of C not belonging to F
    (failure, partial execution, or another changed outcome) is entirely
    the responsibility of the scenario's own reality/outcome rule.
    """
    return action in agent.actual_feasible_set

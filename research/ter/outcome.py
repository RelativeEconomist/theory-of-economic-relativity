from dataclasses import dataclass
from typing import Any

from research.ter.agent import AgentState


@dataclass(frozen=True)
class RealityView:
    """
    The reality-side view of an agent: exactly what TER Model 5.2's R is
    permitted to read about an agent.

        O_i,t = R(C_i,t, F_t)

    name identifies which agent a joint action/outcome entry belongs to
    -- the same bookkeeping role AgentResult already keys results by; it
    is not a TER primitive. C arrives as R's own `actions` argument
    (parallel to `agents` by position). F_t is not agent specific, so it
    does not travel on this view: R reads it from `state` and
    `parameters`.

    model_of_reality (M), perceived_feasible_set (F_hat), valuation (V),
    decision_parameters, and the decision/value callables are
    deliberately absent. Those are decision-side inputs to D (Model
    5.1); R computing what actually happens from what an agent merely
    believes, perceives as an option, or privately values would treat
    belief as reality. Leaving them off this view is what makes that
    boundary mechanical rather than a matter of reality-rule discipline.
    """

    name: str


def reality_view(agent: AgentState) -> RealityView:
    """
    Project an AgentState down to the reality-side view a reality
    function is allowed to see.
    """
    return RealityView(name=agent.name)


def permitted_actions_for(state: dict[str, Any], agent: Any) -> list[Any]:
    """
    Look up the actions the scenario permits for one agent.

    Permission data maps agent names to actions permitted by the relevant
    scenario constraints, considered individually (not as a joint action
    profile): state["permitted_actions"][agent name]. It is an
    implementation representation of a scenario-relevant aspect of F_t,
    the objective feasible state of reality, not F_t itself; F_t is not
    agent specific. It is a lookup, not a TER primitive, and it is not
    agent state -- no AgentState or AgentSpec carries it.

    Accepts an AgentState or a RealityView; only `.name` is read.
    """
    try:
        return state["permitted_actions"][agent.name]
    except KeyError:
        raise ValueError(
            "state['permitted_actions'] has no entry for agent "
            f"{agent.name!r}. Declare the actions F_t permits for each "
            "agent in the scenario's initial_state."
        ) from None


def is_actually_feasible(state: dict[str, Any], agent: Any, action: Any) -> bool:
    """
    Does the scenario's permission data permit this individual agent
    action?

    Returns whether the given action is among the actions permitted for
    that one agent, per state["permitted_actions"] (see
    permitted_actions_for).

    This is a per-agent membership check only. It does not mean:

    - the full joint action profile is feasible -- two agents' actions
      can each be permitted while their joint execution cannot both
      succeed (e.g. two buyers each permitted to buy one unit that only
      exists once);
    - the action will succeed; or
    - the realized outcome is known.

    Interaction, scarcity, conflicts, and the realized outcome are
    resolved by the scenario's own reality function R. This helper does
    not re-run the agent's decision process and does not select a
    fallback action; the consequence of an action not being permitted
    (failure, partial execution, or another changed outcome) is likewise
    R's responsibility.
    """
    return action in permitted_actions_for(state, agent)

from typing import Any


def permitted_actions_for(objective_state: dict[str, Any], agent: Any) -> list[Any]:
    """
    Look up the actions the scenario permits for one agent.

    Permission data maps agent names to actions permitted by the relevant
    scenario constraints, considered individually (not as a joint action
    profile): objective_state["permitted_actions"][agent name]. It is an
    implementation representation of a scenario-relevant aspect of F_t,
    the objective feasible state of reality, not F_t itself; F_t is not
    agent specific. It is a lookup, not a TER primitive, and it is not
    agent state -- no AgentState or AgentSpec carries it.

    Accepts an agent name, or anything with a `.name` (e.g. an
    AgentState); only the name is read. A reality rule receives actions
    keyed by name, so it passes the name directly.
    """
    name = agent if isinstance(agent, str) else agent.name

    try:
        return objective_state["permitted_actions"][name]
    except KeyError:
        raise ValueError(
            "objective_state['permitted_actions'] has no entry for agent "
            f"{name!r}. Declare the actions F_t permits for each "
            "agent in the scenario's initial_state."
        ) from None


def is_actually_feasible(objective_state: dict[str, Any], agent: Any, action: Any) -> bool:
    """
    Does the scenario's permission data permit this individual agent
    action?

    Returns whether the given action is among the actions permitted for
    that one agent, per objective_state["permitted_actions"] (see
    permitted_actions_for).

    This is a per-agent membership check only. It does not mean:

    - the full joint action profile is feasible -- two agents' actions
      can each be permitted while their joint execution cannot both
      succeed (e.g. two buyers each permitted to buy one unit that only
      exists once);
    - the action will succeed; or
    - the realized outcome is known.

    Interaction, scarcity, conflicts, and the realized outcome are
    resolved by the scenario's own reality rule R. This helper does
    not re-run the agent's decision process and does not select a
    fallback action; the consequence of an action not being permitted
    (failure, partial execution, or another changed outcome) is likewise
    R's responsibility.
    """
    return action in permitted_actions_for(objective_state, agent)

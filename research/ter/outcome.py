from typing import Any

from research.ter.agent import AgentState


def is_actually_feasible(agent: AgentState, action: Any) -> bool:
    """
    Check the TER Model 5.2 reality boundary:

        C_i,t in F_i,t   or   C_i,t not in F_i,t

    Returns whether the agent's selected action is actually feasible.

    This checks membership only. It does not determine the realized
    outcome, does not re-run the agent's decision process, and does not
    select a fallback action. The consequence of C not belonging to F
    (failure, partial execution, or another changed outcome) is entirely
    the responsibility of the scenario's own reality/outcome rule.
    """
    return action in agent.actual_feasible_set

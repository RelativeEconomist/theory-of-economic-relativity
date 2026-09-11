from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from research.ter.agent import AgentState
from research.ter.decision import select_action


@dataclass
class SystemResult:
    """
    Result of one TER multi-agent interaction period.
    """

    actions: list[Any]
    outcome: Any


def run_system(
    agents: list[AgentState],
    outcome_function: Callable[[list[AgentState], list[Any]], Any],
) -> SystemResult:
    """
    Execute a minimal TER Model 5.3 interaction step.

    Each agent selects an action through the shared TER decision model:

        C_i = D_i(F_hat_i, G_i, M_i, V_i, H_i)

    The supplied outcome function determines the system outcome
    from the interacting actions.

    Conceptually:

        {C_i} -> O
    """
    actions = [
        select_action(agent)
        for agent in agents
    ]

    outcome = outcome_function(
        agents,
        actions,
    )

    return SystemResult(
        actions=actions,
        outcome=outcome,
    )
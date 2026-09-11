from research.ter.agent import AgentState


def select_action(agent: AgentState):
    """
    Execute TER Model 5.1:

        C = D(F_hat, G, M, V, H)

    The specific behavior of D is supplied by the model or test.
    TER does not require optimization.
    """
    if not agent.perceived_feasible_set:
        raise ValueError("Perceived feasible set cannot be empty.")

    selected = agent.decision_process(agent)

    if selected not in agent.perceived_feasible_set:
        raise ValueError(
            "Decision process selected an action outside the perceived feasible set."
        )

    return selected
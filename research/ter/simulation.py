from collections.abc import Callable
from typing import Any


def simulate(
    initial_state: Any,
    periods: int,
    step_function: Callable[[Any, int], Any],
):
    """
    Run a TER model forward through time.

    Conceptually:

        state_t
            -> decisions
            -> outcomes
            -> feedback
            -> state_t+1

    The model-specific step function defines what happens during
    each period.

    Returns the complete state history, including the initial state.
    """
    history = [initial_state]

    state = initial_state

    for period in range(periods):
        state = step_function(
            state,
            period,
        )

        history.append(state)

    return history
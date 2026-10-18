"""
Validation for the action_values that adapters accept from JSON requests.
"""

import math

# Generous for a pedagogical scenario; keeps request values to a sane size.
MAX_ABS_ACTION_VALUE = 1_000_000_000_000


def validate_action_values(action_values, actions: frozenset) -> None:
    """
    Raise unless action_values gives one finite, in-range number for each
    of the scenario's actions and nothing else.
    """
    if not isinstance(action_values, dict):
        raise TypeError("action_values must be a dict of action -> value.")

    if set(action_values) != actions:
        raise ValueError(
            f"action_values must give exactly these actions: {sorted(actions)}"
        )

    for action, value in action_values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Value for {action!r} must be a number.")

        # Only floats can be non-finite; math.isfinite would overflow on huge ints.
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"Value for {action!r} must be finite.")

        # abs() and int/float comparison are exact, so huge ints never become floats.
        if abs(value) > MAX_ABS_ACTION_VALUE:
            raise ValueError(
                f"Value for {action!r} is out of range; "
                f"it must be between -{MAX_ABS_ACTION_VALUE} and {MAX_ABS_ACTION_VALUE}."
            )

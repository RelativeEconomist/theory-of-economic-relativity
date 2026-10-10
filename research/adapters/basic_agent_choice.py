"""
JSON-safe adapter for the Basic Agent Choice scenario.

Request:

    {
        "scenario": "basic-agent-choice",
        "action_values": {"coffee_a": 4, "coffee_b": 7, "coffee_c": 10},
    }

action_values is optional; without it the reusable SCENARIO runs as is.

Response:

    {
        "scenario": "basic-agent-choice",
        "name": "Coffee Buyer",
        "selected_action": "coffee_c",
        "action_values": {"coffee_a": 4, "coffee_c": 10, "coffee_b": 7},
    }
"""

import math

from research.scenarios.basic_agent_choice import BASE_AGENT, SCENARIO
from research.ter import Scenario, run_scenario

SCENARIO_ID = "basic-agent-choice"

ACTIONS = frozenset(BASE_AGENT.valuation["values"])
REQUEST_KEYS = frozenset({"scenario", "action_values"})

# Generous for a pedagogical scenario; keeps request values to a sane size.
MAX_ABS_ACTION_VALUE = 1_000_000_000_000


def build_scenario(request: dict) -> Scenario:
    """
    Validate a request and return the reusable SCENARIO, or a variant of
    it with the agent's action values replaced.
    """
    if not isinstance(request, dict):
        raise TypeError("Request must be a dict.")

    if request.get("scenario") != SCENARIO_ID:
        raise ValueError(
            f"Unsupported scenario {request.get('scenario')!r}; "
            f"expected {SCENARIO_ID!r}."
        )

    unknown = sorted(set(request) - REQUEST_KEYS)

    if unknown:
        raise ValueError(f"Unknown request key(s): {unknown}")

    if "action_values" not in request:
        return SCENARIO

    action_values = request["action_values"]

    if not isinstance(action_values, dict):
        raise TypeError("action_values must be a dict of action -> value.")

    if set(action_values) != ACTIONS:
        raise ValueError(
            f"action_values must give exactly these actions: {sorted(ACTIONS)}"
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

    agent = BASE_AGENT.variant(valuation={"values": dict(action_values)})

    return SCENARIO.variant(agents=[agent])


def run(request: dict) -> dict:
    """
    Run the Basic Agent Choice scenario for a JSON-safe request and return
    a JSON-safe summary: the selected action and the agent's value for
    each perceived feasible action.
    """
    scenario = build_scenario(request)
    agent = run_scenario(scenario).agent(BASE_AGENT.name)

    return {
        "scenario": SCENARIO_ID,
        "name": scenario.name,
        "selected_action": agent.selected_action,
        "action_values": {
            action: agent.value_of(action)
            for action in agent.state.perceived_feasible_set
        },
    }

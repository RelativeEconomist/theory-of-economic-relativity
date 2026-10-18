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

from research.adapters.action_values import validate_action_values
from research.scenarios.basic_agent_choice import BASE_AGENT, SCENARIO
from research.ter import Scenario, run_scenario

SCENARIO_ID = "basic-agent-choice"

ACTIONS = frozenset(BASE_AGENT.valuation["values"])
REQUEST_KEYS = frozenset({"scenario", "action_values"})


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
    validate_action_values(action_values, ACTIONS)

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

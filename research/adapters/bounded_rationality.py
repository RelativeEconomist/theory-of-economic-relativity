"""
JSON-safe adapter for the Bounded Rationality scenario.

Request:

    {
        "scenario": "bounded-rationality",
        "decision_process": "limited_search",
        "action_values": {"nearby_coffee": 6, "office_coffee": 7, "best_coffee": 10},
        "search_limit": 2,
        "search_order": ["nearby_coffee", "office_coffee", "best_coffee"],
    }

Every key but scenario is optional; omitted ones keep the reusable
scenario's values. decision_process is "maximize_value" or
"limited_search" (the default). search_limit and search_order configure
limited_search only.

Response:

    {
        "scenario": "bounded-rationality",
        "name": "Coffee Buyer",
        "decision_process": "limited_search",
        "selected_action": "office_coffee",
        "selected_value": 7,
        "considered_actions": ["nearby_coffee", "office_coffee"],
        "not_considered_actions": ["best_coffee"],
        "action_values": {"nearby_coffee": 6, "office_coffee": 7, "best_coffee": 10},
        "search_limit": 2,
        "search_order": ["nearby_coffee", "office_coffee", "best_coffee"],
    }

search_limit and search_order are returned for limited_search only.
"""

from research.adapters.action_values import validate_action_values
from research.scenarios.bounded_rationality import (
    BASE_AGENT,
    EXHAUSTIVE_SCENARIO,
    LIMITED_SCENARIO,
)
from research.ter import Scenario, run_scenario
from research.ter.rules import limited_search_considered_actions

SCENARIO_ID = "bounded-rationality"

MAXIMIZE_VALUE = "maximize_value"
LIMITED_SEARCH = "limited_search"

# Both scenarios share G, M, F_hat, V, and H; only D differs.
SCENARIOS = {
    MAXIMIZE_VALUE: EXHAUSTIVE_SCENARIO,
    LIMITED_SEARCH: LIMITED_SCENARIO,
}

ACTIONS = frozenset(BASE_AGENT.valuation["values"])
SEARCH_KEYS = frozenset({"search_limit", "search_order"})
REQUEST_KEYS = frozenset({"scenario", "decision_process", "action_values"}) | SEARCH_KEYS


def build_scenario(request: dict) -> Scenario:
    """
    Validate a request and return the reusable scenario for its decision
    process, with the agent's action values and search configuration
    replaced where the request gives them.
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

    decision_process = request.get("decision_process", LIMITED_SEARCH)

    # A tuple, not the SCENARIOS dict, so unhashable values fail cleanly.
    if decision_process not in (MAXIMIZE_VALUE, LIMITED_SEARCH):
        raise ValueError(
            f"decision_process must be {MAXIMIZE_VALUE!r} or {LIMITED_SEARCH!r}; "
            f"got {decision_process!r}."
        )

    search = {key: request[key] for key in sorted(SEARCH_KEYS) if key in request}

    if search and decision_process != LIMITED_SEARCH:
        raise ValueError(
            f"{sorted(search)} configure {LIMITED_SEARCH!r} only; "
            f"remove them for {decision_process!r}."
        )

    scenario = SCENARIOS[decision_process]
    (agent,) = scenario.agents
    overrides = {}

    if "action_values" in request:
        validate_action_values(request["action_values"], ACTIONS)
        overrides["valuation"] = {"values": dict(request["action_values"])}

    if "search_limit" in search:
        validate_search_limit(search["search_limit"])

    if "search_order" in search:
        validate_search_order(search["search_order"])

    if search:
        overrides["decision_parameters"] = {**agent.decision_parameters, **search}

    return scenario.variant(agents=[agent.variant(**overrides)])


def validate_search_limit(search_limit) -> None:
    """Raise unless search_limit is a whole number from 1 to the number of actions."""
    if isinstance(search_limit, bool) or not isinstance(search_limit, int):
        raise TypeError("search_limit must be a whole number.")

    if not 1 <= search_limit <= len(ACTIONS):
        raise ValueError(f"search_limit must be from 1 to {len(ACTIONS)}.")


def validate_search_order(search_order) -> None:
    """Raise unless search_order lists every action exactly once."""
    if not isinstance(search_order, list):
        raise TypeError("search_order must be a list of actions.")

    # Check the item types first so set() never meets an unhashable item.
    if not (
        len(search_order) == len(ACTIONS)
        and all(isinstance(action, str) for action in search_order)
        and set(search_order) == ACTIONS
    ):
        raise ValueError(
            f"search_order must list each of these actions exactly once: {sorted(ACTIONS)}"
        )


def run(request: dict) -> dict:
    """
    Run the Bounded Rationality scenario for a JSON-safe request and return
    a JSON-safe summary: the selected action and its value, which perceived
    feasible actions the decision process considered, and the agent's
    value for each perceived feasible action.
    """
    scenario = build_scenario(request)
    agent = run_scenario(scenario).agent(BASE_AGENT.name)
    decision_process = request.get("decision_process", LIMITED_SEARCH)
    perceived_feasible_set = agent.state.perceived_feasible_set

    if decision_process == LIMITED_SEARCH:
        considered = list(limited_search_considered_actions(agent.state))
    else:
        # maximize_value values every perceived feasible action.
        considered = list(perceived_feasible_set)

    result = {
        "scenario": SCENARIO_ID,
        "name": scenario.name,
        "decision_process": decision_process,
        "selected_action": agent.selected_action,
        "selected_value": agent.value_of(agent.selected_action),
        "considered_actions": considered,
        "not_considered_actions": [
            action for action in perceived_feasible_set if action not in considered
        ],
        "action_values": {
            action: agent.value_of(action) for action in perceived_feasible_set
        },
    }

    if decision_process == LIMITED_SEARCH:
        result["search_limit"] = agent.state.decision_parameters["search_limit"]
        result["search_order"] = list(agent.state.decision_parameters["search_order"])

    return result

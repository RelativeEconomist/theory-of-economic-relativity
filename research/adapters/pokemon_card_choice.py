"""Validate Pokémon inputs and report the existing engine's decision and outcome."""

import math

from research.scenarios.pokemon_card_choice import (
    KEEP, KEEP_VALUE, SALE_OFFER, SCENARIO, SELL, STUDENT, offer_scenario,
)
from research.ter import Scenario, __version__, run_scenario

SCENARIO_ID = "pokemon-card-choice"
# Increment when the economic specification or input interpretation changes.
SCENARIO_REVISION = 1
REQUEST_KEYS = frozenset({"scenario", "keep_value", "expected_sale_price", "buyer_available"})


def validate_money(value, name: str) -> None:
    """Accept finite nonnegative numbers representable by the valuation rules."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or value < 0:
        raise ValueError(f"{name} must be a finite number of 0 or greater.")


def build_scenario(request: dict) -> Scenario:
    """Configure valuation and sale terms without exposing buyer availability to D."""
    if not isinstance(request, dict):
        raise TypeError("Request must be a dict.")
    if request.get("scenario") != SCENARIO_ID:
        raise ValueError(f"Unsupported scenario {request.get('scenario')!r}; expected {SCENARIO_ID!r}.")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ValueError(f"Unknown request key(s): {unknown}")

    keep_value = request.get("keep_value", KEEP_VALUE)
    sale_price = request.get("expected_sale_price", SALE_OFFER)
    buyer_available = request.get("buyer_available", SCENARIO.initial_state["buyer_exists"])
    validate_money(keep_value, "keep_value")
    validate_money(sale_price, "expected_sale_price")
    if not isinstance(buyer_available, bool):
        raise TypeError("buyer_available must be a boolean.")
    return offer_scenario(sale_price, buyer_available, keep_value)


def run(request: dict) -> dict:
    """Return resolved inputs, engine valuations, C, agent-level O, and provenance."""
    scenario = build_scenario(request)
    agent = run_scenario(scenario).agent(STUDENT.name)
    values = {action: agent.value_of(action) for action in agent.state.perceived_feasible_set}
    return {
        "scenario": SCENARIO_ID,
        "name": scenario.name,
        "inputs": {
            "keep_value": agent.state.valuation["benefits"][KEEP],
            "expected_sale_price": agent.state.model_of_reality["price"],
            "buyer_available": scenario.initial_state["buyer_exists"],
        },
        "action_values": values,
        "values_equal": values[KEEP] == values[SELL],
        "selected_action": agent.selected_action,
        "outcome": dict(agent.outcome),
        "ter_version": __version__,
        "scenario_revision": SCENARIO_REVISION,
    }

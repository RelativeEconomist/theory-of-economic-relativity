"""
JSON-safe adapter for the Asymmetric Information scenario.

Request:

    {
        "scenario": "asymmetric-information",
        "pricing": "pooled",
        "believed_share_high": 0.5,
    }

Every key but scenario is optional; omitted ones keep the reusable
scenario's values. pricing is "pooled" (the default: individual quality is
unobservable) or "verified". believed_share_high, from 0 to 1, sets the
pooled price and configures pooled pricing only.

Response:

    {
        "scenario": "asymmetric-information",
        "name": "Market for Lemons (Asymmetric Information)",
        "pricing": "pooled",
        "sellers": [
            {
                "name": "high_quality_seller_1",
                "actual_quality": "high",
                "known_quality": "high",
                "observed_price": 7.0,
                "reservation_value": 8,
                "action_values": {"sell": -1.0, "hold": 0},
                "selected_action": "hold",
            },
            ...
        ],
        "system_outcome": {"sold_high": 0, "sold_low": 3, "total_sold": 3},
        "believed_share_high": 0.5,
    }

Per seller, actual_quality is the scenario's actual quality (an aspect of
F_t, read only by R); known_quality and observed_price are the seller's
model of reality (M); reservation_value and action_values are its
valuation (V); selected_action is C. system_outcome is O_t from the one
joint R over every seller's selected action. The scenario defines no
seller-level outcomes. believed_share_high is returned for pooled pricing
only.
"""

import math

from research.scenarios.asymmetric_information import (
    ASYMMETRIC_INFORMATION_SCENARIO,
    SELL,
    SYMMETRIC_INFORMATION_SCENARIO,
    pooled_price,
)
from research.ter import Scenario, run_scenario

SCENARIO_ID = "asymmetric-information"

POOLED = "pooled"
VERIFIED = "verified"

SCENARIOS = {
    POOLED: ASYMMETRIC_INFORMATION_SCENARIO,
    VERIFIED: SYMMETRIC_INFORMATION_SCENARIO,
}

REQUEST_KEYS = frozenset({"scenario", "pricing", "believed_share_high"})


def build_scenario(request: dict) -> Scenario:
    """
    Validate a request and return the reusable scenario for its pricing,
    with the pooled price reset from believed_share_high where the request
    gives it.
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

    pricing = request.get("pricing", POOLED)

    # A tuple, not the SCENARIOS dict, so unhashable values fail cleanly.
    if pricing not in (POOLED, VERIFIED):
        raise ValueError(
            f"pricing must be {POOLED!r} or {VERIFIED!r}; got {pricing!r}."
        )

    if "believed_share_high" not in request:
        return SCENARIOS[pricing]

    if pricing != POOLED:
        raise ValueError(
            f"believed_share_high configures {POOLED!r} pricing only; "
            f"remove it for {pricing!r}."
        )

    believed_share_high = request["believed_share_high"]
    validate_believed_share_high(believed_share_high)

    # Every seller observes the same pooled price, whatever its own quality.
    price = pooled_price(believed_share_high)

    return ASYMMETRIC_INFORMATION_SCENARIO.variant(
        parameters={"believed_share_high": believed_share_high},
        agents=[
            seller.variant(model_of_reality={"price": price})
            for seller in ASYMMETRIC_INFORMATION_SCENARIO.agents
        ],
    )


def validate_believed_share_high(believed_share_high) -> None:
    """Raise unless believed_share_high is a finite number from 0 to 1."""
    if isinstance(believed_share_high, bool) or not isinstance(
        believed_share_high, (int, float)
    ):
        raise TypeError("believed_share_high must be a number.")

    # Only floats can be non-finite; math.isfinite would overflow on huge ints.
    if isinstance(believed_share_high, float) and not math.isfinite(believed_share_high):
        raise ValueError("believed_share_high must be finite.")

    if not 0 <= believed_share_high <= 1:
        raise ValueError("believed_share_high must be from 0 to 1.")


def run(request: dict) -> dict:
    """
    Run the Asymmetric Information scenario for a JSON-safe request and
    return a JSON-safe summary: per seller, the actual quality R reads, the
    seller's own model of reality, valuation, and selected action; and the
    system outcome R realizes from all selected actions together.
    """
    scenario = build_scenario(request)
    pricing = request.get("pricing", POOLED)
    result = run_scenario(scenario)
    actual_quality_by_seller = scenario.parameters["actual_quality_by_seller"]
    sellers = []

    for spec in scenario.agents:
        seller = result.agent(spec.name)
        beliefs = seller.state.model_of_reality

        sellers.append(
            {
                "name": spec.name,
                "actual_quality": actual_quality_by_seller[spec.name],
                "known_quality": beliefs["known_quality"],
                "observed_price": beliefs["price"],
                "reservation_value": seller.state.valuation["costs"][SELL],
                "action_values": {
                    action: seller.value_of(action)
                    for action in seller.state.perceived_feasible_set
                },
                "selected_action": seller.selected_action,
            }
        )

    summary = {
        "scenario": SCENARIO_ID,
        "name": scenario.name,
        "pricing": pricing,
        "sellers": sellers,
        "system_outcome": dict(result.trace[-1].reality.system),
    }

    if pricing == POOLED:
        summary["believed_share_high"] = scenario.parameters["believed_share_high"]

    return summary

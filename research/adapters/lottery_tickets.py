"""Validate lottery inputs and report each specification's engine-selected action."""

import math

from research.scenarios.lottery_tickets import (
    BASELINE, BUY, SKIP, SPECIFICATIONS, expected_net_return, lottery_scenario,
    outcome_distribution, ticket_expected_net_return, valuation_not_used,
)
from research.ter import __version__, run_scenario

SCENARIO_ID = "lottery-tickets"
# Increment when the economic specification or input interpretation changes.
SCENARIO_REVISION = 1
REQUEST_KEYS = frozenset({"scenario", "ticket_price", "jackpot", "odds_disclosed"})
MAX_TICKET_PRICE = 1_000
MAX_JACKPOT = 1_000_000_000
# Whole-dollar prices for the price-comparison chart.
PRICE_SWEEP = range(1, 61)


def validate_amount(value, name: str, minimum, maximum) -> None:
    """Accept a finite number within [minimum, maximum]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")


def conditions(request: dict) -> dict:
    """Return the validated changes from the baseline the request asks for."""
    if not isinstance(request, dict):
        raise TypeError("Request must be a dict.")
    if request.get("scenario") != SCENARIO_ID:
        raise ValueError(f"Unsupported scenario {request.get('scenario')!r}; expected {SCENARIO_ID!r}.")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ValueError(f"Unknown request key(s): {unknown}")

    price = request.get("ticket_price", BASELINE["ticket_price"])
    jackpot = request.get("jackpot", BASELINE["jackpot"])
    disclosed = request.get("odds_disclosed", BASELINE["odds_disclosed"])
    validate_amount(price, "ticket_price", 1, MAX_TICKET_PRICE)
    validate_amount(jackpot, "jackpot", 0, MAX_JACKPOT)
    if not isinstance(disclosed, bool):
        raise TypeError("odds_disclosed must be a boolean.")
    return {"ticket_price": price, "jackpot": jackpot, "odds_disclosed": disclosed}


def probability(value) -> dict:
    return {"numerator": value.numerator, "denominator": value.denominator}


def report(specification, changes: dict) -> dict:
    """One specification's beliefs, F̂, values, selected action, and exact outcomes."""
    action, distribution = outcome_distribution(specification, **changes)
    agent = run_scenario(lottery_scenario(specification, **changes)).agent(specification.name)
    state = agent.state
    uses_valuation = specification.valuation_rule is not valuation_not_used

    return {
        "id": specification.name,
        "believed_win_probability": probability(state.model_of_reality["believed_win_probability"]),
        "perceived_feasible_set": list(state.perceived_feasible_set),
        "action_values": (
            {a: float(agent.value_of(a)) for a in state.perceived_feasible_set}
            if uses_valuation else None
        ),
        "entertainment_value": state.valuation.get("entertainment_value"),
        "maximum_price": state.decision_parameters.get("maximum_price"),
        "selected_action": action,
        "expected_net_return": float(expected_net_return(distribution)),
        "outcomes": [
            {"probability": probability(weight), **outcome}
            for weight, outcome in distribution
        ],
    }


def run(request: dict) -> dict:
    """Return inputs, actual conditions, each specification's C and O, and a price sweep."""
    changes = conditions(request)
    scenario = lottery_scenario(SPECIFICATIONS[0], **changes)

    sweep = {
        spec.name: [
            run_scenario(lottery_scenario(spec, **{**changes, "ticket_price": swept}))
            .agent(spec.name).selected_action
            for swept in PRICE_SWEEP
        ]
        for spec in SPECIFICATIONS
    }

    return {
        "scenario": SCENARIO_ID,
        "name": scenario.name,
        "inputs": changes,
        "baseline": {key: BASELINE[key] for key in changes},
        "available_funds": scenario.initial_state["available_funds"],
        "actual_win_probability": probability(scenario.parameters["win_probability"]),
        "hypothetical_ticket_expected_net_return": float(ticket_expected_net_return(**changes)),
        "specifications": [report(spec, changes) for spec in SPECIFICATIONS],
        "price_sweep": {"prices": list(PRICE_SWEEP), "choices": sweep},
        "actions": [BUY, SKIP],
        "ter_version": __version__,
        "scenario_revision": SCENARIO_REVISION,
    }

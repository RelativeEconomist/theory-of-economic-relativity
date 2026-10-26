"""
Pokémon keep or sell scenario (theory/academic.md, Models 5.1 and 5.2).

Personal keep value and the believed attainable offer determine valuation.
Actual buyer availability enters realization only. Selling wins equal values.
The believed offer and payment terms are specified separately but assumed equal.
"""

from research.ter import (
    AgentSpec,
    RealityResult,
    Scenario,
)
from research.ter.rules import maximize_value, price_taking_value


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

KEEP = "keep"
SELL = "sell"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

KEEP_VALUE = 250
SALE_OFFER = 280


# ---------------------------------------------------------------------------
# Reality function (R)
# ---------------------------------------------------------------------------

def card_sale_reality(actions, objective_state, parameters):
    """Realize this student's keep or sell action under actual sale conditions."""
    (student_name, action), = actions.items()

    if action == KEEP:
        status = "kept"
    elif action == SELL:
        status = (
            "sold"
            if objective_state["buyer_exists"]
            else "sale_failed"
        )
    else:
        raise ValueError(f"Unsupported card action: {action}")

    sold = status == "sold"

    return RealityResult(
        agents={
            student_name: {
                "status": status,
                "owns_card": not sold,
                "cash_received": parameters["sale_offer"] if sold else 0,
            },
        },
    )


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

STUDENT = AgentSpec(
    name="student",
    objective="maximize personal benefit from the card decision",
    model_of_reality={"price": SALE_OFFER},
    perceived_feasible_set=[KEEP, SELL],
    valuation={
        "price_taking_action": SELL,
        "price_role": "benefit",
        "benefits": {KEEP: KEEP_VALUE},
        "costs": {},
    },
    valuation_rule=price_taking_value,
    decision_process=maximize_value,
    decision_parameters={"tie_break_preference": SELL},
    horizon="current keep-versus-cash decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIO = Scenario(
    name="Pokemon Card -- Keep or Sell",
    description="A student chooses between retaining a card and selling it.",
    periods=1,
    initial_state={"buyer_exists": True},
    agents=[STUDENT],
    parameters={"sale_offer": SALE_OFFER},
    reality=card_sale_reality,
)


def offer_scenario(offer, buyer_exists, keep_value=KEEP_VALUE):
    """Set the believed offer (M) and the paid offer (R) to the same amount."""
    return SCENARIO.variant(
        agents=[STUDENT.variant(
            model_of_reality={"price": offer},
            valuation={"benefits": {KEEP: keep_value}},
        )],
        parameters={"sale_offer": offer},
        initial_state={"buyer_exists": buyer_exists},
    )



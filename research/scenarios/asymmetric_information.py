"""
Asymmetric Information scenario (theory/academic.md, Models 5.1 and 5.3).

Six used-car sellers, three with high-quality cars and three with lemons,
each choose to sell or hold at the price they observe. Under pooled
pricing every seller observes the same price, set from a believed share
of high-quality cars; under verified pricing each observes its own car's
true value. One joint reality rule counts the cars sold by actual quality.
"""

from research.ter import AgentGroup, AgentSpec, Scenario
from research.ter.rules import maximize_value, price_taking_value, quality_market_reality


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

SELL = "sell"
HOLD = "hold"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

HIGH = "high"
LOW = "low"

HIGH_RESERVATION_VALUE = 8
LOW_RESERVATION_VALUE = 2

VALUE_IF_HIGH = 10
VALUE_IF_LOW = 4

BELIEVED_SHARE_HIGH = 0.5

HIGH_QUALITY_SELLER_COUNT = 3
LOW_QUALITY_SELLER_COUNT = 3


def pooled_price(believed_share_high: float) -> float:
    """
    Return the price offered to every seller when individual quality is
    unobservable: the expected value of a car, given the believed share of
    high-quality cars.
    """
    return (
        believed_share_high * VALUE_IF_HIGH
        + (1 - believed_share_high) * VALUE_IF_LOW
    )


# Both prices are fixed functions of scenario parameters (and, for the
# true price, actual seller quality) -- never of a realized outcome --
# so they are set directly in each seller's initial model of reality
# (M_0) as the offered price it observes, not in an update rule.
POOLED_PRICE = pooled_price(BELIEVED_SHARE_HIGH)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_SELLER = AgentSpec(
    name="seller",
    objective="maximize value from the sale decision",
    model_of_reality={
        "known_quality": None,
        "price": 0,
    },
    valuation={
        "price_taking_action": SELL,
        "price_role": "benefit",
        "costs": {
            SELL: 0,
            HOLD: 0,
        },
    },
    perceived_feasible_set=[
        SELL,
        HOLD,
    ],
    valuation_rule=price_taking_value,
    decision_process=maximize_value,
    horizon="current sale decision",
)


HIGH_QUALITY_SELLERS = AgentGroup(
    base=BASE_SELLER,
    count=HIGH_QUALITY_SELLER_COUNT,
    name_prefix="high_quality_seller",
    model_of_reality={
        "known_quality": HIGH,
        "price": POOLED_PRICE,
    },
    valuation={
        "costs": {
            SELL: HIGH_RESERVATION_VALUE,
            HOLD: 0,
        },
    },
)

LOW_QUALITY_SELLERS = AgentGroup(
    base=BASE_SELLER,
    count=LOW_QUALITY_SELLER_COUNT,
    name_prefix="low_quality_seller",
    model_of_reality={
        "known_quality": LOW,
        "price": POOLED_PRICE,
    },
    valuation={
        "costs": {
            SELL: LOW_RESERVATION_VALUE,
            HOLD: 0,
        },
    },
)

# Priced for the pooled (asymmetric information) market: every seller
# sees the same population-level expected value, regardless of its own
# quality.
SELLERS = HIGH_QUALITY_SELLERS + LOW_QUALITY_SELLERS

# Actual quality: a fact about reality, independent of any seller's own
# model_of_reality. This scenario assumes sellers know their own quality
# perfectly (each seller's known_quality above matches this exactly),
# but quality_market_reality and the verified price below read only this
# scenario-level mapping, never agent.model_of_reality.
ACTUAL_QUALITY_BY_SELLER = {
    seller.name: HIGH
    for seller in HIGH_QUALITY_SELLERS
} | {
    seller.name: LOW
    for seller in LOW_QUALITY_SELLERS
}

# Priced for the verified (symmetric information) market instead: each
# seller sees its own true value up front, based on actual quality, not
# any seller's belief about itself.
TRUE_PRICED_SELLERS = [
    seller.variant(
        model_of_reality={
            "price": (
                VALUE_IF_HIGH
                if ACTUAL_QUALITY_BY_SELLER[seller.name] == HIGH
                else VALUE_IF_LOW
            ),
        },
    )
    for seller in SELLERS
]


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

ASYMMETRIC_INFORMATION_SCENARIO = Scenario(
    name="Market for Lemons (Asymmetric Information)",
    description=(
        "Buyers cannot observe individual seller quality and price every "
        "seller at the pooled expected value of the population."
    ),
    periods=1,

    initial_state={},

    agents=SELLERS,

    parameters={
        "believed_share_high": BELIEVED_SHARE_HIGH,
        "value_if_high": VALUE_IF_HIGH,
        "value_if_low": VALUE_IF_LOW,
        "actual_quality_by_seller": ACTUAL_QUALITY_BY_SELLER,
    },

    reality=quality_market_reality,
)


SYMMETRIC_INFORMATION_SCENARIO = ASYMMETRIC_INFORMATION_SCENARIO.variant(
    name="Verified Quality Market (Symmetric Information)",
    description=(
        "Quality is verifiable, so each seller is priced at their own "
        "true value rather than the pooled average."
    ),
    agents=TRUE_PRICED_SELLERS,
)

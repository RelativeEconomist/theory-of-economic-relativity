"""
TER Replication Test 04: Asymmetric Information and Adverse Selection

Economic question
------------------
Can TER represent the adverse-selection mechanism in Akerlof's "market for
lemons," a classic model of markets where sellers know product quality
better than buyers, causing high-quality sellers to withdraw when individual
quality is unobservable and goods are priced using pooled expected quality?

Scenario
--------
A used-car market. Three sellers each own a genuinely high-quality car
and three each own a low-quality "lemon." Each seller knows the quality
of their own car; buyers cannot observe an individual car's quality, so
under asymmetric information they offer every seller the same pooled
price based on the market's expected quality mix.

    High-quality car:  buyer value = 10   seller reservation value = 8
    Low-quality car:   buyer value = 4    seller reservation value = 2

    Expected share high quality = 50%
    Pooled price = 0.5 * 10 + 0.5 * 4 = 7

Consequence under pooled pricing (price 7):

    high-quality seller: 7 - 8 < 0  -> hold
    low-quality seller:  7 - 2 > 0  -> sell

Consequence under verified quality (each car priced at its true value):

    high-quality car: price 10 -> sell
    low-quality car:  price 4  -> sell

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C ──→ O

known_quality (M) is each seller's own belief about itself. It is never
read by the reality side. O comes only from the scenario's own
actual_quality_by_seller:

    G, M, F̂, V, H
            │
            ▼
       D = MAXIMIZE
            │
            ▼
            C ─────────────────────────┐
                                       ▼
    actual_quality_by_seller ──→ QUALITY_MARKET ──→ O
       (scenario side, not M)

Tested TER mechanics
--------------------
G     Objective              constant: maximize value from the sale
                              decision
M     Model of reality       each seller's own known_quality -- a
                              belief about itself, not read by any
                              reality function
F, F̂  Feasible sets          ["sell", "hold"]; F̂ equals F throughout
V     Valuation               ValuationRule.NET: benefit (price offered)
                              minus cost (reservation value)
H     Time horizon           constant
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        observed result
O     Realized outcome       RealityFunction.QUALITY_MARKET, from the
                              scenario's own actual_quality_by_seller

Economic mechanism
------------------
Under pooled pricing, every seller is offered the same population-level
expected price regardless of its own quality; high-quality sellers
refuse (price below their cost) while low-quality sellers accept --
adverse selection. Under verified pricing, each seller is offered its
own true value and both quality types sell.

Assumptions
-----------
- known_quality is each seller's own belief about itself (M).
  Reservation cost is the seller's own valuation (V, via
  valuation["costs"]). Actual quality -- which determines who sold
  high vs low quality goods -- is a scenario-level fact
  (parameters["actual_quality_by_seller"]), read only by
  RealityFunction.QUALITY_MARKET, never by any agent or valuation rule.
- This test assumes sellers know their own quality perfectly: each
  seller's known_quality is set to match its actual quality exactly
  (see ACTUAL_QUALITY_BY_SELLER). TER does not require this.
- Both prices (pooled and verified) are fixed functions of scenario
  parameters (and, for the verified price, actual seller quality) --
  never of a realized outcome -- so this is not TER feedback. Each
  seller's initial price is set directly in its initial valuation (V).
- F vs F̂ divergence is intentionally out of scope for this test; every
  seller's F̂ equals its F.

Hypothesis
----------
1. Under pooled (asymmetric information) pricing, high quality sellers
   withhold from the market.
2. Under pooled pricing, low quality sellers still sell.
3. The result is adverse selection: only low quality goods trade.
4. Under verified (symmetric information) pricing, both quality types trade.
5. The same sellers, with the same reservation values, decide differently
   purely because of the information available to the pricing mechanism.
6. Gains from trade exist for high quality sellers but go unrealized under
   asymmetric information.
"""

import unittest

from research.ter import (
    AgentGroup,
    AgentSpec,
    DecisionProcess,
    RealityFunction,
    Scenario,
    ValuationRule,
    run_scenario,
)


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

# Both prices are fixed functions of scenario parameters (and, for the
# true price, actual seller quality) -- never of a realized outcome --
# so they are set directly in each seller's initial valuation (V), not
# in a FeedbackRule.
POOLED_PRICE = (
    BELIEVED_SHARE_HIGH * VALUE_IF_HIGH
    + (1 - BELIEVED_SHARE_HIGH) * VALUE_IF_LOW
)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_SELLER = AgentSpec(
    name="seller",
    objective="maximize value from the sale decision",
    model_of_reality={
        "known_quality": None,
    },
    valuation={
        "benefits": {
            SELL: 0,
            HOLD: 0,
        },
        "costs": {
            SELL: 0,
            HOLD: 0,
        },
    },
    actual_feasible_set=[
        SELL,
        HOLD,
    ],
    perceived_feasible_set=[
        SELL,
        HOLD,
    ],
    valuation_rule=ValuationRule.NET,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current sale decision",
)


HIGH_QUALITY_SELLERS = AgentGroup(
    base=BASE_SELLER,
    count=HIGH_QUALITY_SELLER_COUNT,
    name_prefix="high_quality_seller",
    model_of_reality={
        "known_quality": HIGH,
    },
    valuation={
        "costs": {
            SELL: HIGH_RESERVATION_VALUE,
            HOLD: 0,
        },
        "benefits": {
            SELL: POOLED_PRICE,
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
    },
    valuation={
        "costs": {
            SELL: LOW_RESERVATION_VALUE,
            HOLD: 0,
        },
        "benefits": {
            SELL: POOLED_PRICE,
            HOLD: 0,
        },
    },
)

# Priced for the pooled (asymmetric information) market: every seller
# sees the same population-level expected value, regardless of its own
# quality.
SELLERS = HIGH_QUALITY_SELLERS + LOW_QUALITY_SELLERS

# Actual quality: a fact about reality, independent of any seller's own
# model_of_reality. This test assumes sellers know their own quality
# perfectly (each seller's known_quality above matches this exactly),
# but QUALITY_MARKET and the verified price below read only this
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
        valuation={
            "benefits": {
                SELL: (
                    VALUE_IF_HIGH
                    if ACTUAL_QUALITY_BY_SELLER[seller.name] == HIGH
                    else VALUE_IF_LOW
                ),
                HOLD: 0,
            },
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

    initial_state={
        "period": 0,
    },

    agents=SELLERS,

    parameters={
        "believed_share_high": BELIEVED_SHARE_HIGH,
        "value_if_high": VALUE_IF_HIGH,
        "value_if_low": VALUE_IF_LOW,
        "actual_quality_by_seller": ACTUAL_QUALITY_BY_SELLER,
    },

    reality_function=RealityFunction.QUALITY_MARKET,
)


SYMMETRIC_INFORMATION_SCENARIO = ASYMMETRIC_INFORMATION_SCENARIO.variant(
    name="Verified Quality Market (Symmetric Information)",
    description=(
        "Quality is verifiable, so each seller is priced at their own "
        "true value rather than the pooled average."
    ),
    agents=TRUE_PRICED_SELLERS,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAsymmetricInformation(unittest.TestCase):
    TEST_NAME = "Test 04: Asymmetric Information and Adverse Selection"

    def test_high_quality_sellers_withhold_under_pooled_price(self):
        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.final["sold_high"],
            0,
        )

    def test_low_quality_sellers_sell_under_pooled_price(self):
        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.final["sold_low"],
            LOW_QUALITY_SELLER_COUNT,
        )

    def test_adverse_selection_only_low_quality_trades(self):
        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.final["sold_high"],
            0,
        )

        self.assertEqual(
            result.final["sold_low"],
            LOW_QUALITY_SELLER_COUNT,
        )

        self.assertEqual(
            result.final["total_sold"],
            LOW_QUALITY_SELLER_COUNT,
        )

    def test_symmetric_information_restores_full_participation(self):
        result = run_scenario(
            SYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.final["sold_high"],
            HIGH_QUALITY_SELLER_COUNT,
        )

        self.assertEqual(
            result.final["sold_low"],
            LOW_QUALITY_SELLER_COUNT,
        )

        self.assertEqual(
            result.final["total_sold"],
            HIGH_QUALITY_SELLER_COUNT + LOW_QUALITY_SELLER_COUNT,
        )

    def test_information_regime_materially_changes_seller_decision(self):
        asymmetric = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        symmetric = run_scenario(
            SYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertNotEqual(
            asymmetric.final["sold_high"],
            symmetric.final["sold_high"],
        )

        self.assertEqual(
            asymmetric.final["sold_high"],
            0,
        )

        self.assertEqual(
            symmetric.final["sold_high"],
            HIGH_QUALITY_SELLER_COUNT,
        )

    def test_gains_from_trade_exist_but_go_unrealized(self):
        self.assertGreater(
            VALUE_IF_HIGH,
            HIGH_RESERVATION_VALUE,
        )

        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.final["sold_high"],
            0,
        )

    def test_pooled_price_reflects_population_belief_not_individual_quality(self):
        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        expected_price = (
            BELIEVED_SHARE_HIGH * VALUE_IF_HIGH
            + (1 - BELIEVED_SHARE_HIGH) * VALUE_IF_LOW
        )

        self.assertNotEqual(expected_price, VALUE_IF_HIGH)
        self.assertNotEqual(expected_price, VALUE_IF_LOW)

        # Every seller sees the same pooled price, regardless of its own
        # quality -- pooled pricing is population-level, not individual.
        for seller in SELLERS:
            self.assertEqual(
                result.agent(seller.name).valuation["benefits"]["sell"],
                expected_price,
            )

"""
TER Replication Test 18: Consumer Surplus

Economic question
------------------
Can TER represent consumer surplus as the difference between a buyer's
reservation value and the market price for buyers who choose to
purchase?

Scenario
--------
Four buyers face the same fixed quoted market price, 10:

    Buyer 1: reservation value 15 -> BUY -> consumer surplus 5
    Buyer 2: reservation value 12 -> BUY -> consumer surplus 2
    Buyer 3: reservation value 8  -> DO_NOT_BUY
    Buyer 4: reservation value 5  -> DO_NOT_BUY

    total consumer surplus = 5 + 2 = 7

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   maximize transaction value
    M   the quoted market price, assumed correctly observed
    F̂   BUY, DO_NOT_BUY -- F equals F̂
    V   ValuationRule.PRICE_TAKING -- reservation value relative to
        price
    H   current purchase decision
    D   DecisionProcess.MAXIMIZE
    C   BUY or DO_NOT_BUY

Tested TER mechanics
--------------------
G     Objective              constant: maximize transaction value
M     Model of reality       the quoted market price, assumed correctly
                              observed
F, F̂  Feasible sets          BUY, DO_NOT_BUY; F̂ equals F
V     Valuation               reservation value relative to price --
                              CHANGED between buyers
H     Time horizon           constant: current purchase decision
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        BUY or DO_NOT_BUY, observed result

Economic mechanism
------------------
Each buyer independently compares its own reservation value to the
quoted price and buys only if reservation value exceeds price. For a
buyer who buys, agent.value_of(BUY) (reservation value minus price) is
read directly as that buyer's consumer surplus; total consumer surplus
is the sum of that quantity across buyers who actually purchase.

Assumptions
-----------
- The fixed market price is an exogenous test assumption. Buyers are
  assumed to observe it correctly, so it appears in M. This test does
  not model price formation.
- Reservation values and the market price are test-specific economic
  assumptions, not TER primitives.
- No buyer's reservation value equals MARKET_PRICE, so tie-breaking
  behavior never determines the result.
- Consumer surplus is not a TER primitive or realized O in this test.
  Under this specific valuation setup, agent.value_of(BUY) equals
  reservation value minus price, so for buyers who actually select BUY
  it can be read directly as consumer surplus.
- Total consumer surplus is the sum of that derived surplus only across
  buyers who actually purchase.
- This test computes consumer surplus for one fixed price and one
  buyer population; it does not provide a general theory of welfare or
  surplus aggregation across markets.

Hypothesis
----------
1. Buyers with reservation values above the market price choose BUY.
2. Buyers with reservation values below the market price choose
   DO_NOT_BUY.
3. A purchasing buyer's consumer surplus equals reservation value minus
   market price.
4. Total consumer surplus equals the sum of surplus across buyers who
   actually purchase.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

BUY = "buy"
DO_NOT_BUY = "do_not_buy"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

MARKET_PRICE = 10

BUYER_1_RESERVATION_VALUE = 15
BUYER_2_RESERVATION_VALUE = 12
BUYER_3_RESERVATION_VALUE = 8
BUYER_4_RESERVATION_VALUE = 5


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_BUYER = AgentSpec(
    name="buyer",
    objective="maximize transaction value",
    model_of_reality={
        "price": MARKET_PRICE,
    },
    valuation={
        "benefits": {
            BUY: 0,
            DO_NOT_BUY: 0,
        },
        "costs": {
            BUY: 0,
            DO_NOT_BUY: 0,
        },
        "price_taking_action": BUY,
        "price_role": "cost",
    },
    actual_feasible_set=[
        BUY,
        DO_NOT_BUY,
    ],
    perceived_feasible_set=[
        BUY,
        DO_NOT_BUY,
    ],
    valuation_rule=ValuationRule.PRICE_TAKING,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current purchase decision",
)

BUYER_1 = BASE_BUYER.variant(
    name="buyer_1",
    valuation={
        "benefits": {
            BUY: BUYER_1_RESERVATION_VALUE,
            DO_NOT_BUY: 0,
        },
    },
)

BUYER_2 = BASE_BUYER.variant(
    name="buyer_2",
    valuation={
        "benefits": {
            BUY: BUYER_2_RESERVATION_VALUE,
            DO_NOT_BUY: 0,
        },
    },
)

BUYER_3 = BASE_BUYER.variant(
    name="buyer_3",
    valuation={
        "benefits": {
            BUY: BUYER_3_RESERVATION_VALUE,
            DO_NOT_BUY: 0,
        },
    },
)

BUYER_4 = BASE_BUYER.variant(
    name="buyer_4",
    valuation={
        "benefits": {
            BUY: BUYER_4_RESERVATION_VALUE,
            DO_NOT_BUY: 0,
        },
    },
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

CONSUMER_SURPLUS_SCENARIO = Scenario(
    name="Consumer Surplus at a Fixed Market Price",
    description="Four buyers with different reservation values each independently decide whether to buy at a fixed market price.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BUYER_1,
        BUYER_2,
        BUYER_3,
        BUYER_4,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestConsumerSurplus(unittest.TestCase):
    TEST_NAME = "Test 18: Consumer Surplus"

    def test_buyers_above_market_price_choose_buy(self):
        result = run_scenario(CONSUMER_SURPLUS_SCENARIO)

        self.assertEqual(
            result.agent(BUYER_1.name).selected_action,
            BUY,
        )

        self.assertEqual(
            result.agent(BUYER_2.name).selected_action,
            BUY,
        )

    def test_buyers_below_market_price_choose_do_not_buy(self):
        result = run_scenario(CONSUMER_SURPLUS_SCENARIO)

        self.assertEqual(
            result.agent(BUYER_3.name).selected_action,
            DO_NOT_BUY,
        )

        self.assertEqual(
            result.agent(BUYER_4.name).selected_action,
            DO_NOT_BUY,
        )

    def test_purchasing_buyers_surplus_equals_reservation_value_minus_price(self):
        result = run_scenario(CONSUMER_SURPLUS_SCENARIO)

        buyer_1 = result.agent(BUYER_1.name)
        buyer_2 = result.agent(BUYER_2.name)

        self.assertEqual(
            buyer_1.selected_action,
            BUY,
        )

        self.assertEqual(
            buyer_2.selected_action,
            BUY,
        )

        self.assertEqual(
            buyer_1.value_of(BUY),
            BUYER_1_RESERVATION_VALUE - MARKET_PRICE,
        )

        self.assertEqual(
            buyer_2.value_of(BUY),
            BUYER_2_RESERVATION_VALUE - MARKET_PRICE,
        )

    def test_total_consumer_surplus_equals_sum_across_purchasing_buyers(self):
        result = run_scenario(CONSUMER_SURPLUS_SCENARIO)

        buyer_1 = result.agent(BUYER_1.name)
        buyer_2 = result.agent(BUYER_2.name)

        total_consumer_surplus = (
            buyer_1.value_of(BUY)
            + buyer_2.value_of(BUY)
        )

        expected_total_consumer_surplus = (
            BUYER_1_RESERVATION_VALUE - MARKET_PRICE
            + BUYER_2_RESERVATION_VALUE - MARKET_PRICE
        )

        self.assertEqual(
            total_consumer_surplus,
            expected_total_consumer_surplus,
        )

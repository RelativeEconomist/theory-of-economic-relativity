"""
TER Replication Test 19: Producer Surplus

Economic question
------------------
Can TER represent producer surplus as the difference between the
market price and a seller's reservation cost for sellers who choose to
sell?

Scenario
--------
Four sellers face the same fixed quoted market price, 10:

    Seller 1: reservation cost 4  -> SELL -> producer surplus 6
    Seller 2: reservation cost 7  -> SELL -> producer surplus 3
    Seller 3: reservation cost 12 -> DO_NOT_SELL
    Seller 4: reservation cost 15 -> DO_NOT_SELL

    total producer surplus = 6 + 3 = 9

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   maximize transaction value
    M   the quoted market price, assumed correctly observed
    F̂   SELL, DO_NOT_SELL -- F equals F̂
    V   ValuationRule.PRICE_TAKING -- price relative to reservation cost
    H   current sale decision
    D   DecisionProcess.MAXIMIZE
    C   SELL or DO_NOT_SELL

Tested TER mechanics
--------------------
G     Objective              constant: maximize transaction value
M     Model of reality       the quoted market price, assumed correctly
                              observed
F, F̂  Feasible sets          SELL, DO_NOT_SELL; F̂ equals F
V     Valuation               price relative to reservation cost --
                              CHANGED between sellers
H     Time horizon           constant: current sale decision
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        SELL or DO_NOT_SELL, observed result

Economic mechanism
------------------
Each seller independently compares the quoted price to its own
reservation cost and sells only if price exceeds reservation cost. For
a seller who sells, agent.value_of(SELL) (price minus reservation cost)
is read directly as that seller's producer surplus; total producer
surplus is the sum of that quantity across sellers who actually sell.
This is the mirror image of the buyer-side mechanism test_18 uses to
represent decentralized demand, here used to represent decentralized
supply.

Assumptions
-----------
- The fixed market price is an exogenous test assumption. Sellers are
  assumed to observe it correctly, so it appears in M. This test does
  not model price formation.
- Reservation costs and the market price are test-specific economic
  assumptions, not TER primitives.
- No seller's reservation cost equals MARKET_PRICE, so tie-breaking
  behavior never determines the result.
- Producer surplus is not a TER primitive or realized O in this test.
  Under this specific valuation setup, agent.value_of(SELL) equals
  market price minus reservation cost, so for sellers who actually
  select SELL it can be read directly as producer surplus.
- Total producer surplus is the sum of that derived surplus only
  across sellers who actually sell.
- This test computes producer surplus for one fixed price and one
  seller population; it does not provide a general theory of welfare
  or surplus aggregation across markets.

Hypothesis
----------
1. Sellers with reservation costs below the market price choose SELL.
2. Sellers with reservation costs above the market price choose
   DO_NOT_SELL.
3. A selling seller's producer surplus equals market price minus
   reservation cost.
4. Total producer surplus equals the sum of surplus across sellers who
   actually sell.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

SELL = "sell"
DO_NOT_SELL = "do_not_sell"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

MARKET_PRICE = 10

SELLER_1_RESERVATION_COST = 4
SELLER_2_RESERVATION_COST = 7
SELLER_3_RESERVATION_COST = 12
SELLER_4_RESERVATION_COST = 15


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_SELLER = AgentSpec(
    name="seller",
    objective="maximize transaction value",
    model_of_reality={
        "price": MARKET_PRICE,
    },
    valuation={
        "benefits": {
            SELL: 0,
            DO_NOT_SELL: 0,
        },
        "costs": {
            SELL: 0,
            DO_NOT_SELL: 0,
        },
        "price_taking_action": SELL,
        "price_role": "benefit",
    },
    actual_feasible_set=[
        SELL,
        DO_NOT_SELL,
    ],
    perceived_feasible_set=[
        SELL,
        DO_NOT_SELL,
    ],
    valuation_rule=ValuationRule.PRICE_TAKING,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current sale decision",
)

SELLER_1 = BASE_SELLER.variant(
    name="seller_1",
    valuation={
        "costs": {
            SELL: SELLER_1_RESERVATION_COST,
            DO_NOT_SELL: 0,
        },
    },
)

SELLER_2 = BASE_SELLER.variant(
    name="seller_2",
    valuation={
        "costs": {
            SELL: SELLER_2_RESERVATION_COST,
            DO_NOT_SELL: 0,
        },
    },
)

SELLER_3 = BASE_SELLER.variant(
    name="seller_3",
    valuation={
        "costs": {
            SELL: SELLER_3_RESERVATION_COST,
            DO_NOT_SELL: 0,
        },
    },
)

SELLER_4 = BASE_SELLER.variant(
    name="seller_4",
    valuation={
        "costs": {
            SELL: SELLER_4_RESERVATION_COST,
            DO_NOT_SELL: 0,
        },
    },
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

PRODUCER_SURPLUS_SCENARIO = Scenario(
    name="Producer Surplus at a Fixed Market Price",
    description="Four sellers with different reservation costs each independently decide whether to sell at a fixed market price.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        SELLER_1,
        SELLER_2,
        SELLER_3,
        SELLER_4,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestProducerSurplus(unittest.TestCase):
    TEST_NAME = "Test 19: Producer Surplus"

    def test_sellers_below_market_price_choose_sell(self):
        result = run_scenario(PRODUCER_SURPLUS_SCENARIO)

        self.assertEqual(
            result.agent(SELLER_1.name).selected_action,
            SELL,
        )

        self.assertEqual(
            result.agent(SELLER_2.name).selected_action,
            SELL,
        )

    def test_sellers_above_market_price_choose_do_not_sell(self):
        result = run_scenario(PRODUCER_SURPLUS_SCENARIO)

        self.assertEqual(
            result.agent(SELLER_3.name).selected_action,
            DO_NOT_SELL,
        )

        self.assertEqual(
            result.agent(SELLER_4.name).selected_action,
            DO_NOT_SELL,
        )

    def test_selling_sellers_surplus_equals_price_minus_reservation_cost(self):
        result = run_scenario(PRODUCER_SURPLUS_SCENARIO)

        seller_1 = result.agent(SELLER_1.name)
        seller_2 = result.agent(SELLER_2.name)

        self.assertEqual(
            seller_1.selected_action,
            SELL,
        )

        self.assertEqual(
            seller_2.selected_action,
            SELL,
        )

        self.assertEqual(
            seller_1.value_of(SELL),
            MARKET_PRICE - SELLER_1_RESERVATION_COST,
        )

        self.assertEqual(
            seller_2.value_of(SELL),
            MARKET_PRICE - SELLER_2_RESERVATION_COST,
        )

    def test_total_producer_surplus_equals_sum_across_selling_sellers(self):
        result = run_scenario(PRODUCER_SURPLUS_SCENARIO)

        seller_1 = result.agent(SELLER_1.name)
        seller_2 = result.agent(SELLER_2.name)

        total_producer_surplus = (
            seller_1.value_of(SELL)
            + seller_2.value_of(SELL)
        )

        expected_total_producer_surplus = (
            MARKET_PRICE - SELLER_1_RESERVATION_COST
            + MARKET_PRICE - SELLER_2_RESERVATION_COST
        )

        self.assertEqual(
            total_producer_surplus,
            expected_total_producer_surplus,
        )

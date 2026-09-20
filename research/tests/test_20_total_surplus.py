"""
TER Replication Test 20: Total Surplus / Gains from Trade
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
In this configured bilateral trade, do a buyer and a seller both choose to
trade, and does the sum of the surpluses read from their valuations equal
the buyer's reservation value minus the seller's reservation cost?

Scenario
--------
One buyer and one seller face the same fixed quoted market price:

    buyer reservation value = 15
    seller reservation cost = 7
    market price             = 10

    consumer surplus (buyer)  = 15 - 10 = 5
    producer surplus (seller) =  10 - 7 = 3
    total surplus              = 5 + 3  = 8
    reservation value - reservation cost = 15 - 7 = 8

Both routes to total surplus (summing the two derived surpluses, or
subtracting reservation cost from reservation value directly) agree.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize transaction value                     fixed
M   Model of Reality          the quoted market price, assumed correctly     fixed
                              observed by both agents
F̂   Perceived Feasible Set    BUY, DO_NOT_BUY (buyer); SELL, DO_NOT_SELL     fixed
                              (seller)
V   Valuation                 ValuationRule.PRICE_TAKING: reservation value  varied (buyer vs.
                              relative to price (buyer); price relative to   seller)
                              reservation cost (seller)
H   Time Horizon              current transaction decision                   fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           BUY (buyer), SELL (seller)                     observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

The buyer and seller are independent agents in one single-period scenario
with no reality function. Consumer, producer, and total surplus are
computed by the test from each agent's own value_of(...); that arithmetic
is test-specific analysis, not a TER primitive, not R, and not a TER
system outcome. The test introduces no relationship between agent-level
and system-level outcomes.

Economic mechanism
------------------
The buyer buys because reservation value exceeds price (15 > 10); the
seller sells because price exceeds reservation cost (10 > 7). Consumer
surplus, producer surplus, and total surplus are derived measures in
this test: they are read directly from each agent's own
agent.value_of(...) under ValuationRule.PRICE_TAKING, then combined with
plain arithmetic.

Assumptions
-----------
- Reservation value, reservation cost, and the market price are
  test-specific economic assumptions, not TER primitives.
- Neither the buyer's reservation value nor the seller's reservation
  cost equals MARKET_PRICE, so tie-breaking behavior never determines
  the result.
- Consumer surplus, producer surplus, and total surplus are not
  separate outcome rules, primitives, or helpers, and no realized outcome
  or reality function is modeled. They are read directly from the buyer's
  and seller's own agent.value_of(...) under ValuationRule.PRICE_TAKING,
  then combined with plain arithmetic.
- The market price is exogenously fixed; this test does not model how
  the price was set.
- This test examines one bilateral trade between one buyer and one
  seller. It does not claim general welfare efficiency, market
  clearing, or optimal allocation.

Hypothesis
----------
In this configured bilateral trade:
1. The buyer chooses BUY.
2. The seller chooses SELL.
3. Consumer surplus plus producer surplus equals total surplus.
4. Total surplus equals buyer reservation value minus seller
   reservation cost.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

BUY = "buy"
DO_NOT_BUY = "do_not_buy"

SELL = "sell"
DO_NOT_SELL = "do_not_sell"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

BUYER_RESERVATION_VALUE = 15
SELLER_RESERVATION_COST = 7
MARKET_PRICE = 10


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BUYER = AgentSpec(
    name="buyer",
    objective="maximize transaction value",
    model_of_reality={
        "price": MARKET_PRICE,
    },
    valuation={
        "benefits": {
            BUY: BUYER_RESERVATION_VALUE,
            DO_NOT_BUY: 0,
        },
        "costs": {
            BUY: 0,
            DO_NOT_BUY: 0,
        },
        "price_taking_action": BUY,
        "price_role": "cost",
    },
    perceived_feasible_set=[
        DO_NOT_BUY,
        BUY,
    ],
    valuation_rule=ValuationRule.PRICE_TAKING,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current purchase decision",
)

SELLER = AgentSpec(
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
            SELL: SELLER_RESERVATION_COST,
            DO_NOT_SELL: 0,
        },
        "price_taking_action": SELL,
        "price_role": "benefit",
    },
    perceived_feasible_set=[
        DO_NOT_SELL,
        SELL,
    ],
    valuation_rule=ValuationRule.PRICE_TAKING,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current sale decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

TOTAL_SURPLUS_SCENARIO = Scenario(
    name="Total Surplus from a Bilateral Trade at a Fixed Market Price",
    description="One buyer and one seller each independently decide whether to trade at a fixed market price.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BUYER,
        SELLER,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTotalSurplus(unittest.TestCase):
    TEST_NAME = "Test 20: Total Surplus / Gains from Trade"

    def test_buyer_chooses_buy(self):
        result = run_scenario(TOTAL_SURPLUS_SCENARIO)

        self.assertEqual(
            result.agent(BUYER.name).selected_action,
            BUY,
        )

    def test_seller_chooses_sell(self):
        result = run_scenario(TOTAL_SURPLUS_SCENARIO)

        self.assertEqual(
            result.agent(SELLER.name).selected_action,
            SELL,
        )

    def test_consumer_surplus_plus_producer_surplus_equals_total_surplus(self):
        result = run_scenario(TOTAL_SURPLUS_SCENARIO)

        buyer = result.agent(BUYER.name)
        seller = result.agent(SELLER.name)

        self.assertEqual(
            buyer.selected_action,
            BUY,
        )

        self.assertEqual(
            seller.selected_action,
            SELL,
        )

        consumer_surplus = buyer.value_of(BUY)
        producer_surplus = seller.value_of(SELL)

        self.assertEqual(
            consumer_surplus,
            5,
        )

        self.assertEqual(
            producer_surplus,
            3,
        )

        total_surplus = consumer_surplus + producer_surplus

        self.assertEqual(
            total_surplus,
            8,
        )

    def test_total_surplus_equals_reservation_value_minus_reservation_cost(self):
        result = run_scenario(TOTAL_SURPLUS_SCENARIO)

        buyer = result.agent(BUYER.name)
        seller = result.agent(SELLER.name)

        consumer_surplus = buyer.value_of(BUY)
        producer_surplus = seller.value_of(SELL)

        total_surplus = consumer_surplus + producer_surplus

        self.assertEqual(
            total_surplus,
            BUYER_RESERVATION_VALUE - SELLER_RESERVATION_COST,
        )

"""
TER Replication Test 07: Supply and Demand

Economic question
------------------
Can independent buyer and seller decisions, each evaluated at an
externally supplied candidate price, aggregate into downward-sloping
demand, upward-sloping supply, and a market-clearing price where
aggregate demand equals aggregate supply?

Scenario
--------
A market for one standardized good, one unit per agent. At each quoted
price, five buyers independently decide BUY or DO_NOT_BUY (against their
own reservation value) and five sellers independently decide SELL or
DO_NOT_SELL (against their own cost):

    buyer reservation values: 9, 8, 7, 6, 5
    seller costs:             1, 2, 3, 4, 5

TER mapping
-----------
Core architecture, evaluated once per candidate price:

    (G, M, F̂, V, H, D) ──→ C

    M   the quoted price (external to the agent, supplied by the test)
    V   ValuationRule.PRICE_TAKING -- a buyer's reservation value minus
        the price, or a seller's price minus their cost
    D   DecisionProcess.MAXIMIZE, plus an explicit tie_break_preference
        (BUY for buyers, SELL for sellers) -- ties are resolved by this
        stated preference, never by incidental F̂ order
    C   "buy"/"do_not_buy" or "sell"/"do_not_sell", one per agent

F equals F̂ for every agent. Aggregating every agent's C at a given price
produces quantity demanded, quantity supplied, and excess demand
(demand - supply); scanning across the price grid identifies the
candidate price(s) where excess demand is zero.

Tested TER mechanics
--------------------
G   Objective              constant: maximize transaction value
M   Model of reality       the quoted price -- CHANGED across the price
                            grid, external to each agent's own decision
V   Valuation              reservation value / cost minus or plus price
D   Decision process       DecisionProcess.MAXIMIZE with an explicit
                            tie_break_preference
C   Selected action        observed result, aggregated across agents
H   Time horizon           constant

Economic mechanism
------------------
Each agent decides independently at a given price, using only its own
V. Aggregating those decisions across all buyers and sellers gives
quantity demanded and quantity supplied at that price. The test supplies
a fixed grid of candidate prices and evaluates every agent's decision at
each one; it does not run an endogenous auction or price-adjustment
process, and no agent discovers or generates the clearing price itself
-- the test identifies, after the fact, which externally supplied
candidate price(s) leave aggregate demand equal to aggregate supply.

Assumptions
-----------
- Uses market.py's evaluate_market/find_market_clearing_states, not
  Scenario/run_scenario; clearing is found by scanning a fixed price grid,
  not a continuous auction. This is a genuinely different mechanism from
  the rest of the suite (price discovery by search, not a time-stepped
  Scenario), not a workaround.
- Market clearing is identified by evaluating decentralized agent decisions
  across a fixed grid of candidate prices; this test does not model an
  endogenous auction or price-adjustment process.
- When transacting and not transacting have equal value, `maximize_value`
  resolves the tie using each spec's own tie_break_preference
  (decision_parameters) -- BUY for buyers, SELL for sellers -- so
  zero-surplus agents transact. This is decided explicitly by D, not by
  the order of perceived_feasible_set.

Hypothesis
----------
1. Quantity demanded falls as price rises.
2. Quantity supplied rises as price rises.
3. The baseline market has a clearing price.
4. Increased demand raises the clearing price.
5. Increased supply lowers the clearing price.
6. Aggregate demand, supply, and a market-clearing state can be derived
   from decentralized TER agent decisions under the specified price grid.
7. Excess demand is positive below the clearing price, zero at the clearing
   price, and negative above it.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, ValuationRule
from research.ter.market import evaluate_market, find_market_clearing_states


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

PRICES = [1, 2, 3, 4, 5, 6, 7, 8, 9]

BUYER_VALUES = [9, 8, 7, 6, 5]
SELLER_COSTS = [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_BUYER = AgentSpec(
    name="buyer",
    objective="maximize transaction value",
    model_of_reality={
        "price": 0,
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
    # A buyer transacts on a zero-surplus tie -- decided explicitly by
    # D, not by perceived_feasible_set order.
    decision_parameters={
        "tie_break_preference": BUY,
    },
    horizon="current transaction",
)


BASE_SELLER = AgentSpec(
    name="seller",
    objective="maximize transaction value",
    model_of_reality={
        "price": 0,
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
    # A seller transacts on a zero-surplus tie -- decided explicitly by
    # D, not by perceived_feasible_set order.
    decision_parameters={
        "tie_break_preference": SELL,
    },
    horizon="current transaction",
)


def build_buyer(reservation_value, name):
    return BASE_BUYER.variant(
        name=name,
        valuation={
            "benefits": {
                BUY: reservation_value,
                DO_NOT_BUY: 0,
            },
        },
    )


def build_seller(cost, name):
    return BASE_SELLER.variant(
        name=name,
        valuation={
            "costs": {
                SELL: cost,
                DO_NOT_SELL: 0,
            },
        },
    )


def baseline_buyers():
    return [
        build_buyer(
            reservation_value=value,
            name=f"buyer_{index + 1}",
        )
        for index, value in enumerate(BUYER_VALUES)
    ]


def baseline_sellers():
    return [
        build_seller(
            cost=cost,
            name=f"seller_{index + 1}",
        )
        for index, cost in enumerate(SELLER_COSTS)
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSupplyAndDemand(unittest.TestCase):
    TEST_NAME = "Test 07: Supply and Demand"

    def test_quantity_demanded_falls_as_price_rises(self):
        low_price = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=4,
        )

        high_price = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=7,
        )

        self.assertGreater(
            low_price.demand,
            high_price.demand,
        )

    def test_quantity_supplied_rises_as_price_rises(self):
        low_price = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=2,
        )

        high_price = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=5,
        )

        self.assertLess(
            low_price.supply,
            high_price.supply,
        )

    def test_baseline_market_clears_at_expected_price(self):
        equilibria = find_market_clearing_states(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            prices=PRICES,
        )

        self.assertEqual(
            len(equilibria),
            1,
        )

        equilibrium = equilibria[0]

        self.assertEqual(
            equilibrium.price,
            5,
        )

        self.assertEqual(
            equilibrium.demand,
            5,
        )

        self.assertEqual(
            equilibrium.supply,
            5,
        )

    def test_increase_in_demand_raises_market_clearing_price(self):
        baseline = find_market_clearing_states(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            prices=PRICES,
        )[0]

        increased_demand = baseline_buyers() + [
            build_buyer(
                reservation_value=10,
                name="additional_buyer",
            ),
        ]

        shifted = find_market_clearing_states(
            buyers=increased_demand,
            sellers=baseline_sellers(),
            prices=PRICES,
        )[0]

        self.assertEqual(
            baseline.price,
            5,
        )

        self.assertEqual(
            shifted.price,
            6,
        )

        self.assertGreater(
            shifted.price,
            baseline.price,
        )

    def test_increase_in_supply_lowers_market_clearing_price(self):
        baseline = find_market_clearing_states(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            prices=PRICES,
        )[0]

        increased_supply = baseline_sellers() + [
            build_seller(
                cost=4,
                name="additional_seller",
            ),
        ]

        shifted = find_market_clearing_states(
            buyers=baseline_buyers(),
            sellers=increased_supply,
            prices=PRICES,
        )[0]

        self.assertEqual(
            baseline.price,
            5,
        )

        self.assertEqual(
            shifted.price,
            4,
        )

        self.assertLess(
            shifted.price,
            baseline.price,
        )

    def test_excess_demand_changes_sign_around_equilibrium(self):
        below = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=4,
        )

        equilibrium = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=5,
        )

        above = evaluate_market(
            buyers=baseline_buyers(),
            sellers=baseline_sellers(),
            price=6,
        )

        self.assertGreater(
            below.excess_demand,
            0,
        )

        self.assertEqual(
            equilibrium.excess_demand,
            0,
        )

        self.assertLess(
            above.excess_demand,
            0,
        )

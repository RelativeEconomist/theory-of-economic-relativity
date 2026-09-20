"""
TER Replication Test 07: Supply and Demand
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
In this configured market, does a test-specific aggregation of
independently selected buyer and seller actions, evaluated at externally
supplied candidate prices, produce downward-sloping demand, upward-sloping
supply, and a price where quantity demanded equals quantity supplied?

Scenario
--------
A market for one standardized good, one unit per agent. At each quoted
price, five buyers independently decide BUY or DO_NOT_BUY (against their
own reservation value) and five sellers independently decide SELL or
DO_NOT_SELL (against their own cost):

    buyer reservation values: 9, 8, 7, 6, 5
    seller costs:             1, 2, 3, 4, 5

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize transaction value                     fixed
M   Model of Reality          the quoted price, set by the market helper     varied (across the
                              at each candidate price                        price grid)
F̂   Perceived Feasible Set    BUY, DO_NOT_BUY (buyers); SELL, DO_NOT_SELL    fixed
                              (sellers)
V   Valuation                 ValuationRule.PRICE_TAKING: reservation value  fixed
                              minus price (buyer), price minus cost (seller)
H   Time Horizon              current transaction                            fixed
D   Decision Process          DecisionProcess.MAXIMIZE with an explicit      fixed
                              tie_break_preference (BUY for buyers, SELL
                              for sellers)
C   Selected Action           BUY / DO_NOT_BUY or SELL / DO_NOT_SELL, one    observed
                              per agent per price
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Test-specific market analysis: research.ter.market.evaluate_market builds
each agent fresh, sets the quoted price in its M, has it select C through
Model 5.1, and counts BUY and SELL as quantity demanded and quantity
supplied; find_market_clearing_states scans the price grid for prices
where the two are equal. This helper is an analytical tool for this test,
not a TER primitive. It is not R, its returned values (demand, supply,
excess demand) are not a TER system outcome, and this test introduces no
relationship between agent-level and system-level outcomes. The quoted
price is a test-specific market condition supplied to each agent's M, not
a complete representation of F_t.

Economic mechanism
------------------
Each agent decides independently at a given price, using only its own
V. Aggregating those decisions across all buyers and sellers gives
quantity demanded and quantity supplied at that price. The test supplies
a fixed grid of candidate prices and evaluates every agent's decision at
each one; it does not run an endogenous auction or price-adjustment
process, and no agent discovers or generates the clearing price itself
-- the test identifies, after the fact, which externally supplied
candidate price(s) leave quantity demanded equal to quantity supplied.

Assumptions
-----------
- The market helper is used instead of Scenario/run_scenario because
  clearing is found by scanning a fixed price grid, not by a time-stepped
  scenario. This is a test-specific analysis choice, not a TER mechanism.
- Market clearing is identified on a fixed grid of candidate prices; the
  test does not model an endogenous auction or price adjustment, and does
  not claim real markets clear continuously or instantaneously.
- When transacting and not transacting have equal value, `maximize_value`
  resolves the tie using each spec's own tie_break_preference
  (decision_parameters) -- BUY for buyers, SELL for sellers -- so
  zero-surplus agents transact. This is decided explicitly by D, not by
  the order of perceived_feasible_set.
- Statements that supply and demand shift prices in general are economic
  background. The test shows them only for the specific additional buyer
  and seller configured here.

Hypothesis
----------
In this configured market:
1. Quantity demanded falls as price rises.
2. Quantity supplied rises as price rises.
3. The baseline market has one clearing price on the grid (5).
4. Adding one buyer raises the clearing price (5 to 6).
5. Adding one seller lowers the clearing price (5 to 4).
6. The test-specific aggregation applied to independently selected agent
   actions produces quantity demanded, quantity supplied, and a
   market-clearing state over the specified price grid.
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

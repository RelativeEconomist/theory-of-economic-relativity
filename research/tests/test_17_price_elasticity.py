"""
TER Replication Test 17: Price Elasticity of Demand
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
In two constructed buyer populations facing the same price increase, does
a test-specific aggregation of independently selected buy decisions show a
comparatively price-insensitive demand response in one population and a
comparatively price-sensitive response in the other?

Scenario
--------
Price rises from 10 to 12 (+20%). Two buyer populations face the same
price change, with different reservation-value distributions:

    Inelastic population: Qd 10 -> 9   (-10%)
        elasticity = 0.10 / 0.20 = 0.5

    Elastic population:   Qd 10 -> 2   (-80%)
        elasticity = 0.80 / 0.20 = 4.0

Each population's demand is a count of independent buyer decisions at a
given quoted price, not a hand-picked number.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize transaction value                     fixed
M   Model of Reality          the quoted price, set by the market helper     varied (across the
                              at each tested price                           two tested prices)
F̂   Perceived Feasible Set    BUY, DO_NOT_BUY                                fixed
V   Valuation                 ValuationRule.PRICE_TAKING: reservation value  varied (by buyer)
                              relative to price
H   Time Horizon              current transaction                            fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           BUY or DO_NOT_BUY, one per buyer               observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Test-specific market analysis: research.ter.market.evaluate_market
(buyers only, no sellers) builds each buyer fresh, sets the quoted price in
its M, has it select C through Model 5.1, and counts BUY as quantity
demanded. Elasticity is then computed by the test from those counts. The
helper and the elasticity measure are analytical tools for this test, not
TER primitives. Neither is R, the counts are not a TER system outcome, and
this test introduces no relationship between agent-level and system-level
outcomes. The quoted price is a test-specific market condition supplied to
each buyer's M, not a complete representation of F_t.

Economic mechanism
------------------
Each buyer independently compares its own reservation value to the
quoted price and buys only if reservation value exceeds price.
Aggregating those individual decisions across a population gives
quantity demanded at that price; comparing quantity demanded at the two
prices gives the population's elasticity. The inelastic population's
reservation values sit mostly above the whole price range, so only one
buyer drops out when price rises; the elastic population's reservation
values sit mostly between the two prices, so most buyers drop out.

Assumptions
-----------
- The price is externally supplied to evaluate_market; buyers are
  assumed to observe that quoted price correctly, so it appears in M.
  This test does not model price formation.
- Buyer reservation values are test-specific economic assumptions, not
  TER primitives. Two different reservation-value distributions
  (INELASTIC_RESERVATION_VALUES, ELASTIC_RESERVATION_VALUES) are chosen
  so that, across the same INITIAL_PRICE -> NEW_PRICE change, one
  population's demand is comparatively price-insensitive and the other's
  is comparatively price-sensitive.
- Elasticity is computed by the test as abs(percentage_change_in_quantity /
  percentage_change_in_price), each change measured relative to its
  initial ("before") value. This is a finite-change measure, not a
  continuous point elasticity or midpoint/arc elasticity estimate, and not
  a TER primitive, rule, or variable.
- This test measures elasticity for two constructed populations; it does
  not explain what economic forces make one population's demand more or
  less price sensitive than another's.
- Every buyer's reservation value is strictly above or strictly below
  both INITIAL_PRICE and NEW_PRICE (never equal to either), so no
  buyer's decision depends on how a tie is broken.

Hypothesis
----------
In these two constructed populations:
1. The inelastic case has elasticity below 1.
2. The elastic case has elasticity above 1.
3. The elastic case has a larger proportional quantity response than the
   inelastic case.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, ValuationRule
from research.ter.market import evaluate_market


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

BUY = "buy"
DO_NOT_BUY = "do_not_buy"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

INITIAL_PRICE = 10
NEW_PRICE = 12

# Reservation values sit well above the whole INITIAL_PRICE -> NEW_PRICE
# range, and strictly above both tested prices, so only the one buyer
# whose value falls inside that range drops out when price rises.
INELASTIC_RESERVATION_VALUES = [21, 20, 19, 18, 17, 16, 15, 14, 13, 11]

# Most reservation values sit strictly between INITIAL_PRICE and
# NEW_PRICE (never equal to either), so most buyers drop out when price
# rises to NEW_PRICE.
ELASTIC_RESERVATION_VALUES = [20, 15, 11, 11, 11, 11, 11, 11, 11, 11]


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


def inelastic_buyers():
    return [
        build_buyer(
            reservation_value=value,
            name=f"inelastic_buyer_{index + 1}",
        )
        for index, value in enumerate(INELASTIC_RESERVATION_VALUES)
    ]


def elastic_buyers():
    return [
        build_buyer(
            reservation_value=value,
            name=f"elastic_buyer_{index + 1}",
        )
        for index, value in enumerate(ELASTIC_RESERVATION_VALUES)
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPriceElasticity(unittest.TestCase):
    TEST_NAME = "Test 17: Price Elasticity of Demand"

    def test_inelastic_case_has_elasticity_below_one(self):
        initial_quantity = evaluate_market(
            buyers=inelastic_buyers(),
            sellers=[],
            price=INITIAL_PRICE,
        ).demand

        new_quantity = evaluate_market(
            buyers=inelastic_buyers(),
            sellers=[],
            price=NEW_PRICE,
        ).demand

        percentage_change_in_price = (
            (NEW_PRICE - INITIAL_PRICE) / INITIAL_PRICE
        )
        percentage_change_in_quantity = (
            (new_quantity - initial_quantity) / initial_quantity
        )

        elasticity = abs(
            percentage_change_in_quantity
            / percentage_change_in_price
        )

        self.assertLess(
            elasticity,
            1,
        )

    def test_elastic_case_has_elasticity_above_one(self):
        initial_quantity = evaluate_market(
            buyers=elastic_buyers(),
            sellers=[],
            price=INITIAL_PRICE,
        ).demand

        new_quantity = evaluate_market(
            buyers=elastic_buyers(),
            sellers=[],
            price=NEW_PRICE,
        ).demand

        percentage_change_in_price = (
            (NEW_PRICE - INITIAL_PRICE) / INITIAL_PRICE
        )
        percentage_change_in_quantity = (
            (new_quantity - initial_quantity) / initial_quantity
        )

        elasticity = abs(
            percentage_change_in_quantity
            / percentage_change_in_price
        )

        self.assertGreater(
            elasticity,
            1,
        )

    def test_elastic_case_has_larger_proportional_quantity_response(self):
        inelastic_initial = evaluate_market(
            buyers=inelastic_buyers(),
            sellers=[],
            price=INITIAL_PRICE,
        ).demand

        inelastic_new = evaluate_market(
            buyers=inelastic_buyers(),
            sellers=[],
            price=NEW_PRICE,
        ).demand

        elastic_initial = evaluate_market(
            buyers=elastic_buyers(),
            sellers=[],
            price=INITIAL_PRICE,
        ).demand

        elastic_new = evaluate_market(
            buyers=elastic_buyers(),
            sellers=[],
            price=NEW_PRICE,
        ).demand

        inelastic_percentage_change = abs(
            (inelastic_new - inelastic_initial) / inelastic_initial
        )
        elastic_percentage_change = abs(
            (elastic_new - elastic_initial) / elastic_initial
        )

        self.assertGreater(
            elastic_percentage_change,
            inelastic_percentage_change,
        )

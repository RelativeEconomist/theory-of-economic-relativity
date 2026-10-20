"""
TER Replication Test 04: Asymmetric Information and Adverse Selection
Canonical TER: theory/academic.md, Models 5.1 and 5.3

Economic question
-----------------
In a constructed used-car market in the style of Akerlof's "market for
lemons", where sellers know product quality better than buyers, do
high-quality sellers withdraw when individual quality is unobservable and
goods are priced using pooled expected quality?

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

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize value from the sale decision          fixed
M   Model of Reality          price: the offered price the seller observes;  varied (price: pooled
                              known_quality: each seller's own belief about  vs. verified)
                              its own car. Neither is read by R
F̂   Perceived Feasible Set    sell, hold                                     fixed
V   Valuation                 price_taking_value: the observed       fixed (by seller type)
                              price (M) minus the seller's reservation
                              value (valuation["costs"])
H   Time Horizon              current sale decision                          fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           sell or hold, one per seller                   observed
F_t aspects used by R         actual_quality_by_seller: the actual quality   fixed
                              of each seller's car, a scenario-specified
                              condition R reads (not a complete
                              representation of F_t)
R   Reality Function          quality_market_reality: counts sales       fixed
                              by actual quality from the sellers' selected
                              actions
O_t System Outcome            sold_high, sold_low, total_sold, from R        observed
Feedback (Model 5.5)          none                                           --

This is a multi-agent specification: R takes the sellers' selected actions
together, so Model 5.3 applies. This test defines no individual outcomes
O_{i,t} and no relationship between them and O_t.

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
  quality_market_reality, never by any agent or valuation rule.
- This test assumes sellers know their own quality perfectly: each
  seller's known_quality is set to match its actual quality exactly
  (see ACTUAL_QUALITY_BY_SELLER). TER does not require this.
- Buyers are not modeled as agents. The price each seller is offered is
  information the seller observes when deciding, so it is held in the
  seller's M (model_of_reality["price"]); V values selling at that
  observed price against the seller's reservation value. Each seller is
  assumed to observe its offered price correctly.
- Both prices (pooled and verified) are fixed functions of scenario
  parameters (and, for the verified price, actual seller quality) --
  never of a realized outcome -- so this is not feedback in the sense
  of Model 5.5. Each seller's offered price is set directly in its
  initial model of reality (M_0).
- Divergence between F̂ and what reality permits is not modeled in this
  test.

Hypothesis
----------
In this configured scenario:
1. Under pooled (asymmetric information) pricing, high quality sellers
   withhold from the market.
2. Under pooled pricing, low quality sellers still sell.
3. The result is adverse selection: only low quality goods trade.
4. Under verified (symmetric information) pricing, both quality types trade.
5. The same sellers, with the same reservation values, decide differently
   when the offered price changes from the pooled price to the verified
   price.
6. Gains from trade exist for high quality sellers (buyer value exceeds
   reservation value) but go unrealized under pooled pricing.
"""

import unittest

from research.scenarios.asymmetric_information import (
    ASYMMETRIC_INFORMATION_SCENARIO,
    BELIEVED_SHARE_HIGH,
    HIGH_QUALITY_SELLER_COUNT,
    HIGH_RESERVATION_VALUE,
    LOW_QUALITY_SELLER_COUNT,
    SELLERS,
    SYMMETRIC_INFORMATION_SCENARIO,
    VALUE_IF_HIGH,
    VALUE_IF_LOW,
)
from research.ter import run_scenario


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
            result.trace[-1].reality.system["sold_high"],
            0,
        )

    def test_low_quality_sellers_sell_under_pooled_price(self):
        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.trace[-1].reality.system["sold_low"],
            LOW_QUALITY_SELLER_COUNT,
        )

    def test_adverse_selection_only_low_quality_trades(self):
        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.trace[-1].reality.system["sold_high"],
            0,
        )

        self.assertEqual(
            result.trace[-1].reality.system["sold_low"],
            LOW_QUALITY_SELLER_COUNT,
        )

        self.assertEqual(
            result.trace[-1].reality.system["total_sold"],
            LOW_QUALITY_SELLER_COUNT,
        )

    def test_symmetric_information_restores_full_participation(self):
        result = run_scenario(
            SYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.trace[-1].reality.system["sold_high"],
            HIGH_QUALITY_SELLER_COUNT,
        )

        self.assertEqual(
            result.trace[-1].reality.system["sold_low"],
            LOW_QUALITY_SELLER_COUNT,
        )

        self.assertEqual(
            result.trace[-1].reality.system["total_sold"],
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
            asymmetric.trace[-1].reality.system["sold_high"],
            symmetric.trace[-1].reality.system["sold_high"],
        )

        self.assertEqual(
            asymmetric.trace[-1].reality.system["sold_high"],
            0,
        )

        self.assertEqual(
            symmetric.trace[-1].reality.system["sold_high"],
            HIGH_QUALITY_SELLER_COUNT,
        )

    def test_gains_from_trade_exist_but_go_unrealized(self):
        # Scenario-premise check: buyer value exceeds the high-quality
        # seller's reservation value, so gains from trade exist.
        self.assertGreater(
            VALUE_IF_HIGH,
            HIGH_RESERVATION_VALUE,
        )

        result = run_scenario(
            ASYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(
            result.trace[-1].reality.system["sold_high"],
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

        # Scenario-premise check: the pooled price differs from either
        # quality's own value.
        self.assertNotEqual(expected_price, VALUE_IF_HIGH)
        self.assertNotEqual(expected_price, VALUE_IF_LOW)

        # Every seller observes the same pooled price (M), regardless of
        # its own quality -- pooled pricing is population-level, not
        # individual.
        for seller in SELLERS:
            self.assertEqual(
                result.agent(seller.name).state.model_of_reality["price"],
                expected_price,
            )

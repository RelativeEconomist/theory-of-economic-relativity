"""
TER Replication Test 14: Monopoly and Market Power

Economic question
------------------
Can TER represent a seller with market power choosing between prices
when different prices produce different quantities demanded and
profits?

Scenario
--------
A monopolist chooses LOW_PRICE or HIGH_PRICE. Each price sells a
different quantity, at the same unit production cost:

    LOW_PRICE:  price 8,  quantity sold 100
    HIGH_PRICE: price 14, quantity sold 30
    unit cost = 5

Implied profits:

    LOW_PRICE:  revenue = 8 * 100  = 800   cost = 5 * 100 = 500   profit = 300
    HIGH_PRICE: revenue = 14 * 30  = 420   cost = 5 * 30  = 150   profit = 270

LOW_PRICE is therefore selected: 300 > 270, even though HIGH_PRICE
charges more per unit.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   choose the price that maximizes profit
    M   specified but empty
    F̂   LOW_PRICE, HIGH_PRICE -- F equals F̂
    V   ValuationRule.NET -- revenue as benefit, production cost as cost
    H   current pricing decision
    D   DecisionProcess.MAXIMIZE
    C   the selected price

Tested TER mechanics
--------------------
G     Objective              constant: choose the price that maximizes
                              profit
M     Model of reality       specified but empty
F, F̂  Feasible sets          LOW_PRICE, HIGH_PRICE; F̂ equals F
V     Valuation               ValuationRule.NET -- revenue (benefit)
                              minus production cost (cost)
H     Time horizon           constant: current pricing decision
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        LOW_PRICE, observed result

Economic mechanism
------------------
    LOW_PRICE:  800 - 500 = 300  -> selected
    HIGH_PRICE: 420 - 150 = 270

Assumptions
-----------
- The price-to-quantity relationship is a test-specific demand
  schedule. TER does not supply this demand curve. This test uses a
  reduced-form setup where the implied revenue and production cost for
  each price are already represented in V.
- The demand schedule (how much sells at each price) and the unit
  production cost are test-specific economic assumptions, not TER
  primitives. TER does not itself claim any particular demand curve or
  cost structure.
- Revenue and cost are computed once, from the raw price/quantity/cost
  constants below, directly inside the agent's benefits/costs maps --
  there is no separate "profit" primitive; ValuationRule.NET's existing
  benefit-minus-cost mechanism is profit here.
- This test only compares two discrete prices and does not claim to
  solve a continuous monopoly-pricing problem or derive the demand
  curve endogenously.

Hypothesis
----------
1. LOW_PRICE and HIGH_PRICE imply different quantities demanded.
2. LOW_PRICE and HIGH_PRICE imply different profits.
3. The monopolist selects the price that produces the higher profit.
4. Raising price does not automatically increase profit, since quantity
   demanded falls as price rises.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

LOW_PRICE = "low_price"
HIGH_PRICE = "high_price"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

LOW_PRICE_PER_UNIT = 8
HIGH_PRICE_PER_UNIT = 14

LOW_PRICE_QUANTITY = 100
HIGH_PRICE_QUANTITY = 30

UNIT_COST = 5


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_MONOPOLIST = AgentSpec(
    name="monopolist",
    objective="choose the price that maximizes profit",
    model_of_reality={},
    valuation={
        "benefits": {
            LOW_PRICE: LOW_PRICE_PER_UNIT * LOW_PRICE_QUANTITY,
            HIGH_PRICE: HIGH_PRICE_PER_UNIT * HIGH_PRICE_QUANTITY,
        },
        "costs": {
            LOW_PRICE: UNIT_COST * LOW_PRICE_QUANTITY,
            HIGH_PRICE: UNIT_COST * HIGH_PRICE_QUANTITY,
        },
    },
    actual_feasible_set=[
        HIGH_PRICE,
        LOW_PRICE,
    ],
    perceived_feasible_set=[
        HIGH_PRICE,
        LOW_PRICE,
    ],
    valuation_rule=ValuationRule.NET,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current pricing decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

MONOPOLY_PRICING_SCENARIO = Scenario(
    name="Monopoly Pricing Decision",
    description="A monopolist chooses between a low price sold in higher quantity and a high price sold in lower quantity.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_MONOPOLIST,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMonopolyMarketPower(unittest.TestCase):
    TEST_NAME = "Test 14: Monopoly and Market Power"

    def test_prices_imply_different_quantities_demanded(self):
        self.assertNotEqual(
            LOW_PRICE_QUANTITY,
            HIGH_PRICE_QUANTITY,
        )

        self.assertGreater(
            LOW_PRICE_QUANTITY,
            HIGH_PRICE_QUANTITY,
        )

    def test_prices_imply_different_profits(self):
        agent = run_scenario(MONOPOLY_PRICING_SCENARIO).agent(BASE_MONOPOLIST.name)

        low_price_profit = agent.value_of(LOW_PRICE)
        high_price_profit = agent.value_of(HIGH_PRICE)

        self.assertNotEqual(
            low_price_profit,
            high_price_profit,
        )

        self.assertEqual(
            low_price_profit,
            LOW_PRICE_PER_UNIT * LOW_PRICE_QUANTITY - UNIT_COST * LOW_PRICE_QUANTITY,
        )

        self.assertEqual(
            high_price_profit,
            HIGH_PRICE_PER_UNIT * HIGH_PRICE_QUANTITY - UNIT_COST * HIGH_PRICE_QUANTITY,
        )

    def test_monopolist_selects_the_higher_profit_price(self):
        agent = run_scenario(MONOPOLY_PRICING_SCENARIO).agent(BASE_MONOPOLIST.name)

        self.assertEqual(
            agent.selected_action,
            LOW_PRICE,
        )

        self.assertNotEqual(
            agent.selected_action,
            HIGH_PRICE,
        )

    def test_higher_price_does_not_automatically_win(self):
        agent = run_scenario(MONOPOLY_PRICING_SCENARIO).agent(BASE_MONOPOLIST.name)

        self.assertGreater(
            HIGH_PRICE_PER_UNIT,
            LOW_PRICE_PER_UNIT,
        )

        self.assertGreater(
            agent.value_of(LOW_PRICE),
            agent.value_of(HIGH_PRICE),
        )

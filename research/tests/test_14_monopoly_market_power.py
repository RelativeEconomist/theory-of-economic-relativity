"""
TER Replication Test 14: Monopoly and Market Power

Economic question
------------------
Can TER represent a seller with market power choosing among a finite set
of prices, where quantity sold is a genuine function of the chosen price
(a shared demand schedule), and where the profit-maximizing choice
produces a price above marginal cost and a quantity below what a
price-taking competitor facing the same demand and cost would sell?

This is a finite-choice reduced-form monopoly test, not a continuous
monopoly-optimization test: the monopolist chooses among three discrete
candidate prices, not any real-valued price. TER's discrete F_hat is not
a limitation here -- market power is demonstrated through the
price-quantity-profit relationship and the competitive comparison, not
through solving a calculus problem.

Scenario
--------
A monopolist chooses one of three prices. Quantity sold at each price is
not independently declared -- it is computed from one shared linear
demand schedule, quantity_demanded(price) = 160 - 10 * price, applied
identically to every candidate price and to the separately derived
competitive benchmark below. Marginal (unit) cost is constant at 5.

    MONOPOLY_PRICE_LOW  = 8:   quantity = 160 - 10*8  = 80
    MONOPOLY_PRICE_MID  = 11:  quantity = 160 - 10*11 = 50
    MONOPOLY_PRICE_HIGH = 14:  quantity = 160 - 10*14 = 20

Implied profits (price - unit_cost) * quantity_demanded(price):

    LOW:  (8  - 5) * 80 = 240
    MID:  (11 - 5) * 50 = 300  -> selected
    HIGH: (14 - 5) * 20 = 180

The interior price (MID) wins: profit is not monotonic in price, because
raising price always reduces quantity along the same demand schedule.
This is the trade-off market power is about -- see
test_no_demand_response_would_make_the_highest_price_always_win below
for what happens to this trade-off when quantity is decoupled from
price.

Competitive benchmark (derived separately, from the same demand schedule
and cost, never chosen by the monopolist and never part of its F_hat):
a price-taking firm facing the same demand at price = marginal cost.

    COMPETITIVE_PRICE = unit_cost = 5
    COMPETITIVE_QUANTITY = quantity_demanded(5) = 160 - 10*5 = 110

The monopolist's selected price (11) exceeds marginal cost (5): a markup
of 6. The monopolist's selected quantity (50) is less than the
competitive quantity (110): market power restricts output relative to
the competitive benchmark. Both of these are the actual economic
signature of market power -- not merely "the firm picked the more
profitable of two options," which the previous version of this test
demonstrated and nothing more.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   choose the price that maximizes profit
    M   specified but empty -- there is one agent and no shared belief
        environment to represent (contrast test_16, where two agents
        needed a common perceived price)
    F̂   MONOPOLY_PRICE_LOW, MONOPOLY_PRICE_MID, MONOPOLY_PRICE_HIGH --
        F equals F̂. Three discrete points, not two, so the
        profit-maximizing choice cannot be a two-point coincidence: it
        must actually be the interior maximum of the three.
    V   monopoly_price_profit_value -- profit computed from the chosen
        price, this test's shared quantity_demanded(price) schedule, and
        a constant unit cost. Quantity is never independently declared
        per price; it is derived from price every time this rule runs.
    H   current pricing decision
    D   DecisionProcess.MAXIMIZE
    C   the selected price

No reality_function is declared: this test is about what determines C
and about a benchmark comparison computed after C is known, not about
realizing or aggregating an outcome from it.

The competitive benchmark (COMPETITIVE_PRICE, COMPETITIVE_QUANTITY) is
not part of any agent's decision architecture and is not a second agent.
It is a plain comparison value, computed once at module scope by calling
the same quantity_demanded function the monopolist's own valuation rule
calls, at price = marginal cost. It represents what a different market
structure (price-taking competition) would produce under the identical
demand and cost assumptions -- it is not something the monopolist chose
among, perceives, or could have selected.

Tested TER mechanics
--------------------
G     Objective              constant: choose the price that maximizes
                              profit
M     Model of reality       specified but empty
F, F̂  Feasible sets          three discrete monopoly prices; F̂ equals F
V     Valuation               monopoly_price_profit_value -- derives
                              quantity from price via the shared demand
                              schedule, then computes profit
H     Time horizon           constant: current pricing decision
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        MONOPOLY_PRICE_MID, observed result

Assumptions
-----------
- quantity_demanded is a linear demand schedule (a test-specific economic
  assumption, not a TER primitive): quantity = 160 - 10 * price. TER does
  not supply or require any particular demand curve.
- Marginal (unit) cost is constant at 5, a test-specific economic
  assumption.
- The competitive benchmark (price = marginal cost) is the standard
  price-taking prediction under these same demand and cost assumptions.
  It is derived, not independently declared: it calls the same
  quantity_demanded function the monopolist's own valuation rule uses,
  so the comparison cannot silently drift from the mechanism actually
  driving C.
- Three discrete prices are used specifically so the profit-maximizing
  choice is an interior selection (neither the lowest nor the highest of
  the three), which a two-point test cannot distinguish from "the firm
  picks whichever of two arbitrary options is better."
- This test does not claim to solve a continuous monopoly-pricing
  problem (the true unconstrained optimum under this demand and cost is
  price 10.5, not one of the three discrete options tested) or to derive
  the demand curve endogenously. It is a finite-choice reduced-form
  replication.

Hypothesis
----------
1. Quantity demanded strictly decreases as price rises across the three
   candidate prices.
2. The monopolist selects the discrete price that maximizes profit under
   the shared demand schedule (MONOPOLY_PRICE_MID), not the lowest or
   highest price.
3. The selected monopoly price exceeds marginal cost: a positive markup.
4. The monopoly quantity is less than the competitive benchmark quantity
   derived from the same demand schedule and cost at price = marginal
   cost.
5. Every profit figure the framework reports is exactly what
   quantity_demanded and unit cost predict -- not an independently
   declared constant that merely happens to agree.
6. If quantity were unrelated to the firm's chosen price (no demand
   response), the profit-maximizing choice would degenerate to the
   highest available price, and the markup/quantity-restriction
   signature of market power would disappear. This is what the demand
   schedule is for.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario
from research.ter.rules import register_rule


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

MONOPOLY_PRICE_LOW = "monopoly_price_low"
MONOPOLY_PRICE_MID = "monopoly_price_mid"
MONOPOLY_PRICE_HIGH = "monopoly_price_high"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

MONOPOLY_PRICE_LOW_VALUE = 8
MONOPOLY_PRICE_MID_VALUE = 11
MONOPOLY_PRICE_HIGH_VALUE = 14

UNIT_COST = 5

DEMAND_INTERCEPT = 160
DEMAND_SLOPE = 10


def quantity_demanded(price):
    """
    Shared linear demand schedule for this test only:

        quantity_demanded(price) = DEMAND_INTERCEPT - DEMAND_SLOPE * price

    Both monopoly_price_profit_value (the monopolist's own valuation
    rule, below) and this test's separately derived competitive
    benchmark call this exact same function. Neither hand-declares a
    quantity for any price; quantity is always computed from price
    through this one shared schedule, so the monopoly and competitive
    figures cannot silently diverge from a common mechanism.
    """
    return DEMAND_INTERCEPT - DEMAND_SLOPE * price


@register_rule("monopoly_price_profit_value")
def monopoly_price_profit_value(action, agent):
    """
    Local Model 5.1 valuation rule for this test only.

    profit(price) = price * quantity_demanded(price)
                    - unit_cost * quantity_demanded(price)

    Quantity is derived from the chosen price via quantity_demanded on
    every call -- it is never an independently declared per-action
    constant. This is what makes "raising price reduces quantity sold"
    a mechanism this rule enforces, not a coincidence between two
    unrelated numbers a test author picked to agree with each other.

    Required valuation fields:

        price_by_action   action -> the price that action sets
        unit_cost         constant marginal cost per unit
    """
    price = agent.valuation["price_by_action"][action]
    unit_cost = agent.valuation["unit_cost"]

    quantity = quantity_demanded(price)

    revenue = price * quantity
    cost = unit_cost * quantity

    return revenue - cost


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

MONOPOLIST = AgentSpec(
    name="monopolist",
    objective="choose the price that maximizes profit",
    model_of_reality={},
    valuation={
        "price_by_action": {
            MONOPOLY_PRICE_LOW: MONOPOLY_PRICE_LOW_VALUE,
            MONOPOLY_PRICE_MID: MONOPOLY_PRICE_MID_VALUE,
            MONOPOLY_PRICE_HIGH: MONOPOLY_PRICE_HIGH_VALUE,
        },
        "unit_cost": UNIT_COST,
    },
    actual_feasible_set=[
        MONOPOLY_PRICE_LOW,
        MONOPOLY_PRICE_MID,
        MONOPOLY_PRICE_HIGH,
    ],
    perceived_feasible_set=[
        MONOPOLY_PRICE_LOW,
        MONOPOLY_PRICE_MID,
        MONOPOLY_PRICE_HIGH,
    ],
    valuation_rule="monopoly_price_profit_value",
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current pricing decision",
)


# ---------------------------------------------------------------------------
# Scenario
# ---------------------------------------------------------------------------

MONOPOLY_PRICING_SCENARIO = Scenario(
    name="Monopoly Pricing Decision",
    description=(
        "A monopolist chooses among three discrete prices; quantity sold "
        "at each is derived from one shared demand schedule."
    ),
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        MONOPOLIST,
    ],
)


# ---------------------------------------------------------------------------
# Competitive benchmark
# ---------------------------------------------------------------------------
#
# Not an agent, not a second scenario, not part of MONOPOLIST's F_hat --
# a plain comparison value derived from the same demand schedule and
# cost, at the price a price-taking competitor would charge (price =
# marginal cost). It represents a different market structure the
# monopolist did not and could not choose among.

COMPETITIVE_PRICE = UNIT_COST
COMPETITIVE_QUANTITY = quantity_demanded(COMPETITIVE_PRICE)


# ---------------------------------------------------------------------------
# Diagnostic: what happens without a demand response
# ---------------------------------------------------------------------------
#
# If quantity sold did not respond to the firm's own price choice, there
# would be no trade-off, and nothing distinguishing market power from
# ordinary profit maximization. This local scenario holds quantity fixed
# at 50 units (the monopoly-optimal quantity above) regardless of price,
# using the framework's own generic ValuationRule.NET over independently
# declared benefits/costs -- the same shape the previous version of this
# test used throughout, and exactly the shape this test's real mechanism
# no longer relies on.

NO_DEMAND_RESPONSE_QUANTITY = 50

NO_DEMAND_RESPONSE_FIRM = AgentSpec(
    name="firm_with_no_demand_response",
    objective="choose the price that maximizes profit",
    model_of_reality={},
    valuation={
        "benefits": {
            MONOPOLY_PRICE_LOW: MONOPOLY_PRICE_LOW_VALUE * NO_DEMAND_RESPONSE_QUANTITY,
            MONOPOLY_PRICE_MID: MONOPOLY_PRICE_MID_VALUE * NO_DEMAND_RESPONSE_QUANTITY,
            MONOPOLY_PRICE_HIGH: MONOPOLY_PRICE_HIGH_VALUE * NO_DEMAND_RESPONSE_QUANTITY,
        },
        "costs": {
            MONOPOLY_PRICE_LOW: UNIT_COST * NO_DEMAND_RESPONSE_QUANTITY,
            MONOPOLY_PRICE_MID: UNIT_COST * NO_DEMAND_RESPONSE_QUANTITY,
            MONOPOLY_PRICE_HIGH: UNIT_COST * NO_DEMAND_RESPONSE_QUANTITY,
        },
    },
    actual_feasible_set=[
        MONOPOLY_PRICE_LOW,
        MONOPOLY_PRICE_MID,
        MONOPOLY_PRICE_HIGH,
    ],
    perceived_feasible_set=[
        MONOPOLY_PRICE_LOW,
        MONOPOLY_PRICE_MID,
        MONOPOLY_PRICE_HIGH,
    ],
    valuation_rule=ValuationRule.NET,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current pricing decision",
)

NO_DEMAND_RESPONSE_SCENARIO = Scenario(
    name="Pricing Without a Demand Response",
    description=(
        "Diagnostic only: the same three prices and the same unit cost, "
        "but quantity sold is fixed and does not respond to price."
    ),
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        NO_DEMAND_RESPONSE_FIRM,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMonopolyMarketPower(unittest.TestCase):
    TEST_NAME = "Test 14: Monopoly and Market Power"

    def test_quantity_demanded_decreases_as_price_rises(self):
        self.assertGreater(
            quantity_demanded(MONOPOLY_PRICE_LOW_VALUE),
            quantity_demanded(MONOPOLY_PRICE_MID_VALUE),
        )

        self.assertGreater(
            quantity_demanded(MONOPOLY_PRICE_MID_VALUE),
            quantity_demanded(MONOPOLY_PRICE_HIGH_VALUE),
        )

    def test_monopolist_selects_the_profit_maximizing_discrete_price(self):
        result = run_scenario(MONOPOLY_PRICING_SCENARIO)
        monopolist = result.agent(MONOPOLIST.name)

        self.assertEqual(
            monopolist.selected_action,
            MONOPOLY_PRICE_MID,
        )

        self.assertGreater(
            monopolist.value_of(MONOPOLY_PRICE_MID),
            monopolist.value_of(MONOPOLY_PRICE_LOW),
        )

        self.assertGreater(
            monopolist.value_of(MONOPOLY_PRICE_MID),
            monopolist.value_of(MONOPOLY_PRICE_HIGH),
        )

    def test_profits_are_generated_from_the_shared_demand_schedule_not_precomputed_constants(self):
        result = run_scenario(MONOPOLY_PRICING_SCENARIO)
        monopolist = result.agent(MONOPOLIST.name)

        for action, price in (
            (MONOPOLY_PRICE_LOW, MONOPOLY_PRICE_LOW_VALUE),
            (MONOPOLY_PRICE_MID, MONOPOLY_PRICE_MID_VALUE),
            (MONOPOLY_PRICE_HIGH, MONOPOLY_PRICE_HIGH_VALUE),
        ):
            quantity = quantity_demanded(price)

            self.assertEqual(
                monopolist.value_of(action),
                price * quantity - UNIT_COST * quantity,
            )

    def test_selected_monopoly_price_exceeds_marginal_cost(self):
        result = run_scenario(MONOPOLY_PRICING_SCENARIO)
        monopolist = result.agent(MONOPOLIST.name)

        selected_price = MONOPOLIST.valuation["price_by_action"][
            monopolist.selected_action
        ]

        markup = selected_price - UNIT_COST

        self.assertGreater(
            selected_price,
            UNIT_COST,
        )

        self.assertGreater(
            markup,
            0,
        )

    def test_monopoly_quantity_is_less_than_the_competitive_quantity(self):
        result = run_scenario(MONOPOLY_PRICING_SCENARIO)
        monopolist = result.agent(MONOPOLIST.name)

        selected_price = MONOPOLIST.valuation["price_by_action"][
            monopolist.selected_action
        ]
        monopoly_quantity = quantity_demanded(selected_price)

        self.assertLess(
            monopoly_quantity,
            COMPETITIVE_QUANTITY,
        )

    def test_no_demand_response_would_make_the_highest_price_always_win(self):
        # Diagnostic: with quantity decoupled from the firm's own price
        # choice, there is no trade-off left -- profit is strictly
        # increasing in price, so the "profit-maximizing" choice
        # degenerates to whichever price is highest. This is not market
        # power; it is the absence of the mechanism that produces it.
        # Contrast MONOPOLY_PRICING_SCENARIO's interior selection above.
        result = run_scenario(NO_DEMAND_RESPONSE_SCENARIO)
        firm = result.agent(NO_DEMAND_RESPONSE_FIRM.name)

        self.assertEqual(
            firm.selected_action,
            MONOPOLY_PRICE_HIGH,
        )

        self.assertNotEqual(
            firm.selected_action,
            MONOPOLY_PRICE_MID,
        )

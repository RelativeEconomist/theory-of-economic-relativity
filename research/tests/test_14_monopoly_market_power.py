"""
TER Replication Test 14: Monopoly and Market Power
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
In a constructed one-seller setting where quantity sold is a function of
the chosen price (a shared demand schedule), does the seller choose a price
above marginal cost, and a quantity below what a price-taking competitor
facing the same demand and cost would sell?

This is a finite-choice reduced-form monopoly test, not a continuous
monopoly-optimization test: the monopolist chooses among three discrete
candidate prices, not any real-valued price. Market power is
demonstrated through the price-quantity-profit relationship and the
competitive comparison, not through solving a calculus problem.

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
This is the trade-off a downward-sloping demand curve creates -- see
test_perceived_inelastic_demand_removes_the_interior_trade_off below for
what happens when the firm perceives no demand response.

Competitive benchmark (derived separately, from the same demand schedule
and cost, never chosen by the monopolist and never part of its F̂):
a price-taking firm facing the same demand at price = marginal cost.

    COMPETITIVE_PRICE = unit_cost = 5
    COMPETITIVE_QUANTITY = quantity_demanded(5) = 160 - 10*5 = 110

The monopolist's selected price (11) exceeds marginal cost (5): a markup
of 6. The quantity its perceived demand implies at that price (50) is
less than the competitive quantity (110): market power restricts output
relative to the competitive benchmark. Both quantities are derived from
the demand schedule, not realized outcomes; no R runs in this test.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 choose the price that maximizes profit         fixed
M   Model of Reality          demand_intercept, demand_slope: the firm's     fixed
                              perceived linear demand for its product
                              (quantity = intercept - slope * price)
F̂   Perceived Feasible Set    MONOPOLY_PRICE_LOW, MONOPOLY_PRICE_MID,        fixed
                              MONOPOLY_PRICE_HIGH -- three discrete
                              points, so the profit-maximizing choice
                              cannot be a two-point coincidence
V   Valuation                 monopoly_price_profit_value (local): profit    fixed
                              from the chosen price, the quantity the
                              firm's perceived demand (M) implies at that
                              price, and a constant unit cost
H   Time Horizon              current pricing decision                       fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           MONOPOLY_PRICE_MID                             observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

The quantity demanded and the profit are computed inside V, from the
chosen price and the firm's perceived demand (M), to value the actions.
They are not realized outcomes.

The competitive benchmark (COMPETITIVE_PRICE, COMPETITIVE_QUANTITY) is
not part of any agent's decision and is not a second agent. It is a
plain comparison value, computed once at module scope by calling the
same quantity_demanded function the monopolist's own valuation rule
calls (with the analyst's demand parameters rather than the firm's
perceived ones, which are equal here), at price = marginal cost. It
represents what a different market structure (price-taking competition)
would produce under the identical demand and cost assumptions -- it is
not something the monopolist chose among, perceives, or could have
selected.

Economic mechanism
------------------
Quantity is derived from price through the firm's perceived demand
schedule (M) every time the valuation rule runs, so raising price
reduces quantity sold. Profit (price - unit cost) * quantity is
therefore not monotonic in price, and the interior price maximizes it.
Because the selected price exceeds marginal cost, the quantity perceived
demand implies at that price falls short of the competitive quantity.

Assumptions
-----------
- quantity_demanded is a linear demand schedule (a test-specific economic
  assumption, not a TER primitive): quantity = 160 - 10 * price. TER does
  not supply or require any particular demand curve.
- The monopolist perceives demand correctly: its model_of_reality
  demand_intercept and demand_slope are declared equal to
  DEMAND_INTERCEPT and DEMAND_SLOPE, the demand the competitive
  benchmark uses. This is a simplifying assumption of this
  specification; TER does not require correct beliefs, and a firm that
  misperceived demand would value its prices differently.
- Marginal (unit) cost is constant at 5, a test-specific economic
  assumption.
- The competitive benchmark (price = marginal cost) is the standard
  price-taking prediction under these same demand and cost assumptions.
  It is derived, not independently declared: it calls the same
  quantity_demanded function the monopolist's own valuation rule uses,
  with the same declared demand constants, so the comparison cannot
  silently drift from the mechanism driving C.
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
In this configured scenario:
1. Quantity demanded strictly decreases as price rises across the three
   candidate prices.
2. The monopolist selects the discrete price that maximizes profit under
   the shared demand schedule (MONOPOLY_PRICE_MID), not the lowest or
   highest price.
3. The selected monopoly price exceeds marginal cost: a positive markup.
4. The quantity the firm's perceived demand implies at the selected price
   is less than the competitive benchmark quantity derived from the same
   demand schedule and cost at price = marginal cost. Both are derived
   quantities, not realized outcomes.
5. If the firm perceives perfectly inelastic demand (quantity fixed
   regardless of its price), there is no interior trade-off: it selects
   the highest available price, with a larger markup than under the
   downward-sloping demand. Inelastic demand does not remove market
   power -- it removes the output restriction, since quantity no longer
   falls as price rises.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import maximize_value


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


def quantity_demanded(price, intercept=DEMAND_INTERCEPT, slope=DEMAND_SLOPE):
    """
    Shared linear demand schedule for this test only:

        quantity_demanded(price) = intercept - slope * price

    Both monopoly_price_profit_value (the monopolist's own valuation
    rule, below) and this test's separately derived competitive
    benchmark call this exact same function. The valuation rule passes
    the firm's perceived demand parameters from its M; the benchmark and
    premise checks use the defaults, DEMAND_INTERCEPT and DEMAND_SLOPE.
    Neither hand-declares a quantity for any price; quantity is always
    computed from price through this one shared schedule, so the
    monopoly and competitive figures cannot silently diverge from a
    common mechanism.
    """
    return intercept - slope * price


def monopoly_price_profit_value(action, agent):
    """
    Local Model 5.1 valuation rule for this test only.

    profit(price) = price * quantity_demanded(price)
                    - unit_cost * quantity_demanded(price)

    Quantity is derived from the chosen price via quantity_demanded on
    every call, using the firm's perceived demand parameters (M) -- it
    is never an independently declared per-action constant. This is what
    makes "raising price reduces quantity sold" a mechanism this rule
    enforces, not a coincidence between two unrelated numbers a test
    author picked to agree with each other.

    Required model_of_reality fields:

        demand_intercept   perceived demand intercept
        demand_slope       perceived demand slope

    Required valuation fields:

        price_by_action   action -> the price that action sets
        unit_cost         constant marginal cost per unit
    """
    price = agent.valuation["price_by_action"][action]
    unit_cost = agent.valuation["unit_cost"]

    quantity = quantity_demanded(
        price,
        intercept=agent.model_of_reality["demand_intercept"],
        slope=agent.model_of_reality["demand_slope"],
    )

    revenue = price * quantity
    cost = unit_cost * quantity

    return revenue - cost


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

MONOPOLIST = AgentSpec(
    name="monopolist",
    objective="choose the price that maximizes profit",
    model_of_reality={
        "demand_intercept": DEMAND_INTERCEPT,
        "demand_slope": DEMAND_SLOPE,
    },
    valuation={
        "price_by_action": {
            MONOPOLY_PRICE_LOW: MONOPOLY_PRICE_LOW_VALUE,
            MONOPOLY_PRICE_MID: MONOPOLY_PRICE_MID_VALUE,
            MONOPOLY_PRICE_HIGH: MONOPOLY_PRICE_HIGH_VALUE,
        },
        "unit_cost": UNIT_COST,
    },
    perceived_feasible_set=[
        MONOPOLY_PRICE_LOW,
        MONOPOLY_PRICE_MID,
        MONOPOLY_PRICE_HIGH,
    ],
    valuation_rule=monopoly_price_profit_value,
    decision_process=maximize_value,
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
    initial_state={},
    agents=[
        MONOPOLIST,
    ],
)


# ---------------------------------------------------------------------------
# Competitive benchmark
# ---------------------------------------------------------------------------
#
# Not an agent, not a second scenario, not part of MONOPOLIST's F̂ --
# a plain comparison value derived from the same demand schedule and
# cost, at the price a price-taking competitor would charge (price =
# marginal cost). It represents a different market structure the
# monopolist did not and could not choose among.

COMPETITIVE_PRICE = UNIT_COST
COMPETITIVE_QUANTITY = quantity_demanded(COMPETITIVE_PRICE)


# ---------------------------------------------------------------------------
# Diagnostic: perceived perfectly inelastic demand
# ---------------------------------------------------------------------------
#
# If the firm perceives that quantity sold does not respond to its own
# price, raising price never costs it sales, so there is no interior
# trade-off. This is the extreme of pricing power, not its absence: the
# markup is as large as the price grid allows, while the output
# restriction disappears because quantity is fixed. This local scenario
# uses the monopolist's own valuation rule, prices, and unit cost
# unchanged; only the firm's perceived demand (M) differs, holding
# quantity fixed at 50 units (the monopoly-optimal quantity above)
# regardless of price (slope 0). It changes the firm's perception, not
# reality: no R runs.

NO_DEMAND_RESPONSE_QUANTITY = 50

NO_DEMAND_RESPONSE_FIRM = MONOPOLIST.variant(
    name="firm_with_no_demand_response",
    model_of_reality={
        "demand_intercept": NO_DEMAND_RESPONSE_QUANTITY,
        "demand_slope": 0,
    },
)

NO_DEMAND_RESPONSE_SCENARIO = Scenario(
    name="Pricing Without a Demand Response",
    description=(
        "Diagnostic only: the same three prices and the same unit cost, "
        "but the firm perceives quantity sold as fixed, not responding to price "
        "(perfectly inelastic perceived demand)."
    ),
    periods=1,
    initial_state={},
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
        # Scenario-premise check on the demand schedule: no TER model is
        # exercised here.
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

        # The one profit figure checked: (11 - 5) * 50 at the selected price.
        self.assertEqual(
            monopolist.value_of(MONOPOLY_PRICE_MID),
            300,
        )

    def test_selected_monopoly_price_exceeds_marginal_cost(self):
        result = run_scenario(MONOPOLY_PRICING_SCENARIO)
        monopolist = result.agent(MONOPOLIST.name)

        selected_price = MONOPOLIST.valuation["price_by_action"][
            monopolist.selected_action
        ]

        # A positive markup: price above marginal cost.
        self.assertGreater(
            selected_price,
            UNIT_COST,
        )

    def test_quantity_implied_by_the_selected_price_is_below_the_competitive_quantity(self):
        result = run_scenario(MONOPOLY_PRICING_SCENARIO)
        monopolist = result.agent(MONOPOLIST.name)

        selected_price = MONOPOLIST.valuation["price_by_action"][
            monopolist.selected_action
        ]
        # Derived from the firm's perceived demand (M) at the selected
        # price; not a realized outcome.
        perceived_demand = MONOPOLIST.model_of_reality
        monopoly_quantity = quantity_demanded(
            selected_price,
            intercept=perceived_demand["demand_intercept"],
            slope=perceived_demand["demand_slope"],
        )

        self.assertLess(
            monopoly_quantity,
            COMPETITIVE_QUANTITY,
        )

    def test_perceived_inelastic_demand_removes_the_interior_trade_off(self):
        # Diagnostic: when the firm perceives no demand response, profit
        # is strictly increasing in price, so it selects the highest
        # available price. Pricing power is not lost -- the markup is
        # larger than under downward-sloping demand -- only the interior
        # trade-off and the output restriction are gone. Contrast
        # MONOPOLY_PRICING_SCENARIO's interior selection above.
        price_by_action = MONOPOLIST.valuation["price_by_action"]

        inelastic = run_scenario(NO_DEMAND_RESPONSE_SCENARIO).agent(NO_DEMAND_RESPONSE_FIRM.name)
        downward_sloping = run_scenario(MONOPOLY_PRICING_SCENARIO).agent(MONOPOLIST.name)

        self.assertEqual(
            inelastic.selected_action,
            MONOPOLY_PRICE_HIGH,
        )

        self.assertGreater(
            price_by_action[inelastic.selected_action] - UNIT_COST,
            price_by_action[downward_sloping.selected_action] - UNIT_COST,
        )

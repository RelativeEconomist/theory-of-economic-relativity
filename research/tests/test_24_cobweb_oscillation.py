"""
TER Replication Test 24: Cobweb Model / Oscillatory Feedback
Canonical TER: theory/academic.md, Models 5.1, 5.2 and 5.5; Analysis 5.6 (optional analytical methods)

Economic question
-----------------
In one configured cobweb system, does delayed feedback from the realized
price to the producer's expected price make production and price
alternate across periods? The test observes this by simulating that one
configuration, one of the analytical methods Analysis 5.6: Feedback
Analysis and Stability allows.

Scenario
--------
A producer decides how much to produce using the price it expects. The
price actually realized -- determined by how much was produced -- only
becomes known after the decision, and becomes the expectation for the
*next* one (naive, one-period-lag expectations). The cobweb structure is
a standard textbook setup, used here as background, not as a TER claim.

    LOW_PRODUCTION:  quantity 20, cost 0
    HIGH_PRODUCTION: quantity 60, cost 2000
    demand: price = 100 - 1 * quantity_produced
    value crossover (expected_price where LOW and HIGH tie): 50

Starting from an initial expected price of 40 (below the crossover),
production and price alternate every period:

    production: LOW  -> HIGH -> LOW  -> HIGH
    price:       80  ->  40  ->  80  -> 40

TER instantiation
-----------------
Component                       Instantiation in this test                       Status
G   Objective                   profit from current-period production            fixed
M   Model of Reality            expected_price, plus perceived quantities and    expected_price varied
                                costs                                            (by feedback)
F̂   Perceived Feasible Set      LOW_PRODUCTION, HIGH_PRODUCTION                  fixed
V   Valuation                   cobweb_producer_value (local): expected_price    varied (as a consequence
                                * perceived quantity - perceived cost; reads M   of M)
H   Time Horizon                current production period                        fixed
D   Decision Process            DecisionProcess.MAXIMIZE                         fixed
C   Selected Action             LOW_PRODUCTION or HIGH_PRODUCTION                observed (alternates)
F_t aspects used by R           inverse demand conditions (demand_intercept,     fixed
                                demand_slope) and the actual production
                                quantity associated with each action
                                (actual_quantity_by_action), encountered
                                through R
R   Reality Function            linear_inverse_demand_price (local): price       fixed
                                from the actual quantity of the selected action
O_{i,t} Realized Outcome        quantity_produced and price, from R              observed (alternates)
Feedback (Model 5.5)            expected_price_from_realized_price (local):      fixed
                                sets the next period's expected_price to the
                                price just realized

Action permission is not modeled: what F_t permits for LOW_PRODUCTION and
HIGH_PRODUCTION is outside this test's scope.

Economic mechanism
------------------
Each period's realized price pushes expected_price to the *opposite* side
of the 50 crossover from whichever production level caused it: low
production (80) makes HIGH_PRODUCTION worth more next period; high
production (40) makes LOW_PRODUCTION worth more again. The one-period
lag -- the price a decision produces is invisible to that same decision
and reaches only the next one -- is the source of the alternation in
this configuration.

Assumptions
-----------
- Production quantities, costs, and the demand curve's intercept and slope
  are test-specific economic assumptions, not TER primitives.
- Scope: this is a single-agent specification, so Model 5.2 applies and
  the realized outcome is O_{i,t} (quantity_produced and price). The price
  is a market-level quantity that R computes inside this single-agent
  specification; that does not make it a system outcome, and no
  multi-agent interaction is modeled.
- M and R stay separate. The producer's perceived quantities and costs (M,
  read by V) equal the actual quantities R uses exactly, but the two are
  declared independently (parameters["actual_quantity_by_action"] for R).
  That equality is a scenario assumption, not a TER requirement, and R
  never reads the agent's model_of_reality.
- Costs are chosen so the value crossover between the two production
  levels falls at an expected price of 50, comfortably inside the range
  [40, 80] the trajectory visits, so no assertion depends on a tie.
- Local rules: cobweb_producer_value (V), linear_inverse_demand_price (R)
  and expected_price_from_realized_price (Model 5.5 feedback) are local to
  this test. Each implements an existing TER component, is a
  test-specific specification choice, and is neither a TER primitive nor a
  universal economic equation. No shared rule fits this shape. (They are
  registered with register_rule, an implementation detail.)
- Analysis 5.6 is optional, and this test does not rely on it for any TER
  claim. Oscillation here is an analytical behavior observed in one
  configured simulation. The test does not claim that TER predicts
  oscillation, that delayed feedback always produces it, that real cobweb
  markets oscillate rather than converge or explode, or that Analysis 5.6
  requires it. It introduces no oscillation rule, stability criterion, or
  universal feedback coefficient.

Hypothesis
----------
In this configured cobweb system:
1. The first production decision follows from the initial expected price.
2. That production generates the corresponding realized price (via R).
3. The realized price becomes the next period's expected price (via
   feedback), and the next production decision reverses direction.
4. The following realized price reverses direction too.
5. Production alternates over four periods -- repeated reversal, not a
   one-time adjustment.
6. The same rules, applied uniformly every period with no per-period
   special-casing, account for every reversal.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, run_scenario
from research.ter.rules import register_rule


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

LOW_PRODUCTION = "low_production"
HIGH_PRODUCTION = "high_production"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

LOW_PRODUCTION_QUANTITY = 20
HIGH_PRODUCTION_QUANTITY = 60

LOW_PRODUCTION_COST = 0
HIGH_PRODUCTION_COST = 2000

DEMAND_INTERCEPT = 100
DEMAND_SLOPE = 1

# The price the producer expects when making its first decision (M_0).
INITIAL_PRICE_SIGNAL = 40

# R: actual production quantities used by the reality function to
# compute realized price. This test assumes perceived production
# quantities (in the producer's own M, used for valuation) equal actual
# production quantities exactly -- but the two are declared
# independently here, so M and R remain conceptually separate.
ACTUAL_QUANTITY_BY_ACTION = {
    LOW_PRODUCTION: 20,
    HIGH_PRODUCTION: 60,
}


@register_rule("cobweb_producer_value")
def cobweb_producer_value(action, agent):
    """
    Local valuation rule for this test only. Implements V (Model 5.1) for
    this scenario; a test-specific specification choice, not a TER
    primitive or a universal economic equation.

    value(action) = expected_price * quantity(action) - cost(action).
    Both production levels are genuinely price-dependent.

    Required model_of_reality fields:

        expected_price   set by expected_price_from_realized_price
        quantities        action -> quantity
        costs              action -> cost
    """
    expected_price = agent.model_of_reality["expected_price"]
    quantity = agent.model_of_reality["quantities"][action]
    cost = agent.model_of_reality["costs"][action]

    return expected_price * quantity - cost


@register_rule("expected_price_from_realized_price")
def expected_price_from_realized_price(state, outcome, parameters):
    """
    Local feedback rule for this test only. Implements the Model 5.5
    feedback from the realized outcome to M; a test-specific specification
    choice, not a TER primitive, universal feedback coefficient, or
    stability criterion.

    Sets every agent's expected_price to exactly the current
    state["price"] -- this period's own just-realized price (see
    research/ter/runner.py::step: decision -> reality -> feedback, in
    that order). Because feedback updates the environment for the
    *next* period rather than the one it ran in, this is always the
    *previous* period's outcome from that next decision's point of
    view. This one-period lag is the entire mechanism producing
    delayed feedback; nothing else does.

    Required state field:

        price   populated by linear_inverse_demand_price every period.
                The very first call to this rule (after period 0) is no
                different: it reads period 0's own just-realized price.
    """
    for agent in state["agents"]:
        agent.model_of_reality["expected_price"] = state["price"]

    return state


@register_rule("linear_inverse_demand_price")
def linear_inverse_demand_price(state, agents, actions, parameters):
    """
    Local reality function for this test only. Implements R (Model 5.2,
    single-agent specification) for this scenario; the price it reports is
    a market-level quantity computed inside that specification, part of the
    producer's realized outcome.

    A standard linear inverse demand curve: price = demand_intercept -
    demand_slope * quantity_produced, applied fresh each period to
    whatever quantity was actually produced this period. Quantity
    produced is read from the scenario's own actual_quantity_by_action
    parameter -- a fact about reality -- never from any agent's
    model_of_reality. This is not a universal TER pricing equation -- it
    is one admissible R for this scenario, in the same sense
    capacity_constrained_realization (test_feasibility_contract.py) is
    one admissible R for its own. It is applied to the selected actions of
    the modeled agents, of which there is one.

    Required parameters:

        demand_intercept
        demand_slope
        actual_quantity_by_action   action -> actual quantity produced
    """
    actual_quantity_by_action = parameters["actual_quantity_by_action"]

    quantity_produced = sum(
        actual_quantity_by_action[action]
        for action in actions
    )

    price = (
        parameters["demand_intercept"]
        - parameters["demand_slope"] * quantity_produced
    )

    return {
        "quantity_produced": quantity_produced,
        "price": price,
    }


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

PRODUCER = AgentSpec(
    name="producer",
    objective="profit from current-period production",
    model_of_reality={
        # M_0: the producer starts period 0 already expecting the
        # market's own stated initial price -- there is no realized
        # outcome yet for expected_price_from_realized_price to act on,
        # so this cannot be left for feedback to fill in.
        "expected_price": INITIAL_PRICE_SIGNAL,
        # Decision-side (perceived) quantities, read only by
        # cobweb_producer_value (V) to compute value(action). This test
        # assumes these equal the actual production quantities R uses
        # (ACTUAL_QUANTITY_BY_ACTION) exactly, but the two are declared
        # independently so M and R remain conceptually separate.
        "quantities": {
            LOW_PRODUCTION: LOW_PRODUCTION_QUANTITY,
            HIGH_PRODUCTION: HIGH_PRODUCTION_QUANTITY,
        },
        "costs": {
            LOW_PRODUCTION: LOW_PRODUCTION_COST,
            HIGH_PRODUCTION: HIGH_PRODUCTION_COST,
        },
    },
    perceived_feasible_set=[
        LOW_PRODUCTION,
        HIGH_PRODUCTION,
    ],
    valuation_rule="cobweb_producer_value",
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current production period",
)


# ---------------------------------------------------------------------------
# Scenario
# ---------------------------------------------------------------------------

COBWEB_SCENARIO = Scenario(
    name="Cobweb Market",
    description=(
        "A single producer's production decision depends on the price "
        "it expects. Because supply takes a period to reach market, the "
        "price that decision actually realizes only becomes the "
        "producer's expectation for the following decision -- causing "
        "production and price to alternate."
    ),
    periods=4,

    initial_state={
        "period": 0,
    },

    agents=[
        PRODUCER,
    ],

    parameters={
        "demand_intercept": DEMAND_INTERCEPT,
        "demand_slope": DEMAND_SLOPE,
        "actual_quantity_by_action": ACTUAL_QUANTITY_BY_ACTION,
    },

    reality_function="linear_inverse_demand_price",
    feedback_rule="expected_price_from_realized_price",
)


def _producer_value(expected_price, action):
    """
    Test-side, non-TER re-derivation of cobweb_producer_value's formula,
    used only to independently verify *why* a given period's decision
    was correct -- not to re-execute or replace any framework behavior.
    """
    quantity = PRODUCER.model_of_reality["quantities"][action]
    cost = PRODUCER.model_of_reality["costs"][action]
    return expected_price * quantity - cost


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCobwebOscillation(unittest.TestCase):
    TEST_NAME = "Test 24: Cobweb Model / Oscillatory Feedback"

    def test_first_decision_follows_from_the_initial_expected_price(self):
        result = run_scenario(COBWEB_SCENARIO)

        first_decision = result.history[1]["selected_action_by_agent"]["producer"]

        self.assertEqual(
            first_decision,
            LOW_PRODUCTION,
        )

        self.assertGreater(
            _producer_value(INITIAL_PRICE_SIGNAL, LOW_PRODUCTION),
            _producer_value(INITIAL_PRICE_SIGNAL, HIGH_PRODUCTION),
        )

    def test_that_production_generates_the_corresponding_realized_price(self):
        result = run_scenario(COBWEB_SCENARIO)

        period_0 = result.history[1]

        self.assertEqual(
            period_0["quantity_produced"],
            LOW_PRODUCTION_QUANTITY,
        )

        self.assertEqual(
            period_0["price"],
            DEMAND_INTERCEPT - DEMAND_SLOPE * LOW_PRODUCTION_QUANTITY,
        )

    def test_the_realized_price_feeds_the_next_decision_which_reverses(self):
        result = run_scenario(COBWEB_SCENARIO)

        period_0 = result.history[1]
        period_1_decision = result.history[2]["selected_action_by_agent"]["producer"]

        # period_0's realized price is exactly what expected_price_from
        # _realized_price will have handed to period 1's decision.
        realized_price_from_period_0 = period_0["price"]

        self.assertGreater(
            _producer_value(realized_price_from_period_0, HIGH_PRODUCTION),
            _producer_value(realized_price_from_period_0, LOW_PRODUCTION),
        )

        self.assertEqual(
            period_1_decision,
            HIGH_PRODUCTION,
        )

        self.assertNotEqual(
            period_1_decision,
            result.history[1]["selected_action_by_agent"]["producer"],
        )

    def test_the_subsequent_realized_price_reverses_direction_too(self):
        result = run_scenario(COBWEB_SCENARIO)

        period_0_price = result.history[1]["price"]
        period_1_price = result.history[2]["price"]

        self.assertEqual(
            period_1_price,
            DEMAND_INTERCEPT - DEMAND_SLOPE * HIGH_PRODUCTION_QUANTITY,
        )

        self.assertNotEqual(
            period_1_price,
            period_0_price,
        )

    def test_production_oscillates_rather_than_making_a_one_time_adjustment(self):
        result = run_scenario(COBWEB_SCENARIO)

        decisions = [
            result.history[t]["selected_action_by_agent"]["producer"]
            for t in (1, 2, 3, 4)
        ]

        self.assertEqual(
            decisions,
            [LOW_PRODUCTION, HIGH_PRODUCTION, LOW_PRODUCTION, HIGH_PRODUCTION],
        )

        # Three direction changes across four periods -- repeated
        # reversal, not a single bounce that then settles.
        reversals = sum(
            1
            for previous, current in zip(decisions, decisions[1:])
            if previous != current
        )

        self.assertEqual(
            reversals,
            3,
        )

    def test_the_same_rule_produces_every_reversal_with_no_special_casing_by_period(self):
        result = run_scenario(COBWEB_SCENARIO)

        expected_price_entering_period = [INITIAL_PRICE_SIGNAL] + [
            result.history[t]["price"]
            for t in (1, 2, 3)
        ]

        for period_index, expected_price in enumerate(expected_price_entering_period):
            predicted = (
                HIGH_PRODUCTION
                if _producer_value(expected_price, HIGH_PRODUCTION)
                > _producer_value(expected_price, LOW_PRODUCTION)
                else LOW_PRODUCTION
            )

            actual = result.history[period_index + 1]["selected_action_by_agent"]["producer"]

            self.assertEqual(
                actual,
                predicted,
                f"period {period_index} did not follow the same rule as the others",
            )

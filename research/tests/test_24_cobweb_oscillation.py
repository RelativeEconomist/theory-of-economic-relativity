"""
TER Replication Test 24: Cobweb Model / Oscillatory Feedback

Economic question
------------------
Can TER represent an economic system in which delayed feedback causes
decisions and outcomes to oscillate across periods? This directly
demonstrates the "oscillation" concept named in TER Model 5.6 (Feedback
Analysis and Stability), using simulation -- which academic.md
explicitly permits as an alternative to Jacobian/eigenvalue analysis
for systems "nonlinear, discontinuous, strategic, or otherwise
unsuitable for this form of analysis."

Scenario
--------
The classic cobweb model: a producer decides how much to produce using
the price it expects, but the price actually realized -- determined by
how much was produced -- only becomes known after the decision, and
becomes the expectation for the *next* one (naive, one-period-lag
expectations).

    LOW_PRODUCTION:  quantity 20, cost 0
    HIGH_PRODUCTION: quantity 60, cost 2000
    demand: price = 100 - 1 * quantity_produced
    value crossover (expected_price where LOW and HIGH tie): 50

Starting from an initial expected price of 40 (below the crossover),
production and price alternate every period:

    production: LOW  -> HIGH -> LOW  -> HIGH
    price:       80  ->  40  ->  80  -> 40

This is one of the oldest documented sources of oscillatory behavior in
economics, not a mechanism invented for this test.

TER mapping
-----------
The dynamic chain, repeating each period:

    M_t(expected price) ──→ V_t ──→ D ──→ C_t(production) ──→ R
        ──→ O_t(realized quantity and price) ──→ feedback
        ──→ M_{t+1}(expected price) ──→ next C

    M         expected_price -- set by feedback to exactly last
              period's realized price, nothing more
    V         cobweb_producer_value (local): value(action) =
              expected_price * quantity(action) - cost(action)
    D         DecisionProcess.MAXIMIZE -- the same shared rule used
              throughout the suite, unmodified
    C         LOW_PRODUCTION or HIGH_PRODUCTION
    R         linear_inverse_demand_price (local): price =
              demand_intercept - demand_slope * quantity_produced,
              quantity read from the scenario's own
              actual_quantity_by_action, never from any agent's M
    O         quantity_produced and price, from R
    feedback  expected_price_from_realized_price (local): copies this
              period's just-realized price into M for the next period

G, F, F̂, and H stay constant throughout; only M (and, as a consequence,
V, C, and O) change from period to period.

Tested TER mechanics
--------------------
G     Objective              constant: maximize the value of this
                              period's production decision
M     Model of reality       expected_price -- CHANGED every period by
                              feedback
F, F̂  Feasible sets          LOW_PRODUCTION, HIGH_PRODUCTION; F̂ equals F
V     Valuation               cobweb_producer_value -- CHANGED each
                              period, only as a consequence of M
H     Time horizon           constant: current production period
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        oscillates: LOW, HIGH, LOW, HIGH
R     Reality function       local: linear_inverse_demand_price
O     Realized outcome       quantity_produced and price; oscillates
                              in lockstep with C
Feedback                     local: expected_price_from_realized_price

Economic mechanism
------------------
Each period's realized price pushes expected_price to the *opposite*
side of the 50 crossover from whichever production level caused it: low
production (80) makes HIGH_PRODUCTION worth more next period; high
production (40) makes LOW_PRODUCTION worth more again. That one-period
lag -- the realized price a decision produces is invisible to that same
decision, only to the next one -- is the entire source of the
oscillation; it is not a separate mechanism. No existing shared rule
fit this shape (see Assumptions), so three small, local rules implement
V, feedback, and R -- none a new TER primitive, all registered through
the same extension point every shared rule in rules.py uses.

This is a simulation of one configured cobweb system, not a universal
TER prediction: TER does not claim real cobweb markets always
oscillate rather than converge or explode (both are possible depending
on the slopes involved), and no generic oscillation rule, StabilityRule,
universal feedback coefficient, or universal stability/equilibrium
criterion is introduced anywhere in this test or in TER Core.

Assumptions
-----------
- Production quantities, costs, and the demand curve's intercept and
  slope are test-specific economic assumptions, not TER primitives.
- This test assumes perceived production quantities (in the producer's
  own M, used by V) equal actual production quantities (in
  parameters["actual_quantity_by_action"], used by R) exactly -- but
  the two are declared independently, so M and R remain conceptually
  separate. R never reads the agent's model_of_reality.
- Costs are chosen so the value crossover between the two production
  levels falls at an expected price of 50, comfortably inside the
  range [40, 80] the trajectory actually visits, so no assertion below
  depends on a tie or a fragile boundary.
- No existing shared rule fits this test's economics: ValuationRule.
  NET/MAPPED never read a live model_of_reality field; EXPECTED_RETURN
  and PRICE_TAKING each treat one action as a flat outside option, but
  both production levels here are genuinely price-dependent;
  FeedbackRule.PRICE_GROWTH_EXPECTATIONS computes a growth rate, not
  the absolute price level this test's V needs; RealityFunction.
  DEMAND_MOVES_PRICE compounds the *previous* price rather than pricing
  fresh off each period's quantity. Three local rules were written
  instead, following the same convention as
  capacity_constrained_realization (test_feasibility_contract.py) and
  the local rules in test_21/test_22/test_23.
- This test does not claim that all delayed-feedback markets oscillate,
  that oscillation is desirable or stable in a normative sense, or that
  TER predicts oscillation in general. It demonstrates one economically
  coherent, established mechanism that produces it.

Hypothesis
----------
1. The first production decision follows from the initial expected
   price.
2. That production generates the corresponding realized market price.
3. The realized price feeds into the next decision environment and the
   next production decision reverses direction.
4. The following realized price reverses direction too.
5. The next production decision reverses again -- establishing
   repeated oscillation, not a one-time adjustment.
6. The same rule, applied uniformly every period with no per-period
   special-casing, produces every reversal.
7. The whole sequence is produced through ordinary TER decision,
   reality, and feedback execution, using DecisionProcess.MAXIMIZE
   (shared) plus this file's local V/R/feedback rules via the standard
   registration extension point.
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

# The "period -1" price the first decision is made under.
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
    Local Model 5.1 valuation rule for this test only.

    value(action) = expected_price * quantity(action) - cost(action).
    Both production levels are genuinely price-dependent (see module
    docstring for why no existing shared ValuationRule fits this shape).

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
    Local Model 5.5 feedback rule for this test only.

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
    Local Model 5.2 reality function for this test only (one producer).

    A standard linear inverse demand curve: price = demand_intercept -
    demand_slope * quantity_produced, applied fresh each period to
    whatever quantity was actually produced this period. Quantity
    produced is read from the scenario's own actual_quantity_by_action
    parameter -- a fact about reality -- never from any agent's
    model_of_reality. This is not a universal TER pricing equation -- it
    is one admissible R for this scenario, in the same sense
    capacity_constrained_realization (test_feasibility_contract.py) is
    one admissible R for its own.

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
    objective="maximize the value of this period's production decision",
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
    actual_feasible_set=[
        LOW_PRODUCTION,
        HIGH_PRODUCTION,
    ],
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
        "price": INITIAL_PRICE_SIGNAL,
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
    was correct -- not to re-execute or replace any TER Core behavior.
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

    def test_the_sequence_is_produced_through_normal_ter_core_execution(self):
        self.assertEqual(
            PRODUCER.decision_process,
            DecisionProcess.MAXIMIZE,
        )

        self.assertEqual(
            COBWEB_SCENARIO.reality_function,
            "linear_inverse_demand_price",
        )

        self.assertEqual(
            COBWEB_SCENARIO.feedback_rule,
            "expected_price_from_realized_price",
        )

        # No scenario field varies by period; the same rules, agent, and
        # parameters govern every step of the run.
        self.assertEqual(
            COBWEB_SCENARIO.periods,
            4,
        )

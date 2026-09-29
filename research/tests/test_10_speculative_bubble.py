"""
TER Replication Test 10: Speculative Bubble
Canonical TER: theory/academic.md, Models 5.1, 5.3 and 5.5

Economic question
-----------------
Can rising prices alter expectations, increase buying, and reinforce
future price increases through a positive feedback loop?

Scenario
--------
Five investors observe the market's starting price history: price rose
from 100 to 105. That observed growth (5%) becomes every investor's
initial expected appreciation. Each investor has its own required
return:

    required returns: 1%, 2%, 3%, 4%, 5%

Investors whose expected appreciation exceeds their required return
choose BUY; aggregate buying raises price. The 5% investor's required
return exactly equals expected appreciation -- a real tie, resolved by
this test's explicit convention: expected appreciation == required
return -> HOLD. The realized price growth then updates next period's
expected appreciation, which can amplify the price path further over
subsequent periods.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 increase investment value                      fixed
M   Model of Reality          expected_appreciation: a belief about future   varied (expected_
                              price movement, the same for every investor    appreciation, by
                              at the start; feedback_strength: how strongly  observation;
                              the investor believes observed growth          feedback_strength,
                              carries forward                                across scenarios)
F̂   Perceived Feasible Set    BUY, HOLD                                      fixed
V   Valuation                 ValuationRule.EXPECTED_RETURN:                 fixed (distinct per
                              required_return                                investor)
H   Time Horizon              next period                                    fixed
D   Decision Process          DecisionProcess.MAXIMIZE, with an explicit     fixed
                              tie_break_preference of HOLD
C   Selected Action           BUY or HOLD, one per investor                  observed
F_t aspects used by R         the current price (objective state) and        varied (price, by
                                                                             transition)
                              price_sensitivity -- scenario-specified
                              conditions R reads (not a complete
                              representation of F_t)
R   Reality Function          RealityRule.DEMAND_MOVES_PRICE: moves price    fixed
                              according to the number of buyers
O_t System Outcome            buyers and the realized price, from R          observed
Transition (O_t -> F_t+1)     TransitionRule.REALIZED_PRICE: the realized    fixed
                              price becomes the next period's price
Observation                   ObservationRule.PRICE: every investor          fixed
                              observes the resulting price exactly
Update (O_t -> M_t+1)         UpdateRule.PRICE_GROWTH_EXPECTATIONS: each     fixed
                              investor sets its expected_appreciation to
                              its own feedback_strength times the
                              observed growth

This is a multi-agent specification: R takes all investors' selected
actions together, so Model 5.3 applies. This test defines no individual
outcomes O_{i,t} and no relationship between them and O_t.

Economic mechanism
------------------
Period 0: every investor's M_0 (5% expected appreciation) already
exceeds required returns of 1-4%, so those four investors BUY. The 5%
investor is indifferent (expected appreciation == required return,
buy value 0 == hold value 0); this test's explicit tie convention
resolves that to HOLD, via decision_parameters, not by the [BUY, HOLD]
order in F̂. Aggregate buying moves price upward through
DEMAND_MOVES_PRICE. Every investor observes the realized price, and its
update rule recomputes expected_appreciation from that period's own
realized growth, which can again exceed some
investors' required returns -- reinforcing buying, and price growth,
in the following period.

Assumptions
-----------
- price_sensitivity is a scenario parameter, not a TER primitive;
  RealityRule.DEMAND_MOVES_PRICE is one admissible price rule, not a
  universal TER asset-pricing equation.
- feedback_strength is each investor's own belief (M) about how strongly
  observed growth carries forward, set equal for every investor within a
  scenario and varied across scenarios. It is not a TER primitive.
- Every investor's initial expected_appreciation (M_0) is set directly
  from the growth already observed in the scenario's own starting price
  history (previous_price -> price), not left for an update to fill in
  -- there is no realized outcome before period 0's decision.
- This test represents a bubble-like positive-feedback mechanism, but
  does not establish fundamental overvaluation, irrationality, or
  unsustainability. Rising prices alone are not sufficient to prove an
  economic bubble.
- Every investor is assumed to observe the realized market price after
  each period. That observation (ObservationRule.PRICE) is the only
  pathway through which the realized outcome reaches each investor's M; TER does not require
  prices to be observable.

Hypothesis
----------
In this configured scenario:
1. Positive expected appreciation can produce buying.
2. Buying raises price.
3. Stronger feedback produces more amplification.
4. Removing feedback dampens the price path.
"""

import unittest

from research.ter import (
    AgentSpec,
    DecisionProcess,
    ObservationRule,
    RealityRule,
    Scenario,
    TransitionRule,
    UpdateRule,
    ValuationRule,
    run_scenario,
)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

BUY = "buy"
HOLD = "hold"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

INVESTOR_REQUIRED_RETURNS = [0.01, 0.02, 0.03, 0.04, 0.05]

INITIAL_PREVIOUS_PRICE = 100
INITIAL_PRICE = 105

BASE_FEEDBACK_STRENGTH = 1.0

# M_0: each investor's initial expected_appreciation is the growth
# already observed in the scenario's own starting price history
# (INITIAL_PREVIOUS_PRICE -> INITIAL_PRICE), stated directly rather than
# left for an update to fill in -- there is no realized outcome before
# period 0's decision to observe. Investors carry this belief into
# period 0 regardless of feedback_strength, which only governs how
# later, newly observed growth updates it from period 1 on.
INITIAL_EXPECTED_APPRECIATION = (
    (INITIAL_PRICE - INITIAL_PREVIOUS_PRICE) / INITIAL_PREVIOUS_PRICE
)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def build_investor(required_return, name, feedback_strength=BASE_FEEDBACK_STRENGTH):
    return AgentSpec(
        name=name,
        objective="increase investment value",
        model_of_reality={
            "expected_appreciation": INITIAL_EXPECTED_APPRECIATION,
            "feedback_strength": feedback_strength,
        },
        valuation={
            "required_return": required_return,
        },
        perceived_feasible_set=[BUY, HOLD],
        valuation_rule=ValuationRule.EXPECTED_RETURN,
        decision_process=DecisionProcess.MAXIMIZE,
        # Expected appreciation == required return is a real tie (buy
        # value 0 == hold value 0). Resolved explicitly by D, not by
        # [BUY, HOLD] order in F̂: expected appreciation == required
        # return -> HOLD.
        decision_parameters={
            "tie_break_preference": HOLD,
        },
        horizon="next period",
        update_rule=UpdateRule.PRICE_GROWTH_EXPECTATIONS,
    )


INVESTORS = [
    build_investor(
        required_return=required_return,
        name=f"investor_{index + 1}",
    )
    for index, required_return in enumerate(INVESTOR_REQUIRED_RETURNS)
]


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

BASE_SCENARIO = Scenario(
    name="Speculative Bubble",
    description="Positive price expectation feedback",
    periods=5,

    initial_state={
        "previous_price": INITIAL_PREVIOUS_PRICE,
        "price": INITIAL_PRICE,
    },

    agents=INVESTORS,

    parameters={
        "price_sensitivity": 0.01,
    },

    reality=RealityRule.DEMAND_MOVES_PRICE,
    transition=TransitionRule.REALIZED_PRICE,
    observation=ObservationRule.PRICE,
)


def with_feedback_strength(feedback_strength):
    """
    BASE_SCENARIO with every investor holding the given feedback_strength
    belief instead of BASE_FEEDBACK_STRENGTH.
    """
    return BASE_SCENARIO.variant(
        agents=[
            investor.variant(
                model_of_reality={
                    "feedback_strength": feedback_strength,
                },
            )
            for investor in INVESTORS
        ],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSpeculativeBubble(unittest.TestCase):
    TEST_NAME = "Test 10: Speculative Bubble and Positive Feedback"

    def test_positive_expected_appreciation_generates_buying(self):
        result = run_scenario(
            BASE_SCENARIO
        )

        self.assertGreater(
            result.trace[0].reality.system["buyers"],
            0,
        )

    def test_buying_raises_price(self):
        result = run_scenario(
            BASE_SCENARIO
        )

        self.assertGreater(
            result.final["price"],
            result.initial["price"],
        )

    def test_stronger_feedback_produces_more_amplification(self):
        weak = run_scenario(
            with_feedback_strength(0.5)
        )

        strong = run_scenario(
            with_feedback_strength(1.5)
        )

        self.assertGreater(
            strong.final["price"],
            weak.final["price"],
        )

    def test_removing_feedback_dampens_price_path(self):
        no_feedback = run_scenario(
            with_feedback_strength(0.0)
        )

        positive_feedback = run_scenario(
            BASE_SCENARIO
        )

        self.assertGreater(
            positive_feedback.final["price"],
            no_feedback.final["price"],
        )

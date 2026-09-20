"""
TER Replication Test 21: Intertemporal Choice / Time Horizon
Canonical TER: theory/academic.md, Model 5.1; Section 3 (Time Horizon)

Economic question
-----------------
In this configured decision, does changing only the agent's time horizon
H change which consequences its valuation counts, and therefore the
selected action?

Scenario
--------
An agent has two actions, each with a known consequence at a fixed
period and value:

    immediate consequence: period 0, value  4
    delayed consequence:   period 5, value 10

The agent's horizon determines which consequences count toward
valuation:

    SHORT_HORIZON = 2
    LONG_HORIZON  = 8

The two scenarios differ only in H.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 obtain the largest payoff from the decision    fixed
M   Model of Reality          consequence_schedule: each action's known      fixed
                              period and value
F̂   Perceived Feasible Set    IMMEDIATE_PAYOFF_ACTION,                       fixed
                              DELAYED_PAYOFF_ACTION
V   Valuation                 horizon_scoped_value (local): counts an        varied (as a
                              action's consequence only if it falls within   consequence of H)
                              H; reads M and H
H   Time Horizon              SHORT_HORIZON vs. LONG_HORIZON                 varied
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           immediate (short horizon), delayed (long       observed
                              horizon)
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
Short horizon:

    H = 2
    immediate consequence: period 0, value  4
    delayed consequence:   period 5, value 10
    => delayed consequence outside H
    => V(delayed) = 0
    => immediate selected

Long horizon:

    H = 8
    => delayed consequence inside H
    => V(delayed) = 10
    => delayed selected

G, M, F̂, and D are the same in both scenarios. H is the component changed
directly; in this specification V changes as a consequence of H changing
which consequences count.

Assumptions
-----------
- H is represented here as an integer count of periods considered
  relevant to the decision. This is a test-specific operationalization of
  Time Horizon (Section 3), not a universal meaning of horizon.
  AgentSpec.horizon is typed Any; other tests use descriptive strings
  instead, which is equally valid.
- Each action's consequence is described by a "period" (how many periods
  after the decision it is realized) and a "value" (its magnitude),
  declared in model_of_reality["consequence_schedule"]. These are
  test-specific economic facts, not TER primitives. "period" here is
  unrelated to Scenario.periods, which controls the simulation loop
  length; this test uses a single-period Scenario (periods=1) and only
  asks what the agent would select given each horizon.
- horizon_scoped_value is a local valuation rule for this test only. It
  implements V (Model 5.1) as a test-specific specification: an action's
  known consequence counts toward its value only when that consequence's
  period falls within the agent's horizon; otherwise it contributes
  nothing. It is not a TER primitive or a universal equation, and TER
  does not require V to read H directly; this valuation reads H because
  it specifies which consequences the agent counts. (It is registered
  with register_rule, an implementation detail.)
- This is a binary inclusion boundary, not a discount rate. There is no
  decay, weighting, or continuous function of time, and nothing in
  horizon_scoped_value favors the immediate action for being immediate.
  If IMMEDIATE_PAYOFF_VALUE exceeded DELAYED_PAYOFF_VALUE, the immediate
  action would win under both horizons. It wins under the short horizon
  here only because the delayed consequence is excluded from valuation.
- No outcome realization is modeled, and the test does not claim agents
  generally prefer present or future consequences.

Hypothesis
----------
In this configured decision:
1. Under the short horizon, the delayed consequence falls outside H, its
   valuation excludes it, and the decision process selects the
   immediate-payoff action.
2. Under the long horizon, the delayed consequence falls inside H and the
   decision process selects the delayed-payoff action.
3. Changing H changes the delayed action's valuation; the immediate
   action's valuation does not change.
4. The change in selected action follows from that valuation change.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, run_scenario
from research.ter.rules import register_rule


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

IMMEDIATE_PAYOFF_ACTION = "immediate_payoff_action"
DELAYED_PAYOFF_ACTION = "delayed_payoff_action"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

IMMEDIATE_PAYOFF_PERIOD = 0
IMMEDIATE_PAYOFF_VALUE = 4

DELAYED_PAYOFF_PERIOD = 5
DELAYED_PAYOFF_VALUE = 10

# Well clear of the delayed consequence's period on either side, so
# neither horizon sits on the inclusion boundary.
SHORT_HORIZON = 2
LONG_HORIZON = 8


@register_rule("horizon_scoped_value")
def horizon_scoped_value(action, agent):
    """
    Local valuation rule for this test only. Implements V (Model 5.1) as a
    test-specific specification, not a TER primitive or universal
    equation: an action's known consequence counts toward valuation only
    when that consequence's period falls within the agent's horizon (H). A consequence
    whose period exceeds the horizon is not relevant to the current
    decision and contributes nothing. This is a relevance boundary, not
    a discount rate -- there is no decay or weighting, only inclusion or
    exclusion.

    Required model_of_reality field:

        consequence_schedule   action -> {"period": int, "value": float}

    Required agent field:

        horizon   an integer number of periods considered relevant to
                  this decision (see module docstring Assumptions)
    """
    consequence = agent.model_of_reality["consequence_schedule"][action]

    if consequence["period"] > agent.horizon:
        return 0.0

    return consequence["value"]


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="decision_maker",
    objective="obtain the largest payoff from the decision",
    model_of_reality={
        "consequence_schedule": {
            IMMEDIATE_PAYOFF_ACTION: {
                "period": IMMEDIATE_PAYOFF_PERIOD,
                "value": IMMEDIATE_PAYOFF_VALUE,
            },
            DELAYED_PAYOFF_ACTION: {
                "period": DELAYED_PAYOFF_PERIOD,
                "value": DELAYED_PAYOFF_VALUE,
            },
        },
    },
    perceived_feasible_set=[
        IMMEDIATE_PAYOFF_ACTION,
        DELAYED_PAYOFF_ACTION,
    ],
    valuation_rule="horizon_scoped_value",
    decision_process=DecisionProcess.MAXIMIZE,
    horizon=SHORT_HORIZON,
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SHORT_HORIZON_SCENARIO = Scenario(
    name="Short Horizon",
    description="The agent considers only consequences within a short horizon.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)

LONG_HORIZON_SCENARIO = SHORT_HORIZON_SCENARIO.variant(
    name="Long Horizon",
    description="The same agent now considers consequences within a longer horizon.",
    agents=[
        BASE_AGENT.variant(
            horizon=LONG_HORIZON,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIntertemporalChoice(unittest.TestCase):
    TEST_NAME = "Test 21: Intertemporal Choice / Time Horizon"

    def test_short_horizon_agent_selects_immediate_payoff(self):
        agent = run_scenario(SHORT_HORIZON_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            IMMEDIATE_PAYOFF_ACTION,
        )

    def test_long_horizon_agent_selects_delayed_payoff(self):
        agent = run_scenario(LONG_HORIZON_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            DELAYED_PAYOFF_ACTION,
        )

    def test_changing_horizon_changes_the_delayed_actions_valuation(self):
        short = run_scenario(SHORT_HORIZON_SCENARIO).agent(BASE_AGENT.name)
        long_ = run_scenario(LONG_HORIZON_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            short.value_of(DELAYED_PAYOFF_ACTION),
            0.0,
        )

        self.assertEqual(
            long_.value_of(DELAYED_PAYOFF_ACTION),
            DELAYED_PAYOFF_VALUE,
        )

        self.assertNotEqual(
            short.value_of(DELAYED_PAYOFF_ACTION),
            long_.value_of(DELAYED_PAYOFF_ACTION),
        )

        self.assertEqual(
            short.value_of(IMMEDIATE_PAYOFF_ACTION),
            long_.value_of(IMMEDIATE_PAYOFF_ACTION),
        )

    def test_the_change_in_selected_action_follows_from_that_valuation_change(self):
        short = run_scenario(SHORT_HORIZON_SCENARIO).agent(BASE_AGENT.name)
        long_ = run_scenario(LONG_HORIZON_SCENARIO).agent(BASE_AGENT.name)

        # Under the short horizon, the immediate action is valued higher
        # only because the delayed consequence is excluded.
        self.assertGreater(
            short.value_of(IMMEDIATE_PAYOFF_ACTION),
            short.value_of(DELAYED_PAYOFF_ACTION),
        )

        # Under the long horizon, the same immediate valuation is now
        # exceeded once the delayed consequence becomes relevant.
        self.assertGreater(
            long_.value_of(DELAYED_PAYOFF_ACTION),
            long_.value_of(IMMEDIATE_PAYOFF_ACTION),
        )

        self.assertNotEqual(
            short.selected_action,
            long_.selected_action,
        )

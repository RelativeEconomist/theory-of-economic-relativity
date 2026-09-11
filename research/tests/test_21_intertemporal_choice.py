"""
TER Replication Test 21: Intertemporal Choice / Time Horizon

Economic question
------------------
Can TER represent a decision where changing only the agent's time
horizon H changes which consequences are relevant to valuation, and
therefore changes the selected action?

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

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   maximize the value of consequences relevant to the current
        decision
    M   consequence_schedule -- each action's known period and value,
        identical in both scenarios
    F̂   IMMEDIATE_PAYOFF_ACTION, DELAYED_PAYOFF_ACTION -- F equals F̂
    V   horizon_scoped_value, a local valuation rule scoped to this
        test (see Assumptions)
    H   the only component that differs between scenarios:
        SHORT_HORIZON vs. LONG_HORIZON
    D   DecisionProcess.MAXIMIZE, identical in both scenarios
    C   IMMEDIATE_PAYOFF_ACTION (short horizon), DELAYED_PAYOFF_ACTION
        (long horizon)

Tested TER mechanics
--------------------
G     Objective              constant: maximize the value of
                              consequences relevant to the decision
M     Model of reality       consequence_schedule -- constant
F, F̂  Feasible sets          IMMEDIATE_PAYOFF_ACTION,
                              DELAYED_PAYOFF_ACTION; F̂ equals F
V     Valuation               horizon_scoped_value -- CHANGED for the
                              delayed action only, as a consequence of H
H     Time horizon           CHANGED: SHORT_HORIZON vs. LONG_HORIZON --
                              the only TER component changed directly
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        immediate (short horizon), delayed (long
                              horizon)

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

G, M, F, F̂, and D remain constant across both scenarios. H is the only
TER component changed directly; V changes only as a consequence of H
changing which consequences are relevant, not as an independent change.

Assumptions
-----------
- H is represented here as an integer count of periods considered
  relevant to the decision. This is a test-specific operationalization
  of H_{i,t}'s canonical meaning ("the period over which an agent
  considers consequences relevant to a decision") -- not a universal TER
  meaning of horizon. AgentSpec.horizon is typed Any; other tests use
  descriptive strings instead, which remains equally valid.
- Each action's consequence is described by a "period" (how many periods
  after the decision it is realized) and a "value" (its magnitude),
  declared in model_of_reality["consequence_schedule"]. These are
  test-specific economic facts, not TER primitives. "period" here is
  unrelated to Scenario.periods, which controls the simulation loop
  length; this test uses a single-period Scenario (periods=1) and only
  asks what the agent would select given each horizon.
- horizon_scoped_value is a local Model 5.1 valuation rule, scoped to
  this test only, following the same convention as
  capacity_constrained_realization in test_feasibility_contract.py: it
  is registered here, not in the shared rules.py registry, because it is
  specific to this test's economics. It implements a hard relevance
  boundary matching academic.md's own language: a consequence whose
  period falls within the agent's horizon contributes its full value; a
  consequence whose period falls outside the horizon is not relevant to
  the decision and contributes nothing.
- This is a binary relevance-boundary implementation of H, not a
  discount rate. There is no decay, weighting, or continuous function
  of time -- only inclusion or exclusion drawn directly from H_{i,t}. It
  is also not a universal claim that agents prefer present consumption:
  nothing in horizon_scoped_value favors the immediate action for being
  immediate. If IMMEDIATE_PAYOFF_VALUE exceeded DELAYED_PAYOFF_VALUE,
  the immediate action would win under both horizons. It wins under the
  short horizon here only because the delayed action's known
  consequence is entirely excluded from valuation, not because
  immediacy is itself valued.
- This test does not introduce a new TER variable, axiom, or universal
  discount mechanism. horizon_scoped_value is a scenario-specific
  operationalization of the existing H_{i,t}, using the existing
  ValuationRule extension point exactly as net_value, expected_return,
  and other value rules already do.

Hypothesis
----------
1. Under a short horizon, the delayed consequence falls outside the
   relevant window and the agent selects the immediate-payoff action.
2. Under a long horizon, the delayed consequence falls inside the
   relevant window and the agent selects the delayed-payoff action.
3. Changing H changes the delayed action's own valuation; the immediate
   action's valuation does not change.
4. The change in selected action follows from that valuation change --
   every other TER component (G, M, F, F_hat, D) is identical between
   scenarios.
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
    Local Model 5.1 valuation rule for this test only.

    Operationalizes H_{i,t} as academic.md itself describes it: an
    action's known consequence counts toward valuation only when that
    consequence's period falls within the agent's horizon. A consequence
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
    objective="maximize the value of consequences relevant to the current decision",
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
    actual_feasible_set=[
        IMMEDIATE_PAYOFF_ACTION,
        DELAYED_PAYOFF_ACTION,
    ],
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

        # Every other TER component is unchanged between scenarios --
        # only horizon and the resulting selected action differ.
        self.assertEqual(
            short.objective,
            long_.objective,
        )

        self.assertEqual(
            short.model_of_reality,
            long_.model_of_reality,
        )

        self.assertEqual(
            short.actual_feasible_set,
            long_.actual_feasible_set,
        )

        self.assertEqual(
            short.perceived_feasible_set,
            long_.perceived_feasible_set,
        )

        self.assertEqual(
            short.decision_process,
            long_.decision_process,
        )

        self.assertNotEqual(
            short.horizon,
            long_.horizon,
        )

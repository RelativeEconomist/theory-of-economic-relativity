"""
TER Replication Test 02: Decision Processes: Optimization vs. Satisficing
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
Can two different decision processes, applied to the same perceived
feasible set and valuations, select different actions?

Scenario
--------
The same coffee buyer evaluates:

    coffee_a ── V=4
    coffee_b ── V=7
    coffee_c ── V=10

Only the decision process differs between the two scenarios. For
satisficing, threshold = 7.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 choose coffee                                  fixed
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    coffee_a, coffee_b, coffee_c                   fixed
V   Valuation                 ValuationRule.MAPPED: a hand-assigned value    fixed
                              for each coffee
H   Time Horizon              current decision                               fixed
D   Decision Process          DecisionProcess.MAXIMIZE vs.                   varied
                              DecisionProcess.SATISFICE (threshold 7)
C   Selected Action           coffee_c (MAXIMIZE), coffee_b (SATISFICE)      observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
MAXIMIZE selects the highest-valued action in the perceived feasible set.

SATISFICE evaluates actions in order and selects the first action meeting
the threshold.

Assumptions
-----------
- Values are a static, hand-assigned map (valuation["values"]), not
  derived from any utility function.
- SATISFICING_THRESHOLD is a test-specific decision_parameters entry, not
  a TER primitive. It is set equal to COFFEE_B_VALUE so the relationship
  between the threshold and the satisficing choice is explicit.
- Mistaken feasibility and action-to-outcome mechanics are not exercised;
  this test isolates the decision process.

Hypothesis
----------
In this configured scenario:
1. Maximizing selects the highest-valued action.
2. Satisficing may select an acceptable but lower-valued action.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

COFFEE_A = "coffee_a"
COFFEE_B = "coffee_b"
COFFEE_C = "coffee_c"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

COFFEE_A_VALUE = 4
COFFEE_B_VALUE = 7
COFFEE_C_VALUE = 10

SATISFICING_THRESHOLD = COFFEE_B_VALUE


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="coffee_buyer",
    objective="choose coffee",
    model_of_reality={},
    valuation={
        "values": {
            COFFEE_A: COFFEE_A_VALUE,
            COFFEE_B: COFFEE_B_VALUE,
            COFFEE_C: COFFEE_C_VALUE,
        },
    },
    perceived_feasible_set=[
        COFFEE_A,
        COFFEE_B,
        COFFEE_C,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

MAXIMIZING_SCENARIO = Scenario(
    name="Coffee Buyer (Maximizing)",
    description="A single agent chooses among three coffees by maximizing value.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)

SATISFICING_SCENARIO = MAXIMIZING_SCENARIO.variant(
    name="Coffee Buyer (Satisficing)",
    description="The same agent instead accepts the first coffee meeting a threshold.",
    agents=[
        BASE_AGENT.variant(
            decision_process=DecisionProcess.SATISFICE,
            decision_parameters={
                "satisficing_threshold": SATISFICING_THRESHOLD,
            },
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDecisionProcesses(unittest.TestCase):
    TEST_NAME = "Test 02: Decision Processes: Optimization vs. Satisficing"

    def test_maximizing_selects_highest_valued_action(self):
        agent = run_scenario(MAXIMIZING_SCENARIO).agent(BASE_AGENT.name)

        ## The maximizing agent should select the highest-valued action, which is COFFEE_C.
        self.assertEqual(
            agent.selected_action,
            COFFEE_C,
        )

    def test_satisficing_can_select_acceptable_but_lower_valued_action(self):
        agent = run_scenario(SATISFICING_SCENARIO).agent(BASE_AGENT.name)

        ## The satisficing agent should select the first action that meets the threshold, which is COFFEE_B.
        self.assertEqual(
            agent.selected_action,
            COFFEE_B,
        )

        ## The value of the satisficing agent's selected action should be less than the value of COFFEE_C.
        self.assertLess(
            agent.value_of(agent.selected_action),
            agent.value_of(COFFEE_C),
        )

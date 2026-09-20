"""
TER Replication Test 01: Basic Agent Choice
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
Can an agent choose its highest-valued perceived feasible action using a
specified decision process?

Scenario
--------
A coffee buyer evaluates:

    coffee_a ── V=4
    coffee_b ── V=7
    coffee_c ── V=10

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 choose coffee                                  fixed
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    coffee_a, coffee_c, coffee_b                   fixed
V   Valuation                 ValuationRule.MAPPED: a hand-assigned value    fixed
                              for each coffee
H   Time Horizon              current decision                               fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           coffee_c                                       observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
MAXIMIZE selects the highest-valued action in the perceived feasible set.

Assumptions
-----------
- Values are a static, hand-assigned map (valuation["values"]), not
  derived from any utility function.
- Mistaken feasibility and action-to-outcome mechanics are not exercised;
  this test isolates the Model 5.1 decision.

Hypothesis
----------
In this configured scenario:
1. The agent selects the highest-valued action in its perceived feasible
   set.
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


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="coffee_buyer",
    objective="choose coffee",
    model_of_reality={},
    perceived_feasible_set=[
        COFFEE_A,
        COFFEE_C,
        COFFEE_B,
    ],
    valuation={
        "values": {
            COFFEE_A: COFFEE_A_VALUE,
            COFFEE_B: COFFEE_B_VALUE,
            COFFEE_C: COFFEE_C_VALUE,
        },
    },
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIO = Scenario(
    name="Coffee Buyer",
    description="A single agent chooses among three coffees.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBasicAgentChoice(unittest.TestCase):
    TEST_NAME = "Test 01: Basic Agent Choice"

    def test_agent_selects_highest_valued_action(self):
        agent = run_scenario(SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            COFFEE_C,
        )

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
V   Valuation                 mapped_value: a hand-assigned value    fixed
                              for each coffee
H   Time Horizon              current decision                               fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           coffee_c                                       observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
maximize_value selects the highest-valued action in the perceived feasible
set.

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

from research.scenarios.basic_agent_choice import BASE_AGENT, COFFEE_C, SCENARIO
from research.ter import run_scenario


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

"""
TER Replication Test 01: Basic Agent Choice

Economic question
------------------
Can an agent choose its highest-valued perceived feasible action using a
specified decision process?

Scenario
--------
A coffee buyer evaluates:

    coffee_a ── V=4
    coffee_b ── V=7
    coffee_c ── V=10

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

This test uses one maximizing decision process:

    G, M, F̂, V, H
          │
          ▼
     D = MAXIMIZE
          │
          ▼
     C = coffee_c


Tested TER mechanics
--------------------
G   Objective                 specified
M   Model of reality          specified but empty
F̂  Perceived feasible set    three available actions
V   Valuation                 mapped values
H   Time horizon              current decision
D   Decision process          maximize
C   Selected action           observed result

Economic mechanism
------------------
MAXIMIZE selects the highest-valued perceived feasible action.

Assumptions
-----------
- Values are a static, hand-assigned map (valuation["values"]), not
  derived from any utility function.
- The actual feasible set F is identical to the perceived feasible set F̂,
  so this test isolates the Agent Decision Model rather than mistaken
  feasibility or Action to Outcome mechanics.

Hypothesis
----------
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
    actual_feasible_set=[
        COFFEE_A,
        COFFEE_C,
        COFFEE_B,
    ],
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

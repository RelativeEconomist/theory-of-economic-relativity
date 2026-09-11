"""
TER Replication Test 11: Opportunity Cost and Tradeoffs

Economic question
------------------
Can TER represent opportunity cost when an agent chooses among
competing feasible alternatives with different values?

Scenario
--------
A student has one free evening and three ways to spend it:

    STUDY:      V = 10
    WORK_SHIFT: V = 7
    RELAX:      V = 4

All three actions are both actually and perceived feasible.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   choose how to spend the evening
    M   specified but empty
    F̂   STUDY, WORK_SHIFT, RELAX -- F equals F̂
    V   ValuationRule.MAPPED -- each action's value read from a
        declared map
    H   this evening
    D   DecisionProcess.MAXIMIZE
    C   STUDY

Tested TER mechanics
--------------------
G     Objective              constant: choose how to spend the evening
M     Model of reality       specified but empty
F, F̂  Feasible sets          STUDY, WORK_SHIFT, RELAX; F̂ equals F
V     Valuation               ValuationRule.MAPPED, a static declared map
H     Time horizon           constant: this evening
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        STUDY, observed result

Economic mechanism
------------------
    STUDY       V=10  -> selected
    WORK_SHIFT  V=7   -> best unchosen alternative
    RELAX       V=4

Opportunity cost in this test = 7, the value of the best unchosen
alternative (WORK_SHIFT). Opportunity cost has no dedicated rule or 
helper here, and is read directly off ordinary TER outputs -- the 
best unchosen action among perceived_feasible_set, and its 
value from agent.value_of().

Assumptions
-----------
- Values are a static, hand-assigned map (valuation["values"]), not
  derived from any utility function.
- Opportunity cost is not a TER primitive and has no dedicated rule or
  helper here. It is read directly off ordinary TER outputs: the best
  unchosen action among perceived_feasible_set, and its value from
  agent.value_of().
- For this test, opportunity cost is measured as the value of the
  highest-valued unchosen perceived-feasible alternative. Because F
  equals F̂ here, that is also the highest-valued unchosen actually
  feasible alternative.

Hypothesis
----------
1. The agent selects the highest-valued feasible action (STUDY).
2. The best unchosen alternative is WORK_SHIFT, not RELAX.
3. The opportunity cost of studying is WORK_SHIFT_VALUE, the value of
   the highest-valued feasible alternative not selected.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

STUDY = "study"
WORK_SHIFT = "work_shift"
RELAX = "relax"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

STUDY_VALUE = 10
WORK_SHIFT_VALUE = 7
RELAX_VALUE = 4


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_STUDENT = AgentSpec(
    name="student",
    objective="choose how to spend one free evening",
    model_of_reality={},
    valuation={
        "values": {
            STUDY: STUDY_VALUE,
            WORK_SHIFT: WORK_SHIFT_VALUE,
            RELAX: RELAX_VALUE,
        },
    },
    actual_feasible_set=[
        WORK_SHIFT,
        STUDY,
        RELAX,
    ],
    perceived_feasible_set=[
        WORK_SHIFT,
        STUDY,
        RELAX,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="this evening",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

FREE_EVENING_SCENARIO = Scenario(
    name="Free Evening",
    description="A student with one free evening chooses between studying, working a shift, or relaxing.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_STUDENT,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestOpportunityCost(unittest.TestCase):
    TEST_NAME = "Test 11: Opportunity Cost and Tradeoffs"

    def test_agent_selects_highest_valued_action(self):
        agent = run_scenario(FREE_EVENING_SCENARIO).agent(BASE_STUDENT.name)

        self.assertEqual(
            agent.selected_action,
            STUDY,
        )

    def test_best_unchosen_alternative_is_work_shift(self):
        agent = run_scenario(FREE_EVENING_SCENARIO).agent(BASE_STUDENT.name)

        unchosen_actions = [
            action
            for action in agent.perceived_feasible_set
            if action != agent.selected_action
        ]

        best_unchosen_action = max(
            unchosen_actions,
            key=agent.value_of,
        )

        self.assertEqual(
            best_unchosen_action,
            WORK_SHIFT,
        )

        self.assertEqual(
            agent.value_of(best_unchosen_action),
            WORK_SHIFT_VALUE,
        )

    def test_opportunity_cost_is_value_of_best_unchosen_alternative(self):
        agent = run_scenario(FREE_EVENING_SCENARIO).agent(BASE_STUDENT.name)

        unchosen_actions = [
            action
            for action in agent.perceived_feasible_set
            if action != agent.selected_action
        ]

        best_unchosen_action = max(
            unchosen_actions,
            key=agent.value_of,
        )

        opportunity_cost = agent.value_of(best_unchosen_action)

        self.assertEqual(
            opportunity_cost,
            WORK_SHIFT_VALUE,
        )

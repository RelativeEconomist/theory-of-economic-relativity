"""
TER Replication Test 11: Opportunity Cost and Tradeoffs
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
In this configured scenario, when an agent chooses among competing
actions it perceives as feasible, can the opportunity cost of the
selected action be read as the value of the best unchosen action in its
Perceived Feasible Set?

Scenario
--------
A student has one free evening and three ways to spend it:

    STUDY:      V = 10
    WORK_SHIFT: V = 7
    RELAX:      V = 4

All three actions are in the student's Perceived Feasible Set.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 choose how to spend one free evening           fixed
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    STUDY, WORK_SHIFT, RELAX                       fixed
V   Valuation                 ValuationRule.MAPPED, a static declared map    fixed
H   Time Horizon              this evening                                   fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           STUDY                                          observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
    STUDY       V=10  -> selected
    WORK_SHIFT  V=7   -> best unchosen action in F̂
    RELAX       V=4

Opportunity cost in this test = 7, the value of the best unchosen action
in the Perceived Feasible Set (WORK_SHIFT). It is read directly off
ordinary outputs -- the unchosen actions in perceived_feasible_set and
their values from agent.value_of() -- with no dedicated rule or helper.

Assumptions
-----------
- Values are a static, hand-assigned map (valuation["values"]), not
  derived from any utility function.
- Opportunity cost is not a TER primitive. Here it is measured as the
  value of the highest-valued unchosen action in F̂, that is, over the
  alternatives the agent perceives as feasible. The test makes no claim
  about which alternatives are objectively feasible.

Hypothesis
----------
In this configuration:
1. The decision process (MAXIMIZE) selects the highest-valued action in F̂
   (STUDY).
2. The best unchosen action in F̂ is WORK_SHIFT, not RELAX.
3. The opportunity cost of studying, measured as the value of the
   highest-valued unchosen action in F̂, is WORK_SHIFT_VALUE.
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

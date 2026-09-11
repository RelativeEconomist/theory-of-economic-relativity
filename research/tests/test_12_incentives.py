"""
TER Replication Test 12: Incentives and Behavioral Response

Economic question
------------------
Can TER represent an incentive change where adding a cost to one action
changes the action selected by the same agent?

Scenario
--------
A commuter chooses DRIVE or TAKE_TRANSIT:

    DRIVE:        private value 10
    TAKE_TRANSIT: private value 7

Without a tax, DRIVE (10) beats TAKE_TRANSIT (7). With a driving tax of
4, DRIVE's net value falls to 6 while TAKE_TRANSIT remains 7 -- the same
agent switches from DRIVE to TAKE_TRANSIT.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   choose the most valuable way to commute
    M   specified but empty
    F̂   DRIVE, TAKE_TRANSIT -- F equals F̂
    V   ValuationRule.NET -- benefit minus cost
    H   current commute decision
    D   DecisionProcess.MAXIMIZE
    C   the selected commute action

Tested TER mechanics
--------------------
G     Objective              constant: choose the most valuable way to
                              commute
M     Model of reality       specified but empty
F, F̂  Feasible sets          DRIVE, TAKE_TRANSIT; F̂ equals F
V     Valuation               ValuationRule.NET -- CHANGED between
                              scenarios (DRIVE's cost only)
H     Time horizon           constant: current commute decision
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        DRIVE or TAKE_TRANSIT, observed result

Economic mechanism
------------------
No tax:

    DRIVE        10 - 0 = 10  -> selected
    TAKE_TRANSIT  7 - 0 = 7

Driving tax:

    DRIVE        10 - 4 = 6
    TAKE_TRANSIT  7 - 0 = 7   -> selected

Assumptions
-----------
- The driving tax is a test-specific economic assumption represented as
  a cost inside ValuationRule.NET's existing benefit-minus-cost valuation,
  not a new TER primitive, rule, or helper.
- The tax is represented here as a cost in V because this test models
  its effect on the commuter's valuation. A belief about the tax --
  for example, whether the commuter expects it to apply -- would
  instead belong in M.
- TAKE_TRANSIT carries no cost in either scenario; only DRIVE's cost
  changes between scenarios.

Hypothesis
----------
1. Without the tax, the agent selects DRIVE.
2. With the tax, the same agent selects TAKE_TRANSIT.
3. The behavioral change occurs while the objective, feasible actions,
   and decision process remain unchanged.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

DRIVE = "drive"
TAKE_TRANSIT = "take_transit"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

DRIVE_PRIVATE_VALUE = 10
TAKE_TRANSIT_PRIVATE_VALUE = 7

DRIVING_TAX = 4


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_COMMUTER = AgentSpec(
    name="commuter",
    objective="choose the most valuable way to commute",
    model_of_reality={},
    valuation={
        "benefits": {
            DRIVE: DRIVE_PRIVATE_VALUE,
            TAKE_TRANSIT: TAKE_TRANSIT_PRIVATE_VALUE,
        },
        "costs": {
            DRIVE: 0,
            TAKE_TRANSIT: 0,
        },
    },
    actual_feasible_set=[
        DRIVE,
        TAKE_TRANSIT,
    ],
    perceived_feasible_set=[
        DRIVE,
        TAKE_TRANSIT,
    ],
    valuation_rule=ValuationRule.NET,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current commute decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

NO_TAX_SCENARIO = Scenario(
    name="Commute Without a Driving Tax",
    description="A commuter chooses between driving and transit with no cost on either option.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_COMMUTER,
    ],
)

DRIVING_TAX_SCENARIO = NO_TAX_SCENARIO.variant(
    name="Commute With a Driving Tax",
    description="The same commuter now faces a tax on driving.",
    agents=[
        BASE_COMMUTER.variant(
            valuation={
                "costs": {
                    DRIVE: DRIVING_TAX,
                    TAKE_TRANSIT: 0,
                },
            },
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIncentives(unittest.TestCase):
    TEST_NAME = "Test 12: Incentives and Behavioral Response"

    def test_agent_drives_without_the_tax(self):
        agent = run_scenario(NO_TAX_SCENARIO).agent(BASE_COMMUTER.name)

        self.assertEqual(
            agent.selected_action,
            DRIVE,
        )

    def test_agent_switches_to_transit_with_the_tax(self):
        agent = run_scenario(DRIVING_TAX_SCENARIO).agent(BASE_COMMUTER.name)

        self.assertEqual(
            agent.selected_action,
            TAKE_TRANSIT,
        )

        self.assertEqual(
            agent.value_of(DRIVE),
            DRIVE_PRIVATE_VALUE - DRIVING_TAX,
        )

        self.assertEqual(
            agent.value_of(TAKE_TRANSIT),
            TAKE_TRANSIT_PRIVATE_VALUE,
        )

    def test_behavioral_change_leaves_the_rest_of_the_agent_unchanged(self):
        without_tax = run_scenario(NO_TAX_SCENARIO).agent(BASE_COMMUTER.name)
        with_tax = run_scenario(DRIVING_TAX_SCENARIO).agent(BASE_COMMUTER.name)

        self.assertNotEqual(
            without_tax.selected_action,
            with_tax.selected_action,
        )

        self.assertEqual(
            without_tax.objective,
            with_tax.objective,
        )

        self.assertEqual(
            without_tax.actual_feasible_set,
            with_tax.actual_feasible_set,
        )

        self.assertEqual(
            without_tax.perceived_feasible_set,
            with_tax.perceived_feasible_set,
        )

        self.assertEqual(
            without_tax.decision_process,
            with_tax.decision_process,
        )

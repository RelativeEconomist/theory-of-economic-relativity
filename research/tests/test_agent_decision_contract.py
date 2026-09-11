"""
Framework test: agent decision contract.

Purpose
-------
Not an economic replication test. Verifies two structural guarantees of
TER Model 5.1's decision step (research/ter/decision.py::select_action),
independent of any specific economic scenario:

1. The selected action C is always a member of the agent's perceived
   feasible set F_hat.
2. An empty perceived feasible set cannot produce a selected action.

These were previously demonstrated inside an economic replication test
(coffee choice) even though they are properties of the decision
mechanism itself, not economic claims. They live here instead so a
future change to the coffee example can't accidentally weaken framework
coverage, and so an economic test doesn't need to also prove framework
internals.

TestMaximizeTieBreakContract below covers a third, narrower guarantee:
DecisionProcess.MAXIMIZE's optional tie_break_preference (D
configuration, not a TER primitive) only ever resolves ties among
actions already sharing the highest value, never overrides a unique
higher-valued action, and must itself be a perceived feasible action.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

COFFEE_A = "coffee_a"


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="coffee_buyer",
    objective="choose coffee",
    model_of_reality={},
    valuation={
        "values": {
            COFFEE_A: 1,
        },
    },
    actual_feasible_set=[
        COFFEE_A,
    ],
    perceived_feasible_set=[
        COFFEE_A,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SINGLETON_SCENARIO = Scenario(
    name="Singleton Feasible Set",
    description="An agent whose perceived feasible set contains only one action.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)

EMPTY_PERCEIVED_FEASIBLE_SCENARIO = SINGLETON_SCENARIO.variant(
    agents=[
        BASE_AGENT.variant(
            perceived_feasible_set=[],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAgentDecisionContract(unittest.TestCase):
    TEST_NAME = "Framework: Agent Decision Contract"

    def test_selected_action_must_belong_to_perceived_feasible_set(self):
        agent = run_scenario(SINGLETON_SCENARIO).agent(BASE_AGENT.name)

        self.assertIn(
            agent.selected_action,
            agent.perceived_feasible_set,
        )

    def test_empty_perceived_feasible_set_cannot_select_action(self):
        with self.assertRaisesRegex(
            ValueError,
            "Perceived feasible set cannot be empty",
        ):
            run_scenario(EMPTY_PERCEIVED_FEASIBLE_SCENARIO)


# ---------------------------------------------------------------------------
# MAXIMIZE tie-break contract
# ---------------------------------------------------------------------------

ACTION_A = "action_a"
ACTION_B = "action_b"
ACTION_C = "action_c"

TIE_BREAK_BASE_AGENT = AgentSpec(
    name="tie_break_agent",
    objective="test objective",
    model_of_reality={},
    valuation={
        "values": {
            ACTION_A: 5,
            ACTION_B: 5,
            ACTION_C: 1,
        },
    },
    actual_feasible_set=[
        ACTION_A,
        ACTION_B,
        ACTION_C,
    ],
    perceived_feasible_set=[
        ACTION_A,
        ACTION_B,
        ACTION_C,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current decision",
)

# Case 1: ACTION_A and ACTION_B are tied for the highest value (5).
# tie_break_preference names ACTION_B, one of the tied actions.
TIED_WITH_PREFERENCE_SCENARIO = SINGLETON_SCENARIO.variant(
    agents=[
        TIE_BREAK_BASE_AGENT.variant(
            decision_parameters={
                "tie_break_preference": ACTION_B,
            },
        ),
    ],
)

# Case 2: ACTION_A is uniquely highest (10); tie_break_preference names
# ACTION_B, which is not tied for the maximum.
UNIQUE_MAXIMUM_SCENARIO = SINGLETON_SCENARIO.variant(
    agents=[
        TIE_BREAK_BASE_AGENT.variant(
            valuation={
                "values": {
                    ACTION_A: 10,
                    ACTION_B: 5,
                    ACTION_C: 1,
                },
            },
            decision_parameters={
                "tie_break_preference": ACTION_B,
            },
        ),
    ],
)

# Case 3: tie_break_preference names an action outside perceived_feasible_set.
PREFERENCE_OUTSIDE_FHAT_SCENARIO = SINGLETON_SCENARIO.variant(
    agents=[
        TIE_BREAK_BASE_AGENT.variant(
            decision_parameters={
                "tie_break_preference": "not_perceived_feasible",
            },
        ),
    ],
)


class TestMaximizeTieBreakContract(unittest.TestCase):
    TEST_NAME = "Framework: MAXIMIZE Tie-Break Contract"

    def test_tied_maxima_with_valid_preference_selects_preferred_action(self):
        agent = run_scenario(TIED_WITH_PREFERENCE_SCENARIO).agent(TIE_BREAK_BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            ACTION_B,
        )

    def test_unique_maximum_is_not_overridden_by_a_lower_valued_preference(self):
        agent = run_scenario(UNIQUE_MAXIMUM_SCENARIO).agent(TIE_BREAK_BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            ACTION_A,
        )

    def test_preference_outside_perceived_feasible_set_raises_value_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "tie_break_preference must be in the perceived feasible set",
        ):
            run_scenario(PREFERENCE_OUTSIDE_FHAT_SCENARIO)

"""
Framework test: valuation view contract

Canonical TER: theory/academic.md, Model 5.1

Purpose
-------
Verifies that V receives the same information wherever it is evaluated:

    V(a | G, M, H)

During a real run, D consults V through a ValuationView carrying only G
(objective), M (model_of_reality), H (horizon) and the implementation
storage for V (valuation). AgentResult.value_of must evaluate V against
that same view, not the full AgentState -- so agent name, F̂, D, its
decision_parameters, and the update rule are never exposed to V.

Out of scope
------------
Realized outcomes. No reality rule is defined.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.decision import ValuationView
from research.ter.rules import mapped_value, maximize_value


COFFEE_A = "coffee_a"
COFFEE_B = "coffee_b"

COFFEE_A_VALUE = 1
COFFEE_B_VALUE = 3

NON_VALUATION_FIELDS = (
    "name",
    "perceived_feasible_set",
    "decision_parameters",
    "decision_process",
    "update",
    "value",
)


def recording_value(received):
    def value(action, view):
        received.append(view)
        return mapped_value(action, view)

    return value


def make_agent(value_rule):
    return AgentSpec(
        name="coffee_buyer",
        objective="choose coffee",
        model_of_reality={"belief": "coffee is available"},
        valuation={
            "values": {
                COFFEE_A: COFFEE_A_VALUE,
                COFFEE_B: COFFEE_B_VALUE,
            },
        },
        perceived_feasible_set=[COFFEE_A, COFFEE_B],
        valuation_rule=value_rule,
        decision_process=maximize_value,
        horizon="current decision",
        decision_parameters={"tie_break_preference": COFFEE_A},
        update_rule=lambda agent, observation: {},
    )


def run(value_rule):
    agent = make_agent(value_rule)

    return run_scenario(
        Scenario(
            name="Valuation View",
            description="One agent valuing two perceived actions.",
            periods=1,
            initial_state={},
            agents=[agent],
        )
    ).agent(agent.name)


class TestValuationViewContract(unittest.TestCase):
    TEST_NAME = "Framework: Valuation View Contract"

    def test_value_of_receives_the_same_valuation_view_as_decision_time_valuation(self):
        received = []
        agent = run(recording_value(received))

        decision_views = list(received)
        self.assertTrue(decision_views)

        received.clear()
        value_of_result = agent.value_of(COFFEE_B)
        [value_of_view] = received

        for view in [*decision_views, value_of_view]:
            self.assertIsInstance(view, ValuationView)

            for field_name in NON_VALUATION_FIELDS:
                self.assertFalse(
                    hasattr(view, field_name),
                    f"V must not receive {field_name!r}.",
                )

        for decision_view in decision_views:
            self.assertEqual(value_of_view, decision_view)

        # Restricting the view leaves the valuation result unchanged.
        self.assertEqual(value_of_result, COFFEE_B_VALUE)
        self.assertEqual(
            run(mapped_value).value_of(COFFEE_B),
            COFFEE_B_VALUE,
        )
        self.assertEqual(agent.selected_action, COFFEE_B)


if __name__ == "__main__":
    unittest.main()

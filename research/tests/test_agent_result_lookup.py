"""
Framework test: AgentResult attribute lookup precedence.

Purpose
-------
This is not an economic replication test. It verifies
AgentResult.__getattr__'s lookup precedence directly:

    1. per-agent outcome fields
    2. AgentState's own fields
    3. AgentState.model_of_reality fields
    4. AttributeError

This is API convenience only -- it does not exercise or change TER
execution, and it does not copy or move any model_of_reality data.
"""

import unittest

from research.ter.agent import AgentState
from research.ter.scenario import AgentResult


def make_agent(model_of_reality):
    return AgentState(
        objective="test objective",
        model_of_reality=model_of_reality,
        actual_feasible_set=["a"],
        perceived_feasible_set=["a"],
        value=lambda action, agent: 0.0,
        horizon="test horizon",
        decision_process=lambda agent: "a",
        name="test_agent",
        valuation={},
        decision_parameters={},
    )


class TestAgentResultLookupPrecedence(unittest.TestCase):
    TEST_NAME = "Framework: AgentResult Lookup Precedence"

    def test_model_fields_are_reachable_by_attribute(self):
        agent = make_agent(
            model_of_reality={
                "failure_probability": 0.42,
            }
        )

        result = AgentResult(
            state=agent,
            outcome={},
        )

        self.assertEqual(
            result.failure_probability,
            0.42,
        )

    def test_outcome_fields_take_precedence_over_state_fields(self):
        agent = make_agent(model_of_reality={})

        result = AgentResult(
            state=agent,
            outcome={
                "objective": "outcome-provided objective",
            },
        )

        self.assertEqual(
            result.objective,
            "outcome-provided objective",
        )

    def test_state_fields_take_precedence_over_model_fields(self):
        agent = make_agent(
            model_of_reality={
                "objective": "model-provided objective",
            }
        )

        result = AgentResult(
            state=agent,
            outcome={},
        )

        self.assertEqual(
            result.objective,
            "test objective",
        )

    def test_unknown_attribute_raises_attribute_error(self):
        agent = make_agent(
            model_of_reality={
                "failure_probability": 0.42,
            }
        )

        result = AgentResult(
            state=agent,
            outcome={},
        )

        with self.assertRaises(AttributeError):
            result.nonexistent_field

    def test_model_fallback_does_not_copy_or_mutate_model_data(self):
        model = {
            "failure_probability": 0.42,
        }

        agent = make_agent(model_of_reality=model)

        result = AgentResult(
            state=agent,
            outcome={},
        )

        self.assertIs(
            result.state.model_of_reality,
            model,
        )

        _ = result.failure_probability

        self.assertEqual(
            model,
            {
                "failure_probability": 0.42,
            },
        )

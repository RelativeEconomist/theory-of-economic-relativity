"""
Framework test: AgentGroup.

Purpose
-------
This is not an economic replication test. AgentGroup is a researcher-facing
convenience for declaring several structurally identical agents with
sequential names -- it is not a TER primitive and does not change TER
behavior. This test verifies the convenience itself: every generated item
is an ordinary AgentSpec, naming and start_index behave as documented,
model_of_reality overrides use AgentSpec.variant()'s existing merge
behavior, two groups combine into a plain usable list, and invalid
input is rejected.
Duplicate-name detection is not reimplemented here -- it is still handled
by research.ter.runner.build_agents, exercised via run_scenario().
"""

import unittest

from research.ter import (
    AgentGroup,
    AgentSpec,
    DecisionProcess,
    Scenario,
    ValuationRule,
    run_scenario,
)


BASE_AGENT = AgentSpec(
    name="agent",
    objective="test objective",
    model_of_reality={},
    valuation={
        "values": {
            "a": 1,
        },
    },
    actual_feasible_set=["a"],
    perceived_feasible_set=["a"],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
)


class TestAgentGroup(unittest.TestCase):
    TEST_NAME = "Framework: AgentGroup"

    def test_generates_ordinary_agent_specs(self):
        group = AgentGroup(
            base=BASE_AGENT,
            count=3,
            name_prefix="seller",
        )

        for spec in group:
            self.assertIsInstance(
                spec,
                AgentSpec,
            )

    def test_generates_sequential_names_starting_at_one(self):
        group = AgentGroup(
            base=BASE_AGENT,
            count=3,
            name_prefix="seller",
        )

        self.assertEqual(
            [spec.name for spec in group],
            ["seller_1", "seller_2", "seller_3"],
        )

    def test_custom_start_index_offsets_names(self):
        group = AgentGroup(
            base=BASE_AGENT,
            count=2,
            name_prefix="depositor",
            start_index=4,
        )

        self.assertEqual(
            [spec.name for spec in group],
            ["depositor_4", "depositor_5"],
        )

    def test_model_override_uses_variant_merge_semantics(self):
        group = AgentGroup(
            base=BASE_AGENT,
            count=1,
            name_prefix="seller",
            model_of_reality={
                "risk_signal": 0.5,
            },
        )

        expected = BASE_AGENT.variant(
            name="seller_1",
            model_of_reality={
                "risk_signal": 0.5,
            },
        )

        self.assertEqual(
            group[0].model_of_reality,
            expected.model_of_reality,
        )

    def test_two_groups_combine_into_a_usable_list(self):
        first = AgentGroup(
            base=BASE_AGENT,
            count=2,
            name_prefix="high_risk",
        )

        second = AgentGroup(
            base=BASE_AGENT,
            count=2,
            name_prefix="low_risk",
            start_index=3,
        )

        combined = first + second

        self.assertEqual(
            [spec.name for spec in combined],
            ["high_risk_1", "high_risk_2", "low_risk_3", "low_risk_4"],
        )

        result = run_scenario(
            Scenario(
                name="AgentGroup combination smoke test",
                description="Two combined AgentGroups run as a normal agent list.",
                periods=1,
                initial_state={"period": 0},
                agents=combined,
            )
        )

        self.assertEqual(
            len(result.final["agents"]),
            4,
        )

    def test_count_below_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            AgentGroup(
                base=BASE_AGENT,
                count=0,
                name_prefix="seller",
            )

    def test_duplicate_names_across_groups_are_still_caught_at_run_time(self):
        first = AgentGroup(
            base=BASE_AGENT,
            count=2,
            name_prefix="seller",
        )

        second = AgentGroup(
            base=BASE_AGENT,
            count=2,
            name_prefix="seller",
        )

        scenario = Scenario(
            name="AgentGroup duplicate name smoke test",
            description="Two groups reusing the same prefix and range collide.",
            periods=1,
            initial_state={"period": 0},
            agents=first + second,
        )

        with self.assertRaises(ValueError):
            run_scenario(scenario)

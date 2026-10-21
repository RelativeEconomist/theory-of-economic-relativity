"""
Framework test: Basic Agent Choice adapter.

Purpose
-------
This is not an economic replication test. It verifies that the JSON-safe
adapter runs the reusable Basic Agent Choice scenario through run_scenario
and does not reimplement its valuation or decision process.
"""

import json
import unittest

from research.adapters.basic_agent_choice import SCENARIO_ID, build_scenario, run
from research.scenarios.basic_agent_choice import (
    BASE_AGENT,
    COFFEE_A,
    COFFEE_B,
    COFFEE_C,
    SCENARIO,
)
from research.ter import run_scenario


def direct_result(scenario):
    agent = run_scenario(scenario).agent(BASE_AGENT.name)

    return {
        "selected_action": agent.selected_action,
        "action_values": {
            action: agent.value_of(action)
            for action in agent.state.perceived_feasible_set
        },
    }


class TestBasicAgentChoiceAdapter(unittest.TestCase):
    TEST_NAME = "Framework: Basic Agent Choice Adapter"

    def test_default_run_matches_reusable_scenario(self):
        result = run({"scenario": SCENARIO_ID})

        self.assertEqual(
            result,
            {
                "scenario": SCENARIO_ID,
                "name": SCENARIO.name,
                **direct_result(SCENARIO),
            },
        )
        self.assertEqual(result["selected_action"], COFFEE_C)

    def test_configured_values_match_direct_variant_run(self):
        values = {COFFEE_A: 9, COFFEE_B: 7.5, COFFEE_C: 1}
        variant = SCENARIO.variant(
            agents=[BASE_AGENT.variant(valuation={"values": values})],
        )

        result = run({"scenario": SCENARIO_ID, "action_values": values})

        self.assertEqual(result["selected_action"], COFFEE_A)
        self.assertEqual(
            {
                "selected_action": result["selected_action"],
                "action_values": result["action_values"],
            },
            direct_result(variant),
        )

    def test_ties_follow_the_reusable_decision_process(self):
        # maximize_value breaks ties by F_hat order (coffee_a, coffee_c,
        # coffee_b), not by input order or alphabetical order.
        result = run(
            {
                "scenario": SCENARIO_ID,
                "action_values": {COFFEE_B: 10, COFFEE_C: 10, COFFEE_A: 1},
            }
        )

        self.assertEqual(result["selected_action"], COFFEE_C)

    def test_scenarios_reuse_the_shared_rules(self):
        default = build_scenario({"scenario": SCENARIO_ID})
        configured = build_scenario(
            {
                "scenario": SCENARIO_ID,
                "action_values": {COFFEE_A: 1, COFFEE_B: 2, COFFEE_C: 3},
            }
        )

        self.assertIs(default, SCENARIO)

        (agent,) = configured.agents
        self.assertIs(agent.valuation_rule, BASE_AGENT.valuation_rule)
        self.assertIs(agent.decision_process, BASE_AGENT.decision_process)
        self.assertEqual(
            agent.perceived_feasible_set,
            BASE_AGENT.perceived_feasible_set,
        )

    def test_input_and_output_are_json_safe(self):
        for request in (
            {"scenario": SCENARIO_ID},
            {
                "scenario": SCENARIO_ID,
                "action_values": {COFFEE_A: 1, COFFEE_B: 2.5, COFFEE_C: 3},
            },
        ):
            with self.subTest(request=request):
                json.dumps(request, allow_nan=False)
                result = run(request)
                encoded = json.dumps(result, allow_nan=False)
                self.assertEqual(json.loads(encoded), result)

    def test_unsupported_scenario_is_rejected(self):
        for scenario_id in ("other-scenario", None):
            with self.subTest(scenario_id=scenario_id):
                with self.assertRaisesRegex(ValueError, "basic-agent-choice"):
                    run({"scenario": scenario_id})

        with self.assertRaisesRegex(ValueError, "basic-agent-choice"):
            run({})

    def test_invalid_requests_are_rejected(self):
        valid_values = {COFFEE_A: 1, COFFEE_B: 2, COFFEE_C: 3}

        cases = [
            (TypeError, ["basic-agent-choice"]),
            (TypeError, {"scenario": SCENARIO_ID, "action_values": [1, 2, 3]}),
            (ValueError, {"scenario": SCENARIO_ID, "periods": 2}),
            (ValueError, {"scenario": SCENARIO_ID, "action_values": {}}),
            (
                ValueError,
                {"scenario": SCENARIO_ID, "action_values": {COFFEE_A: 1, COFFEE_B: 2}},
            ),
            (
                ValueError,
                {
                    "scenario": SCENARIO_ID,
                    "action_values": {**valid_values, "coffee_d": 4},
                },
            ),
            (
                TypeError,
                {
                    "scenario": SCENARIO_ID,
                    "action_values": {**valid_values, COFFEE_A: "4"},
                },
            ),
            (
                TypeError,
                {
                    "scenario": SCENARIO_ID,
                    "action_values": {**valid_values, COFFEE_A: True},
                },
            ),
            (
                ValueError,
                {
                    "scenario": SCENARIO_ID,
                    "action_values": {**valid_values, COFFEE_A: float("nan")},
                },
            ),
        ]

        for error, request in cases:
            with self.subTest(request=request):
                with self.assertRaises(error):
                    run(request)

    def test_out_of_range_values_are_rejected(self):
        bound = 1_000_000_000_000
        valid_values = {COFFEE_A: 1, COFFEE_B: 2, COFFEE_C: 3}

        # 10**400 is too large to convert to float.
        for value in (bound + 1, -(bound + 1), 1e300, -1e300, 10**400, -(10**400)):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "out of range"):
                    run(
                        {
                            "scenario": SCENARIO_ID,
                            "action_values": {**valid_values, COFFEE_A: value},
                        }
                    )

        result = run(
            {
                "scenario": SCENARIO_ID,
                "action_values": {COFFEE_A: bound, COFFEE_B: -bound, COFFEE_C: 0},
            }
        )
        self.assertEqual(result["selected_action"], COFFEE_A)

    def test_supplied_values_do_not_change_the_reusable_scenario(self):
        run(
            {
                "scenario": SCENARIO_ID,
                "action_values": {COFFEE_A: 9, COFFEE_B: 8, COFFEE_C: 7},
            }
        )

        self.assertEqual(
            BASE_AGENT.valuation["values"],
            {COFFEE_A: 4, COFFEE_B: 7, COFFEE_C: 10},
        )
        self.assertIs(SCENARIO.agents[0], BASE_AGENT)


if __name__ == "__main__":
    unittest.main()

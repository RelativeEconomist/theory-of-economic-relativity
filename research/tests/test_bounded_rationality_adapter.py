"""
Framework test: Bounded Rationality adapter.

Purpose
-------
This is not an economic replication test. It verifies that the JSON-safe
adapter runs the reusable Bounded Rationality scenarios through
run_scenario, changes only the decision process between maximize_value and
limited_search, and does not reimplement valuation or selection.
"""

import json
import unittest

from research.adapters.bounded_rationality import SCENARIO_ID, build_scenario, run
from research.scenarios.bounded_rationality import (
    BASE_AGENT,
    BEST_COFFEE,
    BROADER_SEARCH_SCENARIO,
    EXHAUSTIVE_SCENARIO,
    LIMITED_SCENARIO,
    NEARBY_COFFEE,
    OFFICE_COFFEE,
    REORDERED_SCENARIO,
)
from research.ter import run_scenario


def direct_selection(scenario):
    agent = run_scenario(scenario).agent(BASE_AGENT.name)

    return agent.selected_action, agent.value_of(agent.selected_action)


class TestBoundedRationalityAdapter(unittest.TestCase):
    TEST_NAME = "Framework: Bounded Rationality Adapter"

    def assert_run(self, request, scenario, considered, not_considered):
        result = run({"scenario": SCENARIO_ID, **request})
        selected_action, selected_value = direct_selection(scenario)

        self.assertEqual(result["selected_action"], selected_action)
        self.assertEqual(result["selected_value"], selected_value)
        self.assertEqual(result["considered_actions"], considered)
        self.assertEqual(result["not_considered_actions"], not_considered)

        return result

    def test_maximize_value_considers_every_action_and_selects_the_best(self):
        result = self.assert_run(
            {"decision_process": "maximize_value"},
            EXHAUSTIVE_SCENARIO,
            considered=[NEARBY_COFFEE, OFFICE_COFFEE, BEST_COFFEE],
            not_considered=[],
        )

        self.assertEqual(result["decision_process"], "maximize_value")
        self.assertEqual(result["selected_action"], BEST_COFFEE)

    def test_limited_search_of_two_misses_the_best_action(self):
        # The reusable scenario's own defaults: limited_search, limit 2.
        for request in ({}, {"decision_process": "limited_search", "search_limit": 2}):
            with self.subTest(request=request):
                result = self.assert_run(
                    request,
                    LIMITED_SCENARIO,
                    considered=[NEARBY_COFFEE, OFFICE_COFFEE],
                    not_considered=[BEST_COFFEE],
                )

                self.assertEqual(result["decision_process"], "limited_search")
                self.assertEqual(result["selected_action"], OFFICE_COFFEE)
                self.assertEqual(result["search_limit"], 2)
                self.assertEqual(
                    result["search_order"], [NEARBY_COFFEE, OFFICE_COFFEE, BEST_COFFEE]
                )

    def test_limited_search_of_three_reaches_the_best_action(self):
        result = self.assert_run(
            {"decision_process": "limited_search", "search_limit": 3},
            BROADER_SEARCH_SCENARIO,
            considered=[NEARBY_COFFEE, OFFICE_COFFEE, BEST_COFFEE],
            not_considered=[],
        )

        self.assertEqual(result["selected_action"], BEST_COFFEE)

    def test_changed_search_order_can_reach_the_best_action(self):
        search_order = [NEARBY_COFFEE, BEST_COFFEE, OFFICE_COFFEE]

        result = self.assert_run(
            {
                "decision_process": "limited_search",
                "search_limit": 2,
                "search_order": search_order,
            },
            REORDERED_SCENARIO,
            considered=[NEARBY_COFFEE, BEST_COFFEE],
            not_considered=[OFFICE_COFFEE],
        )

        self.assertEqual(result["selected_action"], BEST_COFFEE)
        self.assertEqual(result["search_order"], search_order)

    def test_only_the_decision_process_differs(self):
        values = {NEARBY_COFFEE: 9, OFFICE_COFFEE: 7.5, BEST_COFFEE: 1}
        maximizing = build_scenario(
            {"scenario": SCENARIO_ID, "decision_process": "maximize_value", "action_values": values}
        )
        limited = build_scenario(
            {"scenario": SCENARIO_ID, "decision_process": "limited_search", "action_values": values}
        )

        (maximizing_agent,) = maximizing.agents
        (limited_agent,) = limited.agents

        for component in (
            "objective",
            "model_of_reality",
            "perceived_feasible_set",
            "valuation",
            "valuation_rule",
            "horizon",
        ):
            with self.subTest(component=component):
                self.assertEqual(
                    getattr(maximizing_agent, component),
                    getattr(limited_agent, component),
                )

        self.assertIsNot(maximizing_agent.decision_process, limited_agent.decision_process)
        self.assertEqual(
            limited_agent.perceived_feasible_set, BASE_AGENT.perceived_feasible_set
        )

    def test_edited_values_match_a_direct_variant_run(self):
        values = {NEARBY_COFFEE: 9, OFFICE_COFFEE: 7.5, BEST_COFFEE: 1}
        variant = LIMITED_SCENARIO.variant(
            agents=[BASE_AGENT.variant(valuation={"values": values})],
        )

        result = self.assert_run(
            {"action_values": values},
            variant,
            considered=[NEARBY_COFFEE, OFFICE_COFFEE],
            not_considered=[BEST_COFFEE],
        )

        self.assertEqual(result["selected_action"], NEARBY_COFFEE)
        self.assertEqual(result["action_values"], values)

    def test_input_and_output_are_json_safe(self):
        for request in (
            {"scenario": SCENARIO_ID},
            {"scenario": SCENARIO_ID, "decision_process": "maximize_value"},
            {
                "scenario": SCENARIO_ID,
                "decision_process": "limited_search",
                "action_values": {NEARBY_COFFEE: 1, OFFICE_COFFEE: 2.5, BEST_COFFEE: 3},
                "search_limit": 1,
                "search_order": [BEST_COFFEE, NEARBY_COFFEE, OFFICE_COFFEE],
            },
        ):
            with self.subTest(request=request):
                json.dumps(request, allow_nan=False)
                result = run(request)
                encoded = json.dumps(result, allow_nan=False)
                self.assertEqual(json.loads(encoded), result)

    def test_unsupported_scenario_is_rejected(self):
        for request in ({"scenario": "basic-agent-choice"}, {"scenario": None}, {}):
            with self.subTest(request=request):
                with self.assertRaisesRegex(ValueError, SCENARIO_ID):
                    run(request)

    def test_invalid_requests_are_rejected(self):
        valid_values = {NEARBY_COFFEE: 1, OFFICE_COFFEE: 2, BEST_COFFEE: 3}
        order = [NEARBY_COFFEE, OFFICE_COFFEE, BEST_COFFEE]

        cases = [
            (TypeError, "dict", [SCENARIO_ID]),
            (ValueError, "Unknown", {"periods": 2}),
            (ValueError, "decision_process", {"decision_process": "satisfice"}),
            (ValueError, "decision_process", {"decision_process": None}),
            (ValueError, "decision_process", {"decision_process": ["limited_search"]}),
            (
                ValueError,
                "limited_search",
                {"decision_process": "maximize_value", "search_limit": 2},
            ),
            (
                ValueError,
                "limited_search",
                {"decision_process": "maximize_value", "search_order": order},
            ),
            (TypeError, "action_values", {"action_values": [1, 2, 3]}),
            (ValueError, "action_values", {"action_values": {NEARBY_COFFEE: 1}}),
            (
                ValueError,
                "action_values",
                {"action_values": {**valid_values, "coffee_d": 4}},
            ),
            (TypeError, "number", {"action_values": {**valid_values, NEARBY_COFFEE: "4"}}),
            (TypeError, "number", {"action_values": {**valid_values, NEARBY_COFFEE: True}}),
            (
                ValueError,
                "finite",
                {"action_values": {**valid_values, NEARBY_COFFEE: float("nan")}},
            ),
            (
                ValueError,
                "out of range",
                {"action_values": {**valid_values, NEARBY_COFFEE: 10**400}},
            ),
            (TypeError, "search_limit", {"search_limit": "2"}),
            (TypeError, "search_limit", {"search_limit": 2.0}),
            (TypeError, "search_limit", {"search_limit": True}),
            (ValueError, "search_limit", {"search_limit": 0}),
            (ValueError, "search_limit", {"search_limit": -1}),
            (ValueError, "search_limit", {"search_limit": 4}),
            (TypeError, "search_order", {"search_order": NEARBY_COFFEE}),
            (ValueError, "search_order", {"search_order": order[:2]}),
            (ValueError, "search_order", {"search_order": [NEARBY_COFFEE, *order[:2]]}),
            (ValueError, "search_order", {"search_order": [*order, "coffee_d"]}),
            (ValueError, "search_order", {"search_order": [{}, [], 1]}),
        ]

        for error, message, request in cases:
            if isinstance(request, dict):
                request = {"scenario": SCENARIO_ID, **request}

            with self.subTest(request=request):
                with self.assertRaisesRegex(error, message):
                    run(request)

    def test_runs_do_not_change_the_reusable_scenario(self):
        run(
            {
                "scenario": SCENARIO_ID,
                "action_values": {NEARBY_COFFEE: 9, OFFICE_COFFEE: 8, BEST_COFFEE: 7},
                "search_limit": 1,
                "search_order": [BEST_COFFEE, OFFICE_COFFEE, NEARBY_COFFEE],
            }
        )

        self.assertEqual(
            BASE_AGENT.valuation["values"],
            {NEARBY_COFFEE: 6, OFFICE_COFFEE: 7, BEST_COFFEE: 10},
        )
        self.assertEqual(
            BASE_AGENT.decision_parameters,
            {"search_limit": 2, "search_order": [NEARBY_COFFEE, OFFICE_COFFEE, BEST_COFFEE]},
        )
        self.assertIs(LIMITED_SCENARIO.agents[0], BASE_AGENT)


if __name__ == "__main__":
    unittest.main()

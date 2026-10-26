"""Protect Pokémon valuation, realization boundaries, validation, and provenance."""

import copy
import json
import unittest

from research.adapters.pokemon_card_choice import SCENARIO_ID, build_scenario, run
from research.scenarios.pokemon_card_choice import KEEP, SCENARIO, SELL, STUDENT
from research.ter import __version__, run_scenario


class TestPokemonCardChoiceAdapter(unittest.TestCase):
    TEST_NAME = "Framework: Pokemon Card Choice Adapter"

    def run_inputs(self, **inputs):
        return run({"scenario": SCENARIO_ID, **inputs})

    def test_decisions_and_outcomes_follow_the_existing_engine(self):
        for keep_value, price, buyer, action, sale_status in (
            (250, 220, True, KEEP, "kept"),
            (250, 220, False, KEEP, "kept"),
            (250, 280, True, SELL, "sold"),
            (250, 280, False, SELL, "sale_failed"),
            (250, 250, True, SELL, "sold"),
            (250, 250, False, SELL, "sale_failed"),
            (300, 280, True, KEEP, "kept"),
            (200, 220, True, SELL, "sold"),
            (0, 0, True, SELL, "sold"),
            (250.25, 280.75, True, SELL, "sold"),
        ):
            inputs = dict(keep_value=keep_value, expected_sale_price=price, buyer_available=buyer)
            with self.subTest(inputs=inputs):
                result = self.run_inputs(**inputs)
                direct = run_scenario(build_scenario({"scenario": SCENARIO_ID, **inputs})).agent(STUDENT.name)
                self.assertEqual(result["inputs"], inputs)
                self.assertEqual(result["selected_action"], action)
                self.assertEqual(result["selected_action"], direct.selected_action)
                self.assertEqual(result["action_values"], {KEEP: keep_value, SELL: price})
                self.assertEqual(result["values_equal"], keep_value == price)
                self.assertEqual(result["outcome"], dict(direct.outcome))
                self.assertEqual(result["outcome"], {
                    "status": sale_status,
                    "owns_card": sale_status != "sold",
                    "cash_received": price if sale_status == "sold" else 0,
                })

    def test_actual_buyer_availability_never_changes_agent_inputs_or_choice(self):
        for buyer in (True, False):
            scenario = build_scenario({"scenario": SCENARIO_ID, "buyer_available": buyer})
            self.assertEqual(scenario.agents[0], STUDENT)
            self.assertEqual(scenario.initial_state["buyer_exists"], buyer)
            self.assertEqual(self.run_inputs(buyer_available=buyer)["selected_action"], SELL)

    def test_keep_value_changes_only_valuation(self):
        scenario = build_scenario({"scenario": SCENARIO_ID, "keep_value": 300})
        agent = scenario.agents[0]
        self.assertEqual(agent.valuation["benefits"][KEEP], 300)
        for field in ("model_of_reality", "objective", "perceived_feasible_set", "horizon", "decision_process", "decision_parameters", "valuation_rule"):
            self.assertEqual(getattr(agent, field), getattr(STUDENT, field))
        self.assertEqual(scenario.initial_state, SCENARIO.initial_state)
        self.assertEqual(scenario.parameters, SCENARIO.parameters)

    def test_defaults_and_execution_provenance_are_json_safe(self):
        result = self.run_inputs()
        self.assertEqual(result["inputs"], {"keep_value": 250, "expected_sale_price": 280, "buyer_available": True})
        self.assertEqual(result["ter_version"], __version__)
        self.assertEqual(result["scenario_revision"], 1)
        self.assertEqual(json.loads(json.dumps(result, allow_nan=False)), result)

    def test_invalid_inputs_are_rejected(self):
        for key in ("keep_value", "expected_sale_price"):
            for invalid in (True, False, None, "250", [], {}, -1, float("inf"), float("-inf"), float("nan"), 10**400):
                with self.subTest(key=key, value=invalid):
                    with self.assertRaises((TypeError, ValueError)):
                        self.run_inputs(**{key: invalid})
        for invalid in (0, 1, "yes", None, [], {}):
            with self.subTest(buyer=invalid):
                with self.assertRaisesRegex(TypeError, "boolean"):
                    self.run_inputs(buyer_available=invalid)
        for request in (None, [], {}, {"scenario": "wrong"}, {"scenario": SCENARIO_ID, "fee": 10}):
            with self.subTest(request=request):
                with self.assertRaises((TypeError, ValueError)):
                    run(request)

    def test_runs_do_not_mutate_the_reusable_scenario(self):
        before = copy.deepcopy(SCENARIO)
        baseline = self.run_inputs()
        self.run_inputs(keep_value=1, expected_sale_price=2, buyer_available=False)
        self.run_inputs(keep_value=900, expected_sale_price=0)
        self.assertEqual(SCENARIO, before)
        self.assertEqual(self.run_inputs(), baseline)

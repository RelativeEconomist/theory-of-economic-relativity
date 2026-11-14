"""Protect lottery choices, the odds boundary, price sweep, validation, and provenance."""

import copy
import json
import unittest

from research.adapters.lottery_tickets import PRICE_SWEEP, SCENARIO_ID, run
from research.scenarios.lottery_tickets import (
    ACTUAL_WIN_PROBABILITY, BASELINE, BUY, CONDITIONS, SPECIFICATIONS,
    comparison_table, lottery_scenario,
)
from research.ter import __version__, run_scenario


def odds(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


class TestLotteryTicketsAdapter(unittest.TestCase):
    TEST_NAME = "Framework: Lottery Tickets Adapter"

    def run_inputs(self, **inputs):
        return run({"scenario": SCENARIO_ID, **inputs})

    def test_simulator_conditions_match_the_verified_comparison_table(self):
        table = {row["condition"]: row for row in comparison_table()}
        for label, changes in CONDITIONS:
            if "available_funds" in changes:
                continue  # Funds are fixed in the simulator.
            with self.subTest(condition=label):
                result = self.run_inputs(**changes)
                row = table[label]
                choices = {spec["id"]: spec["selected_action"] for spec in result["specifications"]}
                returns = {spec["id"]: spec["expected_net_return"] for spec in result["specifications"]}
                self.assertEqual(choices, row["choices"])
                self.assertEqual(returns, row["expected_net_returns"])
                self.assertEqual(
                    result["hypothetical_ticket_expected_net_return"],
                    row["hypothetical_ticket_expected_net_return"],
                )

    def test_disclosure_changes_believed_odds_never_actual_odds(self):
        for disclosed in (False, True):
            result = self.run_inputs(odds_disclosed=disclosed)
            self.assertEqual(result["actual_win_probability"], odds(ACTUAL_WIN_PROBABILITY))
            for spec, report in zip(SPECIFICATIONS, result["specifications"]):
                with self.subTest(disclosed=disclosed, specification=spec.name):
                    believed = (
                        ACTUAL_WIN_PROBABILITY if disclosed
                        else spec.model_of_reality["believed_win_probability"]
                    )
                    self.assertEqual(report["believed_win_probability"], odds(believed))

    def test_price_sweep_reports_the_engine_choice_at_every_price(self):
        changes = {"jackpot": 2_000_000, "odds_disclosed": True}
        result = self.run_inputs(**changes)
        self.assertEqual(result["price_sweep"]["prices"], list(PRICE_SWEEP))
        for spec in SPECIFICATIONS:
            expected = [
                run_scenario(lottery_scenario(spec, **changes, ticket_price=price))
                .agent(spec.name).selected_action
                for price in PRICE_SWEEP
            ]
            self.assertEqual(result["price_sweep"]["choices"][spec.name], expected)

    def test_reports_follow_the_engine_values_and_rules(self):
        mistaken, entertainment, habit = self.run_inputs(ticket_price=24.5)["specifications"]
        self.assertEqual(mistaken["action_values"], {"buy": 15.5, "skip": 0})
        self.assertEqual(entertainment["action_values"], {"buy": 0.5, "skip": 0})
        self.assertIsNone(habit["action_values"])
        self.assertEqual(habit["maximum_price"], 30)
        self.assertEqual({s["selected_action"] for s in (mistaken, entertainment, habit)}, {BUY})

        above_funds = self.run_inputs(ticket_price=BASELINE["available_funds"] + 1)
        for report in above_funds["specifications"]:
            self.assertEqual(report["perceived_feasible_set"], ["skip"])
            self.assertEqual(report["expected_net_return"], 0)
            self.assertEqual(report["outcomes"], [{
                "probability": {"numerator": 1, "denominator": 1},
                "status": "skipped", "spent": 0, "prize": 0, "net_return": 0,
            }])

    def test_defaults_reset_to_baseline_and_are_json_safe(self):
        result = self.run_inputs()
        self.assertEqual(result["inputs"], result["baseline"])
        self.assertEqual(result["inputs"], {
            "ticket_price": 20, "jackpot": 10_000_000, "odds_disclosed": False,
        })
        self.assertEqual(result["available_funds"], 50)
        self.assertEqual(result["ter_version"], __version__)
        self.assertEqual(result["scenario_revision"], 1)
        self.assertEqual(json.loads(json.dumps(result, allow_nan=False)), result)

    def test_invalid_inputs_are_rejected(self):
        for key, invalid_values in (
            ("ticket_price", (True, None, "20", [], 0, -1, 1_001, float("nan"), float("inf"))),
            ("jackpot", (False, None, "1", {}, -1, 1_000_000_001, float("inf"))),
            ("odds_disclosed", (0, 1, "yes", None)),
        ):
            for invalid in invalid_values:
                with self.subTest(key=key, value=invalid):
                    with self.assertRaises((TypeError, ValueError)):
                        self.run_inputs(**{key: invalid})
        for request in (None, [], {}, {"scenario": "wrong"}, {"scenario": SCENARIO_ID, "available_funds": 5}):
            with self.subTest(request=request):
                with self.assertRaises((TypeError, ValueError)):
                    run(request)

    def test_runs_do_not_mutate_the_reusable_specifications(self):
        before = copy.deepcopy(SPECIFICATIONS)
        baseline = self.run_inputs()
        self.run_inputs(ticket_price=45, jackpot=0, odds_disclosed=True)
        self.assertEqual(SPECIFICATIONS, before)
        self.assertEqual(self.run_inputs(), baseline)


if __name__ == "__main__":
    unittest.main()

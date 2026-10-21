"""
Framework test: Asymmetric Information adapter.

Purpose
-------
This is not an economic replication test. It verifies that the JSON-safe
adapter runs the reusable Asymmetric Information scenarios through
run_scenario, changes only the price each seller observes, reports seller
beliefs (M) separately from the actual quality R reads, and reports the
one system outcome O_t from the joint R without inventing seller-level
outcomes.
"""

import json
import unittest

from research.adapters.asymmetric_information import SCENARIO_ID, build_scenario, run
from research.scenarios.asymmetric_information import (
    ACTUAL_QUALITY_BY_SELLER,
    ASYMMETRIC_INFORMATION_SCENARIO,
    BELIEVED_SHARE_HIGH,
    HIGH,
    HIGH_QUALITY_SELLER_COUNT,
    HOLD,
    LOW,
    LOW_QUALITY_SELLER_COUNT,
    POOLED_PRICE,
    SELL,
    SELLERS,
    SYMMETRIC_INFORMATION_SCENARIO,
    VALUE_IF_HIGH,
    VALUE_IF_LOW,
)
from research.ter import run_scenario
from research.ter.rules import quality_market_reality


def direct_result(scenario):
    result = run_scenario(scenario)

    return (
        {seller.name: result.agent(seller.name).selected_action for seller in scenario.agents},
        result.trace[-1].reality.system,
    )


class TestAsymmetricInformationAdapter(unittest.TestCase):
    TEST_NAME = "Framework: Asymmetric Information Adapter"

    def assert_matches_direct_run(self, request, scenario):
        result = run({"scenario": SCENARIO_ID, **request})
        actions, system_outcome = direct_result(scenario)

        self.assertEqual(
            {seller["name"]: seller["selected_action"] for seller in result["sellers"]},
            actions,
        )
        self.assertEqual(result["system_outcome"], system_outcome)

        return result

    def test_pooled_pricing_reproduces_adverse_selection(self):
        for request in ({}, {"pricing": "pooled"}):
            with self.subTest(request=request):
                result = self.assert_matches_direct_run(
                    request, ASYMMETRIC_INFORMATION_SCENARIO
                )

                self.assertEqual(result["pricing"], "pooled")
                self.assertEqual(result["believed_share_high"], BELIEVED_SHARE_HIGH)
                self.assertEqual(
                    result["system_outcome"],
                    {
                        "sold_high": 0,
                        "sold_low": LOW_QUALITY_SELLER_COUNT,
                        "total_sold": LOW_QUALITY_SELLER_COUNT,
                    },
                )

                for seller in result["sellers"]:
                    self.assertEqual(seller["observed_price"], POOLED_PRICE)
                    self.assertEqual(
                        seller["selected_action"],
                        HOLD if seller["actual_quality"] == HIGH else SELL,
                    )

    def test_verified_pricing_restores_full_participation(self):
        result = self.assert_matches_direct_run(
            {"pricing": "verified"}, SYMMETRIC_INFORMATION_SCENARIO
        )

        self.assertEqual(result["pricing"], "verified")
        self.assertNotIn("believed_share_high", result)
        self.assertEqual(
            result["system_outcome"]["total_sold"],
            HIGH_QUALITY_SELLER_COUNT + LOW_QUALITY_SELLER_COUNT,
        )

        for seller in result["sellers"]:
            self.assertEqual(
                seller["observed_price"],
                VALUE_IF_HIGH if seller["actual_quality"] == HIGH else VALUE_IF_LOW,
            )
            self.assertEqual(seller["selected_action"], SELL)

    def test_believed_share_changes_only_the_observed_pooled_price(self):
        share = 0.75
        expected_price = share * VALUE_IF_HIGH + (1 - share) * VALUE_IF_LOW
        scenario = build_scenario(
            {"scenario": SCENARIO_ID, "believed_share_high": share}
        )

        for seller, default in zip(scenario.agents, ASYMMETRIC_INFORMATION_SCENARIO.agents):
            with self.subTest(seller=seller.name):
                self.assertEqual(seller.model_of_reality["price"], expected_price)
                self.assertEqual(
                    seller.model_of_reality["known_quality"],
                    default.model_of_reality["known_quality"],
                )

                for component in (
                    "name",
                    "objective",
                    "perceived_feasible_set",
                    "valuation",
                    "valuation_rule",
                    "decision_process",
                    "horizon",
                ):
                    self.assertEqual(getattr(seller, component), getattr(default, component))

        self.assertEqual(
            scenario.parameters["actual_quality_by_seller"], ACTUAL_QUALITY_BY_SELLER
        )

        # A price of 8.5 clears the high-quality reservation value of 8.
        result = self.assert_matches_direct_run({"believed_share_high": share}, scenario)
        self.assertEqual(result["believed_share_high"], share)
        self.assertEqual(result["system_outcome"]["sold_high"], HIGH_QUALITY_SELLER_COUNT)

    def test_seller_beliefs_are_reported_apart_from_actual_quality(self):
        result = run({"scenario": SCENARIO_ID})

        for seller, spec in zip(result["sellers"], SELLERS):
            with self.subTest(seller=spec.name):
                self.assertEqual(seller["name"], spec.name)
                self.assertEqual(seller["actual_quality"], ACTUAL_QUALITY_BY_SELLER[spec.name])
                self.assertEqual(seller["known_quality"], spec.model_of_reality["known_quality"])
                self.assertEqual(seller["reservation_value"], spec.valuation["costs"][SELL])
                self.assertEqual(
                    seller["action_values"],
                    {SELL: POOLED_PRICE - spec.valuation["costs"][SELL], HOLD: 0},
                )

    def test_system_outcome_follows_actual_quality_not_seller_beliefs(self):
        # Every seller believes the opposite of its car's actual quality.
        opposite = {HIGH: LOW, LOW: HIGH}
        mistaken = ASYMMETRIC_INFORMATION_SCENARIO.variant(
            agents=[
                seller.variant(
                    model_of_reality={
                        "known_quality": opposite[seller.model_of_reality["known_quality"]],
                    },
                )
                for seller in SELLERS
            ],
        )

        self.assertEqual(
            direct_result(mistaken), direct_result(ASYMMETRIC_INFORMATION_SCENARIO)
        )

    def test_system_outcome_comes_from_one_joint_reality_function(self):
        result = run({"scenario": SCENARIO_ID})
        actions = {seller["name"]: seller["selected_action"] for seller in result["sellers"]}
        recorded = run_scenario(ASYMMETRIC_INFORMATION_SCENARIO)

        # O_t is R applied to every seller's action together, not a sum of
        # seller-level outcomes, which this scenario does not define.
        self.assertEqual(
            result["system_outcome"],
            quality_market_reality(actions, {}, ASYMMETRIC_INFORMATION_SCENARIO.parameters).system,
        )
        self.assertEqual(recorded.trace[-1].reality.agents, {})

        for seller in result["sellers"]:
            self.assertEqual(
                set(seller),
                {
                    "name",
                    "actual_quality",
                    "known_quality",
                    "observed_price",
                    "reservation_value",
                    "action_values",
                    "selected_action",
                },
            )

        # Changing one seller's action changes the joint O_t.
        first_high_seller = SELLERS[0].name
        counterfactual = recorded.counterfactual(0, {first_high_seller: SELL})
        self.assertEqual(counterfactual.system["sold_high"], 1)
        self.assertEqual(counterfactual.system["total_sold"], LOW_QUALITY_SELLER_COUNT + 1)

    def test_input_and_output_are_json_safe(self):
        for request in (
            {"scenario": SCENARIO_ID},
            {"scenario": SCENARIO_ID, "pricing": "verified"},
            {"scenario": SCENARIO_ID, "pricing": "pooled", "believed_share_high": 0.67},
            {"scenario": SCENARIO_ID, "believed_share_high": 1},
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
        cases = [
            (TypeError, "dict", [SCENARIO_ID]),
            (ValueError, "Unknown", {"actual_quality_by_seller": {}}),
            (ValueError, "Unknown", {"known_quality": HIGH}),
            (ValueError, "pricing", {"pricing": "symmetric"}),
            (ValueError, "pricing", {"pricing": None}),
            (ValueError, "pricing", {"pricing": ["pooled"]}),
            (ValueError, "pooled", {"pricing": "verified", "believed_share_high": 0.5}),
            (TypeError, "number", {"believed_share_high": "0.5"}),
            (TypeError, "number", {"believed_share_high": True}),
            (TypeError, "number", {"believed_share_high": None}),
            (ValueError, "finite", {"believed_share_high": float("nan")}),
            (ValueError, "finite", {"believed_share_high": float("inf")}),
            (ValueError, "from 0 to 1", {"believed_share_high": -0.1}),
            (ValueError, "from 0 to 1", {"believed_share_high": 1.01}),
            (ValueError, "from 0 to 1", {"believed_share_high": 10**400}),
        ]

        for error, message, request in cases:
            if isinstance(request, dict):
                request = {"scenario": SCENARIO_ID, **request}

            with self.subTest(request=request):
                with self.assertRaisesRegex(error, message):
                    run(request)

    def test_runs_do_not_change_the_reusable_scenario(self):
        run({"scenario": SCENARIO_ID, "believed_share_high": 0.9})

        self.assertEqual(
            ASYMMETRIC_INFORMATION_SCENARIO.parameters["believed_share_high"],
            BELIEVED_SHARE_HIGH,
        )

        for seller in ASYMMETRIC_INFORMATION_SCENARIO.agents:
            self.assertEqual(seller.model_of_reality["price"], POOLED_PRICE)


if __name__ == "__main__":
    unittest.main()

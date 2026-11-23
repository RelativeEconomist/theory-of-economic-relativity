import json
import unittest
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from research.experiments.bank_run_identification import compare
from research.experiments.bank_run_identification.economy import CAPACITIES, ChoiceInformation
from research.experiments.bank_run_identification.evaluation import advantage_result, lock_forecasts
from research.experiments.bank_run_identification.fixtures import exact_rows, generate, json_line
from research.experiments.bank_run_identification.verification import read_bank, replay, verify_exact, verify_ledger


class TestBankRunIdentification(unittest.TestCase):
    TEST_NAME = "Bank run identification experiment"

    def test_three_mappings_reconcile_every_exact_history(self):
        rows = (json.loads(json_line(row)) for row in exact_rows())
        verified = verify_exact(rows, compare.MODELS.values())
        self.assertEqual(verified["cases"], 648)
        self.assertEqual(verified["binding_effect"], Fraction(4, 5))
        self.assertEqual(verified["nonbinding_effect"], 0)
        self.assertTrue(verified["payout_collision"])
        self.assertEqual(verified["maximum_treasury_payout"], Fraction(6, 5))

    def test_delayed_notice_and_queue_stay_outside_choice(self):
        forecasts = lock_forecasts(compare.MODELS)
        mixed = Fraction(27, 35)
        for name, model in compare.MODELS.items():
            information = ChoiceInformation(0, None)
            self.assertEqual(model.select(information, (mixed, mixed), (0, mixed)), tuple("EEW"))
            self.assertEqual(
                {forecasts[name, capacity, "delayed", 0][0] for capacity in CAPACITIES},
                {(Fraction(62, 105), Fraction(62, 105))},
            )
        trace = self.delayed_trace()
        trace["lock"]["information"]["disclosed_capacity"] = trace["assignment"]["capacity"]
        with self.assertRaisesRegex(ValueError, "leaked pre-choice"):
            read_bank(trace)
        trace = self.delayed_trace()
        trace["service_order"]["event"] = 1
        with self.assertRaisesRegex(ValueError, "timing"):
            read_bank(trace)

    def test_priority_and_claim_conservation_are_independently_checked(self):
        bank = read_bank(self.delayed_trace(tenders="EEE"))
        swapped = tuple(reversed(bank.ledger.bank_early))
        with self.assertRaisesRegex(ValueError, "Sequential-service"):
            verify_ledger(bank, replace(bank.ledger, bank_early=swapped))
        with self.assertRaisesRegex(ValueError, "Late claim"):
            verify_ledger(bank, replace(bank.ledger, bank_late=(Fraction(1), Fraction(0), Fraction(0))))
        with self.assertRaisesRegex(ValueError, "Principal"):
            verify_ledger(bank, replace(bank.ledger, invested_after_service=Fraction(3)))
        with self.assertRaisesRegex(ValueError, "Late reserve"):
            verify_ledger(bank, replace(bank.ledger, treasury_returned=Fraction(1)))

    def test_replay_requires_the_factual_ledger_and_reuses_the_full_order(self):
        bank = read_bank(self.delayed_trace())
        self.assertEqual(bank.state.order, (2, 0, 1))
        for model in compare.MODELS.values():
            alternative = replay(model, bank, tuple("EWE"))
            self.assertEqual(alternative.bank_early, (Fraction(4, 5), 0, Fraction(7, 5)))
            corrupted = replace(bank, ledger=replace(bank.ledger, residual=Fraction(1)))
            with self.assertRaisesRegex(ValueError, "Factual replay"):
                replay(model, corrupted, tuple("EWE"))

    def test_frozen_forecast_threshold_requires_an_advantage_over_both(self):
        self.assertEqual(advantage_result([(0.02, 0.04), (0.03, 0.04)]), "pass")
        self.assertEqual(advantage_result([(0.02, 0.04), (0, 0.01)]), "fail")
        self.assertEqual(advantage_result([(0.02, 0.04), (0.005, 0.02)]), "inconclusive")

    def test_seeded_experiment_locks_forecasts_before_reading_labels(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            evidence, output = root / "evidence", root / "output"
            manifest = generate(evidence)
            self.assertEqual(manifest, generate(root / "repeat"))
            read = compare.read_rows

            def check_lock(directory, recorded_manifest, name):
                if name in ("calibration.jsonl", "holdout.jsonl"):
                    self.assertTrue((output / "predictions.json").is_file())
                return read(directory, recorded_manifest, name)

            with patch.object(compare, "read_rows", side_effect=check_lock):
                results = compare.run(evidence, output)
            self.assertTrue((output / "results.json").is_file())
            self.assertEqual(results["evidence"], "synthetic")
            self.assertEqual(results["reviewer_advantage"]["status"], "inconclusive")
            for world, result in results["worlds"].items():
                self.assertEqual(result["prediction"]["primary_advantage"], "fail")
                primary = result["prediction"]["scores"]["request_14/5"]
                self.assertEqual(primary["banks"], 240)
                self.assertEqual(len(set(primary["brier"].values())), 1)
                if world != "equilibrium_mixture":
                    self.assertEqual(result["identification"]["realization"]["status"], "inconclusive")
                    rivals = result["identification"]["selection_rivals"]
                    self.assertEqual(len(rivals["compatible_delayed_baseline"]), 2)
                    self.assertEqual(rivals["compatible_crossed_arms"], [world])

    @staticmethod
    def delayed_trace(tenders="EWW"):
        for row in exact_rows():
            trace = row["trace"]
            assigned = trace["assignment"]
            if (assigned["timing"] == "delayed" and assigned["capacity"] == CAPACITIES[0]
                and trace["lock"]["tenders"] == tenders and assigned["impatient"] == 0
                and trace["service_order"]["permutation"] == (2, 0, 1)):
                return json.loads(json_line(trace))
        raise AssertionError("Missing isolation probe")

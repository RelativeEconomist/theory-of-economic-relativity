"""Check parity, lock forecasts, then score the sealed fixture files."""

import argparse
import hashlib
import json
import platform
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

from . import conventional, state_transition, ter_model
from .economy import CAPACITIES, HEALTHY
from .evaluation import BOOTSTRAPS, identification, lock_forecasts, score_predictions
from .verification import read_bank, require, verify_exact, verify_ledger


MODELS = {"TER": ter_model, "Architecture B": state_transition, "Conventional": conventional}


def read_rows(directory, manifest, name):
    source = (directory / name).read_bytes()
    expected = manifest["files"][name]
    require(hashlib.sha256(source).hexdigest() == expected["sha256"], f"Unexpected evidence hash: {name}")
    rows = source.splitlines()
    require(len(rows) == expected["rows"], f"Unexpected record count: {name}")
    return map(json.loads, rows)


def verify_randomized(split_rows, manifest):
    blocks = defaultdict(dict)
    holdouts = defaultdict(list)
    seen_banks = set()
    for split, rows in split_rows.items():
        for row in rows:
            name, world, block = row["bank"], row["world"], row["block"]
            require(name not in seen_banks, f"Duplicate randomized bank {name}")
            seen_banks.add(name)
            try:
                require(world in manifest["worlds"] and 0 <= block < manifest["blocks_per_world"], "Unknown world or block")
                bank = read_bank(row["trace"])
                require(bank.state.terms == HEALTHY, "Randomization uses the uninsured contract")
                verify_ledger(bank, bank.ledger)
                capacity, timing = bank.state.capacity, row["trace"]["assignment"]["timing"]
                reserved = capacity == CAPACITIES[1] or block % 4 == 0
                require(row["split"] == split and reserved == (split == "holdout"), "Bank violates holdout assignment")
                require((capacity, timing) not in blocks[world, block], "Duplicate treatment cell within block")
                blocks[world, block][capacity, timing] = bank
                if split == "holdout":
                    holdouts[world].append((timing, bank))

                generated = row["synthetic_policy"]
                probability = Fraction(generated["equilibrium_probability"])
                draws = tuple(map(Fraction, generated["draws"]))
                require(len(draws) == 2 and all(0 <= draw < 1 for draw in draws), "Invalid private policy draws")
                strategy = (probability, probability)
                for label, model in MODELS.items():
                    require(strategy in model.equilibria(bank.information), f"{label} rejects the recorded equilibrium")
                    require(model.select(bank.information, strategy, draws) == bank.actions, f"{label} changes recorded tenders")
                    require(model.settle(bank.actions, bank.state) == bank.ledger, f"{label} changes the recorded ledger")
            except ValueError as exc:
                raise ValueError(f"{name}: {exc}") from exc

    cells = set(product(CAPACITIES, ("early", "delayed")))
    ordered = {}
    for world in manifest["worlds"]:
        ordered[world] = [blocks[world, block] for block in range(manifest["blocks_per_world"])]
        require(all(bank_group.keys() == cells for bank_group in ordered[world]), f"Unbalanced assignments in {world}")
    return ordered, holdouts


def write_json(path, value):
    path.write_text(json.dumps(value, default=str, indent=2) + "\n", encoding="utf-8")


def run(fixtures, output):
    manifest = json.loads((fixtures / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["source_sha256"].items():
        path = Path(__file__).with_name(name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"Fixture source changed: {name}")
    exact = verify_exact(read_rows(fixtures, manifest, "exact.jsonl"), MODELS.values())

    forecasts = lock_forecasts(MODELS)
    output.mkdir(parents=True, exist_ok=True)
    prediction_file = output / "predictions.json"
    write_json(prediction_file, [
        {"model": model, "capacity": capacity, "timing": timing, "impatient": role,
         "patient_request": forecast[0], "all_early_paid": forecast[1]}
        for (model, capacity, timing, role), forecast in forecasts.items()
    ])
    locked_hash = hashlib.sha256(prediction_file.read_bytes()).hexdigest()

    # These files contain outcomes. Read them after all forecasts are archived.
    split_rows = {split: read_rows(fixtures, manifest, f"{split}.jsonl") for split in ("calibration", "holdout")}
    blocks, holdouts = verify_randomized(split_rows, manifest)
    resampling_seed = manifest["seeds"]["resampling"]
    results = {
        "python": platform.python_version(),
        "evidence": "synthetic", "fixture_manifest": manifest,
        "predictions_sha256": locked_hash, "bootstrap_replicates": BOOTSTRAPS,
        "exact_verification": exact,
        "worlds": {
            name: {
                "identification": identification(world_blocks, resampling_seed),
                "prediction": score_predictions(holdouts[name], forecasts, MODELS, resampling_seed),
            }
            for name, world_blocks in blocks.items()
        },
        "reviewer_advantage": {"status": "inconclusive", "reason": "Independent reviewer data were not collected."},
    }
    write_json(output / "results.json", results)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        results = run(args.fixtures, args.output)
    except ValueError as error:
        parser.exit(1, f"Verification failed: {error}\n")
    print(f"Exact replay and equilibrium parity passed in {results['exact_verification']['cases']} cases.")
    for world, values in results["worlds"].items():
        print(f"{world}: TER prediction advantage {values['prediction']['primary_advantage']}; "
              f"delayed realization {values['identification']['realization']['status']}.")
    print(f"Wrote {args.output / 'predictions.json'} and {args.output / 'results.json'}.")

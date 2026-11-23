"""Generate evidence with a ledger oracle that imports no model code."""

import argparse
import hashlib
import json
from dataclasses import asdict
from fractions import Fraction
from itertools import product
from pathlib import Path
from random import Random

from .economy import (
    CAPACITIES, DEPOSITORS, GUARANTEE, HEALTHY, HISTORICAL, LATE_FLOOR,
    ORDERS, PRINCIPAL, PROFILES, PROMISE, Ledger, tenders,
)


BLOCKS = 120
SEEDS = {"assignment": 260112, "policy": 260113, "service": 260114, "resampling": 260115}
WORLDS = ("all_wait", "disclosure_responsive", "equilibrium_mixture")
CELLS = tuple(product(CAPACITIES, ("early", "delayed")))
SOURCE = Path(__file__).resolve().parent


def oracle(actions, capacity, order, terms):
    """Allocate numbered hundredths to the tenders in service order."""
    cap = int(100 * capacity)
    claim = int(100 * PROMISE)
    early_queue = [depositor for depositor in order if actions[depositor] == "E"]
    funded = set(range(cap))
    paid = {}
    for rank, depositor in enumerate(early_queue):
        slots = range(rank * claim, (rank + 1) * claim)
        paid[depositor] = Fraction(len(funded.intersection(slots)), 100)

    bank_early = tuple(paid.get(depositor, Fraction(0)) for depositor in DEPOSITORS)
    invested = PRINCIPAL - sum(paid.values())
    pool = terms.maturity_rate * invested
    waiting = actions.count("W")
    bank_late = tuple(pool / waiting if action == "W" else Fraction(0) for action in actions)
    topups_early = tuple(
        PROMISE - paid[depositor] if terms.treasury and depositor in paid else Fraction(0)
        for depositor in DEPOSITORS
    )
    topups_late = tuple(
        max(Fraction(0), LATE_FLOOR - bank_late[depositor])
        if terms.treasury and action == "W" else Fraction(0)
        for depositor, action in enumerate(actions)
    )
    available_treasury = terms.treasury - sum(topups_early)
    return Ledger(
        bank_early, bank_late, topups_early, topups_late, pool if not waiting else Fraction(0),
        invested, capacity - sum(bank_early), available_treasury,
        available_treasury - sum(topups_late),
    )


def event_record(capacity, timing, impatient, terms, actions, order, ledger):
    view = {
        "impatient": impatient,
        "disclosed_capacity": capacity if timing == "early" else None,
        "capacity_lottery": CAPACITIES,
        "terms": asdict(terms),
        "patient_menu": "WE",
        "disclosure_schedule": timing,
    }
    return {
        "assignment": {
            "event": 0, "impatient": impatient, "capacity": capacity, "timing": timing,
            "invested": PRINCIPAL, "treasury": terms.treasury,
        },
        "notice": {"event": 1 if timing == "early" else 3, "capacity": capacity},
        "lock": {"event": 2, "information": view, "tenders": "".join(actions)},
        "service_order": {"event": 4, "permutation": order},
        "early_service": {
            "event": 5,
            "bank_payments": ledger.bank_early,
            "topups": ledger.topups_early,
            "next_state": {
                "invested": ledger.invested_after_service,
                "unused_limit": ledger.limit_after_service,
                "treasury": ledger.treasury_after_service,
                "waiting_claimants": [i for i, action in enumerate(actions) if action == "W"],
            },
            "own_receipt_observations": [
                {"bank": bank_paid, "topup": topup}
                for bank_paid, topup in zip(ledger.bank_early, ledger.topups_early, strict=True)
            ],
        },
        "maturity": {
            "event": 6,
            "bank_payments": ledger.bank_late,
            "topups": ledger.topups_late,
            "residual": ledger.residual,
            "treasury_returned": ledger.treasury_returned,
            "own_receipt_observations": [
                {"bank": bank_paid, "topup": topup}
                for bank_paid, topup in zip(ledger.bank_late, ledger.topups_late, strict=True)
            ],
        },
    }


def choice_fixture(world, notice, rng):
    if world == "all_wait" or notice == CAPACITIES[0]:
        probability = Fraction(0)
    elif world == "disclosure_responsive":
        probability = Fraction(int(notice is not None))
    else:
        mixed = {None: Fraction(27, 35), CAPACITIES[1]: Fraction(3, 11), CAPACITIES[2]: Fraction(1, 4)}
        probability = rng.choice((Fraction(0), mixed[notice], Fraction(1)))

    draws = tuple(Fraction(rng.randrange(probability.denominator), probability.denominator) for _ in range(2))
    profile = tuple("E" if draw < probability else "W" for draw in draws)
    return profile, {"equilibrium_probability": probability, "draws": draws}


def randomized_rows():
    for world in WORLDS:
        assignment, policy, service = (Random(SEEDS[key]) for key in ("assignment", "policy", "service"))
        for block in range(BLOCKS):
            cells = assignment.sample(CELLS, len(CELLS))
            for slot, (capacity, timing) in enumerate(cells):
                impatient = assignment.choice(DEPOSITORS)
                profile, policy_record = choice_fixture(world, capacity if timing == "early" else None, policy)
                actions = tenders(impatient, profile)
                order = service.choice(ORDERS)
                ledger = oracle(actions, capacity, order, HEALTHY)
                yield {
                    "bank": f"{world}-{block:03d}-{slot}", "world": world, "block": block,
                    "split": "holdout" if capacity == CAPACITIES[1] or block % 4 == 0 else "calibration",
                    "synthetic_policy": policy_record,
                    "trace": event_record(capacity, timing, impatient, HEALTHY, actions, order, ledger),
                }


def exact_rows():
    conditions = [("randomized", capacity, timing, HEALTHY) for capacity, timing in CELLS]
    conditions += [(label, PRINCIPAL, "early", terms) for label, terms in HISTORICAL.items()]
    for label, capacity, timing, terms in conditions:
        for impatient, profile, order in product(DEPOSITORS, PROFILES, ORDERS):
            actions = tenders(impatient, profile)
            ledger = oracle(actions, capacity, order, terms)
            yield {"case": label, "trace": event_record(capacity, timing, impatient, terms, actions, order, ledger)}


def json_line(value):
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":")) + "\n"


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    rows = list(randomized_rows())
    records = {
        "exact.jsonl": list(exact_rows()),
        "calibration.jsonl": [row for row in rows if row["split"] == "calibration"],
        "holdout.jsonl": [row for row in rows if row["split"] == "holdout"],
    }
    manifest = {
        "provenance": "Synthetic numbered-slot ledger and protocol-defined equilibrium selections",
        "split": "All k=14/5 and every fourth complete block are held out",
        "blocks_per_world": BLOCKS, "seeds": SEEDS, "worlds": WORLDS,
        "source_sha256": {
            name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
            for name in ("protocol.md", "economy.py", "fixtures.py")
        },
        "files": {},
    }
    for name, cases in records.items():
        contents = "".join(map(json_line, cases)).encode("utf-8")
        (directory / name).write_bytes(contents)
        manifest["files"][name] = {"rows": len(cases), "sha256": hashlib.sha256(contents).hexdigest()}

    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(generate(parser.parse_args().output), indent=2))

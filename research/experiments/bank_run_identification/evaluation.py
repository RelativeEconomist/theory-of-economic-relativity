"""Exact forecast laws and bank-level synthetic evaluation."""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import ceil, floor
from random import Random

from .economy import (
    CAPACITIES, DEPOSITORS, ORDERS, PROFILES, ZERO, ChoiceInformation,
    SettlementState, shortfall, tenders,
)
from .verification import require


BOOTSTRAPS = 4096


def outcome_law(model, information, capacity):
    equilibria = model.equilibria(information)
    law = defaultdict(Fraction)
    for strategy, profile, order in product(equilibria, PROFILES, ORDERS):
        mass = Fraction(1, len(ORDERS) * len(equilibria))
        for action, probability in zip(profile, strategy, strict=True):
            mass *= probability if action == "E" else 1 - probability
        if mass:
            actions = tenders(information.impatient, profile)
            ledger = model.settle(actions, SettlementState(capacity, order, information.terms))
            law[profile, order, ledger] += mass
    require(sum(law.values()) == 1, "Invalid equilibrium outcome distribution")
    return dict(law)


def lock_forecasts(models):
    forecasts = {}
    for capacity, timing, role in product(CAPACITIES, ("early", "delayed"), DEPOSITORS):
        information = ChoiceInformation(role, capacity if timing == "early" else None)
        laws = {name: outcome_law(model, information, capacity) for name, model in models.items()}
        first = next(iter(laws.values()))
        require(all(law == first for law in laws.values()), f"Unequal joint forecast law at {capacity}, {timing}, role {role}")
        for name, law in laws.items():
            patient = tuple(
                sum((mass for (profile, _, _), mass in law.items() if profile[i] == "E"), ZERO)
                for i in range(2)
            )
            all_paid = sum(
                (mass for (profile, _, ledger), mass in law.items()
                 if shortfall(tenders(role, profile), ledger) == 0),
                ZERO,
            )
            forecasts[name, capacity, timing, role] = (patient, all_paid)
    return forecasts


def simultaneous_intervals(series, seed):
    """Bonferroni percentile intervals with paired resampling within each supplied stratum."""
    sizes = tuple(map(len, next(iter(series.values()))))
    require(sizes and all(sizes), "Missing resampling stratum")
    total = sum(sizes)
    rng = Random(seed)
    result, varying = {}, {}
    for name, strata in series.items():
        require(sizes == tuple(map(len, strata)), "Unequal resampling designs in one interval family")
        point = Fraction(sum(sum(stratum) for stratum in strata), total)
        result[name] = {"estimate": point, "interval": (float(point), float(point))}
        if any(len(set(stratum)) > 1 for stratum in strata):
            varying[name] = (tuple(tuple(map(float, group)) for group in strata), [])

    if varying:
        for _ in range(BOOTSTRAPS):
            indices = [rng.choices(range(size), k=size) for size in sizes]
            for groups, estimates in varying.values():
                estimates.append(sum(sum(values[i] for i in selection) for values, selection in zip(groups, indices)) / total)
        tail = 0.05 / (2 * len(series))
        low, high = floor(tail * (BOOTSTRAPS - 1)), ceil((1 - tail) * (BOOTSTRAPS - 1))
        for name, (_, estimates) in varying.items():
            estimates.sort()
            result[name]["interval"] = (estimates[low], estimates[high])
    return result


def equivalence_result(interval, margin=0.05):
    lower, upper = interval
    if lower > margin or upper < -margin:
        return "outside_margin"
    if lower >= -margin and upper <= margin:
        return "within_margin"
    return "inconclusive"


def advantage_result(intervals):
    if all(lower > 0.01 for lower, _ in intervals):
        return "pass"
    if any(upper <= 0.01 for _, upper in intervals):
        return "fail"
    return "inconclusive"


def rival_compatibility(banks):
    def compatible(responsive, delayed_only=False):
        for (_, timing), bank in banks:
            if delayed_only and timing != "delayed":
                continue
            profile = ("E", "E") if responsive and timing == "early" and bank.state.capacity >= CAPACITIES[1] else ("W", "W")
            if bank.profile != profile:
                return False
        return True

    names = (("all_wait", False), ("disclosure_responsive", True))
    baseline = [name for name, responsive in names if compatible(responsive, delayed_only=True)]
    crossed = [name for name, responsive in names if compatible(responsive)]
    return {
        "compatible_delayed_baseline": baseline,
        "compatible_crossed_arms": crossed,
        "restricted_disclosure_effects": {
            str(capacity): sorted({int(name == "disclosure_responsive" and capacity >= CAPACITIES[1]) for name in crossed})
            for capacity in CAPACITIES
        },
        "status": "separated" if len(crossed) == 1 else "inconclusive" if crossed else "both_rejected",
    }


def identification(blocks, seed):
    def request_share(bank):
        return Fraction(bank.profile.count("E"), 2)

    series = {
        f"disclosure_{cap}": ([
            request_share(block[cap, "early"]) - request_share(block[cap, "delayed"])
            for block in blocks
        ],)
        for cap in CAPACITIES
    }
    profile_contrasts = []
    for low, high in combinations(CAPACITIES, 2):
        for profile in PROFILES:
            name = f"delayed_{low}_minus_{high}_{''.join(profile)}"
            profile_contrasts.append(name)
            series[name] = ([
                int(block[low, "delayed"].profile == profile) - int(block[high, "delayed"].profile == profile)
                for block in blocks
            ],)

    low, _, high = CAPACITIES
    exposed = [
        tuple(shortfall(block[cap, "delayed"].actions, block[cap, "delayed"].ledger) for cap in (low, high))
        for block in blocks
    ]
    series["shortfall_low_minus_high"] = ([low_value - high_value for low_value, high_value in exposed],)
    results = simultaneous_intervals(series, seed)
    disclosure = {str(cap): results[f"disclosure_{cap}"] for cap in CAPACITIES}
    profiles = {name: results[name] for name in profile_contrasts}
    for entry in (*disclosure.values(), *profiles.values()):
        entry["margin_result"] = equivalence_result(entry["interval"])
    profile_results = {entry["margin_result"] for entry in profiles.values()}
    equivalent = "pass" if profile_results == {"within_margin"} else "fail" if "outside_margin" in profile_results else "inconclusive"
    binding_cases = sum(value > 0 for pair in exposed for value in pair)
    realization = results["shortfall_low_minus_high"]
    realization.update(
        binding_cases=binding_cases,
        status=equivalent if binding_cases else "inconclusive",
    )
    return {
        "disclosure": disclosure, "delayed_profile_equivalence": equivalent,
        "delayed_profiles": profiles, "realization": realization,
        "selection_rivals": rival_compatibility([item for block in blocks for item in block.items()]),
    }


def score_predictions(holdout, forecasts, model_names, seed):
    losses = defaultdict(list)
    for timing, bank in holdout:
        target = tuple(int(action == "E") for action in bank.profile)
        paid = int(shortfall(bank.actions, bank.ledger) == 0)
        capacity = bank.state.capacity
        for name in model_names:
            request, settlement = forecasts[name, capacity, timing, bank.information.impatient]
            losses[capacity, timing, name, "request"].append(
                sum((probability - event) ** 2 for probability, event in zip(request, target, strict=True)) / 2
            )
            losses[capacity, timing, name, "all_paid"].append((settlement - paid) ** 2)

    scores = {}
    for capacity, target in product(CAPACITIES, ("request", "all_paid")):
        groups = {
            name: tuple(losses[capacity, timing, name, target] for timing in ("early", "delayed"))
            for name in model_names
        }
        differences = {
            name: tuple([comparison - ter for comparison, ter in zip(others, ours, strict=True)]
                        for others, ours in zip(strata, groups["TER"], strict=True))
            for name, strata in groups.items() if name != "TER"
        }
        comparisons = simultaneous_intervals(differences, seed)
        scores[f"{target}_{capacity}"] = {
            "banks": sum(map(len, groups["TER"])),
            "brier": {name: Fraction(sum(map(sum, strata)), sum(map(len, strata))) for name, strata in groups.items()},
            "comparator_minus_TER": comparisons,
        }
    primary = scores[f"request_{CAPACITIES[1]}"]
    return {
        "scores": scores,
        "primary_advantage": advantage_result([item["interval"] for item in primary["comparator_minus_TER"].values()]),
    }

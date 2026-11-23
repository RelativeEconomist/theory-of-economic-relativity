"""Finite withdrawal game with chance service ranks and a normal-form solution."""

from fractions import Fraction
from functools import cache

from .economy import (
    CAPACITIES, DEPOSITORS, LATE_FLOOR, PRINCIPAL, PROFILES, PROMISE, ZERO, Ledger, tenders,
)


def settle(actions, state):
    queue = tuple(i for i in state.order if actions[i] == "E")
    cumulative = [min(rank * PROMISE, state.capacity, PRINCIPAL) for rank in range(len(queue) + 1)]
    receipts = {i: cumulative[j + 1] - cumulative[j] for j, i in enumerate(queue)}
    unliquidated = PRINCIPAL - cumulative[-1]
    maturity_pool = state.terms.maturity_rate * unliquidated
    late_claims = len(DEPOSITORS) - len(queue)
    early = tuple(receipts.get(i, ZERO) for i in DEPOSITORS)
    late = tuple(maturity_pool / late_claims if action == "W" else ZERO for action in actions)

    topups_early = tuple(PROMISE - early[i] if i in receipts and state.terms.treasury else ZERO for i in DEPOSITORS)
    topups_late = tuple(
        max(ZERO, LATE_FLOOR - late[i]) if i not in receipts and state.terms.treasury else ZERO
        for i in DEPOSITORS
    )
    remaining_reserve = state.terms.treasury - sum(topups_early)
    return Ledger(
        early, late, topups_early, topups_late, maturity_pool if late_claims == 0 else ZERO,
        unliquidated, state.capacity - cumulative[-1], remaining_reserve, remaining_reserve - sum(topups_late),
    )


@cache
def payoffs(information):
    """Collapse the uniform rank chance node before evaluating strategies."""
    notice = information.disclosed_capacity
    capacities = CAPACITIES if notice is None else (notice,)
    result = {}
    for profile in PROFILES:
        n_early = 1 + profile.count("E")
        expected_early, expected_wait = ZERO, ZERO
        for capacity in capacities:
            liquidation = min(n_early * PROMISE, capacity, PRINCIPAL)
            early = liquidation / n_early
            wait = (PRINCIPAL - liquidation) * information.terms.maturity_rate / (3 - n_early) if n_early < 3 else ZERO
            if information.terms.treasury:
                early, wait = PROMISE, max(wait, LATE_FLOOR)
            expected_early += early / len(capacities)
            expected_wait += wait / len(capacities)
        result[profile] = tuple(expected_early if action == "E" else expected_wait for action in profile)
    return result


@cache
def equilibria(information):
    utility = payoffs(information)
    pure = []
    for profile in PROFILES:
        first_deviation = ("E" if profile[0] == "W" else "W", profile[1])
        second_deviation = (profile[0], "E" if profile[1] == "W" else "W")
        if utility[profile][0] >= utility[first_deviation][0] and utility[profile][1] >= utility[second_deviation][1]:
            pure.append(tuple(Fraction(int(action == "E")) for action in profile))

    first_left = utility["W", "W"][0] - utility["E", "W"][0]
    first_right = utility["E", "E"][0] - utility["W", "E"][0]
    second_left = utility["W", "W"][1] - utility["W", "E"][1]
    second_right = utility["E", "E"][1] - utility["E", "W"][1]
    if 0 in (first_left, first_right, second_left, second_right):
        raise ValueError("An endpoint tie permits supports outside this finite benchmark.")
    if first_left * first_right > 0 and second_left * second_right > 0:
        pure.append((second_left / (second_left + second_right), first_left / (first_left + first_right)))
    return tuple(sorted(pure))


def select(information, strategy, draws):
    if strategy not in equilibria(information):
        raise ValueError("The strategy must be a best response on the supplied information set.")
    profile = tuple("W" if draw >= probability else "E" for probability, draw in zip(strategy, draws, strict=True))
    return tenders(information.impatient, profile)

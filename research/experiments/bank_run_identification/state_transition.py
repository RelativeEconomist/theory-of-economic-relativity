"""Architecture B. Information-conditioned policies and state transitions."""

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import cache

from .economy import (
    CAPACITIES, DEPOSITORS, LATE_FLOOR, ORDERS, PRINCIPAL, PROFILES, PROMISE, ZERO,
    Ledger, SettlementState, patients, tenders,
)


@dataclass(frozen=True)
class Accounts:
    invested: Fraction
    limit: Fraction
    treasury: Fraction


def settle(actions, state):
    accounts = Accounts(PRINCIPAL, state.capacity, state.terms.treasury)
    early, late, subsidy_early, subsidy_late = ([ZERO] * len(DEPOSITORS) for _ in range(4))
    waiting = []
    for depositor in state.order:
        if actions[depositor] == "W":
            waiting.append(depositor)
            continue
        # R produces the payment. Q applies it to the objective accounts.
        early[depositor] = min(accounts.invested, accounts.limit, PROMISE)
        if state.terms.treasury:
            subsidy_early[depositor] = PROMISE - early[depositor]
        accounts = Accounts(
            accounts.invested - early[depositor], accounts.limit - early[depositor],
            accounts.treasury - subsidy_early[depositor],
        )

    pool = accounts.invested * state.terms.maturity_rate
    at_maturity = accounts
    for depositor in waiting:
        late[depositor] = pool / len(waiting)
        if state.terms.treasury:
            subsidy_late[depositor] = max(ZERO, LATE_FLOOR - late[depositor])
            at_maturity = replace(at_maturity, treasury=at_maturity.treasury - subsidy_late[depositor])

    return Ledger(
        tuple(early), tuple(late), tuple(subsidy_early), tuple(subsidy_late),
        ZERO if waiting else pool, accounts.invested, accounts.limit, accounts.treasury, at_maturity.treasury,
    )


@cache
def payoffs(information):
    notice = information.disclosed_capacity
    possible_states = [
        SettlementState(capacity, order, information.terms)
        for capacity in CAPACITIES if notice is None or capacity == notice
        for order in ORDERS
    ]
    expected = {}
    for profile in PROFILES:
        actions = tenders(information.impatient, profile)
        totals = dict.fromkeys(patients(information.impatient), ZERO)
        for state in possible_states:
            output = settle(actions, state)
            for patient in totals:
                totals[patient] += output.consumption(patient)
        expected[profile] = tuple(total / len(possible_states) for total in totals.values())
    return expected


@cache
def equilibria(information):
    table = payoffs(information)
    if any(table[a, b][0] != table[b, a][1] for a, b in PROFILES):
        raise ValueError("This symmetric game solver requires exchangeable patients.")
    wait_advantage = table["W", "W"][0] - table["E", "W"][0]
    early_advantage = table["E", "E"][0] - table["W", "E"][0]
    if not wait_advantage or not early_advantage:
        raise ValueError("This solver requires strict endpoint comparisons.")
    if wait_advantage > 0 > early_advantage:
        return ((ZERO, ZERO),)
    one = Fraction(1)
    if early_advantage > 0 > wait_advantage:
        return ((one, one),)
    switch = wait_advantage / (wait_advantage + early_advantage)
    pure = ((ZERO, ZERO), (one, one)) if wait_advantage > 0 else ((ZERO, one), (one, ZERO))
    return tuple(sorted((*pure, (switch, switch))))


def select(information, strategy, draws):
    if strategy not in equilibria(information):
        raise ValueError("Policy must be an equilibrium on the supplied information set.")
    selections = ["E" if draw < probability else "W" for probability, draw in zip(strategy, draws, strict=True)]
    return tenders(information.impatient, selections)

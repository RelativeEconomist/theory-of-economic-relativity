"""Verify the archived evidence, independent payments, and fixed-state replays."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from .economy import (
    CAPACITIES, DEPOSITORS, HEALTHY, HISTORICAL, LATE_FLOOR, ORDERS, PRINCIPAL,
    PROFILES, PROMISE, ZERO, ChoiceInformation, Ledger, SettlementState, Terms,
    patients, shortfall, tenders,
)


@dataclass(frozen=True)
class RecordedBank:
    information: ChoiceInformation
    state: SettlementState
    actions: tuple[str, ...]
    ledger: Ledger

    @property
    def profile(self):
        return tuple(self.actions[i] for i in patients(self.information.impatient))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bank(trace):
    assignment, notice, lock, queue, early, late = (
        trace[key] for key in ("assignment", "notice", "lock", "service_order", "early_service", "maturity")
    )
    timing = assignment["timing"]
    require(timing in ("early", "delayed"), "Unknown disclosure assignment")
    actual_events = tuple(event["event"] for event in (assignment, notice, lock, queue, early, late))
    require(actual_events == (0, 1 if timing == "early" else 3, 2, 4, 5, 6), "Invalid event timing")

    capacity, impatient = Fraction(assignment["capacity"]), assignment["impatient"]
    require(capacity in CAPACITIES and impatient in DEPOSITORS, "Invalid capacity or depositor assignment")
    require(Fraction(notice["capacity"]) == capacity, "Notice differs from assigned capacity")
    require(Fraction(assignment["invested"]) == PRINCIPAL, "Wrong opening principal")
    view = lock["information"]
    disclosed = assignment["capacity"] if timing == "early" else None
    require(view == {
        "impatient": impatient, "disclosed_capacity": disclosed,
        "capacity_lottery": list(map(str, CAPACITIES)), "terms": view["terms"],
        "patient_menu": "WE", "disclosure_schedule": timing,
    }, "Missing or leaked pre-choice information")
    terms = Terms(**{key: Fraction(value) for key, value in view["terms"].items()})
    require(Fraction(assignment["treasury"]) == terms.treasury, "Opening reserve differs from contract")
    information = ChoiceInformation(impatient, Fraction(disclosed) if disclosed is not None else None, terms)
    order = tuple(queue["permutation"])
    require(order in ORDERS, "Service order must be a full permutation")
    state = SettlementState(capacity, order, terms)

    actions = tuple(lock["tenders"])
    require(len(actions) == len(DEPOSITORS) and set(actions) <= {"E", "W"}, "Invalid tender record")
    require(actions[impatient] == "E", "The assigned impatient depositor must tender")
    waiters = [i for i, action in enumerate(actions) if action == "W"]
    require(early["next_state"]["waiting_claimants"] == waiters, "The standing claims differ from the locked profile")
    for settlement in (early, late):
        require(len(settlement["bank_payments"]) == len(settlement["topups"]) == len(DEPOSITORS), "Wrong receipt count")
        own_receipts = [
            {"bank": paid, "topup": topup}
            for paid, topup in zip(settlement["bank_payments"], settlement["topups"], strict=True)
        ]
        require(settlement["own_receipt_observations"] == own_receipts, "Invalid settlement observations")

    ledger = Ledger(
        tuple(map(Fraction, early["bank_payments"])), tuple(map(Fraction, late["bank_payments"])),
        tuple(map(Fraction, early["topups"])), tuple(map(Fraction, late["topups"])),
        Fraction(late["residual"]), Fraction(early["next_state"]["invested"]),
        Fraction(early["next_state"]["unused_limit"]), Fraction(early["next_state"]["treasury"]),
        Fraction(late["treasury_returned"]),
    )
    return RecordedBank(information, state, actions, ledger)


def verify_ledger(bank, ledger):
    state, terms = bank.state, bank.state.terms
    prior_paid = ZERO
    for i in state.order:
        tendered = bank.actions[i] == "E"
        expected = min(PROMISE, state.capacity - prior_paid, PRINCIPAL - prior_paid) if tendered else ZERO
        require(ledger.bank_early[i] == expected, f"Sequential-service error for depositor {i}")
        early_topup = PROMISE - expected if terms.treasury and tendered else ZERO
        require(ledger.topups_early[i] == early_topup, f"Early guarantee error for depositor {i}")
        prior_paid += expected

    require(prior_paid + ledger.invested_after_service == PRINCIPAL, "Principal fails to reconcile")
    require(prior_paid + ledger.limit_after_service == state.capacity, "Early limit fails to reconcile")
    require(ledger.invested_after_service >= 0 and ledger.limit_after_service >= 0, "Negative bank balances")
    waiting = bank.actions.count("W")
    pool = ledger.invested_after_service * terms.maturity_rate
    for i, action in enumerate(bank.actions):
        expected = pool / waiting if action == "W" else ZERO
        require(ledger.bank_late[i] == expected, f"Late claim error for depositor {i}")
        late_topup = max(ZERO, LATE_FLOOR - expected) if terms.treasury and action == "W" else ZERO
        require(ledger.topups_late[i] == late_topup, f"Late guarantee error for depositor {i}")
    require(ledger.residual == (ZERO if waiting else pool), "Residual beneficiary fails to reconcile")
    require(ledger.early_paid + sum(ledger.bank_late) + ledger.residual == prior_paid + pool, "Bank uses differ from sources")
    require(sum(ledger.topups_early) + ledger.treasury_after_service == terms.treasury, "Early reserve fails to reconcile")
    require(sum(ledger.topups_late) + ledger.treasury_returned == ledger.treasury_after_service, "Late reserve fails to reconcile")
    require(ledger.treasury_returned >= 0 and ledger.treasury_after_service >= 0, "Insufficient treasury funding")


def replay(model, recorded, actions):
    require(model.settle(recorded.actions, recorded.state) == recorded.ledger, "Factual replay differs from recorded ledger")
    return model.settle(actions, recorded.state)


def reference_equilibria(information):
    if information.terms == HISTORICAL["return_shock"]:
        return ((1, 1),)
    if information.terms == HISTORICAL["guarantee"] or information.disclosed_capacity == CAPACITIES[0]:
        return ((0, 0),)
    interior = {None: Fraction(27, 35), CAPACITIES[1]: Fraction(3, 11), CAPACITIES[2]: Fraction(1, 4)}
    q = interior[information.disclosed_capacity]
    return ((0, 0), (q, q), (1, 1))


def verify_best_responses(table, strategy):
    for i, probability in enumerate(strategy):
        opponent = strategy[1 - i]
        gain = ZERO
        for other, weight in (("W", 1 - opponent), ("E", opponent)):
            wait = ("W", other) if i == 0 else (other, "W")
            early = ("E", other) if i == 0 else (other, "E")
            gain += weight * (table[early][i] - table[wait][i])
        require(not (probability > 0 and gain < 0), "A tender in support is unprofitable")
        require(not (probability < 1 and gain > 0), "Waiting in support is unprofitable")


def verify_exact(rows, models):
    cases = {}
    for row in rows:
        bank = read_bank(row["trace"])
        label = row["case"]
        if label == "randomized":
            require(bank.state.terms == HEALTHY, "Randomized cases use the uninsured contract")
        else:
            require(bank.state.terms == HISTORICAL[label] and bank.state.capacity == PRINCIPAL, "Wrong historical contract")
        key = (label, bank.information, bank.state, bank.actions)
        require(key not in cases, "Duplicate exact case")
        cases[key] = bank

    conditions = [("randomized", k, notice, HEALTHY) for k in CAPACITIES for notice in (k, None)]
    conditions += [(label, PRINCIPAL, PRINCIPAL, terms) for label, terms in HISTORICAL.items()]
    expected_keys = {
        (label, ChoiceInformation(role, notice, terms), SettlementState(k, order, terms), tenders(role, profile))
        for label, k, notice, terms in conditions for role, profile, order in product(DEPOSITORS, PROFILES, ORDERS)
    }
    require(cases.keys() == expected_keys, "Missing or extra cases in the exhaustive grid")

    oracle_payoffs = defaultdict(lambda: defaultdict(list))
    maximum_topups = ZERO
    for (label, information, state, actions), bank in cases.items():
        verify_ledger(bank, bank.ledger)
        totals = tuple(bank.ledger.consumption(i) for i in patients(information.impatient))
        oracle_payoffs[label, information][bank.profile].append(totals)
        maximum_topups = max(maximum_topups, sum(bank.ledger.topups_early + bank.ledger.topups_late))
        alternative = tenders(information.impatient, ("E" if bank.profile[0] == "W" else "W", bank.profile[1]))
        expected = cases[label, information, state, alternative].ledger
        for model in models:
            try:
                require(replay(model, bank, alternative) == expected, "Counterfactual ledger differs from oracle")
            except ValueError as exc:
                raise ValueError(f"{model.__name__}, {label}, {information}, {state}, {actions}: {exc}") from exc

    for (_, information), outcomes in oracle_payoffs.items():
        table = {
            profile: tuple(sum(values) / len(histories) for values in zip(*histories, strict=True))
            for profile, histories in outcomes.items()
        }
        for model in models:
            require(model.payoffs(information) == table, f"{model.__name__} payoffs differ from oracle")
            strategies = model.equilibria(information)
            require(strategies == reference_equilibria(information), f"{model.__name__} equilibrium set differs from protocol")
            for strategy in strategies:
                verify_best_responses(table, strategy)
    require(maximum_topups == HISTORICAL["guarantee"].treasury, "Unexpected maximum fiscal payout")

    low, middle, high = CAPACITIES
    def ledger_at(capacity, actions):
        return cases["randomized", ChoiceInformation(0, None), SettlementState(capacity, DEPOSITORS), actions].ledger

    all_tender, one_tender, two_tender = tuple("EEE"), tuple("EWW"), tuple("EEW")
    binding = shortfall(all_tender, ledger_at(low, all_tender)) - shortfall(all_tender, ledger_at(high, all_tender))
    nonbinding = shortfall(one_tender, ledger_at(low, one_tender)) - shortfall(one_tender, ledger_at(high, one_tender))
    payout_collision = ledger_at(middle, two_tender).early_paid == ledger_at(middle, all_tender).early_paid
    require(binding == Fraction(4, 5) and nonbinding == 0 and payout_collision, "Isolation probes failed")
    return {
        "status": "pass", "cases": len(cases), "maximum_treasury_payout": maximum_topups,
        "binding_effect": binding, "nonbinding_effect": nonbinding, "payout_collision": payout_collision,
    }

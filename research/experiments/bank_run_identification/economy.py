"""Shared contract, decision information, and observable ledger schema."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product


ZERO = Fraction(0)
PRINCIPAL = Fraction(3)
PROMISE = Fraction(7, 5)
LATE_FLOOR = Fraction(8, 5)
GUARANTEE = Fraction(6, 5)
CAPACITIES = (Fraction(11, 5), Fraction(14, 5), PRINCIPAL)
DEPOSITORS = (0, 1, 2)
ORDERS = tuple(permutations(DEPOSITORS))
PROFILES = tuple(product("WE", repeat=2))


@dataclass(frozen=True)
class Terms:
    maturity_rate: Fraction = Fraction(2)
    treasury: Fraction = ZERO


HEALTHY = Terms()
HISTORICAL = {
    "healthy": HEALTHY,
    "return_shock": Terms(Fraction(11, 10)),
    "guarantee": Terms(treasury=GUARANTEE),
}


@dataclass(frozen=True)
class ChoiceInformation:
    impatient: int
    disclosed_capacity: Fraction | None
    terms: Terms = HEALTHY


@dataclass(frozen=True)
class SettlementState:
    capacity: Fraction
    order: tuple[int, ...]
    terms: Terms = HEALTHY


@dataclass(frozen=True)
class Ledger:
    bank_early: tuple[Fraction, ...]
    bank_late: tuple[Fraction, ...]
    topups_early: tuple[Fraction, ...]
    topups_late: tuple[Fraction, ...]
    residual: Fraction
    invested_after_service: Fraction
    limit_after_service: Fraction
    treasury_after_service: Fraction
    treasury_returned: Fraction

    def consumption(self, depositor):
        return sum(
            payments[depositor]
            for payments in (
                self.bank_early, self.bank_late, self.topups_early, self.topups_late
            )
        )

    @property
    def early_paid(self):
        return sum(self.bank_early)


def patients(impatient):
    return tuple(depositor for depositor in DEPOSITORS if depositor != impatient)


def tenders(impatient, profile):
    actions = dict(zip(patients(impatient), profile, strict=True))
    actions[impatient] = "E"
    return tuple(actions[depositor] for depositor in DEPOSITORS)


def shortfall(actions, ledger):
    return actions.count("E") * PROMISE - ledger.early_paid

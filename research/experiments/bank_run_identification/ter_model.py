"""Architecture A. Agent-side valuation and choice, joint reality, then transition."""

from fractions import Fraction
from functools import cache

from research.ter import AgentSpec, RealityResult
from research.ter.decision import ValuationView, select_action
from research.ter.runner import build_agent, frozen_agent

from .economy import (
    CAPACITIES, DEPOSITORS, LATE_FLOOR, ORDERS, PRINCIPAL, PROFILES, PROMISE, ZERO,
    Ledger, SettlementState, patients, tenders,
)


def reality(actions, state):
    """Joint early realization against the recorded objective service order."""
    available = min(PRINCIPAL, state.capacity)
    payments = {i: ZERO for i in DEPOSITORS}
    for depositor in state.order:
        if actions[depositor] == "E":
            payments[depositor] = min(PROMISE, available)
            available -= payments[depositor]

    topups = {
        i: PROMISE - paid if state.terms.treasury and actions[i] == "E" else ZERO
        for i, paid in payments.items()
    }
    return RealityResult(
        system={
            "paid": sum(payments.values()),
            "topups": sum(topups.values()),
            "waiters": tuple(i for i in DEPOSITORS if actions[i] == "W"),
        },
        agents={str(i): {"paid": payments[i], "topup": topups[i]} for i in DEPOSITORS},
    )


def advance(state, outcome):
    return (
        PRINCIPAL - outcome.system["paid"],
        state.capacity - outcome.system["paid"],
        state.terms.treasury - outcome.system["topups"],
        outcome.system["waiters"],
    )


def settle(actions, state):
    early = reality(actions, state)
    invested, unused_limit, treasury, waiters = advance(state, early)
    maturity_pool = invested * state.terms.maturity_rate
    late = tuple(maturity_pool / len(waiters) if i in waiters else ZERO for i in DEPOSITORS)
    late_topups = tuple(
        max(ZERO, LATE_FLOOR - late[i]) if state.terms.treasury and i in waiters else ZERO
        for i in DEPOSITORS
    )
    return Ledger(
        tuple(early.agents[str(i)]["paid"] for i in DEPOSITORS), late,
        tuple(early.agents[str(i)]["topup"] for i in DEPOSITORS), late_topups,
        ZERO if waiters else maturity_pool, invested, unused_limit, treasury, treasury - sum(late_topups),
    )


@cache
def payoffs(information):
    capacities = CAPACITIES if information.disclosed_capacity is None else (information.disclosed_capacity,)
    table = {}
    for profile in PROFILES:
        actions = tenders(information.impatient, profile)
        histories = [
            settle(actions, SettlementState(capacity, order, information.terms))
            for capacity in capacities for order in ORDERS
        ]
        table[profile] = tuple(
            sum(history.consumption(i) for history in histories) / len(histories)
            for i in patients(information.impatient)
        )
    return table


def value(action, agent):
    if agent.objective != "consumption":
        raise ValueError("This contract values consumption.")
    if (1 if action == "E" else 2) not in agent.horizon:
        return ZERO
    belief = agent.model_of_reality
    position, probability = belief["position"], belief["other_tenders"]
    outcomes = payoffs(belief["information"])
    if position == 0:
        wait, early = outcomes[action, "W"][0], outcomes[action, "E"][0]
    else:
        wait, early = outcomes["W", action][1], outcomes["E", action][1]
    return wait * (1 - probability) + early * probability


def decide(agent):
    values = {action: agent.value(action) for action in agent.perceived_feasible_set}
    if values["E"] != values["W"]:
        return max(values, key=values.__getitem__)
    return "E" if agent.decision_parameters["draw"] < agent.decision_parameters["tender_probability"] else "W"


@cache
def equilibria(information):
    zero, one = ZERO, Fraction(1)
    gains = []
    for position in range(2):
        gains_at_endpoints = []
        for other in (zero, one):
            view = ValuationView(
                "consumption", {"information": information, "position": position, "other_tenders": other},
                (1, 2), {},
            )
            gains_at_endpoints.append(value("E", view) - value("W", view))
        gains.append(tuple(gains_at_endpoints))

    if any(zero in endpoints for endpoints in gains):
        raise ValueError("A boundary indifference requires a different equilibrium enumeration.")
    candidates = []
    for first in (zero, one):
        for second in (zero, one):
            if (gains[0][int(second)] > zero) == bool(first) and (gains[1][int(first)] > zero) == bool(second):
                candidates.append((first, second))
    if all(wait * early < zero for wait, early in gains):
        other_probabilities = [wait / (wait - early) for wait, early in gains]
        candidates.append(tuple(reversed(other_probabilities)))
    return tuple(sorted(candidates))


def select(information, strategy, draws):
    selected = []
    for position, depositor in enumerate(patients(information.impatient)):
        spec = AgentSpec(
            name=str(depositor), objective="consumption", horizon=(1, 2),
            model_of_reality={"information": information, "position": position, "other_tenders": strategy[1 - position]},
            perceived_feasible_set=list("WE"), valuation_rule=value, decision_process=decide,
            decision_parameters={"tender_probability": strategy[position], "draw": draws[position]},
        )
        selected.append(select_action(frozen_agent(build_agent(spec))))
    return tenders(information.impatient, selected)

"""
Lottery ticket scenario (theory/academic.md, Models 5.1 and 5.2).

Three illustrative specifications of the same buyer, Alex, choose
between buying one lottery ticket and skipping it. Mistaken odds and
entertainment value select by valuation; habit selects by a price rule
without valuation. The actual win probability and the realized draw
enter only R. research/tests/test_28_lottery_tickets.py states the
assumptions and hypotheses.
"""

from fractions import Fraction

from research.ter import AgentSpec, RealityResult, Scenario, run_scenario
from research.ter.rules import maximize_value


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

BUY = "buy"
SKIP = "skip"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

TICKET_PRICE = 20
JACKPOT = 10_000_000
ACTUAL_WIN_PROBABILITY = Fraction(1, 1_000_000)
AVAILABLE_FUNDS = 50

MISTAKEN_WIN_PROBABILITY = Fraction(1, 250_000)
ENTERTAINMENT_VALUE = 15
HABIT_MAXIMUM_PRICE = 30

# Baseline conditions. Every compared condition changes exactly one.
BASELINE = {
    "ticket_price": TICKET_PRICE,
    "jackpot": JACKPOT,
    "odds_disclosed": False,
    "available_funds": AVAILABLE_FUNDS,
}


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def lottery_value(action, agent):
    """
    V for the two valuation specifications: expected monetary value under
    the believed probability (M), plus any enjoyment value (V data).
    Local because no shared rule values a single-prize lottery.
    """
    if action == SKIP:
        return 0

    beliefs = agent.model_of_reality
    expected_prize = beliefs["believed_win_probability"] * beliefs["jackpot"]

    return (
        expected_prize
        - beliefs["ticket_price"]
        + agent.valuation["entertainment_value"]
    )


def valuation_not_used(action, agent):
    """The habit specification has no V; calling it is a specification error."""
    raise RuntimeError("The habit specification selects without valuation.")


def habit_purchase_rule(agent):
    """
    D for the habit specification: buy whenever buying is perceived as
    available (affordable) and the believed price is at most the habit's
    maximum price. It reads M and F̂ directly and never consults V.
    """
    affordable = BUY in agent.perceived_feasible_set
    price = agent.model_of_reality["ticket_price"]

    if affordable and price <= agent.decision_parameters["maximum_price"]:
        return BUY

    return SKIP


def perceived_options(model_of_reality):
    """F̂: buying is perceived as available only when believed affordable."""
    if model_of_reality["ticket_price"] <= model_of_reality["available_funds"]:
        return [BUY, SKIP]

    return [SKIP]


def adopt_credible_odds(model_of_reality, disclosed_probability):
    """
    Belief update for a credible odds disclosure: the believed win
    probability becomes the disclosed one. Only M changes.
    """
    return {**model_of_reality, "believed_win_probability": disclosed_probability}


def lottery_reality(actions, objective_state, parameters):
    """
    R: realize Alex's action against the actual price, prize, funds, and
    this draw's result. A purchase above actual funds fails.
    """
    (name, action), = actions.items()
    price = parameters["ticket_price"]

    if action == SKIP:
        status, spent, prize = "skipped", 0, 0
    elif action != BUY:
        raise ValueError(f"Unsupported lottery action: {action}")
    elif price > objective_state["available_funds"]:
        status, spent, prize = "purchase_failed", 0, 0
    elif objective_state["ticket_wins"]:
        status, spent, prize = "won", price, parameters["jackpot"]
    else:
        status, spent, prize = "lost", price, 0

    return RealityResult(
        agents={
            name: {
                "status": status,
                "spent": spent,
                "prize": prize,
                "net_return": prize - spent,
            },
        },
    )


# ---------------------------------------------------------------------------
# Agents: three rival specifications of the same person
# ---------------------------------------------------------------------------

MISTAKEN_ODDS = AgentSpec(
    name="alex_mistaken_odds",
    objective="maximize expected money",
    model_of_reality={"believed_win_probability": MISTAKEN_WIN_PROBABILITY},
    perceived_feasible_set=[BUY, SKIP],
    valuation={"entertainment_value": 0},
    valuation_rule=lottery_value,
    decision_process=maximize_value,
    decision_parameters={"tie_break_preference": SKIP},
    horizon="this draw only",
)

ENTERTAINMENT = AgentSpec(
    name="alex_entertainment_value",
    objective="maximize expected money plus enjoyment",
    model_of_reality={"believed_win_probability": ACTUAL_WIN_PROBABILITY},
    perceived_feasible_set=[BUY, SKIP],
    valuation={"entertainment_value": ENTERTAINMENT_VALUE},
    valuation_rule=lottery_value,
    decision_process=maximize_value,
    decision_parameters={"tie_break_preference": SKIP},
    horizon="this draw only",
)

HABIT = AgentSpec(
    name="alex_habit",
    objective="not consulted: the habit selects without valuation",
    model_of_reality={"believed_win_probability": MISTAKEN_WIN_PROBABILITY},
    perceived_feasible_set=[BUY, SKIP],
    valuation_rule=valuation_not_used,
    decision_process=habit_purchase_rule,
    decision_parameters={"maximum_price": HABIT_MAXIMUM_PRICE},
)

SPECIFICATIONS = [MISTAKEN_ODDS, ENTERTAINMENT, HABIT]


# ---------------------------------------------------------------------------
# Reality / Scenario
# ---------------------------------------------------------------------------

def lottery_scenario(specification, ticket_wins=False, **changes):
    """
    One specification deciding under the baseline with `changes` applied.
    Alex perceives price, prize, and funds as they actually are; the
    believed probability changes only through a credible disclosure.
    """
    condition = {**BASELINE, **changes}

    beliefs = {
        **specification.model_of_reality,
        "ticket_price": condition["ticket_price"],
        "jackpot": condition["jackpot"],
        "available_funds": condition["available_funds"],
    }
    if condition["odds_disclosed"]:
        beliefs = adopt_credible_odds(beliefs, ACTUAL_WIN_PROBABILITY)

    agent = specification.variant(
        model_of_reality=beliefs,
        perceived_feasible_set=perceived_options(beliefs),
    )

    return Scenario(
        name="Lottery Tickets -- One Decision, Many Explanations",
        description="Alex chooses between buying one lottery ticket and skipping it.",
        periods=1,
        initial_state={
            "available_funds": condition["available_funds"],
            "ticket_wins": ticket_wins,
        },
        agents=[agent],
        parameters={
            "ticket_price": condition["ticket_price"],
            "jackpot": condition["jackpot"],
            "win_probability": ACTUAL_WIN_PROBABILITY,
        },
        reality=lottery_reality,
    )


def outcome_distribution(specification, **changes):
    """
    Exact distribution of the realized outcome: R under both draw states,
    weighted by the actual win probability. Returns the selected action
    and a list of (probability, outcome), merging identical outcomes.
    """
    probability = lottery_scenario(specification, **changes).parameters["win_probability"]
    selected = set()
    distribution = []

    for ticket_wins, weight in ((True, probability), (False, 1 - probability)):
        scenario = lottery_scenario(specification, ticket_wins=ticket_wins, **changes)
        alex = run_scenario(scenario).agent(specification.name)
        selected.add(alex.selected_action)
        outcome = dict(alex.outcome)

        for index, (existing_weight, existing) in enumerate(distribution):
            if existing == outcome:
                distribution[index] = (existing_weight + weight, existing)
                break
        else:
            distribution.append((weight, outcome))

    (action,) = selected
    return action, distribution


def expected_net_return(distribution):
    return sum(weight * outcome["net_return"] for weight, outcome in distribution)


def ticket_expected_net_return(**changes):
    """
    Actual expected net monetary return of buying one ticket under the
    baseline with `changes` applied: actual odds x prize - price. It is
    hypothetical when no specification buys.
    """
    condition = {**BASELINE, **changes}
    return ACTUAL_WIN_PROBABILITY * condition["jackpot"] - condition["ticket_price"]


# Each compared condition: label and its single change from BASELINE.
CONDITIONS = [
    ("baseline", {}),
    ("price $28", {"ticket_price": 28}),
    ("price $35", {"ticket_price": 35}),
    ("price $45", {"ticket_price": 45}),
    ("prize $2,000,000", {"jackpot": 2_000_000}),
    ("prize $20,000,000", {"jackpot": 20_000_000}),
    ("odds disclosed", {"odds_disclosed": True}),
    ("funds $19", {"available_funds": 19}),
]


def comparison_table():
    """
    One row per condition: each specification's selected action and the
    actual expected net monetary return of that action, plus the
    hypothetical actual expected net monetary return of buying one ticket,
    whether or not anyone buys or can afford it.
    """
    rows = []

    for label, changes in CONDITIONS:
        condition = {**BASELINE, **changes}
        choices = {}
        returns = {}

        for specification in SPECIFICATIONS:
            action, distribution = outcome_distribution(specification, **changes)
            choices[specification.name] = action
            returns[specification.name] = expected_net_return(distribution)

        rows.append({
            "condition": label,
            "changes": changes,
            "choices": choices,
            "expected_net_returns": returns,
            "hypothetical_ticket_expected_net_return": ticket_expected_net_return(**changes),
            "ticket_affordable": condition["ticket_price"] <= condition["available_funds"],
            "distinguishes_specifications": len(set(choices.values())) > 1,
        })

    return rows

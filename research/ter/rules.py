from enum import Enum
from typing import Any, Callable

from research.ter.agent import AgentState
from research.ter.outcome import RealityView, permitted_actions_for


RULES: dict[str, Callable[..., Any]] = {}


def register_rule(name: str):
    """
    Register a reusable TER rule by name.

    Scenarios reference rules declaratively, for example:

        decision_process="maximize_value"
        decision_process="satisfice"
        feedback_rule="price_growth_expectations"
    """

    def decorator(function: Callable[..., Any]):
        if name in RULES:
            raise ValueError(f"Rule already registered: {name}")

        RULES[name] = function
        return function

    return decorator


def get_rule(name: str) -> Callable[..., Any]:
    """
    Resolve a named TER rule.
    """
    try:
        return RULES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown TER rule: {name}") from exc


# ---------------------------------------------------------------------------
# Rule contracts
# ---------------------------------------------------------------------------
#
# Every registered rule fits exactly one of these four shapes. A rule
# declares which one it implements only by its argument names and return
# type; there is no base class to inherit from.
#
#     Decision rule:     (agent)                             -> action
#     Value rule:        (action, agent)                     -> float
#     Reality function:  (state, agents, actions, parameters) -> dict
#     Feedback rule:     (state, outcome, parameters)         -> state
#
# The reality function is R: a model-specific implementation of
# O_t = R(C_1,t, ..., C_n,t, F_t) that determines the realized outcome
# from the selected actions and the objective feasible state of reality.
# F_t is carried by `state` (including state["permitted_actions"], the
# agents' permitted actions) and `parameters`. Its return value
# contributes to O; R is not O itself.


def build_agent_results(
    state: dict[str, Any],
    agents: list[RealityView],
    actions: list[Any],
    compute: Callable[[RealityView, Any], dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the standard named per-agent outcome shape for a reality
    function.

    Internal rule-authoring helper. Not part of the public research.ter
    API -- researchers select rules through the public enums and never
    call this directly. Use it only when writing a reality function that
    has genuinely per-agent results to report; aggregate-only outcomes
    (bank liquidity, market price) should keep returning a flat dict
    instead.

    compute(agent, action) -> dict is called once per agent for its
    actually selected action, and once per action F_t permits for that
    agent (state["permitted_actions"]), so
    ScenarioResult.agent(name).outcome_for(...) can look up an unselected
    action's outcome later without any rule being re-executed.
    Alternatives range over what F_t permits, not F_hat: R (this helper
    included) only ever receives a RealityView, which never carries the
    agent's perceived_feasible_set -- reality's own "what else could have
    happened" is a question about what was actually possible, not about
    what the agent believed was possible.

    Returns:

        {
            "agent_results": {
                agent.name: compute(agent, selected_action),
            },
            "alternative_outcomes": {
                agent.name: {
                    action: compute(agent, action)
                    for action in permitted_actions_for(state, agent)
                },
            },
        }
    """
    agent_results = {}
    alternative_outcomes = {}

    for agent, action in zip(agents, actions):
        agent_results[agent.name] = compute(agent, action)

        alternative_outcomes[agent.name] = {
            candidate: compute(agent, candidate)
            for candidate in permitted_actions_for(state, agent)
        }

    return {
        "agent_results": agent_results,
        "alternative_outcomes": alternative_outcomes,
    }


# ---------------------------------------------------------------------------
# Generic decision rules
# ---------------------------------------------------------------------------


@register_rule("maximize_value")
def maximize_value(agent: AgentState):
    """
    Select the perceived feasible action with the highest assigned value.

    This is one possible D specification.
    TER does not require optimization universally.

    Ties (more than one action sharing the highest value) resolve to
    the first tied action in perceived_feasible_set order, unless
    tie_break_preference names a tied action explicitly -- ties are then
    resolved by that stated preference, not by incidental F_hat order.

    Optional decision_parameters field:

        tie_break_preference   an action to prefer among tied maxima.
                               Has no effect if it isn't itself tied for
                               the highest value. Must be a perceived
                               feasible action if supplied.
    """
    values = {
        action: agent.value(action, agent)
        for action in agent.perceived_feasible_set
    }

    best_value = max(values.values())

    tied = [
        action
        for action in agent.perceived_feasible_set
        if values[action] == best_value
    ]

    preferred = agent.decision_parameters.get("tie_break_preference")

    if (
        preferred is not None
        and preferred not in agent.perceived_feasible_set
    ):
        raise ValueError(
            f"tie_break_preference must be in the perceived feasible set: {preferred}"
        )

    if preferred in tied:
        return preferred

    return tied[0]


@register_rule("satisfice")
def satisfice(agent: AgentState):
    """
    Select the first perceived feasible action whose value reaches the
    configured satisficing threshold.

    Required decision_parameters field:

        satisficing_threshold
    """
    threshold = agent.decision_parameters["satisficing_threshold"]

    for action in agent.perceived_feasible_set:
        if agent.value(action, agent) >= threshold:
            return action

    return agent.perceived_feasible_set[-1]


@register_rule("limited_search")
def limited_search(agent: AgentState):
    """
    Evaluate only the first N actions of a search sequence and select the
    highest valued action among those considered.

    This is one possible D specification: it does not have to maximize V
    over the full perceived feasible set, only over the actions it
    actually considers. Search order is part of D, not F_hat -- it lives
    in decision_parameters, never encoded by reordering
    perceived_feasible_set.

    Required decision_parameters field:

        search_limit

    Optional decision_parameters field:

        search_order   the sequence to search in. Defaults to
                       perceived_feasible_set's own order. Every action
                       in search_order must already be in
                       perceived_feasible_set -- it can reorder what is
                       perceived, not add to it.
    """
    search_limit = agent.decision_parameters["search_limit"]
    search_order = agent.decision_parameters.get(
        "search_order",
        agent.perceived_feasible_set,
    )

    unavailable = [
        action
        for action in search_order
        if action not in agent.perceived_feasible_set
    ]

    if unavailable:
        raise ValueError(
            f"search_order contains actions outside the perceived "
            f"feasible set: {unavailable}"
        )

    considered = search_order[:search_limit]

    if not considered:
        raise ValueError("Limited search considered no actions.")

    return max(
        considered,
        key=lambda action: agent.value(action, agent),
    )


@register_rule("first_feasible")
def first_feasible(agent: AgentState):
    """
    Select the first perceived feasible action.

    Useful for simple rule based, habitual, or ordered decision processes.
    """
    return agent.perceived_feasible_set[0]


# ---------------------------------------------------------------------------
# Generic valuation rules
# ---------------------------------------------------------------------------


@register_rule("mapped_value")
def mapped_value(action: Any, agent: AgentState) -> float:
    """
    Read an action's value from a declarative value map.

    Required valuation field:

        values = {
            "action_a": 5,
            "action_b": 10,
        }
    """
    return agent.valuation["values"][action]


@register_rule("net_value")
def net_value(action: Any, agent: AgentState) -> float:
    """
    Read an action's benefit and cost from declarative maps.

    benefits/costs are declared valuation amounts (V), not beliefs about
    reality -- they say how much an action is worth, not what the agent
    thinks is true.

    Required valuation fields:

        benefits
        costs
    """
    benefit = agent.valuation["benefits"].get(action, 0)
    cost = agent.valuation["costs"].get(action, 0)

    return benefit - cost


@register_rule("expected_return")
def expected_return(action: Any, agent: AgentState) -> float:
    """
    Value an investment action using expected appreciation.

    expected_appreciation is a belief about future reality (M).
    required_return is the agent's own valuation threshold -- the
    return it requires to be worth buying (V). V depends on M here
    without the two becoming the same thing.

    Required model_of_reality field:

        expected_appreciation

    Required valuation field:

        required_return

    Supported actions:

        buy
        hold
    """
    if action == "hold":
        return 0.0

    if action != "buy":
        raise ValueError(
            f"expected_return does not support action: {action}"
        )

    return (
        agent.model_of_reality["expected_appreciation"]
        - agent.valuation["required_return"]
    )


@register_rule("bank_depositor_value")
def bank_depositor_value(action: Any, agent: AgentState) -> float:
    """
    Depositor valuation under perceived bank failure risk.

    failure_probability is a belief about the bank (M). deposit_value,
    deposit_benefit, and withdrawal_cost are the depositor's own
    valuation amounts (V) -- V depends on M here without the two
    becoming the same thing.

    Required model_of_reality field:

        failure_probability

    Required valuation fields:

        deposit_value
        deposit_benefit
        withdrawal_cost
    """
    if action == "withdraw":
        return (
            agent.valuation["deposit_value"]
            - agent.valuation["withdrawal_cost"]
        )

    if action != "stay":
        raise ValueError(
            f"bank_depositor_value does not support action: {action}"
        )

    return (
        agent.valuation["deposit_value"]
        * (1 - agent.model_of_reality["failure_probability"])
        + agent.valuation["deposit_benefit"]
    )


@register_rule("bank_liquidity_confidence")
def bank_liquidity_confidence(
    state: dict[str, Any],
    outcome: Any,
    parameters: dict[str, Any],
):
    """
    Update depositor failure beliefs from bank liquidity.

    Each depositor may also have an independent risk signal.

    Required state fields:

        liquidity
        agents

    Required parameter:

        initial_liquidity
    """
    liquidity_ratio = (
        state["liquidity"]
        / parameters["initial_liquidity"]
    )

    liquidity_risk = max(
        0.0,
        min(1.0, 1 - liquidity_ratio),
    )

    for agent in state["agents"]:
        signal = agent.model_of_reality.get(
            "risk_signal",
            0.0,
        )

        agent.model_of_reality["failure_probability"] = max(
            signal,
            liquidity_risk,
        )

    return state


@register_rule("withdrawals_reduce_liquidity")
def withdrawals_reduce_liquidity(
    state: dict[str, Any],
    agents: list[AgentState],
    actions: list[Any],
    parameters: dict[str, Any],
):
    """
    Aggregate withdrawals and apply the bank's actual liquidity constraint.

    Required state field:

        liquidity

    Required parameter:

        withdrawal_amount
    """
    withdrawals = actions.count("withdraw")

    requested = (
        withdrawals
        * parameters["withdrawal_amount"]
    )

    realized = min(
        requested,
        state["liquidity"],
    )

    remaining = max(
        0,
        state["liquidity"] - realized,
    )

    return {
        "withdrawals": withdrawals,
        "requested_liquidity": requested,
        "realized_withdrawals": realized,
        "liquidity": remaining,
    }

# ---------------------------------------------------------------------------
# Shared dynamic rules
# ---------------------------------------------------------------------------


@register_rule("price_growth_expectations")
def price_growth_expectations(
    state: dict[str, Any],
    outcome: Any,
    parameters: dict[str, Any],
):
    """
    Update expected appreciation from observed price growth.

    Required state fields:

        previous_price
        price
        agents

    Required parameter:

        feedback_strength

    feedback_strength is scenario specific, not a TER primitive.
    """
    previous_price = state["previous_price"]
    current_price = state["price"]

    if previous_price == 0:
        growth = 0.0
    else:
        growth = (
            current_price - previous_price
        ) / previous_price

    expected_appreciation = (
        parameters["feedback_strength"]
        * growth
    )

    for agent in state["agents"]:
        agent.model_of_reality["expected_appreciation"] = (
            expected_appreciation
        )

    return state


@register_rule("demand_moves_price")
def demand_moves_price(
    state: dict[str, Any],
    agents: list[AgentState],
    actions: list[Any],
    parameters: dict[str, Any],
):
    """
    Simple model specific price response to aggregate buying.

    Required state field:

        price

    Required parameter:

        price_sensitivity

    This is not a universal TER asset pricing equation.

    Reports previous_price (the price before this period's update)
    alongside the new price, since this rule is the one place that
    actually changes price. The generic runner does not special case
    any field name.
    """
    buyers = actions.count("buy")

    next_price = state["price"] * (
        1
        + parameters["price_sensitivity"] * buyers
    )

    return {
        "buyers": buyers,
        "previous_price": state["price"],
        "price": next_price,
    }


# ---------------------------------------------------------------------------
# Quality market rules (asymmetric information)
# ---------------------------------------------------------------------------
#
# Pooled/true quality pricing is not modeled here as feedback: both
# prices are fixed functions of scenario parameters (and, for the true
# price, actual seller quality), never of a realized outcome, so they
# belong in each seller's initial valuation (V_0) instead. See
# test_04_asymmetric_information.py.


@register_rule("quality_market_outcome")
def quality_market_outcome(
    state: dict[str, Any],
    agents: list[AgentState],
    actions: list[Any],
    parameters: dict[str, Any],
):
    """
    Aggregate seller sell/hold decisions by actual quality.

    Actual quality is a fact about reality, not any seller's belief --
    read from the scenario side, never from agent.model_of_reality.

    Required parameter:

        actual_quality_by_seller   seller name -> "high" or "low"
    """
    actual_quality_by_seller = parameters["actual_quality_by_seller"]

    sold_high = 0
    sold_low = 0

    for agent, action in zip(agents, actions):
        if action != "sell":
            continue

        if actual_quality_by_seller[agent.name] == "high":
            sold_high += 1
        else:
            sold_low += 1

    return {
        "sold_high": sold_high,
        "sold_low": sold_low,
        "total_sold": sold_high + sold_low,
    }


# ---------------------------------------------------------------------------
# Externality rules
# ---------------------------------------------------------------------------


@register_rule("private_value")
def private_value(action: Any, agent: AgentState) -> float:
    """
    Value an action using only its underlying private value, ignoring any
    external effect.

    private_values is a declared valuation amount (V), not a belief.

    Required valuation field:

        private_values   action -> private value
    """
    return agent.valuation["private_values"][action]


@register_rule("internalized_value")
def internalized_value(action: Any, agent: AgentState) -> float:
    """
    Value an action as private value plus the agent's own *perceived*
    external effect, as if that belief were fully internalized into the
    agent's decision.

    private_values is the agent's own valuation (V).
    perceived_external_effects is the agent's belief about the
    consequence its action has on others (M) -- not necessarily the
    actual effect that feeds the realized outcome (see
    social_value_outcome). V depends on M here without the two becoming
    the same thing.

    Required valuation field:

        private_values                action -> private value

    Required model_of_reality field:

        perceived_external_effects    action -> believed external effect
    """
    return (
        agent.valuation["private_values"][action]
        + agent.model_of_reality["perceived_external_effects"][action]
    )


@register_rule("social_value_outcome")
def social_value_outcome(
    state: dict[str, Any],
    agents: list[RealityView],
    actions: list[Any],
    parameters: dict[str, Any],
):
    """
    Calculate social value under this scenario's stated welfare measure
    as the actual private value plus the actual external effect.

    Reads the scenario's actual private_values and actual external_effects
    -- both facts about reality, not any agent's belief or valuation --
    never the agent's own decision valuation (agent.value or
    agent.valuation) or perceived external effect. This keeps social
    value tied entirely to what actually happens, while remaining a
    scenario-specific welfare measure rather than a universal TER outcome
    equation.

    private_values is deliberately a scenario parameter here, not the
    agent's own valuation["private_values"] (V): the two are declared
    equal in every current scenario that uses this rule (see
    test_08_externalities.py), the same way that scenario's
    perceived_external_effects (M) and external_effects (a condition of
    F_t) are declared equal -- TER does not require either equality, and
    R must not read M or V to find out.

    Required scenario parameters:

        private_values      action -> actual private value
        external_effects    action -> actual external effect

    Reports two things, both keyed by agent name rather than position, and
    neither carrying a "selected_action" marker: which action was actually
    selected comes from the core scenario execution result
    (AgentResult.selected_action), not from a reality function.

        agent_results         the generic outcome for the action actually
                               selected.
        alternative_outcomes  the generic outcome for every action F_t
                               permits for that agent
                               (state["permitted_actions"], including the
                               selected one). Lets a result look up an
                               unselected-but-actually-feasible action's
                               outcome (see AgentResult.outcome_for)
                               without any rule being re-executed later.
    """

    def compute_outcome(agent, action):
        private_value = parameters["private_values"][action]
        external_effect = parameters["external_effects"][action]

        return {
            "action": action,
            "private_value": private_value,
            "external_effect": external_effect,
            "social_value": private_value + external_effect,
        }

    agent_results = {}
    alternative_outcomes = {}

    for agent, action in zip(agents, actions):
        agent_results[agent.name] = compute_outcome(agent, action)

        alternative_outcomes[agent.name] = {
            candidate: compute_outcome(agent, candidate)
            for candidate in permitted_actions_for(state, agent)
        }

    return {
        "agent_results": agent_results,
        "alternative_outcomes": alternative_outcomes,
    }


# ---------------------------------------------------------------------------
# Strategic interaction rules
# ---------------------------------------------------------------------------


@register_rule("payoff_matrix_value")
def payoff_matrix_value(action: Any, agent: AgentState) -> float:
    """
    Value an action by looking up a payoff matrix against the agent's
    expected counterpart action.

    expected_other_action is a belief about what the counterpart will do
    (M), read here at valuation time -- it is a real input to the
    decision, not documentation the test author resolved by hand before
    building the agent. payoff_matrix is the agent's own payoff
    valuation (V) for each action pair.

    Required valuation field:

        payoff_matrix           action -> counterpart_action -> payoff

    Required model_of_reality field:

        expected_other_action   the counterpart action this agent expects
    """
    payoff_matrix = agent.valuation["payoff_matrix"]
    expected_other_action = agent.model_of_reality["expected_other_action"]

    return payoff_matrix[action][expected_other_action]


@register_rule("payoff_matrix_outcome")
def payoff_matrix_outcome(
    state: dict[str, Any],
    agents: list[AgentState],
    actions: list[Any],
    parameters: dict[str, Any],
):
    """
    Realize each of two players' payoff from the scenario's actual
    payoff matrix and both players' selected actions.

    The actual payoff matrix is a fact about reality, not any player's
    valuation -- read from parameters, never from agent.valuation. A
    player's own payoff_matrix_value may or may not match it (see
    test_05_prisoners_dilemma.py for the case where a test assumes they
    do).

    Required parameter:

        actual_payoff_matrix   action -> counterpart_action -> payoff

    Requires exactly two agents -- one two-player game per period.
    """
    if len(agents) != 2:
        raise ValueError(
            "payoff_matrix_outcome requires exactly two agents."
        )

    actual_payoff_matrix = parameters["actual_payoff_matrix"]

    (agent_a, agent_b) = agents
    (action_a, action_b) = actions

    return {
        "payoffs": {
            agent_a.name: actual_payoff_matrix[action_a][action_b],
            agent_b.name: actual_payoff_matrix[action_b][action_a],
        },
    }


# ---------------------------------------------------------------------------
# Market rules
# ---------------------------------------------------------------------------


@register_rule("price_taking_value")
def price_taking_value(action: Any, agent: AgentState) -> float:
    """
    Value an action using net_value's benefit-minus-cost logic, except
    the action named by valuation["price_taking_action"] reads its
    price-facing side directly from the live model_of_reality["price"]
    instead of a static map -- whichever side of the trade this agent is
    on.

    price is the currently observed market price, a belief about
    reality (M). price_taking_action and price_role only configure how
    this valuation rule uses that price, so they live in valuation (V)
    alongside benefits/costs, not in model_of_reality.

    Required model_of_reality field:

        price                 the currently quoted market price

    Required valuation fields:

        price_taking_action   the action whose value depends on price
                               (e.g. "buy" for a buyer, "sell" for a
                               seller)
        price_role             "cost" if price reduces this action's
                               value (a buyer paying the price), or
                               "benefit" if price increases it (a
                               seller receiving the price)
        benefits, costs       the same declarative maps net_value reads,
                               used for every other action
    """
    benefits = agent.valuation.get("benefits", {})
    costs = agent.valuation.get("costs", {})

    if action == agent.valuation.get("price_taking_action"):
        price = agent.model_of_reality["price"]

        if agent.valuation["price_role"] == "cost":
            return benefits.get(action, 0) - price

        return price - costs.get(action, 0)

    return benefits.get(action, 0) - costs.get(action, 0)


# ---------------------------------------------------------------------------
# Public rule enums
# ---------------------------------------------------------------------------
#
# Curated, discoverable names for every rule registered above and shared
# across scenarios. Each member's value is the exact registered rule
# string, so DecisionProcess.MAXIMIZE and "maximize_value" resolve
# through get_rule identically -- this is a naming convenience, not a
# second registration mechanism.
#
# Rules that are registered locally by a single test (e.g.
# capacity_constrained_realization in test_feasibility_contract.py) are
# intentionally left out. They remain valid, usable rule names via their
# plain string, the advanced escape hatch for a rule scoped to one
# scenario.


class DecisionProcess(str, Enum):
    MAXIMIZE = "maximize_value"
    SATISFICE = "satisfice"
    LIMITED_SEARCH = "limited_search"
    FIRST_FEASIBLE = "first_feasible"


class ValuationRule(str, Enum):
    MAPPED = "mapped_value"
    NET = "net_value"
    EXPECTED_RETURN = "expected_return"
    BANK_DEPOSITOR = "bank_depositor_value"
    PRIVATE = "private_value"
    INTERNALIZED = "internalized_value"
    PAYOFF_MATRIX = "payoff_matrix_value"
    PRICE_TAKING = "price_taking_value"


class RealityFunction(str, Enum):
    WITHDRAWALS_REDUCE_LIQUIDITY = "withdrawals_reduce_liquidity"
    DEMAND_MOVES_PRICE = "demand_moves_price"
    QUALITY_MARKET = "quality_market_outcome"
    SOCIAL_VALUE = "social_value_outcome"
    PAYOFF_MATRIX_OUTCOME = "payoff_matrix_outcome"


class FeedbackRule(str, Enum):
    BANK_LIQUIDITY_CONFIDENCE = "bank_liquidity_confidence"
    PRICE_GROWTH_EXPECTATIONS = "price_growth_expectations"
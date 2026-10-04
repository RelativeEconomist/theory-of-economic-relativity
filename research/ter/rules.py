from typing import Any

from research.ter.agent import AgentState
from research.ter.reality import RealityResult


# ---------------------------------------------------------------------------
# Rule contracts
# ---------------------------------------------------------------------------
#
# Every rule fits exactly one of these six shapes. A rule declares which
# one it implements only by its argument names and return type; there is
# no base class, registry, or symbolic reference to resolve. AgentSpec and
# Scenario receive the rule callables directly.
#
#     Decision rule:     (agent)                                -> action
#     Value rule:        (action, agent)                        -> float
#     Reality rule:      (actions, objective_state, parameters)
#                            -> RealityResult
#     Transition rule:   (objective_state, reality, parameters)
#                            -> objective_state
#     Observation rule:  (agents, actions, reality, objective_state,
#                         parameters) -> {agent name: data}
#     Update rule:       (agent, observation) -> {component: new value}
#
# The reality rule is R: a model-specific implementation of
# O_t = R(C_1,t, ..., C_n,t, F_t) that determines the realized outcome
# from the selected actions and the objective feasible state of reality.
# Its return value is O (RealityResult); R is not O itself.
#
# actions maps each acting agent's name to C_i,t; inactive agents are
# absent. objective_state is F_t for R (frozen) and a mutable copy of
# F_t for a transition, which returns F_t+1. F_t is carried by
# objective_state (including objective_state["permitted_actions"], the
# agents' permitted actions) and parameters. An observation rule sees
# F_t+1 and decides what each agent receives; an update rule sees only
# its own agent (research.ter.observation.UpdateView) and that
# Observation, and returns replacements for agent-side components.
#
# Division of labor, one decision point:
#
#     R           realizes O from C and F_t          -- never changes F
#     transition  F_t -> F_t+1 from O                -- never touches agents
#     observation O, F_t+1 -> what each agent learns -- never changes state
#     update      agent + its observation -> agent'  -- never reads F or O
#
# Every rule is a deterministic function of its arguments; there is no
# randomness source yet. ScenarioResult.counterfactual relies on that
# and checks it.


# ---------------------------------------------------------------------------
# Generic decision rules
# ---------------------------------------------------------------------------


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


def first_feasible(agent: AgentState):
    """
    Select the first perceived feasible action.

    Useful for simple rule based, habitual, or ordered decision processes.
    """
    return agent.perceived_feasible_set[0]


# ---------------------------------------------------------------------------
# Generic valuation rules
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Externality rules
# ---------------------------------------------------------------------------


def private_value(action: Any, agent: AgentState) -> float:
    """
    Value an action using only its underlying private value, ignoring any
    external effect.

    private_values is a declared valuation amount (V), not a belief.

    Required valuation field:

        private_values   action -> private value
    """
    return agent.valuation["private_values"][action]


def internalized_value(action: Any, agent: AgentState) -> float:
    """
    Value an action as private value plus the agent's own *perceived*
    external effect, as if that belief were fully internalized into the
    agent's decision.

    private_values is the agent's own valuation (V).
    perceived_external_effects is the agent's belief about the
    consequence its action has on others (M) -- not necessarily the
    actual effect that feeds the realized outcome (see
    social_value_reality). V depends on M here without the two becoming
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


# ---------------------------------------------------------------------------
# Strategic interaction rules
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Market rules
# ---------------------------------------------------------------------------


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
# Reality, transition, observation, and update rules
# ---------------------------------------------------------------------------


def social_value_reality(actions, objective_state, parameters):
    """
    Realize each actor's
    private value, actual external effect, and this scenario's
    social-value measure (their sum) from the scenario's actual
    parameters -- never from any agent's belief or valuation.

    Each actor's outcome depends only on its own action, so this suits
    agent-level specifications (Model 5.2): it reports O_i,t per agent
    and no O_t. An unselected action's outcome comes from a
    counterfactual re-run (ScenarioResult.counterfactual), not from
    precomputed alternatives.

    Required parameters:

        private_values      action -> actual private value
        external_effects    action -> actual external effect
    """
    agents = {}

    for name, action in actions.items():
        private_value = parameters["private_values"][action]
        external_effect = parameters["external_effects"][action]

        agents[name] = {
            "action": action,
            "private_value": private_value,
            "external_effect": external_effect,
            "social_value": private_value + external_effect,
        }

    return RealityResult(agents=agents)


def payoff_matrix_reality(actions, objective_state, parameters):
    """
    Realize both players' payoffs from the scenario's actual payoff matrix and both
    selected actions.

    Each player's payoff depends on the other's action, so it is derived
    from this one joint realization (Model 5.3, "Agent-level outcomes")
    and reported as O_i,t per player. No separate O_t is defined.

    Required parameter:

        actual_payoff_matrix   action -> counterpart_action -> payoff

    Requires exactly two acting agents.
    """
    if len(actions) != 2:
        raise ValueError(
            "payoff_matrix_reality requires exactly two acting agents."
        )

    actual_payoff_matrix = parameters["actual_payoff_matrix"]

    ((name_a, action_a), (name_b, action_b)) = actions.items()

    return RealityResult(
        agents={
            name_a: {"payoff": actual_payoff_matrix[action_a][action_b]},
            name_b: {"payoff": actual_payoff_matrix[action_b][action_a]},
        },
    )


def withdrawal_liquidity_reality(actions, objective_state, parameters):
    """
    Realize aggregate withdrawals against the bank's actual liquidity in F_t.

    Reports O_t only. remaining_liquidity is what the realized
    withdrawals leave; folding it into F_t+1 is the transition's job
    (remaining_liquidity_transition), not R's.

    Required objective_state field:

        liquidity

    Required parameter:

        withdrawal_amount
    """
    withdrawals = list(actions.values()).count("withdraw")

    requested = withdrawals * parameters["withdrawal_amount"]
    realized = min(requested, objective_state["liquidity"])

    return RealityResult(
        system={
            "withdrawals": withdrawals,
            "requested_liquidity": requested,
            "realized_withdrawals": realized,
            "remaining_liquidity": objective_state["liquidity"] - realized,
        },
    )


def quality_market_reality(actions, objective_state, parameters):
    """
    Aggregate seller sell/hold decisions by actual quality.

    Pooled/true quality pricing is not modeled here as feedback: both
    prices are fixed functions of scenario parameters (and, for the true
    price, actual seller quality), never of a realized outcome, so they
    belong in each seller's initial valuation (V_0) instead. See
    test_04_asymmetric_information.py.

    Actual quality is a fact about reality, not any seller's belief --
    read from parameters, never from any agent's model_of_reality.
    Reports O_t only.

    Required parameter:

        actual_quality_by_seller   seller name -> "high" or "low"
    """
    actual_quality_by_seller = parameters["actual_quality_by_seller"]

    sold = [
        actual_quality_by_seller[name]
        for name, action in actions.items()
        if action == "sell"
    ]

    sold_high = sold.count("high")
    sold_low = len(sold) - sold_high

    return RealityResult(
        system={
            "sold_high": sold_high,
            "sold_low": sold_low,
            "total_sold": sold_high + sold_low,
        },
    )


def demand_price_reality(actions, objective_state, parameters):
    """
    A simple model-specific price response to aggregate buying against the price in F_t. Not a
    universal TER asset pricing equation.

    Reports O_t: the number of buyers, the price they met
    (previous_price), and the price their buying realized (price).
    Carrying the new price into F_t+1 is the transition's job
    (realized_price_transition).

    Required objective_state field:

        price

    Required parameter:

        price_sensitivity
    """
    buyers = list(actions.values()).count("buy")

    return RealityResult(
        system={
            "buyers": buyers,
            "previous_price": objective_state["price"],
            "price": objective_state["price"] * (
                1 + parameters["price_sensitivity"] * buyers
            ),
        },
    )


def realized_price_transition(objective_state, reality, parameters):
    """
    O_t -> F_t+1: the market price at the next decision point is the
    price this decision point realized, and the price before it becomes
    previous_price.
    """
    objective_state["previous_price"] = reality.system["previous_price"]
    objective_state["price"] = reality.system["price"]
    return objective_state


def remaining_liquidity_transition(objective_state, reality, parameters):
    """
    O_t -> F_t+1: the bank's liquidity at the next decision point is
    what this decision point's realized withdrawals left.
    """
    objective_state["liquidity"] = reality.system["remaining_liquidity"]
    return objective_state


def observe_own_outcome(agents, actions, reality, objective_state, parameters):
    """
    Each agent observes its own realized outcome O_i,t, exactly, and
    nothing else. Agents with no O_i,t observe nothing.
    """
    return {
        name: dict(reality.agent(name))
        for name in agents
        if name in reality.agents
    }


def observe_public_actions(agents, actions, reality, objective_state, parameters):
    """
    Every agent observes every action selected at this decision point,
    exactly -- the information structure of a sequential game with
    observed moves. Nothing about the outcome is observed.

    Observation data:

        actions   acting agent name -> selected action
    """
    return {
        name: {"actions": dict(actions)}
        for name in agents
    }


def observe_liquidity(agents, actions, reality, objective_state, parameters):
    """
    Every agent observes the bank's liquidity as it stands after this
    decision point's withdrawals (F_t+1), exactly.

    Observation data:

        liquidity
    """
    return {
        name: {"liquidity": objective_state["liquidity"]}
        for name in agents
    }


def observe_price(agents, actions, reality, objective_state, parameters):
    """
    Every agent observes the market price as it stands after this
    decision point (F_t+1), and the price before it, exactly.

    Observation data:

        previous_price
        price
    """
    return {
        name: {
            "previous_price": objective_state["previous_price"],
            "price": objective_state["price"],
        }
        for name in agents
    }


def price_growth_expectation_update(agent, observation):
    """
    Applied by one agent to what it observed: its expected appreciation becomes its own
    extrapolation weight times the observed price growth.

    feedback_strength is the agent's own belief (M) about how strongly
    observed growth carries forward -- not a TER primitive -- so two
    agents observing the same prices may still expect different things.

    Required model_of_reality field:

        feedback_strength

    Required observation fields:

        previous_price
        price
    """
    previous_price = observation["previous_price"]

    if previous_price == 0:
        growth = 0.0
    else:
        growth = (observation["price"] - previous_price) / previous_price

    model = agent.model_of_reality
    model["expected_appreciation"] = model["feedback_strength"] * growth

    return {"model_of_reality": model}


def liquidity_risk_update(agent, observation):
    """
    Applied by one depositor to what it observed: its perceived failure probability
    becomes the larger of its own independent risk signal and the
    shortfall of observed liquidity against the liquidity it regards as
    normal.

    Both inputs besides the observation are the depositor's own beliefs
    (M), so two depositors observing the same liquidity may still reach
    different conclusions.

    Required model_of_reality fields:

        risk_signal
        reference_liquidity

    Required observation field:

        liquidity
    """
    model = agent.model_of_reality

    liquidity_risk = max(
        0.0,
        min(1.0, 1 - observation["liquidity"] / model["reference_liquidity"]),
    )

    model["failure_probability"] = max(
        model.get("risk_signal", 0.0),
        liquidity_risk,
    )

    return {"model_of_reality": model}

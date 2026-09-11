from collections import Counter
from copy import deepcopy
from typing import Any

from research.ter.agent import AgentState
from research.ter.rules import get_rule
from research.ter.scenario import AgentSpec, Scenario, ScenarioResult
from research.ter.simulation import simulate
from research.ter.snapshot import snapshot_agents
from research.ter.system import run_system


def build_agent(spec: AgentSpec) -> AgentState:
    """
    Convert a declarative AgentSpec into an executable TER AgentState.
    """

    valuation_rule = get_rule(spec.valuation_rule)
    decision_process = get_rule(spec.decision_process)

    return AgentState(
        name=spec.name,
        objective=spec.objective,
        model_of_reality=deepcopy(spec.model_of_reality),
        actual_feasible_set=list(spec.actual_feasible_set),
        perceived_feasible_set=list(spec.perceived_feasible_set),
        value=valuation_rule,
        horizon=spec.horizon,
        decision_process=decision_process,
        valuation=deepcopy(spec.valuation),
        decision_parameters=deepcopy(spec.decision_parameters),
    )


def build_agents(specs: list[AgentSpec]) -> list[AgentState]:
    """
    Convert declarative AgentSpecs into executable TER AgentStates.

    Agent names must be unique within a scenario. Names are how a
    ScenarioResult is later addressed (see ScenarioResult.agent), so a
    silent collision would silently discard one agent's result.
    """

    counts = Counter(spec.name for spec in specs)
    duplicates = sorted(
        name
        for name, count in counts.items()
        if count > 1
    )

    if duplicates:
        raise ValueError(
            "Agent names must be unique within a scenario. "
            f"Duplicate name(s): {duplicates}"
        )

    return [
        build_agent(spec)
        for spec in specs
    ]


def run_scenario(scenario: Scenario) -> ScenarioResult:
    """
    Execute a declarative TER Scenario.

    Scenario defines:
        agents
        initial conditions
        parameters
        reality function
        feedback rule

    Shared TER code handles execution. Each period follows the same
    order:

        decision (C_t) -> reality (O_t) -> feedback -> next decision
        environment

    Initial beliefs belong in each agent's model_of_reality at
    construction time (M_0), not in a feedback rule -- feedback only
    ever updates the decision environment from an outcome that has
    already been realized, so it has nothing to act on before period 0.
    """

    agents = build_agents(scenario.agents)

    state: dict[str, Any] = deepcopy(
        scenario.initial_state
    )

    state["agents"] = agents
    state["agent_snapshots"] = snapshot_agents(
        agents,
        scenario.snapshot_fields,
    )

    reality_function = (
        get_rule(scenario.reality_function)
        if scenario.reality_function
        else None
    )

    feedback_rule = (
        get_rule(scenario.feedback_rule)
        if scenario.feedback_rule
        else None
    )

    def step(current_state, period):
        state = current_state

        # Decision (Model 5.1, Model 5.3):
        # every agent selects an action from the same, already-settled
        # decision environment -- nothing in this period's realization or
        # feedback has happened yet, so one agent's later outcome can
        # never leak backward into another agent's decision here.
        if reality_function:
            outcome_function = lambda agents, actions: reality_function(
                state=state,
                agents=agents,
                actions=actions,
                parameters=scenario.parameters,
            )
        else:
            outcome_function = lambda agents, actions: {}

        system_result = run_system(
            agents=state["agents"],
            outcome_function=outcome_function,
        )

        # Reality (Model 5.2, Model 5.3):
        # the reality function turns the full set of selected actions into
        # this period's realized outcome.
        outcome = system_result.outcome

        selected_action_by_agent = {
            agent.name: action
            for agent, action in zip(
                state["agents"],
                system_result.actions,
            )
        }

        next_state = dict(state)

        next_state["period"] = period + 1
        next_state["selected_action_by_agent"] = selected_action_by_agent
        next_state["agent_snapshots"] = snapshot_agents(
            state["agents"],
            scenario.snapshot_fields,
        )

        for key, value in outcome.items():
            next_state[key] = value

        # Feedback (Model 5.5):
        # only now, with a real realized outcome in hand, fold it into the
        # decision environment the next period will decide from. There is
        # no realized outcome before the first decision, so feedback never
        # runs ahead of it.
        if feedback_rule:
            next_state = feedback_rule(
                state=next_state,
                outcome=outcome,
                parameters=scenario.parameters,
            )

        return next_state

    history = simulate(
        initial_state=state,
        periods=scenario.periods,
        step_function=step,
    )

    return ScenarioResult(
        scenario=scenario,
        history=history,
    )
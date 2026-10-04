from collections import Counter
from copy import deepcopy
from dataclasses import replace

from research.ter.agent import AgentState
from research.ter.decision import select_action
from research.ter.immutable import FrozenDict, freeze, thaw
from research.ter.observation import UPDATABLE_FIELDS, Observation, update_view
from research.ter.reality import RealityResult
from research.ter.scenario import AgentSpec, Scenario, ScenarioResult
from research.ter.schedule import Schedule
from research.ter.trace import Trace, TraceStep, record_agents


def build_agent(spec: AgentSpec) -> AgentState:
    """
    Convert a declarative AgentSpec into an executable TER AgentState.
    """

    if not callable(spec.valuation_rule):
        raise TypeError("AgentSpec.valuation_rule must be callable.")

    if not callable(spec.decision_process):
        raise TypeError("AgentSpec.decision_process must be callable.")

    if spec.update_rule is not None and not callable(spec.update_rule):
        raise TypeError("AgentSpec.update_rule must be callable or None.")

    return AgentState(
        name=spec.name,
        objective=spec.objective,
        model_of_reality=deepcopy(spec.model_of_reality),
        perceived_feasible_set=list(spec.perceived_feasible_set),
        value=spec.valuation_rule,
        horizon=spec.horizon,
        decision_process=spec.decision_process,
        valuation=deepcopy(spec.valuation),
        decision_parameters=deepcopy(spec.decision_parameters),
        update=spec.update_rule,
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


def frozen_agent(agent: AgentState) -> AgentState:
    return replace(
        agent,
        objective=freeze(agent.objective),
        model_of_reality=freeze(agent.model_of_reality),
        perceived_feasible_set=freeze(agent.perceived_feasible_set),
        horizon=freeze(agent.horizon),
        valuation=freeze(agent.valuation),
        decision_parameters=freeze(agent.decision_parameters),
    )


def run_scenario(scenario: Scenario) -> ScenarioResult:
    """
    Execute a declarative TER Scenario, one decision point at a time.

    Scenario defines the agents, F_0 (initial_state), parameters, and
    the rules below; this shared code handles execution. At each
    decision point t:

        1. actors     = schedule.actors_at(t)
        2. C_i,t      = D_i(F_hat_i, M_i, V_i(. | G_i, M_i, H_i))
                        for each actor, all from the same settled
                        conditions (Model 5.1). Inactive agents do not
                        decide and contribute no action.
        3. O          = R(actions, F_t, parameters) -> RealityResult
                        (Model 5.2 / 5.3). R sees F_t frozen, never M,
                        F_hat, or V.
        4. F_t+1      = transition(F_t, O, parameters)   (Model 5.5,
                        O_t -> F_t+1). Without a transition, F carries
                        forward unchanged.
        5. observations = observation(agents, actions, O, F_t+1,
                        parameters): what each agent receives. Without
                        an observation rule, no agent learns anything.
        6. each agent with an Observation and an update_rule gets new
           agent-side components from update_rule(UpdateView,
           Observation) (Model 5.5, O_t -> (G, M, F_hat, V, H)_t+1).
           This is the only way an agent's state changes.
        7. the step is appended to the immutable Trace.

    Nothing in steps 3-6 can reach back into step 2 of the same
    decision point: every actor has already selected before R runs.

    Initial beliefs belong in each agent's model_of_reality at
    construction time (M_0), not in an update rule -- an update only
    ever follows an observed, already-realized outcome, so it has
    nothing to act on before the first decision.
    """
    agents = {
        agent.name: agent
        for agent in build_agents(scenario.agents)
    }
    agent_names = tuple(agents)

    schedule = scenario.schedule or Schedule.simultaneous()

    if not isinstance(schedule, Schedule):
        raise TypeError("Scenario.schedule must be a Schedule.")

    schedule.validate(agent_names)

    for name in ("reality", "transition", "observation"):
        rule = getattr(scenario, name)
        if rule is not None and not callable(rule):
            raise TypeError(f"Scenario.{name} must be callable or None.")

    reality = scenario.reality
    transition = scenario.transition
    observation = scenario.observation

    parameters = freeze(scenario.parameters)

    def realize(actions, objective_state) -> RealityResult:
        if reality is None:
            return RealityResult()

        result = reality(
            actions=freeze(dict(actions)),
            objective_state=freeze(objective_state),
            parameters=parameters,
        )

        if not isinstance(result, RealityResult):
            raise TypeError(
                f"Reality rule {scenario.reality!r} returned "
                f"{type(result).__name__}, not RealityResult."
            )

        unknown = sorted(set(result.agents) - set(agent_names))

        if unknown:
            raise ValueError(
                f"Reality rule {scenario.reality!r} reported outcomes "
                f"for unknown agent(s): {unknown}"
            )

        return result

    def advance(objective_state, result):
        if transition is None:
            return objective_state

        next_state = transition(
            objective_state=thaw(objective_state),
            reality=result,
            parameters=parameters,
        )

        if not isinstance(next_state, dict):
            raise TypeError(
                f"Transition rule {scenario.transition!r} must return the "
                "next objective state as a dict."
            )

        return freeze(next_state)

    def observe(actions, result, objective_state):
        if observation is None:
            return FrozenDict()

        received = observation(
            agents=agent_names,
            actions=freeze(dict(actions)),
            reality=result,
            objective_state=objective_state,
            parameters=parameters,
        )

        unknown = sorted(set(received) - set(agent_names))

        if unknown:
            raise ValueError(
                f"Observation rule {scenario.observation!r} addressed "
                f"unknown agent(s): {unknown}"
            )

        return FrozenDict(
            (name, Observation(data=data))
            for name, data in received.items()
        )

    def apply_update(agent: AgentState, observed: Observation) -> AgentState:
        changes = agent.update(update_view(agent), observed)

        if not isinstance(changes, dict):
            raise TypeError(
                f"Update rule for {agent.name!r} must return a dict of "
                "changed agent-side components."
            )

        disallowed = sorted(set(changes) - UPDATABLE_FIELDS)

        if disallowed:
            raise ValueError(
                f"Update rule for {agent.name!r} tried to change "
                f"{disallowed}; it may only change "
                f"{sorted(UPDATABLE_FIELDS)}."
            )

        return replace(
            agent,
            **{
                name: thaw(value)
                for name, value in changes.items()
            },
        )

    initial_objective_state = freeze(scenario.initial_state)
    initial_agents = record_agents(agents)

    objective_state = initial_objective_state
    steps = []

    for step in range(scenario.periods):
        actors = schedule.actors_at(step, agent_names)

        # Each actor decides from a frozen copy of its own state, so D
        # cannot change M or F_hat in place: after construction, an
        # agent's state changes only through its update rule.
        actions = FrozenDict(
            (name, freeze(select_action(frozen_agent(agents[name]))))
            for name in actors
        )

        result = realize(actions, objective_state)
        next_objective_state = advance(objective_state, result)
        observations = observe(actions, result, next_objective_state)

        for name, observed in observations.items():
            if agents[name].update is not None:
                agents[name] = apply_update(agents[name], observed)

        steps.append(
            TraceStep(
                step=step,
                actions=actions,
                reality=result,
                observations=observations,
                objective_state=next_objective_state,
                agents=record_agents(agents),
            )
        )

        objective_state = next_objective_state

    trace = Trace(
        initial_objective_state=initial_objective_state,
        initial_agents=initial_agents,
        steps=tuple(steps),
    )

    return ScenarioResult(
        scenario=scenario,
        trace=trace,
        agent_states=agents,
        realize=realize,
    )

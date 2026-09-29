from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field, fields
from typing import Any, Callable


@dataclass
class AgentSpec:
    """
    Declarative definition of a TER agent.

    TER mapping:
    G     -> objective
    M     -> model_of_reality
    F_hat -> perceived_feasible_set
    V     -> valuation + valuation_rule
    H     -> horizon
    D     -> decision_process

    decision_parameters is not a new TER primitive. It is implementation
    configuration for the existing decision process D (e.g. a search
    depth), kept separate from model_of_reality so decision-process
    configuration is never mistaken for the agent's beliefs about
    reality.

    update_rule names how this agent turns an Observation into changed
    agent-side components (M, F_hat, G, V data, H, decision_parameters)
    between decision points -- the agent-side half of Model 5.5.
    valuation_rule, decision_process, and update_rule are each a
    registered rule name, a public enum member, or a plain callable.

    F_t, the objective feasible state of reality, is not declared here.
    It is not agent specific: it belongs to the Scenario (see
    Scenario.initial_state and Scenario.parameters).
    """

    name: str
    objective: Any
    model_of_reality: dict[str, Any]
    perceived_feasible_set: list[Any]
    valuation_rule: "RuleRef"
    decision_process: "RuleRef"
    horizon: Any = None
    valuation: dict[str, Any] = field(default_factory=dict)
    decision_parameters: dict[str, Any] = field(default_factory=dict)
    update_rule: "RuleRef | None" = None

    def variant(
        self,
        *,
        model_of_reality: dict[str, Any] | None = None,
        valuation: dict[str, Any] | None = None,
        **overrides,
    ) -> "AgentSpec":
        """
        Create a modified copy of this agent specification.
        """
        agent = deepcopy(self)

        if model_of_reality:
            agent.model_of_reality.update(model_of_reality)

        if valuation:
            agent.valuation.update(valuation)

        for key, value in overrides.items():
            setattr(agent, key, value)

        return agent


class AgentGroup(list):
    """
    A small research convenience for declaring several structurally
    identical agents that share one model_of_reality/valuation override,
    with sequential numbered names -- e.g. "seller_1", "seller_2",
    "seller_3".

    AgentGroup is not a TER primitive. It does not change TER behavior,
    execution, or theory. It is sugar for calling AgentSpec.variant() once
    per agent; the overrides are merged using AgentSpec.variant()'s
    existing behavior, unchanged. Every item produced is an ordinary
    AgentSpec.

    AgentGroup is a plain list, so it works anywhere a list of AgentSpec
    works (e.g. Scenario(agents=...)), and two groups combine with the
    normal `+` operator into a plain list.

    Name collisions across groups (e.g. two groups reusing the same
    name_prefix and index range) are not checked here. They are still
    caught where they always were: research.ter.runner.build_agents
    validates that every agent name is unique within a scenario.
    """

    def __init__(
        self,
        *,
        base: AgentSpec,
        count: int,
        name_prefix: str,
        model_of_reality: dict[str, Any] | None = None,
        valuation: dict[str, Any] | None = None,
        start_index: int = 1,
    ):
        if count < 1:
            raise ValueError("AgentGroup count must be at least 1.")

        super().__init__(
            base.variant(
                name=f"{name_prefix}_{index}",
                model_of_reality=model_of_reality,
                valuation=valuation,
            )
            for index in range(start_index, start_index + count)
        )


@dataclass
class Scenario:
    """
    Declarative TER experiment.

    A Scenario describes WHAT is being modeled.
    Shared TER execution code determines HOW it runs.
    """

    name: str
    description: str
    periods: int
    initial_state: dict[str, Any]
    agents: list[AgentSpec]

    parameters: dict[str, Any] = field(
        default_factory=dict
    )

    # The rules that govern execution (research.ter.runner.run_scenario).
    # Each is a registered rule name, a public enum member, or a plain
    # callable:
    #
    #   reality      R:  (actions, objective_state, parameters)
    #                    -> RealityResult          realizes O, nothing else
    #   transition       (objective_state, reality, parameters)
    #                    -> objective_state         F_t -> F_t+1
    #   observation      (agents, actions, reality, objective_state,
    #                     parameters) -> {name: data}
    #                                               what each agent learns
    #   schedule     Schedule; which agents act at each decision point.
    #                Defaults to Schedule.simultaneous().
    #
    # initial_state is F_0 and nothing else: no agents, no bookkeeping.
    # F_t is carried by the objective state (initial_state, advanced only
    # by the transition) and parameters (fixed conditions). The actions
    # F_t permits for each agent may be indexed in
    # objective_state["permitted_actions"] (agent name -> permitted
    # actions); see research.ter.outcome. Agents change only through
    # their own update_rule, applied to the Observation they receive.
    reality: "RuleRef | None" = None
    transition: "RuleRef | None" = None
    observation: "RuleRef | None" = None
    schedule: Any = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def variant(
        self,
        *,
        parameters: dict[str, Any] | None = None,
        initial_state: dict[str, Any] | None = None,
        agents: list[AgentSpec] | None = None,
        **overrides,
    ) -> "Scenario":
        """
        Create a modified copy of this scenario.

        Example:

            stronger = BASE_SCENARIO.variant(
                parameters={
                    "feedback_strength": 1.5,
                }
            )
        """
        scenario = deepcopy(self)

        if parameters:
            scenario.parameters.update(parameters)

        if initial_state:
            scenario.initial_state.update(initial_state)

        if agents is not None:
            scenario.agents = deepcopy(agents)

        for key, value in overrides.items():
            if key not in SCENARIO_FIELDS:
                raise TypeError(f"Scenario has no field {key!r}.")

            setattr(scenario, key, value)

        return scenario


@dataclass
class AgentResult:
    """
    Friendly, named access to one agent's final state and outcome data.

    `selected_action` is always available, for every Scenario, whether or
    not it defines a reality rule: it is the action the agent's own
    decision process selected at its last decision point, not something
    any reality rule needs to report (None if the agent never acted).

    Common state attributes are available directly, e.g. `firm.objective`,
    `firm.perceived_feasible_set`, `firm.model_of_reality`. The full AgentState remains available as
    `.state` for advanced use; normal tests should not need it.

    Attribute lookup precedence:

        1. per-agent outcome fields (e.g. `.social_value`) -- O_i,t, as
           the scenario's reality rule reported it in
           RealityResult.agents for this agent's name.
        2. AgentState's own fields (`.objective`,
           `.perceived_feasible_set`, `.model_of_reality`, `.horizon`,
           `.name`, etc).
        3. AgentState.model_of_reality fields -- an agent's own declared
           economic facts and beliefs, e.g.
           `agent.model_of_reality["failure_probability"]` becomes
           `result.agent(name).failure_probability`. This is a
           read-through only: model_of_reality data is never copied or
           moved, and looking it up this way changes nothing about how
           it was computed or stored.
        4. AttributeError if none of the above has the key.

    `outcome_for(action)` gives this agent's outcome for an alternative
    action by re-running R once, deterministically, at the agent's last
    decision point with only this agent's action replaced (see
    ScenarioResult.counterfactual) -- other agents' actions and F_t stay
    exactly as recorded, and nothing downstream (transition,
    observation, later decisions) is re-run.
    """

    state: Any
    outcome: Mapping[str, Any]
    selected_action: Any = None
    rerun_reality: Callable[[Any], Mapping[str, Any]] | None = None

    def __getattr__(self, key: str) -> Any:
        if key in self.outcome:
            return self.outcome[key]

        if hasattr(self.state, key):
            return getattr(self.state, key)

        if key in self.state.model_of_reality:
            return self.state.model_of_reality[key]

        raise AttributeError(
            f"AgentResult for {self.state.name!r} has no {key!r}. "
            f"Available outcome fields: {sorted(self.outcome)}"
        )

    def value_of(self, action: Any) -> float:
        """
        The agent's own final valuation (V) of an action, using the same
        value function the agent's decision process used to select among
        F_hat. This calls the agent's value function directly; it is not
        reality data and does not require a reality rule.
        """
        return self.state.value(action, self.state)

    def outcome_for(self, action: Any) -> "AgentResult":
        """
        This agent's counterfactual outcome for an alternative action: a
        deterministic re-run of R (see the class docstring). It is not
        another realized outcome.
        """
        if self.rerun_reality is None:
            raise ValueError(
                f"Agent {self.state.name!r} never acted, so there is no "
                "decision point at which to re-run R."
            )

        return AgentResult(
            state=self.state,
            outcome=self.rerun_reality(action),
            selected_action=self.selected_action,
            rerun_reality=self.rerun_reality,
        )


@dataclass
class ScenarioResult:
    """
    Result returned after executing a Scenario.

    trace is the immutable record of every decision point
    (research.ter.trace.Trace), and history is the sequence of objective
    states [F_0, F_1, ..., F_T] -- so initial and final are F_0 and F_T.
    Realized outcomes live on trace steps, not in history.

    agent_states holds each agent's final, executable AgentState;
    realize is the run's own R binding, used only to re-run R for
    counterfactuals.
    """

    scenario: Scenario
    history: list[Any]
    trace: Any
    agent_states: dict[str, Any]
    realize: Callable[..., Any] = field(repr=False)

    @property
    def initial(self):
        return self.history[0]

    @property
    def final(self):
        return self.history[-1]

    def counterfactual(self, step: int, actions: dict[str, Any]):
        """
        Re-run R at decision point `step` with some actors' actions
        replaced, and return the RealityResult that would have been
        realized.

        Everything else is held exactly as recorded: F_t (the objective
        state those actions met), the other actors' actions, and the
        scenario parameters. Only R runs -- no transition, observation,
        or later decision -- so this answers "what would reality have
        made of this action here", not "how would the run have unfolded".

        Before substituting anything, R is re-run on the recorded
        actions and must reproduce the recorded RealityResult exactly. A
        mismatch means R is not a deterministic function of (actions,
        F_t, parameters), and a counterfactual comparison against it
        would be meaningless, so this raises instead.

        Only agents that acted at `step` can be given a different
        action: an inactive agent contributed no action to R there.
        """
        recorded = self.trace[step]

        inactive = sorted(set(actions) - set(recorded.actors))

        if inactive:
            raise ValueError(
                f"Agent(s) {inactive} did not act at step {step}; only "
                f"{list(recorded.actors)} did."
            )

        objective_state = self.trace.objective_state_before(step)

        if self.realize(recorded.actions, objective_state) != recorded.reality:
            raise RuntimeError(
                f"Re-running R on the recorded actions at step {step} did "
                "not reproduce the recorded RealityResult: R is not "
                "deterministic in (actions, objective_state, parameters), "
                "so a counterfactual against it is not meaningful."
            )

        substituted = {
            **recorded.actions,
            **actions,
        }

        return self.realize(substituted, objective_state)

    def agent(self, name: str) -> "AgentResult":
        """
        Look up one agent's final state and outcome data by name, instead
        of by position in the agents list.

        selected_action and outcome come from the last decision point at
        which this agent acted (None and {} if it never did).
        """
        if name not in self.agent_states:
            raise ValueError(
                f"No agent named {name!r} in this scenario's result."
            )

        step = self.trace.last_action_step(name)

        if step is None:
            return AgentResult(
                state=self.agent_states[name],
                outcome={},
            )

        def rerun_reality(action):
            return self.counterfactual(step.step, {name: action}).agent(name)

        return AgentResult(
            state=self.agent_states[name],
            outcome=step.reality.agent(name),
            selected_action=step.actions[name],
            rerun_reality=rerun_reality,
        )


RuleRef = str | Callable[..., Any]

SCENARIO_FIELDS = frozenset(
    scenario_field.name
    for scenario_field in fields(Scenario)
)

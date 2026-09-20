from copy import deepcopy
from dataclasses import dataclass, field
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

    F_t, the objective feasible state of reality, is not declared here.
    It is not agent specific: it belongs to the Scenario (see
    Scenario.initial_state and Scenario.parameters).
    """

    name: str
    objective: Any
    model_of_reality: dict[str, Any]
    perceived_feasible_set: list[Any]
    valuation_rule: str
    decision_process: str
    horizon: Any = None
    valuation: dict[str, Any] = field(default_factory=dict)
    decision_parameters: dict[str, Any] = field(default_factory=dict)

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

    # reality_function implements R: O_t = R(C_1,t, ..., C_n,t, F_t). It
    # determines the realized outcome from the selected actions and the
    # objective feasible state of reality; it is not the outcome itself.
    # F_t is carried by the scenario's `state` (initial_state, which
    # evolves) and `parameters` (fixed conditions). The actions F_t
    # permits for each agent are indexed in state["permitted_actions"]
    # (agent name -> permitted actions); see research.ter.outcome.
    reality_function: str | None = None
    feedback_rule: str | None = None

    # AgentState attribute names to capture into an independent
    # AgentSnapshot for every agent, every period (see
    # research/ter/snapshot.py). ScenarioResult.history[t]["agents"]
    # holds live, mutable AgentState objects shared across every period
    # -- necessary so feedback can affect later decisions, but unsafe to
    # read as historical state once a later period has mutated them.
    # snapshot_fields is the opt-in way to capture specific fields (e.g.
    # "model_of_reality", "perceived_feasible_set") independently of that
    # live state, under
    # history[t]["agent_snapshots"][agent_name]. Empty by default: no
    # snapshots are taken unless requested.
    snapshot_fields: list[str] = field(
        default_factory=list
    )

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
            setattr(scenario, key, value)

        return scenario


@dataclass
class AgentResult:
    """
    Friendly, named access to one agent's final state and outcome data.

    `selected_action` is always available, for every Scenario, whether or
    not it defines a reality_function: it is the action the agent's own
    decision process selected during scenario execution, not something
    any reality_function needs to report.

    Common state attributes are available directly, e.g. `firm.objective`,
    `firm.perceived_feasible_set`, `firm.model_of_reality`. The full AgentState remains available as
    `.state` for advanced use; normal tests should not need it.

    Attribute lookup precedence:

        1. per-agent outcome fields (e.g. `.social_value`) -- the data the
           scenario's reality_function reported under "agent_results"
           for this agent's name.
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

    `outcome_for(action)` looks up this agent's outcome for an
    alternative action, from data the reality_function already computed
    during scenario execution (reported under "alternative_outcomes").
    It is a lookup only: AgentResult never executes a rule itself.
    """

    state: Any
    outcome: dict[str, Any]
    selected_action: Any = None
    alternatives: dict[Any, dict[str, Any]] = field(default_factory=dict)

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
        reality_function data and does not require one.
        """
        return self.state.value(action, self.state)

    def outcome_for(self, action: Any) -> "AgentResult":
        """
        Look up this agent's precomputed outcome for an alternative
        action. The reality_function must have reported it under
        "alternative_outcomes" during scenario execution; this does not
        compute anything new.
        """
        if action not in self.alternatives:
            raise ValueError(
                f"No precomputed outcome for action {action!r} on agent "
                f"{self.state.name!r}. Available: "
                f"{sorted(self.alternatives, key=str)}"
            )

        return AgentResult(
            state=self.state,
            outcome=self.alternatives[action],
            selected_action=self.selected_action,
            alternatives=self.alternatives,
        )


@dataclass
class ScenarioResult:
    """
    Result returned after executing a Scenario.
    """

    scenario: Scenario
    history: list[Any]

    @property
    def initial(self):
        return self.history[0]

    @property
    def final(self):
        return self.history[-1]

    def agent(self, name: str) -> "AgentResult":
        """
        Look up one agent's final state and outcome data by name, instead
        of by position in the agents list.
        """
        for state in self.final["agents"]:
            if state.name == name:
                return AgentResult(
                    state=state,
                    outcome=self.final.get("agent_results", {}).get(name, {}),
                    selected_action=self.final.get(
                        "selected_action_by_agent", {}
                    ).get(name),
                    alternatives=self.final.get(
                        "alternative_outcomes", {}
                    ).get(name, {}),
                )

        raise ValueError(
            f"No agent named {name!r} in this scenario's result."
        )


RuleFunction = Callable[..., Any]

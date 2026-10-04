from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from research.ter.agent import AgentState
from research.ter.immutable import FrozenDict, freeze
from research.ter.observation import Observation
from research.ter.reality import RealityResult


@dataclass(frozen=True)
class AgentRecord:
    """
    One agent's decision-relevant state at one point in a run, frozen.

    Unlike a live AgentState, nothing later in the run can change an
    AgentRecord: every field is a deep, immutable copy taken when the
    record was made.
    """

    name: str
    objective: Any
    model_of_reality: Any
    perceived_feasible_set: Any
    horizon: Any
    valuation: Any
    decision_parameters: Any

    @classmethod
    def of(cls, agent: AgentState) -> "AgentRecord":
        return cls(
            name=agent.name,
            objective=freeze(agent.objective),
            model_of_reality=freeze(agent.model_of_reality),
            perceived_feasible_set=freeze(agent.perceived_feasible_set),
            horizon=freeze(agent.horizon),
            valuation=freeze(agent.valuation),
            decision_parameters=freeze(agent.decision_parameters),
        )


@dataclass(frozen=True)
class TraceStep:
    """
    Everything that happened at one decision point, in the order it
    happened:

        step            t
        actions         C_i,t for each actor, keyed by agent name; its
                        ordered keys are the actors at t
        reality         the RealityResult R realized from those actions
                        and F_t
        observations    what each agent received about it, keyed by
                        agent name (absent: that agent received nothing)
        objective_state F_t+1, the objective state after the transition
        agents          each agent's state after its observation, if
                        any, was taken into account

    F_t itself -- the state these actions were realized against -- is
    the previous step's objective_state (or the trace's initial one);
    see Trace.objective_state_before.
    """

    step: int
    actions: Mapping[str, Any]
    reality: RealityResult
    observations: Mapping[str, Observation]
    objective_state: Mapping[str, Any]
    agents: Mapping[str, AgentRecord]

    @property
    def actors(self) -> tuple[str, ...]:
        return tuple(self.actions)

    def acted(self, name: str) -> bool:
        return name in self.actions


@dataclass(frozen=True)
class Trace:
    """
    The immutable record of a run: the initial conditions and
    one TraceStep per decision point.
    """

    initial_objective_state: Mapping[str, Any]
    initial_agents: Mapping[str, AgentRecord]
    steps: tuple[TraceStep, ...]

    def __len__(self) -> int:
        return len(self.steps)

    def __getitem__(self, step: int) -> TraceStep:
        return self.steps[step]

    def __iter__(self):
        return iter(self.steps)

    @property
    def initial(self) -> Mapping[str, Any]:
        return self.initial_objective_state

    @property
    def final(self) -> Mapping[str, Any]:
        if not self.steps:
            return self.initial_objective_state

        return self.steps[-1].objective_state

    @property
    def history(self) -> tuple[Mapping[str, Any], ...]:
        return (self.initial_objective_state,) + tuple(
            step.objective_state
            for step in self.steps
        )

    def objective_state_before(self, step: int) -> Mapping[str, Any]:
        """
        F_t for decision point `step`: the objective state the actions
        selected there were realized against.
        """
        if step == 0:
            return self.initial_objective_state

        return self.steps[step - 1].objective_state

    def agents_before(self, step: int) -> Mapping[str, AgentRecord]:
        """
        Each agent's state as it stood when decision point `step`'s
        actors selected their actions.
        """
        if step == 0:
            return self.initial_agents

        return self.steps[step - 1].agents

    def last_action_step(self, name: str) -> TraceStep | None:
        """
        The most recent decision point at which this agent acted, or
        None if it never did.
        """
        for step in reversed(self.steps):
            if step.acted(name):
                return step

        return None


def record_agents(agents: Mapping[str, AgentState]) -> FrozenDict:
    return FrozenDict(
        (name, AgentRecord.of(agent))
        for name, agent in agents.items()
    )

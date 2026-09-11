from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from research.ter.agent import AgentState


@dataclass(frozen=True)
class AgentSnapshot:
    """
    An independent capture of a subset of one agent's state at one point
    in time.

    Unlike AgentState, whose mutable fields (model_of_reality,
    actual_feasible_set, perceived_feasible_set) may be mutated in place
    by feedback rules in later periods, an AgentSnapshot's captured
    values are copies taken
    at capture time: later mutation of the live AgentState a snapshot
    was taken from can never retroactively change that snapshot.

    fields holds exactly the AgentState attribute names requested at
    capture time -- nothing else. A snapshot taken with an empty field
    selection carries no captured state at all (see snapshot_agents).
    """

    fields: dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.fields[name]
        except KeyError:
            raise AttributeError(
                f"AgentSnapshot has no captured field {name!r}. "
                f"Captured fields: {sorted(self.fields)}"
            ) from None


def snapshot_agent(agent: AgentState, fields: list[str]) -> AgentSnapshot:
    """
    Capture the named AgentState attributes for one agent.

    Each captured value is deep-copied, so the snapshot is independent
    of the live agent from this point on: appending to a captured list,
    or mutating a captured dict, on the live AgentState cannot alter
    what was already captured here.
    """
    return AgentSnapshot(
        fields={
            name: deepcopy(getattr(agent, name))
            for name in fields
        }
    )


def snapshot_agents(
    agents: list[AgentState],
    fields: list[str],
) -> dict[str, AgentSnapshot]:
    """
    Capture the named AgentState attributes for every agent, keyed by
    agent name -- the same convention selected_action_by_agent,
    agent_results, and alternative_outcomes already use elsewhere in TER
    Core.

    An empty field selection captures nothing: this returns an empty
    dict, not one empty-record snapshot per agent. No per-agent state is
    stored, and no deep copying is done, when no fields are requested.
    """
    if not fields:
        return {}

    return {
        agent.name: snapshot_agent(agent, fields)
        for agent in agents
    }

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from research.ter.immutable import FrozenDict, freeze


@dataclass(frozen=True)
class RealityResult:
    """
    What R realizes at one decision point: the realized outcome O, and
    nothing else.

        O_t   = R(C_1,t, ..., C_n,t, F_t)     (Model 5.3)
        O_i,t = R(C_i,t, F_t)                 (Model 5.2)

    system   O_t, the system outcome of explicitly modeled interacting
             actions. Empty in an agent-level specification, where no
             O_t is defined.
    agents   O_i,t per agent, keyed by agent name. Where an agent's
             outcome depends on the modeled interaction it comes from
             this same joint realization, never from a separate
             single-agent application of R (Model 5.3, "Agent-level
             outcomes"). An agent that did not act may still have an
             outcome here (e.g. an incumbent affected by an entrant's
             move).

    TER does not define O_t as an aggregation of the O_i,t, so neither
    field is derived from the other.

    RealityResult is O, not F_{t+1}: how the outcome changes the
    objective state is the scenario's transition, and what agents learn
    from it is the scenario's observation rule. Both contents are frozen
    at construction, so a realized outcome cannot be rewritten later --
    not by a transition, an observation rule, or a test.
    """

    system: Mapping[str, Any] = field(default_factory=FrozenDict)
    agents: Mapping[str, Mapping[str, Any]] = field(default_factory=FrozenDict)

    def __post_init__(self):
        if not isinstance(self.system, Mapping):
            raise TypeError("RealityResult.system must be a mapping.")

        if not isinstance(self.agents, Mapping) or not all(
            isinstance(outcome, Mapping)
            for outcome in self.agents.values()
        ):
            raise TypeError(
                "RealityResult.agents must map agent names to outcome "
                "mappings."
            )

        object.__setattr__(self, "system", freeze(dict(self.system)))
        object.__setattr__(
            self,
            "agents",
            freeze({
                name: dict(outcome)
                for name, outcome in self.agents.items()
            }),
        )

    def agent(self, name: str) -> Mapping[str, Any]:
        """
        O_i,t for one agent, or an empty mapping if R reported none.
        """
        return self.agents.get(name, FrozenDict())

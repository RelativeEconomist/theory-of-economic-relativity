from dataclasses import dataclass


@dataclass(frozen=True)
class Schedule:
    """
    Which agents act at each decision point.

    Model 5.3 lets a specification represent agents that act together or
    at different decision points, including an agent that does not act at
    a point. The current scenarios need two explicit choices:

        Schedule.simultaneous()       every agent, every point
        Schedule.sequential("a", "b") a at t=0, b at t=1, then repeat

    Sequential schedules cycle, so Scenario.periods may cover several
    rounds. Repeating a name in the order expresses unequal move frequency.

    An agent not scheduled at t is inactive there: its D is not called,
    it contributes no action to R, and it is absent from that trace
    step's actors. Its state carries forward unchanged unless an
    observation reaches it.

    Every agent scheduled at the same point selects its action from the
    same, already-settled conditions; none sees another's action from
    that point. Information from an earlier point reaches a later
    decision only through observation (research.ter.observation).
    """

    order: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if self.order == ():
            raise ValueError("A sequential schedule needs at least one agent.")

    @classmethod
    def simultaneous(cls) -> "Schedule":
        return cls(order=None)

    @classmethod
    def sequential(cls, *order: str) -> "Schedule":
        if not order:
            raise ValueError("A sequential schedule needs at least one agent.")

        return cls(order=tuple(order))

    def validate(self, agent_names: tuple[str, ...]) -> None:
        """
        Every scheduled name must be an agent of the scenario.
        """
        if self.order is None:
            return

        unknown = sorted(set(self.order) - set(agent_names))

        if unknown:
            raise ValueError(
                f"Schedule names agent(s) not in the scenario: {unknown}"
            )

    def actors_at(
        self,
        step: int,
        agent_names: tuple[str, ...],
    ) -> tuple[str, ...]:
        """
        The agents that act at decision point `step`, in the order their
        actions are handed to R.
        """
        if self.order is None:
            return tuple(agent_names)

        return (self.order[step % len(self.order)],)

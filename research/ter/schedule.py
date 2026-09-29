from dataclasses import dataclass


@dataclass(frozen=True)
class Schedule:
    """
    Which agents act at each decision point.

    Model 5.3 allows contemporaneous, sequential, staged, or repeated
    interaction, and lets a specification represent an agent that does
    not act at a decision point by omitting its action. A Schedule is
    that choice, made explicit:

        Schedule.simultaneous()               every agent, every point
        Schedule.sequential("a", "b")         a at t=0, b at t=1, ...
        Schedule.staged(("a", "b"), ("c",))   a and b together, then c

    Sequential and staged schedules cycle: decision point t uses stage
    t % len(stages), so Scenario.periods may cover several rounds.

    An agent not scheduled at t is inactive there: its D is not called,
    it contributes no action to R, and it is absent from that trace
    step's actors. Its state carries forward unchanged unless an
    observation reaches it.

    Every agent scheduled at the same point selects its action from the
    same, already-settled conditions; none sees another's action from
    that point. Information from an earlier point reaches a later
    decision only through observation (research.ter.observation).
    """

    stages: tuple[tuple[str, ...], ...] | None = None

    @classmethod
    def simultaneous(cls) -> "Schedule":
        return cls(stages=None)

    @classmethod
    def sequential(cls, *order: str) -> "Schedule":
        return cls.staged(*((name,) for name in order))

    @classmethod
    def staged(cls, *stages) -> "Schedule":
        normalized = tuple(tuple(stage) for stage in stages)

        if not normalized:
            raise ValueError("A staged schedule needs at least one stage.")

        for stage in normalized:
            if not stage:
                raise ValueError("A schedule stage cannot be empty.")

            if len(set(stage)) != len(stage):
                raise ValueError(
                    f"An agent appears more than once in stage {stage}."
                )

        return cls(stages=normalized)

    def validate(self, agent_names: tuple[str, ...]) -> None:
        """
        Every scheduled name must be an agent of the scenario.
        """
        if self.stages is None:
            return

        unknown = sorted(
            {
                name
                for stage in self.stages
                for name in stage
            }
            - set(agent_names)
        )

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
        if self.stages is None:
            return tuple(agent_names)

        return self.stages[step % len(self.stages)]

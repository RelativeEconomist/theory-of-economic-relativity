"""
Framework test: feedback ordering contract

Canonical TER: theory/academic.md, Models 5.1, 5.2 and 5.5

Purpose
-------
Verifies the execution ordering inside the engine
(research/ter/runner.py::run_scenario):

    decision -> realized outcome -> observation -> update -> later decision

Each period's update rule runs only after that period's own decision and
reality rule have produced a realized outcome (O_{i,t}, single agent) and
the agent has observed it, and it changes only the conditions seen by the
*following* period's decision -- never the period the outcome was
computed from, and never before the first decision (there is no realized
outcome yet to observe). The local update rule below requires and reads
that observed outcome directly, and does not read the selected action, so
if an update ever ran before reality had produced an outcome this test
would raise instead of silently passing.

The bank run (test_09) and speculative bubble (test_10) replication tests
demonstrate feedback producing particular economic outcomes across
multiple periods. This test isolates the ordering guarantee itself, using
minimal local rules scoped to this file only.

Out of scope
------------
F_t. The local update rule changes an agent-side model_of_reality field
only; no transition is declared.
"""

import unittest

from research.ter import (
    AgentSpec,
    RealityResult,
    Scenario,
    run_scenario,
)
from research.ter.rules import mapped_value, observe_own_outcome


LOW = "low"
HIGH = "high"


def record_realized_action(actions, objective_state, parameters):
    """
    Local Model 5.2 reality rule for this test only.

    Realizes O_{i,t} as simply the action each agent selected -- this
    contract needs nothing more elaborate than "the agent's selected
    action was realized."
    """
    return RealityResult(
        agents={
            name: {"realized_action": action}
            for name, action in actions.items()
        },
    )


def record_feedback_flag(agent, observation):
    """
    Local Model 5.5 update rule for this test only. Sets a
    model_of_reality field the agent's *next* decision can observe, only
    once the agent has observed that its realized action was LOW. It
    reads the observed outcome, not the selected action.

    Reading observation["realized_action"] directly (no default) is
    deliberate: if an update ever ran without a realized outcome having
    been observed, this would raise instead of silently succeeding.
    """
    if observation["realized_action"] != LOW:
        return {}

    model = agent.model_of_reality
    model["flag_set_by_feedback"] = True

    return {"model_of_reality": model}


def choose_by_flag(agent):
    """
    Local Model 5.1 decision rule for this test only. Selects HIGH if a
    prior period's update is visible when the decision runs, otherwise
    LOW.
    """
    if agent.model_of_reality.get("flag_set_by_feedback"):
        return HIGH

    return LOW


AGENT = AgentSpec(
    name="agent",
    objective="test objective",
    model_of_reality={},
    perceived_feasible_set=[LOW, HIGH],
    valuation_rule=mapped_value,
    decision_process=choose_by_flag,
    horizon="current decision",
    update_rule=record_feedback_flag,
)


ONE_PERIOD_SCENARIO = Scenario(
    name="Feedback Ordering Contract (one period)",
    description=(
        "A minimal single-agent, single-period scenario isolating "
        "whether an update can run before the first decision."
    ),
    periods=1,
    initial_state={},
    agents=[
        AGENT,
    ],
    reality=record_realized_action,
    observation=observe_own_outcome,
)

TWO_PERIOD_SCENARIO = ONE_PERIOD_SCENARIO.variant(
    name="Feedback Ordering Contract (two periods)",
    description=(
        "A minimal single-agent, two-period scenario isolating whether "
        "a period's update is visible to that same period's decision or "
        "only to the following one."
    ),
    periods=2,
)


class TestFeedbackOrderingContract(unittest.TestCase):
    TEST_NAME = "Framework: Feedback Ordering Contract"

    def test_feedback_changes_only_the_later_decision_after_realization(self):
        result = run_scenario(TWO_PERIOD_SCENARIO)
        first_period = result.trace[0]

        self.assertEqual(
            [step.actions[AGENT.name] for step in result.trace],
            [LOW, HIGH],
        )
        self.assertEqual(
            first_period.reality.agent(AGENT.name)["realized_action"],
            first_period.actions[AGENT.name],
        )
        self.assertEqual(
            first_period.observations[AGENT.name]["realized_action"],
            LOW,
        )
        self.assertTrue(
            first_period.agents[AGENT.name].model_of_reality[
                "flag_set_by_feedback"
            ],
        )

    def test_without_observation_feedback_never_changes_a_later_decision(self):
        result = run_scenario(
            TWO_PERIOD_SCENARIO.variant(
                observation=None,
            )
        )

        self.assertEqual(
            [step.actions[AGENT.name] for step in result.trace],
            [LOW, LOW],
        )

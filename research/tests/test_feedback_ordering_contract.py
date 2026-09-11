"""
Framework test: feedback ordering contract.

Purpose
-------
Not an economic replication test. Verifies the full execution ordering
inside run_scenario (research/ter/runner.py::run_scenario):

    decision -> reality -> feedback

Each period's feedback_rule runs only after that period's own decision
and reality function have produced a genuine realized outcome (O), and
it changes only the *following* period's decision environment -- never
the period O was computed from, and never before the first decision
(there is no realized outcome yet to feed back). The local feedback
rule below requires and reads that realized outcome directly, so if
feedback ever ran before reality had produced one, this test would
raise instead of silently passing.

The bank run (test_09) and speculative bubble (test_10) replication
tests demonstrate feedback producing particular economic outcomes across
multiple periods. This test isolates the ordering guarantee itself,
using a minimal local rule triple scoped to this file only, so it cannot
be confused with -- or accidentally weakened by a change to -- either
economic replication test.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import register_rule


LOW = "low"
HIGH = "high"


@register_rule("record_realized_action")
def record_realized_action(state, agents, actions, parameters):
    """
    Local Model 5.2 reality function for this test only.

    Realizes O_t as simply the action each agent actually selected --
    this contract needs nothing more elaborate than "the agent's
    selected action was realized." Read by record_feedback_flag as a
    genuine O, never inferred from state alone.
    """
    return {
        "realized_action_by_agent": {
            agent.name: action
            for agent, action in zip(agents, actions)
        },
    }


@register_rule("record_feedback_flag")
def record_feedback_flag(state, outcome, parameters):
    """
    Local Model 5.5 feedback rule for this test only. Requires O_t (from
    record_realized_action) and sets a model_of_reality field every
    agent's *next* decision can observe, only once O_t records that
    this agent's realized action was LOW.

    Reading outcome["realized_action_by_agent"] directly (no default)
    is deliberate: if feedback ever ran before reality had produced O_t,
    this would raise instead of silently succeeding -- proving reality
    necessarily precedes feedback, not just that feedback runs after
    decision.

    Required outcome field:

        realized_action_by_agent   set every period by
                                    record_realized_action, the reality
                                    function this scenario runs
                                    immediately before feedback.
    """
    realized_action_by_agent = outcome["realized_action_by_agent"]

    for agent in state["agents"]:
        if realized_action_by_agent.get(agent.name) == LOW:
            agent.model_of_reality["flag_set_by_feedback"] = True

    return state


@register_rule("choose_by_flag")
def choose_by_flag(agent):
    """
    Local Model 5.1 decision rule for this test only. Selects HIGH if a
    prior period's feedback update is visible when the decision runs,
    otherwise LOW.
    """
    if agent.model_of_reality.get("flag_set_by_feedback"):
        return HIGH

    return LOW


AGENT = AgentSpec(
    name="agent",
    objective="test objective",
    model_of_reality={},
    actual_feasible_set=[LOW, HIGH],
    perceived_feasible_set=[LOW, HIGH],
    valuation_rule="mapped_value",
    decision_process="choose_by_flag",
    horizon="current decision",
)


ONE_PERIOD_SCENARIO = Scenario(
    name="Feedback Ordering Contract (one period)",
    description=(
        "A minimal single-agent, single-period scenario isolating "
        "whether feedback can run before the first decision."
    ),
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        AGENT,
    ],
    reality_function="record_realized_action",
    feedback_rule="record_feedback_flag",
)

TWO_PERIOD_SCENARIO = ONE_PERIOD_SCENARIO.variant(
    name="Feedback Ordering Contract (two periods)",
    description=(
        "A minimal single-agent, two-period scenario isolating whether "
        "a period's feedback update is visible to that same period's "
        "decision or only to the following one."
    ),
    periods=2,
)


class TestFeedbackOrderingContract(unittest.TestCase):
    TEST_NAME = "Framework: Feedback Ordering Contract"

    def test_no_feedback_runs_before_the_first_decision(self):
        result = run_scenario(ONE_PERIOD_SCENARIO)
        agent = result.agent(AGENT.name)

        self.assertEqual(
            agent.selected_action,
            LOW,
        )

    def test_a_periods_feedback_is_not_visible_to_that_same_periods_decision(self):
        result = run_scenario(TWO_PERIOD_SCENARIO)

        first_period_decision = result.history[1]["selected_action_by_agent"]

        self.assertEqual(
            first_period_decision[AGENT.name],
            LOW,
        )

    def test_a_periods_feedback_is_visible_to_the_following_periods_decision(self):
        result = run_scenario(TWO_PERIOD_SCENARIO)

        second_period_decision = result.history[2]["selected_action_by_agent"]

        self.assertEqual(
            second_period_decision[AGENT.name],
            HIGH,
        )

    def test_reality_realizes_the_selected_action_before_feedback_reads_it(self):
        result = run_scenario(TWO_PERIOD_SCENARIO)

        first_period_selection = result.history[1]["selected_action_by_agent"]
        first_period_realization = result.history[1]["realized_action_by_agent"]

        # record_realized_action (R) reports exactly what was selected,
        # so O_0 must match C_0 for the same agent, same period.
        self.assertEqual(
            first_period_realization[AGENT.name],
            first_period_selection[AGENT.name],
        )

        self.assertEqual(
            first_period_realization[AGENT.name],
            LOW,
        )

        # record_feedback_flag (feedback) reads
        # outcome["realized_action_by_agent"] with no fallback -- it
        # would raise KeyError rather than silently pass if the runner
        # ever invoked feedback before reality had produced O_t. The
        # flag having been set (proved by the HIGH selection in the
        # following period, above) is therefore itself evidence that R
        # ran and produced O_0 before feedback ran.
        second_period_selection = result.history[2]["selected_action_by_agent"]

        self.assertEqual(
            second_period_selection[AGENT.name],
            HIGH,
        )

    def test_without_a_feedback_rule_the_flag_is_never_set(self):
        result = run_scenario(
            TWO_PERIOD_SCENARIO.variant(
                feedback_rule=None,
            )
        )
        agent = result.agent(AGENT.name)

        self.assertEqual(
            agent.selected_action,
            LOW,
        )

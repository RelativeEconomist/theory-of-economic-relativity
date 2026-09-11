"""
Framework test: agent snapshot contract.

Purpose
-------
Not an economic replication test. Verifies research/ter/snapshot.py and
its wiring into research/ter/runner.py::run_scenario: that requesting
per-period AgentState snapshots via Scenario.snapshot_fields correctly
isolates historical state from later mutation, captures only the fields
requested, stores nothing when no fields are requested, and never
changes execution behavior.

Why this exists
----------------
ScenarioResult.history[t]["agents"] intentionally keeps live, mutable
AgentState objects shared across every period -- necessary so a
feedback rule's mutation of an agent's model_of_reality,
actual_feasible_set, or perceived_feasible_set can affect that agent's
later decisions. But it also means history[t]["agents"] is not a safe
historical record: reading it after the scenario finishes shows
whatever those objects hold *now*, not what they held at period t, once
a later period has mutated them.

Scenario.snapshot_fields is the opt-in mechanism that avoids that trap:
independent, deep-copied captures of exactly the requested fields, taken
once per period, stored under history[t]["agent_snapshots"][agent_name].
This test proves that mechanism, not any economic behavior.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import register_rule


TAG_A = "a"
TAG_B = "b"


@register_rule("snapshot_contract_mutating_feedback")
def snapshot_contract_mutating_feedback(state, outcome, parameters):
    """
    Local feedback rule for this test only. Starting the period after
    the agent has already made one recorded decision, mutates the live
    agent's perceived_feasible_set in place and flips a
    model_of_reality flag -- the worst case for aliasing, since an
    unsafe (non-deep-copying) snapshot would still reflect this change.
    """
    previously_selected = state.get("selected_action_by_agent", {})

    for agent in state["agents"]:
        if previously_selected.get(agent.name) == TAG_A:
            if TAG_B not in agent.perceived_feasible_set:
                agent.perceived_feasible_set.append(TAG_B)
            agent.model_of_reality["mutated"] = True

    return state


@register_rule("snapshot_contract_prefer_a")
def snapshot_contract_prefer_a(agent):
    """
    Local decision rule for this test only. Always selects TAG_A,
    regardless of what else is perceived feasible -- this test is about
    snapshot correctness, not decision behavior, so the decision itself
    is held deliberately constant and uninteresting.
    """
    return TAG_A


BASE_AGENT = AgentSpec(
    name="agent",
    objective="test objective",
    model_of_reality={
        "values": {
            TAG_A: 0,
            TAG_B: 0,
        },
        "mutated": False,
    },
    actual_feasible_set=[
        TAG_A,
        TAG_B,
    ],
    perceived_feasible_set=[
        TAG_A,
    ],
    valuation_rule="mapped_value",
    decision_process="snapshot_contract_prefer_a",
)


SNAPSHOT_SCENARIO = Scenario(
    name="Agent Snapshot Contract",
    description=(
        "A minimal scenario for verifying snapshot isolation, "
        "selectivity, and non-interference with execution."
    ),
    periods=2,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
    feedback_rule="snapshot_contract_mutating_feedback",
    snapshot_fields=["model_of_reality", "perceived_feasible_set"],
)

NO_SNAPSHOT_SCENARIO = SNAPSHOT_SCENARIO.variant(
    snapshot_fields=[],
)

SINGLE_FIELD_SNAPSHOT_SCENARIO = SNAPSHOT_SCENARIO.variant(
    snapshot_fields=["perceived_feasible_set"],
)


class TestAgentSnapshotContract(unittest.TestCase):
    TEST_NAME = "Framework: Agent Snapshot Contract"

    def test_an_earlier_snapshot_is_unaffected_by_a_later_mutation(self):
        result = run_scenario(SNAPSHOT_SCENARIO)

        period_0_snapshot = result.history[0]["agent_snapshots"][BASE_AGENT.name]

        self.assertEqual(
            period_0_snapshot.perceived_feasible_set,
            [TAG_A],
        )

        self.assertFalse(
            period_0_snapshot.model_of_reality["mutated"],
        )

        # The live agent has since been mutated by feedback...
        final_agent = result.final["agents"][0]

        self.assertIn(
            TAG_B,
            final_agent.perceived_feasible_set,
        )

        self.assertTrue(
            final_agent.model_of_reality["mutated"],
        )

        # ...but reading the period 0 snapshot again now still shows the
        # original values: it was never aliased to the live object.
        self.assertEqual(
            period_0_snapshot.perceived_feasible_set,
            [TAG_A],
        )

        self.assertFalse(
            period_0_snapshot.model_of_reality["mutated"],
        )

        self.assertIsNot(
            period_0_snapshot.fields["perceived_feasible_set"],
            final_agent.perceived_feasible_set,
        )

    def test_different_periods_contain_independent_snapshot_values(self):
        result = run_scenario(SNAPSHOT_SCENARIO)

        # Feedback runs after a period's own decision and realization,
        # using that period's own recorded selection, and updates the
        # environment the *following* period decides from. TAG_A is
        # only on record once period 0's own step has run, so the
        # mutation is applied at the end of period 0's step -- after
        # period 0's own snapshot (history[1]) was already taken, and
        # before period 1's decision. It first appears in history[2]
        # (period 1's snapshot, taken before period 1's own feedback),
        # not history[1] (period 0's).
        before_mutation = result.history[1]["agent_snapshots"][BASE_AGENT.name]
        after_mutation = result.history[2]["agent_snapshots"][BASE_AGENT.name]

        self.assertEqual(
            before_mutation.perceived_feasible_set,
            [TAG_A],
        )

        self.assertEqual(
            after_mutation.perceived_feasible_set,
            [TAG_A, TAG_B],
        )

        self.assertFalse(
            before_mutation.model_of_reality["mutated"],
        )

        self.assertTrue(
            after_mutation.model_of_reality["mutated"],
        )

    def test_only_requested_fields_are_captured(self):
        result = run_scenario(SINGLE_FIELD_SNAPSHOT_SCENARIO)

        snapshot = result.history[0]["agent_snapshots"][BASE_AGENT.name]

        self.assertEqual(
            snapshot.fields,
            {
                "perceived_feasible_set": [TAG_A],
            },
        )

        with self.assertRaises(AttributeError):
            snapshot.model_of_reality

    def test_empty_snapshot_fields_stores_no_per_agent_state(self):
        result = run_scenario(NO_SNAPSHOT_SCENARIO)

        for state in result.history:
            self.assertEqual(
                state["agent_snapshots"],
                {},
            )

    def test_snapshot_configuration_does_not_change_execution_behavior(self):
        with_snapshots = run_scenario(SNAPSHOT_SCENARIO)
        without_snapshots = run_scenario(NO_SNAPSHOT_SCENARIO)

        with_agent = with_snapshots.agent(BASE_AGENT.name)
        without_agent = without_snapshots.agent(BASE_AGENT.name)

        self.assertEqual(
            with_agent.selected_action,
            without_agent.selected_action,
        )

        self.assertEqual(
            with_agent.perceived_feasible_set,
            without_agent.perceived_feasible_set,
        )

        self.assertEqual(
            with_agent.model_of_reality,
            without_agent.model_of_reality,
        )

        self.assertEqual(
            [
                state["selected_action_by_agent"]
                for state in with_snapshots.history[1:]
            ],
            [
                state["selected_action_by_agent"]
                for state in without_snapshots.history[1:]
            ],
        )

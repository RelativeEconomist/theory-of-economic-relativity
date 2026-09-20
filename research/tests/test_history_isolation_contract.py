"""
Framework test: history isolation

Purpose
-------
Verifies that ScenarioResult.history stays a safe record after later
periods mutate state:

- history[t]["agents"] holds live AgentState objects, so it reflects later
  mutation. Scenario.snapshot_fields is the opt-in way to capture
  independent copies under history[t]["agent_snapshots"][agent_name].
- history[t]["permitted_actions"] (the reality-side implementation index
  of the scenario-relevant aspects of F_t) keeps its own value per period,
  whether a feedback rule or a reality function mutates it.

Stress mutations
----------------
The local feedback and reality rules below deliberately mutate live agent
state and state["permitted_actions"] in place, to check that history
entries are unaffected. They are artificial mutations used to test history
isolation. They are not TER dynamics, not a specification of Model 5.5
feedback, and not evidence of any direct C_t -> F_{t+1} pathway.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import register_rule


TAG_A = "a"
TAG_B = "b"


@register_rule("snapshot_contract_mutating_feedback")
def snapshot_contract_mutating_feedback(state, outcome, parameters):
    """
    Artificial stressor, not a TER feedback specification: after the
    agent's first decision, mutate the live agent and permitted_actions in
    place, to check that history is unaffected. Not a TER dynamic and not
    evidence of a direct C_t -> F_{t+1} pathway.
    """
    previously_selected = state.get("selected_action_by_agent", {})

    for agent in state["agents"]:
        if previously_selected.get(agent.name) == TAG_A:
            if TAG_B not in agent.perceived_feasible_set:
                agent.perceived_feasible_set.append(TAG_B)
            agent.model_of_reality["mutated"] = True

            permitted = state["permitted_actions"][agent.name]
            if TAG_B in permitted:
                permitted.remove(TAG_B)

    return state


@register_rule("snapshot_contract_mutating_reality")
def snapshot_contract_mutating_reality(state, agents, actions, parameters):
    """
    Artificial stressor, not a TER reality function: mutate the
    permitted_actions it was handed in place and report nothing.
    """
    for agent in agents:
        permitted = state["permitted_actions"][agent.name]
        if TAG_B in permitted:
            permitted.remove(TAG_B)

    return {}


@register_rule("snapshot_contract_prefer_a")
def snapshot_contract_prefer_a(agent):
    """Always select TAG_A, so decisions stay constant."""
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
    perceived_feasible_set=[
        TAG_A,
    ],
    valuation_rule="mapped_value",
    decision_process="snapshot_contract_prefer_a",
)


SNAPSHOT_SCENARIO = Scenario(
    name="Agent Snapshot Contract",
    description="Minimal scenario for verifying history isolation.",
    periods=2,
    initial_state={
        "period": 0,
        "permitted_actions": {
            BASE_AGENT.name: [TAG_A, TAG_B],
        },
    },
    agents=[
        BASE_AGENT,
    ],
    # Artificial mutation used to test history isolation; not a TER dynamic.
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
    TEST_NAME = "Framework: History Isolation Contract"

    def test_an_earlier_snapshot_is_unaffected_by_a_later_mutation(self):
        result = run_scenario(SNAPSHOT_SCENARIO)

        snapshot = result.history[0]["agent_snapshots"][BASE_AGENT.name]
        live_agent = result.final["agents"][0]

        # The live agent was mutated by feedback; the snapshot was not.
        self.assertIn(TAG_B, live_agent.perceived_feasible_set)
        self.assertTrue(live_agent.model_of_reality["mutated"])

        self.assertEqual(snapshot.perceived_feasible_set, [TAG_A])
        self.assertFalse(snapshot.model_of_reality["mutated"])

    def test_different_periods_contain_independent_snapshot_values(self):
        result = run_scenario(SNAPSHOT_SCENARIO)

        # Snapshots are taken before that period's feedback, so period 0's
        # mutation first appears in history[2], not history[1].
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

    def test_history_keeps_each_periods_permitted_actions_when_a_later_period_mutates_them(self):
        history = run_scenario(SNAPSHOT_SCENARIO).history

        self.assertEqual(
            history[0]["permitted_actions"],
            {BASE_AGENT.name: [TAG_A, TAG_B]},
        )

        self.assertEqual(
            history[1]["permitted_actions"],
            {BASE_AGENT.name: [TAG_A]},
        )

    def test_a_reality_function_mutating_permitted_actions_does_not_alter_history(self):
        history = run_scenario(
            SNAPSHOT_SCENARIO.variant(
                reality_function="snapshot_contract_mutating_reality",
                feedback_rule=None,
            )
        ).history

        for entry in history:
            self.assertEqual(
                entry["permitted_actions"],
                {BASE_AGENT.name: [TAG_A, TAG_B]},
            )

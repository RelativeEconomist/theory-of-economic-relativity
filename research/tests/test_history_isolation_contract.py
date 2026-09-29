"""
Framework test: history isolation

Purpose
-------
Verifies that a run's record stays a safe history after later decision
points change agent state or the objective state:

- trace[t].agents[name] records each agent's state as it stood after
  decision point t. A later update can never change an earlier record.
- trace[t].objective_state (and ScenarioResult.history) records F_t+1 as
  it stood after decision point t, including permission data
  (objective_state["permitted_actions"]). A later transition can never
  change an earlier record, even one that edits its working copy of F in
  place.

Stress mutations
----------------
The local update and transition rules below deliberately change agent
state and objective_state["permitted_actions"] in place on their own
working copies, to check that history entries are unaffected. They are
artificial changes used to test history isolation. They are not TER
dynamics, not a specification of Model 5.5 feedback, and not evidence of
any direct C_t -> F_t+1 pathway.
"""

import unittest

from research.ter import AgentSpec, RealityResult, Scenario, run_scenario
from research.ter.rules import register_rule


TAG_A = "a"
TAG_B = "b"


@register_rule("history_contract_echo_reality")
def history_contract_echo_reality(actions, objective_state, parameters):
    """Each agent's O_i,t is the action it selected."""
    return RealityResult(
        agents={
            name: {"selected": action}
            for name, action in actions.items()
        },
    )


@register_rule("history_contract_observe_own")
def history_contract_observe_own(agents, actions, reality, objective_state, parameters):
    """Each agent observes its own O_i,t."""
    return {
        name: dict(reality.agent(name))
        for name in agents
        if name in reality.agents
    }


@register_rule("history_contract_mutating_update")
def history_contract_mutating_update(agent, observation):
    """
    Artificial stressor, not a TER update specification: after the
    agent's first decision, change its working copy of F_hat and M in
    place and return them.
    """
    if observation["selected"] != TAG_A:
        return {}

    if TAG_B not in agent.perceived_feasible_set:
        agent.perceived_feasible_set.append(TAG_B)

    agent.model_of_reality["mutated"] = True

    return {
        "perceived_feasible_set": agent.perceived_feasible_set,
        "model_of_reality": agent.model_of_reality,
    }


@register_rule("history_contract_mutating_transition")
def history_contract_mutating_transition(objective_state, reality, parameters):
    """
    Artificial stressor, not a TER transition: remove TAG_B from every
    agent's permitted actions by editing the working copy in place.
    """
    for permitted in objective_state["permitted_actions"].values():
        if TAG_B in permitted:
            permitted.remove(TAG_B)

    return objective_state


@register_rule("history_contract_prefer_a")
def history_contract_prefer_a(agent):
    """Always select TAG_A, so decisions stay constant."""
    return TAG_A


BASE_AGENT = AgentSpec(
    name="agent",
    objective="test objective",
    model_of_reality={
        "mutated": False,
    },
    perceived_feasible_set=[
        TAG_A,
    ],
    valuation_rule="mapped_value",
    decision_process="history_contract_prefer_a",
    update_rule="history_contract_mutating_update",
)


SCENARIO = Scenario(
    name="History Isolation Contract",
    description="Minimal scenario for verifying history isolation.",
    periods=2,
    initial_state={
        "permitted_actions": {
            BASE_AGENT.name: [TAG_A, TAG_B],
        },
    },
    agents=[
        BASE_AGENT,
    ],
    reality="history_contract_echo_reality",
    observation="history_contract_observe_own",
    # Artificial mutation used to test history isolation; not a TER dynamic.
    transition="history_contract_mutating_transition",
)


class TestHistoryIsolationContract(unittest.TestCase):
    TEST_NAME = "Framework: History Isolation Contract"

    def test_an_earlier_agent_record_is_unaffected_by_a_later_update(self):
        result = run_scenario(SCENARIO)

        initial = result.trace.initial_agents[BASE_AGENT.name]
        final = result.agent(BASE_AGENT.name)

        # The agent was changed by its update; the initial record was not.
        self.assertIn(TAG_B, final.perceived_feasible_set)
        self.assertTrue(final.model_of_reality["mutated"])

        self.assertEqual(initial.perceived_feasible_set, [TAG_A])
        self.assertFalse(initial.model_of_reality["mutated"])

    def test_different_decision_points_record_independent_agent_state(self):
        trace = run_scenario(SCENARIO).trace

        before_update = trace.agents_before(0)[BASE_AGENT.name]
        after_update = trace.agents_before(1)[BASE_AGENT.name]

        self.assertEqual(before_update.perceived_feasible_set, [TAG_A])
        self.assertEqual(after_update.perceived_feasible_set, [TAG_A, TAG_B])

        self.assertFalse(before_update.model_of_reality["mutated"])
        self.assertTrue(after_update.model_of_reality["mutated"])

    def test_history_keeps_each_periods_permitted_actions_when_a_later_transition_changes_them(self):
        history = run_scenario(SCENARIO).history

        self.assertEqual(
            history[0]["permitted_actions"],
            {BASE_AGENT.name: [TAG_A, TAG_B]},
        )

        self.assertEqual(
            history[1]["permitted_actions"],
            {BASE_AGENT.name: [TAG_A]},
        )

    def test_the_scenario_declaration_keeps_its_permission_data(self):
        run_scenario(SCENARIO)

        self.assertEqual(
            SCENARIO.initial_state["permitted_actions"],
            {BASE_AGENT.name: [TAG_A, TAG_B]},
        )

    def test_recording_does_not_change_execution_behavior(self):
        result = run_scenario(SCENARIO)

        self.assertEqual(
            [step.actions[BASE_AGENT.name] for step in result.trace],
            [TAG_A, TAG_A],
        )

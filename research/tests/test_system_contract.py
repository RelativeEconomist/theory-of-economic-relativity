"""
Framework test: multi-agent system contract.

Purpose
-------
Not an economic replication test. Verifies TER Model 5.3's system step
(research/ter/system.py::run_system) structurally, independent of any
specific economic scenario:

1. Every agent independently selects an action through the standard TER
   decision process (Model 5.1); run_system collects one action per
   agent.
2. Actions correspond to the correct agent -- ordering is preserved,
   regardless of the order agents are supplied in.
3. The outcome function receives the complete joint action set, not a
   subset and not a re-derived one.
4. run_system reports exactly one system outcome, taken directly from
   whatever the outcome function returns.

This does not exercise research.ter.market's separate multi-agent
mechanism (evaluate_market/find_market_clearing_states) or any
Scenario/run_scenario machinery -- both already have their own coverage.
"""

import unittest

from research.ter.agent import AgentState
from research.ter.system import run_system


def make_agent(name: str) -> AgentState:
    """
    An agent whose only perceived feasible action is derived from its
    own name, so a selected action can always be traced back to the
    agent that selected it.
    """
    action = f"{name}_action"

    return AgentState(
        objective="test objective",
        model_of_reality={},
        actual_feasible_set=[action],
        perceived_feasible_set=[action],
        value=lambda a, agent: 0.0,
        horizon=None,
        decision_process=lambda agent: agent.perceived_feasible_set[0],
        name=name,
        valuation={},
        decision_parameters={},
    )


AGENT_A = make_agent("agent_a")
AGENT_B = make_agent("agent_b")
AGENT_C = make_agent("agent_c")


class TestSystemContract(unittest.TestCase):
    TEST_NAME = "Framework: Multi-Agent System Contract"

    def test_every_agent_independently_selects_its_own_action(self):
        result = run_system(
            agents=[AGENT_A, AGENT_B, AGENT_C],
            outcome_function=lambda agents, actions: None,
        )

        self.assertEqual(
            result.actions,
            ["agent_a_action", "agent_b_action", "agent_c_action"],
        )

    def test_actions_correspond_to_the_correct_agent_in_input_order(self):
        agents = [AGENT_C, AGENT_A, AGENT_B]

        result = run_system(
            agents=agents,
            outcome_function=lambda agents, actions: None,
        )

        self.assertEqual(
            list(
                zip(
                    (agent.name for agent in agents),
                    result.actions,
                )
            ),
            [
                ("agent_c", "agent_c_action"),
                ("agent_a", "agent_a_action"),
                ("agent_b", "agent_b_action"),
            ],
        )

    def test_outcome_function_receives_the_complete_joint_action_set(self):
        captured = {}

        def capture(agents, actions):
            captured["agents"] = list(agents)
            captured["actions"] = list(actions)
            return "captured outcome"

        result = run_system(
            agents=[AGENT_A, AGENT_B, AGENT_C],
            outcome_function=capture,
        )

        self.assertEqual(
            captured["agents"],
            [AGENT_A, AGENT_B, AGENT_C],
        )

        self.assertEqual(
            captured["actions"],
            result.actions,
        )

        self.assertEqual(
            len(captured["actions"]),
            3,
        )

    def test_one_system_outcome_is_produced_from_the_joint_actions(self):
        result = run_system(
            agents=[AGENT_A, AGENT_B, AGENT_C],
            outcome_function=lambda agents, actions: len(actions),
        )

        self.assertEqual(
            result.outcome,
            3,
        )

"""
Framework test: multi-agent system contract

Canonical TER: theory/academic.md, Model 5.3

Purpose
-------
Verifies the Model 5.3 system step of the engine
(research/ter/runner.py::run_scenario) structurally, independent of any
economic scenario:

1. Every acting agent independently selects an action through the
   standard decision process (Model 5.1); the step collects one action
   per actor.
2. Actions correspond to the correct agent -- keyed by agent name, in the
   order the agents are declared, regardless of what that order is.
3. R receives the complete joint action set, not a subset and not a
   re-derived one.
4. The step reports exactly one system outcome (O_t), taken directly from
   what R returns.

The rules here are passed directly as callables.

Out of scope
------------
F_t: the probes ignore the objective state. No relationship between
individual outcomes O_{i,t} and O_t is defined or tested. This does not
exercise research.ter.market's separate price-grid mechanism
(evaluate_market/find_market_clearing_states), which has its own
coverage.
"""

import unittest

from research.ter import AgentSpec, RealityResult, Scenario, run_scenario


def select_own_action(agent):
    """
    Each agent's only perceived feasible action is derived from its own
    name, so a selected action can always be traced back to the agent
    that selected it.
    """
    return agent.perceived_feasible_set[0]


def make_agent(name: str) -> AgentSpec:
    return AgentSpec(
        name=name,
        objective="test objective",
        model_of_reality={},
        perceived_feasible_set=[f"{name}_action"],
        valuation_rule=lambda action, agent: 0.0,
        decision_process=select_own_action,
    )


AGENT_A = make_agent("agent_a")
AGENT_B = make_agent("agent_b")
AGENT_C = make_agent("agent_c")


def count_actions(actions, objective_state, parameters):
    return RealityResult(system={"action_count": len(actions)})


def scenario(agents, reality=count_actions):
    return Scenario(
        name="System Contract",
        description="Minimal multi-agent step.",
        periods=1,
        initial_state={},
        agents=agents,
        reality=reality,
    )


class TestSystemContract(unittest.TestCase):
    TEST_NAME = "Framework: Multi-Agent System Contract"

    def test_actions_correspond_to_the_correct_agent_in_input_order(self):
        result = run_scenario(scenario([AGENT_C, AGENT_A, AGENT_B]))

        self.assertEqual(
            list(result.trace[0].actions.items()),
            [
                ("agent_c", "agent_c_action"),
                ("agent_a", "agent_a_action"),
                ("agent_b", "agent_b_action"),
            ],
        )

    def test_reality_receives_the_complete_joint_action_set(self):
        captured = {}

        def capture(actions, objective_state, parameters):
            captured["actions"] = dict(actions)
            return RealityResult()

        result = run_scenario(scenario([AGENT_A, AGENT_B, AGENT_C], capture))

        self.assertEqual(
            captured["actions"],
            dict(result.trace[0].actions),
        )

    def test_one_system_outcome_is_produced_from_the_joint_actions(self):
        result = run_scenario(scenario([AGENT_A, AGENT_B, AGENT_C]))

        self.assertEqual(
            result.trace[0].reality.system,
            {"action_count": 3},
        )

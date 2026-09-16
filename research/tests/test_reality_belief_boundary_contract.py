"""
Framework test: reality/belief boundary contract.

Purpose
-------
Not an economic replication test. Verifies that TER Model 5.2's reality
step (research/ter/runner.py's Scenario execution, via
research/ter/outcome.py::RealityView) mechanically enforces the
canonical architectural boundary between R and the agent's decision-side
state:

    O = R(C, F, P, S)

R may read C (the selected action, via its own `actions` argument), F
(each agent's actual_feasible_set), and P/S (state, parameters). R must
never read or depend directly on M (model_of_reality), F_hat
(perceived_feasible_set), or V (valuation) -- those are decision-side
inputs to D (Model 5.1, see test_decision_feasibility_boundary_contract.
py), and a reality function reading them would treat belief or
preference as reality rather than something reality merely constrains.

This exercises the mechanism directly, through an ordinary Scenario,
independent of any specific economic replication.
"""

import unittest

from research.ter.outcome import is_actually_feasible
from research.ter.rules import register_rule
from research.ter.runner import run_scenario
from research.ter.scenario import AgentSpec, Scenario


ORDINARY_ACTION = "ordinary_action"
UNREACHABLE_ACTION = "unreachable_action"


@register_rule("always_select_unreachable")
def always_select_unreachable(view):
    """
    Local Model 5.1 decision rule for this test only. Always selects
    UNREACHABLE_ACTION, which is perceived feasible for every agent here
    but only actually feasible for CLEAR_AGENT -- this forces a genuine
    F vs F_hat mismatch for BLOCKED_AGENT, so the boundary probe below
    has something non-trivial to report.
    """
    return UNREACHABLE_ACTION


@register_rule("boundary_probe_reality")
def boundary_probe_reality(state, agents, actions, parameters):
    """
    Local Model 5.2 reality function for this test only.

    Reports, per agent, exactly what R can and cannot read from the
    RealityView it was given:

        c_seen_by_r            the selected action, read from R's own
                                actions argument (proves R can access C)
        actually_feasible      is_actually_feasible(view, action) (proves
                                R can access F where needed)
        has_model_of_reality       must be False (M is off-limits)
        has_perceived_feasible_set must be False (F_hat is off-limits)
        has_valuation              must be False (V is off-limits)
        has_actual_feasible_set    must be True (F is legitimate)

    Never re-selects or rewrites the action; it only reports what R
    observed about the view and the already-selected C.
    """
    results = {}

    for agent, action in zip(agents, actions):
        results[agent.name] = {
            "c_seen_by_r": action,
            "actually_feasible": is_actually_feasible(agent, action),
            "has_model_of_reality": hasattr(agent, "model_of_reality"),
            "has_perceived_feasible_set": hasattr(agent, "perceived_feasible_set"),
            "has_valuation": hasattr(agent, "valuation"),
            "has_actual_feasible_set": hasattr(agent, "actual_feasible_set"),
        }

    return {"agent_results": results}


BASE_AGENT = AgentSpec(
    name="agent",
    objective="test objective",
    model_of_reality={
        "a_belief": "must never reach R",
    },
    valuation={
        "a_value": "must never reach R",
    },
    actual_feasible_set=[
        ORDINARY_ACTION,
    ],
    perceived_feasible_set=[
        ORDINARY_ACTION,
        UNREACHABLE_ACTION,
    ],
    valuation_rule="mapped_value",
    decision_process="always_select_unreachable",
    horizon="current decision",
)

BLOCKED_AGENT = BASE_AGENT.variant(
    name="blocked_agent",
)

CLEAR_AGENT = BASE_AGENT.variant(
    name="clear_agent",
    actual_feasible_set=[
        ORDINARY_ACTION,
        UNREACHABLE_ACTION,
    ],
)

SCENARIO = Scenario(
    name="Reality/Belief Boundary Probe",
    description=(
        "Two agents whose decision process always selects an action "
        "that is perceived feasible for both but only actually feasible "
        "for one, used to probe exactly what the reality function can "
        "and cannot read about each agent."
    ),
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BLOCKED_AGENT,
        CLEAR_AGENT,
    ],
    reality_function="boundary_probe_reality",
)


class TestRealityBeliefBoundaryContract(unittest.TestCase):
    TEST_NAME = "Framework: Reality/Belief Boundary Contract"

    def test_r_can_access_the_selected_c(self):
        result = run_scenario(SCENARIO)

        self.assertEqual(
            result.agent(BLOCKED_AGENT.name).c_seen_by_r,
            UNREACHABLE_ACTION,
        )

        self.assertEqual(
            result.agent(CLEAR_AGENT.name).c_seen_by_r,
            UNREACHABLE_ACTION,
        )

    def test_r_can_access_actual_feasibility(self):
        result = run_scenario(SCENARIO)

        self.assertFalse(
            result.agent(BLOCKED_AGENT.name).actually_feasible,
        )

        self.assertTrue(
            result.agent(CLEAR_AGENT.name).actually_feasible,
        )

    def test_r_cannot_access_model_of_reality(self):
        result = run_scenario(SCENARIO)

        self.assertFalse(
            result.agent(BLOCKED_AGENT.name).has_model_of_reality,
        )

    def test_r_cannot_access_perceived_feasible_set(self):
        result = run_scenario(SCENARIO)

        self.assertFalse(
            result.agent(BLOCKED_AGENT.name).has_perceived_feasible_set,
        )

    def test_r_cannot_access_valuation(self):
        result = run_scenario(SCENARIO)

        self.assertFalse(
            result.agent(BLOCKED_AGENT.name).has_valuation,
        )

    def test_r_can_access_the_actual_feasible_set(self):
        result = run_scenario(SCENARIO)

        self.assertTrue(
            result.agent(BLOCKED_AGENT.name).has_actual_feasible_set,
        )

    def test_selected_action_is_not_rewritten_by_the_boundary_check(self):
        result = run_scenario(SCENARIO)
        blocked = result.agent(BLOCKED_AGENT.name)

        # C is exactly what D selected, even though it is not actually
        # feasible for this agent -- the reality function reports that
        # mismatch, it does not resolve it by picking a different action.
        self.assertEqual(
            blocked.selected_action,
            UNREACHABLE_ACTION,
        )

        self.assertEqual(
            blocked.c_seen_by_r,
            blocked.selected_action,
        )

"""
Framework test: reality/belief boundary contract

Canonical TER: theory/academic.md, Models 5.1 and 5.2

Purpose
-------
Verifies that the reality step (research/ter/runner.py's Scenario
execution, via research/ter/outcome.py::RealityView) gives R the selected
actions and the scenario state and parameters, and never the agent-side
inputs to D.

R may read the selected action C (via its own `actions` argument) and the
scenario state and parameters, including state["permitted_actions"] -- an
implementation index of the scenario-relevant aspects of F_t, the
Objective Feasible State of Reality (which is not agent-specific). R must
never read M (model_of_reality), F̂ (perceived_feasible_set), or V
(valuation): those are agent-side inputs to D (Model 5.1; see
test_decision_feasibility_boundary_contract.py), and a reality function
reading them would treat belief or preference as reality.

The probe reports per-agent results, so the specification is agent-level
(O_{i,t}); no system outcome O_t is defined.

This exercises the mechanism directly, through an ordinary Scenario,
independent of any economic replication.

Out of scope
------------
Realized outcomes beyond the probe's own report; see
test_feasibility_contract.py.
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
    but permitted by the scenario's permission data only for CLEAR_AGENT --
    this gives BLOCKED_AGENT a mismatch between F̂ and that data, so the
    boundary probe below has something non-trivial to report.
    """
    return UNREACHABLE_ACTION


@register_rule("boundary_probe_reality")
def boundary_probe_reality(state, agents, actions, parameters):
    """
    Local Model 5.2 reality function for this test only.

    Reports, per agent, exactly what R can and cannot read from the
    RealityView and state it was given:

        c_seen_by_r            the selected action, read from R's own
                                actions argument (proves R can access C)
        actually_feasible      is_actually_feasible(state, view, action),
                                a per-agent membership check against the
                                permission data (proves R can read it)
        has_model_of_reality       must be False (M is off-limits)
        has_perceived_feasible_set must be False (F̂ is off-limits)
        has_valuation              must be False (V is off-limits)
        sees_permitted_actions     must be True (the permission data is
                                legitimate for R, and is carried by state
                                rather than by any agent view)

    Does not re-select or alter the action; it only reports what R
    observed about the view and the already-selected C.
    """
    results = {}

    for agent, action in zip(agents, actions):
        results[agent.name] = {
            "c_seen_by_r": action,
            "actually_feasible": is_actually_feasible(state, agent, action),
            "has_model_of_reality": hasattr(agent, "model_of_reality"),
            "has_perceived_feasible_set": hasattr(agent, "perceived_feasible_set"),
            "has_valuation": hasattr(agent, "valuation"),
            "sees_permitted_actions": "permitted_actions" in state,
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
)

SCENARIO = Scenario(
    name="Reality/Belief Boundary Probe",
    description=(
        "Two agents whose decision process always selects an action "
        "that is perceived feasible for both but permitted by the "
        "scenario for only one, used to probe exactly what the reality function can "
        "and cannot read about each agent."
    ),
    periods=1,
    initial_state={
        "period": 0,
        # Permission data (an implementation index of the scenario-relevant
        # aspects of F_t): the scenario permits UNREACHABLE_ACTION for
        # CLEAR_AGENT only.
        "permitted_actions": {
            BLOCKED_AGENT.name: [
                ORDINARY_ACTION,
            ],
            CLEAR_AGENT.name: [
                ORDINARY_ACTION,
                UNREACHABLE_ACTION,
            ],
        },
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

    def test_r_can_check_the_selected_action_against_permitted_actions(self):
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

    def test_r_can_read_the_permission_data_carried_in_state(self):
        result = run_scenario(SCENARIO)

        self.assertTrue(
            result.agent(BLOCKED_AGENT.name).sees_permitted_actions,
        )

    def test_selected_action_record_is_preserved_by_the_boundary_check(self):
        result = run_scenario(SCENARIO)
        blocked = result.agent(BLOCKED_AGENT.name)

        # C is exactly what D selected, even though the scenario does not
        # permit it for this agent -- the reality function reports that
        # mismatch; the framework preserves the selected-action record.
        self.assertEqual(
            blocked.selected_action,
            UNREACHABLE_ACTION,
        )

        self.assertEqual(
            blocked.c_seen_by_r,
            blocked.selected_action,
        )

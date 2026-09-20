"""
Framework test: decision/feasibility boundary contract

Canonical TER: theory/academic.md, Models 5.1 and 5.2

Purpose
-------
Verifies that the decision step (research/ter/decision.py::select_action)
gives D only agent-side inputs -- F̂ (perceived_feasible_set), G
(objective), M (model_of_reality), V (value) and H (horizon) -- and never
F_t. D receives a DecisionView, which has no F_t field.

F_t, the Objective Feasible State of Reality, is not agent-specific. In
this implementation, scenario state carries state["permitted_actions"]
(agent name -> permitted actions), an implementation index of the
scenario-relevant aspects of F_t that the reality side reads. Whether the
scenario permits a selected action is evaluated only after selection, on
the reality/outcome side (research.ter.outcome.is_actually_feasible, a
per-agent membership check against that index).

The framework preserves the selected-action record produced by Model 5.1
when that check runs. This is an implementation invariant of the current
runner, not a theoretical rule.

Model 5.2 outcome realization has its own coverage in
test_feasibility_contract.py.

Out of scope
------------
Realized outcomes. This test exercises the mechanism directly
(AgentState / select_action / DecisionView), independent of any economic
scenario.
"""

import unittest

from research.ter.agent import AgentState
from research.ter.decision import DecisionView, select_action
from research.ter.outcome import is_actually_feasible


ACTUAL_ONLY_ACTION = "actual_only_action"
PERCEIVED_ACTION = "perceived_action"

# Permission data as scenario state carries it (an implementation index of
# the scenario-relevant aspects of F_t): the only action the scenario
# permits for "agent" is one the agent never perceives as feasible.
STATE = {
    "permitted_actions": {
        "agent": [ACTUAL_ONLY_ACTION],
    },
}


def make_agent(decision_process):
    return AgentState(
        objective="test objective",
        model_of_reality={},
        perceived_feasible_set=[PERCEIVED_ACTION],
        value=lambda action, view: 0.0,
        horizon=None,
        decision_process=decision_process,
        name="agent",
        valuation={},
        decision_parameters={},
    )


class TestDecisionFeasibilityBoundaryContract(unittest.TestCase):
    TEST_NAME = "Framework: Decision/Feasibility Boundary Contract"

    def test_decision_process_receives_a_decision_view_not_the_agent_state(self):
        captured = {}

        def capturing_decision_process(view):
            captured["view"] = view
            return view.perceived_feasible_set[0]

        agent = make_agent(capturing_decision_process)
        select_action(agent)

        self.assertIsInstance(captured["view"], DecisionView)
        self.assertNotIsInstance(captured["view"], AgentState)

    def test_decision_process_can_read_the_perceived_feasible_set(self):
        agent = make_agent(lambda view: view.perceived_feasible_set[0])

        self.assertEqual(
            select_action(agent),
            PERCEIVED_ACTION,
        )

    def test_decision_process_cannot_access_the_objective_feasible_state(self):
        def reading_decision_process(view):
            return view.permitted_actions[0]

        agent = make_agent(reading_decision_process)

        with self.assertRaises(AttributeError):
            select_action(agent)

    def test_selection_still_produces_an_action_from_the_perceived_feasible_set(self):
        agent = make_agent(lambda view: view.perceived_feasible_set[0])

        selected = select_action(agent)

        self.assertEqual(selected, PERCEIVED_ACTION)
        self.assertIn(selected, agent.perceived_feasible_set)

    def test_permission_is_checked_after_selection_without_altering_the_selection_record(self):
        agent = make_agent(lambda view: view.perceived_feasible_set[0])

        selected = select_action(agent)

        # C is exactly what D selected from F̂; D never saw F_t.
        self.assertEqual(selected, PERCEIVED_ACTION)

        # Only now, after C is selected, is it checked whether the scenario
        # permits C -- on the reality/outcome side (the permission data is
        # available here, just never to D). This is a per-agent membership
        # check, not a claim that C will succeed. PERCEIVED_ACTION is not
        # among the actions permitted for this agent, so the check reports
        # False rather than silently passing.
        self.assertFalse(is_actually_feasible(STATE, agent, selected))

        # Implementation invariant: the check leaves the selection record
        # unchanged.
        self.assertEqual(selected, PERCEIVED_ACTION)

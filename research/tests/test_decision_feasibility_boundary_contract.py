"""
Framework test: decision/feasibility boundary contract.

Purpose
-------
Not an economic replication test. Verifies TER Model 5.1's decision step
(research/ter/decision.py::select_action) mechanically enforces the
canonical architectural boundary between D and F:

    C = D(F_hat, G, M, V, H)

D may read F_hat (perceived_feasible_set), G (objective), M
(model_of_reality), V (value), and H (horizon). D must never read or
depend directly on F (actual_feasible_set) -- actual feasibility is a
Model 5.2 concern, checked only after C is selected, on the
reality/outcome side (research.ter.outcome.is_actually_feasible), and
that check never rewrites C.

This exercises the mechanism directly (AgentState / select_action /
DecisionView), independent of any specific economic scenario. Model 5.2
itself (partial realization, severity) already has its own coverage in
test_feasibility_contract.py; this test is only about the boundary
select_action enforces on D's input.
"""

import unittest

from research.ter.agent import AgentState
from research.ter.decision import DecisionView, select_action
from research.ter.outcome import is_actually_feasible


ACTUAL_ONLY_ACTION = "actual_only_action"
PERCEIVED_ACTION = "perceived_action"


def make_agent(decision_process):
    return AgentState(
        objective="test objective",
        model_of_reality={},
        actual_feasible_set=[ACTUAL_ONLY_ACTION],
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

    def test_decision_process_cannot_access_the_actual_feasible_set(self):
        def reading_decision_process(view):
            return view.actual_feasible_set[0]

        agent = make_agent(reading_decision_process)

        with self.assertRaises(AttributeError):
            select_action(agent)

    def test_selection_still_produces_an_action_from_the_perceived_feasible_set(self):
        agent = make_agent(lambda view: view.perceived_feasible_set[0])

        selected = select_action(agent)

        self.assertEqual(selected, PERCEIVED_ACTION)
        self.assertIn(selected, agent.perceived_feasible_set)

    def test_actual_feasibility_is_checked_later_without_rewriting_c(self):
        agent = make_agent(lambda view: view.perceived_feasible_set[0])

        selected = select_action(agent)

        # C is exactly what D selected from F_hat, never from F.
        self.assertEqual(selected, PERCEIVED_ACTION)

        # Only now, after C is fixed, is actual feasibility checked -- on
        # the reality/outcome side, against the full AgentState (F is
        # available here, just never to D). PERCEIVED_ACTION is not in
        # this agent's actual_feasible_set, so the check reports False
        # rather than silently passing.
        self.assertFalse(is_actually_feasible(agent, selected))

        # Checking feasibility does not change C.
        self.assertEqual(selected, PERCEIVED_ACTION)

"""
TER Replication Test 06: Coordination and Multiple Equilibria

Economic question
------------------
Can TER represent a coordination game with multiple equilibria, where
each agent's belief about the counterpart's choice determines which of
several mutually consistent outcomes is realized?

Scenario
--------
Two firms must each adopt one of two incompatible technology standards,
A or B. Compatibility, not intrinsic quality, determines payoff:

    both choose A          -> payoff 4 each
    both choose B           -> payoff 3 each
    different standards    -> payoff 0 each

This is a concrete instance of the general coordination mechanism:
whichever standard each firm expects the other to adopt, matching it is
that firm's best response.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C ──→ O

    M   expected_other_action -- each firm's belief about which
        standard the counterpart will adopt
    V   payoff_matrix -- each firm's own perceived payoff structure,
        used only to value actions (ValuationRule.PAYOFF_MATRIX)
    D   DecisionProcess.MAXIMIZE
    C   "standard_a" or "standard_b", one per firm
    R   RealityFunction.PAYOFF_MATRIX_OUTCOME -- realizes payoffs from
        both firms' actual selected actions and the scenario's own
        actual_payoff_matrix, never from any firm's V
    O   each firm's realized payoff

F equals F̂ throughout: both standards are always actually feasible.

Tested TER mechanics
--------------------
G   Objective              constant: maximize coordination payoff
M   Model of reality       expected_other_action -- CHANGED across
                            scenarios
V   Valuation              payoff_matrix (perceived), looked up against M
D   Decision process       constant: DecisionProcess.MAXIMIZE
C   Selected action        observed result
R   Reality function       RealityFunction.PAYOFF_MATRIX_OUTCOME
O   Realized outcome       each firm's realized payoff, from R

Economic mechanism
------------------
ValuationRule.PAYOFF_MATRIX values matching the expected counterpart
standard above switching, so each firm's best response is simply to
adopt whichever standard it expects the other to adopt. When both firms
share the same expectation, (A, A) and (B, B) are both mutual
best-response Nash equilibria of this one-shot game -- neither firm can
do better by unilaterally switching, given the other's action. (A, A)
Pareto-dominates (B, B) under the stated payoff structure: both firms
are strictly better off. TER is not running a general equilibrium
solver here; the two independent firms simply each apply the same
best-response rule, and the pairing of their choices is read off
afterward. When their expectations disagree, neither firm's choice
matches the other's, and both realize the miscoordination payoff.

Assumptions
-----------
- expected_other_action is read directly by ValuationRule.PAYOFF_MATRIX
  at decision time; it is a real input to valuation, not documentation
  the test author resolved by hand before building the agent.
- This test does not model endogenous belief formation or real-time
  strategic interaction; each firm's expectation about the counterpart
  is a fixed model input.
- Each firm correctly understands the payoff structure: the payoff
  matrix in V (PAYOFF_MATRIX, used for valuation) matches the actual
  payoff structure used by R (ACTUAL_PAYOFF_MATRIX, used to realize O)
  exactly. This is a simplifying assumption of this test, not a TER
  requirement -- a firm could misjudge the game's true payoffs, and R
  would still realize the actual ones.

Hypothesis
----------
1. Expecting standard A leads to choosing A.
2. Expecting standard B leads to choosing B.
3. (A, A) and (B, B) are both mutual best-response Nash equilibria of
   this one-shot game.
4. (A, A) Pareto-dominates (B, B) under the stated payoff structure.
5. Miscoordination produces lower payoffs than either coordinated
   equilibrium.
6. The same TER architecture represents all cases.
"""

import unittest

from research.ter import (
    AgentSpec,
    DecisionProcess,
    RealityFunction,
    Scenario,
    ValuationRule,
    run_scenario,
)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

STANDARD_A = "standard_a"
STANDARD_B = "standard_b"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

# V: what each firm believes the payoff structure is, used only for
# valuation (ValuationRule.PAYOFF_MATRIX).
PAYOFF_MATRIX = {
    STANDARD_A: {
        STANDARD_A: 4,
        STANDARD_B: 0,
    },
    STANDARD_B: {
        STANDARD_A: 0,
        STANDARD_B: 3,
    },
}

# R: the actual payoff structure used to realize O
# (RealityFunction.PAYOFF_MATRIX_OUTCOME). This test assumes each firm
# understands the game correctly, so this matches PAYOFF_MATRIX exactly
# -- but it is declared independently and read only by the reality
# side, never derived from any firm's own valuation.
ACTUAL_PAYOFF_MATRIX = {
    STANDARD_A: {
        STANDARD_A: 4,
        STANDARD_B: 0,
    },
    STANDARD_B: {
        STANDARD_A: 0,
        STANDARD_B: 3,
    },
}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="coordinating_agent",
    objective="maximize coordination payoff",
    model_of_reality={
        "expected_other_action": STANDARD_A,
    },
    valuation={
        "payoff_matrix": PAYOFF_MATRIX,
    },
    actual_feasible_set=[
        STANDARD_A,
        STANDARD_B,
    ],
    perceived_feasible_set=[
        STANDARD_A,
        STANDARD_B,
    ],
    valuation_rule=ValuationRule.PAYOFF_MATRIX,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current coordination decision",
)

AGENT_EXPECTING_A = BASE_AGENT.variant(
    name="agent_expecting_a",
    model_of_reality={
        "expected_other_action": STANDARD_A,
    },
)

AGENT_EXPECTING_B = BASE_AGENT.variant(
    name="agent_expecting_b",
    model_of_reality={
        "expected_other_action": STANDARD_B,
    },
)

# Two-firm pairings, each pair independently named agent_1/agent_2.
AGENT_1_EXPECTING_A = BASE_AGENT.variant(
    name="agent_1",
    model_of_reality={
        "expected_other_action": STANDARD_A,
    },
)

AGENT_2_EXPECTING_A = BASE_AGENT.variant(
    name="agent_2",
    model_of_reality={
        "expected_other_action": STANDARD_A,
    },
)

AGENT_1_EXPECTING_B = BASE_AGENT.variant(
    name="agent_1",
    model_of_reality={
        "expected_other_action": STANDARD_B,
    },
)

AGENT_2_EXPECTING_B = BASE_AGENT.variant(
    name="agent_2",
    model_of_reality={
        "expected_other_action": STANDARD_B,
    },
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

EXPECTS_A_SCENARIO = Scenario(
    name="Agent Expecting Standard A",
    description="A single agent values actions assuming the counterpart chooses standard A.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)

EXPECTS_B_SCENARIO = EXPECTS_A_SCENARIO.variant(
    name="Agent Expecting Standard B",
    description="A single agent values actions assuming the counterpart chooses standard B.",
    agents=[
        BASE_AGENT.variant(
            model_of_reality={
                "expected_other_action": STANDARD_B,
            },
        ),
    ],
)

BOTH_EXPECT_A_SCENARIO = EXPECTS_A_SCENARIO.variant(
    name="Two Agents, Both Expecting Standard A",
    description="Two independent agents, each expecting the other to adopt standard A.",
    agents=[
        AGENT_1_EXPECTING_A,
        AGENT_2_EXPECTING_A,
    ],
    parameters={
        "actual_payoff_matrix": ACTUAL_PAYOFF_MATRIX,
    },
    reality_function=RealityFunction.PAYOFF_MATRIX_OUTCOME,
)

BOTH_EXPECT_B_SCENARIO = EXPECTS_A_SCENARIO.variant(
    name="Two Agents, Both Expecting Standard B",
    description="Two independent agents, each expecting the other to adopt standard B.",
    agents=[
        AGENT_1_EXPECTING_B,
        AGENT_2_EXPECTING_B,
    ],
    parameters={
        "actual_payoff_matrix": ACTUAL_PAYOFF_MATRIX,
    },
    reality_function=RealityFunction.PAYOFF_MATRIX_OUTCOME,
)

MISCOORDINATION_SCENARIO = EXPECTS_A_SCENARIO.variant(
    name="Two Agents With Mismatched Expectations",
    description="One agent expects standard A, the other expects standard B.",
    agents=[
        AGENT_EXPECTING_A,
        AGENT_EXPECTING_B,
    ],
    parameters={
        "actual_payoff_matrix": ACTUAL_PAYOFF_MATRIX,
    },
    reality_function=RealityFunction.PAYOFF_MATRIX_OUTCOME,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCoordination(unittest.TestCase):
    TEST_NAME = "Test 06: Coordination and Multiple Equilibria"

    def test_expectation_of_standard_a_leads_to_standard_a(self):
        agent = run_scenario(EXPECTS_A_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            STANDARD_A,
        )

    def test_expectation_of_standard_b_leads_to_standard_b(self):
        agent = run_scenario(EXPECTS_B_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            STANDARD_B,
        )

    def test_different_expectations_produce_different_actions(self):
        expects_a = run_scenario(EXPECTS_A_SCENARIO).agent(BASE_AGENT.name)
        expects_b = run_scenario(EXPECTS_B_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            expects_a.selected_action,
            STANDARD_A,
        )

        self.assertEqual(
            expects_b.selected_action,
            STANDARD_B,
        )

        self.assertEqual(
            expects_a.objective,
            expects_b.objective,
        )

        self.assertEqual(
            expects_a.actual_feasible_set,
            expects_b.actual_feasible_set,
        )

    def test_both_coordinated_outcomes_are_equilibria(self):
        result_a = run_scenario(BOTH_EXPECT_A_SCENARIO)
        result_b = run_scenario(BOTH_EXPECT_B_SCENARIO)

        self.assertEqual(
            (
                result_a.agent(AGENT_1_EXPECTING_A.name).selected_action,
                result_a.agent(AGENT_2_EXPECTING_A.name).selected_action,
            ),
            (STANDARD_A, STANDARD_A),
        )

        self.assertEqual(
            (
                result_b.agent(AGENT_1_EXPECTING_B.name).selected_action,
                result_b.agent(AGENT_2_EXPECTING_B.name).selected_action,
            ),
            (STANDARD_B, STANDARD_B),
        )

        # Realized payoffs come from O (RealityFunction.
        # PAYOFF_MATRIX_OUTCOME), not from re-deriving them off
        # PAYOFF_MATRIX by hand.
        payoffs_a = result_a.final["payoffs"]
        payoffs_b = result_b.final["payoffs"]

        self.assertEqual(
            (
                payoffs_a[AGENT_1_EXPECTING_A.name],
                payoffs_a[AGENT_2_EXPECTING_A.name],
            ),
            (4, 4),
        )

        self.assertEqual(
            (
                payoffs_b[AGENT_1_EXPECTING_B.name],
                payoffs_b[AGENT_2_EXPECTING_B.name],
            ),
            (3, 3),
        )

    def test_one_equilibrium_can_dominate_another(self):
        payoffs_a = run_scenario(BOTH_EXPECT_A_SCENARIO).final["payoffs"]
        payoffs_b = run_scenario(BOTH_EXPECT_B_SCENARIO).final["payoffs"]

        self.assertGreater(
            payoffs_a[AGENT_1_EXPECTING_A.name],
            payoffs_b[AGENT_1_EXPECTING_B.name],
        )

        self.assertGreater(
            payoffs_a[AGENT_2_EXPECTING_A.name],
            payoffs_b[AGENT_2_EXPECTING_B.name],
        )

    def test_miscoordination_produces_lower_payoffs(self):
        result = run_scenario(MISCOORDINATION_SCENARIO)

        agent_a = result.agent(AGENT_EXPECTING_A.name)
        agent_b = result.agent(AGENT_EXPECTING_B.name)

        self.assertEqual(
            (agent_a.selected_action, agent_b.selected_action),
            (STANDARD_A, STANDARD_B),
        )

        # Realized payoffs come from O, not from re-deriving them off
        # PAYOFF_MATRIX by hand.
        miscoordinated = result.final["payoffs"]
        coordinated = run_scenario(BOTH_EXPECT_A_SCENARIO).final["payoffs"]

        self.assertEqual(
            (
                miscoordinated[AGENT_EXPECTING_A.name],
                miscoordinated[AGENT_EXPECTING_B.name],
            ),
            (0, 0),
        )

        self.assertGreater(
            coordinated[AGENT_1_EXPECTING_A.name],
            miscoordinated[AGENT_EXPECTING_A.name],
        )

        self.assertGreater(
            coordinated[AGENT_2_EXPECTING_A.name],
            miscoordinated[AGENT_EXPECTING_B.name],
        )

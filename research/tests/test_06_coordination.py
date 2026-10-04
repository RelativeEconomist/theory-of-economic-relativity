"""
TER Replication Test 06: Coordination and Multiple Equilibria
Canonical TER: theory/academic.md, Models 5.1 and 5.3

Economic question
-----------------
In a coordination game with multiple equilibria, does each firm's belief
about the counterpart's choice determine which standard it selects, and
which of several mutually consistent outcomes is realized when two firms
share a belief?

Scenario
--------
Two firms must each adopt one of two incompatible technology standards,
A or B. Compatibility, not intrinsic quality, determines payoff:

    both choose A          -> payoff 4 each
    both choose B          -> payoff 3 each
    different standards    -> payoff 0 each

This is a concrete instance of the general coordination mechanism:
whichever standard each firm expects the other to adopt, matching it is
that firm's best response.

Single-firm scenarios vary the firm's belief about the counterpart
(Model 5.1 only). Two-firm scenarios add R, which realizes payoffs from
both firms' selected actions (Model 5.3).

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize coordination payoff                   fixed
M   Model of Reality          expected_other_action: the firm's belief       varied (across
                              about which standard the counterpart will      scenarios)
                              adopt
F̂   Perceived Feasible Set    standard_a, standard_b                         fixed
V   Valuation                 payoff_matrix_value: the firm's own    fixed
                              perceived payoff_matrix, looked up against M
H   Time Horizon              current coordination decision                  fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           "standard_a" or "standard_b", one per firm     observed
F_t aspects used by R         actual_payoff_matrix: the scenario's own       fixed
                              payoff structure, a scenario-specified
                              condition R reads (not a complete
                              representation of F_t); two-firm scenarios
                              only
R   Reality Function          payoff_matrix_reality:                     fixed
                              realizes payoffs from both firms' selected
                              actions and actual_payoff_matrix, never from
                              any firm's V
O_{i,t} Agent Outcomes        each firm's realized payoff, derived from      observed
                              the one joint realization
Feedback (Model 5.5)          none                                           --

In the two-firm scenarios R takes both firms' selected actions together,
so Model 5.3 applies. Each firm's payoff depends on the other's action,
so it is an agent-level outcome derived from that same joint R (Model
5.3, "Agent-level outcomes"). No separate system outcome O_t is defined,
and no aggregation of the O_{i,t} into one.

Economic mechanism
------------------
payoff_matrix_value values matching the expected counterpart
standard above switching, so each firm's best response is simply to
adopt whichever standard it expects the other to adopt. When both firms
share the same expectation, (A, A) and (B, B) are both mutual
best-response Nash equilibria of this one-shot game -- neither firm can
do better by unilaterally switching, given the other's action. (A, A)
Pareto-dominates (B, B) under the stated payoff structure: both firms
are strictly better off. The two firms decide independently, each
applying the same valuation and decision process; the pairing of their
choices is read off afterward, and no equilibrium is computed. When
their expectations disagree, neither firm's choice matches the other's,
and both realize the miscoordination payoff.

Equilibrium concept: pure-strategy one-shot Nash equilibrium, verified
afterward against the stated payoff structure -- not embedded in R and
not reached through dynamics. Belief consistency: in each coordinated
scenario both firms expect the standard the counterpart actually
selects, so each expectation matches the realized profile. That
consistency is what makes each firm's best response to its expectation
also a best response to the counterpart's actual action.
In the miscoordination scenario expectations do not match the realized
profile, and the test does not call that profile an equilibrium.

Assumptions
-----------
- expected_other_action is read directly by payoff_matrix_value
  at decision time; it is a real input to valuation, not documentation
  the test author resolved by hand before building the agent.
- This test does not model endogenous belief formation or real-time
  strategic interaction; each firm's expectation about the counterpart
  is a fixed model input.
- Each firm correctly understands the payoff structure: the payoff
  matrix in V (PAYOFF_MATRIX, used for valuation) matches the actual
  payoff structure used by R (ACTUAL_PAYOFF_MATRIX, used to realize O_t)
  exactly. This is a simplifying assumption of this test, not a TER
  requirement -- a firm could misjudge the game's true payoffs, and R
  would still realize the actual ones.

Hypothesis
----------
In this configured scenario:
1. Expecting standard A leads to choosing A.
2. Expecting standard B leads to choosing B.
3. (A, A) and (B, B) are both mutual best-response Nash equilibria of
   this one-shot game.
4. (A, A) Pareto-dominates (B, B) under the stated payoff structure.
5. Miscoordination produces lower payoffs than either coordinated
   equilibrium.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import maximize_value, payoff_matrix_reality, payoff_matrix_value


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

STANDARD_A = "standard_a"
STANDARD_B = "standard_b"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

# V: what each firm believes the payoff structure is, used only for
# valuation (payoff_matrix_value).
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

# R: the actual payoff structure used to realize O_t
# (payoff_matrix_reality). This test assumes each firm
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
    perceived_feasible_set=[
        STANDARD_A,
        STANDARD_B,
    ],
    valuation_rule=payoff_matrix_value,
    decision_process=maximize_value,
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
    initial_state={},
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
    reality=payoff_matrix_reality,
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
    reality=payoff_matrix_reality,
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
    reality=payoff_matrix_reality,
)

def payoffs_of(result):
    """
    Each firm's realized payoff O_{i,t}, derived from the one joint R
    at the scenario's single decision point.
    """
    return {
        name: outcome["payoff"]
        for name, outcome in result.trace[-1].reality.agents.items()
    }


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

        # Scenario-premise check: only M differs between the two agents.
        self.assertEqual(
            expects_a.state.objective,
            expects_b.state.objective,
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

        # Realized payoffs come from O (payoff_matrix_reality), not
        # from re-deriving them off
        # PAYOFF_MATRIX by hand.
        payoffs_a = payoffs_of(result_a)
        payoffs_b = payoffs_of(result_b)

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
        payoffs_a = payoffs_of(run_scenario(BOTH_EXPECT_A_SCENARIO))
        payoffs_b = payoffs_of(run_scenario(BOTH_EXPECT_B_SCENARIO))

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
        miscoordinated = payoffs_of(result)
        coordinated = payoffs_of(run_scenario(BOTH_EXPECT_A_SCENARIO))

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

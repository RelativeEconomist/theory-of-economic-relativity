"""
TER Replication Test 05: Prisoner's Dilemma

Economic question
------------------
Can TER represent the standard Prisoner's Dilemma payoff structure and
dominant-strategy result using the same agent decision architecture?

Scenario
--------
Two players simultaneously choose COOPERATE or DEFECT. Each values the
outcome using its own belief about what the other will do:

    PAYOFF_MATRIX[own action][counterpart action]

        COOPERATE/COOPERATE = 3   COOPERATE/DEFECT = 0
        DEFECT/COOPERATE    = 5   DEFECT/DEFECT    = 1

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C ──→ O

    M   expected_other_action -- each player's belief about the
        counterpart's move
    V   payoff_matrix -- each player's own perceived payoff structure,
        used only to value actions (ValuationRule.PAYOFF_MATRIX)
    D   DecisionProcess.MAXIMIZE
    C   "cooperate" or "defect", one per player
    R   RealityFunction.PAYOFF_MATRIX_OUTCOME -- realizes payoffs from
        both players' actual selected actions and the scenario's own
        actual_payoff_matrix, never from any player's V
    O   each player's realized payoff

F equals F̂ throughout: both actions are always actually feasible.

Tested TER mechanics
--------------------
G   Objective              constant: maximize own payoff
M   Model of reality       expected_other_action -- CHANGED across
                            single-player scenarios
V   Valuation              payoff_matrix (perceived), looked up against M
D   Decision process       constant: DecisionProcess.MAXIMIZE
C   Selected action        observed result
R   Reality function       RealityFunction.PAYOFF_MATRIX_OUTCOME
O   Realized outcome       each player's realized payoff, from R

Economic mechanism
------------------
ValuationRule.PAYOFF_MATRIX values DEFECT above COOPERATE against either
belief about the counterpart, so DEFECT is strictly dominant for each
player under this payoff structure. When both players face that same
structure, (DEFECT, DEFECT) is the Nash equilibrium of this one-shot
game -- neither player can do better by unilaterally switching, given
the other's action. TER is not running a general equilibrium solver
here; the two independent players simply each apply the same dominant
strategy, and the pairing of their choices is read off afterward.

Assumptions
-----------
- expected_other_action is read directly by ValuationRule.PAYOFF_MATRIX
  at decision time; it is a real input to valuation, not documentation
  the test author resolved by hand before building the agent.
- This test does not model endogenous belief formation or real-time
  strategic interaction; each player's expectation about the
  counterpart is a fixed model input.
- Each player correctly understands the payoff structure: the payoff
  matrix in V (PAYOFF_MATRIX, used for valuation) matches the actual
  payoff structure used by R (ACTUAL_PAYOFF_MATRIX, used to realize O)
  exactly. This is a simplifying assumption of this test, not a TER
  requirement -- a player could misjudge the game's true payoffs, and R
  would still realize the actual ones.

Hypothesis
----------
1. Defection is preferred when the other agent cooperates.
2. Defection is preferred when the other agent defects.
3. Expected_other_action changes the valuation of defection itself, even
   though defection remains selected either way.
4. Defection is strictly dominant for each player, so (DEFECT, DEFECT)
   is the resulting one-shot Nash equilibrium.
5. Mutual cooperation would make both agents better off.
6. The same TER architecture represents all strategic cases.
7. The standard Prisoner's Dilemma payoff ordering is preserved.
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

COOPERATE = "cooperate"
DEFECT = "defect"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

# V: what each player believes the payoff structure is, used only for
# valuation (ValuationRule.PAYOFF_MATRIX).
PAYOFF_MATRIX = {
    COOPERATE: {
        COOPERATE: 3,
        DEFECT: 0,
    },
    DEFECT: {
        COOPERATE: 5,
        DEFECT: 1,
    },
}

# R: the actual payoff structure used to realize O
# (RealityFunction.PAYOFF_MATRIX_OUTCOME). This test assumes each
# player understands the game correctly, so this matches PAYOFF_MATRIX
# exactly -- but it is declared independently and read only by the
# reality side, never derived from any player's own valuation.
ACTUAL_PAYOFF_MATRIX = {
    COOPERATE: {
        COOPERATE: 3,
        DEFECT: 0,
    },
    DEFECT: {
        COOPERATE: 5,
        DEFECT: 1,
    },
}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_PLAYER = AgentSpec(
    name="player",
    objective="maximize own payoff",
    model_of_reality={
        "expected_other_action": COOPERATE,
    },
    valuation={
        "payoff_matrix": PAYOFF_MATRIX,
    },
    actual_feasible_set=[
        COOPERATE,
        DEFECT,
    ],
    perceived_feasible_set=[
        COOPERATE,
        DEFECT,
    ],
    valuation_rule=ValuationRule.PAYOFF_MATRIX,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="single interaction",
)

PLAYER_EXPECTING_DEFECTION_1 = BASE_PLAYER.variant(
    name="player_1",
    model_of_reality={
        "expected_other_action": DEFECT,
    },
)

PLAYER_EXPECTING_DEFECTION_2 = BASE_PLAYER.variant(
    name="player_2",
    model_of_reality={
        "expected_other_action": DEFECT,
    },
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

EXPECTS_COOPERATION_SCENARIO = Scenario(
    name="Player Expecting Cooperation",
    description="A single player values actions assuming the other player cooperates.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_PLAYER,
    ],
)

EXPECTS_DEFECTION_SCENARIO = EXPECTS_COOPERATION_SCENARIO.variant(
    name="Player Expecting Defection",
    description="A single player values actions assuming the other player defects.",
    agents=[
        BASE_PLAYER.variant(
            model_of_reality={
                "expected_other_action": DEFECT,
            },
        ),
    ],
)

MUTUAL_DEFECTION_SCENARIO = EXPECTS_COOPERATION_SCENARIO.variant(
    name="Two Players, Both Expecting Defection",
    description="Two independent players, each expecting the other to defect.",
    agents=[
        PLAYER_EXPECTING_DEFECTION_1,
        PLAYER_EXPECTING_DEFECTION_2,
    ],
    parameters={
        "actual_payoff_matrix": ACTUAL_PAYOFF_MATRIX,
    },
    reality_function=RealityFunction.PAYOFF_MATRIX_OUTCOME,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPrisonersDilemma(unittest.TestCase):
    TEST_NAME = "Test 05: Prisoner's Dilemma"

    def test_defection_is_preferred_if_other_agent_cooperates(self):
        agent = run_scenario(EXPECTS_COOPERATION_SCENARIO).agent(BASE_PLAYER.name)

        self.assertEqual(
            agent.selected_action,
            DEFECT,
        )

    def test_defection_is_preferred_if_other_agent_defects(self):
        agent = run_scenario(EXPECTS_DEFECTION_SCENARIO).agent(BASE_PLAYER.name)

        self.assertEqual(
            agent.selected_action,
            DEFECT,
        )

    def test_expected_other_action_changes_valuation_through_payoff_matrix(self):
        expects_cooperation = run_scenario(EXPECTS_COOPERATION_SCENARIO).agent(BASE_PLAYER.name)
        expects_defection = run_scenario(EXPECTS_DEFECTION_SCENARIO).agent(BASE_PLAYER.name)

        self.assertEqual(
            expects_cooperation.value_of(DEFECT),
            PAYOFF_MATRIX[DEFECT][COOPERATE],
        )

        self.assertEqual(
            expects_defection.value_of(DEFECT),
            PAYOFF_MATRIX[DEFECT][DEFECT],
        )

        self.assertNotEqual(
            expects_cooperation.value_of(DEFECT),
            expects_defection.value_of(DEFECT),
        )

    def test_defection_is_dominant_regardless_of_expectation(self):
        expects_cooperation = run_scenario(EXPECTS_COOPERATION_SCENARIO).agent(BASE_PLAYER.name)
        expects_defection = run_scenario(EXPECTS_DEFECTION_SCENARIO).agent(BASE_PLAYER.name)

        self.assertEqual(
            expects_cooperation.selected_action,
            DEFECT,
        )

        self.assertEqual(
            expects_defection.selected_action,
            DEFECT,
        )

    def test_two_agents_produce_mutual_defection_equilibrium(self):
        result = run_scenario(MUTUAL_DEFECTION_SCENARIO)

        player_1 = result.agent(PLAYER_EXPECTING_DEFECTION_1.name)
        player_2 = result.agent(PLAYER_EXPECTING_DEFECTION_2.name)

        self.assertEqual(
            (player_1.selected_action, player_2.selected_action),
            (DEFECT, DEFECT),
        )

        # Realized payoffs come from O (RealityFunction.
        # PAYOFF_MATRIX_OUTCOME), not from re-deriving them off
        # PAYOFF_MATRIX by hand.
        realized_payoffs = result.final["payoffs"]

        self.assertEqual(
            (
                realized_payoffs[PLAYER_EXPECTING_DEFECTION_1.name],
                realized_payoffs[PLAYER_EXPECTING_DEFECTION_2.name],
            ),
            (1, 1),
        )

    def test_mutual_cooperation_would_make_both_agents_better_off(self):
        mutual_defection = (
            PAYOFF_MATRIX[DEFECT][DEFECT],
            PAYOFF_MATRIX[DEFECT][DEFECT],
        )

        mutual_cooperation = (
            PAYOFF_MATRIX[COOPERATE][COOPERATE],
            PAYOFF_MATRIX[COOPERATE][COOPERATE],
        )

        self.assertGreater(
            mutual_cooperation[0],
            mutual_defection[0],
        )

        self.assertGreater(
            mutual_cooperation[1],
            mutual_defection[1],
        )

        self.assertEqual(
            mutual_cooperation,
            (3, 3),
        )

        self.assertEqual(
            mutual_defection,
            (1, 1),
        )

    def test_standard_payoff_ordering_is_preserved(self):
        temptation = PAYOFF_MATRIX[DEFECT][COOPERATE]
        reward = PAYOFF_MATRIX[COOPERATE][COOPERATE]
        punishment = PAYOFF_MATRIX[DEFECT][DEFECT]
        sucker = PAYOFF_MATRIX[COOPERATE][DEFECT]

        self.assertGreater(
            temptation,
            reward,
        )

        self.assertGreater(
            reward,
            punishment,
        )

        self.assertGreater(
            punishment,
            sucker,
        )

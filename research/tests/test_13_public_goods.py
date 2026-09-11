"""
TER Replication Test 13: Public Goods and Free Riding

Economic question
------------------
Can TER represent a public-goods setting where individual incentives
lead agents to free ride even though mutual contribution would produce
a better collective outcome?

Scenario
--------
Two neighboring businesses each decide whether to CONTRIBUTE to a
shared neighborhood improvement that benefits both, or FREE_RIDE on
whatever the other contributes:

    both contribute               -> 3 each
    contribute, other free rides  -> 0 (contributor), 5 (free rider)
    both free ride                -> 1 each

Each business values its own action against its belief about what the
other will do. This test abstracts the public good's actual provision
into this payoff structure alone; it does not separately model how the
improvement gets built or what it costs to provide.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C ──→ R ──→ O

    G   maximize own payoff from the contribution decision
    M   expected_other_action -- each business's belief about which
        action the counterpart will choose
    F̂   CONTRIBUTE, FREE_RIDE -- F equals F̂
    V   payoff_matrix -- each business's own perceived payoff
        structure, used only to value actions
        (ValuationRule.PAYOFF_MATRIX)
    H   single contribution decision
    D   DecisionProcess.MAXIMIZE
    C   "contribute" or "free_ride", one per business
    R   RealityFunction.PAYOFF_MATRIX_OUTCOME -- realizes payoffs from
        both businesses' actual selected actions and the scenario's
        own actual_payoff_matrix, never from any business's V
    O   each business's realized payoff

F equals F̂ throughout: both actions are always actually feasible.

Tested TER mechanics
--------------------
G     Objective              constant: maximize own payoff from the
                              contribution decision
M     Model of reality       expected_other_action -- CHANGED across
                              single-business scenarios
F, F̂  Feasible sets          CONTRIBUTE, FREE_RIDE; F̂ equals F
V     Valuation               payoff_matrix (perceived), looked up
                              against M
H     Time horizon           constant: single contribution decision
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        observed result
R     Reality function       RealityFunction.PAYOFF_MATRIX_OUTCOME
O     Realized outcome       each business's realized payoff, from R

Economic mechanism
------------------
ValuationRule.PAYOFF_MATRIX values FREE_RIDE above CONTRIBUTE against
either belief about the counterpart (5 > 3 if the other contributes;
1 > 0 if the other free rides), so FREE_RIDE is strictly preferred
against either counterpart action for each business under this payoff
structure. When both businesses face that same structure, mutual free
riding is the resulting one-shot Nash equilibrium -- neither business
can do better by unilaterally switching, given the other's action. TER
is not running a general equilibrium solver here; the two independent
businesses simply each apply the same dominant strategy, and the
pairing of their choices is read off afterward. Mutual contribution
would produce a higher combined payoff (3 + 3 = 6) than mutual free
riding (1 + 1 = 2), but is never the equilibrium outcome under this
payoff structure.

Assumptions
-----------
- expected_other_action is read directly by ValuationRule.PAYOFF_MATRIX at
  decision time; it is a real input to valuation, not documentation the
  test author resolved by hand before building the agent.
- This test does not model endogenous belief formation or real-time
  strategic interaction; each business's expectation about the
  counterpart is a fixed model input.
- The public-goods problem is represented through the payoff matrix; this
  test does not separately model production or provision of the public good.
- Each business correctly understands the payoff structure: the payoff
  matrix in V (PAYOFF_MATRIX, used for valuation) matches the actual
  payoff structure used by R (ACTUAL_PAYOFF_MATRIX, used to realize O)
  exactly. This is a simplifying assumption of this test, not a TER
  requirement -- declared independently, not aliased.
- Because FREE_RIDE strictly dominates CONTRIBUTE for each business
  under this payoff structure, no scenario driven by
  DecisionProcess.MAXIMIZE ever actually selects mutual contribution.
  The mutual-contribution comparison therefore reads the payoff
  directly off the actual payoff structure (ACTUAL_PAYOFF_MATRIX) as an
  explicitly labeled counterfactual -- what O would have been had both
  businesses contributed -- not a realized outcome from an executed
  scenario, and not a lookup into the perceived/valuation PAYOFF_MATRIX.

Hypothesis
----------
1. Expecting contribution leads the agent to prefer FREE_RIDE.
2. Expecting free riding also leads the agent to prefer FREE_RIDE.
3. Expected_other_action changes the valuation of free riding itself, even
   though free riding remains selected either way.
4. FREE_RIDE is strictly preferred against either counterpart action
   under this specified payoff structure, so mutual free riding is the
   one-shot Nash equilibrium.
5. Mutual contribution would produce a higher combined payoff than
   mutual free riding.
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

CONTRIBUTE = "contribute"
FREE_RIDE = "free_ride"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

MUTUAL_CONTRIBUTION_PAYOFF = 3
CONTRIBUTE_WHILE_OTHER_FREE_RIDES_PAYOFF = 0
FREE_RIDE_WHILE_OTHER_CONTRIBUTES_PAYOFF = 5
MUTUAL_FREE_RIDING_PAYOFF = 1

# V: what each business believes the payoff structure is, used only for
# valuation (ValuationRule.PAYOFF_MATRIX).
PAYOFF_MATRIX = {
    CONTRIBUTE: {
        CONTRIBUTE: MUTUAL_CONTRIBUTION_PAYOFF,
        FREE_RIDE: CONTRIBUTE_WHILE_OTHER_FREE_RIDES_PAYOFF,
    },
    FREE_RIDE: {
        CONTRIBUTE: FREE_RIDE_WHILE_OTHER_CONTRIBUTES_PAYOFF,
        FREE_RIDE: MUTUAL_FREE_RIDING_PAYOFF,
    },
}

# R: the actual payoff structure used to realize O
# (RealityFunction.PAYOFF_MATRIX_OUTCOME). This test assumes each
# business understands the game correctly, so this matches
# PAYOFF_MATRIX exactly -- but it is declared independently and read
# only by the reality side, never derived from any business's own
# valuation.
ACTUAL_PAYOFF_MATRIX = {
    CONTRIBUTE: {
        CONTRIBUTE: MUTUAL_CONTRIBUTION_PAYOFF,
        FREE_RIDE: CONTRIBUTE_WHILE_OTHER_FREE_RIDES_PAYOFF,
    },
    FREE_RIDE: {
        CONTRIBUTE: FREE_RIDE_WHILE_OTHER_CONTRIBUTES_PAYOFF,
        FREE_RIDE: MUTUAL_FREE_RIDING_PAYOFF,
    },
}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="agent",
    objective="maximize own payoff from the contribution decision",
    model_of_reality={
        "expected_other_action": CONTRIBUTE,
    },
    valuation={
        "payoff_matrix": PAYOFF_MATRIX,
    },
    actual_feasible_set=[
        CONTRIBUTE,
        FREE_RIDE,
    ],
    perceived_feasible_set=[
        CONTRIBUTE,
        FREE_RIDE,
    ],
    valuation_rule=ValuationRule.PAYOFF_MATRIX,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="single contribution decision",
)

AGENT_1 = BASE_AGENT.variant(
    name="agent_1",
    model_of_reality={
        "expected_other_action": FREE_RIDE,
    },
)

AGENT_2 = BASE_AGENT.variant(
    name="agent_2",
    model_of_reality={
        "expected_other_action": FREE_RIDE,
    },
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

EXPECTS_CONTRIBUTION_SCENARIO = Scenario(
    name="Agent Expecting Contribution",
    description="A single agent values actions assuming the other agent contributes.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)

EXPECTS_FREE_RIDING_SCENARIO = EXPECTS_CONTRIBUTION_SCENARIO.variant(
    name="Agent Expecting Free Riding",
    description="A single agent values actions assuming the other agent free rides.",
    agents=[
        BASE_AGENT.variant(
            model_of_reality={
                "expected_other_action": FREE_RIDE,
            },
        ),
    ],
)

MUTUAL_FREE_RIDING_SCENARIO = EXPECTS_CONTRIBUTION_SCENARIO.variant(
    name="Two Agents, Both Expecting Free Riding",
    description="Two independent agents, each expecting the other to free ride.",
    agents=[
        AGENT_1,
        AGENT_2,
    ],
    parameters={
        "actual_payoff_matrix": ACTUAL_PAYOFF_MATRIX,
    },
    reality_function=RealityFunction.PAYOFF_MATRIX_OUTCOME,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPublicGoods(unittest.TestCase):
    TEST_NAME = "Test 13: Public Goods and Free Riding"

    def test_expecting_contribution_leads_to_free_riding(self):
        agent = run_scenario(EXPECTS_CONTRIBUTION_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            FREE_RIDE,
        )

    def test_expecting_free_riding_also_leads_to_free_riding(self):
        agent = run_scenario(EXPECTS_FREE_RIDING_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            FREE_RIDE,
        )

    def test_expected_other_action_changes_valuation_through_payoff_matrix(self):
        expects_contribution = run_scenario(EXPECTS_CONTRIBUTION_SCENARIO).agent(BASE_AGENT.name)
        expects_free_riding = run_scenario(EXPECTS_FREE_RIDING_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            expects_contribution.value_of(FREE_RIDE),
            PAYOFF_MATRIX[FREE_RIDE][CONTRIBUTE],
        )

        self.assertEqual(
            expects_free_riding.value_of(FREE_RIDE),
            PAYOFF_MATRIX[FREE_RIDE][FREE_RIDE],
        )

        self.assertNotEqual(
            expects_contribution.value_of(FREE_RIDE),
            expects_free_riding.value_of(FREE_RIDE),
        )

    def test_mutual_free_riding_is_the_individually_selected_outcome(self):
        result = run_scenario(MUTUAL_FREE_RIDING_SCENARIO)

        agent_1 = result.agent(AGENT_1.name)
        agent_2 = result.agent(AGENT_2.name)

        self.assertEqual(
            (agent_1.selected_action, agent_2.selected_action),
            (FREE_RIDE, FREE_RIDE),
        )

        # Realized payoffs come from O (RealityFunction.
        # PAYOFF_MATRIX_OUTCOME), not from re-deriving them off
        # PAYOFF_MATRIX by hand.
        realized_payoffs = result.final["payoffs"]

        self.assertEqual(
            (
                realized_payoffs[AGENT_1.name],
                realized_payoffs[AGENT_2.name],
            ),
            (1, 1),
        )

    def test_mutual_contribution_would_produce_higher_combined_payoff(self):
        # FREE_RIDE strictly dominates CONTRIBUTE under this payoff
        # structure (see Assumptions), so no MAXIMIZE-driven scenario
        # ever actually selects mutual contribution. This counterfactual
        # payoff is read directly off the actual payoff structure (R),
        # never the perceived/valuation PAYOFF_MATRIX.
        counterfactual_mutual_contribution_payoff = (
            ACTUAL_PAYOFF_MATRIX[CONTRIBUTE][CONTRIBUTE] * 2
        )

        # Mutual free riding, by contrast, is a real, realized outcome:
        # read from O, not from PAYOFF_MATRIX.
        realized_payoffs = run_scenario(MUTUAL_FREE_RIDING_SCENARIO).final["payoffs"]
        realized_mutual_free_riding_payoff = (
            realized_payoffs[AGENT_1.name] + realized_payoffs[AGENT_2.name]
        )

        self.assertGreater(
            counterfactual_mutual_contribution_payoff,
            realized_mutual_free_riding_payoff,
        )

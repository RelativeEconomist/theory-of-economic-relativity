"""
TER Replication Test 13: Public Goods and Free Riding
Canonical TER: theory/academic.md, Models 5.1 and 5.3

Economic question
-----------------
In a public-goods payoff structure where mutual contribution would produce
a higher combined payoff than mutual free riding, does each business's own
valuation lead it to free ride?

Scenario
--------
Two neighboring businesses each decide whether to CONTRIBUTE to a
shared neighborhood improvement that benefits both, or FREE_RIDE on
whatever the other contributes:

    both contribute               -> 3 each
    contribute, other free rides  -> 0 (contributor), 5 (free rider)
    both free ride                -> 1 each

Each business values its own action against its belief about what the
other will do. This test abstracts the public good's provision into this
payoff structure alone; it does not separately model how the improvement
gets built or what it costs to provide.

Single-business scenarios vary the business's belief about the
counterpart (Model 5.1 only). One two-business scenario adds R, which
realizes payoffs from both businesses' selected actions (Model 5.3).

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize own payoff from the contribution      fixed
                              decision
M   Model of Reality          expected_other_action: the business's belief   varied (across the
                              about which action the counterpart will        single-business
                              choose                                         scenarios)
F̂   Perceived Feasible Set    CONTRIBUTE, FREE_RIDE                          fixed
V   Valuation                 payoff_matrix_value: the business's    fixed
                              own perceived payoff_matrix, looked up
                              against M
H   Time Horizon              single contribution decision                   fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           "contribute" or "free_ride", one per business  observed
F_t aspects used by R         actual_payoff_matrix: the scenario's own       fixed
                              payoff structure, a scenario-specified
                              condition R reads (not a complete
                              representation of F_t); two-business
                              scenario only
R   Reality Function          payoff_matrix_reality:                     fixed
                              realizes payoffs from both businesses'
                              selected actions and actual_payoff_matrix,
                              never from any business's V
O_{i,t} Agent Outcomes        each business's realized payoff, derived       observed
                              from the one joint realization
Feedback (Model 5.5)          none                                           --

In the two-business scenario R takes both businesses' selected actions
together, so Model 5.3 applies. Each business's payoff depends on the
other's action, so it is an agent-level outcome derived from that same
joint R (Model 5.3, "Agent-level outcomes"). No separate system outcome
O_t is defined, and no aggregation of the O_{i,t} into one.

Economic mechanism
------------------
payoff_matrix_value values FREE_RIDE above CONTRIBUTE against
either belief about the counterpart (5 > 3 if the other contributes;
1 > 0 if the other free rides), so FREE_RIDE is strictly preferred
against either counterpart action for each business under this payoff
structure. When both businesses face that same structure, mutual free
riding is the resulting one-shot Nash equilibrium -- neither business
can do better by unilaterally switching, given the other's action. The
two businesses decide independently, each applying the same valuation
and decision process; the pairing of their choices is read off
afterward, and no equilibrium is computed. Mutual contribution would
produce a higher combined payoff (3 + 3 = 6) than mutual free riding
(1 + 1 = 2), but is not selected under this payoff structure. The
combined payoff is a sum computed by this test, not an output of R.

Equilibrium concept: pure-strategy one-shot Nash equilibrium, verified
afterward against the stated payoff structure -- not embedded in R and
not reached through dynamics. Belief consistency: in the two-business
scenario each business expects FREE_RIDE and the counterpart selects
FREE_RIDE, so each expectation matches the realized profile. Because
FREE_RIDE is strictly dominant, the equilibrium does not depend on that
consistency.

Assumptions
-----------
- expected_other_action is read directly by payoff_matrix_value at
  decision time; it is a real input to valuation, not documentation the
  test author resolved by hand before building the agent.
- This test does not model endogenous belief formation or real-time
  strategic interaction; each business's expectation about the
  counterpart is a fixed model input.
- The public-goods problem is represented through the payoff matrix; this
  test does not separately model production or provision of the public good.
- Each business correctly understands the payoff structure: the payoff
  matrix in V (PAYOFF_MATRIX, used for valuation) matches the actual
  payoff structure used by R (ACTUAL_PAYOFF_MATRIX, used to realize O_t)
  exactly. This is a simplifying assumption of this test, not a TER
  requirement -- declared independently, not aliased.
- Because FREE_RIDE strictly dominates CONTRIBUTE for each business
  under this payoff structure, no scenario driven by
  maximize_value selects mutual contribution. The
  mutual-contribution comparison therefore reads the payoff directly off
  the actual payoff structure (ACTUAL_PAYOFF_MATRIX) as an explicitly
  labeled counterfactual -- the payoff both businesses would receive had
  both contributed -- not a realized outcome from an executed scenario,
  and not a lookup into the perceived/valuation PAYOFF_MATRIX.

Hypothesis
----------
In this configured scenario:
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

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import maximize_value, payoff_matrix_reality, payoff_matrix_value


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
# valuation (payoff_matrix_value).
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

# R: the actual payoff structure used to realize O_t
# (payoff_matrix_reality). This test assumes each
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
    perceived_feasible_set=[
        CONTRIBUTE,
        FREE_RIDE,
    ],
    valuation_rule=payoff_matrix_value,
    decision_process=maximize_value,
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
    initial_state={},
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
    reality=payoff_matrix_reality,
)

def payoffs_of(result):
    """
    Each business's realized payoff O_{i,t}, derived from the one joint R
    at the scenario's single decision point.
    """
    return {
        name: outcome["payoff"]
        for name, outcome in result.trace[-1].reality.agents.items()
    }


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

        # Realized payoffs come from O (payoff_matrix_reality), not
        # from re-deriving them off
        # PAYOFF_MATRIX by hand.
        realized_payoffs = payoffs_of(result)

        self.assertEqual(
            (
                realized_payoffs[AGENT_1.name],
                realized_payoffs[AGENT_2.name],
            ),
            (1, 1),
        )

    def test_mutual_contribution_would_produce_higher_combined_payoff(self):
        # FREE_RIDE strictly dominates CONTRIBUTE under this payoff
        # structure (see Assumptions), so no maximize_value-driven scenario
        # ever actually selects mutual contribution. This counterfactual
        # payoff is a re-run of the same joint R with both actions
        # replaced -- the actual payoff structure, never the
        # perceived/valuation PAYOFF_MATRIX -- and is not another
        # realized outcome.
        result = run_scenario(MUTUAL_FREE_RIDING_SCENARIO)

        counterfactual = result.counterfactual(
            0,
            {
                AGENT_1.name: CONTRIBUTE,
                AGENT_2.name: CONTRIBUTE,
            },
        )
        counterfactual_mutual_contribution_payoff = (
            counterfactual.agent(AGENT_1.name)["payoff"]
            + counterfactual.agent(AGENT_2.name)["payoff"]
        )

        self.assertEqual(
            counterfactual_mutual_contribution_payoff,
            ACTUAL_PAYOFF_MATRIX[CONTRIBUTE][CONTRIBUTE] * 2,
        )

        # Mutual free riding, by contrast, is a real, realized outcome:
        # read from O, not from PAYOFF_MATRIX.
        realized_payoffs = payoffs_of(result)
        realized_mutual_free_riding_payoff = (
            realized_payoffs[AGENT_1.name] + realized_payoffs[AGENT_2.name]
        )

        self.assertGreater(
            counterfactual_mutual_contribution_payoff,
            realized_mutual_free_riding_payoff,
        )

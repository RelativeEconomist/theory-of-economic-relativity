"""
TER Replication Test 25: Multi-Agent System Outcome
Canonical TER: theory/academic.md, Model 5.3 (Multi Agent Model)

Economic question
------------------
Two buyers and one seller each independently select the action their own
TER decision architecture values most, and each selected action is, on
its own, permitted by the objective feasible state of reality. Only one
unit exists. Can a reality function resolve that scarcity into a single
system outcome, without either buyer's own decision ever selecting that
outcome?

TER mapping
-----------
    C_{i,t} = D_{i,t}(F_hat_{i,t}, G_{i,t}, M_{i,t}, V_{i,t}, H_{i,t})

Agent      G Objective                  M                     F_hat                V (mapped_value)   D -> C
buyer_a    acquire one unit at          trade is available   [buy_8,              prefers buy_8       maximize_value
           acceptable value                                  do_not_buy]                              -> buy_8
buyer_b    acquire one unit at          trade is available   [buy_10,             prefers buy_10      maximize_value
           acceptable value                                  do_not_buy]                              -> buy_10
seller_s   sell one unit at             buyers are            [sell_5, hold]       prefers sell_5      maximize_value
           acceptable value             available                                                     -> sell_5

H is "current period" for all three; not repeated per row above.

F_t is not agent specific. It is carried by the scenario's own `state`
and `parameters`, never by any agent's F_hat, M, V, or D:

- state["permitted_actions"] indexes which action F_t permits each agent
  individually (an implementation index of F_t, not F_t itself -- see
  research.ter.outcome).
- parameters["unit_supply"] = 1: only one unit exists and can actually be
  transferred. parameters["seller"] and parameters["sell_action"] name
  which agent and action actually transfers it.

The amount named by a buy action (buy_8 pays 8, buy_10 pays 10) is part
of what that selected action C itself means, not a separate fact of F_t.
R below decodes it directly from the action string; F_t is never asked
"what does this buyer offer."

R (reality_function="single_unit_market_outcome", registered locally
below -- this test's own admissible specification of R, not a universal
TER consequence rule):

    O_t = R(C_{buyer_a,t}, C_{buyer_b,t}, C_{seller_s,t}, F_t)

It keeps only the selected actions F_t individually permits
(is_actually_feasible), decodes each permitted buy action's amount from
C, checks whether the seller's transfer action was selected, and --
because F_t supplies only one unit -- allocates it to the higher bid via
research.ter.market.allocate_single_unit (a small, scenario-agnostic
"give the scarce unit to the highest bidder" helper; it raises ValueError
on a tie rather than resolving one, which does not arise here since
8 != 10).

O_t is the flat dict single_unit_market_outcome returns (quantity, buyer,
seller, unmatched_buyers), reported directly as scenario state
(ScenarioResult.final) rather than under "agent_results" -- so it is one
system outcome, not an aggregation of any per-agent O_{i,t} (none is
defined for any agent here).

Scenario
--------
Buyer A's action proposes to pay 8; Buyer B's proposes to pay 10; Seller
S's action transfers a unit at 5. Exactly one unit exists. All three
agents decide in the same period, independently -- no agent's M
references the others' actions.

Tested TER mechanics
---------------------
1. Each agent independently selects C_i = D_i(F_hat_i, G_i, M_i, V_i, H_i).
2. Each selected action (buy_8, buy_10, sell_5) is individually permitted
   by F_t -- but individual permission is not joint feasibility: F_t
   supplies only one unit, so buy_8 and buy_10 cannot both be realized.
3. R resolves that interaction and scarcity into one system outcome O_t.
4. No individual agent directly selects O_t -- Buyer A's own C_a remains
   buy_8; "unmatched" is a fact O_t reports about how buy_8 fared once it
   met F_t and Buyer B's competing buy_10, not an action Buyer A chose.

Economic mechanism
-------------------
Each buyer values transacting over not transacting; neither buyer's
valuation encodes the other buyer's proposed amount or the seller's
action. Because only one unit can actually be transferred, R allocates it
to the higher of the two individually permitted buy actions (10 over 8)
only after both have been selected.

Assumptions
-----------
- Each buyer's valuation (mapped_value) encodes only an ordinal
  preference for transacting over not transacting (1 vs. 0), not the
  amount it offers -- that amount is read from the action itself. TER
  does not require these to coincide; keeping them apart is what lets
  this test show that individual permission is not the same thing as
  joint feasibility.
- Single period, no feedback rule, and a deterministic decision process
  (maximize_value): no multi-period dynamics and no stochastic behavior.

Hypothesis
----------
In this configured scenario:
1. Buyer A selects buy_8, Buyer B selects buy_10, Seller S selects sell_5.
2. All three selected actions are individually permitted by F_t.
3. The system quantity actually transferred is exactly 1, not 2, despite
   two individually permitted buy actions.
4. Buyer B receives the unit and Seller S sells it; Buyer A is unmatched.
5. No agent's own outcome record defines a system-level result -- only
   O_t (ScenarioResult.final) does.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario
from research.ter.market import allocate_single_unit
from research.ter.outcome import is_actually_feasible
from research.ter.rules import register_rule


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

BUY_8 = "buy_8"
BUY_10 = "buy_10"
DO_NOT_BUY = "do_not_buy"

SELL_5 = "sell_5"
HOLD = "hold"


# ---------------------------------------------------------------------------
# Reality function (R) -- scoped to this test, like
# capacity_constrained_realization in test_feasibility_contract.py
# ---------------------------------------------------------------------------

@register_rule("single_unit_market_outcome")
def single_unit_market_outcome(state, agents, actions, parameters):
    """
    One admissible TER Model 5.3 reality function for this test only.

    Keeps only the selected actions F_t individually permits
    (is_actually_feasible), then decodes each permitted buy_<amount>
    action's amount directly from the action itself -- that amount is
    part of what C means, not a fact read from F_t. Because only one
    unit can actually be transferred (parameters["unit_supply"]),
    allocates it to the higher decoded amount via allocate_single_unit.

    Returns a flat dict: O_t, the single system outcome, never reported
    under "agent_results" -- so no O_{i,t} is defined for any agent here.

    Required parameters:

        seller         the name of the agent who can transfer the unit
        sell_action    the action that transfers the unit, if selected
        unit_supply    how many units can actually be transferred (1)
    """
    permitted = {
        agent.name: action
        for agent, action in zip(agents, actions)
        if is_actually_feasible(state, agent, action)
    }

    seller_name = parameters["seller"]
    sell_action = parameters["sell_action"]

    competing_bids = {
        name: int(action.rsplit("_", 1)[1])
        for name, action in permitted.items()
        if action.startswith("buy_")
    }

    seller_ready = permitted.get(seller_name) == sell_action

    winner = allocate_single_unit(competing_bids) if seller_ready else None

    return {
        "quantity": parameters["unit_supply"] if winner else 0,
        "buyer": winner,
        "seller": seller_name if winner else None,
        "unmatched_buyers": [
            name
            for name in competing_bids
            if name != winner
        ],
    }


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BUYER_A = AgentSpec(
    name="buyer_a",
    objective="acquire one unit at acceptable value",
    model_of_reality={
        "trade_available": True,
    },
    valuation={
        "values": {
            BUY_8: 1,
            DO_NOT_BUY: 0,
        },
    },
    perceived_feasible_set=[
        BUY_8,
        DO_NOT_BUY,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current period",
)


BUYER_B = AgentSpec(
    name="buyer_b",
    objective="acquire one unit at acceptable value",
    model_of_reality={
        "trade_available": True,
    },
    valuation={
        "values": {
            BUY_10: 1,
            DO_NOT_BUY: 0,
        },
    },
    perceived_feasible_set=[
        BUY_10,
        DO_NOT_BUY,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current period",
)


SELLER_S = AgentSpec(
    name="seller_s",
    objective="sell one unit at acceptable value",
    model_of_reality={
        "buyers_available": True,
    },
    valuation={
        "values": {
            SELL_5: 1,
            HOLD: 0,
        },
    },
    perceived_feasible_set=[
        SELL_5,
        HOLD,
    ],
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current period",
)


# ---------------------------------------------------------------------------
# F_t and scenario
# ---------------------------------------------------------------------------

# Implementation index of the scenario-relevant aspects of F_t: which
# actions F_t permits each agent individually. Not F_t itself, and not a
# TER primitive -- see research.ter.outcome.
PERMITTED_ACTIONS = {
    BUYER_A.name: [BUY_8, DO_NOT_BUY],
    BUYER_B.name: [BUY_10, DO_NOT_BUY],
    SELLER_S.name: [SELL_5, HOLD],
}


SCENARIO = Scenario(
    name="Single-Unit Market",
    description=(
        "Two buyers and one seller each independently select the action "
        "their own decision process values most. Only one unit exists, "
        "so R must resolve which individually permitted buy action is "
        "actually realized."
    ),
    periods=1,
    initial_state={
        "period": 0,
        "permitted_actions": PERMITTED_ACTIONS,
    },
    agents=[
        BUYER_A,
        BUYER_B,
        SELLER_S,
    ],
    parameters={
        "unit_supply": 1,
        "seller": SELLER_S.name,
        "sell_action": SELL_5,
    },
    reality_function="single_unit_market_outcome",
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMultiAgentSystemOutcome(unittest.TestCase):
    TEST_NAME = "Test 25: Multi-Agent System Outcome"

    def test_each_agent_independently_selects_its_own_action(self):
        result = run_scenario(SCENARIO)

        self.assertEqual(
            result.agent(BUYER_A.name).selected_action,
            BUY_8,
        )

        self.assertEqual(
            result.agent(BUYER_B.name).selected_action,
            BUY_10,
        )

        self.assertEqual(
            result.agent(SELLER_S.name).selected_action,
            SELL_5,
        )

    def test_every_selected_action_is_individually_permitted_by_f_t(self):
        result = run_scenario(SCENARIO)
        state = {"permitted_actions": PERMITTED_ACTIONS}

        for agent_name in (BUYER_A.name, BUYER_B.name, SELLER_S.name):
            agent = result.agent(agent_name)

            self.assertTrue(
                is_actually_feasible(state, agent.state, agent.selected_action)
            )

    def test_individually_permitted_joint_profile_cannot_be_fully_realized(self):
        result = run_scenario(SCENARIO)

        # Both buy_8 and buy_10 are each individually permitted (previous
        # test), yet only one unit can actually be transferred.
        self.assertEqual(
            result.final["quantity"],
            1,
        )

        self.assertLess(
            result.final["quantity"],
            2,
        )

    def test_reality_resolves_scarcity_into_one_system_outcome(self):
        result = run_scenario(SCENARIO)

        self.assertEqual(
            result.final["buyer"],
            BUYER_B.name,
        )

        self.assertEqual(
            result.final["seller"],
            SELLER_S.name,
        )

        self.assertEqual(
            result.final["unmatched_buyers"],
            [BUYER_A.name],
        )

    def test_no_individual_agent_selects_the_system_outcome(self):
        result = run_scenario(SCENARIO)
        buyer_a = result.agent(BUYER_A.name)

        # Buyer A's own selected action is buy_8 -- it never selects
        # "unmatched". Being unmatched is a fact O_t reports about how
        # buy_8 fared once it met F_t and Buyer B's competing buy_10, not
        # an action any agent chose.
        self.assertEqual(
            buyer_a.selected_action,
            BUY_8,
        )

        self.assertIn(
            BUYER_A.name,
            result.final["unmatched_buyers"],
        )

        # No per-agent O_{i,t} is defined for any agent -- only the
        # system-level O_t (result.final) is.
        for agent_name in (BUYER_A.name, BUYER_B.name, SELLER_S.name):
            self.assertEqual(
                result.agent(agent_name).outcome,
                {},
            )

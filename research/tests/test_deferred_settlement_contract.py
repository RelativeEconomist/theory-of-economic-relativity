"""A standing buy order can settle later without a new choice by its owner."""

import unittest

from research.ter import AgentSpec, RealityResult, Scenario, Schedule, run_scenario
from research.ter.rules import first_feasible, mapped_value


BUY_LIMIT = 10
MATCHING_ASK = 9
HIGHER_ASK = 11
LOWER_LIMIT = 8


def realize_order(actions, objective_state, parameters):
    """Accept the bid first, then match the seller against the carried order."""
    if "buyer" in actions:
        return RealityResult(system={"accepted_limit": actions["buyer"], "quantity": 0})

    limit = objective_state["resting_limit"]
    ask = actions["seller"]
    if limit is None or ask > limit or objective_state["inventory"] == 0:
        return RealityResult(system={"quantity": 0})

    return RealityResult(
        system={"quantity": 1, "price": ask},
        agents={"buyer": {"paid": ask}, "seller": {"received": ask}},
    )


def carry_order(objective_state, reality, parameters):
    if "accepted_limit" in reality.system:
        objective_state["resting_limit"] = reality.system["accepted_limit"]
    elif reality.system["quantity"]:
        objective_state["resting_limit"] = None
        objective_state["inventory"] -= reality.system["quantity"]
    return objective_state


class TestDeferredSettlementContract(unittest.TestCase):
    TEST_NAME = "Framework: Deferred Settlement Contract"

    def test_standing_order_settles_without_a_new_buyer_action(self):
        buyer = AgentSpec(
            name="buyer", objective="buy one unit", model_of_reality={},
            perceived_feasible_set=[BUY_LIMIT], valuation_rule=mapped_value,
            decision_process=first_feasible,
        )
        seller = buyer.variant(name="seller", objective="sell one unit", perceived_feasible_set=[MATCHING_ASK, HIGHER_ASK])
        scenario = Scenario(
            name="Standing buy order", description="The seller arrives after a limit order is accepted.",
            periods=2, initial_state={"resting_limit": None, "inventory": 1},
            agents=[buyer, seller], schedule=Schedule.sequential("buyer", "seller"),
            reality=realize_order, transition=carry_order,
        )

        result = run_scenario(scenario)
        accepted, settlement = result.trace
        self.assertEqual(dict(accepted.actions), {"buyer": BUY_LIMIT})
        self.assertEqual(dict(accepted.reality.system), {"accepted_limit": BUY_LIMIT, "quantity": 0})
        self.assertEqual(result.trace.objective_state_before(1)["resting_limit"], BUY_LIMIT)
        self.assertEqual(dict(settlement.actions), {"seller": MATCHING_ASK})
        self.assertEqual(settlement.reality.agent("buyer")["paid"], MATCHING_ASK)
        self.assertEqual(settlement.reality.agent("seller")["received"], MATCHING_ASK)
        self.assertEqual(settlement.reality.system["quantity"], 1)
        self.assertEqual(result.final["inventory"], 0)

        later_replay = result.counterfactual(1, {"seller": HIGHER_ASK})
        self.assertEqual(later_replay.system["quantity"], 0)

        earlier_replay = result.counterfactual(0, {"buyer": LOWER_LIMIT})
        self.assertEqual(earlier_replay.system["accepted_limit"], LOWER_LIMIT)
        changed_path = run_scenario(scenario.variant(agents=[buyer.variant(perceived_feasible_set=[LOWER_LIMIT]), seller]))
        self.assertEqual(changed_path.trace[1].reality.system["quantity"], 0)
        self.assertEqual(changed_path.final["inventory"], 1)

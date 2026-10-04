"""
TER Test Template: Buying at an Unexpected Price
Canonical TER: theory/academic.md, Models 5.1 and 5.2

Copy to research/tests/test_NN_<topic>.py, replace the example, and check
it against research/templates/TEST_VERIFICATION.md.
Run: python3 -m unittest research.templates.ter_test_template -v

Purpose
-------
The buyer expects the price to be 6, so it chooses to buy. The actual
price is 12, so the realized outcome is worse than expected. The error is
in the buyer's belief, not in its decision.

TER mapping
-----------
Symbol  Status    In this example
G       fixed     gain from buying the good
M       fixed     expected price: 6
F̂       fixed     buy, do not buy
V       fixed     the good's worth to the buyer (10) minus the expected price
H       fixed     this purchase only
D       fixed     choose the highest-valued action
F_t     varied    actual price: 12 (6 in the comparison run)
R       fixed     a buy order fills at the actual price
C       observed  the action the buyer chose
O       observed  quantity bought and price paid

Assumptions
-----------
- The price is set after the buyer chooses and before the order fills.
- A buy order always fills, at whatever the actual price is.
- One buyer, one period.

Hypothesis
----------
1. The buyer buys, because at the expected price buying is worth more
   than not buying.
2. The buyer pays the actual price, which is more than the good is worth
   to it.
3. Changing only the actual price changes what the buyer pays, not what
   it chooses.
"""

import unittest

from research.ter import AgentSpec, RealityResult, Scenario, run_scenario
from research.ter.rules import maximize_value, price_taking_value


# Agent

BUY = "buy"
DO_NOT_BUY = "do_not_buy"

GOOD_VALUE = 10
EXPECTED_PRICE = 6

BUYER = AgentSpec(
    name="buyer",
    objective="gain from buying the good",
    # M: what the buyer believes the price will be. It can be wrong.
    model_of_reality={"price": EXPECTED_PRICE},
    # F̂: actions the buyer thinks it can try, not what reality allows.
    perceived_feasible_set=[BUY, DO_NOT_BUY],
    # V: what the good is worth to the buyer, a preference, not a belief.
    valuation={
        "benefits": {BUY: GOOD_VALUE},
        "price_taking_action": BUY,
        "price_role": "cost",
    },
    valuation_rule=price_taking_value,
    # D chooses from what the buyer believes. The actual price is never an
    # input; it can affect the choice only through M.
    decision_process=maximize_value,
    horizon="this purchase",
)


# Reality / Scenario

# F_t: settled after the buyer chooses, so it is a fact about reality, not
# a belief.
ACTUAL_PRICE = 12


def fill_buy_order(actions, objective_state, parameters):
    """
    R: fill each buy order at the actual price. Reads only the chosen
    actions and F_t, never the buyer's beliefs. Local because no shared
    rule fills an order at a price in F_t.
    """
    return RealityResult(
        agents={
            name: {
                "quantity": 1 if action == BUY else 0,
                "price_paid": objective_state["price"] if action == BUY else 0,
            }
            for name, action in actions.items()
        },
    )


SCENARIO = Scenario(
    name="Buying at an Unexpected Price",
    description="Buy on the expected price, pay the actual price.",
    periods=1,
    initial_state={"price": ACTUAL_PRICE},
    agents=[BUYER],
    reality=fill_buy_order,
)

PRICE_AS_EXPECTED = SCENARIO.variant(initial_state={"price": EXPECTED_PRICE})


# Tests

class TestBuyingAtAnUnexpectedPrice(unittest.TestCase):
    TEST_NAME = "Template: Buying at an Unexpected Price"

    @classmethod
    def setUpClass(cls):
        cls.buyer = run_scenario(SCENARIO).agent(BUYER.name)
        cls.buyer_at_expected_price = run_scenario(PRICE_AS_EXPECTED).agent(
            BUYER.name
        )

    def test_buyer_buys_because_of_expected_price(self):
        self.assertEqual(self.buyer.selected_action, BUY)
        self.assertEqual(self.buyer.value_of(BUY), GOOD_VALUE - EXPECTED_PRICE)
        self.assertGreater(
            self.buyer.value_of(BUY), self.buyer.value_of(DO_NOT_BUY)
        )

    def test_buyer_pays_actual_price_and_loses(self):
        self.assertEqual(
            self.buyer.outcome, {"quantity": 1, "price_paid": ACTUAL_PRICE}
        )
        self.assertGreater(self.buyer.outcome["price_paid"], GOOD_VALUE)

    def test_actual_price_changes_outcome_not_choice(self):
        self.assertEqual(
            self.buyer_at_expected_price.selected_action,
            self.buyer.selected_action,
        )
        self.assertEqual(
            self.buyer_at_expected_price.outcome["price_paid"], EXPECTED_PRICE
        )

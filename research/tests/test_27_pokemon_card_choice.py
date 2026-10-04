"""
TER Replication Test 27: Pokemon Card -- Keep or Sell
Canonical TER: theory/academic.md, Models 5.1 and 5.2

Economic question
-----------------
Should a high school student with little disposable income keep a rare
Charizard or sell it for cash, given the student's personal keep value
and the sale offer? Can selecting sell still result in retaining the
card when no real buyer exists at that price?

Scenario
--------
A high school student with very little disposable income has already
spent $20 on a Pokemon booster pack and unexpectedly pulled a rare,
mint-condition Charizard. The student believes it could sell for roughly
$300 and must now choose between keeping it and attempting to sell it.
The student's personal value of keeping the card is assumed to be $250.

Each case is a separate, single-decision experiment. A buyer is an
external condition of realization, not a second modeled agent.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize personal benefit from the card        fixed
                              decision
M   Model of Reality          understands the card market; believes it       fixed market
                              could sell for roughly $300 and treats the     belief; offer
                              stated offer as available                      varied
F̂   Perceived Feasible Set    keep, sell, including when selling will fail   fixed
V   Valuation                 keep value = $250; sell value = believed offer keep fixed;
                                                                             offer varied
H   Time Horizon              current keep-versus-cash decision; no future    fixed
                              appreciation or resale forecast
D   Decision Process          compare the two values; sell on equality       fixed
C   Selected Action           keep or sell                                   observed
F_t aspects                   whether a real buyer exists at the stated      varied
                              offer
R   Reality Function          realizes the selected action against actual    fixed
                              sale conditions
O   Realized Outcome          sale success or failure, continued card        observed
                              ownership, and cash received

    C = D(F_hat, M, V(. | G, M, H)); then O = R(C, F_t)

D selects from the student's perceived options using beliefs and
valuations, not actual buyer existence. R uses the selected action and
actual sale conditions, not the student's belief that a sale is possible.
This is an agent-level specification: O is the student's O_i,t; no
separate system outcome is defined.

Economic mechanism
------------------
The student compares the personal benefit of owning the card with the
cash value of the believed sale offer. An offer below the keep value
leads to keep; an offer at or above it leads to sell. A sale attempt
produces cash only when a real buyer exists at that price.

    keep                    -> retain the card; receive no cash
    sell, buyer exists      -> transfer the card; receive the offered cash
    sell, no buyer exists   -> sale fails; retain the card; receive no cash

V supplies the values; D supplies the comparison and sell-on-tie rule.
The student may perceive selling as possible when it is not. A failed
sale changes O, not C: the selected action remains sell even though the
student retains the card.

Little disposable income motivates the question but does not force the
answer or introduce an additional decision rule. Its relevance to the
student's preferences is represented by the stated valuation assumptions.

Assumptions
-----------
- The $250 keep value is a scenario assumption, not a TER claim or an
  objective market appraisal. Values are expressed on a dollar-equivalent
  scale so keeping the card and receiving cash can be compared directly.
- The roughly $300 resale belief is context, not a guaranteed payment or
  a separately added valuation. The stated offer determines V(sell).
- The offer presented to the student equals the amount paid if a buyer
  exists. Believed offer and actual payment terms have distinct roles,
  even though this specification assumes their amounts agree.
- The student treats the offer as attainable when choosing; buyer
  existence is varied independently to expose a possible belief error.
- Selling is an attempt, not a guarantee. Keeping and a failed sale each
  yield no cash and leave the student owning the card. A successful sale
  transfers the card and pays the stated offer, with no fees or costs.
- At equality, D selects sell. This tie rule is a scenario choice, not a
  universal TER decision rule.
- The original $20 pack price is already spent. It is context only and
  does not enter this decision's valuations or cash-received outcome.
  Sunk-cost reasoning is not modeled.
- The card, its condition, and all dollar amounts are stipulated for this
  exercise; this is not an empirical claim about Pokemon card prices.
- No trading, pull probabilities, bargaining, additional agents, repeated
  decisions, learning, transitions, or price dynamics are modeled.

Hypothesis
----------
In this configured scenario:
1. At a $220 offer, the student selects keep, retains the card, and
   receives no cash, regardless of buyer existence.
2. At a $280 offer with a buyer, the student selects sell, transfers the
   card, and receives $280.
3. At the same $280 offer without a buyer, the student still selects
   sell, but the sale fails: the card is retained and no cash is received.
4. At a $250 offer, the student selects sell under the explicit tie rule;
   sale success still depends on buyer existence.

The executable tests below cover all four hypotheses. Hypothesis 1 is
tested without a buyer: keep is selected either way, so buyer existence
cannot matter. Hypothesis 4 is tested with a buyer; the failed-sale path
is already covered by hypothesis 3.
"""

import unittest

from research.ter import (
    AgentSpec,
    RealityResult,
    Scenario,
    run_scenario,
)
from research.ter.rules import maximize_value, price_taking_value


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

KEEP = "keep"
SELL = "sell"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

KEEP_VALUE = 250
SALE_OFFER = 280
LOW_OFFER = 220
TIE_OFFER = KEEP_VALUE


# ---------------------------------------------------------------------------
# Reality function (R) -- scoped to this test
# ---------------------------------------------------------------------------

def card_sale_reality(actions, objective_state, parameters):
    """Realize this student's keep or sell action under actual sale conditions."""
    (student_name, action), = actions.items()

    if action == KEEP:
        status = "kept"
    elif action == SELL:
        status = (
            "sold"
            if objective_state["buyer_exists"]
            else "sale_failed"
        )
    else:
        raise ValueError(f"Unsupported card action: {action}")

    sold = status == "sold"

    return RealityResult(
        agents={
            student_name: {
                "status": status,
                "owns_card": not sold,
                "cash_received": parameters["sale_offer"] if sold else 0,
            },
        },
    )


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

STUDENT = AgentSpec(
    name="student",
    objective="maximize personal benefit from the card decision",
    model_of_reality={"price": SALE_OFFER},
    perceived_feasible_set=[KEEP, SELL],
    valuation={
        "price_taking_action": SELL,
        "price_role": "benefit",
        "benefits": {KEEP: KEEP_VALUE},
        "costs": {},
    },
    valuation_rule=price_taking_value,
    decision_process=maximize_value,
    decision_parameters={"tie_break_preference": SELL},
    horizon="current keep-versus-cash decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIO = Scenario(
    name="Pokemon Card -- Keep or Sell",
    description="A student chooses between retaining a card and selling it.",
    periods=1,
    initial_state={"buyer_exists": True},
    agents=[STUDENT],
    parameters={"sale_offer": SALE_OFFER},
    reality=card_sale_reality,
)


def offer_scenario(offer, buyer_exists):
    """Set the believed offer (M) and the paid offer (R) to the same amount."""
    return SCENARIO.variant(
        agents=[STUDENT.variant(model_of_reality={"price": offer})],
        parameters={"sale_offer": offer},
        initial_state={"buyer_exists": buyer_exists},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPokemonCardChoice(unittest.TestCase):
    TEST_NAME = "Test 27: Pokemon Card -- Keep or Sell"

    def test_offer_above_keep_value_with_buyer_realizes_sale(self):
        student = run_scenario(SCENARIO).agent(STUDENT.name)

        self.assertEqual(student.selected_action, SELL)
        self.assertEqual(
            student.outcome,
            {
                "status": "sold",
                "owns_card": False,
                "cash_received": SALE_OFFER,
            },
        )

    def test_offer_above_keep_value_without_buyer_fails_to_sell(self):
        scenario = SCENARIO.variant(initial_state={"buyer_exists": False})
        student = run_scenario(scenario).agent(STUDENT.name)

        self.assertEqual(student.selected_action, SELL)
        self.assertEqual(
            student.outcome,
            {
                "status": "sale_failed",
                "owns_card": True,
                "cash_received": 0,
            },
        )

    def test_offer_below_keep_value_keeps_card(self):
        scenario = offer_scenario(LOW_OFFER, buyer_exists=False)
        student = run_scenario(scenario).agent(STUDENT.name)

        self.assertEqual(student.selected_action, KEEP)
        self.assertEqual(
            student.outcome,
            {
                "status": "kept",
                "owns_card": True,
                "cash_received": 0,
            },
        )

    def test_offer_equal_to_keep_value_sells_on_tie(self):
        scenario = offer_scenario(TIE_OFFER, buyer_exists=True)
        student = run_scenario(scenario).agent(STUDENT.name)

        self.assertEqual(student.selected_action, SELL)
        self.assertEqual(
            student.outcome,
            {
                "status": "sold",
                "owns_card": False,
                "cash_received": TIE_OFFER,
            },
        )

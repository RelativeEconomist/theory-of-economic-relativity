"""
TER Replication Test 16: Comparative Advantage and Specialization
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
In this configured scenario, when two producers with different absolute
productivities each independently choose the good that maximizes their own
value at one common perceived relative price, do they specialize according
to comparative advantage rather than absolute advantage?

Scenario
--------
Two producers can each spend a period producing Good A or Good B.
Productivity (units producible in one period) differs by producer and
good:

    Producer A: Good A = 5   Good B = 20
    Producer B: Good A = 1   Good B = 3

Producer A is absolutely more productive at both goods (5 > 1, 20 > 3).

Opportunity costs (units of the other good foregone per unit produced),
derived by simple arithmetic from the productivity figures above:

    Good A: Producer A = 20/5 = 4.0   Producer B = 3/1 = 3.0
            -> Producer B has the lower opportunity cost: comparative
               advantage in Good A

    Good B: Producer A = 5/20 = 0.25   Producer B = 1/3 = 0.333...
            -> Producer A has the lower opportunity cost: comparative
               advantage in Good B

Both producers perceive one common relative price of Good A, expressed
in units of Good B: 3.5 units of Good B per unit of Good A. This price
lies strictly between Producer B's opportunity cost of Good A (3.0) and
Producer A's opportunity cost of Good A (4.0).

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize the market value of the period's      fixed
                              production
M   Model of Reality          price_in_good_b_by_action: the one common      price fixed (identical
                              relative price both producers perceive;        for both producers);
                              productivity: the producer's own perceived     productivity varied
                              units producible per period, by good           (by producer)
F̂   Perceived Feasible Set    PRODUCE_GOOD_A, PRODUCE_GOOD_B                 fixed
V   Valuation                 priced_productivity_value (local): values an   fixed
                              action as the producer's perceived
                              productivity for it times the common price,
                              both read from M
H   Time Horizon              current production period                      fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           PRODUCE_GOOD_B (Producer A), PRODUCE_GOOD_A    observed
                              (Producer B)
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Three kinds of content, kept distinct:
- Exogenous scenario inputs: the productivity figures and the common
  relative price.
- Arithmetic derived from those inputs: opportunity costs, comparative
  advantage, and priced values. These are ordinary economics computed in
  this file; TER does not define productivity or opportunity-cost
  formulas.
- Agent choices produced by TER: each producer's selected action, from
  its own V and D.

Economic mechanism
------------------
Priced value of each option (productivity x price_in_good_b_by_action):

    Producer A: Good A = 5 x 3.5  = 17.5   Good B = 20 x 1 = 20
                -> maximizes at Good B

    Producer B: Good A = 1 x 3.5  = 3.5    Good B = 3 x 1  = 3
                -> maximizes at Good A

This matches the comparative-advantage allocation identified above
(Producer A -> Good B, Producer B -> Good A). Neither producer's V or D
reads the other producer's productivity or any opportunity-cost figure;
each uses only its own perceived productivity and the one shared price.

Control: at a relative price of 4.5, above both opportunity costs of
Good A (3.0 and 4.0), both producers value Good A more (Producer A:
22.5 > 20; Producer B: 4.5 > 3) and both select it. There is no
specialization, so the price band, not the productivity figures alone,
determines the comparative-advantage choices.

Assumptions
-----------
- Productivity figures are test-specific economic assumptions, not TER
  primitives. Each producer's productivity is its own perceived
  capability, so it belongs in M (academic.md section 6.2 grounds
  opportunity costs in agents' resources, capabilities, and
  constraints); V only evaluates actions using it. Producers are assumed
  to perceive their own productivity correctly.
- price_in_good_b_by_action is a common relative price both producers are
  declared to perceive identically (M). TER does not require producers to
  perceive the same price; that they do here is a simplifying assumption
  of this test, analogous to test_08's assumption that a firm perceives its
  own external effect exactly.
- The price (3.5) is chosen inside the band between the two producers'
  opportunity costs of Good A (3.0 and 4.0). As economic background, a
  relative price inside that band makes each producer's own value
  maximization pick its comparative advantage, and a price outside it would
  not. This test relies on that only for its configured numbers.
- priced_productivity_value is a local valuation rule for this test only.
  It implements V (Model 5.1) as a test-specific specification, not a TER
  primitive or a universal pricing rule. It is passed directly as a local callable.
- Some assertions below check scenario premises (the productivity ordering
  and the price band) directly from the configured constants. They guard
  the fixture and are not evidence for the hypothesis.
- This test demonstrates specialization decisions at given prices
  (Model 5.1). It does not model production, exchange, or consumption,
  so it shows no realized gains from trade, and it does not derive the
  price (no price-formation mechanism). Nor does it claim physical-output
  dominance: the specialized allocation produces (1 of Good A, 20 of
  Good B) and the opposite allocation (Producer A on Good A, Producer B
  on Good B) produces (5, 3), so neither has more of both goods.

Hypothesis
----------
Scenario premises (fixture checks, not evidence): Producer A has absolute
advantage in both goods, and the common perceived price lies strictly
between the two producers' opportunity costs of Good A. Given the
derived arithmetic above, this places Producer B's comparative advantage
in Good A and Producer A's in Good B.

In this configured scenario:
1. Each producer's decision process selects the good of its comparative
   advantage (Producer A: Good B; Producer B: Good A).
2. At a common relative price outside the band (above both opportunity
   costs of Good A), the same producers do not specialize: both select
   Good A.
"""

import unittest

from research.ter import AgentSpec, Scenario, run_scenario
from research.ter.rules import maximize_value


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

PRODUCE_GOOD_A = "produce_good_a"
PRODUCE_GOOD_B = "produce_good_b"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

# Units producible in one period if a producer spends the whole period on
# one good. Producer A is absolutely more productive at both goods, and
# (unlike a productivity matrix where the two happen to line up) the
# comparative advantages below run in different directions for each good.
PRODUCER_A_PRODUCTIVITY_GOOD_A = 5
PRODUCER_A_PRODUCTIVITY_GOOD_B = 20

PRODUCER_B_PRODUCTIVITY_GOOD_A = 1
PRODUCER_B_PRODUCTIVITY_GOOD_B = 3

# The one common relative price both producers perceive (M): units of
# Good B per unit of Good A. Good B is the numeraire, priced at 1.
# Chosen to lie strictly between Producer B's opportunity cost of Good A
# (3.0) and Producer A's opportunity cost of Good A (4.0) -- see
# Assumptions above and the band test below.
RELATIVE_PRICE_OF_GOOD_A_IN_GOOD_B = 3.5

PRICE_IN_GOOD_B_BY_ACTION = {
    PRODUCE_GOOD_A: RELATIVE_PRICE_OF_GOOD_A_IN_GOOD_B,
    PRODUCE_GOOD_B: 1,
}

# Control price, above both producers' opportunity costs of Good A (3.0
# and 4.0): outside the specialization band.
OUT_OF_BAND_RELATIVE_PRICE_OF_GOOD_A_IN_GOOD_B = 4.5


# ---------------------------------------------------------------------------
# Valuation rule
# ---------------------------------------------------------------------------

def priced_productivity_value(action, agent):
    """
    Local valuation rule for this test only. Implements V (Model 5.1) as a
    test-specific specification, not a TER primitive or a universal
    pricing rule.

    Values a production action as this producer's own perceived
    productivity for that action, priced at the one common relative price
    both producers perceive -- never at any opportunity cost, and never by
    reading the other producer's productivity. A common price is what
    makes two producers with different absolute productivity comparable
    in the same units; comparative-advantage specialization then falls
    out of each producer independently maximizing its own priced value.

    Required model_of_reality fields:

        productivity                action -> units producible in one period
        price_in_good_b_by_action   action -> price in units of Good B
                                     (the numeraire good is priced at 1)
    """
    productivity = agent.model_of_reality["productivity"][action]
    price = agent.model_of_reality["price_in_good_b_by_action"][action]

    return productivity * price


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_PRODUCER = AgentSpec(
    name="producer",
    objective="maximize the market value of the period's production",
    model_of_reality={
        "price_in_good_b_by_action": PRICE_IN_GOOD_B_BY_ACTION,
        "productivity": {
            PRODUCE_GOOD_A: 0,
            PRODUCE_GOOD_B: 0,
        },
    },
    perceived_feasible_set=[
        PRODUCE_GOOD_A,
        PRODUCE_GOOD_B,
    ],
    valuation_rule=priced_productivity_value,
    decision_process=maximize_value,
    horizon="current production period",
)

PRODUCER_A = BASE_PRODUCER.variant(
    name="producer_a",
    model_of_reality={
        "productivity": {
            PRODUCE_GOOD_A: PRODUCER_A_PRODUCTIVITY_GOOD_A,
            PRODUCE_GOOD_B: PRODUCER_A_PRODUCTIVITY_GOOD_B,
        },
    },
)

PRODUCER_B = BASE_PRODUCER.variant(
    name="producer_b",
    model_of_reality={
        "productivity": {
            PRODUCE_GOOD_A: PRODUCER_B_PRODUCTIVITY_GOOD_A,
            PRODUCE_GOOD_B: PRODUCER_B_PRODUCTIVITY_GOOD_B,
        },
    },
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SPECIALIZATION_SCENARIO = Scenario(
    name="Comparative Advantage and Specialization",
    description=(
        "Two producers with different absolute productivities each "
        "independently maximize value at one common perceived relative "
        "price, choosing which good to produce."
    ),
    periods=1,
    initial_state={},
    agents=[
        PRODUCER_A,
        PRODUCER_B,
    ],
)

# Control: the same producers, perceiving one common price outside the band.
OUT_OF_BAND_PRICE_IN_GOOD_B_BY_ACTION = {
    PRODUCE_GOOD_A: OUT_OF_BAND_RELATIVE_PRICE_OF_GOOD_A_IN_GOOD_B,
    PRODUCE_GOOD_B: 1,
}

OUT_OF_BAND_PRICE_SCENARIO = SPECIALIZATION_SCENARIO.variant(
    agents=[
        producer.variant(
            model_of_reality={
                "price_in_good_b_by_action": OUT_OF_BAND_PRICE_IN_GOOD_B_BY_ACTION,
            },
        )
        for producer in (PRODUCER_A, PRODUCER_B)
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestComparativeAdvantage(unittest.TestCase):
    TEST_NAME = "Test 16: Comparative Advantage and Specialization"

    def test_producer_a_has_absolute_advantage_in_both_goods(self):
        # Scenario-premise check: guards the configured productivity
        # ordering that makes this a comparative- versus absolute-advantage
        # demonstration. Not evidence for the hypothesis.
        self.assertGreater(
            PRODUCER_A_PRODUCTIVITY_GOOD_A,
            PRODUCER_B_PRODUCTIVITY_GOOD_A,
        )

        self.assertGreater(
            PRODUCER_A_PRODUCTIVITY_GOOD_B,
            PRODUCER_B_PRODUCTIVITY_GOOD_B,
        )

    def test_common_relative_price_lies_strictly_between_the_two_opportunity_costs(self):
        # Scenario-premise check: guards the price band. Since each
        # producer's opportunity cost of Good B is the reciprocal of its
        # opportunity cost of Good A, this band also fixes which producer
        # holds each comparative advantage. Not evidence for the hypothesis.
        producer_a_opportunity_cost_of_good_a = (
            PRODUCER_A_PRODUCTIVITY_GOOD_B / PRODUCER_A_PRODUCTIVITY_GOOD_A
        )
        producer_b_opportunity_cost_of_good_a = (
            PRODUCER_B_PRODUCTIVITY_GOOD_B / PRODUCER_B_PRODUCTIVITY_GOOD_A
        )

        # This band is exactly the set of prices at which each producer's
        # own value-maximizing choice, independently, reproduces
        # comparative-advantage specialization. A price outside it would
        # not.
        self.assertLess(
            producer_b_opportunity_cost_of_good_a,
            RELATIVE_PRICE_OF_GOOD_A_IN_GOOD_B,
        )

        self.assertLess(
            RELATIVE_PRICE_OF_GOOD_A_IN_GOOD_B,
            producer_a_opportunity_cost_of_good_a,
        )

    def test_each_producer_selects_the_good_of_its_comparative_advantage(self):
        result = run_scenario(SPECIALIZATION_SCENARIO)

        producer_a = result.agent(PRODUCER_A.name)
        producer_b = result.agent(PRODUCER_B.name)

        self.assertEqual(
            producer_a.selected_action,
            PRODUCE_GOOD_B,
        )

        self.assertEqual(
            producer_b.selected_action,
            PRODUCE_GOOD_A,
        )

    def test_a_price_outside_the_band_does_not_produce_specialization(self):
        # Control through D: only the perceived common price differs
        # from SPECIALIZATION_SCENARIO. Above both opportunity costs of
        # Good A, both producers select Good A.
        result = run_scenario(OUT_OF_BAND_PRICE_SCENARIO)

        self.assertEqual(
            result.agent(PRODUCER_A.name).selected_action,
            PRODUCE_GOOD_A,
        )

        self.assertEqual(
            result.agent(PRODUCER_B.name).selected_action,
            PRODUCE_GOOD_A,
        )

"""
TER Replication Test 16: Comparative Advantage and Specialization

Economic question
------------------
Can TER represent two producers with different absolute productivities,
who each independently maximize their own value at one common perceived
relative price, specializing according to comparative advantage rather
than absolute advantage?

Scenario
--------
Two producers can each spend a period producing Good A or Good B.
Productivity (units producible in one period) differs by producer and
good:

    Producer A: Good A = 5   Good B = 20
    Producer B: Good A = 1   Good B = 3

Producer A is absolutely more productive at both goods (5 > 1, 20 > 3).

Opportunity costs (units of the other good foregone per unit produced),
computed directly from the productivity constants above:

    Good A: Producer A = 20/5 = 4.0   Producer B = 3/1 = 3.0
            -> Producer B has the lower opportunity cost: comparative
               advantage in Good A

    Good B: Producer A = 5/20 = 0.25   Producer B = 1/3 = 0.333...
            -> Producer A has the lower opportunity cost: comparative
               advantage in Good B

Both producers perceive one common relative price of Good A, expressed
in units of Good B: 3.5 units of Good B per unit of Good A. This price
lies strictly between Producer B's opportunity cost of Good A (3.0) and
Producer A's opportunity cost of Good A (4.0) -- the terms-of-trade band
in which each producer's own value-maximizing choice, at a shared price,
reproduces comparative-advantage specialization. This is not a
coincidence of the productivity numbers (contrast the raw-productivity
mechanism this test replaces, and
test_raw_absolute_productivity_maximization_would_select_the_wrong_allocation
below): it is what a common market price is for.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   choose the production activity with the highest value
    M   price_in_good_b_by_action -- the one common relative price both
        producers perceive: Good A priced at 3.5 units of Good B, Good B
        at 1 (numeraire). Part of the environment producers act on, not
        either producer's own valuation.
    F̂   PRODUCE_GOOD_A, PRODUCE_GOOD_B -- F equals F̂
    V   priced_productivity_value -- each producer's own productivity
        for an action, valued at the common price read from M. Productivity
        is CHANGED between producers; the price they value it at is not.
    H   current production period
    D   DecisionProcess.MAXIMIZE
    C   the selected production activity

productivity (V's raw input, from valuation) and the common price (M)
are two separate declared facts. Neither producer's opportunity cost is
computed anywhere in G, M, F̂, V, H, or D -- only the shared price is,
and only by construction, once, as a scenario-level constant. Comparative
-advantage specialization is a consequence of maximizing priced value at
that shared price, not something TER computes directly or that either
producer's decision reads off the other producer's productivity.

Tested TER mechanics
--------------------
G     Objective              constant: choose the production activity
                              with the highest value
M     Model of reality       price_in_good_b_by_action -- CONSTANT and
                              IDENTICAL for both producers (the common
                              price they both perceive)
F, F̂  Feasible sets          PRODUCE_GOOD_A, PRODUCE_GOOD_B; F̂ equals F
V     Valuation               priced_productivity_value -- CHANGED
                              between producers (own productivity);
                              reads the shared price from M
H     Time horizon           constant: current production period
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        PRODUCE_GOOD_B (Producer A), PRODUCE_GOOD_A
                              (Producer B), observed result

No reality_function is declared: this test is about what determines C,
not about realizing or aggregating an outcome from it.

Economic mechanism
------------------
Priced value of each option (productivity x price_in_good_b_by_action):

    Producer A: Good A = 5 x 3.5  = 17.5   Good B = 20 x 1 = 20
                -> maximizes at Good B

    Producer B: Good A = 1 x 3.5  = 3.5    Good B = 3 x 1  = 3
                -> maximizes at Good A

This is exactly the comparative-advantage allocation identified above
(Producer A -> Good B, Producer B -> Good A), reached without either
producer's decision ever reading the other producer's productivity or
any opportunity-cost figure -- only their own productivity and the one
shared price.

Comparative-advantage (this scenario's) allocation, valued in Good B
units at the shared price: Producer A produces Good B (20), Producer B
produces Good A (3.5) -- combined value 23.5.

Reversed allocation: Producer A produces Good A (17.5), Producer B
produces Good B (3) -- combined value 20.5.

23.5 > 20.5: the comparative-advantage allocation outperforms the
reversed one under the shared price.

Assumptions
-----------
- Productivity figures are test-specific economic assumptions, not TER
  primitives.
- price_in_good_b_by_action is a common relative price both producers
  are declared to perceive identically (M). TER does not require
  producers to perceive the same price -- that they do here is a
  simplifying assumption of this test, analogous to test_08's assumption
  that a firm perceives its own external effect exactly.
- The chosen price (3.5) is not an arbitrary convenience: it is asserted
  to lie strictly between the two producers' opportunity costs of Good A
  (3.0 and 4.0). A price outside that band would not reproduce
  comparative-advantage specialization from private value-maximization
  alone; a price inside it always does, for any productivity numbers,
  which is what makes this a mechanism rather than a numeric coincidence.
- Opportunity cost and comparative advantage are computed directly from
  the named productivity constants inside the tests themselves -- there
  is no comparative-advantage primitive, rule, or helper, and neither
  producer's V or D computation involves an opportunity-cost calculation.
- priced_productivity_value is a local Model 5.1 valuation rule scoped to
  this test only, not a universal TER pricing rule.
- This test does not establish the general gains-from-trade theorem or a
  price-formation mechanism (the price is given, not derived). It shows
  one scenario where private value-maximization at a given common price
  produces comparative-advantage specialization and greater combined
  value than the reversed allocation.

Hypothesis
----------
1. Producer A has absolute advantage in both Good A and Good B.
2. Producer A has comparative advantage in Good B; Producer B has
   comparative advantage in Good A -- the two producers' comparative
   advantages differ, and neither coincides with Producer A's absolute
   advantage in both goods.
3. The common perceived relative price lies strictly between the two
   producers' opportunity costs of Good A.
4. Each producer's own value-maximizing choice at that shared price
   selects the good of its comparative advantage.
5. Maximizing raw absolute productivity instead (ignoring the shared
   price) would select a different, non-comparative-advantage allocation
   for Producer B.
6. The comparative-advantage allocation produces greater combined priced
   value than the reversed allocation.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, run_scenario
from research.ter.rules import register_rule


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


# ---------------------------------------------------------------------------
# Valuation rule
# ---------------------------------------------------------------------------

@register_rule("priced_productivity_value")
def priced_productivity_value(action, agent):
    """
    Local Model 5.1 valuation rule for this test only.

    Values a production action as this producer's own productivity for
    that action, priced at the one common relative price both producers
    perceive (M) -- never at any opportunity cost, and never by reading
    the other producer's productivity. A common price is what makes two
    producers with different absolute productivity comparable in the
    same units; comparative-advantage specialization then falls out of
    each producer independently maximizing its own priced value.

    Required valuation field:

        productivity   action -> units producible in one period

    Required model_of_reality field:

        price_in_good_b_by_action   action -> price in units of Good B
                                     (the numeraire good is priced at 1)
    """
    productivity = agent.valuation["productivity"][action]
    price = agent.model_of_reality["price_in_good_b_by_action"][action]

    return productivity * price


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_PRODUCER = AgentSpec(
    name="producer",
    objective="choose the production activity with the highest value",
    model_of_reality={
        "price_in_good_b_by_action": PRICE_IN_GOOD_B_BY_ACTION,
    },
    valuation={
        "productivity": {
            PRODUCE_GOOD_A: 0,
            PRODUCE_GOOD_B: 0,
        },
    },
    actual_feasible_set=[
        PRODUCE_GOOD_A,
        PRODUCE_GOOD_B,
    ],
    perceived_feasible_set=[
        PRODUCE_GOOD_A,
        PRODUCE_GOOD_B,
    ],
    valuation_rule="priced_productivity_value",
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current production period",
)

PRODUCER_A = BASE_PRODUCER.variant(
    name="producer_a",
    valuation={
        "productivity": {
            PRODUCE_GOOD_A: PRODUCER_A_PRODUCTIVITY_GOOD_A,
            PRODUCE_GOOD_B: PRODUCER_A_PRODUCTIVITY_GOOD_B,
        },
    },
)

PRODUCER_B = BASE_PRODUCER.variant(
    name="producer_b",
    valuation={
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
    initial_state={
        "period": 0,
    },
    agents=[
        PRODUCER_A,
        PRODUCER_B,
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestComparativeAdvantage(unittest.TestCase):
    TEST_NAME = "Test 16: Comparative Advantage and Specialization"

    def test_producer_a_has_absolute_advantage_in_both_goods(self):
        self.assertGreater(
            PRODUCER_A_PRODUCTIVITY_GOOD_A,
            PRODUCER_B_PRODUCTIVITY_GOOD_A,
        )

        self.assertGreater(
            PRODUCER_A_PRODUCTIVITY_GOOD_B,
            PRODUCER_B_PRODUCTIVITY_GOOD_B,
        )

    def test_producer_b_has_comparative_advantage_in_good_a(self):
        # Opportunity cost of Good A = how much Good B is foregone per
        # unit of Good A produced.
        producer_a_opportunity_cost_of_good_a = (
            PRODUCER_A_PRODUCTIVITY_GOOD_B / PRODUCER_A_PRODUCTIVITY_GOOD_A
        )
        producer_b_opportunity_cost_of_good_a = (
            PRODUCER_B_PRODUCTIVITY_GOOD_B / PRODUCER_B_PRODUCTIVITY_GOOD_A
        )

        self.assertLess(
            producer_b_opportunity_cost_of_good_a,
            producer_a_opportunity_cost_of_good_a,
        )

    def test_producer_a_has_comparative_advantage_in_good_b(self):
        # Opportunity cost of Good B = how much Good A is foregone per
        # unit of Good B produced.
        producer_a_opportunity_cost_of_good_b = (
            PRODUCER_A_PRODUCTIVITY_GOOD_A / PRODUCER_A_PRODUCTIVITY_GOOD_B
        )
        producer_b_opportunity_cost_of_good_b = (
            PRODUCER_B_PRODUCTIVITY_GOOD_A / PRODUCER_B_PRODUCTIVITY_GOOD_B
        )

        self.assertLess(
            producer_a_opportunity_cost_of_good_b,
            producer_b_opportunity_cost_of_good_b,
        )

    def test_common_relative_price_lies_strictly_between_the_two_opportunity_costs(self):
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

    def test_raw_absolute_productivity_maximization_would_select_the_wrong_allocation(self):
        # If each producer instead maximized raw absolute productivity,
        # ignoring the common price (the mechanism this test previously,
        # incorrectly, used), Producer B would select Good B -- not Good
        # A, its actual comparative advantage. Comparing raw productivity
        # only within one producer's own two options never involves the
        # other producer's numbers at all, so it cannot reliably track
        # comparative advantage, which is inherently a cross-producer
        # comparison. The priced mechanism this scenario actually uses
        # gets Producer B to Good A instead.
        raw_productivity_pick_for_producer_b = (
            PRODUCE_GOOD_A
            if PRODUCER_B_PRODUCTIVITY_GOOD_A > PRODUCER_B_PRODUCTIVITY_GOOD_B
            else PRODUCE_GOOD_B
        )

        self.assertEqual(
            raw_productivity_pick_for_producer_b,
            PRODUCE_GOOD_B,
        )

        result = run_scenario(SPECIALIZATION_SCENARIO)
        producer_b = result.agent(PRODUCER_B.name)

        self.assertNotEqual(
            raw_productivity_pick_for_producer_b,
            producer_b.selected_action,
        )

    def test_comparative_advantage_allocation_outperforms_reversed_allocation(self):
        result = run_scenario(SPECIALIZATION_SCENARIO)

        producer_a = result.agent(PRODUCER_A.name)
        producer_b = result.agent(PRODUCER_B.name)

        specialization_value = (
            producer_a.value_of(PRODUCE_GOOD_B)
            + producer_b.value_of(PRODUCE_GOOD_A)
        )

        # The comparison allocation: each producer makes the other good
        # instead -- the reverse of comparative advantage.
        reversed_allocation_value = (
            producer_a.value_of(PRODUCE_GOOD_A)
            + producer_b.value_of(PRODUCE_GOOD_B)
        )

        self.assertGreater(
            specialization_value,
            reversed_allocation_value,
        )

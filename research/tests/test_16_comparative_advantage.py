"""
TER Replication Test 16: Comparative Advantage and Specialization

Economic question
------------------
Can TER represent two producers with different opportunity costs whose
selected production activities align with comparative advantage under
specified productivity and valuation assumptions?

Scenario
--------
Two producers can each spend a period producing Good A or Good B.
Productivity (units producible in one period) differs by producer and
good:

    Producer A: Good A = 6   Good B = 4
    Producer B: Good A = 1   Good B = 2

Opportunity costs (units of the other good foregone per unit produced):

    Good A: Producer A = 4/6   Producer B = 2/1
            -> Producer A has the lower opportunity cost: comparative
               advantage in Good A

    Good B: Producer A = 6/4   Producer B = 1/2
            -> Producer B has the lower opportunity cost: comparative
               advantage in Good B

Producer A is absolutely more productive at both goods, yet each
producer's own value-maximizing choice still specializes by comparative
advantage, not absolute advantage.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

    G   choose the production activity with the highest value
    M   specified but empty
    F̂   PRODUCE_GOOD_A, PRODUCE_GOOD_B -- F equals F̂
    V   ValuationRule.MAPPED -- each producer's own productivity, used
        directly as its value for that activity
    H   current production period
    D   DecisionProcess.MAXIMIZE
    C   the selected production activity

Equal unit values for Good A and Good B are a simplifying assumption
(see Assumptions): it is what lets productivity be used directly as V,
without TER needing any notion of price or trade.

Tested TER mechanics
--------------------
G     Objective              constant: choose the production activity
                              with the highest value
M     Model of reality       specified but empty
F, F̂  Feasible sets          PRODUCE_GOOD_A, PRODUCE_GOOD_B; F̂ equals F
V     Valuation               ValuationRule.MAPPED -- CHANGED between
                              producers (own productivity)
H     Time horizon           constant: current production period
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        PRODUCE_GOOD_A (Producer A), PRODUCE_GOOD_B
                              (Producer B), observed result

Economic mechanism
------------------
Comparative-advantage allocation (each producer's own value-maximizing
choice): Producer A produces Good A (value 6), Producer B produces
Good B (value 2) -- combined value 8.

Reversed allocation: Producer A produces Good B (value 4), Producer B
produces Good A (value 1) -- combined value 5.

8 > 5: the comparative-advantage allocation outperforms the reversed one.

Assumptions
-----------
- Productivity figures (units producible if a producer spends the whole
  period on one good) are test-specific economic assumptions, not TER
  primitives.
- Good A and Good B are assumed to carry equal unit value, so each
  producer's declared V is simply its own productivity figure. This is
  what makes each producer's own value-maximizing choice coincide with
  comparative advantage, without TER needing any notion of price or
  trade.
- For these productivity assumptions and equal unit values, each
  producer's individually highest-valued activity happens to coincide
  with the good in which that producer has comparative advantage. This
  alignment is specific to this scenario and is not a general
  implication of comparative advantage.
- Opportunity cost and comparative advantage are computed directly from
  the named productivity constants inside the tests themselves -- there
  is no comparative-advantage primitive, rule, or helper.
- This test does not establish the general gains-from-trade theorem. It
  shows one scenario where private value-maximizing specialization
  aligns with comparative advantage and produces greater combined
  production value than the reversed allocation.

Hypothesis
----------
1. Producer A has comparative advantage in Good A under the declared
   productivity assumptions.
2. Producer B has comparative advantage in Good B.
3. Each producer selects the activity consistent with that comparative
   advantage.
4. The comparative-advantage allocation produces greater combined value
   than the reversed allocation under these assumptions.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

PRODUCE_GOOD_A = "produce_good_a"
PRODUCE_GOOD_B = "produce_good_b"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

# Units producible in one period if a producer spends the whole period on
# one good. Producer A is absolutely more productive at both goods; the
# comparative-advantage tests below show specialization does not follow
# from that absolute edge.
PRODUCER_A_PRODUCTIVITY_GOOD_A = 6
PRODUCER_A_PRODUCTIVITY_GOOD_B = 4

PRODUCER_B_PRODUCTIVITY_GOOD_A = 1
PRODUCER_B_PRODUCTIVITY_GOOD_B = 2


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_PRODUCER = AgentSpec(
    name="producer",
    objective="choose the production activity with the highest value",
    model_of_reality={},
    valuation={
        "values": {
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
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current production period",
)

PRODUCER_A = BASE_PRODUCER.variant(
    name="producer_a",
    valuation={
        "values": {
            PRODUCE_GOOD_A: PRODUCER_A_PRODUCTIVITY_GOOD_A,
            PRODUCE_GOOD_B: PRODUCER_A_PRODUCTIVITY_GOOD_B,
        },
    },
)

PRODUCER_B = BASE_PRODUCER.variant(
    name="producer_b",
    valuation={
        "values": {
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
    description="Two producers with different relative productivities each independently choose which good to produce.",
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

    def test_producer_a_has_comparative_advantage_in_good_a(self):
        # Opportunity cost of Good A = how much Good B is foregone per
        # unit of Good A produced.
        producer_a_opportunity_cost_of_good_a = (
            PRODUCER_A_PRODUCTIVITY_GOOD_B / PRODUCER_A_PRODUCTIVITY_GOOD_A
        )
        producer_b_opportunity_cost_of_good_a = (
            PRODUCER_B_PRODUCTIVITY_GOOD_B / PRODUCER_B_PRODUCTIVITY_GOOD_A
        )

        self.assertLess(
            producer_a_opportunity_cost_of_good_a,
            producer_b_opportunity_cost_of_good_a,
        )

    def test_producer_b_has_comparative_advantage_in_good_b(self):
        # Opportunity cost of Good B = how much Good A is foregone per
        # unit of Good B produced.
        producer_a_opportunity_cost_of_good_b = (
            PRODUCER_A_PRODUCTIVITY_GOOD_A / PRODUCER_A_PRODUCTIVITY_GOOD_B
        )
        producer_b_opportunity_cost_of_good_b = (
            PRODUCER_B_PRODUCTIVITY_GOOD_A / PRODUCER_B_PRODUCTIVITY_GOOD_B
        )

        self.assertLess(
            producer_b_opportunity_cost_of_good_b,
            producer_a_opportunity_cost_of_good_b,
        )

    def test_producer_a_has_absolute_advantage_in_both_goods(self):
        # Contrast with comparative advantage: Producer A is more
        # productive at everything, yet the tests above still assign
        # Good A to Producer A and Good B to Producer B, not both goods
        # to Producer A.
        self.assertGreater(
            PRODUCER_A_PRODUCTIVITY_GOOD_A,
            PRODUCER_B_PRODUCTIVITY_GOOD_A,
        )

        self.assertGreater(
            PRODUCER_A_PRODUCTIVITY_GOOD_B,
            PRODUCER_B_PRODUCTIVITY_GOOD_B,
        )

    def test_each_producer_selects_the_good_of_its_comparative_advantage(self):
        result = run_scenario(SPECIALIZATION_SCENARIO)

        producer_a = result.agent(PRODUCER_A.name)
        producer_b = result.agent(PRODUCER_B.name)

        self.assertEqual(
            producer_a.selected_action,
            PRODUCE_GOOD_A,
        )

        self.assertEqual(
            producer_b.selected_action,
            PRODUCE_GOOD_B,
        )

    def test_comparative_advantage_allocation_outperforms_reversed_allocation(self):
        result = run_scenario(SPECIALIZATION_SCENARIO)

        producer_a = result.agent(PRODUCER_A.name)
        producer_b = result.agent(PRODUCER_B.name)

        specialization_value = (
            producer_a.value_of(PRODUCE_GOOD_A)
            + producer_b.value_of(PRODUCE_GOOD_B)
        )

        # The comparison allocation: each producer makes the other good
        # instead -- the reverse of comparative advantage.
        reversed_allocation_value = (
            PRODUCER_A_PRODUCTIVITY_GOOD_B
            + PRODUCER_B_PRODUCTIVITY_GOOD_A
        )

        self.assertGreater(
            specialization_value,
            reversed_allocation_value,
        )

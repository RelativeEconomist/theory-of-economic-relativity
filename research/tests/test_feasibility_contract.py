"""
TER Model 5.2 Test: Actual vs. Perceived Feasibility

Economic question
------------------
When an agent's belief about what is feasible (F_hat) exceeds what is
actually feasible (F), does the selected action remain the action the
agent chose, while the realized outcome is capped by reality rather than
re-decided by the agent?

TER components
--------------
G      objective              identical for every producer: maximize
                               realized production value.
M      model of reality       agent beliefs about reality (empty here).
F      actual feasible set    the true production ceiling; differs across
                               agents; independent of what they believe.
F_hat  perceived feasible set what each producer believes it can produce;
                               differs from F for two of the three agents.
V      valuation              valuation["values"], via mapped_value.
H      time horizon           "current production decision".
D      decision process       maximize_value, applied once, only to F_hat.
C      selected action        recorded and preserved exactly as selected.
O      realized outcome       realized_units, determined by
                               capacity_constrained_realization (this
                               scenario's own R), never by re-running D or
                               V against F.

Assumptions
-----------
- This is a test of the TER execution mechanism itself, not a scenario-
  specific economic replication.
- capacity_constrained_realization is one admissible specification of
  R(C, F, P, S), scoped to this test only, and is registered here rather
  than in the generic rules.py registry.

Hypothesis
----------
1. When F_hat = F, the selected action is fully realized.
2. When C is perceived feasible but not actually feasible, the realized
   outcome may be a partial realization of C, capped by F.
3. C itself is never rewritten; only O can differ from what was selected.
4. A more severe mismatch between F_hat and F, using the same reality
   rule, can produce a near total shortfall, but this is not asserted as
   a universal consequence of C not belonging to F.
"""

import unittest

from research.ter.outcome import is_actually_feasible
from research.ter.rules import build_agent_results, register_rule
from research.ter.runner import build_agent, run_scenario
from research.ter.scenario import AgentSpec, Scenario


HOLD = "hold"
PRODUCE_60 = "produce_60"
PRODUCE_100 = "produce_100"


QUANTITY = {
    HOLD: 0,
    PRODUCE_60: 60,
    PRODUCE_100: 100,
}


@register_rule("capacity_constrained_realization")
def capacity_constrained_realization(state, agents, actions, parameters):
    """
    One admissible TER Model 5.2 reality function for this test only.

    For each agent, if the selected action C is actually feasible
    (C in F), it is realized exactly as selected. Otherwise, reality caps
    the realized quantity at the largest quantity actually achievable
    under F, a ceiling read mechanically from F itself.

    This never calls the agent's value function or decision process.
    Nothing here re-selects or re-evaluates an action; it only measures
    how much of the already selected action reality permits. It also
    never reports the selected action itself -- that comes from core
    Scenario execution (AgentResult.selected_action), not from this rule.

    This is not a universal TER consequence rule. A different scenario
    may specify a different R.

    Uses the internal build_agent_results helper so each producer's
    actually_feasible/realized_units can be looked up by name via
    ScenarioResult.agent(name), the same convention social_value_outcome
    uses. Kept local to this test rather than promoted to RealityFunction.

    Required parameter:

        quantity   scenario-specific mapping from each action token to
                   a unit quantity
    """
    quantity = parameters["quantity"]

    def compute(agent, action):
        if is_actually_feasible(agent, action):
            return {
                "actually_feasible": True,
                "realized_units": quantity[action],
            }

        capacity = max(
            quantity[feasible_action]
            for feasible_action in agent.actual_feasible_set
        )

        return {
            "actually_feasible": False,
            "realized_units": min(quantity[action], capacity),
        }

    return build_agent_results(agents, actions, compute)


BASE_PRODUCER = AgentSpec(
    name="producer",
    objective="maximize realized production value",
    model_of_reality={},
    valuation={
        "values": {
            HOLD: 0,
            PRODUCE_60: 6,
            PRODUCE_100: 10,
        },
    },
    actual_feasible_set=[
        HOLD,
        PRODUCE_60,
    ],
    perceived_feasible_set=[
        HOLD,
        PRODUCE_60,
    ],
    valuation_rule="mapped_value",
    decision_process="maximize_value",
    horizon="current production decision",
)


ACCURATE_PRODUCER = BASE_PRODUCER.variant(
    name="accurate_producer",
)


MISTAKEN_PRODUCER = BASE_PRODUCER.variant(
    name="mistaken_producer",
    perceived_feasible_set=[
        HOLD,
        PRODUCE_60,
        PRODUCE_100,
    ],
)


SEVERE_PRODUCER = BASE_PRODUCER.variant(
    name="severe_producer",
    actual_feasible_set=[
        HOLD,
    ],
    perceived_feasible_set=[
        HOLD,
        PRODUCE_60,
        PRODUCE_100,
    ],
)


SCENARIO = Scenario(
    name="Actual vs. Perceived Production Capacity",
    description=(
        "Producers select a production action from their perceived "
        "feasible set. Reality realizes each selected action only up to "
        "the actual feasible set's true ceiling."
    ),
    periods=1,

    initial_state={
        "period": 0,
    },

    agents=[
        ACCURATE_PRODUCER,
        MISTAKEN_PRODUCER,
        SEVERE_PRODUCER,
    ],

    parameters={
        "quantity": QUANTITY,
    },

    reality_function="capacity_constrained_realization",
)


class TestModel52ActualVsPerceivedFeasibility(unittest.TestCase):
    TEST_NAME = "Model 5.2: Actual vs. Perceived Feasibility"

    def test_accurate_feasibility_check_is_pure_membership(self):
        agent = build_agent(ACCURATE_PRODUCER)

        self.assertTrue(
            is_actually_feasible(agent, PRODUCE_60)
        )

        self.assertFalse(
            is_actually_feasible(agent, PRODUCE_100)
        )

    def test_mistaken_action_is_perceived_feasible_but_not_actually_feasible(self):

        agent = build_agent(MISTAKEN_PRODUCER)

        self.assertIn(

            PRODUCE_100,

            agent.perceived_feasible_set,

        )

        self.assertNotIn(

            PRODUCE_100,

            agent.actual_feasible_set,
        )

    def test_accurate_feasibility_is_fully_realized(self):
        result = run_scenario(SCENARIO)
        agent = result.agent(ACCURATE_PRODUCER.name)

        self.assertEqual(
            agent.selected_action,
            PRODUCE_60,
        )

        self.assertTrue(
            agent.actually_feasible
        )

        self.assertEqual(
            agent.realized_units,
            60,
        )

    def test_mistaken_feasibility_produces_partial_realization(self):
        result = run_scenario(SCENARIO)
        agent = result.agent(MISTAKEN_PRODUCER.name)

        self.assertEqual(
            agent.selected_action,
            PRODUCE_100,
        )

        self.assertFalse(
            agent.actually_feasible
        )

        self.assertEqual(
            agent.realized_units,
            60,
        )

    def test_selected_action_is_not_rewritten_to_the_realized_outcome(self):
        result = run_scenario(SCENARIO)
        agent = result.agent(MISTAKEN_PRODUCER.name)

        self.assertEqual(
            agent.selected_action,
            PRODUCE_100,
        )

        self.assertNotEqual(
            agent.selected_action,
            PRODUCE_60,
        )

        self.assertEqual(
            agent.realized_units,
            QUANTITY[PRODUCE_60],
        )

    def test_severe_constraint_produces_total_shortfall(self):
        result = run_scenario(SCENARIO)
        agent = result.agent(SEVERE_PRODUCER.name)

        self.assertEqual(
            agent.selected_action,
            PRODUCE_100,
        )

        self.assertFalse(
            agent.actually_feasible
        )

        self.assertEqual(
            agent.realized_units,
            0,
        )

    def test_same_reality_rule_produces_different_severity_from_differing_actual_feasibility(self):
        result = run_scenario(SCENARIO)
        mistaken = result.agent(MISTAKEN_PRODUCER.name)
        severe = result.agent(SEVERE_PRODUCER.name)

        self.assertEqual(
            mistaken.selected_action,
            severe.selected_action,
        )

        self.assertGreater(
            mistaken.realized_units,
            severe.realized_units,
        )

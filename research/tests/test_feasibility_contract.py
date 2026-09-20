"""
Framework test: perceived feasible set and outcome realization

Canonical TER: theory/academic.md, Models 5.1 and 5.2

Purpose
-------
Verifies, through a minimal local reality function, that when an agent's
perceived feasible set F̂ includes an action the scenario does not permit,
the framework keeps the selected action as Model 5.1 selected it and
reports a realized outcome that differs from it as the local R specifies.
Not an economic replication test.

Representation:

- F_t is not agent-specific. state["permitted_actions"] (agent name ->
  permitted actions) is an implementation index of the scenario-relevant
  aspects of F_t -- here, each producer's production ceiling -- read only
  by the local R.
- F̂ (perceived_feasible_set) is agent-side. It equals the permitted
  actions for one producer and exceeds them for two.
- V is valuation["values"] via mapped_value; D applies maximize_value once,
  to F̂ only.
- O_{i,t} is realized_units, produced by capacity_constrained_realization
  (this test's own R), never by re-running D or V. The specification is
  agent-level, so no system outcome O_t is defined.
- The result fields actually_feasible and the function
  is_actually_feasible are implementation identifiers for a per-agent
  membership check against the permission data; they do not claim that F_t
  is a per-agent set.

Verified behavior
-----------------
1. When F̂ matches the permitted actions, the selected action is fully
   realized.
2. When the selected action is in F̂ but not permitted, the realized
   outcome may be a partial realization of it, capped by the permission
   data.
3. The framework preserves the selected-action record produced by
   Model 5.1 during outcome realization; only the realized outcome
   differs from what was selected. This is an implementation invariant of
   the current runner, not a theoretical rule.
4. A more severe mismatch, under the same R, can produce a near total
   shortfall. This is not asserted as a universal consequence of a
   selected action not being permitted.

Out of scope
------------
capacity_constrained_realization is one admissible specification of R,
scoped to this test and registered here rather than in the generic
rules.py registry. It is not a universal TER consequence rule.
"""

import unittest

from research.ter.outcome import is_actually_feasible, permitted_actions_for
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

    For each agent, if the selected action is among the actions the
    scenario permits for that agent (state["permitted_actions"], an
    implementation index of the scenario-relevant aspects of F_t), it is
    realized exactly as selected. Otherwise, R caps the realized quantity
    at the largest quantity among the actions permitted for that agent.

    This never calls the agent's value function or decision process.
    Nothing here re-selects or re-evaluates an action; it only measures
    how much of the already selected action the permission data allows.
    It also never reports the selected action itself -- that comes from
    core Scenario execution (AgentResult.selected_action), not from this
    rule.

    This is not a universal TER consequence rule. A different scenario
    may specify a different R.

    Uses the internal build_agent_results helper so each producer's
    actually_feasible/realized_units (implementation field names) can be
    looked up by name via
    ScenarioResult.agent(name), the same convention social_value_outcome
    uses. Kept local to this test rather than promoted to RealityFunction.

    Required parameter:

        quantity   scenario-specific mapping from each action token to
                   a unit quantity
    """
    quantity = parameters["quantity"]

    def compute(agent, action):
        if is_actually_feasible(state, agent, action):
            return {
                "actually_feasible": True,
                "realized_units": quantity[action],
            }

        capacity = max(
            quantity[feasible_action]
            for feasible_action in permitted_actions_for(state, agent)
        )

        return {
            "actually_feasible": False,
            "realized_units": min(quantity[action], capacity),
        }

    return build_agent_results(state, agents, actions, compute)


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
    perceived_feasible_set=[
        HOLD,
        PRODUCE_60,
        PRODUCE_100,
    ],
)


# Permission data: the actions the scenario permits for each producer (an
# implementation index of the scenario-relevant aspects of F_t, which is not
# agent-specific). SEVERE_PRODUCER's ceiling is tighter than the others'.
PERMITTED_ACTIONS = {
    ACCURATE_PRODUCER.name: [
        HOLD,
        PRODUCE_60,
    ],
    MISTAKEN_PRODUCER.name: [
        HOLD,
        PRODUCE_60,
    ],
    SEVERE_PRODUCER.name: [
        HOLD,
    ],
}


SCENARIO = Scenario(
    name="Perceived vs. Permitted Production Capacity",
    description=(
        "Producers select a production action from their perceived "
        "feasible set. Reality realizes each selected action only up to "
        "the true ceiling the objective feasible state of reality "
        "permits."
    ),
    periods=1,

    initial_state={
        "period": 0,
        "permitted_actions": PERMITTED_ACTIONS,
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


class TestModel52PerceivedFeasibleSetAndOutcomeRealization(unittest.TestCase):
    TEST_NAME = "Model 5.2: Perceived Feasible Set and Outcome Realization"

    def test_accurate_feasibility_check_is_pure_membership(self):
        agent = build_agent(ACCURATE_PRODUCER)
        state = {"permitted_actions": PERMITTED_ACTIONS}

        self.assertTrue(
            is_actually_feasible(state, agent, PRODUCE_60)
        )

        self.assertFalse(
            is_actually_feasible(state, agent, PRODUCE_100)
        )

    def test_feasibility_check_requires_a_permitted_actions_entry_for_the_agent(self):
        agent = build_agent(ACCURATE_PRODUCER)

        with self.assertRaises(ValueError):
            is_actually_feasible({"permitted_actions": {}}, agent, PRODUCE_60)

    def test_mistaken_action_is_in_the_perceived_feasible_set_but_not_in_permitted_actions(self):

        agent = build_agent(MISTAKEN_PRODUCER)

        self.assertIn(

            PRODUCE_100,

            agent.perceived_feasible_set,

        )

        self.assertNotIn(

            PRODUCE_100,

            permitted_actions_for(
                {"permitted_actions": PERMITTED_ACTIONS},
                agent,
            ),
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

    def test_selected_action_record_is_preserved_alongside_the_realized_outcome(self):
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

    def test_same_reality_rule_produces_different_severity_from_differing_permitted_actions(self):
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

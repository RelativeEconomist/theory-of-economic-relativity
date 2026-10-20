"""
Framework test: Feasible Set Learning adapter.

Purpose
-------
This is not an economic replication test. It verifies that the JSON-safe
adapter runs the reusable Feasible Set Learning scenario through
run_scenario and reports each decision point from the recorded trace, in
order: the agent's state when it decided, the permission data, the
selected action, the realized O_{i,t}, what the agent observed, and its
state after the update. Earlier decision points are never reconstructed
from final state.
"""

import json
import unittest

from research.adapters.feasible_set_learning import SCENARIO_ID, run
from research.scenarios.feasible_set_learning import (
    BASE_AGENT,
    BETTER_ACTION,
    LEARNING_SCENARIO,
    ORDINARY_ACTION,
)
from research.ter import run_scenario

AGENT = BASE_AGENT.name
PERMITTED = [ORDINARY_ACTION, BETTER_ACTION]


class TestFeasibleSetLearningAdapter(unittest.TestCase):
    TEST_NAME = "Framework: Feasible Set Learning Adapter"

    def test_default_run_reproduces_test_22(self):
        result = run({"scenario": SCENARIO_ID})
        first, second = result["periods"]

        self.assertEqual(result["scenario"], SCENARIO_ID)
        self.assertEqual(result["name"], LEARNING_SCENARIO.name)
        self.assertEqual(result["agent"], AGENT)

        self.assertEqual(first["decision_state"]["perceived_feasible_set"], [ORDINARY_ACTION])
        self.assertEqual(first["selected_action"], ORDINARY_ACTION)
        self.assertEqual(first["updated_agent_state"]["perceived_feasible_set"], PERMITTED)
        self.assertEqual(first["added_actions"], [BETTER_ACTION])

        self.assertEqual(second["decision_state"]["perceived_feasible_set"], PERMITTED)
        self.assertEqual(second["selected_action"], BETTER_ACTION)

        # The final update truthfully reports no further change.
        self.assertEqual(second["updated_agent_state"], second["decision_state"])
        self.assertEqual(second["added_actions"], [])

    def test_each_period_is_read_from_its_own_trace_step(self):
        result = run({"scenario": SCENARIO_ID})
        trace = run_scenario(LEARNING_SCENARIO).trace

        self.assertEqual(len(result["periods"]), LEARNING_SCENARIO.periods)
        self.assertEqual(len(result["periods"]), len(trace))

        for t, period in enumerate(result["periods"]):
            with self.subTest(t=t):
                before = trace.agents_before(t)[AGENT]
                after = trace[t].agents[AGENT]

                self.assertEqual(period["decision_point"], trace[t].step)
                self.assertEqual(
                    period["decision_state"],
                    {
                        "model_of_reality": before.model_of_reality,
                        "perceived_feasible_set": before.perceived_feasible_set,
                    },
                )
                self.assertEqual(
                    period["objective_conditions"],
                    {"permitted_actions": trace.objective_state_before(t)["permitted_actions"][AGENT]},
                )
                self.assertEqual(period["selected_action"], trace[t].actions[AGENT])
                self.assertEqual(period["realized_outcome"], trace[t].reality.agent(AGENT))
                self.assertEqual(period["observation"], trace[t].observations[AGENT].data)
                self.assertEqual(
                    period["updated_agent_state"],
                    {
                        "model_of_reality": after.model_of_reality,
                        "perceived_feasible_set": after.perceived_feasible_set,
                    },
                )

    def test_decision_time_state_is_not_the_final_state(self):
        result = run({"scenario": SCENARIO_ID})
        final_state = run_scenario(LEARNING_SCENARIO).agent(AGENT).state

        # The first decision ran before the update; final state is after it.
        self.assertEqual(final_state.perceived_feasible_set, PERMITTED)
        self.assertNotEqual(
            result["periods"][0]["decision_state"]["perceived_feasible_set"],
            final_state.perceived_feasible_set,
        )

        # Each update is the state the next decision starts from.
        first, second = result["periods"]
        self.assertEqual(second["decision_state"], first["updated_agent_state"])

    def test_realized_outcome_reaches_f_hat_only_through_the_observation(self):
        result = run({"scenario": SCENARIO_ID})

        for period in result["periods"]:
            with self.subTest(t=period["decision_point"]):
                # R records the experienced action as O_{i,t}; the agent
                # observes its own O_{i,t} exactly.
                self.assertEqual(
                    period["realized_outcome"],
                    {"experienced_action": period["selected_action"]},
                )
                self.assertEqual(period["observation"], period["realized_outcome"])

        # The same R with no observation rule: no update, so no learning.
        unobserved = run_scenario(LEARNING_SCENARIO.variant(observation=None)).trace

        for t in range(len(unobserved)):
            with self.subTest(unobserved_t=t):
                self.assertEqual(unobserved[t].observations, {})
                self.assertEqual(unobserved[t].actions[AGENT], ORDINARY_ACTION)
                self.assertEqual(
                    unobserved[t].agents[AGENT].perceived_feasible_set, [ORDINARY_ACTION]
                )

    def test_permission_data_is_fixed_and_kept_apart_from_agent_state(self):
        result = run({"scenario": SCENARIO_ID})
        trace = run_scenario(LEARNING_SCENARIO).trace

        self.assertEqual(result["permitted_actions"], PERMITTED)
        self.assertEqual(trace.final, LEARNING_SCENARIO.initial_state)

        for period in result["periods"]:
            with self.subTest(t=period["decision_point"]):
                self.assertEqual(period["objective_conditions"], {"permitted_actions": PERMITTED})

                for state in (period["decision_state"], period["updated_agent_state"]):
                    self.assertEqual(set(state), {"model_of_reality", "perceived_feasible_set"})
                    # M is empty and fixed; F̂ is the changing component.
                    self.assertEqual(state["model_of_reality"], {})

        # BETTER_ACTION is permitted from the start but not yet perceived.
        self.assertNotIn(
            BETTER_ACTION, result["periods"][0]["decision_state"]["perceived_feasible_set"]
        )

    def test_output_is_json_safe(self):
        result = run({"scenario": SCENARIO_ID})
        encoded = json.dumps(result, allow_nan=False)

        self.assertEqual(json.loads(encoded), result)
        self.assertEqual(
            set(result), {"scenario", "name", "agent", "permitted_actions", "periods"}
        )

        for period in result["periods"]:
            self.assertEqual(
                set(period),
                {
                    "decision_point",
                    "decision_state",
                    "objective_conditions",
                    "selected_action",
                    "realized_outcome",
                    "observation",
                    "updated_agent_state",
                    "added_actions",
                },
            )

    def test_unsupported_scenario_is_rejected(self):
        for request in ({"scenario": "basic-agent-choice"}, {"scenario": None}, {}):
            with self.subTest(request=request):
                with self.assertRaisesRegex(ValueError, SCENARIO_ID):
                    run(request)

    def test_invalid_requests_are_rejected(self):
        with self.assertRaisesRegex(TypeError, "dict"):
            run([SCENARIO_ID])

        # The scenario has no adjustable inputs.
        for key in ("periods", "perceived_feasible_set", "permitted_actions", "action_values"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "Unknown"):
                    run({"scenario": SCENARIO_ID, key: []})

    def test_runs_do_not_change_the_reusable_scenario(self):
        first = run({"scenario": SCENARIO_ID})
        second = run({"scenario": SCENARIO_ID})

        self.assertEqual(first, second)
        self.assertEqual(BASE_AGENT.perceived_feasible_set, [ORDINARY_ACTION])
        self.assertEqual(LEARNING_SCENARIO.agents[0].perceived_feasible_set, [ORDINARY_ACTION])
        self.assertEqual(
            LEARNING_SCENARIO.initial_state, {"permitted_actions": {AGENT: PERMITTED}}
        )


if __name__ == "__main__":
    unittest.main()

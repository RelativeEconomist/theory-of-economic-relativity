"""
Framework test: scheduled engine contract

Canonical TER: theory/academic.md, Models 5.1, 5.2, 5.3 and 5.5

Purpose
-------
Freezes the contracts of the execution engine (research.ter.runner.
run_scenario), independent of any economic scenario:

1. RealityResult -- R returns one, it is immutable, and it names only
   agents of the scenario.
2. R / transition split -- R sees F_t frozen and cannot change it; only a
   transition produces F_t+1, and without one F carries forward.
3. Observation -- an agent's state changes only through its own update
   rule applied to an Observation it received; D cannot change it in
   place, and an update rule sees only the agent's own view.
4. Schedule -- inactive agents do not decide and contribute no action;
   staged schedules cycle; actors at one decision point all decide
   before anything at that point is realized.
5. Trace -- every recorded field is immutable after the run.
6. Counterfactual re-runs -- deterministic R only, active agents only,
   and they never alter the recorded trace.
7. Every scenario records a trace, and a variant cannot introduce a
   field Scenario does not have.

The local rules below are minimal probes, not TER dynamics.
"""

import unittest
from dataclasses import FrozenInstanceError

from research.ter import AgentSpec, RealityResult, Scenario, Schedule, run_scenario
from research.ter.observation import Observation, UpdateView
from research.ter.rules import register_rule


LOW = "low"
HIGH = "high"


@register_rule("sched_contract_echo_reality")
def sched_contract_echo_reality(actions, objective_state, parameters):
    """Each actor's O_i,t is its own action; O_t counts the actors."""
    return RealityResult(
        system={"actors": len(actions)},
        agents={
            name: {"realized": action}
            for name, action in actions.items()
        },
    )


@register_rule("sched_contract_legacy_shaped_reality")
def sched_contract_legacy_shaped_reality(actions, objective_state, parameters):
    return {"not": "a RealityResult"}


@register_rule("sched_contract_unknown_agent_reality")
def sched_contract_unknown_agent_reality(actions, objective_state, parameters):
    return RealityResult(agents={"nobody": {}})


@register_rule("sched_contract_mutating_reality")
def sched_contract_mutating_reality(actions, objective_state, parameters):
    objective_state["counter"] = 99
    return RealityResult()


_NONDETERMINISTIC_CALLS = []


@register_rule("sched_contract_nondeterministic_reality")
def sched_contract_nondeterministic_reality(actions, objective_state, parameters):
    _NONDETERMINISTIC_CALLS.append(None)
    return RealityResult(system={"call": len(_NONDETERMINISTIC_CALLS)})


@register_rule("sched_contract_count_transition")
def sched_contract_count_transition(objective_state, reality, parameters):
    objective_state["counter"] += reality.system["actors"]
    return objective_state


@register_rule("sched_contract_observe_own")
def sched_contract_observe_own(agents, actions, reality, objective_state, parameters):
    return {
        name: dict(reality.agent(name))
        for name in agents
        if name in reality.agents
    }


_UPDATE_CALLS = []


@register_rule("sched_contract_flag_update")
def sched_contract_flag_update(agent, observation):
    _UPDATE_CALLS.append((agent, observation))
    model = agent.model_of_reality
    model["flag"] = True
    return {"model_of_reality": model}


@register_rule("sched_contract_forbidden_update")
def sched_contract_forbidden_update(agent, observation):
    return {"decision_process": "maximize_value"}


@register_rule("sched_contract_choose_by_flag")
def sched_contract_choose_by_flag(agent):
    return HIGH if agent.model_of_reality.get("flag") else LOW


@register_rule("sched_contract_mutating_decision")
def sched_contract_mutating_decision(agent):
    agent.model_of_reality["flag"] = True
    return LOW


_DECISIONS = []


@register_rule("sched_contract_recording_decision")
def sched_contract_recording_decision(agent):
    _DECISIONS.append(agent.name)
    return LOW


def make_agent(name, decision_process="sched_contract_choose_by_flag", update_rule=None):
    return AgentSpec(
        name=name,
        objective="test objective",
        model_of_reality={"flag": False},
        perceived_feasible_set=[LOW, HIGH],
        valuation_rule="mapped_value",
        decision_process=decision_process,
        update_rule=update_rule,
    )


AGENT_A = make_agent("agent_a", update_rule="sched_contract_flag_update")
AGENT_B = make_agent("agent_b", update_rule="sched_contract_flag_update")


BASE_SCENARIO = Scenario(
    name="Scheduled Engine Contract",
    description="Minimal scenario for the scheduled engine's contracts.",
    periods=2,
    initial_state={"counter": 0},
    agents=[AGENT_A, AGENT_B],
    reality="sched_contract_echo_reality",
    transition="sched_contract_count_transition",
    observation="sched_contract_observe_own",
)


class TestRealityResultContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- RealityResult"

    def test_reality_result_contents_are_immutable(self):
        result = RealityResult(system={"x": [1]}, agents={"a": {"y": 2}})

        with self.assertRaises(TypeError):
            result.system["x"] = 2

        with self.assertRaises(TypeError):
            result.system["x"].append(2)

        with self.assertRaises(TypeError):
            result.agents["a"]["y"] = 3

        with self.assertRaises(FrozenInstanceError):
            result.system = {}

    def test_reality_result_does_not_alias_its_inputs(self):
        system = {"x": [1]}
        result = RealityResult(system=system)

        system["x"].append(2)

        self.assertEqual(result.system, {"x": [1]})

    def test_reality_must_return_a_reality_result(self):
        with self.assertRaises(TypeError):
            run_scenario(
                BASE_SCENARIO.variant(
                    reality="sched_contract_legacy_shaped_reality",
                    transition=None,
                )
            )

    def test_reality_may_only_report_outcomes_for_scenario_agents(self):
        with self.assertRaises(ValueError):
            run_scenario(
                BASE_SCENARIO.variant(
                    reality="sched_contract_unknown_agent_reality",
                    transition=None,
                )
            )


class TestRealityTransitionSplitContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- R / Transition Split"

    def test_reality_cannot_change_the_objective_state(self):
        with self.assertRaises(TypeError):
            run_scenario(
                BASE_SCENARIO.variant(
                    reality="sched_contract_mutating_reality",
                    transition=None,
                )
            )

    def test_only_the_transition_advances_the_objective_state(self):
        result = run_scenario(BASE_SCENARIO)

        self.assertEqual(
            [state["counter"] for state in result.history],
            [0, 2, 4],
        )

    def test_without_a_transition_the_objective_state_carries_forward(self):
        result = run_scenario(BASE_SCENARIO.variant(transition=None))

        self.assertEqual(
            [state["counter"] for state in result.history],
            [0, 0, 0],
        )

    def test_history_is_the_sequence_of_objective_states(self):
        result = run_scenario(BASE_SCENARIO)

        self.assertEqual(result.initial, BASE_SCENARIO.initial_state)
        self.assertEqual(result.final, result.trace[-1].objective_state)
        self.assertEqual(len(result.history), BASE_SCENARIO.periods + 1)


class TestObservationContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- Observation"

    def test_an_observation_changes_state_only_for_the_next_decision(self):
        result = run_scenario(BASE_SCENARIO)

        self.assertEqual(result.trace[0].actions[AGENT_A.name], LOW)
        self.assertEqual(result.trace[1].actions[AGENT_A.name], HIGH)

    def test_without_an_observation_rule_no_agent_changes(self):
        result = run_scenario(BASE_SCENARIO.variant(observation=None))

        self.assertEqual(result.trace[1].actions[AGENT_A.name], LOW)
        self.assertFalse(
            result.trace[-1].agents[AGENT_A.name].model_of_reality["flag"]
        )

    def test_an_update_rule_sees_only_its_own_view_and_observation(self):
        _UPDATE_CALLS.clear()

        run_scenario(BASE_SCENARIO.variant(periods=1))

        self.assertEqual(len(_UPDATE_CALLS), 2)

        for view, observation in _UPDATE_CALLS:
            self.assertIsInstance(view, UpdateView)
            self.assertIsInstance(observation, Observation)
            self.assertFalse(hasattr(view, "objective_state"))
            self.assertEqual(observation.agent, view.name)
            self.assertEqual(observation["realized"], LOW)

    def test_an_update_rule_cannot_change_decision_or_value_rules(self):
        with self.assertRaises(ValueError):
            run_scenario(
                BASE_SCENARIO.variant(
                    agents=[
                        make_agent(
                            "agent_a",
                            update_rule="sched_contract_forbidden_update",
                        ),
                    ],
                )
            )

    def test_a_decision_process_cannot_change_agent_state_in_place(self):
        with self.assertRaises(TypeError):
            run_scenario(
                BASE_SCENARIO.variant(
                    agents=[
                        make_agent(
                            "agent_a",
                            decision_process="sched_contract_mutating_decision",
                        ),
                    ],
                )
            )


class TestScheduleContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- Schedule"

    def test_inactive_agents_do_not_decide(self):
        _DECISIONS.clear()

        result = run_scenario(
            BASE_SCENARIO.variant(
                periods=3,
                agents=[
                    make_agent("agent_a", "sched_contract_recording_decision"),
                    make_agent("agent_b", "sched_contract_recording_decision"),
                ],
                schedule=Schedule.sequential("agent_a", "agent_b"),
            )
        )

        self.assertEqual(_DECISIONS, ["agent_a", "agent_b", "agent_a"])
        self.assertEqual(
            [step.actors for step in result.trace],
            [("agent_a",), ("agent_b",), ("agent_a",)],
        )
        self.assertEqual(
            [set(step.actions) for step in result.trace],
            [{"agent_a"}, {"agent_b"}, {"agent_a"}],
        )

    def test_inactive_agents_contribute_no_action_to_reality(self):
        result = run_scenario(
            BASE_SCENARIO.variant(
                schedule=Schedule.staged(("agent_a",), ("agent_a", "agent_b")),
            )
        )

        self.assertEqual(result.trace[0].reality.system["actors"], 1)
        self.assertEqual(result.trace[1].reality.system["actors"], 2)

    def test_actors_at_one_point_decide_before_anything_there_is_realized(self):
        # Both agents act at t=0. If either's decision could see the
        # other's realized outcome (and so its update), it would select
        # HIGH at t=0.
        result = run_scenario(
            BASE_SCENARIO.variant(
                schedule=Schedule.staged(("agent_a", "agent_b")),
            )
        )

        self.assertEqual(
            dict(result.trace[0].actions),
            {"agent_a": LOW, "agent_b": LOW},
        )

    def test_a_schedule_naming_an_unknown_agent_is_refused(self):
        with self.assertRaises(ValueError):
            run_scenario(
                BASE_SCENARIO.variant(schedule=Schedule.sequential("nobody"))
            )

    def test_an_agent_that_never_acts_has_no_selected_action(self):
        result = run_scenario(
            BASE_SCENARIO.variant(schedule=Schedule.sequential("agent_a"))
        )

        agent_b = result.agent("agent_b")

        self.assertIsNone(agent_b.selected_action)
        self.assertEqual(agent_b.outcome, {})


class TestTraceContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- Trace"

    def test_every_trace_field_is_immutable(self):
        trace = run_scenario(BASE_SCENARIO).trace
        step = trace[0]

        with self.assertRaises(TypeError):
            step.actions["agent_a"] = HIGH

        with self.assertRaises(TypeError):
            step.objective_state["counter"] = 99

        with self.assertRaises(TypeError):
            step.observations["agent_a"].data["realized"] = HIGH

        with self.assertRaises(TypeError):
            step.agents["agent_a"].model_of_reality["flag"] = False

        with self.assertRaises(TypeError):
            step.agents["agent_a"].perceived_feasible_set.append(HIGH)

        with self.assertRaises(FrozenInstanceError):
            step.step = 5

        with self.assertRaises(FrozenInstanceError):
            trace.steps = ()

    def test_each_step_records_the_state_it_produced(self):
        trace = run_scenario(BASE_SCENARIO).trace

        self.assertFalse(trace.initial_agents["agent_a"].model_of_reality["flag"])
        self.assertTrue(trace[0].agents["agent_a"].model_of_reality["flag"])
        self.assertEqual(trace.objective_state_before(1), trace[0].objective_state)

    def test_the_scenario_declaration_is_not_changed_by_a_run(self):
        run_scenario(BASE_SCENARIO)

        self.assertEqual(BASE_SCENARIO.initial_state, {"counter": 0})
        self.assertEqual(AGENT_A.model_of_reality, {"flag": False})


class TestCounterfactualContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- Counterfactual Re-runs"

    def test_a_counterfactual_holds_other_actions_and_f_t_fixed(self):
        result = run_scenario(BASE_SCENARIO)

        counterfactual = result.counterfactual(0, {"agent_a": HIGH})

        self.assertEqual(counterfactual.agent("agent_a")["realized"], HIGH)
        self.assertEqual(counterfactual.agent("agent_b")["realized"], LOW)

    def test_a_counterfactual_does_not_alter_the_recorded_trace(self):
        result = run_scenario(BASE_SCENARIO)
        recorded = result.trace[0].reality

        result.counterfactual(0, {"agent_a": HIGH})

        self.assertIs(result.trace[0].reality, recorded)
        self.assertEqual(recorded.agent("agent_a")["realized"], LOW)

    def test_an_inactive_agent_cannot_be_given_a_counterfactual_action(self):
        result = run_scenario(
            BASE_SCENARIO.variant(schedule=Schedule.sequential("agent_a", "agent_b"))
        )

        with self.assertRaises(ValueError):
            result.counterfactual(0, {"agent_b": HIGH})

    def test_a_nondeterministic_reality_is_refused(self):
        result = run_scenario(
            BASE_SCENARIO.variant(
                reality="sched_contract_nondeterministic_reality",
                transition=None,
                observation=None,
            )
        )

        with self.assertRaises(RuntimeError):
            result.counterfactual(0, {"agent_a": HIGH})


class TestScenarioDeclarationContract(unittest.TestCase):
    TEST_NAME = "Framework: Scheduled Engine -- Scenario Declaration"

    def test_a_scenario_without_rules_still_records_a_trace(self):
        result = run_scenario(
            Scenario(
                name="Decision only",
                description="No reality, transition, or observation rule.",
                periods=1,
                initial_state={},
                agents=[make_agent("agent_a")],
            )
        )

        self.assertEqual(dict(result.trace[0].actions), {"agent_a": LOW})
        self.assertEqual(result.trace[0].reality, RealityResult())

    def test_a_variant_cannot_introduce_an_unknown_field(self):
        with self.assertRaises(TypeError):
            BASE_SCENARIO.variant(feedback_rule="anything")

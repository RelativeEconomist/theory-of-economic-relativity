"""
TER Replication Test 22: Learning / Feasible Set Discovery
Canonical TER: theory/academic.md, Models 5.1, 5.2 and 5.5

Economic question
-----------------
In this configured scenario, does a realized outcome lead an agent to add
to its Perceived Feasible Set an action that the scenario's permission
data already lists as permitted, so that a later decision selects it?

Scenario
--------
An agent has two actions. BETTER_ACTION is listed as permitted from period
0 onward, but the agent does not initially perceive it:

    permission data (F_t aspect) = [ORDINARY_ACTION, BETTER_ACTION], throughout
    F̂ at period 0               = [ORDINARY_ACTION]

Period 0's decision is therefore restricted to ORDINARY_ACTION. The
realized outcome records that experience; the agent observes it and adds
BETTER_ACTION to F̂ for period 1, where maximize_value selects
it for its higher declared value.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 obtain the highest payoff from its choice      fixed
                              of action
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    [ORDINARY_ACTION] at period 0; adds            varied (by update)
                              BETTER_ACTION for period 1
V   Valuation                 mapped_value                           fixed
H   Time Horizon              "ongoing decision"                             fixed
D   Decision Process          maximize_value                       fixed
C   Selected Action           ORDINARY_ACTION (period 0), BETTER_ACTION      observed
                              (period 1)
F_t aspects                   permission data declared in                    fixed
                              objective_state["permitted_actions"]:
                              ORDINARY_ACTION
                              and BETTER_ACTION are listed as permitted;
                              no rule changes it
R   Reality Function          record_experienced_action (local): reports    fixed
                              the action the agent selected as the action
                              it experienced
O_{i,t} Realized Outcome      experienced_action, from R                     observed
Observation                   observe_own_outcome: the agent         fixed
                              observes its own O_{i,t} exactly
Update (Model 5.5)            learn_from_experience (local): adds            fixed
                              BETTER_ACTION to F̂ once the agent observes
                              that it experienced ORDINARY_ACTION

The scenario's mismatch is between F̂ (what the agent perceives) and the
permission data (BETTER_ACTION listed as permitted but not perceived). No
Python field is claimed to be F_t.

Economic mechanism
------------------
Period 0: F̂ = [ORDINARY_ACTION], so the decision process selects
ORDINARY_ACTION (the only option). R reports the realized outcome,
recording that ORDINARY_ACTION was experienced. The agent observes that
outcome, and its update rule adds BETTER_ACTION to F̂ before period 1
begins.

Period 1: F̂ = [ORDINARY_ACTION, BETTER_ACTION], so maximize_value now
selects BETTER_ACTION (value 9 > 4).

Assumptions
-----------
- Scope: this is a single-agent specification, so Model 5.2 applies and
  the realized outcome is O_{i,t} (RealityResult.agents). No contemporaneous
  multi-agent interaction is modeled, and no system outcome exists here.
- ORDINARY_ACTION and BETTER_ACTION's declared values are test-specific
  economic assumptions, not TER primitives.
- record_experienced_action (R) and learn_from_experience (the Model 5.5
  update) are local rules for this test only. Each implements an
  existing TER component as a test-specific specification, not a TER
  primitive or a universal outcome or learning rule. R reports exactly the
  selected action, with no other consequence logic. Both rules are passed
  directly as functions; no registration is needed.
- The update changes only what the agent perceives (F̂), and only
  because the agent observed the realized outcome. Selected action ->
  realized outcome -> observation -> later change in F̂; nothing reads
  the selected action directly to change F̂. Model 5.5 (Section 5.5) allows experience to bring F̂ closer to what
  F_t permits, and this rule implements one such trigger (having just
  experienced ORDINARY_ACTION); it does not claim experience always
  improves perception.
- The permission data is never written by anything in this test. The
  action is listed as permitted throughout; only what the agent perceives
  changes.
- The test does not model why the agent initially failed to perceive
  BETTER_ACTION, or a general process of learning.
- The run's trace records each decision point's actions and the agent's
  resulting state immutably, so F̂ before and after each update can be
  read directly from it.

Hypothesis
----------
In this configured scenario:
1. BETTER_ACTION appears in the permission data but not in the initial
   Perceived Feasible Set (a scenario-premise check).
2. The first decision is restricted to ORDINARY_ACTION.
3. The observed outcome of that decision causes the update to add
   BETTER_ACTION to the Perceived Feasible Set for the next decision.
4. The next decision selects BETTER_ACTION, now perceived and more highly
   valued.
5. The permission data does not change during the run; only perception
   does.
"""

import unittest

from research.ter import (
    AgentSpec,
    RealityResult,
    Scenario,
    run_scenario,
)
from research.ter.rules import mapped_value, maximize_value, observe_own_outcome



# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

ORDINARY_ACTION = "ordinary_action"
BETTER_ACTION = "better_alternative_action"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

ORDINARY_ACTION_VALUE = 4
BETTER_ACTION_VALUE = 9


def record_experienced_action(actions, objective_state, parameters):
    """
    Local reality rule for this test only. Implements R (Model 5.2,
    single-agent specification) as a test-specific specification, not a
    TER primitive or universal outcome rule.

    Realizes O_{i,t} as simply the action the agent actually selected --
    this test's economics need nothing more elaborate than "the agent
    experienced whatever it selected."
    """
    return RealityResult(
        agents={
            name: {"experienced_action": action}
            for name, action in actions.items()
        },
    )


def learn_from_experience(agent, observation):
    """
    Local update rule for this test only. Implements the agent-side half
    of Model 5.5 as a test-specific specification, not a TER primitive
    or universal learning rule.

    Once the agent observes (observe_own_outcome) that it
    experienced ORDINARY_ACTION, BETTER_ACTION is added to its perceived
    feasible set. It reads only its own observation and its own F̂ --
    never the permission data, which it cannot reach.

    Required observation field:

        experienced_action   the agent's own O_{i,t}
    """
    if observation["experienced_action"] != ORDINARY_ACTION:
        return {}

    if BETTER_ACTION in agent.perceived_feasible_set:
        return {}

    return {
        "perceived_feasible_set": agent.perceived_feasible_set + [BETTER_ACTION],
    }


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="decision_maker",
    objective="obtain the highest payoff from its choice of action",
    model_of_reality={},
    valuation={
        "values": {
            ORDINARY_ACTION: ORDINARY_ACTION_VALUE,
            BETTER_ACTION: BETTER_ACTION_VALUE,
        },
    },
    perceived_feasible_set=[
        ORDINARY_ACTION,
    ],
    valuation_rule=mapped_value,
    decision_process=maximize_value,
    horizon="ongoing decision",
    update_rule=learn_from_experience,
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

LEARNING_SCENARIO = Scenario(
    name="Feasible Set Discovery Through Experience",
    description=(
        "An agent initially perceives only one of two actions the "
        "objective feasible state of reality permits. Experience from the "
        "first decision expands what it perceives as feasible before the "
        "next decision."
    ),
    periods=2,
    initial_state={
        # Scenario permission data: both actions are permitted by the relevant
        # reality constraint from the start (an implementation representation,
        # not F_t itself).
        "permitted_actions": {
            BASE_AGENT.name: [
                ORDINARY_ACTION,
                BETTER_ACTION,
            ],
        },
    },
    agents=[
        BASE_AGENT,
    ],
    reality=record_experienced_action,
    observation=observe_own_outcome,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFeasibleSetLearning(unittest.TestCase):
    TEST_NAME = "Test 22: Learning / Feasible Set Discovery"

    def test_better_action_is_permitted_but_not_initially_perceived(self):
        # Scenario-premise check: the configured mismatch between the
        # permission data and the initial Perceived Feasible Set. It guards
        # the fixture and is not evidence for the learning hypothesis.
        self.assertIn(
            BETTER_ACTION,
            LEARNING_SCENARIO.initial_state["permitted_actions"][BASE_AGENT.name],
        )

        self.assertNotIn(
            BETTER_ACTION,
            BASE_AGENT.perceived_feasible_set,
        )

    def test_first_decision_is_restricted_to_the_perceived_feasible_set(self):
        result = run_scenario(LEARNING_SCENARIO)

        first_period_selection = result.trace[0].actions

        self.assertEqual(
            first_period_selection[BASE_AGENT.name],
            ORDINARY_ACTION,
        )

        # BETTER_ACTION is worth more. If it had already been perceived
        # feasible, maximize_value would have selected it instead.
        # Selecting the lower-valued action is itself evidence that
        # BETTER_ACTION was not yet in F_hat at this decision -- this
        # does not require reading AgentState.perceived_feasible_set, which
        # would be unsafe here (see the implementation note in Assumptions).
        self.assertGreater(
            BETTER_ACTION_VALUE,
            ORDINARY_ACTION_VALUE,
        )

    def test_feedback_admits_better_action_after_the_first_selection(self):
        result = run_scenario(LEARNING_SCENARIO)

        second_period_selection = result.trace[1].actions

        # select_action enforces C in F_hat (see
        # test_agent_decision_contract.py). BETTER_ACTION being the
        # recorded selection for period 1 is therefore itself proof that
        # the update had already added it to F_hat by the time that
        # decision ran.
        self.assertEqual(
            second_period_selection[BASE_AGENT.name],
            BETTER_ACTION,
        )

        # The trace shows the same thing directly: F_hat as the agent
        # held it before each decision.
        self.assertEqual(
            result.trace.agents_before(0)[BASE_AGENT.name].perceived_feasible_set,
            [ORDINARY_ACTION],
        )

        self.assertEqual(
            result.trace.agents_before(1)[BASE_AGENT.name].perceived_feasible_set,
            [ORDINARY_ACTION, BETTER_ACTION],
        )

    def test_permission_data_never_changes(self):
        result = run_scenario(LEARNING_SCENARIO)

        self.assertEqual(
            result.final["permitted_actions"],
            LEARNING_SCENARIO.initial_state["permitted_actions"],
        )

        self.assertIn(
            BETTER_ACTION,
            result.final["permitted_actions"][BASE_AGENT.name],
        )

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
realized outcome records that experience; feedback then adds
BETTER_ACTION to F̂ for period 1, where DecisionProcess.MAXIMIZE selects
it for its higher declared value.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 obtain the highest payoff from its choice      fixed
                              of action
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    [ORDINARY_ACTION] at period 0; adds            varied (by feedback)
                              BETTER_ACTION for period 1
V   Valuation                 ValuationRule.MAPPED                           fixed
H   Time Horizon              "ongoing decision"                             fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           ORDINARY_ACTION (period 0), BETTER_ACTION      observed
                              (period 1)
F_t aspects                   permission data declared in                    fixed
                              state["permitted_actions"]: ORDINARY_ACTION
                              and BETTER_ACTION are listed as permitted;
                              R and feedback do not read or change it
R   Reality Function          record_experienced_action (local): reports    fixed
                              the action the agent selected as the action
                              it experienced
O_{i,t} Realized Outcome      experienced_action_by_agent, from R            observed
Feedback (Model 5.5)          learn_from_experience (local): adds            fixed
                              BETTER_ACTION to F̂ once the realized outcome
                              records that ORDINARY_ACTION was experienced

The scenario's mismatch is between F̂ (what the agent perceives) and the
permission data (BETTER_ACTION listed as permitted but not perceived). No
Python field is claimed to be F_t.

Economic mechanism
------------------
Period 0: F̂ = [ORDINARY_ACTION], so the decision process selects
ORDINARY_ACTION (the only option). R reports the realized outcome,
recording that ORDINARY_ACTION was experienced. Feedback reads that
outcome and adds BETTER_ACTION to F̂ before period 1 begins.

Period 1: F̂ = [ORDINARY_ACTION, BETTER_ACTION], so MAXIMIZE now selects
BETTER_ACTION (value 9 > 4).

Assumptions
-----------
- Scope: this is a single-agent specification, so Model 5.2 applies and
  the realized outcome is O_{i,t}. It is keyed by agent name only because
  that is how the reality function reports it. No contemporaneous
  multi-agent interaction is modeled, and no system outcome exists here.
- ORDINARY_ACTION and BETTER_ACTION's declared values are test-specific
  economic assumptions, not TER primitives.
- record_experienced_action (R) and learn_from_experience (Model 5.5
  feedback) are local rules for this test only. Each implements an
  existing TER component as a test-specific specification, not a TER
  primitive or a universal outcome or learning rule. R reports exactly the
  selected action, with no other consequence logic. (They are registered
  with register_rule, an implementation detail.)
- Feedback changes only what the agent perceives (F̂), and only because
  it reads the realized outcome. Selected action -> realized outcome ->
  later change in F̂; nothing reads the selected action directly to change
  F̂. Model 5.5 (Section 5.5) allows experience to bring F̂ closer to what
  F_t permits, and this rule implements one such trigger (having just
  experienced ORDINARY_ACTION); it does not claim experience always
  improves perception.
- The permission data is never written by anything in this test. The
  action is listed as permitted throughout; only what the agent perceives
  changes.
- The test does not model why the agent initially failed to perceive
  BETTER_ACTION, or a general process of learning.
- Implementation note: history[t]["agents"] holds live AgentState objects
  shared across periods, so this test reads BASE_AGENT's declared lists and
  history[t]["selected_action_by_agent"] (a fresh dict per period) instead
  of live AgentState fields.

Hypothesis
----------
In this configured scenario:
1. BETTER_ACTION appears in the permission data but not in the initial
   Perceived Feasible Set (a scenario-premise check).
2. The first decision is restricted to ORDINARY_ACTION.
3. The realized outcome of that decision causes feedback to add
   BETTER_ACTION to the Perceived Feasible Set for the next decision.
4. The next decision selects BETTER_ACTION, now perceived and more highly
   valued.
5. The permission data does not change during the run; only perception
   does.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario
from research.ter.rules import register_rule


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


@register_rule("record_experienced_action")
def record_experienced_action(state, agents, actions, parameters):
    """
    Local reality function for this test only. Implements R (Model 5.2,
    single-agent specification) as a test-specific specification, not a
    TER primitive or universal outcome rule.

    Reports O_{i,t} as simply the action the agent actually selected --
    this test's economics need nothing more elaborate than "the agent
    experienced whatever it selected." Reports experienced_action_by_
    agent, keyed by agent name, so learn_from_experience can read a
    realized outcome, never the agent's own valuation or decision process.
    """
    return {
        "experienced_action_by_agent": {
            agent.name: action
            for agent, action in zip(agents, actions)
        },
    }


@register_rule("learn_from_experience")
def learn_from_experience(state, outcome, parameters):
    """
    Local feedback rule for this test only. Implements Model 5.5 feedback
    as a test-specific specification, not a TER primitive or universal
    learning rule.

    Once the realized outcome (from record_experienced_action) records that
    an agent experienced ORDINARY_ACTION, BETTER_ACTION -- listed as
    permitted in the permission data -- is added to that agent's perceived
    feasible set. state["permitted_actions"] is never touched.

    Required outcome field:

        experienced_action_by_agent   set every period by
                                       record_experienced_action, the
                                       reality function this scenario
                                       runs immediately before feedback.
    """
    experienced_action_by_agent = outcome["experienced_action_by_agent"]

    for agent in state["agents"]:
        if experienced_action_by_agent.get(agent.name) == ORDINARY_ACTION:
            if BETTER_ACTION not in agent.perceived_feasible_set:
                agent.perceived_feasible_set.append(BETTER_ACTION)

    return state


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
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="ongoing decision",
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
        "period": 0,
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
    reality_function="record_experienced_action",
    feedback_rule="learn_from_experience",
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

        first_period_selection = result.history[1]["selected_action_by_agent"]

        self.assertEqual(
            first_period_selection[BASE_AGENT.name],
            ORDINARY_ACTION,
        )

        # BETTER_ACTION is worth more. If it had already been perceived
        # feasible, DecisionProcess.MAXIMIZE would have selected it instead.
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

        second_period_selection = result.history[2]["selected_action_by_agent"]

        # select_action enforces C in F_hat (see
        # test_agent_decision_contract.py). BETTER_ACTION being the
        # recorded selection for period 1 is therefore itself proof that
        # feedback had already added it to F_hat by the time that
        # decision ran.
        self.assertEqual(
            second_period_selection[BASE_AGENT.name],
            BETTER_ACTION,
        )

    def test_subsequent_decision_selects_the_newly_perceived_higher_valued_action(self):
        result = run_scenario(LEARNING_SCENARIO)

        first_period_selection = result.history[1]["selected_action_by_agent"][BASE_AGENT.name]
        second_period_selection = result.history[2]["selected_action_by_agent"][BASE_AGENT.name]

        self.assertEqual(
            first_period_selection,
            ORDINARY_ACTION,
        )

        self.assertEqual(
            second_period_selection,
            BETTER_ACTION,
        )

        self.assertNotEqual(
            first_period_selection,
            second_period_selection,
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

"""
TER Replication Test 22: Learning / Feasible Set Discovery

Economic question
------------------
Can TER represent learning, where an action is actually feasible but
not initially perceived as feasible, and a realized outcome provides
the information that causes the agent to recognize that action in the
next decision environment?

Scenario
--------
An agent has two actions. BETTER_ACTION is actually feasible from
period 0 onward, but the agent does not initially perceive it:

    F        = [ORDINARY_ACTION, BETTER_ACTION], throughout
    F_hat_0  = [ORDINARY_ACTION]

Period 0's decision is therefore restricted to ORDINARY_ACTION. The
realized outcome records that experience; feedback then adds
BETTER_ACTION to F_hat for period 1, where DecisionProcess.MAXIMIZE
selects it for its higher declared value.

TER mapping
-----------
The canonical dynamic path, followed exactly:

    C_t ──→ R ──→ O_t ──→ feedback ──→ F̂_{t+1} ──→ C_{t+1}

    C_0        ORDINARY_ACTION -- the only perceived feasible action
    R          record_experienced_action, a local Model 5.2 reality
               function reading each agent's actual selected action
    O_0        {"experienced_action_by_agent": {agent: ORDINARY_ACTION}}
    feedback   learn_from_experience, a local Model 5.5 feedback rule:
               adds BETTER_ACTION to F_hat once O_0 records that
               ORDINARY_ACTION was experienced
    F̂_1        [ORDINARY_ACTION, BETTER_ACTION]
    C_1        BETTER_ACTION -- now perceived and more highly valued

G, M, V, H, and D are unchanged throughout: one AgentSpec, run through
one continuous Scenario.

Tested TER mechanics
--------------------
G     Objective              constant: maximize the value of the
                              perceived feasible action
M     Model of reality       specified but empty; constant
F     Actual feasible set    [ORDINARY_ACTION, BETTER_ACTION]; constant
F̂     Perceived feasible set [ORDINARY_ACTION] at t=0; CHANGED to add
                              BETTER_ACTION for t=1, by feedback
V     Valuation               ValuationRule.MAPPED; constant
H     Time horizon           constant: "ongoing decision"
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        ORDINARY_ACTION (t=0), BETTER_ACTION (t=1)
R     Reality function       local: record_experienced_action
O     Realized outcome       experienced_action_by_agent, from R
Feedback                     local: learn_from_experience, using O_0 to
                              update F̂_1

Economic mechanism
------------------
Period 0: F_hat = [ORDINARY_ACTION] -> C_0 = ORDINARY_ACTION (the only
option). R realizes O_0, recording that ORDINARY_ACTION was
experienced. Feedback sees that record and adds BETTER_ACTION to F_hat
before period 1 begins.

Period 1: F_hat = [ORDINARY_ACTION, BETTER_ACTION] -> MAXIMIZE now
selects BETTER_ACTION (value 9 > 4).

History caution
----------------
history[t]["agents"] holds live, mutable AgentState objects shared
across every period, not independent snapshots -- reading
perceived_feasible_set from history after the run finishes would show
the final, already-learned contents, not what was perceived at period
t. This test avoids that trap: it reads BASE_AGENT's own declared lists
(never mutated) and history[t]["selected_action_by_agent"] (a fresh
dict per period) instead of live AgentState fields.

Assumptions
-----------
- ORDINARY_ACTION and BETTER_ACTION's declared values are test-specific
  economic assumptions, not TER primitives.
- record_experienced_action is a local Model 5.2 reality function,
  scoped to this test only: it reports exactly what each agent actually
  selected, with no additional consequence logic. It is one admissible,
  minimal R -- not a universal TER outcome rule.
- learn_from_experience is a local Model 5.5 feedback rule, scoped to
  this test only (same convention as capacity_constrained_realization in
  test_feasibility_contract.py and the local rules in
  test_feedback_ordering_contract.py and test_21). It is one admissible
  operationalization of academic.md's Model 5.5 claim that "experience
  may bring F_hat closer to F" -- not a universal theory of learning. It
  does not claim experience always improves perception, only that it
  can under the specific trigger declared here (having just experienced
  ORDINARY_ACTION).
- actual_feasible_set is never written by anything in this test. The
  action was always actually feasible; only what the agent perceives
  changes.
- This test does not model why the agent initially failed to perceive
  BETTER_ACTION, or the general cognitive process of learning -- only
  that TER's existing reality/feedback mechanism can move F_hat between
  periods in response to a realized outcome.
- This does not introduce a new TER primitive or a universal learning
  rule: R and feedback here are ordinary, scenario-specific
  implementations of the existing extension points.

Hypothesis
----------
1. BETTER_ACTION is actually feasible but not initially perceived
   feasible.
2. The first decision is therefore restricted to ORDINARY_ACTION.
3. The realized outcome of that decision causes feedback to add
   BETTER_ACTION to the perceived feasible set for the next decision.
4. The next decision selects BETTER_ACTION now that it is perceived and
   more highly valued.
5. Actual feasibility never changes; only perception does.
6. This is produced through the existing TER Core decision, reality,
   and feedback paths -- ValuationRule.MAPPED and
   DecisionProcess.MAXIMIZE are the ordinary, shared rules; only R and
   feedback are local to this test.
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
    Local Model 5.2 reality function for this test only.

    Realizes O_t as simply the action each agent actually selected --
    this test's economics need nothing more elaborate than "the agent
    experienced whatever it selected." Reports experienced_action_by_
    agent, keyed by agent name, so learn_from_experience can read a
    genuine realized outcome, never the agent's own valuation or
    decision process.
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
    Local Model 5.5 feedback rule for this test only.

    Operationalizes "experience may bring F_hat closer to F": once O_t
    (from record_experienced_action) records that an agent experienced
    ORDINARY_ACTION, BETTER_ACTION -- already actually feasible -- is
    added to that agent's perceived feasible set. actual_feasible_set is
    never touched.

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
    objective="maximize the value of the perceived feasible action",
    model_of_reality={},
    valuation={
        "values": {
            ORDINARY_ACTION: ORDINARY_ACTION_VALUE,
            BETTER_ACTION: BETTER_ACTION_VALUE,
        },
    },
    actual_feasible_set=[
        ORDINARY_ACTION,
        BETTER_ACTION,
    ],
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
        "An agent initially perceives only one of two actually feasible "
        "actions. Experience from the first decision expands what it "
        "perceives as feasible before the next decision."
    ),
    periods=2,
    initial_state={
        "period": 0,
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

    def test_better_action_is_actually_feasible_but_not_initially_perceived(self):
        self.assertIn(
            BETTER_ACTION,
            BASE_AGENT.actual_feasible_set,
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
        # would be unsafe here (see History caution above).
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

    def test_actual_feasibility_never_changes(self):
        result = run_scenario(LEARNING_SCENARIO)

        self.assertEqual(
            result.agent(BASE_AGENT.name).actual_feasible_set,
            BASE_AGENT.actual_feasible_set,
        )

        self.assertIn(
            BETTER_ACTION,
            result.agent(BASE_AGENT.name).actual_feasible_set,
        )

    def test_learning_operates_through_the_standard_decision_and_valuation_rules(self):
        result = run_scenario(LEARNING_SCENARIO)
        agent = result.agent(BASE_AGENT.name)

        self.assertEqual(
            BASE_AGENT.valuation_rule,
            ValuationRule.MAPPED,
        )

        self.assertEqual(
            BASE_AGENT.decision_process,
            DecisionProcess.MAXIMIZE,
        )

        self.assertEqual(
            agent.objective,
            BASE_AGENT.objective,
        )

        self.assertEqual(
            agent.model_of_reality,
            BASE_AGENT.model_of_reality,
        )

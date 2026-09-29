"""
TER Replication Test 26: Sequential Entry
Canonical TER: theory/academic.md, Models 5.1, 5.3 and 5.5

Economic question
-----------------
When an incumbent moves first and an entrant observes that move before
deciding, can the incumbent's earlier action change the entrant's later
decision -- through what the entrant observes, not through the entrant
reading reality directly?

Scenario
--------
An incumbent decides whether to EXPAND capacity or HOLD. An entrant then
decides whether to ENTER or STAY_OUT. The entrant's payoff from entering
depends on the incumbent's capacity:

    entrant payoff   ENTER    STAY_OUT
    incumbent HOLD     4         0
    incumbent EXPAND  -2         0

The entrant's prior (M_0) is that the incumbent will HOLD. Under a
sequential schedule the entrant sees the incumbent's actual move before
choosing; under a simultaneous schedule it must act on its prior.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize own payoff                            fixed
M   Model of Reality          expected_other_action: each firm's belief      varied (entrant's, by
                              about the other's move                         observation)
F̂   Perceived Feasible Set    incumbent: EXPAND, HOLD;                       fixed
                              entrant: ENTER, STAY_OUT
V   Valuation                 ValuationRule.PAYOFF_MATRIX against M          fixed
H   Time Horizon              single market entry                            fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           one per firm, at its own decision point        observed
Schedule                      Schedule.sequential(incumbent, entrant), or    varied
                              Schedule.simultaneous() for comparison
F_t aspects used by R         capacity (objective state) and the actual      varied (capacity, by
                              payoff tables -- scenario-specified            transition)
                              conditions R reads
R   Reality Function          entry_game_reality (local): realizes the       fixed
                              incumbent's capacity choice, and the payoffs
                              of an entry decision against the capacity F_t
                              actually holds
Transition (O_t -> F_t+1)     entry_game_transition (local): a realized      fixed
                              capacity choice becomes F_t+1's capacity
Observation                   ObservationRule.PUBLIC_ACTIONS: both firms     fixed
                              observe every move exactly
Update (O_t -> M_t+1)         adopt_observed_move (local): a firm that       fixed
                              observes the other's move adopts it as its
                              expectation

Under the sequential schedule the incumbent acts at t=0 and is inactive
at t=1; the entrant is inactive at t=0 and acts at t=1. An inactive
agent's D is not called and it contributes no action to R. The
entrant's payoff at t=1 depends on capacity set at t=0, and the
incumbent's payoff at t=1 depends on the entrant's move, so both are
derived from the one joint R at t=1 (Model 5.3, "Agent-level
outcomes") even though only the entrant acts there.

Economic mechanism
------------------
The incumbent expects entry, and EXPAND (2) beats HOLD (1) against
ENTER, so it expands. Sequentially, the entrant observes EXPAND, updates
its expectation, and STAY_OUT (0) beats ENTER (-2). Simultaneously, the
entrant still expects HOLD, enters (4 > 0), and meets expanded capacity
anyway: the same choice by the incumbent, realized the same way, but
without the information pathway the entrant acts on a stale belief.

Assumptions
-----------
- Payoffs as each firm values them (V) equal the actual payoffs R reads
  (parameters). TER does not require this.
- Observation is exact and public; TER does not require either.
- The incumbent's own payoff from its capacity choice is realized only
  once the entrant's move is realized against it; at t=0 R realizes the
  capacity choice itself and no payoff.

Hypothesis
----------
In this configured scenario:
1. Only the scheduled agent acts at each decision point.
2. The incumbent expands.
3. Under the sequential schedule the entrant observes the expansion,
   updates its expectation, and stays out.
4. Under the simultaneous schedule the entrant, acting on its prior,
   enters and realizes a loss.
5. The entrant's outcome is realized against the capacity F_t holds at
   its own decision point, and a counterfactual ENTER there would have
   realized the loss.
"""

import unittest

from research.ter import (
    AgentSpec,
    DecisionProcess,
    ObservationRule,
    RealityResult,
    Scenario,
    Schedule,
    ValuationRule,
    run_scenario,
)
from research.ter.rules import register_rule


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

EXPAND = "expand"
HOLD = "hold"

ENTER = "enter"
STAY_OUT = "stay_out"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

# capacity -> entrant action -> payoff
ENTRANT_PAYOFFS = {
    HOLD: {ENTER: 4, STAY_OUT: 0},
    EXPAND: {ENTER: -2, STAY_OUT: 0},
}

# capacity -> entrant action -> payoff
INCUMBENT_PAYOFFS = {
    HOLD: {ENTER: 1, STAY_OUT: 5},
    EXPAND: {ENTER: 2, STAY_OUT: 3},
}


# ---------------------------------------------------------------------------
# Rules -- scoped to this test
# ---------------------------------------------------------------------------

@register_rule("entry_game_reality")
def entry_game_reality(actions, objective_state, parameters):
    """
    Local reality rule for this test only (Model 5.3).

    An incumbent action realizes a capacity choice (O_t). An entrant
    action is realized against the capacity in effect: the incumbent's
    move at this same point if it acted here, otherwise the capacity F_t
    already holds. Both firms' payoffs follow from that one joint
    realization.

    Required parameters:

        incumbent, entrant                 agent names
        incumbent_payoffs, entrant_payoffs capacity -> entry -> payoff
    """
    incumbent = parameters["incumbent"]
    entrant = parameters["entrant"]

    system = {}

    if incumbent in actions:
        system["capacity"] = actions[incumbent]

    if entrant not in actions:
        return RealityResult(system=system)

    capacity = system.get("capacity", objective_state.get("capacity"))
    entry = actions[entrant]

    return RealityResult(
        system=system,
        agents={
            entrant: {"payoff": parameters["entrant_payoffs"][capacity][entry]},
            incumbent: {"payoff": parameters["incumbent_payoffs"][capacity][entry]},
        },
    )


@register_rule("entry_game_transition")
def entry_game_transition(objective_state, reality, parameters):
    """
    Local transition for this test only: a realized capacity choice is
    the capacity F_t+1 holds.
    """
    if "capacity" in reality.system:
        objective_state["capacity"] = reality.system["capacity"]

    return objective_state


@register_rule("adopt_observed_move")
def adopt_observed_move(agent, observation):
    """
    Local update rule for this test only: a firm that observes the
    other firm's move adopts it as its expectation of that move.

    Required model_of_reality field:

        counterpart   the other firm's name
    """
    observed = observation["actions"].get(agent.model_of_reality["counterpart"])

    if observed is None:
        return {}

    model = agent.model_of_reality
    model["expected_other_action"] = observed

    return {"model_of_reality": model}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

INCUMBENT = AgentSpec(
    name="incumbent",
    objective="maximize own payoff",
    model_of_reality={
        "counterpart": "entrant",
        "expected_other_action": ENTER,
    },
    valuation={
        # own action -> entrant action -> payoff
        "payoff_matrix": INCUMBENT_PAYOFFS,
    },
    perceived_feasible_set=[
        EXPAND,
        HOLD,
    ],
    valuation_rule=ValuationRule.PAYOFF_MATRIX,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="single market entry",
    update_rule="adopt_observed_move",
)

ENTRANT = AgentSpec(
    name="entrant",
    objective="maximize own payoff",
    model_of_reality={
        "counterpart": INCUMBENT.name,
        "expected_other_action": HOLD,
    },
    valuation={
        # own action -> incumbent capacity -> payoff
        "payoff_matrix": {
            entry: {
                capacity: ENTRANT_PAYOFFS[capacity][entry]
                for capacity in ENTRANT_PAYOFFS
            }
            for entry in (ENTER, STAY_OUT)
        },
    },
    perceived_feasible_set=[
        ENTER,
        STAY_OUT,
    ],
    valuation_rule=ValuationRule.PAYOFF_MATRIX,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="single market entry",
    update_rule="adopt_observed_move",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SEQUENTIAL_SCENARIO = Scenario(
    name="Sequential Entry",
    description=(
        "The incumbent chooses capacity first; the entrant observes it "
        "and then decides whether to enter."
    ),
    periods=2,
    initial_state={},
    agents=[
        INCUMBENT,
        ENTRANT,
    ],
    parameters={
        "incumbent": INCUMBENT.name,
        "entrant": ENTRANT.name,
        "incumbent_payoffs": INCUMBENT_PAYOFFS,
        "entrant_payoffs": ENTRANT_PAYOFFS,
    },
    reality="entry_game_reality",
    transition="entry_game_transition",
    observation=ObservationRule.PUBLIC_ACTIONS,
    schedule=Schedule.sequential(INCUMBENT.name, ENTRANT.name),
)

SIMULTANEOUS_SCENARIO = SEQUENTIAL_SCENARIO.variant(
    name="Simultaneous Entry",
    description="Both firms decide at once; the entrant acts on its prior.",
    periods=1,
    schedule=Schedule.simultaneous(),
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSequentialEntry(unittest.TestCase):
    TEST_NAME = "Test 26: Sequential Entry"

    def test_only_the_scheduled_agent_acts_at_each_decision_point(self):
        trace = run_scenario(SEQUENTIAL_SCENARIO).trace

        self.assertEqual(trace[0].actors, (INCUMBENT.name,))
        self.assertEqual(set(trace[0].actions), {INCUMBENT.name})

        self.assertEqual(trace[1].actors, (ENTRANT.name,))
        self.assertEqual(set(trace[1].actions), {ENTRANT.name})

    def test_incumbent_expands(self):
        result = run_scenario(SEQUENTIAL_SCENARIO)

        self.assertEqual(
            result.agent(INCUMBENT.name).selected_action,
            EXPAND,
        )

    def test_entrant_observes_expansion_and_stays_out(self):
        result = run_scenario(SEQUENTIAL_SCENARIO)
        trace = result.trace

        # The entrant's belief before and after observing t=0's move.
        self.assertEqual(
            trace.agents_before(0)[ENTRANT.name].model_of_reality["expected_other_action"],
            HOLD,
        )

        self.assertEqual(
            trace[0].observations[ENTRANT.name]["actions"],
            {INCUMBENT.name: EXPAND},
        )

        self.assertEqual(
            trace.agents_before(1)[ENTRANT.name].model_of_reality["expected_other_action"],
            EXPAND,
        )

        self.assertEqual(
            result.agent(ENTRANT.name).selected_action,
            STAY_OUT,
        )

    def test_without_the_observation_the_entrant_enters_and_loses(self):
        result = run_scenario(SIMULTANEOUS_SCENARIO)
        entrant = result.agent(ENTRANT.name)

        self.assertEqual(
            result.agent(INCUMBENT.name).selected_action,
            EXPAND,
        )

        self.assertEqual(
            entrant.selected_action,
            ENTER,
        )

        self.assertEqual(
            entrant.payoff,
            ENTRANT_PAYOFFS[EXPAND][ENTER],
        )

        self.assertLess(
            entrant.payoff,
            0,
        )

    def test_entrant_is_realized_against_the_capacity_f_t_holds(self):
        result = run_scenario(SEQUENTIAL_SCENARIO)
        entrant = result.agent(ENTRANT.name)

        # F_1 carries the capacity realized at t=0.
        self.assertEqual(
            result.trace.objective_state_before(1)["capacity"],
            EXPAND,
        )

        self.assertEqual(
            entrant.payoff,
            ENTRANT_PAYOFFS[EXPAND][STAY_OUT],
        )

        # Counterfactual, not another realized outcome: the same R and
        # the same F_1, with the entrant entering instead.
        self.assertEqual(
            entrant.outcome_for(ENTER).payoff,
            ENTRANT_PAYOFFS[EXPAND][ENTER],
        )

        # The incumbent did not act at t=1, but its payoff there is
        # derived from the same joint realization.
        self.assertEqual(
            result.trace[1].reality.agent(INCUMBENT.name)["payoff"],
            INCUMBENT_PAYOFFS[EXPAND][STAY_OUT],
        )

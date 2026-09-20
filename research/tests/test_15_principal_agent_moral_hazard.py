"""
TER Replication Test 15: Principal-Agent and Moral Hazard
Canonical TER: theory/academic.md, Models 5.1 and 5.2

Economic question
-----------------
In a constructed principal-agent setting where effort is hidden and costly,
does a performance incentive change the effort a worker selects, and what
does the principal's outcome then become?

Scenario
--------
A worker chooses HIGH_EFFORT or LOW_EFFORT. Effort is private and
costly to the worker, and is not directly contractible by the principal
in the baseline:

    HIGH_EFFORT: cost 6   LOW_EFFORT: cost 2
    base compensation: 10 (paid regardless of effort, in the baseline)
    performance bonus: 5 (paid only when HIGH_EFFORT is chosen, in the
    incentive scenario)

    principal's outcome if HIGH_EFFORT: 20
    principal's outcome if LOW_EFFORT:  8

Without a performance incentive, LOW_EFFORT nets the worker more
(10 - 2 = 8 vs 10 - 6 = 4), even though HIGH_EFFORT produces the better
principal outcome (20 vs 8) -- this misalignment is the moral hazard.
A performance bonus large enough to reward HIGH_EFFORT (15 - 6 = 9 vs
10 - 2 = 8) realigns the worker's private incentive with the
principal's preferred outcome.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize personal compensation net of effort   fixed
                              cost
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    HIGH_EFFORT, LOW_EFFORT                        fixed
V   Valuation                 ValuationRule.NET: compensation (benefit)      varied (HIGH_EFFORT's
                              minus effort cost                              benefit only)
H   Time Horizon              current effort decision                        fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           HIGH_EFFORT or LOW_EFFORT                      observed
F_t aspects used by R         principal_outcomes_by_effort: the principal's  fixed
                              outcome under each effort level, a
                              scenario-specified condition R reads (not a
                              complete representation of F_t)
R   Reality Function          principal_outcome_by_effort (local):           fixed
                              realizes the principal's outcome from the
                              worker's selected effort, never from the
                              worker's V
O_{i,t} Realized Outcome      the principal's realized outcome, from R       observed
Feedback (Model 5.5)          none                                           --

This is a single-worker specification, so Model 5.2 applies. The
principal is not modeled as a TER agent; the outcome R realizes from the
worker's selected effort is the principal's outcome. No interaction among
multiple agents is modeled, and no system outcome O_t is defined.

Economic mechanism
------------------
Fixed compensation:

    HIGH_EFFORT: 10 - 6 = 4
    LOW_EFFORT:  10 - 2 = 8   -> selected

    realized principal outcome (from LOW_EFFORT): 8

Performance incentive:

    HIGH_EFFORT: 15 - 6 = 9   -> selected
    LOW_EFFORT:  10 - 2 = 8

    realized principal outcome (from HIGH_EFFORT): 20

Assumptions
-----------
- The principal cannot condition base compensation on the worker's effort in
  this test. Effort is treated as hidden/non-contractible in the
  baseline; the principal is not modeled as a separate TER agent.
- The performance bonus is a reduced-form representation of
  compensation expected to be associated with HIGH_EFFORT through an
  observable performance measure. The test does not model the
  measurement process, monitoring technology, or stochastic
  relationship between effort and performance.
- Effort costs, base compensation, and the performance bonus are
  test-specific economic assumptions, not TER primitives.
- The principal's outcome under each effort level
  (principal_outcomes_by_effort, a scenario parameter) is realized only
  by the reality side, from the worker's selected effort -- never
  read from or fed into the worker's own valuation. That separation is
  the moral-hazard mechanism itself: the principal's preference and the
  worker's private incentive are only brought into alignment by
  redesigning compensation (the bonus), never by the principal's outcome
  directly.
- This test does not provide a general theory of contracts, monitoring,
  or moral hazard; it demonstrates one incentive misalignment and one
  bonus large enough to correct it.

Hypothesis
----------
In this configured scenario:
1. Without a performance incentive, the agent selects LOW_EFFORT.
2. HIGH_EFFORT produces the better principal outcome.
3. Adding a sufficient performance bonus changes the agent's valuation so
   HIGH_EFFORT is selected.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario
from research.ter.rules import register_rule


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

HIGH_EFFORT = "high_effort"
LOW_EFFORT = "low_effort"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

HIGH_EFFORT_COST = 6
LOW_EFFORT_COST = 2

BASE_COMPENSATION = 10
PERFORMANCE_BONUS = 5

PRINCIPAL_OUTCOME_HIGH_EFFORT = 20
PRINCIPAL_OUTCOME_LOW_EFFORT = 8


@register_rule("principal_outcome_by_effort")
def principal_outcome_by_effort(state, agents, actions, parameters):
    """
    Local Model 5.2 reality function for this test only.

    Realizes the principal's outcome from the worker's actual selected
    effort and the scenario's own principal_outcomes_by_effort mapping
    -- never from the worker's own valuation. This is what keeps the
    principal's outcome a genuine O rather than something read off the
    worker's V: the worker's compensation/effort-cost valuation and the
    principal's outcome are computed from entirely separate data.

    Requires exactly one agent (the worker).

    Required parameter:

        principal_outcomes_by_effort   effort -> principal outcome
    """
    if len(agents) != 1:
        raise ValueError(
            "principal_outcome_by_effort requires exactly one agent."
        )

    (selected_effort,) = actions

    return {
        "principal_outcome": parameters["principal_outcomes_by_effort"][selected_effort],
    }


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_WORKER = AgentSpec(
    name="worker",
    objective="maximize personal compensation net of effort cost",
    model_of_reality={},
    valuation={
        "benefits": {
            HIGH_EFFORT: BASE_COMPENSATION,
            LOW_EFFORT: BASE_COMPENSATION,
        },
        "costs": {
            HIGH_EFFORT: HIGH_EFFORT_COST,
            LOW_EFFORT: LOW_EFFORT_COST,
        },
    },
    perceived_feasible_set=[
        HIGH_EFFORT,
        LOW_EFFORT,
    ],
    valuation_rule=ValuationRule.NET,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current effort decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

FIXED_COMPENSATION_SCENARIO = Scenario(
    name="Fixed Compensation (No Performance Incentive)",
    description="The worker is paid the same base compensation regardless of effort; only effort cost differs.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_WORKER,
    ],
    parameters={
        "principal_outcomes_by_effort": {
            HIGH_EFFORT: PRINCIPAL_OUTCOME_HIGH_EFFORT,
            LOW_EFFORT: PRINCIPAL_OUTCOME_LOW_EFFORT,
        },
    },
    reality_function="principal_outcome_by_effort",
)

PERFORMANCE_INCENTIVE_SCENARIO = FIXED_COMPENSATION_SCENARIO.variant(
    name="Performance-Based Compensation",
    description="A performance bonus rewards high effort, changing the worker's private incentive.",
    agents=[
        BASE_WORKER.variant(
            valuation={
                "benefits": {
                    HIGH_EFFORT: BASE_COMPENSATION + PERFORMANCE_BONUS,
                    LOW_EFFORT: BASE_COMPENSATION,
                },
            },
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPrincipalAgentMoralHazard(unittest.TestCase):
    TEST_NAME = "Test 15: Principal-Agent and Moral Hazard"

    def test_without_incentive_agent_selects_low_effort(self):
        agent = run_scenario(FIXED_COMPENSATION_SCENARIO).agent(BASE_WORKER.name)

        self.assertEqual(
            agent.selected_action,
            LOW_EFFORT,
        )

    def test_high_effort_produces_the_better_principal_outcome(self):
        # Realized principal outcomes come from O (the local
        # principal_outcome_by_effort reality function), driven by each
        # scenario's own actually selected effort -- not compared by
        # hand off the PRINCIPAL_OUTCOME_* constants.
        fixed_result = run_scenario(FIXED_COMPENSATION_SCENARIO)
        incentivized_result = run_scenario(PERFORMANCE_INCENTIVE_SCENARIO)

        self.assertEqual(
            fixed_result.agent(BASE_WORKER.name).selected_action,
            LOW_EFFORT,
        )

        self.assertEqual(
            fixed_result.final["principal_outcome"],
            PRINCIPAL_OUTCOME_LOW_EFFORT,
        )

        self.assertEqual(
            incentivized_result.agent(BASE_WORKER.name).selected_action,
            HIGH_EFFORT,
        )

        self.assertEqual(
            incentivized_result.final["principal_outcome"],
            PRINCIPAL_OUTCOME_HIGH_EFFORT,
        )

        self.assertGreater(
            incentivized_result.final["principal_outcome"],
            fixed_result.final["principal_outcome"],
        )

    def test_performance_bonus_makes_high_effort_privately_preferred(self):
        agent = run_scenario(PERFORMANCE_INCENTIVE_SCENARIO).agent(BASE_WORKER.name)

        self.assertEqual(
            agent.selected_action,
            HIGH_EFFORT,
        )

        self.assertEqual(
            agent.value_of(HIGH_EFFORT),
            BASE_COMPENSATION + PERFORMANCE_BONUS - HIGH_EFFORT_COST,
        )

        self.assertEqual(
            agent.value_of(LOW_EFFORT),
            BASE_COMPENSATION - LOW_EFFORT_COST,
        )

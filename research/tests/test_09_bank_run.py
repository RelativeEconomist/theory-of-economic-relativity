"""
TER Replication Test 09: Bank Run and Liquidity Feedback
Canonical TER: theory/academic.md, Models 5.1, 5.3 and 5.5

Economic question
-----------------
Can individually reasonable withdrawal decisions reduce a bank's
liquidity, and can that realized liquidity loss feed back into other
depositors' beliefs and trigger further withdrawal requests?

Scenario
--------
A bank starts with liquidity 1000. 3 depositors already perceive high
failure risk (failure_probability 0.50); 7 depositors start confident
(failure_probability 0.05):

    high-risk depositors (3): perceive 50% failure risk -> request WITHDRAW
    low-risk depositors  (7): perceive  5% failure risk -> choose STAY

The 3 requested withdrawals (300) are realized against the bank's
liquidity, leaving 700. Lower realized liquidity then raises every
depositor's perceived failure risk for the next period -- including the
previously confident ones. If that pushes a low-risk depositor's belief
past its own threshold, it now requests WITHDRAW too, even though nothing
about its personal risk_signal changed.

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 preserve deposit value                         fixed
M   Model of Reality          failure_probability and risk_signal: each      varied (failure_probability,
                              depositor's belief about the bank, not a       by feedback)
                              valuation
F̂   Perceived Feasible Set    STAY, WITHDRAW                                 fixed
V   Valuation                 ValuationRule.BANK_DEPOSITOR: deposit_value,   fixed
                              deposit_benefit, withdrawal_cost
H   Time Horizon              immediate liquidity decision                   fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           STAY, or WITHDRAW (a withdrawal request)       observed
F_t aspects used by R         the bank's liquidity (scenario state) and      varied (liquidity, by R)
                              withdrawal_amount -- scenario-specified
                              conditions R reads (not a complete
                              representation of F_t)
R   Reality Function          RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY:  fixed
                              realizes as much of the requested
                              withdrawals as liquidity allows
O_t System Outcome            withdrawal requests, realized withdrawals,     observed
                              and remaining liquidity, from R
Feedback (Model 5.5)          FeedbackRule.BANK_LIQUIDITY_CONFIDENCE:        fixed
                              updates the next period's M from this
                              period's realized liquidity

This is a multi-agent specification: R takes all depositors' selected
actions together, so Model 5.3 applies. This test defines no individual
outcomes O_{i,t} and no relationship between them and O_t.

WITHDRAW means the depositor submits a withdrawal request. What happens
to the request is R's job: WITHDRAWALS_REDUCE_LIQUIDITY realizes only as
much as the bank's liquidity allows. Requested withdrawals can therefore
exceed realized withdrawals; the depositor's selected action stays
WITHDRAW, and only how much of it is realized differs.

Economic mechanism
------------------
Period 0: high-risk depositors' already-elevated M_0 makes WITHDRAW
their best response immediately; low-risk depositors' M_0 makes STAY
theirs. R realizes the 3 requested withdrawals against the bank's
liquidity (1000 -> 700). Feedback then raises every depositor's
failure_probability from that lower liquidity, including low-risk
depositors whose own risk_signal never changed. If the resulting belief
crosses their own threshold, period 1 sees additional WITHDRAW requests
-- more withdrawal pressure than period 0, produced entirely by the
realized-liquidity -> belief -> decision loop, not by any change in the
depositor's valuation or personal risk signal.

Assumptions
-----------
- The bank itself is not an AgentState; liquidity is scenario state, and
  withdrawal capacity is capped by RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY
  reading scenario state["liquidity"], not by any per-agent permission.
- initial_liquidity is a scenario parameter used to normalize perceived
  risk; it is independent of the "liquidity" state value.
- Every depositor's initial failure_probability (M_0) is set equal to
  its own risk_signal directly, not left for feedback to fill in:
  feedback only ever updates M for a period that follows a realized
  outcome, and there is no realized outcome before period 0's decision.
  This is exactly what BANK_LIQUIDITY_CONFIDENCE would compute anyway
  from a starting liquidity_risk of 0, stated up front instead of
  relying on that coincidence.

Hypothesis
----------
In this configured scenario:
1. High-confidence depositors prefer to remain deposited.
2. High perceived failure risk produces withdrawal.
3. Initial withdrawals reduce bank liquidity.
4. Reduced liquidity raises perceived failure risk.
5. Feedback can produce additional withdrawals.
6. High liquidity and confidence can remain stable.
7. Requested withdrawals may exceed the liquidity available to realize
   them.
"""

import unittest

from research.ter import (
    AgentGroup,
    AgentSpec,
    DecisionProcess,
    FeedbackRule,
    RealityFunction,
    Scenario,
    ValuationRule,
    run_scenario,
)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

STAY = "stay"
WITHDRAW = "withdraw"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

STABLE_DEPOSITOR_COUNT = 10

HIGH_RISK_DEPOSITOR_COUNT = 3
LOW_RISK_DEPOSITOR_COUNT = 7

INSOLVENT_DEPOSITOR_COUNT = 5

BASE_FAILURE_PROBABILITY = 0.05
LOW_RISK_SIGNAL = 0.05
HIGH_RISK_SIGNAL = 0.50
INSOLVENT_RISK_SIGNAL = 0.90

DEPOSIT_VALUE = 100
DEPOSIT_BENEFIT = 6
WITHDRAWAL_COST = 1

STARTING_LIQUIDITY = 1000
INSOLVENT_STARTING_LIQUIDITY = 200
RISK_NORMALIZATION_LIQUIDITY = 1000

WITHDRAWAL_AMOUNT = 100


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_DEPOSITOR = AgentSpec(
    name="depositor",
    objective="preserve deposit value",
    model_of_reality={
        "failure_probability": BASE_FAILURE_PROBABILITY,
        "risk_signal": LOW_RISK_SIGNAL,
    },
    valuation={
        "deposit_value": DEPOSIT_VALUE,
        "deposit_benefit": DEPOSIT_BENEFIT,
        "withdrawal_cost": WITHDRAWAL_COST,
    },
    perceived_feasible_set=[
        STAY,
        WITHDRAW,
    ],
    valuation_rule=ValuationRule.BANK_DEPOSITOR,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="immediate liquidity decision",
)


STABLE_DEPOSITORS = AgentGroup(
    base=BASE_DEPOSITOR,
    count=STABLE_DEPOSITOR_COUNT,
    name_prefix="depositor",
)


HIGH_RISK_DEPOSITORS = AgentGroup(
    base=BASE_DEPOSITOR,
    count=HIGH_RISK_DEPOSITOR_COUNT,
    name_prefix="depositor",
    model_of_reality={
        # M_0: before any liquidity feedback, a depositor's own belief
        # already equals its personal risk signal (bank_liquidity_
        # confidence would compute the same thing from a starting
        # liquidity_risk of 0 -- this just states it directly instead of
        # relying on feedback to initialize the first decision).
        "risk_signal": HIGH_RISK_SIGNAL,
        "failure_probability": HIGH_RISK_SIGNAL,
    },
)

LOW_RISK_DEPOSITORS = AgentGroup(
    base=BASE_DEPOSITOR,
    count=LOW_RISK_DEPOSITOR_COUNT,
    name_prefix="depositor",
    start_index=HIGH_RISK_DEPOSITOR_COUNT + 1,
    model_of_reality={
        "risk_signal": LOW_RISK_SIGNAL,
        "failure_probability": LOW_RISK_SIGNAL,
    },
)

RUN_DEPOSITORS = HIGH_RISK_DEPOSITORS + LOW_RISK_DEPOSITORS

# The depositor with the lowest individual risk signal (last in the
# low-risk group), named here so its result can be looked up by name
# rather than by position: proving even the least-alarmed depositor's
# beliefs are moved by liquidity feedback is the point of the hypothesis
# this checks.
LEAST_ALARMED_DEPOSITOR_NAME = (
    f"depositor_{HIGH_RISK_DEPOSITOR_COUNT + LOW_RISK_DEPOSITOR_COUNT}"
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

STABLE_SCENARIO = Scenario(
    name="Stable Bank",
    description="High liquidity and depositor confidence",
    periods=2,

    initial_state={
        "period": 0,
        "liquidity": STARTING_LIQUIDITY,
        "withdrawals": 0,
    },

    agents=STABLE_DEPOSITORS,

    parameters={
        "initial_liquidity": RISK_NORMALIZATION_LIQUIDITY,
        "withdrawal_amount": WITHDRAWAL_AMOUNT,
    },

    reality_function=RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY,
    feedback_rule=FeedbackRule.BANK_LIQUIDITY_CONFIDENCE,
)


RUN_SCENARIO = STABLE_SCENARIO.variant(
    name="Bank Run",
    description=(
        "Initial risk signals trigger withdrawals, reducing liquidity "
        "and reinforcing perceived failure risk"
    ),
    periods=2,
    agents=RUN_DEPOSITORS,
)


INSOLVENT_LIQUIDITY_SCENARIO = Scenario(
    name="Withdrawal Demand Exceeds Liquidity",
    description="All depositors attempt to withdraw from a liquidity-constrained bank",
    periods=1,

    initial_state={
        "period": 0,
        "liquidity": INSOLVENT_STARTING_LIQUIDITY,
        "withdrawals": 0,
    },

    agents=AgentGroup(
        base=BASE_DEPOSITOR,
        count=INSOLVENT_DEPOSITOR_COUNT,
        name_prefix="depositor",
        model_of_reality={
            "risk_signal": INSOLVENT_RISK_SIGNAL,
            "failure_probability": INSOLVENT_RISK_SIGNAL,
        },
    ),

    parameters={
        "initial_liquidity": RISK_NORMALIZATION_LIQUIDITY,
        "withdrawal_amount": WITHDRAWAL_AMOUNT,
    },

    reality_function=RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY,
    feedback_rule=FeedbackRule.BANK_LIQUIDITY_CONFIDENCE,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBankRun(unittest.TestCase):
    TEST_NAME = "Test 09: Bank Run and Liquidity Feedback"

    def test_high_confidence_depositors_prefer_to_stay(self):
        result = run_scenario(
            STABLE_SCENARIO.variant(
                periods=1,
            )
        )

        self.assertEqual(
            result.final["withdrawals"],
            0,
        )

    def test_high_failure_risk_leads_to_withdrawal(self):
        scenario = STABLE_SCENARIO.variant(
            periods=1,
            agents=[
                BASE_DEPOSITOR.variant(
                    model_of_reality={
                        "risk_signal": HIGH_RISK_SIGNAL,
                        "failure_probability": HIGH_RISK_SIGNAL,
                    },
                )
            ],
        )

        result = run_scenario(
            scenario
        )

        self.assertEqual(
            result.final["withdrawals"],
            1,
        )

    def test_initial_withdrawals_reduce_bank_liquidity(self):
        result = run_scenario(
            RUN_SCENARIO.variant(
                periods=1,
            )
        )

        self.assertEqual(
            result.final["withdrawals"],
            HIGH_RISK_DEPOSITOR_COUNT,
        )

        self.assertEqual(
            result.final["liquidity"],
            STARTING_LIQUIDITY - HIGH_RISK_DEPOSITOR_COUNT * WITHDRAWAL_AMOUNT,
        )

    def test_lower_liquidity_increases_perceived_failure_risk(self):
        result = run_scenario(
            RUN_SCENARIO
        )

        least_alarmed_depositor = result.agent(LEAST_ALARMED_DEPOSITOR_NAME)

        self.assertGreaterEqual(
            least_alarmed_depositor.failure_probability,
            0.30,
        )

    def test_liquidity_feedback_accelerates_withdrawals(self):
        result = run_scenario(
            RUN_SCENARIO
        )

        first_period = result.history[1]
        second_period = result.history[2]

        self.assertEqual(
            first_period["withdrawals"],
            HIGH_RISK_DEPOSITOR_COUNT,
        )

        self.assertGreater(
            second_period["withdrawals"],
            first_period["withdrawals"],
        )

    def test_high_liquidity_and_confidence_remain_stable(self):
        result = run_scenario(
            STABLE_SCENARIO
        )

        self.assertEqual(
            result.history[1]["withdrawals"],
            0,
        )

        self.assertEqual(
            result.history[2]["withdrawals"],
            0,
        )

        self.assertEqual(
            result.final["liquidity"],
            STARTING_LIQUIDITY,
        )

    def test_requested_withdrawals_can_exceed_actual_liquidity(self):
        result = run_scenario(
            INSOLVENT_LIQUIDITY_SCENARIO
        )

        self.assertEqual(
            result.final["withdrawals"],
            INSOLVENT_DEPOSITOR_COUNT,
        )

        self.assertEqual(
            result.final["requested_liquidity"],
            INSOLVENT_DEPOSITOR_COUNT * WITHDRAWAL_AMOUNT,
        )

        self.assertEqual(
            result.final["realized_withdrawals"],
            INSOLVENT_STARTING_LIQUIDITY,
        )

        self.assertEqual(
            result.final["liquidity"],
            0,
        )

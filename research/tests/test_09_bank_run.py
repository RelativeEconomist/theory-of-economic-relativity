"""
TER Replication Test 09: Bank Run and Liquidity Feedback

Economic question
------------------
Can individually reasonable withdrawal decisions reduce actual bank
liquidity, and can that realized liquidity loss feed back into other
depositors' beliefs and trigger further withdrawal requests?

Scenario
--------
A bank starts with liquidity 1000. 3 depositors already perceive high
failure risk (failure_probability 0.50); 7 depositors start confident
(failure_probability 0.05):

    high-risk depositors (3): perceive 50% failure risk -> request WITHDRAW
    low-risk depositors  (7): perceive  5% failure risk -> choose STAY

The 3 requested withdrawals (300) are realized against actual liquidity,
leaving 700. Lower realized liquidity then raises every depositor's
perceived failure risk for the next period -- including the previously
confident ones. If that pushes a low-risk depositor's belief past its
own threshold, it now requests WITHDRAW too, even though nothing about
its personal risk_signal changed.

TER mapping
-----------
Core architecture, with feedback carried into the next period:

    (G, M, F̂, V, H, D) ──→ C ──→ R ──→ O
                                        │
                            feedback    │
                     (BANK_LIQUIDITY_CONFIDENCE)
                                        │
                                        ▼
                              next period's M

    M         failure_probability / risk_signal -- each depositor's
              belief about the bank, not a valuation
    V         deposit_value, deposit_benefit, withdrawal_cost -- the
              depositor's own valuation of staying or withdrawing
    D         DecisionProcess.MAXIMIZE
    C         STAY, or WITHDRAW (a withdrawal request -- see below)
    R         RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY
    O         withdrawal requests, realized liquidity withdrawal, and
              remaining liquidity
    feedback  FeedbackRule.BANK_LIQUIDITY_CONFIDENCE, updating the next
              period's M from this period's realized liquidity

WITHDRAW means the depositor submits a withdrawal request -- that
action is feasible, so it belongs in F and F̂ exactly like STAY. What
happens to the request is entirely R's job: WITHDRAWALS_REDUCE_LIQUIDITY
realizes only as much as the bank's actual liquidity allows. Requested
withdrawals can therefore exceed realized withdrawals without C ever
being rewritten -- the depositor's selected action stays WITHDRAW; only
how much of it reality honors changes.

Tested TER mechanics
--------------------
G     Objective              constant: preserve deposit value
M     Model of reality       failure_probability, risk_signal -- CHANGED
                              between periods by feedback
F, F̂  Feasible sets          STAY, WITHDRAW; F̂ equals F throughout
V     Valuation               deposit_value, deposit_benefit,
                              withdrawal_cost -- constant
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        STAY or WITHDRAW (a request, not a
                              guarantee of realization)
R     Reality function       RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY
O     Realized outcome       requests, realized withdrawals, remaining
                              liquidity
Feedback                     FeedbackRule.BANK_LIQUIDITY_CONFIDENCE,
                              from this period's realized liquidity to
                              the next period's M

Economic mechanism
------------------
Period 0: high-risk depositors' already-elevated M_0 makes WITHDRAW
their best response immediately; low-risk depositors' M_0 makes STAY
theirs. R realizes the 3 requested withdrawals against actual liquidity
(1000 -> 700). Feedback then raises every depositor's failure_probability
from that lower liquidity, including low-risk depositors whose own
risk_signal never changed. If the resulting belief crosses their own
threshold, period 1 sees additional WITHDRAW requests -- more withdrawal
pressure than period 0, produced entirely by the realized-liquidity ->
belief -> decision loop, not by any change in the depositor's valuation
or personal risk signal.

Assumptions
-----------
- The bank itself is not an AgentState; liquidity is scenario state, and
  withdrawal capacity is capped by RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY,
  not by any agent's actual_feasible_set.
- initial_liquidity is a scenario parameter used to normalize perceived
  risk; it is independent of the "liquidity" state value.
- Every depositor's initial failure_probability (M_0) is set equal to
  its own risk_signal directly, not left for feedback to fill in:
  feedback only ever updates the environment for a period that follows
  a realized outcome, and there is no realized outcome before period
  0's decision. This is exactly what BANK_LIQUIDITY_CONFIDENCE would
  compute anyway from a starting liquidity_risk of 0, stated up front
  instead of relying on that coincidence.

Hypothesis
----------
1. High-confidence depositors prefer to remain deposited.
2. High perceived failure risk produces withdrawal.
3. Initial withdrawals reduce actual bank liquidity.
4. Reduced liquidity raises perceived failure risk.
5. Feedback can produce additional withdrawals.
6. High liquidity and confidence can remain stable.
7. Requested withdrawals may exceed what reality permits.
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
    actual_feasible_set=[
        STAY,
        WITHDRAW,
    ],
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

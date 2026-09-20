"""
TER Replication Test 23: State Persistence Under a Liquidity Constraint
Canonical TER: theory/academic.md, Models 5.1, 5.3 and 5.5; Constraint 5.4 (State Persistence Constraint)

Economic question
-----------------
In this configured bank, does growing withdrawal demand eventually exceed
the liquidity the bank has available, so that continuation of the existing
state -- withdrawal requests honored in full from that liquidity -- is no
longer feasible?

Scenario
--------
A bank starts with liquidity 4000. 2 depositors already perceive high
failure risk (risk_signal 0.10) and request withdrawals from period 0;
40 depositors start confident (risk_signal 0.03):

    period 0: 2 request  -> 200 requested,  200 realized, liquidity 3800
    period 1: 2 request  -> 200 requested,  200 realized, liquidity 3600
    period 2: liquidity feedback has pushed the 40 confident depositors'
              perceived risk past their own threshold too -- all 42
              request -> 4200 requested, only 3600 available
              -> 3600 realized, liquidity driven to 0

TER instantiation
-----------------
Component                         Instantiation in this test                     Status
G   Objective                     preserve deposit value                         fixed
M   Model of Reality              failure_probability, risk_signal               varied (by feedback)
F̂   Perceived Feasible Set        STAY, WITHDRAW                                 fixed
V   Valuation                     deposit_value, deposit_benefit,                fixed
                                  withdrawal_cost (BANK_DEPOSITOR)
H   Time Horizon                  "immediate liquidity decision"                 fixed
D   Decision Process              DecisionProcess.MAXIMIZE                       fixed
C   Selected Action               STAY, or WITHDRAW (a withdrawal request)       observed
F_t aspects used by R             the bank's available liquidity (scenario       varied (by outcome)
                                  state["liquidity"]), which limits how much
                                  of the requests can be honored
R   Reality Function              RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY,  fixed
                                  applied to all 42 depositors' selected
                                  actions and the liquidity condition
O_t System Outcome                withdrawals, requested_liquidity,              observed
                                  realized_withdrawals, remaining liquidity
Feedback (Model 5.5)              FeedbackRule.BANK_LIQUIDITY_CONFIDENCE:        fixed
                                  updates each depositor's M from the
                                  remaining liquidity in the prior outcome
System state (Constraint 5.4)     the existing state in which withdrawal         observed
                                  requests are honored in full from the
                                  bank's available liquidity

Economic mechanism
------------------
The 2 early depositors' requests are honored in full while liquidity
covers them (periods 0 and 1), and each realized withdrawal lowers the
bank's liquidity. The feedback rule raises every depositor's perceived
failure risk as liquidity falls, until the 40 latent depositors' beliefs
cross their own threshold too. In period 2, requested withdrawals (4200)
exceed the liquidity available going into that period (3600), so the
existing state -- requests honored in full -- cannot be continued. In
this scenario R limits realized withdrawals to the available liquidity,
and remaining liquidity is 0. That limit is this scenario's R, not
something Constraint 5.4 computes: the constraint does not specify what
state follows, and this test does not claim the resulting state is an
equilibrium, an improvement, or a recovery.

Assumptions
-----------
- Depositor population, risk signals, deposit terms, and starting
  liquidity are test-specific economic assumptions, not TER primitives.
  They match test_09's in kind and differ only in number, chosen so one
  continuous run shows requests persisting, growing, and exceeding
  available liquidity.
- Given DEPOSIT_VALUE, DEPOSIT_BENEFIT, and WITHDRAWAL_COST, a depositor
  prefers withdrawing once its perceived failure_probability exceeds a
  fixed value implied by those constants (the same arithmetic as
  test_09's bank_depositor_value). EARLY_WITHDRAWAL_RISK_SIGNAL is above
  that value, so those depositors withdraw from period 0. LATENT_RISK_SIGNAL
  is below it, so those depositors withdraw only once the shared
  liquidity_risk term, driven by the bank's falling liquidity and
  identical for every depositor, pushes their perceived failure_probability
  past it.
- Scope: all 42 depositors are explicitly modeled, and their contemporaneous
  requests interact through the bank's shared liquidity, so Model 5.3
  applies. The fields reported each period are computed by R directly from
  the joint selected actions and the liquidity condition. This test defines
  no relationship between per-depositor outcomes and the system outcome.
- System state versus F_t: the state whose continuation is evaluated is the
  system of depositors and bank together (requests honored in full). F_t is
  not that state. The bank's available liquidity is the scenario condition
  that implements the relevant aspect of F_t, and R applies it to the
  requests. The remaining liquidity is reported in the outcome and carried
  into the next period's state. WITHDRAW is a request, so R decides how
  much of it is realized.
- withdrawal_amount (the size of each request) is an R parameter, and
  initial_liquidity is read only by the feedback rule to scale perceived
  risk into M; neither is a TER variable. No permission data for F_t is
  instantiated here, so what F_t permits for STAY or WITHDRAW is outside
  this test's scope.
- RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY and
  FeedbackRule.BANK_LIQUIDITY_CONFIDENCE are shared framework rules. Each is
  one admissible implementation of R and of the Model 5.5 feedback for this
  scenario, not a TER primitive or a universal equation. This test defines
  no local rule.
- This test does not claim all liquidity-constrained systems behave this
  way, that TER predicts when continuation becomes infeasible, or that any
  subsequent state follows from Constraint 5.4.

Hypothesis
----------
In this configured system:
1. Early withdrawal requests remain within available liquidity, so requests
   are honored in full.
2. Withdrawal requests persist, then grow, across periods.
3. In period 2, requested withdrawals exceed the liquidity available going
   into that period, so continuation of the existing state (requests
   honored in full) is no longer feasible.
4. In that period, realized withdrawals fall short of the request: the
   existing state does not persist unchanged.
5. Under this scenario's R, realized withdrawals equal the available
   liquidity.
6. Under this scenario's R, the remaining liquidity is 0.
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

DEPOSIT_VALUE = 100
DEPOSIT_BENEFIT = 6
WITHDRAWAL_COST = 1

STARTING_LIQUIDITY = 4000
WITHDRAWAL_AMOUNT = 100

EARLY_WITHDRAWAL_DEPOSITOR_COUNT = 2
EARLY_WITHDRAWAL_RISK_SIGNAL = 0.10

LATENT_DEPOSITOR_COUNT = 40
LATENT_RISK_SIGNAL = 0.03


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_DEPOSITOR = AgentSpec(
    name="depositor",
    objective="preserve deposit value",
    model_of_reality={
        "failure_probability": 0.0,
        "risk_signal": 0.0,
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

EARLY_WITHDRAWAL_DEPOSITORS = AgentGroup(
    base=BASE_DEPOSITOR,
    count=EARLY_WITHDRAWAL_DEPOSITOR_COUNT,
    name_prefix="early_withdrawal_depositor",
    model_of_reality={
        # M_0: this belief is set directly at construction, not left for
        # feedback to fill in -- there is no realized outcome before
        # period 0's decision for feedback to act on.
        "risk_signal": EARLY_WITHDRAWAL_RISK_SIGNAL,
        "failure_probability": EARLY_WITHDRAWAL_RISK_SIGNAL,
    },
)

LATENT_DEPOSITORS = AgentGroup(
    base=BASE_DEPOSITOR,
    count=LATENT_DEPOSITOR_COUNT,
    name_prefix="latent_depositor",
    start_index=EARLY_WITHDRAWAL_DEPOSITOR_COUNT + 1,
    model_of_reality={
        "risk_signal": LATENT_RISK_SIGNAL,
        "failure_probability": LATENT_RISK_SIGNAL,
    },
)

DEPOSITORS = EARLY_WITHDRAWAL_DEPOSITORS + LATENT_DEPOSITORS


# ---------------------------------------------------------------------------
# Scenario
# ---------------------------------------------------------------------------

LIQUIDITY_CONSTRAINT_SCENARIO = Scenario(
    name="Liquidity Constraint / State Persistence",
    description=(
        "A small group of depositors withdraws from period 0, gradually "
        "eroding liquidity. Once liquidity has fallen far enough, the "
        "remaining depositors' perceived risk crosses the same threshold "
        "and they withdraw too, pushing requested withdrawals past what "
        "the bank's remaining liquidity can supply."
    ),
    periods=3,

    initial_state={
        "period": 0,
        "liquidity": STARTING_LIQUIDITY,
        "withdrawals": 0,
    },

    agents=DEPOSITORS,

    parameters={
        "initial_liquidity": STARTING_LIQUIDITY,
        "withdrawal_amount": WITHDRAWAL_AMOUNT,
    },

    reality_function=RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY,
    feedback_rule=FeedbackRule.BANK_LIQUIDITY_CONFIDENCE,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestStatePersistenceLiquidityConstraint(unittest.TestCase):
    TEST_NAME = "Test 23: State Persistence Under a Liquidity Constraint"

    def test_early_requests_remain_within_available_liquidity(self):
        result = run_scenario(LIQUIDITY_CONSTRAINT_SCENARIO)

        period_0 = result.history[1]
        period_1 = result.history[2]

        self.assertLessEqual(
            period_0["requested_liquidity"],
            result.history[0]["liquidity"],
        )

        self.assertLessEqual(
            period_1["requested_liquidity"],
            period_0["liquidity"],
        )

    def test_withdrawal_pressure_persists_then_grows_across_periods(self):
        result = run_scenario(LIQUIDITY_CONSTRAINT_SCENARIO)

        period_0 = result.history[1]
        period_1 = result.history[2]
        period_2 = result.history[3]

        # Persists: the same early group withdraws again, unchanged.
        self.assertEqual(
            period_0["withdrawals"],
            EARLY_WITHDRAWAL_DEPOSITOR_COUNT,
        )

        self.assertEqual(
            period_1["withdrawals"],
            EARLY_WITHDRAWAL_DEPOSITOR_COUNT,
        )

        # Grows: the latent group's perceived risk crosses the same
        # threshold once liquidity has eroded enough, and they join.
        self.assertGreater(
            period_2["withdrawals"],
            period_1["withdrawals"],
        )

        self.assertEqual(
            period_2["withdrawals"],
            EARLY_WITHDRAWAL_DEPOSITOR_COUNT + LATENT_DEPOSITOR_COUNT,
        )

    def test_a_later_period_requests_exceed_available_liquidity(self):
        result = run_scenario(LIQUIDITY_CONSTRAINT_SCENARIO)

        period_1 = result.history[2]
        period_2 = result.history[3]

        # The liquidity actually available going into period 2 is
        # period 1's resulting liquidity -- an immutable, already-
        # computed outcome field, not a read of any mutable agent state.
        available_liquidity = period_1["liquidity"]

        self.assertGreater(
            period_2["requested_liquidity"],
            available_liquidity,
        )

    def test_reality_prevents_the_full_request_from_being_realized(self):
        result = run_scenario(LIQUIDITY_CONSTRAINT_SCENARIO)

        period_2 = result.history[3]

        self.assertLess(
            period_2["realized_withdrawals"],
            period_2["requested_liquidity"],
        )

    def test_realized_withdrawals_are_constrained_by_available_liquidity(self):
        result = run_scenario(LIQUIDITY_CONSTRAINT_SCENARIO)

        period_1 = result.history[2]
        period_2 = result.history[3]

        self.assertEqual(
            period_2["realized_withdrawals"],
            period_1["liquidity"],
        )

    def test_the_remaining_liquidity_is_zero_under_the_scenarios_reality_function(self):
        result = run_scenario(LIQUIDITY_CONSTRAINT_SCENARIO)

        period_2 = result.history[3]

        # max(0, liquidity - realized_withdrawals), as implemented by
        # withdrawals_reduce_liquidity, with nothing left to realize the
        # remainder of the request.
        self.assertEqual(
            period_2["liquidity"],
            0,
        )

        self.assertEqual(
            result.final["liquidity"],
            0,
        )

"""
TER Replication Test 23: Unsustainable Imbalance / Forced Adjustment

Economic question
------------------
Can TER represent a growing economic imbalance that persists until
reality's constraints make the existing trajectory unsustainable, and
force an adjustment?

This directly operationalizes TER Model 5.4's State Persistence
Constraint (continuation of the existing state no longer feasible =>
existing state cannot persist unchanged), using this test's own
shorthand -- I and J are not academic.md notation -- to narrate it:

    I_t -> unsustainable conditions -> J_{t+1} -> O_{t+1}

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
              (unsustainable) -> 3600 realized, liquidity driven to 0

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
              belief about the bank
    V         deposit_value, deposit_benefit, withdrawal_cost
    D         DecisionProcess.MAXIMIZE
    C         STAY, or WITHDRAW (a withdrawal request)
    R         RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY -- the same
              shared rule test_09 uses
    O         requested withdrawals, realized withdrawals, remaining
              liquidity
    feedback  FeedbackRule.BANK_LIQUIDITY_CONFIDENCE -- the same shared
              rule test_09 uses

Model 5.4 mapping, in terms of the fields R already reports each
period. I and J below are this test's own shorthand for narrating the
persistence constraint, not symbols academic.md defines:

    I_t                     requested_liquidity relative to available
                            liquidity -- not a TER primitive or a
                            separately computed quantity
    unsustainable condition requested_liquidity > available liquidity --
                            a plain numeric comparison this test makes,
                            not a generic "unsustainability threshold"
    J (adjustment)          the forced cap R already applies:
                            realized_withdrawals = min(requested,
                            liquidity); liquidity = max(0, liquidity -
                            realized). Represented entirely through the
                            existing reality function, not a new
                            AdjustmentRule.
    O (resulting state)     the capped realized_withdrawals and the
                            resulting liquidity

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
I_t (the gap between requested and available liquidity) starts small
and is fully honored by R for two periods. Feedback keeps raising every
depositor's perceived risk as liquidity falls, until the 40 previously
confident depositors' beliefs cross their own threshold too. At that
point requested_liquidity (4200) exceeds available liquidity (3600):
the unsustainable condition. J is produced by nothing more than R's own
existing cap -- realized_withdrawals is driven to the available amount
and liquidity to zero. This test does not claim that resulting state is
an equilibrium, an improvement, or a recovery: Model 5.4 explicitly
leaves the resulting state open, and academic.md's Scope and Limits
section does not assume adjustment always improves the system. Here the
resulting state is a depleted bank: demand permanently exceeds what
reality can supply.

Assumptions
-----------
- Depositor population, risk signals, deposit terms, and starting
  liquidity are test-specific economic assumptions, not TER primitives.
  All of them, and the resulting DecisionProcess.MAXIMIZE comparison, are
  identical in kind to test_09's -- only the specific numbers differ,
  chosen so a single continuous run demonstrates persistence, growth,
  and the unsustainable crossing without needing separate scenario
  variants the way test_09 does. test_09 studies belief contagion across
  scenario variants; this test asks a Model 5.4 shaped question along
  one continuous trajectory instead.
- Given DEPOSIT_VALUE, DEPOSIT_BENEFIT, and WITHDRAWAL_COST, a depositor
  prefers withdrawing once its perceived failure_probability exceeds a
  fixed value implied by those constants (identical arithmetic to
  test_09's bank_depositor_value; this test does not add a new
  threshold concept, it just uses the existing formula's own behavior).
  EARLY_WITHDRAWAL_RISK_SIGNAL is set above that value, so those
  depositors withdraw from period 0 regardless of liquidity conditions.
  LATENT_RISK_SIGNAL is set below it, so those depositors only withdraw
  once the shared liquidity_risk term (driven by the bank's own
  depleting liquidity, identical for every depositor) pushes their
  perceived failure_probability past it.
- I and J are not new TER primitives, variables, or generic rules; they
  are read directly off the existing reality function's own output
  fields (requested_liquidity, realized_withdrawals, liquidity), the
  same way capacity_constrained_realization (test_feasibility_contract.py)
  is one admissible, scenario-specific realization of R.
- Every value in the assertions below was verified by directly running
  this scenario and reading its real, computed period-by-period output;
  none is asserted by construction alone.
- This test does not claim all imbalances resolve this way, that TER
  can predict in general when an imbalance becomes unsustainable, or
  that forced adjustment restores equilibrium. It demonstrates one
  economically coherent, scenario-specific instance of Model 5.4, using
  only existing, unmodified TER Core execution paths.

Hypothesis
----------
1. Early withdrawal demand remains within available liquidity.
2. Withdrawal pressure persists, then grows, across periods.
3. A later period's requested withdrawals exceed the liquidity available
   at that point -- the unsustainable condition.
4. At that point, realized withdrawals fall short of what was requested.
5. Realized withdrawals are exactly capped by the liquidity actually
   available, not by any other mechanism.
6. The resulting state (liquidity driven to zero) reflects that forced
   adjustment.
7. All of this is produced entirely by existing, shared, unmodified TER
   Core rules and execution paths.
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

UNSUSTAINABLE_IMBALANCE_SCENARIO = Scenario(
    name="Unsustainable Imbalance / Forced Adjustment",
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

class TestUnsustainableImbalance(unittest.TestCase):
    TEST_NAME = "Test 23: Unsustainable Imbalance / Forced Adjustment"

    def test_imbalance_initially_remains_within_available_liquidity(self):
        result = run_scenario(UNSUSTAINABLE_IMBALANCE_SCENARIO)

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
        result = run_scenario(UNSUSTAINABLE_IMBALANCE_SCENARIO)

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

    def test_a_later_period_reaches_unsustainable_conditions(self):
        result = run_scenario(UNSUSTAINABLE_IMBALANCE_SCENARIO)

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
        result = run_scenario(UNSUSTAINABLE_IMBALANCE_SCENARIO)

        period_2 = result.history[3]

        self.assertLess(
            period_2["realized_withdrawals"],
            period_2["requested_liquidity"],
        )

    def test_realized_withdrawals_are_constrained_by_available_liquidity(self):
        result = run_scenario(UNSUSTAINABLE_IMBALANCE_SCENARIO)

        period_1 = result.history[2]
        period_2 = result.history[3]

        self.assertEqual(
            period_2["realized_withdrawals"],
            period_1["liquidity"],
        )

    def test_the_resulting_state_reflects_the_forced_adjustment(self):
        result = run_scenario(UNSUSTAINABLE_IMBALANCE_SCENARIO)

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

    def test_the_adjustment_is_produced_through_existing_ter_core_rules_only(self):
        self.assertEqual(
            UNSUSTAINABLE_IMBALANCE_SCENARIO.reality_function,
            RealityFunction.WITHDRAWALS_REDUCE_LIQUIDITY,
        )

        self.assertEqual(
            UNSUSTAINABLE_IMBALANCE_SCENARIO.feedback_rule,
            FeedbackRule.BANK_LIQUIDITY_CONFIDENCE,
        )

        for depositor in DEPOSITORS:
            self.assertEqual(
                depositor.valuation_rule,
                ValuationRule.BANK_DEPOSITOR,
            )

            self.assertEqual(
                depositor.decision_process,
                DecisionProcess.MAXIMIZE,
            )

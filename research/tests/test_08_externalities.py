"""
TER Replication Test 08: Externalities

Economic question
------------------
Can a privately preferred action create a negative external effect on
others, producing a lower total value under a specified social-value
measure, without changing TER's core decision architecture?

Scenario
--------
A firm decides whether to produce. Producing gives the firm private
value 4 but imposes an external effect of -7 on others; not producing
gives private value 0 and external effect 0:

    PRODUCE:        private value  4    external effect -7
    DO_NOT_PRODUCE: private value  0    external effect  0

Under private valuation the firm chooses PRODUCE. When the external
effect is internalized into its own valuation instead, the firm chooses
DO_NOT_PRODUCE. This is a concrete instance of the general externality
mechanism: whether a privately preferred action remains preferred once
its effect on others is folded into the deciding agent's own valuation.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C ──→ O

    G   maximize value from the production decision
    M   perceived_external_effects -- the firm's belief about each
        action's consequence on others
    F̂   PRODUCE / DO_NOT_PRODUCE
    V   private_values, always; INTERNALIZED valuation additionally
        folds in M, so V depends on M without the two becoming the
        same thing
    H   current production decision
    D   DecisionProcess.MAXIMIZE
    C   the firm's selected production action
    R   RealityFunction.SOCIAL_VALUE -- realizes O from private_values
        and the scenario's own actual external_effects, never from any
        firm's belief or valuation
    O   realized private value, actual external effect, and this
        scenario's specified social-value measure

F equals F̂ throughout: both actions are always actually feasible.

Tested TER mechanics
--------------------
G     Objective              constant: maximize value from the
                              production decision
M     Model of reality       perceived_external_effects -- the firm's
                              own belief, not read by the reality side
F, F̂  Feasible sets          PRODUCE / DO_NOT_PRODUCE; F̂ equals F
                              throughout
V     Valuation               private_values (constant); valuation_rule
                              CHANGED between scenarios (private_value
                              vs internalized_value)
D     Decision process       constant: DecisionProcess.MAXIMIZE
C     Selected action        observed result
R     Reality function       RealityFunction.SOCIAL_VALUE
O     Realized outcome       private value, actual external effect, and
                              social value, from R -- reads the actual
                              external_effects scenario parameter, never
                              any firm's model_of_reality

Both scenarios (private and internalized) use the same TER architecture
-- only valuation_rule differs.

Economic mechanism
------------------
Private valuation:

    PRODUCE:        4
    DO_NOT_PRODUCE: 0
    -> PRODUCE

Specified social-value measure (private value + actual external effect):

    PRODUCE:        4 + (-7) = -3
    DO_NOT_PRODUCE: 0 + 0    =  0

Internalized valuation (private value + perceived external effect):

    PRODUCE:        4 + (-7) = -3
    DO_NOT_PRODUCE: 0
    -> DO_NOT_PRODUCE

Internalization is represented here by a different valuation_rule
(internalized_value) reading the same perceived external effect, not by
a separate mechanism that causes internalization. TER does not itself
supply a mechanism that makes an agent internalize an externality --
that is a scenario-specific choice of V.

Assumptions
-----------
- private_values is the firm's own valuation of each action (V).
  perceived_external_effects is the firm's belief about each action's
  consequence on others (M). external_effects (a scenario parameter) is
  the actual consequence, used only to compute the realized social
  value -- it is not visible to any valuation rule.
- This test assumes the firm knows its own external effect exactly:
  perceived_external_effects is declared equal to external_effects (see
  BASE_FIRM). TER does not require this; it is a simplifying assumption
  of this test, not a framework constraint.
- valuation_rule determines what the firm's own decision process sees:
  private_value ignores perceived_external_effects; internalized_value
  adds it in, V depending on M without the two becoming the same thing.
- social_value_outcome always reads private_values and the scenario's
  actual external_effects directly, never the firm's own decision
  valuation (agent.value) or belief, so social value is not double
  counted when internalized_value has already folded a perceived effect
  into the firm's own valuation.
- Social value is a scenario-specific welfare measure defined by this
  test (private value + external effect), not a universal TER outcome
  equation.
- Social value is not precomputed into its own constant: assertions
  express it directly as PRIVATE_VALUE + EXTERNAL_EFFECT for the action in
  question, so the raw assumptions above stay the only place a number is
  defined; firm.social_value remains the framework's own computed result.
- The selected action produces the realized outcome O.
  AgentResult.outcome_for(action) is used only for counterfactual
  comparison of alternative feasible actions and must not be
  interpreted as another realized outcome. It is a lookup into outcomes
  social_value_outcome already computed for every perceived_feasible_set
  action during scenario execution -- it does not re-run any rule and
  does not change the firm's actual_feasible_set or perceived_feasible_set.

Hypothesis
----------
1. Production is privately profitable.
2. Production creates a negative external effect.
3. Private value can be positive while social value is negative.
4. The privately selected action's realized social value can be lower
   than the counterfactual social value of the feasible alternative,
   under this test's specified social-value measure.
5. Internalizing the external cost can change the selected action.
6. Both cases use the same TER architecture.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, RealityFunction, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

PRODUCE = "produce"
DO_NOT_PRODUCE = "do_not_produce"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

PRODUCE_PRIVATE_VALUE = 4
PRODUCE_EXTERNAL_EFFECT = -7

DO_NOT_PRODUCE_PRIVATE_VALUE = 0
DO_NOT_PRODUCE_EXTERNAL_EFFECT = 0


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_FIRM = AgentSpec(
    name="firm",
    objective="maximize value from the production decision",
    model_of_reality={
        # This test assumes the firm knows its own external effect
        # exactly: perceived_external_effects is set equal to the
        # scenario's actual external_effects parameter below. TER does
        # not require this -- a firm could misperceive its own
        # externality -- Test 08 just doesn't examine that case.
        "perceived_external_effects": {
            PRODUCE: PRODUCE_EXTERNAL_EFFECT,
            DO_NOT_PRODUCE: DO_NOT_PRODUCE_EXTERNAL_EFFECT,
        },
    },
    valuation={
        "private_values": {
            PRODUCE: PRODUCE_PRIVATE_VALUE,
            DO_NOT_PRODUCE: DO_NOT_PRODUCE_PRIVATE_VALUE,
        },
    },
    actual_feasible_set=[
        PRODUCE,
        DO_NOT_PRODUCE,
    ],
    perceived_feasible_set=[
        PRODUCE,
        DO_NOT_PRODUCE,
    ],
    valuation_rule=ValuationRule.PRIVATE,
    decision_process=DecisionProcess.MAXIMIZE,
    horizon="current production decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

PRIVATE_INCENTIVE_SCENARIO = Scenario(
    name="Private Incentive",
    description="A firm decides whether to produce based on private value alone.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_FIRM,
    ],
    # The actual external effect: what really happens to others,
    # regardless of what the firm believes. Read by social_value_outcome
    # to compute the realized social value, not by any valuation rule.
    parameters={
        "external_effects": {
            PRODUCE: PRODUCE_EXTERNAL_EFFECT,
            DO_NOT_PRODUCE: DO_NOT_PRODUCE_EXTERNAL_EFFECT,
        },
    },
    reality_function=RealityFunction.SOCIAL_VALUE,
)


INTERNALIZED_SCENARIO = PRIVATE_INCENTIVE_SCENARIO.variant(
    name="Internalized Externality",
    description="The firm's own valuation already incorporates the external cost.",
    agents=[
        BASE_FIRM.variant(
            valuation_rule=ValuationRule.INTERNALIZED,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExternalities(unittest.TestCase):
    TEST_NAME = "Test 08: Externalities"

    def test_private_incentive_leads_firm_to_produce(self):
        firm = run_scenario(PRIVATE_INCENTIVE_SCENARIO).agent(BASE_FIRM.name)

        self.assertEqual(
            firm.selected_action,
            PRODUCE,
        )

        self.assertEqual(
            firm.private_value,
            PRODUCE_PRIVATE_VALUE,
        )

    def test_production_creates_negative_external_effect(self):
        firm = run_scenario(PRIVATE_INCENTIVE_SCENARIO).agent(BASE_FIRM.name)

        self.assertEqual(
            firm.external_effect,
            PRODUCE_EXTERNAL_EFFECT,
        )

        self.assertLess(
            firm.external_effect,
            0,
        )

    def test_private_value_can_be_positive_while_social_value_is_negative(self):
        firm = run_scenario(PRIVATE_INCENTIVE_SCENARIO).agent(BASE_FIRM.name)

        self.assertEqual(
            firm.private_value,
            PRODUCE_PRIVATE_VALUE,
        )

        self.assertEqual(
            firm.social_value,
            PRODUCE_PRIVATE_VALUE + PRODUCE_EXTERNAL_EFFECT,
        )

        self.assertGreater(
            firm.private_value,
            0,
        )

        self.assertLess(
            firm.social_value,
            0,
        )

    def test_privately_selected_action_has_lower_realized_social_value_than_counterfactual_alternative(self):
        firm = run_scenario(PRIVATE_INCENTIVE_SCENARIO).agent(BASE_FIRM.name)

        self.assertEqual(
            firm.selected_action,
            PRODUCE,
        )

        # firm.social_value is the realized O for the action actually
        # selected (PRODUCE).
        self.assertEqual(
            firm.social_value,
            PRODUCE_PRIVATE_VALUE + PRODUCE_EXTERNAL_EFFECT,
        )

        # firm.outcome_for(DO_NOT_PRODUCE) is a counterfactual: what
        # social value would have resulted from the alternative feasible
        # action, not another realized outcome.
        self.assertEqual(
            firm.outcome_for(DO_NOT_PRODUCE).social_value,
            DO_NOT_PRODUCE_PRIVATE_VALUE + DO_NOT_PRODUCE_EXTERNAL_EFFECT,
        )

        self.assertLess(
            firm.social_value,
            firm.outcome_for(DO_NOT_PRODUCE).social_value,
        )

    def test_internalizing_external_cost_changes_selected_action(self):
        private_firm = run_scenario(PRIVATE_INCENTIVE_SCENARIO).agent(BASE_FIRM.name)
        internalized_firm = run_scenario(INTERNALIZED_SCENARIO).agent(BASE_FIRM.name)

        self.assertEqual(
            private_firm.selected_action,
            PRODUCE,
        )

        self.assertEqual(
            internalized_firm.selected_action,
            DO_NOT_PRODUCE,
        )

    def test_internalization_uses_same_ter_architecture(self):
        private_firm = run_scenario(PRIVATE_INCENTIVE_SCENARIO).agent(BASE_FIRM.name)
        internalized_firm = run_scenario(INTERNALIZED_SCENARIO).agent(BASE_FIRM.name)

        self.assertEqual(
            private_firm.objective,
            internalized_firm.objective,
        )

        self.assertEqual(
            private_firm.actual_feasible_set,
            internalized_firm.actual_feasible_set,
        )

        self.assertEqual(
            private_firm.perceived_feasible_set,
            internalized_firm.perceived_feasible_set,
        )

        self.assertEqual(
            private_firm.decision_process,
            internalized_firm.decision_process,
        )

        self.assertNotEqual(
            private_firm.selected_action,
            internalized_firm.selected_action,
        )

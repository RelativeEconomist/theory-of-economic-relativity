"""
TER Replication Test 08: Externalities
Canonical TER: theory/academic.md, Models 5.1 and 5.2

Economic question
-----------------
Can a privately preferred action create a negative external effect on
others, producing a lower value under a specified social-value measure,
and can internalizing that effect in the firm's own valuation change the
action it selects?

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

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 maximize value from the production decision   fixed
M   Model of Reality          perceived_external_effects: the firm's own     fixed
                              belief about each action's consequence on
                              others; not read by R
F̂   Perceived Feasible Set    PRODUCE, DO_NOT_PRODUCE                        fixed
V   Valuation                 private_values (always); under INTERNALIZED,   varied (valuation_rule:
                              also folds in the perceived external effect    PRIVATE vs. INTERNALIZED)
                              from M, so V depends on M without the two
                              becoming the same thing
H   Time Horizon              current production decision                    fixed
D   Decision Process          DecisionProcess.MAXIMIZE                       fixed
C   Selected Action           PRODUCE or DO_NOT_PRODUCE                      observed
F_t aspects used by R         the scenario's actual private_values and       fixed
                              external_effects for each action, and the
                              actions permitted for the firm --
                              scenario-specified conditions R reads (not a
                              complete representation of F_t)
R   Reality Function          RealityFunction.SOCIAL_VALUE: realizes O from  fixed
                              the firm's selected action and the scenario's
                              own parameters, never from the firm's belief
                              or declared valuation
O_{i,t} Realized Outcome      private value, actual external effect, and     observed
                              this test's specified social-value measure,
                              from R
Feedback (Model 5.5)          none                                           --

This is a single-agent specification, so Model 5.2 applies. The effect on
others is a scenario-specified component of the firm's realized outcome;
no interaction among multiple agents is modeled, and no system outcome
O_t is defined.

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
- BASE_FIRM's valuation["private_values"] is the firm's own valuation of
  each action (V), read by the private_value/internalized_value
  valuation rules to select C. The scenario's parameters["private_values"]
  is the actual private value each action really yields once selected (a
  fact used only to compute the realized social value, never by any
  valuation rule) -- declared equal to the firm's own V here, but reality
  (R) never reads V to find that out, only its own copy in parameters.
  perceived_external_effects is the firm's belief about each action's
  consequence on others (M). external_effects (a scenario parameter) is
  the actual consequence, used only to compute the realized social
  value -- it is not visible to any valuation rule.
- This test assumes the firm knows its own private value and external
  effect exactly: parameters["private_values"] matches
  valuation["private_values"], and perceived_external_effects is
  declared equal to external_effects (see BASE_FIRM and
  PRIVATE_INCENTIVE_SCENARIO). TER does not require either equality;
  these are simplifying assumptions of this test, not framework
  constraints.
- valuation_rule determines what the firm's own decision process sees:
  private_value ignores perceived_external_effects; internalized_value
  adds it in.
- social_value_outcome always reads parameters["private_values"] and
  parameters["external_effects"] directly, never the firm's own decision
  valuation (agent.value), declared valuation (agent.valuation), or
  belief, so social value is not double counted when internalized_value
  has already folded a perceived effect into the firm's own valuation.
- Social value is a scenario-specific welfare measure defined by this
  test (private value + external effect), not a universal TER outcome
  equation.
- Social value is not precomputed into its own constant: assertions
  express it directly as PRIVATE_VALUE + EXTERNAL_EFFECT for the action in
  question, so the raw assumptions above stay the only place a number is
  defined; firm.social_value remains the framework's own computed result.
- The selected action produces the realized outcome O_{i,t}.
  AgentResult.outcome_for(action) is used only for counterfactual
  comparison with the alternative action and must not be interpreted as
  another realized outcome. It is a lookup into outcomes
  social_value_outcome already computed for every action permitted for
  the firm during scenario execution; it does not re-run any rule.

Hypothesis
----------
In this configured scenario:
1. Production is privately profitable.
2. Production creates a negative external effect.
3. Private value can be positive while social value is negative.
4. The privately selected action's realized social value can be lower
   than the counterfactual social value of the alternative action,
   under this test's specified social-value measure.
5. Internalizing the external cost can change the selected action.
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
        # Reality-side index of the actions permitted for each agent
        # (an implementation detail read by social_value_outcome, not a
        # TER variable).
        "permitted_actions": {
            BASE_FIRM.name: [
                PRODUCE,
                DO_NOT_PRODUCE,
            ],
        },
    },
    agents=[
        BASE_FIRM,
    ],
    # The actual private value and external effect: what actually
    # results from producing, regardless of the firm's own valuation or
    # belief. Read by social_value_outcome to compute the realized
    # social value, not by any valuation rule. Declared equal to
    # BASE_FIRM's valuation["private_values"] here -- this test assumes
    # the firm's own valuation matches reality exactly, the same
    # simplifying assumption already made for perceived_external_effects
    # vs external_effects; TER does not require either equality.
    parameters={
        "private_values": {
            PRODUCE: PRODUCE_PRIVATE_VALUE,
            DO_NOT_PRODUCE: DO_NOT_PRODUCE_PRIVATE_VALUE,
        },
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
        # social value would have resulted from the alternative action,
        # not another realized outcome.
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

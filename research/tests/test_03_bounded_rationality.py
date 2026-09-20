"""
TER Replication Test 03: Bounded Rationality and Incomplete Search
Canonical TER: theory/academic.md, Model 5.1

Economic question
-----------------
Can a limited search process select a lower-valued action than exhaustive
search over the same perceived feasible set?

Scenario
--------
A coffee buyer perceives three coffees:

    nearby_coffee ── V=6
    office_coffee ── V=7
    best_coffee   ── V=10

The buyer knows all three coffees are available and values BEST_COFFEE
most highly, but it is farther away and appears later in the search
order. Under limited search, the buyer may stop before reaching it.

Scenarios (only D's configuration differs):

    MAXIMIZE (no limit)                          -> best_coffee
    LIMITED_SEARCH limit=2, default order        -> office_coffee
    LIMITED_SEARCH limit=3, default order        -> best_coffee
    LIMITED_SEARCH limit=2,
      search_order=[nearby, best, office]        -> best_coffee

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 choose preferred coffee                        fixed
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    nearby_coffee, office_coffee, best_coffee      fixed (identical, same
                              -- same order in every scenario                order, in every scenario)
V   Valuation                 ValuationRule.MAPPED: a hand-assigned value    fixed
                              for each coffee
H   Time Horizon              current purchase                               fixed
D   Decision Process          MAXIMIZE, or LIMITED_SEARCH with               varied
                              decision_parameters search_limit and
                              search_order
C   Selected Action           see Scenario                                   observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
MAXIMIZE considers every action in the perceived feasible set and selects
the highest-valued one.

LIMITED_SEARCH considers only the first search_limit actions of a search
sequence -- decision_parameters["search_order"] if given, otherwise F̂'s
own order -- and selects the highest-valued action among those
considered. It can therefore stop short of the highest-valued action.

Assumptions
-----------
- search_limit and search_order are test-specific decision_parameters
  entries, not TER primitives. They configure how
  DecisionProcess.LIMITED_SEARCH searches; they are not part of F̂.
- perceived_feasible_set is identical, in the same order, across every
  scenario in this test. Search order is represented by
  decision_parameters["search_order"], never by reordering F̂.
- Mistaken feasibility and action-to-outcome mechanics are not exercised;
  this test isolates the decision process.

Hypothesis
----------
In this configured scenario:
1. Exhaustive search selects the highest-valued action.
2. Limited search can select a lower-valued action.
3. Increasing search depth can change the selected action.
4. Search order can matter under incomplete search.
"""

import unittest

from research.ter import AgentSpec, DecisionProcess, Scenario, ValuationRule, run_scenario


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

NEARBY_COFFEE = "nearby_coffee"
OFFICE_COFFEE = "office_coffee"
BEST_COFFEE = "best_coffee"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

NEARBY_COFFEE_VALUE = 6
OFFICE_COFFEE_VALUE = 7
BEST_COFFEE_VALUE = 10

LIMITED_SEARCH_DEPTH = 2
BROADER_SEARCH_DEPTH = 3


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="coffee_buyer",
    objective="choose preferred coffee",
    model_of_reality={},
    perceived_feasible_set=[
        NEARBY_COFFEE,
        OFFICE_COFFEE,
        BEST_COFFEE,
    ],
    valuation={
        "values": {
            NEARBY_COFFEE: NEARBY_COFFEE_VALUE,
            OFFICE_COFFEE: OFFICE_COFFEE_VALUE,
            BEST_COFFEE: BEST_COFFEE_VALUE,
        },
    },
    valuation_rule=ValuationRule.MAPPED,
    decision_process=DecisionProcess.LIMITED_SEARCH,
    decision_parameters={
        "search_limit": LIMITED_SEARCH_DEPTH,
        "search_order": [
            NEARBY_COFFEE,
            OFFICE_COFFEE,
            BEST_COFFEE,
        ],
    },
    horizon="current purchase",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

BASE_SCENARIO = Scenario(
    name="Coffee Buyer",
    description="A single agent searches among three coffees under varying search depth and order.",
    periods=1,
    initial_state={
        "period": 0,
    },
    agents=[
        BASE_AGENT,
    ],
)


LIMITED_SCENARIO = BASE_SCENARIO

EXHAUSTIVE_SCENARIO = BASE_SCENARIO.variant(
    agents=[
        BASE_AGENT.variant(
            decision_process=DecisionProcess.MAXIMIZE,
            # MAXIMIZE does not use limited-search configuration.
            decision_parameters={},
        ),
    ],
)

BROADER_SEARCH_SCENARIO = BASE_SCENARIO.variant(
    agents=[
        BASE_AGENT.variant(
            decision_parameters={
                "search_limit": BROADER_SEARCH_DEPTH,
                "search_order": [
                    NEARBY_COFFEE,
                    OFFICE_COFFEE,
                    BEST_COFFEE,
                ],
            },
        ),
    ],
)

REORDERED_SCENARIO = BASE_SCENARIO.variant(
    agents=[
        BASE_AGENT.variant(
            decision_parameters={
                "search_limit": LIMITED_SEARCH_DEPTH,
                "search_order": [
                    NEARBY_COFFEE,
                    BEST_COFFEE,
                    OFFICE_COFFEE,
                ],
            },
        ),
    ],
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBoundedRationality(unittest.TestCase):
    TEST_NAME = "Test 03: Bounded Rationality and Incomplete Search"

    def test_exhaustive_search_selects_highest_valued_action(self):
        agent = run_scenario(EXHAUSTIVE_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            BEST_COFFEE,
        )

    def test_incomplete_search_can_select_nonoptimal_action(self):
        agent = run_scenario(LIMITED_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            agent.selected_action,
            OFFICE_COFFEE,
        )

        self.assertLess(
            agent.value_of(agent.selected_action),
            agent.value_of(BEST_COFFEE),
        )

    def test_increasing_search_changes_selected_action(self):
        limited_agent = run_scenario(LIMITED_SCENARIO).agent(BASE_AGENT.name)
        broader_agent = run_scenario(BROADER_SEARCH_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            limited_agent.selected_action,
            OFFICE_COFFEE,
        )

        self.assertEqual(
            broader_agent.selected_action,
            BEST_COFFEE,
        )

    def test_search_order_can_change_bounded_choice(self):
        original_agent = run_scenario(LIMITED_SCENARIO).agent(BASE_AGENT.name)
        reordered_agent = run_scenario(REORDERED_SCENARIO).agent(BASE_AGENT.name)

        self.assertEqual(
            original_agent.selected_action,
            OFFICE_COFFEE,
        )

        self.assertEqual(
            reordered_agent.selected_action,
            BEST_COFFEE,
        )

        # Scenario-premise check: F̂ itself never changed -- only D's
        # search_order configuration did.
        self.assertEqual(
            original_agent.perceived_feasible_set,
            reordered_agent.perceived_feasible_set,
        )

    def test_selected_action_belongs_to_perceived_feasible_set_under_each_search_process(self):
        bounded_agent = run_scenario(LIMITED_SCENARIO).agent(BASE_AGENT.name)
        exhaustive_agent = run_scenario(EXHAUSTIVE_SCENARIO).agent(BASE_AGENT.name)

        self.assertIn(
            bounded_agent.selected_action,
            bounded_agent.perceived_feasible_set,
        )

        self.assertIn(
            exhaustive_agent.selected_action,
            exhaustive_agent.perceived_feasible_set,
        )

        self.assertNotEqual(
            bounded_agent.selected_action,
            exhaustive_agent.selected_action,
        )

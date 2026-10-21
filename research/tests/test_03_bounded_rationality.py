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

    maximize_value (no limit)                    -> best_coffee
    limited_search limit=2, default order        -> office_coffee
    limited_search limit=3, default order        -> best_coffee
    limited_search limit=2,
      search_order=[nearby, best, office]        -> best_coffee

TER instantiation
-----------------
Component                     Instantiation in this test                     Status
G   Objective                 choose preferred coffee                        fixed
M   Model of Reality          specified but empty                            fixed
F̂   Perceived Feasible Set    nearby_coffee, office_coffee, best_coffee      fixed (identical, same
                              -- same order in every scenario                order, in every scenario)
V   Valuation                 mapped_value: a hand-assigned value    fixed
                              for each coffee
H   Time Horizon              current purchase                               fixed
D   Decision Process          maximize_value, or limited_search with         varied
                              decision_parameters search_limit and
                              search_order
C   Selected Action           see Scenario                                   observed
F_t, R, outcomes              F_t and outcome realization are outside this test's scope.

Economic mechanism
------------------
maximize_value considers every action in the perceived feasible set and
selects the highest-valued one.

limited_search considers only the first search_limit actions of a search
sequence -- decision_parameters["search_order"] if given, otherwise F̂'s
own order -- and selects the highest-valued action among those
considered. It can therefore stop short of the highest-valued action.

Assumptions
-----------
- search_limit and search_order are test-specific decision_parameters
  entries, not TER primitives. They configure how
  limited_search searches; they are not part of F̂.
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

from research.scenarios.bounded_rationality import (
    BASE_AGENT,
    BEST_COFFEE,
    BROADER_SEARCH_SCENARIO,
    EXHAUSTIVE_SCENARIO,
    LIMITED_SCENARIO,
    OFFICE_COFFEE,
    REORDERED_SCENARIO,
)
from research.ter import run_scenario


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
            original_agent.state.perceived_feasible_set,
            reordered_agent.state.perceived_feasible_set,
        )

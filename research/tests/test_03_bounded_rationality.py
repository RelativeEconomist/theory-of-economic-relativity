"""
TER Replication Test 03: Bounded Rationality and Incomplete Search

Economic question
------------------
Can TER represent a nonoptimal choice produced by limited search rather
than universal optimization?

Scenario
--------
A coffee buyer perceives three coffees:

    nearby_coffee ── V=6
    office_coffee ── V=7
    best_coffee   ── V=10

The buyer knows all three coffees are available and values BEST_COFFEE
most highly, but it is farther away and appears later in the search
order. Under limited search, the buyer may stop before reaching it.

TER mapping
-----------
Core architecture:

    (G, M, F̂, V, H, D) ──→ C

This test holds G, M, F̂, V, H constant across every scenario. Only D
changes -- and only through D's own configuration (decision_process,
decision_parameters). F̂ itself never changes:

    same G, M, F̂, V, H
            │
    ┌───────┼───────────────┬────────────────────┐
    ▼       ▼               ▼                    ▼
 MAXIMIZE  LIMITED_SEARCH  LIMITED_SEARCH        LIMITED_SEARCH
 (no limit) limit=2         limit=3               limit=2
            default order   default order         search_order=[nearby,best,office]
    │       │                |                      │
    ▼       ▼                ▼                      ▼
best_coffee office_coffee   best_coffee           best_coffee


Tested TER mechanics
--------------------
G   Objective                 constant
M   Model of reality          constant
F̂   Perceived feasible set    constant -- identical, same order, in
                               every scenario
V   Valuation                 constant
H   Time horizon              constant
D   Decision process          CHANGED -- decision_process and
                               decision_parameters vary; F̂ never does
C   Selected action           observed result

Economic mechanism
------------------
MAXIMIZE searches every perceived feasible action and selects the
highest-valued one.

LIMITED_SEARCH considers only the first search_limit actions of a
search sequence -- decision_parameters["search_order"] if given,
otherwise F̂'s own order -- and selects the highest-valued action among
those considered. It can therefore stop short of the actually best
action.

Assumptions
-----------
- search_limit and search_order are test-specific decision_parameters
  entries, not TER primitives. They configure how
  DecisionProcess.LIMITED_SEARCH searches; they are not part of F̂.
- perceived_feasible_set is identical, in the same order, across every
  scenario in this test. Search order is represented by
  decision_parameters["search_order"], never by reordering F̂.
- The actual feasible set F is identical to the perceived feasible set
  F̂, so this test isolates the decision process rather than mistaken
  feasibility or Action to Outcome mechanics.

Hypothesis
----------
1. Exhaustive search selects the highest valued action.
2. Limited search can select a lower valued action.
3. Increasing search depth can change the selected action.
4. Search order can matter under incomplete search.
5. All cases use the same TER architecture.
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
    actual_feasible_set=[
        NEARBY_COFFEE,
        OFFICE_COFFEE,
        BEST_COFFEE,
    ],
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

        # F̂ itself never changed -- only D's search_order configuration
        # did.
        self.assertEqual(
            original_agent.perceived_feasible_set,
            reordered_agent.perceived_feasible_set,
        )

    def test_same_architecture_supports_bounded_and_exhaustive_search(self):
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

"""
Bounded Rationality scenario (theory/academic.md, Model 5.1).

A coffee buyer perceives three coffees with hand-assigned values. Only the
decision process differs between scenarios: maximize_value searches every
perceived feasible coffee; limited_search considers only the first
search_limit coffees of its search order.
"""

from research.ter import AgentSpec, Scenario
from research.ter.rules import limited_search, mapped_value, maximize_value


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
    valuation_rule=mapped_value,
    decision_process=limited_search,
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
    initial_state={},
    agents=[
        BASE_AGENT,
    ],
)


LIMITED_SCENARIO = BASE_SCENARIO

EXHAUSTIVE_SCENARIO = BASE_SCENARIO.variant(
    agents=[
        BASE_AGENT.variant(
            decision_process=maximize_value,
            # maximize_value does not use limited-search configuration.
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

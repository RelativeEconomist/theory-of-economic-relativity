"""
Basic Agent Choice scenario (theory/academic.md, Model 5.1).

A coffee buyer chooses among three coffees with hand-assigned values.
"""

from research.ter import AgentSpec, Scenario
from research.ter.rules import mapped_value, maximize_value


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

COFFEE_A = "coffee_a"
COFFEE_B = "coffee_b"
COFFEE_C = "coffee_c"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

COFFEE_A_VALUE = 4
COFFEE_B_VALUE = 7
COFFEE_C_VALUE = 10


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="coffee_buyer",
    objective="choose coffee",
    model_of_reality={},
    perceived_feasible_set=[
        COFFEE_A,
        COFFEE_C,
        COFFEE_B,
    ],
    valuation={
        "values": {
            COFFEE_A: COFFEE_A_VALUE,
            COFFEE_B: COFFEE_B_VALUE,
            COFFEE_C: COFFEE_C_VALUE,
        },
    },
    valuation_rule=mapped_value,
    decision_process=maximize_value,
    horizon="current decision",
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIO = Scenario(
    name="Coffee Buyer",
    description="A single agent chooses among three coffees.",
    periods=1,
    initial_state={},
    agents=[
        BASE_AGENT,
    ],
)

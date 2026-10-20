"""
Feasible Set Learning scenario (theory/academic.md, Models 5.1, 5.2 and 5.5).

One agent decides at two decision points between two actions. The
scenario's permission data lists both as permitted throughout, but the
agent initially perceives only ORDINARY_ACTION. R records the action the
agent experienced; the agent observes that own outcome exactly, and its
update rule adds BETTER_ACTION to F̂ before the next decision. Nothing
changes the permission data.
"""

from research.ter import AgentSpec, RealityResult, Scenario
from research.ter.rules import mapped_value, maximize_value, observe_own_outcome


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

ORDINARY_ACTION = "ordinary_action"
BETTER_ACTION = "better_alternative_action"


# ---------------------------------------------------------------------------
# Economic assumptions
# ---------------------------------------------------------------------------

ORDINARY_ACTION_VALUE = 4
BETTER_ACTION_VALUE = 9


def record_experienced_action(actions, objective_state, parameters):
    """
    Scenario-specific reality rule. Implements R (Model 5.2,
    single-agent specification) as a specification of this scenario, not
    a TER primitive or universal outcome rule.

    Realizes O_{i,t} as simply the action the agent actually selected --
    this scenario's economics need nothing more elaborate than "the agent
    experienced whatever it selected."
    """
    return RealityResult(
        agents={
            name: {"experienced_action": action}
            for name, action in actions.items()
        },
    )


def learn_from_experience(agent, observation):
    """
    Scenario-specific update rule. Implements the agent-side half of
    Model 5.5 as a specification of this scenario, not a TER primitive or
    universal learning rule.

    Once the agent observes (observe_own_outcome) that it
    experienced ORDINARY_ACTION, BETTER_ACTION is added to its perceived
    feasible set. It reads only its own observation and its own F̂ --
    never the permission data, which it cannot reach.

    Required observation field:

        experienced_action   the agent's own O_{i,t}
    """
    if observation["experienced_action"] != ORDINARY_ACTION:
        return {}

    if BETTER_ACTION in agent.perceived_feasible_set:
        return {}

    return {
        "perceived_feasible_set": agent.perceived_feasible_set + [BETTER_ACTION],
    }


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

BASE_AGENT = AgentSpec(
    name="decision_maker",
    objective="obtain the highest payoff from its choice of action",
    model_of_reality={},
    valuation={
        "values": {
            ORDINARY_ACTION: ORDINARY_ACTION_VALUE,
            BETTER_ACTION: BETTER_ACTION_VALUE,
        },
    },
    perceived_feasible_set=[
        ORDINARY_ACTION,
    ],
    valuation_rule=mapped_value,
    decision_process=maximize_value,
    horizon="ongoing decision",
    update_rule=learn_from_experience,
)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

LEARNING_SCENARIO = Scenario(
    name="Feasible Set Discovery Through Experience",
    description=(
        "An agent initially perceives only one of two actions the "
        "objective feasible state of reality permits. Experience from the "
        "first decision expands what it perceives as feasible before the "
        "next decision."
    ),
    periods=2,
    initial_state={
        # Scenario permission data: both actions are permitted by the relevant
        # reality constraint from the start (an implementation representation,
        # not F_t itself).
        "permitted_actions": {
            BASE_AGENT.name: [
                ORDINARY_ACTION,
                BETTER_ACTION,
            ],
        },
    },
    agents=[
        BASE_AGENT,
    ],
    reality=record_experienced_action,
    observation=observe_own_outcome,
)

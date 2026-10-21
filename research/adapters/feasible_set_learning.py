"""
JSON-safe adapter for the Feasible Set Learning scenario.

Request:

    {"scenario": "feasible-set-learning"}

The scenario has no adjustable inputs; every run replays it as specified.

Response:

    {
        "scenario": "feasible-set-learning",
        "name": "Feasible Set Discovery Through Experience",
        "agent": "decision_maker",
        "permitted_actions": ["ordinary_action", "better_alternative_action"],
        "action_values": {"ordinary_action": 4, "better_alternative_action": 9},
        "periods": [
            {
                "decision_point": 0,
                "decision_state": {
                    "model_of_reality": {},
                    "perceived_feasible_set": ["ordinary_action"],
                },
                "objective_conditions": {
                    "permitted_actions": ["ordinary_action", "better_alternative_action"],
                },
                "selected_action": "ordinary_action",
                "realized_outcome": {"experienced_action": "ordinary_action"},
                "observation": {"experienced_action": "ordinary_action"},
                "updated_agent_state": {
                    "model_of_reality": {},
                    "perceived_feasible_set": ["ordinary_action", "better_alternative_action"],
                },
                "added_actions": ["better_alternative_action"],
            },
            ...
        ],
    }

Each period is read from its own trace step, never from final state.
decision_state is the agent's M and F̂ when it decided (C_{i,t}, the
selected_action); objective_conditions is the scenario's permission data
at that decision point, one relevant aspect of F_t, which D never sees.
realized_outcome is O_{i,t} from R; observation is what the agent
received about it; updated_agent_state is its M and F̂ after the update,
which the next decision starts from. added_actions lists the actions the
update added to F̂. permitted_actions is the agent's permission data in
the initial objective state. action_values is the agent's own V for each
action in its final F̂, which the update made the full permitted set.
"""

from research.scenarios.feasible_set_learning import BASE_AGENT, LEARNING_SCENARIO
from research.ter import run_scenario

SCENARIO_ID = "feasible-set-learning"

REQUEST_KEYS = frozenset({"scenario"})


def validate_request(request: dict) -> None:
    """Raise unless request names this scenario and nothing else."""
    if not isinstance(request, dict):
        raise TypeError("Request must be a dict.")

    if request.get("scenario") != SCENARIO_ID:
        raise ValueError(
            f"Unsupported scenario {request.get('scenario')!r}; "
            f"expected {SCENARIO_ID!r}."
        )

    unknown = sorted(set(request) - REQUEST_KEYS)

    if unknown:
        raise ValueError(f"Unknown request key(s): {unknown}")


def agent_side_state(record) -> dict:
    """The recorded M and F̂ of one agent at one point in the trace."""
    return {
        "model_of_reality": dict(record.model_of_reality),
        "perceived_feasible_set": list(record.perceived_feasible_set),
    }


def run(request: dict) -> dict:
    """
    Run the Feasible Set Learning scenario and return a JSON-safe summary
    of each decision point, in the order the trace recorded it: the
    agent's state when it decided, the permission data, the selected
    action, the realized outcome, the agent's observation of it, and the
    agent's state after its update.
    """
    validate_request(request)
    result = run_scenario(LEARNING_SCENARIO)
    trace = result.trace
    agent = BASE_AGENT.name
    agent_result = result.agent(agent)
    periods = []

    for t, step in enumerate(trace):
        before = trace.agents_before(t)[agent]
        after = step.agents[agent]

        periods.append(
            {
                "decision_point": step.step,
                "decision_state": agent_side_state(before),
                "objective_conditions": {
                    "permitted_actions": list(
                        trace.objective_state_before(t)["permitted_actions"][agent]
                    ),
                },
                "selected_action": step.actions[agent],
                "realized_outcome": dict(step.reality.agent(agent)),
                "observation": dict(step.observations[agent].data),
                "updated_agent_state": agent_side_state(after),
                "added_actions": [
                    action
                    for action in after.perceived_feasible_set
                    if action not in before.perceived_feasible_set
                ],
            }
        )

    return {
        "scenario": SCENARIO_ID,
        "name": LEARNING_SCENARIO.name,
        "agent": agent,
        "permitted_actions": list(trace.initial["permitted_actions"][agent]),
        "action_values": {
            action: agent_result.value_of(action)
            for action in agent_result.state.perceived_feasible_set
        },
        "periods": periods,
    }

# TER Research Framework

Practical guide to building, running, and extending TER specifications in code.

This file is the practical companion to [`../theory/academic.md`](../theory/academic.md) (canonical theory) and [`ter-methodology-notes.md`](ter-methodology-notes.md) (deeper modeling discipline and variable boundary guidance). It does not restate the theory — see those files for definitions, axioms, and modeling judgment calls. For contribution workflow (proposing changes, submission checklist, reporting a TER problem), see [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

In short: this file is *how to use the software* — the API, test structure, and running results. [`ter-methodology-notes.md`](ter-methodology-notes.md) is *how to specify TER correctly* — where a concept belongs among the variables and how to avoid known modeling mistakes.

## Start Here

1. Read the core architecture — [root README](../README.md) or [`theory/academic.md`](../theory/academic.md) §5 for the formal models.
2. Review the modeling guidance in [`ter-methodology-notes.md`](ter-methodology-notes.md) before writing a new specification.
3. Run the suite and read [`test_01_basic_agent_choice.py`](tests/test_01_basic_agent_choice.py) — the simplest scenario, and the clearest map from a plain economic question to the API below.
4. Modify an existing test.
5. Create a new test.

## Running Tests

Run the suite from the repo root:

    python3 run_tests.py

Run a single test file, as a module (not by file path, which fails with `ModuleNotFoundError` since this isn't an installed package):

    python3 -m unittest research.tests.test_24_cobweb_oscillation -v

[`test_08_externalities.py`](tests/test_08_externalities.py) shows the same API with per-agent economic outcomes.

## The Research API

The core research objects come from `research.ter`; shared rule functions
come directly from `research.ter.rules`:

```python
from research.ter import (
    AgentSpec,
    AgentGroup,
    Scenario,
    RealityResult,
    Schedule,
    run_scenario,
)
from research.ter.rules import mapped_value, maximize_value
```

You define agents and a scenario declaratively, run it, and read named results back. You should not need to open any file under `research/ter/` to do this — see "Framework Internals" at the end of this guide if you ever do.

The one deliberate exception is [`test_07_supply_and_demand.py`](tests/test_07_supply_and_demand.py), which imports `evaluate_market`/`find_market_clearing_states` directly from `research.ter.market`. Market clearing is found by scanning a price grid, not by running a `Scenario` over time, so it doesn't fit the `run_scenario`/`AgentResult` API — see the comment in that file and [`ter/market.py`](ter/market.py).

## The TER Components, in Plain Language

Every TER agent decision can be described with nine components. Full formal definitions live in [`theory/academic.md`](../theory/academic.md) §3; boundary distinctions between components (e.g. `M` vs. `F̂`, `G` vs. `V`) live in [`ter-methodology-notes.md`](ter-methodology-notes.md) (Variable Placement). Notation is given for reference; you don't need to know it to read or write a test.

- **Objective (G)** — what the agent is trying to achieve.
- **Model of reality (M)** — what the agent believes or knows, right or wrong.
- **Objective feasible state of reality (F_t)** — what reality permits, regardless of belief. It is not agent specific: it is one state that every action taken at time `t` encounters. It is never an input to `D`.
- **Perceived feasible set (F̂)** — what the agent believes is possible.
- **Valuation (V)** — how the agent scores a possible action.
- **Horizon (H)** — how far ahead the agent looks when it decides.
- **Decision process (D)** — how the agent picks among what it believes is feasible.
- **Selected action (C)** — the action the agent actually chose.
- **Outcome (O)** — what happened once the choice met reality: `O_{i,t}` in an agent-level specification, `O_t` where contemporaneous interactions among agents are explicitly modeled. `R` is the reality function that produces it.

A test's docstring should name only the components that matter for *that* test, in this plain-language-first style — not repeat this whole list every time. See `test_01`'s or `test_08`'s "TER instantiation" table for the pattern.

## The Building Blocks

- **`AgentSpec`** — one agent's G, M, F̂, V, H, D, declared as data: `objective`, `model_of_reality`, `perceived_feasible_set`, `valuation`, `valuation_rule`, `decision_process`, `decision_parameters`, `horizon` — plus `update_rule`, how the agent turns what it observes into changed beliefs or perceptions (Model 5.5).
- **`AgentGroup`** — a convenience for declaring several structurally identical agents at once: `AgentGroup(base=BASE_AGENT, count=3, name_prefix="seller", model_of_reality={...})` produces `seller_1`, `seller_2`, `seller_3` as ordinary `AgentSpec`s. It's sugar for a loop over `AgentSpec.variant()`, not a TER primitive — reach for it only when a test would otherwise repeat the same agent construction several times (see `test_04_asymmetric_information.py`, `test_09_bank_run.py`).
- **`Scenario`** — the agents, the initial objective state `F_0` (`initial_state`) and `parameters` (fixed scenario conditions), and (optionally) the `reality`, `transition`, and `observation` rules and the `schedule` that govern interaction and change over time.
- **Shared rule functions** — reusable D/V/R/transition/observation/update implementations in `research.ter.rules`, such as `maximize_value`, `satisfice`, `net_value`, and `social_value_reality`. Import and pass the function directly.
- **`run_scenario(scenario)`** — executes it and returns a `ScenarioResult`.
- **`AgentResult`** — what `result.agent(name)` gives you back: one agent's final state and outcome, addressed by name.

## How TER Maps to Python

The canonical architecture is defined in `theory/academic.md` §3 and §5; this section only names the current `research.ter` objects that implement or configure each part of it. For *why* a fact belongs in one TER variable rather than another, see [`ter-methodology-notes.md`](ter-methodology-notes.md) (Variable Placement) — this section doesn't repeat that reasoning.

### TER variable to Python mapping

| TER | Python | Notes |
| --- | --- | --- |
| `G` | `AgentSpec.objective` / `AgentState.objective` | the objective value itself |
| `M` | `AgentSpec.model_of_reality` / `AgentState.model_of_reality` | a dict of beliefs; changes only through the agent's own `update_rule`, applied to what it observes |
| `F_t` | no dedicated field: the objective state (`Scenario.initial_state` as `F_0`, advanced only by the `transition`) and `Scenario.parameters` may encode conditions and constraints relevant to what `F_t` permits | implementation fields, not TER primitives; no single field is identical to `F_t`. Not an `AgentSpec`/`AgentState` field; never read by a decision process |
| `F̂` | `AgentSpec.perceived_feasible_set` / `AgentState.perceived_feasible_set` | agent-side; what the decision process selects from. Not a copy of what the scenario permits |
| `V` | `AgentSpec.valuation` (data) + `AgentSpec.valuation_rule` (a callable) | `valuation` is declarative data (e.g. a value map); `valuation_rule` is the function that reads it and returns a score. Together they implement `V`. |
| `H` | `AgentSpec.horizon` / `AgentState.horizon` | carried as data; no shared rule currently reads it |
| `D` | `AgentSpec.decision_process` (a callable) + `AgentSpec.decision_parameters` (data) | the function implements `D`, which reads `F̂`, `G`, `M`, `V`, `H` and never `F_t`; `decision_parameters` configures it (e.g. `search_limit`, `search_order`) — not a new primitive |
| `C` | return value of `select_action()` (`research/ter/decision.py`); read back as `AgentResult.selected_action` | the action actually selected |
| `O` | the `RealityResult` the `reality` rule returns — `.system` is `O_t`, `.agents[name]` is `O_{i,t}` — recorded on `ScenarioResult.trace[t].reality`; read back per agent via `AgentResult` | `O_{i,t}` (Model 5.2) or `O_t` (Model 5.3), by the scope of the specification; the framework defines no aggregation of `O_{i,t}` into `O_t` |
| `R` | `Scenario.reality` (a callable) | implements the Model 5.2 relation for `O_{i,t}` in an agent-level specification and the Model 5.3 relation for `O_t` where interactions are explicitly modeled — the rule itself, not its output |

Prevailing conditions, shocks, laws, institutions, resources, physical and market conditions, and other objective constraints are aspects of `F_t` (`theory/academic.md` §3), not separate variables. In an implementation, a `reality` rule reads the scenario-relevant conditions from `objective_state` (conditions that change over time, e.g. `liquidity`, `price`) and `Scenario.parameters` (fixed conditions, e.g. `actual_payoff_matrix`). Some specifications also use permission data, `objective_state["permitted_actions"]`, which maps an agent name to the actions the scenario permits for that agent. It is an implementation representation of a scenario-relevant constraint, indexed by agent for convenience — not `F_t` itself, not an agent-specific `F_t`, and not agent state. It is read only on the reality side, through `permitted_actions_for()` and `is_actually_feasible()` (`research/ter/outcome.py`, a per-agent membership check), never by a decision process. The Model 5.5 pathway is split in three (none a TER primitive): a `transition` carries the realized outcome into `F_t+1`, an `observation` rule decides what each agent learns, and each agent's `update_rule` turns its own observation into changed agent-side components. A shock that changes what reality permits is a scenario-specific change to the objective state or `parameters` independent of realized outcomes.

### Agent specification vs. Scenario

> If it changes how an agent chooses, it usually belongs in the agent specification. If it describes objective scenario conditions or configures how reality responds, it usually belongs in the Scenario.

In practice: `objective`, `model_of_reality`, `valuation`, `valuation_rule`, `decision_process`, `decision_parameters`, `horizon`, `perceived_feasible_set`, and `update_rule` all live on `AgentSpec`. `initial_state` (which may include permission data such as `permitted_actions`), `parameters`, `reality`, `transition`, `observation`, and `schedule` all live on `Scenario`. `F_t` is not agent specific, so it is never declared on an `AgentSpec`. "Usually," because placement still depends on the role a concept plays — e.g. a price an agent merely observes is objective state (the agent learns it through an `observation` and its `update_rule` writes it into `model_of_reality`), while a price threshold that changes how the agent decides is agent data (`valuation`), and how an agent interprets what it observes (e.g. `reference_liquidity`, `feedback_strength`) is its own belief (`model_of_reality`).

### Configuration distinction

- `AgentSpec.decision_parameters` configures `D` — e.g. `search_limit`, `search_order`, `satisficing_threshold`, `tie_break_preference` (all read by the `decision_process` callable assigned to that same `AgentSpec`).
- `Scenario.parameters` configures the model-specific `reality`/`transition`/`observation` mechanics and encodes fixed scenario conditions a `reality` rule reads — e.g. `withdrawal_amount`, `price_sensitivity`, `actual_payoff_matrix`, `external_effects`. An `update_rule` never reads `parameters`; anything it needs beyond the observation belongs in the agent's own `model_of_reality`.

## Execution: One Decision Point at a Time

`run_scenario` records every decision point in an immutable `Trace`. At each decision point `t`:

1. **Schedule** (`Schedule.simultaneous()` — the default — or `Schedule.sequential("a", "b")`) names the actors. Inactive agents do not decide and contribute no action. Sequential schedules cycle over `periods`.
2. Every actor selects `C_i,t` from a frozen copy of its own state (Model 5.1), before anything at `t` is realized.
3. **`reality`** — `R(actions, objective_state, parameters) -> RealityResult`. `actions` maps actor name to action; `objective_state` is `F_t`, frozen. `RealityResult.system` is `O_t`; `RealityResult.agents[name]` is `O_i,t`, derived from the same joint realization where it depends on the interaction. R never changes `F`. Without a reality rule, nothing is realized.
4. **`transition`** — `(objective_state, reality, parameters) -> objective_state`: `F_t → F_t+1`. Without one, `F` carries forward unchanged.
5. **`observation`** — `(agents, actions, reality, objective_state, parameters) -> {name: data}`: what each agent learns (it sees `F_t+1`). An agent with no entry learns nothing.
6. **`AgentSpec.update_rule`** — `(agent, observation) -> {component: new value}`: the agent's own rule for turning its `Observation` into a new `M`, `F̂`, `G`, `V` data, `H`, or `decision_parameters`. It sees only its own `UpdateView` and that observation — never `F` or `O` — and cannot replace the agent's decision or valuation rule. This is the only way agent state changes.

`initial_state` is `F_0` and nothing else — no `"period"` or other bookkeeping. Initial beliefs belong in each agent's `model_of_reality` (`M_0`): an update only ever follows an observed outcome. Every rule must be deterministic; there is no randomness source yet.

### Result API

```python
result = run_scenario(SCENARIO)

result.trace[t].actors                  # derived from ordered action keys
result.trace[t].actions[name]           # C_i,t
result.trace[t].reality.system          # O_t
result.trace[t].reality.agent(name)     # O_i,t
result.trace[t].observations[name]      # what that agent received
result.trace[t].objective_state         # F_t+1
result.trace[t].agents[name]            # that agent's state after its update
result.trace.objective_state_before(t)  # F_t
result.trace.agents_before(t)           # every agent's state when t's actors decided
result.history                          # [F_0, F_1, ..., F_T]; result.initial is F_0, result.final is F_T

result.agent(name)                      # AgentResult from that agent's last decision point
result.agent(name).outcome_for(action)  # counterfactual re-run of R there, this agent's action replaced
result.counterfactual(t, {name: action})  # the full RealityResult for a joint counterfactual
```

A counterfactual re-runs R alone, with `F_t` and the other actors' recorded actions held fixed — it answers "what would reality have made of this action here", not "how would the run have unfolded". It first re-runs R on the recorded actions and refuses (`RuntimeError`) if that does not reproduce the recorded result. Everything in a `Trace` is frozen; mutating it raises `TypeError`.

See [`test_scheduled_engine_contract.py`](tests/test_scheduled_engine_contract.py) for the contracts themselves, and `test_08` (single agent), `test_25`, `test_05` and `test_13` (joint R and joint counterfactuals), `test_26` (sequential observation), `test_09`, `test_10`, `test_23` and `test_24` (multi-period transition and updates), and `test_22` (learning `F̂`) for them in use.

## Standard Test Structure

Organize a test file in this order, using section comments, and keep the docstring to these parts:

```python
"""
TER Replication Test NN: <Title>
Canonical TER: theory/academic.md, <the models the test actually exercises>

Economic question
------------------
1-3 sentences, phrased as a question.

Scenario
--------
What the agents/actions/setup actually are, in plain language.

TER instantiation
-----------------
A table of the components this test instantiates -- G, M, F̂, V, H, D, C,
plus R, O and feedback only where used -- each marked fixed, varied, or
observed. A Model 5.1-only test states that F_t and outcome realization
are outside its scope.

Economic mechanism
-------------------
The economic story that produces the hypothesis, in plain language.

Assumptions
-----------
Test-specific choices that are not part of TER itself.

Hypothesis
----------
Numbered claims, scoped to the configured specification.
"""

# Actions
# Economic assumptions
# Agents
# Scenarios
# Tests
```

Not every test needs every section at length — a one-agent test's "Scenarios" section can be a single `Scenario(...)`. Keep the order even when a section is short.

## Naming Constants vs. Inline Values

Every important economic assumption and its actual numeric value should be visible and easy to edit near the top of the file — that's the point of the `# Economic assumptions` section.

- Name a constant for any action token or economic fact that appears inside an `AgentSpec`/`Scenario` **and** is referenced again anywhere else (another variant, an assertion). See `PRODUCE_PRIVATE_VALUE`, `PRODUCE_EXTERNAL_EFFECT` in `test_08`.
- A value used exactly once, nowhere else, can stay inline.
- Express a *derived* fact as a computation from its raw constants at the point you need it (`PRODUCE_PRIVATE_VALUE + PRODUCE_EXTERNAL_EFFECT`), rather than pre-baking it into its own constant. That way every number a reader can see still traces back to a raw, editable assumption.
- Sign-boundary literals like `0` in `assertGreater(x, 0)` always stay inline — that `0` is a universal mathematical boundary, not a scenario fact, and naming it would obscure rather than clarify.
- Reference an agent by its own spec, never a retyped string: `result.agent(BASE_AGENT.name)`, not `result.agent("coffee_buyer")`. Don't introduce an alias constant for it either — `BASE_AGENT.name` already is one.

## Reading Results

```python
result = run_scenario(SCENARIO)
agent = result.agent(BASE_AGENT.name)

agent.selected_action          # C: what the agent actually chose
agent.outcome["social_value"]  # an O_i,t field reported by this scenario's reality rule
agent.state.model_of_reality["failure_probability"]
agent.value_of("coffee_c")     # V: the agent's own valuation of any action, selected or not
agent.outcome_for(DO_NOT_PRODUCE).outcome["social_value"]
```

`.agent(name)` looks up by name, never by position. Provenance is explicit: read realized fields from `.outcome` and final agent-side state from `.state`.

`.value_of()` reads the agent's own value function directly (the same one its decision used); it runs no reality rule. `.outcome_for()` re-runs only `R`, at the agent's last decision point, with that agent's action replaced and everything else held as recorded — a counterfactual, not another realized outcome.

## Shared Rules vs. Local Rules

Import shared rule functions directly from `research.ter.rules`. Rule fields accept callables only; symbolic strings such as `"maximize_value"` are not supported.

If no existing rule fits, define a **local** rule — one that's genuinely specific to the test's economics — in the same file, before its first use, with a short docstring saying what it computes and why it isn't shared. Pass the function directly to `AgentSpec` or `Scenario`; see `test_22_feasible_set_learning.py` and `test_26_sequential_entry.py`.

The trigger to move a local rule into `research.ter.rules` is simple: a **second** test wants the same mechanism. (`social_value_reality`, `private_value`, and `internalized_value` all started this way.)

## Modify an Existing Test

Changing a test is encouraged. You can experiment with:

- agent information or beliefs (`model_of_reality`)
- perceived feasible actions, or permission data (`objective_state["permitted_actions"]`) where the specification uses it
- objectives, decision rules, valuation rules
- interactions between agents (`reality`) and who acts when (`schedule`)
- feedback between outcomes and future decisions (`transition`, `observation`, `update_rule`)
- scenario-specific `parameters`

Keep assumptions introduced by the test separate from TER itself — see "Keep This Distinction Clear" in [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Create a New Test

Before defining agents, consult [`ter-methodology-notes.md`](ter-methodology-notes.md) — it's the place to go when you're creating a new TER specification, deciding where a concept belongs among the TER variables (e.g. `M` vs. `F̂`, `G` vs. `V`), resolving any other modeling boundary, introducing a new model-specific mechanism (like a local `R` or `D` rule), or checking your specification against known modeling mistakes.

1. Copy the existing test closest to your economic question — `test_01` for a single-agent decision, `test_08` for per-agent economic outcomes.
2. Rename it `test_NN_your_topic.py`.
3. Update the economic question and assumptions in the docstring.
4. Define agents (`AgentSpec`) and a scenario (`Scenario`), importing shared rule functions from `research.ter.rules` where they fit.
5. Run it with `run_scenario` and read results with `.agent(name)`.
6. Add assertions for your hypothesis; run the new test, then the full suite.

A useful test answers one clear economic question:

> Can feedback amplify an initial change under these conditions?

> Can bounded search produce a different action than exhaustive search?

## Framework Internals (Advanced)

Only needed if you're authoring a new **shared** reusable rule or working on the framework itself — not for writing or modifying a test.

- [`ter/scenario.py`](ter/scenario.py) — `AgentSpec`, `AgentGroup`, `Scenario`, `ScenarioResult`, `AgentResult`
- [`ter/runner.py`](ter/runner.py) — `run_scenario`
- [`ter/rules.py`](ter/rules.py) — shared rule functions and the six rule signatures every rule follows (decision, value, reality, transition, observation, update — see the comment block near the top of the file)
- [`ter/agent.py`](ter/agent.py) — `AgentState`, the executable form of an agent
- [`ter/decision.py`](ter/decision.py) — `select_action`, the shared decision step
- [`ter/outcome.py`](ter/outcome.py) — `is_actually_feasible` and `permitted_actions_for`, the per-agent lookups against the permission data in `objective_state["permitted_actions"]`, used on the reality side (Model 5.2)
- [`ter/reality.py`](ter/reality.py), [`ter/schedule.py`](ter/schedule.py), [`ter/observation.py`](ter/observation.py), [`ter/trace.py`](ter/trace.py) — `RealityResult`, `Schedule`, `Observation`/`UpdateView`, and `Trace`, the engine's contracts
- [`ter/immutable.py`](ter/immutable.py) — `freeze`/`thaw` and the frozen containers the engine records with
- [`ter/market.py`](ter/market.py) — `evaluate_market`, `find_market_clearing_states`; the price-grid comparative-statics path `test_07_supply_and_demand.py` uses instead of `run_scenario`

Use direct function references for shared and local rules (see "Shared Rules vs. Local Rules" above). Read named agent results via `.agent(name)` rather than positional indexing.


## AI Usage

AI is a powerful tool and accelerant, not a replacement for economic and engineering judgment. AI tools were used in the development of TER for research assistance, adversarial review, software implementation, testing, editing, and documentation.

TER is an open framework developed with extensive use of modern AI systems. AI is treated as a tool, not a source of authority.

The theory, assumptions, models, tests, and claims are evaluated against economic literature, internal consistency, reproducible tests, and external criticism rather than accepted because an AI system produced them.

The use of AI should make the work easier to inspect, test, and challenge, not exempt it from those standards.


## Next

Pick `test_01` or `test_08`, change one assumption, and run it. That is the fastest way to start working with TER. When you're ready to submit, see [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the submission checklist.

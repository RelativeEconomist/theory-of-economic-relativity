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

Everything a researcher normally needs comes from one import:

```python
from research.ter import (
    AgentSpec,
    AgentGroup,
    Scenario,
    DecisionProcess,
    ValuationRule,
    RealityFunction,
    FeedbackRule,
    run_scenario,
)
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

- **`AgentSpec`** — one agent's G, M, F̂, V, H, D, declared as data: `objective`, `model_of_reality`, `perceived_feasible_set`, `valuation`, `valuation_rule`, `decision_process`, `decision_parameters`, `horizon`.
- **`AgentGroup`** — a convenience for declaring several structurally identical agents at once: `AgentGroup(base=BASE_AGENT, count=3, name_prefix="seller", model_of_reality={...})` produces `seller_1`, `seller_2`, `seller_3` as ordinary `AgentSpec`s. It's sugar for a loop over `AgentSpec.variant()`, not a TER primitive — reach for it only when a test would otherwise repeat the same agent construction several times (see `test_04_asymmetric_information.py`, `test_09_bank_run.py`).
- **`Scenario`** — the agents, initial state and `parameters` (scenario conditions a `reality_function` may read), and (optionally) which `reality_function`/`feedback_rule` govern interaction and change over time.
- **`DecisionProcess` / `ValuationRule` / `RealityFunction` / `FeedbackRule`** — enums naming every shared, reusable D/V/R-and-feedback implementation, e.g. `DecisionProcess.MAXIMIZE`, `DecisionProcess.SATISFICE`, `ValuationRule.NET`, `RealityFunction.SOCIAL_VALUE`. Pick from these before writing anything new.
- **`run_scenario(scenario)`** — executes it and returns a `ScenarioResult`.
- **`AgentResult`** — what `result.agent(name)` gives you back: one agent's final state and outcome, addressed by name.

## How TER Maps to Python

The canonical architecture is defined in `theory/academic.md` §3 and §5; this section only names the current `research.ter` objects that implement or configure each part of it. For *why* a fact belongs in one TER variable rather than another, see [`ter-methodology-notes.md`](ter-methodology-notes.md) (Variable Placement) — this section doesn't repeat that reasoning.

### TER variable to Python mapping

| TER | Python | Notes |
| --- | --- | --- |
| `G` | `AgentSpec.objective` / `AgentState.objective` | the objective value itself |
| `M` | `AgentSpec.model_of_reality` / `AgentState.model_of_reality` | a dict of beliefs; a `FeedbackRule` may update it between periods |
| `F_t` | no dedicated field: scenario `state` (`Scenario.initial_state`, evolving) and `Scenario.parameters` may encode conditions and constraints relevant to what `F_t` permits | implementation fields, not TER primitives; no single field is identical to `F_t`. Not an `AgentSpec`/`AgentState` field; never read by a decision process |
| `F̂` | `AgentSpec.perceived_feasible_set` / `AgentState.perceived_feasible_set` | agent-side; what a `DecisionProcess` selects from. Not a copy of what the scenario permits |
| `V` | `AgentSpec.valuation` (data) + `AgentSpec.valuation_rule` (a `ValuationRule` member) | `valuation` is declarative data (e.g. a value map); `valuation_rule` names the function that reads it and returns a score. Neither the dict nor the enum member is a new TER primitive — together they implement `V`. |
| `H` | `AgentSpec.horizon` / `AgentState.horizon` | carried as data; no shared rule currently reads it |
| `D` | `AgentSpec.decision_process` (a `DecisionProcess` member) + `AgentSpec.decision_parameters` (data) | the named rule implements `D`, which reads `F̂`, `G`, `M`, `V`, `H` and never `F_t`; `decision_parameters` configures it (e.g. `search_limit`, `search_order`) — not a new primitive |
| `C` | return value of `select_action()` (`research/ter/decision.py`); read back as `AgentResult.selected_action` | the action actually selected |
| `O` | the dict a `RealityFunction` returns, merged into `ScenarioResult.history[t]`; read back per agent via `AgentResult` | `O_{i,t}` (Model 5.2) or `O_t` (Model 5.3), by the scope of the specification; the framework defines no aggregation of `O_{i,t}` into `O_t` |
| `R` | `Scenario.reality_function` (a `RealityFunction` member) | implements the Model 5.2 relation for `O_{i,t}` in an agent-level specification and the Model 5.3 relation for `O_t` where interactions are explicitly modeled — the rule itself, not its output |

Prevailing conditions, shocks, laws, institutions, resources, physical and market conditions, and other objective constraints are aspects of `F_t` (`theory/academic.md` §3), not separate variables. In an implementation, a `RealityFunction` reads the scenario-relevant conditions from `state` (conditions that change over time, e.g. `liquidity`, `price`) and `Scenario.parameters` (fixed conditions, e.g. `actual_payoff_matrix`). Some specifications also use permission data, `state["permitted_actions"]`, which maps an agent name to the actions the scenario permits for that agent. It is an implementation representation of a scenario-relevant constraint, indexed by agent for convenience — not `F_t` itself, not an agent-specific `F_t`, and not agent state. It is read only on the reality side, through `permitted_actions_for()` and `is_actually_feasible()` (`research/ter/outcome.py`, a per-agent membership check), never by a decision process. `FeedbackRule` is the Model 5.5 mechanism (not a TER primitive): it receives the realized outcome and updates `state`/`model_of_reality` between periods. A shock that changes what reality permits is a scenario-specific change to `state` or `parameters` independent of realized outcomes.

### Agent specification vs. Scenario

> If it changes how an agent chooses, it usually belongs in the agent specification. If it describes objective scenario conditions or configures how reality responds, it usually belongs in the Scenario.

In practice: `objective`, `model_of_reality`, `valuation`, `valuation_rule`, `decision_process`, `decision_parameters`, `horizon`, and `perceived_feasible_set` all live on `AgentSpec`. `initial_state` (which may include permission data such as `permitted_actions`), `parameters`, `reality_function`, and `feedback_rule` all live on `Scenario`. `F_t` is not agent specific, so it is never declared on an `AgentSpec`. "Usually," because placement still depends on the role a concept plays — e.g. a price an agent merely observes is scenario state (`model_of_reality["price"]` reads it, but the price itself moves in `Scenario.parameters`/`reality_function`), while a price threshold that changes how the agent decides is agent data (`valuation`).

### Configuration distinction

- `AgentSpec.decision_parameters` configures `D` — e.g. `search_limit`, `search_order`, `satisficing_threshold`, `tie_break_preference` (all read by the `decision_process` rule named on that same `AgentSpec`).
- `Scenario.parameters` configures the model-specific `reality_function`/`feedback_rule` mechanics and encodes fixed scenario conditions a `reality_function` reads — e.g. `withdrawal_amount`, `initial_liquidity`, `price_sensitivity`, `feedback_strength`, `actual_payoff_matrix`, `external_effects`.

### Result API

- `result.initial` — `history[0]`, the state before any period has run.
- `result.history[t]` — the full scenario state after period `t` (agents, `agent_snapshots`, `selected_action_by_agent`, and whatever that period's `reality_function`/`feedback_rule` returned).
- `result.final` — `history[-1]`, the last period's state.
- `result.agent(name)` — looks up one agent by name from `result.final` and returns an `AgentResult` — never index by position.

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
agent.social_value             # any field this scenario's reality_function reported for this agent
agent.failure_probability      # falls through to agent.model_of_reality["failure_probability"]
agent.value_of("coffee_c")     # V: the agent's own valuation of any action, selected or not
agent.outcome_for(DO_NOT_PRODUCE).social_value   # outcome for an action that wasn't selected
```

`.agent(name)` looks up by name, never by position — there should be no `result.final["..."][0]`-style indexing in a test. Attribute lookup checks, in order: outcome data a `reality_function` reported for this agent, then the agent's own fields (`objective`, `perceived_feasible_set`, `model_of_reality`, ...), then that agent's `model_of_reality` dict directly — so `agent.model_of_reality["x"]` and `agent.x` both work, and you should prefer the latter.

`.value_of()` and `.outcome_for()` never execute or re-run anything: `.value_of()` reads the agent's own value function directly (the same one its decision used), and `.outcome_for()` looks up data a `reality_function` already computed during the run.

## Shared Rules vs. Local Rules

Always reach for the public enums first — `DecisionProcess`, `ValuationRule`, `RealityFunction`, `FeedbackRule` — imported from `research.ter`. A bare string like `"maximize_value"` should not appear in a new test in place of a *shared* rule's enum member.

If no existing rule fits, a test may define and register its own **local** rule — one that's genuinely specific to that test's economics, not meant to be reused. Register it in the same file, right above its first use, with a short docstring saying what it computes and why it isn't shared, and reference it by its bare registered name (there is no enum member for a local rule — see `capacity_constrained_realization` in `test_feasibility_contract.py`).

The trigger to promote a local rule into the shared registry is simple: a **second** test wants the same mechanism. (`social_value_outcome`, `private_value`, and `internalized_value` all started this way.)

## Modify an Existing Test

Changing a test is encouraged. You can experiment with:

- agent information or beliefs (`model_of_reality`)
- perceived feasible actions, or permission data (`state["permitted_actions"]`) where the specification uses it
- objectives, decision rules, valuation rules
- interactions between agents (`reality_function`)
- feedback between outcomes and future decisions (`feedback_rule`)
- scenario-specific `parameters`

Keep assumptions introduced by the test separate from TER itself — see "Keep This Distinction Clear" in [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Create a New Test

Before defining agents, consult [`ter-methodology-notes.md`](ter-methodology-notes.md) — it's the place to go when you're creating a new TER specification, deciding where a concept belongs among the TER variables (e.g. `M` vs. `F̂`, `G` vs. `V`), resolving any other modeling boundary, introducing a new model-specific mechanism (like a local `R` or `D` rule), or checking your specification against known modeling mistakes.

1. Copy the existing test closest to your economic question — `test_01` for a single-agent decision, `test_08` for per-agent economic outcomes.
2. Rename it `test_NN_your_topic.py`.
3. Update the economic question and assumptions in the docstring.
4. Define agents (`AgentSpec`) and a scenario (`Scenario`), using `DecisionProcess`/`ValuationRule`/`RealityFunction`/`FeedbackRule` where they fit.
5. Run it with `run_scenario` and read results with `.agent(name)`.
6. Add assertions for your hypothesis; run the new test, then the full suite.

A useful test answers one clear economic question:

> Can feedback amplify an initial change under these conditions?

> Can bounded search produce a different action than exhaustive search?

## Framework Internals (Advanced)

Only needed if you're authoring a new **shared** reusable rule or working on the framework itself — not for writing or modifying a test.

- [`ter/scenario.py`](ter/scenario.py) — `AgentSpec`, `AgentGroup`, `Scenario`, `ScenarioResult`, `AgentResult`
- [`ter/runner.py`](ter/runner.py) — `run_scenario`
- [`ter/rules.py`](ter/rules.py) — the registry behind the public enums, and the four rule signatures every reusable rule follows (decision, value, reality, feedback — see the comment block near the top of the file)
- [`ter/agent.py`](ter/agent.py) — `AgentState`, the executable form of an agent
- [`ter/decision.py`](ter/decision.py) — `select_action`, the shared decision step
- [`ter/outcome.py`](ter/outcome.py) — `is_actually_feasible` and `permitted_actions_for`, the per-agent lookups against the permission data in `state["permitted_actions"]`, used on the reality side (Model 5.2)
- [`ter/system.py`](ter/system.py) — `run_system`, multi-agent interaction for one period
- [`ter/market.py`](ter/market.py) — `evaluate_market`, `find_market_clearing_states`; the price-grid comparative-statics path `test_07_supply_and_demand.py` uses instead of `run_scenario`

Every numbered replication test and every framework test follows this API: public enums for shared rules, bare strings reserved for local test-scoped rules (see "Shared Rules vs. Local Rules" above), results read via `.agent(name)` rather than positional indexing.


## AI Usage

AI is a powerful tool and accelerant, not a replacement for economic and engineering judgment. AI tools were used in the development of TER for research assistance, adversarial review, software implementation, testing, editing, and documentation.

TER is an open framework developed with extensive use of modern AI systems. AI is treated as a tool, not a source of authority.

The theory, assumptions, models, tests, and claims are evaluated against economic literature, internal consistency, reproducible tests, and external criticism rather than accepted because an AI system produced them.

The use of AI should make the work easier to inspect, test, and challenge, not exempt it from those standards.


## Next

Pick `test_01` or `test_08`, change one assumption, and run it. That is the fastest way to start working with TER. When you're ready to submit, see [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the submission checklist.

# TER Methodology

Practical guidance for researchers and programmers specifying, implementing, and testing TER models — not a second theory document.

- [`theory/academic.md`](../theory/academic.md) is canonical. If anything here ever conflicts with it, `academic.md` wins.
- This guide covers modeling judgment: where a fact belongs among TER's variables, and how to keep a specification testable rather than merely representational.
- [`research/README.md`](README.md) covers software and API usage — building and running a `Scenario`. Scenario state, parameters, and permission data such as `state["permitted_actions"]` can represent aspects of `F_t` in a specification; they are implementation fields, not TER primitives, and none is identical to `F_t`.
- [`research/tests/`](tests/) are the executable examples.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) covers contribution workflow, including how to report a problem with TER itself.

## Variable Placement

The most common way to misuse TER is placing a fact in the wrong component. This table is the fast reference for where something belongs.

> **`D` selects from `F̂`; `F_t` is not an input to `D` (Model 5.1).**

| Boundary | Practical rule | Example / common confusion |
|---|---|---|
| `G` vs `V` | `G` is the objective that provides the reference for valuation when valuation is used; `V` evaluates actions relative to it. Don't invent multiple objectives just because multiple attributes are valued. | A firm valuing both profit and reputation can represent both through one valuation relative to one `G` unless the specification genuinely requires distinct objectives. |
| `M` vs `F̂` | `M` is what the agent believes about the world; `F̂` is what it perceives as available to attempt. Beliefs about whether an action can be attempted belong in `F̂`; beliefs about what may happen if attempted belong in `M`. | Believing a rival will cut prices (`M`) vs. not perceiving undercutting as an available action (`F̂`). A low probability of success belongs in `M` and does not by itself remove the action from `F̂`. |
| `M` vs `V` | `M` holds beliefs about states, probabilities, or conditions; `V` holds how outcomes are valued. Never put preferences in `M` or beliefs in `V`. | Expected appreciation is `M`; a cost of capital netted into the action's value belongs in `V`, while a cutoff the selection rule uses to accept or stop belongs in `D`. |
| `M` vs reality and `R` | `M` can be incomplete or wrong; reality determines actual consequences regardless of belief. `R`, which determines `O` from `C` and `F_t`, must never be built from `M`, and `M` must never substitute for the conditions of reality when determining what `F_t` allows to be realized or when realizing `O`. | A depositor's belief about failure risk (`M`) never determines how much liquidity is actually available; a seller's believed demand never substitutes for the market-clearing rule. |
| `F_t` vs `F̂` | `F_t` is the objective state of reality relevant when the selected action is realized; `F̂` is the set of actions the agent perceives as available to attempt. `F_t` is not agent specific. | An agent may select an action that reality does not allow to be fully realized; failure, partial execution, or changed consequences are part of `O` (Model 5.2). |
| `F̂` vs `D` | An unperceived option is missing from `F̂`; a perceived-but-not-fully-evaluated option is a `D` mechanism. | A search limit belongs in `D`, not in a narrowed `F̂`. |
| `V` vs `D` | `V` scores actions; `D` is the selection process (maximize, satisfice, threshold). Don't fold a decision rule's cutoff into `V`, or valuation weighting into `D`. | A satisficing threshold lives in `D`; the value compared against it lives in `V`. |
| `H` vs `V` | `H` is which future consequences count; `V` is how they're weighted. A short horizon isn't the same as heavy discounting. When `H` and valuation parameters are observationally equivalent, use independent evidence or experimental design rather than infer both from the same observed choice. | A consequence inside `H` can still get near-zero weight through `V`. |
| `G` / `H` vs `D` | `G` and `H` condition valuation when valuation is used; they are not universal direct inputs to `D`. A nonvaluative decision process may select from `F̂` based on `M` without actively using `G` or `H`. | A reflexive withdrawal rule may use `M = threat present` without consulting valuation; do not add direct `G` or `H` inputs merely to make the rule look goal directed. |
| `C` vs `O` | `C` is what was selected; `O` is the realized outcome. Failure, partial execution, or changed consequences belong in `O`, not in a different `C`. | A partially executed action is still the action that was selected; the shortfall is part of `O`. |
| `F_t` conditions | Prevailing conditions, external shocks, laws, institutions, resources, physical conditions, market conditions, and other objective constraints are aspects of `F_t`, not separate variables. `F_t` is objective but not necessarily exogenous: where it changes because of agent actions and interactions, the change arrives through realized outcomes (Model 5.5); external shocks may alter it independently. | A price ceiling is an aspect of `F_t`. |
| External shock vs external effect | An external shock originates outside the modeled system boundary; an external effect arises from an action inside the modeled system and is experienced by others. What counts as an external shock depends on the model's own boundary. Where a shock changes objectively realized conditions or constraints, represent that change in `F_t`; external effects belong in realized outcomes. | A modeled competitor's action is endogenous; a war outside the modeled system may be a shock changing `F_t`; pollution imposed on another modeled agent is an external effect in `O`. |
| `R` vs `O` | `R` is the mechanism — a modeling choice; `O` is its realized output at the relevant decision point or time: `O_{i,t}` at the agent level (Model 5.2), `O_t` where interactions are explicitly modeled (Model 5.3). Don't describe `R` as just a restatement of one `O`. When an agent-level outcome depends on explicitly modeled interaction, derive it from the same joint `R`; TER does not define `O_t` as an aggregation of the `O_{i,t}`. | "Withdrawals capped at liquidity" is `R`; "60 units realized" is one `O`. |
| `F_t` (residual use) | The conditions and constraints in `F_t` must be defined explicitly, not used to catch unexplained outcome variation. | "Market conditions" as a vague catch-all is not a valid specification of `F_t`. |

## Variable Definitions

| Variable | Definition | Put it here when… | Do not put it here when… |
|---|---|---|---|
| **`G`** Objective | The objective that provides the reference for valuation when valuation is used | It defines the result, state, or condition relative to which actions are evaluated, such as profit, survival, wellbeing, stability, growth, or security | It is merely a belief, valuation, action, decision rule, or a universal direct input to `D` |
| **`M`** Model of reality | The agent's information, beliefs, assumptions, expectations, and interpretations about reality | It describes what the agent believes to be true, including beliefs about other agents or about its own future state, valuations, or decision tendencies | It is an actual constraint, actual condition, valuation itself, or the decision algorithm |
| **`F_t`** Objective feasible state of reality | The objectively realized conditions and constraints relevant when selected action(s) at decision point `t` are realized; not agent specific | It is a condition or constraint of objective reality relevant to realization: resources, capabilities, prevailing conditions, the effects of external shocks, laws, institutions, technology, physical, market, and environmental conditions | The agent merely believes or expects it |
| **`F̂`** Perceived feasible set | The actions the agent perceives as available to attempt | The agent perceives the action as available to attempt, whether or not reality ultimately allows it to be fully realized | The action is merely known about but excluded by search, filtering, attention, or selection inside `D`, or is considered unlikely to succeed but still available to attempt |
| **`V`** Valuation | The value assigned to actions relative to `G` | It determines how desirable or costly an action is relative to the agent's objective | It is the objective itself, a belief about reality, or the process used to select |
| **`H`** Time horizon | The future consequences considered relevant when valuation is forward looking | It determines which future consequences enter valuation when valuation is used | It merely determines how strongly an already-considered consequence is valued, or is being added as a universal direct input to `D` |
| **`D`** Decision process | The process through which the agent selects among actions in `F̂`; it may condition directly on `M` and may use `V` when applicable | It represents optimization, satisficing, heuristics, habits, reflexes, limited search, strategic reasoning, stochastic choice, or other selection procedures | It contains what `F_t` allows to be realized, realized consequences, or hidden preferences that properly belong in `V` |
| **`C`** Selected action | The action produced by the decision process at a decision point | It is the action the agent selects, including where appropriate a commitment, contract, policy, or contingent strategy | It is the realized result (that belongs in `O`) or a later action merely prescribed by an earlier commitment |
| **`R`** Reality function | The mechanism determining realized consequences from selected actions and the objective feasible state of reality | It maps `C` (or the interacting actions `C_1,…,C_n`) and `F_t` into realized outcomes | It treats `M`, `F̂`, or `V` as objective reality, or acts as an unconstrained residual explanation |
| **`O`** Realized outcome | The result produced when a selected action (`O_{i,t}`, Model 5.2) or explicitly modeled interacting actions (`O_t`, Model 5.3) encounter `F_t` | It records what actually happens, including success, failure, partial execution, and external effects | It is merely intended, expected, believed, or selected |

> When external search, attention, or information acquisition is itself an economically chosen activity, represent that activity as an action in `F̂`, place its costs and consequences in `R`/`O`, and reflect acquired information in subsequent `M`. Internal consideration or search within a decision procedure remains part of `D`.

### Common specification objects that are not TER primitives

| Object | How to use it |
|---|---|
| **Model state / stocks** | Wealth, inventory, capital, location, technology, balance sheets, physical stocks, and similar objects may be declared as model-specific state. They may be aspects of `F_t` when objectively realized and relevant to realization, be represented imperfectly in `M`, and evolve through model-specific laws of motion. |
| **System state** | The economically relevant properties of the modeled system at a given time may be collected as a specification-level system state. This is not a TER primitive and is not interchangeable with `F_t`; only the objectively realized conditions and constraints relevant to realization belong in `F_t`. |
| **Feedback / update rules** | Dynamic specifications should declare the mechanisms by which realized outcomes (`O_{i,t}` or `O_t`) may change `G, M, F̂, V, H, D` and `F` at `t+1`; external shocks may change `F` independently. Outcomes may affect `M` only through information available to the agent; do not update beliefs from an unobserved system outcome as if it were directly known. Other components may change through explicitly modeled mechanisms that do not require a belief update: for example, resource depletion may change `F`, while habituation or learned routines may change `V` or `D` if the specification defines that mechanism. These are specification-specific update mechanisms, not TER primitives and not part of within-period `D`. |

> **Every economically relevant fact should have one primary TER location. If the same fact appears in multiple components, the specification must explain why that duplication is necessary rather than silently double counting it.**

## Specification Rules

Practices that keep a TER specification testable instead of merely descriptive.

- **Representation is not validation.** Being able to represent an observed outcome in TER is not evidence that a specification is correct — constrain assumptions with evidence you can check independently.
- **Don't infer components from `C` alone, and don't fit after the fact.** Observed `C` does not uniquely identify `G`, `M`, `F̂`, `V`, `H`, or `D`. Constrain those components, and `F_t`, with independent evidence, and treat rival explanations as competing specifications rather than post hoc fits.
- **Avoid double counting.** The same mechanism shouldn't be encoded across multiple components unless each has a genuinely distinct causal role.
- **Preserve established economic mechanisms.** Map utility functions, beliefs, heuristics, and solution concepts into TER; don't rewrite their substance to fit.
- **`D` may be deterministic or stochastic, but must be substantive.** Its flexibility isn't an explanation unless it's specified precisely enough to generate testable implications.
- **Specify `R` substantively, and never use `R` or `F_t` as a residual.** Both must be defined enough to generate testable implications, not absorb whatever's left unexplained.
- **Define the agent/system boundary explicitly.** A coordinated group may be one agent or many depending on the question — but don't double-count a collective action as also an independent constituent action, and don't assume an institution's objective is automatically each member's `G`.
- **Label what is observed, inferred, and assumed.** A specification should state which TER components are directly observed, which are inferred from evidence, and which are imposed as assumptions. Do not present an inferred or assumed component as if it were directly measured.
- **Compare against alternatives.** A specification's implications should be checked against competing specifications, established non-TER models, and null explanations — not judged solely by whether it can be made to fit one observation.
- **Distinguish framework failure from specification failure.** Most failed predictions challenge one specification, not TER itself — a framework-level challenge means a determinant can't be represented without distorting TER's definitions, two components collapse into one, or an axiom contradicts itself.
- **Replication tests must preserve variable meaning.** Don't redefine what a variable means just to reproduce a target result.
- **Distinguish belief error, decision error, and realization.** If the agent's representation of reality is wrong, the error is in `M`. If `D` selects an action poorly given the specified `M` and `V`, that is a decision-formation error. If the selected action produces a different result than expected because of realized conditions or the reality mechanism, that is realization through `F_t` and `R`. Keep the three apart.
- **Components can be functionally related without collapsing together.** Two components influencing each other in a given model doesn't mean they're the same variable — their conceptual separation doesn't require statistical or causal independence.
- **Match time resolution to the mechanism.** `t` indexes the relevant decision point or time in the specification and may represent a period, stage, round, event, or other decision point. `F_t` is the objective state relevant when the action selected at `t` is realized; the agent need not know that realized state when selecting.
- **Separate uncertainty from realization.** Expectations, probabilities, and beliefs before uncertainty resolves belong in `M`. If uncertainty resolves after selection but before realization, the realized condition belongs in the relevant `F_t`; `R` then maps the selected action and that realized state to the outcome. TER does not require the underlying evolution of reality to be fundamentally deterministic or stochastic. For reproducible implementations and tests, resolve random draws into `F_t` or an explicitly declared model-specific realized state before `R` runs, keep `R` deterministic conditional on its explicit inputs, and declare the scenario seed; a stochastic `D` must draw from that declared seed on the agent side, and randomness used by `D` must never be routed through `F_t`. This is an implementation convention, not a claim that reality itself is fundamentally deterministic.
- **External effects belong in realized consequences.** When the mechanism produces effects on other agents, represent them in `O`; they do not require a separate TER primitive. Specifications making welfare claims should distinguish price-mediated pecuniary effects from technological or other non-price external effects when that distinction matters to the economic conclusion.
- **Treat commitments as selected objects, not future actions already taken.** A commitment, contract, policy, or contingent strategy may be `C` at one decision point. Later realized actions remain separate `C` values at later decision points. Enforceable commitments may alter later objective conditions in `F`; nonbinding, self-enforcing, or perceived commitments may instead shape `M`, `F̂`, `V`, or `D`, depending on the specification.
- **Specify interaction timing explicitly.** Multi-agent specifications may be contemporaneous, sequential, staged, asynchronous, or repeated. At each indexed decision point, apply `R` to the action or actions relevant to the outcome being realized; a specification need not assign a new `C` to an agent that does not act at that point.
- **State the equilibrium concept and how it enters the specification.** TER does not impose one universal equilibrium concept. Specify the relevant consistency conditions, including the applicable feasibility and belief requirements, and state whether equilibrium is embedded in `R` as a clearing mechanism, emerges from repeated agent decisions, or is verified afterward as a consistency check. Equilibrium does not by itself imply static behavior, dynamic stability, optimality, permanence, or desirability.

## Common Mistakes

Anti-patterns worth a second look before you trust a result — see Variable Placement and Specification Rules above for the reasoning behind each.

- Inferring `G`, `M`, `F̂`, `V`, `H`, or `D` directly from an observed action `C`.
- Fitting `D` (or another component) to a result after seeing it, instead of specifying it independently.
- Double-counting the same mechanism across more than one component.
- Putting a search or attention limit into `F̂` instead of `D`.
- Confusing an agent's beliefs (`M`) with what `F_t` allows to be realized.
- Removing an action from `F̂` merely because the agent believes success is unlikely.
- Passing `G` or `H` directly into `D` by default instead of using them through valuation when valuation is part of the mechanism.
- Treating a failed or partially executed action as a different selected action instead of part of `O`.
- Treating an expected or believed outcome as if it were the realized `O`.
- Using `F_t` or `R` as an unexplained residual for whatever else can't be accounted for.
- Silently promoting a test-specific assumption into a general TER claim.
- Rewriting an established economic mechanism's substance just to make it fit TER.

## Practical Tips

1. Ask whether the fact is an agent-side component (`G`, `M`, `F̂`, `V`, `H`, `D`) or part of objective realization (`F_t`, `R`).
2. Ask whether it changes what the agent believes (`M`), perceives as available to attempt (`F̂`), values (`V`), or how it selects (`D`).
3. Avoid encoding the same mechanism twice.
4. Prefer the simplest specification that preserves the economics being studied.
5. If two placements remain plausible, treat them as competing specifications and test which better fits the evidence.

A TER specification should make its assumptions visible enough that another researcher can reproduce, challenge, or replace them.

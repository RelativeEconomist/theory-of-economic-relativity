# TER Methodology

Practical guidance for researchers and programmers specifying, implementing, and testing TER models — not a second theory document.

- [`theory/academic.md`](../theory/academic.md) is canonical. If anything here ever conflicts with it, `academic.md` wins.
- This guide covers modeling judgment: where a fact belongs among TER's variables, and how to keep a specification testable rather than merely representational.
- [`research/README.md`](README.md) covers software and API usage — building and running a `Scenario`.
- [`research/tests/`](tests/) are the executable examples.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) covers contribution workflow, including how to report a problem with TER itself.

## Variable Placement

The most common way to misuse TER is placing a fact in the wrong component. This table is the fast reference for where something belongs.

> **`D` selects from `F̂`, never directly from `F`.**

| Boundary | Practical rule | Example / common confusion |
|---|---|---|
| `G` vs `V` | `G` is the objective; `V` scores actions against it. Don't invent multiple objectives just because multiple attributes are valued. | A firm valuing both profit and reputation still has one `G` unless the spec needs two distinct objectives. |
| `M` vs `F̂` | `M` is what the agent believes about the world; `F̂` is what it perceives as available to do. An unknown option is outside `F̂`; a known-but-ignored option is a `D` matter. | Believing a rival will cut prices (`M`) vs. not perceiving undercutting as an option at all (`F̂`). |
| `M` vs `V` | `M` holds beliefs about states, probabilities, or conditions; `V` holds how outcomes are valued. Never put preferences in `M` or beliefs in `V`. | Expected appreciation is `M`; the required-return threshold compared against it is `V`. |
| `M` vs reality | `M` can be incomplete or wrong; reality determines actual consequences regardless of belief. Never substitute `M` for actual conditions when computing `F` or `O`. | A depositor's belief about failure risk (`M`) never determines how much liquidity is actually available. |
| `F` vs `F̂` | `F` is what reality permits; `F̂` is what the agent perceives as permitted. | An agent may select an action that turns out infeasible; `C` stays selected, while `O` reflects what reality permits. |
| `F̂` vs `D` | An unperceived option is missing from `F̂`; a perceived-but-not-fully-evaluated option is a `D` mechanism. | A search limit belongs in `D`, not in a narrowed `F̂`. |
| `V` vs `D` | `V` scores actions; `D` is the selection process (maximize, satisfice, threshold). Don't fold a decision rule's cutoff into `V`, or valuation weighting into `D`. | A satisficing threshold lives in `D`; the value compared against it lives in `V`. |
| `H` vs `V` | `H` is which future consequences count; `V` is how they're weighted. A short horizon isn't the same as heavy discounting. | A consequence inside `H` can still get near-zero weight through `V`. |
| `H` vs `D` | If a rule or heuristic sets the effective horizon, state that relationship once rather than encoding it separately in both. | A regulatory planning-horizon cap should be represented in one place, not duplicated. |
| `C` vs `O` | `C` is what was selected; `O` is what actually happened. `C` is never rewritten after the fact. | A rejected or partially executed action stays `C`; only `O` reflects the shortfall. |
| `F` vs `P` | `F` is the feasible set itself; `P` is the prevailing conditions under which a feasible action produces its consequences. | A price ceiling can shape both `F` (what's feasible to sell) and `P` (what price applies) — state each role explicitly. |
| `P` vs `S` | `P` is ongoing background conditions; `S` is a shock originating outside the modeled agent or system. What counts as "external" depends on the model's own boundary. | A modeled competitor's action is endogenous; an unexpected war outside the modeled system may enter as `S`. |
| `M` vs `R` | `M` is the agent's (possibly wrong) belief; `R` is the reality function computing `O` from actual conditions. `R` must never be built from `M`. | A seller's believed demand never substitutes for the market-clearing rule. |
| `R` vs `O` | `R` is the mechanism — a one-time modeling choice; `O` is its output for one agent and period. Don't describe `R` as just a restatement of one `O`. | "Withdrawals capped at liquidity" is `R`; "60 units realized" is one `O`. |
| `P` (residual use) | `P` must be defined explicitly, not used to catch unexplained outcome variation. | "Market conditions" as a vague catch-all is not a valid `P`. |

## TER Variable Placement and Boundaries

| Variable | Definition | Put it here when… | Do not put it here when… |
|---|---|---|---|
| **`G`** Objective | The objective relevant to the agent's decision | It defines what the agent is acting in relation to, such as profit, survival, wellbeing, stability, growth, or security | It is merely a belief, valuation, action, or decision rule |
| **`M`** Model of reality | The agent's information, beliefs, assumptions, expectations, and interpretations about reality | It describes what the agent believes to be true, including beliefs about other agents or about its own future state, valuations, or decision tendencies | It is an actual constraint, actual condition, valuation itself, or the decision algorithm |
| **`F`** Actual feasible set | The actions reality actually permits for the agent at that time | The action is genuinely possible under current resources, institutions, technology, physical conditions, and other relevant constraints | The agent merely believes the action is possible |
| **`F̂`** Perceived feasible set | The actions the agent perceives as feasible and available to its decision process | The agent believes the action is available for consideration, whether or not reality actually permits it | The action is merely known about but excluded by search, filtering, attention, or selection inside `D` |
| **`V`** Valuation | The value assigned to actions relative to `G` | It determines how desirable or costly an action is relative to the agent's objective | It is the objective itself, a belief about reality, or the process used to select |
| **`H`** Time horizon | The future interval or consequences considered relevant to the decision | It determines which future consequences enter the decision problem | It merely determines how strongly an already-considered consequence is valued |
| **`D`** Decision process | The process through which the agent considers, compares, filters, and selects among actions in `F̂` | It represents optimization, satisficing, heuristics, habits, limited search, stochastic choice, or other selection procedures | It contains actual feasibility, realized consequences, or hidden preferences that properly belong in `V` |
| **`C`** Selected action | The action produced by the decision process | It is the action the agent actually selects | It is the realized result, or an action rewritten after failure or partial execution |
| **`R`** Reality function | The mechanism determining realized consequences from selected actions and actual conditions | It maps `C`, actual feasibility, prevailing conditions, shocks, and interacting actions into realized outcomes | It treats `M`, `F̂`, or `V` as objective reality, or acts as an unconstrained residual explanation |
| **`P`** Prevailing conditions | Actual conditions affecting realized consequences | It represents relevant environmental, institutional, technological, market, or system conditions at the time of realization | It is merely believed by the agent or used to absorb unexplained outcome variation |
| **`S`** External shocks | Changes external to the modeled system boundary that affect realization | The disturbance originates outside the system being modeled | It is generated endogenously by agents or mechanisms already inside the modeled system |
| **`O`** Realized outcome | The result produced when selected actions encounter reality and interact with other agents and conditions | It records what actually happens, including success, failure, partial execution, external effects, and system outcomes | It is merely intended, expected, believed, or selected |

### Hard boundary rules

**`G` vs `V`**

`G` is what the agent acts in relation to. `V` is how actions are valued relative to that objective.

**`M` vs `V`**

`M` is what the agent believes. `V` is how the agent values actions given its objective and relevant beliefs.

**`M` vs `F̂`**

`M` contains beliefs and understanding. `F̂` contains the actions perceived as actually available to the decision process.

**`F̂` vs `D`**

`F̂` defines what enters the decision environment. `D` determines what is examined, filtered, compared, and selected.

**`H` vs `V`**

`H` determines which future consequences are relevant. `V` determines how relevant consequences are valued. When they are observationally equivalent, use independent evidence or experimental design rather than infer both from the same observed choice.

**`D` vs `R`**

`D` selects. `R` realizes.

$$
(G,M,\hat{F},V,H,D) \rightarrow C
$$

then

$$
(C,F,P,S) \rightarrow O
$$

For multiple agents:

$$
O_t = R(C_{1,t},\ldots,C_{n,t},P_t,S_t)
$$

**`C` vs `O`**

Never rewrite `C` because execution fails. Failure, partial execution, or changed consequences belong in `O`.

**`F` is objective, not necessarily exogenous.**

`F` for agent `i` at time `t` is what is actually feasible. It may change endogenously because of institutions, resources, technology, or other agents' actions.

> When external search, attention, or information acquisition is itself an economically chosen activity, represent that activity as an action in `F̂`, place its costs and consequences in `R`/`O`, and reflect acquired information in subsequent `M`. Internal consideration or search within a decision procedure remains part of `D`.

### Common specification objects that are not TER primitives

| Object | How to use it |
|---|---|
| **Model state / stocks** | Wealth, inventory, capital, location, technology, balance sheets, physical stocks, and similar objects may be declared as model-specific state. They may constrain `F`, affect `P`, be represented imperfectly in `M`, and evolve through model-specific laws of motion. |
| **Feedback / update rules** | Dynamic specifications should declare the mechanisms by which `O_t` changes `G, M, F, F̂, V, H, D` at `t+1`. These are specification-specific update mechanisms, not a universal `U` primitive and not part of within-period `D`. |

> **Every economically relevant fact should have one primary TER location. If the same fact appears in multiple components, the specification must explain why that duplication is necessary rather than silently double counting it.**

## Specification Rules

Practices that keep a TER specification testable instead of merely descriptive.

- **Representation is not validation.** Being able to represent an observed outcome in TER is not evidence that a specification is correct — constrain assumptions with evidence you can check independently.
- **Don't infer components from `C` alone, and don't fit after the fact.** Observed action `C` doesn't uniquely identify `G`, `M`, `F̂`, `V`, `H`, or `D` — treat rival explanations as competing specifications, not post hoc adjustments.
- **Avoid double counting.** The same mechanism shouldn't be encoded across multiple components unless each has a genuinely distinct causal role.
- **Preserve established economic mechanisms.** Map utility functions, beliefs, heuristics, and solution concepts into TER; don't rewrite their substance to fit.
- **`D` may be deterministic or stochastic, but must be substantive.** Its flexibility isn't an explanation unless it's specified precisely enough to generate testable implications.
- **`C` is never rewritten after realization.** Failure, partial execution, or side effects belong in `O`.
- **`F` is objective, not belief.** Never infer actual feasibility from an agent's expectations, beliefs, or perceived probability of success. Those belong in `M`; perceived action availability belongs in `F̂`.
- **Specify `R` substantively, and never use `R` or `P` as a residual.** Both must be defined enough to generate testable implications, not absorb whatever's left unexplained.
- **Define the agent/system boundary explicitly.** A coordinated group may be one agent or many depending on the question — but don't double-count a collective action as also an independent constituent action, and don't assume an institution's objective is automatically each member's `G`.
- **Use independent evidence.** Constrain `G`, `M`, `F`, `F̂`, `V`, `H`, `D` from observed constraints, elicited beliefs, experiments, or structural estimation — not by reverse-engineering them from the result you want.
- **Compare against alternatives.** A specification's implications should be checked against competing specifications, established non-TER models, and null explanations — not judged solely by whether it can be made to fit one observation.
- **Distinguish framework failure from specification failure.** Most failed predictions challenge one specification, not TER itself — a framework-level challenge means a determinant can't be represented without distorting TER's definitions, two components collapse into one, or an axiom contradicts itself.
- **Replication tests must preserve variable meaning.** Don't redefine what a variable means just to reproduce a target result.
- **Distinguish decision error from execution error.** If `D` selects the wrong action, that's a decision-formation problem; if the selected action differs from what was actually executed, that's realization — keep the two apart.
- **Components can be functionally related without collapsing together.** Two components influencing each other in a given model doesn't mean they're the same variable — their conceptual separation doesn't require statistical or causal independence.
- **Match time resolution to the mechanism.** In sequential or multi-agent settings, feasibility can change between selection and realization; evaluate `F` at the point where execution occurs.
- **External effects belong in realized consequences.** When the mechanism produces effects on other agents, represent them in `O`; they do not require a separate TER primitive.

## Common Mistakes

Anti-patterns worth a second look before you trust a result — see Variable Placement and Specification Rules above for the reasoning behind each.

- Inferring `G`, `M`, `F̂`, `V`, `H`, or `D` directly from an observed action `C`.
- Fitting `D` (or another component) to a result after seeing it, instead of specifying it independently.
- Double-counting the same mechanism across more than one component.
- Putting a search or attention limit into `F̂` instead of `D`.
- Confusing an agent's beliefs (`M`) with actual feasibility (`F`).
- Rewriting `C` after execution fails or is partial, instead of recording it in `O`.
- Treating an expected or believed outcome as if it were the realized `O`.
- Using `P` or `R` as an unexplained residual for whatever else can't be accounted for.
- Silently promoting a test-specific assumption into a general TER claim.
- Rewriting an established economic mechanism's substance just to make it fit TER.

## Practical Tips

1. Ask whether the fact describes the agent's decision environment or realized reality.
2. Ask whether it changes what the agent perceives, values, or how it selects.
3. Avoid encoding the same mechanism twice.
4. Prefer the simplest specification that preserves the economics being studied.
5. If two placements remain plausible, treat them as competing specifications and test which better fits the evidence.

A TER specification should make its assumptions visible enough that another researcher can reproduce, challenge, or replace them.

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

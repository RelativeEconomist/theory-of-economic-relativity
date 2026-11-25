# TER v0.6.0 release notes draft

## v0.5.0 to v0.6.0

The [canonical paper](../../theory/academic.md) now states the decision and realization boundaries as explicit restrictions. It specifies rule domains, model-specific constraint checks, joint outcome readouts, dated information delivery, and separate objective and agent-side transitions. It also distinguishes settlement under a market rule from equilibrium consistency analysis. [v0.5.0 baseline](https://github.com/RelativeEconomist/theory-of-economic-relativity/blob/cc9547d231ba29adbc3c834049af094c0db8a780/theory/academic.md) · [Methodology](../ter-methodology-notes.md)

| v0.5.0 axiom | Disposition in v0.6.0 |
| --- | --- |
| 1. Information and beliefs | Combined into **Agent Selection**. Available agent-side information may shape choice. Required sensitivity to beliefs would exclude the habits already allowed in Model 5.1. |
| 2. Perceived feasible actions | Retained in **Agent Selection** as membership in the perceived set of attempts. Section 3 separately defines perceived attempt availability and objective feasibility at realization. |
| 3. Relative valuation | Retained in **Agent Selection** when valuation is used. The objective, model of reality, and time horizon condition valuation. |
| 4. Decision process | Combined into **Agent Selection**. Heterogeneous, stochastic, and valuation-free rules remain admissible. |
| 5. Actions and external effects | Combined into **Objective Realization**. Actions can affect outcomes and other agents. A particular effect depends on the specified mechanism and conditions. |
| 6. Effects on other agents | Combined into **Dynamic Feedback** for later effects. Immediate external effects belong to **Objective Realization**. |
| 7. Reality constrains consequences | Retained in **Objective Realization**. At fixed actions and realization conditions, the outcome comes from `R`. Beliefs can affect outcomes through the actions they shape. |
| 8. Infeasible continuation | Retained as **State Persistence**. It rules out unchanged continuation under infeasibility. The transition model determines what follows. |
| 9. Outcome feedback | Combined into **Dynamic Feedback**. Objective changes due to actions pass through realized outcomes. Belief updates use available information. |

**Formal changes.** A scalar score already evaluated as an expectation enters an optimizing rule directly. A state-contingent score requires a specified probability law. Conditional realization, observation, and transition equations use specification-level notation. All eleven named TER objects retain their roles. Constraint validation uses the model's own economic conditions. Fixed-state replay and rerunning a path after a policy change answer different questions.

**Compatibility.** A complete finite staged model that already respects its objective constraints can retain its choice, realization, and update rules. Use its joint result for the outcome readouts and keep deliveries at their original times. With the same initial conditions and draws, each stage gives the same result, so induction preserves the trace. Missing information, transition, or constraint assumptions still require a specification.

## Unresolved theoretical issues

- A literal same-event cycle between choice and its realized outcome requires separate causal and intervention semantics. Market clearing from submitted schedules and equilibrium consistency can already be specified.
- A realized outcome that depends directly on another agent's private beliefs at fixed actions and objective conditions requires separate justification. Belief-dependent valuation can already use higher-order beliefs.
- Exact stochastic continuum models and continuous-time replay require domain-specific measurability, aggregation, and timing results.
- Behavioral identification still depends on independent evidence. The matched bank-run comparison establishes parity for its game. Comparative predictive or reviewer-audit advantages remain open. [Bank-run comparison](../experiments/bank_run_identification/comparison.md)

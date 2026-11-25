# TER v0.6.0 architecture candidate

**Status** Research proposal. The candidate consolidates existing obligations, specifies their mathematical interfaces, and clarifies how to represent clearing and equilibrium. It introduces no TER primitives. [Canonical v0.5.0](https://github.com/RelativeEconomist/theory-of-economic-relativity/blob/cc9547d231ba29adbc3c834049af094c0db8a780/theory/academic.md)

## Basis for the proposal

The necessity audit found overlapping axioms and named objects that can be combined for particular prediction tasks. A reduced policy can reproduce choices while leaving the underlying menu, beliefs, and valuation unidentified. The same economy can also admit several equivalent implementations. TER, Architecture B, and the conventional withdrawal game matched on 648 exact histories and all held-out scores in the bank-run comparison. That establishes parity for the specified game. It leaves empirical performance and the comparative value of explicit boundaries open. [Methodology](../ter-methodology-notes.md) · [Coordination experiment](../experiments/architecture-adversarial-bank-run.md) · [Structural experiment](../experiments/architecture-adversarial-bank-run-structural.md) · [Identification results](../experiments/bank_run_identification/comparison.md) · [Architecture B](../experiments/architecture-b-state-transition.md)

## Consolidated axioms

1. **Selection.** At each decision point, an acting agent selects from the actions it perceives as available to attempt. Its decision process may use its model of reality and, when consulted, its valuation. Valuation evaluates actions relative to the agent's objective, given its model of reality and relevant horizon. Choice may be stochastic and may use a heuristic or habit. The agent selects using its available information and agent-side state.
2. **Objective realization.** Selected actions encounter the relevant objective conditions through a specified reality function. Realization may include failure, partial execution, and effects on other agents. Where actions jointly determine consequences, one joint realization supplies the system outcome and any interaction-dependent individual outcomes.
3. **Feedback.** Realized outcomes may change later objective conditions and later agent-side components, including those of other agents. Objective changes caused by modeled actions pass through their realized consequences. Beliefs about an outcome can change through information available to the agent. External shocks can change objective conditions outside the modeled action pathway.
4. **Persistence.** An existing system state can persist unchanged only while its continuation is objectively feasible.

| v0.5.0 axiom | Candidate disposition |
| --- | --- |
| 1. Information and beliefs | Combined into 1. Clarifies available inputs and permits a rule whose choice is insensitive to a particular belief. |
| 2. Perceived feasible actions | Retained in 1 as the choice support condition. Perceived attempt availability remains distinct from objective realization. |
| 3. Relative valuation | Retained in 1 as the condition on valuation when used. |
| 4. Decision process | Combined into 1. States menu membership once and preserves valuation-free and stochastic choice. |
| 5. Actions and external effects | Combined into 2. An asserted nonzero action effect requires a contrast in the specified outcome. |
| 6. Effects on other agents | Combined into 3 for later feedback. Contemporaneous effects remain part of 2. |
| 7. Reality constrains consequences | Retained in 2 as the realization boundary. Its decision-side clause is covered by 1. |
| 8. Infeasible continuation | Retained as 4 with the same one-way implication. |
| 9. Outcome feedback | Combined into 3 with the observation and mediation boundaries from §5.5. Feedback remains optional. |

The consolidation follows §5's allowance for heuristic decisions and realization failures. A reading of Axiom 1 or 5 that requires essential dependence on beliefs or actions in every model would change under this proposal. Adoption requires resolving that reading explicitly. [v0.5.0 axioms and formal architecture](https://github.com/RelativeEconomist/theory-of-economic-relativity/blob/cc9547d231ba29adbc3c834049af094c0db8a780/theory/academic.md#4-axioms)

## Mathematical specification

All auxiliary notation below describes a particular specification. The stage index $t$ pairs a choice with its realization conditions. Specify when each signal, choice, and objective condition occurs. The next stage is the next relevant event or decision point.

### Selection and information

Let $I^-_{i,t}$ denote information available to agent $i$ before selection. Declare how the agent's initial components, prior local state, and $I^-_{i,t}$ supply the choice inputs. The analyst may observe additional data. For each acting agent, the perceived menu is nonempty and selection obeys

$$
C_{i,t}=D_{i,t}(\hat F_{i,t},M_{i,t},v_{i,t};u^D_{i,t})\in\hat F_{i,t},
\qquad v_{i,t}(a)=V_{i,t}(a\mid G_{i,t},M_{i,t},H_{i,t}).
$$

Omit the valuation argument for a decision process that does not use it. $G$ and $H$ enter through valuation when used. For stochastic choice, declare the joint law of the draws $u^D$, including any common randomization and what agents can observe. Holding the permitted choice inputs, rule, and draw fixed, varying hidden $F_t$ leaves $C_{i,t}$ fixed. An objectively prevailing price can affect choice through a report that reaches the agent before selection. Only agents acting at a stage produce a new $C$ there.

### Joint realization and replay

Write $\mathbf C_t$ for the actions included in joint realization. Let $\mathcal O_t$ denote the collection of declared outcomes, with $O_t$ as its system outcome and any interaction-dependent $O_{i,t}$ supplied by the same realization. Then

$$
\mathcal O_t=R(\mathbf C_t,F_t).
$$

For an agent-level specification without explicit joint determination at that stage, use $O_{i,t}=R(C_{i,t},F_t)$. $F_t$ contains objective conditions relevant at realization. It can include an objectively resolved service order or shock that was unknown at choice. $R$ takes selected actions and these conditions as inputs. It reports what the rules actually deliver, including shortfalls, while preserving the original tender or attempted action.

For fixed-state replay, first reproduce the factual outcome from recorded actions and $F_t$. Substitute the action or actions of interest and hold other actions and the realization conditions fixed. A stochastic model must preserve any realized inputs or coupling needed for this query. A marginal outcome distribution alone does not specify what would have happened in the same case. A simulation of a new policy can instead recompute choices and conditions according to the declared intervention.

### Feedback and persistence

Let $S_t$ denote the specification's opening objective system state, $B_{i,t}$ the tuple of existing agent-side components, and $\xi_t$ any additional objective conditions resolved by realization. Let $L_{i,t}$ be the information made available between decisions, which may include an own action record or receipt. Use separate rules to represent objective conditions, state transitions, and agent updates,

$$
F_t=\Phi_t(S_t,\xi_t),
\qquad S_{t+1}=T_t(S_t,F_t,\mathcal O_t,e_{t+1}),
\qquad B_{i,t+1}=U_{i,t}(B_{i,t},L_{i,t}).
$$

The maps and the external transition input $e$ are specification-specific. A declared observation rule maps dated events to each agent's $L_{i,t}$. An agent may retain local state or follow an internal update without seeing the system outcome. Declare local draws when agent updates are stochastic. If an action changes objective conditions before a later modeled event, record its realized consequence at the earlier event. An enforceable commitment is one example. External inputs need not be statistically independent of other variables.

For persistence, define $\operatorname{CanContinue}(S_t,F_t)$ independently of the proposed successor. Interpret state equality on the economically relevant properties whose continuation is being studied.

$$
\neg\operatorname{CanContinue}(S_t,F_t)\ \Longrightarrow\ S_{t+1}\ne S_t.
$$

In a stochastic specification, impose this restriction on admissible paths. Stability analysis remains optional and depends on the specified transition. [Canonical timing, reality, persistence, and feedback](../../theory/academic.md#5-formal-architecture)

## Simultaneous clearing and equilibrium

| Economic case | Representation already available |
| --- | --- |
| Price posted before quantity choice | Place the delivered quote in $M$, and apply the actual price and settlement constraints through $F_t$ and $R$. A later price revision is a separate event. |
| Sealed bids or schedules clear together | The submitted bid or contingent schedule is $C_i$. One joint $R$ calculates the clearing price, allocations, transfers, and any rationing from the submitted objects and the market rule. |
| Equilibrium conditions solved simultaneously | Evaluate candidate decisions under their specified information and solve the source model's best-response, feasibility, and belief-consistency conditions. The solver is an analytical device unless the economic model specifies it as part of the institution. |
| Price adjustment or learning | Use staged choices, observations, and price updates with a declared adjustment law. Equilibrium existence alone implies no convergence. |

For an interior price-taking benchmark, write $z_i(p)$ for participant $i$'s optimal net demand conditional on $p$. Under exact aggregate clearing, solve $\sum_i z_i(p)=0$ subject to the source model's feasibility and other equilibrium conditions. A clearing rule operating on admissible submitted schedules $z_i(\cdot)$ can realize a feasible root. With the same demand schedules and constraints, every root it realizes satisfies the benchmark conditions. Equality of equilibrium sets requires preserving all feasible roots and any branches of set-valued demand. Equality of point predictions requires the same selected outcome in the cases compared. A static analyst can evaluate the same equations without positing that participants submit entire schedules. [Arrow and Debreu, 1954](https://web.stanford.edu/class/msande311/arrow-debreu.pdf) · [Scarf, 1959 working paper](https://elischolar.library.yale.edu/cowles-discussion-paper-series/303/)

The existing supply-and-demand scan evaluates choices at candidate quotes. The Krugman configuration derives candidate prices and quantities from specified behavior and source equilibrium conditions, then checks joint realization. These examples show two existing uses of equilibrium. A candidate price should reach an executed decision only through the information assumed by the source model. An equilibrium solver's trial evaluations do not by themselves describe observed trades or the sequence of messages in a market. [Supply-and-demand scan](../ter/market.py) · [Krugman configuration](../reproductions/krugman_1980_configuration.md)

**Proven limit at fixed event semantics.** Let a supplier choose $q=p$ and let the same event realize $p=2-q$. The equations have the unique solution $(q,p)=(1,1)$. Replacing the price equation with $p=1/2$ gives $q=1/2$. Replacing the quantity equation with $q=1/2$ gives $p=3/2$. A TER stage in which $q$ is selected before $p$ is realized cannot reproduce the first intervention while holding the supplier's pre-choice inputs fixed. A posted price before choice, an admissible contingent schedule, or an analytical fixed-point calculation can represent the applicable economics with its stated timing and intervention semantics. A literal contemporaneous cycle with the original action and outcome meanings requires separate justification. The candidate leaves the existing ordering in place.

## Compatibility and change log

| Topic | v0.5.0 | Candidate |
| --- | --- | --- |
| Axiom presentation | Nine clauses, with overlapping support, information, and feedback language | Four consolidated clauses with an explicit crosswalk |
| Selection | Optional valuation and a separate perceived menu | Same decision relation, with declared choice-time information and randomness conventions |
| Realization | Agent-level or joint $R$ under objective conditions | Same mechanisms, with a joint outcome readout and explicit fixed-state replay semantics |
| Dynamics | Optional outcome feedback and a persistence constraint | Separate objective and agent update equations with delivery timing and the same persistence implication |
| Clearing and equilibrium | Specification-level mechanisms and consistency conditions | Explicit treatment of posted prices, joint clearing, equilibrium analysis, and adjustment |
| Representation | Named components and model-specific analytical states | Allow component composition when required meanings, readouts, and interventions remain recoverable |

Keep the boundaries between perceived attempts and objective execution, available information and objective conditions, selection and realization, individual and system effects, and outcomes and later state. Preserve separate valuation and decision logic when both are modeled. A fixed $G$ or $H$ can be bound into valuation. Histories may use sufficient summaries, and one joint outcome record may supply multiple readouts. A coarser representation is adequate only if any two states it merges yield the same law for the declared queries, including the relevant interventions.

**Conditional equivalence.** For a fully specified finite staged model, preserve its initial law, decision inputs and joint draws, realization outputs, update laws, and observation process. The proposed notation then gives the same conditional law at the first stage. Each preserved transition and delivery yields the same conditional law at the next stage. Induction gives equality of all finite trace laws. Under a declared intervention, the same argument applies if both representations replace the same mechanism and preserve the coupling needed for replay. This establishes equivalence for the specified class and queries. It leaves a general minimality theorem open. An Architecture B encoding qualifies when it retains the same information and mechanism boundaries, including a realized consequence for any action-induced objective transition.

**Separate theory decisions.** A universal equilibrium or selection rule, mandatory optimizing behavior, exact aggregate Markov closure, and literal same-event cyclic feedback would each change the theory. Introducing any of them requires an economic motivation and a demonstration that the existing mechanisms cannot handle the target while preserving its meaning. A continuous-time causality or replay claim beyond the stated finite-stage result likewise needs its own semantics and proof.

## Adoption criteria

### Proof obligations

1. **Conservative restatement.** Verify the crosswalk both ways on the intended class. Exhibit a mapping from every supported v0.5.0 specification into the candidate and a reverse mapping that preserves canonical meanings. Resolve any disagreement about essential dependence or about which feedback channels the prose permits.
2. **Information and replay.** Prove that the mapping preserves permitted choice inputs, realized inputs, joint randomization, and the effects of the declared substitutions. Show that matching marginal realization kernels alone can fail same-case replay.
3. **Economic closure.** For each benchmark, state the domains and derive feasibility, best-response and information-consistency conditions from the source assumptions. Account for empty and multiple equilibrium sets. Require a specified selection or failure rule whenever a unique realized outcome is claimed. Preserve the distinction between the consistency set and an adjustment path.
4. **Scope and evidence.** For any proposed compression, specify the preserved queries and show why the chosen state is sufficient. Test any claim of better prediction, identification, or researcher auditability separately under matched economics and evidence.

### Regression tests required before adoption

| Test | Required result |
| --- | --- |
| Selection boundary | Changing hidden reality at fixed agent-side inputs and draw leaves choice unchanged. Changing a delivered signal may change choice under a responsive rule. Cover valuation-free decisions, constant policies, $C\in\hat F$, and cases where $G,H$ affect selection only through valuation. |
| Joint settlement and replay | Reproduce the 648 bank histories, exact claim and reserve identities, settlement priority, the $4/5$ binding contrast, the zero nonbinding contrast, and the $6/5$ maximum historical guarantee. Verify factual replay before substitutions. |
| Feedback and persistence | A withheld outcome changes objective accounts without being treated as observed. A delivered receipt can affect only subsequent choices. A binding resource constraint rules out unchanged continuation while leaving separately specified successors admissible. |
| Clearing and equilibrium | Preserve the supply-and-demand and Krugman checks. Add a submitted-schedule clearing case with known roots and matched accounting. Exercise no root, multiple roots, a declared selection rule, and a case where an equilibrium exists without convergence. Keep the same-event cyclic counterexample as a boundary check. |
| Comparative parity | Compare exact ledgers, equilibrium sets, and joint forecast laws under the frozen bank contract. Reproduce the tied held-out Brier losses under matched assumptions. |

Adopt the consolidation after the conservative mapping and regression checks pass. Keep any extension beyond that mapping under separate review. [Bank-run protocol](../experiments/bank_run_identification/protocol.md) · [Decision boundary tests](../tests/test_decision_feasibility_boundary_contract.py) · [Feedback ordering tests](../tests/test_feedback_ordering_contract.py) · [Krugman tests](../reproductions/test_krugman_1980_ter.py)

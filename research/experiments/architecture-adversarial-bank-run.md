# Adversarial Architecture Test 01: Bank Run Coordination

**Status:** Completed analytical toy benchmark, not an empirical test or reproduction of Diamond–Dybvig (1983).  
**Architecture A:** TER canonical v0.5.0 (`academic.md`, unchanged).  
**Architecture B:** State–Decision–Transition Economics draft v0.1.0 (`architecture-b-state-transition.md`, unchanged).  
**Decision target:** Does B dominate TER in mathematical completeness, distinct economic predictions, identification, or reduced independent assumptions?

## 1. Independent benchmark

Two patient depositors simultaneously select **W** (wait) or **D** (withdraw). Payoffs below are *declared reduced-form assumptions*: they are **not** derived from a bank balance sheet, a sequential-service contract, or the original Diamond–Dybvig optimization problem. Each cell reports depositor 1, depositor 2. Thus this test targets coordination and architecture, not full banking economics.

| Economic regime | (W,W) | (D,W) | (W,D) | (D,D) |
|---|---|---|---|---|
| Healthy | (2, 2) | (1, 0) | (0, 1) | (0.8, 0.8) |
| Fundamental shock | (0.7, 0.7) | (1, 0) | (0, 1) | (0.8, 0.8) |
| Credible guarantee | (2, 2) | (1, 1.2) | (1.2, 1) | (0.8, 0.8) |

**Interpretation:** Shock damages the return from waiting even if both wait. Guarantee protects a waiting depositor even if the other withdraws. These are explicitly assumed payoff consequences, **not** independently modeled liquidity and insurance mechanisms. Accordingly their direction is illustrative, not an estimated causal effect.

## 2. Exact game-theoretic results

For each agent, compare action payoffs holding the other agent's action fixed. The pure Nash equilibria are:

- **Healthy:** (W,W) and (D,D).
- **Fundamental shock:** (D,D) is unique.
- **Credible guarantee:** (W,W) is unique.

In the healthy regime, let \(q_i\) denote depositor \(i\)'s *subjective* probability that the other withdraws. Then

\[
E_i[W\mid q_i]=2(1-q_i),\qquad E_i[D\mid q_i]=1-0.2q_i.
\]

Thus \(D\) is weakly preferred exactly when \(q_i\ge 5/9\). With common \(q=0.2\), both choose W; with common \(q=0.8\), both choose D. Those belief-based choices are **not** themselves proofs of equilibrium unless beliefs are consistent with actual policies. For the guarantee regime, \(E[W]=2-0.8q\) exceeds \(E[D]=1-0.2q\) for all \(q\in[0,1]\). For the shock regime, \(E[W]=0.7(1-q)\) is below \(E[D]=1-0.2q\) for all \(q\in[0,1]\).

**Execution check:** An exhaustive enumeration of all four pure action profiles under each payoff matrix confirmed the equilibrium sets above. No Monte Carlo simulation or data fitting was needed.

## 3. Architecture A mapping: TER v0.5.0

For each depositor \(i\), with the original definitions preserved:

- \(G_{i,t}\): consumption payoff is the reference for valuation (benchmark choice).
- \(M_{i,t}\): subjective \(q_i\) and beliefs about the announced regime and consequences.
- \(\hat F_{i,t}=\{W,D\}\): perceived actions available to attempt, identical across regimes here.
- \(H_{i,t}\): relevant horizon spanning the wait/withdraw payoff realization.
- \(V_{i,t}(a\mid G,M,H)\): expected payoff from \(a\) calculated from the declared payoff table and beliefs; the believed payoff matrix enters through \(M\), not as a fact about objective reality.
- \(D_{i,t}\): choose a payoff-maximizing action from \(\hat F\) (deterministic tie-break W, declared before results).
- \(C_{i,t}\): chosen W or D.
- \(F_t\): objectively realized economic regime and its stipulated payoff conditions, **not** the subjective probability \(q_i\).
- Joint \(R(C_{1,t},C_{2,t},F_t)\): return the pair of *realized* payoffs and withdrawal count from the true regime table.
- \(O_t\): this joint result, with agent-level results obtained from the same joint \(R\), not independent single-agent applications of \(R\).

For multiple stages, define an **optional benchmark-specific** belief update after agents observe the previous withdrawal count, e.g. \(q_{i,t+1}=0.2\) after zero withdrawals and \(0.8\) after two withdrawals. Observed information is required before changing \(M\). Objective regimes change only via declared external shocks or realized outcomes, according to TER Model 5.5. This feedback choice is a **toy extension**, not part of Diamond–Dybvig or a new TER axiom.

## 4. Architecture B mapping: draft v0.1.0

- \(X_t\): objective regime, with its payoff table (the economic state, not beliefs).
- \(I_{i,t}\): available subjective \(q_i\), regime announcement and historical observations. Distinguish what is observed from what is merely believed.
- \(A_i(I_{i,t})=\{W,D\}\).
- \(\pi_i(\cdot\mid I_{i,t})\): payoff-maximizing selection rule, using the **same** believed table, beliefs and tie-break as TER.
- \(Y_t\sim \mathcal R(\cdot\mid X_t,a_t)\): deterministic realized payoff/withdrawal tuple from the true table.
- \(X_{t+1}\sim\mathcal Q(\cdot\mid X_t,a_t,Y_t)\): regime transition, e.g. unchanged absent an exogenous shock or specified intervention.
- Agent information at \(t+1\) must be generated from available observations and histories by an **additional model-specific information process**, not \(\mathcal Q\) alone. The same optional toy belief update as above is used for parity.

**Critical mathematical point:** B's three headline relations do not form an executable stochastic model until the initial state distribution and information/observation mechanism are declared. This is acknowledged in B v0.1.0, but must be enforced as part of any actual specification. The Markov property of \(X_t\) cannot simply be assumed for an insufficient aggregate state.

## 5. Equality of outcomes and where the architectures differ

With the same payoff matrices, beliefs, decision rule, observations and regime transitions, both mappings predict identical actions, equilibria, realized payoffs and subsequent observed histories. There is **no predictive advantage for either architecture in this benchmark**. That equality follows by direct construction, not empirical validation.

| Criterion | TER A | Architecture B | Result |
|---|---|---|---|
| Original game-theoretic equilibria | Reproduced | Reproduced | Tie |
| Belief-induced runs vs fundamental shock | Distinguishes \(M\) from \(F\) by construction | Can distinguish \(I\) from \(X\) when specified | Tie on outcomes; TER is more explicit |
| Institutional guarantee | Explicit change in objective realization conditions, plus beliefs when observed | Explicit change in state/realization, plus information when observed | Tie |
| Multi-period implementation | Requires explicit feedback mechanisms | Requires explicit transition **and information process** | No demonstrated winner |
| Number of independent economic assumptions | Same payoff tables, information and choice rules | Same payoff tables, information and choice rules | Tie; shorter notation is not fewer assumptions |
| Explanation/identification | Not identified from actions alone | Not identified from actions alone | Tie |

**Observational equivalence:** Seeing (D,D) alone cannot identify whether the cause was a healthy bank with sufficiently pessimistic beliefs, a fundamental shock, or some other specified incentive mechanism. If the payoff regime, beliefs and interventions are not measured independently, *neither architecture can recover the cause from the action profile alone*. Encoding \(M\) separately does not solve identification without evidence.

## 6. Second challenge: micro-to-macro sufficiency

Let \(Z_t\) be just the aggregate withdrawal count. A zero withdrawal observation is compatible with materially different objective regimes and belief distributions. Those microstates can produce different probabilities of next-stage withdrawals when new signals arrive. Therefore a closed law \(P(Z_{t+1}\mid Z_t)\) is not guaranteed by either architecture. In B the required condition is that all microstates with the same aggregate \(Z_t\) induce the same conditional law for \(Z_{t+1}\); in TER the comparable requirement must be imposed when constructing a model-specific aggregate system state and its update mechanisms.

**Consequence:** Neither architecture automatically unifies micro and macro at the level of a closed aggregate Markov equation. Both require economically sufficient state descriptions or explicitly justified approximations.

## 7. Decision / action on TER

**Architecture B: RETIRE its claim to superiority on compactness or formal predictive strength based on this test.** Compact notation alone has not eliminated any independent economic assumption, increased identification, or improved a result. **Do not declare Architecture B universally falsified:** this single constructed toy case cannot rule out advantages in other models.

**Retain B as a frozen adversarial baseline only if the research program requires further comparisons.** It does **not** earn equal standing as a validated rival or a second canonical theory for the public site.

**Potential improvement to TER, proposed separately (no canonical change):** create an *optional mathematical specification contract*, not a new axiom or primitive, requiring (i) precise domains of \(D\), \(R\), and time/state indexing, (ii) declared observations and update rules for \(M\), \(\hat F\), etc., (iii) explicit equilibrium consistency requirements where used, and (iv) a declared aggregation mapping and sufficiency check where macro claims are made. This improves mathematical auditability while preserving canonical TER's semantic distinctions.

**What this test cannot establish:** reproduction of the actual Diamond–Dybvig (1983) banking contract; empirical prediction; institutional insurance feasibility, budget consequences, or welfare; correctness of either framework as a universal economic architecture. A stronger future test would derive sequential service, liquidation, resource constraints, insurance finance, and information experiments from one common fully specified economic model rather than stipulating payoffs.

## Sources

- TER v0.5.0: `academic.md`, especially §§3–5, 7.7–7.10.
- TER methodology: `ter-methodology-notes.md`, especially Variable Placement and Specification Rules.
- Architecture B v0.1.0: `architecture-b-state-transition.md`.
- Diamond, Douglas W., and Philip H. Dybvig (1983), *Bank Runs, Deposit Insurance, and Liquidity*, *Journal of Political Economy* 91(3), 401–419, https://doi.org/10.1086/261155 . This paper motivates the coordination example; the numbers above are **not** taken from it.

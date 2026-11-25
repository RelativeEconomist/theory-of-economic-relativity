# Independent Adversarial Architectural Review of TER v0.5.0

**Status:** Research proposal and review. Not canonical. Does not amend `theory/academic.md`.
**Reviewed version:** TER v0.5.0 (`theory/academic.md`), with `research/ter-methodology-notes.md`, `research/README.md`, `research/experiments/architecture-b-state-transition.md`, both adversarial bank-run benchmarks, `research/experiments/bank_run_identification/` (protocol and results), and `research/ter/market.py` with `research/tests/test_07_supply_and_demand.py` for the market-clearing question.
**Independence:** No v0.6.0 proposal (Codex or otherwise) was read before or during this review.
**Date:** 2026-11-23

## Reading guide

Every claim carries one label:

| Label | Meaning |
|---|---|
| **[Proof]** | Follows deductively from the canonical text under the formal reading stated in §1. |
| **[CE]** | Formal counterexample: a concrete specification that exposes a defect. |
| **[Hyp]** | Hypothesis. Plausible, not proven, would need theoretical or empirical work. |
| **[Judg]** | Reviewer judgment about design value. Not a mathematical claim. |
| **[Verified]** | Independently recomputed by the reviewer. |

Section 2–8 evaluate TER **as written**, with canonical definitions preserved. Proposed changes appear only in §9–§11 and are marked as proposals.

---

## 0. Executive verdict

1. **The axioms carry little of TER's mathematical content.** [Proof] Of nine axioms, four are permission statements ("may", "can") that every specification satisfies, one is analytic (A8), one is definitional (A3), and one is a subset of another (A2 ⊂ A4). The boundaries that actually restrict specifications, and which `AGENTS.md` treats as core, live mostly in the *Boundary* and *Scope* paragraphs of §5, not in §4.
2. **The eleven named objects are not mutually independent.** [Proof] `G` and `H` are absorbable into `V`; `O_{i,t}` is a projection of `O_t`; and the six-way agent-side decomposition `(G, M, F̂, V, H, D)` is a coordinate choice on a single agent state. The decomposition is justified only where each component has its own evidence or intervention, which the canon asserts but does not operationalize.
3. **Two structural maps are missing.** [Proof] Model 5.5 is written with arrows, not functions. A dynamic TER specification is not a well-defined process without (a) an objective transition for `F` and (b) an observation channel from reality to `M`. The second is needed to enforce TER's own rule that "realized outcomes may affect an agent's model of reality only through the information available to that agent".
4. **"Objective feasible state" has no formal feasibility content.** [Proof] `F_t` is a state; `F̂_{i,t}` is a set of actions. Nothing in the canon maps one to the other, and nothing forces `R` to respect resource or accounting limits. Under canonical TER, `R` may pay every bank-run claimant in full regardless of assets.
5. **Equilibrium is defined in words but not in the architecture.** [Proof] Models 5.1–5.5 are recursive (belief → choice → realization → update). Nash, Bayes–Nash, rational-expectations and Walrasian equilibria are fixed points across that recursion. TER can verify them after the fact or import them into `M`; it cannot state them. The bank-run experiments and `test_07` both import or externally compute the equilibrium.
6. **The Architecture B and bank-run experiments were bound to tie.** [Proof] Faithful encodings of the same stochastic game induce the same outcome law, so equal Brier losses are a theorem, not evidence. The experiments are correct as consistency checks and the reported equilibria are right [Verified], but they cannot discriminate architectures. One TER mapping in the structural benchmark also conflicts with the canonical definition of `F_t` (§7.3).
7. **A smaller architecture preserves TER's advantages.** [Judg, with Proof for equivalence] A kernel of seven primitives plus two structural maps (§10) keeps every boundary TER uses in practice and adds formal content. It is smaller in independent primitives, not in symbol count.
8. **Genuine limitations exist.** [CE] Psychological games, multi-period realization, continuum economies, menu-dependent valuation, and rational-expectations prices each require either a boundary violation or an unstated extension (§11).

**Overall recommendation:** Keep TER's core distinctions (belief vs reality, perceived vs objective feasibility, selection vs valuation, one joint realization). Revise the axiom set into a short list of testable restrictions. Add a transition map, an observation channel, an outcome-constraint correspondence and an optional consistency (equilibrium) condition. Demote `G`, `H`, and `O_{i,t}` from independent core objects. Do not adopt Architecture B as a replacement.

---

## 1. Formal reading of TER v0.5.0

To test independence and necessity, the canon must be typed. The reading below uses only canonical content. Where the canon is silent, the gap is flagged rather than filled.

For agent `i` at decision point `t`:

| Object | Canonical role | Type used in this review | Source |
|---|---|---|---|
| $\mathcal A_i$ | action universe | set (not named in canon; implied by "potential action $a$") | §3 |
| $\hat F_{i,t}$ | perceived feasible set | $\hat F_{i,t}\subseteq\mathcal A_i$ | §3, 5.2 |
| $M_{i,t}$ | model of reality | element of an agent state space $\mathcal M_i$ | §3 |
| $G_{i,t}, H_{i,t}$ | objective, horizon | parameters of valuation | §3, 5.1 |
| $V_{i,t}$ | valuation | $V_{i,t}:\mathcal A_i\to\mathbb R$ (the canon writes "value"; real-valued is the standard reading and the one `argmax` requires) | 5.1 |
| $D_{i,t}$ | decision process | $D_{i,t}:(\hat F,M,V)\mapsto\Delta(\hat F)$ (deterministic as a degenerate case) | 5.1 |
| $C_{i,t}$ | selected action | $C_{i,t}\in\hat F_{i,t}$ | 5.2 |
| $F_t$ | objective feasible state | element of an objective state space $\mathcal F$ | §3 |
| $R$ | reality function | $R:\prod_i\mathcal A_i\times\mathcal F\to\mathcal O$; deterministic conditional on inputs (methodology convention) | 5.2, 5.3 |
| $O_t, O_{i,t}$ | system, agent outcome | $O_t\in\mathcal O$; $O_{i,t}$ derived from the same joint $R$ | 5.3 |
| Model 5.5 | feedback | **untyped**: arrows "indicate possible influence" | 5.5 |
| Constraint 5.4 | persistence | **untyped**: "continuation no longer feasible" is undefined | 5.4 |
| Equilibrium | consistency | **untyped**: "under the equilibrium concept being used" | §3 |

The three untyped rows are the main source of the findings below.

---

## 2. Axioms: independence and redundancy

### 2.1 Classification

A sentence restricts a specification only if some specification fails it. Using that test:

| Axiom | Logical form | Class | Excludes any specification? |
|---|---|---|---|
| A1 Agents act on information and beliefs | "Decisions depend on $M$" | substantive only under reinterpretation (Prop 2.4) | as written, excludes admissible ones |
| A2 Select among perceived feasible actions | $C\in\hat F$; "$\hat F$ may differ from what reality allows" | first clause = A4; second = permission | no (beyond A4) |
| A3 Valuation relative to objectives | "when valuation occurs, $V(\cdot\mid G,M,H)$" | definitional | no (Prop 2.3) |
| A4 Selection through a decision process | $C=D(\hat F,\ldots)$, $C\in\hat F$ | substantive (support restriction) | **yes** |
| A5 Actions contribute to outcomes | "outcomes may also depend on interactions and $F$" | permission plus the form of $R$ | no |
| A6 Actions can affect other agents | "can change ... at later decision points" | permission; corollary of A5+A9 | no |
| A7 Reality constrains consequences | "reality ultimately determines consequences" | substantive only under reinterpretation (Prop 2.5) | as written, false in TER's own bank-run example |
| A8 Infeasible continuation prevents persistence | "infeasible ⇒ cannot persist" | analytic | no (Prop 2.2) |
| A9 Outcomes may shape subsequent conditions | "may alter" | permission | no |

### 2.2 Propositions

**Proposition 2.1 (permission axioms are tautologies). [Proof]** Read as a property of a given specification $S$, "component $X$ *may* respond to $Y$" is satisfied whether $S$ makes $X$ respond to $Y$ or not. Read as a modal claim ("some admissible specification lets $X$ respond to $Y$"), it constrains the class of admissible specifications only by *enlarging* it, never by excluding a member. Either way no specification is ruled out. Hence A5's second sentence, A6, A9, and A2's second sentence have no restrictive content. They serve as scope declarations: they tell readers that TER does not forbid these channels.

**Proposition 2.2 (A8 is analytic). [Proof]** Let "continuation of state $x$ is feasible" mean "there exists an admissible path on which $x$ continues unchanged". Then "continuation infeasible ⇒ $x$ cannot persist unchanged" is the contrapositive of "persists ⇒ some admissible path continues it", which holds by the meaning of *admissible*. Constraint 5.4 inherits this: it states a definition, not a restriction, and the canon itself notes that it "does not specify what state follows or the mechanism through which change occurs".

**Proposition 2.3 (A3 is definitional; G is not independently identified). [Proof]** Given any real-valued $\tilde V:\mathcal A\times\mathcal M\to\mathbb R$, set $G:=\tilde V$ (the objective "maximize $\tilde V$") and $H$ to any horizon that includes every consequence $\tilde V$ uses. Then $\tilde V(a\mid M)=V(a\mid G,M,H)$. Every valuation is "relative to an objective", so A3 excludes nothing. The methodology concedes the practical version: "Don't invent multiple objectives ... one valuation relative to one `G`".

**Proposition 2.4 (A1 as written conflicts with admissible decision processes). [CE]** Let $D_{i,t}(\hat F,M,V)=a_0$ for all inputs, with $a_0\in\hat F$. This is a habit rule, which §3 and 5.1 explicitly admit. Under it, decisions do not depend on information, beliefs, or $M$, contradicting A1's "Decisions depend on an agent's information, beliefs, and model of reality". Either A1 means "may depend" (then Prop 2.1 applies and it is empty) or it means something else. The only reading that is both restrictive and consistent with §5.1 is the **exclusion form**:

$$
C_{i,t}\;\perp\!\!\!\perp\;F_t\;\Big|\;(M_{i,t},\hat F_{i,t})
$$

with any randomization in $D$ drawn on the agent side. That is, objective conditions affect choice only through agent-side objects. This is exactly the 5.1 *Boundary* paragraph. It is TER's most important restriction and is testable when $M$ is measured.

**Proposition 2.5 (A7 as written is false in TER's own example; its exclusion form is correct). [CE]** In the healthy-regime bank (structural benchmark, $r=2$), the profile `WW` yields consumption $8/5$ each and `DD` yields $1$ each, with identical objective state. Which profile occurs depends on depositors' beliefs $q_i$ (run if $q_i>1/4$). So consequences are *not* determined "regardless of an agent's beliefs or expectations" (Reality definition, §3). Beliefs determine consequences through actions. The restrictive and correct form is:

$$
O_t\;\perp\!\!\!\perp\;(M,\hat F,V,D)\;\Big|\;(C_t,F_t),
$$

that is, $R$ takes no agent-side argument. That is the methodology's rule "`R` must never be built from `M`". The canonical slogan "behavior is shaped by perceived reality, consequences are constrained by reality" survives under this reading; the stronger "regardless of beliefs" wording does not.

**Proposition 2.6 (A2 ⊂ A4; A6 ⊂ A5 ∧ A9). [Proof]** A4 states that $C$ results from $D$ "from among its perceived feasible actions", which is A2's first sentence. A2's second sentence is a permission. A6 says actions can, through outcomes, change later conditions of other agents and $F$; A5 gives action → outcome and A9 gives outcome → later $(G,M,\hat F,V,H,D,F)$ without restricting to the acting agent. A6 is a corollary.

### 2.3 What the axioms are missing

The restrictions that do define TER in practice are in §5 and the methodology, not in §4:

| Working restriction | Where it lives now | Axiom? |
|---|---|---|
| $D$ does not take $F_t$ (exclusion) | 5.1 Boundary | no (A1 only gestures at it) |
| $R$ does not take agent-side objects | methodology Variable Placement | no (A7 wording is weaker and partly false) |
| interaction-dependent agent outcomes come from one joint $R$ | 5.3 Agent-level outcomes | no |
| $M$ updates only through information available to the agent | 5.5 prose | no |
| endogenous change in $F$ arrives through outcomes; shocks are exogenous | 5.5 Sources of change | no |
| realized outcome is distinct from later objective state | `AGENTS.md` | no |

**Finding. [Proof]** The axiom set is neither minimal (redundancies above) nor complete (it does not entail the working restrictions). The Axiom Map's claim that axioms "primarily support" each model is notional for the permission axioms.

---

## 3. Necessity of the eleven named objects

Necessity criterion used here: an object is **mathematically necessary** if removing it shrinks the set of representable choice-and-outcome processes; it is **methodologically necessary** if removing it loses a distinction that has its own evidence or intervention, even though the process is unchanged.

### 3.1 Propositions

**Proposition 3.1 (H is absorbable into V). [Proof]** Let valuation be $V(a\mid G,M,H)=\sum_{s\ge0}\delta_s\,\mathbb E_M[u_G(a,s)]$ restricted to $s\le H$. Define weights $w_s=\delta_s\mathbf 1\{s\le H\}$. Then $V=\sum_s w_s\,\mathbb E_M[u_G(a,s)]$ with no $H$. Every horizon is a weight profile with zeros. The methodology concedes this ("When `H` and valuation parameters are observationally equivalent ..."). $H$ is distinct from discounting only if there is evidence about *which consequences are considered* (attention, elicitation), not just how they are weighted.

**Proposition 3.2 (O_{i,t} is a projection). [Proof]** The canon requires interaction-dependent agent outcomes to come from the same joint $R$ as $O_t$. Define $O_{i,t}=\pi_i(O_t)$ for a declared projection $\pi_i$. Model 5.2 is the case $n=1$. A separate primitive adds nothing except the risk of the inconsistency in CE-10.

**Proposition 3.3 (agent-side factorization is a coordinate choice). [Proof]** Model 5.5 lets feedback change any of $(G,M,\hat F,V,H,D)$. Define an augmented agent state $\tilde M_{i,t}=(M_{i,t},G_{i,t},H_{i,t},\hat F_{i,t},\theta^V_{i,t},\theta^D_{i,t})$, where $\theta$ index the valuation and decision rules. Define one fixed rule $\tilde D_i(\tilde M)=D_{\theta^D}(\hat F,M,V_{\theta^V}(\cdot\mid G,M,H))$. Every TER dynamic specification with time-varying components equals a specification with fixed $\tilde D_i$ and a single updating state $\tilde M_{i,t}$. Consequently "learning changes $D$" and "learning changes $M$" are not distinguishable from choice-and-outcome data alone. The six-way decomposition has value only to the extent its parts are separately measured or manipulated.

**Proposition 3.4 (F̂ is not identified under deterministic optimization; it is under full-support stochastic choice). [Proof]**
(a) If $D=\arg\max_{a\in\hat F}V(a)$, the specifications $(\hat F,V)$ and $(\mathcal A,V')$ with $V'(a)=V(a)$ on $\hat F$ and $V'(a)=-\infty$ elsewhere produce the same choice on every menu. Perceived unavailability is indistinguishable from "certain to be worthless".
(b) If $D$ assigns positive probability to every element of $\hat F$ (logit, random utility with full support), then $\hat F=\operatorname{supp}C$ given enough repetitions at fixed $M$, and actions with very low $V$ still appear while actions outside $\hat F$ never do. This matches the consideration-set literature (Masatlioglu, Nakajima and Ozbay 2012; Manzini and Mariotti 2014), which identifies consideration sets only under menu variation and structural restrictions.

Note a further gap: the methodology places "perceived but not evaluated" in $D$ and "not perceived" in $\hat F$. The consideration-set literature does not draw that line, and the canon gives no evidence class that separates the two. [Judg]

### 3.2 Object-by-object assessment

| Object | Mathematically necessary? | Methodologically necessary? | Assessment |
|---|---|---|---|
| $G$ | No (Prop 2.3) | Weakly: labels the objective | **Revise:** parameter of $V$, not an independent core object |
| $M$ | Yes: belief/reality split | Yes | **Keep;** pair with an observation channel (§5.2) |
| $F_t$ | Yes | Yes | **Keep;** clarify it is the objective state, and give "feasible" formal content (§5.3) |
| $\hat F$ | Only with stochastic $D$ or menu variation (Prop 3.4) | Yes: discovery, unawareness, mistaken opportunities | **Keep,** with stated identification conditions |
| $V$ | Only when $D$ uses it | Yes: separates evaluation from selection | **Keep (optional);** fix signature (§4.1) |
| $H$ | No (Prop 3.1) | Only with attention evidence | **Revise:** parameter of $V$ |
| $D$ | Yes | Yes | **Keep** |
| $C$ | Yes | Yes: attempt vs result | **Keep** |
| $O_t$ | Yes | Yes | **Keep** |
| $O_{i,t}$ | No (Prop 3.2) | Notational convenience | **Revise:** define as projection of $O_t$ |
| $R$ | Yes | Yes | **Keep;** add constraint correspondence and population form |

---

## 4. Decision boundary

### 4.1 Typing errors in Model 5.1

**CE-13 (expectation operator has no measure). [Proof]** Model 5.1 writes
$\arg\max_{a\in\hat F}E[V(a\mid G,M,H)]$. $V$ already conditions on $M$, which holds the agent's beliefs. The outer $E$ therefore either (i) integrates a second time over the same subjective measure, which is redundant, or (ii) integrates over an objective measure, which would let the distribution of $F_t$ into $D$ and break the 5.1 Boundary. The consistent form is
$V(a\mid G,M,H)=\int u_{G,H}(a,s)\,\mu_M(ds)$ and $D=\arg\max_{a\in\hat F}V(a\mid G,M,H)$, where $\mu_M$ is the belief in $M$.

**CE-12 (menu-dependent valuation). [CE]** In the decoy effect (Huber, Payne and Puto 1982) and regret theory (Loomes and Sugden 1982), the value of $a$ depends on what else is available. $V(a\mid G,M,H)$ has no menu argument. A specification must either place the menu in $M$, which duplicates $\hat F$ against the "one primary location" rule, or move all menu effects into $D$, which is admissible but means $V$ cannot represent these valuations. Revision: either add $\hat F$ to $V$'s conditioning set or state explicitly that context effects belong to $D$.

**Lexicographic and incomplete preferences. [Proof]** Lexicographic order on $\mathbb R^2$ has no real-valued representation (Debreu 1954). Real-valued $V$ cannot carry it, so it must sit in $D$. This is admissible but should be stated, because §6.1 presents $V$ as where preferences live.

### 4.2 What the decision boundary gets right

The exclusion restriction of Prop 2.4 is TER's strongest contribution. [Judg] It is standard in POMDPs and Bayesian games, but TER states it as a modeling rule for all economic agents, and the test suite enforces it (`test_decision_feasibility_boundary_contract.py`, `test_reality_belief_boundary_contract.py`). It has empirical content: with measured $M$, any residual dependence of $C$ on $F_t$ falsifies the specification's $M$.

---

## 5. Information, feasibility, and realization boundaries

### 5.1 Pre-decision objective state is unnamed

**[Proof]** $F_t$ is "the objective state relevant when the selected action is realized". The objective state *at selection* has no name. The bank-run protocol delivers a capacity notice before choices lock. That notice is a signal about an objective condition realized at date 0. Canonically it can only be described as information about $F_t$ arriving before $C$. This works, but every specification must improvise the channel.

### 5.2 The observation channel is missing

**CE-16. [Proof]** The canon requires that outcomes affect $M$ "only through the information available to that agent" and that agents need not observe the full system outcome. Enforcing this requires a map $y_{i,t}=\sigma_i(F_t,O_t)$ from reality to what agent $i$ receives, and an update $M_{i,t+1}=U_i(M_{i,t},y_{i,t})$. The canon names neither. $\sigma_i$ cannot live in $M$ because it is a property of reality (what is delivered), and it is not in $F_t$ or $R$ by definition.

Consequence for compatibility: §7.8 claims compatibility with partially observable decision models. A POMDP has five essential parts: state, action, transition, reward, and **observation kernel**. TER names the first three only implicitly and lacks the fifth. The implementation already has the object (`research/ter/observation.py`), which suggests the theory is behind its own practice.

### 5.3 Feasibility has no formal content

**CE-6 (type mismatch: individual feasibility is joint). [CE, Verified]** The canon says $\hat F_{i,t}$ "may differ from what reality ultimately allows". $\hat F$ is a set of actions; $F_t$ is a state. To compare them, one needs an objective action set $A^*_i(F_t)$. In the bank-run protocol at $k=14/5$ with all three depositors tendering, the third served depositor receives $0$ against a claim of $7/5$. Whether patient 1's request is "realizable" depends on $C_{-1}$ and the queue, not on $F_t$ alone. So $A^*_i$ must be $A^*_i(F_t,C_{-i,t})$, which is not an agent-level object. TER's handling — failure appears in $O$ — is right. But it means the "$\hat F$ vs $F$" distinction is, formally, (i) the support restriction on $C$ plus (ii) the gap between what $M$ predicts $R$ will return and what $R$ returns. The canon's wording suggests a set-versus-set comparison that does not exist.

**CE-17 (R can create resources). [CE]** Take the structural bank with $b_0=3$. Define $R'$ that pays every early claimant $7/5$ and every waiter $2\cdot 3/|L|$. $R'$ is deterministic, takes only $(C,F_t)$, and is a "reality function" under every canonical clause, yet total payments exceed assets. The methodology says $R$ must be "substantive", but nothing in the canon requires $R$ to respect $F_t$'s constraints. The phrase "objective feasible state" implies a constraint correspondence $\Gamma:\mathcal F\rightrightarrows\mathcal O$ with $R(c,F)\in\Gamma(F)$ for every profile $c$. That restriction would give Axiom 7 testable content ("no action profile, however mistaken, yields an outcome outside $\Gamma(F_t)$") and make accounting identities part of the architecture. The structural benchmark proposed exactly this as a "ledger contract".

### 5.4 Realization boundary

**CE-9 (multi-period realization). [CE]** A firm invests $k$ at $t$; returns at $t+1,\dots,t+T$ depend on prices produced by later modeled actions. Model 5.2 writes $O_{i,t}=R(C_{i,t},F_t)$ with one index. Putting future prices in $F_t$ violates §3 ("conditions produced by modeled actions ... may become part of a *later* $F$"). The workable encoding stores installed capital in $F_{t+1}$ and realizes later income as $R(\text{no-action},F_{t+s})$. This is admissible, but it breaks the link "outcome associated with agent $i$'s selected action" and it means counterfactuals on $C_{i,t}$ require rerunning the whole path, not one $R$ call. The same issue arises for resting limit orders, which fill when *another* agent acts. TER can represent these only through a state-transition object it declines to name ("System State ... not a separate TER primitive").

**CE-10 (choosing Model 5.2 vs 5.3 depends on realized actions). [CE]** Two buyers, one unit in inventory. If each is realized with Model 5.2 against an $F_t$ holding one unit, both receive it. The canon says to use the joint $R$ "where an agent-level outcome depends on contemporaneous ... interactions", but whether the scarcity binds depends on whether both buy, which is known only after selection. Correct condition [Proof]: Model 5.2 is valid for agent $i$ iff the $i$-th projection of the joint $R$ is invariant to $C_{-i}$ over the support of the specification. That is a property of $R$ that should be declared in advance.

**CE-8 (psychological games). [CE]** In guilt aversion (Battigalli and Dufwenberg 2007), $A$'s realized payoff is $m_A-\gamma\max\{0,\;\mathbb E_{B}[m_A]-m_A\}$, where $\mathbb E_B$ is $B$'s *actual* belief. Realizing it requires $R$ to read $M_B$, which the methodology forbids. The alternatives both cost something: (a) treat $M_B$ as part of $F_t$ from $A$'s standpoint, which dissolves the agent-side/objective partition, since another agent's belief is an objective fact; or (b) keep only material outcomes in $O$ and move belief-dependent payoffs into $V$, which loses the realized payoff. TER needs an explicit rule for other agents' mental states as objective facts. The same issue arises for reputation, credit ratings, and sentiment-dependent contracts.

**CE-14 (one $F_t$ with intra-period sequencing). [CE]** Sequential service changes the bank's balance between servicing events at one decision point. The balance before the second payment is produced by the first payment. By §3 it cannot be in $F_t$. The correct canonical encoding keeps intermediate balances inside $R$. This is consistent, but it means $R$ may contain an internal state process, which the canon should say. The structural benchmark gets this wrong (§7.3).

---

## 6. Simultaneous equilibrium and market clearing

### 6.1 The structural problem

**[Proof]** Models 5.1–5.5 form a recursion per decision point:

$$
M_{i,t}\to C_{i,t}\to O_t=R(C_t,F_t)\to y_{i,t}\to M_{i,t+1}.
$$

Standard equilibrium concepts are fixed points *across* this recursion:

| Concept | Fixed point | Where TER stands |
|---|---|---|
| Nash | $C_i^*\in BR_i(C_{-i}^*)$; beliefs in $M_i$ equal $D_{-i}$'s output | beliefs must be set to the equilibrium in $M$ |
| Bayes–Nash | $M_i$'s belief over $(C_{-i},F)$ = law induced by $D_{-i}$ and the prior | cross-agent restriction on $M$ and $D$; no TER object states it |
| Rational expectations (Muth; Lucas) | subjective law in $M$ = objective law generated by $R$, $D$ and the $F$ process | links $M$ to $R$'s induced law; the methodology forbids building $R$ from $M$ but has no rule for the converse |
| Walrasian | $p^*$ such that $\sum_i x_i(p^*)=0$ | see §6.2 |
| REE with informative prices (Grossman 1976) | agents condition demand on $p$, which aggregates their private signals | price is an outcome at $t$ used by $D$ at $t$ |

The canon's Equilibrium definition ("actions and expectations ... consistent ... under the equilibrium concept being used") is the right *idea*, but it has no formal object. The methodology's rule "state whether equilibrium is embedded in R, emerges from repeated decisions, or is verified afterward" admits that TER has three external ways to handle it and no internal one.

### 6.2 Market clearing in practice

- **Faithful canonical encoding (works). [Proof]** Let $C_i$ be a demand schedule $x_i(\cdot)$, which §3 allows ("contingent strategy"). Let $R$ find $p^*$ with $\sum_i x_i(p^*)=0$ and allocate. The price is then part of $O_t$, consistent with §3. Uniform-price auctions and supply-function models also take this form.
- **Implemented encoding in `test_07` (outside the recursion). [Proof]** `evaluate_market` writes each hypothetical price into $M$, runs $D$, and `find_market_clearing_states` keeps prices where quantities match. This evaluates notional decisions at unrealized prices and imposes $M$-price $=$ realized price as a selection criterion. It is a rational-expectations fixed point computed outside TER. The test documents this honestly, but it is evidence that the architecture has no consistency operator.
- **REE with informative prices (CE-7). [CE]** In Grossman (1976), the equilibrium price function $P(s_1,\dots,s_n)$ must equal the one agents use to infer others' signals. With schedules, $C_i=x_i(\cdot;s_i)$ must embed beliefs about $P$, and those beliefs must equal the $P$ that $R$ produces from the schedules. That condition links $M_i$ to $R$'s output law at the same $t$. TER can check it but not state it.

### 6.3 Where TER is strong

**[Judg]** Disequilibrium and rationing models (Drèze 1975; Bénassy; Barro and Grossman 1971) fit TER more naturally than Walrasian ones: agents select quantities at believed prices, $R$ rations against objective supply, and the gap between attempted and realized trade is exactly TER's $C$/$O$ distinction. TER's claim "markets always clear is not assumed" (§8) is well supported by its architecture.

### 6.4 Consequence

**[Proof]** Any TER reproduction of an equilibrium model contains the equilibrium as a configuration input or an external computation, not as an output of Models 5.1–5.5. The bank-run protocol says this explicitly ("For each equilibrium, $D$ ... assigns probability only to maximizing actions"; "average the distinct equilibrium outcome distributions"). This is honest and consistent with the methodology's "configurations, not TER assumptions", but it limits §6.5's claim that markets and macro outcomes "may emerge from interacting agent decisions": in equilibrium models they are imposed, then verified.

---

## 7. Architecture B and the bank-run experiments

### 7.1 Independent verification

[Verified] With a standalone exact-arithmetic script (not importing repository code) for the protocol's contract — three depositors, $d=7/5$, $r=2$, uniform service permutation, early-liquidation cap $k$ — the patient payoff tables give:

| Information | Pure equilibria | Symmetric mixed $P(E)$ |
|---|---|---|
| $k=11/5$ | `WW` | none (waiting weakly dominant) |
| $k=14/5$ | `WW`, `EE` | $3/11$ |
| $k=3$ | `WW`, `EE` | $1/4$ |
| uniform prior over $k$ | `WW`, `EE` | $27/35$ |

These match the protocol and the archived results. The structural benchmark's table and $6/5$ guarantee bound also match its saved output.

### 7.2 What the experiments can and cannot show

**Proposition 7.1 (encoding invariance). [Proof]** If two architectures encode the same primitives — action sets, information structure, decision laws, realization law, transition law, and initial distribution — and both encodings are faithful, they induce the same joint law over histories. Every score that is a function of that law (Brier loss, equilibrium set, identified set) is identical. Equal losses with paired intervals $[0,0]$ are therefore implied before any data are generated. The results document states this ("Identical outcome laws imply this result").

Consequences:

1. The "prediction advantage" arm cannot, by construction, support either architecture. It is a parity check, not a test. [Proof]
2. The identification results come from randomized design (disclosure and capacity assignment), which is architecture-independent. They are correct and useful, but they say nothing about TER. [Proof]
3. The only arm that *could* discriminate — the specification-audit arm with independent reviewers — was not run. TER's plausible advantage is auditability. That remains **untested**. [Hyp]
4. An architecture's content is the set of specifications it **excludes**. None of the experiments presents a specification that one architecture admits and the other rejects. The informative comparison is between admissible classes (§9.6). [Judg]

### 7.3 Boundary errors in the experiment mappings

These are defects in non-canonical documents, measured against canonical definitions.

| Document | Mapping | Problem | Canonical rule |
|---|---|---|---|
| `architecture-adversarial-bank-run-structural.md` §3 | `F_t` includes "remaining balance before each sequential payment" | Balances after the first payment are produced by modeled actions at the same decision point | §3: such conditions "are realized as outcomes and may become part of a later $F$" |
| same, §3 | `H`: "whether the patient consumes at date 1 or 2" | Consumption date is a consequence of the action, not the set of consequences considered | §3 Time Horizon |
| `architecture-adversarial-bank-run.md` §3 | `V` computed "from the declared payoff table"; table "enters through $M$" | Correct, but the same table also defines `F_t`'s "stipulated payoff conditions", so `R` and `M` share one object; parity holds only because beliefs are assumed correct | methodology: one primary location per fact |
| protocol mapping A | $D$ "for each equilibrium ... assigns probability only to maximizing actions" | Equilibrium mixing probabilities sit in $M$ as imported beliefs; selection convention is external | §6.4 above |

None of these changes the numerical results, which are architecture-invariant (Prop 7.1).

### 7.4 Architecture B as a rival

**[Judg]** Architecture B's own text concedes its main weaknesses, and the experiments confirm them. Two of B's features are improvements TER should adopt: an explicit transition kernel $\mathcal Q$ and an explicit observation process. B's main loss is that it collapses $M$, $\hat F$ and $V$ into $I$, $A(I)$ and $\pi$, which forfeits the separately evidenced distinctions in Props 3.4 and 2.4. **Recommendation: reject B as a replacement; adopt its two structural maps into TER (§10).**

---

## 8. Compatibility with established models

| Model family | Maps into TER v0.5.0? | What must be added outside the canon |
|---|---|---|
| Consumer and producer choice under constraints | Yes | Budget as $\Gamma(F)$; otherwise nothing |
| Bounded rationality, heuristics, satisficing | Yes, natively | — |
| Consideration sets, unawareness | Yes, via $\hat F$ | Identification conditions (Prop 3.4) |
| Normal-form and extensive-form games | Yes as representation | Equilibrium as external consistency condition |
| Bayesian games, mechanism design | Yes; mechanism is an institution in $F$, designer's choice is a commitment $C$ | Common-prior and Bayes–Nash conditions are cross-agent restrictions TER cannot state |
| Psychological games | Only by boundary strain (CE-8) | Rule for other agents' beliefs as objective facts |
| Walrasian general equilibrium | Yes via schedules + clearing $R$ | Existence and fixed point are external |
| Rational-expectations macro (RBC, NK DSGE) | Partially | RE consistency; representative agent is an aggregation device, not a "coordinated group" (§3 Agent); Calvo reset opportunity placement is ambiguous ($F$, $\hat F$, or $D$) |
| Search and matching (DMP) | Yes; matching function in $R$ | Free-entry and Nash bargaining as consistency conditions |
| Disequilibrium, rationing | Yes, naturally | — |
| Stock-flow-consistent macro | Partially | Accounting identities need $\Gamma(F)$ (CE-17) |
| Continuum economies, mean-field games (Aumann 1964) | No as written (CE-11) | $R$ over an action distribution |
| Agent-based models | Yes, natively | Transition and observation maps |
| Heterogeneous-agent macro aggregation | Same limit as B | Lumpability / sufficiency condition (Kemeny and Snell 1960) |

**CE-11 (continuum of agents). [CE]** Model 5.3 writes $R(C_{1,t},\dots,C_{n,t},F_t)$ with finite $n$. In Aumann's (1964) atomless economy, no single agent affects prices, and core equivalence holds only in the limit. Finite-$n$ approximations retain market power at every finite size. The original Diamond–Dybvig model also uses a continuum. Revision: let the action profile be a measurable map $i\mapsto C_i$ on an agent measure space, so $R$ depends on the profile's distribution where agents are anonymous.

**Representation is not unification. [Judg]** Every family above can be *encoded* in TER, because TER's objects are general enough to encode any stochastic game with observation. The canon agrees (§7.10: representation is not validation). Unification has content only if TER's restrictions (Props 2.4, 2.5, joint $R$, observation-only updating, $\Gamma$) are shown to be satisfied by these models and *violated* by some economically mistaken specifications. That claim is plausible but has not been tested. [Hyp]

---

## 9. Proposed theoretical changes

**These are proposals. None is canonical. Each should be weighed against `theory/academic.md` and §7.10's rule that changes need theoretical necessity, evidence, contradiction, or demonstrated explanatory improvement.** Each item cites the finding that motivates it.

### 9.1 Replace the nine axioms with six restrictions and three definitions

Restrictions (each excludes some specification):

| ID | Restriction | Replaces | Motivated by |
|---|---|---|---|
| T1 Agent-side selection | $C_{i,t}=D_i(\hat F_{i,t},M_{i,t},\xi_{i,t})$; $\xi$ drawn agent-side; equivalently $C\perp F_t\mid(M,\hat F)$ | A1, A4 | Prop 2.4 |
| T2 Perceived support | $\operatorname{supp}C_{i,t}\subseteq\hat F_{i,t}$ | A2, A4 | Prop 2.6 |
| T3 Belief-free realization | $O_t=R(C_t,F_t)$ with no agent-side argument | A5, A7 | Prop 2.5 |
| T4 Constrained realization | $R(c,F)\in\Gamma(F)$ for every profile $c$ | A7 | CE-17 |
| T5 Joint consistency | agent outcomes are projections $\pi_i(O_t)$; Model 5.2 applies iff $\pi_i\circ R$ is invariant to $C_{-i}$ | 5.3 prose | Prop 3.2, CE-10 |
| T6 Observation-only updating | $M_{i,t+1}=U_i(M_{i,t},y_{i,t})$, $y_{i,t}=\sigma_i(F_t,O_t)$ | A9 (agent side), 5.5 prose | CE-16 |

Definitions (admissibility requirements, not empirical laws):

| ID | Definition | Replaces |
|---|---|---|
| Def-V | Valuation $V(a\mid\theta,M)=\int u_\theta(a,s)\,\mu_M(ds)$, with $\theta=(G,H)$ declared | A3 |
| Def-Φ | Objective transition $F_{t+1}=\Phi(F_t,O_t,\varepsilon_{t+1})$, with $\varepsilon$ exogenous shocks | A6, A9 (objective side) |
| Def-Viab | Persistence via viability (§9.4) | A8 |

**Independence of T1–T6. [Proof, sketch]** Each has a specification satisfying the other five and violating it: T1 — $D$ reads $F_t$ (clairvoyant agent); T2 — $C\notin\hat F$; T3 — $R$ reads $M$ (CE-8 encoded literally); T4 — CE-17; T5 — CE-10 with two Model 5.2 calls; T6 — $M_{t+1}$ set to the unobserved system outcome.

**Honest limit. [Proof]** Def-Φ alone has no empirical bite: since $O$ is unrestricted, setting $O_t:=(C_t,F_t)$ makes "endogenous change arrives through outcomes" vacuous. It is a bookkeeping requirement, as Architecture B concedes for its own transition axiom.

### 9.2 Add the observation channel

Name $\sigma_i$ (or require $O_t$ to contain agent-indexed observation components $y_{i,t}$). Also allow pre-decision signals $y^{\text{pre}}_{i,t}=\sigma^{\text{pre}}_i(F_t)$ so disclosure designs like the bank-run protocol have a canonical home. This makes TER's POMDP compatibility claim true and its information boundary checkable.

### 9.3 Give "feasible" formal content

Add $\Gamma:\mathcal F\rightrightarrows\mathcal O$. Then:
- the "objective feasible state" becomes the pair $(F_t,\Gamma)$;
- budget, resource, and accounting identities become declared parts of $\Gamma$;
- the agent-level objective feasibility that the canon gestures at can be *derived*: $a$ is objectively realizable for $i$ given $(F_t,C_{-i})$ iff $\pi_i(R(a,C_{-i},F_t))$ matches the intended execution of $a$. This states CE-6's joint dependence openly.

### 9.4 Formalize persistence and imbalance with viability theory

Let $K\subseteq\mathcal F$ be the states consistent with the "existing state" (for example, a currency peg holds). Following Aubin (1991):

- $\operatorname{Viab}(K)$: states from which **some** admissible profile of decision processes keeps the system in $K$.
- $\operatorname{Inv}_D(K)$: states from which the **current** profile $D$ keeps the system in $K$.

Then:
- **Infeasible continuation (Constraint 5.4):** $F_t\notin\operatorname{Viab}(K)$. Change is forced regardless of behavior.
- **Imbalance:** $F_t\in\operatorname{Viab}(K)\setminus\operatorname{Inv}_D(K)$. Continuation is possible, but current behavior leaves $K$.

This separates the two concepts the canon carefully distinguishes in prose (§3 Imbalance, §5.4), gives both testable content, and keeps the canon's position that imbalance does not by itself force correction. [Hyp: that this definition matches the canon's intended meaning of "pressures"; the canon's wording is not precise enough to confirm.]

### 9.5 Add an optional consistency condition (equilibrium)

An optional component parallel to Analysis 5.6:

> **Consistency 5.7 (optional).** A specification may impose a consistency condition $\mathcal E(M,D;R,\Phi,\sigma,\text{prior})$ linking agent-side objects to the law that the specification itself generates. Examples: Nash ($D_i$ best-responds to $M_i$'s belief, which equals $D_{-i}$); Bayes–Nash; rational expectations ($M_i$'s law equals the induced law); Walrasian clearing (as a property of $R$ over schedules). $\mathcal E$ restricts which configurations are studied; it never gives $D$ access to $F_t$ or $R$ access to $M$.

This states what the methodology already requires ("State the equilibrium concept and how it enters"), without making equilibrium a TER assumption, and it resolves the asymmetry in §6.1: $R$ is never built from $M$, but $M$ may be *required to match* $R$'s law.

### 9.6 Other targeted revisions

| Item | Proposal | Motivated by |
|---|---|---|
| Model 5.1 notation | Drop outer $E[\cdot]$ or define $V$ as state-contingent and $E$ under $\mu_M$ | CE-13 |
| $V$ signature | Allow $V(a\mid\hat F,\theta,M)$ or state that menu effects belong to $D$ | CE-12 |
| $G$, $H$ | Parameters $\theta$ of $V$; keep names, drop independent-object status | Props 2.3, 3.1 |
| $O_{i,t}$ | Define as $\pi_i(O_t)$ | Prop 3.2 |
| Model 5.3 | Action profile as a measurable map over an agent space | CE-11 |
| $R$ internals | State that $R$ may contain an intra-period sequence (queues, matching) and that intermediate states stay inside $R$ | CE-14 |
| Other agents' beliefs | State whether $M_j$ may be an argument of $R$ for $i$'s outcome (psychological payoffs), or restrict $O$ to non-mental outcomes | CE-8 |
| Multi-period realization | Allow outcomes of a $C_{i,t}$ to be realized at later points through $\Phi$ and attribute them explicitly | CE-9 |
| Necessity test | For each agent-side object, name an intervention class that moves it and not the others (information treatments → $M$; menu changes → $\hat F$; attention or framing of time → $H$) | Prop 3.3 |
| Architecture comparisons | Compare admissible classes: find specifications one architecture admits and the other rejects, and check which rejection is economically right | Prop 7.1 |

---

## 10. A smaller architecture that preserves TER's advantages

### 10.1 The kernel ("TER-K", proposal)

Primitives (seven): $F_t$, $\Gamma$, $M_{i,t}$, $\hat F_{i,t}$, $D_i$, $C_{i,t}$, $R$ (with output $O_t$).
Structural maps (two): $\sigma_i$ (observation), $\Phi$ (objective transition), with update $U_i$ as part of the agent's specification.
Optional: $V(\cdot\mid\theta,M)$ with $\theta=(G,H)$; consistency $\mathcal E$; analysis 5.6; viability sets.
Restrictions: T1–T6.

$$
\begin{aligned}
y_{i,t}&=\sigma^{\text{pre}}_i(F_t) &&\text{(pre-decision information)}\\
M_{i,t}&=U_i(M_{i,t-1},y_{i,t-1},y_{i,t})\\
C_{i,t}&\sim D_i(\hat F_{i,t},M_{i,t}),\quad\operatorname{supp}C_{i,t}\subseteq\hat F_{i,t}\\
O_t&=R(C_t,F_t)\in\Gamma(F_t)\\
y_{i,t}&=\sigma_i(F_t,O_t) &&\text{(post-realization information)}\\
F_{t+1}&=\Phi(F_t,O_t,\varepsilon_{t+1})
\end{aligned}
$$

### 10.2 Preservation check

| TER advantage | Preserved in TER-K? | How |
|---|---|---|
| Belief vs reality | Yes, strengthened | T1, T3 as conditional-independence restrictions |
| Perceived vs objective feasibility | Yes, stated precisely | T2 + $\Gamma$ + derived joint realizability (§9.3) |
| Valuation vs selection | Yes, where used | optional $V$ consumed by $D$ |
| Heterogeneous decision processes | Yes | $D_i$ unrestricted beyond T1–T2 |
| One joint realization | Yes, sharpened | T5 with a stated separability test |
| Outcome distinct from later state | Yes | $O_t$ vs $F_{t+1}=\Phi(\cdot)$ |
| Observation-only updating | Yes, now enforceable | $\sigma_i$, $U_i$ |
| Counterfactual replay | Yes | rerun $R$ on recorded $(C,F_t)$; multi-period via $\Phi$ |
| Methodological neutrality (§7.8) | Yes | no solution concept or method imposed |

### 10.3 What is lost or traded

- **Named $G$ and $H$.** They remain as declared parameters, so the pedagogical vocabulary survives; only their status as independent core objects goes. [Judg]
- **Symbol count does not fall** (eleven → seven primitives plus two maps). The reduction is in *independent* objects; the addition is formal content TER already needs. [Proof: Props 2.3, 3.1, 3.2 remove three; §5.2 and Def-Φ add two that dynamic specifications already require.]
- **Equivalence. [Proof, sketch]** Every TER v0.5.0 specification that declares its transition and information mechanisms (as the methodology already requires for dynamic specifications) maps into TER-K by setting $\theta=(G,H)$, $O_{i,t}=\pi_i(O_t)$ and $\Gamma(F)=\mathcal O$. The converse holds by reading the TER-K maps as the specification-level update rules the methodology permits. The two differ only where TER-K is stricter: T4 with nontrivial $\Gamma$, and T5's separability condition.

### 10.4 Is TER-K better than Architecture B?

**[Judg]** Yes on the evidence available. TER-K has B's two structural maps and keeps $M$, $\hat F$ and $V$ as separately evidenced objects, which B folds into $I$ and $\pi$. Whether those separations pay off empirically is the open question that only the unrun audit arm or an admissible-class comparison can answer.

---

## 11. Counterexample index

| ID | Short name | Exposes | Type | Section |
|---|---|---|---|---|
| CE-1 | Permission axioms satisfied by every spec | A2(2nd), A5, A6, A9 vacuous | Proof | 2.2 |
| CE-2 | A8 analytic | A8 has no content | Proof | 2.2 |
| CE-3 | $G:=\tilde V$ | $G$ not identified | Proof | 2.2 |
| CE-4 | Constant habit $D$ | A1 wording contradicts 5.1 | CE | 2.2 |
| CE-5 | Healthy-bank run | A7 "regardless of beliefs" false | CE | 2.2 |
| CE-6 | Third-in-queue at $k=14/5$ | individual feasibility is joint | CE, Verified | 5.3 |
| CE-7 | Grossman REE | consistency not expressible | CE | 6.2 |
| CE-8 | Guilt aversion | $R$ needs another agent's $M$ | CE | 5.4 |
| CE-9 | Multi-period investment, limit orders | single-index realization | CE | 5.4 |
| CE-10 | Two buyers, one unit | 5.2 vs 5.3 decided ex post | CE | 5.4 |
| CE-11 | Atomless economy | finite-arity $R$ | CE | 8 |
| CE-12 | Decoy, regret | menu-free $V$ | CE | 4.1 |
| CE-13 | $E[V(\cdot\mid M)]$ | ill-typed expectation | Proof | 4.1 |
| CE-14 | Sequential service | intermediate balances not in $F_t$ | CE | 5.4, 7.3 |
| CE-15 | Time-varying $D$ ≡ fixed $\tilde D$ on augmented $M$ | agent-side factorization not identified | Proof | 3.1 |
| CE-16 | Missing $\sigma_i$ | information boundary unenforceable; POMDP gap | Proof | 5.2 |
| CE-17 | $R$ pays all claims | no formal feasibility constraint | CE | 5.3 |

None of these shows TER is inconsistent in the strict logical sense. [Proof sketch: the one literal contradiction, A1 vs admissible habit rules, disappears under the "may depend" reading, at the cost of making A1 empty.] They show that TER's axioms are weak, that several canonical objects are dependent, and that dynamics, feasibility, information and equilibrium are under-formalized.

---

## 12. Keep, revise, reject

### 12.1 Axioms

| Axiom | Recommendation | Replacement |
|---|---|---|
| A1 | **Revise** | T1 (exclusion form) |
| A2 | **Reject as separate axiom** | merged into T2 |
| A3 | **Revise** | Def-V |
| A4 | **Keep** (merged) | T1 + T2 |
| A5 | **Revise** | T3 |
| A6 | **Reject** | corollary; keep as stated implication |
| A7 | **Revise** | T3 + T4 |
| A8 | **Reject as axiom** | Def-Viab; keep 5.4 formalized |
| A9 | **Revise** | T6 + Def-Φ |

### 12.2 Objects

| Object | Recommendation |
|---|---|
| $G$ | **Revise** → parameter of $V$ |
| $M$ | **Keep** + observation channel |
| $F_t$ | **Keep** + $\Gamma$; clarify "objective state" |
| $\hat F$ | **Keep** + identification conditions |
| $V$ | **Keep (optional)** + fixed signature |
| $H$ | **Revise** → parameter of $V$ |
| $D$ | **Keep** |
| $C$ | **Keep** |
| $O_t$ | **Keep** |
| $O_{i,t}$ | **Revise** → projection |
| $R$ | **Keep** + $\Gamma$, population form, internal sequencing |

### 12.3 Models

| Component | Recommendation |
|---|---|
| 5.1 | **Revise** notation (CE-13), menu dependence (CE-12) |
| 5.2 | **Revise**: declare separability condition (CE-10) |
| 5.3 | **Revise**: population form (CE-11), intra-period sequencing (CE-14) |
| 5.4 | **Revise**: viability formalization (§9.4) |
| 5.5 | **Revise**: functions $\Phi$, $\sigma_i$, $U_i$ (CE-16) |
| 5.6 | **Keep** |
| new 5.7 | **Add (optional)**: consistency condition (§9.5) |

### 12.4 Non-canonical documents (no edits made; for maintainers)

| File | Issue | Recommendation |
|---|---|---|
| `research/README.md` | $\hat F$ described as "what the agent believes is possible", against §3 "available to attempt" and the methodology's rule that low success probability stays in $\hat F$ | **Revise** wording |
| `research/README.md` | $H$ as "how far ahead the agent looks when it decides" — omits "relevant to valuation" and invites passing $H$ into $D$ | **Revise** wording |
| `architecture-adversarial-bank-run-structural.md` §3 | intra-date balances in `F_t`; `H` as consumption date | **Revise** mapping (§7.3) |
| `bank_run_identification/comparison.md` | correctly reports the tie; should state Prop 7.1 up front so readers do not take parity as evidence | **Revise** framing |
| Architecture B | as replacement | **Reject**; adopt $\mathcal Q$ and observation process |

---

## 13. Hypotheses that would change this verdict

1. **[Hyp] TER's decomposition improves error detection.** If the unrun audit arm shows reviewers catch timing, tender-vs-payment, and ledger errors more often in TER traces than in B or conventional traces, the methodological necessity of $M$/$\hat F$/$V$ gains direct support even though predictions tie.
2. **[Hyp] $\hat F$ is separately identified in field or lab data.** Awareness elicitation plus menu variation could show unperceived options behave differently from perceived-but-dominated ones. Failure would weaken $\hat F$'s case to that of $H$.
3. **[Hyp] $H$ is separable from discounting.** If attention or elicitation evidence shows horizon truncation distinct from low weights, $H$ earns independent status back.
4. **[Hyp] TER's restrictions have bite.** An admissible-class study (§9.6) that finds economically mistaken specifications admitted by B but rejected by TER-K would be the strongest available evidence for TER's architecture. Finding none would mean TER's distinctions are useful vocabulary rather than theory.

## 14. Limits of this review

- The reviewer read the canon, methodology, research README, Architecture B, both bank-run benchmarks, the identification protocol and results, and the market-clearing code. The Krugman (1980) reproduction and most numbered and contract tests were not reviewed in depth.
- Formal reading choices in §1 (real-valued $V$, $D$ into distributions, deterministic $R$) follow the canon and methodology where stated. Where the canon is silent, findings are stated conditionally on that reading.
- Proofs are short and standard. They have not been machine-checked. Only the bank-run equilibria were recomputed.
- No empirical evidence was gathered. Every claim about TER's practical value beyond formal structure is labeled as hypothesis or judgment.

## References

- Aubin, J.-P. (1991). *Viability Theory*. Birkhäuser.
- Aumann, R. J. (1964). Markets with a continuum of traders. *Econometrica* 32(1–2), 39–50.
- Barro, R. J., and Grossman, H. I. (1971). A general disequilibrium model of income and employment. *American Economic Review* 61(1), 82–93.
- Battigalli, P., and Dufwenberg, M. (2007). Guilt in games. *American Economic Review* 97(2), 170–176.
- Debreu, G. (1954). Representation of a preference ordering by a numerical function. In Thrall, Coombs and Davis (eds.), *Decision Processes*.
- Diamond, D. W., and Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy* 91(3), 401–419.
- Drèze, J. H. (1975). Existence of an exchange equilibrium under price rigidities. *International Economic Review* 16(2), 301–320.
- Geanakoplos, J., Pearce, D., and Stacchetti, E. (1989). Psychological games and sequential rationality. *Games and Economic Behavior* 1(1), 60–79.
- Grossman, S. J. (1976). On the efficiency of competitive stock markets where traders have diverse information. *Journal of Finance* 31(2), 573–585.
- Huber, J., Payne, J. W., and Puto, C. (1982). Adding asymmetrically dominated alternatives. *Journal of Consumer Research* 9(1), 90–98.
- Kemeny, J. G., and Snell, J. L. (1960). *Finite Markov Chains*. Van Nostrand.
- Loomes, G., and Sugden, R. (1982). Regret theory. *Economic Journal* 92(368), 805–824.
- Manzini, P., and Mariotti, M. (2014). Stochastic choice and consideration sets. *Econometrica* 82(3), 1153–1176.
- Masatlioglu, Y., Nakajima, D., and Ozbay, E. Y. (2012). Revealed attention. *American Economic Review* 102(5), 2183–2205.
- TER v0.5.0, `theory/academic.md`; `research/ter-methodology-notes.md`; `research/experiments/` as listed above.

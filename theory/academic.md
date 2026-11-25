# Theory of Economic Relativity

**Version:** 0.6.0

## Abstract

The Theory of Economic Relativity is a proposed unifying framework built on established economic principles. It organizes concepts such as scarcity, opportunity cost, marginal analysis, incentives, prices, supply and demand, externalities, institutions, and equilibrium within a common agent centered architecture.

The theory begins with a simple observation:

> Economic outcomes emerge from agent decisions interacting with reality.

An agent may be an individual, household, business, nonprofit, government, or organization. Although agents differ in objectives, information, constraints, and decision processes, their economic decisions can be represented through a common architecture: agents interpret reality through available information, act from the alternatives they perceive as feasible, and select actions through a decision process. Where valuation is used, objectives provide the reference against which actions are evaluated.

Outcomes emerge when those actions and interactions encounter the objective feasible state of reality, which may differ from what agents perceive as feasible, and may include external effects on other agents.

The central hypothesis is:

> Economic behavior emerges from agents selecting actions through decision processes shaped by their information, beliefs, and perceived feasible actions. Where valuation is used, agents evaluate actions relative to objectives and relevant time horizons. Selected actions then encounter reality and interact with other agents to produce outcomes. Those outcomes may alter the information, constraints, opportunities, valuations, institutions, and other conditions shaping future decisions and outcomes, allowing economic systems to evolve over time.

---

## 1. Introduction

Economics seeks to explain how decisions, institutions, and interactions produce economic outcomes. Over time, the field has developed a rich body of theory describing incentives, markets, information, institutions, strategic interaction, and the allocation of scarce resources.

Economic Relativity proposes a unifying framework centered on the agent.

Agents may differ substantially in their objectives, information, constraints, valuations, time horizons, and decision processes. Economic Relativity does not assume that they optimize or use a common decision rule.

Instead, it proposes that economically relevant decisions can be represented through a common architecture. Agents interpret conditions through their models of reality, act from alternatives they perceive as feasible, and select actions through decision processes (Section 3). Where valuation is used, objectives provide the reference against which actions are evaluated.

Those actions interact with actual conditions and with the actions of other agents to produce outcomes. The resulting outcomes may then alter information, constraints, opportunities, valuations, institutions, and subsequent decisions.

Economic Relativity therefore organizes established economic mechanisms within a common agent centered architecture while allowing heterogeneous behavior, interaction, and dynamic change across individuals, firms, institutions, markets, and broader economic systems.

---

## 2. Core Hypothesis

The central hypothesis of Economic Relativity is:

> **Economic behavior emerges from agents selecting actions through decision processes shaped by their information, beliefs, and perceived feasible actions. Where valuation is used, agents evaluate actions relative to objectives and relevant time horizons. Selected actions then encounter reality and interact with other agents to produce outcomes. Those outcomes may alter the information, constraints, opportunities, valuations, institutions, and other conditions shaping future decisions and outcomes, allowing economic systems to evolve over time.**

This hypothesis contains five core claims:

1. Economic behavior arises from agents selecting actions through decision processes.

2. Decision processes are shaped by information, beliefs, and perceived feasible actions; where valuation is used, objectives and relevant time horizons condition valuation.

3. The actions agents perceive as feasible may differ from what reality ultimately allows to be realized.

4. Outcomes emerge from agent actions and interactions encountering the objective feasible state of reality, and may include external effects.

5. Outcomes may alter the conditions shaping future decisions, causing economic systems to evolve over time.

## 3. Core Definitions

### TER Variables and Notation

The core TER symbols, their canonical names and roles, and the models that use them. Detailed definitions follow the table.

| Symbol | Canonical name | Concept / role | Used in |
|---|---|---|---|
| $G_{i,t}$ | Objective | Result or condition that provides the reference for valuation when valuation is used | 5.1, 5.5 |
| $M_{i,t}$ | Model of Reality | Agent $i$'s understanding of reality, including information, beliefs, assumptions, expectations, and interpretations | 5.1, 5.5 |
| $F_t$ | Objective Feasible State of Reality | TER's representation of the objectively realized conditions and constraints relevant when selected action(s) at decision point $t$ are realized; not agent specific | 5.2, 5.3, 5.5 |
| $\hat{F}_{i,t}$ | Perceived Feasible Set | Actions agent $i$ perceives as available to attempt at $t$ | 5.1, 5.2, 5.5 |
| $V_{i,t}$ | Valuation | Evaluates actions relative to the agent's objective, given its model of reality and time horizon | 5.1, 5.5 |
| $H_{i,t}$ | Time Horizon | Which future consequences agent $i$ considers relevant to valuation | 5.1, 5.5 |
| $D_{i,t}$ | Decision Process | Process through which agent $i$ selects among perceived feasible actions; it may condition directly on the agent's model of reality and may use valuation when applicable | 5.1, 5.5 |
| $C_{i,t}$ | Selected Action | Action agent $i$ selects from its perceived feasible set | 5.1, 5.2, 5.3, 5.5 |
| $O_{i,t}$ | Realized Outcome | Agent $i$'s realized outcome at $t$, which may follow an earlier selected action. Interaction-dependent outcomes come from the same joint $R$ as $O_t$. | 5.2, 5.3, 5.5 |
| $O_t$ | System Outcome | Realized system outcome produced by interacting selected actions encountering $F_t$ | 5.3, 5.5 |
| $R(\cdot)$ | Reality Function | Maps the selected action(s) and the relevant objectively realized state $F_t$ to the realized outcome; its arguments depend on model scope | 5.2, 5.3, 5.5 |

Where:

- $i$ identifies the agent.

- $t$ indexes the relevant decision point or time in the specification; depending on the model, it may represent a period, stage, round, event, or other decision point.

- $a$ represents a potential action.

Model 5.1 specifies selection from the perceived feasible set, with valuation when used. Models 5.2 and 5.3 specify what the selected actions realize under objective conditions.

### Agent

A decision making entity that selects among actions it perceives as feasible.

An agent may be an individual or a coordinated group of agents acting toward one or more objectives.

Examples include individuals, households, businesses, nonprofits, governments, and institutions.

### Institution

A structure or system of agents organized through rules, relationships, or common functions that shapes individual and collective action.

Institutions may both act as agents and alter the information, incentives, and perceived feasible sets of other agents. The laws, rules, and other institutional conditions that constrain what can occur are aspects of $F_t$, and institutional change may alter them.

### Objective

A result, state, or condition that provides the reference for valuation when valuation is used.

Examples include profit, survival, growth, security, happiness, stability, market share, or social welfare.

### System

A set of interacting agents, institutions, conditions, and relationships considered together for analysis.

The boundary of a system depends on the level of analysis.

### System State

The specification of the economically relevant properties of a modeled system at a given time. The contents of a system state depend on the specification and are not a separate TER primitive.

### Information

The facts, signals, observations, and other inputs available to an agent when making a decision.

Information may be incomplete, inaccurate, or interpreted differently by different agents.

### Model of Reality

An agent's internal understanding of reality, formed from its information, beliefs, assumptions, expectations, and interpretations.

An agent's model of reality may differ from reality and may change as new information and outcomes are observed. Decision relevant memory or learned state may be represented in $M_{i,t}$ and may inform either valuation or selection according to the mechanism being modeled.

### Constraints

The limitations that determine what can occur, including time, resources, technology, laws, institutions, access, authority, and physical conditions. Constraints are aspects of $F_t$.

### Objective Feasible State of Reality

$F_t$ represents the objective feasible state of reality relevant when the selected action or actions at decision point $t$ are realized: the objectively realized conditions and constraints that determine what can occur at realization.

It includes prevailing conditions, resources, capabilities, institutions, market and environmental conditions, shocks, and other objective constraints. These are aspects of $F_t$, not separate core variables.

$F_t$ refers to objective conditions shared at the relevant stage, although those conditions can affect agents differently. An agent may know some of them through available information. A researcher specifies which conditions matter and may only approximate them. Expectations about unresolved conditions belong in $M_{i,t}$. If a relevant condition resolves after selection but before realization, its realized value belongs in $F_t$. Conditions produced by modeled actions or interactions enter as realized outcomes and may become part of a later $F$.

### Perceived Feasible Set

The set of actions an agent perceives as available to attempt for the decision at $t$, whether or not each action is actively evaluated by the decision process. The actions in the set are its perceived feasible actions.

The perceived feasible set may differ from what reality ultimately allows to be realized, for example when an agent perceives constraints imperfectly. Beliefs represented in $M_{i,t}$ may shape $\hat{F}_{i,t}$, but $M_{i,t}$ represents the agent's broader understanding of reality while $\hat{F}_{i,t}$ records perceived action availability.

### Decision Process

The process through which an agent selects among perceived feasible actions, given its model of reality.

A decision process may involve optimization, satisficing, heuristics, habits, intuition, reflexive responses, strategic reasoning, stochastic selection, or other mechanisms. It may condition directly on the agent's model of reality and may use valuation when applicable. It need not produce an objectively optimal action.

### Selected Action

The course of action an agent selects from its perceived feasible set at a decision point, denoted $C_{i,t}$. In some specifications, the selected action may itself be a commitment, contract, policy, or contingent strategy whose consequences or prescribed actions unfold over later decision points.

Examples of actions include buying, selling, saving, hiring, investing, regulating, producing, consuming, delaying, committing, contracting, or adopting a policy. Later actions taken under a prior commitment remain subsequent selected actions at their own decision points.

### Valuation

The valuation, $V_{i,t}$, assigns value to actions relative to the agent's objective, given its model of reality and time horizon. $V_{i,t}(a \mid G_{i,t}, M_{i,t}, H_{i,t})$ denotes the value assigned to action $a$. Valuation need not be conscious or exhaustive, and a decision process need not consult it for every selected action.

### Time Horizon

The period over which an agent considers future consequences relevant to valuation.

A time horizon may range from immediate outcomes to consequences extending years, generations, or beyond the agent's lifetime. A nonprospective decision process that does not use valuation need not actively use $H_{i,t}$ in selection.

### Realized Outcome and System Outcome

The realized result of agent actions and interactions encountering the objective feasible state of reality, which may include external effects. $O_{i,t}$ is the outcome for agent $i$ at $t$. It may follow from an action selected at that decision point or from an earlier action, such as a standing order that fills later. $O_t$ is the system outcome of explicitly modeled interacting actions (Model 5.3).

### External Effect

A consequence of an agent's action experienced by other agents that is not fully internalized by the originating agent's decision process.

### External Shock

An event or change originating outside the modeled system boundary that alters relevant conditions, actions, or outcomes.

An external shock is not a separate core variable. Where a shock alters objectively realized conditions or constraints, it is represented as a change in $F_t$, which may occur independently of realized outcomes generated within the modeled system.

What constitutes an external shock depends on the boundary of the model. A change external to one modeled system may result from the actions of agents in a broader system. External shocks are distinguished from external effects by origin: a shock enters from outside the modeled system boundary, while an external effect arises from an action within the modeled system and is experienced by others.

Examples include pandemics, natural disasters, wars, and sudden technological or resource disruptions.

### Imbalance

A state in which existing actions, conditions, or relationships create pressures that reduce the ability of the current system state to persist under reality's constraints.

An imbalance may persist, grow, diminish, or be resolved as agents, institutions, and conditions change. Its presence does not by itself establish that a system is unstable or predict when the existing state will cease to persist.

### Equilibrium

A condition in which the modeled agents’ actions and expectations are consistent with each other under the equilibrium concept being used. Different equilibrium concepts impose different requirements on beliefs, feasible alternatives, and deviations. Equilibrium does not by itself imply stability, optimality, permanence, or desirability.

### Reality

The objective world itself, whose conditions constrain what selected actions can realize. Beliefs and expectations may change consequences through the actions they shape.

Reality is not a TER variable. $F_t$ is TER's representation of reality's objectively realized conditions and constraints relevant at realization (see Objective Feasible State of Reality). TER does not assume that the evolution of reality is fundamentally deterministic or stochastic; such assumptions belong to the scientific and economic specification being studied.

## 4. Axioms

### Axiom 1: Agent Selection

An acting agent's decision process selects an action from its perceived feasible set. Selection uses permitted agent-side inputs, including available information as represented in the agent's components. The decision process has no direct access to $F_t$. It may use the agent's model of reality directly and may consult valuation. When used, valuation evaluates actions relative to the agent's objective, given its model of reality and relevant time horizon. Choice can be stochastic, habitual, or nonoptimizing.

### Axiom 2: Objective Realization

The reality function determines the realized consequences of selected actions under the objective conditions and constraints relevant to their realization. Its inputs are the selected actions and those objective conditions. Realization may differ from what an agent intended or expected and can produce external effects. Where actions jointly determine consequences, the same joint realization supplies the system outcome and the interaction-dependent agent outcomes.

### Axiom 3: Dynamic Feedback

Realized outcomes may change later objective conditions and agent-side components, including those of other agents. Modeled actions change later objective conditions through their realized consequences. External shocks may change those conditions outside that pathway. An outcome can affect an agent's model of reality only through information available to that agent. The objective transition and agent-side updates are distinct.

### Axiom 4: State Persistence

An existing system state can persist unchanged only while its continuation is objectively feasible.

## 5. Formal Architecture

Section 3 defines the TER variables. The following models and constraint specify their relationships. Auxiliary objects used to describe individual specifications are not TER primitives.

- **Model 5.1, Agent Decision Model:** how an agent selects an action.

- **Model 5.2, Action to Outcome Model:** the agent-level outcome of a selected action.

- **Model 5.3, Multi Agent Model:** the system outcome of explicitly modeled interacting actions.

- **Constraint 5.4, State Persistence Constraint:** whether an existing system state can continue.

- **Model 5.5, Dynamic Feedback Model:** how realized outcomes may alter later conditions.

- **Analysis 5.6, Feedback Analysis and Stability:** optional analysis of a specified dynamic model.

- **Section 5.7, Equilibrium Consistency:** optional conditions for a specified equilibrium concept.

### 5.1 Agent Decision Model

For each acting agent $i$, declare an action space $\mathcal A_{i,t}$ and a nonempty perceived feasible set $\hat F_{i,t}\subseteq \mathcal A_{i,t}$. The decision process $D_{i,t}$ maps admitted tuples of agent-side inputs to actions in $\mathcal A_{i,t}$, with the restriction

$$
C_{i,t}=D_{i,t}(\hat F_{i,t},M_{i,t},v_{i,t};u^D_{i,t})\in\hat F_{i,t}.
$$

When valuation is used, $v_{i,t}=V_{i,t}(\cdot\mid G_{i,t},M_{i,t},H_{i,t})$ is the valuation on the declared action domain with the score space used by the specification. Omit $v_{i,t}$ where the decision process does not consult valuation. $G_{i,t}$ and $H_{i,t}$ condition valuation when used. $M_{i,t}$ may condition valuation and selection through distinct mechanisms.

The draw $u^D_{i,t}$ is optional. A stochastic specification may provide a decision kernel directly, assigning probability one to the measurable perceived feasible set for each admitted choice context. Declare the law of any shared decision randomization and what each agent can observe. $D_{i,t}$ can use only the inputs available at selection through the agent's own components and permitted draws. Holding those inputs and the chosen rule fixed, varying a hidden realization condition leaves selection unchanged. The restriction is on the mechanism's inputs and does not assert statistical independence between choices and objective conditions.

Optimization is one possible decision rule. For a scalar score $v_{i,t}(a)$, a maximizing rule selects an element of $\arg\max_{a\in\hat F_{i,t}}v_{i,t}(a)$. Specify conditions for a maximum and how selection resolves ties. If the score is an expectation of state-contingent consequences, specify the probability law represented in $M_{i,t}$ and conditions for the expectation to exist. A score already evaluated as an expectation enters the comparison directly. Habits, heuristics, satisficing, strategic rules, and other decision processes use the same selection boundary.

### 5.2 Action to Outcome Model

For an agent-level specification, declare the domain $\mathcal F_t$ of objective realization conditions and the outcome space $\mathcal Y_t$. The reality function $R$ maps admitted pairs $(c,f)$ in $\mathcal A_{i,t}\times\mathcal F_t$ to $\mathcal Y_t$:

$$
O_{i,t}=R(C_{i,t},F_t).
$$

Admitted inputs include attempts that can fail or partially execute. Record the original selected action and the outcome delivered by the mechanism. This model applies when other agents' actions are outside the scope of explicit joint determination at that stage. Earlier events caused by other agents may enter as objective conditions in $F_t$.

Each specification states the relevant admissible inputs and outcome constraints, such as budgets, resource limits, or settlement rules. If $K_t(c,f,y)$ denotes the applicable constraints on a proposed outcome $y$, require $K_t(c,f,R(c,f))$ for every input pair admitted by the specification, including any pairs admitted for replay. Specify those constraints independently of the computed result. The symbol $K_t$ expresses a model-specific check.

The stage index $t$ pairs the action with its realization conditions. Selection and realization can occur at different times. An objective draw that resolves by realization, such as a service order unknown at choice, can be recorded in $F_t$. At fixed selected actions and $F_t$, $R$ has no additional agent-side inputs. This boundary allows uncertainty in how the conditions arise.

For a fixed-state counterfactual, first reproduce the factual outcome using the recorded actions and $F_t$. Change only the action or actions under study. For a stochastic specification, retain the realized inputs or the coupling required for that replay. A change to an earlier decision can alter later actions and conditions. Evaluate that path with the dynamic specification in Model 5.5.

### 5.3 Multi Agent Model

For explicitly modeled interaction, declare the profile space $\mathcal C_t$ of included actions. In a finite model it is a subset of the product of the included agents' action spaces. Other population domains require the structure used by the specification, such as measurability and integrability for a continuum aggregate. Agents without a decision at a stage make no new selection. An explicit no-action may itself be selected where the specification requires it.

One joint $R$ maps admitted pairs in $\mathcal C_t\times\mathcal F_t$ to a joint realized result $Y_t$ in the declared outcome space $\mathcal Y_t$:

$$
Y_t=R(\mathbf C_t,F_t),\qquad
O_t=P_{\mathrm{sys}}(Y_t),\qquad
O_{i,t}=P_i(Y_t)\ \text{where an individual outcome is specified}.
$$

Here $\mathbf C_t$ collects the included actions. $Y_t$ and the readouts $P_{\mathrm{sys}}$ and $P_i$ are specification notation. An individual readout can record a consequence to an agent without a new action, such as a fill of its standing order. The system outcome may be the full joint result or a coarser record. TER defines no general aggregation of individual outcomes into $O_t$. Where a reduction to Model 5.2 is claimed for an individual readout, it must be invariant to variations in companion actions at fixed $C_{i,t}$ and $F_t$ on the declared query domain. Then the readout can be written as a function of those two inputs.

The included actions encounter the same objective conditions, which may affect agents differently. Apply the outcome constraints in Model 5.2 to the joint result. Settlement may contain internal steps, such as serving an already fixed queue from one opening balance. When later agents act on information received during a sequence, represent those choices at later decision points. Joint consequences may include external effects and may create or restrict opportunities such as exchange, cooperation, and specialization.

### 5.4 State Persistence Constraint

Let $s_t$ denote the system state whose persistence is being assessed, with equality evaluated on the economically relevant properties. Declare a nonempty set $\mathcal T_t$ of later times in the continuation interval. In Model 5.5, $S_t$ denotes the opening objective system state and $T_t$ denotes the objective transition rule.

Write $\operatorname{CanContinue}_t(s_t;\mathcal T_t)$ for the feasibility of unchanged continuation over the interval. Evaluate it using the relevant objective conditions and constraints throughout that interval, specified independently of the proposed path. This evaluation can require conditions beyond those relevant to realization at $t$. Then

$$
\neg\operatorname{CanContinue}_t(s_t;\mathcal T_t)
\quad\Longrightarrow\quad
\neg\bigl(s_u=s_t\ \text{for every }u\in\mathcal T_t\bigr).
$$

The implication restricts admissible paths, including in a stochastic specification. The transition mechanism determines what follows, including whether a state can recur after a change. An imbalance may persist, grow, diminish, or resolve while continuation remains feasible. An imbalance alone establishes neither infeasibility nor the timing or direction of change.

### 5.5 Dynamic Feedback Model

A dynamic specification declares its initial states, event order, observations, and transition rules. Let $S_t$ denote its opening objective system state and $B^-_{i,t}$ and $B^+_{i,t}$ collect the existing agent-side components $(G,M,\hat F,V,H,D)$ at selection and after the stage's updates. Let $Y_t$ denote the realized result, either the joint record from Model 5.3 or the agent outcome from Model 5.2. These symbols and the maps below describe the specification.

An observation rule $\sigma^\pm_{i,t}$ maps the relevant dated event record $\mathscr E_{\le d^\pm_{i,t}}$ at delivery time $d^\pm_{i,t}$ into information $L^\pm_{i,t}$ available to agent $i$. Use a pre-choice delivery where one occurs, and post-event delivery for information that arrives later:

$$
L^-_{i,t}=\sigma^-_{i,t}(\mathscr E_{\le d^-_{i,t}}),\qquad
B^-_{i,t}=U^-_{i,t}(B^+_{i,t-1},L^-_{i,t}).
$$

Realization uses $F_t=\rho_t(S_t,\xi_t)$, where $\xi_t$ denotes any additional objective inputs resolved by realization. The objective transition and the later agent-side updates are

$$
S_{t+1}=T_t(S_t,F_t,Y_t;\varepsilon_{t+1}),\qquad
L^+_{i,t}=\sigma^+_{i,t}(\mathscr E_{\le d^+_{i,t}}),\qquad
B^+_{i,t}=U^+_{i,t}(B^-_{i,t},L^+_{i,t}).
$$

Declare the domains of the state and event records, the delivered information spaces, and the permitted inputs to each map. $\rho_t$ returns a condition in $\mathcal F_t$, $T_t$ returns a state in the declared space for $S_{t+1}$, and the update functions return agent-side tuples in their declared spaces. The first selection uses the initialized local state and any information then available. Specify stochastic maps by their kernels or by conditioning on declared draws, with their timing and dependence. The observation mechanism can use only events available to it at delivery. Agent-side updates use what the agent actually receives or otherwise has available, which can include own actions, noisy reports, and retained local state. Declared internal changes such as habituation can occur without observing the system outcome. A channel may be inactive, and a state may carry forward unchanged.

$Y_t$ records what happened. $S_{t+1}$ records the resulting objective state, with $\varepsilon_{t+1}$ representing any declared outside inputs. If a modeled action changes subsequent objective conditions, identify the realized event that transmits the effect. For example, acceptance of a limit order creates a standing instruction. The transition carries it forward, and a later joint realization can fill it against an incoming order. The fill is a later consequence of the recorded instruction. It does not create a new selection by the owner unless the owner actually makes one. An enforceable commitment may change later objective constraints. A perceived or nonbinding commitment may instead change agent-side components through the specified mechanisms.

An outcome may affect the same agent, other agents, or later objective conditions through these paths. At the next relevant choice, Model 5.1 uses the updated agent-side components. The next realization uses the objective conditions then relevant.

### 5.6 Feedback Analysis and Stability

**Optional analytical methods.** This section is not a TER primitive or a required model. TER does not require one universal mathematical representation of feedback dynamics; the strength, structure, and consequences of the relationships in Model 5.5 may be analyzed using methods appropriate to the TER specification being studied.

Feedback may differ in:

- **sensitivity:** how strongly one component responds to another

- **amplification:** whether changes become larger through feedback

- **damping:** whether changes diminish over time

- **propagation:** how changes spread across agents or the system

- **persistence:** how long effects remain significant

- **oscillation:** whether responses repeatedly change direction

- **threshold effects:** whether sufficiently large changes produce different behavior

- **changing feedback regimes:** whether the feedback relationships themselves change as conditions change

When appropriate, the economically relevant variables and conditions of a particular TER specification may be collected into an analytical state vector:

$$

\mathbf{Z}_t

$$

and represented through a model-specific law of motion:

$$

\mathbf{Z}_{t+1}

=

\Phi_t(\mathbf{Z}_t)

$$

Here, $\mathbf{Z}_t$ and $\Phi_t$ are analytical constructions defined by the particular specification.

When the specified relationships are differentiable, their local response structure may be analyzed using a Jacobian:

$$

\mathcal{J}_t

=

\frac{\partial \Phi_t}{\partial \mathbf{Z}_t}

$$

For a sufficiently small change:

$$

\Delta \mathbf{Z}_{t+1}

\approx

\mathcal{J}_t \Delta \mathbf{Z}_t

$$

Where a locally time invariant approximation around a fixed point is appropriate, the eigenvalues of the Jacobian may be used to characterize local stability. In a discrete time model, deviations diminish locally when all relevant eigenvalues lie strictly inside the unit circle, while an eigenvalue outside the unit circle indicates local instability. Negative real eigenvalues may produce alternating responses, while complex eigenvalues may produce oscillatory responses.

These analytical methods are conditional on the structure of the model being studied. They do not imply that an entire economic system is globally stable or unstable.

Many economic systems may be stochastic, nonlinear, discontinuous, strategic, path dependent, or otherwise unsuitable for local Jacobian analysis in a particular specification. In those cases, feedback and stability may be studied through simulations, agent based models, econometric estimation, finite changes, regime specific analysis, sequence space methods, or other appropriate analytical and empirical methods.

Importantly, amplification alone does not imply instability or imbalance. Strong feedback may accompany productive growth, technological adoption, coordination, speculation, adaptation, or destabilization. Its economic significance depends on the underlying agents, conditions, interactions, constraints, and whether the resulting path remains feasible under reality's constraints.

### 5.7 Equilibrium Consistency

When a specification studies equilibrium, declare the candidate configurations and the conditions that define the source model's equilibrium concept. These can include feasibility, optimality against admitted deviations, or consistency of expectations with the law induced by the specified mechanisms. Each condition applies on the histories or information sets required by that concept. For example, an informative-price model may require beliefs conditional on the agent's signal and received price to match the corresponding law under the equilibrium price function. Solving the conditions simultaneously establishes consistency. Any price treated as observed when an agent selects must reach the agent through a specified pre-choice information path.

For a declared candidate domain $\mathcal W$ and consistency predicates $Q_j$, the equilibrium set is

$$
\mathcal E=\{w\in\mathcal W: Q_j(w)\ \text{holds for every declared condition }j\}.
$$

It may be empty or contain several configurations. A single equilibrium prediction in the latter case requires a specified selection rule. When an institution clears submitted bids or schedules, its rule belongs in the joint $R$. An analyst can also solve simultaneous consistency conditions without specifying an institutional clearing rule or a path to equilibrium. Convergence, stability, optimization, and market clearing are properties to establish where relevant to the specification.

## 6. Consolidated Principles

This section interprets the TER architecture through established economics. Sections 3–5 give the definitions, axioms, and formal models.

### 6.1 Agent Objective

Objectives provide the reference for valuation (Section 3), which a decision process need not consult for every selected action.

Many established economic concepts describe different forms of this process. Utility and preferences describe how consumers value alternatives. Profit maximization describes firms evaluating actions relative to profit. Incentives change the relative value of potential actions, while expected value provides one way agents may evaluate actions under uncertainty.

The same architecture can represent consumers pursuing utility, firms pursuing profit, governments pursuing stability, or other agents pursuing different objectives without requiring them to use the same decision process.

Because value is relative to the agent's objective, the same action, resource, or outcome may have different value to different agents, or to the same agent pursuing a different objective.

### 6.2 Feasibility and Constraints

Scarcity is a fundamental source of constraints. Limited resources such as time, capital, labor, technology, and natural resources restrict what an agent can actually do. Budget and production constraints are specific examples of these limits.

Constraints are represented in $F_t$, while information and beliefs shape what agents perceive as feasible (Models 5.1 and 5.2). What agents perceive as available to attempt and what reality ultimately allows to be realized may differ, and both may change over time.

Choosing among competing alternatives creates opportunity costs. Because agents face different resources, capabilities, and constraints, they may also face different opportunity costs. These differences can create comparative advantage and opportunities for mutually beneficial trade.

Interactions with other agents can also change what is feasible, through the outcomes they produce. Cooperation, exchange, specialization, and institutions may expand or restrict the actions available to an agent. Institutions can further shape what is feasible through laws, rules, property rights, contracts, and other structures that form part of $F_t$.

### 6.3 Agent Model of Reality

Agents may use a model of reality, $M_{i,t}$ (Section 3), that differs from objective conditions (Axioms 1 and 2). Information economics, expectations, behavioral economics, bounded rationality, and learning describe different aspects of how agents form, use, and update this model.

$M_{i,t}$ may inform valuation through $V_{i,t}$ and may also directly condition selection through $D_{i,t}$ (Model 5.1). Neither the agent's model of reality nor its perceived feasible set must perfectly correspond to reality.

This distinction allows Economic Relativity to represent both highly informed and imperfect decision making. An agent may have incomplete information, incorrect beliefs, biased expectations, limited ability to evaluate alternatives, or an inaccurate understanding of what actions are available.

Valuation and decision processes may also be shaped by reference points, framing, heuristics, biases, and subjective beliefs. Bounded rationality and behavioral effects therefore operate within the agent's decision architecture rather than as exceptions to it.

Outcomes can provide new information that changes the agent's model of reality. Those changes may also affect the actions the agent perceives as feasible, but TER does not require changes in perceived feasibility to occur through a single pathway.

Learning does not require convergence toward perfect knowledge. Agents may update correctly, incorrectly, partially, or not at all.

### 6.4 Action Selection

Different agents, or the same agent under different conditions, may use different decision processes (Section 3, Model 5.1). A decision process may condition directly on the agent's model of reality, may use valuation, or may use both for distinct roles, and the selected action need not be objectively optimal (Axiom 1).

Marginal analysis remains an important special case of valuation. Agents may evaluate expected marginal benefits and marginal costs when assigning value to alternatives; $D_{i,t}$ may then optimize over those values or select through another mechanism.

Because action selection may use valuation or condition directly on the agent's model of reality, the considerations driving the selected action may differ from the consequences ultimately realized.

### 6.5 Outcomes and System Effects

Economic outcomes emerge from the actions and interactions of agents encountering the objective feasible state of reality (Model 5.3). As agents affect one another, individual decisions can contribute to market and system level outcomes that no single agent determines independently.

Supply and demand describe aggregate patterns generated by buyers and sellers making individual decisions. Their interactions produce prices and quantities, while those prices become information and conditions that influence subsequent decisions.

Externalities are external effects (Section 3). Individually selected actions may therefore produce outcomes that conflict with the objectives of other agents or the broader system. When such outcomes are inefficient relative to a specified welfare criterion, economics may describe them as market failures.

Because agents and markets are interconnected, changes in one part of an economic system can alter the information, constraints, opportunities, and decisions of agents elsewhere. General equilibrium studies these interdependencies, while macroeconomic aggregation examines how individual actions and interactions contribute to economy wide outcomes.

System outcomes also feed back into future agent decisions (Model 5.5). Prices, employment, production, income, institutions, and other aggregate conditions may change what agents know, what they can do, what time horizons they consider relevant, how they value alternatives, and how subsequent decisions are made.

Within TER specifications, markets and macroeconomic outcomes need not be treated as independent starting points. They may emerge from interacting agent decisions and the conditions under which those decisions occur, while the resulting system outcomes may become part of the conditions shaping future decisions.

Institutions participate in this feedback process. They may emerge from agent interactions and collective action. They also shape the information, incentives, and perceived feasible sets that influence later decisions and outcomes, and form part of the objective feasible state of reality. Agents may act to create, preserve, modify, or remove institutions, and the outcomes of those actions may further change the conditions faced by themselves and others.

### 6.6 Persistence and Change Over Time

Economic systems evolve as agents respond to changing outcomes, information, constraints, institutions, time horizons, and external shocks.

Changes in these conditions may alter actions, beliefs, constraints, or interactions so that the equilibrium consistency condition being applied no longer holds (Section 3). The actions and conditions that sustain an equilibrium may themselves alter the relationships on which that equilibrium depends, allowing stability to generate endogenous change or instability over time.

An imbalance does not by itself establish that continuation is infeasible or predict when change will occur (Section 3, Constraint 5.4). External shocks (Section 3) and feedback (Model 5.5, Section 5.6) can also drive change.

Productivity, technology, capital, knowledge, cooperation, and institutional change can transform what agents and systems are capable of achieving. Growth can therefore involve changes in $F_t$, while learning can reveal actions that reality already allowed to be realized but the agent had not perceived.

Economic systems therefore do not necessarily move toward a single optimal or permanent equilibrium. They evolve as agents, institutions, conditions, outcomes, and reality interact over time.

## 7. TER Contributions and Claims

The Theory of Economic Relativity (TER) is proposed as a general framework for describing economic decision making, interaction, and change.

TER incorporates established findings from economics, including constrained choice, marginal analysis, bounded rationality, asymmetric information, strategic interaction, institutions, externalities, heterogeneous agents, feedback, and dynamic adjustment. TER does not claim these underlying concepts as novel.

Its central contribution is the hypothesis that these mechanisms can be organized within a common agent centered architecture and applied consistently across different economic problems, agents, and levels of analysis.

Consistent with this architecture, TER's analytical scope is:

> **TER studies how economic agents make decisions, how their actions interact with other agents and reality's constraints, and how the resulting outcomes shape economic systems over time.**

This scope does not reject scarcity based approaches to economics. Scarcity remains a fundamental source of constraints, tradeoffs, and opportunity costs within economic systems. TER's broader scope also includes information, beliefs, institutions, strategic interaction, external effects, feedback, and dynamic change within a common agent centered architecture.

The following are the principal contributions and claims of TER.

### 7.1 A Common Agent Decision Architecture

TER proposes that economically relevant agent decisions can be represented through the common architecture formalized in Models 5.1 and 5.2.

The claim is not that all agents behave identically, but that heterogeneous economic behavior can be analyzed through a common underlying architecture.

### 7.2 Common Architecture Does Not Imply a Common Decision Algorithm

TER separates the structure of an economic decision from the particular process through which an agent selects an action.

Two agents may face similar conditions while using different decision processes and therefore choose different actions.

Likewise, the same agent may use different decision processes under different conditions.

This allows optimization, behavioral decision making, bounded rationality, heuristics, strategic behavior, and other established approaches to operate within the same broader framework rather than requiring one universal model of rationality.

### 7.3 Perceived Reality and Reality Have Distinct Economic Roles

TER explicitly distinguishes an agent's model of reality from reality itself.

An agent's model of reality, $M_{i,t}$ (Section 3), may shape decisions even when incomplete or incorrect.

Economic consequences, however, remain constrained by reality.

TER therefore proposes the general distinction:

> Economic behavior is shaped by perceived reality, while economic consequences are constrained by reality.

This allows TER to represent mistaken beliefs, uncertainty, asymmetric information, expectations, learning, surprise, and prediction error without assuming that agents possess complete knowledge of the economic system.

### 7.4 The Perceived Feasible Set and the Objective Feasible State of Reality Are Distinct

TER explicitly distinguishes the objective feasible state of reality, $F_t$, from the perceived feasible set, $\hat{F}_{i,t}$ (Section 3). Neither is reduced to the other, and the agent does not require knowledge of $F_t$.

An action may be absent from $\hat{F}_{i,t}$ even though the objective conditions represented by $F_t$ would allow it to be realized if attempted. Conversely, an action may be included in $\hat{F}_{i,t}$ but fail, partially execute, or produce a different outcome when the selected action encounters $F_t$ through $R$.

Beliefs represented in $M_{i,t}$ may shape which actions enter $\hat{F}_{i,t}$, but beliefs about states, consequences, and probabilities remain conceptually distinct from perceived action availability. Low probability of success does not by itself make an action unavailable to attempt.

This distinction allows discovery, misinformation, technological change, institutional knowledge, mistaken opportunities, hidden constraints, and learning to be represented within the same architecture.

### 7.5 Decisions, Consequences, and Future Decisions Form a Common Dynamic Structure

TER connects decisions to realized outcomes and subsequent decisions by linking Models 5.1, 5.2, and 5.5: a selected action encounters $F_t$ to produce an outcome, and the outcome may alter later agent-side conditions and the objective feasible state of reality (Model 5.5).

TER therefore treats economic activity as an evolving feedback process rather than a sequence of isolated decisions.

The strength and structure of this feedback may vary (Section 5.6), and TER does not assume a universal feedback coefficient or stability constant.

### 7.6 Agent Interaction Connects Microeconomic Decisions to System Outcomes

TER extends the same architecture to interacting agents, whose actions can affect one another through the outcomes they produce (Axioms 2 and 3).

In the Multi Agent Model (Model 5.3), interacting selected actions encounter the same $F_t$ to produce the system outcome $O_t$, which may in turn alter later conditions (Model 5.5).

TER does not imply that system outcomes must be analytically simple or directly inferable from individual decisions. Complex and emergent behavior may arise from interaction itself.

### 7.7 Established Economic Theories May Be Represented Within a Common Framework

TER hypothesizes that mechanisms described by many established economic theories may be represented as particular configurations, relationships, or processes within the broader TER architecture.

Examples include:

- asymmetric information through differences in $M_i$

- bounded rationality through $M_i$, $\hat{F}_i$, and $D_i$

- strategic interaction through interdependent agent decisions

- institutions through their effects on feasible actions, information, incentives, and decision processes

- technological innovation through changes in $F_t$ or perceived feasible actions

- financial amplification through feedback between outcomes, constraints, beliefs, valuations, and subsequent actions

- collective action through interacting objectives, incentives, institutions, expectations, and decision processes

TER does not claim to replace these theories.

The stronger claim is that theories traditionally studied separately may describe different mechanisms or configurations operating within a shared economic architecture.

### 7.8 The Framework Is Independent of a Particular Modeling Method

TER is not inherently computational, econometric, analytical, or qualitative.

A TER model may be implemented using:

- mathematical optimization

- game theory

- agent based computational models

- econometrics

- experiments

- simulations

- dynamical systems analysis

- case studies

- qualitative analysis

- other appropriate scientific methods

This permits the same conceptual framework to be applied to individual agents, firms, institutions, markets, governments, and larger economic systems while allowing the analytical method to vary with the research question.

TER is intended to remain compatible with established formal and computational frameworks, including optimization models, game theoretic models, agent based models, partially observable decision models, and related approaches. Its contribution is not to replace those frameworks, but to provide a shared economic architecture that distinguishes perceived reality from objective reality, perceived feasible actions from realized feasibility, valuation from selection, agent-level outcomes from system outcomes, and static decisions from feedback over time.

TER does not replace models from other sciences, but its economic specifications may incorporate scientifically established constraints, mechanisms, or conditions where they are relevant to the economic question being studied.

### 7.9 TER Is a Framework for Analysis, Not an Omniscient Prediction System

TER does not assume that an observer can know every objective, belief, constraint, interaction, external effect, future action, or shock within an economic system.

Researchers themselves are agents operating with incomplete information.

A particular TER model is therefore a specification of the framework using the information, assumptions, and methods available to the researcher. In particular, it may only approximate $F_t$ (Section 3).

TER may be used to explain observed decisions and outcomes, identify economic mechanisms, compare possible responses, construct conditional predictions, and evaluate how changes may propagate through a system.

The framework does not imply perfect prediction. In particular, the presence of amplification, imbalance, or fragility does not by itself establish when a system state will change or which outcome will follow.

### 7.10 TER Is an Open and Testable Framework

TER is intended to remain testable, extensible, and subject to revision. The core TER framework is a general economic architecture: it defines relationships, boundaries, and constraints that valid specifications must respect. Empirical predictions arise primarily from particular TER specifications that impose additional assumptions, parameterizations, mechanisms, and evidence.

Its claims should be challenged by attempting to:

- identify economically meaningful phenomena that cannot be represented without violating TER's assumptions

- identify internal contradictions within the framework

- demonstrate that a foundational claim is inconsistent with empirical evidence

- show that a proposed TER variable or mechanism is unnecessary or incorrectly specified

- reproduce established economic results using TER

- derive and test hypotheses from particular TER specifications

- propose alternative frameworks with greater explanatory power or fewer necessary assumptions

The ability to represent an observed outcome is not by itself evidence that a particular TER explanation is correct. Individual TER specifications should constrain their assumptions using available evidence and derive implications that can be compared with observations, competing specifications, or counterfactual results.

Observed actions or outcomes alone may not uniquely identify the underlying model of reality, perceived feasible set, valuation, or decision process. Identification therefore depends on the evidence, assumptions, and restrictions imposed by a particular specification. This limitation is not unique to TER; economic and scientific models commonly rely on variables, mechanisms, or states that are only partially observed or indirectly inferred. TER specifications should therefore state which components are observed, inferred, or assumed and should be evaluated by the quality of those restrictions, evidence, and resulting testable implications rather than by requiring every underlying component to be directly observable with certainty.

Operational rules for constructing, comparing, and validating TER specifications are provided in the accompanying TER methodology. Those rules implement the theory's boundaries without adding new core primitives or changing their meanings.

Variables, axioms, and models should not be added, removed, or materially changed merely because additional concepts can be represented explicitly. Changes to the core framework should be supported by theoretical necessity, empirical evidence, repeated testing, contradiction, or demonstrated explanatory improvement.

TER is therefore presented not as a completed or infallible theory, but as an open, versioned framework that economists and other researchers can test, criticize, extend, and improve.

### Central Research Claim

The strongest general hypothesis proposed by TER is:

> Many economic phenomena traditionally described through separate models and theories can be understood as different configurations and dynamics of a common agent centered economic architecture.

If this claim is correct, TER provides a shared framework for connecting economic decision making, information, constraints, interaction, outcomes, and dynamic change without requiring specialized economic theories to be discarded.

The validity, scope, usefulness, and distinctiveness of this claim remain open to theoretical, empirical, and comparative testing.

## 8. Scope and Limits

The Theory of Economic Relativity is descriptive and analytical, not normative.

It explains and analyzes how agents make decisions, how outcomes emerge, and how systems change. It does not claim that outcomes are optimal, fair, efficient, or desirable.

The theory does not assume:

* Agents are perfectly rational

* Agents have complete information

* Agents optimize correctly

* Markets always clear

* Equilibrium is always good

* Change always improves the system

* Individual rationality produces collective welfare

* Agents or researchers know the objective feasible state of reality perfectly

The theory allows for:

* Mistakes

* Bubbles

* Externalities

* Market failure

* Institutional failure

* Instability

* Collapse

* Learning

* Adaptation

* Growth

The framework is intentionally broad and remains compatible with multiple established economic approaches (Section 7).

## 9. Summary

Economic Relativity begins with a simple observation:

> Economic outcomes emerge from agent decisions interacting with reality.

Agents select actions through decision processes shaped by their information, beliefs, and perceived feasible actions. Where valuation is used, agents evaluate actions relative to objectives and relevant time horizons. Agents may use different decision processes, and the actions they perceive as available to attempt may differ from what reality ultimately allows to be realized.

Selected actions encounter the objective feasible state of reality and interact with the actions of other agents to produce outcomes. These outcomes can alter the conditions of future decisions, creating feedback that may amplify, dampen, persist, propagate, or change over time.

Through these interactions, individual decisions contribute to markets, institutions, and broader economic outcomes. Complex system behavior may emerge that no individual agent intended or controls.

Reality ultimately constrains what actions and conditions can persist (Axiom 4, Constraint 5.4). What follows depends on the particular agents, institutions, conditions, constraints, shocks, and interactions involved.

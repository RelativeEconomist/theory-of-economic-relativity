# Theory of Economic Relativity

**Version:** 0.5.0

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

Economic Relativity proposes a unifying framework centered on the agent. It begins with a simple premise:

> Economic outcomes emerge from agent decisions interacting with reality.

Agents may differ substantially in their objectives, information, constraints, valuations, time horizons, and decision processes. Economic Relativity does not assume that they optimize or use a common decision rule.

Instead, it proposes that economically relevant decisions can be represented through a common architecture. Agents interpret conditions through their models of reality, act from alternatives they perceive as feasible, and select actions through decision processes that may include optimization, satisficing, heuristics, habits, intuition, reflexive responses, strategic reasoning, stochastic selection, or other mechanisms. Where valuation is used, objectives provide the reference against which actions are evaluated.

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

| $\hat{F}_{i,t}$ | Perceived Feasible Set | Actions agent $i$ perceives as available to attempt at time $t$ | 5.1, 5.2, 5.5 |

| $V_{i,t}$ | Valuation | Evaluates actions relative to the agent's objective, given its model of reality and time horizon | 5.1, 5.5 |

| $H_{i,t}$ | Time Horizon | Which future consequences agent $i$ considers relevant to valuation | 5.1, 5.5 |

| $D_{i,t}$ | Decision Process | Process through which agent $i$ selects among perceived feasible actions; it may condition directly on the agent's model of reality and may use valuation when applicable | 5.1, 5.5 |

| $C_{i,t}$ | Selected Action | Action agent $i$ selects from its perceived feasible set | 5.1, 5.2, 5.3, 5.5 |

| $O_{i,t}$ | Realized Outcome | Realized outcome associated with agent $i$'s selected action; where explicit interaction matters, an interaction-dependent agent-level outcome is derived from the same joint $R$ as $O_t$ | 5.2, 5.3, 5.5 |

| $O_t$ | System Outcome | Realized system outcome produced by interacting selected actions encountering $F_t$ | 5.3, 5.5 |

| $R(\cdot)$ | Reality Function | Maps the selected action(s) and the relevant objectively realized state $F_t$ to the realized outcome; its arguments depend on model scope | 5.2, 5.3, 5.5 |

Where:

- $i$ identifies the agent.

- $t$ indexes the relevant decision point or time in the specification; depending on the model, it may represent a period, stage, round, event, or other decision point.

- $a$ represents a potential action.

The core decision and outcome structure, formalized in Models 5.1 and 5.2, can be summarized as:

$$

C_{i,t}

=

D_{i,t}

\left(

\hat{F}_{i,t},

M_{i,t},

V_{i,t}(\cdot \mid G_{i,t}, M_{i,t}, H_{i,t})

\right)

$$

while the objective feasible state of reality constrains the realized outcome:

$$

(C_{i,t},F_t)

\rightarrow

O_{i,t}

$$

The perceived feasible set $\hat{F}_{i,t}$ contains the actions agent $i$ perceives as available to attempt, while $F_t$ represents the objective conditions relevant when the selected action is realized.

Analytical objects such as $\mathbf{Z}_t$, $\Phi_t$, and $\mathcal{J}_t$ (Section 5.6) may be introduced within a particular specification when useful, but they are not TER primitives or required components of the framework.

### Agent

A decision making entity that selects among actions it perceives as feasible.

An agent may be an individual or a coordinated group of agents acting toward one or more objectives.

Examples include individuals, households, businesses, nonprofits, governments, and institutions.

### Institution

A structure or system of agents organized through rules, relationships, or common functions that shapes individual and collective action.

Institutions may both act as agents and alter the information, incentives, constraints, and perceived feasible sets of other agents. The laws, rules, and other institutional conditions that constrain what can occur are aspects of $F_t$.

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

$F_t$ is not agent specific, may be perceived imperfectly, and may only be approximated in empirical or computational specifications. Conditions objectively realized by the point of realization belong to the relevant $F_t$. Expectations or predictions about unresolved conditions belong in $M_{i,t}$; if uncertainty resolves after selection but before realization, the realized condition belongs in the relevant $F_t$. Conditions produced by modeled actions or interactions are realized as outcomes and may become part of a later $F$.

### Perceived Feasible Set

The set of actions an agent perceives as available to attempt for the decision at time $t$, whether or not each action is actively evaluated by the decision process. The actions in the set are its perceived feasible actions.

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

The realized result of agent actions and interactions encountering the objective feasible state of reality, which may include external effects. $O_{i,t}$ is the realized outcome associated with an agent's selected action (Model 5.2); $O_t$ is the system outcome of explicitly modeled interacting actions (Model 5.3).

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

A specification-level condition in which the modeled actions, beliefs, constraints, and interactions are mutually consistent under the equilibrium concept being applied. The treatment of deviations, feasibility, and belief consistency is determined by that equilibrium concept. An equilibrium does not imply that underlying actions or states are static, nor that the equilibrium is dynamically stable, optimal, permanent, or desirable.

### Reality

The objective world itself, whose conditions ultimately determine the consequences of actions, regardless of an agent's beliefs or expectations.

Reality is not a TER variable. $F_t$ is TER's representation of the objective feasible state of reality at time $t$: the objectively realized conditions and constraints of Reality that determine what can occur. TER does not assume that the evolution of reality is fundamentally deterministic or stochastic; such assumptions belong to the scientific and economic specification being studied.

## 4. Axioms

The Theory of Economic Relativity rests on the following axioms. Some axioms state structural or definitional commitments of the framework, while others impose substantive restrictions on valid TER specifications.

### Axiom 1: Agents act on information and beliefs

Decisions depend on an agent's information, beliefs, and model of reality, which may be incomplete or incorrect.

### Axiom 2: Agents select among perceived feasible actions

Agents select among the actions they perceive as available to attempt for the decision process at the time of decision. The perceived feasible set may differ from what reality ultimately allows to be realized.

### Axiom 3: Valuation is relative to objectives

When valuation occurs, actions or their consequences are evaluated relative to the agent's objective, given its model of reality and relevant time horizon.

Evaluation need not be conscious, exhaustive, or perfectly optimizing.

### Axiom 4: Agents select actions through a decision process

The selected action is the action that results from the agent's decision process at that time from among its perceived feasible actions.

The decision process may condition directly on the agent's model of reality and may use valuation when applicable. The selected action need not be objectively optimal or result from exhaustive comparison among alternatives.

### Axiom 5: Actions contribute to outcomes and external effects

Agent actions contribute to outcomes and may create external effects. Outcomes may also depend on interactions among agents and on the objective feasible state of reality.

### Axiom 6: Actions can affect other agents

One agent's actions can, through the outcomes they contribute to, change at later decision points or stages the information, constraints, incentives, or perceived feasible actions of other agents, and the objective feasible state of reality that subsequent actions encounter.

### Axiom 7: Reality constrains consequences

Agents make decisions according to their understanding of reality, but reality ultimately determines the consequences of those decisions.

### Axiom 8: Infeasible continuation prevents persistence

When continuation of an existing state becomes infeasible under reality's constraints, that state cannot persist unchanged.

### Axiom 9: Realized outcomes may shape subsequent conditions

Realized outcomes may shape subsequent conditions when their economically relevant consequences alter those conditions. The conditions that may change include the objective feasible state of reality and the objectives, models of reality, perceived feasible sets, valuations, time horizons, and decision processes that shape later decisions. When an outcome does change conditions relevant to a later decision, those changes are reflected in the subsequent conditions.

### Axiom Map

The axioms primarily supporting each formal component (Section 5) and each interpretive principle (Section 6).

| Component | Primary supporting axioms |

|---|---|

| 5.1 Agent Decision Model | 1 ($M$), 2 ($\hat{F}$), 3 ($V$), 4 ($D$) |

| 5.2 Action to Outcome Model | 2, 5, 7 |

| 5.3 Multi Agent Model | 5, 6, 7 |

| 5.4 State Persistence Constraint | 7, 8 |

| 5.5 Dynamic Feedback Model | 1, 6, 7, 9 |

| 5.6 Feedback Analysis and Stability | 5, 6, 7, 8, 9 |

| 6.1 Agent Objective | 3, 4; Model 5.1 |

| 6.2 Feasibility and Constraints | 1, 2, 4, 6, 7; Models 5.1, 5.2, 5.3 |

| 6.3 Agent Model of Reality | 1, 2, 3, 7, 9; Models 5.1, 5.2, 5.5 |

| 6.4 Action Selection | 1, 2, 3, 4, 7; Models 5.1, 5.2 |

| 6.5 Outcomes and System Effects | 1, 5, 6, 7, 9; Models 5.2, 5.3, 5.5 |

| 6.6 Persistence and Change Over Time | 1, 2, 5, 6, 7, 8, 9; Sections 5.3–5.6 |

## 5. Formal Architecture

Variables and notation are defined in Section 3. The formal architecture has five components and one optional set of analytical methods:

- **Model 5.1, Agent Decision Model:** how an agent selects an action.

- **Model 5.2, Action to Outcome Model:** the agent-level outcome of a selected action.

- **Model 5.3, Multi Agent Model:** the system outcome of explicitly modeled interacting actions.

- **Constraint 5.4, State Persistence Constraint:** whether an existing system state can continue.

- **Model 5.5, Dynamic Feedback Model:** how realized outcomes may alter later conditions.

- **Analysis 5.6, Feedback Analysis and Stability:** optional analytical methods, not a TER primitive or a required model.

### 5.1 Agent Decision Model

The Agent Decision Model describes how a single agent selects an action. It is the fundamental decision model of Economic Relativity, upon which the broader framework builds.

$$

C_{i,t}

=

D_{i,t}

\left(

\hat{F}_{i,t},

M_{i,t},

V_{i,t}(\cdot \mid G_{i,t}, M_{i,t}, H_{i,t})

\right)

$$

Symbols are defined in Section 3. In this model:

- $V_{i,t}$ = the valuation

- $V_{i,t}(a \mid G_{i,t}, M_{i,t}, H_{i,t})$ = the value assigned to action $a$ relative to the objective, given the agent's model of reality and time horizon

**Scope.** The selected action is the action that results from the agent's decision process. This does not require the agent to identify the objectively best action or exhaustively compare every alternative. TER does not require deterministic choice: a particular specification may define $D$ as deterministic or stochastic.

**Boundary.** $F_t$ represents the objective conditions and constraints relevant to realization and therefore affects realized outcomes (Model 5.2), but it is not an input to $D_{i,t}$: the agent acts from $\hat{F}_{i,t}$ and does not require knowledge of $F_t$. Objective conditions represented in $F_t$ affect an agent's action selection only insofar as they are perceived or represented through agent-side components such as $M_{i,t}$ or $\hat{F}_{i,t}$. $F_t$ and $\hat{F}_{i,t}$ may differ. Agents may overlook available actions, incorrectly believe an action is possible, or discover new alternatives as information and constraints change.

**Valuation.** When the decision process uses valuation, $V_{i,t}(a \mid G_{i,t}, M_{i,t}, H_{i,t})$ represents the value assigned to action $a$ relative to the objective, given the agent's model of reality and time horizon. The time horizon determines which future consequences the agent considers relevant to the valuation.

**Decision processes.** $D_{i,t}$ governs selection. It receives the agent's model of reality directly and may condition selection on that perceived state without invoking valuation. It may optimize over valuations, satisfice, apply a heuristic, follow habit, respond reflexively, select stochastically, or use another mechanism. Valuation is therefore a component of the architecture but need not be consulted for every selected action. $G_{i,t}$ and $H_{i,t}$ are not universal direct inputs to $D_{i,t}$; when valuation is used, they condition $V_{i,t}$.

$M_{i,t}$ may therefore inform both valuation and selection: through $V_{i,t}$ when actions are evaluated, and directly through $D_{i,t}$ when selection depends on perceived state. These roles should remain distinct within a specification.

Optimization remains one possible specification in which $D_{i,t}$ may use $M_{i,t}$ through valuation:

$$

D_{i,t}(\cdot)

=

\arg\max_{a \in \hat{F}_{i,t}}

E[V_{i,t}(a \mid G_{i,t}, M_{i,t}, H_{i,t})]

$$

### 5.2 Action to Outcome Model

The Action to Outcome Model describes how a selected action encounters reality and produces an outcome.

An agent selects an action from its perceived feasible set:

$$

C_{i,t} \in \hat{F}_{i,t}

$$

The selected action encounters the objective feasible state of reality relevant at its point of realization:

$$

O_{i,t} = R(C_{i,t}, F_t)

$$

Symbols are defined in Section 3. Here $R(\cdot)$ is applied to agent $i$'s selected action and $F_t$.

**Scope.** This model applies to an agent-level specification in which interactions with other agents are not explicitly modeled as joint determinants of the realized outcome at that decision point or stage. Relevant objective conditions created by other agents may still be represented through $F_t$.

**Failure and partial execution.** An action in $\hat{F}_{i,t}$ is perceived as available to attempt, not guaranteed to succeed. When the selected action encounters the objective conditions and constraints represented by $F_t$ through $R$, it may succeed, partially execute, fail, or produce a different consequence than the agent expected; that realized result becomes part of the outcome.

**Time.** TER uses the same index $t$ for a selected action and the objective state relevant to its realization, but this does not imply that the agent knows $F_t$ when selecting the action. Later decision points are evaluated against the objective state relevant when their selected actions are realized, through the feedback described in Model 5.5.

**Reality and uncertainty.** $F_t$ represents the objectively realized state relevant when the selected action is realized, while $R$ maps the selected action and that realized state to the outcome. Uncertainty may resolve after selection but before realization; the realized condition then belongs to the relevant $F_t$, while the agent's prior expectations remain in $M$. TER does not assume that the evolution of reality is fundamentally deterministic or stochastic. A specification may model uncertainty in how later states arise without changing the distinction between the agent's beliefs in $M$ and the objective state represented by $F$.

### 5.3 Multi Agent Model

The Multi Agent Model describes how the actions and interactions of multiple agents shape one another and produce system outcomes.

At decision point $t$, the actions included in the modeled interaction encounter the same objective feasible state of reality, $F_t$, and their interaction produces the system outcome:

$$

O_t = R(C_{1,t}, C_{2,t}, \ldots, C_{n,t}, F_t)

$$

Symbols are defined in Section 3. Here $n$ is the number of explicitly modeled agents whose actions are included at decision point $t$, and $R(\cdot)$ is applied to those selected actions and $F_t$. A specification may represent an agent that does not act at that decision point by omitting its action from the interaction or by using an explicit no-action where the model requires one.

**Scope.** $O_t$ applies where interactions among multiple agents are explicitly modeled. TER does not define $O_t$ as an aggregation of the individual outcomes $O_{i,t}$.

**Agent-level outcomes.** Where an agent-level realized outcome depends on contemporaneous or otherwise explicitly modeled interactions, that outcome should be derived from the same joint reality function that determines the system outcome. Where an agent-level outcome does not depend on those interactions at the chosen modeling scope, Model 5.2 may still be applied.

**Interaction timing.** A multi-agent specification may represent contemporaneous, sequential, staged, asynchronous, or repeated interaction. The index $t$ refers to the relevant decision point or time in the specification. Where actions occur in an ordered sequence, later moves use later decision points so that each agent acts from the information and perceived feasible actions available then. Earlier actions may affect later selection through updated agent-side conditions such as $M$ or $\hat{F}$ rather than through direct access by $D$ to $F$.

**One $F_t$.** Within the relevant decision point or stage, the conditions and constraints represented by the same $F_t$ may differ in their relevance to particular actions according to those actions' circumstances.

System outcomes may include external effects (Section 3). Interactions may also create opportunities that agents could not achieve independently, including cooperation, exchange, specialization, and institutions.

**Later decision points.** Through the outcomes they produce, agents' actions can expand, restrict, or alter the opportunities available to others at later decision points or stages. Changes resulting from an interaction may be captured through the system outcome and represented in later states such as $F_{t+1}$ (Model 5.5). A multi-agent specification may represent feasibility constraints explicitly when they are relevant to the system outcome.

### 5.4 State Persistence Constraint

The State Persistence Constraint describes the boundary condition governing whether an existing system state can continue unchanged under reality's constraints.

Here the state being evaluated is the existing system state (Section 3); $F_t$ is not that state but represents the objective conditions and constraints that determine whether its continuation is feasible.

When continuation of an existing state is no longer feasible under reality's constraints, that state cannot persist unchanged:

$$

\text{continuation of the existing state no longer feasible under reality's constraints}

\Rightarrow

\text{existing state cannot persist unchanged}

$$

The conditions preventing continuation may arise from agent actions and interactions, institutions, markets, physical conditions, external shocks, or other factors that affect what reality allows to persist or occur.

An imbalance (Section 3) may persist, grow, diminish, or be resolved while the existing state remains feasible. Its presence does not by itself establish that the state cannot continue or predict when a change will occur; it may contribute to infeasible continuation, persist through it, or be unrelated to it, and imbalance by itself does not force correction.

This constraint does not specify what state follows or the mechanism through which change occurs. Subsequent outcomes may emerge through agent decisions, interactions, external shocks, institutional processes, physical processes, and feedback represented elsewhere in TER. The resulting state may represent equilibrium, continued imbalance, instability, transformation, failure, or another outcome permitted by the conditions that follow.

### 5.5 Dynamic Feedback Model

The Dynamic Feedback Model describes how realized outcomes can alter subsequent conditions, including the elements shaping later decisions and the objective feasible state of reality.

Realized outcomes become part of the conditions shaping subsequent decisions. The feedback represented here is path dependent: later decisions reflect the consequences of prior outcomes, while the objective feasible state of reality at each time, which external shocks may change, also affects what is realized as the system evolves.

In the relationships below, arrows indicate possible influence, not that every outcome necessarily changes every subsequent component. They are written from the system outcome $O_t$; in a single-agent specification, feedback may originate from $O_{i,t}$ instead. Realized outcomes may affect an agent's model of reality only through the information available to that agent. TER does not assume that agents observe the full system outcome or observe outcomes without error.

$$

O_t

\rightarrow

(G_{i,t+1}, M_{i,t+1}, \hat{F}_{i,t+1}, V_{i,t+1}, H_{i,t+1}, D_{i,t+1})

\rightarrow

C_{i,t+1}

$$

$$

O_t

\rightarrow

F_{t+1}

$$

For a single-agent specification, the next realized outcome remains:

$$

O_{i,t+1}

=

R(C_{i,t+1}, F_{t+1})

$$

Where interactions among agents are explicitly modeled, the next system outcome is $O_{t+1} = R(C_{1,t+1}, \ldots, C_{n,t+1}, F_{t+1})$. Any agent-level outcome that depends on those interactions is derived from that same joint reality function rather than from a separate single-agent application of $R$.

Symbols are defined in Section 3, and $t+1$ denotes the next relevant decision point in the specification. The agent's next action, $C_{i,t+1}$, is selected through Model 5.1 with $t+1$ indices. $F_{t+1}$ represents the objective state relevant when that selected action is realized, but it is not an input to $D_{i,t+1}$; the agent selects using its agent-side components and encounters $F_{t+1}$ through the outcome model.

**Sources of change in $F$.** Changes to $F_t$ resulting from agent actions and interactions are captured through realized outcomes, while external shocks, which originate outside the modeled action and outcome pathway, may also alter it independently.

Experience may bring $\hat{F}_i$ closer to what reality allows to be realized, reveal previously unknown actions, change how alternatives are valued, or change how an agent makes decisions. When $C_{i,t}$ is a commitment, contract, policy, or contingent strategy, it is the object selected at that decision point; later realized actions remain separate selected actions at later decision points. Enforceable commitments may alter later objective conditions and constraints represented in $F$, while nonbinding, self-enforcing, or perceived commitments may instead shape $M$, $\hat{F}$, $V$, or $D$, depending on the specification.

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

A realized outcome may have little effect on subsequent decisions or may propagate through many agents and institutions. Changes may be amplified or damped, disappear quickly or persist, and contribute to convergence, divergence, oscillation, thresholds, or changing patterns of behavior. Researchers should use methods appropriate to the particular economic relationships represented in the specification.

Importantly, amplification alone does not imply instability or imbalance. Strong feedback may accompany productive growth, technological adoption, coordination, speculation, adaptation, or destabilization. Its economic significance depends on the underlying agents, conditions, interactions, constraints, and whether the resulting path remains feasible under reality's constraints.

## 6. Consolidated Principles

This section interprets the TER architecture through established economics. Definitions are in Section 3, formal models in Section 5, and the axioms each principle draws on in the Axiom Map (Section 4).

### 6.1 Agent Objective

Objectives provide the reference against which agents value potential actions when valuation is used. A decision process need not actively consult an objective or valuation for every selected action.

Many established economic concepts describe different forms of this process. Utility and preferences describe how consumers value alternatives. Profit maximization describes firms evaluating actions relative to profit. Incentives change the relative value of potential actions, while expected value provides one way agents may evaluate actions under uncertainty.

In Model 5.1, the objective $G_{i,t}$ is the reference against which the valuation $V_{i,t}$ evaluates actions.

The same architecture can represent consumers pursuing utility, firms pursuing profit, governments pursuing stability, or other agents pursuing different objectives without requiring them to use the same decision process.

Because value is relative to the agent's objective, the same action, resource, or outcome may have different value to different agents, or to the same agent pursuing a different objective.

### 6.2 Feasibility and Constraints

Scarcity is a fundamental source of constraints. Limited resources such as time, capital, labor, technology, and natural resources restrict what an agent can actually do. Budget and production constraints are specific examples of these limits.

Constraints are represented in $F_t$, while information and beliefs shape what agents perceive as feasible (Models 5.1 and 5.2). What agents perceive as available to attempt and what reality ultimately allows to be realized may differ, and both may change over time.

Choosing among competing alternatives creates opportunity costs. Because agents face different resources, capabilities, and constraints, they may also face different opportunity costs. These differences can create comparative advantage and opportunities for mutually beneficial trade.

Interactions with other agents can also change what is feasible, through the outcomes they produce. Cooperation, exchange, specialization, and institutions may expand or restrict the actions available to an agent. Institutions can further shape what is feasible through laws, rules, property rights, contracts, and other structures that form part of $F_t$.

Differences in constraints and interactions among agents give rise to opportunity costs, comparative advantage, trade, and changing feasibility.

### 6.3 Agent Model of Reality

Agents make decisions according to their model of reality, which may differ from reality itself.

The agent's model of reality, $M_{i,t}$ (Section 3), draws on information, beliefs, assumptions, expectations, and interpretations. Information economics, expectations, behavioral economics, bounded rationality, and learning describe different aspects of how agents form, use, and update this model.

$M_{i,t}$ shapes the agent's understanding of actions and consequences. It may inform valuation through $V_{i,t}$ and may also directly condition selection through $D_{i,t}$. Neither the agent's model of reality nor its perceived feasible set must perfectly correspond to reality.

This distinction allows Economic Relativity to represent both highly informed and imperfect decision making. An agent may have incomplete information, incorrect beliefs, biased expectations, limited ability to evaluate alternatives, or an inaccurate understanding of what actions are available.

Valuation and decision processes may also be shaped by reference points, framing, heuristics, biases, and subjective beliefs. Bounded rationality and behavioral effects therefore operate within the agent's decision architecture rather than as exceptions to it.

Outcomes can provide new information that changes the agent's model of reality. Those changes may also affect the actions the agent perceives as feasible, but TER does not require changes in perceived feasibility to occur through a single pathway.

Learning does not require convergence toward perfect knowledge. Agents may update correctly, incorrectly, partially, or not at all.

### 6.4 Action Selection

Different agents, or the same agent under different conditions, may use different decision processes (Model 5.1). A decision process may condition directly on the agent's model of reality, may use valuation, or may use both for distinct roles. Optimization, satisficing, heuristics, habits, and other established mechanisms may operate as decision processes, so the selected action need not be objectively optimal or result from exhaustive comparison among alternatives.

Marginal analysis remains an important special case of valuation. Agents may evaluate expected marginal benefits and marginal costs when assigning value to alternatives. Optimization, satisficing, heuristics, habits, reflexive responses, and other mechanisms may then govern how $D_{i,t}$ selects an action.

Because action selection may use valuation or condition directly on the agent's model of reality, the considerations driving the selected action may differ from the consequences ultimately realized.

### 6.5 Outcomes and System Effects

Economic outcomes emerge from the actions and interactions of agents encountering the objective feasible state of reality. As agents affect one another, individual decisions can contribute to market and system level outcomes that no single agent determines independently.

Supply and demand describe aggregate patterns generated by buyers and sellers making individual decisions. Their interactions produce prices and quantities, while those prices become information and conditions that influence subsequent decisions.

In the Multi Agent Model (Model 5.3), the outcome of interacting selected actions encountering $F_t$ is the system outcome $O_t$, which may include external effects on other agents.

Externalities are external effects (Section 3). Individually selected actions may therefore produce outcomes that conflict with the objectives of other agents or the broader system. When such outcomes are inefficient relative to a specified welfare criterion, economics may describe them as market failures.

Because agents and markets are interconnected, changes in one part of an economic system can alter the information, constraints, opportunities, and decisions of agents elsewhere. General equilibrium studies these interdependencies, while macroeconomic aggregation examines how individual actions and interactions contribute to economy wide outcomes.

System outcomes also feed back into future agent decisions (Model 5.5). Prices, employment, production, income, institutions, and other aggregate conditions may change what agents know, what they can do, what time horizons they consider relevant, how they value alternatives, and how subsequent decisions are made.

Within TER specifications, markets and macroeconomic outcomes need not be treated as independent starting points. They may emerge from interacting agent decisions and the conditions under which those decisions occur, while the resulting system outcomes may become part of the conditions shaping future decisions.

Institutions participate in this feedback process. They may emerge from agent interactions and collective action, while also shaping the information, incentives, constraints, and perceived feasible sets that influence subsequent agent decisions and outcomes, and forming part of the objective feasible state of reality. Agents may also act to create, preserve, modify, or remove institutions, and through the outcomes of those actions further change the conditions faced by themselves and others.

### 6.6 Persistence and Change Over Time

Economic systems evolve as agents respond to changing outcomes, information, constraints, institutions, time horizons, and external shocks.

Changes in these conditions may alter actions, beliefs, constraints, or interactions so that the equilibrium consistency condition being applied no longer holds (Section 3). The actions and conditions that sustain an equilibrium may themselves alter the relationships on which that equilibrium depends, allowing stability to generate endogenous change or instability over time.

Under the State Persistence Constraint (Constraint 5.4), an imbalance neither establishes that continuation is infeasible nor predicts when state change will occur, and TER does not prescribe what follows when continuation becomes infeasible. External shocks (Section 3) can also change outcomes and conditions, including $F_t$. Feedback (Model 5.5) may dampen or amplify change, and amplification alone does not imply instability or imbalance (Section 5.6).

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

Agents act according to their model of reality, $M_{i,t}$ (Section 3). This model may be incomplete or incorrect.

Economic consequences, however, remain constrained by reality.

TER therefore proposes the general distinction:

> Economic behavior is shaped by perceived reality, while economic consequences are constrained by reality.

This allows TER to represent mistaken beliefs, uncertainty, asymmetric information, expectations, learning, surprise, and prediction error without assuming that agents possess complete knowledge of the economic system.

### 7.4 The Perceived Feasible Set and the Objective Feasible State of Reality Are Distinct

TER explicitly distinguishes the objective feasible state of reality, $F_t$, from the perceived feasible set, $\hat{F}_{i,t}$ (Section 3). Neither is reduced to the other, and the agent does not require knowledge of $F_t$.

$\hat{F}_{i,t}$ contains actions the agent perceives as available to attempt. An action may be absent from $\hat{F}_{i,t}$ even though the objective conditions represented by $F_t$ would allow it to be realized if attempted. Conversely, an action may be included in $\hat{F}_{i,t}$ but fail, partially execute, or produce a different outcome when the selected action encounters $F_t$ through $R$.

Beliefs represented in $M_{i,t}$ may shape which actions enter $\hat{F}_{i,t}$, but beliefs about states, consequences, and probabilities remain conceptually distinct from perceived action availability. Low probability of success does not by itself make an action unavailable to attempt.

This distinction allows discovery, misinformation, technological change, institutional knowledge, mistaken opportunities, hidden constraints, and learning to be represented within the same architecture.

### 7.5 Decisions, Consequences, and Future Decisions Form a Common Dynamic Structure

TER connects decisions to realized outcomes and subsequent decisions by linking Models 5.1, 5.2, and 5.5: a selected action encounters $F_t$ to produce an outcome, and the outcome may alter one or more subsequent conditions, including an agent's objective, model of reality, perceived feasible set, valuation, time horizon, or decision process, and the objective feasible state of reality.

TER therefore treats economic activity as an evolving feedback process rather than a sequence of isolated decisions.

The strength and structure of this feedback may vary (Section 5.6), and TER does not assume a universal feedback coefficient or stability constant.

### 7.6 Agent Interaction Connects Microeconomic Decisions to System Outcomes

TER extends the same architecture to interacting agents.

Through the outcomes they produce, actions taken by one agent may alter the information, incentives, constraints, opportunities, or outcomes experienced by other agents.

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

This architecture connects objectives, perceived reality, feasible actions, decision processes, interactions, realized outcomes, and feedback over time without requiring agents to share a common decision algorithm.

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

The framework is intentionally broad. Its purpose is to organize established economic mechanisms around agent decision making, interaction, outcomes, and change while remaining compatible with multiple established economic approaches.

## 9. Summary

Economic Relativity begins with a simple observation:

> Economic outcomes emerge from agent decisions interacting with reality.

Agents select actions through decision processes shaped by their information, beliefs, and perceived feasible actions. Where valuation is used, agents evaluate actions relative to objectives and relevant time horizons. Agents may use different decision processes, and the actions they perceive as available to attempt may differ from what reality ultimately allows to be realized.

Selected actions encounter the objective feasible state of reality and interact with the actions of other agents to produce outcomes. These outcomes can alter the conditions of future decisions, creating feedback that may amplify, dampen, persist, propagate, or change over time.

Through these interactions, individual decisions contribute to markets, institutions, and broader economic outcomes. Complex system behavior may emerge that no individual agent intended or controls.

Reality ultimately constrains what actions and conditions can persist. When continuation of an existing state becomes infeasible under reality's constraints, that state cannot persist unchanged. What follows depends on the particular agents, institutions, conditions, constraints, shocks, and interactions involved.

In short:

> Economic behavior emerges from agents selecting actions through heterogeneous decision processes within a common underlying architecture. Where valuation is used, agents evaluate actions relative to objectives and relevant time horizons. Their actions encounter reality, interact with other agents, produce outcomes, and reshape the conditions shaping future decisions. Economic systems therefore evolve through the continuing interaction of agent decisions, feedback, and reality.

# Theory of Economic Relativity

**Version:** 0.30.0

## Abstract

The Theory of Economic Relativity is a proposed unifying framework built on established economic principles. It organizes concepts such as scarcity, opportunity cost, marginal analysis, incentives, prices, supply and demand, externalities, institutions, and equilibrium within a common agent centered architecture.

The theory begins with a simple observation:

> Economic outcomes emerge from agent decisions interacting with reality.

An agent may be an individual, household, business, nonprofit, government, or organization. Although agents differ in objectives, information, constraints, and decision processes, their economic decisions can be represented through a common architecture: agents act in relation to objectives, interpret reality through available information, act from the alternatives they perceive as feasible, and select actions through a decision process.

Outcomes emerge from those actions and interactions under prevailing conditions and external shocks, and may include external effects on other agents.

The central hypothesis is:

> Economic behavior emerges from agents acting in relation to objectives through decision processes shaped by their information, beliefs, perceived feasible actions, valuations, and time horizons. Selected actions encounter reality and interact with the actions of other agents to produce outcomes. Those outcomes may alter the information, constraints, opportunities, valuations, institutions, and other conditions shaping future decisions, allowing economic systems to evolve over time.

---

## 1. Introduction

Economics seeks to explain how decisions, institutions, and interactions produce economic outcomes. Over time, the field has developed a rich body of theory describing incentives, markets, information, institutions, strategic interaction, and the allocation of scarce resources.

Economic Relativity proposes a unifying framework centered on the agent. It begins with a simple premise:

> Economic outcomes emerge from agent decisions interacting with reality.

Agents may differ substantially in their objectives, information, constraints, valuations, time horizons, and decision processes. Economic Relativity does not assume that they optimize or use a common decision rule.

Instead, it proposes that economically relevant decisions can be represented through a common architecture. Agents act in relation to objectives, interpret conditions through their models of reality, act from alternatives they perceive as feasible, and select actions through decision processes that may include optimization, satisficing, heuristics, habits, intuition, strategic reasoning, or other mechanisms.

Those actions interact with actual conditions and with the actions of other agents to produce outcomes. The resulting outcomes may then alter information, constraints, opportunities, valuations, institutions, and subsequent decisions.

Economic Relativity therefore organizes established economic mechanisms within a common agent centered architecture while allowing heterogeneous behavior, interaction, and dynamic change across individuals, firms, institutions, markets, and broader economic systems.

---

## 2. Core Hypothesis

The central hypothesis of Economic Relativity is:

> **Economic behavior emerges from agents acting in relation to objectives through decision processes shaped by their information, beliefs, perceived feasible actions, valuations, and time horizons. Selected actions encounter reality and interact with the actions of other agents to produce outcomes. Those outcomes may alter the information, constraints, opportunities, valuations, institutions, and other conditions shaping future decisions, allowing economic systems to evolve over time.**

This hypothesis contains five core claims:

1. Economic behavior begins with agents acting in relation to objectives.
2. Agents act according to their information, beliefs, perceived feasible actions, valuations, time horizons, and decision processes.
3. The actions agents perceive as feasible may differ from the actions actually permitted by reality.
4. Outcomes emerge from agent actions and interactions under prevailing conditions and external shocks, and may include external effects.
5. Outcomes may alter future decision environments, causing economic systems to evolve over time.

## 3. Core Definitions

### TER Variables and Notation

The core TER decision architecture uses the following variables:

| Symbol | Meaning |
|---|---|
| $G_{i,t}$ | Objective relevant to agent $i$'s decision at time $t$ |
| $M_{i,t}$ | Agent $i$'s model of reality, including information, beliefs, assumptions, expectations, and interpretations |
| $F_{i,t}$ | Actual feasible set available to agent $i$ at time $t$ |
| $\hat{F}_{i,t}$ | Feasible set agent $i$ perceives as available at time $t$ |
| $V_{i,t}$ | Valuation of actions relative to the agent's objective at time $t$ |
| $H_{i,t}$ | Time horizon considered relevant to the decision |
| $D_{i,t}$ | Decision process used to evaluate and select among perceived feasible actions |
| $C_{i,t}$ | Action selected by the agent |
| $O_{i,t}$ | Realized outcome associated with the selected action |

Where:

- $i$ identifies the agent.
- $t$ identifies the time period.
- $a$ represents a potential action.

The core decision and outcome structure can be summarized as:

$$

(G,M,\hat{F},V,H,D)_{i,t}
\rightarrow
C_{i,t}

$$

while actual feasibility, prevailing conditions, and external shocks constrain the realized outcome:

$$

(C_{i,t},F_{i,t},P_{i,t},S_{i,t})
\rightarrow
O_{i,t}

$$

Additional notation used in specific models includes:

| Symbol | Meaning |
|---|---|
| $R(\cdot)$ | Reality function determining realized outcomes |
| $P_t$ | Prevailing conditions |
| $S_t$ | External shocks |

Section 5.6 discusses optional analytical methods for studying feedback and stability, including state-space representations, Jacobians, eigenvalue analysis, simulation, and other appropriate methods. Analytical objects such as $\mathbf{Z}_t$, $\Phi_t$, and $\mathcal{J}_t$ may be introduced within a particular specification when useful, but they are not TER primitives or required components of the framework.

### Agent

A decision making entity that selects among actions it perceives as feasible.

An agent may be an individual or a coordinated group of agents acting toward one or more objectives.

Examples include individuals, households, businesses, nonprofits, governments, and institutions.

### Institution

A structure or system of agents organized through rules, relationships, or common functions that shapes individual and collective action.

Institutions may both act as agents and alter the information, incentives, constraints, and feasible sets of other agents.

### Objective

A result, state, or condition relative to which an agent's actions are directed or evaluated.

Examples include profit, survival, growth, security, happiness, stability, market share, or social welfare.

### System

A set of interacting agents, institutions, conditions, and relationships considered together for analysis.

The boundary of a system depends on the level of analysis.

### Information

The facts, signals, observations, and other inputs available to an agent when making a decision.

Information may be incomplete, inaccurate, or interpreted differently by different agents.

### Model of Reality

An agent's internal understanding of reality, formed from its information, beliefs, assumptions, expectations, and interpretations.

An agent's model of reality may differ from reality and may change as new information and outcomes are observed.

### Constraints

The limitations that determine which actions are actually feasible, including time, resources, technology, laws, institutions, access, authority, and physical conditions.

An agent may perceive these constraints imperfectly, causing its perceived feasible set to differ from the actions actually available.

### Actual Feasible Set

The set of actions actually available to an agent given its resources, capabilities, constraints, and prevailing conditions.

### Perceived Feasible Set

The set of actions an agent perceives as available for the decision at time \(t\), whether or not each action is actively evaluated by the decision process.

The perceived feasible set may differ from the actual feasible set.

### Decision Process

The process through which an agent evaluates and selects among perceived feasible actions.

A decision process may involve optimization, satisficing, heuristics, habits, intuition, reflexive responses, strategic reasoning, or other mechanisms. It need not produce an objectively optimal action.

### Action

The course of action selected by an agent from its perceived feasible set in relation to an objective.

Examples include buying, selling, saving, hiring, investing, regulating, producing, consuming, or delaying.

### Value

The contribution an agent assigns to an action, resource, outcome, or condition relative to its objective.

### Time Horizon

The period over which an agent considers consequences relevant to a decision.

A time horizon may range from immediate outcomes to consequences extending years, generations, or beyond the agent's lifetime.

### Outcome

The realized result of agent actions and interactions under prevailing conditions and external shocks, which may include external effects.

### External Effect

A consequence of an agent’s action experienced by other agents that is not fully considered in the originating agent’s decision.

### External Shock

An event or change originating outside the agent or system being modeled that alters conditions, actions, or outcomes.

What constitutes an external shock depends on the boundary of the model. A change external to one agent or system may result from the actions of another agent in a broader system.

Examples include pandemics, natural disasters, wars, and sudden technological or resource disruptions.

### Imbalance

A state in which existing actions, conditions, or relationships create pressures that reduce the ability of the current system state to persist under prevailing conditions.

An imbalance may persist, grow, diminish, or be resolved as agents, institutions, and conditions change. Its presence does not by itself establish that a system is unstable or predict when the existing state will cease to persist.

### Equilibrium

A state in which no agent both has sufficient incentive and a feasible ability to change its current action, given existing information, constraints, and the actions of others.

### Reality

The objective conditions of the world that ultimately determine the consequences of actions, regardless of an agent's beliefs or expectations.

## 4. Axioms

The Theory of Economic Relativity rests on the following axioms.

### Axiom 1: Agent actions relate to objectives

Agent actions are selected in relation to one or more objectives.

### Axiom 2: Agents act on information and beliefs

Decisions depend on an agent's information, beliefs, and model of reality, which may be incomplete or incorrect.

### Axiom 3: Agents choose among perceived feasible actions

Agents choose among the actions they perceive as feasible and available for the decision process at the time of decision. The perceived feasible set may differ from what reality actually permits.

### Axiom 4: Agents evaluate actions relative to their objectives

Value is relative to an agent's objective. When actions or their consequences are evaluated within the decision process, their value is evaluated relative to the agent's objective.

Evaluation may be deliberate, bounded, heuristic, habitual, intuitive, or otherwise shaped by the agent's decision process. It does not require exhaustive comparison or perfect optimization.

### Axiom 5: Agents select actions through a decision process

The action selected is the action that results from the agent's decision process at that time, given its objective, information, beliefs, perceived feasible actions, valuations, and time horizon.

The selected action need not be objectively optimal or result from exhaustive comparison among alternatives.

### Axiom 6: Actions contribute to outcomes and external effects

Agent actions contribute to outcomes and may create external effects. Outcomes may also depend on interactions among agents, prevailing conditions, and external shocks.

### Axiom 7: Actions affect other agents

One agent's actions can change the information, constraints, incentives, or actual and perceived feasible actions of other agents.

### Axiom 8: Reality constrains consequences

Agents make decisions according to their understanding of reality, but reality ultimately determines the consequences of those decisions.

### Axiom 9: Infeasible continuation prevents persistence

When continuation of an existing state becomes infeasible under reality's constraints, that state cannot persist unchanged.

### Axiom 10: Realized outcomes shape subsequent decision environments

Subsequent decision environments are shaped by the economically relevant consequences of prior realized outcomes. When an outcome changes conditions relevant to a later decision, those changes are reflected in the subsequent decision environment.

## 5. Formal Architecture

### 5.1 Agent Decision Model

The Agent Decision Model describes how a single agent selects an action. It is the fundamental decision model of Economic Relativity, upon which the broader framework builds.

$$
C_{i,t}
=
D_{i,t}
\left(
\hat{F}_{i,t},
G_{i,t},
M_{i,t},
V_{i,t},
H_{i,t}
\right)
$$

Where:

- $i$ = the agent
- $t$ = the time of decision
- $a$ = a potential action
- $F_{i,t}$ = the set of actions actually feasible for agent $i$ at time $t$
- $\hat{F}_{i,t}$ = the set of actions agent $i$ perceives as feasible and available to its decision process at time $t$
- $G_{i,t}$ = the objective relevant to agent $i$'s decision at time $t$
- $M_{i,t}$ = the agent's model of reality at time $t$, including its information, beliefs, and expectations
- $H_{i,t}$ = the time horizon over which agent $i$ considers consequences relevant to the decision at time $t$
- $V_{i,t}(a)$ = the value agent $i$ assigns to action $a$ toward its objective at time $t$
- $D_{i,t}(\cdot)$ = the decision process through which agent $i$ evaluates and selects among perceived feasible actions at time $t$
- $C_{i,t}$ = the action selected by agent $i$ at time $t$

**Plain language**

An agent chooses from the actions it perceives as available based on its objective, understanding of reality, valuation of the alternatives, and relevant time horizon.

The selected action is the action that results from the agent’s decision process. This does not require the agent to identify the objectively best action or exhaustively compare every alternative.

TER does not require deterministic choice. A particular specification may define \(D\) as deterministic or stochastic.

Decision processes may include optimization, satisficing, heuristics, habits, intuition, or reflexive responses. When decisions involve uncertainty, agents may evaluate actions according to their expected value based on what they currently know and believe.

Optimization is therefore one possible decision process:

$$
D_{i,t}(\cdot)
=
\arg\max_{a \in \hat{F}_{i,t}}
E[V_{i,t}(a \mid G_{i,t}, M_{i,t}, H_{i,t})]
$$

but it is not required by Economic Relativity. The broader model requires only that an action is selected through the agent's decision process at that time.

The time horizon $H_{i,t}$ determines which future consequences the agent considers relevant to the current decision. The horizon may range from immediate consequences to outcomes extending years, generations, or beyond the agent's lifetime. Agents considering similar horizons may still value future consequences differently.

The perceived feasible set $\hat{F}_{i,t}$ may differ from the actual feasible set $F_{i,t}$. Agents may overlook available actions, incorrectly believe an action is possible, or discover new alternatives as information and constraints change.

This section directly reflects:

- **Axiom 1:** Agent actions relate to objectives → $G_{i,t}$
- **Axiom 2:** Agents act on information and beliefs → $M_{i,t}$
- **Axiom 3:** Agents choose among perceived feasible actions → $\hat{F}_{i,t}$
- **Axiom 4:** Agents evaluate actions relative to their objectives → $V_{i,t}$
- **Axiom 5:** Agents select actions through a decision process → $D_{i,t}$

Marginal analysis remains an important form of action evaluation within Economic Relativity. When relevant to the agent's decision process, agents may compare the expected marginal benefits and marginal costs of choosing more, less, or a different course of action. Marginal analysis is therefore a possible mechanism within $D_{i,t}$ rather than a requirement imposed on every decision.

### 5.2 Action to Outcome Model

The Action to Outcome Model describes how a selected action encounters reality and produces an outcome.

An agent selects an action from its perceived feasible set:

$$
C_{i,t} \in \hat{F}_{i,t}
$$

$$
C_{i,t} \in F_{i,t} \quad \text{or} \quad C_{i,t} \notin F_{i,t}
$$

$$
O_{i,t} = R(C_{i,t}, F_{i,t}, P_{i,t}, S_{i,t})
$$

Where:

- $i$ = the agent
- $t$ = the time period
- $C_{i,t}$ = the action selected by agent $i$ at time $t$
- $\hat{F}_{i,t}$ = the set of actions agent $i$ perceives as feasible at time $t$
- $F_{i,t}$ = the set of actions actually feasible for agent $i$ at time $t$
- $O_{i,t}$ = the realized outcome associated with the selected action
- $P_{i,t}$ = prevailing conditions affecting the outcome
- $S_{i,t}$ = external shocks affecting the outcome
- $R(\cdot)$ = the reality function that determines the realized outcome

**Plain language**

An agent chooses according to its understanding of what is possible, but reality determines whether the selected action can actually be carried out and what consequences follow.

When $\hat{F}_i$ and $F_i$ differ, an agent may select an action that is not actually feasible. The resulting failure, partial execution, or changed outcome becomes part of the realized outcome.

This section directly reflects:

- **Axiom 3:** Agents choose among perceived feasible actions
- **Axiom 6:** Actions contribute to outcomes and external effects
- **Axiom 8:** Reality constrains consequences

### 5.3 Multi Agent Model

The Multi Agent Model describes how the actions and interactions of multiple agents shape one another and produce system outcomes.

One agent's actions may change the conditions faced by other agents, including their information, incentives, constraints, actual feasible sets, and perceived feasible sets:

$$

(C_{1,t}, C_{2,t}, \ldots, C_{n,t})

\rightarrow

(F_{i,t+1}, \hat{F}_{i,t+1})

$$

The equation illustrates changes in feasible sets but does not imply that these are the only components of another agent's decision environment that interaction may affect.

Interactions may also create opportunities that agents could not achieve independently, including cooperation, exchange, specialization, and institutions.

System outcomes are then determined by:

$$

O_t = R(C_{1,t}, C_{2,t}, \ldots, C_{n,t}, P_t, S_t)

$$

These system outcomes may include external effects: consequences experienced by other agents that were not fully considered in the originating decisions.

Where:

- $O_t$ = system outcome at time $t$

- $C_{1,t}, C_{2,t}, \ldots, C_{n,t}$ = actions selected by agents $1$ through $n$ at time $t$

- $F_{i,t+1}$ = actual feasible set available to agent $i$ in the next period

- $\hat{F}_{i,t+1}$ = feasible set perceived by agent $i$ in the next period

- $P_t$ = prevailing conditions affecting the system at time $t$

- $S_t$ = external shocks affecting the system at time $t$

- $R(\cdot)$ = the reality function that determines the realized system outcome

- $t$ = time period

**Plain language**

Agents do not act in isolation. Their actions can expand, restrict, or alter the opportunities available to others. Cooperation among agents may also make actions possible that no individual agent could achieve alone.

System outcomes emerge from these interacting actions under prevailing conditions and external shocks, and may include external effects on other agents.

Actual feasibility remains constrained by reality and can change as interactions unfold. A multi-agent specification may represent those feasibility constraints explicitly when they are relevant to the system outcome.

This section directly reflects:

- **Axiom 6:** Actions contribute to outcomes and external effects

- **Axiom 7:** Actions affect other agents

- **Axiom 8:** Reality constrains consequences


### 5.4 State Persistence Constraint

The State Persistence Constraint describes the boundary condition governing whether an existing system state can continue unchanged under reality's constraints.

When continuation of an existing state is no longer feasible under reality's constraints, that state cannot persist unchanged:

$$

\text{continuation of the existing state no longer feasible under reality's constraints}

\Rightarrow

\text{existing state cannot persist unchanged}

$$

The conditions preventing continuation may arise from agent actions and interactions, institutions, markets, physical conditions, external shocks, changing feasible sets, or other factors that affect what reality permits.

An imbalance may persist, grow, diminish, or be resolved while the existing state remains feasible. Its presence does not by itself establish that the state cannot continue or predict when a change will occur.

This constraint does not specify what state follows or the mechanism through which change occurs. Subsequent outcomes may emerge through agent decisions, interactions, changing feasibility, external shocks, institutional processes, physical processes, and feedback represented elsewhere in TER.

The resulting state may represent equilibrium, continued imbalance, instability, transformation, failure, or another outcome permitted by the conditions that follow.

**Plain language**

Economic systems can continue through changing and imperfect conditions while their existing state remains feasible.

But when reality's constraints make continuation of that state no longer feasible, the state cannot persist unchanged.

An imbalance may contribute to this condition, persist through it, or be unrelated to what makes continuation infeasible. Imbalance by itself does not force correction.

TER does not specify a universal response to infeasible continuation. What follows depends on the agents, interactions, conditions, constraints, shocks, and other processes that determine subsequent outcomes.

This section directly reflects:

- **Axiom 8:** Reality constrains consequences

- **Axiom 9:** Infeasible continuation prevents persistence

### 5.5 Dynamic Feedback Model

The Dynamic Feedback Model describes how realized outcomes can alter one or more components of subsequent decision environments.

Realized outcomes become part of the conditions shaping subsequent decisions. The feedback represented here is path dependent: later decision environments reflect the consequences of prior outcomes, while prevailing conditions and external shocks may also affect what is realized as the system evolves.

$$
O_t
\rightarrow
(G_{i,t+1}, M_{i,t+1}, F_{i,t+1}, \hat{F}_{i,t+1}, V_{i,t+1}, H_{i,t+1}, D_{i,t+1})
\rightarrow
C_{i,t+1}
\rightarrow
O_{t+1}
$$

Where:

- $O_t$ = realized outcome at time $t$
- $G_{i,t+1}$ = objective relevant to agent $i$'s decision in the next period
- $M_{i,t+1}$ = agent $i$'s model of reality in the next period
- $F_{i,t+1}$ = actual feasible set available to agent $i$ in the next period
- $\hat{F}_{i,t+1}$ = feasible set perceived by agent $i$ in the next period
- $V_{i,t+1}$ = valuation of actions relative to the agent's objective in the next period
- $H_{i,t+1}$ = time horizon considered by agent $i$ in the next period
- $D_{i,t+1}$ = decision process used by agent $i$ in the next period
- $C_{i,t+1}$ = action selected by agent $i$ in the next period
- $O_{t+1}$ = resulting outcome in the next period
- $t$ = time period

**Plain language**

Outcomes may change the conditions agents face and may change how agents understand, value, and respond to those conditions. As objectives, models of reality, actual and perceived feasible actions, valuations, time horizons, and decision processes evolve, agents make new decisions that produce new outcomes.

Experience may bring $\hat{F}_i$ closer to $F_i$, reveal previously unknown actions, change how alternatives are valued, or change how an agent makes decisions. Agent actions, interactions, external shocks, and changing conditions may also alter $F_i$ itself.

This section directly reflects:

- **Axiom 2:** Agents act on information and beliefs
- **Axiom 7:** Actions affect other agents
- **Axiom 8:** Reality constrains consequences
- **Axiom 10:** Realized outcomes shape subsequent decision environments

### 5.6 Feedback Analysis and Stability

The Dynamic Feedback Model describes how realized outcomes can alter subsequent decision environments. The strength, structure, and consequences of those feedback relationships may be analyzed using methods appropriate to the TER specification being studied.

Feedback may differ in:

- **sensitivity:** how strongly one component responds to another
- **amplification:** whether changes become larger through feedback
- **damping:** whether changes diminish over time
- **propagation:** how changes spread across agents or the system
- **persistence:** how long effects remain significant
- **oscillation:** whether responses repeatedly change direction
- **threshold effects:** whether sufficiently large changes produce different behavior
- **changing feedback regimes:** whether the feedback relationships themselves change as conditions change

TER does not require one universal mathematical representation of these dynamics.

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

Here, $\mathbf{Z}_t$ and $\Phi_t$ are analytical constructions defined by the particular specification. They are not TER primitives and do not imply that TER requires a universal economic state variable or law of motion.

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

**Plain language**

Economic feedback can vary greatly in strength and structure.

A realized outcome may have little effect on subsequent decisions or may propagate through many agents and institutions. Changes may be amplified or damped, disappear quickly or persist, and contribute to convergence, divergence, oscillation, thresholds, or changing patterns of behavior.

TER does not prescribe a universal stability equation or analytical method. Researchers should use methods appropriate to the particular economic relationships represented in the TER specification.

State-space models, Jacobians, eigenvalue analysis, simulation, and related methods can be useful when the underlying specification supports them, but these are analytical tools rather than additional components of TER.

Importantly, amplification alone does not imply instability or imbalance. Strong feedback may accompany productive growth, technological adoption, coordination, speculation, adaptation, or destabilization. Its economic significance depends on the underlying agents, conditions, interactions, constraints, and whether the resulting path remains feasible under reality's constraints.

This section directly reflects:

- **Axiom 6:** Actions contribute to outcomes and external effects
- **Axiom 7:** Actions affect other agents
- **Axiom 8:** Reality constrains consequences
- **Axiom 9:** Infeasible continuation prevents persistence
- **Axiom 10:** Realized outcomes shape subsequent decision environments
- **Model 5.5:** Dynamic Feedback Model


## 6. Consolidated Principles

### 6.1 Agent Objective

Agents make decisions in relation to objectives. Those objectives shape how agents value potential actions.

Many established economic concepts describe different forms of this process. Utility and preferences describe how consumers value alternatives. Profit maximization describes firms evaluating actions relative to profit. Incentives change the relative value of potential actions, while expected value provides one way agents may evaluate actions under uncertainty.

In the Agent Decision Model:

$$
C_{i,t}
=
D_{i,t}
\left(
\hat{F}_{i,t},
G_{i,t},
M_{i,t},
V_{i,t},
H_{i,t}
\right)
$$

the objective $G_{i,t}$ provides the reference against which value $V_{i,t}$ is evaluated at time $t$. The time horizon $H_{i,t}$ determines which future consequences the agent considers relevant to that decision.

The same architecture can represent consumers pursuing utility, firms pursuing profit, governments pursuing stability, or other agents pursuing different objectives without requiring them to use the same decision process.

This principle is primarily supported by:

- **Axiom 1:** Agent actions relate to objectives
- **Axiom 3:** Agents choose among perceived feasible actions
- **Axiom 4:** Agents evaluate actions relative to their objectives
- **Axiom 5:** Agents select actions through a decision process
- **Model 5.1:** Agent Decision Model

Value is relative to the agent's objective. The same action, resource, or outcome may therefore have different value to different agents, or to the same agent pursuing a different objective.


### 6.2 Feasible Set and Constraints

Agents choose among actions they perceive as feasible, while reality determines which actions are actually feasible.

Scarcity is a fundamental source of constraints. Limited resources such as time, capital, labor, technology, and natural resources restrict what an agent can actually do. Budget and production constraints are specific examples of these limits.

In the Agent Decision Model:

$$
C_{i,t}
=
D_{i,t}
\left(
\hat{F}_{i,t},
G_{i,t},
M_{i,t},
V_{i,t},
H_{i,t}
\right)
$$

the perceived feasible set $\hat{F}_{i,t}$ represents the actions the agent believes are available to its decision process at time $t$. The actual feasible set $F_{i,t}$ represents the actions reality permits given the agent's constraints at that time. These sets may differ and may change over time.

Choosing among competing alternatives creates opportunity costs. Because agents face different resources, capabilities, and constraints, they may also face different opportunity costs. These differences can create comparative advantage and opportunities for mutually beneficial trade.

Interactions with other agents can also change what is feasible. Cooperation, exchange, specialization, and institutions may expand or restrict the actions available to an agent. Institutions can further shape feasible sets through laws, rules, property rights, contracts, and other structures.

This principle is primarily supported by:

- **Axiom 2:** Agents act on information and beliefs
- **Axiom 3:** Agents choose among perceived feasible actions
- **Axiom 5:** Agents select actions through a decision process
- **Axiom 7:** Actions affect other agents
- **Axiom 8:** Reality constrains consequences
- **Models 5.1, 5.2, and 5.3:** Agent Decision, Action to Outcome, and Multi Agent Models

Scarcity and constraints determine what is actually possible, while information and beliefs shape what agents perceive as possible. Differences in constraints and interactions among agents give rise to opportunity costs, comparative advantage, trade, and changing feasible sets.


### 6.3 Agent Model of Reality

Agents make decisions according to their understanding of reality, which may differ from reality itself.

Information, beliefs, assumptions, expectations, and interpretations form the agent's model of reality, $M_{i,t}$, at the time of decision. Information economics, expectations, behavioral economics, bounded rationality, and learning describe different aspects of how agents form, use, and update this model.

In the Agent Decision Model:

$$
C_{i,t}
=
D_{i,t}
\left(
\hat{F}_{i,t},
G_{i,t},
M_{i,t},
V_{i,t},
H_{i,t}
\right)
$$

the agent's decision process uses $M_{i,t}$ as part of the environment from which an action is selected, while $\hat{F}_{i,t}$ represents the actions perceived as available. Neither the agent's model of reality nor its perceived feasible set must perfectly correspond to reality.

This distinction allows Economic Relativity to represent both highly informed and imperfect decision making. An agent may have incomplete information, incorrect beliefs, biased expectations, limited ability to evaluate alternatives, or an inaccurate understanding of what actions are available.

The agent's valuation and decision process may also be shaped by reference points, framing, heuristics, biases, and subjective beliefs. Bounded rationality and behavioral effects therefore operate within the agent's decision architecture rather than as exceptions to it.

Outcomes can provide new information that changes the agent's model of reality. Those changes may also affect the actions the agent perceives as feasible, but TER does not require changes in perceived feasibility to occur through a single pathway.

Learning does not require convergence toward perfect knowledge. Agents may update correctly, incorrectly, partially, or not at all.

This principle is primarily supported by:

- **Axiom 2:** Agents act on information and beliefs
- **Axiom 3:** Agents choose among perceived feasible actions
- **Axiom 4:** Agents evaluate actions relative to their objectives
- **Axiom 8:** Reality constrains consequences
- **Axiom 10:** Realized outcomes shape subsequent decision environments
- **Models 5.1, 5.2, and 5.5:** Agent Decision, Action to Outcome, and Dynamic Feedback Models

Economic Relativity does not require agents to understand reality correctly. It requires only that their decisions depend on the model of reality from which they act, while the consequences of those decisions remain constrained by reality.


### 6.4 Action Selection

Agents select actions through decision processes shaped by their objectives, information, beliefs, perceived feasible actions, valuations, and time horizons.

In the Agent Decision Model:

$$
C_{i,t}
=
D_{i,t}
\left(
\hat{F}_{i,t},
G_{i,t},
M_{i,t},
V_{i,t},
H_{i,t}
\right)
$$

the decision process $D_{i,t}$ determines how the agent evaluates and selects among perceived feasible actions. Different agents, or the same agent under different conditions, may use different decision processes.

These processes may include optimization, satisficing, heuristics, habits, intuition, reflexive responses, strategic reasoning, or other mechanisms. The selected action therefore need not represent the objectively optimal action or result from exhaustive comparison among alternatives.

Marginal analysis remains an important special case. When relevant to the decision process, agents may compare the expected marginal benefits and marginal costs of choosing more, less, or a different course of action. Cost benefit analysis and optimization under constraints represent related forms of action evaluation.

Because action selection depends on the agent's model of reality, perceived feasible set, valuations, and time horizon, the considerations driving the selected action may differ from the consequences ultimately realized.

This principle is primarily supported by:

- **Axiom 1:** Agent actions relate to objectives
- **Axiom 2:** Agents act on information and beliefs
- **Axiom 3:** Agents choose among perceived feasible actions
- **Axiom 4:** Agents evaluate actions relative to their objectives
- **Axiom 5:** Agents select actions through a decision process
- **Axiom 8:** Reality constrains consequences
- **Models 5.1 and 5.2:** Agent Decision and Action to Outcome Models

Economic Relativity therefore provides a common architecture for action selection without requiring a universal decision algorithm. Marginal analysis, optimization, and other established decision mechanisms may operate within that architecture when appropriate.


### 6.5 Outcomes and System Effects

Economic outcomes emerge from the actions and interactions of agents under prevailing conditions. As agents affect one another, individual decisions can contribute to market and system level outcomes that no single agent determines independently.

Supply and demand describe aggregate patterns generated by buyers and sellers making individual decisions. Their interactions produce prices and quantities, while those prices become information and conditions that influence subsequent decisions.

In the Multi Agent Model:

$$
O_t = R(C_{1,t}, C_{2,t}, \ldots, C_{n,t}, P_t, S_t)
$$

the system outcome $O_t$ emerges from interacting agent actions, prevailing conditions, and external shocks, and may include external effects on other agents.

Externalities arise when an agent's action creates consequences for other agents that are not fully considered in the originating agent's decision. Individually selected actions may therefore produce outcomes that conflict with the objectives of other agents or the broader system. When such outcomes are inefficient relative to a specified welfare criterion, economics may describe them as market failures.

Because agents and markets are interconnected, changes in one part of an economic system can alter the information, constraints, opportunities, and decisions of agents elsewhere. General equilibrium studies these interdependencies, while macroeconomic aggregation examines how individual actions and interactions contribute to economy wide outcomes.

System outcomes also feed back into future agent decisions. Prices, employment, production, income, institutions, and other aggregate conditions may change what agents know, what they can do, what time horizons they consider relevant, how they value alternatives, and how subsequent decisions are made.

This principle is primarily supported by:

- **Axiom 2:** Agents act on information and beliefs
- **Axiom 6:** Actions contribute to outcomes and external effects
- **Axiom 7:** Actions affect other agents
- **Axiom 8:** Reality constrains consequences
- **Axiom 10:** Realized outcomes shape subsequent decision environments
- **Models 5.2, 5.3, and 5.5:** Action to Outcome, Multi Agent, and Dynamic Feedback Models

Markets and macroeconomic outcomes are therefore not independent starting points in Economic Relativity. They emerge from interacting agent decisions and the conditions under which those decisions occur, while the resulting system outcomes become part of the conditions shaping future decisions.

Institutions participate in this feedback process. They may emerge from agent interactions and collective action, while also shaping the information, incentives, constraints, and actual and perceived feasible sets that influence subsequent agent decisions. Agents may also act to create, preserve, modify, or remove institutions, further changing the decision environment faced by themselves and others.


### 6.6 Persistence and Change Over Time

Economic systems evolve as agents respond to changing outcomes, information, constraints, institutions, time horizons, and external shocks.

An equilibrium represents a state in which no agent both has sufficient incentive and a feasible ability to change its current action, given existing information, constraints, and the actions of others. It does not imply that the state is dynamically stable, optimal, permanent, or desirable to every agent.

Changes in these conditions may create sufficient incentive or ability for agents to change their actions, disrupting the existing equilibrium. The actions that sustain an equilibrium may themselves alter the conditions on which that equilibrium depends, allowing stability to generate endogenous change or instability over time.

The State Persistence Constraint states:

$$

\text{continuation of the existing state no longer feasible under reality's constraints}

\Rightarrow

\text{existing state cannot persist unchanged}

$$

An imbalance may persist, grow, diminish, or be resolved as agents, institutions, and conditions change. Its presence does not by itself establish that the existing state cannot continue or predict when state change will occur.

When continuation does become infeasible, TER does not prescribe a universal transition mechanism or resulting state. Subsequent outcomes may arise through agent decisions and interactions, changing feasible sets, institutional processes, external shocks, physical processes, and the feedback represented elsewhere in the framework.

The resulting change may produce equilibrium, continued imbalance, instability, transformation, failure, or another state permitted by reality's constraints.

External shocks can also change outcomes and conditions. Whether a change is external depends on the boundary of the system being modeled: what appears as an external shock to one agent or system may be the result of another agent's decision in a broader model.

Changes in outcomes and conditions may alter objectives, information, actual and perceived feasible sets, valuations, time horizons, decision processes, institutions, and subsequent actions.

The resulting feedback may dampen or amplify change. Amplification alone does not imply instability or imbalance. Strong feedback may accompany productive growth, adaptation, coordination, or destabilization depending on the underlying conditions and whether the resulting path remains feasible under reality's constraints.

Productivity, technology, capital, knowledge, cooperation, and institutional change can transform what agents and systems are capable of achieving. Growth can therefore involve changes in actual feasible sets, while learning can reveal possibilities that were already feasible but previously unknown.

This principle is primarily supported by:

- **Axiom 2:** Agents act on information and beliefs
- **Axiom 3:** Agents choose among perceived feasible actions
- **Axiom 6:** Actions contribute to outcomes and external effects
- **Axiom 7:** Actions affect other agents
- **Axiom 8:** Reality constrains consequences
- **Axiom 9:** Infeasible continuation prevents persistence
- **Axiom 10:** Realized outcomes shape subsequent decision environments
- **Sections 5.3, 5.4, 5.5, and 5.6:** Multi Agent Model, State Persistence Constraint, Dynamic Feedback Model, and Feedback Analysis and Stability

Economic systems therefore do not necessarily move toward a single optimal or permanent equilibrium. They evolve as agents, institutions, conditions, outcomes, and reality interact over time.

## 7. TER Contributions and Claims

The Theory of Economic Relativity (TER) is proposed as a general framework for describing economic decision making, interaction, and change.

TER incorporates established findings from economics, including constrained choice, marginal analysis, bounded rationality, asymmetric information, strategic interaction, institutions, externalities, heterogeneous agents, feedback, and dynamic adjustment. TER does not claim these underlying concepts as novel.

Its central contribution is the hypothesis that these mechanisms can be organized within a common agent centered architecture and applied consistently across different economic problems, agents, and levels of analysis.

Consistent with this architecture, TER proposes the following broad definition of economics:

> **Economics is the study of how agents make decisions, how their actions interact with other agents and reality's constraints, and how the resulting outcomes shape economic systems over time.**

This definition does not reject scarcity based definitions of economics. Scarcity remains a fundamental source of constraints, tradeoffs, and opportunity costs within economic systems. The broader definition reflects TER's hypothesis that economic analysis also encompasses information, beliefs, institutions, strategic interaction, external effects, feedback, and dynamic change within a common agent centered architecture.

The following are the principal contributions and claims of TER.

### 7.1 A Common Agent Decision Architecture

TER proposes that economically relevant agent decisions can be represented through a common conceptual architecture involving:

- objectives
- models of reality, including information and beliefs
- actual feasible actions
- perceived feasible actions
- valuations
- time horizons
- decision processes

Conceptually:

$$
C_{i,t}
=
D_{i,t}
(
\hat F_{i,t},
G_{i,t},
M_{i,t},
V_{i,t},
H_{i,t}
)
$$

TER does not require agents to share the same decision rule. The decision process may involve optimization, satisficing, heuristics, habits, intuition, reflexive behavior, strategic reasoning, or other mechanisms.

The claim is therefore not that all agents behave identically, but that heterogeneous economic behavior can be analyzed through a common underlying architecture.

### 7.2 Common Architecture Does Not Imply a Common Decision Algorithm

TER separates the structure of an economic decision from the particular process through which an agent selects an action.

Two agents may face similar conditions while using different decision processes and therefore choose different actions.

Likewise, the same agent may use different decision processes under different conditions.

This allows optimization, behavioral decision making, bounded rationality, heuristics, strategic behavior, and other established approaches to operate within the same broader framework rather than requiring one universal model of rationality.

### 7.3 Perceived Reality and Reality Have Distinct Economic Roles

TER explicitly distinguishes an agent's model of reality from reality itself.

Agents act according to the information, beliefs, assumptions, expectations, and interpretations represented in:

$$
M_{i,t}
$$

This model may be incomplete or incorrect.

Economic consequences, however, remain constrained by reality.

TER therefore proposes the general distinction:

> Economic behavior is shaped by perceived reality, while economic consequences are constrained by reality.

This allows TER to represent mistaken beliefs, uncertainty, asymmetric information, expectations, learning, surprise, and prediction error without assuming that agents possess complete knowledge of the economic system.

### 7.4 Perceived and Actual Feasible Sets Are Distinct

TER explicitly distinguishes:

$$
F_{i,t}
$$

the actions actually feasible to an agent, from:

$$
\hat F_{i,t}
$$

the actions the agent perceives as feasible and available to its decision process.

Therefore:

$$
a \in F_{i,t}, \quad a \notin \hat F_{i,t}
$$

represents an available action the agent does not perceive, while:

$$
a \in \hat F_{i,t}, \quad a \notin F_{i,t}
$$

represents an action the agent believes possible but that reality does not permit.

This distinction allows discovery, misinformation, technological change, institutional knowledge, mistaken opportunities, hidden constraints, and learning to be represented within the same architecture.

### 7.5 Decisions, Consequences, and Future Decisions Form a Common Dynamic Structure

TER connects decisions to realized outcomes and subsequent decisions:

Conceptually:

$$

(G,M,\hat F,V,H,D)_t
\rightarrow
C_t

$$

$$

(C_t,F_t,P_t,S_t)
\rightarrow
O_t

$$

$$

O_t
\rightarrow
(G,M,F,\hat F,V,H,D)_{t+1}

$$

where an outcome may alter one or more components of the subsequent decision environment.

An outcome may change an agent's objectives, model of reality, actual or perceived feasible actions, valuations, time horizon, or future decision process.

TER therefore treats economic activity as an evolving feedback process rather than a sequence of isolated decisions.

The strength and structure of this feedback may vary. Responses may be amplified or damped, temporary or persistent, localized or propagated across agents and institutions. TER does not assume a universal feedback coefficient or stability constant.

### 7.6 Agent Interaction Connects Microeconomic Decisions to System Outcomes

TER extends the same architecture to interacting agents.

Actions taken by one agent may alter the information, incentives, constraints, opportunities, or outcomes experienced by other agents.

Conceptually:

$$
\{C_{i,t}\}_{i=1}^{n}
\rightarrow
O_t
\rightarrow
\{G,M,F,\hat F,V,H,D\}_{i,t+1}
$$

Aggregate outcomes therefore emerge from heterogeneous agent actions and interactions under prevailing conditions, and subsequently become part of the environment affecting future decisions.

TER does not imply that aggregate outcomes must be analytically simple or directly inferable from individual decisions. Complex and emergent behavior may arise from interaction itself.

### 7.7 Established Economic Theories May Be Represented Within a Common Framework

TER hypothesizes that mechanisms described by many established economic theories may be represented as particular configurations, relationships, or processes within the broader TER architecture.

Examples include:

- asymmetric information through differences in $M_i$
- bounded rationality through $M_i$, $\hat F_i$, and $D_i$
- strategic interaction through interdependent agent decisions
- institutions through their effects on feasible actions, information, incentives, and decision processes
- technological innovation through changes in actual or perceived feasible actions
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

### 7.9 TER Is a Framework for Analysis, Not an Omniscient Prediction System

TER does not assume that an observer can know every objective, belief, constraint, interaction, external effect, future action, or shock within an economic system.

Researchers themselves are agents operating with incomplete information.

A particular TER model is therefore a specification of the framework using the information, assumptions, and methods available to the researcher.

TER may be used to explain observed decisions and outcomes, identify economic mechanisms, compare possible responses, construct conditional predictions, and evaluate how changes may propagate through a system.

The framework does not imply perfect prediction. In particular, the presence of amplification, imbalance, or fragility does not by itself establish when a system state will change or which outcome will follow.

### 7.10 TER Is an Open and Testable Framework

TER is intended to remain testable, extensible, and subject to revision.

Its claims should be challenged by attempting to:

- identify economically meaningful phenomena that cannot be represented without violating TER's assumptions
- identify internal contradictions within the framework
- demonstrate that a foundational claim is inconsistent with empirical evidence
- show that a proposed TER variable or mechanism is unnecessary or incorrectly specified
- reproduce established economic results using TER
- derive and test hypotheses from particular TER specifications
- propose alternative frameworks with greater explanatory power or fewer necessary assumptions

The ability to represent an observed outcome is not by itself evidence that a particular TER explanation is correct. Individual TER specifications should constrain their assumptions using available evidence and derive implications that can be compared with observations, competing specifications, or counterfactual results.

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

Agents act in relation to objectives through decision processes shaped by their information, beliefs, perceived feasible actions, valuations, and time horizons. Agents may use different decision processes, and the actions they perceive as feasible may differ from those reality actually permits.

Selected actions interact with reality and with the actions of other agents to produce outcomes. These outcomes can alter the conditions of future decisions, creating feedback that may amplify, dampen, persist, propagate, or change over time.

Through these interactions, individual decisions contribute to markets, institutions, and broader economic outcomes. Complex system behavior may emerge that no individual agent intended or controls.

Reality ultimately constrains what actions and conditions can persist. When continuation of an existing state becomes infeasible under reality's constraints, that state cannot persist unchanged. What follows depends on the particular agents, institutions, conditions, constraints, shocks, and interactions involved.

In short:

> Economic behavior emerges from agents acting in relation to objectives through heterogeneous decision processes within a common underlying architecture. Their actions encounter reality, interact with other agents, produce outcomes, and reshape future decision environments. Economic systems therefore evolve through the continuing interaction of agent decisions, feedback, and reality.

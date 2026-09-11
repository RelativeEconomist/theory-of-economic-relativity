# Theory of Economic Relativity

> **Economic outcomes emerge from agent decisions interacting with reality.**

The **Theory of Economic Relativity (TER)** is an open economic theory and analytical framework for explaining how agent decisions, interactions, constraints, and realized outcomes combine to produce economic behavior and change over time.

TER proposes that many economic phenomena traditionally studied through separate models and theories can be understood as different configurations and dynamics of a **common agent centered architecture**.

At its core, TER models agents acting in relation to objectives through decision processes shaped by their information, beliefs, perceived feasible actions, valuations, and time horizons. Selected actions then encounter reality, interact with other agents, and produce realized outcomes that may reshape future decision environments.

This creates a common structure for studying mechanisms such as constrained choice, asymmetric information, bounded rationality, strategic interaction, institutions, externalities, markets, equilibrium, and dynamic feedback while keeping their specific assumptions and mechanisms explicit.

TER is built on established economics, but its central claim is stronger than simple compatibility:

> **Many economic phenomena traditionally described through separate models and theories can be understood as different configurations and dynamics of a common agent centered economic architecture.**

That claim is intended to be tested.

This repository contains the canonical theory, an executable TER research framework, and a growing suite of replication and adversarial tests designed to reproduce established economic results, expose weaknesses, identify counterexamples, and test the limits of the framework.

TER is open for researchers, economists, programmers, and students to **use, challenge, reproduce, falsify, and improve**.

> **Canonical theory:** [`theory/academic.md`](theory/academic.md) is the source of truth for TER's definitions, axioms, models, claims, and limitations.

**Website:** https://www.theoryofeconomicrelativity.com

**DOI:** https://doi.org/10.5281/zenodo.22711351

## Where to Go

| I want to... | Go here |
| --- | --- |
| Understand TER | This README |
| Read the canonical theory | [`theory/academic.md`](theory/academic.md) |
| Build or reason about a TER model | [`research/README.md`](research/README.md) |
| Review variable boundaries and modeling discipline | [`research/ter-methodology-notes.md`](research/ter-methodology-notes.md) |
| See executable examples | [`research/tests/`](research/tests/) |
| Run the research code | [Getting Started](#getting-started) below |
| Contribute | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Table of Contents

- [Where to Go](#where-to-go)
- [The Core Idea](#the-core-idea)
- [The TER Architecture](#the-ter-architecture)
- [From Decisions to Economic Systems](#from-decisions-to-economic-systems)
- [What TER Is Testing](#what-ter-is-testing)
- [Research and Replication Tests](#research-and-replication-tests)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Contributing and Criticism](#contributing-and-criticism)
- [Project Status](#project-status)
- [License](#license)

## The Core Idea

TER asks whether many economic phenomena traditionally described through separate models and theories can be understood as different configurations and dynamics of a common agent centered architecture.

A key distinction within that architecture is:

> **Agents make decisions according to their perceived reality, while reality constrains the consequences of those decisions.**

An agent may be an individual, household, business, nonprofit, government, institution, or coordinated group.

Agents may differ in objectives, information, beliefs, constraints, valuations, time horizons, and decision processes. TER does **not** assume that every agent optimizes or follows the same decision process algorithm.

At a high level:

```text
Agent
  ↓
Objectives + perceived reality + perceived feasible actions
  ↓
Decision process
  ↓
Selected action
  ↓
Reality + other agents + prevailing conditions
  ↓
Outcome
  ↓
Feedback and adjustment
  ↓
Next decision environment
```

This architecture can be applied from a single decision to interacting agents and evolving economic systems.

## The TER Architecture

TER represents the selected action of agent $i$ at time $t$ as:

$$ C_{i,t} = D_{i,t}(\hat{F}_{i,t}, G_{i,t}, M_{i,t}, V_{i,t}, H_{i,t}) $$

In plain language, an agent selects an action through a decision process shaped by:

| Symbol | Meaning |
| --- | --- |
| $G$ | Objective |
| $M$ | Model of reality, including information and beliefs |
| $F$ | Actual feasible actions |
| $\hat{F}$ | Perceived feasible actions |
| $V$ | Valuation of actions relative to the agent's objective |
| $H$ | Time horizon |
| $D$ | Decision process used to select among perceived feasible actions |
| $C$ | Selected action |
| $O$ | Realized outcome |

> **Quick reference** — the canonical definitions, with full notation and time indices, are in [`theory/academic.md`](theory/academic.md#3-core-definitions).

The selected action is simply the action that wins the agent's decision process. That process may involve optimization, satisficing, heuristics, habits, intuition, strategic reasoning, or another mechanism.

The distinction between $F$ and $\hat{F}$ is especially important. An agent may believe an action is possible when reality does not permit it, or fail to recognize an opportunity that actually exists.

The selected action then encounters reality:

$$ C_{i,t} \rightarrow O_{i,t} $$

Outcomes may depend on actual constraints, other agents, prevailing conditions, external effects, and external shocks. Those outcomes can then change future information, beliefs, feasible actions, valuations, time horizons, decision processes, and subsequent actions.

For the formal definitions, axioms, and equations, see [`theory/academic.md`](theory/academic.md).

## From Decisions to Economic Systems

TER develops this architecture through three core models, a state persistence constraint, a dynamic feedback model, and optional analytical methods for studying feedback and stability.

1. **Agent Decision** — how an agent selects an action.
2. **Action to Outcome** — how the selected action encounters actual conditions.
3. **Multi Agent** — how interacting decisions produce system outcomes.
4. **State Persistence Constraint** — the boundary condition for when an existing state can no longer persist unchanged under reality's constraints.
5. **Dynamic Feedback** — how outcomes alter future decision environments.
6. **Feedback Analysis and Stability** — how feedback may amplify, damp, propagate, persist, oscillate, or change across regimes.

These models are not six separate theories. They describe different layers of the same framework.

The complete formal treatment is in [`theory/academic.md`](theory/academic.md#5-formal-architecture).

## What TER Is Testing

TER's central research direction is whether established economic mechanisms can be represented as configurations and dynamics of this common architecture without erasing the assumptions that make those mechanisms distinct.

The framework is intentionally broad, but it is not intended to explain everything by definition.

TER does not assume that agents are perfectly rational, that markets reach equilibrium, that adjustment improves a system, that perceived reality is accurate, or that economic systems are universally predictable.

The theory is meant to be challenged through replication, counterexamples, simulation, empirical work, and comparison with established economics.

## Research and Replication Tests

TER includes an executable Python research framework under [`research/ter/`](research/ter/) and a replication suite under [`research/tests/`](research/tests/).

The numbered tests currently reproduce economic concepts and mechanisms including:

- choice under constraints and bounded rationality
- asymmetric information
- strategic interaction and coordination
- supply, demand, and elasticity
- externalities
- bank runs and speculative feedback
- opportunity cost and incentives
- public goods and market power
- comparative advantage
- consumer, producer, and total surplus
- intertemporal choice and time horizon
- learning and changing perceived feasible sets
- unsustainable imbalance and forced adjustment
- oscillatory feedback through a cobweb model

The purpose is not to claim that passing these tests proves TER. The tests ask a narrower and more useful question: **can the framework reproduce established economic behavior while preserving the theory's stated architecture?**

The suite also includes framework contract tests that protect TER Core behavior and researcher-facing infrastructure.

## Repository Structure

```text
theory/
  academic.md          Canonical TER specification

research/
  ter/                 Executable TER research framework
  tests/               Economic replication and framework tests

run_tests.py           Test runner
CONTRIBUTING.md        Contributor workflow
LICENSE                CC BY 4.0 research and content license
LICENSE-SOFTWARE       MIT software license
LICENSE-SCOPE.txt      License scope
```

The academic specification takes precedence over implementations, examples, tests, website content, and explanatory material.

## Getting Started

You can explore TER directly on GitHub, or clone the repository locally to run the framework and replication tests.

1. Clone the repository.
2. Open it in your preferred code editor.
3. Make sure Python 3 is installed.
4. Run the research suite:

```bash
python3 run_tests.py
```

Run a single replication test:

```bash
python3 run_tests.py research/tests/test_24_cobweb_oscillation.py
```

### Explore the implementation

A useful starting path is:

```text
research/ter/agent.py
research/ter/decision.py
research/ter/scenario.py
research/ter/runner.py
research/ter/rules.py
research/ter/outcome.py
research/ter/system.py
```

The framework separates TER's common architecture from scenario-specific economics. Specialized assumptions belong in configurations or rules rather than being silently promoted into universal TER claims.

### Read the theory

Start with this README for the architecture and repository, then use [`theory/academic.md`](theory/academic.md) when you need the complete definitions, axioms, formal models, claims, and limitations.

## Contributing and Criticism

TER is an open research project. Contributions do not need to agree with the theory.

Useful contributions include:

- replicate another established economic result
- identify a case TER cannot represent cleanly
- find an inconsistency between the theory and TER Core
- test a boundary or counterexample
- improve the research framework
- improve documentation or reproducibility
- challenge a definition, axiom, model, or claim with a concrete argument

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the test and contribution workflow.

Criticism is valuable when it makes the framework more precise, more falsifiable, or easier to compare with established economics.

## Project Status

TER is under active development and public testing.

The current research baseline includes **24 numbered economic replication tests** plus framework contract tests. The project is continuing to expand replication coverage, simulation capability, documentation, and public research tooling.

The theory itself remains governed by [`theory/academic.md`](theory/academic.md). Implementation convenience should not silently change the theory.

## Author’s Note

Humanity expands its feasible set by pursuing difficult goals through fair competition, institutions, cooperation, knowledge sharing, and scientific exploration.

That perspective is personal and separate from TER’s formal theory.

TER is open so others can use it, challenge it, reproduce it, and improve it through open science and engineering.

## License

TER uses separate licenses for its research content and software:

- **Theory, research, documentation, and other non-software content:** [CC BY 4.0](LICENSE)
- **TER Core and supporting software:** [MIT License](LICENSE-SOFTWARE)

You are encouraged to study, test, share, adapt, and build upon TER. See the respective license files for the complete terms.

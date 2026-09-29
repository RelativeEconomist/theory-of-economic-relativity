# Frequently Asked Questions and Challenges

This document addresses recurring conceptual and methodological questions researchers raise when they first specify or challenge a TER model. It is explanatory only. Where anything here ever conflicts with the canonical specification, [`theory/academic.md`](../theory/academic.md) wins.

## Is TER a theory or a framework?

Both.

The theory is the set of definitions, axioms, and models that describe how agents, decisions, reality, outcomes, and feedback relate.

The framework is the general economic architecture those definitions, axioms, and models establish. TER’s methodology, software, and test suite are how that architecture is specified, implemented, tested, and applied in practice.

TER is still open to testing, criticism, and revision. Calling it a theory does not mean it is settled, and calling it a framework does not reduce it to software or documentation.

## Can TER explain anything after the fact?

No — representational breadth is not the same as explanatory success. TER's ability to represent an observed outcome does not, by itself, validate a particular explanation of that outcome.

Observed action `C` alone does not identify `G`, `M`, `F̂`, `V`, `H`, or `D` — different underlying mechanisms can produce the same observed action. A defensible specification should constrain its assumptions before, or independently of, the outcome being explained wherever possible, and competing specifications should then be compared using observations, subsequent behavior, experiments, counterfactuals, or other testable implications.

See [§7.10](../theory/academic.md#710-ter-is-an-open-and-testable-framework) and [`ter-methodology-notes.md`](ter-methodology-notes.md).

## Can a researcher just change the objective `G` to explain an observed action?

No. Changing `G` after observing an action may produce a representation that fits, but it does not establish that the objective was actually responsible for the action.

`G` — like `M`, `F̂`, `V`, `H`, and `D` — is part of a specification, not a free parameter to be adjusted until the observed action fits. As the previous answer notes, TER treats a rival explanation as a *competing specification*, to be constrained by independent evidence, rather than a rewrite of the same specification's `G`.

See [`ter-methodology-notes.md`](ter-methodology-notes.md), particularly the guidance against inferring components from `C` alone and against post hoc fitting.

## Is TER falsifiable?

At the level of an individual specification: yes. A specification should generate hypotheses and implications that can fail against evidence — see the previous two questions.

At the framework level, TER explicitly invites challenges, including: an internal contradiction within the framework; an economically meaningful phenomenon that cannot be represented without violating TER's definitions; a foundational claim that conflicts with empirical evidence; a TER variable or mechanism that is unnecessary or incorrectly specified; or a failure to reproduce an established economic mechanism without changing that mechanism.

This does not mean every possible specification someone writes is automatically falsifiable — a poorly built specification can still be unfalsifiable in practice, which is exactly what the guidance above is meant to prevent. See [§7.10](../theory/academic.md#710-ter-is-an-open-and-testable-framework).

## Is TER predictive?

Only conditionally, and only at the level of a particular specification. A specification that fixes `G`, `M`, `F̂`, `V`, `H`, and `D` from independent evidence can generate a conditional prediction — given this specification, this action or outcome should follow — that can then be checked against evidence.

TER itself is not an omniscient prediction system: it does not assume an observer can know every agent's objectives, beliefs, constraints, interactions, or the shocks that will occur. The presence of imbalance, feedback, or amplification does not by itself predict when or how a system state will change. See [§7.9](../theory/academic.md#79-ter-is-a-framework-for-analysis-not-an-omniscient-prediction-system).

## Does TER make irrational behavior secretly rational?

No. TER does not require optimization, exhaustive comparison, or objectively rational behavior.

`D` may represent satisficing, heuristics, habits, intuition, reflexive responses, strategic reasoning, or other decision processes — Axiom 3 explicitly states that evaluation "need not be conscious, exhaustive, or perfectly optimizing," and Axiom 4 that the selected action "need not be objectively optimal or result from exhaustive comparison among alternatives."

A poor decision remains a poor decision if the evidence supports that interpretation — TER only requires that the selected action results from the agent's specified decision process acting on its perceived feasible set and model of reality, using valuation relative to its objective and time horizon where valuation applies, not that the result be good. See [Axiom 3](../theory/academic.md#axiom-3-valuation-is-relative-to-objectives), [Axiom 4](../theory/academic.md#axiom-4-agents-select-actions-through-a-decision-process), and [§5.1](../theory/academic.md#51-agent-decision-model).

## Why distinguish `F_t` from `F̂`?

`F_t` is the objective feasible state of reality: the objective state of reality relevant when the selected action is realized. `F̂` is what the agent perceives as available to attempt. TER keeps these separate on purpose.

The distinction lets TER represent overlooked opportunities, mistaken beliefs about what is possible, hidden constraints, misinformation, discovery, and learning — all without treating perceived possibility as if it were actual feasibility. An agent can select an action that later turns out infeasible; the selection itself doesn't change, only the realized outcome does.

See the [Objective Feasible State of Reality](../theory/academic.md#objective-feasible-state-of-reality) and [Perceived Feasible Set](../theory/academic.md#perceived-feasible-set) definitions, and [§7.4](../theory/academic.md#74-the-perceived-feasible-set-and-the-objective-feasible-state-of-reality-are-distinct).

## Does TER require optimization or deterministic choice?

No. Optimization is one possible `D`, not a universal TER assumption — the same is true of deterministic choice.

A particular specification may define `D` as deterministic or stochastic. See [§5.1](../theory/academic.md#51-agent-decision-model).

## Does TER replace existing economic theories?

No. TER explicitly builds on established economics and does not claim concepts such as bounded rationality, asymmetric information, strategic interaction, institutions, externalities, equilibrium, or behavioral economics as novel.

Its contribution is the common architecture used to organize and connect them: many of these established mechanisms may be represented as configurations or processes within a common agent-centered architecture, without changing what they mean. See [§7.7](../theory/academic.md#77-established-economic-theories-may-be-represented-within-a-common-framework) and [`foundations-and-references.md`](foundations-and-references.md).

## What is actually novel?

As the previous answer notes, TER does not claim to have invented the established economic mechanisms it uses.

Its contribution is the way those mechanisms are organized and separated within a common agent centered architecture. That includes distinctions TER treats as structurally important, such as actual versus perceived feasibility, decision versus realization, and the separation of objectives, beliefs, valuation, time horizon, decision process, and realized outcomes.

Some of these components have clear prior literature. What remains to be established is whether TER’s particular configuration of them, together with its open, versioned methodology, executable framework, and replication tests, is itself distinctive and useful.

That is the claim TER puts forward for testing. See the [Central Research Claim](../theory/academic.md#central-research-claim) and [§7.10](../theory/academic.md#710-ter-is-an-open-and-testable-framework).

## Was AI used to develop TER?

Yes. AI was used for research assistance, adversarial review, software implementation, testing, editing, and documentation.

AI is treated as a tool, not a source of authority. TER's theory, assumptions, models, tests, and claims remain subject to the same standards regardless of how they were produced: economic literature, internal consistency, reproducible tests, and external criticism.

See [`research/README.md`](README.md#ai-usage) for the fuller statement.

## Canonical sources

- [`theory/academic.md`](../theory/academic.md) — canonical TER definitions, axioms, formal architecture, claims, and limitations.
- [`ter-methodology-notes.md`](ter-methodology-notes.md) — how to place concepts and build a defensible specification.
- [`foundations-and-references.md`](foundations-and-references.md) — the established economics TER builds on, and primary references.

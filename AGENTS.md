# TER AI Project Instructions

## Project purpose

This repository contains the Theory of Economic Relativity (TER), its research framework, executable economic tests, educational examples, and related applications.

## Canonical theory sources

Treat these files as authoritative, in this order:

1. `theory/academic.md`
2. `research/ter-methodology-notes.md`
3. `research/README.md`

If implementation, tests, docs, or prior conversations conflict with `theory/academic.md`, the academic paper wins.

Do not change TER definitions, axioms, variables, models, claims, or limitations merely to make software implementation easier.

If a software task appears to require changing the theory, stop and identify the conflict separately.

## TER implementation rules

Preserve the distinction between:

- established TER
- implications derived from TER
- hypotheses being tested
- implementation details
- pedagogical simplifications

Prefer the smallest implementation that preserves the economics.

Do not introduce new TER primitives, variables, or mechanisms for software convenience.

Prefer direct and understandable implementations over speculative flexibility or abstraction.

An abstraction should solve a repeated current problem, not a hypothetical future one.

## Coding guidelines

Follow `CODING_GUIDELINES.md` for readability, documentation, naming, and abstraction decisions.

## Core execution boundaries

Preserve these boundaries unless the canonical theory changes:

- `D` selects from `F̂`
- `D` does not inspect objective `F_t`
- `G` and `H` condition valuation when valuation is used
- `R` realizes selected actions against objective reality
- joint interaction-dependent outcomes come from one joint `R`
- realized outcomes are distinct from later objective state
- agent updates occur only through information available to that agent
- objective-state transition and agent-side updates remain distinct
- counterfactuals rerun `R` against recorded actions and recorded `F_t`

## Development workflow

Claude Code CLI is the default coding agent for this repository.

Use Claude Code for:

- repository inspection
- code changes
- refactoring
- debugging
- tests
- repository-wide searches
- implementation verification
- final code review

Use ChatGPT for:

- planning
- theory
- research
- architecture
- design decisions
- implementation prompts
- adversarial review
- reviewing Claude Code reports

Hermes coordinates work and prepares handoffs. Hermes should not directly modify repository code unless explicitly requested.

## Before editing

For implementation work:

1. inspect `git status`
2. inspect relevant existing code and tests
3. read relevant canonical TER documentation
4. preserve staged and unstaged user changes
5. make the smallest necessary change

## Testing

Run the most relevant focused tests first.

Before reporting completion, run the full applicable test suite when practical.

Do not optimize for test count. Prefer strong tests that protect:

- TER theory boundaries
- economically meaningful behavior
- important execution contracts

Avoid tests that only protect incidental implementation details.

## Git safety

Do not commit, push, rebase, reset, discard changes, or alter the index unless explicitly requested.

Never overwrite unrelated staged or unstaged user work.

## Implementation report

After code work, report only:

1. files changed
2. what changed
3. tests run and results
4. unresolved concerns or risks
5. current git state if relevant

Keep the report concise.

## Writing and simplicity standard

TER should be lean, simple, and easy to learn without sacrificing correctness.

For all public-facing or instructional content outside the canonical academic paper, including website copy, README files, guides, replication tests, release notes, examples, and educational material:

- Prefer the shortest wording that preserves canonical TER meaning.
- Every sentence should add new information.
- Remove duplicated ideas, repeated definitions, unnecessary qualifications, academic filler, and restatements of obvious points.
- Do not repeat theory text when a shorter explanation or link to the canonical theory is sufficient.
- Use plain language by default while preserving TER terminology where precision matters.
- Structure explanations progressively: simple baseline first, deeper detail only when needed.
- Match complexity to the intended audience without changing the underlying TER architecture.
- Treat unnecessary verbosity, repetitive content, and avoidable complexity as defects to fix before PR review.

Before finalizing public-facing or instructional changes, perform a dedicated simplicity pass and check:

1. Can anything be removed without losing meaning?
2. Can any sentences be combined?
3. Is any idea stated more than once?
4. Is any wording more academic or verbose than necessary?
5. Is the baseline explanation understandable to the intended audience?
6. Does the wording remain faithful to canonical TER?

Do not modify `theory/academic.md` as part of this simplification pass unless explicitly authorized.
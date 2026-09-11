# Contributing to TER

Thanks for helping test and improve the Theory of Economic Relativity.

The goal is simple: make it easy to test whether economic phenomena can be represented using TER's existing framework — without needing to read the framework's internals first.

The canonical theory is [`theory/academic.md`](theory/academic.md). The research code tests it. If they ever disagree, `academic.md` wins.

## Before You Start

This file covers contribution workflow only. For everything about writing, running, and reading TER research code — the API, building blocks, standard test structure, naming conventions, reading results, shared vs. local rules, and framework internals — see [`research/README.md`](research/README.md).

## Git and GitHub Workflow

- Fork or clone the repository, and branch from the current default branch (`main`) with a short, descriptive name.
- Keep one focused change per branch — one new test, one fix, or one doc update.
- Write clear commit messages that explain *why*, not just what changed.
- Run the relevant test file directly while you iterate (see [`research/README.md`](research/README.md) for how).
- Run `python3 run_tests.py` before submitting.
- Open a PR that explains the problem, your approach, and the test evidence.
- Avoid mixing theory changes with unrelated software changes — keep them in separate PRs.
- Keep PRs reasonably small and reviewable.
- Resolve conflicts by merging or rebasing the default branch into yours before requesting review.
- Releases and versioning are handled by maintainers unless otherwise documented.

## Keep This Distinction Clear

**TER** — what [`theory/academic.md`](theory/academic.md) actually defines.

**Test assumptions** — conditions introduced for this experiment.

**Hypothesis** — what you expect the experiment to demonstrate.

**Result** — what actually happened.

A simulation assumption does not become part of TER just because a test uses it.

## AI-Assisted Contributions

AI-assisted contributions are welcome. They are held to the same standards as any other contribution — correctness, evidence, testing, and review — regardless of the tools used to produce them. See [`research/README.md`](research/README.md#ai-usage) for the project's broader AI usage statement.

## Found a Problem With TER?

Great. Do not change the theory just to make the test pass. Document:

1. What you expected
2. What happened
3. Why the existing TER framework may be insufficient

Failed tests and counterexamples are useful contributions.

## Before Submitting

Run `python3 run_tests.py` and check that:

- existing tests still pass
- the new test has a clear economic question
- shared rules are selected via the public enums; bare strings are used only for local, test-scoped rules registered in that same file/module
- results are read via `.agent(name)`, not positional indexing
- important numeric assumptions are visible near the top, not buried
- test assumptions are not presented as TER rules
- no TER definitions, variables, axioms, or claims were silently changed

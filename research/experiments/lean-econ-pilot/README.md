# Lean economics pilot

Lean 4 and Mathlib support a small benchmark for finite choice and shared-stock allocation. The pilot determines total allocation even when the rationing rule is unspecified. TER v0.6.0 can represent the same constraints and a rule that satisfies them, so this example establishes overlap. Expand by one comparative benchmark before considering a competing framework.

## Reproduce

Install Lean via Elan and ensure `lake` is on your `PATH`. The toolchain file pins Lean 4.35.0, and the Lake manifest pins Mathlib 4.35.0 and its transitive dependencies. [Lean installation](https://lean-lang.org/install/), [Lean 4.35.0 release](https://github.com/leanprover/lean4/releases/tag/v4.35.0), [Mathlib 4.35.0 release](https://github.com/leanprover-community/mathlib4/releases/tag/v4.35.0)

Run these commands from the repository root.

```sh
cd research/experiments/lean-econ-pilot
lake exe cache get Mathlib.Data.Finset.Max
lake build
lake env leanchecker --fresh -v LeanEconPilot
```

The pinned build and fresh kernel replay passed on arm64 macOS from a clean project directory. The eight guarded axiom checks reported only `propext`, `Classical.choice`, and `Quot.sound` in aggregate. The rationing example uses none. The existing Python research suite passed all 365 tests.

## Assumptions and results

Each of two agents has a nonempty finite menu of requests and a private natural-number score for ranking its options. The choice rule keeps every maximizer. Requests are simultaneous and concern one stock of identical, indivisible units. A joint allocation may grant each agent up to their request, may allocate at most the available stock, and may leave stock unused only when both requests are filled. The example uses first-agent priority as one executable rationing rule.

- `mem_bestRequests`, `bestRequests_nonempty`, and `bestRequests_keeps_ties` establish menu membership, maximality, existence, and tie preservation.
- `firstPriority_clears` proves the priority rule satisfies all joint constraints for every stock and request pair. `Clears.total_eq_min` proves that every admissible allocation grants exactly the smaller of stock and total requests. `Clears.conserves` proves that grants plus unallocated units equal opening stock.
- `selected_requests_not_jointly_fillable` refutes the claim that individually fillable selections are always jointly fillable. Given `{0, 1}` and score `id`, each agent uniquely chooses one unit. Either request can be filled if the other is zero. One shared unit cannot fill both one-unit requests. `clears_leaves_rationing_open` proves that either agent can receive the unit under the same constraints.

The proofs establish consequences of the stated assumptions. Welfare, behavior in real economies, and empirical fit remain open.

## Library reuse

| Library | Reuse for economic modeling |
| --- | --- |
| Lean 4 | Natural numbers, executable definitions, and kernel-checked proofs, including arithmetic via `omega` and finite examples via `decide`. [Proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) |
| Mathlib | The pilot uses `Finset.mem_filter` for the choice characterization and `Finset.exists_max_image` for existence. `Finset` makes the menu and its filtered result executable. [Filter](https://github.com/leanprover-community/mathlib4/blob/56a005855ea17e0b0958f73ec801ae140b0a1679/Mathlib/Data/Finset/Filter.lean), [Max](https://github.com/leanprover-community/mathlib4/blob/56a005855ea17e0b0958f73ec801ae140b0a1679/Mathlib/Data/Finset/Max.lean) |
| MathEconLib | `Choice.maximizers` and `maximizers_nonempty_of_finite` generalize choice to complete preferences on finite menus. `CompletePreference.exists_nat_utility_maximizers` supplies a score representation on a finite alternative type. `bestOption` covers finite menus with an outside option and an ordered tie-break. [Maximizers](https://github.com/matheconlib/matheconlib/blob/f3b16e9b6b48aa0b6823d12867200c2d3b508370/MathEconLib/Choice/Maximizers.lean), [Finite option](https://github.com/matheconlib/matheconlib/blob/f3b16e9b6b48aa0b6823d12867200c2d3b508370/MathEconLib/Choice/FiniteOption.lean) |
| Econlib | `PreferenceRel`, `argmaxRel`, and `PreferenceRel.exists_greatest_on` offer an ordinal choice route. `exists_nat_utility_representation_of_finite` supplies a score representation. `FeasibleOver` supplies aggregate feasibility for real-valued bundles with free disposal. Request caps and the rule for using spare stock are specific to this pilot. [Finite preferences](https://github.com/danlyng/Econlib/blob/d7bd9477476cade1c6695c8891746048ceddc52f/Econlib/Preferences/Representation/Finite.lean), [Relational argmax](https://github.com/danlyng/Econlib/blob/d7bd9477476cade1c6695c8891746048ceddc52f/Econlib/Optimization/ComparativeStatics/MonotoneSelection.lean), [Aggregate feasibility](https://github.com/danlyng/Econlib/blob/d7bd9477476cade1c6695c8891746048ceddc52f/Econlib/Equilibrium/Economy.lean) |

The economics libraries were reviewed from source. At the linked revisions MathEconLib targets Lean 4.35.0 and Econlib targets 4.29.0. The pilot build imports Mathlib alone.

## Comparison with TER v0.6.0

| Pilot definition | Closest TER component |
| --- | --- |
| `bestRequests` returns all maximizing requests using a menu and supplied score. Stock is absent from its inputs. | In §5.1 the menu corresponds to `F̂` and a supplied score can represent a valuation already conditioned on `G`, `M`, and `H`. TER's `D` produces a selected action or specifies a stochastic choice rule. It permits nonoptimizing decisions as well. |
| `Clears` specifies admissible joint grants from a request pair and stock. `firstPriority` picks one pair. | In §§5.2–5.3, stock is the modeled part of `F_t`, the pair of requests is the selected action profile, and `Clears` can serve as the constraint `K_t`. `firstPriority` can serve as the joint `R`. Each grant is a projection of the same outcome. |
| The remainder is a quantity accounted for in the current stage. | Under §§5.4–5.5, opening conditions, realized outcomes, later objective state, and agent updates have separate roles. This one-stage model leaves persistence, observation, and transitions unspecified. |

For a fixed-stock comparison, the relation can bound possible grants after changing a request. TER's fixed-state replay reproduces the factual allocation first and then reruns the specified `R` against held-fixed objective conditions. The example's first-priority rule supports that narrower question once selected requests and stock are recorded. [TER v0.6.0 formal architecture](../../../theory/academic.md#5-formal-architecture)

The pilot uses standalone definitions. Its design used the TER baseline to choose a comparable problem. A blind comparison belongs in the next benchmark.

## Next research step

1. Give separate LLM sessions the same two-period rationing problem, with carried inventory and private feedback, using a brief written independently of TER. Freeze their assumptions, candidate definitions, observables, and proposed claims before comparison. Have another session look for counterexamples and a human reviewer approve the economic interpretation.
2. Formalize the smallest surviving claims. Pin dependencies, check the statements against the frozen brief, build with warnings treated as errors, audit transitive proof dependencies, and replay compiled proofs. Keep empirical questions in a separate evaluation.
3. Specify the same timing, information, and resource assumptions in TER. Compare the admissible observable traces and fixed-input counterfactuals. Expand the architecture only if the benchmark yields a strict difference in representable traces or a useful observable result under fewer economic assumptions. Otherwise use Lean to verify individual models.
4. Bring reusable economics results to an economics library after discussing definition changes with maintainers. Bring general-purpose lemmas to Mathlib with human review and AI-use disclosure under its contribution policy. [MathEconLib contributions](https://mathecon.dev/#contributing), [Econlib issues](https://github.com/danlyng/Econlib/issues), [Mathlib contributions](https://leanprover-community.github.io/contribute/index.html#use-of-ai)

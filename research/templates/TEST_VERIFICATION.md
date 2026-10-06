# TER Test Checklist

Check every box before you submit a new or changed TER test. If something here seems to conflict with [`theory/academic.md`](../../theory/academic.md), the paper wins. For placement examples, see [`ter-methodology-notes.md`](../ter-methodology-notes.md).

## TER placement

- [ ] The docstring's TER mapping lists the components the test uses, and the code matches it.
- [ ] `D` chooses only from `F̂`. It never reads `F_t`, and actual conditions are not copied into `M`, `V`, or `decision_parameters` unless an assumption says the agent knows them.
- [ ] `M` holds only what the agent believes, which can be wrong (for example, the expected price).
- [ ] `F̂` lists the actions the agent thinks it can try, not what reality allows. An action that may fail stays in `F̂`.
- [ ] `F_t` holds the actual conditions (for example, the actual price), set in the `Scenario`, never on the agent.
- [ ] `R` turns the chosen actions and `F_t` into outcomes. A failed or partly filled action shows up in `O`, not as a different `C`.

## Economic validity

- [ ] Test-specific assumptions are listed in the docstring, key numbers are named constants, and no assumption is presented as part of TER.
- [ ] Established economics keeps its standard meaning. Any equilibrium concept used is named.
- [ ] The setup was chosen for economic reasons before seeing the result, not tuned backward to make the hypothesis pass.

## Test quality

- [ ] Assertions check the mechanism (what was chosen, why, and what reality made of it), not implementation details.
- [ ] Shared rules from `research.ter.rules` are used where they fit. A local rule has a short docstring saying why it is local.
- [ ] Every rule is deterministic, so every run gives the same result.
- [ ] The focused test passes: `python3 -m unittest research.tests.test_NN_your_topic -v`
- [ ] The full suite passes before merge: `python3 run_tests.py`

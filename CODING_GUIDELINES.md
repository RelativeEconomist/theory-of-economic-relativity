# Coding Guidelines

Practical rules for humans and coding agents working in this repository. Theory boundaries live in `AGENTS.md` and `theory/academic.md`.

1. **Write the simple version first.**
   Solve the current problem with the most direct code that works. Use plain functions, data, and control flow before classes, registries, or configuration layers. Add complexity only when a real case requires it.

2. **Use clear, descriptive names.**
   Names should say what a value is or what a function does: `selected_action`, `realize_outcome`, not `x`, `tmp`, or `handler2`. Avoid unexplained abbreviations. Short names are fine for tight loops and standard TER symbols such as `D`, `R`, or `F_t`.

3. **Keep functions small and focused.**
   Each function should do one thing you can describe in one sentence. Split it when it mixes concerns or becomes hard to understand or verify. Do not create tiny helpers that only add indirection.

4. **Document lightly, where it helps.**
   Give public modules and non-obvious functions a short docstring stating purpose, inputs, and outputs. Comment on why, not what. Skip comments that restate the code, and delete comments that no longer match it.

5. **Use simple terms before technical or economic precision.**
   Explain behavior in plain language first, then add precise TER or economic terms where accuracy depends on them. A reader new to the code should follow the idea before meeting the formal vocabulary.

6. **Preserve canonical TER meaning without restating the theory.**
   Code, tests, and docs must match the definitions in `theory/academic.md`. Use canonical names and boundaries consistently, and do not invent new primitives for convenience. Link to the theory instead of copying it into docstrings or READMEs.

7. **Make data flow explicit.**
   Pass inputs as arguments and return results. Avoid hidden global state, mutation at a distance, implicit defaults that change behavior, monkey-patching, and other magic. A reader should see where each value comes from and where it goes.

8. **Reuse before abstracting.**
   Use existing functions and the standard library first. Introduce a new abstraction, pattern, or framework only after the same need has appeared in real code more than once, and keep it as small as that need allows. Duplication is cheaper than the wrong abstraction.

9. **Test what matters.**
   Prefer a small number of strong tests for critical behavior, TER boundaries, and execution contracts. Do not chase coverage percentages or test count. Use integration or end-to-end tests when they give more confidence than isolated unit tests.

10. **Optimize for readability and review.**
    Write code a reviewer can understand in one pass. Keep changes small and on topic, prefer obvious code over clever code, and leave unrelated code alone. If a diff is hard to explain in a few sentences, split or simplify it.

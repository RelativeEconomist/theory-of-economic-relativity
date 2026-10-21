# Configuration K Validation — Krugman (1980), Section I

## Purpose

This document defines how Configuration K should be validated against Krugman’s Section I results.

The goal is to test whether the approved TER configuration reproduces Krugman’s analytical implications without inserting those implications as assumptions merely to make the replication succeed.

A result may be used downstream once it has been independently derived upstream. It may not be assumed in order to prove itself.

---

## Validation Dependency Chain

> Preferences + technology + agent behavior  
> → pricing  
> → output per firm  
> → equilibrium firm / variety count  
> → market and labor consistency  
> → integrated-trade results  
> → welfare comparison

The validation should follow this dependency order rather than treating all results as simultaneous inputs.

---

## Validation Matrix

| Krugman result | Allowed inputs | Must emerge / be derived | Failure means |
|---|---|---|---|
| Markup `p/w = β/θ` | Profit objective, demand structure, production technology, large-number approximation | Firm pricing relationship | Firm-side source specification, TER mapping, or derivation is incorrect |
| Output per firm `x = αθ / [β(1-θ)]` | Derived pricing relationship, production technology, Krugman free-entry / zero-profit equilibrium specification | Equilibrium output per firm | Configuration does not reproduce Krugman’s firm-level equilibrium relationship |
| Variety count `n = L(1-θ)/α` | Labor endowment, production technology, derived output per firm, free-entry equilibrium specification | Equilibrium firm / variety count | System-level equilibrium mapping or derivation fails |
| Zero profit | Profit-maximizing firm behavior, free-entry environment, demand, technology, realized or derived price and output | Active-firm equilibrium profit equals zero | Proposed Configuration K outcome is inconsistent with Krugman’s free-entry equilibrium |
| No profitable excluded entrant | Free-entry equilibrium specification and the same profit environment faced by active firms | No remaining strictly profitable entry opportunity | Proposed equilibrium is inconsistent with free entry |
| Market clearing | Consumer choices, firm pricing, production environment, available varieties | Intended purchases and available production are mutually consistent without unintended rationing or unsold output | Configuration is not in Krugman’s goods-market equilibrium |
| Full employment | Labor supply `L`, production technology, derived production and firm count | Total labor use equals available labor | Proposed equilibrium fails Krugman’s labor-market consistency condition |
| Symmetry | Identical firm specifications and common market environment | Predicted common price and output relationships across active firms | Symmetric equilibrium is not reproduced |
| Equal wages under integrated trade | Identical preferences and technologies, zero transport costs, integrated market access, Krugman equilibrium conditions | `w = w*` | Integrated equilibrium differs from Krugman’s result |
| Trade shares | Derived variety counts, consumer demand structure, integrated market access | Krugman’s predicted import / expenditure shares | Trade mapping or integrated equilibrium is incorrect |
| Balanced trade | Realized or derived bilateral expenditure and trade flows | Import value equals export value | Integrated-trade equilibrium fails |
| Welfare gain from trade | Completed autarky and integrated-trade configurations with the same preference and technology assumptions | `U_trade > U_autarky` through increased variety | Krugman’s comparative welfare result is not reproduced |

---

## Validation Order

### 1. Firm pricing

Start from Krugman’s firm objective, demand structure, production technology, and large-number approximation.

Validate that the configured firm decision problem implies:

`p/w = β/θ`

The markup relationship must be derived from the decision problem. It must not be inserted as the firm’s only available action or assumed merely because it is the expected answer.

### 2. Output per firm

Using the independently derived pricing relationship together with Krugman’s production technology and free-entry / zero-profit equilibrium specification, derive:

`x = αθ / [β(1-θ)]`

This result may use the validated markup from the previous step because it is now an upstream derived result.

### 3. Equilibrium variety count

Using labor endowment, production technology, and the independently derived output per firm, derive:

`n = L(1-θ)/α`

Treat `n` as a derived equilibrium system quantity, not as an agent-level selected action or realized outcome.

### 4. Closed-economy consistency

Using the completed closed-economy configuration, verify:

- active firms earn zero profit;
- no strictly profitable entry opportunity remains under Krugman’s free-entry equilibrium specification;
- goods markets clear without unintended rationing or unsold output;
- total labor use equals available labor;
- identical active firms satisfy the predicted symmetric price and output relationships.

These are equilibrium checks on the completed configuration, not TER assumptions.

### 5. Integrated-trade equilibrium

Construct the integrated-trade configuration using Krugman’s source assumptions:

- identical preferences;
- identical technologies;
- zero transportation costs;
- integrated market access;
- country labor endowments `L` and `L*`.

Then verify:

- home and foreign equilibrium variety counts;
- unchanged output per firm;
- consumer access to `n + n*` varieties;
- equal wages under Krugman’s integrated equilibrium;
- predicted trade shares;
- balanced bilateral trade.

### 6. Welfare comparison

Compare realized or analytically implied consumer utility under autarky and integrated trade.

The comparison should preserve Krugman’s population accounting and preference structure.

Validate only the ordinal conclusion that integrated trade raises utility through access to additional varieties. Do not reinterpret the utility difference as a cardinal welfare magnitude.

---

## TER Execution Results

`test_krugman_1980_ter.py` validates the TER execution of Configuration K (see the configuration document, TER Execution). The markup comes from a TER firm decision. Output per firm and firm count are derived from it with Krugman's zero-profit and full-employment conditions, following steps 1–3 above, and equal wages follow from world goods-market clearing. No closed-form answer is supplied to TER (Anti-Circularity Rules 1 and 5). `krugman_1980.py` is used only as the external benchmark the tests compare against.

Equilibrium conditions are used to derive the equilibrium, so TER can confirm that its joint `R` realizes them but cannot validate them independently.

| Krugman result | Status in TER execution |
|---|---|
| Markup `p/w = β/θ` | **TER agent decision**: each firm's `D` maximizes its own `V`. It does not depend on the expected market level and scales with the wage (tested). Matches the benchmark. |
| Output per firm | **Derived** from the TER markup by zero profit; matches the benchmark. Realized output matches it (realization check). |
| Variety count | **Derived** from that output by full employment; matches the benchmark. |
| Expected prices | **Derived**: the TER-selected price. Firms' selected prices match it (fixed-point confirmation, not independent evidence). |
| Zero profit | **Equilibrium condition** (free entry), used in the derivation; realization check. |
| No profitable entry | **Equilibrium condition** (free entry); realization check with an active firm's `V` under the large-number approximation. |
| Market clearing | **Equilibrium condition**; realization check. `R` produces what is purchased, so no unsold output can occur; that `F_t` permits the whole allocation and consumers exhaust their budgets is checked. |
| Full employment | **Equilibrium condition**, used in the derivation; realization check. |
| Symmetry | **Derived** from identical agent specifications; realization check. |
| Equal wages | **Derived** from world goods-market clearing (configuration document, Equal Wages); unequal wages violate that condition (benchmark test). |
| Trade shares | **Realized** from consumer decisions given the derived variety counts; matches the benchmark. |
| Balanced trade | **Equilibrium condition** (equivalent to world goods-market clearing with two countries); realization check; matches the benchmark. |
| Welfare gain | **Realized** consumption evaluated with each consumer's `V`; matches the benchmark; ordinal gain only. |

Configuration K therefore derives Krugman's equilibrium from one TER decision, the firm's markup, plus Krugman's stated equilibrium conditions, and shows that one joint `R` realizes it feasibly. It does not test the equilibrium conditions themselves, and its single-pass fixed point relies on the markup not depending on expected market conditions.

---

## Failure Classification

A failed validation check does not automatically imply a failure of TER.

Classify the failure in this order:

1. **Source-specification failure** — Configuration K does not faithfully reproduce Krugman’s assumptions, equations, or equilibrium concept.
2. **TER-mapping failure** — the source model was placed incorrectly among TER components or boundaries.
3. **Derivation / implementation failure** — the configured model is correct but the analytical or computational reproduction is wrong.
4. **Framework failure** — the Krugman mechanism cannot be represented without violating TER’s definitions, collapsing required distinctions, or contradicting a TER axiom.

Only the fourth category is evidence of a TER framework-level problem.

---

## Anti-Circularity Rules

1. Do not insert a predicted result as a configuration input merely to reproduce it.
2. Do not restrict an agent’s feasible actions to the known equilibrium answer unless the source model itself imposes that restriction.
3. Do not encode zero profit, full employment, market clearing, symmetry, equal wages, or equilibrium variety count as universal TER conditions.
4. Do not let `R` silently rewrite selected actions to force Krugman’s equilibrium.
5. Upstream results may be used downstream only after they have been independently derived or validated.
6. Keep source-model assumptions distinct from TER definitions and from researcher-level equilibrium checks.

---

## Validation Standard

Configuration K passes the baseline replication only if the Krugman configuration, using its approved assumptions and TER mappings, reproduces the source model’s core analytical relationships without changing Krugman’s economics or TER’s definitions.

Passing Configuration K does not by itself validate TER as a general theory. It demonstrates that this established economic model can be faithfully represented and its predicted relationships reproduced within the TER architecture.

> Configuration → selected actions → realized outcomes → compare against Krugman hypotheses → compare against competing configurations

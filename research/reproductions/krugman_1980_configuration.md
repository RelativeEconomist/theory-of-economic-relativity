# Configuration K — Krugman (1980), Section I

## Research Question

Can Krugman’s Section I model be represented as a TER configuration without changing either Krugman’s economics or TER’s definitions?

Given Krugman’s specified preferences, technology, market structure, agent behavior, information assumptions, and trade conditions:

1. What actions do consumers and active firms select?
2. What outcomes result when those actions interact with the objective economic environment?
3. Do those outcomes satisfy the equilibrium relationships and comparative results derived by Krugman?

Configuration K treats Krugman’s model as one economic configuration within TER. Its predicted results are tested as implications of that configuration, not assumed as general TER claims.

---

## Configuration Inputs

| Source-model element | TER placement | Classification | Notes |
|---|---|---|---|
| Labor force `L` and, under trade, `L*` | `F_t` | Configuration input | Objective labor resources available in each country. |
| Consumer preferences `U = Σ c_i^θ`, `0 < θ < 1` | Consumer `V` specification | Configuration input | Krugman’s preference structure over differentiated varieties. |
| Production technology `l_i = α + βx_i` | `F_t` and `R` | Configuration input / realization mechanism | Fixed labor requirement `α` plus constant marginal labor requirement `β`. |
| Labor is the only factor of production | `F_t` | Configuration input | Defines the productive environment. |
| One differentiated variety per active firm | Firm/environment specification | Configuration input | Each active firm produces one variety. |
| Costless product differentiation | `F_t` | Configuration input | Differentiation itself does not require an additional modeled resource cost. |
| Large-number monopolistic-competition approximation | Source-model specification; reflected in firm `M` / `D` where relevant | Configuration input | Individual firms treat relevant aggregate market conditions as given rather than modeling strategic effects from their own actions. The approximation itself is a Krugman assumption, not merely a subjective firm belief. |
| Free entry and exit | Source-model equilibrium specification / market environment | Configuration input | Entry is permitted. Configuration K does not model a separate entrant decision process or adjustment path. |
| Identical consumers within each country | Consumer specification | Configuration input | Allows representative treatment without changing the underlying economic assumption. |
| Identical technologies across countries | `F_t` | Configuration input | Applies in the integrated-trade specification. |
| Identical preferences across countries | Consumer `V` specifications | Configuration input | Applies in the integrated-trade specification. |
| Zero transportation costs | `F_t` | Configuration input | Applies to Krugman’s integrated-trade baseline. |
| Autarky or integrated trade | `F_t` / system boundary | Configuration input | These are separate economic configurations, not sequential periods of an adjustment path. |

---

## Agent Mappings

### Consumers

| TER component | Configuration K |
|---|---|
| `G` | Maximize utility from consumption. |
| `M` | Prices, income, and available varieties as understood by the consumer. |
| `F̂` | Consumption bundles the consumer perceives as available within the perceived budget and market environment. |
| `V` | Krugman’s utility function `U = Σ c_i^θ`. |
| `H` | Current static consumption decision; Section I does not introduce an intertemporal consumption problem. |
| `D` | Constrained utility maximization. |
| `C` | Selected consumption bundle / demand plan. |

**Classification:** Agent behavior.

The consumer’s perceived budget and available alternatives belong on the agent side. Actual resources, available production, and other objectively realized constraints remain part of `F_t` and realization.

### Active firms

| TER component | Configuration K |
|---|---|
| `G` | Maximize profit. |
| `M` | Profit-relevant beliefs and information required by Krugman’s model, including perceived demand conditions, wage, market size, and the large-number competitive environment. |
| `F̂` | Prices or pricing actions the firm perceives as available. |
| `V` | Expected profit associated with available pricing actions under the firm’s model of demand and costs. |
| `H` | Current static profit decision. |
| `D` | Profit maximization. |
| `C` | Selected price. |

**Classification:** Agent behavior.

The markup relationship is not itself the firm’s decision process. It is a result implied by the configured profit-maximization problem.

### Potential entrants

Potential entrants are not modeled as explicit TER agents in baseline Configuration K.

Free entry remains part of Krugman’s source-model equilibrium specification. Configuration K therefore does not invent a separate entrant `M`, `V`, `D`, `C`, entry sequence, or adjustment path that Section I does not specify.

If a later competing configuration explicitly models entry behavior, entrants may be represented as TER agents. In that case, their `M` should contain only the minimum profit-relevant information supported by the source model unless the competing configuration intentionally changes that assumption.

**Classification:** Source-model equilibrium specification in Configuration K; explicit entrant behavior is deferred.

---

## Realized Outcomes

The selected actions of consumers and active firms interact with the objective market environment through a joint reality function.

Relevant realized outcomes include:

| Outcome | TER placement | Classification |
|---|---|---|
| Realized consumption | `O_i`, `O_t` | Realized outcome |
| Realized sales | `O_i`, `O_t` | Realized outcome |
| Output per firm | `O_i`, `O_t` | Realized outcome |
| Labor used | `O_i`, `O_t` | Realized outcome |
| Firm revenue | `O_i` | Realized outcome |
| Firm cost | `O_i` | Realized outcome |
| Firm profit | `O_i` | Realized outcome |
| Aggregate expenditure | `O_t` | Realized outcome |
| Trade flows | `O_t` | Realized outcome |
| Realized consumer utility | Consumer `V` evaluated at realized consumption (`O_i`) | Evaluation of a realized outcome |
| Rationing, unmet demand, unsold production, or unemployment if present | `O_i`, `O_t` | Realized outcome (not realized in the TER execution, which reports such allocations infeasible; see Modeling Choices) |

The number of active firms or varieties, `n`, is treated in Configuration K as a **derived equilibrium system quantity**, not as an agent-level realized outcome. It is evaluated from the completed Krugman specification and checked against the source model’s equilibrium relationship. In the TER execution, `n` is derived from the TER-selected markup through the zero-profit and full-employment conditions (see TER Execution).

`R` must preserve transaction and resource accounting. It should not silently change selected actions merely to force the system into Krugman’s predicted equilibrium.

---

## Krugman Hypotheses

After Configuration K has been fully specified, its actions and outcomes are compared against Krugman’s analytical results.

### Closed economy

| Hypothesis or consistency condition | Classification |
|---|---|
| Firm pricing satisfies Krugman’s markup relationship `p/w = β/θ` | Derived result |
| Equilibrium output per firm satisfies `x = αθ / [β(1-θ)]` | Derived result |
| Equilibrium variety count satisfies `n = L(1-θ)/α` | Derived equilibrium system quantity / equilibrium hypothesis |
| Active firms earn zero profit | Equilibrium condition (free entry) |
| No profitable entry opportunity remains | Equilibrium condition (free entry) |
| Goods markets clear without unintended rationing or unsold output | Equilibrium condition |
| Total labor use equals available labor | Equilibrium condition (full employment) |
| Identically configured firms exhibit the predicted symmetric price and output relationships | Derived result |

### Integrated trade

| Hypothesis or consistency condition | Classification |
|---|---|
| Home variety count satisfies `n = L(1-θ)/α` | Derived equilibrium system quantity |
| Foreign variety count satisfies `n* = L*(1-θ)/α` | Derived equilibrium system quantity |
| Output per firm remains unchanged relative to autarky | Derived comparative result |
| Consumers gain access to `n + n*` varieties | Derived result |
| Wages are equal under Krugman’s frictionless symmetric integrated equilibrium | Derived result (from world goods-market clearing; see Equal Wages) |
| Trade shares correspond to the relative numbers of foreign and domestic varieties | Derived result |
| Bilateral trade values balance | Equilibrium condition (equivalent to world goods-market clearing with two countries) |
| Consumer utility rises because integrated trade expands available variety | Derived comparative result |

Equilibrium conditions define Krugman's equilibrium concept; they are used to derive the equilibrium and can only be confirmed as realized, not independently validated. Derived results follow from those conditions and the source assumptions. None of these relationships are TER axioms, universal equilibrium requirements, or assumptions to insert merely so the replication succeeds.

---

## TER Execution

`krugman_1980_ter.py` runs Configuration K through TER Core; `test_krugman_1980_ter.py` validates it. Home autarky, foreign autarky, and integrated trade are separate one-period scenarios. In each, every agent acts once at the same decision point and one joint `R` realizes the outcomes. There is no adjustment path.

`krugman_1980.py` implements Krugman's closed-form solution without TER. It is an external benchmark for the tests only; the configuration shares its illustrative fixtures (`L`, `L*`, `α`, `β`, `θ`) but none of its solution functions.

| Category | Contents | Source |
|---|---|---|
| Source assumptions | Preferences `U = Σ c_i^θ`; technology `α + βx`; labor endowments `L`, `L*`; labor as the only factor; large-number approximation; identical consumers, tastes, and technologies; zero transport costs | Krugman (1980), Section I (Configuration Inputs above) |
| Equilibrium conditions | Free entry (zero profit), full employment, goods-market clearing, mutually consistent expectations; wage numeraire `w = 1` | Krugman's equilibrium concept |
| TER agent decisions | Firm: price maximizing its expected-profit `V` over `F̂` = all positive prices, giving markup `m = p/w`. Consumer: CES demand over `F̂` = its perceived budget set. `C ∈ F̂` is enforced | Each agent's `M`, `V`, `D` |
| Analytical derivation | From `m` and the equilibrium conditions: output per firm `x = α/(m−β)`, firm count `n = L/(α+βx)`, equal wages, expected price `p = m·w` | `coordinate_equilibrium`, before the scenario runs |
| Realized outcomes | If `F_t` permits the selected allocation: consumption, expenditure, sales, output, labor use, revenue, cost, profit, imports, exports. Otherwise: the allocation is reported infeasible, with the violated constraints and attempted quantities, and nothing is realized | One joint `R` against `F_t` |
| Checks | Realization checks (realized outcomes meet the equilibrium conditions) and benchmark comparisons (TER results against Krugman's closed forms) | `test_krugman_1980_ter.py` |

### Equilibrium Derivation

1. **Markup (TER decision).** `coordinate_equilibrium` runs one configured firm through TER and reads its selected price. The firm's `D` does not depend on the market level it expects (tested), so provisional market beliefs suffice. A firm holding the derived beliefs must then select the same price (a fixed point); otherwise coordination raises an error instead of iterating, since Krugman specifies no adjustment process.
2. **Output per firm (zero profit).** `m·w·x = w(α + βx)`, so `x = α/(m − β)`.
3. **Firm count (full employment).** `n(α + βx) = L`, so `n = L/(α + βx)`.
4. **Expected price.** `p = m·w`. Every agent holds it as a belief in `M`; no agent observes another agent's selected action.

### Equal Wages

Krugman states that wages are equal by symmetry. This follows from his equilibrium conditions without further assumptions. Let `ω = w/w*` and `σ = 1/(1−θ)`:

1. The markup is the same in both countries, so `p/p* = ω`.
2. Zero profit fixes `x` independently of wages, so full employment gives `n/n* = L/L*` at any `ω`.
3. With CES demand and wage income (profits are zero), world spending on home varieties equals home firms' revenue `n·p·x = wL` only if `w·L·n*·p*^(1−σ) = w*·L*·n·p^(1−σ)`.
4. Substituting steps 1 and 2 gives `ω^σ = 1`. Since `σ > 0`, `ω = 1` is the only solution.

`test_krugman_1980.py` checks this condition independently of TER: world goods-market excess demand for home varieties is zero at `ω = 1` and nonzero at `ω = 0.9` and `1.1`. With two countries, this clearing condition is equivalent to balanced trade.

### Modeling Choices

1. **Price expectations.** Krugman's static equilibrium requires mutually consistent expectations. Agents expect the price derived from the TER firm decision. Checking that selected prices equal it confirms the fixed point; it is not independent evidence. Firms take expected prices and market spending as given (large-number approximation).
2. **Equilibrium conditions.** Zero profit, full employment, and goods-market clearing are used to derive `x`, `n`, and equal wages. TER confirms that its joint `R` realizes them; that confirmation tests the implementation, not the conditions.
3. **Representative consumers.** One consumer agent per country stands for its `L` identical consumers, each supplying one unit of labor; `R` scales the per-capita bundle by `L`. Income is the wage; equilibrium profits are zero, so no profit income is distributed.
4. **Realization.** Firms produce what is purchased at their selected price, so unsold output cannot occur. `R` realizes the allocation only if `F_t` permits all of it: every price is positive, no purchase is negative, every purchased variety is offered, each consumer can pay for its bundle at the selected prices from its actual wage, and each country's firms need no more labor than its labor force. Otherwise `R` reports the allocation infeasible, with the violated constraints and attempted quantities, and realizes nothing. A price or quantity that is not a finite number is an input error, and `R` raises. Krugman specifies no rationing or adjustment rule, so none is invented, and `R` never rewrites a selected action.
5. **Welfare.** Realized utility is the consumer's own `V` evaluated at its realized consumption, keeping preferences agent-side rather than in `F_t` or `R`. Only the ordinal comparison is validated.
6. **Technology.** `α` and `β` appear in firm `M` (cost beliefs) and in `F_t` (actual technology). The values coincide because Krugman's firms know their technology.
7. **Decision processes.** The firm's `D` brackets the best price by doubling or halving from its perceived marginal cost, then narrows it by golden-section search; it resolves price to about `5e-9` (relative) at any wage scale. If expected profit has no interior maximum (perceived demand elasticity `≤ 1`), it raises an error rather than returning a boundary price. The consumer's `D` is the closed-form maximizer of its `V`, verified against `V` by test.

### Limitations

- **Whole-number firm counts.** Firms are agents, so `n` must be a whole number (within a relative `1e-6`, which allows for the markup's numerical resolution); `coordinate_equilibrium` rejects fixtures where it is not. Krugman treats `n` as continuous.
- **Counterfactuals.** Consumers choose quantities from expected prices. A counterfactual firm price above the expected price makes the allocation infeasible (consumers cannot pay); one below it changes that firm's revenue but not the quantity demanded. Counterfactuals away from equilibrium do not represent Krugman's demand response.
- **Infeasible allocations.** Reported, not resolved: without a rationing rule, Configuration K says nothing about what would be realized instead.
- **Entry.** Potential entrants remain unmodeled. "No profitable entry" is checked with an active firm's own `V`, which an identical entrant would share under the large-number approximation.

---

## Configuration Audit

Configuration K must preserve the following boundaries:

1. Krugman’s assumptions remain Krugman assumptions.
2. TER definitions remain unchanged.
3. Equilibrium predictions are not inserted as inputs merely to reproduce them.
4. Agent behavior is distinguished from system-level outcomes.
5. Free entry remains part of Krugman’s equilibrium specification in baseline Configuration K; no entrant behavior or adjustment path is invented.
6. The equilibrium firm count `n` is treated as a derived equilibrium system quantity, not an agent outcome.
7. Entrant information and behavior are deferred until entrants are explicitly modeled; when they are, only source-supported information should be assumed unless a competing configuration intentionally changes it.
8. Equilibrium is evaluated using Krugman’s equilibrium concept.
9. Failure to reproduce a Krugman result must first be classified as a source-specification, mapping, or implementation problem before being treated as evidence of a TER framework failure.
10. Competing configurations must change assumptions or mechanisms explicitly rather than retrofitting Configuration K after observing its outcomes.

> Configuration → selected actions → realized outcomes → compare against Krugman hypotheses → compare against competing configurations

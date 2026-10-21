# Established Model Configuration

## Research Question

<!-- State the source model and the exact question this TER replication is testing. -->

## Configuration Inputs

<!-- List the source model's assumptions and fixed conditions. Classify each as a configuration input. -->

| Source-model element | TER placement | Classification | Notes |
|---|---|---|---|
|  |  | Configuration input |  |

## Agent Mappings

<!-- Map each modeled agent without changing the source model or TER definitions. -->

### Agent

| TER component | Specification |
|---|---|
| `G` |  |
| `M` |  |
| `F̂` |  |
| `V` |  |
| `H` |  |
| `D` |  |
| `C` |  |

**Classification:** Agent behavior

## Realized Outcomes

<!-- List what is produced when selected actions interact with objective conditions through `R`. -->

| Outcome | TER placement | Classification | Notes |
|---|---|---|---|
|  | `O_i` / `O_t` | Realized outcome |  |

## Source-Model Hypotheses

<!-- List predicted or derived results to test after the configuration is specified. Do not promote them into TER assumptions unless the source model explicitly treats them as inputs. -->

| Hypothesis or consistency condition | Classification | Test |
|---|---|---|
|  | Derived result / Equilibrium hypothesis |  |

## Configuration Audit

Use these classifications consistently:

- **Configuration input** — assumption or fixed condition supplied by the source model.
- **Agent behavior** — objective, belief, valuation, feasible action, decision process, or selected action specified for an agent.
- **Realization mechanism** — source-model mechanism governing how selected actions and objective conditions produce outcomes.
- **Derived result** — implication derived from the completed specification.
- **Equilibrium hypothesis** — source-model consistency condition checked against the resulting actions and outcomes.

Before implementation, confirm:

1. The source model has not been changed to fit TER.
2. TER definitions have not been changed to fit the source model.
3. Predicted results have not been inserted as inputs merely to reproduce them.
4. Assumptions, agent behavior, mechanisms, derived results, and equilibrium hypotheses are clearly separated.
5. Competing configurations can be created by changing explicit assumptions or mechanisms rather than fitting the original configuration after observing the result.

> Configuration → selected actions → realized outcomes → compare against source-model hypotheses → compare against competing configurations

# Bank run identification protocol

**Status** Proposed for an exact synthetic implementation first. Participant evidence is required to evaluate actual behavior. All added quantities and rules below belong to this specification. [Canonical TER](../../../theory/academic.md) · [TER methodology](../../ter-methodology-notes.md)

## Research question

Can TER improve causal attribution or forecast accuracy under the same banking contract, information, and evidence as Architecture B and a conventional withdrawal game? Equivalent encodings of the same candidate specifications imply the same identified sets and predictions. Use parity as a control. Measure any effect of the representation on researchers' ability to detect specification errors using the same bank cases.

The coordination example and structural script agree with an independent payoff check. Both yield the reported pure equilibria, and the healthy mixed withdrawal probabilities are $5/9$ and $1/4$ respectively. The structural guarantee needs $6/5$ at most. Its script checks one ledger and game, while the A and B mappings are analytical. The aggregate resource cap can hold even when cash and reserves fail to reconcile. Tests 09 and 23 supply the attempt/payment distinction, shared liquidity cap, and transition pattern. Their rule lacks individual claims and priority, and their configured belief update and repeat withdrawal requests do not carry over to this contract. [Coordination benchmark](../architecture-adversarial-bank-run.md) · [Structural benchmark](../architecture-adversarial-bank-run-structural.md) · [Structural script](../bank_run_structural_test.py) · [Test 09](../../tests/test_09_bank_run.py) · [Test 23](../../tests/test_23_unsustainable_imbalance.py)

## Shared economy and accounting

Three depositors invest one unit each at date 0. One is assigned an immediate liquidity need and submits the contract's mandatory early request. Two patient depositors can each make one early request (`E`) or wait (`W`). The bank and any insurer follow the contract. The patient payoff is consumption at the chosen date, with risk-neutral evaluation. One unit liquidated yields one unit at date 1, while one unit left invested yields $r=2$ at date 2. Early requests promise $d=7/5$ each, and a tender ends the claim on the maturity pool even when payment is partial.

The early liquidation limit $k$ can be $11/5$, $14/5$, or $3$. A restriction on early liquidation changes the cash available for early service. Initial principal, technology, and maturity return are identical across cells. Let $b_j$ be invested principal and $k_j$ the unused early limit after the $j$th request is served. With $b_0=3$ and $k_0=k$, bank payment is

$$
p_j=\min(d,b_{j-1},k_{j-1}),\qquad b_j=b_{j-1}-p_j,\qquad k_j=k_{j-1}-p_j.
$$

For $n$ early requests, $P=\sum_j p_j$, shortfall is $nd-P$, and the maturity pool is $r b_n$. Divide the pool equally among waiters. If everyone tenders, pay the residual pool to a passive residual claimant. That claimant has no decision in the game. Reconcile $P+b_n=3$, $P+k_n=k$, and total bank disbursement across both dates as $P+r b_n$. All balances and payments must be nonnegative. Only actual payments consume early liquidity, and each depositor can use a claim once.

Use the prior uncapped cases as regression checks. At $k=3$, rerun the healthy economy, the $r=11/10$ return shock, and the credible guarantee at $r=2$. In the guarantee check, taxpayers deposit $T=6/5$ into a separate reserve at date 0. The insurer tops up early receipts to $d$ and late patient receipts to at least $8/5$. Verify that total top-ups plus the reserve returned to taxpayers equal $T$ in every history. Report bank receipts and transfers separately. The randomized experiment uses the uninsured contract.

## Timing, information, and evidence

1. At date 0, assign the liquidity role and independently randomize $k$ and truthful disclosure timing at bank level. Give each of the six cells equal allocation within blocks. Players know the role assignment, contract, uniform capacity lottery, and disclosure schedule. Keep groups isolated from other groups' assignments and choices.
2. At date 1, deliver the capacity notice before simultaneous choices lock in the early arm. The delayed arm receives the same notice after choices lock. Before lock, its players know the prior over $k$. They receive no balance, rival choice, service order, or outcome information.
3. After lock, draw a uniform permutation of all three depositors and serve only those who tendered, in that order. Use the full permutation for fixed-state replays, including replays that change who tenders. Send each depositor their own settlement record after service. Pay out the maturity pool at date 2. There is one strategic decision window.

| Status | Evidence or assumption |
| --- | --- |
| Assigned and logged | Bank, role, capacity, disclosure schedule, and service permutation, with assignment source and timestamps. |
| Observed | Delivered messages, locked requests, individual payments, opening and closing balances, and maturity distributions. A displayed menu records offered actions. Use a separate pre-choice comprehension check if a claim depends on the perceived menu. |
| Inferred | Effects of disclosure and capacity, conditional on randomized assignment and the logged treatment protocol. An optional separate elicitation cohort can report the probability of full payment on a standardized second-in-queue request. Reports constrain beliefs only under a stated measurement model. |
| Assumed | Contract enforcement, risk neutrality, patient horizon, and equilibrium beliefs and strategies for the benchmark. Log any deviations from delivery or settlement, keep randomized groups in the intention-to-treat analysis, and report missing records and bounds. Withdrawal choices alone leave beliefs unidentified. |

An independent evidence author prepares fixtures from the contract and records the ledgers, assignments, message delivery, and outcome labels before the model authors receive the calibration data. Include externally scripted choices for isolation probes and retain their provenance as synthetic interventions. A later participant study uses actual locked choices and settlement logs under the same protocol.

## Equilibrium and architecture mappings

Solve the finite game conditional on each common information set. Patient strategies assign request probabilities given the notice history. For any action assigned positive probability, its expected payoff, integrated over the opponent's strategy, the service order, and the capacity posterior, must be at least that of the other action. The posterior is the disclosed point mass or the delayed arm's uniform prior. Enumerate pure and mixed equilibria, with independent patient randomization within each equilibrium. Check best responses and belief consistency outside the settlement rule. Report the entire equilibrium set. For point forecasting, average the distinct equilibrium outcome distributions with equal weights after solving for them. This forecasting convention is shared across mappings.

| Information at choice | Pure equilibria | Symmetric mixed probability of `E` |
| --- | --- | --- |
| Disclosed $k=11/5$ | `WW` | None |
| Disclosed $k=14/5$ | `WW`, `EE` | $3/11$ |
| Disclosed $k=3$ | `WW`, `EE` | $1/4$ |
| Delayed report with uniform prior | `WW`, `EE` | $27/35$ |

| Model | Mapping |
| --- | --- |
| A, canonical TER | The perceived patient menu is $\hat F=\{W,E\}$. $M$ holds notices and conditional beliefs about capacity, rival choices, and service. $G$ is consumption and $H$ covers both payout dates. $V$ evaluates each action's expected consumption using $G,M,H$. For each equilibrium, $D$ selects from the menu and assigns probability only to maximizing actions. One joint $R$ applies chosen requests to objective contract terms, balances, capacity, and the realized service permutation in $F_t$. Joint settlement supplies both individual receipts and system outcomes. The objective transition carries balances forward. Agent-side updates use delivered records. |
| B, state–decision–transition | $X_t$ records the objective contract and balances, and includes the permutation once drawn. $I_{i,t}$ records the same notice history and conditional beliefs. $A_i(I_{i,t})$ supplies the same menu. $\pi_i$ uses the same decision law. $\mathcal R$ settles joint tenders and $\mathcal Q$ advances the objective state. A declared observation process supplies $I_{i,t+1}$, with the same initial distribution and timing as A. |
| Conventional benchmark | Solve the finite Diamond–Dybvig-inspired withdrawal game directly from its extensive form. Chance assigns capacity, disclosure, and service order. Two patients choose at the same stage without seeing each other's actions. Payoffs come from the common ledger. The benchmark uses this finite contract and the equilibrium conditions above. |

Use the same evidence, assumptions, forecasting convention, and comparison budget. Compare shared trace fields on every profile, queue, and condition, then compare equilibrium sets and forecast distributions. Any mismatch or information leak fails the parity check. Apply each behavioral restriction across all three representations. [Architecture B](../architecture-b-state-transition.md) · [Diamond and Dybvig, 1983](https://doi.org/10.1086/261155)

## Identification and prediction

- **Information effect.** Compare the patient request share between early and delayed notice at each fixed $k$. This identifies the effect of earlier disclosure, which can include coordination through common information. Belief mediation requires additional evidence and restrictions. Allow a zero effect, including selection of `WW` in every cell.
- **Realization effect.** Within the delayed arm, compare total unpaid requested amounts between $k=11/5$ and $k=3$. Check the controlled contrast separately by replaying the same externally specified requests and permutation at both capacities. With all three requesting, increasing the cap from $11/5$ to $3$ reduces total shortfall by $4/5$. A single request is the nonbinding control. Verify the timing records and compare the joint patient request distribution across capacities in the delayed arm. Equal mean request rates can coexist with different frequencies of requests arriving together.
- **Observational equivalence.** At $k=14/5$, two and three early claims both yield aggregate early payments of $14/5$. Independently logged requests separate these histories. For a strategic test, compare a rule selecting `WW` in all cells with one selecting `EE` when $k\ge14/5$ is disclosed early and `WW` otherwise. Both are equilibrium selections and agree throughout the delayed baseline. Crossed arms distinguish their disclosure-effect predictions. Report the remaining identified set for any target on which compatible restrictions differ.
- **Held-out forecasts.** Lock predictions before seeing outcomes. Hold out whole banks, including all banks at $k=14/5$ and a preregistered split at the two outer levels. Analysts may condition payment forecasts on the randomized cell. In the delayed arm, the choice strategy still receives only the prior. The primary score is the mean of the two patient-request Brier losses per bank at $k=14/5$. Secondary scores cover requests at the outer levels and the bank-level probability that all early requests are paid. Report matched bank-level differences against both comparators for each score.

## Decision rules

| Test | Pass, fail, or inconclusive |
| --- | --- |
| Exact consistency | Require exact reconciliation, equivalent outcome distributions, and the reference equilibria on exhaustive replay. Any discrepancy fails this gate. Diagnose it before comparing performance. |
| Identification | Require supported cells, valid assignment and timing, and exact binding and nonbinding probes. Use simultaneous 95% bank-level intervals. A meaningful disclosure effect requires the interval to lie outside $\pm 0.05$ of the patient request share. An interval wholly within the band supports a negligible effect. Crossing a margin is inconclusive. For the delayed arm, require the intervals for differences in each of the four request-profile probabilities across capacities to lie within $\pm 0.05$. A timing leak or a precise difference beyond the margin fails that check. Low precision, missing evidence, or no realized binding cases leaves the corresponding participant realization interpretation inconclusive. |
| Prediction advantage | Define improvement as comparator minus TER Brier loss. Use simultaneous 95% paired bank-level intervals. TER passes for the primary target only if both lower bounds exceed 0.01. The claimed advantage fails if either upper bound is at or below 0.01. An interval that straddles the required margin is inconclusive unless the claim already fails against the other comparator. Report secondary scores even when the primary test fails. |
| Specification audit advantage | Give independent reviewers matched traces with and without planted errors in information timing, recording tender versus payment, or ledger conservation. Counterbalance representation assignment across reviewers and use different case variants for each reviewer. Hide fault labels and give each reviewer equal time, evidence, and diagnostics. Score the mean of the correct fault-type-and-stage rate on corrupted traces and the correct acceptance rate on clean traces. Require a gain of more than 10 percentage points over each comparator, using the same interval rule as prediction and pairing by reviewer. Interpret a gain as an audit advantage for this task. |

Failure of an economic or forecast restriction challenges that specification. A general architectural challenge needs a consequential distinction that the competing architecture cannot express faithfully, or a demonstrated inconsistency in its own boundaries.

## Reproduction and implementation gate

- Publish the contract, fixture provenance and hashes, exact arithmetic, software version, run command, and seed or enumeration order. Keep random streams for assignment, policy draws, and service separate. Archive the full pre-choice information, requests, realization inputs, payments, objective transitions, and delivered observations by bank and event.
- Commit the holdout split and scoring rules to the study record before releasing calibration outcomes. Use exhaustive cases for exact checks. For a participant run, lock the recruitment and sample size using a bank-level power calculation for the declared margins, specify exclusions and missing-data rules before assignment, and use bank-group resampling within design strata for paired intervals. Lock reviewer sample size and analysis before the audit exercise.
- Start with an independently authored ledger oracle and exact fixtures. Verify the historical cases with `python3 -B research/experiments/bank_run_structural_test.py`, then check the three mappings and their replay parity before adding the scoring harness. For a factual replay, rerun settlement against recorded actions and realization-time conditions before substituting any actions. Funding and disclosure changes use separately assigned scenarios.
- Proceed to participant forecasting and comparative audit claims after fixture parity, holdout custody, and the study's sample-size plan are in place. Synthetic results describe the specified model and recovery checks.

# Bank-run identification results

TER, Architecture B, and the conventional withdrawal game produced the same exact ledgers, equilibrium sets, and joint forecast laws under the frozen contract. All three had identical held-out losses. The two prescribed equilibrium-selection rules agreed in the delayed baseline and were distinguished by the crossed disclosure arms. These are exact model checks and synthetic recovery results. [Frozen protocol](protocol.md) · [Evidence and results archive](synthetic_run.zip)

## Exact verification

- **Pass.** All three mappings matched the ledger oracle on 648 histories covering all patient profiles, full service permutations, and impatient-role assignments. This includes 432 randomized-design histories and 216 historical histories. Factual replay preceded the action substitutions at fixed capacity and queue. Balances, individual receipts, standing claims, service priority, and prefunded transfers reconciled exactly.
- The equilibrium sets matched the protocol, including mixed early-request probabilities of $3/11$ at disclosed capacity $14/5$, $1/4$ at disclosed capacity $3$, and $27/35$ under delayed disclosure. The low-capacity disclosed game had only the all-wait patient equilibrium. The historical script reproduced its saved output. The largest historical guarantee payout was $6/5$.
- At fixed requests, raising the cap from $11/5$ to $3$ reduced the three-tender shortfall by $4/5$. It left the single-tender shortfall at zero. Two and three tenders both yielded $14/5$ in early bank payments at the middle cap. The request record resolved that ambiguity. [Historical structural results](../bank_run_structural_results.txt)

## Synthetic identification

Each of the three predeclared generators has 120 randomized blocks with one bank per capacity and disclosure cell. The disclosure estimate is early minus delayed notice in patient request share. Brackets give simultaneous 95% bootstrap intervals within each generator.

| Generator | Cap $11/5$ | Cap $14/5$ | Cap $3$ | Delayed-arm realization |
| --- | --- | --- | --- | --- |
| All wait | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] | Inconclusive. The profile check passed and no claims were rationed. |
| Disclosure responsive | 0 [0, 0] | +1 [1, 1] | +1 [1, 1] | Inconclusive. The profile check passed and no claims were rationed. |
| Equilibrium mixture | −0.538 [−0.663, −0.413] | −0.088 [−0.271, 0.104] | −0.238 [−0.413, −0.063] | Inconclusive. There were 142 binding cases at the outer caps. The joint-profile intervals did not establish equivalence within ±0.05. |

In the mixture, the low- and high-capacity disclosure contrasts cleared the five-point margin. The middle-capacity contrast was inconclusive. The delayed shortfall difference (low minus high) was 0.325 [0.030, 0.623] units. Its interpretation as a realization-only contrast remains inconclusive because of the profile check. The fixed-request probe established the mechanical effect separately.

The two deterministic selections matched every delayed bank in both scripted worlds. The crossed arms recovered the generating rule in each. Both deterministic rules failed to reproduce the mixture. The restricted identified set therefore contains one rule in each scripted world and neither rule in the mixture. The exercise leaves any belief-mediated effect unidentified.

## Held-out prediction

Each generator had 360 held-out banks. These include 240 at the middle cap and 60 at each outer cap. The equal-weight equilibrium forecast was fixed before the scorer loaded calibration or holdout outcomes. Each cell below gives the Brier loss shared by all three models.

| Generator | Request $11/5$ | **Request $14/5$** | Request $3$ | All paid $11/5$ | All paid $14/5$ | All paid $3$ |
| --- | --- | --- | --- | --- | --- | --- |
| All wait | 0.1743 | **0.2643** | 0.2611 | 0.2108 | 0.2055 | 0.2041 |
| Disclosure responsive | 0.1743 | **0.3401** | 0.3445 | 0.2108 | 0.3474 | 0.3499 |
| Equilibrium mixture | 0.1185 | **0.2492** | 0.2396 | 0.1113 | 0.2503 | 0.2434 |

**Predictive-advantage criterion failed.** Comparator-minus-TER differences were zero for every bank and score, with paired intervals of [0, 0]. The primary gain fell below the 0.01 threshold against both comparators. Identical outcome laws imply this result for any labels scored under the matched specification.

## Reproduction

Run from the repository root with Python 3.14.7. The implementation uses the standard library and the existing TER decision interface.

```sh
run_dir=$(mktemp -d)
python3 -B -m research.experiments.bank_run_identification.fixtures --output "$run_dir/evidence"
python3 -B -m research.experiments.bank_run_identification.compare --fixtures "$run_dir/evidence" --output "$run_dir/results"
python3 -B research/experiments/bank_run_structural_test.py
python3 -B run_tests.py research/tests/test_bank_run_identification.py
python3 -B run_tests.py
```

The archive contains both fixture splits, exact histories, a hash manifest, locked forecasts, and full results, including the delayed-profile contrasts. The manifest records separate assignment, policy, service, and resampling seeds. Ledger checks, equilibrium enumeration, and losses use exact fractions. Intervals use 4,096 complete-block draws for the identification contrasts and paired banks within disclosure strata for score differences. Bonferroni adjustment applies within each reported interval family. [Archived run](synthetic_run.zip)

## Limits

- The oracle allocates numbered cash units and imports no model code. Fixtures were generated and hashed before implementation of the model mappings. The same implementer authored the oracle and mappings. The independent-author and external holdout-custody requirements remain outstanding.
- The fixture generators prescribe their own equilibrium selections. Recovering them checks the experiment's diagnostics under known conditions. The mixture also uses the forecasting convention, so its loss is a calibration check under the stipulated generator.
- The 120-block design exercises synthetic scoring. A participant study still needs a power calculation, independent data, and a locked analysis plan. Reviewer advantage is **inconclusive** because no independent reviewers were enrolled. The matched game supplies no evidence for architecture-wide superiority.

# Adversarial Architecture Test 02: Structural Bank Run With Funded Insurance

**Status:** Completed exact finite-model benchmark. Not an empirical validation, full reproduction of Diamond–Dybvig (1983), or proof of a universal framework.

**Architecture A:** TER v0.5.0 (`academic.md`), unchanged. **Architecture B:** State–Decision–Transition Economics draft v0.1.0 (`architecture-b-state-transition.md`), unchanged.

**Executable check:** `bank_run_structural_test.py`, Python standard library, exact rational arithmetic. Run: `python bank_run_structural_test.py`.

## 1. Economic model independent of either architecture

This **new, explicitly simplified finite Diamond–Dybvig-inspired model** includes three depositors, a bank, and a public guarantor. It is **not the original Diamond–Dybvig contract optimization model**, does not establish optimal risk sharing or a general insurance theorem, and assumes risk-neutral patient depositors for the equilibrium calculations.

- **Dates:** 0 (deposit/funding), 1 (withdrawal requests and sequential service), 2 (maturity and late consumption). Time 1 includes ordered servicing events. Each depositor contributes one unit at date 0; the bank invests all three units in a project that yields **1 per unit liquidated at date 1** or **2 per unit held to date 2** (except in the fundamental-shock regime, where late return is **1.1**). Thus early liquidation destroys potential long-run production.
- **Types:** one genuinely impatient depositor withdraws at date 1; two patient depositors choose independently between **W** (wait) and **D** (request early withdrawal). Their date-1 choice is simultaneous; early requests are serviced in a uniformly random order. Each patient seeks to maximize **the consumption received at their chosen consumption date**; other utility structures would change the model and must not be silently inferred.
- **Contract:** promised date-1 payment is **1.4** per request, **subject to available assets and sequential service**. On each arrival the bank liquidates only the assets needed to pay the claim, up to remaining assets. Date-2 output from remaining assets is divided equally among those who waited. Insolvent late claims receive the actual residual, including zero.
- **Financed guarantee intervention:** only in the third regime, a public guarantor promises every early claimant at least **1.4** and every patient who waits at least **1.6**. A **1.2-unit prefunded treasury reserve**, paid at date 0 by separately modeled outside taxpayers, covers shortfalls in every possible withdrawal history. Any unspent public reserve stays with taxpayers. The guarantee is common knowledge and enforceable. The tax is an economic cost/transfer and is **not free additional bank output**. This is an intentionally stipulated public guarantee, not an endogenous derivation of government financing or deposit-insurance optimality.

Let `E` denote the early-withdrawal queue (including the impatient depositor), `L` the set of patient waiters, and `b_0=3`. Sequential service and the bank budget obey

\[
p_j=\min\{1.4,b_{j-1}\},\quad b_j=b_{j-1}-p_j\qquad(j\text{ in the early queue}).
\]

If `b_E` is the bank investment left after all early requests, each patient waiter receives

\[
c_{i,2}=\frac{r b_E}{|L|}\quad(i\in L),
\]

where `r=2` normally or `r=1.1` in the fundamental-shock regime. All three early claimants together can receive at most 3 from the bank. Under insurance the guarantor pays exactly the shortfalls between these bank payments and the stated guaranteed minimums, with total top-ups no greater than 1.2 in every modeled history. The guarantee leaves investment returns unchanged but changes final consumption through fiscal transfers.

## 2. Derived consumption payoffs and exact equilibrium result

Each cell is expected realized consumption of **patient 1, patient 2**, averaging only over possible random service orders. The impatient depositor's receipts are accounted for in every cell but not listed. These payoffs are **derived from the bank asset ledger**, not separately stipulated.

| Regime | WW | WD | DW | DD | Pure Nash equilibria |
|---|---|---|---|---|---|
| Healthy, `r=2` | (1.6, 1.6) | (0.4, 1.4) | (1.4, 0.4) | (1.0, 1.0) | **WW, DD** |
| Fundamental return shock, `r=1.1` | (0.88, 0.88) | (0.22, 1.4) | (1.4, 0.22) | (1.0, 1.0) | **DD** |
| Funded and credible guarantee, `r=2` | (1.6, 1.6) | (1.6, 1.4) | (1.4, 1.6) | (1.4, 1.4) | **WW** |

**Proof by unilateral deviation:** Healthy: when the other patient waits, waiting pays `1.6 > 1.4`; when the other withdraws, withdrawing pays `1.0 > 0.4`. Both WW and DD are equilibria. Under the fundamental shock, withdrawing beats waiting whether the other waits (`1.4 > 0.88`) or withdraws (`1.0 > 0.22`), yielding unique DD. Under the guarantee, waiting always pays `1.6 > 1.4`, yielding unique WW. Exhaustive enumeration verifies each pure strategy profile, every sequential service queue, and the guarantor's maximum deficit, using exact fractions.

**Belief threshold (healthy):** For a patient assigning subjective probability `q` to the other patient's early withdrawal, `E[W]=1.6-1.2q` and `E[D]=1.4-0.4q`. Thus `D` is preferred if `q>0.25`; at equality the patient is indifferent. This describes best response under beliefs, not equilibrium selection without consistency of actual strategies and beliefs.

**Fiscal audit:** In histories with two early claims and one late claimant, bank payments are 2.8 at date 1 and 0.4 at date 2, and the public guarantor tops up 1.2. With three early claims, the bank pays total 3 and the guarantor tops up 1.2. The fully funded maximum is **1.2**, taken from taxpayers' separate prior resources. Nothing creates a risk-free guarantee without resources.

## 3. Architecture A, canonical TER mapping

For each patient depositor and the bank's explicit interactions:

- `G`: benchmark-specific consumption objective for valuation; `H`: whether the patient consumes at date 1 or 2 as relevant to the considered action. `V`: expected consumption value of W and D using the perceived other-withdrawal probability and believed contractual consequences.
- `M`: subjective withdrawal probability, beliefs about returns, guarantees and enforceability, and what the agent has learned. **No depositor is given access to objective conditions not observed by them.** `F̂={W,D}` is the perceived set of actions available to attempt, not a guarantee that a bank will pay a requested amount.
- `D`: explicit expected-consumption maximization (this is a **model-specific optimization assumption**, not a universal TER rule); `C`: selected W or D.
- `F_t`: objective bank assets, investment returns, contractual and fiscal obligations, remaining balance before each sequential payment, actual queue, and the objectively realized conditions at the relevant realization event. Actual bank conditions are not passed into `D` unless perceived via `M`/`F̂`.
- Joint `R(C_1,C_2,C_3,F_t)`: the **specified** sequential ledger and subsequent maturity/guarantee settlement, with individual and system outcomes derived from the same joint realization. Here the impatient depositor chooses D; the bank's and state's institutional obligations are included in the objective constraints and settlement mechanism.
- `O_t`: payments, liquidations, losses, and public top-ups. Model 5.5 can pass realized balance-sheet consequences to later `F` and *observed* payment information to later `M`; it must not give depositors knowledge of unobserved outcomes. The stages within dates 1–2 are explicitly indexed if the implementation models subsequent decisions.

This adheres to TER's distinction between **action selected**, **what is objectively feasible at realization**, and **actual payment received**. It does not introduce any new TER core primitive.

## 4. Architecture B mapping

- `X_t`: objective project return, bank assets, outstanding contract and insurer reserve at each stage.
- `I_i`: the depositor's information and subjective withdrawal probability; distinguish observations and beliefs through **model-specific** fields.
- `A_i(I_i)={W,D}` and `π_i`: the same expected-consumption choice as TER (and the impatient depositor's fixed early need).
- `𝓡`: the same sequential-service, maturity and insurance accounting outcomes from the joint action profile and objective state.
- `𝓠`: updates the assets, liabilities, fiscal reserves and later investment returns from the outcomes. A separately specified observation mechanism delivers stage-appropriate information to agents before any later choice.

**Important:** B's notation is shorter but its complete implementation requires *the same* subjective-belief model, action timing, contractual accounting, bank-return process and fiscal constraint. Neither the stochastic realization kernel nor the transition kernel can compensate for an unspecified accounting identity or an unjustified information process.

## 5. Can either architecture explain the cause of a run?

No, **not from observed withdrawals alone**. DD is compatible with pessimism in a healthy bank and with a genuine low-return fundamental shock. The model predicts different outcomes under credible insurance and different late-return disclosures, but only given **independent evidence** about information, fundamentals, funding, incentives, and policy credibility. A framework's symbol names do not identify unobservable causes.

The two mappings generate **identical consumption vectors and strategic incentives by construction** when the benchmark economy and information rules are held fixed. No mathematical prediction or efficiency improvement can be attributed to one architecture here. The observation that TER makes `M` distinct from `F` protects model transparency, but is not proof that TER predicts better.

## 6. Verdict and what would justify changing TER

**Current outcome: retire Architecture B v0.1.0's claim of superior economy of assumptions.** Shorter notation does not reduce economic assumptions: both need the identical bank ledger, choice functions, beliefs and financing mechanism. This structural test **does not falsify** B as a general framework or validate TER empirically.

**Actionable TER improvement proposal (outside the canonical paper):** add a *methodological specification contract* for tests involving strategic interaction and money: (1) formal event timing and domains; (2) explicit realization ledger satisfying stock-flow and public financing identities; (3) independently constrained beliefs, information and decision rules; (4) declared equilibrium notion, best-response deviations and observational equivalences; (5) comparison to a predeclared non-TER baseline. These are implementation/research standards, **not new axioms, variables or mechanisms in TER**.

**Further adversarial check if pursuing general superiority:** models with heterogeneity, production, endogenous price formation, noisy private signals, public finance and aggregate shocks; predeclare whether the research goal is reproduction, identification, conditional prediction or efficient implementation. One positive finite-game test cannot settle architecture-wide superiority.

## Reference and limits

- Diamond, Douglas W., and Philip H. Dybvig (1983), *Bank Runs, Deposit Insurance, and Liquidity*, *Journal of Political Economy* 91(3): 401–419, DOI `10.1086/261155`. Structural motivation: maturity transformation, sequential service, and bank runs. This example replaces the paper's continuum agents, optimal bank contract, utility assumptions, and type distribution with a **three-depositor finite model**; no original quantitative theorem is claimed.
- TER `academic.md` v0.5.0, §§3–5 and §7.10; `ter-methodology-notes.md`, sections “Variable Placement” and “Specification Rules”.
- Architecture B `architecture-b-state-transition.md` draft v0.1.0.
- The model is analytical and simulated exhaustively, **not calibrated to bank data**. The guarantee is assumed credible and fully prefunded from a separate taxpayer sector; no welfare ranking is claimed because the taxpayer utility and alternative use of funds were not modeled.

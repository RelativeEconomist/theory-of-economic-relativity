"""
TER Replication Test 28: Lottery Tickets -- One Decision, Many Explanations
Canonical TER: theory/academic.md, Models 5.1 and 5.2; Section 7.10

Economic question
-----------------
Alex buys a $20 lottery ticket that loses money on average. Does that
choice reveal why Alex bought it? Can different specifications that all
buy today be told apart by how they respond when conditions change?

Scenario
--------
Alex chooses between buying one $20 ticket and skipping it. The ticket
wins a $10,000,000 prize with actual probability 1 in 1,000,000 and
otherwise pays nothing, so a ticket's actual expected net monetary
return is 10 - 20 = -$10. Alex has $50 available for this decision.

Three illustrative specifications of Alex all buy in this baseline:

1. Mistaken odds: Alex believes the chance is 1 in 250,000 and selects
   by expected monetary value (believed: 40 - 20 = +$20).
2. Entertainment value: Alex knows the actual odds and also values the
   experience at $15 (10 - 20 + 15 = +$5).
3. Habit: Alex buys one ticket whenever it is affordable and costs at
   most $30, without comparing valuations.

They are constructed examples, not empirically validated explanations
or an exhaustive list of motives. Each condition is a separate,
single-decision experiment that changes one baseline condition.

TER instantiation
-----------------
Component        Mistaken odds         Entertainment value   Habit
G   Objective    expected money        expected money plus   not consulted
                                       enjoyment
M   Model of     believed odds 1 in    believed odds equal   believed odds 1 in
    Reality      250,000; price,       actual odds; price,   250,000; price,
                 prize, funds          prize, funds          prize, funds
F̂   Perceived    buy and skip if the believed price is within believed funds,
    Feasible Set otherwise skip only (same rule for all three)
V   Valuation    V(buy) = believed     V(buy) = believed     not used
                 odds x prize - price  odds x prize - price
                                       + $15; V(skip) = 0
H   Horizon      this draw only        this draw only        not used
D   Decision     maximize V; skip on   maximize V; skip on   buy if buy is in F̂
    Process      equal values          equal values          and believed price
                                                             <= $30, else skip
C   Selected     buy or skip (observed)
F_t aspects      actual price, prize, win probability, available funds, and
                 whether this draw's ticket wins
R   Reality      charges the price and pays the prize on a winning draw;
                 a purchase above actual funds fails
O   Realized     status, amount spent, prize received, net monetary return
    Outcome

    C = D(F_hat, M, V(. | G, M, H)); then O = R(C, F_t)

M informs V for the two valuation specifications and informs D directly
for the habit. D never reads F_t: the actual probability and the
realized draw enter only R. Enjoyment is part of V, never of O, so every
reported return is monetary. This is an agent-level specification; no
system outcome is defined.

Odds disclosure
---------------
Alex is shown the official win probability before deciding and treats
it as credible: the believed probability in M is replaced by the
disclosed one. No other belief, F̂, the valuation rule, or D changes,
and the actual probability is unchanged. Because V is calculated from M,
the same valuation rule can now assign buying a different value. Whether
C changes depends on whether the specification's selection uses that
belief, directly or through V.

Assumptions
-----------
- All numbers are stipulated for this exercise, not empirical claims
  about lotteries or players. They were fixed before comparing
  conditions and are not tuned per condition.
- One fixed prize; otherwise zero payout. Taxes, shared jackpots,
  secondary prizes, annuity options, and other ticket buyers are omitted.
- Alex perceives the price, prize, and available funds correctly. Win
  probability is the only belief that can be wrong.
- A ticket is affordable when its price is at most the available funds.
  Alex does not perceive buying as available otherwise. R also checks
  actual funds, so an unaffordable purchase fails rather than
  overdrawing.
- Both valuation specifications skip when buying and skipping have equal
  value. The habit buys at exactly its $30 maximum price. These tie and
  threshold rules are scenario choices, not TER rules.
- The $15 enjoyment value does not depend on price, prize, or odds.
- Each decision is one draw. Winnings, repeated purchases, learning from
  outcomes, and realized enjoyment are not modeled.
- Outcome probabilities are exact: each condition is evaluated under
  both draw states and weighted by the actual probability. Nothing is
  sampled, so no seed is needed.

Hypothesis
----------
In this configured scenario (B = buy, S = skip; ticket return = actual
expected net monetary return of buying one ticket, which is hypothetical
when no specification buys):

Condition          Change from baseline    Mistaken  Enjoyment  Habit  Ticket return
baseline           none                    B         B          B      -$10
price $28          price 20 -> 28          B         S          B      -$18
price $35          price 20 -> 35          B         S          S      -$25
price $45          price 20 -> 45          S         S          S      -$35
prize $2,000,000   prize 10M -> 2M         S         S          B      -$18
prize $20,000,000  prize 10M -> 20M        B         B          B        $0
odds disclosed     odds shown to Alex      S         B          B      -$10
funds $19          funds 50 -> 19          S         S          S      -$10, hypothetical

With $19, no ticket is affordable: every specification selects skip, and
the expected monetary return of that selected action is $0.

1. All three specifications buy in the baseline, where the actual
   expected net monetary return is negative.
2. Each condition produces the choices in the table above.
3. Price, prize, and disclosure each separate at least one specification
   from the others; the baseline, a larger prize, a $45 price, and
   insufficient funds do not.
4. Disclosure changes every specification's believed probability to the
   actual one without changing the actual probability. Only the
   mistaken-odds choice changes.
5. Thresholds, ties, and budget limits behave as stated above.
6. Outcome probabilities and net payoffs match the lottery exactly.
7. Results are reproducible.
"""

import unittest
from fractions import Fraction

from research.scenarios.lottery_tickets import (
    ACTUAL_WIN_PROBABILITY, BASELINE, BUY, CONDITIONS, ENTERTAINMENT, HABIT,
    HABIT_MAXIMUM_PRICE, MISTAKEN_ODDS, MISTAKEN_WIN_PROBABILITY, SKIP,
    SPECIFICATIONS, TICKET_PRICE, comparison_table, expected_net_return,
    lottery_scenario, outcome_distribution,
)
from research.ter import run_scenario


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# The hypothesis table, written out independently of the scenario's rules.
EXPECTED_CHOICES = {
    "baseline": (BUY, BUY, BUY),
    "price $28": (BUY, SKIP, BUY),
    "price $35": (BUY, SKIP, SKIP),
    "price $45": (SKIP, SKIP, SKIP),
    "prize $2,000,000": (SKIP, SKIP, BUY),
    "prize $20,000,000": (BUY, BUY, BUY),
    "odds disclosed": (SKIP, BUY, BUY),
    "funds $19": (SKIP, SKIP, SKIP),
}

# Actual expected net return of one ticket, in dollars: odds x prize - price.
EXPECTED_TICKET_RETURNS = {
    "baseline": 10 - 20,
    "price $28": 10 - 28,
    "price $35": 10 - 35,
    "price $45": 10 - 45,
    "prize $2,000,000": 2 - 20,
    "prize $20,000,000": 20 - 20,
    "odds disclosed": 10 - 20,
    "funds $19": 10 - 20,
}


def selected_action(specification, **changes):
    scenario = lottery_scenario(specification, **changes)
    return run_scenario(scenario).agent(specification.name).selected_action


class TestLotteryTickets(unittest.TestCase):
    TEST_NAME = "Test 28: Lottery Tickets -- One Decision, Many Explanations"

    @classmethod
    def setUpClass(cls):
        cls.table = {row["condition"]: row for row in comparison_table()}

    def choices(self, condition):
        row = self.table[condition]
        return tuple(row["choices"][spec.name] for spec in SPECIFICATIONS)

    def test_all_specifications_buy_despite_negative_actual_return(self):
        self.assertEqual(self.choices("baseline"), (BUY, BUY, BUY))
        self.assertLess(self.table["baseline"]["hypothetical_ticket_expected_net_return"], 0)

    def test_each_condition_changes_exactly_one_baseline_condition(self):
        for label, changes in CONDITIONS[1:]:
            with self.subTest(condition=label):
                self.assertEqual(len(changes), 1)
                ((key, value),) = changes.items()
                self.assertNotEqual(value, BASELINE[key])

    def test_conditions_produce_hypothesized_choices_and_returns(self):
        self.assertEqual(set(self.table), set(EXPECTED_CHOICES))

        for label, expected in EXPECTED_CHOICES.items():
            with self.subTest(condition=label):
                row = self.table[label]
                self.assertEqual(self.choices(label), expected)
                self.assertEqual(
                    row["hypothetical_ticket_expected_net_return"], EXPECTED_TICKET_RETURNS[label]
                )
                for spec in SPECIFICATIONS:
                    bought = row["choices"][spec.name] == BUY
                    self.assertEqual(
                        row["expected_net_returns"][spec.name],
                        EXPECTED_TICKET_RETURNS[label] if bought else 0,
                    )

    def test_some_conditions_distinguish_specifications_and_others_do_not(self):
        distinguishing = {
            label for label, row in self.table.items()
            if row["distinguishes_specifications"]
        }

        self.assertEqual(
            distinguishing,
            {"price $28", "price $35", "prize $2,000,000", "odds disclosed"},
        )

    def test_disclosure_updates_beliefs_but_not_actual_odds(self):
        for spec in SPECIFICATIONS:
            with self.subTest(specification=spec.name):
                before = lottery_scenario(spec)
                after = lottery_scenario(spec, odds_disclosed=True)
                beliefs_before = before.agents[0].model_of_reality
                beliefs_after = after.agents[0].model_of_reality

                self.assertEqual(
                    beliefs_after["believed_win_probability"], ACTUAL_WIN_PROBABILITY
                )
                self.assertEqual(
                    {k: v for k, v in beliefs_after.items() if k != "believed_win_probability"},
                    {k: v for k, v in beliefs_before.items() if k != "believed_win_probability"},
                )
                self.assertEqual(after.parameters, before.parameters)
                self.assertEqual(after.initial_state, before.initial_state)

        # The habit's belief changes, but its selection does not use it.
        self.assertEqual(
            lottery_scenario(HABIT).agents[0].model_of_reality["believed_win_probability"],
            MISTAKEN_WIN_PROBABILITY,
        )
        self.assertEqual(selected_action(HABIT, odds_disclosed=True), BUY)

    def test_valuation_thresholds_skip_on_equal_values(self):
        # Mistaken odds: believed expected prize is 1/250,000 x 10M = $40.
        self.assertEqual(selected_action(MISTAKEN_ODDS, ticket_price=39), BUY)
        self.assertEqual(selected_action(MISTAKEN_ODDS, ticket_price=40), SKIP)
        self.assertEqual(selected_action(MISTAKEN_ODDS, jackpot=5_000_000), SKIP)

        # Entertainment: $10 expected prize + $15 enjoyment = $25.
        self.assertEqual(selected_action(ENTERTAINMENT, ticket_price=24), BUY)
        self.assertEqual(selected_action(ENTERTAINMENT, ticket_price=25), SKIP)

    def test_habit_follows_its_price_rule_without_valuation(self):
        # valuation_not_used raises if called, so these runs also show
        # the habit's D never consults V.
        self.assertEqual(selected_action(HABIT, ticket_price=HABIT_MAXIMUM_PRICE), BUY)
        self.assertEqual(selected_action(HABIT, ticket_price=HABIT_MAXIMUM_PRICE + 1), SKIP)
        self.assertEqual(selected_action(HABIT, jackpot=1), BUY)

    def test_budget_limit_removes_buying_and_blocks_purchase(self):
        for spec in SPECIFICATIONS:
            with self.subTest(specification=spec.name):
                self.assertEqual(selected_action(spec, available_funds=TICKET_PRICE), BUY)

                scenario = lottery_scenario(spec, available_funds=TICKET_PRICE - 1)
                self.assertEqual(scenario.agents[0].perceived_feasible_set, [SKIP])

                alex = run_scenario(scenario).agent(spec.name)
                self.assertEqual(alex.selected_action, SKIP)
                # R enforces actual funds even if buy were attempted.
                self.assertEqual(alex.outcome_for(BUY).outcome["status"], "purchase_failed")
                self.assertEqual(alex.outcome_for(BUY).outcome["net_return"], 0)

        row = self.table["funds $19"]
        self.assertFalse(row["ticket_affordable"])
        self.assertLess(row["hypothetical_ticket_expected_net_return"], 0)
        self.assertEqual(set(row["expected_net_returns"].values()), {0})

    def test_outcome_probabilities_and_net_payoffs_are_exact(self):
        action, distribution = outcome_distribution(ENTERTAINMENT)

        self.assertEqual(action, BUY)
        self.assertEqual(
            distribution,
            [
                (Fraction(1, 1_000_000),
                 {"status": "won", "spent": 20, "prize": 10_000_000,
                  "net_return": 9_999_980}),
                (Fraction(999_999, 1_000_000),
                 {"status": "lost", "spent": 20, "prize": 0, "net_return": -20}),
            ],
        )
        self.assertEqual(expected_net_return(distribution), -10)

        action, distribution = outcome_distribution(MISTAKEN_ODDS, odds_disclosed=True)

        self.assertEqual(action, SKIP)
        self.assertEqual(
            distribution,
            [(1, {"status": "skipped", "spent": 0, "prize": 0, "net_return": 0})],
        )

    def test_results_are_reproducible(self):
        self.assertEqual(comparison_table(), list(self.table.values()))


if __name__ == "__main__":
    unittest.main()

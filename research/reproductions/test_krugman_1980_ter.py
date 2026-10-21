"""Validation of Configuration K (Krugman 1980, Section I) executed through TER.

Follows krugman_1980_validation.md: pricing, output per firm, closed-economy
consistency, integrated trade, welfare. Expected values come from
krugman_1980.py, the external benchmark implementing Krugman's closed-form
solution without TER; the configuration never uses it.

The markup is a TER firm decision. Output per firm, firm count, and
expected prices are derived from it with Krugman's equilibrium conditions;
wages are equal by the goods-market derivation. Realization checks confirm
that the joint R realizes that derived equilibrium; they are not
independent evidence for the conditions used to derive it. See "TER
Execution Results" in krugman_1980_validation.md for each result's status.

Run with:
    python3 run_tests.py research/reproductions/test_krugman_1980_ter.py

Fixture values are illustrative test inputs, not empirical claims.
"""

import unittest
from unittest import mock

from research.reproductions.krugman_1980 import (
    ALPHA,
    BETA,
    FOREIGN_LABOR,
    HOME_LABOR,
    THETA,
    import_share,
    imports_in_wage_units,
    output_per_firm,
    price_wage_ratio,
    utility_per_consumer,
    variety_count,
)
from research.reproductions import krugman_1980_ter
from research.reproductions.krugman_1980_ter import (
    FOREIGN_AUTARKY,
    HOME_AUTARKY,
    INTEGRATED_TRADE,
    WAGE,
    coordinate_equilibrium,
    firm_spec,
    krugman_scenario,
)
from research.ter import Scenario, run_scenario
from research.ter.feasible import Interval, Region

# The firm's price comes from a numerical search of a flat maximum, which
# resolves it to about 5e-9 (relative); every equilibrium quantity is
# derived from that price. Comparisons are relative, with an absolute floor
# for values near zero (e.g. profit): as strict as 7 decimal places at unit
# scale, stricter at larger scales.
TOLERANCE = 1e-7


class CloseTestCase(unittest.TestCase):
    def assertClose(self, actual, expected):
        self.assertLessEqual(
            abs(actual - expected),
            TOLERANCE * max(1.0, abs(expected)),
            f"{actual} != {expected} within relative tolerance {TOLERANCE}",
        )


RESULTS = {
    "home": run_scenario(HOME_AUTARKY),
    "foreign": run_scenario(FOREIGN_AUTARKY),
    "integrated": run_scenario(INTEGRATED_TRADE),
}
LABOR = {"home": HOME_LABOR, "foreign": FOREIGN_LABOR}


def firms(result):
    return [name for name in result.agent_states if "_firm_" in name]


def consumers(result):
    return [name for name in result.agent_states if name.endswith("_consumer")]


def outcome(result, name):
    return result.agent(name).outcome


class ConfigurationKInformationBoundaryTest(CloseTestCase):
    TEST_NAME = "Krugman K: Static Decisions and Information Boundaries"

    def test_every_agent_acts_once_at_one_decision_point(self):
        for key, result in RESULTS.items():
            with self.subTest(configuration=key):
                self.assertEqual(len(result.trace), 1)
                self.assertEqual(set(result.trace[0].actors), set(result.agent_states))

    def test_agents_hold_expectations_not_other_agents_actions(self):
        result = RESULTS["integrated"]
        consumer_model = result.trace.initial_agents["home_consumer"].model_of_reality
        firm_model = result.trace.initial_agents["home_firm_1"].model_of_reality

        self.assertEqual(set(consumer_model), {"income", "expected_prices"})
        self.assertNotIn("price", firm_model)
        self.assertEqual(result.trace[0].observations, {})

    def test_mathematical_perceived_feasible_sets_are_used(self):
        result = RESULTS["integrated"]

        firm_set = result.agent_states["home_firm_1"].perceived_feasible_set
        consumer_set = result.agent_states["home_consumer"].perceived_feasible_set

        self.assertEqual(firm_set, Interval(0, float("inf"), closed_low=False))
        self.assertIsInstance(consumer_set, Region)
        self.assertEqual(set(consumer_set.coordinates), set(firms(result)))


class ConfigurationKEquilibriumDerivationTest(CloseTestCase):
    TEST_NAME = "Krugman K: Equilibrium Derived From the TER Markup"

    def test_derivation_follows_the_ter_decision_not_the_benchmark(self):
        # Firms whose elasticity belief implies theta = 0.7 select a higher
        # markup, and the derived equilibrium follows that decision (12
        # firms), not the benchmark's theta = 0.75 answer (10 firms).
        with mock.patch.object(krugman_1980_ter, "THETA", 0.7):
            derived = coordinate_equilibrium({"home": HOME_LABOR})

        self.assertClose(derived["markup"], price_wage_ratio(BETA, 0.7))
        self.assertClose(derived["firm_count"]["home"], variety_count(HOME_LABOR, ALPHA, 0.7))
        self.assertNotEqual(derived["firm_count"]["home"], variety_count(HOME_LABOR, ALPHA, THETA))

    def test_chain_from_the_ter_markup_reproduces_krugman(self):
        # TER markup -> zero profit -> output -> full employment -> firm count.
        derived = coordinate_equilibrium(LABOR)

        self.assertClose(derived["markup"], price_wage_ratio(BETA, THETA))
        self.assertClose(derived["output_per_firm"], output_per_firm(ALPHA, BETA, THETA))
        self.assertEqual(
            derived["firm_count"],
            {country: variety_count(labor, ALPHA, THETA) for country, labor in LABOR.items()},
        )

    def test_scenarios_use_the_derived_equilibrium(self):
        derived = coordinate_equilibrium(LABOR)
        result = RESULTS["integrated"]
        expected_prices = result.trace.initial_agents["home_consumer"].model_of_reality[
            "expected_prices"
        ]

        self.assertEqual(set(expected_prices.values()), {derived["expected_price"]})
        self.assertEqual(len(firms(result)), sum(derived["firm_count"].values()))


class ConfigurationKFirmPricingTest(CloseTestCase):
    TEST_NAME = "Krugman K: Firm Pricing Through V and D"

    def test_selected_price_satisfies_markup(self):
        for key, result in RESULTS.items():
            for firm in firms(result):
                with self.subTest(configuration=key, firm=firm):
                    self.assertClose(
                        result.agent(firm).selected_action / WAGE,
                        price_wage_ratio(BETA, THETA)
                    )

    def test_selected_price_maximizes_the_firms_own_valuation(self):
        firm = RESULTS["home"].agent("home_firm_1")
        price = firm.selected_action

        for alternative in (price * 0.99, price * 1.01, price * 0.5, price * 2):
            with self.subTest(alternative=alternative):
                self.assertGreater(firm.value_of(price), firm.value_of(alternative))

    def test_markup_is_independent_of_perceived_market_size(self):
        # The markup comes from the elasticity in M, not the expected
        # market level: a firm expecting a much larger market prices the
        # same. This is why coordinate_equilibrium needs no iteration.
        larger = firm_spec("home_firm_1", 10 * HOME_LABOR, 10, 2.0, WAGE)
        scenario = HOME_AUTARKY.variant(
            agents=[larger] + HOME_AUTARKY.agents[1:]
        )

        self.assertClose(
            run_scenario(scenario).agent("home_firm_1").selected_action,
            price_wage_ratio(BETA, THETA) * WAGE
        )

    def test_selected_prices_match_the_expected_prices(self):
        # Fixed-point confirmation, not independent evidence: the expected
        # price was derived from this same firm decision.
        for key, result in RESULTS.items():
            expected_prices = result.trace.initial_agents[consumers(result)[0]].model_of_reality[
                "expected_prices"
            ]

            for firm in firms(result):
                with self.subTest(configuration=key, firm=firm):
                    self.assertClose(
                        result.agent(firm).selected_action, expected_prices[firm]
                    )


class ConfigurationKClosedEconomyTest(CloseTestCase):
    TEST_NAME = "Krugman K: Closed-Economy Consistency"

    def test_realized_output_per_firm(self):
        for country in LABOR:
            result = RESULTS[country]

            for firm in firms(result):
                with self.subTest(country=country, firm=firm):
                    self.assertClose(
                        outcome(result, firm)["output"],
                        output_per_firm(ALPHA, BETA, THETA)
                    )

    def test_active_firms_earn_zero_profit(self):
        for country in LABOR:
            result = RESULTS[country]

            for firm in firms(result):
                with self.subTest(country=country, firm=firm):
                    self.assertClose(outcome(result, firm)["profit"], 0)

    def test_no_profitable_entry_remains(self):
        # An identically configured entrant facing the same conditions has
        # the active firm's V; its best expected profit is not positive.
        for country in LABOR:
            firm = RESULTS[country].agent(f"{country}_firm_1")

            with self.subTest(country=country):
                self.assertLessEqual(firm.value_of(firm.selected_action), 1e-7)

    def test_goods_market_clears_without_rationing(self):
        # R realizes the allocation only if F_t permits all of it, and
        # unsold output cannot occur (firms produce what is purchased).
        # This checks feasibility and budget exhaustion.
        for key, result in RESULTS.items():
            with self.subTest(configuration=key):
                self.assertTrue(result.trace[0].reality.system["allocation_feasible"])

            for consumer in consumers(result):
                realized = outcome(result, consumer)

                with self.subTest(configuration=key, consumer=consumer):
                    self.assertClose(realized["expenditure"], realized["income"])

    def test_full_employment(self):
        for country, labor in LABOR.items():
            with self.subTest(country=country):
                self.assertClose(
                    RESULTS[country].trace[0].reality.system["labor_used"][country],
                    labor
                )

    def test_symmetric_prices_and_outputs(self):
        for key, result in RESULTS.items():
            prices = {result.agent(firm).selected_action for firm in firms(result)}
            outputs = {outcome(result, firm)["output"] for firm in firms(result)}

            with self.subTest(configuration=key):
                self.assertEqual(len(prices), 1)
                self.assertEqual(len(outputs), 1)

    def test_consumer_choice_maximizes_its_valuation_within_its_budget(self):
        consumer = RESULTS["home"].agent("home_consumer")
        bundle = dict(consumer.selected_action)
        budget_set = consumer.state.perceived_feasible_set
        first, second = sorted(bundle)[:2]

        # Shift spending between two equally priced varieties: still
        # affordable, but lower utility.
        shifted = {**bundle, first: bundle[first] * 1.1, second: bundle[second] * 0.9}

        self.assertIn(shifted, budget_set)
        self.assertGreater(consumer.value_of(bundle), consumer.value_of(shifted))


class ConfigurationKIntegratedTradeTest(CloseTestCase):
    TEST_NAME = "Krugman K: Integrated Trade"

    def setUp(self):
        self.result = RESULTS["integrated"]
        self.system = self.result.trace[0].reality.system
        self.home_varieties = variety_count(HOME_LABOR, ALPHA, THETA)
        self.foreign_varieties = variety_count(FOREIGN_LABOR, ALPHA, THETA)
        self.world_varieties = self.home_varieties + self.foreign_varieties

    def test_consumers_access_all_varieties(self):
        for consumer in consumers(self.result):
            with self.subTest(consumer=consumer):
                self.assertEqual(
                    len(outcome(self.result, consumer)["consumption"]), self.world_varieties
                )

    def test_output_per_firm_unchanged_from_autarky(self):
        for firm in firms(self.result):
            with self.subTest(firm=firm):
                self.assertClose(
                    outcome(self.result, firm)["output"],
                    outcome(RESULTS["home"], "home_firm_1")["output"]
                )

    def test_realized_allocation_meets_the_equilibrium_conditions(self):
        # Realization check at the derived equal wages: each country is
        # fully employed and every firm breaks even. That only w = w*
        # clears the world goods market is shown analytically in
        # test_krugman_1980.py; balanced trade is checked below.
        for country, labor in LABOR.items():
            with self.subTest(country=country):
                self.assertClose(self.system["labor_used"][country], labor)

        for firm in firms(self.result):
            with self.subTest(firm=firm):
                self.assertClose(outcome(self.result, firm)["profit"], 0)

    def test_trade_shares(self):
        for country, foreign_varieties in (
            ("home", self.foreign_varieties),
            ("foreign", self.home_varieties),
        ):
            consumer = outcome(self.result, f"{country}_consumer")
            share = self.system["imports"][country] / (LABOR[country] * consumer["expenditure"])

            with self.subTest(country=country):
                self.assertClose(
                    share, import_share(foreign_varieties, self.world_varieties)
                )

    def test_balanced_trade_in_wage_units(self):
        self.assertClose(
            self.system["imports"]["home"],
            imports_in_wage_units(HOME_LABOR, self.foreign_varieties, self.world_varieties)
        )
        self.assertClose(
            self.system["imports"]["foreign"],
            imports_in_wage_units(FOREIGN_LABOR, self.home_varieties, self.world_varieties)
        )
        self.assertClose(
            self.system["imports"]["home"], self.system["imports"]["foreign"]
        )


class ConfigurationKWelfareTest(CloseTestCase):
    TEST_NAME = "Krugman K: Welfare"

    @staticmethod
    def realized_utility(result, consumer):
        # The consumer's own V evaluated at its realized consumption.
        agent = result.agent(consumer)
        return agent.value_of(dict(agent.outcome["consumption"]))

    def test_realized_utility_matches_the_closed_form_solution(self):
        output = output_per_firm(ALPHA, BETA, THETA)
        world_labor = HOME_LABOR + FOREIGN_LABOR

        for country, labor in LABOR.items():
            with self.subTest(configuration=f"{country} autarky"):
                self.assertClose(
                    self.realized_utility(RESULTS[country], f"{country}_consumer"),
                    utility_per_consumer(variety_count(labor, ALPHA, THETA), output, labor, THETA)
                )
            with self.subTest(configuration=f"{country} integrated"):
                self.assertClose(
                    self.realized_utility(RESULTS["integrated"], f"{country}_consumer"),
                    utility_per_consumer(
                        variety_count(world_labor, ALPHA, THETA), output, world_labor, THETA
                    )
                )

    def test_both_countries_gain_from_trade(self):
        # Utility is ordinal: only the direction of change is tested.
        for country in LABOR:
            with self.subTest(country=country):
                self.assertGreater(
                    self.realized_utility(RESULTS["integrated"], f"{country}_consumer"),
                    self.realized_utility(RESULTS[country], f"{country}_consumer"),
                )


class ConfigurationKCompetingSpecificationTest(CloseTestCase):
    TEST_NAME = "Krugman K: Equilibrium Checks Can Fail"

    def test_misperceived_elasticity_breaks_the_equilibrium_checks(self):
        # A competing configuration: firms believe demand is less elastic
        # than the beliefs the equilibrium was derived from. Nothing in R or
        # the checks forces the Krugman result, so it is not reproduced.
        scenario = krugman_scenario("Misperceived elasticity", {"home": HOME_LABOR})
        for agent in scenario.agents:
            if "_firm_" in agent.name:
                agent.model_of_reality["demand_elasticity"] = 3.0

        result = run_scenario(scenario)
        firm = result.agent("home_firm_1")

        # Firms charge more than consumers expected, so consumers cannot pay
        # for their chosen bundles: R reports the allocation infeasible.
        self.assertNotAlmostEqual(firm.selected_action, price_wage_ratio(BETA, THETA), places=3)
        self.assertFalse(result.trace[0].reality.system["allocation_feasible"])
        self.assertNotIn("profit", firm.outcome)


def violated_constraints(reality):
    return {violation["constraint"] for violation in reality.system["violations"]}


class ConfigurationKInfeasibleAllocationTest(CloseTestCase):
    TEST_NAME = "Krugman K: Infeasible Allocations Are Not Realized"

    def assert_nothing_realized(self, reality):
        self.assertFalse(reality.system["allocation_feasible"])
        self.assertNotIn("labor_used", reality.system)
        for name, realized in reality.agents.items():
            with self.subTest(agent=name):
                self.assertEqual(realized, {"allocation_feasible": False})

    def test_labor_demand_beyond_the_labor_force(self):
        # F_t has less labor than agents expect: n firms' production needs
        # 20 + 0.75 * 60 = 65 units of labor, but only 60 exist.
        scenario = HOME_AUTARKY.variant(
            parameters={"countries": {"home": {"labor": 60, "wage": WAGE}}}
        )
        reality = run_scenario(scenario).trace[0].reality

        self.assert_nothing_realized(reality)
        self.assertEqual(violated_constraints(reality), {"labor"})
        self.assertClose(reality.system["attempted"]["labor_demand"]["home"], 65)

    def test_price_above_what_consumers_can_pay_at_any_monetary_scale(self):
        # Counterfactual: one firm charging 1% more than consumers expected
        # makes them overspend by 0.1% of income. The same rescaled
        # allocation must be equally infeasible, in R and in the consumer's
        # perceived budget, at a tiny wage.
        for wage in (WAGE, 1e-8):
            result = run_scenario(krugman_scenario("Rescaled", {"home": HOME_LABOR}, wage=wage))
            price = result.agent("home_firm_1").selected_action
            consumer = result.agent("home_consumer")
            bundle = dict(consumer.selected_action)

            with self.subTest(wage=wage):
                reality = result.counterfactual(0, {"home_firm_1": price * 1.01})
                self.assert_nothing_realized(reality)
                self.assertEqual(violated_constraints(reality), {"budget"})
                self.assertNotIn(
                    {**bundle, "home_firm_1": bundle["home_firm_1"] * 1.01},
                    consumer.state.perceived_feasible_set,
                )

    def test_zero_demand_for_an_unoffered_variety_is_ignored(self):
        result = RESULTS["home"]
        bundle = dict(result.agent("home_consumer").selected_action)

        ignored = result.counterfactual(0, {"home_consumer": {**bundle, "unoffered": 0.0}})
        self.assertTrue(ignored.system["allocation_feasible"])
        self.assertEqual(ignored.system["labor_used"], result.trace[0].reality.system["labor_used"])

        rejected = result.counterfactual(0, {"home_consumer": {**bundle, "unoffered": 1e-3}})
        self.assert_nothing_realized(rejected)
        self.assertIn("unoffered_varieties", violated_constraints(rejected))

    def test_negative_purchases_are_infeasible_and_invalid_numbers_rejected(self):
        result = RESULTS["home"]
        bundle = dict(result.agent("home_consumer").selected_action)

        for variety in ("home_firm_1", "unoffered"):
            with self.subTest(variety=variety):
                reality = result.counterfactual(0, {"home_consumer": {**bundle, variety: -1.0}})
                self.assert_nothing_realized(reality)
                self.assertIn("negative_quantity", violated_constraints(reality))

        for quantity in (float("nan"), float("inf"), "1", None, True):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, "must be a finite number"):
                    result.counterfactual(0, {"home_consumer": {**bundle, "home_firm_1": quantity}})

    def test_nonpositive_prices_are_infeasible_and_invalid_prices_rejected(self):
        result = RESULTS["home"]

        for price in (0.0, -0.5):
            with self.subTest(price=price):
                reality = result.counterfactual(0, {"home_firm_1": price})
                self.assert_nothing_realized(reality)
                self.assertIn("nonpositive_price", violated_constraints(reality))

        for price in (float("nan"), float("inf"), "0.5", None, True):
            with self.subTest(price=price):
                with self.assertRaisesRegex(ValueError, "home_firm_1's price .* must be a finite number"):
                    result.counterfactual(0, {"home_firm_1": price})

    def test_purchase_of_an_unoffered_variety(self):
        # A variety the consumer expects is not offered by any acting firm.
        scenario = HOME_AUTARKY.variant(
            agents=[agent for agent in HOME_AUTARKY.agents if agent.name != "home_firm_10"]
        )
        reality = run_scenario(scenario).trace[0].reality

        self.assert_nothing_realized(reality)
        self.assertIn("unoffered_varieties", violated_constraints(reality))


class ConfigurationKPriceSearchTest(CloseTestCase):
    TEST_NAME = "Krugman K: Scale-Aware Price Search"

    def test_markup_and_equilibrium_hold_under_wage_rescaling(self):
        baseline = outcome(RESULTS["home"], "home_firm_1")

        for wage in (1e-4, 1e4, 1e8):
            result = run_scenario(krugman_scenario("Rescaled", {"home": HOME_LABOR}, wage=wage))
            firm = outcome(result, "home_firm_1")

            with self.subTest(wage=wage):
                self.assertTrue(result.trace[0].reality.system["allocation_feasible"])
                self.assertClose(
                    result.agent("home_firm_1").selected_action / wage,
                    price_wage_ratio(BETA, THETA)
                )
                self.assertClose(firm["output"], baseline["output"])
                self.assertClose(firm["profit"] / wage, 0)

    def test_peak_hidden_by_rounded_ties_is_found(self):
        # theta = 0.99: demand elasticity 100 puts the best price within 1%
        # of marginal cost, and V at twice marginal cost rounds to exactly
        # V at marginal cost. The search narrows its step instead of
        # mistaking the tie for no interior maximum.
        # Demand is computed in relative prices, so elasticity 100 does not
        # overflow or underflow when the wage is far from 1.
        for wage in (1e-8, WAGE, 1e8):
            with self.subTest(wage=wage):
                with mock.patch.object(krugman_1980_ter, "THETA", 0.99):
                    price = krugman_1980_ter.selected_firm_price({"home": HOME_LABOR}, 1, BETA * wage, wage)

                self.assertClose(price / wage, price_wage_ratio(BETA, 0.99))

    def test_consumer_demand_is_stable_at_high_elasticity_and_any_wage(self):
        # theta = 0.99 (sigma = 100): each consumer still spends its income
        # equally across equally priced varieties.
        for wage in (1e-8, WAGE, 1e8):
            with mock.patch.object(krugman_1980_ter, "THETA", 0.99):
                consumer = krugman_1980_ter.consumer_spec("c", ("a", "b"), 2 * wage, wage)

            scenario = Scenario(
                name="Consumer choice", description="", periods=1, initial_state={}, agents=[consumer]
            )
            bundle = run_scenario(scenario).agent("c").selected_action

            with self.subTest(wage=wage):
                self.assertClose(bundle["a"], 0.25)
                self.assertClose(bundle["b"], 0.25)

    def test_no_interior_maximum_is_rejected_not_returned_as_a_boundary(self):
        # With perceived elasticity <= 1, expected profit rises without
        # bound in price: there is no best price to select.
        for elasticity in (1.0, 0.8):
            firm = firm_spec("home_firm_1", HOME_LABOR, 10, 2 / 3, WAGE)
            firm.model_of_reality["demand_elasticity"] = elasticity
            scenario = HOME_AUTARKY.variant(agents=[firm] + HOME_AUTARKY.agents[1:])

            with self.subTest(elasticity=elasticity):
                with self.assertRaisesRegex(ValueError, "No interior profit-maximizing price"):
                    run_scenario(scenario)


if __name__ == "__main__":
    unittest.main()

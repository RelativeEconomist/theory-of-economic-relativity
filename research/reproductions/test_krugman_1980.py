"""Tests for the Krugman (1980), Section I analytical reproduction.

Run with:
    python3 run_tests.py research/reproductions/test_krugman_1980.py

Fixture values are illustrative test inputs, not empirical claims.
"""

import unittest

from research.reproductions.krugman_1980 import (
    home_goods_excess_demand,
    import_share,
    imports_in_wage_units,
    output_per_firm,
    price_wage_ratio,
    utility_per_consumer,
    variety_count,
)

# Illustrative fixtures only; not empirical assumptions.
HOME_LABOR = 80
FOREIGN_LABOR = 40
ALPHA = 2
BETA = 0.5
THETA = 0.75


class Krugman1980SectionITest(unittest.TestCase):
    def test_markup_pricing_satisfies_lerner_identity(self):
        price_over_wage = price_wage_ratio(BETA, THETA)

        self.assertAlmostEqual(price_over_wage, BETA / THETA)
        # Markup over marginal labor cost equals 1 - theta.
        self.assertAlmostEqual((price_over_wage - BETA) / price_over_wage, 1 - THETA)

    def test_firm_output_earns_zero_profit(self):
        price_over_wage = price_wage_ratio(BETA, THETA)
        output = output_per_firm(ALPHA, BETA, THETA)

        self.assertAlmostEqual(output, ALPHA * THETA / (BETA * (1 - THETA)))
        # Revenue equals labor cost in wage units.
        self.assertAlmostEqual(price_over_wage * output - (ALPHA + BETA * output), 0)

    def test_variety_count_clears_labor_market(self):
        output = output_per_firm(ALPHA, BETA, THETA)
        varieties = variety_count(HOME_LABOR, ALPHA, THETA)

        self.assertAlmostEqual(varieties, HOME_LABOR * (1 - THETA) / ALPHA)
        self.assertAlmostEqual(varieties * (ALPHA + BETA * output), HOME_LABOR)

    def test_trade_variety_counts_scale_with_labor(self):
        home_varieties = variety_count(HOME_LABOR, ALPHA, THETA)
        foreign_varieties = variety_count(FOREIGN_LABOR, ALPHA, THETA)

        self.assertAlmostEqual(home_varieties / foreign_varieties, HOME_LABOR / FOREIGN_LABOR)
        self.assertAlmostEqual(
            home_varieties + foreign_varieties,
            variety_count(HOME_LABOR + FOREIGN_LABOR, ALPHA, THETA),
        )

    def test_output_per_firm_unchanged_after_trade(self):
        output = output_per_firm(ALPHA, BETA, THETA)
        world_varieties = variety_count(HOME_LABOR, ALPHA, THETA) + variety_count(
            FOREIGN_LABOR, ALPHA, THETA
        )

        # Zero profit at markup pricing fixes output independently of market size.
        self.assertAlmostEqual(output, ALPHA / (price_wage_ratio(BETA, THETA) - BETA))
        # The same output and the world variety count clear world labor.
        self.assertAlmostEqual(
            world_varieties * (ALPHA + BETA * output), HOME_LABOR + FOREIGN_LABOR
        )

    def test_only_equal_wages_clear_the_world_goods_market(self):
        def excess(wage_ratio):
            return home_goods_excess_demand(wage_ratio, HOME_LABOR, FOREIGN_LABOR, ALPHA, BETA, THETA)

        self.assertAlmostEqual(excess(1.0), 0)
        # A higher home wage makes home varieties dearer: demand falls short
        # of what home firms must sell to break even, and conversely.
        self.assertLess(excess(1.1), -1e-3)
        self.assertGreater(excess(0.9), 1e-3)

    def test_trade_shares_and_balanced_trade(self):
        home_varieties = variety_count(HOME_LABOR, ALPHA, THETA)
        foreign_varieties = variety_count(FOREIGN_LABOR, ALPHA, THETA)
        world_varieties = home_varieties + foreign_varieties
        world_labor = HOME_LABOR + FOREIGN_LABOR

        self.assertAlmostEqual(
            import_share(foreign_varieties, world_varieties), FOREIGN_LABOR / world_labor
        )
        self.assertAlmostEqual(
            import_share(home_varieties, world_varieties), HOME_LABOR / world_labor
        )
        self.assertAlmostEqual(
            imports_in_wage_units(HOME_LABOR, foreign_varieties, world_varieties),
            imports_in_wage_units(FOREIGN_LABOR, home_varieties, world_varieties),
        )

    def test_both_countries_gain_from_increased_variety(self):
        output = output_per_firm(ALPHA, BETA, THETA)
        home_varieties = variety_count(HOME_LABOR, ALPHA, THETA)
        foreign_varieties = variety_count(FOREIGN_LABOR, ALPHA, THETA)
        world_varieties = home_varieties + foreign_varieties
        world_labor = HOME_LABOR + FOREIGN_LABOR

        home_autarky = utility_per_consumer(home_varieties, output, HOME_LABOR, THETA)
        foreign_autarky = utility_per_consumer(
            foreign_varieties, output, FOREIGN_LABOR, THETA
        )
        integrated_trade = utility_per_consumer(world_varieties, output, world_labor, THETA)

        # Autarky consumption per variety uses domestic population; trade uses world population.
        self.assertAlmostEqual(home_autarky, home_varieties * (output / HOME_LABOR) ** THETA)
        self.assertAlmostEqual(
            foreign_autarky, foreign_varieties * (output / FOREIGN_LABOR) ** THETA
        )
        self.assertAlmostEqual(
            integrated_trade, world_varieties * (output / world_labor) ** THETA
        )

        # Utility is ordinal: test the direction of change and analytical ratios only.
        self.assertGreater(integrated_trade, home_autarky)
        self.assertGreater(integrated_trade, foreign_autarky)
        self.assertAlmostEqual(
            integrated_trade / home_autarky, (world_labor / HOME_LABOR) ** (1 - THETA)
        )
        self.assertAlmostEqual(
            integrated_trade / foreign_autarky, (world_labor / FOREIGN_LABOR) ** (1 - THETA)
        )


if __name__ == "__main__":
    unittest.main()

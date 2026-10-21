"""Analytical reproduction of Krugman (1980), Section I.

Source: Paul Krugman, "Scale Economies, Product Differentiation, and the
Pattern of Trade," American Economic Review 70(5), 1980, Section I.

This reproduction is independent of TER and does not use the TER framework.

Section I assumptions:
- Labor is the only factor of production.
- Consumers have identical symmetric preferences U = sum c_i^theta, 0 < theta < 1.
- Producing x units of a variety takes alpha + beta * x units of labor.
- Free entry drives profits to zero.
- Product differentiation is costless.
- Variety counts are treated as continuous analytical quantities.
- Two-country trade comparison: identical tastes and technologies, zero
  transport costs. Krugman states that wages are equal by symmetry;
  home_goods_excess_demand checks that w = w* is the wage ratio at which
  the world goods market clears.

Run with:
    python3.14 -m research.reproductions.krugman_1980
"""

# Illustrative demonstration/test fixtures only; not empirical assumptions.
HOME_LABOR = 80
FOREIGN_LABOR = 40
ALPHA = 2
BETA = 0.5
THETA = 0.75


def price_wage_ratio(beta, theta):
    """Profit-maximizing markup pricing: p/w = beta / theta."""
    return beta / theta


def output_per_firm(alpha, beta, theta):
    """Zero-profit output per firm: x = alpha * theta / (beta * (1 - theta))."""
    return alpha * theta / (beta * (1 - theta))


def variety_count(labor, alpha, theta):
    """Full-employment variety count: n = L * (1 - theta) / alpha."""
    return labor * (1 - theta) / alpha


def home_goods_excess_demand(wage_ratio, home_labor, foreign_labor, alpha, beta, theta):
    """
    World spending on home varieties minus home firms' revenue, in units
    of the foreign wage, at home/foreign wage ratio w/w*.

    Markup pricing gives p/p* = w/w*; zero profit fixes output per firm
    and full employment fixes variety counts, neither depending on wages.
    Consumers spend their wage income across all varieties with CES
    shares n p^(1-sigma) / (n p^(1-sigma) + n* p*^(1-sigma)),
    sigma = 1 / (1 - theta). Setting this to zero reduces to
    (w/w*)^sigma = 1, so w = w* is the only clearing wage ratio.
    """
    sigma = 1 / (1 - theta)
    home_price = price_wage_ratio(beta, theta) * wage_ratio
    foreign_price = price_wage_ratio(beta, theta)
    home_varieties = variety_count(home_labor, alpha, theta)
    foreign_varieties = variety_count(foreign_labor, alpha, theta)

    home_weight = home_varieties * home_price ** (1 - sigma)
    foreign_weight = foreign_varieties * foreign_price ** (1 - sigma)
    world_spending = wage_ratio * home_labor + foreign_labor
    home_revenue = home_varieties * home_price * output_per_firm(alpha, beta, theta)

    return world_spending * home_weight / (home_weight + foreign_weight) - home_revenue


def import_share(foreign_varieties, total_varieties):
    """Share of spending on foreign varieties when all prices are equal."""
    return foreign_varieties / total_varieties


def imports_in_wage_units(importer_labor, foreign_varieties, total_varieties):
    """Importer income (labor in wage units) times its import share."""
    return importer_labor * foreign_varieties / total_varieties


def utility_per_consumer(varieties, output_per_variety, consumers, theta):
    """U = n * (x / consumers)^theta, with each variety's output shared evenly."""
    return varieties * (output_per_variety / consumers) ** theta


def main():
    world_labor = HOME_LABOR + FOREIGN_LABOR
    output = output_per_firm(ALPHA, BETA, THETA)
    home_varieties = variety_count(HOME_LABOR, ALPHA, THETA)
    foreign_varieties = variety_count(FOREIGN_LABOR, ALPHA, THETA)
    world_varieties = home_varieties + foreign_varieties

    home_autarky = utility_per_consumer(home_varieties, output, HOME_LABOR, THETA)
    foreign_autarky = utility_per_consumer(foreign_varieties, output, FOREIGN_LABOR, THETA)
    integrated_trade = utility_per_consumer(world_varieties, output, world_labor, THETA)

    print("Krugman (1980), Section I: analytical reproduction (independent of TER)")
    print(
        f"Illustrative fixtures, not empirical assumptions: L={HOME_LABOR}, "
        f"L*={FOREIGN_LABOR}, alpha={ALPHA}, beta={BETA}, theta={THETA}"
    )
    print()
    print("Closed economies")
    print(f"  price/wage p/w = beta/theta         {price_wage_ratio(BETA, THETA):.4f}")
    print(f"  output per firm x                   {output:.4f}")
    print(f"  home varieties n                    {home_varieties:.4f}")
    print(f"  foreign varieties n*                {foreign_varieties:.4f}")
    print(f"  home utility n(x/L)^theta           {home_autarky:.4f}")
    print(f"  foreign utility n*(x/L*)^theta      {foreign_autarky:.4f}")
    print()
    print("Integrated trade")
    print(f"  output per firm x (unchanged)       {output:.4f}")
    print(f"  world varieties n + n*              {world_varieties:.4f}")
    print(
        "  home import share n*/(n+n*)         "
        f"{import_share(foreign_varieties, world_varieties):.4f}"
    )
    print(
        "  foreign import share n/(n+n*)       "
        f"{import_share(home_varieties, world_varieties):.4f}"
    )
    print(
        "  home imports (wage units)           "
        f"{imports_in_wage_units(HOME_LABOR, foreign_varieties, world_varieties):.4f}"
    )
    print(
        "  foreign imports (wage units)        "
        f"{imports_in_wage_units(FOREIGN_LABOR, home_varieties, world_varieties):.4f}"
    )
    print(f"  utility (n+n*)(x/(L+L*))^theta      {integrated_trade:.4f}")
    print()
    print("Welfare (utility is ordinal; ratios show direction of gain)")
    print(f"  home trade/autarky utility ratio    {integrated_trade / home_autarky:.4f}")
    print(f"  foreign trade/autarky utility ratio {integrated_trade / foreign_autarky:.4f}")


if __name__ == "__main__":
    main()

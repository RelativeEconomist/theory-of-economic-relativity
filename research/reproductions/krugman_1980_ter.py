"""Configuration K: Krugman (1980), Section I, executed through TER Core.

Source assumptions, mappings, and hypotheses: krugman_1980_configuration.md.
Validation order and anti-circularity rules: krugman_1980_validation.md.
External benchmark (Krugman's closed-form solution, without TER):
krugman_1980.py. Only its illustrative fixtures (L, L*, alpha, beta,
theta) are shared; none of its solution functions is used here.

The file has two clearly separated layers.

1. Equilibrium derivation (researcher-level, not an agent).
   Krugman's equilibrium is static: every agent takes the equilibrium
   market conditions as given. coordinate_equilibrium obtains the markup
   from a genuine TER firm decision (V -> D -> C), then derives output per
   firm and firm count from Krugman's zero-profit and full-employment
   conditions. Wages are equal (the only wage ratio that clears the world
   goods market; see the configuration document). These values enter only
   as beliefs in each agent's M and as F_t; no agent sees another agent's
   selected action from the decision point.

2. Agent decisions and realization (TER).
   Each firm selects a price by maximizing its own V (expected profit)
   over its F_hat (any positive price). Each consumer selects a bundle
   from its F_hat (its perceived budget set) by CES demand. All agents act
   at one decision point, and one joint R realizes the allocation, or
   reports it infeasible.

Whether the realized outcomes match the derived equilibrium, and how they
compare with the benchmark, is checked afterward (test_krugman_1980_ter.py).
Nothing in V, D, or R encodes an expected output.

Run with:
    python3 run_tests.py research/reproductions/test_krugman_1980_ter.py
"""

import math
from numbers import Real

from research.reproductions.krugman_1980 import (
    ALPHA,
    BETA,
    FOREIGN_LABOR,
    HOME_LABOR,
    THETA,
)
from research.ter import AgentSpec, RealityResult, Scenario, run_scenario
from research.ter.feasible import Interval, Region

WAGE = 1.0  # Krugman's numeraire: prices are measured in wage units.

# Membership slack for the budget line only, as a share of income: CES
# demand spends exactly the income, which floating point can overshoot by
# rounding.
BUDGET_TOLERANCE = 1e-9

# The firm's numerical search (part of its D): relative precision of the
# final price bracket, and how many steps it may take to bracket the best
# price before rejecting the problem as having no interior maximum.
PRICE_SEARCH_TOLERANCE = 1e-12
PRICE_BRACKET_STEPS = 200

# While bracketing, two values of V closer than this (relative to the
# larger value or the firm's perceived fixed cost) count as a tie: the
# difference is floating-point rounding, not a slope the search can follow.
VALUE_TIE_TOLERANCE = 1e-12

# R's slack when checking an allocation against F_t, relative to each
# limit (no absolute floor, so results do not depend on the monetary
# unit). The firm's search resolves price to about 5e-9 (relative), which
# moves spending by the same order; 1e-7 absorbs that and nothing
# economically meaningful.
REALIZATION_TOLERANCE = 1e-7

# Relative slack for quantities derived from the TER-selected markup: the
# whole-number firm count and the fixed-point check. The markup's ~5e-9
# resolution moves derived firm counts by ~1e-8.
DERIVATION_TOLERANCE = 1e-6


# ---------------------------------------------------------------------------
# Layer 1: equilibrium derivation (not an agent decision)
# ---------------------------------------------------------------------------


def selected_firm_price(labor_by_country, firm_total, expected_price, wage):
    """
    The price a configured firm selects through TER (V -> D -> C), given
    market beliefs. Runs the firm alone for one decision point; no reality
    rule is needed because only its selected action is read.
    """
    firm = firm_spec("firm", sum(labor_by_country.values()), firm_total, expected_price, wage)
    scenario = Scenario(
        name="Firm pricing decision",
        description="One firm's price, selected from its own M, V, D.",
        periods=1,
        initial_state={},
        agents=[firm],
    )

    return run_scenario(scenario).agent("firm").selected_action


def coordinate_equilibrium(labor_by_country, wage=WAGE):
    """
    Krugman's static equilibrium, derived from the TER firm decision:

        markup m     the price a TER firm selects, over the wage
        output x     zero profit (free entry):  m*w*x = w*(alpha + beta*x)
                     so x = alpha / (m - beta)
        firm count   full employment:  n * (alpha + beta*x) = L
        wages        equal in every country: w = w* is the only wage ratio
                     that clears the world goods market (configuration
                     document); the common wage is the numeraire
        expected     m * w, the price every agent expects each variety
        price        to carry

    The markup is first obtained with provisional market beliefs (all
    spending on a single variety at marginal cost), because the firm's D
    does not depend on the market level under the large-number
    approximation. It is then confirmed as a fixed point: a firm holding
    the derived beliefs must select the same price. If it does not, this
    raises rather than iterating, since that would require an adjustment
    process Krugman does not specify.

    Firm counts must be whole numbers to instantiate firm agents; Krugman
    treats n as continuous, so other fixtures may not be representable.
    """
    provisional_price = selected_firm_price(labor_by_country, 1, BETA * wage, wage)
    markup = provisional_price / wage

    if markup <= BETA:
        raise ValueError(
            f"Selected markup {markup} does not exceed marginal labor cost "
            f"{BETA}: no zero-profit output exists."
        )

    output = ALPHA / (markup - BETA)
    firm_count = {}

    for country, labor in labor_by_country.items():
        count = labor / (ALPHA + BETA * output)

        if not math.isclose(count, round(count), rel_tol=DERIVATION_TOLERANCE):
            raise ValueError(
                f"Derived firm count for {country} is {count}, not a whole "
                "number of firm agents."
            )

        firm_count[country] = round(count)

    expected_price = markup * wage
    confirmed_price = selected_firm_price(
        labor_by_country, sum(firm_count.values()), expected_price, wage
    )

    if not math.isclose(confirmed_price, expected_price, rel_tol=DERIVATION_TOLERANCE):
        raise ValueError(
            f"Firm price {confirmed_price} under the derived beliefs differs "
            f"from the expected price {expected_price}: not a fixed point."
        )

    return {
        "markup": markup,
        "output_per_firm": output,
        "firm_count": firm_count,
        "expected_price": expected_price,
        "wage": wage,
    }


# ---------------------------------------------------------------------------
# Layer 2a: firm V and D
# ---------------------------------------------------------------------------


def expected_profit_value(price, view):
    """
    V for a firm: expected profit at a price, under the firm's model of
    demand and costs (M).

    Large-number approximation (Krugman): the firm perceives constant
    demand elasticity and treats market spending and the price index as
    given. With n varieties expected at price p_bar, its perceived CES
    demand E * p^(-elasticity) / (n * p_bar^(1 - elasticity)) is computed
    in relative prices, which is the same quantity without raising money
    prices to large powers (that overflows at high elasticity when wages
    are far from 1):

        x(p) = market_expenditure / (n * p_bar) * (p / p_bar)^(-elasticity)
    """
    model = view.model_of_reality
    expected_price = model["expected_price"]
    quantity = (
        model["market_expenditure"]
        / (model["expected_varieties"] * expected_price)
        * (price / expected_price) ** (-model["demand_elasticity"])
    )
    marginal_cost = model["marginal_labor"] * model["wage"]
    fixed_cost = model["fixed_labor"] * model["wage"]

    return (price - marginal_cost) * quantity - fixed_cost


def profit_maximizing_price(view):
    """
    D for a firm: numerical search for the price in F_hat with the highest
    V, scaled to the firm's own perceived marginal cost (M).

    1. Bracket: starting at perceived marginal cost with neighbors a
       factor of 2 away, move toward a neighbor with strictly higher V
       until the price has strictly higher V than both neighbors. When V
       ties with a neighbor (within VALUE_TIE_TOLERANCE: rounding can make
       V look flat over a coarse step, e.g. a peak just above marginal
       cost with very elastic demand), narrow the step instead of moving.
       If no strict peak appears within PRICE_BRACKET_STEPS steps (e.g.
       perceived demand elasticity <= 1, where V keeps rising with price
       or levels off), raise: there is no interior best price to return.
    2. Golden-section search inside that bracket, which assumes V has a
       single peak there (true for constant-elasticity profit).

    The result is always strictly inside the bracket, never a search
    boundary.
    """
    model = view.model_of_reality
    start = model["marginal_labor"] * model["wage"]
    tolerance = view.decision_parameters["search_tolerance"]

    if not (start > 0 and math.isfinite(start)):
        raise ValueError("Perceived marginal cost must be positive and finite to scale the price search.")

    value_scale = model["fixed_labor"] * model["wage"]

    def above(value, reference):
        tie = VALUE_TIE_TOLERANCE * max(abs(value), abs(reference), value_scale)
        return value - reference > tie

    middle, factor = start, 2.0

    for _ in range(PRICE_BRACKET_STEPS):
        low, high = middle / factor, middle * factor
        low_value, middle_value, high_value = view.value(low), view.value(middle), view.value(high)

        if above(low_value, middle_value):
            middle = low
        elif above(high_value, middle_value):
            middle = high
        elif above(middle_value, low_value) and above(middle_value, high_value):
            break
        else:
            factor = math.sqrt(factor)
    else:
        raise ValueError(
            "No interior profit-maximizing price: V showed no strict peak within "
            f"{PRICE_BRACKET_STEPS} steps from perceived marginal cost "
            f"(last price tried {middle}, step factor {factor})."
        )

    inverse_golden = (math.sqrt(5) - 1) / 2
    left = high - inverse_golden * (high - low)
    right = low + inverse_golden * (high - low)
    left_value = view.value(left)
    right_value = view.value(right)

    while high - low > tolerance * low:
        if left_value < right_value:
            low, left, left_value = left, right, right_value
            right = low + inverse_golden * (high - low)
            right_value = view.value(right)
        else:
            high, right, right_value = right, left, left_value
            left = high - inverse_golden * (high - low)
            left_value = view.value(left)

    return (low + high) / 2


# ---------------------------------------------------------------------------
# Layer 2b: consumer V, F_hat, and D
# ---------------------------------------------------------------------------


def ces_utility_value(bundle, view):
    """V for a consumer: Krugman's utility U = sum c_i^theta."""
    theta = view.valuation["theta"]

    return math.fsum(quantity ** theta for quantity in bundle.values())


def perceived_budget(model_of_reality):
    """
    F_hat for a consumer: the bundles of perceived varieties affordable at
    the prices and income it expects. Built only from M, so prices have
    one source. The budget line is stated in shares of income,
    sum (p_i / income) * c_i <= 1, the same set as sum p_i * c_i <= income,
    so its rounding slack is a share of income at any monetary scale.
    """
    prices = model_of_reality["expected_prices"]
    income = model_of_reality["income"]

    return Region(
        coordinates=tuple(prices),
        lower={variety: 0.0 for variety in prices},
        constraints=(({variety: price / income for variety, price in prices.items()}, 1.0),),
        tolerance=BUDGET_TOLERANCE,
    )


def ces_demand(view):
    """
    D for a consumer: the closed-form maximizer of its V over its budget
    set (CES demand), from its expected prices and income (M) and its
    preference parameter (V's data):

        c_i = income * p_i^(-sigma) / sum_j p_j^(1 - sigma),
        sigma = 1 / (1 - theta)

    computed in prices relative to the lowest expected price r_i = p_i / p_min,
    the same quantity without raising money prices to large powers:

        c_i = (income / p_min) * r_i^(-sigma) / sum_j r_j^(1 - sigma)
    """
    sigma = 1 / (1 - view.valuation["theta"])
    prices = view.model_of_reality["expected_prices"]
    income = view.model_of_reality["income"]
    reference = min(prices.values())
    denominator = math.fsum((price / reference) ** (1 - sigma) for price in prices.values())

    return {
        variety: income / reference * (price / reference) ** (-sigma) / denominator
        for variety, price in prices.items()
    }


# ---------------------------------------------------------------------------
# Joint R
# ---------------------------------------------------------------------------


def _exceeds(amount, limit):
    return amount > limit + REALIZATION_TOLERANCE * abs(limit)


def _require_finite_number(value, description):
    """
    A price or quantity that is not a finite number is not an action R can
    assess against F_t at all, so it is an input error, not an infeasible
    choice.
    """
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{description} is {value!r}: it must be a finite number.")


def krugman_reality(actions, objective_state, parameters):
    """
    One joint R for every firm price and consumer bundle selected at the
    decision point, against F_t: technology (alpha, beta), each country's
    labor force and wage, and where each firm produces.

    Each consumer stands for its country's identical consumers (one per
    unit of labor), so its per-capita bundle is purchased by that whole
    population. Firms produce what is purchased at their selected price.

    Every price and purchase quantity must be a finite number (otherwise R
    raises). The selected allocation is realized only if F_t permits all
    of it: every price is positive (Krugman's market is defined only at
    positive prices), no quantity is negative, every purchased variety is
    offered, every consumer can pay for its bundle at the selected prices
    from its actual wage, and each country's firms need no more labor
    than its labor force. Otherwise R reports the
    allocation infeasible: which constraints failed and the attempted
    quantities, and no realized consumption, output, or profit. Krugman
    specifies no rationing or adjustment rule, so R does not invent one,
    and it never rewrites a selected action.
    """
    alpha = parameters["alpha"]
    beta = parameters["beta"]
    countries = parameters["countries"]
    firm_country = parameters["firm_country"]
    consumer_country = parameters["consumer_country"]

    prices = {name: action for name, action in actions.items() if name in firm_country}
    bundles = {name: action for name, action in actions.items() if name in consumer_country}

    violations = []
    sales = {firm: 0.0 for firm in prices}
    expenditure = {}

    for firm, price in prices.items():
        _require_finite_number(price, f"{firm}'s price")

        if price <= 0:
            violations.append({"constraint": "nonpositive_price", "agent": firm, "price": price})

    for consumer, bundle in bundles.items():
        country = consumer_country[consumer]
        population = countries[country]["labor"]

        for variety, quantity in bundle.items():
            _require_finite_number(quantity, f"{consumer}'s quantity of {variety}")

        negative = sorted(variety for variety, quantity in bundle.items() if quantity < 0)

        if negative:
            violations.append({"constraint": "negative_quantity", "agent": consumer, "varieties": negative})

        unoffered = sorted(variety for variety, quantity in bundle.items() if variety not in prices and quantity > 0)

        if unoffered:
            violations.append({"constraint": "unoffered_varieties", "agent": consumer, "varieties": unoffered})

        expenditure[consumer] = math.fsum(
            prices[variety] * quantity for variety, quantity in bundle.items() if variety in prices
        )
        income = countries[country]["wage"]

        if _exceeds(expenditure[consumer], income):
            violations.append(
                {"constraint": "budget", "agent": consumer, "required": expenditure[consumer], "available": income}
            )

        for variety, quantity in bundle.items():
            if variety in prices:
                sales[variety] += population * quantity

    labor_demand = {country: 0.0 for country in countries}

    for firm in prices:
        labor_demand[firm_country[firm]] += alpha + beta * sales[firm]

    for country, demanded in labor_demand.items():
        if _exceeds(demanded, countries[country]["labor"]):
            violations.append(
                {"constraint": "labor", "country": country, "required": demanded, "available": countries[country]["labor"]}
            )

    if violations:
        return RealityResult(
            system={
                "allocation_feasible": False,
                "violations": violations,
                "attempted": {"sales": sales, "expenditure": expenditure, "labor_demand": labor_demand},
            },
            agents={name: {"allocation_feasible": False} for name in actions},
        )

    return _realized_allocation(prices, bundles, sales, expenditure, labor_demand, parameters)


def _realized_allocation(prices, bundles, sales, expenditure, labor_used, parameters):
    """The outcomes of an allocation F_t permits in full."""
    alpha = parameters["alpha"]
    beta = parameters["beta"]
    countries = parameters["countries"]
    firm_country = parameters["firm_country"]
    consumer_country = parameters["consumer_country"]

    imports = {country: 0.0 for country in countries}
    exports = {country: 0.0 for country in countries}
    agents = {}

    for consumer, bundle in bundles.items():
        country = consumer_country[consumer]
        population = countries[country]["labor"]

        for variety, quantity in bundle.items():
            if variety not in prices:
                continue  # zero demand for an unoffered variety: nothing traded

            producer_country = firm_country[variety]

            if producer_country != country:
                value = population * prices[variety] * quantity
                imports[country] += value
                exports[producer_country] += value

        agents[consumer] = {
            "allocation_feasible": True,
            "consumption": dict(bundle),
            "expenditure": expenditure[consumer],
            "income": countries[country]["wage"],
        }

    for firm, price in prices.items():
        wage = countries[firm_country[firm]]["wage"]
        output = sales[firm]
        labor = alpha + beta * output
        revenue = price * output
        cost = wage * labor

        agents[firm] = {
            "allocation_feasible": True,
            "price": price,
            "output": output,
            "labor_used": labor,
            "revenue": revenue,
            "cost": cost,
            "profit": revenue - cost,
        }

    return RealityResult(
        system={
            "allocation_feasible": True,
            "varieties": len(prices),
            "labor_used": labor_used,
            "imports": imports,
            "exports": exports,
        },
        agents=agents,
    )


# ---------------------------------------------------------------------------
# Configurations
# ---------------------------------------------------------------------------


def firm_spec(name, market_labor, firm_total, expected_price, wage):
    """
    An active firm. Its M holds the market conditions it takes as given
    (supplied), its demand elasticity belief, and its cost beliefs; its
    F_hat is every positive price.
    """
    elasticity = 1 / (1 - THETA)

    return AgentSpec(
        name=name,
        objective="maximize profit",
        model_of_reality={
            "wage": wage,
            "fixed_labor": ALPHA,
            "marginal_labor": BETA,
            "demand_elasticity": elasticity,
            "market_expenditure": wage * market_labor,
            "expected_varieties": firm_total,
            "expected_price": expected_price,
        },
        perceived_feasible_set=Interval(0, math.inf, closed_low=False),
        valuation_rule=expected_profit_value,
        decision_process=profit_maximizing_price,
        decision_parameters={"search_tolerance": PRICE_SEARCH_TOLERANCE},
        horizon="current static profit decision",
    )


def consumer_spec(name, varieties, expected_price, wage):
    """
    A country's representative consumer. Its M holds the prices it
    expects for the varieties it can buy and its wage income; its F_hat is
    the budget set those beliefs imply.
    """
    model_of_reality = {
        "income": wage,
        "expected_prices": {variety: expected_price for variety in varieties},
    }

    return AgentSpec(
        name=name,
        objective="maximize utility from consumption",
        model_of_reality=model_of_reality,
        perceived_feasible_set=perceived_budget(model_of_reality),
        valuation_rule=ces_utility_value,
        decision_process=ces_demand,
        valuation={"theta": THETA},
        horizon="current static consumption decision",
    )


def krugman_scenario(name, labor_by_country, wage=WAGE):
    """
    One Krugman economy over the given countries: a single country is
    autarky; several countries are one integrated market with zero
    transport costs, identical tastes and technologies.
    """
    equilibrium = coordinate_equilibrium(labor_by_country, wage=wage)
    expected_price = equilibrium["expected_price"]
    wage = equilibrium["wage"]

    firm_country = {
        f"{country}_firm_{index}": country
        for country, count in equilibrium["firm_count"].items()
        for index in range(1, count + 1)
    }
    consumer_country = {f"{country}_consumer": country for country in labor_by_country}
    market_labor = sum(labor_by_country.values())

    firms = [
        firm_spec(firm, market_labor, len(firm_country), expected_price, wage)
        for firm in firm_country
    ]
    consumers = [
        consumer_spec(consumer, tuple(firm_country), expected_price, wage)
        for consumer in consumer_country
    ]

    return Scenario(
        name=name,
        description="Krugman (1980) Section I, Configuration K.",
        periods=1,
        initial_state={},
        agents=firms + consumers,
        parameters={
            "alpha": ALPHA,
            "beta": BETA,
            "countries": {
                country: {"labor": labor, "wage": wage}
                for country, labor in labor_by_country.items()
            },
            "firm_country": firm_country,
            "consumer_country": consumer_country,
        },
        reality=krugman_reality,
    )


HOME_AUTARKY = krugman_scenario("Home autarky", {"home": HOME_LABOR})
FOREIGN_AUTARKY = krugman_scenario("Foreign autarky", {"foreign": FOREIGN_LABOR})
INTEGRATED_TRADE = krugman_scenario(
    "Integrated trade", {"home": HOME_LABOR, "foreign": FOREIGN_LABOR}
)

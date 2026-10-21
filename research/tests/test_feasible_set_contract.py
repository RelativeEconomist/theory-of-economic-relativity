"""
Framework test: mathematical perceived feasible set contract

Canonical TER: theory/academic.md, Models 5.1-5.3 (C in F̂)

Purpose
-------
Verifies that F̂ may be a mathematical set (research.ter.feasible.Interval
or Region) instead of a list, and that:

- C in F̂ is still enforced by select_action, by membership;
- open boundaries never admit an excluded action, even with a tolerance;
- tolerance only relaxes closed boundaries, by a stated amount;
- discrete decision rules refuse a set they cannot enumerate;
- continuous actions run unchanged through one joint R, observation,
  update, trace, and counterfactuals.

Fixture rules here (pricing, revenue) are test mechanics, not economic
claims.
"""

import math
import unittest

from research.ter import AgentSpec, RealityResult, Scenario, run_scenario
from research.ter.agent import AgentState
from research.ter.decision import select_action
from research.ter.feasible import Interval, Region
from research.ter.immutable import FrozenDict
from research.ter.rules import (
    first_feasible,
    limited_search,
    maximize_value,
    observe_own_outcome,
    satisfice,
)


def make_agent(perceived_feasible_set, decision_process, decision_parameters=None):
    return AgentState(
        objective="test objective",
        model_of_reality={},
        perceived_feasible_set=perceived_feasible_set,
        value=lambda action, view: 0.0,
        horizon=None,
        decision_process=decision_process,
        name="agent",
        valuation={},
        decision_parameters=decision_parameters or {},
    )


def select(perceived_feasible_set, action):
    return select_action(
        make_agent(perceived_feasible_set, lambda view: action)
    )


# Two varieties at prices 0.1 and 0.2 with income 0.3. Buying one of each
# spends exactly the income, but 0.1 + 0.2 rounds to 0.30000000000000004.
PRICES = {"a": 0.1, "b": 0.2}
INCOME = 0.3
EXACT_SPEND = {"a": 1.0, "b": 1.0}


def budget(tolerance=0.0):
    return Region(
        coordinates=("a", "b"),
        lower={"a": 0, "b": 0},
        constraints=((PRICES, INCOME),),
        tolerance=tolerance,
    )


class TestIntervalMembership(unittest.TestCase):
    TEST_NAME = "Framework: Interval Membership"

    def test_closed_bounds_admit_their_endpoints(self):
        interval = Interval(0, 1)

        self.assertIn(0, interval)
        self.assertIn(1.0, interval)
        self.assertIn(0.5, interval)
        self.assertNotIn(-1e-12, interval)
        self.assertNotIn(1 + 1e-12, interval)

    def test_open_bounds_never_admit_the_endpoint_even_with_tolerance(self):
        interval = Interval(0, 1, closed_low=False, closed_high=False, tolerance=1e-3)

        self.assertNotIn(0, interval)
        self.assertNotIn(-1e-4, interval)
        self.assertNotIn(1, interval)
        self.assertNotIn(1 + 1e-4, interval)
        self.assertIn(math.nextafter(0, 1), interval)
        self.assertIn(math.nextafter(1, 0), interval)

    def test_tolerance_relaxes_closed_bounds_by_the_stated_amount_only(self):
        interval = Interval(0, 100, tolerance=1e-9)

        # Slack is tolerance * max(1, |bound|): 1e-9 at 0, 1e-7 at 100.
        self.assertIn(-0.5e-9, interval)
        self.assertNotIn(-2e-9, interval)
        self.assertIn(100 + 0.5e-7, interval)
        self.assertNotIn(100 + 2e-7, interval)

    def test_unbounded_interval_admits_finite_reals_only(self):
        positive = Interval(0, math.inf, closed_low=False)

        self.assertIn(1e300, positive)
        self.assertNotIn(math.inf, positive)
        self.assertNotIn(0, positive)
        self.assertIn(5, Interval(-math.inf, math.inf))

    def test_non_numbers_are_never_members(self):
        interval = Interval(0, 1)

        for action in (math.nan, True, False, "0.5", None, [0.5]):
            with self.subTest(action=action):
                self.assertNotIn(action, interval)

    def test_invalid_intervals_are_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            Interval(1, 0)
        with self.assertRaises(ValueError):
            Interval(math.nan, 1)
        with self.assertRaises(ValueError):
            Interval(1, 1, closed_low=False)
        with self.assertRaises(ValueError):
            Interval(0, 1, tolerance=-1e-9)

        self.assertIn(1, Interval(1, 1))


class TestRegionMembership(unittest.TestCase):
    TEST_NAME = "Framework: Region Membership"

    def test_budget_region_admits_affordable_bundles(self):
        region = budget()

        self.assertIn({"a": 0.0, "b": 0.0}, region)
        self.assertIn({"a": 1.0, "b": 0.5}, region)
        self.assertIn({"a": 2.0, "b": 0.0}, region)
        self.assertIn(FrozenDict({"a": 1.0, "b": 0.5}), region)

    def test_exact_tolerance_rejects_rounding_past_the_budget_line(self):
        self.assertGreater(math.fsum(PRICES[k] * EXACT_SPEND[k] for k in PRICES), INCOME)
        self.assertNotIn(EXACT_SPEND, budget())

    def test_declared_tolerance_admits_rounding_but_not_overspending(self):
        region = budget(tolerance=1e-9)

        self.assertIn(EXACT_SPEND, region)
        self.assertNotIn({"a": 1.0, "b": 1.0 + 1e-6}, region)

    def test_bounds_coordinates_and_values_are_enforced(self):
        region = budget(tolerance=1e-9)

        self.assertNotIn({"a": -0.1, "b": 0.0}, region)
        self.assertNotIn({"a": 1.0}, region)
        self.assertNotIn({"a": 1.0, "b": 0.0, "c": 0.0}, region)
        self.assertNotIn({"a": 1.0, "b": math.nan}, region)
        self.assertNotIn({"a": 1.0, "b": True}, region)
        self.assertNotIn({"a": "1", "b": 0.0}, region)
        self.assertNotIn((1.0, 0.0), region)

    def test_upper_bounds_and_unbounded_coordinates(self):
        region = Region(coordinates=("x", "y"), upper={"x": 2})

        self.assertIn({"x": 2, "y": -1e9}, region)
        self.assertNotIn({"x": 2.5, "y": 0}, region)

    def test_invalid_regions_are_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            Region(coordinates=())
        with self.assertRaises(ValueError):
            Region(coordinates=("a", "a"))
        with self.assertRaises(ValueError):
            Region(coordinates=("a",), lower={"b": 0})
        with self.assertRaises(ValueError):
            Region(coordinates=("a",), lower={"a": 2}, upper={"a": 1})
        with self.assertRaises(ValueError):
            Region(coordinates=("a",), constraints=(({"b": 1}, 1),))
        with self.assertRaises(ValueError):
            Region(coordinates=("a",), constraints=(({"a": 1}, math.inf),))

    def test_region_is_immutable(self):
        source = {"a": 0}
        region = Region(coordinates=("a",), lower=source)
        source["a"] = 5

        self.assertEqual(region.lower, {"a": 0})
        with self.assertRaises(TypeError):
            region.lower["a"] = 1
        with self.assertRaises(AttributeError):
            region.tolerance = 1.0


class TestSelectedActionMembership(unittest.TestCase):
    TEST_NAME = "Framework: C in Mathematical F̂"

    def test_member_of_an_interval_is_selected(self):
        self.assertEqual(select(Interval(0, 1), 0.25), 0.25)

    def test_action_outside_an_interval_is_rejected(self):
        positive = Interval(0, math.inf, closed_low=False, tolerance=1e-6)

        for action in (0, -1.0, math.inf, math.nan):
            with self.subTest(action=action):
                with self.assertRaisesRegex(ValueError, "outside the perceived feasible set"):
                    select(positive, action)

    def test_bundle_outside_a_region_is_rejected(self):
        self.assertEqual(select(budget(), {"a": 1.0, "b": 0.5}), {"a": 1.0, "b": 0.5})

        with self.assertRaisesRegex(ValueError, "outside the perceived feasible set"):
            select(budget(), {"a": 2.0, "b": 1.0})

    def test_empty_list_is_still_rejected_before_deciding(self):
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            select([], "anything")

    def test_discrete_rules_refuse_a_set_they_cannot_enumerate(self):
        rules = (
            (maximize_value, {}),
            (satisfice, {"satisficing_threshold": 0}),
            (limited_search, {"search_limit": 1}),
            (first_feasible, {}),
        )

        for perceived_feasible_set in (Interval(0, 1), budget()):
            for rule, parameters in rules:
                with self.subTest(rule=rule.__name__, set=type(perceived_feasible_set).__name__):
                    agent = make_agent(perceived_feasible_set, rule, parameters)

                    with self.assertRaisesRegex(TypeError, "cannot be enumerated"):
                        select_action(agent)


# ---------------------------------------------------------------------------
# A continuous scenario through the full runner
# ---------------------------------------------------------------------------


def price_from_belief(view):
    # D reads M only; the selected price is checked against F̂ by the runner.
    return view.model_of_reality["intended_price"]


def joint_revenue_reality(actions, objective_state, parameters):
    # One joint R: each seller's quantity depends on both prices.
    total = sum(actions.values())
    market_size = objective_state["market_size"]

    return RealityResult(
        system={"average_price": total / len(actions)},
        agents={
            name: {"revenue": price * market_size * (1 - price / total)}
            for name, price in actions.items()
        },
    )


def lower_price_ceiling(agent, observation):
    # The agent learns it can no longer attempt prices above 1.5.
    return {"perceived_feasible_set": Interval(0, 1.5, closed_low=False)}


def seller(name, intended_price, update_rule=None):
    return AgentSpec(
        name=name,
        objective="revenue",
        model_of_reality={"intended_price": intended_price},
        perceived_feasible_set=Interval(0, 2, closed_low=False),
        valuation_rule=lambda action, view: 0.0,
        decision_process=price_from_belief,
        update_rule=update_rule,
    )


CONTINUOUS_SCENARIO = Scenario(
    name="Continuous prices",
    description="Two sellers choose prices from an interval; one joint R.",
    periods=1,
    initial_state={"market_size": 10.0},
    agents=[seller("north", 1.25), seller("south", 0.75)],
    reality=joint_revenue_reality,
)


class TestContinuousScenario(unittest.TestCase):
    TEST_NAME = "Framework: Continuous Actions Through the Runner"

    def test_continuous_actions_reach_one_joint_reality(self):
        result = run_scenario(CONTINUOUS_SCENARIO)
        step = result.trace[0]

        self.assertEqual(dict(step.actions), {"north": 1.25, "south": 0.75})
        self.assertAlmostEqual(step.reality.system["average_price"], 1.0)
        self.assertAlmostEqual(result.agent("north").outcome["revenue"], 1.25 * 10 * 0.375)

    def test_trace_records_the_mathematical_set(self):
        result = run_scenario(CONTINUOUS_SCENARIO)

        self.assertEqual(
            result.trace.initial_agents["north"].perceived_feasible_set,
            Interval(0, 2, closed_low=False),
        )

    def test_counterfactual_accepts_a_continuous_alternative(self):
        result = run_scenario(CONTINUOUS_SCENARIO)
        alternative = result.agent("north").outcome_for(1.5)

        self.assertAlmostEqual(alternative.outcome["revenue"], 1.5 * 10 * (1 - 1.5 / 2.25))

    def test_selection_outside_the_interval_stops_the_run(self):
        scenario = CONTINUOUS_SCENARIO.variant(
            agents=[seller("north", 2.5), seller("south", 0.75)]
        )

        with self.assertRaisesRegex(ValueError, "outside the perceived feasible set"):
            run_scenario(scenario)

    def test_update_rule_can_replace_a_mathematical_set(self):
        scenario = CONTINUOUS_SCENARIO.variant(
            periods=2,
            agents=[
                seller("north", 1.75, update_rule=lower_price_ceiling),
                seller("south", 0.75),
            ],
            observation=observe_own_outcome,
        )

        # North's unchanged intended price (1.75) is in F̂ at t=0 but not
        # after its update narrows F̂ to (0, 1.5].
        with self.assertRaisesRegex(ValueError, "outside the perceived feasible set"):
            run_scenario(scenario)

        scenario = scenario.variant(periods=1)
        result = run_scenario(scenario)

        self.assertEqual(
            result.agent_states["north"].perceived_feasible_set,
            Interval(0, 1.5, closed_low=False),
        )


if __name__ == "__main__":
    unittest.main()

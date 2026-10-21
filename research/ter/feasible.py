"""
Mathematical perceived feasible sets.

TER does not require F_hat to be finite. A perceived feasible set may be
a plain list of actions, or one of the immutable sets defined here, which
describe the actions an agent perceives as available to attempt by a
membership rule instead of by enumeration:

    Interval   a scalar action: a price, quantity, or amount
    Region     an action with named coordinates (e.g. a consumption
               bundle), bounded per coordinate and by linear constraints

These are representations of F_hat, not new TER primitives. They hold no
F_t: whether reality permits a selected action is still R's concern.

The only contract D relies on is `action in perceived_feasible_set`, which
select_action uses to enforce C in F_hat. A mathematical set cannot be
enumerated, so decision rules that list F_hat (e.g. maximize_value) apply
only to list sets.

Tolerance
---------
Each set takes an explicit `tolerance` (default 0.0: exact). It only
relaxes closed boundaries, by `tolerance * max(1, |bound|)`, so an action
computed in floating point that lands on a closed bound (e.g. spending
exactly a budget) is not rejected by rounding error. Open boundaries are
always strict: an action at or beyond an open bound is never admitted.
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Real
from typing import Any

from research.ter.immutable import freeze


def _is_real(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _is_finite_real(value: Any) -> bool:
    return _is_real(value) and math.isfinite(value)


def _slack(tolerance: float, bound: float) -> float:
    # An infinite bound needs no slack (and inf * 0 would be NaN).
    if math.isinf(bound):
        return 0.0

    return tolerance * max(1.0, abs(bound))


def _check_tolerance(tolerance: Any) -> None:
    if not _is_finite_real(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be a finite, non-negative number.")


@dataclass(frozen=True)
class Interval:
    """
    The scalar actions between low and high.

    Bounds may be infinite (e.g. any positive price:
    Interval(0, math.inf, closed_low=False)). Members are always finite
    real numbers; bools, NaN, and non-numbers are never members.
    """

    low: float
    high: float
    closed_low: bool = True
    closed_high: bool = True
    tolerance: float = 0.0

    def __post_init__(self):
        for bound in (self.low, self.high):
            if not _is_real(bound) or math.isnan(bound):
                raise ValueError("Interval bounds must be real numbers.")

        _check_tolerance(self.tolerance)

        if self.low > self.high:
            raise ValueError(
                f"Interval low ({self.low}) exceeds high ({self.high})."
            )

        if self.low == self.high and not (self.closed_low and self.closed_high):
            raise ValueError(
                "An Interval with low == high must be closed at both ends; "
                "otherwise it is empty."
            )

    def __contains__(self, action: Any) -> bool:
        if not _is_finite_real(action):
            return False

        if self.closed_low:
            above_low = action >= self.low - _slack(self.tolerance, self.low)
        else:
            above_low = action > self.low

        if self.closed_high:
            below_high = action <= self.high + _slack(self.tolerance, self.high)
        else:
            below_high = action < self.high

        return above_low and below_high


@dataclass(frozen=True)
class Region:
    """
    The actions with exactly the given named coordinates that satisfy
    every bound and linear constraint. All boundaries are closed.

        coordinates   the names an action must use, e.g. variety names
        lower, upper  coordinate -> bound; a missing coordinate is
                      unbounded on that side
        constraints   pairs (coefficients, bound) meaning
                      sum(coefficients[k] * action[k]) <= bound;
                      a coordinate missing from coefficients has
                      coefficient 0

    For example, a perceived budget set over two varieties at perceived
    prices p_a, p_b and income w:

        Region(
            coordinates=("a", "b"),
            lower={"a": 0, "b": 0},
            constraints=(({"a": p_a, "b": p_b}, w),),
        )

    An action is a mapping with exactly these coordinates as keys, each a
    finite real number. A Region is not checked for emptiness when built:
    if no action satisfies it, every selected action is rejected.
    """

    coordinates: tuple[Any, ...]
    lower: Mapping[Any, float] = None
    upper: Mapping[Any, float] = None
    constraints: tuple[tuple[Mapping[Any, float], float], ...] = ()
    tolerance: float = 0.0

    def __post_init__(self):
        coordinates = tuple(self.coordinates)

        if not coordinates:
            raise ValueError("A Region needs at least one coordinate.")

        if len(set(coordinates)) != len(coordinates):
            raise ValueError("Region coordinates must be unique.")

        lower = dict(self.lower or {})
        upper = dict(self.upper or {})
        constraints = tuple(
            (dict(coefficients), bound)
            for coefficients, bound in self.constraints
        )

        known = set(coordinates)

        for label, mapping in (("lower", lower), ("upper", upper)):
            unknown = set(mapping) - known
            if unknown:
                raise ValueError(
                    f"Region {label} names unknown coordinate(s): {sorted(map(str, unknown))}"
                )
            for bound in mapping.values():
                if not _is_real(bound) or math.isnan(bound):
                    raise ValueError(f"Region {label} bounds must be real numbers.")

        for name in known & set(lower) & set(upper):
            if lower[name] > upper[name]:
                raise ValueError(
                    f"Region lower bound exceeds upper bound for {name!r}."
                )

        for coefficients, bound in constraints:
            unknown = set(coefficients) - known
            if unknown:
                raise ValueError(
                    f"Region constraint names unknown coordinate(s): {sorted(map(str, unknown))}"
                )
            if not all(_is_finite_real(value) for value in coefficients.values()):
                raise ValueError("Region constraint coefficients must be finite real numbers.")
            if not _is_finite_real(bound):
                raise ValueError("Region constraint bounds must be finite real numbers.")

        _check_tolerance(self.tolerance)

        object.__setattr__(self, "coordinates", coordinates)
        object.__setattr__(self, "lower", freeze(lower))
        object.__setattr__(self, "upper", freeze(upper))
        object.__setattr__(self, "constraints", freeze(constraints))

    def __contains__(self, action: Any) -> bool:
        if not isinstance(action, Mapping):
            return False

        if set(action) != set(self.coordinates):
            return False

        if not all(_is_finite_real(value) for value in action.values()):
            return False

        for name, bound in self.lower.items():
            if action[name] < bound - _slack(self.tolerance, bound):
                return False

        for name, bound in self.upper.items():
            if action[name] > bound + _slack(self.tolerance, bound):
                return False

        for coefficients, bound in self.constraints:
            total = math.fsum(
                coefficient * action[name]
                for name, coefficient in coefficients.items()
            )
            if total > bound + _slack(self.tolerance, bound):
                return False

        return True


MATHEMATICAL_SETS = (Interval, Region)

# What an agent's perceived_feasible_set may be.
PerceivedFeasibleSet = list[Any] | Interval | Region


def require_enumerated(perceived_feasible_set: Any) -> Any:
    """
    Return F_hat unchanged if it can be enumerated; raise a clear
    TypeError if it is a mathematical set. For decision rules that list
    every perceived feasible action.
    """
    if isinstance(perceived_feasible_set, MATHEMATICAL_SETS):
        raise TypeError(
            f"This decision rule lists every perceived feasible action, but "
            f"F_hat is a {type(perceived_feasible_set).__name__}, which "
            "cannot be enumerated. Use a decision process that selects "
            "from F_hat without listing it."
        )

    return perceived_feasible_set

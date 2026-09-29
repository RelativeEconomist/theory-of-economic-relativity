from copy import deepcopy
from typing import Any


class FrozenDict(dict):
    """
    A dict that refuses mutation after construction.

    Subclassing dict keeps it a drop-in value: it compares equal to a
    plain dict with the same items, indexes, iterates, and prints like
    one. Only the mutating methods are blocked. Construct it through
    freeze(), which also freezes every nested value, so an immutable
    outer mapping never hands out a mutable inner one.
    """

    __slots__ = ()

    def _immutable(self, *args, **kwargs):
        raise TypeError(
            "This mapping is immutable. Build a new one instead of "
            "changing it in place (see research.ter.immutable.thaw)."
        )

    __setitem__ = _immutable
    __delitem__ = _immutable
    __ior__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return (FrozenDict, (dict(self),))


class FrozenList(list):
    """
    A list that refuses mutation after construction.

    Compares equal to a plain list with the same items. `+` still works
    and returns a new plain list, so `frozen + [x]` is the natural way to
    build a changed copy.
    """

    __slots__ = ()

    def _immutable(self, *args, **kwargs):
        raise TypeError(
            "This list is immutable. Build a new one instead of changing "
            "it in place (see research.ter.immutable.thaw)."
        )

    __setitem__ = _immutable
    __delitem__ = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return (FrozenList, (list(self),))


def freeze(value: Any) -> Any:
    """
    Return a deeply immutable copy of value.

    dicts become FrozenDict, lists become FrozenList, sets become
    frozenset, and tuples are rebuilt with frozen items. Any other value
    is deep-copied, so nothing reachable from the result is shared with
    the caller's original.
    """
    if isinstance(value, FrozenDict | FrozenList):
        return value

    if isinstance(value, dict):
        return FrozenDict(
            (key, freeze(item))
            for key, item in value.items()
        )

    if isinstance(value, list):
        return FrozenList(freeze(item) for item in value)

    if isinstance(value, tuple):
        return tuple(freeze(item) for item in value)

    if isinstance(value, set | frozenset):
        return frozenset(freeze(item) for item in value)

    return deepcopy(value)


def thaw(value: Any) -> Any:
    """
    Return an independent, mutable deep copy of a frozen value: the
    inverse of freeze(). Mutating the result never affects the original.
    """
    if isinstance(value, dict):
        return {
            key: thaw(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [thaw(item) for item in value]

    if isinstance(value, tuple):
        return tuple(thaw(item) for item in value)

    if isinstance(value, frozenset):
        return {thaw(item) for item in value}

    return deepcopy(value)

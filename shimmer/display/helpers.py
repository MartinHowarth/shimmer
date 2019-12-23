"""Collection of small functions to simplify common tasks."""

from typing import Callable


def bundle_callables(*callables: Callable) -> Callable:
    """
    Bundle many callables into a single function.

    Callables will be invoked in the order given.
    """

    def bundle_callables_inner(*args, **kwargs):
        """Call all callables in order."""
        for method in callables:
            method(*args, **kwargs)

    return bundle_callables_inner


def bitwise_add(a: int, b: int) -> int:
    """Merge two binary masks together."""
    return a | b


def bitwise_remove(a: int, b: int) -> int:
    """Remove a binary mask from another mask."""
    if bitwise_contains(a, b):
        return a ^ b
    return a


def bitwise_contains(a: int, b: int) -> bool:
    """Return True if any bit of mask `b` is contained in `a`."""
    return bool(a & b)

"""Iterative binary search on a sorted random-access sequence."""

from __future__ import annotations

from collections.abc import Sequence


def binary_search[T](values: Sequence[T], target: T) -> int:
    """Return an index of ``target`` in a nondecreasing sequence, or -1.

    Precondition: ``values`` is sorted in nondecreasing order under ``<``.
    The algorithm does not spend a linear scan checking that precondition.
    If it is false, the returned index is undefined.

    Invariant: if ``target`` occurs in the original sequence, it occurs in
    ``values[low : high + 1]``. When the slice is empty, ``target`` is absent.

    Duplicate targets may occupy any matching index, not necessarily the
    leftmost one. Time is Θ(1) when the first midpoint hits and Θ(log n)
    otherwise. Extra memory is Θ(1).
    """
    low = 0
    high = len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] < target:
            low = middle + 1
        elif target < values[middle]:
            high = middle - 1
        else:
            return middle
    return -1

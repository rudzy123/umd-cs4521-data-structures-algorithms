"""Comparison sorts and counting sort.

Every sort returns a new list and leaves the input sequence unchanged.
Comparison sorts order values with ``<`` only, so a type needs nothing except
a strict weak order.

Stability means equal keys keep the relative order they had in the input.
In-place means the algorithm needs only Θ(1) extra memory besides the output
(recursion stack is called out separately when it is larger than that).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence


def merge_sort[T](values: Sequence[T]) -> list[T]:
    """Return a stable, nondecreasing copy of ``values``.

    Time is Θ(n log n) in the best, average, and worst case. This version
    does not stop early on an already sorted run, so sorted input is not
    faster. Auxiliary space is Θ(n). The sort is stable and not in-place.

    The merge step takes from the left run when the two heads are equal
    (``right[j] < left[i]`` is false), which is what keeps the original order.
    """
    items = list(values)
    if len(items) <= 1:
        return items
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    return _merge(left, right)


def _merge[T](left: list[T], right: list[T]) -> list[T]:
    merged: list[T] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if right[j] < left[i]:
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quicksort[T](values: Sequence[T]) -> list[T]:
    """Return a nondecreasing copy of ``values`` using Lomuto partition.

    The pivot is the last element of the current slice. Partition then places
    that pivot in its final index: everything at a lower index compares ``<=``
    the pivot, and everything at a higher index compares ``>`` the pivot.

    Time is Θ(n log n) on average for random distinct keys and Θ(n²) in the
    worst case. Sorted input, reverse-sorted input, and inputs full of equal
    keys are worst cases for this pivot, because every partition peels off
    only one element. Extra memory is the recursion stack: Θ(log n) expected
    and Θ(n) in that worst case. The sort is in-place aside from that stack,
    and it is not stable.

    A long worst-case chain can exceed Python's recursion limit. The
    benchmark raises the limit; production code that must survive adversarial
    order should pick the pivot at random or bound the depth and switch to
    heap sort.
    """
    items = list(values)
    _quicksort(items, 0, len(items) - 1)
    return items


def _quicksort[T](values: list[T], low: int, high: int) -> None:
    if low >= high:
        return
    pivot_index = _partition(values, low, high)
    _quicksort(values, low, pivot_index - 1)
    _quicksort(values, pivot_index + 1, high)


def _partition[T](values: list[T], low: int, high: int) -> int:
    pivot = values[high]
    store = low
    for index in range(low, high):
        # ``not (pivot < values[index])`` is ``values[index] <= pivot`` and
        # needs only ``<``. Equal keys gather on the left of the pivot.
        if not (pivot < values[index]):
            values[store], values[index] = values[index], values[store]
            store += 1
    values[store], values[high] = values[high], values[store]
    return store


def heap_sort[T](values: Sequence[T]) -> list[T]:
    """Return a nondecreasing copy of ``values`` with an in-place max-heap.

    This is the same heap shape as ``MinHeap``, with the comparison reversed
    so the largest key sits at index 0. The algorithm then swaps that maximum
    into the sorted suffix and sifts the displaced leaf down through the
    unsorted prefix.

    Invariant during the extraction loop: ``values[end + 1:]`` is sorted in
    nondecreasing order, and every key still in the heap is ``<= values[end]``
    once ``end`` has received the extracted maximum.

    Time is Θ(n log n) for distinct keys and Θ(n) when every key is equal,
    because each sift-down stops at the root. Average and worst case on
    distinct keys are Θ(n log n). Extra memory is Θ(1) besides the output
    copy. The sort is in-place and not stable. It does not call ``MinHeap``;
    the index arithmetic is the implementation.
    """
    items = list(values)
    heap_size = len(items)
    for index in range(heap_size // 2 - 1, -1, -1):
        _sift_down_max(items, index, heap_size)
    for end in range(heap_size - 1, 0, -1):
        items[0], items[end] = items[end], items[0]
        _sift_down_max(items, 0, end)
    return items


def _sift_down_max[T](values: list[T], index: int, heap_size: int) -> None:
    while True:
        left = 2 * index + 1
        right = left + 1
        largest = index
        if left < heap_size and values[largest] < values[left]:
            largest = left
        if right < heap_size and values[largest] < values[right]:
            largest = right
        if largest == index:
            return
        values[index], values[largest] = values[largest], values[index]
        index = largest


def counting_sort[T](
    values: Sequence[T],
    *,
    key: Callable[[T], int] | None = None,
    maximum: int | None = None,
) -> list[T]:
    """Stable sort for nonnegative integer keys in a bounded range.

    Constraints
        Every key must be an integer in ``0 .. maximum`` inclusive. When
        ``maximum`` is omitted it is the largest key in the input. Negatives,
        booleans, and non-integers are rejected. ``k`` (the maximum) has to
        be small enough that an array of ``k + 1`` counters is acceptable;
        the algorithm allocates Θ(n + k) memory.

    Time is Θ(n + k) in every case, which is why counting sort can beat the
    Ω(n log n) comparison-sort lower bound: it is not a comparison sort.
    The sort is stable and not in-place.

    Stability comes from the cumulative counters and the right-to-left scan.
    After the prefix sums, ``counts[v]`` is the number of keys that are
    ``<= v``, which is also the index just past the block where ``v`` belongs.
    Placing items from the end of the input fills that block from right to
    left, so an earlier equal key lands in an earlier slot.

    ``key`` defaults to the identity function and exists so equal integers can
    carry an identity (for a stability test, or for a later radix pass).
    The counting and placement steps are still the integer algorithm.
    """
    items = list(values)
    if not items:
        return []
    keys = [_count_key(item if key is None else key(item)) for item in items]
    if maximum is None:
        upper = max(keys)
    else:
        upper = _count_key(maximum)
        if any(count_key > upper for count_key in keys):
            raise ValueError(f"key exceeds maximum {upper}")
    counts = [0] * (upper + 1)
    for count_key in keys:
        counts[count_key] += 1
    for index in range(1, upper + 1):
        counts[index] += counts[index - 1]
    ordered = list(items)
    for index in range(len(items) - 1, -1, -1):
        count_key = keys[index]
        counts[count_key] -= 1
        ordered[counts[count_key]] = items[index]
    return ordered


def _count_key(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("counting sort keys must be nonnegative integers")
    if value < 0:
        raise ValueError("counting sort keys must be nonnegative")
    return value

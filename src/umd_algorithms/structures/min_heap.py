"""Array-backed binary min-heap.

Shape
    The tree is complete and packed left to right into a list. For an index
    ``i``, the parent is ``(i - 1) // 2``, the left child is ``2i + 1``, and
    the right child is ``2i + 2``.

Invariant
    For every ``i > 0``, ``data[parent(i)] <= data[i]``. The minimum is at
    index 0 whenever the heap is nonempty. Comparison uses ``<`` only.

Complexity
    ``peek`` is Θ(1). ``push`` is Θ(1) in the best case and Θ(log n) in the
    worst case; a random new key stops after an expected constant number of
    swaps. ``pop`` is Θ(log n) in the average and worst case, and Θ(1) only
    when the relocated leaf already satisfies the heap property.
    ``heapify`` (Floyd's bottom-up construction) is Θ(n), which is tighter
    than pushing ``n`` keys one at a time (Θ(n log n)).
"""

from __future__ import annotations

from collections.abc import Iterable


def _parent(index: int) -> int:
    return (index - 1) // 2


def _left(index: int) -> int:
    return 2 * index + 1


def _right(index: int) -> int:
    return 2 * index + 2


class MinHeap[T]:
    """Priority queue that returns the smallest key first."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __repr__(self) -> str:
        return f"MinHeap({self._data})"

    @classmethod
    def heapify(cls, values: Iterable[T]) -> MinHeap[T]:
        """Build a heap in Θ(n) time by sifting down from the last parent."""
        heap = cls()
        heap._data = list(values)
        last_parent = len(heap._data) // 2 - 1
        for index in range(last_parent, -1, -1):
            heap._sift_down(index)
        return heap

    def peek(self) -> T:
        """Return the minimum without removing it."""
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def push(self, value: T) -> None:
        """Insert ``value`` and sift it up until the heap property holds."""
        self._data.append(value)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> T:
        """Remove and return the minimum.

        The last leaf takes the root's place and sifts down. That keeps the
        complete shape: the array stays packed with no holes.
        """
        if not self._data:
            raise IndexError("pop from empty heap")
        minimum = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return minimum

    def is_valid(self) -> bool:
        """Return whether every parent is ``<=`` both of its children."""
        for index in range(1, len(self._data)):
            if self._data[index] < self._data[_parent(index)]:
                return False
        return True

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = _parent(index)
            if not (self._data[index] < self._data[parent]):
                return
            self._data[index], self._data[parent] = self._data[parent], self._data[index]
            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self._data)
        while True:
            left = _left(index)
            right = _right(index)
            smallest = index
            if left < size and self._data[left] < self._data[smallest]:
                smallest = left
            if right < size and self._data[right] < self._data[smallest]:
                smallest = right
            if smallest == index:
                return
            self._data[index], self._data[smallest] = self._data[smallest], self._data[index]
            index = smallest

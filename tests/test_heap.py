"""Min-heap order and Floyd's linear heapify."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import MinHeap


def test_empty_heap() -> None:
    heap = MinHeap[int]()
    assert not heap
    assert len(heap) == 0
    assert heap.is_valid()
    with pytest.raises(IndexError):
        heap.peek()
    with pytest.raises(IndexError):
        heap.pop()


def test_push_and_pop_with_duplicates() -> None:
    heap = MinHeap[int]()
    for value in (5, 1, 5, 3, 1, 4):
        heap.push(value)
        assert heap.is_valid()
        assert heap.peek() == min(heap.peek(), value)
    popped = [heap.pop() for _ in range(6)]
    assert popped == [1, 1, 3, 4, 5, 5]
    assert heap.is_valid()
    assert len(heap) == 0


def test_heapify_matches_sorted_order() -> None:
    values = [9, 4, 7, 1, 4, 0, 8]
    heap = MinHeap.heapify(values)
    assert heap.is_valid()
    assert [heap.pop() for _ in values] == sorted(values)
    assert values == [9, 4, 7, 1, 4, 0, 8]


@given(st.lists(st.integers(-500, 500), max_size=50))
def test_pop_order_matches_sorted(values: list[int]) -> None:
    heap = MinHeap.heapify(values)
    assert heap.is_valid()
    assert [heap.pop() for _ in values] == sorted(values)
    assert heap.is_valid()


@given(st.lists(st.integers(), max_size=40))
def test_incremental_pushes_keep_the_invariant(values: list[int]) -> None:
    heap = MinHeap[int]()
    seen: list[int] = []
    for value in values:
        heap.push(value)
        seen.append(value)
        assert heap.is_valid()
        assert heap.peek() == min(seen)
    assert [heap.pop() for _ in seen] == sorted(seen)

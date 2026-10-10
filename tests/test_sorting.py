"""Sorting correctness, stability, constraints, and comparison with ``sorted``."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import counting_sort, heap_sort, merge_sort, quicksort

SORTS = (merge_sort, quicksort, heap_sort)


class Item:
    """Ordered only by ``key``. ``label`` exposes whether a sort is stable."""

    def __init__(self, key: int, label: int) -> None:
        self.key = key
        self.label = label

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self.key < other.key

    def __repr__(self) -> str:
        return f"Item({self.key}, {self.label})"


def test_empty_and_singleton() -> None:
    for sort in (*SORTS, counting_sort):
        assert sort([]) == []
        assert sort([7]) == [7]


def test_does_not_mutate_the_input() -> None:
    original = [3, 1, 2, 1]
    snapshot = list(original)
    for sort in (*SORTS, counting_sort):
        assert sort(original) == [1, 1, 2, 3]
        assert original == snapshot


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize(
    "values",
    [
        [3, 1, 2],
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [5, 1, 5, 1, 5],
        [-2, 0, -2, 8, 3],
    ],
)
def test_comparison_sorts_match_python_sorted(sort, values: list[int]) -> None:
    assert sort(values) == sorted(values)


def test_counting_sort_matches_python_sorted_on_nonnegative_ints() -> None:
    assert counting_sort([3, 1, 2, 1, 0]) == [0, 1, 1, 2, 3]
    assert counting_sort([4, 1, 3], maximum=10) == [1, 3, 4]
    assert counting_sort([0, 0, 0]) == [0, 0, 0]


def test_counting_sort_constraints() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        counting_sort([1, -1, 0])
    with pytest.raises(TypeError, match="integers"):
        counting_sort([1, True, 0])
    with pytest.raises(TypeError, match="integers"):
        counting_sort([1.0, 2.0])  # type: ignore[list-item]
    with pytest.raises(ValueError, match="maximum"):
        counting_sort([1, 4], maximum=3)
    with pytest.raises(ValueError, match="nonnegative"):
        counting_sort([1], maximum=-1)


def test_merge_sort_and_counting_sort_are_stable() -> None:
    keys = [3, 1, 3, 2, 1, 3, 2]
    items = [Item(key, index) for index, key in enumerate(keys)]
    expected = [item.label for item in sorted(items)]
    assert [item.label for item in merge_sort(items)] == expected
    counted = counting_sort(items, key=lambda item: item.key)
    assert [item.label for item in counted] == expected


@given(st.lists(st.integers(-1000, 1000), max_size=40))
def test_comparison_sorts_match_sorted_property(values: list[int]) -> None:
    expected = sorted(values)
    for sort in SORTS:
        snapshot = list(values)
        assert sort(values) == expected
        assert values == snapshot


@given(st.lists(st.integers(0, 30), max_size=40))
def test_counting_sort_matches_sorted_property(values: list[int]) -> None:
    assert counting_sort(values) == sorted(values)


@given(st.lists(st.integers(0, 6), max_size=30))
def test_stability_property(keys: list[int]) -> None:
    items = [Item(key, index) for index, key in enumerate(keys)]
    expected = [item.label for item in sorted(items)]
    assert [item.label for item in merge_sort(items)] == expected
    assert [item.label for item in counting_sort(items, key=lambda item: item.key)] == expected


@given(st.lists(st.integers(0, 5), min_size=1, max_size=25))
def test_equal_heavy_inputs_match_sorted(values: list[int]) -> None:
    expected = sorted(values)
    assert quicksort(values) == expected
    assert heap_sort(values) == expected
    assert merge_sort(values) == expected
    assert counting_sort(values) == expected

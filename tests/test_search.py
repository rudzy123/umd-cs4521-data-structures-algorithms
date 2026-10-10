"""Binary search on sorted sequences, including duplicates and empty input."""

from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import binary_search


def test_empty_and_edges() -> None:
    assert binary_search([], 1) == -1
    assert binary_search([4], 4) == 0
    assert binary_search([4], 5) == -1
    assert binary_search([1, 2, 3, 4], 1) == 0
    assert binary_search([1, 2, 3, 4], 4) == 3
    assert binary_search([1, 2, 3, 4], 0) == -1
    assert binary_search([1, 2, 3, 4], 5) == -1


def test_duplicates_return_some_matching_index() -> None:
    values = [1, 2, 2, 2, 3]
    index = binary_search(values, 2)
    assert index in {1, 2, 3}
    assert values[index] == 2


def test_strings() -> None:
    words = ["ant", "bee", "cat", "dog"]
    assert binary_search(words, "cat") == 2
    assert binary_search(words, "asp") == -1


@given(st.lists(st.integers(-200, 200), max_size=40), st.integers(-250, 250))
def test_matches_membership(values: list[int], target: int) -> None:
    ordered = sorted(values)
    index = binary_search(ordered, target)
    if target in ordered:
        assert index != -1
        assert ordered[index] == target
    else:
        assert index == -1


@given(st.lists(st.integers(), unique=True, max_size=30))
def test_unique_sorted_index_is_exact(values: list[int]) -> None:
    ordered = sorted(values)
    for expected, value in enumerate(ordered):
        assert binary_search(ordered, value) == expected
    if ordered:
        assert binary_search(ordered, ordered[0] - 1) == -1
        assert binary_search(ordered, ordered[-1] + 1) == -1


def test_precondition_is_sorted_order() -> None:
    # The supported input is a nondecreasing sequence. The result is undefined
    # when that precondition is false, so this test only covers a sorted one.
    assert binary_search([1, 3, 5, 7, 9], 7) == 3

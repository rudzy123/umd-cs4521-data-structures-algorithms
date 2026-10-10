"""Dynamic programming: subsequence structure and optimal knapsack value."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import knapsack_01, longest_common_subsequence


def _is_subsequence(pattern: str, text: str) -> bool:
    index = 0
    for character in text:
        if index < len(pattern) and pattern[index] == character:
            index += 1
    return index == len(pattern)


def _lcs_length(left: str, right: str) -> int:
    memo: dict[tuple[int, int], int] = {}

    def length(i: int, j: int) -> int:
        if i == len(left) or j == len(right):
            return 0
        key = (i, j)
        if key not in memo:
            if left[i] == right[j]:
                memo[key] = 1 + length(i + 1, j + 1)
            else:
                memo[key] = max(length(i + 1, j), length(i, j + 1))
        return memo[key]

    return length(0, 0)


def _brute_knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    best = 0
    for mask in range(1 << len(weights)):
        weight = 0
        value = 0
        for index in range(len(weights)):
            if mask & (1 << index):
                weight += weights[index]
                value += values[index]
        if weight <= capacity:
            best = max(best, value)
    return best


def test_lcs_examples_and_empty_strings() -> None:
    assert longest_common_subsequence("", "abc") == ""
    assert longest_common_subsequence("abc", "") == ""
    assert longest_common_subsequence("abc", "abc") == "abc"
    assert longest_common_subsequence("abc", "def") == ""
    assert longest_common_subsequence("aXbYc", "abc") == "abc"
    classic = longest_common_subsequence("ABCBDAB", "BDCABA")
    assert len(classic) == 4
    assert _is_subsequence(classic, "ABCBDAB")
    assert _is_subsequence(classic, "BDCABA")


def test_knapsack_examples_empty_and_zero_capacity() -> None:
    assert knapsack_01([], [], 5) == (0, [])
    assert knapsack_01([2], [3], 0) == (0, [])
    assert knapsack_01([0], [5], 0) == (5, [0])
    assert knapsack_01([5], [9], 4) == (0, [])

    weights = [1, 3, 4, 5]
    values = [1, 4, 5, 7]
    best, chosen = knapsack_01(weights, values, 7)
    assert best == 9
    assert sum(weights[index] for index in chosen) <= 7
    assert sum(values[index] for index in chosen) == 9

    # Density greedy takes the first item (value 3). The optimum takes the second.
    assert knapsack_01([2, 3], [3, 4], 3) == (4, [1])


def test_knapsack_constraints() -> None:
    with pytest.raises(ValueError, match="same length"):
        knapsack_01([1], [1, 2], 1)
    with pytest.raises(ValueError, match="nonnegative"):
        knapsack_01([1, -1], [1, 1], 2)
    with pytest.raises(ValueError, match="nonnegative"):
        knapsack_01([1], [1], -3)
    with pytest.raises(TypeError):
        knapsack_01([1, True], [1, 1], 2)  # type: ignore[list-item]
    with pytest.raises(TypeError):
        knapsack_01([1.5], [1], 2)  # type: ignore[list-item]


@given(st.text(alphabet="abcd", max_size=7), st.text(alphabet="abcd", max_size=7))
def test_lcs_is_optimal_subsequence(left: str, right: str) -> None:
    found = longest_common_subsequence(left, right)
    assert _is_subsequence(found, left)
    assert _is_subsequence(found, right)
    assert len(found) == _lcs_length(left, right)
    assert longest_common_subsequence(left, left) == left


@given(
    st.lists(st.tuples(st.integers(0, 10), st.integers(0, 15)), max_size=8),
    st.integers(0, 25),
)
def test_knapsack_matches_brute_force(items: list[tuple[int, int]], capacity: int) -> None:
    weights = [weight for weight, _value in items]
    values = [value for _weight, value in items]
    best, chosen = knapsack_01(weights, values, capacity)
    assert best == _brute_knapsack(weights, values, capacity)
    assert sorted(chosen) == chosen
    assert len(set(chosen)) == len(chosen)
    assert sum(weights[index] for index in chosen) <= capacity
    assert sum(values[index] for index in chosen) == best

"""Longest common subsequence and 0/1 knapsack.

Both problems have optimal substructure and overlapping subproblems, so a
table of smaller answers is filled once and reused. Neither problem has the
greedy-choice property that would let a locally best step be fixed forever.
"""

from __future__ import annotations

from collections.abc import Sequence


def longest_common_subsequence(left: str, right: str) -> str:
    """Return one longest common subsequence of ``left`` and ``right``.

    A subsequence keeps relative order and may skip characters. It is not a
    substring: the chosen characters do not have to be contiguous.

    ``dp[i][j]`` is the length of an LCS of ``left[:i]`` and ``right[:j]``.
    When the current characters match, the optimum extends the LCS of the two
    prefixes with that character removed. When they differ, the optimum is the
    better of skipping one character from either string.

    Time and space are Θ(1) when either string is empty and Θ(mn) otherwise,
    where ``m`` and ``n`` are the string lengths. Several subsequences can
    share that optimal length. Reconstruction prefers skipping a character of
    ``left`` when the two choices have equal length, so the result is
    deterministic.
    """
    if not left or not right:
        return ""
    rows = len(left) + 1
    columns = len(right) + 1
    lengths = [[0] * columns for _ in range(rows)]
    for i in range(1, rows):
        for j in range(1, columns):
            if left[i - 1] == right[j - 1]:
                lengths[i][j] = lengths[i - 1][j - 1] + 1
            else:
                lengths[i][j] = max(lengths[i - 1][j], lengths[i][j - 1])
    characters: list[str] = []
    i = len(left)
    j = len(right)
    while i > 0 and j > 0:
        if left[i - 1] == right[j - 1]:
            characters.append(left[i - 1])
            i -= 1
            j -= 1
        elif lengths[i - 1][j] >= lengths[i][j - 1]:
            i -= 1
        else:
            j -= 1
    characters.reverse()
    return "".join(characters)


def knapsack_01(
    weights: Sequence[int],
    values: Sequence[int],
    capacity: int,
) -> tuple[int, list[int]]:
    """Solve the 0/1 knapsack problem with a capacity table.

    Each item may be taken once or not at all. ``dp[i][c]`` is the maximum
    value using only the first ``i`` items and capacity ``c``. The recurrence
    either skips item ``i - 1`` or, when it fits, takes it on top of the best
    packing of the earlier items in the remaining capacity.

    Return ``(best_value, chosen_indexes)``. Indexes are in increasing order.
    When several packs share the optimal value, reconstruction skips an item
    whose row does not change the cell, so a zero-value item is left behind
    and ties prefer the later items that actually improved the table.

    Constraints: ``weights`` and ``values`` have the same length, every weight
    and value is a nonnegative integer, and ``capacity`` is a nonnegative
    integer. Booleans are rejected. Time and space are Θ(n W). That is
    pseudo-polynomial: it is polynomial in the numeric value of ``W``, not in
    the number of bits needed to write ``W``.

    The value-density greedy rule that solves the fractional knapsack problem
    is not correct here. An item with the best value per unit weight can fill
    the pack and block a higher-value combination of smaller items.
    """
    if len(weights) != len(values):
        raise ValueError("weights and values must have the same length")
    _require_nonnegative_int(capacity, "capacity")
    checked_weights = [_require_nonnegative_int(weight, "weight") for weight in weights]
    checked_values = [_require_nonnegative_int(value, "value") for value in values]
    item_count = len(checked_weights)
    table = [[0] * (capacity + 1) for _ in range(item_count + 1)]
    for item in range(1, item_count + 1):
        weight = checked_weights[item - 1]
        value = checked_values[item - 1]
        previous = table[item - 1]
        current = table[item]
        for room in range(capacity + 1):
            best = previous[room]
            if weight <= room:
                best = max(best, previous[room - weight] + value)
            current[room] = best
    chosen: list[int] = []
    room = capacity
    for item in range(item_count, 0, -1):
        if table[item][room] != table[item - 1][room]:
            chosen.append(item - 1)
            room -= checked_weights[item - 1]
    chosen.reverse()
    return table[item_count][capacity], chosen


def _require_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be a nonnegative integer")
    if value < 0:
        raise ValueError(f"{label} must be nonnegative")
    return value

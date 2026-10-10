"""Path compression, union by rank, and connectivity."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import DisjointSet


def test_elements_start_separate() -> None:
    components = DisjointSet([1, 2, 3])
    assert len(components) == 3
    assert components.component_count() == 3
    assert components.connected(1, 1)
    assert not components.connected(1, 2)
    assert components.find(2) == 2
    assert components.union(1, 1) is False
    assert components.stored_rank(1) == 0


def test_union_by_rank_and_path_compression() -> None:
    components = DisjointSet(range(8))
    for left, right in ((0, 1), (2, 3), (4, 5), (6, 7)):
        assert components.union(left, right) is True
    assert components.parent_pointer(1) == 0
    assert components.stored_rank(0) == 1
    assert components.stored_rank(1) == 0

    assert components.union(0, 2) is True
    assert components.union(4, 6) is True
    assert components.stored_rank(0) == 2
    assert components.parent_pointer(2) == 0
    assert components.parent_pointer(3) == 2

    assert components.find(3) == 0
    assert components.parent_pointer(3) == 0
    assert components.parent_pointer(2) == 0

    assert components.union(0, 4) is True
    assert components.stored_rank(0) == 3
    # 5 still points at 4, and 4 now points at 0. find compresses only its path.
    assert components.parent_pointer(5) == 4
    assert components.find(5) == 0
    assert components.parent_pointer(5) == 0
    assert components.parent_pointer(4) == 0
    assert components.parent_pointer(6) == 4
    assert components.find(6) == 0
    assert components.parent_pointer(6) == 0

    assert components.component_count() == 1
    for element in range(8):
        parent = components.parent_pointer(element)
        if parent != element:
            assert components.stored_rank(parent) >= components.stored_rank(element)
        assert components.connected(element, 0)


def test_unknown_element_and_nan() -> None:
    components = DisjointSet([1])
    with pytest.raises(KeyError):
        components.find(2)
    with pytest.raises(ValueError, match="NaN"):
        components.add(float("nan"))
    components.add(4)
    assert 4 in components
    assert components.union(1, 4) is True
    assert components.connected(4, 1)


class _ParentOracle:
    """Connectivity oracle that compresses paths and does not use rank."""

    def __init__(self, count: int) -> None:
        self._parent = list(range(count))

    def find(self, element: int) -> int:
        if self._parent[element] != element:
            self._parent[element] = self.find(self._parent[element])
        return self._parent[element]

    def union(self, left: int, right: int) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left != root_right:
            self._parent[root_right] = root_left

    def connected(self, left: int, right: int) -> bool:
        return self.find(left) == self.find(right)


@given(
    st.integers(1, 25),
    st.lists(st.tuples(st.integers(0, 24), st.integers(0, 24)), max_size=40),
)
def test_connectivity_matches_an_independent_oracle(
    count: int, unions: list[tuple[int, int]]
) -> None:
    components = DisjointSet(range(count))
    oracle = _ParentOracle(count)
    for left, right in unions:
        if left >= count or right >= count:
            continue
        components.union(left, right)
        oracle.union(left, right)
    for left in range(count):
        for right in range(count):
            assert components.connected(left, right) is oracle.connected(left, right)

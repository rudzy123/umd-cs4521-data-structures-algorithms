"""AVL balance, rotations, and the Fibonacci height bound."""

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import AVLTree, maximum_avl_height


def _independent_height_limit(node_count: int) -> int:
    """Oracle copied from the recurrence, so the test does not trust the library."""
    if node_count == 0:
        return -1
    shortest_previous = 0
    shortest_current = 1
    height = 0
    while True:
        shortest_next = 1 + shortest_current + shortest_previous
        if shortest_next > node_count:
            return height
        shortest_previous = shortest_current
        shortest_current = shortest_next
        height += 1


def assert_avl_shape(tree: AVLTree[int]) -> None:
    count = len(tree)
    assert tree.is_valid()
    assert tree.height() <= _independent_height_limit(count)
    if count:
        assert tree.height() >= math.floor(math.log2(count))
        for key in tree.inorder():
            assert tree.balance_factor(key) in {-1, 0, 1}


def test_height_limit_matches_the_recurrence() -> None:
    expected = {0: -1, 1: 0, 2: 1, 3: 1, 4: 2, 6: 2, 7: 3, 11: 3, 12: 4}
    for count, height in expected.items():
        assert maximum_avl_height(count) == height
        assert _independent_height_limit(count) == height


def test_sorted_insertion_stays_balanced() -> None:
    tree = AVLTree[int]()
    assert tree.height() == -1
    for key in range(1, 32):
        tree.insert(key)
        assert tree.inorder() == list(range(1, key + 1))
        assert_avl_shape(tree)
    # The same insertion order makes an unbalanced BST a chain of height 30.
    assert tree.height() < 30


def test_classic_rotations() -> None:
    left_left = AVLTree[int]()
    for key in (3, 2, 1):
        left_left.insert(key)
    assert left_left.inorder() == [1, 2, 3]
    assert left_left.height() == 1

    right_right = AVLTree[int]()
    for key in (1, 2, 3):
        right_right.insert(key)
    assert right_right.height() == 1

    left_right = AVLTree[int]()
    for key in (3, 1, 2):
        left_right.insert(key)
    assert left_right.inorder() == [1, 2, 3]
    assert left_right.height() == 1

    right_left = AVLTree[int]()
    for key in (1, 3, 2):
        right_left.insert(key)
    assert right_left.height() == 1


def test_delete_rebalances() -> None:
    tree = AVLTree[int]()
    for key in (2, 1, 3):
        tree.insert(key)
    tree.delete(1)
    assert tree.inorder() == [2, 3]
    assert_avl_shape(tree)
    tree.delete(2)
    tree.delete(3)
    assert tree.inorder() == []
    assert tree.height() == -1
    assert tree.is_valid()


def test_duplicate_missing_and_nan() -> None:
    tree = AVLTree[int]()
    tree.insert(5)
    with pytest.raises(ValueError, match="duplicate"):
        tree.insert(5)
    with pytest.raises(KeyError):
        tree.delete(8)
    with pytest.raises(KeyError):
        tree.balance_factor(8)
    with pytest.raises(ValueError, match="empty"):
        AVLTree[int]().minimum()
    with pytest.raises(ValueError, match="NaN"):
        AVLTree[float]().insert(math.nan)
    assert tree.inorder() == [5]
    assert len(tree) == 1


@given(st.lists(st.integers(-300, 300), unique=True, max_size=48))
def test_random_updates_stay_balanced(keys: list[int]) -> None:
    tree = AVLTree[int]()
    for key in keys:
        tree.insert(key)
        assert key in tree
        assert_avl_shape(tree)
    assert tree.inorder() == sorted(keys)
    for key in keys[::2]:
        tree.delete(key)
        assert key not in tree
        assert_avl_shape(tree)
    remaining = [key for key in keys if key not in set(keys[::2])]
    assert tree.inorder() == sorted(remaining)
    assert len(tree) == len(remaining)
    if remaining:
        assert tree.minimum() == min(remaining)
        assert tree.maximum() == max(remaining)

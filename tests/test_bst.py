"""Binary search tree: order, deletion cases, and shape."""

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import BinarySearchTree


def test_empty_tree() -> None:
    tree = BinarySearchTree[int]()
    assert len(tree) == 0
    assert tree.height() == -1
    assert tree.inorder() == []
    assert tree.is_valid()
    assert 1 not in tree
    with pytest.raises(ValueError, match="empty"):
        tree.minimum()
    with pytest.raises(ValueError, match="empty"):
        tree.maximum()
    with pytest.raises(KeyError):
        tree.delete(1)


def test_sorted_insertion_degenerates_to_a_chain() -> None:
    tree = BinarySearchTree[int]()
    keys = list(range(12))
    for key in keys:
        tree.insert(key)
        assert tree.is_valid()
    assert tree.inorder() == keys
    assert tree.height() == len(keys) - 1
    assert tree.minimum() == 0
    assert tree.maximum() == 11


def test_delete_leaf_one_child_and_two_children() -> None:
    tree = BinarySearchTree[int]()
    for key in (5, 2, 8, 1, 3, 7, 9):
        tree.insert(key)
    tree.delete(2)  # two children; successor is 3
    assert tree.inorder() == [1, 3, 5, 7, 8, 9]
    tree.delete(1)  # leaf
    tree.delete(9)  # leaf
    tree.delete(8)  # only the left child 7 remains
    assert tree.inorder() == [3, 5, 7]
    assert tree.is_valid()
    assert len(tree) == 3


def test_duplicate_and_missing_key_leave_the_tree_unchanged() -> None:
    tree = BinarySearchTree[int]()
    tree.insert(4)
    with pytest.raises(ValueError, match="duplicate"):
        tree.insert(4)
    with pytest.raises(KeyError):
        tree.delete(9)
    assert tree.inorder() == [4]
    assert len(tree) == 1
    assert tree.is_valid()


def test_nan_is_rejected() -> None:
    tree = BinarySearchTree[float]()
    with pytest.raises(ValueError, match="NaN"):
        tree.insert(math.nan)
    assert len(tree) == 0


def test_delete_until_empty() -> None:
    tree = BinarySearchTree[int]()
    for key in (2, 1, 3):
        tree.insert(key)
    for key in (2, 1, 3):
        tree.delete(key)
        assert tree.is_valid()
    assert tree.inorder() == []
    assert tree.height() == -1


@given(st.lists(st.integers(-200, 200), unique=True, max_size=40))
def test_insert_delete_preserves_order_and_invariant(keys: list[int]) -> None:
    tree = BinarySearchTree[int]()
    for key in keys:
        tree.insert(key)
        assert tree.is_valid()
        assert key in tree
    assert tree.inorder() == sorted(keys)
    assert len(tree) == len(keys)
    removed = keys[::2]
    for key in removed:
        tree.delete(key)
        assert tree.is_valid()
        assert key not in tree
    remaining = [key for key in keys if key not in set(removed)]
    assert tree.inorder() == sorted(remaining)
    assert len(tree) == len(remaining)
    if remaining:
        assert tree.minimum() == min(remaining)
        assert tree.maximum() == max(remaining)

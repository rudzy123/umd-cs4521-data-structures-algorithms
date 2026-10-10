"""Unbalanced binary search tree.

Invariant
    For every node ``x``, every key in the left subtree is ``< x.key`` and every
    key in the right subtree is ``> x.key``. Equivalently, an inorder walk is
    strictly increasing. Duplicate keys are rejected, so the order is strict.

Complexity
    Let ``h`` be the height (empty tree = -1, a leaf = 0).
    ``search``, ``insert``, and ``delete`` take Θ(h) time and Θ(h) stack space.
    On a random insertion order the expected height is Θ(log n). Sorted
    insertion produces a chain of height n - 1, so the worst case is Θ(n).
    ``minimum`` and ``maximum`` are Θ(h) time and Θ(1) extra memory.
    ``height`` walks the whole tree, so it is Θ(n). ``inorder`` is Θ(n).

The tree stores only child links. Nothing here rebalances; see ``AVLTree``
for the same ordered-set interface with a logarithmic height bound.
"""

from __future__ import annotations

import math
from typing import cast


class _Node[T]:
    __slots__ = ("key", "left", "right")

    def __init__(self, key: T) -> None:
        self.key = key
        self.left: _Node[T] | None = None
        self.right: _Node[T] | None = None


def _reject_nan(key: object) -> None:
    if isinstance(key, float) and math.isnan(key):
        raise ValueError("NaN is not a valid ordered key")


class BinarySearchTree[T]:
    """Ordered set of unique, totally ordered keys."""

    def __init__(self) -> None:
        self._root: _Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        return self.search(cast(T, key))

    def __repr__(self) -> str:
        return f"BinarySearchTree({self.inorder()})"

    def search(self, key: T) -> bool:
        """Return whether ``key`` is stored. Time Θ(h)."""
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return True
        return False

    def insert(self, key: T) -> None:
        """Insert ``key``. Raise ``ValueError`` if it is already present."""
        _reject_nan(key)
        self._root = self._insert(self._root, key)
        self._size += 1

    def delete(self, key: T) -> None:
        """Remove ``key``. Raise ``KeyError`` if it is absent.

        A node with two children is replaced by its inorder successor, the
        least key in the right subtree. That successor has no left child, so
        removing it is a one-child deletion.
        """
        self._root = self._delete(self._root, key)
        self._size -= 1

    def minimum(self) -> T:
        """Return the least key. Raise ``ValueError`` on an empty tree."""
        node = self._root
        if node is None:
            raise ValueError("empty tree")
        while node.left is not None:
            node = node.left
        return node.key

    def maximum(self) -> T:
        """Return the greatest key. Raise ``ValueError`` on an empty tree."""
        node = self._root
        if node is None:
            raise ValueError("empty tree")
        while node.right is not None:
            node = node.right
        return node.key

    def height(self) -> int:
        """Return the height. An empty tree has height -1 and a leaf has height 0."""
        return _height(self._root)

    def inorder(self) -> list[T]:
        """Return keys in sorted order. Time Θ(n), stack Θ(h)."""
        keys: list[T] = []
        _inorder(self._root, keys)
        return keys

    def is_valid(self) -> bool:
        """Check the BST subtree invariant and the stored size.

        Bounds are ancestor nodes: every key under ``node`` must lie strictly
        between the nearest smaller ancestor and the nearest larger ancestor.
        """
        return _valid(self._root, None, None) and _count(self._root) == self._size

    def _insert(self, node: _Node[T] | None, key: T) -> _Node[T]:
        if node is None:
            return _Node(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif node.key < key:
            node.right = self._insert(node.right, key)
        else:
            raise ValueError(f"duplicate key: {key!r}")
        return node

    def _delete(self, node: _Node[T] | None, key: T) -> _Node[T] | None:
        if node is None:
            raise KeyError(key)
        if key < node.key:
            node.left = self._delete(node.left, key)
            return node
        if node.key < key:
            node.right = self._delete(node.right, key)
            return node
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.key = successor.key
        node.right = self._delete(node.right, successor.key)
        return node


def _height[T](node: _Node[T] | None) -> int:
    if node is None:
        return -1
    return 1 + max(_height(node.left), _height(node.right))


def _inorder[T](node: _Node[T] | None, keys: list[T]) -> None:
    if node is None:
        return
    _inorder(node.left, keys)
    keys.append(node.key)
    _inorder(node.right, keys)


def _valid[T](node: _Node[T] | None, lower: _Node[T] | None, upper: _Node[T] | None) -> bool:
    if node is None:
        return True
    if lower is not None and not (lower.key < node.key):
        return False
    if upper is not None and not (node.key < upper.key):
        return False
    return _valid(node.left, lower, node) and _valid(node.right, node, upper)


def _count[T](node: _Node[T] | None) -> int:
    if node is None:
        return 0
    return 1 + _count(node.left) + _count(node.right)

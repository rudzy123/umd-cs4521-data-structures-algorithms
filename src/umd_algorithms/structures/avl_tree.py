"""AVL tree: a binary search tree whose height stays logarithmic.

Invariant
    The BST invariant holds: for every node, left keys are smaller and right
    keys are larger. In addition every node stores its height and the balance
    factor ``height(left) - height(right)`` is in ``{-1, 0, 1}``.
    Empty height is -1 and a leaf has height 0.

    The tallest AVL tree on ``n`` nodes has height ``h`` where ``n`` is at
    least the Fibonacci number of nodes ``N(h) = 1 + N(h - 1) + N(h - 2)``,
    with ``N(0) = 1`` and ``N(-1) = 0``. Therefore ``h`` is Θ(log n), about
    ``1.44 log2(n)`` in the worst shape.

Complexity
    ``search``, ``insert``, and ``delete`` are Θ(log n) time and Θ(log n)
    stack space in every case. ``height`` is Θ(1) because it reads the stored
    root height. ``inorder`` is Θ(n). ``minimum`` and ``maximum`` are Θ(log n).

Rotations restore the balance factor after an update. A single rotation fixes
a straight imbalance (left-left or right-right). A double rotation fixes a
bent imbalance (left-right or right-left).
"""

from __future__ import annotations

import math
from typing import cast


class _Node[T]:
    __slots__ = ("height", "key", "left", "right")

    def __init__(self, key: T) -> None:
        self.key = key
        self.left: _Node[T] | None = None
        self.right: _Node[T] | None = None
        self.height = 0


def _reject_nan(key: object) -> None:
    if isinstance(key, float) and math.isnan(key):
        raise ValueError("NaN is not a valid ordered key")


def _height[T](node: _Node[T] | None) -> int:
    return -1 if node is None else node.height


class AVLTree[T]:
    """Height-balanced ordered set of unique keys."""

    def __init__(self) -> None:
        self._root: _Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        return self.search(cast(T, key))

    def __repr__(self) -> str:
        return f"AVLTree({self.inorder()})"

    def search(self, key: T) -> bool:
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
        """Insert ``key`` and rebalance. Raise ``ValueError`` on a duplicate."""
        _reject_nan(key)
        self._root = self._insert(self._root, key)
        self._size += 1

    def delete(self, key: T) -> None:
        """Remove ``key`` and rebalance. Raise ``KeyError`` if it is absent."""
        self._root = self._delete(self._root, key)
        self._size -= 1

    def minimum(self) -> T:
        node = self._root
        if node is None:
            raise ValueError("empty tree")
        while node.left is not None:
            node = node.left
        return node.key

    def maximum(self) -> T:
        node = self._root
        if node is None:
            raise ValueError("empty tree")
        while node.right is not None:
            node = node.right
        return node.key

    def height(self) -> int:
        """Return the stored root height. Θ(1)."""
        return _height(self._root)

    def balance_factor(self, key: T) -> int:
        """Return ``height(left) - height(right)`` for the node holding ``key``."""
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return _height(node.left) - _height(node.right)
        raise KeyError(key)

    def inorder(self) -> list[T]:
        keys: list[T] = []
        _inorder(self._root, keys)
        return keys

    def is_valid(self) -> bool:
        """Check BST order, stored heights, balance factors, and size."""
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
        self._refresh(node)
        return self._rebalance(node)

    def _delete(self, node: _Node[T] | None, key: T) -> _Node[T] | None:
        if node is None:
            raise KeyError(key)
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif node.key < key:
            node.right = self._delete(node.right, key)
        elif node.left is None:
            return node.right
        elif node.right is None:
            return node.left
        else:
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        self._refresh(node)
        return self._rebalance(node)

    def _refresh(self, node: _Node[T]) -> None:
        node.height = 1 + max(_height(node.left), _height(node.right))

    def _rebalance(self, node: _Node[T]) -> _Node[T]:
        balance = _height(node.left) - _height(node.right)
        if balance > 1:
            left = node.left
            if left is None:
                raise RuntimeError("AVL balance is inconsistent with the left child")
            # Left-right: the left child leans right, so rotate it first.
            if _height(left.right) > _height(left.left):
                node.left = self._rotate_left(left)
            return self._rotate_right(node)
        if balance < -1:
            right = node.right
            if right is None:
                raise RuntimeError("AVL balance is inconsistent with the right child")
            # Right-left: the right child leans left, so rotate it first.
            if _height(right.left) > _height(right.right):
                node.right = self._rotate_right(right)
            return self._rotate_left(node)
        return node

    def _rotate_left(self, node: _Node[T]) -> _Node[T]:
        child = node.right
        if child is None:
            raise RuntimeError("left rotation requires a right child")
        node.right = child.left
        child.left = node
        # Refresh the lower node first; the new root's height depends on it.
        self._refresh(node)
        self._refresh(child)
        return child

    def _rotate_right(self, node: _Node[T]) -> _Node[T]:
        child = node.left
        if child is None:
            raise RuntimeError("right rotation requires a left child")
        node.left = child.right
        child.right = node
        self._refresh(node)
        self._refresh(child)
        return child


def _inorder[T](node: _Node[T] | None, keys: list[T]) -> None:
    if node is None:
        return
    _inorder(node.left, keys)
    keys.append(node.key)
    _inorder(node.right, keys)


def _valid[T](node: _Node[T] | None, lower: _Node[T] | None, upper: _Node[T] | None) -> bool:
    if node is None:
        return True
    if node.height != 1 + max(_height(node.left), _height(node.right)):
        return False
    if abs(_height(node.left) - _height(node.right)) > 1:
        return False
    if lower is not None and not (lower.key < node.key):
        return False
    if upper is not None and not (node.key < upper.key):
        return False
    return _valid(node.left, lower, node) and _valid(node.right, node, upper)


def _count[T](node: _Node[T] | None) -> int:
    if node is None:
        return 0
    return 1 + _count(node.left) + _count(node.right)


def maximum_avl_height(node_count: int) -> int:
    """Return the largest height an AVL tree with ``node_count`` nodes can have.

    Height uses the same convention as ``AVLTree.height``: empty is -1 and a
    leaf is 0. ``N(h) = 1 + N(h - 1) + N(h - 2)`` is the fewest nodes that can
    produce height ``h``.
    """
    if node_count < 0:
        raise ValueError("node_count must be nonnegative")
    if node_count == 0:
        return -1
    shortest_previous = 0  # N(-1), the empty tree
    shortest_current = 1  # N(0), a single leaf
    height = 0
    while True:
        shortest_next = 1 + shortest_current + shortest_previous
        if shortest_next > node_count:
            return height
        shortest_previous = shortest_current
        shortest_current = shortest_next
        height += 1

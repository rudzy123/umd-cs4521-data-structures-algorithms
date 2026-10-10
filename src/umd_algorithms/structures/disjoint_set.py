"""Disjoint-set union with path compression and union by rank.

Invariant
    Parent pointers form trees. A root is its own parent and is the
    representative of its component. ``find`` returns that root and makes
    every node on the walked path point directly at it (path compression).

    ``union`` links the root with smaller rank under the root with larger
    rank. Equal ranks link the second root under the first and then increment
    the surviving root's rank. Rank is therefore an upper bound on tree height
    *before* compression; compression shortens paths and does not reduce rank.

Complexity
    A sequence of ``m`` ``find`` and ``union`` operations on ``n`` elements
    takes Θ(m α(n)) time, where ``α`` is the inverse Ackermann function.
    α(n) is at most 4 for every ``n`` that can be stored in the observable
    universe, so the operations are constant time for every practical input.
    This bound is amortized over the sequence: one ``find`` can still walk a
    short path, and later finds on that path are cheaper because of compression.
    Space is Θ(n).

``connected`` is an equivalence relation on the elements that have been added:
reflexive, symmetric, and transitive.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterable


class DisjointSet[T: Hashable]:
    """Partition of hashable elements, grown by explicit insertion and union."""

    def __init__(self, elements: Iterable[T] = ()) -> None:
        self._parent: dict[T, T] = {}
        self._rank: dict[T, int] = {}
        for element in elements:
            self.add(element)

    def __len__(self) -> int:
        return len(self._parent)

    def __contains__(self, element: object) -> bool:
        return element in self._parent

    def add(self, element: T) -> None:
        """Add ``element`` as a singleton. Adding it again is a no-op."""
        if isinstance(element, float) and math.isnan(element):
            raise ValueError("NaN is not a valid element")
        if element not in self._parent:
            self._parent[element] = element
            self._rank[element] = 0

    def find(self, element: T) -> T:
        """Return the representative of ``element`` and compress its path."""
        parent = self._parent.get(element)
        if parent is None:
            raise KeyError(element)
        if parent != element:
            self._parent[element] = self.find(parent)
        return self._parent[element]

    def union(self, left: T, right: T) -> bool:
        """Merge the components of ``left`` and ``right``.

        Return ``True`` when two components become one, and ``False`` when
        both elements were already in the same component.
        """
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return False
        rank_left = self._rank[root_left]
        rank_right = self._rank[root_right]
        if rank_left < rank_right:
            self._parent[root_left] = root_right
        elif rank_right < rank_left:
            self._parent[root_right] = root_left
        else:
            self._parent[root_right] = root_left
            self._rank[root_left] = rank_left + 1
        return True

    def connected(self, left: T, right: T) -> bool:
        """Return whether ``left`` and ``right`` have the same representative."""
        return self.find(left) == self.find(right)

    def component_count(self) -> int:
        """Return the number of components. Does not compress paths. Θ(n)."""
        return sum(1 for element, parent in self._parent.items() if element == parent)

    def parent_pointer(self, element: T) -> T:
        """Return the current parent of ``element`` without compressing.

        After ``find(element)``, this equals the representative. A node that
        ``find`` did not walk can still point at an intermediate parent.
        """
        if element not in self._parent:
            raise KeyError(element)
        return self._parent[element]

    def stored_rank(self, element: T) -> int:
        """Return the rank stored at ``element`` itself, not at its root."""
        if element not in self._rank:
            raise KeyError(element)
        return self._rank[element]

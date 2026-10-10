"""Directed and undirected graphs stored as adjacency lists.

Representation
    Each vertex maps to a list of ``(neighbor, weight)`` pairs in the order
    edges were inserted. An undirected edge is stored once in ``edges()`` and
    in both adjacency lists, except a self-loop, which is stored once.
    Parallel edges are kept; nothing silently overwrites an earlier weight.

Invariant
    Every endpoint of an edge is a vertex. ``directed`` does not change after
    construction. Weights are finite ints or floats. Booleans are rejected
    because ``bool`` is a subclass of ``int``.

Complexity
    ``add_vertex`` and ``add_edge`` are Θ(1) amortized (list append and dict
    insert). ``neighbors`` copies the adjacency list, so it is Θ(degree).
    ``vertices`` is Θ(V) and ``edges`` is Θ(E). Space is Θ(V + E).

Vertex insertion order is preserved, and neighbor order is insertion order.
Graph algorithms in this package use those orders as their deterministic
tie breaks.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterable


class Graph[T: Hashable]:
    """Adjacency-list graph. Construct with ``directed=True`` or ``directed=False``."""

    def __init__(self, *, directed: bool = False) -> None:
        self._directed = directed
        self._adjacency: dict[T, list[tuple[T, float]]] = {}
        self._edges: list[tuple[T, T, float]] = []

    def __contains__(self, vertex: object) -> bool:
        return vertex in self._adjacency

    def __len__(self) -> int:
        """Return the number of vertices."""
        return len(self._adjacency)

    def __repr__(self) -> str:
        kind = "directed" if self._directed else "undirected"
        return f"Graph({kind}, vertices={self.vertices()}, edges={self.edges()})"

    @property
    def directed(self) -> bool:
        return self._directed

    def add_vertex(self, vertex: T) -> None:
        """Add an isolated vertex. Adding an existing vertex is a no-op."""
        if vertex not in self._adjacency:
            self._adjacency[vertex] = []

    def add_vertices(self, vertices: Iterable[T]) -> None:
        for vertex in vertices:
            self.add_vertex(vertex)

    def add_edge(self, source: T, target: T, weight: float = 1.0) -> None:
        """Add an edge and create any missing endpoint.

        Undirected edges record ``(source, target, weight)`` in the order
        given here. The opposite adjacency entry is added when the edge is
        not a self-loop.
        """
        checked = _validate_weight(weight)
        self.add_vertex(source)
        self.add_vertex(target)
        self._adjacency[source].append((target, checked))
        if not self._directed and source != target:
            self._adjacency[target].append((source, checked))
        self._edges.append((source, target, checked))

    def neighbors(self, vertex: T) -> list[tuple[T, float]]:
        """Return a copy of ``(neighbor, weight)`` pairs in insertion order."""
        self._require_vertex(vertex)
        return list(self._adjacency[vertex])

    def vertices(self) -> list[T]:
        """Return vertices in insertion order."""
        return list(self._adjacency)

    def edges(self) -> list[tuple[T, T, float]]:
        """Return edges in insertion order.

        An undirected edge appears once, oriented as it was passed to
        ``add_edge``. A directed edge appears once, from source to target.
        """
        return list(self._edges)

    def _require_vertex(self, vertex: T) -> None:
        if vertex not in self._adjacency:
            raise KeyError(vertex)


def _validate_weight(weight: float) -> float:
    if isinstance(weight, bool) or not isinstance(weight, int | float):
        raise TypeError("edge weight must be an int or float")
    numeric = float(weight)
    if not math.isfinite(numeric):
        raise ValueError("edge weight must be finite")
    return numeric

"""Breadth-first search, depth-first search, topological sort, Dijkstra, and Kruskal.

The queue below is a singly linked list so both ends are Θ(1) in the worst
case. ``list.pop(0)`` would be Θ(n) and would make BFS Θ(V²) on a path, which
would make the complexity claims false.
"""

from __future__ import annotations

import math
from collections.abc import Hashable

from umd_algorithms.algorithms.sorting import merge_sort
from umd_algorithms.exceptions import CycleError
from umd_algorithms.structures.disjoint_set import DisjointSet
from umd_algorithms.structures.graph import Graph
from umd_algorithms.structures.min_heap import MinHeap


class _QueueNode[T]:
    __slots__ = ("next", "value")

    def __init__(self, value: T) -> None:
        self.value = value
        self.next: _QueueNode[T] | None = None


class _Queue[T]:
    """FIFO linked queue. ``append`` and ``popleft`` are Θ(1)."""

    def __init__(self) -> None:
        self._head: _QueueNode[T] | None = None
        self._tail: _QueueNode[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def append(self, value: T) -> None:
        node = _QueueNode(value)
        if self._tail is None:
            self._head = node
            self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def popleft(self) -> T:
        node = self._head
        if node is None:
            raise IndexError("pop from empty queue")
        self._head = node.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return node.value


class ShortestPaths[T: Hashable]:
    """Distances and predecessor links produced by Dijkstra's algorithm.

    ``distance[v]`` is ``math.inf`` when ``v`` is not reachable from ``source``.
    ``predecessor`` records the vertex that last improved the distance, which
    is enough to rebuild one shortest path.
    """

    def __init__(
        self,
        source: T,
        distance: dict[T, float],
        predecessor: dict[T, T],
    ) -> None:
        self.source = source
        self.distance = distance
        self.predecessor = predecessor

    def path_to(self, target: T) -> list[T]:
        """Return one shortest path from the source to ``target``.

        Raise ``KeyError`` when ``target`` is not a vertex and ``ValueError``
        when no finite path exists.
        """
        if target not in self.distance:
            raise KeyError(target)
        if math.isinf(self.distance[target]):
            raise ValueError(f"no path from {self.source!r} to {target!r}")
        path = [target]
        while path[-1] != self.source:
            current = path[-1]
            if current not in self.predecessor:
                raise ValueError("predecessor chain is broken")
            path.append(self.predecessor[current])
        path.reverse()
        return path


def breadth_first_search[T: Hashable](graph: Graph[T], start: T) -> list[T]:
    """Return vertices reachable from ``start``, closest vertices first.

    Neighbor lists are scanned in insertion order, so the order inside one
    distance layer follows the order edges were added.

    Invariant: the queue holds vertices whose hop distances differ by at most
    one, and the first time a vertex is enqueued is along a shortest path in
    number of edges. Each reachable vertex and each edge out of a reachable
    vertex is processed once, so the time is Θ(V_r + E_r) for the reachable
    component. Disconnected vertices are left unvisited.
    """
    if start not in graph:
        raise KeyError(start)
    visited = {start}
    order: list[T] = []
    queue: _Queue[T] = _Queue()
    queue.append(start)
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor, _weight in graph.neighbors(vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def depth_first_search[T: Hashable](graph: Graph[T], start: T) -> list[T]:
    """Return a preorder of the depth-first forest grown from ``start``.

    The walk is iterative. Neighbors are pushed right to left so the first
    inserted neighbor is explored first, matching the usual recursive loop.
    Each reachable vertex is visited once. Time is Θ(V_r + E_r). Vertices in
    other components are omitted. Cycles are cut by the visited set.
    """
    if start not in graph:
        raise KeyError(start)
    visited: set[T] = set()
    order: list[T] = []
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex in visited:
            continue
        visited.add(vertex)
        order.append(vertex)
        neighbors = [neighbor for neighbor, _weight in graph.neighbors(vertex)]
        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def topological_sort[T: Hashable](graph: Graph[T]) -> list[T]:
    """Return a topological order of a directed acyclic graph.

    Kahn's algorithm repeatedly removes a vertex of indegree 0. Among vertices
    that become ready at the same time, the earlier one in vertex insertion
    order (for the initial queue) or in neighbor insertion order (for later
    queues) is emitted first. The order is therefore deterministic, and it is
    one of possibly many topological orders.

    Time and extra space are Θ(V + E). A self-loop or any longer directed
    cycle leaves at least one vertex unemitted; that raises ``CycleError``.
    An undirected graph raises ``ValueError`` because "directed edge" is part
    of the problem statement, not something the algorithm can invent.
    Disconnected vertices are included.
    """
    if not graph.directed:
        raise ValueError("topological sort requires a directed graph")
    indegree = dict.fromkeys(graph.vertices(), 0)
    for _source, target, _weight in graph.edges():
        indegree[target] += 1
    queue: _Queue[T] = _Queue()
    for vertex, degree in indegree.items():
        if degree == 0:
            queue.append(vertex)
    order: list[T] = []
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor, _weight in graph.neighbors(vertex):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(indegree):
        raise CycleError("graph contains a directed cycle")
    return order


def dijkstra[T: Hashable](graph: Graph[T], source: T) -> ShortestPaths[T]:
    """Compute single-source shortest paths for nonnegative edge weights.

    The search is the usual greedy algorithm: the unsettled vertex with the
    smallest tentative distance is finalized, then its outgoing edges relax
    their heads. A binary min-heap stores tentative distances. Decrease-key
    is replaced by inserting a new pair; a stale pair is ignored when its
    vertex is already finalized. Because a simple graph has ``E <= V²``,
    ``log E`` is Θ(log V), and the heap work is O((V + E) log V).

    The implementation also scans every edge before searching, so a graph
    with no edges still takes Θ(V) time and any negative weight is rejected
    even when that edge is not reachable from ``source``. Nonnegative weights
    are a property of the instance, not of one source. The error is
    ``ValueError``.

    Greedy finalization is sound only while every edge weight is ``>= 0``.
    A negative edge could improve a vertex after the algorithm has already
    treated its distance as finished, so the result would no longer be a
    shortest-path tree.

    Zero-weight edges and zero-weight cycles are allowed. Unreachable vertices
    keep distance ``math.inf`` and have no predecessor.
    """
    if source not in graph:
        raise KeyError(source)
    _reject_negative_edges(graph)
    distance = {vertex: math.inf for vertex in graph.vertices()}
    distance[source] = 0.0
    predecessor: dict[T, T] = {}
    heap: MinHeap[tuple[float, int, T]] = MinHeap()
    ticket = 0
    heap.push((0.0, ticket, source))
    settled: set[T] = set()
    while heap:
        tentative, _ticket, vertex = heap.pop()
        if vertex in settled or tentative > distance[vertex]:
            continue
        settled.add(vertex)
        for neighbor, weight in graph.neighbors(vertex):
            candidate = distance[vertex] + weight
            if candidate < distance[neighbor]:
                distance[neighbor] = candidate
                predecessor[neighbor] = vertex
                ticket += 1
                heap.push((candidate, ticket, neighbor))
    return ShortestPaths(source, distance, predecessor)


def kruskal[T: Hashable](graph: Graph[T]) -> list[tuple[T, T, float]]:
    """Return a minimum spanning forest as edges in the order they were accepted.

    The algorithm is greedy. Edges are ordered by nondecreasing weight with
    this repository's merge sort, using the original index as a tie break so
    vertex objects never need to be ordered. An edge is accepted exactly when
    its endpoints lie in different components of the forest built so far.
    Union by rank and path compression perform that test.

    The accepted edges are acyclic. On a connected graph they form a minimum
    spanning tree with ``V - 1`` edges. On a disconnected graph they form a
    minimum spanning forest with ``V - C`` edges, where ``C`` is the number of
    connected components. Negative weights are allowed and are preferred,
    because a lighter edge is still safe to add when it joins two components.
    Self-loops are rejected by the union step.

    Time is Θ(E log E + V) because of the sort, plus the nearly constant
    disjoint-set work. Space is Θ(V + E). A directed graph raises
    ``ValueError``; spanning trees in this sense are undirected.
    """
    if graph.directed:
        raise ValueError("Kruskal's algorithm requires an undirected graph")
    edges = graph.edges()
    order = merge_sort([(edge[2], index) for index, edge in enumerate(edges)])
    components: DisjointSet[T] = DisjointSet(graph.vertices())
    forest: list[tuple[T, T, float]] = []
    for _weight, index in order:
        source, target, weight = edges[index]
        if components.union(source, target):
            forest.append((source, target, weight))
    return forest


def _reject_negative_edges[T: Hashable](graph: Graph[T]) -> None:
    connector = "->" if graph.directed else "--"
    for source, target, weight in graph.edges():
        if weight < 0:
            raise ValueError(
                "Dijkstra requires nonnegative edge weights; "
                f"found {source} {connector} {target} with weight {weight}"
            )

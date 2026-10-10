"""Traversals, cycle detection, Dijkstra's precondition, and spanning forests."""

import math
from itertools import combinations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import (
    CycleError,
    DisjointSet,
    Graph,
    breadth_first_search,
    depth_first_search,
    dijkstra,
    kruskal,
    topological_sort,
)


class Box:
    """Hashable vertex that does not implement ordering."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Box) and self.name == other.name

    def __repr__(self) -> str:
        return self.name


def test_bfs_and_dfs_orders_and_directed_edges() -> None:
    star = Graph[int]()
    for leaf in range(1, 5):
        star.add_edge(0, leaf)
    assert breadth_first_search(star, 0) == [0, 1, 2, 3, 4]

    directed = Graph[int](directed=True)
    directed.add_edge(0, 1)
    directed.add_edge(0, 2)
    directed.add_edge(1, 3)
    assert depth_first_search(directed, 0) == [0, 1, 3, 2]
    assert breadth_first_search(directed, 0) == [0, 1, 2, 3]
    assert depth_first_search(directed, 2) == [2]


def test_disconnected_graph_stays_in_the_start_component() -> None:
    graph = Graph[int]()
    graph.add_edge(0, 1)
    graph.add_edge(2, 3)
    graph.add_vertex(4)
    assert breadth_first_search(graph, 0) == [0, 1]
    assert set(depth_first_search(graph, 2)) == {2, 3}
    assert breadth_first_search(graph, 4) == [4]


def test_cycles_do_not_make_traversals_loop() -> None:
    undirected = Graph[int]()
    undirected.add_edge(0, 1)
    undirected.add_edge(1, 2)
    undirected.add_edge(2, 0)
    assert set(breadth_first_search(undirected, 0)) == {0, 1, 2}
    assert len(depth_first_search(undirected, 0)) == 3

    directed = Graph[int](directed=True)
    directed.add_edge(0, 1)
    directed.add_edge(1, 0)
    assert set(depth_first_search(directed, 0)) == {0, 1}


def test_empty_and_missing_start() -> None:
    empty = Graph[int](directed=True)
    assert topological_sort(empty) == []
    assert kruskal(Graph[int]()) == []
    with pytest.raises(KeyError):
        breadth_first_search(empty, 0)
    with pytest.raises(KeyError):
        depth_first_search(Graph[int](), 0)
    with pytest.raises(KeyError):
        dijkstra(Graph[int](), 0)


def test_topological_order_on_a_disconnected_dag() -> None:
    graph = Graph[str](directed=True)
    graph.add_edge("a", "c")
    graph.add_edge("b", "c")
    graph.add_edge("c", "d")
    graph.add_vertex("e")
    order = topological_sort(graph)
    # a, b, and the isolated vertex e start with indegree 0, in insertion order.
    # c becomes ready only after both of its incoming edges are removed.
    assert order == ["a", "b", "e", "c", "d"]
    position = {vertex: index for index, vertex in enumerate(order)}
    for source, target, _weight in graph.edges():
        assert position[source] < position[target]


def test_topological_sort_detects_cycles_and_rejects_undirected_graphs() -> None:
    cycle = Graph[int](directed=True)
    cycle.add_edge(0, 1)
    cycle.add_edge(1, 2)
    cycle.add_edge(2, 0)
    with pytest.raises(CycleError, match="cycle"):
        topological_sort(cycle)

    loop = Graph[int](directed=True)
    loop.add_edge(1, 1)
    with pytest.raises(CycleError):
        topological_sort(loop)

    undirected = Graph[int]()
    undirected.add_edge(0, 1)
    with pytest.raises(ValueError, match="directed") as caught:
        topological_sort(undirected)
    assert not isinstance(caught.value, CycleError)


def test_dijkstra_path_and_unreachable_vertex() -> None:
    graph = Graph[str](directed=True)
    graph.add_edge("s", "a", 1)
    graph.add_edge("s", "b", 4)
    graph.add_edge("a", "b", 1)
    graph.add_vertex("z")
    result = dijkstra(graph, "s")
    assert result.distance["s"] == 0
    assert result.distance["b"] == 2
    assert result.path_to("b") == ["s", "a", "b"]
    assert math.isinf(result.distance["z"])
    with pytest.raises(ValueError, match="no path"):
        result.path_to("z")
    assert result.path_to("s") == ["s"]


def test_dijkstra_rejects_negative_edges_even_when_unreachable() -> None:
    graph = Graph[int](directed=True)
    graph.add_edge(0, 1, 1)
    graph.add_edge(2, 3, -1)
    with pytest.raises(ValueError, match="nonnegative"):
        dijkstra(graph, 0)

    undirected = Graph[int]()
    undirected.add_edge(0, 1, -0.5)
    with pytest.raises(ValueError, match="nonnegative"):
        dijkstra(undirected, 0)


def test_dijkstra_allows_zero_weights_and_unordered_vertices() -> None:
    start = Box("start")
    left = Box("left")
    right = Box("right")
    graph = Graph[Box](directed=True)
    graph.add_edge(start, left, 2)
    graph.add_edge(start, right, 2)
    graph.add_edge(left, right, 0)
    result = dijkstra(graph, start)
    assert result.distance[left] == 2
    assert result.distance[right] == 2
    assert result.path_to(left)[0] is start


def test_kruskal_tree_forest_negatives_and_parallel_edges() -> None:
    tree = Graph[int]()
    tree.add_edge(0, 1, 4)
    tree.add_edge(1, 2, 1)
    tree.add_edge(0, 2, 3)
    assert kruskal(tree) == [(1, 2, 1.0), (0, 2, 3.0)]

    forest = Graph[int]()
    forest.add_edge(0, 1, 1)
    forest.add_edge(1, 2, 2)
    forest.add_edge(0, 2, 4)
    forest.add_edge(3, 4, 5)
    edges = kruskal(forest)
    assert len(edges) == 3
    assert sum(weight for _source, _target, weight in edges) == 8

    negative = Graph[int]()
    negative.add_edge(0, 1, -5)
    negative.add_edge(1, 2, 1)
    negative.add_edge(0, 2, 4)
    assert kruskal(negative) == [(0, 1, -5.0), (1, 2, 1.0)]

    parallel = Graph[int]()
    parallel.add_edge(0, 1, 5)
    parallel.add_edge(0, 1, 1)
    chosen = kruskal(parallel)
    assert len(chosen) == 1
    assert chosen[0][2] == 1

    boxes = Graph[Box]()
    a, b, c = Box("a"), Box("b"), Box("c")
    boxes.add_edge(a, b, 3)
    boxes.add_edge(b, c, 1)
    boxes.add_edge(a, c, 2)
    accepted = kruskal(boxes)
    assert [weight for _source, _target, weight in accepted] == [1.0, 2.0]

    with pytest.raises(ValueError, match="undirected"):
        kruskal(Graph[int](directed=True))


def _bellman_ford(graph: Graph[int], source: int) -> dict[int, float]:
    distance = {vertex: math.inf for vertex in graph.vertices()}
    distance[source] = 0.0
    for _ in range(max(len(graph) - 1, 0)):
        changed = False
        for vertex in graph.vertices():
            if math.isinf(distance[vertex]):
                continue
            for neighbor, weight in graph.neighbors(vertex):
                candidate = distance[vertex] + weight
                if candidate < distance[neighbor]:
                    distance[neighbor] = candidate
                    changed = True
        if not changed:
            break
    return distance


def _forest_weight(graph: Graph[int]) -> float:
    vertices = graph.vertices()
    edges = graph.edges()
    components = DisjointSet(vertices)
    for source, target, _weight in edges:
        components.union(source, target)
    needed = len(vertices) - components.component_count()
    if needed == 0:
        return 0.0
    best = math.inf
    for chosen in combinations(range(len(edges)), needed):
        subset = DisjointSet(vertices)
        weight = 0.0
        acyclic = True
        for index in chosen:
            source, target, edge_weight = edges[index]
            if not subset.union(source, target):
                acyclic = False
                break
            weight += edge_weight
        if acyclic:
            best = min(best, weight)
    return best


@st.composite
def _small_graphs(draw: st.DrawFn) -> tuple[Graph[int], bool]:
    count = draw(st.integers(1, 6))
    directed = draw(st.booleans())
    graph = Graph[int](directed=directed)
    graph.add_vertices(range(count))
    for _ in range(draw(st.integers(0, 10))):
        graph.add_edge(
            draw(st.integers(0, count - 1)),
            draw(st.integers(0, count - 1)),
            draw(st.integers(0, 9)),
        )
    return graph, directed


@given(_small_graphs())
def test_random_graphs(case: tuple[Graph[int], bool]) -> None:
    graph, directed = case
    start = 0
    breadth = breadth_first_search(graph, start)
    depth = depth_first_search(graph, start)
    assert set(breadth) == set(depth)
    assert len(breadth) == len(set(breadth))

    distance = {start: 0}
    frontier = [start]
    head = 0
    while head < len(frontier):
        vertex = frontier[head]
        head += 1
        for neighbor, _weight in graph.neighbors(vertex):
            if neighbor not in distance:
                distance[neighbor] = distance[vertex] + 1
                frontier.append(neighbor)
    levels = [distance[vertex] for vertex in breadth]
    assert levels == sorted(levels)

    paths = dijkstra(graph, start)
    assert paths.distance == _bellman_ford(graph, start)
    for vertex in graph.vertices():
        if math.isinf(paths.distance[vertex]):
            with pytest.raises(ValueError):
                paths.path_to(vertex)
            continue
        path = paths.path_to(vertex)
        assert path[0] == start
        assert path[-1] == vertex
        for left, right in zip(path, path[1:], strict=False):
            difference = paths.distance[right] - paths.distance[left]
            assert any(
                neighbor == right and weight == difference
                for neighbor, weight in graph.neighbors(left)
            )

    if not directed:
        accepted = kruskal(graph)
        assert sum(weight for _source, _target, weight in accepted) == _forest_weight(graph)
        forest = DisjointSet(graph.vertices())
        for source, target, _weight in accepted:
            assert forest.union(source, target) is True


@given(st.integers(1, 8), st.lists(st.tuples(st.integers(0, 7), st.integers(0, 7)), max_size=12))
def test_dag_topological_order(count: int, forward_edges: list[tuple[int, int]]) -> None:
    graph = Graph[int](directed=True)
    graph.add_vertices(range(count))
    for source, target in forward_edges:
        if source < target < count:
            graph.add_edge(source, target)
    order = topological_sort(graph)
    assert set(order) == set(range(count))
    position = {vertex: index for index, vertex in enumerate(order)}
    for source, target, _weight in graph.edges():
        assert position[source] < position[target]


def test_adding_a_back_edge_creates_a_detected_cycle() -> None:
    graph = Graph[int](directed=True)
    graph.add_edge(0, 1)
    graph.add_edge(1, 2)
    graph.add_edge(2, 0)
    with pytest.raises(CycleError):
        topological_sort(graph)

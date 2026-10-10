"""Adjacency-list graph representation."""

import math

import pytest

from umd_algorithms import Graph


def test_undirected_edge_is_stored_once_and_linked_both_ways() -> None:
    graph = Graph[str]()
    graph.add_edge("u", "v", 2)
    assert graph.directed is False
    assert graph.vertices() == ["u", "v"]
    assert len(graph) == 2
    assert graph.neighbors("u") == [("v", 2.0)]
    assert graph.neighbors("v") == [("u", 2.0)]
    assert graph.edges() == [("u", "v", 2.0)]
    assert "u" in graph
    assert "missing" not in graph


def test_directed_edge_does_not_create_the_reverse() -> None:
    graph = Graph[str](directed=True)
    graph.add_edge("u", "v")
    assert graph.neighbors("u") == [("v", 1.0)]
    assert graph.neighbors("v") == []
    assert graph.edges() == [("u", "v", 1.0)]


def test_isolated_vertices_parallel_edges_and_self_loops() -> None:
    graph = Graph[int]()
    graph.add_vertex(5)
    graph.add_vertices([5, 6])
    graph.add_edge(5, 5, 3)
    graph.add_edge(5, 6, 1)
    graph.add_edge(5, 6, 4)
    assert graph.vertices() == [5, 6]
    assert graph.neighbors(5) == [(5, 3.0), (6, 1.0), (6, 4.0)]
    # The self-loop is not mirrored, and each undirected edge is stored once.
    assert graph.edges() == [(5, 5, 3.0), (5, 6, 1.0), (5, 6, 4.0)]
    assert graph.neighbors(6) == [(5, 1.0), (5, 4.0)]


def test_empty_graph() -> None:
    graph = Graph[int](directed=True)
    assert graph.vertices() == []
    assert graph.edges() == []
    assert len(graph) == 0
    with pytest.raises(KeyError):
        graph.neighbors(1)


def test_weight_validation() -> None:
    graph = Graph[int]()
    with pytest.raises(TypeError):
        graph.add_edge(0, 1, True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite"):
        graph.add_edge(0, 1, math.inf)
    with pytest.raises(ValueError, match="finite"):
        graph.add_edge(0, 1, math.nan)


def test_callers_cannot_mutate_internal_lists() -> None:
    graph = Graph[int]()
    graph.add_edge(0, 1, 1)
    graph.neighbors(0).append((2, 9.0))
    graph.edges().clear()
    graph.vertices().append(3)
    assert graph.neighbors(0) == [(1, 1.0)]
    assert graph.edges() == [(0, 1, 1.0)]
    assert graph.vertices() == [0, 1]

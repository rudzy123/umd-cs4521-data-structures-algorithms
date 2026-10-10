"""Importing the public package surface."""

import umd_algorithms
from umd_algorithms import (
    AVLTree,
    BinarySearchTree,
    CycleError,
    DisjointSet,
    Graph,
    HashTable,
    MinHeap,
    ShortestPaths,
    binary_search,
    breadth_first_search,
    counting_sort,
    depth_first_search,
    dijkstra,
    heap_sort,
    knapsack_01,
    kruskal,
    longest_common_subsequence,
    merge_sort,
    quicksort,
    topological_sort,
)


def test_public_names_are_exported() -> None:
    exported = [
        AVLTree,
        BinarySearchTree,
        CycleError,
        DisjointSet,
        Graph,
        HashTable,
        MinHeap,
        ShortestPaths,
        binary_search,
        breadth_first_search,
        counting_sort,
        depth_first_search,
        dijkstra,
        heap_sort,
        knapsack_01,
        kruskal,
        longest_common_subsequence,
        merge_sort,
        quicksort,
        topological_sort,
    ]
    assert umd_algorithms.__version__ == "1.0.0"
    for name in exported:
        assert name.__name__ in umd_algorithms.__all__

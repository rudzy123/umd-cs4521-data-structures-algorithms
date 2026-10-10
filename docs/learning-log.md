# Learning log

Date: 2026-10-10

This log records the design choices in the lab and the checks that justify them. Each entry is something that is easy to get wrong if the only definition available is a one-line complexity claim.

## A balanced tree is a height bound, not a different search rule

Inserting keys in sorted order makes the binary search tree a chain. Search, insert, and delete become Θ(n), and the recursion uses Θ(n) stack. The AVL tree uses the same `<` comparisons. The extra rule is local: every balance factor stays in `{-1, 0, 1}`, restored by one rotation or two. The Fibonacci recurrence `N(h) = 1 + N(h - 1) + N(h - 2)` is what turns that local rule into `h = Θ(log n)`.

The test that caught a bad rotation is small. Three sorted insertions must end at height 1. A tree that forgets the rotation has height 2, which is already above `maximum_avl_height(3)`.

`height()` on the BST walks every node, so it is Θ(n). `height()` on the AVL tree reads a stored field, so it is Θ(1). Same name, different cost, because only one of them maintains the field the rotations need.

## A heap is the right structure when the only query is the minimum

The min-heap invariant is weaker than the BST invariant. Children are larger than their parent, and the two children are unordered. That is enough to keep the minimum at index 0, and it is not enough to binary-search an arbitrary key. `heapify` is Θ(n) because the sifts near the leaves are short. Building the same heap by pushing one key at a time is Θ(n log n). The classmethod exists so that difference stays visible.

Heapsort uses the same shape with the comparison reversed and never calls `MinHeap`. The in-place index arithmetic is the algorithm. When every key is equal, each sift-down stops at once and the sort is Θ(n). Distinct keys pay Θ(n log n). That is a real best case, and it is still not a stable sort.

## Chaining is the hash table; `hash()` is only the bucket function

The table is a list of lists. `hash(key) % capacity` chooses the list, and `==` walks it. A negative hash is still a valid index because Python's remainder with a positive modulus is nonnegative. That is a portability note: the same formula in C can produce a negative index.

Growth doubles the bucket array and rehashes every entry. One doubling is not always enough when `max_load_factor * capacity < 1`, so `put` keeps doubling until `size <= max_load_factor * capacity`. Across a sequence of insertions the copying sums to Θ(n), which is the amortized bound. A single `put` can still be Θ(n). Deletion does not shrink the table; shrinking at the same threshold would rehash forever on a workload that oscillates around it.

Expected Θ(1) assumes chains stay short. It is not a worst-case promise. The collision test pins capacity at 2, raises the load cap so the table cannot hide behind a resize, and checks the pigeonhole principle: 8 keys in 2 buckets force some chain to have length at least 4.

## The queue has to be Θ(1) or the BFS bound is false

`list.pop(0)` moves every later element. On a path graph that would make BFS quadratic while the textbook still says Θ(V + E). The traversals use a linked FIFO whose `append` and `popleft` are Θ(1) in the worst case, including when the vertex itself is `None`. The complexity claim in the docstring is then the complexity of the code.

## Dijkstra's precondition is a property of the graph

The dangerous case is a negative edge that is not even reachable from the source. If the algorithm ignored it, a later edit that starts at a different vertex would silently become wrong. The implementation scans every edge and raises `ValueError` on the first negative weight. Zero is allowed. A zero-weight cycle does not improve a settled distance, so the search still terminates.

The heap stores `(distance, ticket, vertex)`. The ticket is unique, so two vertices with the same distance never need to be compared. Vertices therefore do not have to be ordered, only hashable.

The reason the greedy step works: when a vertex is settled, every unsettled path still has to enter the settled set across some edge, and a nonnegative edge cannot undercut the distance already chosen. A negative edge can. That is the whole separation from Bellman-Ford.

## Kruskal may accept a negative edge, and it must survive a disconnected graph

Sorting edges by weight and adding an edge when its endpoints are in different components is safe for negative weights. The lightest safe edge is still safe when it is negative. The tests include a negative edge that belongs in the forest and a heavier edge that closes a cycle.

A disconnected graph has no spanning tree. The same loop returns a minimum spanning forest with `V - C` edges. The test oracle enumerates acyclic subsets of that size on graphs small enough to brute force, so the weight check does not depend on Kruskal to grade Kruskal.

Edge order is this repository's merge sort on `(weight, insertion index)`. The index tie break means vertex objects are never asked to be ordered. A `Box` vertex with `__hash__` and `__eq__` and no `__lt__` still gets a correct forest.

## Topological sort fails by counting, not by throwing on the first back edge

Kahn's algorithm emits a vertex only at indegree 0. A cycle, including a self-loop, leaves at least one vertex unemitted. The algorithm finishes the scan and then raises `CycleError`. An undirected graph is a different error: the problem statement asks for a directed acyclic graph, so the function raises `ValueError` before it looks for a cycle.

Disconnected DAGs are valid. Every isolated vertex starts in the queue. The deterministic order is insertion order among the vertices that are ready, which is why an isolated vertex can appear before a vertex that is still waiting on an incoming edge.

## This quicksort is supposed to look bad on sorted input

The pivot is the last element. On a sorted array the partition peels off one key and recurses on `n - 1` keys. Reverse-sorted input does the same, so those two columns are the Θ(n²) demonstration. Lomuto's handling of equals sends them all to the left. The duplicate-heavy column draws every key from `0 .. 4`, which makes splits uneven; the all-equal input is the extreme and is also Θ(n²). The benchmark checks `result == sorted(values)` and then prints milliseconds. A timing assertion would fail because the machine is busy, which is not an algorithms failure.

The recursive form can exceed Python's recursion limit on a long worst-case chain. The benchmark raises the limit for the process. The docstring records that a production sort would randomize the pivot or switch to heap sort at a depth bound. Hiding that behind `sorted()` would delete the lesson.

## Counting sort buys its speed with a constraint

The comparison-sort lower bound says some inputs force Ω(n log n) comparisons. Counting sort does not compare keys. It indexes an array of counters, so every key must be an integer in `0 .. k`, and the Θ(k) memory has to be acceptable. Booleans are rejected because `bool` is a subclass of `int` in Python; `True` would otherwise sort as 1 and hide a type error.

Stability is the right-to-left scan into the cumulative counts. The tests carry an `Item` whose order is only its integer key and whose label remembers the input position. Merge sort and counting sort keep those labels in the same order as Python's stable `sorted`. That is an observable stability test, not a comment.

## Dynamic programming is the fallback when the greedy choice is unsafe

The knapsack test with weights `(2, 3)`, values `(3, 4)`, and capacity 3 is the decision procedure in miniature. Value density picks the first item and scores 3. The optimum scores 4 by taking only the second item. LCS has the same shape of overlapping subproblems: the match case and the two skip cases share prefixes, so the table stores them once. Both reconstructions are deterministic about ties, and the tests check feasibility and optimality rather than one lucky item list.

## What the property tests are for

Unit tests pin the small cases: a rotation, a two-child deletion, a negative edge, a self-loop, an empty input. Property tests generate the cases those examples miss.

- Trees: random insertions and deletions, then inorder equals the sorted survivors, and the AVL height stays inside an independently coded Fibonacci bound.
- Heap and sorts: the output equals `sorted`.
- Hash table: the table agrees with a `dict` under overwrites and deletions, and `is_valid` holds after each step.
- Disjoint set: connectivity agrees with a parent-array oracle that does not use union by rank. Rank and compression have their own hand-built tree.
- Dijkstra: distances agree with Bellman-Ford, and each predecessor hop is a real edge of that length.
- Kruskal: on small graphs the forest weight agrees with an enumeration of acyclic edge sets.
- LCS and knapsack: the result is feasible and matches a recursive or brute-force optimum.

The benchmark is not in that list. Correctness belongs in pytest. Timings belong in `python -m benchmarks.sort_bench`.

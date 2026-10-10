# Invariants

An invariant is a statement that is true after every public operation. The tests call `is_valid` where a structure can check itself, and they also check observable consequences (sorted order, optimal value, connectivity) that do not trust that checker alone.

Height conventions used below: an empty tree has height -1, and a leaf has height 0.

## Binary search tree

For every node `x`:

- every key in the left subtree is `< x.key`
- every key in the right subtree is `> x.key`
- `len(tree)` equals the number of nodes

An inorder walk is therefore strictly increasing. Equal keys are rejected, so the inequalities are strict. `search`, `insert`, and `delete` walk one root-to-leaf path and use Θ(h) stack space. Nothing in this structure limits `h`.

## AVL tree

The binary-search-tree invariant holds, and for every node:

- the stored height equals `1 + max(height(left), height(right))`
- the balance factor `height(left) - height(right)` is `-1`, `0`, or `1`

A single rotation repairs a straight imbalance (left-left or right-right). A double rotation repairs a bent imbalance (left-right or right-left). After deletion, a child whose balance factor is 0 is repaired with one rotation.

The fewest nodes in an AVL tree of height `h` is `N(h) = 1 + N(h - 1) + N(h - 2)`, with `N(0) = 1` and `N(-1) = 0`. That Fibonacci recurrence is why `h` is Θ(log n), at most about `1.44 log2(n)`. `maximum_avl_height` computes the bound. `height()` reads the stored root height and is Θ(1).

## Min-heap

The array is a complete binary tree, packed left to right.

- parent of `i` is `(i - 1) // 2`
- left child of `i` is `2i + 1`
- right child of `i` is `2i + 2`
- for every `i > 0`, `data[parent(i)] <= data[i]`

The minimum, when the heap is nonempty, is at index 0. Comparisons use `<` only. `heapify` sifts down from the last parent and builds the same invariant in Θ(n) time.

## Hash table

Separate chaining:

- key `k` is stored in bucket `hash(k) % capacity`
- Python's `%` with a positive modulus is nonnegative, so a negative hash is still a legal index
- each key appears in exactly one pair
- `__len__` equals the number of stored pairs
- `size <= max_load_factor * capacity` after every public operation

A replacement does not change the size. Deletion does not shrink the table, so the load factor may fall well below the cap; the cap is an upper bound. Keys must obey the usual contract: if `a == b`, then `hash(a) == hash(b)`. `NaN` is rejected because it is not equal to itself.

## Graph

- `directed` is fixed at construction
- every endpoint of an edge is a vertex
- a directed edge appears once in `edges()` and once in the source adjacency list
- an undirected edge appears once in `edges()`, oriented as passed to `add_edge`, and in both adjacency lists, except a self-loop, which appears once
- parallel edges are preserved
- weights are finite ints or floats; booleans are rejected
- vertex order and neighbor order are insertion order, and the graph algorithms use that order as their tie break

## Disjoint set

- parent pointers form trees; a root is its own parent
- `find(x)` returns the root of `x` and points every node on that path at the root
- `union` links the smaller-rank root under the larger-rank root
- when the ranks are equal, the second root is linked under the first and the surviving root's rank increases by 1
- rank is an upper bound on height before compression; compression does not decrease rank
- `connected` is reflexive, symmetric, and transitive on the elements that have been added

`parent_pointer` and `stored_rank` report the current arrays without compressing. They exist so the compression and rank rules can be observed directly.

## Sorting

Merge: the output is sorted, and equal keys keep their input order because the merge takes the left run when `right[j] < left[i]` is false.

Quicksort, after Lomuto partition on the last element: the pivot is in its final index, every earlier element is `<=` the pivot, and every later element is `>` the pivot. Equal keys gather on the left. The algorithm may reorder equal keys.

Heapsort: after the max-heap is built, the growing suffix `values[end + 1:]` is sorted, and the extracted maximum placed at `end` is `>=` every key still in the heap. Equal keys may be reordered.

Counting sort: keys are integers in `0 .. maximum`. After the prefix sums, `counts[v]` is the number of keys `<= v`. Filling from the right end of the input places an earlier equal key in an earlier slot.

Every public sort returns a new list and leaves the caller's sequence unchanged.

## Binary search

Precondition: the sequence is sorted nondecreasing under `<`. The algorithm does not scan the sequence to check that. While the search runs, if `target` occurs at all, it occurs inside `values[low : high + 1]`. An empty slice means `target` is absent. Any matching index is a correct answer when duplicates exist.

## Breadth-first and depth-first search

BFS: a vertex is enqueued the first time it is seen, and that first visit is a minimum-hop path from the start. The queue's hop distances differ by at most one. Each reachable vertex appears once. Vertices outside the start component are omitted.

DFS: each reachable vertex is visited once, in preorder. Neighbors are pushed right to left so the first inserted neighbor is explored first. The visited set cuts cycles.

## Topological sort

The output is a total order of every vertex such that each directed edge `u -> v` has `u` before `v`. Kahn's algorithm removes indegree-0 vertices. The initial queue follows vertex insertion order. Later vertices enter the queue in neighbor insertion order. If any vertex remains, the graph has a directed cycle and the algorithm raises `CycleError`. An undirected graph raises `ValueError`.

## Dijkstra

Before the search, every edge weight in the graph is `>= 0`. A negative weight raises `ValueError` even when the edge cannot be reached from the source.

Once a vertex is removed from the heap and settled, its distance is final. That greedy step needs nonnegative weights: a later negative edge could otherwise improve a settled vertex. `distance[v]` is the length of a shortest path from the source, or `math.inf` when none exists. Each predecessor link is an edge that realized the stored distance, so `path_to` rebuilds one shortest path. Zero-weight edges are allowed.

## Kruskal

The accepted edges form a forest. An edge is accepted exactly when its endpoints are in different components. On a connected undirected graph the result is a minimum spanning tree with `V - 1` edges. On a disconnected graph it is a minimum spanning forest with `V - C` edges. Edge order is nondecreasing weight, with the original insertion index breaking ties, produced by this repository's merge sort. Negative weights are safe and are preferred. A directed graph raises `ValueError`.

## Longest common subsequence

`dp[i][j]` is the length of an LCS of `left[:i]` and `right[:j]`. A match extends the diagonal. A mismatch takes the larger of the cell above and the cell to the left. The returned string is a common subsequence of that optimal length. When the two mismatch choices are equal, reconstruction skips a character of `left`.

## 0/1 knapsack

`dp[i][c]` is the maximum value using the first `i` items and capacity `c`. Item `i - 1` is either skipped, or taken when its weight fits, on top of the best packing of the earlier items in the remaining capacity. The returned indexes are increasing, feasible, and achieve `dp[n][W]`. A cell that does not change is treated as a skip, so a zero-value item is not selected.

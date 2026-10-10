# Choosing a structure or an algorithm

Start from the question the caller asks, then from the operation that dominates, then from the shape of the data. A structure that makes one operation Θ(1) usually makes another operation more expensive.

## Data structures

| You need | Use | Why | Look elsewhere when |
| --- | --- | --- | --- |
| Ordered unique keys, and inputs arrive in random order | Binary search tree | Expected Θ(log n) search, insert, and delete, and inorder is the sorted order | Insertions are sorted or adversarial. The tree becomes a chain and every operation becomes Θ(n) |
| Ordered unique keys, and the cost must be logarithmic in every case | AVL tree | The same ordered-set operations with height Θ(log n). `height()` is Θ(1) | You only pop the minimum, or you only test membership. The rotations are wasted work |
| Repeatedly remove the smallest key | Min-heap | `peek` is Θ(1), `pop` is Θ(log n), and Floyd's `heapify` is Θ(n). Duplicate keys are allowed | You need to find an arbitrary key, or you need the keys in order without removing them |
| Membership and lookup by an exact key | Hash table with separate chaining | Expected Θ(1) `get`, `put`, and `delete` | You need sorted order, range queries, or a worst-case guarantee. One bucket can hold every key, which is Θ(n). Adversarial keys also belong here as a risk |
| Relationships, paths, or traversal | Adjacency-list graph | Θ(1) edge insertion and Θ(V + E) space. Directed and undirected graphs share one representation | The graph is tiny and dense and you mostly ask "is there an edge?". A matrix answers that in Θ(1) and uses Θ(V²) space. This repository teaches the list form |
| Merge groups, or test whether two elements are in the same group | Disjoint set with path compression and union by rank | Amortized Θ(α(n)) `find` and `union`, which is constant for every practical n | You need the actual path, the edge that joined two vertices, or a delete-from-component operation |

Concrete contrasts inside this repository:

- Inserting `1 .. n` in order into `BinarySearchTree` produces height `n - 1`. The same keys in `AVLTree` stay inside the Fibonacci height bound.
- A heap finds the minimum quickly and does not help you search for an arbitrary key. A tree does the opposite trade.
- A hash table overwrites a duplicate key. A BST rejects it. They are different contracts, not two implementations of one idea.
- Kruskal needs a disjoint set because the question is "are these endpoints already connected?", asked once per edge. Dijkstra needs a heap because the question is "which unsettled vertex is closest?".

## Sorting

| Shape of the data | Sort | Reason |
| --- | --- | --- |
| Need a predictable Θ(n log n) bound and equal keys must keep their order | Merge sort | Stable. The bound does not depend on input order. It allocates Θ(n) extra memory, and this version does not get faster on an already sorted list |
| Average case on random distinct keys, and extra memory must stay small | Quicksort | Expected Θ(n log n) and expected Θ(log n) stack. This last-element Lomuto pivot is Θ(n²) on sorted input, reverse-sorted input, and all-equal input |
| Need in-place Θ(n log n) that ignores input order | Heap sort | Working memory Θ(1). Distinct keys are Θ(n log n) in every typical case. Equal keys may be reordered. The all-equal input is Θ(n) |
| Nonnegative integers in a small range `0 .. k` | Counting sort | Θ(n + k) and stable. This is legal because the keys are integers, so the Ω(n log n) comparison lower bound does not apply. Large `k`, negatives, and non-integers are outside the contract |

CPython's `sorted` (Timsort) is a useful clock in the benchmark and is not one of the teaching implementations. It is stable and adaptive: a sorted list is Θ(n). Our merge sort does not have that shortcut, so the benchmark's presorted column is a real comparison of algorithms, not a race the teaching code is expected to win.

## Graph problems

| Question | Algorithm | Required shape |
| --- | --- | --- |
| Visit a component one hop-layer at a time | BFS | Directed or undirected. Unweighted. Other components stay unvisited |
| Visit a component depth first | DFS | Directed or undirected. Cycles are cut by the visited set |
| Order tasks so every prerequisite comes first | Topological sort | Directed acyclic graph. A cycle raises `CycleError`. Undirected input raises `ValueError` |
| Shortest path when every weight is `>= 0` | Dijkstra | Directed or undirected. Any negative weight raises `ValueError`, including an unreachable one. Zero weights are allowed |
| Connect every vertex at minimum total weight | Kruskal | Undirected. A disconnected graph yields a minimum spanning forest. Negative weights are allowed and are preferred |

BFS is the shortest-path algorithm when every edge has the same positive cost, because hop count is then the distance. Dijkstra is the generalization to unequal nonnegative weights. A negative edge breaks the reason Dijkstra can settle a vertex forever; that instance belongs to Bellman-Ford or a different problem, which this repository intentionally does not solve.

## Greedy or dynamic programming

Use the greedy algorithm when a locally best choice can be proved safe for the global optimum.

- Dijkstra settles the unsettled vertex with the smallest tentative distance. Nonnegative weights make that choice safe.
- Kruskal adds the lightest edge that joins two components. The cycle property makes that choice safe, including when the lightest edge is negative.

Use dynamic programming when a solution is built from overlapping smaller solutions and a greedy choice is not safe.

- Longest common subsequence tries a match, or a skip in either string, and stores both so the same prefixes are solved once.
- 0/1 knapsack tries taking an item or leaving it, for every capacity. The fractional rule "take the best value per unit weight" fails here. Items `(weight 2, value 3)` and `(weight 3, value 4)` with capacity 3 are the counterexample: the denser item is worth 3, and the other item alone is worth 4. `knapsack_01` returns 4.

Knapsack's Θ(nW) table is pseudo-polynomial. It is the right algorithm when `W` is moderate. It is the wrong algorithm when `W` has hundreds of bits, even if `n` is small.

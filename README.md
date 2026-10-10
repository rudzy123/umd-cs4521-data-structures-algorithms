# UMD CS 4521 — Data Structures and Algorithms

Teaching implementations of the core structures and algorithms, written so the
mechanism stays on the page. Trees rotate themselves, the hash table is a list
of chains, Dijkstra uses the min-heap in this repository, and Kruskal orders
its edges with this repository's merge sort. The code does not call `dict` to
implement a map, `heapq` to implement a heap, `bisect` to implement binary
search, or `sorted` to implement a sort. `sorted` appears only as the test
oracle and as the Timsort column in the benchmark.

Python 3.12. Tests are pytest and Hypothesis. Style is Ruff. The pipeline is
GitHub Actions.

## Build, test, and benchmark

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check src tests benchmarks
ruff format --check src tests benchmarks
pytest
python -m benchmarks.sort_bench --smoke
python -m benchmarks.sort_bench
```

`pytest` runs the unit tests and the property tests. `--smoke` runs every
sort on four small inputs, checks each result against `sorted`, and prints
one timing sample. The full benchmark uses sizes 500 and 2000, three repeats,
and seed 4521. Both commands exit nonzero when a sort is wrong. Neither
command treats a duration as pass or fail.

```bash
python -m benchmarks.sort_bench --seed 4521 --sizes 500 2000 --repeats 3
```

Import the library with `import umd_algorithms` or from the modules under
`src/umd_algorithms`.

## Asymptotic notation

Let `f` and `g` be functions from input size to cost (comparisons, assignments,
or words of memory).

**Big-O** is an upper bound. `f(n)` is `O(g(n))` when there exist constants
`c > 0` and `n0` such that `f(n) <= c · g(n)` for every `n >= n0`. The bound
may be loose: `3n + 5` is `O(n)` and also `O(n²)`.

**Big-Omega** is a lower bound. `f(n)` is `Ω(g(n))` when `f(n) >= c · g(n)`
for every large `n`. `3n + 5` is `Ω(n)` and also `Ω(1)`.

**Big-Theta** is both. `f(n)` is `Θ(g(n))` when it is `O(g(n))` and
`Ω(g(n))`. `3n + 5` is `Θ(n)`. Use Θ when this implementation's leading term
is pinned down. Dijkstra's binary-heap bound below is written `O((V + E) log V)`
because an easy graph does less heap work than that expression, while the
expression still covers the worst graph.

Comparison sorts have an `Ω(n log n)` worst-case lower bound: some family of
inputs forces that many comparisons. Merge sort and heap sort meet it.
Counting sort is faster only because its keys are integers in a bounded
range, so it is not a comparison sort.

## Best, average, and worst case

These words describe *which input* of size `n` you measured. They are not
synonyms for Ω, Θ, and O. A worst-case cost can itself be `Θ(n log n)`.

- **Best case:** the cheapest input of that size.
- **Worst case:** the most expensive input of that size.
- **Average case:** the expected cost over a stated distribution. Unless a
  row says otherwise, the distribution is uniform over permutations, or
  simple uniform hashing for the hash table.

Examples from this code:

- Binary search is `Θ(1)` when the first midpoint is the target and `Θ(log n)`
  on every other successful or failed search. The sequence must already be
  sorted. The function does not spend a linear scan checking that.
- Unbalanced BST search is `Θ(1)` at the root, `Θ(log n)` after random
  insertions, and `Θ(n)` after inserting keys in sorted order.
- This quicksort's average on a random permutation is `Θ(n log n)`, because
  the last element is then a uniform random pivot. Sorted and reverse-sorted
  input force `Θ(n²)`.
- Heap sort is `Θ(n)` when every sift-down stops immediately, which includes
  the all-equal input, and `Θ(n log n)` for distinct keys.
- This merge sort is `Θ(n log n)` on sorted input too. It does not look for
  already-sorted runs. Timsort does, which is why the benchmark's presorted
  Timsort column is in a different class.

## Amortized analysis

An amortized bound is the cost of a *sequence* of operations divided by the
length of the sequence, and the sequence is chosen adversarially. One call
may be expensive. The expensive calls are rare enough that the average over
the sequence stays small. This is not an average over random input.

**Hash table growth.** Inserting into a full-enough table allocates a bucket
array of twice the capacity and rehashes every key. One `put` is then `Θ(n)`.
Across `n` insertions the copied lengths form a geometric series
`1 + 2 + 4 + ... + n`, which sums to `Θ(n)`. Each insertion is therefore
`Θ(1)` amortized, times the expected cost of walking a chain. Deletion does
not shrink the table. Shrinking at the same threshold would rehash on every
oscillation around the load factor.

If `max_load_factor * capacity < 1`, one doubling still leaves a single key
over the cap, so `put` keeps doubling until the cap holds.

**Disjoint set.** Path compression and union by rank make any sequence of
`m` `find` and `union` operations `Θ(m α(n))`. `α`, the inverse Ackermann
function, is at most 4 for every `n` that fits in the observable universe, so
the operations are constant time in practice. The bound is amortized: one
`find` may walk a short path, and compression makes the next `find` on that
path cheaper. Rank is an upper bound on height *before* compression.
Compression shortens paths and does not reduce rank.

**Expected is a different word.** A hash-table lookup is expected `Θ(1)`
because of the hash function, and a resizing insertion is amortized `Θ(1)`
because of the geometric series. A heap `push` of a random key stops after an
expected constant number of swaps; its worst case is still `Θ(log n)`. That
expectation is over the key, not over a sequence of forced resizes.

## Stability and in-place sorting

A sort is **stable** when equal keys keep the relative order they had in the
input. Merge sort is stable because a tie takes the left run
(`right[j] < left[i]` is false). Counting sort is stable because cumulative
counts are filled from the right end of the input, so an earlier equal key
lands in an earlier slot. Quicksort and heap sort may reorder equal keys.

**In-place** means the algorithm's working memory is `Θ(1)` beyond the array
it rearranges. Every public function in this repository first copies its
input, so the caller's list is unchanged and the copy itself is `Θ(n)`. The
column below is the memory used *after* that copy. Quicksort's recursion
stack is `Θ(log n)` on average and `Θ(n)` in the worst case, so the in-place
claim for quicksort excludes that stack. Heap sort's working memory is `Θ(1)`.

| Algorithm | Stable | Working memory after the input copy | In-place |
| --- | --- | --- | --- |
| Merge sort | yes | `Θ(n)` | no |
| Quicksort | no | `Θ(log n)` expected stack, `Θ(n)` worst | aside from the stack |
| Heap sort | no | `Θ(1)` | yes |
| Counting sort | yes | `Θ(n + k)` | no |

Counting sort accepts only nonnegative integers in `0 .. maximum`. Booleans
are rejected (`bool` is a subclass of `int`). Negatives, floats, and a key
above `maximum` are rejected. Omit `maximum` and it is the largest key.
Time and space are `Θ(n + k)` with `k = maximum`. The optional `key`
function exists so an object can carry its identity through that integer
sort; the counting and placement steps are still the integer algorithm.

## Choosing a data structure

Pick the structure from the question that dominates, then check the worst
input you are willing to accept.

| Question | Structure | Cost to remember | Walk away when |
| --- | --- | --- | --- |
| Is this key present, and can I list the keys in order? | BST | Expected `Θ(log n)` if insertions are random | Keys arrive sorted or from an adversary. Height becomes `n - 1` |
| Same question, and the bound must hold for every insertion order | AVL | `Θ(log n)` search, insert, and delete. `height()` is `Θ(1)` | The only query is "remove the minimum" |
| Remove the smallest key, repeatedly | Min-heap | `peek` `Θ(1)`, `pop` `Θ(log n)`, `heapify` `Θ(n)` | You must find an arbitrary key |
| Look up an exact key | Hash table, separate chaining | Expected `Θ(1)`, worst `Θ(n)` | You need order, range queries, or a hard worst case |
| Store a relationship and walk it | Adjacency-list graph | `Θ(V + E)` space, `Θ(1)` edge insertion | You only ask "is `(u, v)` present?" on a dense graph |
| Are these two elements in the same group after a series of merges? | Disjoint set | Amortized `Θ(α(n))` | You need the path or the edge that connected them |

The same keys make the contrast concrete. Inserting `1 .. n` in order makes
`BinarySearchTree` a chain. `AVLTree` keeps those keys inside the Fibonacci
height bound `N(h) = 1 + N(h - 1) + N(h - 2)`. A heap answers a weaker
question than either tree and answers it faster. A hash table overwrites a
duplicate key; a tree rejects it.

`docs/algorithm-selection.md` extends this table to the sorts and the graph
algorithms.

## Greedy algorithms and dynamic programming

A **greedy** algorithm locks in a locally best choice and never reconsiders
it. That is correct only when the choice can be proved safe.

- **Dijkstra** settles the unsettled vertex with the smallest tentative
  distance. Nonnegative weights make the choice safe: a later edge cannot
  undercut a settled vertex. A negative weight, even on an unreachable edge,
  raises `ValueError`. Zero-weight edges are allowed.
- **Kruskal** adds the lightest edge that joins two different components.
  The cycle property makes that choice safe, including when the lightest
  edge is negative. A disconnected undirected graph produces a minimum
  spanning forest with `V - C` edges. A directed graph raises `ValueError`.

**Dynamic programming** fills a table of smaller answers that overlap. Use it
when a greedy choice is unsafe and the same subproblem would otherwise be
solved many times.

- **Longest common subsequence.** `dp[i][j]` is the LCS length of the
  prefixes `left[:i]` and `right[:j]`. A match extends the diagonal. A
  mismatch takes the better of the cell above and the cell to the left.
  Time and space are `Θ(mn)`, or `Θ(1)` when either string is empty. The
  returned string is one optimal subsequence; equal choices skip a character
  of `left`.
- **0/1 knapsack.** `dp[i][c]` is the best value using the first `i` items
  and capacity `c`. Each item is taken once or not at all. Time and space
  are `Θ(nW)`, which is pseudo-polynomial: polynomial in the number `W`, not
  in the number of bits of `W`.

The fractional rule "take the best value per unit weight" solves a different
problem. For items `(weight 2, value 3)` and `(weight 3, value 4)` with
capacity 3, that rule scores 3 and the optimum scores 4. `knapsack_01`
returns `(4, [1])`.

## Complexity

`n` is the number of elements. `h` is height (empty tree `-1`, leaf `0`).
`k` is the maximum counting-sort key. `V` and `E` are vertices and edges.
`V_r` and `E_r` are the reachable component. `m` and `n` in the LCS row are
the string lengths. `W` is knapsack capacity. `α` is the inverse Ackermann
function. The same tables, with less prose, are in
[`docs/complexity-cheat-sheet.md`](docs/complexity-cheat-sheet.md).
Invariants are in [`docs/invariants.md`](docs/invariants.md).

### Structures

| Structure | Operation | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- | --- |
| BST | search | Θ(1) | Θ(log n) | Θ(n) | Θ(h) stack |
| BST | insert, delete | Θ(1) | Θ(log n) | Θ(n) | Θ(h) stack |
| BST | minimum, maximum | Θ(1) | Θ(log n) | Θ(n) | Θ(1) |
| BST | inorder | Θ(n) | Θ(n) | Θ(n) | Θ(h) stack |
| BST | height | Θ(n) | Θ(n) | Θ(n) | Θ(h) stack |
| AVL | search | Θ(1) | Θ(log n) | Θ(log n) | Θ(1) |
| AVL | insert, delete | Θ(log n) | Θ(log n) | Θ(log n) | Θ(log n) stack |
| AVL | minimum, maximum | Θ(1) | Θ(log n) | Θ(log n) | Θ(1) |
| AVL | height | Θ(1) | Θ(1) | Θ(1) | Θ(1) |
| AVL | inorder | Θ(n) | Θ(n) | Θ(n) | Θ(log n) stack |
| Min-heap | peek | Θ(1) | Θ(1) | Θ(1) | Θ(1) |
| Min-heap | push | Θ(1) | Θ(1) expected | Θ(log n) | Θ(1) |
| Min-heap | pop | Θ(1) | Θ(log n) | Θ(log n) | Θ(1) |
| Min-heap | heapify | Θ(n) | Θ(n) | Θ(n) | Θ(1) |
| Hash table | get, put, delete | Θ(1) | Θ(1) expected | Θ(n) | Θ(1) |
| Hash table | put, with growth | Θ(1) amortized expected | Θ(1) amortized expected | Θ(n) | Θ(n) |
| Graph | add vertex, add edge | Θ(1) | Θ(1) | Θ(1) amortized | Θ(1) |
| Graph | neighbors | Θ(degree) | Θ(degree) | Θ(degree) | Θ(degree) |
| Graph | vertices / edges | Θ(V) / Θ(E) | Θ(V) / Θ(E) | Θ(V) / Θ(E) | Θ(V) / Θ(E) |
| Disjoint set | find, union, connected | Θ(α(n)) amortized | Θ(α(n)) amortized | Θ(α(n)) amortized | Θ(1) |
| Disjoint set | component count | Θ(n) | Θ(n) | Θ(n) | Θ(1) |

Stored size is `Θ(n)` for the trees, the heap, and the disjoint set, `Θ(n)`
buckets for the hash table after growth, and `Θ(V + E)` for the graph.

### Sorting

| Algorithm | Best | Average | Worst | Stable | In-place |
| --- | --- | --- | --- | --- | --- |
| Merge sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | yes | no |
| Quicksort, last pivot, Lomuto | Θ(n log n) | Θ(n log n) | Θ(n²) | no | aside from the stack |
| Heap sort | Θ(n) | Θ(n log n) | Θ(n log n) | no | yes |
| Counting sort | Θ(n + k) | Θ(n + k) | Θ(n + k) | yes | no |

### Graph algorithms, search, and dynamic programming

| Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- |
| Binary search | Θ(1) | Θ(log n) | Θ(log n) | Θ(1) |
| BFS, DFS | Θ(V_r + E_r) | Θ(V_r + E_r) | Θ(V_r + E_r) | Θ(V_r) |
| Topological sort | Θ(V + E) | Θ(V + E) | Θ(V + E) | Θ(V + E) |
| Dijkstra, this binary heap | Θ(V + E) | O((V + E) log V) | O((V + E) log V) | O(V + E) |
| Kruskal | Θ(V) when E = 0 | Θ(E log E + V) | Θ(E log E + V) | Θ(V + E) |
| Longest common subsequence | Θ(1) if either string is empty | Θ(mn) | Θ(mn) | Θ(mn) |
| 0/1 knapsack | Θ(1) if there are no items | Θ(nW) | Θ(nW) | Θ(nW) |

BFS and DFS leave other components unvisited. Topological sort includes
every vertex of a directed acyclic graph and raises `CycleError` when a
directed cycle, including a self-loop, exists. Dijkstra initializes every
vertex and scans every edge before searching, which is why a negative edge
in another component is rejected and why the best case is still `Θ(V + E)`.
The heap stores `(distance, ticket, vertex)` so vertices do not need to be
ordered. Kruskal's `Θ(E log E)` term is the merge sort of the edges.

## Layout

```text
.
├── .github/workflows/ci.yml
├── benchmarks/sort_bench.py
├── docs/
│   ├── algorithm-selection.md
│   ├── complexity-cheat-sheet.md
│   ├── invariants.md
│   └── learning-log.md
├── src/umd_algorithms/
│   ├── structures/     BST, AVL, min-heap, hash table, graph, disjoint set
│   └── algorithms/     sorts, binary search, graph algorithms, DP
├── tests/
├── pyproject.toml
└── README.md
```

Each module docstring states the invariant and the complexity before the
code. `docs/learning-log.md` records why those choices were made, including
the cases the property tests are there to catch.

## Tests

The suite checks the contracts above directly.

- Every sort is compared with `sorted` on empty input, duplicates, sorted
  input, and reverse-sorted input. Merge sort and counting sort are also
  checked for stability.
- BST and AVL insertions and deletions must leave an inorder walk equal to
  the sorted survivors. AVL height must stay inside an independently coded
  Fibonacci bound. The sorted-insertion BST must be a chain.
- Heap pops must match `sorted`, and `is_valid` must hold after every push.
- The hash table must agree with a `dict` under overwrites and deletions,
  including after resize, and a two-bucket table must show a long chain.
- Graph tests cover an empty graph, a disconnected graph, directed and
  undirected edges, parallel edges, self-loops, and cycles that must not
  make BFS or DFS loop.
- Topological sort must order a disconnected DAG and raise `CycleError` on
  a cycle and on a self-loop.
- Dijkstra must reject a negative edge that the source cannot reach, and its
  distances must match a Bellman-Ford oracle. Predecessor hops must be real
  edges of that length.
- Kruskal's forest weight on small graphs must match an enumeration of
  acyclic edge sets. Negative edges that connect components must be kept.
- LCS results must be common subsequences of optimal length. Knapsack
  results must be feasible and match brute force, including the density
  counterexample.

Hypothesis draws the random cases (40 examples, fixed seed). The hand-written
tests pin the rotations, the deletion shapes, and the error types.

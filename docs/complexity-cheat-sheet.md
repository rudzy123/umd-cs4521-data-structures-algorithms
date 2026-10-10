# Complexity cheat sheet

`n` is the number of elements. `h` is tree height (empty = -1, leaf = 0). `k` is the maximum counting-sort key. `V` and `E` are vertices and edges. `m` and `n` are the two string lengths in LCS. `W` is knapsack capacity. `α` is the inverse Ackermann function.

Θ means a tight bound. O in the Dijkstra row is an upper bound for this binary-heap implementation. "Expected" means a random hash or a random key. "Amortized" means the worst-case cost of a sequence, divided by the length of that sequence.

## Data structures

| Structure | Operation | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- | --- |
| BST | search | Θ(1) | Θ(log n) expected height | Θ(n) | Θ(h) stack |
| BST | insert | Θ(1) | Θ(log n) | Θ(n) | Θ(h) stack |
| BST | delete | Θ(1) | Θ(log n) | Θ(n) | Θ(h) stack |
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
| Hash table | put, including growth | Θ(1) | Θ(1) expected amortized | Θ(n) | Θ(n) |
| Graph | add vertex, add edge | Θ(1) | Θ(1) | Θ(1) amortized | Θ(1) |
| Graph | neighbors | Θ(degree) | Θ(degree) | Θ(degree) | Θ(degree) copy |
| Graph | vertices, edges | Θ(V), Θ(E) | Θ(V), Θ(E) | Θ(V), Θ(E) | Θ(V), Θ(E) |
| Disjoint set | find, union, connected | Θ(α(n)) amortized | Θ(α(n)) amortized | Θ(α(n)) amortized | Θ(1) |
| Disjoint set | component count | Θ(n) | Θ(n) | Θ(n) | Θ(1) |

Structure space: BST, AVL, heap, and disjoint set use Θ(n). The hash table uses Θ(n) buckets after growth. The graph uses Θ(V + E).

## Sorting

The public functions copy their input, so the caller is unchanged. The extra-space column is the memory the algorithm uses beyond that copy. In-place means that working memory is Θ(1), ignoring the output list.

| Algorithm | Best | Average | Worst | Working space | Stable | In-place |
| --- | --- | --- | --- | --- | --- | --- |
| Merge sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | Θ(n) | yes | no |
| Quicksort (last pivot, Lomuto) | Θ(n log n) | Θ(n log n) | Θ(n²) | Θ(n) stack worst, Θ(log n) expected | no | aside from the stack |
| Heap sort | Θ(n) | Θ(n log n) | Θ(n log n) | Θ(1) | no | yes |
| Counting sort | Θ(n + k) | Θ(n + k) | Θ(n + k) | Θ(n + k) | yes | no |

Heap sort's linear best case includes the all-equal input: every sift-down stops immediately. Distinct keys cost Θ(n log n).

Quicksort's average assumes a random permutation, which makes the last element a uniform pivot. Sorted input, reverse-sorted input, and long runs of equal keys are Θ(n²) for this partition. The benchmark's duplicate-heavy column draws keys from `0 .. 4`.

Counting sort is defined only for nonnegative integers in `0 .. k`. It is not a comparison sort.

## Searching and graph algorithms

| Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- |
| Binary search | Θ(1) | Θ(log n) | Θ(log n) | Θ(1) |
| BFS, DFS | Θ(V_r + E_r) | Θ(V_r + E_r) | Θ(V_r + E_r) | Θ(V_r) |
| Topological sort | Θ(V + E) | Θ(V + E) | Θ(V + E) | Θ(V + E) |
| Dijkstra (this binary heap) | Θ(V + E) | O((V + E) log V) | O((V + E) log V) | O(V + E) |
| Kruskal | Θ(V) when E = 0 | Θ(E log E + V) | Θ(E log E + V) | Θ(V + E) |

`V_r` and `E_r` are the vertices and edges reachable from the start. BFS and DFS leave other components alone. Topological sort, Dijkstra, and Kruskal look at the whole graph. Dijkstra's best case still initializes every vertex and scans every edge so it can reject a negative weight.

## Dynamic programming

| Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- |
| LCS | Θ(1) if either string is empty | Θ(mn) | Θ(mn) | Θ(mn) |
| 0/1 knapsack | Θ(1) if there are no items | Θ(nW) | Θ(nW) | Θ(nW) |

Knapsack is pseudo-polynomial: Θ(nW) is polynomial in the number `W`, not in the bits of `W`.

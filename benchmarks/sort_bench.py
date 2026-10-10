"""Reproducible timings for the sorting implementations.

The script prints median milliseconds. It checks that every algorithm matches
``sorted`` and then exits 0. It does not assert anything about the timings:
machine noise would make a duration check fail for reasons that have nothing
to do with correctness.

Quicksort in this repository pivots on the last element and partitions with
Lomuto's scheme. Sorted and reverse-sorted input make every partition peel off
one key, which is the Θ(n²) case. Duplicate-heavy input draws keys from
``0 .. 4``; equal keys all go to the left of the pivot, so those partitions
are lopsided too. Merge sort stays Θ(n log n) and does not speed up on sorted
input. Counting sort is Θ(n + k) and likes this small ``k``. Heap sort stays
Θ(n log n) on distinct keys. ``sorted`` is CPython's Timsort, included only
as a reference clock.

Run from the repository root:

    python -m benchmarks.sort_bench --smoke
    python -m benchmarks.sort_bench
    python -m benchmarks.sort_bench --seed 4521 --sizes 500 2000 --repeats 3
"""

from __future__ import annotations

import argparse
import platform
import random
import sys
import time
from collections.abc import Callable, Sequence

from umd_algorithms import counting_sort, heap_sort, merge_sort, quicksort

Algorithm = Callable[[Sequence[int]], list[int]]

ALGORITHMS: tuple[tuple[str, Algorithm], ...] = (
    ("merge_sort", merge_sort),
    ("quicksort", quicksort),
    ("heap_sort", heap_sort),
    ("counting_sort", counting_sort),
    ("timsort", sorted),
)


def _datasets(size: int, seed: int) -> dict[str, list[int]]:
    generator = random.Random(seed)
    # Five distinct keys. Lomuto partition places every key that is <= the
    # pivot on its left, so this alphabet makes duplicate-heavy splits uneven.
    return {
        "random": [generator.randrange(size) for _ in range(size)],
        "presorted": list(range(size)),
        "reverse_sorted": list(range(size - 1, -1, -1)),
        "duplicate_heavy": [generator.randrange(5) for _ in range(size)],
    }


def _median(samples: list[float]) -> float:
    ordered = sorted(samples)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _time_algorithm(algorithm: Algorithm, values: list[int], repeats: int) -> float:
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        algorithm(values)
        samples.append(time.perf_counter() - started)
    return _median(samples)


def run(sizes: list[int], repeats: int, seed: int) -> None:
    if not sizes or any(size < 0 for size in sizes) or repeats < 1:
        raise SystemExit("sizes must be nonnegative and repeats must be positive")
    limit = max(sys.getrecursionlimit(), max(sizes, default=0) + 50)
    sys.setrecursionlimit(limit)
    print(
        f"python {platform.python_version()}  "
        f"implementation {platform.python_implementation()}  seed {seed}"
    )
    print(
        "Quicksort pivots on the last element. Presorted and reverse-sorted "
        "inputs are quadratic; duplicate-heavy keys are drawn from 0..4."
    )
    header = f"{'pattern':<18}{'n':>8}" + "".join(f"{name:>16}" for name, _algorithm in ALGORITHMS)
    print(header)
    print("-" * len(header))
    for size in sizes:
        for pattern, values in _datasets(size, seed + size).items():
            expected = sorted(values)
            durations: list[str] = []
            for name, algorithm in ALGORITHMS:
                copied = list(values)
                result = algorithm(copied)
                if result != expected:
                    raise SystemExit(f"{name} failed on {pattern} n={size}")
                if copied != values:
                    raise SystemExit(f"{name} mutated its input")
                milliseconds = _time_algorithm(algorithm, values, repeats) * 1000
                durations.append(f"{milliseconds:16.3f}")
            print(f"{pattern:<18}{size:8d}{''.join(durations)}")
    print("times are median milliseconds and are not a pass/fail check")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="small default size and one repeat, for CI and a sanity check",
    )
    parser.add_argument("--seed", type=int, default=4521)
    parser.add_argument("--sizes", type=int, nargs="*", default=None)
    parser.add_argument("--repeats", type=int, default=None)
    args = parser.parse_args(argv)
    if args.smoke:
        sizes = args.sizes or [128]
        repeats = args.repeats or 1
    else:
        sizes = args.sizes or [500, 2000]
        repeats = args.repeats or 3
    run(sizes, repeats, args.seed)


if __name__ == "__main__":
    main()

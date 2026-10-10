"""Hash table with separate chaining.

Bucket selection calls the key's own ``__hash__`` through ``hash(key)`` and
reduces it with ``hash(key) % capacity``. Python's remainder is nonnegative
for a positive modulus, so a negative hash still lands inside the table.
Each bucket is an explicit list of ``(key, value)`` pairs. Lookup walks that
list with ``==``. This class does not store its entries in a ``dict``.

Invariant
    Every stored key ``k`` lives in bucket ``hash(k) % capacity``, each key
    appears once, ``__len__`` equals the number of stored pairs, and after
    every public operation ``size <= max_load_factor * capacity``.

Complexity
    Under simple uniform hashing a chain has expected constant length, so
    ``get``, ``put``, and ``delete`` are expected Θ(1). One unlucky bucket
    can hold every key, which is Θ(n). A resize copies every entry and is
    Θ(n), but doubling makes a sequence of ``n`` insertions Θ(n) altogether,
    so each insertion is amortized expected Θ(1).

    Deletion does not shrink the table. Oscillating around the load threshold
    would otherwise rehash on every other update.

``max_load_factor`` may be larger than 1 when a caller wants long chains on
purpose (collision demonstrations). The default is 0.75.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterator


class HashTable[K: Hashable, V]:
    """Map from hashable keys to values, resolved by separate chaining."""

    def __init__(self, capacity: int = 8, max_load_factor: float = 0.75) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        if (
            isinstance(max_load_factor, bool)
            or not isinstance(max_load_factor, int | float)
            or not math.isfinite(float(max_load_factor))
            or float(max_load_factor) <= 0
        ):
            raise ValueError("max_load_factor must be a finite number greater than 0")
        self._max_load_factor = float(max_load_factor)
        self._buckets: list[list[tuple[K, V]]] = [[] for _ in range(capacity)]
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        try:
            index = hash(key) % len(self._buckets)
        except TypeError:
            return False
        return any(stored == key for stored, _value in self._buckets[index])

    def __getitem__(self, key: K) -> V:
        return self.get(key)

    def __setitem__(self, key: K, value: V) -> None:
        self.put(key, value)

    def __delitem__(self, key: K) -> None:
        self.delete(key)

    def __iter__(self) -> Iterator[K]:
        for chain in self._buckets:
            for key, _value in chain:
                yield key

    def __repr__(self) -> str:
        return f"HashTable({self.items()})"

    @property
    def bucket_count(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / len(self._buckets)

    @property
    def max_load_factor(self) -> float:
        return self._max_load_factor

    def chain_lengths(self) -> list[int]:
        """Return the number of entries in each bucket, in bucket order."""
        return [len(chain) for chain in self._buckets]

    def put(self, key: K, value: V) -> None:
        """Insert or replace ``key``. Replacement does not change the size."""
        _reject_nan(key)
        index = self._index(key)
        chain = self._buckets[index]
        for position, (stored, _stored_value) in enumerate(chain):
            if stored == key:
                chain[position] = (key, value)
                return
        chain.append((key, value))
        self._size += 1
        # One doubling is not enough when ``max_load_factor * capacity < 1``:
        # a single stored key would still exceed the cap. Keep doubling until
        # the load invariant holds. ``max_load_factor > 0`` guarantees this ends.
        while self._size > self._max_load_factor * len(self._buckets):
            self._resize()

    def get(self, key: K) -> V:
        """Return the value stored for ``key``. Raise ``KeyError`` if absent."""
        for stored, value in self._buckets[self._index(key)]:
            if stored == key:
                return value
        raise KeyError(key)

    def delete(self, key: K) -> None:
        """Remove ``key``. Raise ``KeyError`` if it is absent."""
        chain = self._buckets[self._index(key)]
        for position, (stored, _value) in enumerate(chain):
            if stored == key:
                chain.pop(position)
                self._size -= 1
                return
        raise KeyError(key)

    def items(self) -> list[tuple[K, V]]:
        """Return pairs in bucket order. Order is not insertion order."""
        return [(key, value) for chain in self._buckets for key, value in chain]

    def is_valid(self) -> bool:
        """Check bucket placement, uniqueness, size, and the load-factor cap."""
        seen: set[K] = set()
        counted = 0
        for index, chain in enumerate(self._buckets):
            for key, _value in chain:
                if self._index(key) != index or key in seen:
                    return False
                seen.add(key)
                counted += 1
        within_load = self._size <= self._max_load_factor * len(self._buckets)
        return counted == self._size and within_load

    def _index(self, key: K) -> int:
        # C's '%' can stay negative. Python's '%' with a positive modulus cannot,
        # so this index is always in ``[0, capacity)``.
        return hash(key) % len(self._buckets)

    def _resize(self) -> None:
        entries = self.items()
        new_capacity = len(self._buckets) * 2
        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        for key, value in entries:
            bucket = self._index(key)
            self._buckets[bucket].append((key, value))
            self._size += 1


def _reject_nan(key: object) -> None:
    if isinstance(key, float) and math.isnan(key):
        raise ValueError("NaN is not a valid hash-table key")

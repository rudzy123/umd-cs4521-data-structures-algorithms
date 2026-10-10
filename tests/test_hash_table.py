"""Separate chaining, replacement, deletion, and resizing."""

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from umd_algorithms import HashTable


def test_put_get_replace_and_delete() -> None:
    table = HashTable[str, int]()
    assert len(table) == 0
    assert "missing" not in table
    table.put("alpha", 1)
    table["beta"] = 2
    table.put("alpha", 5)
    assert len(table) == 2
    assert table.get("alpha") == 5
    assert table["beta"] == 2
    assert table.is_valid()
    del table["beta"]
    assert "beta" not in table
    with pytest.raises(KeyError):
        table.get("beta")
    with pytest.raises(KeyError):
        table.delete("beta")
    assert table.is_valid()
    assert len(table) == 1


def test_resize_keeps_every_entry() -> None:
    table = HashTable[int, int](capacity=4, max_load_factor=0.75)
    for key in range(30):
        table.put(key, key * 10)
        assert table.is_valid()
    assert table.bucket_count > 4
    assert table.load_factor <= table.max_load_factor
    assert {key: table.get(key) for key in range(30)} == {key: key * 10 for key in range(30)}


def test_tiny_load_factor_doubles_until_the_invariant_holds() -> None:
    table = HashTable[int, str](capacity=1, max_load_factor=0.1)
    table.put(7, "seven")
    assert table.is_valid()
    assert table.get(7) == "seven"
    assert table.bucket_count > 1


def test_pigeonhole_chains_when_resize_is_disabled() -> None:
    table = HashTable[int, int](capacity=2, max_load_factor=10)
    for key in range(8):
        table.put(key, -key)
    assert table.bucket_count == 2
    assert max(table.chain_lengths()) >= 4
    assert table.is_valid()
    table.delete(3)
    assert table.get(0) == 0
    assert 3 not in table
    assert table.is_valid()


def test_unhashable_and_nan_keys() -> None:
    table = HashTable[object, int]()
    assert ["not", "hashable"] not in table
    with pytest.raises(TypeError):
        table.put(["not", "hashable"], 1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="NaN"):
        table.put(math.nan, 1)


def test_rejects_bad_construction() -> None:
    with pytest.raises(ValueError):
        HashTable[int, int](capacity=0)
    with pytest.raises(ValueError):
        HashTable[int, int](max_load_factor=0)
    with pytest.raises(ValueError):
        HashTable[int, int](capacity=True)  # type: ignore[arg-type]


@given(
    st.lists(st.tuples(st.integers(-50, 50), st.integers()), max_size=40),
    st.lists(st.integers(-50, 50), max_size=20),
)
def test_matches_dict_under_overwrites_and_deletes(
    pairs: list[tuple[int, int]],
    deletions: list[int],
) -> None:
    table = HashTable[int, int](capacity=2, max_load_factor=0.75)
    reference: dict[int, int] = {}
    for key, value in pairs:
        table.put(key, value)
        reference[key] = value
        assert table.is_valid()
    assert len(table) == len(reference)
    for key, value in reference.items():
        assert table.get(key) == value
    for key in deletions:
        if key in reference:
            table.delete(key)
            del reference[key]
        else:
            with pytest.raises(KeyError):
                table.delete(key)
        assert table.is_valid()
    assert dict(table.items()) == reference

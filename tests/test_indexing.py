"""Indexing, slicing, and membership behaviour."""

from __future__ import annotations

import pytest

from ringbuf import RingBuffer


def test_positive_index_returns_correct_item() -> None:
    rb = RingBuffer(4, ["a", "b", "c", "d"])
    assert rb[0] == "a"
    assert rb[3] == "d"


def test_negative_index_counts_from_newest() -> None:
    rb = RingBuffer(4, ["a", "b", "c", "d"])
    assert rb[-1] == "d"
    assert rb[-4] == "a"


def test_index_after_wrap_is_correct() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend([1, 2, 3, 4, 5])  # holds [3,4,5]
    assert rb[0] == 3
    assert rb[1] == 4
    assert rb[2] == 5
    assert rb[-1] == 5
    assert rb[-3] == 3


def test_index_out_of_range_positive_raises() -> None:
    rb = RingBuffer(3, [1, 2])
    with pytest.raises(IndexError):
        rb[2]


def test_index_out_of_range_negative_raises() -> None:
    rb = RingBuffer(3, [1, 2])
    with pytest.raises(IndexError):
        rb[-3]


def test_index_with_non_int_raises_type_error() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    with pytest.raises(TypeError):
        rb["a"]  # type: ignore[index]


def test_index_with_bool_raises_type_error() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    with pytest.raises(TypeError):
        rb[True]  # type: ignore[index]


def test_slice_returns_list_of_items() -> None:
    rb = RingBuffer(5, [1, 2, 3, 4, 5])
    assert rb[1:4] == [2, 3, 4]


def test_slice_with_step_returns_correct_items() -> None:
    rb = RingBuffer(5, [10, 20, 30, 40, 50])
    assert rb[::2] == [10, 30, 50]


def test_slice_after_wrap_still_oldest_to_newest() -> None:
    rb: RingBuffer[int] = RingBuffer(4)
    rb.extend([1, 2, 3, 4, 5, 6])  # holds [3,4,5,6]
    assert rb[:] == [3, 4, 5, 6]
    assert rb[1:3] == [4, 5]
    assert rb[::-1] == [6, 5, 4, 3]


def test_contains_true_when_item_present() -> None:
    rb = RingBuffer(3, ["a", "b", "c"])
    assert "b" in rb
    assert "a" in rb


def test_contains_false_when_item_absent() -> None:
    rb = RingBuffer(3, ["a", "b", "c"])
    assert "z" not in rb


def test_contains_only_finds_live_items_after_overwrite() -> None:
    rb: RingBuffer[int] = RingBuffer(2)
    rb.extend([1, 2, 3])  # holds [2, 3]; the original 1 is gone
    assert 1 not in rb
    assert 2 in rb
    assert 3 in rb


def test_contains_uses_equality_not_identity() -> None:
    rb: RingBuffer[float] = RingBuffer(3)
    rb.append(1.0)
    rb.append(2.0)
    assert 1 in rb  # int 1 == float 1.0

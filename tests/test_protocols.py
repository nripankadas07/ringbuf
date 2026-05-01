"""Sequence protocol details: equality, repr, hashability."""

from __future__ import annotations

import pytest

from ringbuf import RingBuffer


def test_equal_buffers_same_capacity_same_items() -> None:
    a = RingBuffer(3, [1, 2, 3])
    b = RingBuffer(3, [1, 2, 3])
    assert a == b


def test_buffers_different_capacity_not_equal() -> None:
    a = RingBuffer(3, [1, 2, 3])
    b = RingBuffer(5, [1, 2, 3])
    assert a != b


def test_buffers_different_items_not_equal() -> None:
    a = RingBuffer(3, [1, 2, 3])
    b = RingBuffer(3, [1, 2, 4])
    assert a != b


def test_buffer_unequal_to_arbitrary_object_returns_not_implemented() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    assert (rb == [1, 2, 3]) is False  # NotImplemented bubbles to False
    assert (rb == "abc") is False


def test_repr_is_round_trippable_string() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    text = repr(rb)
    assert "RingBuffer(capacity=3" in text
    assert "1, 2, 3" in text


def test_repr_empty_buffer() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    text = repr(rb)
    assert "items=[]" in text
    assert "capacity=3" in text


def test_buffer_is_unhashable_like_list() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    with pytest.raises(TypeError):
        {rb}  # type: ignore[arg-type]


def test_bool_truthiness_matches_size() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    assert bool(rb) is False
    rb.append(1)
    assert bool(rb) is True


def test_equal_after_round_trip_through_pop_and_append() -> None:
    a = RingBuffer(3, [1, 2, 3])
    b = RingBuffer(3, [1, 2, 3])
    b.popleft()
    b.append(4)
    a.popleft()
    a.append(4)
    assert a == b
    assert a.to_list() == [2, 3, 4]


def test_eq_returns_false_on_first_value_mismatch() -> None:
    # Force the inner ``return False`` branch in __eq__ where capacity and
    # size match but a value differs.
    a = RingBuffer(2, [10, 20])
    b = RingBuffer(2, [10, 99])
    assert (a == b) is False


def test_eq_returns_false_on_size_mismatch_with_same_capacity() -> None:
    # Force the size-mismatch branch in __eq__ â same capacity, different fill.
    a = RingBuffer(5, [1, 2])
    b = RingBuffer(5, [1, 2, 3])
    assert (a == b) is False

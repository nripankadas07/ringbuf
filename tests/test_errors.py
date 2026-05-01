"""Error and validation edge cases."""

from __future__ import annotations

import pytest

from ringbuf import (
    CapacityError,
    RingBuffer,
    RingBufferEmpty,
    RingBufferError,
)


def test_capacity_zero_raises_capacity_error() -> None:
    with pytest.raises(CapacityError):
        RingBuffer(0)


def test_capacity_negative_raises_capacity_error() -> None:
    with pytest.raises(CapacityError):
        RingBuffer(-1)


def test_capacity_non_int_raises_capacity_error() -> None:
    with pytest.raises(CapacityError):
        RingBuffer(3.5)  # type: ignore[arg-type]


def test_capacity_string_raises_capacity_error() -> None:
    with pytest.raises(CapacityError):
        RingBuffer("3")  # type: ignore[arg-type]


def test_capacity_bool_raises_capacity_error() -> None:
    # booleans are ints in Python â the constructor must reject them.
    with pytest.raises(CapacityError):
        RingBuffer(True)  # type: ignore[arg-type]


def test_pop_empty_raises_ringbuffer_empty() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    with pytest.raises(RingBufferEmpty):
        rb.pop()


def test_popleft_empty_raises_ringbuffer_empty() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    with pytest.raises(RingBufferEmpty):
        rb.popleft()


def test_peek_oldest_empty_raises_ringbuffer_empty() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    with pytest.raises(RingBufferEmpty):
        rb.peek_oldest()


def test_peek_newest_empty_raises_ringbuffer_empty() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    with pytest.raises(RingBufferEmpty):
        rb.peek_newest()


def test_pop_after_clear_raises_ringbuffer_empty() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    rb.clear()
    with pytest.raises(RingBufferEmpty):
        rb.pop()


def test_ringbuffer_empty_is_index_error_too() -> None:
    rb: RingBuffer[int] = RingBuffer(2)
    with pytest.raises(IndexError):
        rb.pop()


def test_capacity_error_is_value_error_too() -> None:
    with pytest.raises(ValueError):
        RingBuffer(0)


def test_all_errors_share_base_class() -> None:
    assert issubclass(CapacityError, RingBufferError)
    assert issubclass(RingBufferEmpty, RingBufferError)

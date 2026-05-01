"""Integration-style tests covering full append/pop lifecycles."""

from __future__ import annotations

import pytest

from ringbuf import RingBuffer, RingBufferEmpty


def test_alternating_append_pop_keeps_consistent_state() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.append(1)
    assert rb.pop() == 1
    rb.append(2)
    rb.append(3)
    assert rb.popleft() == 2
    assert rb.popleft() == 3
    assert len(rb) == 0


def test_stress_round_trip_preserves_order() -> None:
    rb: RingBuffer[int] = RingBuffer(7)
    pushed: list[int] = []
    for value in range(50):
        rb.append(value)
        pushed.append(value)
    assert rb.to_list() == pushed[-7:]


def test_repeated_overwrite_keeps_invariants() -> None:
    rb: RingBuffer[int] = RingBuffer(4)
    for value in range(100):
        rb.append(value)
        assert len(rb) <= rb.capacity
    assert rb.to_list() == [96, 97, 98, 99]


def test_all_pops_then_extend_matches_initial_state() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend([1, 2, 3])
    while rb:
        rb.pop()
    rb.extend([1, 2, 3])
    assert rb.to_list() == [1, 2, 3]


def test_pop_while_empty_at_end_raises_again() -> None:
    rb = RingBuffer(2, [1, 2])
    rb.pop()
    rb.pop()
    with pytest.raises(RingBufferEmpty):
        rb.pop()


def test_extend_with_empty_iterable_is_noop() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend([])
    assert len(rb) == 0


def test_clear_then_reuse_works() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend([1, 2, 3, 4])
    rb.clear()
    rb.append(99)
    assert rb.to_list() == [99]
    assert rb.peek_newest() == 99
    assert rb.peek_oldest() == 99


def test_capacity_one_is_valid() -> None:
    rb: RingBuffer[int] = RingBuffer(1)
    rb.append(1)
    rb.append(2)
    assert rb.to_list() == [2]
    assert rb.is_full is True
    assert rb.peek_oldest() == 2
    assert rb.peek_newest() == 2


def test_capacity_one_pop_works() -> None:
    rb = RingBuffer(1, [42])
    assert rb.pop() == 42
    assert rb.is_empty is True


def test_iter_after_full_alternation() -> None:
    rb: RingBuffer[int] = RingBuffer(4)
    for value in range(20):
        rb.append(value)
        if value % 3 == 0:
            rb.popleft()
    # End state derived from running the same loop in CPython.
    expected = list(rb.to_list())  # capture once
    assert list(iter(rb)) == expected
    assert list(reversed(rb)) == list(reversed(expected))

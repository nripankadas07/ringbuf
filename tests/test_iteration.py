"""Iteration order tests including the post-wrap path."""

from __future__ import annotations

from ringbuf import RingBuffer


def test_iter_returns_oldest_to_newest_before_wrap() -> None:
    rb = RingBuffer(5, [1, 2, 3])
    assert list(iter(rb)) == [1, 2, 3]


def test_iter_returns_oldest_to_newest_after_wrap() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend([1, 2, 3, 4, 5, 6, 7])  # last three: 5, 6, 7
    assert list(iter(rb)) == [5, 6, 7]


def test_reversed_returns_newest_to_oldest_before_wrap() -> None:
    rb = RingBuffer(5, [1, 2, 3])
    assert list(reversed(rb)) == [3, 2, 1]


def test_reversed_returns_newest_to_oldest_after_wrap() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend(range(1, 8))
    assert list(reversed(rb)) == [7, 6, 5]


def test_iter_does_not_mutate_buffer() -> None:
    rb = RingBuffer(3, ["a", "b", "c"])
    list(iter(rb))
    list(reversed(rb))
    assert rb.to_list() == ["a", "b", "c"]


def test_iter_after_partial_wrap_then_pop_round_trip() -> None:
    rb: RingBuffer[int] = RingBuffer(4)
    rb.extend([1, 2, 3, 4, 5])  # holds [2,3,4,5]
    rb.popleft()                # holds [3,4,5]
    rb.append(6)                # holds [3,4,5,6]
    assert list(iter(rb)) == [3, 4, 5, 6]
    assert list(reversed(rb)) == [6, 5, 4, 3]


def test_for_loop_uses_iter() -> None:
    rb = RingBuffer(3, [10, 20, 30])
    accumulator: list[int] = []
    for value in rb:
        accumulator.append(value)
    assert accumulator == [10, 20, 30]

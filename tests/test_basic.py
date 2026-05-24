"""Basic happy-path tests for RingBuffer."""

from __future__ import annotations


from ringbuf import RingBuffer


def test_init_empty_buffer_has_zero_length() -> None:
    rb: RingBuffer[int] = RingBuffer(5)
    assert len(rb) == 0
    assert rb.is_empty is True
    assert rb.is_full is False
    assert rb.capacity == 5


def test_init_with_iterable_populates_in_order() -> None:
    rb = RingBuffer(5, [1, 2, 3])
    assert len(rb) == 3
    assert rb.to_list() == [1, 2, 3]


def test_append_single_item_increases_length() -> None:
    rb: RingBuffer[str] = RingBuffer(3)
    rb.append("a")
    assert len(rb) == 1
    assert rb.to_list() == ["a"]


def test_append_until_full_marks_is_full() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    for value in (1, 2, 3):
        rb.append(value)
    assert rb.is_full is True
    assert rb.is_empty is False
    assert rb.to_list() == [1, 2, 3]


def test_append_past_capacity_overwrites_oldest() -> None:
    rb: RingBuffer[int] = RingBuffer(3)
    rb.extend([1, 2, 3, 4, 5])
    assert rb.to_list() == [3, 4, 5]
    assert len(rb) == 3


def test_extend_with_iterable_longer_than_capacity_keeps_last_n() -> None:
    rb: RingBuffer[int] = RingBuffer(2)
    rb.extend(range(10))
    assert rb.to_list() == [8, 9]


def test_pop_returns_newest_and_shrinks() -> None:
    rb = RingBuffer(3, [10, 20, 30])
    assert rb.pop() == 30
    assert rb.to_list() == [10, 20]
    assert len(rb) == 2


def test_popleft_returns_oldest_and_shrinks() -> None:
    rb = RingBuffer(3, [10, 20, 30])
    assert rb.popleft() == 10
    assert rb.to_list() == [20, 30]
    assert len(rb) == 2


def test_clear_resets_size_but_keeps_capacity() -> None:
    rb = RingBuffer(4, [1, 2, 3, 4])
    rb.clear()
    assert len(rb) == 0
    assert rb.capacity == 4
    assert rb.is_empty is True


def test_peek_oldest_and_peek_newest_do_not_remove() -> None:
    rb = RingBuffer(4, ["a", "b", "c"])
    assert rb.peek_oldest() == "a"
    assert rb.peek_newest() == "c"
    assert rb.to_list() == ["a", "b", "c"]


def test_to_list_returns_independent_snapshot() -> None:
    rb = RingBuffer(3, [1, 2, 3])
    snapshot = rb.to_list()
    snapshot.append(99)
    assert rb.to_list() == [1, 2, 3]

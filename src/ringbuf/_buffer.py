"""Core :class:`RingBuffer` implementation.

A ring buffer (a.k.a. circular buffer) is a fixed-capacity sequence
where every operation is O(1). When the buffer is full and another
item is appended, the *oldest* item is silently overwritten.

Internals
---------

The container is a Python list of length ``capacity``. Two integers
track state:

``_head``
    Index where the *next* appended item will be stored. After each
    append it advances by one (mod capacity).

``_size``
    How many of the slots actually hold valid items. Always satisfies
    ``0 <= _size <= capacity``.

The oldest item lives at ``(_head - _size) mod capacity``; the newest
at ``(_head - 1) mod capacity``. Indexing position ``i`` (where
``0`` is oldest) maps to ``(_head - _size + i) mod capacity``.
"""

from __future__ import annotations

from typing import Generic, Iterable, Iterator, TypeVar, overload

from ._errors import CapacityError, RingBufferEmpty

T = TypeVar("T")
_SENTINEL: object = object()


class RingBuffer(Generic[T]):
    """Fixed-capacity ring buffer with overwrite-oldest semantics.

    Parameters
    ----------
    capacity:
        Maximum number of items the buffer can hold. Must be a
        positive integer; a :class:`CapacityError` is raised otherwise.
    iterable:
        Optional initial items. If the iterable yields more than
        ``capacity`` items, only the last ``capacity`` are kept,
        matching :meth:`extend`.
    """

    __slots__ = ("_capacity", "_buffer", "_head", "_size")

    def __init__(
        self,
        capacity: int,
        iterable: Iterable[T] | None = None,
    ) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise CapacityError(
                f"capacity must be int, got {type(capacity).__name__}"
            )
        if capacity <= 0:
            raise CapacityError(
                f"capacity must be a positive integer, got {capacity}"
            )
        self._capacity: int = capacity
        self._buffer: list[T] = [_SENTINEL] * capacity  # type: ignore[list-item]
        self._head: int = 0
        self._size: int = 0
        if iterable is not None:
            self.extend(iterable)

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def capacity(self) -> int:
        """Maximum number of items the buffer can hold."""
        return self._capacity

    @property
    def is_full(self) -> bool:
        """``True`` when the buffer holds ``capacity`` items."""
        return self._size == self._capacity

    @property
    def is_empty(self) -> bool:
        """``True`` when the buffer holds zero items."""
        return self._size == 0

    # ------------------------------------------------------------------ #
    # Mutation
    # ------------------------------------------------------------------ #

    def append(self, item: T) -> None:
        """Append ``item`` to the newest end. O(1).

        If the buffer is full, the oldest item is silently overwritten.
        """
        self._buffer[self._head] = item
        self._head = (self._head + 1) % self._capacity
        if self._size < self._capacity:
            self._size += 1

    def extend(self, iterable: Iterable[T]) -> None:
        """Append every item from ``iterable``.

        If the iterable is longer than ``capacity`` only the last
        ``capacity`` items remain, matching ``append`` repeated.
        """
        for item in iterable:
            self.append(item)

    def pop(self) -> T:
        """Remove and return the *newest* item. O(1).

        Raises :class:`RingBufferEmpty` if the buffer is empty.
        """
        if self._size == 0:
            raise RingBufferEmpty("pop from empty RingBuffer")
        self._head = (self._head - 1) % self._capacity
        self._size -= 1
        item = self._buffer[self._head]
        self._buffer[self._head] = _SENTINEL  # type: ignore[assignment]
        return item

    def popleft(self) -> T:
        """Remove and return the *oldest* item. O(1).

        Raises :class:`RingBufferEmpty` if the buffer is empty.
        """
        if self._size == 0:
            raise RingBufferEmpty("popleft from empty RingBuffer")
        tail = (self._head - self._size) % self._capacity
        item = self._buffer[tail]
        self._buffer[tail] = _SENTINEL  # type: ignore[assignment]
        self._size -= 1
        return item

    def clear(self) -> None:
        """Remove all items. The capacity is unchanged."""
        self._buffer = [_SENTINEL] * self._capacity  # type: ignore[list-item]
        self._head = 0
        self._size = 0

    # ------------------------------------------------------------------ #
    # Read-only views
    # ------------------------------------------------------------------ #

    def peek_oldest(self) -> T:
        """Return the oldest item without removing it.

        Raises :class:`RingBufferEmpty` if the buffer is empty.
        """
        if self._size == 0:
            raise RingBufferEmpty("peek_oldest on empty RingBuffer")
        tail = (self._head - self._size) % self._capacity
        return self._buffer[tail]

    def peek_newest(self) -> T:
        """Return the newest item without removing it.

        Raises :class:`RingBufferEmpty` if the buffer is empty.
        """
        if self._size == 0:
            raise RingBufferEmpty("peek_newest on empty RingBuffer")
        return self._buffer[(self._head - 1) % self._capacity]

    def to_list(self) -> list[T]:
        """Return a list snapshot in oldest-to-newest order."""
        return list(self)

    # ------------------------------------------------------------------ #
    # Sequence protocol
    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        size = self._size
        capacity = self._capacity
        head = self._head
        buffer = self._buffer
        tail = (head - size) % capacity
        for offset in range(size):
            yield buffer[(tail + offset) % capacity]

    def __reversed__(self) -> Iterator[T]:
        size = self._size
        capacity = self._capacity
        head = self._head
        buffer = self._buffer
        for offset in range(1, size + 1):
            yield buffer[(head - offset) % capacity]

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: int | slice) -> T | list[T]:
        if isinstance(index, slice):
            return self._slice(index)
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(
                f"RingBuffer indices must be int or slice, "
                f"not {type(index).__name__}"
            )
        return self._index(index)

    def __contains__(self, item: object) -> bool:
        for value in self:
            if value is item or value == item:
                return True
        return False

    # ------------------------------------------------------------------ #
    # Identity / equality / repr
    # ------------------------------------------------------------------ #

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RingBuffer):
            return NotImplemented
        if self._capacity != other._capacity:
            return False
        if self._size != other._size:
            return False
        for left, right in zip(self, other):
            if left != right:
                return False
        return True

    # Mutable container â explicitly unhashable, matching list/deque.
    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        items = ", ".join(repr(x) for x in self)
        return f"RingBuffer(capacity={self._capacity}, items=[{items}])"

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _index(self, index: int) -> T:
        size = self._size
        if index < 0:
            index += size
        if index < 0 or index >= size:
            raise IndexError("RingBuffer index out of range")
        tail = (self._head - size) % self._capacity
        return self._buffer[(tail + index) % self._capacity]

    def _slice(self, sl: slice) -> list[T]:
        return [self._index(i) for i in range(*sl.indices(self._size))]

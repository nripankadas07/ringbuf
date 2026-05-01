"""ringbuf â fixed-capacity ring buffer with O(1) append.

A small, dependency-free Python ring buffer that overwrites the oldest
item when the capacity is reached. Supports indexing, slicing,
forward and reverse iteration, peek, pop from either end, and
length/membership operators.

Public API:

* :class:`RingBuffer` â the buffer itself.
* :class:`RingBufferError` â base for every error raised here.
* :class:`RingBufferEmpty` â raised when reading or popping an empty
  buffer. Subclass of :class:`IndexError`.
* :class:`CapacityError` â raised when an invalid capacity is given.
  Subclass of :class:`ValueError`.
"""

from __future__ import annotations

from ._buffer import RingBuffer
from ._errors import CapacityError, RingBufferEmpty, RingBufferError

__all__ = [
    "CapacityError",
    "RingBuffer",
    "RingBufferEmpty",
    "RingBufferError",
]

__version__ = "0.1.0"

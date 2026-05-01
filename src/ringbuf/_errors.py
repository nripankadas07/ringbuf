"""Exception types raised by :mod:`ringbuf`."""

from __future__ import annotations


class RingBufferError(Exception):
    """Base class for all ring buffer errors."""


class RingBufferEmpty(RingBufferError, IndexError):
    """Raised when reading from or popping an empty buffer.

    Subclasses :class:`IndexError` so existing ``try/except IndexError``
    blocks (familiar from ``list.pop`` and similar) keep working.
    """


class CapacityError(RingBufferError, ValueError):
    """Raised when an invalid capacity is supplied at construction time.

    Subclasses :class:`ValueError` because it represents a programmer
    error caught at d[boundary of the public API.
    """

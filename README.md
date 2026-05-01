# ringbuf

A small, dependency-free Python ring buffer (a.k.a. circular buffer)
with **O(1) append**, **overwrite-oldest** semantics when full,
indexable, slice-able, and reversible.

`ringbuf` exists to give you the classical fixed-capacity buffer
without dragging in `collections.deque(maxlen=...)`'s linked-list
overhead, and without the "throws when full" surprise of
`queue.Queue(maxsize=...)`. When the buffer is full and you append
again, the oldest item is silently overwritten â exactly what you
want for rolling logs, sliding windows, latest-N caches, and
event-loop telemetry.

## Why not just use `collections.deque`?

`deque(maxlen=n)` is the standard answer and works well, but:

* `deque` is a linked list of blocks; random access by index is O(n).
* A ring buffer backed by a list is O(1) for indexing **and** for
  forward / reverse iteration without rotation.
* `deque` does not expose `is_full`, `peek_oldest`, `peek_newest`,
  or a typed empty-error.

If you need a thread-safe queue, reach for `queue.Queue`. This
library targets the single-threaded case.

## Install

```bash
pip install ringbuf
```

`ringbuf` requires Python 3.10 or newer. Zero runtime dependencies.

## Quick start

```python
from ringbuf import RingBuffer

rb: RingBuffer[int] = RingBuffer(capacity=3)
rb.append(1)
rb.append(2)
rb.append(3)
rb.append(4)            # overwrites 1

list(rb)                # [2, 3, 4]
rb[0], rb[-1]           # (2, 4)
rb.peek_oldest()        # 2
rb.peek_newest()        # 4
rb.popleft()            # 2  -> rb is now [3, 4]
rb.pop()                # 4  -> rb is now [3]
```

You can construct a buffer pre-filled from any iterable. If the
iterable is longer than the capacity, only the last `capacity`
items survive â same semantics as `append` repeated:

```python
rb = RingBuffer(3, range(10))
list(rb)                # [7, 8, 9]
```

## API reference

### `RingBuffer(capacity: int, iterable: Iterable[T] | None = None)`

Construct a buffer holding at most `capacity` items.

* `capacity` must be a positive `int`. Booleans are rejected so
  `RingBuffer(True)` does not silently mean `RingBuffer(1)`.
* `iterable`, if given, populates the buffer in order. Items beyond
  `capacity` overwrite earlier ones.

Raises `CapacityError` (subclass of `ValueError`) on invalid input.

### Mutation

| Method            | Description                                                                       |
| ----------------- | --------------------------------------------------------------------------------- |
| `append(item)`    | O(1). Appends to the newest end. Overwrites the oldest item if the buffer is full.|
| `extend(iter)`    | Appends every item from `iter`. Same overwrite behaviour as `append` repeated.    |
| `pop()`           | O(1). Removes and returns the *newest* item. Raises `RingBufferEmpty` if empty.   |
| `popleft()`       | O(1). Removes and returns the *oldest* item. Raises `RingBufferEmpty` if empty.   |
| `clear()`         | Removes all items. Capacity is unchanged.                                         |

### Read-only views

| Method / property | Description                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| `peek_oldest()`   | Returns the oldest item without removing it.                             |
| `peek_newest()`   | Returns the newest item without removing it.                             |
| `to_list()`       | Returns a `list` snapshot in oldest-to-newest order.                     |
| `capacity`        | The configured capacity (read-only).                                     |
| `is_full`         | `True` when the buffer holds `capacity` items.                           |
| `is_empty`        | `True` when the buffer holds zero items.                                 |

### Sequence protocol

* `len(rb)` â number of items currently stored.
* `iter(rb)` â yields oldest â newest.
* `reversed(rb)` â yields newest â oldest.
* `rb[i]` â positional access. Negative indices count from the
  newest end. `IndexError` is raised on out-of-range.
* `rb[a:b:s]` â slice access returns a `list`.
* `item in rb` â membership test using equality.
* `rb == other` â true iff `other` is a `RingBuffer` with the same
  capacity and the same items in the same order.
* `repr(rb)` â `RingBuffer(capacity=N, items=[â¦])`.
* The buffer is **unhashable**, matching `list` and `deque`.

### Errors

* `RingBufferError` â base class for every error this library raises.
* `RingBufferEmpty` â raised by `pop`, `popleft`, `peek_oldest`,
  `peek_newest` when the buffer is empty. Subclass of `IndexError`,
  so existing `except IndexError` blocks still catch it.
* `CapacityError` â raised by the constructor on invalid capacity.
  Subclass of `ValueError`.

## Edge cases worth knowing

* `RingBuffer(0)` raises `CapacityError`. So does any negative or
  non-`int` capacity. Booleans are rejected because `True` and `False`
  are technically `int` in Python and this library refuses to guess.
* `RingBuffer(1)` is allowed. Every append replaces the only item.
* After enough appends to wrap, indexing and iteration still report
  oldest-to-newest order; the wrap is invisible to callers.
* `__contains__` only finds items currently in the buffer. Items that
  were overwritten are gone.
* `RingBuffer` is **not** thread-safe.

## Running tests

```bash
git clone https://github.com/nripankadas07/ringbuf
cd ringbuf
pip install -e ".[dev]"
pytest
```

Tests are organised by topic under `tests/`:

```
tests/test_basic.py        â happy path
tests/test_iteration.py    â forward / reverse iteration, post-wrap order
tests/test_indexing.py     â int / negative / slice indexing, contains
tests/test_errors.py       â CapacityError, RingBufferEmpty surfaces
tests/test_protocols.py    â equality, repr, hashability, truthiness
tests/test_lifecycle.py    â long-running append/pop sequences
```

Coverage is 100% line-and-statement on the source tree.

## License

MIT â see [`LICENSE`](LICENSE).

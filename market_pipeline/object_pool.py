"""
object_pool.py
===============

The Object Pool optimization -- introduced ONLY after Chapter 5 proves,
with a profiler, that object allocation is a real bottleneck.

WHY THIS FILE EXISTS
---------------------
Read docs/05_performance_problem.md and docs/06_object_pool.md for the
full story. In short:

At high tick rates (hundreds of thousands to millions per second),
allocating a brand new ``Tick`` object for every single event puts
constant pressure on Python's memory allocator and garbage collector.
Each allocation is cheap in isolation, but at this volume the *sum* of
that cost becomes measurable and shows up directly as reduced
throughput -- confirmed via ``cProfile`` in Chapter 5.

An Object Pool sidesteps this by pre-allocating a fixed number of
``Tick`` objects once, up front, and recycling them: instead of
"create a new Tick, and later let the garbage collector clean up the
old one," we say "borrow an existing Tick, overwrite its fields, and
return it to the pool when we're done."

ENGINEERING TRADEOFFS (be honest about the cost, not just the win)
--------------------------------------------------------------------
- Extra complexity: callers MUST return objects with ``release()`` or
  the pool leaks and degrades back into "always allocate new."
- The pooled objects are mutable and reused, so no code may hold onto
  a Tick reference *after* releasing it -- doing so would read another
  consumer's data. This is a real footgun and is called out explicitly
  in docs/06_object_pool.md under "Common Beginner Mistakes."
- Pools only help when allocation is actually the bottleneck. Applying
  this pattern without first profiling is premature optimization --
  which is exactly why this file did not exist in Chapter 1-4.
"""

from __future__ import annotations

import logging
from collections import deque

from market_pipeline.models import Tick

logger = logging.getLogger(__name__)


class TickObjectPool:
    """A simple fixed-size pool of reusable ``Tick`` objects.

    The pool pre-allocates ``pool_size`` Tick instances at construction
    time. ``acquire()`` returns an existing instance (overwritten with
    new data) if one is available, or allocates a new one as a
    fallback if the pool is exhausted -- so correctness never depends
    on sizing the pool perfectly, only performance does.
    """

    def __init__(self, pool_size: int = 1000) -> None:
        self._pool_size = pool_size
        self._available: deque[Tick] = deque(
            Tick(symbol="", price=0.0, quantity=0, timestamp_ns=0) for _ in range(pool_size)
        )
        self.objects_created = pool_size  # the initial pre-allocation
        self.objects_reused = 0

    def acquire(
        self,
        symbol: str,
        price: float,
        quantity: int,
        timestamp_ns: int,
        exchange: str = "SIM",
    ) -> Tick:
        """Borrow a Tick from the pool, populated with the given data."""
        if self._available:
            tick = self._available.popleft()
            tick.reset(symbol, price, quantity, timestamp_ns, exchange)
            self.objects_reused += 1
            return tick

        # Pool exhausted -- fall back to a real allocation rather than
        # blocking or raising. We log this because it means the pool
        # is undersized for the current load, which is useful
        # operational information, not a silent failure.
        logger.debug("Pool exhausted, allocating overflow Tick")
        self.objects_created += 1
        return Tick(symbol, price, quantity, timestamp_ns, exchange)

    def release(self, tick: Tick) -> None:
        """Return a Tick to the pool once the consumer is done with it.

        WARNING: after calling this, the caller must not read or write
        `tick` again -- another consumer may immediately reuse it.
        """
        if len(self._available) < self._pool_size:
            self._available.append(tick)
        # If the pool is already full (e.g. this was an overflow
        # object), we simply let it be garbage collected normally.

    @property
    def available_count(self) -> int:
        return len(self._available)

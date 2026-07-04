"""
models.py
=========

Defines the core data structure that flows through the entire pipeline:
the ``Tick``.

WHY THIS FILE EXISTS
---------------------
Every market data system, no matter how large, is built around one
question: "what does a single unit of market information look like?"

In real exchanges (NSE, NYSE, CME, Binance...) this unit is often called
a "tick" -- a single price/quantity update for one instrument at one
point in time. Everything downstream (strategies, risk engines, order
routers) consumes ticks. If we get this shape wrong, every layer built
on top of it inherits the mistake. So we design it first, deliberately,
before writing any pipeline code.

We use a ``dataclass`` (not a plain dict) because:
- It gives us type safety and editor autocompletion.
- It documents the schema in one place.
- It is significantly faster to construct than a dict with the same
  keys, which matters once we start measuring throughput in Chapter 5.
- ``slots=True`` removes the per-instance ``__dict__``, cutting memory
  per object substantially -- important when millions of these exist
  per second.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Tick:
    """A single market data event for one instrument.

    Attributes:
        symbol: Instrument identifier, e.g. "RELIANCE", "AAPL".
        price: Last traded price.
        quantity: Last traded quantity (lot size / shares / contracts).
        timestamp_ns: Exchange (or simulated) event time, in nanoseconds
            since the Unix epoch. We use nanoseconds -- not seconds or
            milliseconds -- because latency measurement in trading
            systems is routinely discussed in microseconds, and
            sub-millisecond precision is required to reason about it
            honestly.
        exchange: Origin venue of this tick, e.g. "NSE", "NASDAQ".
    """

    symbol: str
    price: float
    quantity: int
    timestamp_ns: int
    exchange: str = "SIM"

    def reset(
        self,
        symbol: str,
        price: float,
        quantity: int,
        timestamp_ns: int,
        exchange: str = "SIM",
    ) -> None:
        """Overwrite this Tick's fields in place.

        WHY THIS METHOD EXISTS:
        This is the method that makes the Object Pool optimization
        (see ``object_pool.py`` and docs/06_object_pool.md) possible.
        Instead of allocating a brand-new ``Tick`` for every market
        event, the pool hands back an existing, "retired" Tick object
        and we simply overwrite its contents. This method is the only
        place that mutation happens -- everywhere else in the codebase
        treats a Tick as if it were immutable, by convention.
        """
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.timestamp_ns = timestamp_ns
        self.exchange = exchange

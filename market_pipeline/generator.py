"""
generator.py
============

Simulates an exchange market data feed (the "Producer").

WHY THIS FILE EXISTS
---------------------
We don't have a real NSE/NASDAQ feed handy for a teaching repository,
and we shouldn't need one to learn the engineering. So we simulate
what a real feed *behaves like*: a continuous stream of ``Tick``
events for a fixed universe of symbols, arriving as fast as the
exchange (or our simulation) can produce them.

This is intentionally the ONLY place that creates ``Tick`` objects
directly with ``Tick(...)``. Every other producer in this repo
(the optimized version) goes through the object pool instead. Keeping
tick creation isolated here makes the naive-vs-optimized comparison
fair and easy to audit.
"""

from __future__ import annotations

import random
import time
from collections.abc import AsyncIterator

from market_pipeline.models import Tick

DEFAULT_SYMBOLS: tuple[str, ...] = (
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "LT",
)


async def generate_ticks(
    count: int,
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    seed: int | None = 42,
) -> AsyncIterator[Tick]:
    """Yield ``count`` simulated market ticks as fast as possible.

    This is an ``async generator``. WHY async? Because a real feed
    handler receives data over a WebSocket or TCP socket, and network
    I/O is exactly the kind of "waiting" operation asyncio was built
    to handle efficiently -- while we wait for the next byte off the
    wire, the event loop can do other useful work instead of blocking
    a whole OS thread. We use ``asyncio`` from day one, even in the
    simulation, so the mental model transfers directly to a real
    exchange connector.

    Args:
        count: Number of ticks to generate before stopping.
        symbols: Universe of instruments to simulate.
        seed: Random seed for reproducible benchmark runs. Use ``None``
            for non-deterministic output.
    """
    rng = random.Random(seed)
    prices = {symbol: rng.uniform(100, 4000) for symbol in symbols}

    for _ in range(count):
        symbol = rng.choice(symbols)
        # Simulate a small random walk in price -- realistic enough to
        # exercise the pipeline without needing real market data.
        prices[symbol] *= 1 + rng.uniform(-0.001, 0.001)

        yield Tick(
            symbol=symbol,
            price=round(prices[symbol], 2),
            quantity=rng.randint(1, 500),
            timestamp_ns=time.time_ns(),
        )

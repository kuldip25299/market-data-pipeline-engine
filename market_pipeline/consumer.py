"""
consumer.py
===========

The "strategy" side of the pipeline -- whatever consumes ticks after
the pipeline delivers them.

WHY THIS FILE EXISTS
---------------------
In a real trading platform, a trading strategy is the consumer: it
receives a tick and decides whether to act on it (place an order,
update a position, recalculate a signal). We don't build a real
trading strategy in this repository -- that is out of scope for a
market-data-pipeline project -- but we need *something* on the
receiving end to make the pipeline realistic and measurable.

``process_tick`` deliberately does a tiny, fixed amount of CPU work
(a couple of arithmetic operations) to simulate "a strategy looked at
this tick and did something with it," without introducing an
artificial ``sleep()`` that would misrepresent real consumer latency.
"""

from __future__ import annotations

import logging

from market_pipeline.models import Tick

logger = logging.getLogger(__name__)

# A tiny in-memory "last seen price" table -- stands in for whatever
# state a real strategy would maintain (moving averages, positions,
# order books, etc).
_last_price: dict[str, float] = {}


def process_tick(tick: Tick) -> float:
    """Simulate a strategy reacting to a single tick.

    Returns the price delta versus the last seen price for that
    symbol (0.0 on first sight). The return value isn't used for
    anything important -- it exists so the function does real,
    non-trivial work that the optimizer can't eliminate, keeping our
    benchmarks honest.
    """
    previous = _last_price.get(tick.symbol, tick.price)
    delta = tick.price - previous
    _last_price[tick.symbol] = tick.price
    return delta

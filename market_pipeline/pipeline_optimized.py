"""
pipeline_optimized.py
======================

STEP 4 of the learning journey: the same producer/consumer pipeline as
``pipeline_naive.py``, rebuilt to use ``TickObjectPool`` instead of
allocating a new ``Tick`` per event.

This file should be read side by side with ``pipeline_naive.py``. The
control flow is intentionally identical -- the ONLY structural
difference is:

  naive:     tick = Tick(...)                (allocate)
  optimized: tick = pool.acquire(...)         (borrow)
             ...
             pool.release(tick)               (return)

Everything else (queue-based hand-off, sentinel shutdown, metrics
collection) is unchanged, so that benchmarks/compare.py measures the
effect of ONE variable at a time -- good experimental hygiene, not
just good software engineering.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time

from market_pipeline.consumer import process_tick
from market_pipeline.generator import DEFAULT_SYMBOLS
from market_pipeline.metrics import PipelineMetrics
from market_pipeline.models import Tick
from market_pipeline.object_pool import TickObjectPool

logger = logging.getLogger(__name__)


async def _producer(
    queue: asyncio.Queue[Tick | None],
    tick_count: int,
    pool: TickObjectPool,
    metrics: PipelineMetrics,
    seed: int | None = 42,
) -> None:
    """Generate ticks via the object pool instead of raw allocation."""
    rng = random.Random(seed)
    prices = {symbol: rng.uniform(100, 4000) for symbol in DEFAULT_SYMBOLS}

    for _ in range(tick_count):
        symbol = rng.choice(DEFAULT_SYMBOLS)
        prices[symbol] *= 1 + rng.uniform(-0.001, 0.001)

        tick = pool.acquire(
            symbol=symbol,
            price=round(prices[symbol], 2),
            quantity=rng.randint(1, 500),
            timestamp_ns=time.time_ns(),
        )
        await queue.put(tick)
        metrics.ticks_generated += 1
        metrics.record_queue_size(queue.qsize())

    await queue.put(None)


async def _consumer(
    queue: asyncio.Queue[Tick | None],
    pool: TickObjectPool,
    metrics: PipelineMetrics,
) -> None:
    """Pull ticks off the queue, process them, then return them to the pool."""
    while True:
        tick: Tick | None = await queue.get()
        if tick is None:
            break
        process_tick(tick)
        metrics.ticks_processed += 1
        pool.release(tick)  # <-- the step that makes the pool actually work


async def run_optimized_pipeline(tick_count: int, pool_size: int = 1000) -> PipelineMetrics:
    """Run the object-pool-optimized producer/consumer pipeline.

    Args:
        tick_count: How many simulated ticks to push through.
        pool_size: Number of Tick objects to pre-allocate. Chapter 7
            (benchmarking) explores how this number affects the
            objects_created / objects_reused ratio.

    IMPORTANT DESIGN NOTE -- why the queue is bounded here:
    An unbounded queue (as used in ``pipeline_naive.py``) lets the
    producer race arbitrarily far ahead of the consumer. Under
    asyncio's cooperative scheduling, ``queue.put()`` on a non-full
    unbounded queue never actually suspends the producer, so the
    entire producer loop can run to completion *before the consumer
    gets a turn* -- which would exhaust the pool almost immediately
    and force every subsequent tick into overflow allocation, silently
    defeating the whole optimization. Bounding the queue at
    ``pool_size`` forces the producer to block (via
    ``await queue.put(...)``) once in-flight ticks reach the pool's
    capacity, which yields control to the consumer and lets released
    objects flow back to the pool before more are requested. This is
    also a realistic and correct use of backpressure -- see
    docs/06_object_pool.md and docs/03_market_data_flow.md.
    """
    metrics = PipelineMetrics()
    queue: asyncio.Queue[Tick | None] = asyncio.Queue(maxsize=pool_size)
    pool = TickObjectPool(pool_size=pool_size)

    metrics.start()
    await asyncio.gather(
        _producer(queue, tick_count, pool, metrics),
        _consumer(queue, pool, metrics),
    )
    metrics.stop()

    metrics.objects_created = pool.objects_created
    metrics.objects_reused = pool.objects_reused

    logger.info("Optimized pipeline run complete: %s ticks", tick_count)
    return metrics

"""
pipeline_naive.py
==================

STEP 1 of the learning journey: the simplest possible pipeline that
correctly moves ticks from a producer to a consumer.

WHY THIS FILE EXISTS
---------------------
Before optimizing anything, we need a correct, working baseline. This
is the version you would probably write on your first day, and that
is exactly the point -- see docs/04_building_pipeline.md.

DESIGN
------
- One producer coroutine calls ``generate_ticks`` and pushes every
  Tick it creates onto an ``asyncio.Queue``.
- One consumer coroutine pulls ticks off the queue and calls
  ``process_tick``.
- ``asyncio.Queue`` gives us a thread-safe (well, task-safe) hand-off
  point between the two coroutines, plus built-in backpressure if we
  set ``maxsize`` -- though in this naive version we intentionally
  leave it unbounded to first observe what happens (see Chapter 5).

WHAT'S "NAIVE" ABOUT IT
------------------------
Every single Tick is a brand new object, allocated with ``Tick(...)``.
For low tick rates this is completely fine. Chapter 5 shows exactly
when and why it stops being fine.
"""

from __future__ import annotations

import asyncio
import logging

from market_pipeline.consumer import process_tick
from market_pipeline.generator import DEFAULT_SYMBOLS, generate_ticks
from market_pipeline.metrics import PipelineMetrics
from market_pipeline.models import Tick

logger = logging.getLogger(__name__)


async def _producer(
    queue: asyncio.Queue[Tick | None],
    tick_count: int,
    metrics: PipelineMetrics,
) -> None:
    """Generate ticks and push them onto the shared queue."""
    async for tick in generate_ticks(tick_count, DEFAULT_SYMBOLS):
        await queue.put(tick)
        metrics.ticks_generated += 1
        metrics.objects_created += 1  # every tick here is a fresh object
        metrics.record_queue_size(queue.qsize())

    # Sentinel value tells the consumer there is no more data coming.
    await queue.put(None)


async def _consumer(queue: asyncio.Queue[Tick | None], metrics: PipelineMetrics) -> None:
    """Pull ticks off the queue and hand them to the strategy layer."""
    while True:
        tick = await queue.get()
        if tick is None:
            break
        process_tick(tick)
        metrics.ticks_processed += 1


async def run_naive_pipeline(tick_count: int) -> PipelineMetrics:
    """Run the naive one-producer/one-consumer pipeline end to end.

    Args:
        tick_count: How many simulated ticks to push through the
            pipeline before stopping.

    Returns:
        A populated ``PipelineMetrics`` instance for reporting.
    """
    metrics = PipelineMetrics()
    queue: asyncio.Queue[Tick | None] = asyncio.Queue()  # unbounded, on purpose

    metrics.start()
    await asyncio.gather(
        _producer(queue, tick_count, metrics),
        _consumer(queue, metrics),
    )
    metrics.stop()

    logger.info("Naive pipeline run complete: %s ticks", tick_count)
    return metrics

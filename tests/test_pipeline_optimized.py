"""Integration tests for the object-pool-optimized pipeline."""

import pytest

from market_pipeline.pipeline_optimized import run_optimized_pipeline


@pytest.mark.asyncio
async def test_optimized_pipeline_processes_all_ticks() -> None:
    metrics = await run_optimized_pipeline(tick_count=5000, pool_size=100)

    assert metrics.ticks_generated == 5000
    assert metrics.ticks_processed == 5000


@pytest.mark.asyncio
async def test_optimized_pipeline_reuses_far_more_than_it_creates() -> None:
    metrics = await run_optimized_pipeline(tick_count=10_000, pool_size=100)

    # The pool starts with exactly `pool_size` objects. A small number
    # of overflow allocations can occur while the queue first fills up
    # and backpressure kicks in (see the design note in
    # pipeline_optimized.py), so we assert an upper bound rather than
    # exact equality -- the key property is that creation stays close
    # to pool_size while reuse dominates the workload.
    assert metrics.objects_created < 150
    assert metrics.objects_reused > 9_900
    assert metrics.objects_reused > metrics.objects_created * 50


@pytest.mark.asyncio
async def test_small_pool_still_correct_via_overflow() -> None:
    """Even a badly undersized pool must remain correct (just slower)."""
    metrics = await run_optimized_pipeline(tick_count=2000, pool_size=1)

    assert metrics.ticks_processed == 2000
    assert metrics.objects_created >= 1

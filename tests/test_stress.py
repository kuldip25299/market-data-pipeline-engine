"""Stress tests: larger workloads to catch issues that only appear at scale.

These are marked with the `stress` marker (see pyproject.toml) so they
can be excluded from the fast default test run:

    pytest -m "not stress"     # fast suite, for every commit / CI
    pytest -m "stress"         # slow suite, for release validation
"""

import pytest

from market_pipeline.object_pool import TickObjectPool
from market_pipeline.pipeline_naive import run_naive_pipeline
from market_pipeline.pipeline_optimized import run_optimized_pipeline

pytestmark = pytest.mark.stress


@pytest.mark.asyncio
async def test_naive_pipeline_handles_large_volume() -> None:
    metrics = await run_naive_pipeline(tick_count=200_000)
    assert metrics.ticks_processed == 200_000


@pytest.mark.asyncio
async def test_optimized_pipeline_handles_large_volume() -> None:
    metrics = await run_optimized_pipeline(tick_count=200_000, pool_size=1000)
    assert metrics.ticks_processed == 200_000
    # At scale, reuse should dominate creation by orders of magnitude.
    assert metrics.objects_reused > metrics.objects_created * 100


def test_object_pool_survives_heavy_churn() -> None:
    """Simulate a long-running process cycling millions of acquire/release
    calls, verifying the pool never grows beyond its configured size
    (i.e. no leak from repeated use)."""
    pool = TickObjectPool(pool_size=500)

    for i in range(1_000_000):
        tick = pool.acquire(symbol="A", price=float(i), quantity=1, timestamp_ns=i)
        pool.release(tick)

    assert pool.available_count == 500

"""End-to-end integration tests that compare naive vs optimized behavior."""

import pytest

from market_pipeline.pipeline_naive import run_naive_pipeline
from market_pipeline.pipeline_optimized import run_optimized_pipeline


@pytest.mark.asyncio
async def test_both_pipelines_process_identical_tick_counts() -> None:
    """Regardless of internal implementation, both pipelines must be
    functionally equivalent from the outside: same input count in,
    same processed count out. This is the contract that allows us to
    swap implementations without touching calling code."""
    naive_metrics = await run_naive_pipeline(tick_count=1000)
    optimized_metrics = await run_optimized_pipeline(tick_count=1000, pool_size=200)

    assert naive_metrics.ticks_processed == optimized_metrics.ticks_processed == 1000


@pytest.mark.asyncio
async def test_optimized_allocates_far_fewer_objects_than_naive() -> None:
    """This is the test that *proves* the optimization does what it
    claims: for the same workload, the optimized pipeline creates
    dramatically fewer objects than the naive one."""
    tick_count = 5000
    naive_metrics = await run_naive_pipeline(tick_count=tick_count)
    optimized_metrics = await run_optimized_pipeline(tick_count=tick_count, pool_size=100)

    assert naive_metrics.objects_created == tick_count
    # A small overflow above pool_size (100) can occur during warm-up
    # before backpressure fully kicks in -- see the design note in
    # pipeline_optimized.py. The important property is the dramatic
    # reduction versus the naive pipeline's one-allocation-per-tick.
    assert optimized_metrics.objects_created < 150
    assert optimized_metrics.objects_created < naive_metrics.objects_created

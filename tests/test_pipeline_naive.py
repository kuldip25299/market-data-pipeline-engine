"""Integration tests for the naive pipeline."""

import pytest

from market_pipeline.pipeline_naive import run_naive_pipeline


@pytest.mark.asyncio
async def test_naive_pipeline_processes_all_ticks() -> None:
    metrics = await run_naive_pipeline(tick_count=500)

    assert metrics.ticks_generated == 500
    assert metrics.ticks_processed == 500
    # Every tick in the naive version is a fresh allocation.
    assert metrics.objects_created == 500
    assert metrics.objects_reused == 0
    assert metrics.elapsed_seconds > 0


@pytest.mark.asyncio
async def test_naive_pipeline_handles_zero_ticks() -> None:
    metrics = await run_naive_pipeline(tick_count=0)

    assert metrics.ticks_generated == 0
    assert metrics.ticks_processed == 0

"""
benchmark_optimized.py
========================

Standalone benchmark for the object-pool-optimized pipeline.

Run with:
    python benchmarks/benchmark_optimized.py [tick_count] [pool_size]
"""

from __future__ import annotations

import asyncio
import sys

from market_pipeline.logging_config import configure_logging
from market_pipeline.pipeline_optimized import run_optimized_pipeline


async def main(tick_count: int, pool_size: int) -> None:
    configure_logging()
    metrics = await run_optimized_pipeline(tick_count=tick_count, pool_size=pool_size)
    print(metrics.report(title="Optimized Pipeline Benchmark"))


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    pool = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    asyncio.run(main(count, pool))

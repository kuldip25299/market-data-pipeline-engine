"""
benchmark_naive.py
===================

Standalone benchmark for the naive (unoptimized) pipeline.

Run with:
    python benchmarks/benchmark_naive.py [tick_count]
"""

from __future__ import annotations

import asyncio
import sys

from market_pipeline.logging_config import configure_logging
from market_pipeline.pipeline_naive import run_naive_pipeline


async def main(tick_count: int) -> None:
    configure_logging()
    metrics = await run_naive_pipeline(tick_count=tick_count)
    print(metrics.report(title="Naive Pipeline Benchmark"))


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    asyncio.run(main(count))

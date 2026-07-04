"""
run_optimized_example.py
==========================

The smallest possible working example of the object-pool-optimized
pipeline. Compare this file line-by-line with run_naive_example.py --
notice how little changes at the call site.

Run with:
    python examples/run_optimized_example.py
"""

import asyncio

from market_pipeline.logging_config import configure_logging
from market_pipeline.pipeline_optimized import run_optimized_pipeline


async def main() -> None:
    configure_logging()
    print("Starting optimized pipeline with 10,000 simulated ticks...\n")

    metrics = await run_optimized_pipeline(tick_count=10_000, pool_size=200)

    print()
    print(metrics.report(title="Optimized Pipeline Example"))


if __name__ == "__main__":
    asyncio.run(main())

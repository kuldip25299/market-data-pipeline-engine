"""
run_naive_example.py
=====================

The smallest possible working example of the naive pipeline. Start
here if you've just cloned the repo.

Run with:
    python examples/run_naive_example.py
"""

import asyncio

from market_pipeline.logging_config import configure_logging
from market_pipeline.pipeline_naive import run_naive_pipeline


async def main() -> None:
    configure_logging()
    print("Starting naive pipeline with 10,000 simulated ticks...\n")

    metrics = await run_naive_pipeline(tick_count=10_000)

    print()
    print(metrics.report(title="Naive Pipeline Example"))


if __name__ == "__main__":
    asyncio.run(main())

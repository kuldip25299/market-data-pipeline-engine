"""
compare.py
==========

Runs BOTH pipelines back to back on identical workloads and prints a
side-by-side comparison table. Optionally saves a bar chart to
benchmarks/results/ if matplotlib is installed.

Run with:
    python benchmarks/compare.py [tick_count] [pool_size]

WHY THIS FILE EXISTS
---------------------
Every number in docs/07_benchmark.md and the README's "Expected
Output" section is reproducible by running this exact script. This is
the difference between "trust me, pools are faster" and an engineering
claim you can independently verify.
"""

from __future__ import annotations

import asyncio
import sys

from market_pipeline.logging_config import configure_logging
from market_pipeline.metrics import PipelineMetrics
from market_pipeline.pipeline_naive import run_naive_pipeline
from market_pipeline.pipeline_optimized import run_optimized_pipeline


def _print_comparison_table(naive: PipelineMetrics, optimized: PipelineMetrics) -> None:
    rows = [
        ("Ticks Processed", naive.ticks_processed, optimized.ticks_processed),
        ("Objects Created", naive.objects_created, optimized.objects_created),
        ("Objects Reused", naive.objects_reused, optimized.objects_reused),
        ("Peak Queue Size", naive.peak_queue_size, optimized.peak_queue_size),
        (
            "Elapsed Time (s)",
            f"{naive.elapsed_seconds:.3f}",
            f"{optimized.elapsed_seconds:.3f}",
        ),
        (
            "Throughput (ticks/s)",
            f"{naive.throughput_per_sec:,.0f}",
            f"{optimized.throughput_per_sec:,.0f}",
        ),
        (
            "Peak Memory (MB)",
            f"{naive.peak_memory_mb:.2f}",
            f"{optimized.peak_memory_mb:.2f}",
        ),
    ]

    header = f"{'Metric':<22}{'Naive':>16}{'Optimized':>16}"
    print(header)
    print("-" * len(header))
    for name, naive_val, opt_val in rows:
        print(f"{name:<22}{str(naive_val):>16}{str(opt_val):>16}")

    if optimized.elapsed_seconds > 0:
        speedup = naive.elapsed_seconds / optimized.elapsed_seconds
        print(f"\nSpeedup: {speedup:.2f}x")


def _try_save_chart(naive: PipelineMetrics, optimized: PipelineMetrics) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "\n(matplotlib not installed -- skipping chart generation. "
            "Run `pip install matplotlib` to enable it.)"
        )
        return

    labels = ["Throughput (ticks/s)", "Objects Created", "Peak Memory (MB)"]
    naive_vals = [naive.throughput_per_sec, naive.objects_created, naive.peak_memory_mb]
    opt_vals = [optimized.throughput_per_sec, optimized.objects_created, optimized.peak_memory_mb]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, label, n_val, o_val in zip(axes, labels, naive_vals, opt_vals, strict=True):
        ax.bar(["Naive", "Optimized"], [n_val, o_val], color=["#d9534f", "#5cb85c"])
        ax.set_title(label)

    fig.suptitle("Naive vs Object-Pool-Optimized Pipeline")
    fig.tight_layout()

    output_path = "benchmarks/results/comparison_chart.png"
    fig.savefig(output_path, dpi=150)
    print(f"\nChart saved to {output_path}")


async def main(tick_count: int, pool_size: int) -> None:
    configure_logging()

    print(f"Running comparison with {tick_count:,} ticks (pool_size={pool_size})...\n")

    naive_metrics = await run_naive_pipeline(tick_count=tick_count)
    optimized_metrics = await run_optimized_pipeline(tick_count=tick_count, pool_size=pool_size)

    _print_comparison_table(naive_metrics, optimized_metrics)
    _try_save_chart(naive_metrics, optimized_metrics)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    pool = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    asyncio.run(main(count, pool))

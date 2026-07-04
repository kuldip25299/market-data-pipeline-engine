"""
metrics.py
==========

Lightweight metrics collection shared by both pipeline implementations
and the benchmark scripts.

WHY THIS FILE EXISTS
---------------------
"You can't optimize what you don't measure." Before we touch a single
line of optimization code in Chapter 5/6, we need a trustworthy,
consistent way to answer:

- How many events did we process?
- How long did it take?
- How many objects did we allocate vs. reuse?
- How big did the internal queue get (a proxy for backpressure risk)?

Every number printed in this repository's README and docs comes from
this class -- nothing is hand-waved.
"""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass, field


@dataclass
class PipelineMetrics:
    """Accumulates counters for a single pipeline run."""

    ticks_generated: int = 0
    ticks_processed: int = 0
    objects_created: int = 0
    objects_reused: int = 0
    peak_queue_size: int = 0
    _start_time: float = field(default=0.0, repr=False)
    _end_time: float = field(default=0.0, repr=False)
    _peak_memory_bytes: int = field(default=0, repr=False)

    def start(self) -> None:
        """Begin timing and memory tracking for this run."""
        tracemalloc.start()
        self._start_time = time.perf_counter()

    def stop(self) -> None:
        """Stop timing and capture peak memory usage."""
        self._end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        self._peak_memory_bytes = peak
        tracemalloc.stop()

    def record_queue_size(self, current_size: int) -> None:
        """Track the highest queue depth seen during the run.

        A consistently growing queue size is the classic symptom of a
        producer that is faster than its consumer -- see
        docs/05_performance_problem.md for how we diagnose this.
        """
        self.peak_queue_size = max(self.peak_queue_size, current_size)

    @property
    def elapsed_seconds(self) -> float:
        return self._end_time - self._start_time

    @property
    def throughput_per_sec(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.ticks_processed / self.elapsed_seconds

    @property
    def peak_memory_mb(self) -> float:
        return self._peak_memory_bytes / (1024 * 1024)

    def report(self, title: str = "Market Data Pipeline") -> str:
        """Render a human-readable summary block, used by examples
        and benchmark scripts so terminal output stays consistent."""
        bar = "=" * 51
        lines = [
            bar,
            title.center(51),
            bar,
            f"{'Ticks Generated':<22}: {self.ticks_generated:,}",
            f"{'Ticks Processed':<22}: {self.ticks_processed:,}",
            f"{'Objects Created':<22}: {self.objects_created:,}",
            f"{'Objects Reused':<22}: {self.objects_reused:,}",
            f"{'Peak Queue Size':<22}: {self.peak_queue_size:,}",
            f"{'Elapsed Time':<22}: {self.elapsed_seconds:.2f} sec",
            f"{'Throughput':<22}: {self.throughput_per_sec:,.0f} ticks/sec",
            f"{'Peak Memory':<22}: {self.peak_memory_mb:.2f} MB",
            bar,
        ]
        return "\n".join(lines)

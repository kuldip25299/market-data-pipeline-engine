"""
market_pipeline
================

A teaching-grade, production-inspired market data pipeline.

This package intentionally ships TWO implementations of the same pipeline:

1. ``pipeline_naive``     -> the "obvious" first implementation.
2. ``pipeline_optimized`` -> the same pipeline after we found (and proved)
                              a real bottleneck via profiling.

Why keep both instead of just deleting the slow one?
-----------------------------------------------------
Because the entire point of this repository is to *demonstrate the
engineering journey*, not just hand you the final answer. In a real
trading firm, the naive version is usually still sitting in the git
history -- and the commit that replaces it is backed by a benchmark,
not a hunch. Keeping both lets us prove, with numbers, that the
optimization was worth the added complexity.
"""

from market_pipeline.models import Tick

__all__ = ["Tick"]
__version__ = "0.1.0"

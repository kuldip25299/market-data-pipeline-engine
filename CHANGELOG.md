# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-07-04

### Added
- Initial public release.
- Naive producer/consumer pipeline (`pipeline_naive.py`) built on `asyncio.Queue`.
- Simulated exchange feed generator (`generator.py`) for a fixed universe of symbols.
- Profiling-driven identification of allocation overhead as the primary bottleneck (see `docs/05_performance_problem.md`).
- Object Pool optimization (`object_pool.py`, `pipeline_optimized.py`).
- Benchmark suite comparing naive vs. optimized implementations (`benchmarks/`).
- Full documentation set: introduction, real-world problem framing, market data flow, pipeline construction, performance analysis, object pool design, benchmarking methodology, scaling strategy, future architecture, and glossary.
- Unit, integration, and stress test suites.
- Docker and docker-compose support for reproducible benchmark runs.
- GitHub Actions CI (lint, type-check, test).
- ADRs documenting the asyncio and object-pool design decisions.

### Notes
- This is a teaching repository. It does not connect to any real exchange
  and should not be used as-is for live trading infrastructure.
